import copy
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from check_browser_inference import check, code_hashes, selected_candidate, verify
from compare_runs import compare_runs
from ingest_statsbomb import AuditError, canonical, sha256
from model_export import seal
from run_io import PROJECT, PROTOCOL_PATH, publish, read_json


def fixture():
    return read_json(PROJECT / "tests/fixtures/inference-models.json")[6]["envelope"]


def synthetic_training(root):
    """Invented integrity-only run, never a claim of actual training/quality evidence."""
    envelope = fixture()
    envelope["provenance"]["protocol_sha256"] = sha256(PROTOCOL_PATH.read_bytes())
    envelope = seal(envelope)
    decision = {"status": "frozen_candidate", "test_status": "unopened", "selected_model": envelope["model_version"],
                "selected_artifact_id": envelope["artifact_id"]}
    return publish(root, PROJECT / "tests/fixtures", "training", {
        "selected-model.json": envelope, envelope["model_version"] + ".json": envelope,
        "selection.json": decision, "evaluation.json": {"selection": decision}, "protocol.json": read_json(PROTOCOL_PATH),
    }, {**envelope["provenance"], "selected_model": envelope["model_version"],
        "feature_contract_sha256": envelope["feature_contract_sha256"]}, lambda: None)


def resign(root):
    m = read_json(root / "manifest.json")
    m.pop("run_id")
    m["outputs"] = {n: sha256((root / n).read_bytes()) for n in m["outputs"]}
    m["run_id"] = sha256(canonical(m).encode())
    (root / "manifest.json").write_text(canonical(m))


class BrowserInferenceTests(unittest.TestCase):
    def test_independent_reference_parity_for_all_parameter_kinds_and_calibrators(self):
        for f in read_json(PROJECT / "tests/fixtures/inference-models.json"):
            with self.subTest(model=f["name"]):
                result = verify(f["envelope"])
                self.assertEqual(result["status"], "pass")
                self.assertGreater(result["case_counts"]["learned"], 150)
                self.assertGreaterEqual(result["case_counts"]["penalty"], 3)
                self.assertGreater(result["case_counts"]["unsupported"], 5)
                self.assertGreater(result["case_counts"]["invalid_vectors"], 0)
                self.assertLessEqual(result["max_probability_error"], result["tolerance"])

    def test_complete_candidate_verification_and_repeat_report_comparison(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            training = synthetic_training(root / "training")
            self.assertEqual(selected_candidate(training)[2]["artifact_id"], read_json(training / "selected-model.json")["artifact_id"])
            left = check(training, root / "first")
            right = check(training, root / "repeat")
            self.assertEqual(compare_runs(left, right)["run_id"], left.name)
            report = read_json(left / "parity.json")
            self.assertFalse(report["held_out_labels_accessed"])
            self.assertFalse(report["parameters_published"])
            self.assertEqual(report["training_run_id"], training.name)
            self.assertEqual(set(p.name for p in left.iterdir()), {"parity.json", "manifest.json"})
            self.assertNotIn('"parameters":', canonical(report))

    def test_wrong_phase_no_candidate_selection_drift_and_hash_failures(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            training = synthetic_training(root / "training")
            manifest = read_json(training / "manifest.json")
            manifest["phase"] = "preparation"
            (training / "manifest.json").write_text(canonical(manifest))
            resign(training)
            with self.assertRaisesRegex(AuditError, "Expected training phase"):
                selected_candidate(training)
            manifest["phase"] = "training"
            (training / "manifest.json").write_text(canonical(manifest))
            resign(training)
            selected = read_json(training / "selection.json")
            selected["selected_artifact_id"] = "a" * 64
            (training / "selection.json").write_text(canonical(selected))
            resign(training)
            with self.assertRaisesRegex(AuditError, "disagree"):
                selected_candidate(training)
            (training / "selected-model.json").write_text("{}")
            with self.assertRaisesRegex(AuditError, "Output hash mismatch"):
                selected_candidate(training)
            no_candidate = publish(root / "none", PROJECT / "tests/fixtures", "training", {
                "selection.json": {"status": "no_candidate"}}, {}, lambda: None)
            with self.assertRaisesRegex(AuditError, "No complete frozen candidate"):
                selected_candidate(no_candidate)

    def test_detects_input_code_change_without_publishing_complete_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            codes = code_hashes()
            with patch("check_browser_inference.code_hashes", side_effect=[codes, {**codes, "changed": "a" * 64}]), \
                    patch("check_browser_inference.verify", return_value={"status": "pass"}):
                with self.assertRaisesRegex(AuditError, "changed during verification"):
                    check(None, Path(tmp) / "out", synthetic=True)
            self.assertEqual(list((Path(tmp) / "out").iterdir()), [])

    def test_rejects_runner_missing_probability_cases_without_completed_evidence(self):
        with patch("check_browser_inference.subprocess.run") as runner:
            runner.return_value.returncode = 0
            runner.return_value.stdout = canonical({"loaded": {"status": "ready"}, "cases": []})
            with self.assertRaisesRegex(AuditError, "inventory differs"):
                verify(fixture())


if __name__ == "__main__":
    unittest.main()
