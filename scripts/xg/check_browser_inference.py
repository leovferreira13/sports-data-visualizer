#!/usr/bin/env python3
"""Verify a frozen local candidate against the browser-safe TypeScript bundle."""

import argparse
import copy
from pathlib import Path
import subprocess
import sys

import numpy as np
from jsonschema import ValidationError

from compare_runs import verified_run
from features import CONTRACT_PATH, extract_metric_features
from ingest_statsbomb import AuditError, canonical, sha256
from model_export import predict_envelope, validate_envelope
from run_io import PROJECT, PROTOCOL_PATH, publish, read_json
from scene_evaluation import scenes

INFERENCE_PATH = PROJECT / "model/inference-contract.json"
RUNNER = PROJECT / "scripts/xg/browser_inference_runner.mjs"


def code_hashes():
    paths = ["lib/model.ts", "lib/predict.ts", "lib/features.ts", "lib/geometry.ts", "lib/scenario.ts",
             "model/model-artifact.schema.json", "model/feature-contract.json", "model/inference-contract.json",
             "scripts/xg/check_browser_inference.py", "scripts/xg/browser_inference_runner.mjs",
             "scripts/xg/inference_bridge.ts", "scripts/xg/model_export.py", "scripts/xg/features.py",
             "scripts/xg/scene_evaluation.py", "scripts/xg/run_io.py", "scripts/xg/compare_runs.py",
             "scripts/xg/ingest_statsbomb.py", "scripts/xg/requirements.lock", "package-lock.json",
             "tests/fixtures/training-presets.json", "tests/fixtures/inference-models.json"]
    return {p: sha256((PROJECT / p).read_bytes()) for p in paths}


def selected_candidate(directory):
    root, manifest, names = verified_run(directory)
    if manifest.get("phase") != "training":
        raise AuditError("Expected training phase; use the completed train_models.py output, not preparation")
    required = {"selected-model.json", "selection.json", "protocol.json", "evaluation.json"}
    if not required <= names:
        raise AuditError("No complete frozen candidate; selected-model.json and selection evidence are required")
    selection, envelope = read_json(root / "selection.json"), read_json(root / "selected-model.json")
    validate_envelope(envelope)
    if (selection.get("status") != "frozen_candidate" or selection.get("test_status") != "unopened"
            or selection.get("selected_artifact_id") != envelope["artifact_id"]
            or selection.get("selected_model") != envelope["model_version"]
            or manifest.get("selected_model") != envelope["model_version"]
            or read_json(root / "evaluation.json").get("selection") != selection):
        raise AuditError("Selected envelope, decision and training evidence disagree")
    selected_name = envelope["model_version"] + ".json"
    if selected_name not in names or (root / selected_name).read_bytes() != (root / "selected-model.json").read_bytes():
        raise AuditError("Selected candidate differs from its frozen experiment envelope")
    # Training identifies the canonical protocol, not the formatted source file.
    # The feature contract intentionally uses its source-file byte identity.
    frozen_protocol = canonical(read_json(PROTOCOL_PATH)).encode()
    if (root / "protocol.json").read_bytes() != frozen_protocol:
        raise AuditError("Frozen protocol content differs from the committed training protocol")
    if manifest.get("protocol_sha256") != sha256(frozen_protocol):
        raise AuditError("Frozen protocol identity differs from its canonical training digest")
    if manifest.get("feature_contract_sha256") != sha256(CONTRACT_PATH.read_bytes()):
        raise AuditError("Frozen feature contract byte identity differs from the committed contract")
    for key, value in envelope["provenance"].items():
        if manifest.get(key) != value:
            raise AuditError(f"Envelope and training provenance disagree: {key}")
    return root, manifest, envelope


