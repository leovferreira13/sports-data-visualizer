import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import fixtures from "../tests/fixtures/inference-models.json";
import inference from "../model/inference-contract.json";
import schema from "../model/model-artifact.schema.json";
import protocol from "../model/training-protocol.json";
import { extractMetricFeatures, extractScenarioFeatures } from "./features";
import { isLoadedModel, loadModel, predictVector, type ValidatedModel } from "./model";
import { predictMetricScene, predictScenario } from "./predict";
import { getPreset, presetIds } from "./presets";
import { FIELD } from "./scenario";

function loaded(value: unknown = fixtures[6].envelope) {
  const result = loadModel(value);
  if (result.status !== "ready") throw new Error(result.reason);
  return result.model;
}
function probability(value: unknown, model = loaded()) {
  const result = predictScenario(value, model);
  expect(result.status).toBe("ok");
  if (result.status !== "ok") throw new Error(result.reason);
  return result.probability;
}
const base = getPreset("centralChance");
const metric = { contract_version: "positional-features/v1", shot_type: "open-play", shooter: base.players.shooter,
  goalkeepers: [base.players.goalkeeper], defenders: [base.players.defender1, base.players.defender2], observation: "synthetic" };

describe("artifact loading", () => {
  it("pins contract bytes and supported schema keywords", () => {
    expect(inference.feature_contract_sha256).toBe(createHash("sha256").update(readFileSync("model/feature-contract.json")).digest("hex"));
    expect(inference).toMatchObject({ version: "browser-inference/v1", max_trees: protocol.xgboost.n_estimators,
      max_depth: Math.max(...protocol.xgboost.max_depth), max_nodes_per_tree: 2 ** (Math.max(...protocol.xgboost.max_depth) + 1) - 1,
      penalty_probability: .76, penalty_convention: "penalty-fixed-0.76/v1" });
    const supported = new Set(["$schema", "type", "additionalProperties", "properties", "required", "const", "enum", "oneOf",
      "minItems", "maxItems", "items", "uniqueItems", "pattern", "minimum", "maximum", "exclusiveMinimum"]);
    function walk(s: Record<string, unknown>) {
      for (const [key, value] of Object.entries(s)) {
        expect(supported.has(key), `Unimplemented schema keyword ${key}`).toBe(true);
        if (key === "properties") Object.values(value as Record<string, Record<string, unknown>>).forEach(walk);
        if (key === "items" || key === "additionalProperties" && typeof value === "object") walk(value as Record<string, unknown>);
        if (key === "oneOf") (value as Record<string, unknown>[]).forEach(walk);
      }
    }
    walk(schema);
  });
  it("loads all model kinds and calibrators and captures immutable parameters", () => {
    for (const f of fixtures) expect(loaded(f.envelope).modelVersion).toBe(f.envelope.model_version);
    const raw = structuredClone(fixtures[6].envelope);
    const model = loaded(raw), before = probability(base, model);
    raw.parameters.base_margin = 100;
    expect(probability(base, model)).toBe(before);
    expect(Object.isFrozen(model)).toBe(true);
    expect(Object.isFrozen(model.usedFeatures)).toBe(true);
    expect(isLoadedModel({ ...model })).toBe(false);
  });
  it("rejects incompatible mappings, nonfinite values, malformed metadata and preprocessing", () => {
    const mutations: ((v: Record<string, unknown>) => void)[] = [
      v => { v.schema_version = 2; }, v => { v.feature_contract_sha256 = "a".repeat(64); },
      v => { v.feature_order = [...fixtures[6].envelope.feature_order].reverse(); },
      v => { v.feature_indices = [0, 1, 2]; }, v => { v.objective = "regression"; },
      v => { v.artifact_id = "bad"; }, v => { v.provenance = {}; }, v => { v.licensing = null; },
      v => { v.export_tolerance = 1; }, v => { v.calibration = { method: "sigmoid", slope: -1, intercept: 0, clip: 1e-12 }; },
      v => { (v.parameters as Record<string, unknown>).base_margin = Infinity; },
      v => { v.unexpected = true; }, v => { v.parameters = { kind: "logistic", mean: [0], scale: [0], coefficients: [1], intercept: 0 }; },
    ];
    for (const mutate of mutations) {
      const raw = structuredClone(fixtures[6].envelope) as Record<string, unknown>;
      mutate(raw);
      expect(loadModel(raw).status).toBe("invalid");
    }
    for (const scale of [0, -1, NaN]) {
      const raw = structuredClone(fixtures[0].envelope);
      raw.parameters.scale![0] = scale;
      expect(loadModel(raw).status).toBe("invalid");
    }
    const cyclic: Record<string, unknown> = {};
    cyclic.self = cyclic;
    expect(loadModel(cyclic).status).toBe("invalid");
  });
  it("rejects cycles, missing children, shared/unreachable nodes, excessive trees and depth", () => {
    for (const child of [0, 99, -1, 1.5]) {
      const raw = structuredClone(fixtures[6].envelope);
      raw.parameters.trees![0][0].left = child;
      expect(loadModel(raw).status).toBe("invalid");
    }
    const shared = structuredClone(fixtures[6].envelope);
    shared.parameters.trees![0][0].right = 1;
    expect(loadModel(shared).status).toBe("invalid");
    const unused = structuredClone(fixtures[6].envelope);
    unused.parameters.trees![0].push({ leaf: 0 });
    expect(loadModel(unused).status).toBe("invalid");
    const oversized = structuredClone(fixtures[6].envelope);
    oversized.parameters.trees = Array.from({ length: 300 }, () => [{ leaf: Math.fround(.01) }]);
    expect(loadModel(oversized).status).toBe("ready");
    oversized.parameters.trees = Array.from({ length: 301 }, () => [{ leaf: 0 }]);
    expect(loadModel(oversized).status).toBe("invalid");
    const deep = structuredClone(fixtures[6].envelope);
    deep.parameters.trees = [[
      { feature: 0, threshold: 21, left: 1, right: 8 }, { feature: 0, threshold: 21, left: 2, right: 7 },
      { feature: 0, threshold: 21, left: 3, right: 6 }, { feature: 0, threshold: 21, left: 4, right: 5 },
      { leaf: 0 }, { leaf: 0 }, { leaf: 0 }, { leaf: 0 }, { leaf: 0 },
    ]];
    expect(loadModel(deep).status).toBe("invalid");
  });
});

