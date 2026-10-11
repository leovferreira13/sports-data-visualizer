import contract from "../model/feature-contract.json";
import { shotAngle, shotDistance } from "./geometry";
import { FIELD, fieldBounds, goalPosts, type Point } from "./scenario";

export const featureNames = [
  "shot_distance_m", "goal_opening_angle_deg", "absolute_lateral_offset_m",
  "visible_defender_count", "defenders_in_cone_count",
  "nearest_visible_defender_distance_m", "goalkeeper_distance_to_goal_m",
  "goalkeeper_distance_to_shot_m",
] as const;
export type FeatureName = typeof featureNames[number];
export type Observation = "synthetic" | "embedded-frame" | "browser-scene";
export type MetricScene = {
  contract_version: string;
  shot_type: string;
  shooter: Point;
  goalkeepers: Point[];
  defenders: Point[];
  observation: Observation;
};
export type UnsupportedReason =
  | "invalid_scene" | "contract_version" | "penalty_separate_route"
  | "unsupported_shot_type" | "invalid_shooter" | "goal_line_shot"
  | "missing_goalkeeper" | "multiple_goalkeepers" | "invalid_goalkeeper"
  | "missing_defenders" | "too_many_defenders" | "invalid_defender"
  | "invalid_observation" | "invalid_scenario" | "invalid_geometry";
export type FeatureResult = {
  status: "ok";
  contract_version: string;
  features: Record<FeatureName, number>;
  vector: number[];
  metadata: { observation: Observation; goalkeeper_visibility: "observed"; defender_visibility: "partial" | "represented" | "synthetic" };
} | { status: "unsupported"; contract_version: string; reason: UnsupportedReason };

// Drift must fail at import time rather than producing a differently interpreted vector.
if (contract.version !== "positional-features/v1"
  || contract.pitch.length_m !== FIELD.length || contract.pitch.width_m !== FIELD.width
  || contract.pitch.goal_width_m !== FIELD.goalWidth || contract.pitch.center_y_m !== FIELD.centerY
  || contract.source.length !== 120 || contract.source.width !== 80
  || contract.source.attacking_direction !== "+x" || contract.source.ingestion_schema_version !== 1
  || contract.domain.max_defenders !== 10 || contract.domain.goalkeeper_count !== 1
  || contract.domain.shot_type !== "open-play" || contract.domain.population !== "male"
  || contract.domain.body_parts.join() !== "Left Foot,Right Foot" || !contract.domain.shot_before_goal_line
  || contract.ui_bounds.x_min !== fieldBounds.xMin || contract.ui_bounds.x_max !== fieldBounds.xMax
  || contract.ui_bounds.y_min !== fieldBounds.yMin || contract.ui_bounds.y_max !== fieldBounds.yMax
  || contract.missingness.frame !== "reject-missing-empty-invalid" || contract.missingness.goalkeeper !== "reject-zero-multiple"
  || contract.missingness.zero_defenders_distance !== "pitch-diagonal" || contract.missingness.unseen_players !== "never-impute"
  || contract.cone !== "closed-finite-triangle-of-player-centers"
  || contract.tolerance.barycentric !== 1e-9
  || contract.tolerance.absolute !== 1e-9 || contract.tolerance.relative !== 1e-9
  || contract.features.map(f => f.name).join() !== featureNames.join()
  || contract.features.some((f, i) => f.type !== ([3, 4].includes(i) ? "integer" : "float")
    || f.unit !== ([3, 4].includes(i) ? "count" : i === 1 ? "degrees" : "m"))) {
  throw new Error("Unsupported positional feature contract");
}
export const featureContract = contract;

function object(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}
function point(value: unknown): value is Point {
  return object(value) && typeof value.x === "number" && typeof value.y === "number"
    && Number.isFinite(value.x) && Number.isFinite(value.y)
    && value.x >= 0 && value.x <= FIELD.length && value.y >= 0 && value.y <= FIELD.width;
}
function unsupported(reason: UnsupportedReason): FeatureResult {
  return { status: "unsupported", contract_version: contract.version, reason };
}

