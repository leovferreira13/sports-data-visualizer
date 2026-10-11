#!/usr/bin/env python3
"""Validate aggregate-only evidence and regenerate the English methodology report."""

import argparse
from pathlib import Path
import sys

from jsonschema import validate, ValidationError

from features import FEATURE_NAMES
from ingest_statsbomb import AuditError, canonical, sha256
from run_io import PROJECT, read_json


def validate_evaluation(evaluation):
    validate(evaluation, read_json(PROJECT / "model/evaluation.schema.json"))
    canonical(evaluation)
    if evaluation["evidence_id"] != sha256(canonical(evaluation["provenance"]).encode()):
        raise AuditError("Evaluation provenance identity drift")
    if evaluation["feature_order"] != list(FEATURE_NAMES):
        raise AuditError("Evaluation feature order drift")
    expected = ["constant", *[e["id"] for e in evaluation["protocol"]["experiments"]]]
    if [e["id"] for e in evaluation["experiments"]] != expected:
        raise AuditError("Evaluation omits a declared experiment")
    forbidden = {"event_id", "match_id", "match_ids", "vector", "vectors", "location", "players",
                 "features.jsonl", "labels", "raw_predictions"}
    def walk(item):
        if isinstance(item, dict):
            if forbidden & item.keys():
                raise AuditError("Shot-level fields cannot enter public aggregate evidence")
            for value in item.values():
                walk(value)
        elif isinstance(item, list):
            for value in item:
                walk(value)
    walk(evaluation)


