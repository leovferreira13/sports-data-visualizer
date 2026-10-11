import { extractMetricFeatures, extractScenarioFeatures } from "../../lib/features";
import { loadModel, predictVector } from "../../lib/model";
import { predictMetricScene, predictScenario } from "../../lib/predict";

type Case = { name: string; mode: "metric" | "scenario" | "vector"; value: unknown };
export function evaluate(payload: { envelope: unknown; cases: Case[] }) {
  const loaded = loadModel(payload.envelope);
  if (loaded.status !== "ready") return { loaded, cases: [] };
  return { loaded: { status: "ready", model: loaded.model }, cases: payload.cases.map(c => ({
    name: c.name,
    ...(c.mode === "vector" ? { probability: predictVector(c.value, loaded.model) }
      : { features: c.mode === "metric" ? extractMetricFeatures(c.value) : extractScenarioFeatures(c.value),
        result: c.mode === "metric" ? predictMetricScene(c.value, loaded.model) : predictScenario(c.value, loaded.model) }),
  })) };
}
