# Football, Visualized — architecture overview

**Status:** bilingual shell, playable pitch, local ingestion, positional features, offline training and browser-safe inference infrastructure implemented. Owner-run actual-candidate browser-bundle parity passed; final evaluation infrastructure is implemented; actual-corpus scientific review is accepted with limitations; distribution/product QA and guided Learn remain pending.

## Application and scene

Next.js App Router supplies pages and locale routes. A React Client Component owns the interactive scenario; TypeScript defines its shape. SVG draws the attacking half. Pointer Events move preset and added players with mouse or touch; focusable player markers support arrow-key movement.

Pointer, keyboard and preset interactions update metric scenario state, which drives geometry, SVG drawing and distance/angle labels. State uses a 105 × 68 m field with x increasing toward the attacked goal. A uniform SVG projection rotates the attacking half so the goal is at the top; SVG coordinates never become model inputs.

Six presets and a versioned, validated tab-scoped snapshot preserve positions, including added players, across reloads and locale changes. Learn will reuse this simulation. Shared feature extraction is implemented, but there is no trained prediction or public xG value yet.

## Local data and features

`scripts/xg/ingest_statsbomb.py` reads a pinned official StatsBomb checkout, audits embedded shot frames separately from optional 360 coverage, and emits deterministic local-only outputs. Source and shot rows stay private; competition-level aggregate evidence may be published. Python ingestion is not a Next.js runtime or production-build dependency.

`lib/features.ts` and `scripts/xg/features.py` independently implement the eight positional inputs in `model/feature-contract.json`. Tests execute both languages on common synthetic scenes. Observation metadata remains outside the vector. `scripts/xg/extract_features.py` materializes private immutable runs with aggregate diagnostics. The full-corpus aggregate and submitted manifest have been reviewed; the owner confirmed equality of the compared files locally. See the [feature audit](../reports/xg-feature-audit.md) for evidence and verification limits.

`scripts/xg/compare_runs.py` validates each run's manifest identity, file inventory and output hashes, then compares every declared output and the manifest byte for byte. It supports ingestion and feature runs and returns nonzero on a mismatch. Run it on two distinct completed run directories; it performs no writes.

## Offline training and browser prediction boundary

`scripts/xg/prepare_training.py` and `train_models.py` implement offline match-isolated preparation, train-only tuning, separate calibration/selection validation and frozen parameter export. A dedicated Python dependency lock and synthetic CI checks keep training outside the web runtime. The first owner-run actual-corpus artifacts passed internal review and select an XGBoost candidate; complete reproduction was confirmed by the owner. See the [training guide](reference/xg-training.md) and [execution status](../reports/xg-training-methodology.md).

Versioned aggregate evaluation evidence supplies both the generated English report and the future bilingual Methodology and results tab; held-out test outcomes are opened only by the #13 final evaluator after frozen-run verification. The owner-run final evidence now passes automated gates and aggregate review; publication QA remains pending.

`lib/model.ts` validates and captures immutable versioned parameters; `lib/predict.ts` evaluates scene features with the frozen preprocessing/calibration and returns explicit learned, convention, unsupported or unavailable results. Penalties return the separate fixed 0.76 convention. The local parity command checks the browser-safe bundle against Python and emits aggregate immutable evidence; actual parameters stay local. See the [prediction guide](reference/prediction.md). Final evaluation and rights QA in #13/#8 precede public display in #4.

Python may train and export a model offline; it is not a browser/runtime dependency. Authentication, a database and an inference API are outside v0.1 scope.

## Localization

`/br` and `/en` are implemented under `app/[locale]`, with `/br` mapped to `pt-BR` and server-loaded dictionaries. The root route selects saved cookie preference, then browser language, then English. Language selection retains the rest of the URL. Scene state stays in client memory during locale navigation and in `sessionStorage` across reloads, independently of the language cookie.

## Documentation map

Read [module references](reference/README.md) for responsibilities and contracts, and [ADRs](adr/README.md) for consequential decisions. References distinguish implemented and proposed behavior; update them as boundaries change.

`evaluate_final.py` verifies original immutable runs, records test access and emits final probability scores, match-bootstrap uncertainty, scene-support diagnostics and reviewed-data app views. Generated reports and app tables share one aggregate artifact. Automated checks never authorize publication. See the [final evaluation guide](reference/xg-final-evaluation.md) and [ADR 008](adr/008-final-evaluation-and-publication-gate.md).

## Actual-corpus final review

The owner-run final evidence passes all automated predicates and the owner reports all requested comparators PASS. Aggregate identity/provenance and report/app consistency were independently checked. Scientific evidence is accepted with sparse/extreme/preset support limitations; actual parameter/export/rights and integrated #4/#8 publication QA remain pending. See `docs/reports/xg-final-evaluation.md` and `docs/reports/xg-final-review-record.json`. Public xG remains disabled.

## Rights completion handoff

The owner assigned interface-dependent publication QA to #4. The dated #8 rights/artifact/repository completion review is in `docs/reports/statsbomb-rights-completion.md`. After its documentation is merged, #8 and the completed model epic #3 may close. Actual xG/methodology pages, final build/network content and attribution/logo QA remain mandatory in #4 before #5 publishes with owner authorization. No new training cycle or public release is authorized by this handoff.
