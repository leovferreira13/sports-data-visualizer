#!/usr/bin/env python3
"""Score the frozen current and monotonic XGBoost envelopes on one split.

Does not fit, does not score logistic, and does not write the published model.
Selection vectors live in the preparation run, so --prepared-dir is required
alongside the training run and the complete phase-A directory.
"""

import argparse
from pathlib import Path
import sys

import numpy as np

from ingest_statsbomb import AuditError, canonical, sha256
from run_io import PROJECT, read_json

EVIDENCE_ID = "f62228e611a9712acaac4abcbc61b0f3ffc1ec0b0880e111bd0aa447f872dee8"
SPLIT_SHA256 = "64f02e169df4b2d176b54ce47ef72a7afa3840d7990ac45b6841008e94aa71d1"
TRAINING_RUN_ID = "222909fe801f4865897fea3541e023fed626f6736dca6ef69ceada1f7c57945a"
CURRENT_ARTIFACT = "758526873b8a3a2681f655c064dee52f8bd33749accd499d015420dbe8e11b9a"
MONOTONIC_ARTIFACT = "e19402c5ba622ebc2775df202956aa5b942dd5e841b647cb7eeb531faf2a12ce"
PUBLISHED_FILE_SHA256 = "c0d91256a2c0f83ede48f1f549b8a0cc379e6ef675ccd4ce9ef10e471bb4350d"
SEED = 42
DIRECTION_TOLERANCE = 1e-7
REPRODUCTION_METRIC = 1e-08
METRIC_CLIP = 1e-12
CONSTRAINTS = [-1, 1, 0, 0, 0, 0, 0, 0]
DECISION_LIMITS = (
    "max_log_loss_degradation", "max_brier_degradation",
    "min_jump_rate_reduction", "one_sided_confidence",
)
# Same predicate set as behavior_statistics.gates. A missing name is not a pass.
PREDECLARED_GATES = (
    "log_loss", "brier", "constant_reference", "partial_directions",
    "primary_segments_available", "interactive_improvement",
    "invariants", "parity", "native_export",
)
PUBLISHED_MODEL = PROJECT / "model" / "selected-model.json"


def require_constraints(constraints):
    if list(constraints) != CONSTRAINTS:
        raise AuditError("Unsupported monotonic constraint tuple")


def mean_log_loss(y, probabilities):
    labels = np.asarray(y, dtype=float)
    clipped = np.clip(np.asarray(probabilities, dtype=float), METRIC_CLIP, 1 - METRIC_CLIP)
    if labels.shape != clipped.shape or not len(labels) or not np.isin(labels, [0, 1]).all():
        raise AuditError("Invalid log-loss inputs")
    return float((-(labels * np.log(clipped) + (1 - labels) * np.log1p(-clipped))).mean())


def direction_violation_count(probabilities, direction, tolerance=DIRECTION_TOLERANCE):
    delta = np.diff(np.asarray(probabilities, dtype=float)) * direction
    return int((delta < -tolerance).sum())


def violation_totals(isolated):
    distance = angle = 0
    for row in isolated:
        name = row["name"]
        if name.endswith("shot_distance_m"):
            distance += int(row["violations"])
        elif name.endswith("goal_opening_angle_deg"):
            angle += int(row["violations"])
    return distance, angle


def require_decision_limits(protocol):
    """Every numeric gate limit is read from protocol.decision. Nothing is filled in here."""
    decision = protocol.get("decision") if isinstance(protocol, dict) else None
    if not isinstance(decision, dict):
        raise AuditError("Protocol decision limits are missing")
    limits = {}
    for key in DECISION_LIMITS:
        value = decision.get(key)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise AuditError("Protocol decision limit is missing: " + key)
        limits[key] = float(value)
    return limits


def revised_decision(*, identity_ok, pairs_equal, log_loss_increase, distance_violations,
                     angle_violations, limits):
    cap = limits["max_log_loss_degradation"]
    if not identity_ok or not pairs_equal:
        return "insufficient_evidence", ["Identity, seed, split, or primary pair counts are not comparable"]
    if log_loss_increase > cap:
        return "retain", [f"Selection log-loss increase is above {cap}"]
    if distance_violations or angle_violations:
        return "retain", ["Isolated distance or angle direction violation"]
    return "recommend_replacement", [f"Log-loss increase is within {cap} and isolated directions pass"]


