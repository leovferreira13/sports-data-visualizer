"""Pure metric extraction and an adapter for the version-1 local ingestion corpus."""

import json
import math
from pathlib import Path

from ingest_statsbomb import POSITIONS, unique_keys

CONTRACT_PATH = Path(__file__).resolve().parents[2] / "model/feature-contract.json"
CONTRACT = json.loads(CONTRACT_PATH.read_text(), object_pairs_hook=unique_keys)
FEATURE_NAMES = (
    "shot_distance_m", "goal_opening_angle_deg", "absolute_lateral_offset_m",
    "visible_defender_count", "defenders_in_cone_count",
    "nearest_visible_defender_distance_m", "goalkeeper_distance_to_goal_m",
    "goalkeeper_distance_to_shot_m",
)
VERSION = "positional-features/v1"
PITCH = CONTRACT["pitch"]
LENGTH, WIDTH, CENTER, GOAL_WIDTH = (PITCH[k] for k in
                                    ("length_m", "width_m", "center_y_m", "goal_width_m"))
if (CONTRACT["version"] != VERSION
        or (LENGTH, WIDTH, CENTER, GOAL_WIDTH) != (105, 68, 34, 7.32)
        or CONTRACT["source"] != {"length": 120, "width": 80,
                                   "attacking_direction": "+x", "ingestion_schema_version": 1}
        or CONTRACT["domain"]["max_defenders"] != 10
        or CONTRACT["domain"]["goalkeeper_count"] != 1
        or CONTRACT["domain"]["shot_type"] != "open-play"
        or CONTRACT["domain"]["population"] != "male"
        or CONTRACT["domain"]["body_parts"] != ["Left Foot", "Right Foot"]
        or CONTRACT["domain"]["shot_before_goal_line"] is not True
        or CONTRACT["ui_bounds"] != {"x_min": 53.9, "x_max": 103.6, "y_min": 1.4, "y_max": 66.6}
        or CONTRACT["missingness"] != {"frame": "reject-missing-empty-invalid", "goalkeeper": "reject-zero-multiple",
                                       "zero_defenders_distance": "pitch-diagonal", "unseen_players": "never-impute"}
        or CONTRACT["cone"] != "closed-finite-triangle-of-player-centers"
        or CONTRACT["tolerance"]["barycentric"] != 1e-9
        or CONTRACT["tolerance"]["absolute"] != 1e-9 or CONTRACT["tolerance"]["relative"] != 1e-9
        or tuple(f["name"] for f in CONTRACT["features"]) != FEATURE_NAMES
        or any(f["type"] != ("integer" if i in (3, 4) else "float")
               or f["unit"] != ("count" if i in (3, 4) else "degrees" if i == 1 else "m")
               for i, f in enumerate(CONTRACT["features"]))):
    raise ValueError("Unsupported positional feature contract")


def unsupported(reason):
    return {"status": "unsupported", "contract_version": VERSION, "reason": reason}


def point(value):
    return (isinstance(value, dict)
            and all(type(value.get(k)) in (int, float) for k in ("x", "y"))
            and 0 <= value["x"] <= LENGTH and 0 <= value["y"] <= WIDTH
            and all(math.isfinite(value[k]) for k in ("x", "y")))


def normalize_source_point(value):
    if (not isinstance(value, list) or len(value) != 2
            or not all(type(v) in (int, float) for v in value)
            or not 0 <= value[0] <= CONTRACT["source"]["length"]
            or not 0 <= value[1] <= CONTRACT["source"]["width"]
            or not all(math.isfinite(v) for v in value)):
        return None
    return {"x": value[0] * LENGTH / CONTRACT["source"]["length"],
            "y": value[1] * WIDTH / CONTRACT["source"]["width"]}


def distance(a, b):
    return math.hypot(a["x"] - b["x"], a["y"] - b["y"])


def in_cone(s, d):
    ax, ay = LENGTH - s["x"], CENTER - GOAL_WIDTH / 2 - s["y"]
    bx, by = LENGTH - s["x"], CENTER + GOAL_WIDTH / 2 - s["y"]
    dx, dy = d["x"] - s["x"], d["y"] - s["y"]
    determinant = ax * by - ay * bx
    u = (dx * by - dy * bx) / determinant
    v = (ax * dy - ay * dx) / determinant
    epsilon = CONTRACT["tolerance"]["barycentric"]
    return u >= -epsilon and v >= -epsilon and 1 - u - v >= -epsilon


