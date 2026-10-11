#!/usr/bin/env python3
"""Verify feature provenance and prepare label-isolated match partitions."""

import argparse
from collections import Counter, defaultdict
import math
from pathlib import Path
import sys

from compare_runs import verified_run
from features import CONTRACT_PATH, FEATURE_NAMES, VERSION
from ingest_statsbomb import AuditError, canonical, sha256
from run_io import code_identity, load_json, protocol, publish, read_json, recheck

PARTITIONS = ("train", "calibration", "selection", "test")


def validate_row(row):
    required = {"competition_id", "season_id", "match_id", "event_id", "is_goal",
                "status", "contract_version", "features", "vector", "metadata"}
    if not isinstance(row, dict) or set(row) != required:
        raise AuditError("Feature row fields differ from the contract")
    if (any(type(row[k]) is not int or row[k] <= 0 for k in ("competition_id", "season_id", "match_id"))
            or not isinstance(row["event_id"], str) or not row["event_id"]
            or type(row["is_goal"]) is not int or row["is_goal"] not in (0, 1)
            or row["status"] != "ok" or row["contract_version"] != VERSION):
        raise AuditError("Invalid row identity, context or label")
    vector, features = row["vector"], row["features"]
    if (not isinstance(vector, list) or len(vector) != 8 or not isinstance(features, dict)
            or set(features) != set(FEATURE_NAMES)
            or any(type(v) not in (int, float) or not math.isfinite(v) or v < 0 for v in vector)
            or vector != [features[n] for n in FEATURE_NAMES]):
        raise AuditError("Invalid or inconsistent feature vector")
    diagonal = math.hypot(105, 68)
    if (any(type(vector[i]) is not int for i in (3, 4))
            or not 0 <= vector[4] <= vector[3] <= 10
            or vector[1] > 180 or vector[2] > 34
            or any(vector[i] > diagonal for i in (0, 5, 6, 7))
            or (vector[3] == 0 and vector[5] != diagonal)):
        raise AuditError("Features violate physical or missingness constraints")
    if row["metadata"] != {"observation": "embedded-frame", "goalkeeper_visibility": "observed",
                           "defender_visibility": "partial"}:
        raise AuditError("Training requires the embedded-frame population")


def matches(rows):
    groups, seen = defaultdict(list), set()
    for row in rows:
        validate_row(row)
        identity = (row["match_id"], row["event_id"])
        if identity in seen:
            raise AuditError("Duplicate shot identity")
        seen.add(identity)
        groups[row["match_id"]].append(row)
    for group in groups.values():
        if len({(r["competition_id"], r["season_id"]) for r in group}) != 1:
            raise AuditError("Conflicting match metadata")
    return groups


def allocate(count, weights):
    total = sum(weights)
    quotas = [count * w / total for w in weights]
    result = [int(q) for q in quotas]
    order = sorted(range(len(weights)), key=lambda i: (-(quotas[i] - result[i]), i))
    for i in order[:count - sum(result)]:
        result[i] += 1
    return result


def split_matches(rows, config):
    groups, strata = matches(rows), defaultdict(list)
    for mid, group in groups.items():
        strata[(group[0]["competition_id"], group[0]["season_id"])].append(mid)
    assignments = {}
    for key, mids in sorted(strata.items()):
        mids.sort(key=lambda mid: (sha256(f"{config['seed']}:{key[0]}:{key[1]}:{mid}".encode()), mid))
        counts = allocate(len(mids), [config["partition_weights"][p] for p in PARTITIONS])
        if min(counts) == 0:
            raise AuditError("Insufficient match support in a competition-season stratum")
        start = 0
        for name, count in zip(PARTITIONS, counts):
            for mid in mids[start:start + count]:
                assignments[mid] = name
            start += count
    return assignments


def fold_assignments(rows, config):
    strata = defaultdict(list)
    for mid, group in matches(rows).items():
        strata[(group[0]["competition_id"], group[0]["season_id"])].append(mid)
    result = {}
    offset = 0
    for key, mids in sorted(strata.items()):
        mids.sort(key=lambda mid: (sha256(f"fold:{config['seed']}:{key[0]}:{key[1]}:{mid}".encode()), mid))
        for i, mid in enumerate(mids):
            result[mid] = (offset + i) % config["folds"]
        offset = (offset + len(mids)) % config["folds"]
    return result