def render_report(e):
    validate_evaluation(e)
    p = e["protocol"]
    lines = ["# xG training methodology and validation results", "",
             "**Status:** validation evidence only; final test unopened; public inference is not approved.", "",
             f"Evidence: `{e['evidence_id']}`. Feature run: `{e['provenance']['feature_run_id']}`.", "",
             "## Research question and data", "",
             "We test whether observed defender and keeper positions add predictive information beyond shot geometry, and whether shallow boosted trees justify their complexity. Actual goal/non-goal outcomes are labels; StatsBomb xG is never used for training.", "",
             "The source is StatsBomb Open Data, credited as training data rather than the author of this independent model. Eligible rows are male open-play left/right-foot shots with valid positional frames and an observed opposing keeper. Penalties, headers and unsupported observations are excluded. The penalty value 0.76 is a separate convention reserved for browser integration.", "",
             "## Partitions and leakage prevention", "",
             "Match-level, label-blind competition-season allocation uses seed 42 and approximate 60/10/10/20 training/calibration/selection/test proportions. Largest-remainder allocation can change exact ratios in small strata. Train-only five-fold CV tunes hyperparameters; calibration and selection validation have separate roles. The pipeline is frozen without a final refit. Test goal counts, prevalence and predictions are deliberately absent.", "",
             "| Partition | Matches | Shots | Goals | Prevalence |", "| --- | ---: | ---: | ---: | ---: |"]
    for name, s in e["partitions"].items():
        goals = str(s["goals"]) if "goals" in s else "Unopened"
        prevalence = f"{s['prevalence']:.6%}" if "prevalence" in s else "Unopened"
        lines.append(f"| {name} | {s['matches']} | {s['shots']} | {goals} | {prevalence} |")
    lines += ["", "## Features, exploration and preprocessing", "",
              "Geometry uses distance, physical goal opening angle and absolute lateral offset. The defender group adds visible count, finite-cone count and nearest observed distance. The keeper group adds distances to goal and shooter. Full logistic and XGBoost use all eight; the selected model need not retain every group.", "",
              "Distances/counts/angles have different scales. Fold-local StandardScaler and L2 regularization make logistic fitting comparable while reducing unstable correlated weights. The scaler is later fitted only on the full training partition, and its mean/scale travel with the model. Trees use raw finite features. Neither family uses class balancing, resampling, automatic clipping of positions, or test feedback.", "",
              f"Training contains {e['training_exploration']['zero_defender_sentinel_shots']} zero-visible-defender frames. Their pitch-diagonal distance is a sentinel, excluded from continuous distance distributions/correlations. Zero visible defenders does not establish absence of defenders.", "",
              "Training-only distributions, quantiles, Pearson/Spearman correlations, goal rates and competition slices are in `evaluation.json`. Correlations omit sentinel rows, and undefined correlations are null. Sparse means fewer than 100 shots or 10 goals; that reporting rule does not certify other slices as reliable. UI incompatibility counts come from the feature audit because accepted vectors omit original player coordinates. Full-pitch positions are retained.", "",
              "## Tuning and calibration", "",
              "Logistic C values are 0.01, 0.1, 1 and 10. XGBoost has eight combinations of depth 2/3, learning rate 0.05/0.1 and minimum child weight 5/20, with 300 trees. CPU execution uses one thread, full row/column sampling and no early stopping. Fold-pooled natural-log loss chooses settings; deterministic ties favor the declared simpler configuration.", "",
              "Each estimator has identity and, when valid, two-parameter sigmoid calibration. The sigmoid is fitted to clipped base-probability logits on calibration rows only, and must have a positive slope. Selection rows decide adoption: at least 0.0001 log-loss improvement with a paired interval below zero and at most 0.0001 Brier degradation. No isotonic variant or post-result grid expansion is used.", "",
              "## Selection validation comparisons", "",
              "These metrics belong to selection validation, not the final held-out test. Lower log loss and Brier are better. Calibration tables use ten fixed probability bins and retain counts/empty bins.", "",
              "| Experiment | Calibration | Log loss | Brier | Mean probability |", "| --- | --- | ---: | ---: | ---: |"]
    for experiment in e["experiments"]:
        if experiment["status"] != "ok":
            lines.append(f"| {experiment['id']} | Failed | — | — | — |")
        for variant in experiment["variants"]:
            m = variant["metrics"]
            lines.append(f"| {experiment['id']} | {variant['calibration']} | {m['log_loss']:.10f} | {m['brier']:.10f} | {m['mean_probability']:.10f} |")
    selection = e["selection"]
    lines += ["", "## Decision and uncertainty", "",
              f"Decision: **{selection['status']}**. Selected model: **{selection.get('selected_model', 'none')}**.", "",
              selection.get("rationale", selection.get("reason", "")), "",
              "A candidate must improve the training-prevalence reference under the declared paired rule. Among eligible candidates, choose the simplest competitive model, ordered geometry logistic, defender logistic, full logistic, then XGBoost. Full logistic and the constant are retained for issue #13. A no-candidate result withholds a positional model instead of declaring success.", "",
              f"Comparison intervals use {p['bootstrap']['resamples']} paired match bootstrap samples, seed {p['bootstrap']['seed']}, retaining each sampled match's complete shot multiplicity. The 95% intervals are exploratory selection evidence, not a new untouched test or causal inference. Numeric differences, intervals, calibration decisions and hypotheses/consequences are recorded in `selection`.", "",
              "## Controlled scenes, export and limitations", "",
              "Invented current presets and controlled geometry/defender/keeper changes check finite probabilities, reflection, defender order and omitted-group invariance. Effects are model comparisons, not real-world causal claims. No universal monotonic rule is imposed on coupled positional features. Sparse or extreme scenes require the final empirical-support review.", "",
              "The local export contains coefficients/scaler or inference-only tree nodes/base margin plus calibration and provenance. An independent evaluator checks logistic probabilities within 1e-10 and XGBoost within 1e-7, including numeric tree thresholds. Tree inputs and margin accumulation preserve float32 behavior. Browser parity is still issue #12.", "",
              *[f"- {limitation}." for limitation in e["limitations"]], "",
              "## Reproduction and handoff", "",
              "See `docs/architecture/reference/xg-training.md` for the locked environment, exact commands and complete-run comparison. This report is regenerated from the same versioned `evaluation.json` used by the future bilingual Methodology and results tab. No real feature rows, shot coordinates or match/event identities appear in public evidence. Candidate parameters stay local pending issue #8/#13 review.", "",
              "Issue #13 must evaluate the exact frozen candidate, full-logistic baseline and constant on the same held-out rows, report match-level uncertainty and relevant slices, and record the final rights/release decision. Do not tune against that test and continue calling it untouched.", ""]
    return "\n".join(lines).encode()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evaluation", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        report = render_report(read_json(args.evaluation))
        if args.output.resolve() == args.evaluation.resolve():
            raise AuditError("Report cannot overwrite evidence")
        args.output.write_bytes(report)
    except (AuditError, OSError, ValueError, ValidationError):
        print("FAIL: invalid aggregate evidence or report output", file=sys.stderr)
        return 1
    print("PASS: methodology regenerated from aggregate evidence")
    return 0


if __name__ == "__main__":
    sys.exit(main())
