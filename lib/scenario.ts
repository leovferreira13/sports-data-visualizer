export const FIELD = {
  length: 105,
  width: 68,
  halfLine: 52.5,
  goalWidth: 7.32,
  centerY: 34,
  markerRadius: 1.4,
} as const;

export const playerIds = ["shooter", "goalkeeper", "defender1", "defender2"] as const;
export type PlayerId = (typeof playerIds)[number];
export type Point = { x: number; y: number };
export type ShotType = "open-play" | "penalty";
export type Scenario = {
  shotType: ShotType;
  players: Record<PlayerId, Point>;
};

export const goalPosts: readonly [Point, Point] = [
  { x: FIELD.length, y: FIELD.centerY - FIELD.goalWidth / 2 },
  { x: FIELD.length, y: FIELD.centerY + FIELD.goalWidth / 2 },
];

export const fieldBounds = {
  xMin: FIELD.halfLine + FIELD.markerRadius,
  xMax: FIELD.length - FIELD.markerRadius,
  yMin: FIELD.markerRadius,
  yMax: FIELD.width - FIELD.markerRadius,
};

export function clampPosition(point: Point): Point {
  return {
    x: Number.isFinite(point.x)
      ? Math.min(fieldBounds.xMax, Math.max(fieldBounds.xMin, point.x))
      : fieldBounds.xMin,
    y: Number.isFinite(point.y)
      ? Math.min(fieldBounds.yMax, Math.max(fieldBounds.yMin, point.y))
      : FIELD.centerY,
  };
}

export function movePlayer(scenario: Scenario, id: PlayerId, point: Point): Scenario {
  return {
    ...scenario,
    players: { ...scenario.players, [id]: clampPosition(point) },
  };
}

export function isValidPosition(value: unknown): value is Point {
  if (typeof value !== "object" || value === null) return false;
  const point = value as Record<string, unknown>;
  return (
    typeof point.x === "number" &&
    typeof point.y === "number" &&
    Number.isFinite(point.x) &&
    Number.isFinite(point.y) &&
    point.x >= fieldBounds.xMin &&
    point.x <= fieldBounds.xMax &&
    point.y >= fieldBounds.yMin &&
    point.y <= fieldBounds.yMax
  );
}
