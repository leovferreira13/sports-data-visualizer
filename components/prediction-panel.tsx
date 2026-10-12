import type { Dictionary } from "@/lib/i18n/dictionaries";
import type { Locale } from "@/lib/i18n/config";
import { extractScenarioFeatures, featureNames } from "@/lib/features";
import { probabilityLabels } from "@/lib/insights";
import type { PredictionResult } from "@/lib/predict";
import type { Scenario } from "@/lib/scenario";

type Props = {
  locale: Locale;
  copy: Dictionary["playground"]["results"];
  scenario: Scenario;
  result: PredictionResult;
  loading?: boolean;
};

export function PredictionPanel({
  locale,
  copy,
  scenario,
  result,
  loading,
}: Props) {
  // Penalty cards describe positions only; the fixed convention ignores these inputs.
  const features = extractScenarioFeatures(
    scenario.shotType === "penalty"
      ? { ...scenario, shotType: "open-play" }
      : scenario,
  );
  const number = new Intl.NumberFormat(locale, { maximumFractionDigits: 1 });
  const labels =
    result.status === "ok"
      ? probabilityLabels(result.probability, locale)
      : null;
  const convention =
    result.status === "ok" && result.source === "penalty-convention";
  return (
    <>
      <section
        className="prediction-card"
        aria-labelledby="estimate-title"
        data-result-status={result.status}
      >
        <div className="estimate-heading">
          <p id="estimate-title" className="eyebrow">
            {copy.estimate}
          </p>
          <span className="model-kind">
            {convention ? copy.fixedPenalty : copy.independentModel}
          </span>
        </div>
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
        {convention && <p className="penalty-note">{copy.convention}</p>}
      </section>
      <section className="features-section" aria-labelledby="features-title">
        <h2 id="features-title">
          {convention ? copy.positionFeatures : copy.modelFeatures}
        </h2>
        <div className="feature-cards" aria-live="off">
          {featureNames.map((name) => {
            const value =
              features.status === "ok" ? features.features[name] : null;
            const missing =
              name === "nearest_visible_defender_distance_m" &&
              features.status === "ok" &&
              features.features.visible_defender_count === 0;
            const unit = [
              "visible_defender_count",
              "defenders_in_cone_count",
            ].includes(name)
              ? ""
              : name === "goal_opening_angle_deg"
                ? "°"
                : "m";
            return (
              <div
                className="feature-card"
                key={name}
                data-feature={name}
                title={copy.features[name]}
              >
                <span className="feature-name">{copy.cardLabels[name]}</span>
                <strong
                  aria-label={`${copy.features[name]}: ${missing ? copy.noDefender : value === null ? "—" : number.format(value)}`}
                >
                  <span className="feature-value">
                    {value === null || missing ? "—" : number.format(value)}
                  </span>
                  {!missing && value !== null && unit && <small>{unit}</small>}
                </strong>
                {missing && (
                  <span className="feature-note">{copy.noDefender}</span>
                )}
              </div>
            );
          })}
        </div>
      </section>
    </>
  );
}
