import type { Dictionary } from "@/lib/i18n/dictionaries";
import type { Locale } from "@/lib/i18n/config";
import { extractScenarioFeatures } from "@/lib/features";
import { probabilityLabels, type Comparison } from "@/lib/insights";
import type { PredictionResult } from "@/lib/predict";
import type { Scenario } from "@/lib/scenario";

type Props = {
  locale: Locale;
  copy: Dictionary["playground"]["results"];
  scenario: Scenario;
  result: PredictionResult;
  loading?: boolean;
  comparison: Comparison | null;
  originalSupport?: string;
};

export function PredictionPanel({
  locale,
  copy,
  scenario,
  result,
  loading,
  comparison,
  originalSupport,
}: Props) {
  const features = extractScenarioFeatures(scenario);
  const number = new Intl.NumberFormat(locale, { maximumFractionDigits: 1 });
  const labels =
    result.status === "ok"
      ? probabilityLabels(result.probability, locale)
      : null;
  const delta =
    comparison &&
    new Intl.NumberFormat(locale, {
      maximumFractionDigits: 1,
      minimumFractionDigits: 1,
      signDisplay: "exceptZero",
    }).format(comparison.delta * 100);
  return (
    <>
      <section
        className="prediction-card"
        aria-labelledby="estimate-title"
        data-result-status={result.status}
      >
        <p id="estimate-title" className="eyebrow">
          {result.status === "ok" && result.source === "penalty-convention"
            ? copy.penalty
            : copy.estimate}
        </p>
        {labels ? (
          <div className="prediction-value">
            <strong data-testid="xg">
              {labels.xg} <small>xG</small>
            </strong>
            <span data-testid="percentage">{labels.percent}</span>
          </div>
        ) : (
          <p role="status">
            {loading
              ? copy.loading
              : result.status === "unsupported"
                ? copy.unsupported
                : copy.unavailable}
          </p>
        )}
        <p>
          {result.status === "ok" && result.source === "penalty-convention"
            ? copy.convention
            : copy.explanation}
        </p>
      </section>
      {features.status === "ok" && (
        <details className="feature-observations">
          <summary>{copy.observations}</summary>
          <dl>
            {Object.entries(features.features).map(([name, value]) => (
              <div key={name}>
                <dt>{copy.features[name as keyof typeof copy.features]}</dt>
                <dd>
                  {name === "nearest_visible_defender_distance_m" &&
                  features.features.visible_defender_count === 0
                    ? "—"
                    : number.format(value)}
                </dd>
              </div>
            ))}
          </dl>
        </details>
      )}
      <aside className="support-note">
        <p>{copy.support}</p>
        {features.status === "ok" &&
          features.features.visible_defender_count === 0 && <p>{copy.zero}</p>}
        {originalSupport &&
          result.status === "ok" &&
          result.source === "learned-model" && (
            <p>
              {originalSupport === "outside_training_reference"
                ? copy.outside
                : originalSupport === "within_training_reference"
                  ? copy.within
                  : copy.zero}
            </p>
          )}
      </aside>
      {comparison && result.status === "ok" && (
        <section
          className="comparison-card"
          aria-live="polite"
          aria-atomic="true"
        >
          <h2>{copy.comparison}</h2>
          <dl className="comparison-values">
            <div>
              <dt>{copy.before}</dt>
              <dd>{probabilityLabels(comparison.before, locale).percent}</dd>
            </div>
            <div>
              <dt>{copy.after}</dt>
              <dd>{probabilityLabels(comparison.after, locale).percent}</dd>
            </div>
            <div>
              <dt>{copy.difference}</dt>
              <dd>
                {comparison.kind === "below-resolution"
                  ? `${comparison.delta > 0 ? "+" : "−"}< ${number.format(0.1)}`
                  : delta}
              </dd>
            </div>
          </dl>
          {comparison.kind !== "changed" && (
            <p>
              {
                copy[
                  comparison.kind === "below-resolution"
                    ? "belowResolution"
                    : comparison.kind
                ]
              }
            </p>
          )}
          {!!comparison.changed.length && (
            <p>
              {copy.changed}:{" "}
              {comparison.changed.map((name) => copy.features[name]).join("; ")}
            </p>
          )}
          <p className="muted">{copy.causality}</p>
        </section>
      )}
    </>
  );
}