def cases_for(envelope):
    cases = [{"name": f["name"], "mode": "metric", "value": f["scene"]} for f in scenes()]
    for i, change in enumerate(({"shot_type": "header"}, {"defenders": None},
                                {"goalkeepers": [None]}, {"goalkeepers": [{"x": 100, "y": 34}] * 2},
                                {"defenders": [{"x": 90, "y": 34}] * 11}, {"contract_version": "v2"})):
        cases.append({"name": f"invalid_{i}", "mode": "metric", "value": {**copy.deepcopy(cases[0]["value"]), **change}})
    cases.append({"name": "null_scene", "mode": "metric", "value": None})
    cases.append({"name": "penalty_without_geometry", "mode": "scenario", "value": {"shotType": "penalty"}})
    for fixture in scenes()[:6]:
        s = fixture["scene"]
        cases.append({"name": "scenario_" + fixture["name"], "mode": "scenario", "value": {
            "shotType": s["shot_type"], "players": {"shooter": s["shooter"], "goalkeeper": s["goalkeepers"][0],
                                                   "defender1": s["defenders"][0], "defender2": s["defenders"][1]},
            "extraAttackers": [], "extraDefenders": []}})
    base = extract_metric_features(scenes()[0]["scene"])["vector"]
    if envelope["parameters"]["kind"] == "xgboost":
        for ti, nodes in enumerate(envelope["parameters"]["trees"]):
            for ni, node in enumerate(nodes):
                if "leaf" in node:
                    continue
                index, threshold = envelope["feature_indices"][node["feature"]], np.float32(node["threshold"])
                for direction, value in (("below", np.nextafter(threshold, np.float32(-np.inf))),
                                         ("at", threshold), ("above", np.nextafter(threshold, np.float32(np.inf)))):
                    vector = list(base)
                    vector[index] = float(value)
                    # Invalid count/domain vectors are explicit negative tests, not rounded into the domain.
                    cases.append({"name": f"tree_{ti}_node_{ni}_{direction}", "mode": "vector", "value": vector})
    for i in range(160):
        s = copy.deepcopy(scenes()[0]["scene"])
        s["shooter"] = {"x": i * .65, "y": i * 7 % 68}
        s["goalkeepers"] = [{"x": 103 - i % 35, "y": i * 3 % 68}]
        s["defenders"] = [{"x": i * 17 % 106, "y": i * 11 % 69}]
        cases.append({"name": f"varied_scene_{i}", "mode": "metric", "value": s})
    for name, vector in (("invalid_count", [21, 20, 0, 1.5, 1, 5, 3, 18]),
                         ("invalid_zero_sentinel", [21, 20, 0, 0, 0, 0, 3, 18]),
                         ("invalid_shape", [1, 2]), ("domain_corner", [125, 180, 34, 10, 10, 125, 125, 125])):
        cases.append({"name": name, "mode": "vector", "value": vector})
    return cases


def reference(case, envelope):
    value = case["value"]
    if case["mode"] == "vector":
        try:
            return {"probability": float(predict_envelope(envelope, [value], validate=False)[0])}
        except (AuditError, ValueError):
            return {"probability": None}
    if case["mode"] == "scenario" and value.get("shotType") == "penalty":
        return {"penalty": True}
    if case["mode"] == "scenario":
        p = value["players"]
        value = {"contract_version": "positional-features/v1", "shot_type": value["shotType"],
                 "shooter": p["shooter"], "goalkeepers": [p["goalkeeper"]],
                 "defenders": [p["defender1"], p["defender2"], *value["extraDefenders"]], "observation": "browser-scene"}
    if isinstance(value, dict) and value.get("shot_type") == "penalty":
        return {"penalty": True}
    f = extract_metric_features(value)
    if f["status"] != "ok":
        return {"features": f}
    return {"features": f, "probability": float(predict_envelope(envelope, [f["vector"]], validate=False)[0])}


