import copy
import json
import math
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from features import (FEATURE_NAMES, VERSION, extract_metric_features,
                      extract_statsbomb_features, normalize_source_point)
from extract_features import PROJECT, run
from ingest_statsbomb import AuditError, canonical, sha256

GOLDEN = json.loads((PROJECT / "tests/fixtures/shot-features-v1.json").read_text())


def player(location=(116, 40), teammate=False, keeper=True):
    return {"location": list(location), "teammate": teammate, "keeper": keeper,
            "position": "Goalkeeper" if keeper else "Center Back"}


def row(event_id="synthetic-a"):
    return {"schema_version": 1, "competition_id": 1, "season_id": 1, "match_id": 1,
            "event_id": event_id, "outcome": "Goal", "is_goal": 1, "body_part": "Left Foot",
            "location": [96, 40], "embedded_frame": {"status": "valid", "players": [
                player(), player((104, 40), keeper=False), player((100, 60), teammate=True, keeper=False)]},
            "position_usable": True}


def write_input(directory, rows):
    directory.mkdir(parents=True, exist_ok=True)
    shots = "".join(canonical(r) for r in rows).encode()
    audit = canonical({"totals": {"base": len(rows), "base_goals": sum(r["is_goal"] for r in rows)}}).encode()
    manifest = {"schema_version": 1, "complete": True, "source_url": "synthetic-test-only",
                "source_revision": "synthetic", "extractor_version": "1.0.0", "extractor_sha256": "synthetic",
                "selection": ["synthetic"], "outputs": {"shots.jsonl": sha256(shots), "audit.json": sha256(audit)}}
    manifest["run_id"] = sha256(canonical(manifest).encode())
    (directory / "shots.jsonl").write_bytes(shots)
    (directory / "audit.json").write_bytes(audit)
    (directory / "manifest.json").write_text(canonical(manifest))


class MetricTests(unittest.TestCase):
    def test_golden_and_order(self):
        for fixture in GOLDEN:
            with self.subTest(fixture=fixture["name"]):
                result = extract_metric_features(fixture["scene"])
                self.assertEqual(result["status"], fixture["expected"]["status"])
                if result["status"] == "ok":
                    self.assertEqual(tuple(result["features"]), FEATURE_NAMES)
                    self.assertEqual(result["vector"], list(result["features"].values()))
                    self.assertTrue(all(math.isfinite(v) for v in result["vector"]))
                    for name, expected in fixture["expected"].get("features", {}).items():
                        self.assertAlmostEqual(result["features"][name], expected, delta=1e-9)
                else:
                    self.assertEqual(result["reason"], fixture["expected"]["reason"])

    def test_analytic_oracles(self):
        result = extract_metric_features(GOLDEN[0]["scene"])
        self.assertAlmostEqual(result["vector"][1], 2 * math.degrees(math.atan(3.66 / 21)))
        scene = copy.deepcopy(GOLDEN[0]["scene"])
        scene["defenders"] = []
        self.assertEqual(extract_metric_features(scene)["vector"][5], math.sqrt(105 ** 2 + 68 ** 2))

    def test_nonfinite_boolean_and_missing_inputs(self):
        for value in (None, True, "84", math.nan, math.inf, -1, 106, 10 ** 400):
            scene = copy.deepcopy(GOLDEN[0]["scene"])
            scene["shooter"]["x"] = value
            self.assertEqual(extract_metric_features(scene)["reason"], "invalid_shooter")
        for changes, reason in (({"goalkeepers": []}, "missing_goalkeeper"),
                                ({"defenders": None}, "missing_defenders"),
                                ({"contract_version": "v2"}, "contract_version"),
                                ({"shot_type": "penalty"}, "penalty_separate_route")):
            self.assertEqual(extract_metric_features({**GOLDEN[0]["scene"], **changes})["reason"], reason)

    def test_source_scaling_and_physical_posts(self):
        self.assertEqual(normalize_source_point([96, 40]), {"x": 84, "y": 34})
        self.assertEqual(normalize_source_point([0, 0]), {"x": 0, "y": 0})
        self.assertAlmostEqual(normalize_source_point([120, 36])["y"], 30.6)
        self.assertNotEqual(normalize_source_point([120, 36])["y"], 34 - 7.32 / 2)
        for value in (None, [True, 40], [120, math.nan], [120, math.inf], [121, 40], [1, 2, 3], [10 ** 400, 40]):
            self.assertIsNone(normalize_source_point(value))


