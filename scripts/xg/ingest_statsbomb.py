#!/usr/bin/env python3
"""Audit a pinned official Open Data checkout; never export source rows publicly."""

import argparse
from collections import Counter
import csv
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile

VERSION = "1.0.0"
SCHEMA_VERSION = 1
SOURCE_URL = "https://github.com/hudl/open-data"
COHORT = {
    "world-cup-2022": ("FIFA World Cup", "2022"),
    "euro-2020": ("UEFA Euro", "2020"),
    "bundesliga-2015-16": ("1. Bundesliga", "2015/2016"),
    "la-liga-2015-16": ("La Liga", "2015/2016"),
    "ligue-1-2015-16": ("Ligue 1", "2015/2016"),
    "premier-league-2015-16": ("Premier League", "2015/2016"),
    "serie-a-2015-16": ("Serie A", "2015/2016"),
    "world-cup-2018": ("FIFA World Cup", "2018"),
    "euro-2024": ("UEFA Euro", "2024"),
    "copa-america-2024": ("Copa America", "2024"),
}
# Official Open Data specification v1.1, Shot / outcome. The specification also
# spells outcome 116 "Saved To Post"; event files use "Saved to Post".
OUTCOMES = {
    "Blocked": 0, "Goal": 1, "Off T": 0, "Post": 0, "Saved": 0,
    "Wayward": 0, "Saved Off Target": 0, "Saved to Post": 0,
    "Saved To Post": 0,
}
POSITIONS = {
    "Goalkeeper", "Right Back", "Right Center Back", "Center Back",
    "Left Center Back", "Left Back", "Right Wing Back", "Left Wing Back",
    "Right Defensive Midfield", "Center Defensive Midfield",
    "Left Defensive Midfield", "Right Midfield", "Right Center Midfield",
    "Center Midfield", "Left Center Midfield", "Left Midfield", "Right Wing",
    "Right Attacking Midfield", "Center Attacking Midfield",
    "Left Attacking Midfield", "Left Wing", "Right Center Forward", "Center Forward",
    "Left Center Forward", "Secondary Striker",
}
STAGES = ("all_shots", "open_play", "foot", "base", "valid_frame", "position_usable")
REASONS = ("missing_type", "not_open_play", "missing_body_part", "not_foot",
           "invalid_location", "missing_outcome", "unknown_outcome")


