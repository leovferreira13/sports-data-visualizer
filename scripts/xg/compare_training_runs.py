#!/usr/bin/env python3
"""Compare verified complete training runs, with predeclared numeric tolerances."""

import argparse
from pathlib import Path
import sys

from jsonschema import ValidationError

from compare_runs import verified_run
from ingest_statsbomb import AuditError
from run_io import read_json

DERIVED_IDS = {"artifact_id", "selected_artifact_id", "evidence_id", "preparation_run_id"}


def compare_json(a, b, tolerance, path="root"):
    if isinstance(a, bool) or isinstance(b, bool):
        if type(a) is not type(b) or a != b:
            raise AuditError(f"Reproduction differs: {path}")
    elif type(a) is int or type(b) is int:
        # Counts, labels and tree topology must be exact; floats have their own tolerance.
        if type(a) is not type(b) or a != b:
            raise AuditError(f"Reproduction differs: {path}")
    elif isinstance(a, float) and isinstance(b, float):
        if abs(a - b) > tolerance:
            raise AuditError(f"Numeric reproduction tolerance failed: {path}")
    elif isinstance(a, dict) and isinstance(b, dict):
        if set(a) != set(b):
            raise AuditError(f"Reproduction fields differ: {path}")
        for k in sorted(a):
            if k not in DERIVED_IDS:
                compare_json(a[k], b[k], tolerance, f"{path}.{k}")
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            raise AuditError(f"Reproduction lengths differ: {path}")
        for i, (x, y) in enumerate(zip(a, b)):
            compare_json(x, y, tolerance, f"{path}[{i}]")
    elif type(a) is not type(b) or a != b:
        raise AuditError(f"Reproduction differs: {path}")


def verified_side(directory, side):
    try:
        return verified_run(directory)
    except AuditError as exc:
        raise AuditError(f"{side} run: {exc}") from exc
    except OSError as exc:
        filename = "manifest.json" if exc.filename and Path(exc.filename).name == "manifest.json" else "a declared output"
        raise AuditError(f"{side} run: cannot read {filename} ({type(exc).__name__})") from exc


def compare_training(left_dir, right_dir):
    if Path(left_dir).resolve() == Path(right_dir).resolve():
        raise AuditError("Comparison requires distinct runs")
    left, lm, lf = verified_side(left_dir, "left")
    right, rm, rf = verified_side(right_dir, "right")
    if lm.get("phase") != "training" or rm.get("phase") != "training" or lf != rf:
        raise AuditError("Expected matching complete training inventories")
    for key in ("code_sha256", "dependencies", "protocol_sha256", "feature_run_id", "source_revision",
                "split_sha256", "feature_contract_sha256", "selected_model"):
        if lm[key] != rm[key]:
            if isinstance(lm[key], dict) and isinstance(rm[key], dict):
                changed = sorted(name for name in set(lm[key]) | set(rm[key]) if lm[key].get(name) != rm[key].get(name))
                raise AuditError(f"Scientific provenance differs: {key}.{changed[0]}")
            raise AuditError(f"Scientific provenance or decision differs: {key}")
    config = read_json(left / "protocol.json")
    from model_export import validate_envelope
    from report_training import render_report, validate_evaluation
    byte_differences = []
    for name in sorted(lf - {"manifest.json"}):
        a, b = (left / name).read_bytes(), (right / name).read_bytes()
        if a != b:
            byte_differences.append(name)
        if name == "methodology.md":
            for directory, contents in ((left, a), (right, b)):
                if contents != render_report(read_json(directory / "evaluation.json")):
                    raise AuditError("Methodology differs from its own evidence")
            continue
        ja, jb = read_json(left / name), read_json(right / name)
        if name == "evaluation.json":
            validate_evaluation(ja)
            validate_evaluation(jb)
        if isinstance(ja, dict) and "parameters" in ja:
            validate_envelope(ja)
            validate_envelope(jb)
        tolerance = config["tolerances"]["reproduction_probability"] if name == "validation-predictions.json" else config["tolerances"]["reproduction_metric"]
        # Export check errors are bounded independently, not a required identical error residual.
        if name == "evaluation.json":
            ja, jb = dict(ja), dict(jb)
            for evaluation in (ja, jb):
                for check in evaluation["export_checks"].values():
                    if check["absolute_probability_error"] > check["tolerance"]:
                        raise AuditError("Stored export parity check failed")
            ja["export_checks"] = {k: {kk: vv for kk, vv in v.items() if kk != "absolute_probability_error"} for k, v in ja["export_checks"].items()}
            jb["export_checks"] = {k: {kk: vv for kk, vv in v.items() if kk != "absolute_probability_error"} for k, v in jb["export_checks"].items()}
        compare_json(ja, jb, tolerance, name)
    if verified_run(left)[1] != lm or verified_run(right)[1] != rm:
        raise AuditError("Run changed during comparison")
    return {"status": "pass", "files_verified": len(lf), "byte_differences": byte_differences,
            "python_versions": [lm["python_version"], rm["python_version"]],
            "run_ids": [lm["run_id"], rm["run_id"]]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--left-dir", type=Path, required=True)
    parser.add_argument("--right-dir", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = compare_training(args.left_dir, args.right_dir)
    except AuditError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    except OSError as exc:
        # The failure category is useful; filenames may disclose local/private paths.
        print(f"FAIL: cannot read a complete run ({type(exc).__name__})", file=sys.stderr)
        return 1
    except ValidationError as exc:
        path = ".".join(str(part) for part in exc.absolute_path) or "root"
        print(f"FAIL: invalid artifact schema at {path} ({exc.validator})", file=sys.stderr)
        return 1
    except (KeyError, TypeError, ValueError):
        print("FAIL: malformed run metadata or numeric content", file=sys.stderr)
        return 1
    print(f"PASS: {result['files_verified']} files verified; {len(result['byte_differences'])} files differ byte for byte")
    print("PASS: scientific configuration, decisions and numeric tolerances agree")
    return 0


if __name__ == "__main__":
    sys.exit(main())