export function normalizeSourcePoint(value: unknown): Point | null {
  if (!Array.isArray(value) || value.length !== 2
    || value.some(v => typeof v !== "number" || !Number.isFinite(v))
    || value[0] < 0 || value[0] > contract.source.length
    || value[1] < 0 || value[1] > contract.source.width) return null;
  return { x: value[0] * FIELD.length / contract.source.length, y: value[1] * FIELD.width / contract.source.width };
}

function inCone(s: Point, d: Point): boolean {
  const [a, b] = goalPosts;
  const ax = a.x - s.x, ay = a.y - s.y;
  const bx = b.x - s.x, by = b.y - s.y;
  const dx = d.x - s.x, dy = d.y - s.y;
  const determinant = ax * by - ay * bx;
  const u = (dx * by - dy * bx) / determinant;
  const v = (ax * dy - ay * dx) / determinant;
  const epsilon = contract.tolerance.barycentric;
  return u >= -epsilon && v >= -epsilon && 1 - u - v >= -epsilon;
}

export function extractMetricFeatures(value: unknown): FeatureResult {
  if (!object(value)) return unsupported("invalid_scene");
  if (value.contract_version !== contract.version) return unsupported("contract_version");
  if (value.shot_type === "penalty") return unsupported("penalty_separate_route");
  if (value.shot_type !== "open-play") return unsupported("unsupported_shot_type");
  if (!point(value.shooter)) return unsupported("invalid_shooter");
  if (value.shooter.x >= FIELD.length) return unsupported("goal_line_shot");
  if (!Array.isArray(value.goalkeepers) || value.goalkeepers.length === 0) return unsupported("missing_goalkeeper");
  if (value.goalkeepers.length !== 1) return unsupported("multiple_goalkeepers");
  const keeper: unknown = value.goalkeepers[0];
  if (!point(keeper)) return unsupported("invalid_goalkeeper");
  if (!Array.isArray(value.defenders)) return unsupported("missing_defenders");
  if (value.defenders.length > contract.domain.max_defenders) return unsupported("too_many_defenders");
  if (!value.defenders.every(point)) return unsupported("invalid_defender");
  const defenders = value.defenders as Point[];
  if (!["synthetic", "embedded-frame", "browser-scene"].includes(value.observation as string)) return unsupported("invalid_observation");
  const observation = value.observation as Observation;
  const s = value.shooter;
  const nearest = defenders.length ? Math.min(...defenders.map(d => Math.hypot(d.x - s.x, d.y - s.y))) : Math.hypot(FIELD.length, FIELD.width);
  const vector = [shotDistance(s), shotAngle(s), Math.abs(s.y - FIELD.centerY),
    defenders.length, defenders.filter(d => inCone(s, d)).length, nearest,
    Math.hypot(FIELD.length - keeper.x, FIELD.centerY - keeper.y), Math.hypot(keeper.x - s.x, keeper.y - s.y)];
  if (!vector.every(Number.isFinite)) return unsupported("invalid_geometry");
  return {
    status: "ok", contract_version: contract.version,
    features: Object.fromEntries(featureNames.map((name, i) => [name, vector[i]])) as Record<FeatureName, number>, vector,
    metadata: { observation, goalkeeper_visibility: "observed", defender_visibility: observation === "embedded-frame" ? "partial" : observation === "browser-scene" ? "represented" : "synthetic" },
  };
}

export function extractScenarioFeatures(value: unknown): FeatureResult {
  if (!object(value)) return unsupported("invalid_scenario");
  if (value.shotType === "penalty") return unsupported("penalty_separate_route");
  if (value.shotType !== "open-play") return unsupported("unsupported_shot_type");
  if (!object(value.players) || !Array.isArray(value.extraDefenders)) return unsupported("invalid_scenario");
  return extractMetricFeatures({ contract_version: contract.version, shot_type: value.shotType,
    shooter: value.players.shooter, goalkeepers: [value.players.goalkeeper],
    defenders: [value.players.defender1, value.players.defender2, ...value.extraDefenders], observation: "browser-scene" });
}
