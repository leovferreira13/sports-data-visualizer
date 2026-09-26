# Source material and quality gates

**Status:** proposed checks for the first release.

## Suggested code map

The implementation may use `app/[lang]/page.tsx`, `app/[lang]/layout.tsx`, `components/Pitch.tsx`, `components/InsightPanel.tsx`, `components/LearnMode.tsx`, `lib/geometry.ts`, `lib/features.ts`, `lib/predict.ts`, `lib/presets.ts`, `locales/pt-BR.json`, and `locales/en.json`. `model/model.json` and `scripts/train_model.py` are conditional on the model choice; `lib/scenario-url.ts` only exists if shareable URLs make v0.1. These are proposals, not existing files.

## Quality gates

- Check geometry, boundaries, feature extraction and inference with focused tests. Verify the same feature definitions during training and browser inference.
- Manually exercise drag on desktop and touch, and ensure keyboard or equivalent controls can operate every critical piece.
- Keep decorative SVG elements quiet for screen readers; give movable pieces names and visible focus states.
- Profile before adding debounce: a small local model should update on each move if practical.
- The number and explanation must expose the training population and omissions. Technique, player identity, preceding movement, assist and unseen pressure may be unknown to the model.
- Historic goals require sourced positions and shot type; reconstructed scenes cannot be presented as measured ground truth.

## References to validate during implementation

- [Next.js App Router localization](https://nextjs.org/docs/app/guides/internationalization).
- [StatsBomb Open Data terms and file formats](https://github.com/hudl/open-data/blob/master/README.md). Not every shot has a complete 360 freeze frame; inspect the actual sample.
- [SoccerBoard](https://github.com/arnavmahadev/SoccerBoard) for interaction inspiration. A public repository without a clear license is not permission to copy its code or weights.
- [KU Leuven soccer_xg](https://github.com/ML-KULeuven/soccer_xg) as a potential licensed candidate; assess inputs and inference format before adoption.
