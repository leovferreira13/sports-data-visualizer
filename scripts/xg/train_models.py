#!/usr/bin/env python3
"""Tune on training folds, calibrate separately, select/freeze without opening test outcomes."""

import argparse
import copy
from pathlib import Path
import sys

import numpy as np
from jsonschema import ValidationError

from compare_runs import verified_run
from evaluation import bins, explore, metrics, slices
from features import CONTRACT_PATH, FEATURE_NAMES
from ingest_statsbomb import AuditError, canonical, sha256
from model_export import (IDENTITY, calibration_apply, export_estimator,
                          predict_envelope, seal, validate_envelope)
from prepare_training import PARTITIONS, fold_assignments, matches, require_classes, summary
from run_io import code_identity, load_json, protocol, publish, read_json, recheck
from scene_evaluation import diagnose
from training import (arrays, choose_calibration, dependencies, fit_calibration,
                      predict, select, tune)


def development_input(directory):
    directory, manifest, files = verified_run(directory)
    expected = {"manifest.json", "split.json", "protocol.json", "preparation-summary.json",
                *(f"{p}.jsonl" for p in PARTITIONS)}
    config, codes = protocol(), code_identity()
    if (manifest.get("phase") != "preparation" or files != expected
            or manifest.get("protocol_sha256") != sha256(canonical(config).encode())
            or read_json(directory / "protocol.json") != config
            or manifest.get("feature_contract_sha256") != sha256(CONTRACT_PATH.read_bytes())
            or manifest.get("code_sha256") != codes):
        raise AuditError("Preparation/configuration/code drift: prepare again")
    split = read_json(directory / "split.json")
    reports = read_json(directory / "preparation-summary.json")
    rows = {p: [load_json(line) for line in (directory / f"{p}.jsonl").read_bytes().splitlines()]
            for p in PARTITIONS if p != "test"}
    membership, seen = split["partitions"], set()
    if set(membership.values()) != set(PARTITIONS):
        raise AuditError("Invalid split partition names")
    for name, values in rows.items():
        grouped = matches(values)
        if any(membership.get(str(mid)) != name for mid in grouped) or set(grouped) & seen:
            raise AuditError("Match isolation failure")
        if {str(mid) for mid in grouped} != {mid for mid, part in membership.items() if part == name}:
            raise AuditError("Incomplete development membership")
        seen.update(grouped)
        if summary(values) != reports["partitions"][name]:
            raise AuditError("Development partition counts differ")
    expected_folds = {str(k): v for k, v in fold_assignments(rows["train"], config).items()}
    if split["train_folds"] != expected_folds:
        raise AuditError("Fold assignment differs from the protocol")
    for name in ("calibration", "selection"):
        require_classes(rows[name], config["minima"]["validation_class"])
    for fold in range(config["folds"]):
        for held in (True, False):
            require_classes([r for r in rows["train"] if (expected_folds[str(r["match_id"])] == fold) == held],
                            config["minima"]["fold_class"])
    if (reports["test_status"] != "unopened"
            or set(reports["partitions"]["test"]) != {"shots", "matches", "composition"}
            or any(set(c) != {"competition_id", "season_id", "shots", "matches"}
                   for c in reports["partitions"]["test"]["composition"])):
        raise AuditError("Preparation exposes held-out outcomes")
    return directory, manifest, rows, split, reports, config, codes


def verify_parity(envelope, model, vectors, indices, calibration, tolerance):
    vectors = np.asarray(vectors, dtype=float)
    reference = calibration_apply(predict(model, vectors[:, indices]), calibration)
    exported = predict_envelope(envelope, vectors)
    error = float(np.max(np.abs(reference - exported)))
    if error > tolerance:
        raise AuditError("Model export probability tolerance failed")
    return error