describe("learned inference", () => {
  it("returns bounded identified predictions for all supported presets", () => {
    for (const f of fixtures) for (const id of presetIds.filter(id => id !== "penalty")) {
      const result = predictScenario(getPreset(id), loaded(f.envelope));
      expect(result).toMatchObject({ status: "ok", source: "learned-model", artifactId: f.envelope.artifact_id });
      if (result.status === "ok") expect(result.probability).toBeGreaterThanOrEqual(0);
      if (result.status === "ok") expect(result.probability).toBeLessThanOrEqual(1);
    }
  });
  it("has independent scaling, float32 threshold and calibration oracles", () => {
    const vector = [21, 20, 0, 2, 1, 5, 3, 18];
    const logistic = fixtures[0].envelope.parameters;
    const margin = logistic.intercept! + vector.slice(0, 3).reduce((sum, x, i) => sum
      + (x - logistic.mean![i]) / logistic.scale![i] * logistic.coefficients![i], 0);
    expect(predictVector(vector, loaded(fixtures[0].envelope))).toBeCloseTo(1 / (1 + Math.exp(-margin)), 14);
    // At threshold, strict < selects the right leaf. Adjacent JS doubles round to the same float32.
    const p = fixtures[6].envelope.parameters;
    const expectedMargin = Math.fround(Math.fround(p.base_margin! + Math.fround(-.2)) + Math.fround(.15));
    const expected = Math.fround(1 / (1 + Math.exp(-expectedMargin)));
    expect(predictVector(vector, loaded())).toBe(expected);
    const adjacentDouble = 21 - Number.EPSILON * 16;
    expect(adjacentDouble).toBeLessThan(21);
    expect(predictVector([adjacentDouble, ...vector.slice(1)], loaded())).toBe(expected);
    expect(predictVector([20.999998092651367, ...vector.slice(1)], loaded())).not.toBe(expected);
    const c = fixtures[7].envelope.calibration;
    const calibrated = 1 / (1 + Math.exp(-(c.slope! * (Math.log(expected) - Math.log1p(-expected)) + c.intercept!)));
    expect(predictVector(vector, loaded(fixtures[7].envelope))).toBeCloseTo(calibrated, 14);
  });
  it("keeps stable extremes and fails on nonfinite intermediate arithmetic", () => {
    for (const intercept of [-1000, 1000]) {
      const raw = structuredClone(fixtures[0].envelope);
      raw.parameters.intercept = intercept;
      const value = probability(base, loaded(raw));
      expect(Number.isFinite(value)).toBe(true);
      expect(value).toBe(intercept < 0 ? 0 : 1);
      const calibrated = structuredClone(fixtures[1].envelope);
      calibrated.parameters.intercept = intercept;
      const calibratedValue = probability(base, loaded(calibrated));
      expect(Number.isFinite(calibratedValue)).toBe(true);
      expect(calibratedValue).toBeGreaterThan(0);
      expect(calibratedValue).toBeLessThan(1);
    }
    const raw = structuredClone(fixtures[0].envelope);
    raw.parameters.coefficients![0] = Number.MAX_VALUE;
    expect(predictScenario(base, loaded(raw))).toEqual({ status: "unavailable", reason: "numeric_failure" });
  });
  it("preserves omitted-group, attacker, order and reflection invariants", () => {
    const changed = structuredClone(base);
    changed.players.goalkeeper = { x: 60, y: 40 };
    for (const i of [0, 2]) expect(probability(changed, loaded(fixtures[i].envelope))).toBe(probability(base, loaded(fixtures[i].envelope)));
    changed.players.defender1 = { x: 95, y: 34 };
    changed.extraDefenders.push({ x: 91, y: 34 });
    expect(probability(changed, loaded(fixtures[0].envelope))).toBe(probability(base, loaded(fixtures[0].envelope)));
    const attacker = structuredClone(base);
    attacker.extraAttackers.push({ x: 95, y: 20 });
    expect(predictScenario(attacker, loaded())).toEqual(predictScenario(base, loaded()));
    const reversed = { ...metric, defenders: [...metric.defenders].reverse() };
    expect(predictMetricScene(reversed, loaded())).toEqual(predictMetricScene(metric, loaded()));
    const reflected = { ...metric, shooter: { ...metric.shooter, y: 68 - metric.shooter.y },
      goalkeepers: metric.goalkeepers.map(p => ({ ...p, y: 68 - p.y })), defenders: metric.defenders.map(p => ({ ...p, y: 68 - p.y })) };
    expect(predictMetricScene(reflected, loaded())).toEqual(predictMetricScene(metric, loaded()));
  });
  it("classifies invalid scenes and unavailable/forged models without a probability", () => {
    expect(predictScenario(base)).toEqual({ status: "unavailable", reason: "missing_model" });
    expect(predictScenario(base, {} as ValidatedModel)).toEqual({ status: "unavailable", reason: "invalid_model" });
    for (const change of [{ goalkeepers: [] }, { goalkeepers: [metric.goalkeepers[0], metric.goalkeepers[0]] },
      { defenders: null }, { defenders: Array(11).fill(metric.defenders[0]) }, { shooter: { x: 105, y: 34 } },
      { shooter: { x: NaN, y: 34 } }, { shooter: { x: 84, y: Infinity } }, { shooter: { x: -1, y: 34 } },
      { shot_type: "header" }, { contract_version: "v2" }]) {
      const result = predictMetricScene({ ...metric, ...change }, loaded());
      expect(result.status).toBe("unsupported");
      expect(result).not.toHaveProperty("probability");
    }
    const empty = predictMetricScene({ ...metric, defenders: [] }, loaded());
    expect(empty).toMatchObject({ status: "ok", warnings: ["represented_scene_not_empirical_support", "zero_defender_support_unestablished"] });
    const features = extractMetricFeatures({ ...metric, defenders: [] });
    if (features.status === "ok") expect(features.vector[5]).toBe(Math.hypot(FIELD.length, FIELD.width));
    expect(extractScenarioFeatures(base).status).toBe("ok");
  });
});

it("routes penalties without a model or geometry and labels the invariant convention", () => {
  const expected = { status: "ok", source: "penalty-convention", probability: .76,
    conventionId: "penalty-fixed-0.76/v1", learned: false };
  expect(predictScenario({ shotType: "penalty" })).toEqual(expected);
  expect(predictMetricScene({ shot_type: "penalty" })).toEqual(expected);
  const preset = getPreset("penalty");
  for (const model of [undefined, loaded(), {} as ValidatedModel]) {
    expect(predictScenario(preset, model)).toEqual(expected);
    const moved = structuredClone(preset);
    for (const p of Object.values(moved.players)) { p.x = 55; p.y = 2; }
    expect(predictScenario(moved, model)).toEqual(expected);
  }
  for (const value of [null, [], { shotType: "unknown" }]) expect(predictScenario(value).status).toBe("unsupported");
});
