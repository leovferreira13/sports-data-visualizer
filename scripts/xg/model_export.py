"""Parameter-only envelope conversion and independent inference."""

import copy
import json
import math
import struct

import numpy as np
from scipy.special import expit

from features import CONTRACT_PATH, FEATURE_NAMES, VERSION
from ingest_statsbomb import AuditError, canonical, sha256

IDENTITY = {"method": "identity"}


def float32(value):
    return struct.unpack("f", struct.pack("f", float(value)))[0]


def calibration_apply(p, calibration):
    p = np.asarray(p, dtype=float)
    if calibration["method"] == "identity":
        return p
    q = np.clip(p, calibration["clip"], 1 - calibration["clip"])
    return expit(calibration["slope"] * (np.log(q) - np.log1p(-q)) + calibration["intercept"])


def export_estimator(estimator, experiment, provenance, config):
    indices = experiment["indices"]
    if experiment["kind"] == "logistic":
        scaler, fitted = estimator.named_steps["scale"], estimator.named_steps["model"]
        parameters = {"kind": "logistic", "mean": scaler.mean_.tolist(), "scale": scaler.scale_.tolist(),
                      "coefficients": fitted.coef_[0].tolist(), "intercept": float(fitted.intercept_[0])}
    else:
        # This is the documented model-save format, not a training-object snapshot/dump.
        saved = json.loads(estimator.get_booster().save_raw(raw_format="json"))
        learner = saved["learner"]
        if (saved["version"][:2] != [3, 0] or learner["objective"]["name"] != "binary:logistic"
                or learner["gradient_booster"]["name"] != "gbtree"
                or int(learner["learner_model_param"]["num_feature"]) != len(indices)):
            raise AuditError("Unsupported XGBoost save-model format")
        base = float(learner["learner_model_param"]["base_score"])
        if not 0 < base < 1:
            raise AuditError("Unsupported XGBoost base probability")
        trees = []
        raw = learner["gradient_booster"]["model"]
        if any(i != 0 for i in raw["tree_info"]):
            raise AuditError("Only single-output binary trees are supported")
        for tree in raw["trees"]:
            if (any(tree["split_type"]) or int(tree["tree_param"]["num_deleted"]) != 0
                    or int(tree["tree_param"]["size_leaf_vector"]) != 1):
                raise AuditError("Unsupported categorical, deleted or vector-leaf tree")
            nodes = []
            for i, left in enumerate(tree["left_children"]):
                if left == -1:
                    nodes.append({"leaf": float32(tree["split_conditions"][i])})
                else:
                    nodes.append({"feature": tree["split_indices"][i],
                                  "threshold": float32(tree["split_conditions"][i]),
                                  "left": left, "right": tree["right_children"][i]})
            trees.append(nodes)
        # XGBoost accumulates dense-tree margins with float32 arithmetic.
        parameters = {"kind": "xgboost", "base_margin": float32(math.log(base / (1 - base))),
                      "input_precision": "float32", "accumulator_precision": "float32", "trees": trees}
    envelope = {"schema_version": 1, "contract_version": VERSION,
                "feature_contract_sha256": sha256(CONTRACT_PATH.read_bytes()),
                "feature_order": list(FEATURE_NAMES), "feature_indices": indices,
                "model_version": experiment["id"], "objective": "binary:logistic",
                "parameters": parameters, "calibration": copy.deepcopy(IDENTITY),
                "provenance": provenance,
                "licensing": {"data": "StatsBomb Open Data; non-commercial portfolio scope; release review required",
                              "code": "Independent project implementation; no SoccerBoard code or weights",
                              "libraries": {"scikit-learn": "BSD-3-Clause", "XGBoost": "Apache-2.0"}},
                "export_tolerance": config["tolerances"][experiment["kind"] + "_export"]}
    return seal(envelope)


def seal(envelope):
    envelope = copy.deepcopy(envelope)
    envelope.pop("artifact_id", None)
    envelope["artifact_id"] = sha256(canonical(envelope).encode())
    return envelope


