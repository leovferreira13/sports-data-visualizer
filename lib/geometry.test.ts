import { describe, expect, it } from "vitest";

import { fromSvg, shotAngle, shotDistance, toSvg } from "./geometry";
import { getPreset, presetIds } from "./presets";
import { initialScene, parseScene, serializeScene } from "./scenario-session";
import { addPlayer, FIELD, fieldBounds, goalPosts, maxExtraPlayers, movePlayer, playerIds, playerPosition } from "./scenario";

describe("field geometry", () => {
  it("measures a centered penalty from the same posts used by the drawing", () => {
    const shooter = getPreset("penalty").players.shooter;
    expect(shooter).toEqual({ x: 94, y: 34 });
    expect(shotDistance(shooter)).toBe(11);
    expect(shotAngle(shooter)).toBeCloseTo(
      (2 * Math.atan((FIELD.goalWidth / 2) / 11) * 180) / Math.PI,
    );
    expect(goalPosts.map(toSvg)).toEqual([
      { x: 30.34, y: 0 },
      { x: 37.66, y: 0 },
    ]);
  });

  it("changes distance and cone angle consistently for lateral and longitudinal moves", () => {
    const center = { x: 88, y: 34 };
    expect(shotDistance({ x: 95, y: 34 })).toBeLessThan(shotDistance(center));
    expect(shotAngle({ x: 95, y: 34 })).toBeGreaterThan(shotAngle(center));
    expect(shotDistance({ x: 88, y: 52 })).toBeGreaterThan(shotDistance(center));
    expect(shotAngle({ x: 88, y: 52 })).toBeLessThan(shotAngle(center));
  });

  it("projects all physical axes with equal scale and reversibly", () => {
    for (const point of [
      { x: FIELD.halfLine, y: 0 },
      { x: 94, y: 34 },
      { x: FIELD.length, y: FIELD.width },
    ]) {
      expect(fromSvg(toSvg(point))).toEqual(point);
    }
    expect(toSvg({ x: 95, y: 34 }).y - toSvg({ x: 94, y: 34 }).y).toBe(-1);
    expect(toSvg({ x: 94, y: 35 }).x - toSvg({ x: 94, y: 34 }).x).toBe(1);
  });

  it("keeps every piece within the visible playing region", () => {
    const starting = getPreset("oneOnOne");
    for (const id of playerIds) {
      const lower = movePlayer(starting, id, { x: -100, y: -100 });
      expect(lower.players[id]).toEqual({ x: fieldBounds.xMin, y: fieldBounds.yMin });
      const upper = movePlayer(starting, id, { x: 1000, y: 1000 });
      expect(upper.players[id]).toEqual({ x: fieldBounds.xMax, y: fieldBounds.yMax });
      expect(movePlayer(starting, id, { x: NaN, y: Infinity }).players[id]).toEqual({
        x: fieldBounds.xMin,
        y: FIELD.centerY,
      });
    }
  });
});

describe("presets and tab snapshot", () => {
  it("starts with a centered attack and defenders between shooter and goal", () => {
    const scene = initialScene();
    const { shooter, goalkeeper, defender1, defender2 } = scene.scenario.players;
    expect(scene.presetId).toBe("centralChance");
    expect(shooter.y).toBe(FIELD.centerY);
    expect(defender1.x).toBeGreaterThan(shooter.x);
    expect(defender2.x).toBeGreaterThan(shooter.x);
    expect(defender1.x).toBeLessThan(goalkeeper.x);
    expect(defender2.x).toBeLessThan(goalkeeper.x);
    expect(defender1.x).toBe(defender2.x);
    expect(defender1.y + defender2.y).toBe(FIELD.centerY * 2);
    expect(shotDistance(shooter)).toBeLessThan(shotDistance(getPreset("longShot").players.shooter));
  });

  it("gives each preset a distinct, valid, editable scene that resets independently", () => {
    const positions = new Set<string>();
    for (const id of presetIds) {
      const original = getPreset(id);
      const edited = movePlayer(original, "shooter", { x: 80, y: 25 });
      expect(getPreset(id)).toEqual(original);
      expect(edited).not.toBe(original);
      expect(edited.players.shooter).not.toBe(original.players.shooter);
      for (const player of playerIds) {
        expect(original.players[player].x).toBeGreaterThanOrEqual(fieldBounds.xMin);
        expect(original.players[player].x).toBeLessThanOrEqual(fieldBounds.xMax);
        expect(original.players[player].y).toBeGreaterThanOrEqual(fieldBounds.yMin);
        expect(original.players[player].y).toBeLessThanOrEqual(fieldBounds.yMax);
      }
      positions.add(JSON.stringify(original.players));
    }
    expect(positions.size).toBe(presetIds.length);
  });

  it("round-trips a changed scenario independently of language", () => {
    const state = {
      presetId: "tightAngle" as const,
      scenario: movePlayer(getPreset("tightAngle"), "defender1", { x: 90, y: 42 }),
    };
    expect(parseScene(serializeScene(state))).toEqual(state);
  });

  it("adds independent, movable players and saves them in the tab snapshot", () => {
    const base = getPreset("centralChance");
    const added = addPlayer(addPlayer(addPlayer(base, "attacker"), "attacker"), "defender");
    expect(base.extraAttackers).toHaveLength(0);
    expect(added.extraAttackers).toHaveLength(2);
    expect(added.extraDefenders).toHaveLength(1);
    expect(added.extraAttackers[0]).not.toEqual(added.extraAttackers[1]);
    const moved = movePlayer(added, "attacker-1", { x: 90, y: 20 });
    expect(playerPosition(moved, "attacker-1")).toEqual({ x: 90, y: 20 });
    expect(playerPosition(added, "attacker-1")).not.toEqual(playerPosition(moved, "attacker-1"));
    expect(parseScene(serializeScene({ presetId: "centralChance", scenario: moved }))).toEqual({ presetId: "centralChance", scenario: moved });
    let full = moved;
    for (let i = 0; i < 20; i++) full = addPlayer(full, "defender");
    expect(full.extraDefenders).toHaveLength(1);
    for (let i = 0; i < 20; i++) full = addPlayer(full, "attacker");
    expect(full.extraAttackers).toHaveLength(maxExtraPlayers.attacker);
  });

  it("reads existing v1 tab scenes with empty extra-player lists", () => {
    const { shotType, players } = getPreset("longShot");
    expect(parseScene(JSON.stringify({ version: 1, presetId: "longShot", scenario: { shotType, players } })))
      .toEqual({ presetId: "longShot", scenario: { shotType, players, extraAttackers: [], extraDefenders: [] } });
  });

  it("rejects corrupt, stale, unknown, or out-of-bounds snapshots", () => {
    const valid = JSON.parse(serializeScene(initialScene()));
    expect(parseScene("{")).toBeNull();
    expect(parseScene(null)).toBeNull();
    expect(parseScene(JSON.stringify({ ...valid, version: 4 }))).toBeNull();
    expect(parseScene(JSON.stringify({ ...valid, presetId: "unknown" }))).toBeNull();
    expect(parseScene(JSON.stringify({ ...valid, scenario: { ...valid.scenario, shotType: "penalty" } }))).toBeNull();
    expect(parseScene(JSON.stringify({ ...valid, scenario: { ...valid.scenario, extraAttackers: [{ x: 105, y: 34 }] } }))).toBeNull();
    valid.scenario.players.shooter.x = 105;
    expect(parseScene(JSON.stringify(valid))).toBeNull();
  });
});
