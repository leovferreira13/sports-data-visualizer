#!/usr/bin/env python3
"""Materialize private feature rows from a verified local ingestion run."""

import argparse
from collections import Counter
import json
import os
from pathlib import Path
import platform
import shutil
import sys
import tempfile

from features import (CONTRACT, CONTRACT_PATH, FEATURE_NAMES, VERSION,
                      extract_statsbomb_features, normalize_source_point)
from ingest_statsbomb import AuditError, OUTCOMES, canonical, integer, sha256, unique_keys

EXTRACTOR_VERSION = "1.0.0"
PROJECT = Path(__file__).resolve().parents[2]


def load_json(data):
    try:
        return json.loads(data, object_pairs_hook=unique_keys,
                          parse_constant=lambda _: (_ for _ in ()).throw(ValueError("Nonfinite JSON")))
    except (ValueError, UnicodeError) as exc:
        raise AuditError("Invalid JSON in feature input") from exc


def input_run(directory):
    data = {name: (directory / name).read_bytes() for name in ("manifest.json", "shots.jsonl", "audit.json")}
    manifest = load_json(data["manifest.json"])
    if (not isinstance(manifest, dict) or manifest.get("complete") is not True
            or type(manifest.get("schema_version")) is not int or manifest["schema_version"] != 1
            or not isinstance(manifest.get("outputs"), dict)):
        raise AuditError("Incompatible or incomplete ingestion manifest")
    for name in ("shots.jsonl", "audit.json"):
        if manifest["outputs"].get(name) != sha256(data[name]):
            raise AuditError("Ingestion output hash mismatch")
    identity = {k: v for k, v in manifest.items() if k != "run_id"}
    if manifest.get("run_id") != sha256(canonical(identity).encode()):
        raise AuditError("Ingestion run identity mismatch")
    audit = load_json(data["audit.json"])
    if not isinstance(audit, dict) or not isinstance(audit.get("totals"), dict):
        raise AuditError("Incompatible ingestion audit")
    return data, manifest, audit


def ui_position(p):
    b = CONTRACT["ui_bounds"]
    return b["x_min"] <= p["x"] <= b["x_max"] and b["y_min"] <= p["y"] <= b["y_max"]


def new_counts():
    return {"input_shots": 0, "input_goals": 0, "accepted_shots": 0, "accepted_goals": 0,
            "rejected_shots": 0, "rejected_goals": 0, "reasons": Counter(),
            "zero_defender_sentinel": 0, "shooter_outside_ui_bounds": 0,
            "shooter_in_defensive_half": 0, "represented_scene_outside_ui_bounds": 0,
            "visible_defender_distribution": Counter(), "feature_ranges": {}}


def update(counts, row, result):
    counts["input_shots"] += 1
    counts["input_goals"] += row["is_goal"]
    if result["status"] != "ok":
        counts["rejected_shots"] += 1
        counts["rejected_goals"] += row["is_goal"]
        counts["reasons"][result["reason"]] += 1
        return
    counts["accepted_shots"] += 1
    counts["accepted_goals"] += row["is_goal"]
    n = result["features"]["visible_defender_count"]
    counts["visible_defender_distribution"][str(n)] += 1
    counts["zero_defender_sentinel"] += int(n == 0)
    s = normalize_source_point(row["location"])
    counts["shooter_outside_ui_bounds"] += int(not ui_position(s))
    counts["shooter_in_defensive_half"] += int(s["x"] < 52.5)
    opponents = [normalize_source_point(p["location"]) for p in row["embedded_frame"]["players"] if not p["teammate"]]
    counts["represented_scene_outside_ui_bounds"] += int(not all(ui_position(p) for p in [s, *opponents]))
    for name, v in result["features"].items():
        r = counts["feature_ranges"].setdefault(name, {"min": v, "max": v})
        r["min"], r["max"] = min(r["min"], v), max(r["max"], v)


def validate_row(row):
    if not isinstance(row, dict) or type(row.get("schema_version")) is not int or row["schema_version"] != 1:
        raise AuditError("Incompatible ingestion row schema")
    if (not all(integer(row.get(k)) for k in ("competition_id", "season_id", "match_id"))
            or not isinstance(row.get("event_id"), str) or not row["event_id"]
            or type(row.get("is_goal")) is not int or row["is_goal"] not in (0, 1)
            or not isinstance(row.get("outcome"), str) or row["outcome"] not in OUTCOMES
            or OUTCOMES[row["outcome"]] != row["is_goal"]):
        raise AuditError("Invalid row identity or goal label")


