# Initial backlog for GitHub Issues

Historical starting scope; the current Issue and ROADMAP.md supersede earlier assumptions. Create bounded Issues for remaining outcomes. The first two can start independently after repository setup. Keep the board statuses described in `DEVELOPMENT_PROCESS.md`.

## 1. Scaffold the bilingual Next.js application

**Outcome:** A local app starts with localized `/pt-BR` and `/en` routes, and Playground is the default screen.

**Scope:** Next.js App Router, React, TypeScript, minimal layout, matching translation keys, language detection and persisted manual choice. No pitch or xG calculation yet.

**Acceptance:** Fresh browser language chooses a supported locale; switching languages preserves current mode and scenario when those states exist; both locales render; basic build/lint pass.

**Validation:** Build and manual browser checks for `pt-BR`, `en`, unsupported browser language, and manual toggle.

**Milestone:** 0–1. **Dependency:** none.

## 2. Build the first playable pitch

**Outcome:** Someone can drag the shooter, goalkeeper, and two defenders on a responsive half-pitch and see distance and angle change.

**Scope:** SVG field, one geometry system in meters, pointer events, shot cone, five editable presets and reset. No number labeled xG.

**Acceptance:** Pieces stay in bounds; mouse and touch work; drawn and numeric geometry agree; presets can be edited; desktop and mobile usable.

**Validation:** Focused geometry tests and manual desktop/touch checks. **Milestone:** 1. **Dependency:** app scaffold.

## 3. Prove the xG model and its license

**Outcome:** A documented, reproducible calculation accepts scenario features and returns a bounded estimate that responds to defender and goalkeeper positions when claimed.

**Scope:** Evaluate a licensed reusable model; if unsuitable, train a small regression from permitted open data. Record data rights, feature definitions, population, calibration checks, penalties, provenance, and limitations. Keep model research time boxed.

**Acceptance:** A documented decision names the chosen model and license; representative scenarios behave plausibly; browser feature extraction matches training; keeper/defender effects are actually included or explicitly deferred; no misleading xG is published.

**Validation:** Targeted fixtures, sample holdout by match if trained, calibration/Brier inspection, comparisons across presets. **Milestone:** 2. **Dependency:** pitch geometry contract.

## 4. Turn the pitch into a public Playground

**Outcome:** A visitor can build a situation and understand what the displayed xG estimate includes.

**Scope:** Validated real-time prediction, up to three defenders, add/remove, two-language insight panel, before/after comparison, model limitations, penalty rule, accessible controls.

**Acceptance:** The number remains within [0,1], changes only for supported model inputs, and is presented as an estimate; all controls work on desktop/mobile and have keyboard or equivalent alternatives; translations are complete.

**Validation:** Model fixtures, relevant interface checks, manual mouse/touch/keyboard walkthrough. **Milestone:** 3. **Dependency:** model proof and playable pitch.

## 5. Add optional Learn mode (deferred)

**Outcome:** A visitor can complete two or three guided experiments and exit without losing the scene.

**Scope:** Distance/angle, defender and keeper experiments supported by the same model and scene. Publication belongs to #26; portfolio presentation belongs to #25; localization was delivered in #24.

**Acceptance:** Playground stays the default; guided experiments support all five locales and preserve the scene. Learn is not a public-release dependency.

**Validation:** Targeted guided-experiment walkthroughs. **Dependency:** reviewed Playground.

## Later, after feedback

Scenario links, then sourced historical reconstructions. Do not block v0.1 on them.