def extract_metric_features(value):
    if not isinstance(value, dict):
        return unsupported("invalid_scene")
    if value.get("contract_version") != VERSION:
        return unsupported("contract_version")
    if value.get("shot_type") == "penalty":
        return unsupported("penalty_separate_route")
    if value.get("shot_type") != "open-play":
        return unsupported("unsupported_shot_type")
    s = value.get("shooter")
    if not point(s):
        return unsupported("invalid_shooter")
    if s["x"] >= LENGTH:
        return unsupported("goal_line_shot")
    keepers = value.get("goalkeepers")
    if not isinstance(keepers, list) or not keepers:
        return unsupported("missing_goalkeeper")
    if len(keepers) != 1:
        return unsupported("multiple_goalkeepers")
    k = keepers[0]
    if not point(k):
        return unsupported("invalid_goalkeeper")
    defenders = value.get("defenders")
    if not isinstance(defenders, list):
        return unsupported("missing_defenders")
    if len(defenders) > CONTRACT["domain"]["max_defenders"]:
        return unsupported("too_many_defenders")
    if not all(point(d) for d in defenders):
        return unsupported("invalid_defender")
    observation = value.get("observation")
    if observation not in ("synthetic", "embedded-frame", "browser-scene"):
        return unsupported("invalid_observation")
    ax, ay = LENGTH - s["x"], CENTER - GOAL_WIDTH / 2 - s["y"]
    bx, by = LENGTH - s["x"], CENTER + GOAL_WIDTH / 2 - s["y"]
    angle = math.degrees(math.atan2(abs(ax * by - ay * bx), ax * bx + ay * by))
    vector = [distance(s, {"x": LENGTH, "y": CENTER}), angle, abs(s["y"] - CENTER),
              len(defenders), sum(in_cone(s, d) for d in defenders),
              min(distance(s, d) for d in defenders) if defenders else math.hypot(LENGTH, WIDTH),
              distance(k, {"x": LENGTH, "y": CENTER}), distance(k, s)]
    if not all(math.isfinite(v) for v in vector):
        return unsupported("invalid_geometry")
    return {"status": "ok", "contract_version": VERSION,
            "features": dict(zip(FEATURE_NAMES, vector)), "vector": vector,
            "metadata": {"observation": observation, "goalkeeper_visibility": "observed",
                         "defender_visibility": {"embedded-frame": "partial",
                                                 "browser-scene": "represented",
                                                 "synthetic": "synthetic"}[observation]}}


def extract_statsbomb_features(row):
    """Only accepts local base rows produced by ingestion, never raw event/360 records."""
    if not isinstance(row, dict) or type(row.get("schema_version")) is not int or row["schema_version"] != 1:
        return unsupported("ingestion_schema_version")
    # Schema 1 materializes only Open Play shots; it omits the original shot type.
    # Reject contradictory contexts if supplied, rather than accepting a penalty as a base row.
    if "shot_type" in row and row["shot_type"] != "Open Play":
        return unsupported("unsupported_shot_type")
    if row.get("body_part") not in CONTRACT["domain"]["body_parts"]:
        return unsupported("unsupported_body_part")
    s = normalize_source_point(row.get("location"))
    if s is None:
        return unsupported("invalid_shooter")
    frame = row.get("embedded_frame")
    if frame is None:
        return unsupported("missing_frame")
    if not isinstance(frame, dict):
        return unsupported("invalid_frame")
    status = frame.get("status")
    if not isinstance(status, str):
        return unsupported("invalid_frame")
    if status != "valid":
        return unsupported({"missing": "missing_frame", "empty": "empty_frame"}.get(status, "invalid_frame"))
    players = frame.get("players")
    if not isinstance(players, list):
        return unsupported("invalid_frame")
    if not players:
        return unsupported("empty_frame")
    keepers, defenders = [], []
    for player in players:
        if (not isinstance(player, dict) or type(player.get("teammate")) is not bool
                or type(player.get("keeper")) is not bool
                or not isinstance(player.get("position"), str)
                or player.get("position") not in POSITIONS
                or player["keeper"] != (player["position"] == "Goalkeeper")):
            return unsupported("invalid_role")
        p = normalize_source_point(player.get("location"))
        if p is None:
            return unsupported("invalid_player_location")
        if not player["teammate"]:
            (keepers if player["keeper"] else defenders).append(p)
    # Frame counters are diagnostics, never an alternative to examining actual roles/positions.
    return extract_metric_features({"contract_version": VERSION, "shot_type": "open-play",
                                    "shooter": s, "goalkeepers": keepers, "defenders": defenders,
                                    "observation": "embedded-frame"})
