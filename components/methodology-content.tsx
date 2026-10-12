import type { Locale } from "@/lib/i18n/config";
import { getDictionary } from "@/lib/i18n/dictionaries";
import { featureNames } from "@/lib/features";
import {
  xgEvidence,
  scientificReview,
  selectedTest,
  adverseConeSlice,
  frozenConfiguration,
  trainingPartitions,
  selectedTreeCount,
} from "@/lib/xg-evidence";

export async function MethodologyContent({ locale }: { locale: Locale }) {
  const dictionary = await getDictionary(locale),
    c = dictionary.methodology;
  const number = new Intl.NumberFormat(locale, { maximumFractionDigits: 6 });
  const integer = new Intl.NumberFormat(locale);
  const percent = new Intl.NumberFormat(locale, {
    style: "percent",
    maximumFractionDigits: 1,
  });
  const modelName = (id: string) =>
    c.models[
      id === "constant-training-prevalence"
        ? "constant"
        : (id as keyof typeof c.models)
    ];
  const interval = (values: readonly number[]) =>
    `[${values.map((v) => number.format(v)).join("; ")}]`;
  const sections = [
    "overview",
    "data",
    "features",
    "training",
    "scores",
    "calibration",
    "slices",
    "support",
    "inference",
  ] as const;
  const scoreRows = (
    rows: {
      id: string;
      metrics: {
        shots: number;
        goals: number;
        log_loss: number;
        brier: number;
      };
    }[],
  ) => (
    <div className="table-scroll" tabIndex={0}>
      <table>
        <thead>
          <tr>
            <th scope="col">{c.model}</th>
            <th scope="col">{c.shots}</th>
            <th scope="col">{c.goals}</th>
            <th scope="col">Log loss</th>
            <th scope="col">Brier</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row.id}>
              <th scope="row">{modelName(row.id)}</th>
              <td>{integer.format(row.metrics.shots)}</td>
              <td>{integer.format(row.metrics.goals)}</td>
              <td>{number.format(row.metrics.log_loss)}</td>
              <td>{number.format(row.metrics.brier)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
  const bins = xgEvidence.charts.calibration;
  const x = (value: number) => 60 + value * 420,
    y = (value: number) => 350 - value * 300;
  return (
    <section
      id="methodology"
      className="methodology"
      aria-labelledby="methodology-title"
    >
      <header className="methodology-header">
        <p className="eyebrow">{c.eyebrow}</p>
        <h2 id="methodology-title">{c.title}</h2>
        <p className="lead">{c.intro}</p>
      </header>
      <div className="methodology-layout">
        <nav
          className="methodology-index"
          aria-label={dictionary.navigation.methodology}
        >
          {sections.map((id) => (
            <a key={id} href={`#${id}`}>
              {c[`${id}Title`]}
            </a>
          ))}
        </nav>
        <article className="methodology-content">
          <section id="overview">
            <h2>{c.overviewTitle}</h2>
            <p>{c.overview}</p>
          </section>
          <section id="data">
            <h2>{c.dataTitle}</h2>
            <p>{c.data}</p>
            <a href="https://github.com/hudl/open-data">StatsBomb Open Data</a>
          </section>
          <section id="features">
            <h2>{c.featuresTitle}</h2>
            <p>{c.featuresIntro}</p>
            <div className="table-scroll" tabIndex={0}>
              <table>
                <thead>
                  <tr>
                    <th scope="col">{c.feature}</th>
                    <th scope="col">{c.rationale}</th>
                  </tr>
                </thead>
                <tbody>
                  {featureNames.map((name) => (
                    <tr key={name}>
                      <th scope="row">
                        {dictionary.playground.results.features[name]}
                      </th>
                      <td>{c.featureRationales[name]}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
          <section id="training">
            <h2>{c.trainingTitle}</h2>
            <p>{c.training}</p>
            <div className="table-scroll" tabIndex={0}>
              <table>
                <caption>{c.partitionsTitle}</caption>
                <thead>
                  <tr>
                    <th scope="col">{c.partition}</th>
                    <th scope="col">{c.matches}</th>
                    <th scope="col">{c.shots}</th>
                    <th scope="col">{c.goals}</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(trainingPartitions).map(([id, values]) => (
                    <tr key={id}>
                      <th scope="row">
                        {c.partitions[id as keyof typeof c.partitions]}
                      </th>
                      <td>{integer.format(values.matches)}</td>
                      <td>{integer.format(values.shots)}</td>
                      <td>
                        {"goals" in values
                          ? integer.format(values.goals)
                          : c.unopened}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <p>{c.selection}</p>
            <dl className="model-configuration">
              <div>
                <dt>XGBoost</dt>
                <dd>
                  {selectedTreeCount} {c.trees} · {c.depth}{" "}
                  {frozenConfiguration.max_depth} · {c.learningRate}{" "}
                  {number.format(frozenConfiguration.learning_rate!)} ·{" "}
                  {c.minChildWeight} {frozenConfiguration.min_child_weight}
                </dd>
              </div>
              <div>
                <dt>{c.calibrationLabel}</dt>
                <dd>identity</dd>
              </div>
            </dl>
          </section>
          <section id="scores">
            <h2>{c.scoresTitle}</h2>
            <p>{c.scores}</p>
            <h3>{c.validation}</h3>
            {scoreRows(
              xgEvidence.tables.validation.map((row) => ({
                id: row.id,
                metrics: row.variants.find((v) => v.calibration === "identity")!
                  .metrics,
              })),
            )}
            <h3>{c.final}</h3>
            {scoreRows(
              xgEvidence.tables.final_test.map((row) => ({
                id: row.model_version,
                metrics: row.metrics,
              })),
            )}
            <h3>{c.pairedTitle}</h3>
            <p>{c.paired}</p>
            <div className="table-scroll" tabIndex={0}>
              <table>
                <thead>
                  <tr>
                    <th scope="col">{c.reference}</th>
                    <th scope="col">{c.score}</th>
                    <th scope="col">{c.estimate}</th>
                    <th scope="col">{c.interval}</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(xgEvidence.paired).flatMap(([key, scores]) =>
                    Object.entries(scores).map(([score, v]) => (
                      <tr key={`${key}-${score}`}>
                        <th scope="row">
                          {modelName(
                            key === "selected_minus_constant"
                              ? "constant"
                              : "full_logistic",
                          )}
                        </th>
                        <td>{score === "log_loss" ? "Log loss" : "Brier"}</td>
                        <td>{number.format(v.estimate)}</td>
                        <td>{interval(v.interval)}</td>
                      </tr>
                    )),
                  )}
                </tbody>
              </table>
            </div>
          </section>
          <section id="calibration">
            <h2>{c.calibrationTitle}</h2>
            <p>{c.calibration}</p>
            <figure className="calibration-figure">
              <svg
                viewBox="0 0 520 415"
                role="img"
                aria-labelledby="calibration-chart-title calibration-chart-description"
              >
                <title id="calibration-chart-title">{c.calibrationTitle}</title>
                <desc id="calibration-chart-description">{c.calibration}</desc>
                {[0, 0.25, 0.5, 0.75, 1].map((t) => (
                  <g key={t}>
                    <line
                      className="chart-grid"
                      x1={x(0)}
                      y1={y(t)}
                      x2={x(1)}
                      y2={y(t)}
                    />
                    <text x="50" y={y(t) + 4} textAnchor="end">
                      {percent.format(t)}
                    </text>
                    <text x={x(t)} y="371" textAnchor="middle">
                      {percent.format(t)}
                    </text>
                  </g>
                ))}
                <line
                  className="chart-diagonal"
                  x1={x(0)}
                  y1={y(0)}
                  x2={x(1)}
                  y2={y(1)}
                />
                {bins
                  .filter(
                    (bin) =>
                      bin.mean_probability !== null &&
                      bin.observed_rate !== null,
                  )
                  .map((bin) => (
                    <g key={bin.lower}>
                      <line
                        className="chart-interval"
                        x1={x(bin.mean_probability!)}
                        x2={x(bin.mean_probability!)}
                        y1={y(bin.observed_interval.interval[0])}
                        y2={y(bin.observed_interval.interval[1])}
                      />
                      <circle
                        className={
                          bin.sparse
                            ? "chart-point chart-point--sparse"
                            : "chart-point"
                        }
                        cx={x(bin.mean_probability!)}
                        cy={y(bin.observed_rate!)}
                        r="4.5"
                      />
                    </g>
                  ))}
                <text x="270" y="403" textAnchor="middle">
                  {c.mean}
                </text>
                <text
                  transform="translate(14 200) rotate(-90)"
                  textAnchor="middle"
                >
                  {c.observed}
                </text>
              </svg>
              <figcaption>{c.calibration}</figcaption>
            </figure>
            <div className="table-scroll" tabIndex={0}>
              <table>
                <caption>{c.calibrationTitle}</caption>
                <thead>
                  <tr>
                    <th scope="col">{c.bin}</th>
                    <th scope="col">{c.shots}</th>
                    <th scope="col">{c.mean}</th>
                    <th scope="col">{c.observed}</th>
                    <th scope="col">{c.interval}</th>
                    <th scope="col">{c.sparse}</th>
                  </tr>
                </thead>
                <tbody>
                  {bins.map((bin) => (
                    <tr key={bin.lower}>
                      <th scope="row">
                        {percent.format(bin.lower)}–{percent.format(bin.upper)}
                      </th>
                      <td>{integer.format(bin.shots)}</td>
                      <td>
                        {bin.mean_probability === null
                          ? "—"
                          : percent.format(bin.mean_probability)}
                      </td>
                      <td>
                        {bin.observed_rate === null
                          ? "—"
                          : percent.format(bin.observed_rate)}
                      </td>
                      <td>
                        {bin.observed_interval.interval
                          .map((v) => percent.format(v))
                          .join(" – ")}
                      </td>
                      <td>{bin.sparse ? c.sparse : c.supported}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
          <section id="slices">
            <h2>{c.slicesTitle}</h2>
            <p>{c.slices}</p>
            <p>
              {c.shots}: {integer.format(adverseConeSlice.shots)} ·{" "}
              {adverseConeSlice.sparse ? c.sparse : c.supported}
            </p>
            <div className="table-scroll" tabIndex={0}>
              <table>
                <caption>XGBoost − {c.models.full_logistic}</caption>
                <thead>
                  <tr>
                    <th scope="col">{c.score}</th>
                    <th scope="col">{c.estimate}</th>
                    <th scope="col">{c.interval}</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(adverseConeSlice.paired!.full_logistic).map(
                    ([score, v]) => (
                      <tr key={score}>
                        <th scope="row">
                          {score === "log_loss" ? "Log loss" : "Brier"}
                        </th>
                        <td>{number.format(v.estimate)}</td>
                        <td>{interval(v.interval)}</td>
                      </tr>
                    ),
                  )}
                </tbody>
              </table>
            </div>
          </section>
          <section id="support">
            <h2>{c.supportTitle}</h2>
            <p>{c.support}</p>
          </section>
          <section id="inference">
            <h2>{c.inferenceTitle}</h2>
            <p>{c.inference}</p>
            <p>{c.review}</p>
            <details className="evidence-identity">
              <summary>{c.identity}</summary>
              <dl>
                <dt>{c.artifact}</dt>
                <dd>{xgEvidence.selected_artifact_id}</dd>
                <dt>{c.trainingRun}</dt>
                <dd>{xgEvidence.training_run_id}</dd>
                <dt>{c.evidence}</dt>
                <dd>{xgEvidence.evidence_id}</dd>
                <dt>
                  {c.scientificReview} · {scientificReview.review_date}
                </dt>
                <dd>{scientificReview.scientific_review}</dd>
                <dt>{c.automatedStatus}</dt>
                <dd>{xgEvidence.release_status}</dd>
                <dt>{c.publicationAuthorization}</dt>
                <dd>{String(xgEvidence.publication_authorized)}</dd>
                <dt>{c.final}</dt>
                <dd>
                  {integer.format(selectedTest.metrics.shots)} {c.shots} ·{" "}
                  {integer.format(selectedTest.metrics.goals)} {c.goals}
                </dd>
              </dl>
            </details>
          </section>
        </article>
      </div>
    </section>
  );
}