def summary(rows, labels=True):
    result = {"shots": len(rows), "matches": len({r["match_id"] for r in rows}),
              "composition": []}
    strata = defaultdict(list)
    for r in rows:
        strata[(r["competition_id"], r["season_id"])].append(r)
    for (cid, sid), group in sorted(strata.items()):
        item = {"competition_id": cid, "season_id": sid, "shots": len(group),
                "matches": len({r["match_id"] for r in group})}
        if labels:
            item["goals"] = sum(r["is_goal"] for r in group)
            item["prevalence"] = item["goals"] / len(group)
        result["composition"].append(item)
    if labels:
        result["goals"] = sum(r["is_goal"] for r in rows)
        result["prevalence"] = result["goals"] / len(rows) if rows else None
    return result


def require_classes(rows, minimum):
    counts = Counter(r["is_goal"] for r in rows)
    if min(counts[0], counts[1]) < minimum:
        raise AuditError("Insufficient development class support; revise protocol before fitting")


def prepare(input_dir, output_dir):
    directory, manifest, names = verified_run(input_dir)
    if names != {"features.jsonl", "feature-audit.json", "manifest.json"} or manifest.get("contract_version") != VERSION:
        raise AuditError("Expected a complete feature run")
    if manifest.get("code_sha256", {}).get("model/feature-contract.json") != sha256(CONTRACT_PATH.read_bytes()):
        raise AuditError("Feature contract checksum drift")
    config, codes = protocol(), code_identity()
    for name in ("scripts/xg/extract_features.py", "scripts/xg/features.py", "scripts/xg/ingest_statsbomb.py"):
        if manifest.get("code_sha256", {}).get(name) != codes[name]:
            raise AuditError("Feature extractor code drift: reproduce features from the pinned corpus")
    if not isinstance(manifest.get("ingestion"), dict) or not isinstance(manifest["ingestion"].get("source_revision"), str):
        raise AuditError("Missing source revision provenance")
    rows = [load_json(line) for line in (directory / "features.jsonl").read_bytes().splitlines()]
    groups = matches(rows)
    rows.sort(key=lambda r: (r["competition_id"], r["season_id"], r["match_id"], r["event_id"]))
    audit = read_json(directory / "feature-audit.json")
    totals = audit["totals"]
    # Reconcile known full-corpus metadata, without printing held-out outcomes.
    if (len(rows) != totals["accepted_shots"] or sum(r["is_goal"] for r in rows) != totals["accepted_goals"]
            or len(groups) != totals["represented_matches"]):
        raise AuditError("Feature audit does not reconcile with rows")
    minima = config["minima"]
    if (len(rows) < minima["shots"] or totals["accepted_goals"] < minima["goals"]
            or len(groups) < minima["matches"]
            or len({r["competition_id"] for r in rows}) < minima["competitions"]):
        raise AuditError("Corpus feasibility minima do not pass")
    assignments = split_matches(rows, config)
    partitions = {p: [r for r in rows if assignments[r["match_id"]] == p] for p in PARTITIONS}
    folds = fold_assignments(partitions["train"], config)
    for p in ("calibration", "selection"):
        require_classes(partitions[p], minima["validation_class"])
    for fold in range(config["folds"]):
        require_classes([r for r in partitions["train"] if folds[r["match_id"]] == fold], minima["fold_class"])
        require_classes([r for r in partitions["train"] if folds[r["match_id"]] != fold], minima["fold_class"])
    split = {"partitions": {str(k): v for k, v in sorted(assignments.items())},
             "train_folds": {str(k): v for k, v in sorted(folds.items())}}
    files = {f"{p}.jsonl": "".join(canonical(r) for r in partitions[p]).encode() for p in PARTITIONS}
    files.update({"split.json": split, "protocol.json": config,
                  "preparation-summary.json": {"schema_version": 1, "feature_contract": VERSION,
                    "partitions": {p: summary(partitions[p], p != "test") for p in PARTITIONS},
                    "test_status": "unopened", "ui_diagnostics_from_feature_audit": {
                      k: totals[k] for k in ("shooter_outside_ui_bounds", "represented_scene_outside_ui_bounds")}}})
    return publish(output_dir, directory, "preparation", files,
                   {"feature_run_id": manifest["run_id"], "feature_manifest_sha256": sha256((directory / "manifest.json").read_bytes()),
                    "feature_contract_sha256": sha256(CONTRACT_PATH.read_bytes()), "code_sha256": codes,
                    "source": manifest["ingestion"], "protocol_sha256": sha256(canonical(config).encode())},
                   lambda: recheck(directory, manifest, codes))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    try:
        path = prepare(args.input_dir, args.output_dir)
    except (AuditError, OSError, KeyError, TypeError, ValueError) as exc:
        message = str(exc) if isinstance(exc, AuditError) else "Invalid provenance, inputs, support or output boundary"
        print(f"FAIL: {message}", file=sys.stderr)
        return 1
    print(f"Complete private preparation: {path}; test outcomes unopened")
    return 0


if __name__ == "__main__":
    sys.exit(main())
