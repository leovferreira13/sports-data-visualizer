import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

from jsonschema import ValidationError

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from compare_training_runs import compare_training, main, verified_side
from ingest_statsbomb import AuditError, canonical, sha256


class ComparisonDiagnosticsTests(unittest.TestCase):
    def write_run(self, root, phase, filenames):
        root.mkdir()
        outputs = {}
        for name in filenames:
            contents = b"{}"
            (root / name).write_bytes(contents)
            outputs[name] = sha256(contents)
        manifest = {"schema_version": 1, "complete": True, "phase": phase, "outputs": outputs}
        manifest["run_id"] = sha256(canonical(manifest).encode())
        (root / "manifest.json").write_text(json.dumps(manifest))

    def test_verified_preparation_directory_reports_side_and_phase(self):
        with tempfile.TemporaryDirectory() as directory:
            left, right = Path(directory) / "left", Path(directory) / "right"
            self.write_run(left, "training", ["evaluation.json"])
            self.write_run(right, "preparation", ["preparation-summary.json"])
            with self.assertRaisesRegex(AuditError, "right run: expected training phase, found preparation"):
                compare_training(left, right)

    def test_verified_training_inventory_mismatch_lists_both_directions(self):
        with tempfile.TemporaryDirectory() as directory:
            left, right = Path(directory) / "left", Path(directory) / "right"
            self.write_run(left, "training", ["evaluation.json", "selected-model.json"])
            self.write_run(right, "training", ["evaluation.json", "full_logistic.json"])
            with self.assertRaises(AuditError) as raised:
                compare_training(left, right)
            self.assertEqual(str(raised.exception), "Training inventories differ: left-only=[selected-model.json]; right-only=[full_logistic.json]")

    def run_failure(self, error):
        stream = io.StringIO()
        with patch("sys.argv", ["compare_training_runs.py", "--left-dir", "left", "--right-dir", "right"]), \
                patch("compare_training_runs.compare_training", side_effect=error), contextlib.redirect_stderr(stream):
            self.assertEqual(main(), 1)
        return stream.getvalue()

    def test_reports_integrity_provenance_and_numeric_failure_without_suppressing_reason(self):
        for reason in ("Run directory is missing or not a directory", "Comparison requires distinct runs",
                       "Scientific provenance or decision differs: code_sha256",
                       "Numeric reproduction tolerance failed: evaluation.json.experiments[1].variants[0].metrics.log_loss",
                       "Output hash mismatch: validation-predictions.json"):
            self.assertEqual(self.run_failure(AuditError(reason)), f"FAIL: {reason}\n")

    def test_missing_manifest_identifies_side_without_disclosing_local_path(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(AuditError, r"right run: Run must contain a regular manifest.json"):
                verified_side(directory, "right")

    def test_schema_and_filesystem_failures_do_not_print_private_content(self):
        error = ValidationError("PRIVATE_SHOT_VALUES", validator="type", path=["parameters", "scale"])
        text = self.run_failure(error)
        self.assertIn("parameters.scale (type)", text)
        self.assertNotIn("PRIVATE_SHOT_VALUES", text)
        text = self.run_failure(FileNotFoundError("PRIVATE_LOCAL_PATH"))
        self.assertIn("FileNotFoundError", text)
        self.assertNotIn("PRIVATE_LOCAL_PATH", text)


if __name__ == "__main__":
    unittest.main()
