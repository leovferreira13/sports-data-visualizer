# Football, Visualized

An interactive, bilingual playground for understanding expected goals (xG). Move the shooter, goalkeeper, and defenders to explore how shot geometry and positioning affect a model's estimate.

**Status:** bilingual playable pitch with six editable presets, movable players, addable attackers and defenders, distance, and angle. No published xG estimate until its model, inputs, and limitations are validated.

## Local development

Requirements: Node.js 20.9 or newer and npm.

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

`npm install` also configures the repository's `.githooks/pre-commit` hook. Every commit runs `npm run check:precommit`, which covers lint, TypeScript, focused geometry tests, Markdown language, and lightweight shell-script validation. Build and route smoke checks remain CI-level integration checks.

## Project documents

- [Product vision](docs/VISION.md)
- [Delivery roadmap](docs/ROADMAP.md)
- [Architecture overview](docs/architecture/overview.py), [module reference](docs/architecture/reference/README.md) and [ADRs](docs/architecture/adr/README.md)
- [Development process](docs/DEVELOPMENT_PROCESS.md)
- [Chat commands for spec, dev and review](docs/COMMANDS.md)

Work is tracked in GitHub Issues. Choose a starting situation or add players above the pitch; the measurements refer to the original striker (the shot taker). Drag a player or focus its marker and use the arrow keys (Shift for larger steps). Reset returns to the selected preset and removes added players. The scene remains in place when changing language within the same browser tab. Model validation follows before an xG value is published.

## Data source and publication status

<a href="https://github.com/hudl/open-data"><img src="assets/hudl-statsbomb-logo.png" width="320" alt="Hudl Statsbomb logo" /></a>

The planned xG model will be independently trained using [StatsBomb Open Data](https://github.com/hudl/open-data), subject to the [StatsBomb Public Data User Agreement](https://github.com/hudl/open-data/blob/master/LICENSE.pdf). StatsBomb supplies the training data; it does not create or endorse this project or its model. The current pitch does not display a trained xG estimate. The site footer shows the official logo, source credit and an independent-project disclaimer in both languages. The future xG methodology will also identify the source and model provenance. No source event or 360 records or shot-level training examples will be redistributed here.

The intended use is a free, non-commercial professional portfolio without ads, paid services, raw-data hosting or resale. Publishing a model artifact requires a separate review to ensure it contains parameters and metadata only. The logo above comes from the [official Hudl Statsbomb Media Pack](https://statsbomb.com/media-pack/). See the [rights and release record](docs/architecture/reference/statsbomb-rights.md) for the source terms, Hudl Support's conditional answer, and the remaining publication checks.
