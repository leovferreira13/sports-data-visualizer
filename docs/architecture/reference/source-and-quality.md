# Source material and quality gates

**Status:** ingestion, features, training, browser inference and final evaluation infrastructure are implemented; actual-corpus scientific review is accepted with limitations; integrated publication QA remains pending.

Local StatsBomb ingestion and its synthetic tests are implemented in `scripts/xg/ingest_statsbomb.py` and `scripts/xg/tests/test_ingest_statsbomb.py`. See [ingestion and audit](statsbomb-ingestion.md) for reproducible commands, eligibility, visibility and output contracts. The corpus and per-match counts stay local; the [completed competition-level audit](../../reports/xg-data-audit.md) records the passing feasibility screen and its limitations. Training and browser prediction have owner-run evidence; see [training](xg-training.md), [prediction](prediction.md) and [final evaluation](xg-final-evaluation.md).

## Suggested code map

The current shell and pitch use `app/[locale]/page.tsx`, `app/[locale]/layout.tsx`, `components/playable-pitch.tsx`, `lib/scenario.ts`, `lib/geometry.ts`, `lib/presets.ts`, `lib/scenario-session.ts`, `locales/pt-BR.json`, and `locales/en.json`. Prediction uses `lib/model.ts`, `lib/predict.ts` and local frozen parameter envelopes; Learn remains planned. `lib/scenario-url.ts` only exists if shareable URLs are implemented later.

## Quality gates

- `npm run check:precommit` runs lint, typecheck, focused geometry/preset/snapshot tests, synthetic Python ingestion tests, and documentation checks. CI also builds and checks localized routes. Feature/inference tests verify shared definitions; the dedicated synthetic training CI also exercises the final evaluator and complete comparison.
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