def original_decision(gates_result, limits):
    """Map the full behavior_statistics.gates result. Omitted predicates do not pass."""
    require_decision_limits({"decision": limits})
    predicates = gates_result.get("predicates") if isinstance(gates_result, dict) else None
    if not isinstance(predicates, dict):
        return "insufficient_evidence", ["Original gates are missing"]
    missing = [name for name in PREDECLARED_GATES if name not in predicates]
    if missing:
        return "insufficient_evidence", ["Original gates omitted " + ", ".join(missing)]
    failed = [name for name in PREDECLARED_GATES if not predicates[name]]
    failed.extend(name for name in gates_result.get("failures", []) if name not in failed)
    if failed:
        return "retain", [f"Predeclared gate failed: {name}" for name in failed]
    if gates_result.get("eligible") is not True:
        return "insufficient_evidence", ["Original gates are not eligible"]
    return "recommend_replacement", ["Every predeclared gate passed"]


def pair_decisions(*, identity_ok, pairs_equal, gates_result, limits, log_loss_increase,
                   distance_violations, angle_violations):
    if not identity_ok or not pairs_equal:
        original_status, original_reasons = (
            "insufficient_evidence",
            ["Identity, seed, split, or primary pair counts are not comparable"],
        )
    else:
        original_status, original_reasons = original_decision(gates_result, limits)
    revised_status, revised_reasons = revised_decision(
        identity_ok=identity_ok, pairs_equal=pairs_equal, log_loss_increase=log_loss_increase,
        distance_violations=distance_violations, angle_violations=angle_violations, limits=limits)
    return {
        "original_predeclared": {
            "status": original_status, "reasons": original_reasons, "includes_jump_reduction_gate": True,
            "jump_reduction_required": limits["min_jump_rate_reduction"], "limits": limits,
            "predicates": None if not isinstance(gates_result, dict) else gates_result.get("predicates"),
        },
        "revised": {
            "status": revised_status, "reasons": revised_reasons,
            "log_loss_increase_limit": limits["max_log_loss_degradation"],
            "includes_jump_reduction_gate": False,
        },
        "depends_on_revision": original_status != revised_status,
    }


def assert_identity(evaluation, training_manifest):
    if evaluation.get("evidence_id") != EVIDENCE_ID:
        raise AuditError("Research evidence id does not match the phase-A binding")
    protocol = evaluation["protocol"]["original_training_protocol"]
    if protocol.get("seed") != SEED:
        raise AuditError("Training seed is not 42")
    if evaluation["provenance"].get("split_sha256") != SPLIT_SHA256:
        raise AuditError("Research split SHA-256 does not match the bound partition")
    if training_manifest.get("split_sha256") != SPLIT_SHA256 or training_manifest.get("run_id") != TRAINING_RUN_ID:
        raise AuditError("Training manifest is not the bound run and split")
    if evaluation.get("original_training_run_id") != TRAINING_RUN_ID:
        raise AuditError("Research run is not bound to the original training run")
    require_constraints(evaluation["protocol"]["candidate"]["monotone_constraints"])
    current = evaluation["models"]["full_xgboost"]["artifact_id"]
    monotonic = evaluation["models"]["full_monotonic_xgboost"]["artifact_id"]
    if current != CURRENT_ARTIFACT or monotonic != MONOTONIC_ARTIFACT:
        raise AuditError("Artifact id does not match the phase-A binding")


def assert_selection_counts(rows, recorded_shots, recorded_goals):
    labels = [row["is_goal"] for row in rows]
    if len(rows) != recorded_shots or int(sum(labels)) != recorded_goals:
        raise AuditError("Selection row or label count differs from the bound evaluation")


def assert_output_allowed(output_dir):
    root = Path(output_dir).resolve()
    blocked = [(PROJECT / "model").resolve(), (PROJECT / "public" / "model").resolve()]
    if any(root == path or path in root.parents for path in blocked):
        raise AuditError("Refusing to write under the published model directories")
    derived = (PROJECT / "data" / "derived").resolve()
    if root == PROJECT.resolve() or PROJECT.resolve() in root.parents:
        if root != derived and derived not in root.parents:
            raise AuditError("Project outputs must stay under ignored data/derived")
    return root


