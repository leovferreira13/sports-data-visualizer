import { spawnSync } from "node:child_process";
import { describe, expect, it } from "vitest";
import golden from "../tests/fixtures/shot-features-v1.json";
import { extractMetricFeatures, extractScenarioFeatures, featureContract, featureNames, normalizeSourcePoint, type FeatureResult } from "./features";
import { getPreset, presetIds } from "./presets";
import { FIELD } from "./scenario";

function ok(result: FeatureResult) {
  expect(result.status).toBe("ok");
  if (result.status !== "ok") throw new Error(result.reason);
  return result;
}
function close(a: number, b: number) {
  expect(Math.abs(a - b)).toBeLessThanOrEqual(featureContract.tolerance.absolute + featureContract.tolerance.relative * Math.max(Math.abs(a), Math.abs(b)));
}
const central = golden[0].scene;

describe("versioned positional extraction", () => {
  for (const fixture of golden) it(fixture.name, () => {
    const result = extractMetricFeatures(fixture.scene);
    expect(result.status).toBe(fixture.expected.status);
    if (result.status === "ok") {
      expect(Object.keys(result.features)).toEqual([...featureNames]);
      expect(result.vector).toEqual(featureNames.map(n => result.features[n]));
      expect(result.vector.every(Number.isFinite)).toBe(true);
      for (const [name, value] of Object.entries(fixture.expected.features ?? {})) close(result.features[name as typeof featureNames[number]], value);
    } else expect(result.reason).toBe(fixture.expected.reason);
  });
  it("has independent central-shot angle and zero-defender distance oracles", () => {
    close(ok(extractMetricFeatures(central)).features.goal_opening_angle_deg, 2 * Math.atan(3.66 / 21) * 180 / Math.PI);
    close(ok(extractMetricFeatures(golden.find(c => c.name === "zero-defenders")!.scene)).vector[5], Math.sqrt(105 ** 2 + 68 ** 2));
  });
  it("uses all open-play presets and routes penalties separately", () => {
    for (const id of presetIds) {
      const result = extractScenarioFeatures(getPreset(id));
      if (id === "penalty") expect(result).toMatchObject({ status: "unsupported", reason: "penalty_separate_route" });
      else expect(ok(result).metadata.defender_visibility).toBe("represented");
    }
  });
  it("responds to fixed and extra defenders and goalkeeper movement", () => {
    const scene = getPreset("centralChance");
    scene.players.defender1 = { x: 93, y: 34 };
    const before = ok(extractScenarioFeatures(scene));
    scene.players.defender1.y = 40;
    const after = ok(extractScenarioFeatures(scene));
    expect(after.vector[4]).toBe(before.vector[4] - 1);
    scene.extraDefenders.push({ x: 86, y: 34 });
    const added = ok(extractScenarioFeatures(scene));
    expect(added.vector[3]).toBe(after.vector[3] + 1);
    expect(added.vector[5]).toBe(2);
    scene.players.goalkeeper.x -= 5;
    const keeper = ok(extractScenarioFeatures(scene));
    expect(keeper.vector[6]).not.toBe(added.vector[6]);
    expect(keeper.vector[7]).not.toBe(added.vector[7]);
    scene.extraAttackers.push({ x: 80, y: 20 });
    expect(extractScenarioFeatures(scene)).toEqual(keeper);
  });
  it("is invariant to defender order and lateral reflection", () => {
    expect(extractMetricFeatures({ ...central, defenders: [...central.defenders].reverse() })).toEqual(extractMetricFeatures(central));
    const a = ok(extractMetricFeatures(golden[1].scene)), b = ok(extractMetricFeatures(golden[2].scene));
    a.vector.forEach((v, i) => close(v, b.vector[i]));
  });
  it("normalizes source positions without moving posts or clamping", () => {
    expect(normalizeSourcePoint([96, 40])).toEqual({ x: 84, y: 34 });
    expect(normalizeSourcePoint([0, 0])).toEqual({ x: 0, y: 0 });
    expect(normalizeSourcePoint([120, 80])).toEqual({ x: 105, y: 68 });
    expect(normalizeSourcePoint([120, 36])!.y).toBeCloseTo(30.6);
    expect(normalizeSourcePoint([120, 36])!.y).not.toBe(FIELD.centerY - FIELD.goalWidth / 2);
    for (const invalid of [null, [true, 40], ["96", 40], [121, 40], [96, -1], [96, NaN], [96, Infinity], [1, 2, 3]]) expect(normalizeSourcePoint(invalid)).toBeNull();
  });
  it("returns no vector for invalid and missing inputs", () => {
    const cases: [unknown, string][] = [[null, "invalid_scene"], [{ ...central, contract_version: "v2" }, "contract_version"],
      [{ ...central, shot_type: "penalty" }, "penalty_separate_route"], [{ ...central, shot_type: "header" }, "unsupported_shot_type"],
      [{ ...central, shooter: { x: true, y: 34 } }, "invalid_shooter"], [{ ...central, shooter: { x: 84, y: NaN } }, "invalid_shooter"],
      [{ ...central, shooter: { x: Infinity, y: 34 } }, "invalid_shooter"], [{ ...central, shooter: { x: -1, y: 34 } }, "invalid_shooter"],
      [{ ...central, goalkeepers: [] }, "missing_goalkeeper"], [{ ...central, goalkeepers: [central.goalkeepers[0], central.goalkeepers[0]] }, "multiple_goalkeepers"],
      [{ ...central, goalkeepers: [null] }, "invalid_goalkeeper"], [{ ...central, defenders: null }, "missing_defenders"],
      [{ ...central, defenders: [null] }, "invalid_defender"], [{ ...central, observation: "complete" }, "invalid_observation"]];
    for (const [value, reason] of cases) {
      const result = extractMetricFeatures(value);
      expect(result).toMatchObject({ status: "unsupported", reason });
      expect(result).not.toHaveProperty("vector");
    }
    expect(extractScenarioFeatures(null)).toMatchObject({ reason: "invalid_scenario" });
    expect(extractScenarioFeatures({ shotType: "open-play", players: {} })).toMatchObject({ reason: "invalid_scenario" });
  });
});

