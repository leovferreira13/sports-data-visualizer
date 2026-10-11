"""Entirely synthetic source repositories; no network or real shot fixtures."""

import copy
import contextlib
import csv
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import ingest_statsbomb as ingest


def keeper(teammate=False):
    return {"location": [117, 40], "teammate": teammate,
            "position": {"id": 1, "name": "Goalkeeper"},
            "player": {"id": 999, "name": "Synthetic player"}}


def defender():
    return {"location": [105, 42], "teammate": False,
            "position": {"id": 4, "name": "Center Back"}}


def shot(eid="synthetic-shot", outcome="Goal"):
    return {"id": eid, "type": {"name": "Shot"}, "location": [100, 40],
            "shot": {"type": {"name": "Open Play"},
                     "body_part": {"name": "Right Foot"},
                     "outcome": {"name": outcome}, "statsbomb_xg": 0.99,
                     "freeze_frame": [keeper(), defender()]}}


class SyntheticSource:
    def __init__(self, root):
        self.root = root
        self.write("data/competitions.json", [{
            "competition_id": 43, "season_id": 106,
            "competition_name": "FIFA World Cup", "season_name": "2022",
            "competition_gender": "male", "competition_youth": False}])
        self.write("data/matches/43/106.json", [self.fixture(1)])
        self.write("data/events/1.json", [shot()])
        self.git("init", "-q")
        self.commit()

    @staticmethod
    def fixture(mid):
        return {"match_id": mid, "competition": {"competition_id": 43},
                "season": {"season_id": 106}}

    def write(self, path, value):
        p = self.root / path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(value), encoding="utf-8")

    def git(self, *args):
        return subprocess.check_output(["git", "-C", str(self.root), *args],
                                       stderr=subprocess.PIPE).decode().strip()

    def commit(self):
        self.git("add", ".")
        self.git("-c", "user.name=Synthetic fixture", "-c", "user.email=fixture@example.invalid",
                 "commit", "-qm", "Synthetic source", "--allow-empty")


