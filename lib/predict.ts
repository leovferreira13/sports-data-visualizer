import inference from "../model/inference-contract.json";
import { extractMetricFeatures, extractScenarioFeatures, type FeatureResult, type UnsupportedReason } from "./features";
import { isLoadedModel, predictVector, type ValidatedModel } from "./model";

export type PredictionResult = {
  status: "ok"; source: "learned-model"; probability: number;
  artifactId: string; modelVersion: string; contractVersion: string; usedFeatures: readonly string[];
  metadata: Extract<FeatureResult, { status: "ok" }>["metadata"];
  warnings: readonly ("represented_scene_not_empirical_support" | "zero_defender_support_unestablished")[];
} | {
  status: "ok"; source: "penalty-convention"; probability: 0.76;
  conventionId: string; learned: false;
} | { status: "unsupported"; reason: UnsupportedReason }
  | { status: "unavailable"; reason: "missing_model" | "invalid_model" | "numeric_failure" };

function penalty(value: unknown, key: string): boolean {
  return typeof value === "object" && value !== null && !Array.isArray(value)
    && Object.getPrototypeOf(value) === Object.prototype
    && (value as Record<string, unknown>)[key] === "penalty";
}
function convention(): PredictionResult {
  return { status: "ok", source: "penalty-convention", probability: 0.76,
    conventionId: inference.penalty_convention, learned: false };
}
function learned(features: FeatureResult, model?: ValidatedModel): PredictionResult {
  if (features.status !== "ok") return { status: "unsupported", reason: features.reason };
  if (model === undefined) return { status: "unavailable", reason: "missing_model" };
  if (!isLoadedModel(model)) return { status: "unavailable", reason: "invalid_model" };
  const probability = predictVector(features.vector, model);
  if (probability === null) return { status: "unavailable", reason: "numeric_failure" };
  const warnings: Extract<PredictionResult, { source: "learned-model" }>["warnings"][number][] = [];
  if (features.metadata.observation !== "embedded-frame") warnings.push("represented_scene_not_empirical_support");
  if (features.vector[3] === 0) warnings.push("zero_defender_support_unestablished");
  return { status: "ok", source: "learned-model", probability, artifactId: model.artifactId,
    modelVersion: model.modelVersion, contractVersion: model.contractVersion, usedFeatures: model.usedFeatures,
    metadata: features.metadata, warnings };
}

export function predictScenario(value: unknown, model?: ValidatedModel): PredictionResult {
  if (penalty(value, "shotType")) return convention();
  return learned(extractScenarioFeatures(value), model);
}
export function predictMetricScene(value: unknown, model?: ValidatedModel): PredictionResult {
  if (penalty(value, "shot_type")) return convention();
  return learned(extractMetricFeatures(value), model);
}