def train(input_dir, output_dir):
    directory, manifest, rows, split, reports, config, codes = development_input(input_dir)
    deps = dependencies()
    provenance = {"preparation_run_id": manifest["run_id"], "feature_run_id": manifest["feature_run_id"],
                  "source_revision": manifest["source"]["source_revision"],
                  "protocol_sha256": manifest["protocol_sha256"],
                  "split_sha256": sha256((directory / "split.json").read_bytes()),
                  "code_sha256": codes, "dependencies": deps}
    evidence_id = sha256(canonical(provenance).encode())
    selection_rows = rows["selection"]
    vectors, y = arrays(selection_rows, list(range(8)))
    prevalence = sum(r["is_goal"] for r in rows["train"]) / len(rows["train"])
    constant = np.full(len(y), prevalence)
    files, candidates, experiments, cv, parity = {}, [], [], {}, {}
    private_predictions = {"constant": constant.tolist()}
    files["constant-reference.json"] = {"probability": prevalence, "fitted_partition": "train"}
    experiments.append({"id": "constant", "stage": "validation-selection", "status": "ok",
                        "feature_indices": [], "configuration": {"probability": prevalence},
                        "variants": [{"calibration": "identity", "metrics": metrics(y, constant, config),
                                      "calibration_bins": bins(y, constant, config),
                                      "slices": slices(selection_rows, y, constant, config)}]})
    for experiment in config["experiments"]:
        eid = experiment["id"]
        print(f"Training {eid}: bounded train-only group CV", flush=True)
        model, cv[eid] = tune(rows["train"], split["train_folds"], experiment, config)
        record = {"id": eid, "stage": "validation-selection", "feature_indices": experiment["indices"],
                  "status": "failed", "variants": []}
        experiments.append(record)
        if model is None:
            record["reason"] = "training_failed"
            continue
        record["configuration"] = cv[eid]["selected_configuration"]
        indices = experiment["indices"]
        xc, yc = arrays(rows["calibration"], indices)
        base = predict(model, vectors[:, indices])
        fitted_cal = fit_calibration(yc, predict(model, xc), config)
        calibrated = calibration_apply(base, fitted_cal) if fitted_cal else None
        use_cal, comparison = choose_calibration(selection_rows, y, base, calibrated, config)
        calibration = fitted_cal if use_cal else copy.deepcopy(IDENTITY)
        final = calibrated if use_cal else base
        record.update(status="ok", calibration_decision={"adopted": bool(use_cal), "comparison": comparison,
                                                        "fit_status": "ok" if fitted_cal else "declined"})
        for name, p in [("identity", base), *([("sigmoid", calibrated)] if calibrated is not None else [])]:
            record["variants"].append({"calibration": name, "metrics": metrics(y, p, config),
                                       "calibration_bins": bins(y, p, config),
                                       "slices": slices(selection_rows, y, p, config)})
            private_predictions[eid + ":" + name] = p.tolist()
        envelope = export_estimator(model, experiment, provenance, config)
        raw_envelope = copy.deepcopy(envelope)
        envelope["calibration"] = calibration
        envelope = seal(envelope)
        validate_envelope(envelope)
        diagnostics, synthetic_vectors = diagnose(envelope, rows["train"])
        all_vectors = np.vstack([vectors, arrays(rows["calibration"], list(range(8)))[0], synthetic_vectors])
        # Boundary vectors preserve the feature domain and exercise each observed tree threshold.
        if experiment["kind"] == "xgboost":
            boundary = []
            for nodes in envelope["parameters"]["trees"]:
                for node in nodes:
                    if "feature" not in node:
                        continue
                    index, threshold = node["feature"], node["threshold"]
                    if index in (3, 4):
                        continue  # Integer count thresholds are covered by legal validation vectors.
                    for value in (np.nextafter(np.float32(threshold), np.float32(-np.inf)).item(), threshold,
                                  np.nextafter(np.float32(threshold), np.float32(np.inf)).item()):
                        vector = vectors[0].copy()
                        vector[index] = value
                        if (0 <= value <= (180 if index == 1 else 34 if index == 2 else np.hypot(105, 68))
                                and (index != 5 or vector[3] != 0)):
                            boundary.append(vector)
            if boundary:
                all_vectors = np.vstack([all_vectors, boundary])
        tolerance = envelope["export_tolerance"]
        parity[eid] = {"absolute_probability_error": verify_parity(envelope, model, all_vectors, indices, calibration, tolerance),
                       "vectors_checked": len(all_vectors), "tolerance": tolerance}
        if experiment["kind"] == "logistic":
            record["standardized_coefficients"] = dict(zip([FEATURE_NAMES[i] for i in indices],
                                                            envelope["parameters"]["coefficients"]))
        files[eid + "-raw.json"] = raw_envelope
        files[eid + ".json"] = envelope
        record["scene_diagnostics"] = diagnostics
        candidates.append({"id": eid, "probabilities": final, "artifact_id": envelope["artifact_id"]})
    chosen, decision = select(selection_rows, y, candidates, constant, config)
    if not any(c["id"] == "full_logistic" for c in candidates):
        chosen = None
        decision = {"status": "no_candidate", "reason": "Required full-logistic test baseline unavailable",
                    "candidate_checks": decision.get("candidate_checks", [])}
    decision["test_status"] = "unopened"
    decision["hypothesis"] = "Additional positional groups or nonlinear trees improve probability estimation"
    decision["consequences"] = "No refit after selection; #13 evaluates this exact pipeline and controls public release"
    if chosen:
        files["selected-model.json"] = files[chosen["id"] + ".json"]
        decision["selected_artifact_id"] = chosen["artifact_id"]
    evaluation = {"schema_version": 1, "contract_version": "xg-evaluation/v1", "evidence_id": evidence_id,
                  "provenance": provenance, "population": "male open-play foot shots with observed keeper; partial defenders",
                  "exclusions": ["penalties", "headers", "missing/invalid frames", "missing/multiple keeper", "goal-line shots"],
                  "feature_order": list(FEATURE_NAMES), "partitions": reports["partitions"],
                  "test_status": "unopened", "experiments": experiments, "selection": decision,
                  "export_checks": parity, "training_exploration": explore(rows["train"], config),
                  "cv": cv, "ui_diagnostics_from_feature_audit": reports["ui_diagnostics_from_feature_audit"],
                  "limitations": ["Match holdout does not establish competition or period transfer",
                                  "Partial observed defenders differ from represented browser scenes",
                                  "Marginal feature ranges do not prove joint support",
                                  "Sentinel and extreme keeper positions may be sparsely supported",
                                  "Coefficients and controlled scenes do not demonstrate causality",
                                  "Selection bootstrap is exploratory; final test remains unopened"],
                  "protocol": config}
    from report_training import validate_evaluation, render_report
    validate_evaluation(evaluation)
    files.update({"evaluation.json": evaluation, "selection.json": decision, "protocol.json": config,
                  "split.json": split, "validation-predictions.json": {
                    "match_ids": [r["match_id"] for r in selection_rows], "labels": y.tolist(), "probabilities": private_predictions},
                  "methodology.md": render_report(evaluation)})
    return publish(output_dir, directory, "training", files,
                   {**provenance, "evidence_id": evidence_id, "feature_contract_sha256": sha256(CONTRACT_PATH.read_bytes()),
                    "selected_model": chosen["id"] if chosen else None},
                   lambda: recheck(directory, manifest, codes))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    try:
        path = train(args.input_dir, args.output_dir)
    except (AuditError, OSError, KeyError, TypeError, ValueError, ValidationError) as exc:
        message = str(exc) if isinstance(exc, AuditError) else "Invalid preparation, fitting, export or scientific output"
        print(f"FAIL: {message}; no completed run", file=sys.stderr)
        return 1
    print(f"Complete immutable training: {path}; test outcomes unopened")
    return 0


if __name__ == "__main__":
    sys.exit(main())
