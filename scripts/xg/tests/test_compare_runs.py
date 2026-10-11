import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from compare_runs import compare_runs
from ingest_statsbomb import AuditError, canonical, sha256


def make_run(directory, feature=True, data=b"synthetic\n"):
    directory.mkdir(parents=True, exist_ok=True)
    files = {"feature-audit.json": b"{}\n", "features.jsonl": data} if feature else {
        "audit.json": b"{}\n", "shots.jsonl": data, "match-counts.csv": b"synthetic\n"}
    for name, contents in files.items():
        (directory / name).write_bytes(contents)
    manifest = {"schema_version": 1, "complete": True, "source_revision": "synthetic",
                "outputs": {name: sha256(b) for name, b in files.items()}}
    manifest["run_id"] = sha256(canonical(manifest).encode())
    (directory / "manifest.json").write_text(canonical(manifest))


class CompareRunsTests(unittest.TestCase):
    def test_complete_ingestion_and_feature_runs(self):
        for feature in (False, True):
            with self.subTest(feature=feature), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                make_run(root / "a", feature)
                make_run(root / "b", feature)
                result = compare_runs(root / "a", root / "b")
                self.assertIn("manifest.json", result["files"])
                self.assertEqual(len(result["files"]), 3 if feature else 4)

    def test_same_directory_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            make_run(Path(tmp))
            with self.assertRaisesRegex(AuditError, "distinct"):
                compare_runs(tmp, tmp)

    def test_two_internally_valid_different_runs_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_run(root / "a")
            make_run(root / "b", data=b"different\n")
            with self.assertRaisesRegex(AuditError, "differ byte"):
                compare_runs(root / "a", root / "b")

    def test_identical_but_corrupt_runs_are_not_accepted(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name in ("a", "b"):
                make_run(root / name)
                (root / name / "features.jsonl").write_text("corrupt")
            with self.assertRaisesRegex(AuditError, "hash mismatch"):
                compare_runs(root / "a", root / "b")

    def test_missing_extra_directory_and_symlink_outputs(self):
        for kind in ("missing", "extra", "directory", "symlink"):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                make_run(root / "a")
                make_run(root / "b")
                p = root / "b/features.jsonl"
                if kind == "extra":
                    (root / "b/extra").write_text("extra")
                else:
                    p.unlink()
                    if kind == "directory":
                        p.mkdir()
                    elif kind == "symlink":
                        p.symlink_to(root / "a/features.jsonl")
                with self.assertRaises(AuditError):
                    compare_runs(root / "a", root / "b")

    def test_manifest_identity_completeness_and_path_safety(self):
        for change in ({"run_id": "invalid"}, {"complete": False}, {"outputs": {"../secret": "0" * 64}},
                       {"outputs": {"secret\\path": "0" * 64}}, {"outputs": {"manifest.json": "0" * 64}}):
            with self.subTest(change=change), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                make_run(root / "a")
                make_run(root / "b")
                p = root / "b/manifest.json"
                m = json.loads(p.read_text())
                m.update(change)
                if "run_id" not in change:
                    m.pop("run_id")
                    m["run_id"] = sha256(canonical(m).encode())
                p.write_text(canonical(m))
                with self.assertRaises(AuditError):
                    compare_runs(root / "a", root / "b")

    def test_cli_exit_status_and_read_only_behavior(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name in ("a", "b"):
                make_run(root / name, data=b"s" * (1024 * 1024 + 1))
            before = {str(p): p.read_bytes() for p in root.rglob("*") if p.is_file()}
            command = [sys.executable, str(Path(__file__).resolve().parents[1] / "compare_runs.py"),
                       "--left-dir", str(root / "a"), "--right-dir", str(root / "b")]
            passed = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(passed.returncode, 0, passed.stderr)
            self.assertIn("PASS: complete comparison", passed.stdout)
            self.assertEqual(before, {str(p): p.read_bytes() for p in root.rglob("*") if p.is_file()})
            (root / "b/features.jsonl").write_text("corrupt")
            failed = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(failed.returncode, 1)
            self.assertIn("FAIL:", failed.stderr)


if __name__ == "__main__":
    unittest.main()