def run(input_dir, output_dir):
    input_dir, output = Path(input_dir).resolve(), Path(output_dir).resolve()
    derived = PROJECT / "data/derived"
    if (output == PROJECT or PROJECT in output.parents) and output != derived and derived not in output.parents:
        raise AuditError("Inside this project, outputs must be under ignored data/derived")
    if output == input_dir or input_dir in output.parents:
        raise AuditError("Feature outputs must be outside the ingestion run")
    data, ingestion, ingestion_audit = input_run(input_dir)
    files = [Path(__file__), Path(__file__).with_name("features.py"), Path(__file__).with_name("ingest_statsbomb.py"), CONTRACT_PATH]
    code_hashes = {p.relative_to(PROJECT).as_posix(): sha256(p.read_bytes()) for p in files}
    rows, seen = [], set()
    for line in data["shots.jsonl"].splitlines():
        row = load_json(line)
        validate_row(row)
        key = (row["match_id"], row["event_id"])
        if key in seen:
            raise AuditError("Duplicate input shot identity")
        seen.add(key)
        rows.append(row)
    rows.sort(key=lambda r: (r["competition_id"], r["season_id"], r["match_id"], r["event_id"]))
    totals, competitions, accepted_matches = new_counts(), {}, {}
    output.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=".staging-", dir=output))
    try:
        with (stage / "features.jsonl").open("w", encoding="utf-8", newline="\n") as handle:
            for row in rows:
                result = extract_statsbomb_features(row)
                key = (row["competition_id"], row["season_id"])
                group = competitions.setdefault(key, new_counts())
                for counts in (totals, group):
                    update(counts, row, result)
                if result["status"] == "ok":
                    accepted_matches.setdefault(key, set()).add(row["match_id"])
                    identity = {k: row[k] for k in ("competition_id", "season_id", "match_id", "event_id", "is_goal")}
                    handle.write(canonical({**identity, **result}))
        if (totals["input_shots"] != ingestion_audit["totals"].get("base")
                or totals["input_goals"] != ingestion_audit["totals"].get("base_goals")):
            raise AuditError("Feature input counts do not reconcile with ingestion audit")
        for counts in (totals, *competitions.values()):
            if (counts["accepted_shots"] + counts["rejected_shots"] != counts["input_shots"]
                    or sum(counts["reasons"].values()) != counts["rejected_shots"]
                    or counts["accepted_goals"] + counts["rejected_goals"] != counts["input_goals"]):
                raise AuditError("Feature counts do not reconcile")
        totals["represented_matches"] = len(set().union(*accepted_matches.values())) if accepted_matches else 0
        for key, counts in competitions.items():
            counts["represented_matches"] = len(accepted_matches.get(key, ()))
        audit = {"schema_version": 1, "contract_version": VERSION, "totals": totals,
                 "competitions": [{"competition_id": cid, "season_id": sid, **counts}
                                  for (cid, sid), counts in sorted(competitions.items())],
                 "finite_features": True, "visibility": "observed opponents only; embedded frames may be partial",
                 "planning_minima": {"shots_at_least_10000": totals["accepted_shots"] >= 10000,
                                     "goals_at_least_1000": totals["accepted_goals"] >= 1000,
                                     "matches_at_least_200": totals["represented_matches"] >= 200,
                                     "competitions_at_least_3": len({cid for (cid, sid), ids in accepted_matches.items() if ids}) >= 3}}
        (stage / "feature-audit.json").write_text(canonical(audit), encoding="utf-8")
        if any(sha256((input_dir / name).read_bytes()) != sha256(b) for name, b in data.items()):
            raise AuditError("Ingestion inputs changed during extraction")
        if any(sha256((PROJECT / name).read_bytes()) != digest for name, digest in code_hashes.items()):
            raise AuditError("Feature code or contract changed during extraction")
        manifest = {"schema_version": 1, "complete": True, "contract_version": VERSION,
                    "extractor_version": EXTRACTOR_VERSION, "python_version": platform.python_version(),
                    "code_sha256": code_hashes, "ingestion": {k: ingestion[k] for k in
                       ("run_id", "source_url", "source_revision", "extractor_version", "extractor_sha256", "selection")},
                    "input_sha256": {name: sha256(b) for name, b in data.items()},
                    "outputs": {p.name: sha256(p.read_bytes()) for p in stage.iterdir()}}
        manifest["run_id"] = sha256(canonical(manifest).encode())
        (stage / "manifest.json").write_text(canonical(manifest), encoding="utf-8")
        destination = output / manifest["run_id"]
        if destination.exists():
            if (not destination.is_dir() or {p.name for p in destination.iterdir()} != {p.name for p in stage.iterdir()}
                    or any(not (destination / p.name).is_file() or (destination / p.name).read_bytes() != p.read_bytes()
                           for p in stage.iterdir())):
                raise AuditError("Existing immutable features differ; use a fresh output directory")
        else:
            os.rename(stage, destination)
        return destination, audit
    finally:
        if stage.exists():
            shutil.rmtree(stage)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, required=True, help="Completed ingestion run containing shots.jsonl/manifest.json/audit.json")
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    try:
        destination, audit = run(args.input_dir, args.output_dir)
    except (AuditError, OSError, KeyError, TypeError) as exc:
        # Do not interpolate source rows, identities or coordinate values in errors.
        print(f"Feature extraction failed: {exc}" if isinstance(exc, (AuditError, OSError))
              else "Feature extraction failed: malformed input structure", file=sys.stderr)
        return 1
    print(f"Complete local features: {destination}")
    print(f"Accepted={audit['totals']['accepted_shots']}; rejected={audit['totals']['rejected_shots']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
