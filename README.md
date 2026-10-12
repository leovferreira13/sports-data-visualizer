# Football, Visualized

An interactive, bilingual playground for understanding expected goals (xG). Move the shooter, goalkeeper, and defenders to explore how shot geometry and positioning affect a model's estimate.

**Status:** bilingual reviewed-model Playground and Methodology/results implemented; optional Learn and authorized public release remain #5.

## Local development

Requirements: Node.js 20.9 or newer, npm, Python 3.10 or newer, and Git. Python/Git run the offline ingestion tests and checks; the web application itself runs with Next.js.

```bash
npm install
npm run dev
```

Open `http://localhost:3000`. The root route chooses a saved language preference, then browser language, then English. Direct application routes are `/en` and `/br`.

Quality checks:

```bash
npm run check:precommit
npm run test
npm run build
npm run check:localization
```

`npm install` also configures the repository's `.githooks/pre-commit` hook. Every commit runs `npm run check:precommit`, which covers lint, TypeScript, focused geometry tests, synthetic Python ingestion tests, Markdown language, and lightweight shell-script validation. Build and route smoke checks remain CI-level integration checks.

## Project documents

- [Product vision](docs/VISION.md)
- [Delivery roadmap](docs/ROADMAP.md)
- [Completed xG data feasibility audit](docs/reports/xg-data-audit.md)
- [Architecture overview](docs/architecture/overview.md), [module reference](docs/architecture/reference/README.md) and [ADRs](docs/architecture/adr/README.md)
- [Development process](docs/DEVELOPMENT_PROCESS.md)
- [Chat commands for spec, dev and review](docs/COMMANDS.md)

Work is tracked in GitHub Issues. Choose a starting situation or add players above the pitch; the measurements refer to the original striker (the shot taker). Drag a player or focus its marker and use the arrow keys (Shift for larger steps). Reset returns to the selected preset and removes added players. The scene remains in place when changing language within the same browser tab. Model validation follows before an xG value is published.

## Data source and publication status

<a href="https://github.com/hudl/open-data"><img src="assets/hudl-statsbomb-logo.png" width="320" alt="Hudl Statsbomb logo" /></a>

The integrated xG model was independently trained using [StatsBomb Open Data](https://github.com/hudl/open-data), subject to the [StatsBomb Public Data User Agreement](https://github.com/hudl/open-data/blob/master/LICENSE.pdf). StatsBomb supplies the training data; it does not create or endorse this project or its model. The pitch fetches the exact reviewed parameter-only static asset, verifies its SHA-256, and executes it locally in the browser. The site footer shows the official logo, source credit and an independent-project disclaimer in both languages. The bilingual Methodology/results view identifies the source, model provenance and accepted limitations. No source event or 360 records or shot-level training examples will be redistributed here.

The intended use is a free, non-commercial professional portfolio without ads, paid services, raw-data hosting or resale. Publishing a model artifact requires a separate review to ensure it contains parameters and metadata only. The logo above comes from the [official Hudl Statsbomb Media Pack](https://statsbomb.com/media-pack/). See the [rights and release record](docs/architecture/reference/statsbomb-rights.md) for the source terms, Hudl Support's conditional answer, and the remaining publication checks.

The offline [shot ingestion guide](docs/architecture/reference/statsbomb-ingestion.md) explains how to rebuild a pinned local corpus and compare embedded shot-frame coverage with separate 360 coverage. All source, per-match and shot-level files remain under ignored local data paths. The completed [aggregate audit for #9](docs/reports/xg-data-audit.md) covers 1,813 matches and all 166 corresponding tracked 360 files. Two full local runs agreed byte for byte; the planning screen passes with 35,024 position-usable shots and 3,261 goals across eight distinct competitions. This audit measures feasibility, not model performance. Feature extraction, training and validation remain separate tasks.

## Positional feature extraction

The shared [feature contract and reproduction guide](docs/architecture/reference/shot-features.md) covers Python/browser parity and local feature generation. [Validation status](docs/reports/xg-feature-audit.md): synthetic checks, full-corpus aggregates and manifest provenance pass; local compared-file equality is owner-confirmed. Use the documented comparator to verify complete runs. Features are not yet an xG model or public prediction. The [architecture overview](docs/architecture/overview.md) is now Markdown.

## Offline model training

Issue #11 supplies [local training scripts and commands](docs/architecture/reference/xg-training.md), a committed experiment protocol, frozen parameter export and versioned aggregate evidence for the methodology/results section. Train on your private complete feature run using the locked Python 3.12 environment. [Execution status](docs/reports/xg-training-methodology.md): synthetic workflow/reproduction checks pass; the first owner-run corpus artifacts passed internal review, with successful complete reproduction confirmed by the owner. Test outcomes stay unopened until #13; no public xG is enabled.

## Browser inference verification

Issue #12 implements validated logistic/XGBoost inference and a separate fixed 0.76 penalty convention. Use the [prediction guide](docs/architecture/reference/prediction.md) to verify your existing frozen training run locally; no retraining or uploading parameters is required. Repeat the parity command and compare its completed directories with `compare_runs.py`. Share only `parity.json`, `manifest.json` and the comparator output. [Verification status](docs/reports/xg-browser-inference.md) distinguishes invented-fixture checks from actual-candidate evidence. The owner-run frozen candidate passed 2,886 parity cases with zero probability difference; complete repeat-run comparison passed and the submitted aggregate evidence was reviewed. The public xG display and Methodology and results section remain gated by #13/#8 and implemented in #4.

## Final xG evaluation

The final evaluator is implemented for local frozen-run execution; actual held-out scientific evidence is accepted with limitations; public release remains pending. See the [command and review guide](docs/architecture/reference/xg-final-evaluation.md) and the [six-stage xG implementation summary](docs/reports/xg-implementation-summary.md). Reports and the app methodology section derive from the same versioned aggregate evidence.

## Actual-corpus final review

The owner-run final evidence passes all automated predicates and the owner reports all requested comparators PASS. Aggregate identity/provenance and report/app consistency were independently checked. Scientific evidence is accepted with sparse/extreme/preset support limitations; actual parameter/export/rights and integrated #4/#8 publication QA remain pending. See `docs/reports/xg-final-evaluation.md` and `docs/reports/xg-final-review-record.json`. Public xG remains disabled.

## Reviewed xG Playground and methodology

The local app now executes the original reviewed independent XGBoost in the browser. Explore six editable presets, move players with mouse/touch/keyboard or position inputs, add/remove up to three represented defenders, and see the current xG and all eight live input cards. Other attackers are visual only. Penalties use a separately labeled fixed 0.76 convention.

Methodology/results follows the Playground on the same page, directly accessible at `/en#methodology` and `/br#methodology`; old dedicated URLs redirect there. Its tables/chart use the same reviewed aggregate evidence as the reports, with selection and final test clearly separated, sparse calibration bins and the adverse cone-count slice visible.

Run `npm run build` and `npm start`; no private dataset or Python runtime is needed for the application. Model/evidence byte checks run before building. See the [integration reference](docs/architecture/reference/playground-and-methodology.md), [ADR](docs/architecture/adr/009-integrated-playground-and-evidence.md) and [integrated QA](docs/reports/xg-playground-qa.md). Public publication remains owner-authorized in #5.
