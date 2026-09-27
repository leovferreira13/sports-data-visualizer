# Football, Visualized

An interactive, bilingual playground for understanding expected goals (xG). Move the shooter, goalkeeper, and defenders to explore how shot geometry and positioning affect a model's estimate.

**Status:** bilingual playable pitch with four movable players, five editable presets, distance, and angle. No published xG estimate until its model, inputs, and limitations are validated.

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

Work is tracked in GitHub Issues. Drag a player or focus its marker and use the arrow keys (Shift for larger steps). The scene remains in place when changing language within the same browser tab. Model validation follows before an xG value is published.
