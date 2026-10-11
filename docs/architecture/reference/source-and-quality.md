# Source material and quality gates

**Status:** proposed checks for the first release.

Local StatsBomb ingestion and its synthetic tests are implemented in `scripts/xg/ingest_statsbomb.py` and `scripts/xg/tests/test_ingest_statsbomb.py`. See [ingestion and audit](statsbomb-ingestion.md) for reproducible commands, eligibility, visibility and output contracts. The corpus and per-match counts stay local; the [completed competition-level audit](../../../reports/xg-data-audit.md) records the passing feasibility screen and its limitations. Training and browser prediction remain planned.

## Suggested code map

The current shell and pitch use `app/[locale]/page.tsx`, `app/[locale]/layout.tsx`, `components/playable-pitch.tsx`, `lib/scenario.ts`, `lib/geometry.ts`, `lib/presets.ts`, `lib/scenario-session.ts`, `locales/pt-BR.json`, and `locales/en.json`. Prediction and Learn modules are still proposals; create their boundaries when their Issues establish real contracts. `model/model.json` and `scripts/train_model.py` are conditional on the model choice; `lib/scenario-url.ts` only exists if shareable URLs are implemented later.

## Quality gates

- `npm run check:precommit` runs lint, typecheck, focused geometry/preset/snapshot tests, synthetic Python ingestion tests, and documentation checks. CI also builds and checks localized routes. Feature extraction and inference tests will be needed when the model exists; verify the same definitions during training and browser inference.
- Manually exercise drag on desktop and touch, and ensure keyboard or equivalent controls can operate every critical piece.
- Keep decorative SVG elements quiet for screen readers; give movable pieces names and visible focus states.
- Profile before adding debounce: a small local model should update on each move if practical.
- The number and explanation must expose the training population and omissions. Technique, player identity, preceding movement, assist and unseen pressure may be unknown to the model.
- Historic goals require sourced positions and shot type; reconstructed scenes cannot be presented as measured ground truth.

## References to validate during implementation

- [Next.js App Router localization](https://nextjs.org/docs/app/guides/internationalization).
- [StatsBomb Open Data terms and file formats](https://github.com/hudl/open-data/blob/master/README.md). Not every shot has a complete 360 freeze frame; inspect the actual sample.
- [SoccerBoard](https://github.com/arnavmahadev/SoccerBoard) for interaction inspiration. A public repository without a clear license is not permission to copy its code or weights.
- Parent #3 selects our own logistic regression baseline and constrained XGBoost candidate. External model artifacts are not the implementation path.
