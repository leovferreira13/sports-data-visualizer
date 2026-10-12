# Football, Visualized — architecture overview

**Release preparation (2026-10-12):** an existing Railway Node deployment is publicly accessible. #26 adds explicit public binding, Git-free installation compatibility and remote release/browser QA, with production settings staged on the existing service. Final metadata/branding/public-repository gates remain open. See [Railway deployment](reference/railway-deployment.md) and [release QA](../reports/public-release-qa.md).

**Status:** five-language shell, playable pitch, local ingestion, positional features, offline training and browser-safe inference infrastructure implemented. Locally executed actual-candidate browser-bundle parity passed; final evaluation infrastructure is implemented; actual-corpus scientific review is accepted with limitations; integrated product QA is recorded in #4; exact asset-guidance/public-release checks and guided Learn remain pending.

## Application and scene

Next.js App Router supplies pages and locale routes. A React Client Component owns the interactive scenario; TypeScript defines its shape. SVG draws the attacking half. Pointer Events move preset and added players with mouse or touch; focusable player markers support arrow-key movement.

Pointer, keyboard and preset interactions update metric scenario state, which drives geometry, SVG drawing and distance/angle labels. State uses a 105 × 68 m field with x increasing toward the attacked goal. A uniform SVG projection rotates the attacking half so the goal is at the top; SVG coordinates never become model inputs.

Six presets and a versioned, validated tab-scoped snapshot preserve positions, including added players, across reloads and locale changes. Learn will reuse this simulation. Shared features drive the integrated reviewed XGBoost estimate. v3 snapshots support deliberate defender removal; the fitted feature contract is unchanged.

## Local data and features

`scripts/xg/ingest_statsbomb.py` reads a pinned official StatsBomb checkout, audits embedded shot frames separately from optional 360 coverage, and emits deterministic local-only outputs. Source and shot rows stay private; competition-level aggregate evidence may be published. Python ingestion is not a Next.js runtime or production-build dependency.

`lib/features.ts` and `scripts/xg/features.py` independently implement the eight positional inputs in `model/feature-contract.json`. Tests execute both languages on common synthetic scenes. Observation metadata remains outside the vector. `scripts/xg/extract_features.py` materializes private immutable runs with aggregate diagnostics. The full-corpus aggregate and submitted manifest have been reviewed; equality of the compared files was reported locally. See the [feature audit](../reports/xg-feature-audit.md) for evidence and verification limits.

`scripts/xg/compare_runs.py` validates each run's manifest identity, file inventory and output hashes, then compares every declared output and the manifest byte for byte. It supports ingestion and feature runs and returns nonzero on a mismatch. Run it on two distinct completed run directories; it performs no writes.

## Offline training and browser prediction boundary

`scripts/xg/prepare_training.py` and `train_models.py` implement offline match-isolated preparation, train-only tuning, separate calibration/selection validation and frozen parameter export. A dedicated Python dependency lock and synthetic CI checks keep training outside the web runtime. The first locally executed actual-corpus artifacts passed internal review and select an XGBoost candidate; complete reproduction was reported locally. See the [training guide](reference/xg-training.md) and [execution status](../reports/xg-training-methodology.md).

Versioned aggregate evaluation evidence supplies both the generated English report and the implemented five-language Methodology and results section; held-out test outcomes are opened only by the #13 final evaluator after frozen-run verification. The locally executed final evidence now passes automated gates and aggregate review; publication QA remains pending.

`lib/model.ts` validates and captures immutable versioned parameters; `lib/predict.ts` evaluates scene features with the frozen preprocessing/calibration and returns explicit learned, convention, unsupported or unavailable results. Penalties return the separate fixed 0.76 convention. The local parity command checks the browser-safe bundle against Python and emits aggregate immutable evidence; the original parity harness does not emit parameters; #4 now serves the separately reviewed static artifact. See the [prediction guide](reference/prediction.md). Scientific/rights dispositions from #13/#8 authorize integration within the recorded scope; #4 records local product QA; #26 owns authorized public release and live checks.

Python may train and export a model offline; it is not a browser/runtime dependency. Authentication, a database and an inference API are outside v0.1 scope.

## Localization

`/br`, `/en`, `/nl`, `/es` and `/de` are implemented under `app/[locale]`, with `/br` mapped to `pt-BR` and server-loaded dictionaries. The root route selects saved cookie preference, then browser language, then English. Language selection retains the rest of the URL. Scene state stays in client memory during locale navigation and in `sessionStorage` across reloads, independently of the language cookie.

## Documentation map

Read [module references](reference/README.md) for responsibilities and contracts, and [ADRs](adr/README.md) for consequential decisions. References distinguish implemented and proposed behavior; update them as boundaries change.

`evaluate_final.py` verifies original immutable runs, records test access and emits final probability scores, match-bootstrap uncertainty, scene-support diagnostics and reviewed-data app views. Generated reports and app tables share one aggregate artifact. Automated checks never authorize publication. See the [final evaluation guide](reference/xg-final-evaluation.md) and [ADR 008](adr/008-final-evaluation-and-publication-gate.md).

## Integrated product and release boundary

The reviewed parameter envelope is fetched as an exact hash-checked static asset. Desktop places pitch left and current xG/eight live cards right; mobile uses a sticky result strip bounded by the Playground. Methodology/results follows the pitch on the same locale page. Position inputs complement mouse/touch/keyboard controls. Support explanations remain in Methodology; no last-change or technical-links promotional panel is rendered.

#3/#8 scoped reviews are complete. #4 records local production QA and #24 records the five-language extension. The exact current per-asset logo guidance remains a #26 release check. No public deployment is implied by local evidence; private-row reproduction was reported locally, while submitted aggregate/provenance consistency was independently inspected.

## Portfolio and metadata

`lib/project.ts` holds confirmed identity/links; the page renders a compact localized author line. `lib/portfolio-metadata.ts` builds the locale metadata from dictionary copy and an explicit build-time `SITE_URL`. Configured HTTPS origins enable canonical/hreflang/social image URLs and indexing; absent origins omit those URLs and disable indexing. `app/robots.ts`, `app/sitemap.ts` and `app/icon.svg` supply metadata routes/assets. See [portfolio presentation](reference/portfolio-presentation.md).

#25 prepares the README/presentation/editorial work; #26 provides Railway hosting, final live links, refreshed release QA and deployed preview validation. Optional Learn remains deferred in #5. This boundary adds no inference service, database or scene persistence change.

## Offline behavior research

#31 uses `model/behavior-protocol.json`, a separate historical-reference loader and immutable `behavior-research` runs to compare frozen full logistic/current XGBoost with a bounded monotonic tree family. Dense sweeps distinguish isolated partial directions, multi-feature physical paths, support and count transitions. Optional genuinely unused matches must be reserved before fitting and opened once against the frozen choice. The shared loader accepts the research model identity for parity, but production asset selection and publication gates are unchanged. Actual-corpus phase A is reviewed as exploratory evidence, with full reproduction reported locally and the original retain-current decision preserved. Detailed current-versus-monotonic comparison is deferred to #34, prioritizing isolated direction compliance; no phase B or replacement is authorized by this disposition. See [the research guide](reference/xg-behavior.md) and [ADR 010](adr/010-xg-behavior-research-boundary.md).