it("executes Python and TypeScript on the same golden, boundary, failure and source inputs", () => {
  const scenes: unknown[] = golden.map(c => c.scene);
  for (const change of [{ contract_version: "v2" }, { shot_type: "penalty" }, { shot_type: "other" },
    { shooter: { x: true, y: 34 } }, { shooter: { x: "84", y: 34 } }, { shooter: { x: null, y: 34 } },
    { goalkeepers: [] }, { goalkeepers: [null] }, { goalkeepers: [central.goalkeepers[0], central.goalkeepers[0]] },
    { defenders: null }, { defenders: [null] }, { observation: "complete" }]) scenes.push({ ...central, ...change });
  scenes.push(null);
  // Deterministic varied scenes extend coverage without using licensed records.
  for (let i = 0; i < 120; i++) scenes.push({ ...central, shooter: { x: 10 + i * 0.78, y: i * 7 % 68 },
    goalkeepers: [{ x: 103 - i % 20, y: i * 3 % 68 }], defenders: [{ x: i * 17 % 106, y: i * 11 % 69 }, { x: 100, y: 34 }] });
  const points = [[96, 40], [120, 36], [120, 44], [0, 80], [true, 40], [121, 0], [1, 2, 3], null];
  const cases = [...scenes.map(scene => ({ mode: "metric", scene })), ...points.map(point => ({ mode: "source_point", point }))];
  const process = spawnSync("python3", ["scripts/xg/tests/feature_parity_runner.py"], { input: JSON.stringify(cases), encoding: "utf8", timeout: 15000 });
  if (process.error) throw process.error;
  expect(process.status, process.stderr).toBe(0);
  const actual = JSON.parse(process.stdout) as unknown[];
  expect(actual).toHaveLength(cases.length);
  scenes.forEach((scene, i) => {
    const ts = extractMetricFeatures(scene), py = actual[i] as FeatureResult;
    expect(py.status).toBe(ts.status);
    if (ts.status === "ok" && py.status === "ok") {
      expect(py.contract_version).toBe(ts.contract_version);
      expect(py.metadata).toEqual(ts.metadata);
      expect(Object.keys(py.features)).toEqual([...featureNames]);
      expect(py.vector).toHaveLength(featureNames.length);
      ts.vector.forEach((value, j) => {
        if ([3, 4].includes(j)) expect(py.vector[j]).toBe(value);
        else close(py.vector[j], value);
        close(py.features[featureNames[j]], value);
      });
    } else expect(py).toEqual(ts);
  });
  points.forEach((point, i) => expect(actual[scenes.length + i]).toEqual(normalizeSourcePoint(point)));
});