def verify(envelope, browser=False):
    validate_envelope(envelope)
    cases = cases_for(envelope)
    payload = canonical({"envelope": envelope, "cases": cases})
    command = ["node", str(RUNNER), *(["--browser"] if browser else [])]
    result = subprocess.run(command, input=payload, text=True, capture_output=True, cwd=PROJECT, timeout=120)
    if result.returncode:
        raise AuditError("TypeScript bridge failed; run npm ci and check Node / optional Playwright installation")
    from run_io import load_json
    actual = load_json(result.stdout)
    if actual["loaded"]["status"] != "ready" or len(actual["cases"]) != len(cases):
        raise AuditError("Browser loader rejected the envelope or bridge inventory differs")
    max_probability_error, max_feature_error = 0., 0.
    counts = {"learned": 0, "penalty": 0, "unsupported": 0, "vectors": 0, "invalid_vectors": 0}
    for case, ts in zip(cases, actual["cases"]):
        if ts["name"] != case["name"]:
            raise AuditError("Bridge case ordering differs")
        py = reference(case, envelope)
        if py.get("penalty"):
            if (ts["result"].get("source") != "penalty-convention" or ts["result"].get("probability") != .76
                    or ts["result"].get("learned") is not False or "artifactId" in ts["result"]):
                raise AuditError("Penalty convention parity failed")
            counts["penalty"] += 1
            continue
        if case["mode"] != "vector":
            f = py["features"]
            if f["status"] != "ok":
                if ts["features"] != f or ts["result"] != {"status": "unsupported", "reason": f["reason"]}:
                    raise AuditError(f"Unsupported scene parity failed: {case['name']}")
                counts["unsupported"] += 1
                continue
            if (ts["features"].get("status") != "ok" or ts["features"].get("metadata") != f["metadata"]
                    or ts["features"].get("contract_version") != f["contract_version"]
                    or len(ts["features"].get("vector", [])) != 8):
                raise AuditError(f"Scene feature metadata differs: {case['name']}")
            for a, b in zip(ts["features"]["vector"], f["vector"]):
                error = abs(a - b)
                if error > 1e-9 + 1e-9 * max(abs(a), abs(b)):
                    raise AuditError(f"Feature parity failed: {case['name']}")
                max_feature_error = max(max_feature_error, error)
            prediction = ts["result"]
            if (prediction.get("source") != "learned-model" or prediction.get("artifactId") != envelope["artifact_id"]
                    or prediction.get("modelVersion") != envelope["model_version"]):
                raise AuditError("Learned result identity differs")
            probability = prediction["probability"]
            counts["learned"] += 1
        else:
            probability = ts["probability"]
            counts["vectors"] += 1
        if py["probability"] is None:
            if probability is not None:
                raise AuditError("Invalid vector produced a probability")
            counts["invalid_vectors"] += 1
            continue
        if type(probability) not in (int, float) or not 0 <= probability <= 1:
            raise AuditError("Supported input did not produce a bounded probability")
        error = abs(probability - py["probability"])
        if error > envelope["export_tolerance"]:
            raise AuditError(f"Probability parity tolerance failed: {case['name']}")
        max_probability_error = max(max_probability_error, error)
    return {"artifact_id": envelope["artifact_id"], "model_version": envelope["model_version"],
            "status": "pass", "tolerance": envelope["export_tolerance"], "case_counts": counts,
            "cases_checked": len(cases), "max_probability_error": max_probability_error,
            "max_feature_error": max_feature_error, "engine": actual["engine"],
            "synthetic_harness_bundle_bytes": actual["bundle_bytes"], "esbuild_version": actual["esbuild_version"]}


def check(training_dir, output_dir, synthetic=False, browser=False):
    inference = read_json(INFERENCE_PATH)
    if inference["feature_contract_sha256"] != sha256(CONTRACT_PATH.read_bytes()):
        raise AuditError("Browser feature contract digest is stale")
    codes = code_hashes()
    if synthetic:
        root = PROJECT / "tests/fixtures"
        manifest = None
        candidates = [f["envelope"] for f in read_json(root / "inference-models.json")]
    else:
        root, manifest, candidate = selected_candidate(training_dir)
        candidates = [candidate]
    checks = [verify(e, browser) for e in candidates]
    report = {"schema_version": 1, "contract_version": "browser-inference/v1", "status": "pass",
              "evidence_scope": "invented-artifact" if synthetic else "frozen-local-candidate",
              "training_run_id": manifest["run_id"] if manifest else None,
              "feature_contract_sha256": sha256(CONTRACT_PATH.read_bytes()), "code_sha256": codes,
              "checks": checks, "held_out_labels_accessed": False,
              "parameters_published": False, "penalty": {"probability": .76, "source": "convention"},
              "reproduction": "check_browser_inference.py " + ("--synthetic" if synthetic else "--training-dir <completed-training-directory>")
                              + " --output-dir <local-output-root>" + (" --browser" if browser else ""),
              "limitations": ["Numerical parity does not establish model fitness or empirical scene support",
                              "Public parameter distribution and display require #8/#13/#4 gates",
                              "Node bundle verification is distinct from the optional actual Chromium run"]}

    def guard():
        if code_hashes() != codes or (manifest is not None and verified_run(root)[1] != manifest):
            raise AuditError("Inputs or inference code changed during verification")

    return publish(output_dir, root, "browser-inference", {"parity.json": report},
                   {"code_sha256": codes, "training_run_id": report["training_run_id"],
                    "evidence_scope": report["evidence_scope"]}, guard)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--training-dir", type=Path)
    source.add_argument("--synthetic", action="store_true", help="Invented envelopes only; not actual-candidate evidence")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--browser", action="store_true", help="Optional local Chromium run (requires Playwright)")
    args = parser.parse_args()
    try:
        destination = check(args.training_dir, args.output_dir, args.synthetic, args.browser)
    except (AuditError, OSError, ValueError, KeyError, TypeError, ValidationError, subprocess.TimeoutExpired) as exc:
        message = str(exc) if isinstance(exc, AuditError) else "Invalid input, dependency or incomplete verification"
        print(f"FAIL: {message}; no completed parity run", file=sys.stderr)
        return 1
    report = read_json(destination / "parity.json")
    print(f"PASS: {sum(c['cases_checked'] for c in report['checks'])} cases; {report['evidence_scope']}; fixed tolerances agree")
    print(f"Complete immutable browser-inference run: {destination}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
