# Football, Visualized

An interactive, bilingual playground for understanding expected goals (xG). Move the shooter, goalkeeper, and defenders to explore how shot geometry and positioning affect a model's estimate.

**Status:** bilingual application shell implemented; the playable pitch is next. No published xG estimate until its model, inputs, and limitations are validated.

## Local development

Requirements: Node.js 20.9 or newer and npm.

```bash
npm install
npm run dev
```

Open `http://localhost:3000`. The root route chooses a saved language preference, then browser language, then English. Direct application routes are `/en` and `/br`.

Quality checks:

```bash
npm run lint
npm run build
npm run check:localization
python3 scripts/check_markdown_language.py
```

## Project documents

- [Product vision](docs/VISION.md)
- [Delivery roadmap](docs/ROADMAP.md)
- [Architecture overview](docs/architecture/overview.py), [module reference](docs/architecture/reference/README.md) and [ADRs](docs/architecture/adr/README.md)
- [Development process](docs/DEVELOPMENT_PROCESS.md)
- [Chat commands for spec, dev and review](docs/COMMANDS.md)

Work is tracked in GitHub Issues. The first playable milestone focuses on a draggable pitch, geometry, and presets; model validation follows before an xG value is published.