class AdapterTests(unittest.TestCase):
    def test_source_and_equivalent_metric_scene(self):
        source = row()
        result = extract_statsbomb_features(source)
        metric = {"contract_version": VERSION, "shot_type": "open-play", "shooter": {"x": 84, "y": 34},
                  "goalkeepers": [{"x": 101.5, "y": 34}], "defenders": [{"x": 91, "y": 34}], "observation": "embedded-frame"}
        self.assertEqual(result, extract_metric_features(metric))
        self.assertEqual(result["metadata"]["defender_visibility"], "partial")
        self.assertEqual(result["vector"][3], 1)
        # Diagnostic counters and 360 records never replace the actual embedded observations.
        source["embedded_frame"]["opponent_goalkeepers"] = 0
        source["separate_360"] = {"players": [player((0, 0))]}
        self.assertEqual(extract_statsbomb_features(source), result)

    def test_zero_defenders_is_not_empty_or_missing_frame(self):
        source = row()
        source["embedded_frame"]["players"] = [player()]
        self.assertEqual(extract_statsbomb_features(source)["vector"][3], 0)
        for frame, reason in ((None, "missing_frame"), ({"status": "missing"}, "missing_frame"),
                              ({"status": "empty", "players": []}, "empty_frame"),
                              ({"status": "invalid"}, "invalid_frame"),
                              ({"status": []}, "invalid_frame"),
                              ({"status": "valid", "players": []}, "empty_frame")):
            self.assertEqual(extract_statsbomb_features({**source, "embedded_frame": frame})["reason"], reason)

    def test_keeper_and_role_failures(self):
        for players, reason in (([player(keeper=False)], "missing_goalkeeper"),
                                ([player(), player()], "multiple_goalkeepers"),
                                ([{**player(), "teammate": None}], "invalid_role"),
                                ([{**player(), "position": "Unknown"}], "invalid_role"),
                                ([{**player(), "position": []}], "invalid_role"),
                                ([{**player(), "keeper": False}], "invalid_role"),
                                ([player((121, 40))], "invalid_player_location")):
            source = row()
            source["embedded_frame"]["players"] = players
            result = extract_statsbomb_features(source)
            self.assertEqual(result["reason"], reason)
            self.assertNotIn("vector", result)

    def test_schema_population_and_boundary_rejections(self):
        for changes, reason in (({"schema_version": True}, "ingestion_schema_version"),
                                ({"schema_version": 2}, "ingestion_schema_version"),
                                ({"body_part": "Head"}, "unsupported_body_part"),
                                ({"shot_type": "Penalty"}, "unsupported_shot_type"),
                                ({"location": [120, 40]}, "goal_line_shot")):
            self.assertEqual(extract_statsbomb_features({**row(), **changes})["reason"], reason)


class MaterializationTests(unittest.TestCase):
    def test_reproducibility_aggregation_and_private_rows(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            a, b, rejected = row("a"), row("b"), row("c")
            b.update(outcome="Saved", is_goal=0, match_id=2, competition_id=2)
            b["embedded_frame"]["players"] = [player()]
            rejected["embedded_frame"]["players"] = [player(keeper=False)]
            write_input(root / "input", [b, rejected, a])
            first, audit = run(root / "input", root / "output")
            second, _ = run(root / "input", root / "output-again")
            self.assertEqual(first.name, second.name)
            for p in first.iterdir():
                self.assertEqual(p.read_bytes(), (second / p.name).read_bytes())
            self.assertEqual(run(root / "input", root / "output")[0], first)
            totals = audit["totals"]
            self.assertEqual((totals["input_shots"], totals["accepted_shots"], totals["rejected_shots"]), (3, 2, 1))
            self.assertEqual((totals["input_goals"], totals["accepted_goals"], totals["rejected_goals"]), (2, 1, 1))
            self.assertEqual(totals["reasons"], {"missing_goalkeeper": 1})
            self.assertEqual(totals["zero_defender_sentinel"], 1)
            self.assertNotIn("event_id", canonical(audit))
            exported = [json.loads(line) for line in (first / "features.jsonl").read_text().splitlines()]
            self.assertEqual([r["event_id"] for r in exported], ["a", "b"])
            self.assertNotIn("location", exported[0])
            self.assertEqual(exported[0]["is_goal"], 1)

    def test_hash_mismatch_and_no_partial_run(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write_input(root / "input", [row()])
            (root / "input/shots.jsonl").write_text("corrupted")
            with self.assertRaisesRegex(AuditError, "hash mismatch"):
                run(root / "input", root / "output")
            self.assertFalse((root / "output").exists())

    def test_duplicate_ids_bad_labels_and_schema_are_fatal(self):
        for rows in ([row(), row()], [{**row(), "is_goal": 0}], [{**row(), "schema_version": 2}], [{**row(), "match_id": True}]):
            with self.subTest(rows=len(rows)), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                write_input(root / "input", rows)
                with self.assertRaises(AuditError):
                    run(root / "input", root / "output")
                self.assertFalse((root / "output").exists())

    def test_output_protection_and_immutable_collision(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write_input(root / "input", [row()])
            for output in (root / "input", PROJECT / "docs/reports/private-features"):
                with self.assertRaises(AuditError):
                    run(root / "input", output)
            first, _ = run(root / "input", root / "output")
            (first / "features.jsonl").write_text("tampered")
            with self.assertRaisesRegex(AuditError, "immutable"):
                run(root / "input", root / "output")
            self.assertEqual(list((root / "output").iterdir()), [first])

    def test_counts_and_manifest_identity_are_verified(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write_input(root / "input", [row()])
            manifest_path = root / "input/manifest.json"
            manifest = json.loads(manifest_path.read_text())
            manifest["source_revision"] = "tampered"
            manifest_path.write_text(canonical(manifest))
            with self.assertRaisesRegex(AuditError, "identity"):
                run(root / "input", root / "output")
            write_input(root / "input", [row()])
            audit_path = root / "input/audit.json"
            audit = {"totals": {"base": 2, "base_goals": 1}}
            audit_path.write_text(canonical(audit))
            manifest = json.loads(manifest_path.read_text())
            manifest["outputs"]["audit.json"] = sha256(audit_path.read_bytes())
            del manifest["run_id"]
            manifest["run_id"] = sha256(canonical(manifest).encode())
            manifest_path.write_text(canonical(manifest))
            with self.assertRaisesRegex(AuditError, "reconcile"):
                run(root / "input", root / "output")
            self.assertEqual(list((root / "output").iterdir()), [])


if __name__ == "__main__":
    unittest.main()
