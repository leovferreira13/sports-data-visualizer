import {
  extractScenarioFeatures,
  featureNames,
  type FeatureName,
} from "./features";
import type { PredictionResult } from "./predict";
import type { Scenario } from "./scenario";

export type Comparison = {
  before: number;
  after: number;
  delta: number;
  changed: FeatureName[];
  kind: "plateau" | "below-resolution" | "changed" | "omitted" | "convention";
};

export function compareScenes(
  before: Scenario,
  after: Scenario,
  a: PredictionResult,
  b: PredictionResult,
): Comparison | null {
  if (a.status !== "ok" || b.status !== "ok" || a.source !== b.source)
    return null;
  if (
    a.source === "learned-model" &&
    b.source === "learned-model" &&
    a.artifactId !== b.artifactId
  )
    return null;
  const first = extractScenarioFeatures(before),
    last = extractScenarioFeatures(after);
  const changed =
    first.status === "ok" && last.status === "ok"
      ? featureNames.filter(
          (name) => first.features[name] !== last.features[name],
        )
      : [];
  const delta = b.probability - a.probability;
  const kind =
    a.source === "penalty-convention"
      ? "convention"
      : delta === 0
        ? changed.length
          ? "plateau"
          : "omitted"
        : Math.abs(delta * 100) < 0.05
          ? "below-resolution"
          : "changed";
  return { before: a.probability, after: b.probability, delta, changed, kind };
}

export function probabilityLabels(probability: number, locale: string) {
  const xg = new Intl.NumberFormat(locale, {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
  const percent = new Intl.NumberFormat(locale, {
    style: "percent",
    minimumFractionDigits: 1,
    maximumFractionDigits: 1,
  });
  return {
    xg:
      probability > 0 && probability < 0.005
        ? `< ${xg.format(0.005)}`
        : xg.format(probability),
    percent:
      probability > 0 && probability < 0.0005
        ? `< ${percent.format(0.0005)}`
        : percent.format(probability),
  };
}