def validate_envelope(envelope):
    import jsonschema
    from run_io import PROJECT, read_json
    jsonschema.validate(envelope, read_json(PROJECT / "model/model-artifact.schema.json"))
    clean = {k: v for k, v in envelope.items() if k != "artifact_id"}
    indices = envelope["feature_indices"]
    if (envelope["artifact_id"] != sha256(canonical(clean).encode())
            or envelope["contract_version"] != VERSION
            or envelope["feature_contract_sha256"] != sha256(CONTRACT_PATH.read_bytes())
            or envelope["feature_order"] != list(FEATURE_NAMES)
            or indices not in [list(range(3)), list(range(6)), list(range(8))]):
        raise AuditError("Invalid model identity, feature mapping or contract")
    params = envelope["parameters"]
    expected = {"geometry_logistic": ("logistic", 3), "defenders_logistic": ("logistic", 6),
                "full_logistic": ("logistic", 8), "full_xgboost": ("xgboost", 8)}
    if (params["kind"], len(indices)) != expected[envelope["model_version"]]:
        raise AuditError("Model identity and parameters disagree")
    expected_tolerance = 1e-10 if params["kind"] == "logistic" else 1e-7
    if envelope["export_tolerance"] != expected_tolerance:
        raise AuditError("Model export tolerance drift")
    if params["kind"] == "logistic":
        if (any(len(params[k]) != len(indices) for k in ("mean", "scale", "coefficients"))
                or any(v <= 0 for v in params["scale"])):
            raise AuditError("Invalid logistic preprocessing")
    else:
        if indices != list(range(8)):
            raise AuditError("Unsupported tree feature mapping")
        for nodes in params["trees"]:
            visited = set()
            def walk(i):
                if i in visited or not 0 <= i < len(nodes):
                    raise AuditError("Invalid tree topology")
                visited.add(i)
                node = nodes[i]
                if "leaf" not in node:
                    if not 0 <= node["feature"] < len(indices):
                        raise AuditError("Invalid tree feature")
                    walk(node["left"])
                    walk(node["right"])
            walk(0)
            if len(visited) != len(nodes):
                raise AuditError("Unreachable tree nodes")
    # JSON Schema treats infinity as a number: strict serialization also protects all numeric fields.
    canonical(envelope)  # canonical uses allow_nan=False.


def predict_envelope(envelope, vectors, validate=True):
    if validate:
        validate_envelope(envelope)
    raw = np.asarray(vectors, dtype=float)
    if raw.ndim != 2 or raw.shape[1] != 8 or not np.isfinite(raw).all():
        raise AuditError("Expected finite vectors in the full contract order")
    if ((raw < 0).any() or (raw[:, 1] > 180).any() or (raw[:, 2] > 34).any()
            or (raw[:, 3] > 10).any() or (raw[:, 4] > raw[:, 3]).any()
            or not np.equal(raw[:, 3:5], np.floor(raw[:, 3:5])).all()
            or (raw[:, [0, 5, 6, 7]] > math.hypot(105, 68)).any()
            or not np.equal(raw[raw[:, 3] == 0, 5], math.hypot(105, 68)).all()):
        raise AuditError("Vector violates feature domain")
    x = raw[:, envelope["feature_indices"]]
    p = envelope["parameters"]
    if p["kind"] == "logistic":
        margin = ((x - p["mean"]) / p["scale"]) @ p["coefficients"] + p["intercept"]
        base = expit(margin)
    else:
        probabilities = []
        for row in x:
            row = [float32(v) for v in row]
            margin = p["base_margin"]
            for nodes in p["trees"]:
                i = 0
                while "leaf" not in nodes[i]:
                    node = nodes[i]
                    i = node["left"] if row[node["feature"]] < node["threshold"] else node["right"]
                margin = float32(margin + nodes[i]["leaf"])
            probability = 1 / (1 + math.exp(-margin)) if margin >= 0 else math.exp(margin) / (1 + math.exp(margin))
            probabilities.append(float32(probability))
        base = np.asarray(probabilities)
    result = calibration_apply(base, envelope["calibration"])
    if not np.isfinite(result).all() or (result < 0).any() or (result > 1).any():
        raise AuditError("Nonfinite exported prediction")
    return result