def render_pair_report(summary):
    decisions = summary["decisions"]
    original = decisions["original_predeclared"]
    revised = decisions["revised"]
    metrics = summary["metrics"]
    lines = [
        "# Current versus monotonic XGBoost",
        "",
        "Both columns use the same selection rows, seed 42, and split. "
        f"The original column is every predeclared gate, including the {original['jump_reduction_required']:.0%} jump-reduction gate, "
        "constant reference, partial directions, invariants, parity, and native export. "
        "Limits come from protocol.decision. "
        "The revised column is the selection log-loss increase and isolated distance and angle violations. "
        "A recommendation does not publish either model.",
        "",
        "| Rule | Decision | Why |",
        "| --- | --- | --- |",
        f"| Original predeclared gates, including the {original['jump_reduction_required']:.0%} jump-reduction gate | {original['status']} | {'; '.join(original['reasons'])} |",
        f"| Revised (log-loss increase ≤ {revised['log_loss_increase_limit']} and isolated directions) | {revised['status']} | {'; '.join(revised['reasons'])} |",
        "",
        f"Decision depends on the revision: **{str(decisions['depends_on_revision']).lower()}**.",
        "",
        "| Model | Log loss | Brier | Distance violations | Angle violations | Primary >0.02 jump rate | Primary p95 jump |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for name in ("full_xgboost", "full_monotonic_xgboost"):
        row = metrics[name]
        lines.append(
            f"| {name} | {row['log_loss']:.8f} | {row['brier']:.8f} | {row['distance_violations']} | "
            f"{row['angle_violations']} | {row['large_jump_rate']:.8f} | {row['p95_jump']:.8f} |"
        )
    lines.extend([
        "",
        f"Selection log-loss increase (monotonic minus current): {summary['log_loss_increase']:.8f}. "
        f"Limit: {revised['log_loss_increase_limit']}.",
        f"Paired one-sided 95% upper bounds versus current: log loss {summary['log_loss_upper']}, "
        f"Brier {summary['brier_upper']}.",
        "",
        "The 0.8–0.9 probability band is issue #40 and is not a gate here.",
        "This run does not change `model/selected-model.json` or deployment configuration.",
        "",
    ])
    return "\n".join(lines)


def write_outputs(output_dir, files):
    root = assert_output_allowed(output_dir)
    root.mkdir(parents=True, exist_ok=True)
    written = []
    for name, payload in files.items():
        if Path(name).name != name:
            raise AuditError("Invalid comparison output name")
        path = root / name
        path.write_bytes(payload if isinstance(payload, bytes) else canonical(payload).encode())
        written.append(path)
    return written


def _recorded_metric(evaluation, name, key):
    return evaluation["models"][name]["quality"]["metrics"][key]


def run_comparison(prepared_dir, training_dir, research_dir, output_dir):
    published_sha = sha256(PUBLISHED_MODEL.read_bytes())
    if published_sha != PUBLISHED_FILE_SHA256:
        raise AuditError("Published model file SHA-256 is not the reviewed envelope")
    research = Path(research_dir)
    evaluation = read_json(research / "behavior-evaluation.json")
    training_manifest = read_json(Path(training_dir) / "manifest.json")
    assert_identity(evaluation, training_manifest)
    print(f"seed {SEED}", flush=True)
    print(f"split_sha256 {SPLIT_SHA256}", flush=True)
    from behavior_io import original_inputs
    from behavior_statistics import gates, quality
    from behavior_sweeps import evaluate_sweeps
    from model_export import predict_envelope

    limits = require_decision_limits(evaluation["protocol"])

    context = original_inputs(Path(prepared_dir), Path(training_dir), evaluation["protocol"])
    rows = context["rows"]["selection"]
    assert_selection_counts(
        rows, _recorded_metric(evaluation, "full_xgboost", "shots"),
        _recorded_metric(evaluation, "full_xgboost", "goals"))
    current = read_json(research / "current-model.json")
    candidate = read_json(research / "candidate-model.json")
    if current != context["current"] or current["artifact_id"] != CURRENT_ARTIFACT:
        raise AuditError("Research current envelope is not the published model")
    if candidate["artifact_id"] != MONOTONIC_ARTIFACT:
        raise AuditError("Research candidate artifact id drifted")
    vectors = np.asarray([row["vector"] for row in rows], dtype=float)
    labels = np.asarray([row["is_goal"] for row in rows])
    probabilities = {
        "full_xgboost": predict_envelope(current, vectors),
        "full_monotonic_xgboost": predict_envelope(candidate, vectors),
    }
    for name, values in probabilities.items():
        got = mean_log_loss(labels, values)
        recorded = _recorded_metric(evaluation, name, "log_loss")
        if abs(got - recorded) > REPRODUCTION_METRIC:
            raise AuditError(f"Recomputed {name} log loss does not match the bound evaluation")
    final_config = read_json(PROJECT / "model" / "final-evaluation-protocol.json")
    training_config = evaluation["protocol"]["original_training_protocol"]
    behaviors = {}
    for name, envelope in (("full_xgboost", current), ("full_monotonic_xgboost", candidate)):
        behaviors[name] = evaluate_sweeps(envelope, context["rows"]["train"], evaluation["protocol"], final_config)[0]
    quality_record = quality(
        rows, labels, probabilities["full_monotonic_xgboost"], context["constant"],
        probabilities["full_xgboost"], training_config, final_config, evaluation["protocol"],
    )
    paired = quality_record["paired_with_current"]
    frozen = evaluation["models"]["full_monotonic_xgboost"]
    gate_result = gates(
        {"quality": quality_record, "behavior": behaviors["full_monotonic_xgboost"],
         "scene_audit": frozen["scene_audit"], "parity": frozen["parity"],
         "native_export_pass": frozen["native_export_pass"]},
        behaviors["full_xgboost"], evaluation["protocol"])
    current_primary = behaviors["full_xgboost"]["pooled"]["primary"]
    monotonic_primary = behaviors["full_monotonic_xgboost"]["pooled"]["primary"]
    current_distance, current_angle = violation_totals(behaviors["full_xgboost"]["isolated"])
    mono_distance, mono_angle = violation_totals(behaviors["full_monotonic_xgboost"]["isolated"])
    pairs_equal = current_primary["pairs"] > 0 and current_primary["pairs"] == monotonic_primary["pairs"]
    log_loss_increase = mean_log_loss(labels, probabilities["full_monotonic_xgboost"]) - mean_log_loss(
        labels, probabilities["full_xgboost"])
    decisions = pair_decisions(
        identity_ok=True, pairs_equal=pairs_equal, gates_result=gate_result, limits=limits,
        log_loss_increase=log_loss_increase, distance_violations=mono_distance, angle_violations=mono_angle)
    metrics = {}
    for name, probability, distance, angle, primary in (
            ("full_xgboost", probabilities["full_xgboost"], current_distance, current_angle, current_primary),
            ("full_monotonic_xgboost", probabilities["full_monotonic_xgboost"], mono_distance, mono_angle, monotonic_primary)):
        from evaluation import metrics as score_metrics
        scored = score_metrics(labels, probability, training_config)
        metrics[name] = {
            "log_loss": scored["log_loss"], "brier": scored["brier"],
            "distance_violations": distance, "angle_violations": angle,
            "large_jump_rate": primary["large_jump_rate"], "p95_jump": primary["p95_jump"],
            "primary_pairs": primary["pairs"],
        }
    summary = {
        "log_loss_increase": log_loss_increase,
        "log_loss_limit": limits["max_log_loss_degradation"],
        "log_loss_upper": paired["log_loss"]["upper_95"],
        "brier_upper": paired["brier"]["upper_95"],
        "metrics": metrics, "decisions": decisions,
    }
    identity = {
        "evidence_id": EVIDENCE_ID, "seed": SEED, "split_sha256": SPLIT_SHA256,
        "training_run_id": TRAINING_RUN_ID,
        "current_artifact_id": CURRENT_ARTIFACT, "monotonic_artifact_id": MONOTONIC_ARTIFACT,
        "current_model_file_sha256": sha256((research / "current-model.json").read_bytes()),
        "monotonic_model_file_sha256": sha256((research / "candidate-model.json").read_bytes()),
        "published_model_file_sha256": published_sha,
        "published_model_unchanged": True,
    }
    report = render_pair_report(summary)
    write_outputs(output_dir, {
        "pair-identity.json": identity,
        "pair-metrics.json": {"summary": summary, "decisions": decisions},
        "pair-decision.md": report.encode(),
    })
    print(f"original {decisions['original_predeclared']['status']}", flush=True)
    print(f"revised {decisions['revised']['status']}", flush=True)
    print(f"depends_on_revision {str(decisions['depends_on_revision']).lower()}", flush=True)
    return decisions


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("prepared-dir", "training-dir", "research-dir", "output-dir"):
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args()
    try:
        run_comparison(args.prepared_dir, args.training_dir, args.research_dir, args.output_dir)
    except (AuditError, OSError, ValueError, TypeError, KeyError) as exc:
        message = str(exc) if isinstance(exc, AuditError) else "Invalid comparison inputs or outputs"
        print("FAIL: " + message + "; no comparison output", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
