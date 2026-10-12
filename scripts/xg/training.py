"""Bounded training, explicit calibration and evidence-backed model selection."""

from importlib import metadata
from itertools import product
import warnings
import sys

import numpy as np
from sklearn.exceptions import ConvergenceWarning
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from threadpoolctl import threadpool_limits
from xgboost import XGBClassifier

from evaluation import checked, metrics, paired_difference
from ingest_statsbomb import AuditError
from model_export import IDENTITY, calibration_apply
from run_io import PROJECT


def dependencies():
    if sys.version_info[:2] != (3, 12):
        raise AuditError("Reference training requires Python 3.12")
    result = {}
    for line in (PROJECT / "scripts/xg/requirements.lock").read_text().splitlines():
        if not line or line.startswith("#"):
            continue
        name, version = line.split("==")
        installed = metadata.version(name)
        if installed != version:
            raise AuditError("Training dependencies differ from the committed lock")
        result[name] = installed
    return result


def arrays(rows, indices):
    return (np.asarray([r["vector"] for r in rows], dtype=float)[:, indices],
            np.asarray([r["is_goal"] for r in rows]))


def configurations(experiment, config):
    if experiment["kind"] == "logistic":
        return [{"C": c} for c in config["logistic"]["C"]]
    return [{"max_depth": d, "min_child_weight": m, "learning_rate": lr}
            for d, m, lr in product(config["xgboost"]["max_depth"], sorted(config["xgboost"]["min_child_weight"], reverse=True),
                                    config["xgboost"]["learning_rate"])]


def estimator(experiment, hyper, config):
    if experiment["kind"] == "logistic":
        params = {k: v for k, v in config["logistic"].items() if k != "C"}
        return Pipeline([("scale", StandardScaler()),
                         ("model", LogisticRegression(**params, **hyper, random_state=config["seed"]))])
    params = {k: v for k, v in config["xgboost"].items() if k not in hyper}
    if "monotone_constraints" in experiment:
        constraints = experiment["monotone_constraints"]
        if (experiment["indices"] != list(range(8))
                or constraints != [-1, 1, 0, 0, 0, 0, 0, 0]):
            raise AuditError("Unsupported research monotonic feature mapping")
        params["monotone_constraints"] = tuple(constraints)
    return XGBClassifier(**params, **hyper, random_state=config["seed"])


def fit(model, x, y):
    if set(y.tolist()) != {0, 1}:
        raise AuditError("Training fit requires both classes")
    with threadpool_limits(limits=1), warnings.catch_warnings():
        warnings.simplefilter("error", ConvergenceWarning)
        model.fit(x, y)
    return model


def predict(model, x):
    with threadpool_limits(limits=1):
        p = model.predict_proba(x)[:, 1].astype(float)
    checked(np.zeros(len(p)), p)
    return p


def tune(rows, fold_map, experiment, config):
    x, y = arrays(rows, experiment["indices"])
    folds = np.asarray([fold_map[str(r["match_id"])] for r in rows])
    candidates, best = [], None
    for hyper in configurations(experiment, config):
        try:
            oof = np.full(len(y), np.nan)
            fold_metrics = []
            for fold in range(config["folds"]):
                held = folds == fold
                model = fit(estimator(experiment, hyper, config), x[~held], y[~held])
                oof[held] = predict(model, x[held])
                fold_metrics.append(metrics(y[held], oof[held], config))
            score = metrics(y, oof, config)
            result = {"configuration": hyper, "status": "ok", "oof_metrics": score, "fold_metrics": fold_metrics}
            if best is None or score["log_loss"] < best["oof_metrics"]["log_loss"] - config["decision"]["cv_tie_tolerance"]:
                best = result
        except (AuditError, ConvergenceWarning, FloatingPointError, ValueError):
            result = {"configuration": hyper, "status": "failed", "reason": "fit_or_probability_failure"}
        candidates.append(result)
    if best is None:
        return None, {"status": "failed", "candidates": candidates}
    try:
        model = fit(estimator(experiment, best["configuration"], config), x, y)
    except (AuditError, ConvergenceWarning, FloatingPointError, ValueError):
        return None, {"status": "failed", "candidates": candidates, "reason": "final_train_fit_failed"}
    return model, {"status": "ok", "selected_configuration": best["configuration"], "candidates": candidates}


def fit_calibration(y, p, config):
    c = config["calibration"]
    q = np.clip(p, c["clip"], 1 - c["clip"])
    x = (np.log(q) - np.log1p(-q)).reshape(-1, 1)
    try:
        if np.ptp(x) == 0:
            return None
        model = fit(LogisticRegression(penalty=c["penalty"], solver="lbfgs", max_iter=c["max_iter"], tol=c["tol"]), x, y)
        slope, intercept = float(model.coef_[0, 0]), float(model.intercept_[0])
        if not np.isfinite([slope, intercept]).all() or slope <= 0:
            return None
        return {"method": "sigmoid", "slope": slope, "intercept": intercept, "clip": c["clip"]}
    except (ConvergenceWarning, AuditError, ValueError):
        return None


def improvement(comparison, config):
    d = config["decision"]
    return (comparison["log_loss"]["difference"] <= -d["min_log_loss_improvement"]
            and comparison["log_loss"]["interval"][1] < 0
            and comparison["brier"]["difference"] <= d["max_brier_degradation"])


def choose_calibration(rows, y, base, calibrated, config):
    if calibrated is None:
        return False, None
    difference = paired_difference(rows, y, calibrated, base, config)
    return improvement(difference, config), difference


def select(rows, y, candidates, constant, config):
    decisions = []
    eligible = []
    for candidate in candidates:
        comparison = paired_difference(rows, y, candidate["probabilities"], constant, config)
        accepted = improvement(comparison, config)
        decisions.append({"model": candidate["id"], "comparison_with_constant": comparison, "eligible": accepted})
        if accepted:
            eligible.append(candidate)
    if not eligible:
        return None, {"status": "no_candidate", "candidate_checks": decisions,
                      "reason": "No candidate passed predeclared reference and numerical checks"}
    best = min(eligible, key=lambda c: metrics(y, c["probabilities"], config)["log_loss"])
    comparisons = []
    chosen = best
    d = config["decision"]
    for candidate in eligible:  # Protocol order is the declared complexity order.
        diff = paired_difference(rows, y, candidate["probabilities"], best["probabilities"], config)
        competitive = (diff["log_loss"]["difference"] < d["min_log_loss_improvement"]
                       or diff["log_loss"]["interval"][0] <= 0 <= diff["log_loss"]["interval"][1])
        competitive &= diff["brier"]["difference"] <= d["max_brier_degradation"]
        comparisons.append({"model": candidate["id"], "comparison_with_best": diff, "competitive": bool(competitive)})
        if competitive:
            chosen = candidate
            break
    return chosen, {"status": "frozen_candidate", "selected_model": chosen["id"],
                    "lowest_log_loss_model": best["id"], "candidate_checks": decisions,
                    "simplicity_checks": comparisons, "test_status": "unopened",
                    "rationale": "Use simplest reference-improving pipeline competitive under the predeclared paired rules"}
