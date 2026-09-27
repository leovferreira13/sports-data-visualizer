export const FIELD = {
  length: 105,
  width: 68,
  halfLine: 52.5,
  goalWidth: 7.32,
  centerY: 34,
  markerRadius: 1.4,
} as const;

export const playerIds = ["shooter", "goalkeeper", "defender1", "defender2"] as const;
export type PlayerId = (typeof playerIds)[number] | `attacker-${number}` | `defender-${number}`;
export type Point = { x: number; y: number };
export type ShotType = "open-play" | "penalty";
export type BaseScenario = {
  shotType: ShotType;
  players: Record<(typeof playerIds)[number], Point>;
};
export type Scenario = BaseScenario & { extraAttackers: Point[]; extraDefenders: Point[] };
export const maxExtraPlayers = { attacker: 9, defender: 8 } as const;

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
  if (id.startsWith("attacker-") || id.startsWith("defender-")) {
    const attacker = id.startsWith("attacker-");
    const index = Number(id.slice(9));
    const key = attacker ? "extraAttackers" : "extraDefenders";
    if (!Number.isInteger(index) || index < 0 || index >= scenario[key].length) return scenario;
    const positions = [...scenario[key]];
    positions[index] = clampPosition(point);
    return { ...scenario, [key]: positions };
  }
  return {
    ...scenario,
    players: { ...scenario.players, [id]: clampPosition(point) },
  };
}

export function playerPosition(scenario: Scenario, id: PlayerId): Point {
  if (id.startsWith("attacker-")) return scenario.extraAttackers[Number(id.slice(9))];
  if (id.startsWith("defender-")) return scenario.extraDefenders[Number(id.slice(9))];
  return scenario.players[id as (typeof playerIds)[number]];
}

export function addPlayer(scenario: Scenario, team: "attacker" | "defender"): Scenario {
  const key = team === "attacker" ? "extraAttackers" : "extraDefenders";
  const index = scenario[key].length;
  if (index >= maxExtraPlayers[team]) return scenario;
  const shooter = scenario.players.shooter;
  const point = team === "attacker"
    ? { x: shooter.x - 4 - Math.floor(index / 2) * 3, y: shooter.y + (index % 2 ? -1 : 1) * (6 + Math.floor(index / 2) * 3) }
    : { x: (shooter.x + scenario.players.goalkeeper.x) / 2, y: FIELD.centerY + (index % 2 ? -1 : 1) * (9 + Math.floor(index / 2) * 3) };
  return { ...scenario, [key]: [...scenario[key], clampPosition(point)] };
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