class AuditError(ValueError):
    """Input or output integrity failure, with no source records in the message."""


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False,
                      allow_nan=False, separators=(",", ":")) + "\n"


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def git_blob_sha(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def git(root, *args):
    try:
        return subprocess.check_output(["git", "-C", str(root), *args],
                                       stderr=subprocess.PIPE).decode().strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise AuditError("Source must be a pinned local Git checkout") from exc


def integer(value):
    return type(value) is int and value > 0


def name(value):
    result = value.get("name") if isinstance(value, dict) else None
    return result if isinstance(result, str) and result else None


def point(value):
    return (isinstance(value, list) and len(value) == 2
            and all(type(v) in (int, float) and math.isfinite(v) for v in value)
            and 0 <= value[0] <= 120 and 0 <= value[1] <= 80)


def unique_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON key")
        result[key] = value
    return result


class Source:
    def __init__(self, root):
        self.root = Path(root).resolve()
        if Path(git(self.root, "rev-parse", "--show-toplevel")).resolve() != self.root:
            raise AuditError("Source directory must be the source checkout root")
        self.revision = git(self.root, "rev-parse", "HEAD")
        self.entries = {}
        for line in git(self.root, "ls-tree", "-r", "HEAD").splitlines():
            metadata, path = line.split("\t", 1)
            mode, kind, digest = metadata.split()
            if kind == "blob":
                self.entries[path] = (mode, digest)
        self.inventory = {}

    def read(self, path, optional=False):
        file = self.root / path
        entry = self.entries.get(path)
        if entry is None:
            if optional and not file.exists():
                return None
            raise AuditError(f"Untracked or absent source input: {path}")
        if entry[0] != "100644" or file.is_symlink():
            raise AuditError(f"Unsupported source file type: {path}")
        try:
            data = file.read_bytes()
        except OSError as exc:
            raise AuditError(f"Missing/unreadable source input: {path}") from exc
        if git_blob_sha(data) != entry[1]:
            raise AuditError(f"Source input differs from pinned commit: {path}")
        self.inventory[path] = {"path": path, "sha256": sha256(data),
                                "git_blob_sha": entry[1]}
        try:
            value = json.loads(data, object_pairs_hook=unique_keys)
        except (ValueError, UnicodeError) as exc:
            raise AuditError(f"Malformed JSON: {path}") from exc
        if not isinstance(value, list) or any(not isinstance(v, dict) for v in value):
            raise AuditError(f"Expected array of objects: {path}")
        return value

    def recheck(self):
        if git(self.root, "rev-parse", "HEAD") != self.revision:
            raise AuditError("Source revision changed during audit")
        for path, entry in self.inventory.items():
            try:
                data = (self.root / path).read_bytes()
            except OSError as exc:
                raise AuditError(f"Source input disappeared during audit: {path}") from exc
            if sha256(data) != entry["sha256"]:
                raise AuditError(f"Source input changed during audit: {path}")


def inspect_frame(value, separate_360=False):
    result = {"status": "missing", "players": [], "invalid_entries": 0,
              "invalid_locations": 0, "unknown_roles": 0,
              "visible_players": None, "visible_defenders": None,
              "opponent_goalkeepers": None, "goalkeeper_case": "not_assessable"}
    if value is None:
        return result
    if not isinstance(value, list):
        result.update(status="invalid", invalid_entries=1)
        return result
    result["status"] = "empty" if not value else "valid"
    defenders = keepers = 0
    for player in value:
        if not isinstance(player, dict):
            result["invalid_entries"] += 1
            continue
        valid_location = point(player.get("location"))
        teammate = player.get("teammate")
        position = name(player.get("position"))
        if separate_360:
            keeper = player.get("keeper")
            valid_role = (type(teammate) is bool and type(keeper) is bool
                          and type(player.get("actor")) is bool)
        else:
            keeper = position == "Goalkeeper"
            valid_role = type(teammate) is bool and position in POSITIONS
        result["invalid_locations"] += int(not valid_location)
        result["unknown_roles"] += int(not valid_role)
        if not valid_location or not valid_role:
            result["invalid_entries"] += 1
            continue
        normalized = {"location": player["location"], "teammate": teammate,
                      "keeper": keeper}
        if not separate_360:
            normalized["position"] = position
        else:
            normalized["actor"] = player["actor"]
        result["players"].append(normalized)
        if not teammate:
            keepers += int(keeper)
            defenders += int(not keeper)
    result["players"].sort(key=canonical)
    result.update(visible_players=len(result["players"]), visible_defenders=defenders,
                  opponent_goalkeepers=keepers,
                  goalkeeper_case="zero" if keepers == 0 else "one" if keepers == 1 else "multiple")
    if result["invalid_entries"]:
        result["status"] = "invalid"
    return result


def position_usable(frame):
    return frame["status"] == "valid" and frame["opponent_goalkeepers"] == 1


def new_counts():
    counts = {"fixtures": 0, "events_read": 0, "matches_with_360_file": 0,
              "orphan_360_events": 0, "invalid_player_entries": 0,
              "invalid_player_locations": 0, "unknown_player_roles": 0,
              "frame_comparisons": 0, "frame_discrepancies": 0,
              "all_unknown_outcomes": 0, "all_missing_outcomes": 0,
              "base_360_valid": 0, "base_360_position_usable": 0,
              "all_360_joined": 0, "all_360_valid": 0, "base_360_joined": 0}
    for stage in STAGES:
        for suffix in ("", "_goals", "_matches"):
            counts[stage + suffix] = 0
    for reason in REASONS:
        counts["exclude_" + reason] = 0
    for status in ("missing", "empty", "valid", "invalid"):
        counts["frame_" + status] = 0
        counts["base_360_frame_" + status] = 0
    for case in ("not_assessable", "zero", "one", "multiple"):
        counts["keeper_" + case] = 0
    return counts


def validate_counts(counts):
    exclusions = lambda *reasons: sum(counts["exclude_" + r] for r in reasons)
    checks = (
        counts["all_shots"] == counts["open_play"] + exclusions("missing_type", "not_open_play"),
        counts["open_play"] == counts["foot"] + exclusions("missing_body_part", "not_foot"),
        counts["foot"] == counts["base"] + exclusions("invalid_location", "missing_outcome", "unknown_outcome"),
        counts["base"] == sum(counts["frame_" + s] for s in ("missing", "empty", "valid", "invalid")),
        counts["base"] == sum(counts["keeper_" + s] for s in ("not_assessable", "zero", "one", "multiple")),
        counts["base"] == sum(counts["base_360_frame_" + s] for s in ("missing", "empty", "valid", "invalid")),
        counts["valid_frame"] == counts["frame_valid"],
        0 <= counts["position_usable"] <= counts["valid_frame"] <= counts["base"],
        counts["position_usable_goals"] <= counts["valid_frame_goals"] <= counts["base_goals"],
    )
    if not all(checks):
        raise AuditError("Count reconciliation failed")


def audit_match(source, match_id, context, seen):
    path = f"data/events/{match_id}.json"
    events = source.read(path)
    counts = new_counts()
    counts.update(fixtures=1, events_read=len(events))
    identifiers = []
    for event in events:
        eid = event.get("id")
        if not isinstance(eid, str) or not eid:
            raise AuditError(f"Missing/invalid event identifier: {path}")
        if not isinstance(event.get("type"), dict) or not isinstance(name(event["type"]), str):
            raise AuditError(f"Missing/invalid event type: {path}")
        identifiers.append(eid)
    frequencies = Counter(identifiers)
    duplicates = sum(n - 1 for n in frequencies.values()) + len(set(identifiers) & seen)
    if duplicates:
        raise AuditError(f"Duplicate event occurrences={duplicates}: {path}")
    seen.update(identifiers)
    frames = source.read(f"data/three-sixty/{match_id}.json", optional=True)
    frame_map = {}
    if frames is not None:
        counts["matches_with_360_file"] = 1
        uuids = [f.get("event_uuid") for f in frames]
        if any(not isinstance(v, str) or not v for v in uuids):
            raise AuditError(f"Invalid 360 event identifier: match {match_id}")
        duplicates = sum(n - 1 for n in Counter(uuids).values())
        if duplicates:
            raise AuditError(f"Duplicate 360 occurrences={duplicates}: match {match_id}")
        frame_map = {f["event_uuid"]: inspect_frame(f.get("freeze_frame"), True) for f in frames}
        counts["orphan_360_events"] = len(set(frame_map) - set(identifiers))
    shots = []
    defender_counts = Counter()
    outcomes = Counter()
    for event in events:
        if name(event.get("type")) != "Shot":
            continue
        shot = event.get("shot")
        shot = shot if isinstance(shot, dict) else {}
        outcome = name(shot.get("outcome"))
        goal = int(outcome == "Goal")
        outcomes[outcome if isinstance(outcome, str) else "<missing>"] += 1
        counts["all_missing_outcomes"] += int(outcome is None)
        counts["all_unknown_outcomes"] += int(outcome is not None and outcome not in OUTCOMES)
        frame360 = frame_map.get(event["id"], inspect_frame(None, True))
        joined = event["id"] in frame_map
        counts["all_360_joined"] += int(joined)
        counts["all_360_valid"] += int(frame360["status"] == "valid")
        counts["all_shots"] += 1
        counts["all_shots_goals"] += goal
        reason = None
        shot_type = name(shot.get("type"))
        body_part = name(shot.get("body_part"))
        if shot_type is None:
            reason = "missing_type"
        elif shot_type != "Open Play":
            reason = "not_open_play"
        else:
            counts["open_play"] += 1
            counts["open_play_goals"] += goal
            if body_part is None:
                reason = "missing_body_part"
            elif body_part not in ("Left Foot", "Right Foot"):
                reason = "not_foot"
            else:
                counts["foot"] += 1
                counts["foot_goals"] += goal
                if not point(event.get("location")):
                    reason = "invalid_location"
                elif outcome is None:
                    reason = "missing_outcome"
                elif outcome not in OUTCOMES:
                    reason = "unknown_outcome"
        if reason:
            counts["exclude_" + reason] += 1
            continue
        counts["base"] += 1
        counts["base_goals"] += goal
        frame = inspect_frame(shot.get("freeze_frame"))
        counts["frame_" + frame["status"]] += 1
        counts["keeper_" + frame["goalkeeper_case"]] += 1
        counts["invalid_player_entries"] += frame["invalid_entries"]
        counts["invalid_player_locations"] += frame["invalid_locations"]
        counts["unknown_player_roles"] += frame["unknown_roles"]
        if frame["status"] == "valid":
            counts["valid_frame"] += 1
            counts["valid_frame_goals"] += goal
            defender_counts[str(frame["visible_defenders"])] += 1
        usable = position_usable(frame)
        counts["position_usable"] += int(usable)
        counts["position_usable_goals"] += int(usable) * goal
        counts["base_360_joined"] += int(joined)
        counts["base_360_frame_" + frame360["status"]] += 1
        counts["base_360_valid"] += int(frame360["status"] == "valid")
        counts["base_360_position_usable"] += int(position_usable(frame360))
        comparison = None
        if joined and frame["status"] != "missing":
            fields = ("status", "visible_players", "visible_defenders", "opponent_goalkeepers")
            comparison = {key: frame[key] != frame360[key] for key in fields}
            counts["frame_comparisons"] += 1
            counts["frame_discrepancies"] += int(any(comparison.values()))
        shots.append({"schema_version": SCHEMA_VERSION, **context, "match_id": match_id,
                      "event_id": event["id"], "outcome": outcome, "is_goal": goal,
                      "body_part": body_part, "location": event["location"],
                      "embedded_frame": frame, "position_usable": usable,
                      "separate_360": {"joined": joined, **frame360},
                      "frame_comparison": comparison})
    for stage in STAGES:
        counts[stage + "_matches"] = int(counts[stage] > 0)
    validate_counts(counts)
    return counts, shots, defender_counts, outcomes


def rates(counts):
    def ratio(numerator, denominator):
        n, d = counts[numerator], counts[denominator]
        return {"numerator": n, "denominator": d, "rate": n / d if d else None}
    result = {
        "base_goal_prevalence": ratio("base_goals", "base"),
        "embedded_valid_coverage": ratio("valid_frame", "base"),
        "embedded_position_usable_coverage": ratio("position_usable", "base"),
        "match_360_availability": ratio("matches_with_360_file", "fixtures"),
        "all_shot_360_join_coverage": ratio("all_360_joined", "all_shots"),
        "all_shot_360_valid_coverage": ratio("all_360_valid", "all_shots"),
        "base_360_join_coverage": ratio("base_360_joined", "base"),
        "base_360_valid_coverage": ratio("base_360_valid", "base"),
    }
    for status in ("missing", "empty", "valid", "invalid"):
        result["embedded_frame_" + status + "_rate"] = ratio("frame_" + status, "base")
        result["base_360_frame_" + status + "_rate"] = ratio("base_360_frame_" + status, "base")
    for case in ("not_assessable", "zero", "one", "multiple"):
        result["embedded_keeper_" + case + "_rate"] = ratio("keeper_" + case, "base")
    return result


def feasibility(total, competitions, match_counts, complete):
    # Diagnostic only: select whole matches in a deterministic hash order until
    # both holdout minima are met, then verify a nonempty complement remains.
    groups = sorted(match_counts, key=lambda m: sha256(str(m["match_id"]).encode()))
    shots = goals = matches = 0
    for group in groups:
        if shots >= 2000 and goals >= 100:
            break
        if group["position_usable"]:
            shots += group["position_usable"]
            goals += group["position_usable_goals"]
            matches += 1
    active = len({c["competition_id"] for c in competitions
                  if c["counts"]["position_usable"]})
    checks = {
        "complete_requested_cohort": complete,
        "position_usable_shots_at_least_10000": total["position_usable"] >= 10000,
        "position_usable_goals_at_least_1000": total["position_usable_goals"] >= 1000,
        "represented_matches_at_least_200": total["position_usable_matches"] >= 200,
        "represented_competitions_at_least_3": active >= 3,
        "diagnostic_holdout_capacity": (shots >= 2000 and goals >= 100
                                        and shots < total["position_usable"]
                                        and goals < total["position_usable_goals"]),
    }
    return {"passes_planning_screen": all(checks.values()), "checks": checks,
            "diagnostic_holdout": {"shots": shots, "goals": goals, "matches": matches},
            "represented_competitions": active,
            "limitation": "Planning minima only; not a split, quality guarantee or calibration evidence."}


def build_audit(source, selection, shot_file):
    metadata = source.read("data/competitions.json")
    for competition in metadata:
        if (not integer(competition.get("competition_id"))
                or not integer(competition.get("season_id"))
                or any(not isinstance(competition.get(field), str) or not competition[field]
                       for field in ("competition_name", "season_name", "competition_gender"))
                or type(competition.get("competition_youth")) is not bool):
            raise AuditError("Invalid competition metadata: data/competitions.json")
    competitions, match_counts = [], []
    seen, fixture_ids = set(), set()
    total = new_counts()
    for key in sorted(selection):
        competition_name, season_name = COHORT[key]
        candidates = [c for c in metadata if c.get("competition_name") == competition_name
                      and c.get("season_name") == season_name
                      and c.get("competition_gender") == "male"
                      and c.get("competition_youth") is False]
        if len(candidates) > 1:
            raise AuditError(f"Ambiguous competition selection: {key}")
        entry = {"selection": key, "competition_name": competition_name,
                 "season_name": season_name, "competition_id": None, "season_id": None,
                 "available": bool(candidates), "counts": new_counts()}
        distribution, outcomes = Counter(), Counter()
        if candidates:
            c = candidates[0]
            cid, sid = c.get("competition_id"), c.get("season_id")
            if not integer(cid) or not integer(sid):
                raise AuditError(f"Invalid competition/season identifiers: {key}")
            entry.update(competition_id=cid, season_id=sid)
            fixtures = source.read(f"data/matches/{cid}/{sid}.json")
            for match in fixtures:
                mid = match.get("match_id")
                if (not integer(mid) or mid in fixture_ids
                        or not isinstance(match.get("competition"), dict)
                        or not isinstance(match.get("season"), dict)
                        or match["competition"].get("competition_id") != cid
                        or match["season"].get("season_id") != sid):
                    raise AuditError(f"Invalid, duplicate or contradictory fixture mapping: {key}")
                fixture_ids.add(mid)
            for match in sorted(fixtures, key=lambda m: m["match_id"]):
                mid = match["match_id"]
                context = {"competition_id": cid, "season_id": sid}
                counts, shots, defenders, match_outcomes = audit_match(source, mid, context, seen)
                for row in sorted(shots, key=lambda s: s["event_id"]):
                    shot_file.write(canonical(row))
                match_counts.append({**context, "match_id": mid, **counts})
                for field, value in counts.items():
                    entry["counts"][field] += value
                distribution.update(defenders)
                outcomes.update(match_outcomes)
            print(f"Audited {key}: {len(fixtures)} matches", file=sys.stderr)
        entry["visible_defender_distribution_valid_embedded_frames"] = dict(sorted(distribution.items()))
        entry["all_shot_outcomes"] = dict(sorted(outcomes.items()))
        entry["rates"] = rates(entry["counts"])
        validate_counts(entry["counts"])
        competitions.append(entry)
        for field, value in entry["counts"].items():
            total[field] += value
    validate_counts(total)
    for field, value in total.items():
        if value != sum(m[field] for m in match_counts):
            raise AuditError("Match/competition totals disagree")
    audit = {"schema_version": SCHEMA_VERSION, "selection": sorted(selection),
             "complete_requested_cohort": set(selection) == set(COHORT),
             "competitions": competitions, "totals": total, "rates": rates(total)}
    audit["feasibility"] = feasibility(total, competitions, match_counts,
                                       audit["complete_requested_cohort"])
    return audit, match_counts


def run(source_dir, output_dir, selection=None):
    extractor_digest = sha256(Path(__file__).read_bytes())
    selection = sorted(set(selection if selection is not None else COHORT))
    if not selection or any(key not in COHORT for key in selection):
        raise AuditError("Selection must contain known cohort keys")
    source = Source(source_dir)
    output = Path(output_dir).resolve()
    project = Path(__file__).resolve().parents[2]
    derived = project / "data" / "derived"
    if ((output == project or project in output.parents)
            and output != derived and derived not in output.parents):
        raise AuditError("Inside this project, outputs must be under ignored data/derived")
    if output == source.root or source.root in output.parents:
        raise AuditError("Outputs must be outside the source checkout")
    output.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=".staging-", dir=output))
    try:
        with (stage / "shots.jsonl").open("w", encoding="utf-8", newline="\n") as handle:
            audit, match_counts = build_audit(source, selection, handle)
        with (stage / "match-counts.csv").open("w", encoding="utf-8", newline="") as handle:
            fields = ["competition_id", "season_id", "match_id", *new_counts()]
            writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
            writer.writeheader()
            writer.writerows(sorted(match_counts, key=lambda m: (m["competition_id"], m["season_id"], m["match_id"])))
        (stage / "audit.json").write_text(canonical(audit), encoding="utf-8")
        source.recheck()
        if sha256(Path(__file__).read_bytes()) != extractor_digest:
            raise AuditError("Extractor changed during audit")
        manifest = {"schema_version": SCHEMA_VERSION, "complete": True,
                    "source_url": SOURCE_URL, "source_revision": source.revision,
                    "extractor_version": VERSION,
                    "extractor_sha256": extractor_digest,
                    "python_version": platform.python_version(), "selection": selection,
                    "source_files": [source.inventory[p] for p in sorted(source.inventory)],
                    "outputs": {p.name: sha256(p.read_bytes()) for p in sorted(stage.iterdir())}}
        run_id = sha256(canonical(manifest).encode())
        manifest["run_id"] = run_id
        (stage / "manifest.json").write_text(canonical(manifest), encoding="utf-8")
        destination = output / run_id
        if destination.exists():
            if (not destination.is_dir()
                    or {p.name for p in destination.iterdir()} != {p.name for p in stage.iterdir()}
                    or any(not (destination / p.name).is_file()
                           or (destination / p.name).read_bytes() != p.read_bytes()
                           for p in stage.iterdir())):
                raise AuditError("Existing immutable output differs; use a fresh output directory")
        else:
            os.rename(stage, destination)
        return destination, audit
    finally:
        if stage.exists():
            shutil.rmtree(stage)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--competition", action="append", choices=sorted(COHORT),
                        help="Optional subset; repeat for multiple keys. Default: complete cohort.")
    args = parser.parse_args()
    try:
        destination, audit = run(args.source_dir, args.output_dir, args.competition)
    except (AuditError, OSError) as exc:
        print(f"Audit failed: {exc}", file=sys.stderr)
        return 1
    print(f"Complete local audit: {destination}")
    print(f"Base shots={audit['totals']['base']}; position-usable={audit['totals']['position_usable']}; "
          f"planning screen={audit['feasibility']['passes_planning_screen']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
