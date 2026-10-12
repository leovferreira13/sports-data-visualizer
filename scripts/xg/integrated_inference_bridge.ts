import { extractScenarioFeatures } from "../../lib/features";
import { predictScenario } from "../../lib/predict";
import { predictVector } from "../../lib/model";
import { loadSelectedModel } from "../../lib/selected-model";

export function evaluate(payload: {
  envelope: unknown;
  cases: { mode: "scenario" | "vector"; value: unknown }[];
}) {
  const selectedModel = loadSelectedModel(payload.envelope);
  if (selectedModel.status !== "ready")
    throw new Error("Reviewed model unavailable");
  const model = selectedModel.model;
  return {
    artifact_id: model.artifactId,
    cases: payload.cases.map((c) =>
      c.mode === "vector"
        ? { probability: predictVector(c.value, model) }
        : {
            features: extractScenarioFeatures(c.value),
            result: predictScenario(c.value, model),
          },
    ),
  };
}