class AuditTests(unittest.TestCase):
    def setUp(self):
        silence = contextlib.redirect_stderr(io.StringIO())
        silence.__enter__()
        self.addCleanup(silence.__exit__, None, None, None)
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = SyntheticSource(self.root / "source")
        self.output = self.root / "derived"

    def run_audit(self, selection=None):
        return ingest.run(self.source.root, self.output, selection)

    def events(self, events):
        self.source.write("data/events/1.json", events)
        self.source.commit()

    def test_reproducible_outputs_and_source_identity(self):
        first, audit = self.run_audit()
        snapshots = {p.name: p.read_bytes() for p in first.iterdir()}
        second, rerun = self.run_audit()
        self.assertEqual(first, second)
        self.assertEqual(audit, rerun)
        self.assertEqual(snapshots, {p.name: p.read_bytes() for p in second.iterdir()})
        manifest = json.loads((first / "manifest.json").read_text())
        self.assertEqual(manifest["source_revision"], self.source.git("rev-parse", "HEAD"))
        self.assertTrue(manifest["complete"])
        self.assertEqual(audit["totals"]["position_usable_goals"], 1)
        self.assertEqual(len(audit["competitions"]), len(ingest.COHORT))
        row = json.loads((first / "shots.jsonl").read_text())
        self.assertNotIn("statsbomb_xg", json.dumps(row))
        self.assertNotIn("Synthetic player", json.dumps(row))
        self.assertNotIn("match_id", json.dumps(audit))

    def test_every_outcome_is_explicitly_labeled(self):
        self.events([shot(f"outcome-{i}", n) for i, n in enumerate(ingest.OUTCOMES)])
        folder, audit = self.run_audit()
        rows = [json.loads(line) for line in (folder / "shots.jsonl").read_text().splitlines()]
        self.assertEqual({r["outcome"]: r["is_goal"] for r in rows}, ingest.OUTCOMES)
        self.assertEqual(audit["totals"]["base_goals"], 1)

    def test_exclusive_funnel_and_missing_or_unknown_values(self):
        events = [shot(str(i)) for i in range(9)]
        events[0]["shot"]["type"]["name"] = "Penalty"
        events[0]["shot"]["body_part"]["name"] = "Head"
        events[1]["shot"]["type"]["name"] = "Free Kick"
        del events[2]["shot"]["type"]
        events[3]["shot"]["body_part"]["name"] = "Head"
        del events[4]["shot"]["body_part"]
        events[5]["location"] = [float("nan"), 40]
        del events[6]["shot"]["outcome"]
        events[7]["shot"]["outcome"]["name"] = "Unrecognized"
        self.events(events)
        _, audit = self.run_audit()
        c = audit["totals"]
        self.assertEqual((c["all_shots"], c["open_play"], c["foot"], c["base"]), (9, 6, 4, 1))
        self.assertEqual(sum(c["exclude_" + r] for r in ingest.REASONS), 8)
        self.assertEqual(c["all_unknown_outcomes"], 1)
        self.assertEqual(c["exclude_unknown_outcome"], 1)
        self.assertEqual(c["exclude_missing_outcome"], 1)

    def test_non_shot_events_and_zero_shot_matches(self):
        self.events([{"id": "synthetic-pass", "type": {"name": "Pass"}}])
        folder, audit = self.run_audit()
        c = audit["totals"]
        self.assertEqual((c["fixtures"], c["events_read"], c["all_shots"]), (1, 1, 0))
        self.assertIsNone(audit["rates"]["base_goal_prevalence"]["rate"])
        rows = list(csv.DictReader(io.StringIO((folder / "match-counts.csv").read_text())))
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["base"], "0")

    def test_missing_empty_invalid_and_ambiguous_frames_are_retained(self):
        frames = [None, [], "invalid", [keeper(True)], [keeper(), keeper()],
                  [keeper(), {**defender(), "teammate": "false"}], [keeper(), defender()]]
        events = []
        for i, frame in enumerate(frames):
            e = shot(str(i))
            e["shot"]["freeze_frame"] = frame
            events.append(e)
        self.events(events)
        folder, audit = self.run_audit()
        c = audit["totals"]
        self.assertEqual(c["base"], 7)
        self.assertEqual(c["position_usable"], 1)
        self.assertEqual([c["frame_" + x] for x in ("missing", "empty", "invalid", "valid")], [1, 1, 2, 3])
        self.assertEqual(c["keeper_multiple"], 1)
        self.assertEqual(c["unknown_player_roles"], 1)
        self.assertEqual(audit["rates"]["embedded_frame_invalid_rate"]["numerator"], 2)
        self.assertEqual(audit["rates"]["embedded_frame_invalid_rate"]["denominator"], 7)
        rows = [json.loads(x) for x in (folder / "shots.jsonl").read_text().splitlines()]
        self.assertIsNone(rows[0]["embedded_frame"]["visible_defenders"])
        self.assertEqual(audit["competitions"][-1]["selection"], "world-cup-2022")

    def test_coordinate_and_role_boundaries(self):
        for invalid in ([True, 40], [121, 40], [-1, 40], [100, 81], [100], [100, 40, 0], [float("inf"), 0]):
            with self.subTest(invalid=invalid):
                self.assertFalse(ingest.point(invalid))
        self.assertTrue(ingest.point([120, 80]))
        frame = ingest.inspect_frame([keeper(), {**defender(), "position": {"name": "Unknown"}}])
        self.assertEqual(frame["status"], "invalid")
        self.assertEqual(frame["visible_defenders"], 0)
        self.assertFalse(ingest.position_usable(frame))
        frame = ingest.inspect_frame([keeper(), {**defender(), "location": [121, 40]}])
        self.assertEqual(frame["invalid_locations"], 1)
        forward = {**defender(), "position": {"id": 23, "name": "Center Forward"}}
        frame = ingest.inspect_frame([keeper(), forward])
        self.assertEqual(frame["status"], "valid")
        self.assertEqual(frame["visible_defenders"], 1)

    def test_360_join_orphans_and_discrepancies_do_not_repair_shots(self):
        event = shot()
        event["shot"]["freeze_frame"] = None
        self.events([event, shot("second")])
        frame = [{"location": [117, 40], "teammate": False, "keeper": True, "actor": False}]
        self.source.write("data/three-sixty/1.json", [
            {"event_uuid": "synthetic-shot", "freeze_frame": frame},
            {"event_uuid": "second", "freeze_frame": frame},
            {"event_uuid": "orphan", "freeze_frame": frame}])
        self.source.commit()
        _, audit = self.run_audit()
        c = audit["totals"]
        self.assertEqual((c["base"], c["position_usable"]), (2, 1))
        self.assertEqual((c["all_360_joined"], c["base_360_valid"], c["orphan_360_events"]), (2, 2, 1))
        self.assertEqual((c["frame_comparisons"], c["frame_discrepancies"]), (1, 1))

    def test_duplicate_events_in_match_fail_with_occurrence_count(self):
        self.events([shot(), shot(), shot()])
        with self.assertRaisesRegex(ingest.AuditError, "occurrences=2"):
            self.run_audit()
        self.assertFalse(list(self.output.glob("*/manifest.json")))

    def test_duplicate_events_across_matches_fail(self):
        self.source.write("data/matches/43/106.json", [self.source.fixture(1), self.source.fixture(2)])
        self.source.write("data/events/2.json", [shot()])
        self.source.commit()
        with self.assertRaisesRegex(ingest.AuditError, "occurrences=1"):
            self.run_audit()

    def test_duplicate_360_ids_fail(self):
        self.source.write("data/three-sixty/1.json", [{"event_uuid": "same"}, {"event_uuid": "same"}])
        self.source.commit()
        with self.assertRaisesRegex(ingest.AuditError, "Duplicate 360 occurrences=1"):
            self.run_audit()

    def test_corrupt_optional_file_is_not_missing_coverage(self):
        p = self.source.root / "data/three-sixty/1.json"
        p.parent.mkdir(parents=True)
        p.write_text("invalid json")
        self.source.commit()
        with self.assertRaisesRegex(ingest.AuditError, "Malformed JSON"):
            self.run_audit()

    def test_tracked_but_unavailable_optional_file_fails(self):
        self.source.write("data/three-sixty/1.json", [])
        self.source.commit()
        (self.source.root / "data/three-sixty/1.json").unlink()
        with self.assertRaisesRegex(ingest.AuditError, "Missing/unreadable"):
            self.run_audit()

    def test_absent_optional_file_is_valid_missing_coverage(self):
        _, audit = self.run_audit()
        self.assertEqual(audit["totals"]["matches_with_360_file"], 0)
        self.assertEqual(audit["totals"]["base_360_frame_missing"], 1)

    def test_dirty_source_and_untracked_optional_file_fail(self):
        self.source.write("data/events/1.json", [shot("edited")])
        with self.assertRaisesRegex(ingest.AuditError, "differs from pinned"):
            self.run_audit()
        self.source.commit()
        self.source.write("data/three-sixty/1.json", [])
        with self.assertRaisesRegex(ingest.AuditError, "Untracked or absent"):
            self.run_audit()

    def test_incomplete_and_malformed_source_documents_fail(self):
        for content, message in (({}, "Expected array"), ([{}], "Missing/invalid event identifier")):
            with self.subTest(content=content):
                self.events(content)
                with self.assertRaisesRegex(ingest.AuditError, message):
                    self.run_audit()
        (self.source.root / "data/events/1.json").unlink()
        with self.assertRaisesRegex(ingest.AuditError, "Missing/unreadable"):
            self.run_audit()

    def test_ambiguous_metadata_and_contradictory_fixture_fail(self):
        p = self.source.root / "data/competitions.json"
        metadata = json.loads(p.read_text())
        self.source.write("data/competitions.json", metadata * 2)
        self.source.commit()
        with self.assertRaisesRegex(ingest.AuditError, "Ambiguous competition"):
            self.run_audit()
        self.source.write("data/competitions.json", metadata)
        fixture = self.source.fixture(1)
        fixture["competition"]["competition_id"] = 99
        self.source.write("data/matches/43/106.json", [fixture])
        self.source.commit()
        with self.assertRaisesRegex(ingest.AuditError, "contradictory fixture"):
            self.run_audit()

    def test_women_and_unavailable_competitions_are_not_selected(self):
        p = self.source.root / "data/competitions.json"
        metadata = json.loads(p.read_text())
        female = copy.deepcopy(metadata[0])
        female["competition_gender"] = "female"
        self.source.write("data/competitions.json", metadata + [female])
        self.source.commit()
        _, audit = self.run_audit()
        self.assertEqual(audit["totals"]["fixtures"], 1)
        self.assertEqual(sum(not c["available"] for c in audit["competitions"]), 9)

    def test_subset_is_explicit_and_cannot_pass_complete_screen(self):
        _, audit = self.run_audit(["world-cup-2022"])
        self.assertFalse(audit["complete_requested_cohort"])
        self.assertFalse(audit["feasibility"]["passes_planning_screen"])
        with self.assertRaisesRegex(ingest.AuditError, "known cohort"):
            self.run_audit(["not-a-competition"])

    def test_reconciliation_and_failure_preserve_complete_run(self):
        first, audit = self.run_audit()
        snapshots = {p.name: p.read_bytes() for p in first.iterdir()}
        self.events([shot(), shot()])
        with self.assertRaises(ingest.AuditError):
            self.run_audit()
        self.assertEqual(snapshots, {p.name: p.read_bytes() for p in first.iterdir()})
        self.assertFalse(list(self.output.glob(".staging-*")))
        broken = copy.deepcopy(audit["totals"])
        broken["base"] += 1
        with self.assertRaisesRegex(ingest.AuditError, "reconciliation"):
            ingest.validate_counts(broken)

    def test_modified_output_refuses_overwrite(self):
        first, _ = self.run_audit()
        (first / "shots.jsonl").write_text("corrupt")
        with self.assertRaisesRegex(ingest.AuditError, "immutable output differs"):
            self.run_audit()
        self.assertEqual((first / "shots.jsonl").read_text(), "corrupt")

    def test_source_mutation_before_finalization_prevents_publication(self):
        original = ingest.Source.recheck
        def mutate(source):
            (source.root / "data/events/1.json").write_text("[]")
            original(source)
        with patch.object(ingest.Source, "recheck", mutate):
            with self.assertRaisesRegex(ingest.AuditError, "changed during audit"):
                self.run_audit()
        self.assertFalse(list(self.output.glob("*/manifest.json")))

    def test_outputs_cannot_modify_source_checkout(self):
        with self.assertRaisesRegex(ingest.AuditError, "outside the source"):
            ingest.run(self.source.root, self.source.root / "derived")

    def test_project_public_and_tracked_paths_cannot_receive_source_rows(self):
        project = Path(ingest.__file__).resolve().parents[2]
        for output in (project / "public" / "raw-shots", project / "reports" / "raw-shots"):
            with self.subTest(output=output):
                with self.assertRaisesRegex(ingest.AuditError, "under ignored data/derived"):
                    ingest.run(self.source.root, output)
                self.assertFalse(output.exists())

    def test_extractor_change_prevents_finalization(self):
        original = ingest.sha256
        code = Path(ingest.__file__).read_bytes()
        observations = 0
        def changed(data):
            nonlocal observations
            if data == code:
                observations += 1
                if observations > 1:
                    return "changed-extractor"
            return original(data)
        with patch.object(ingest, "sha256", changed):
            with self.assertRaisesRegex(ingest.AuditError, "Extractor changed"):
                self.run_audit()
        self.assertFalse(list(self.output.glob("*/manifest.json")))

    def test_planning_screen_capacity_is_not_a_training_split(self):
        total = ingest.new_counts()
        total.update(position_usable=12000, position_usable_goals=1200,
                     position_usable_matches=240)
        comps = [{"competition_id": i, "counts": {"position_usable": 4000}} for i in range(3)]
        matches = [{"match_id": i + 1, "position_usable": 50,
                    "position_usable_goals": 5} for i in range(240)]
        result = ingest.feasibility(total, comps, matches, True)
        self.assertTrue(result["passes_planning_screen"])
        self.assertEqual(result["diagnostic_holdout"]["shots"], 2000)
        self.assertFalse(ingest.feasibility(total, comps, matches, False)["passes_planning_screen"])

    def test_missing_event_type_and_invalid_names_are_handled(self):
        self.events([{"id": "bad-type"}])
        with self.assertRaisesRegex(ingest.AuditError, "Missing/invalid event type"):
            self.run_audit()
        event = shot()
        event["shot"]["outcome"]["name"] = []
        self.events([event])
        _, audit = self.run_audit()
        self.assertEqual(audit["totals"]["exclude_missing_outcome"], 1)

    def test_corrupt_json_and_duplicate_keys_fail(self):
        for value in ('not json', '[{"id":"one","id":"two"}]'):
            with self.subTest(value=value):
                (self.source.root / "data/events/1.json").write_text(value)
                self.source.commit()
                with self.assertRaisesRegex(ingest.AuditError, "Malformed JSON"):
                    self.run_audit()

    def test_duplicate_fixtures_fail(self):
        self.source.write("data/matches/43/106.json", [self.source.fixture(1)] * 2)
        self.source.commit()
        with self.assertRaisesRegex(ingest.AuditError, "duplicate or contradictory"):
            self.run_audit()

    def test_invalid_metadata_cannot_masquerade_as_unavailable_cohort(self):
        self.source.write("data/competitions.json", [{"competition_name": "FIFA World Cup"}])
        self.source.commit()
        with self.assertRaisesRegex(ingest.AuditError, "Invalid competition metadata"):
            self.run_audit()

    def test_fixture_and_event_order_do_not_change_extracted_corpus(self):
        self.events([shot("z-last"), shot("a-first", "Saved")])
        first, _ = self.run_audit()
        corpus = (first / "shots.jsonl").read_bytes()
        self.events([shot("a-first", "Saved"), shot("z-last")])
        second, _ = self.run_audit()
        self.assertEqual(corpus, (second / "shots.jsonl").read_bytes())
        self.assertNotEqual(first, second)  # Provenance changes with the source revision.

    def test_invalid_360_roles_and_locations_are_counted(self):
        frame = ingest.inspect_frame([
            {"location": [117, 40], "teammate": False, "keeper": True, "actor": False},
            {"location": [110, 40], "teammate": False, "keeper": "false", "actor": False},
            {"location": [float("inf"), 40], "teammate": False, "keeper": False, "actor": False},
        ], True)
        self.assertEqual(frame["status"], "invalid")
        self.assertEqual(frame["invalid_entries"], 2)
        self.assertEqual(frame["unknown_roles"], 1)
        self.assertEqual(frame["invalid_locations"], 1)
        self.assertFalse(ingest.position_usable(frame))


if __name__ == "__main__":
    unittest.main()
