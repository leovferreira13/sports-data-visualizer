import contextlib
import io
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

from jsonschema import ValidationError

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from compare_training_runs import main, verified_side
from ingest_statsbomb import AuditError


class ComparisonDiagnosticsTests(unittest.TestCase):
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
