"""Invented preset and controlled scene probes; no source examples."""

import copy

import numpy as np

from features import extract_metric_features
from ingest_statsbomb import AuditError
from model_export import predict_envelope
from run_io import PROJECT, read_json


def scenes():
    presets = read_json(PROJECT / "tests/fixtures/training-presets.json")
    result = copy.deepcopy(presets)
    base = presets[0]["scene"]
    changes = {
        "zero_defenders": {"defenders": []},
        "one_defender": {"defenders": base["defenders"][:1]},
        "added_defender": {"defenders": base["defenders"] + [{"x": 91, "y": 34}]},
        "cone_inside": {"defenders": [{"x": 96, "y": 34}, base["defenders"][1]]},
        "cone_outside": {"defenders": [{"x": 96, "y": 44}, base["defenders"][1]]},
        "nearest_defender": {"defenders": [{"x": 85, "y": 34}, base["defenders"][1]]},
        "keeper_advanced": {"goalkeepers": [{"x": 91, "y": 34}]},
        "keeper_lateral": {"goalkeepers": [{"x": 102, "y": 40}]},
        "keeper_extreme": {"goalkeepers": [{"x": 45, "y": 34}]},
        "coincident_defender": {"defenders": [base["shooter"]]},
        "near_goal": {"shooter": {"x": 104.99, "y": 34}},
        "full_pitch_corner": {"shooter": {"x": 0, "y": 0}},
        "missing_keeper": {"goalkeepers": []},
        "invalid_coordinate": {"shooter": {"x": -1, "y": 34}},
        "goal_line": {"shooter": {"x": 105, "y": 34}},
        "reordered_defenders": {"defenders": list(reversed(base["defenders"]))},
    }
    for name, change in changes.items():
        result.append({"name": name, "scene": {**copy.deepcopy(base), **copy.deepcopy(change)}})
    reflected = copy.deepcopy(base)
    for p in [reflected["shooter"], *reflected["goalkeepers"], *reflected["defenders"]]:
        p["y"] = 68 - p["y"]
    result.append({"name": "reflection", "scene": reflected})
    return result


def diagnose(envelope, training_rows):
    result, vectors, names = [], [], []
    train = np.asarray([r["vector"] for r in training_rows])
    low, high = train.min(axis=0), train.max(axis=0)
    for fixture in scenes():
        features = extract_metric_features(fixture["scene"])
        if features["status"] != "ok":
            result.append({"scene": fixture["name"], "status": "unsupported", "reason": features["reason"]})
            continue
        vector = np.array(features["vector"])
        p = float(predict_envelope(envelope, [vector], validate=False)[0])
        result.append({"scene": fixture["name"], "status": "ok", "probability": p,
                       "outside_training_marginals": bool(((vector < low) | (vector > high)).any()),
                       "zero_defender_support_unestablished": bool(vector[3] == 0),
                       "note": "Synthetic represented scene; marginal compatibility is not joint empirical support"})
        vectors.append(vector.tolist())
        names.append(fixture["name"])
    lookup = {r["scene"]: r for r in result}
    base = lookup["centralChance"]["probability"]
    tolerance = envelope["export_tolerance"]
    for name in ("reflection", "reordered_defenders"):
        if abs(lookup[name]["probability"] - base) > tolerance:
            raise AuditError("Scene invariance check failed")
    indices = envelope["feature_indices"]
    if 6 not in indices:
        for name in ("keeper_advanced", "keeper_lateral", "keeper_extreme"):
            if abs(lookup[name]["probability"] - base) > tolerance:
                raise AuditError("An omitted keeper group changed prediction")
    if 3 not in indices:
        for name in ("zero_defenders", "one_defender", "added_defender", "cone_inside", "cone_outside", "nearest_defender"):
            if abs(lookup[name]["probability"] - base) > tolerance:
                raise AuditError("An omitted defender group changed prediction")
    return result, vectors
