# Football, Visualized — delivery roadmap

**Status:** plan for the first public release · **Updated:** 2026-09-26

## Delivery rule

Build a working first interaction as soon as possible, then complete a small, trustworthy release. The time ranges below are **focused-effort estimates**, not promised deadlines. Model investigation determines whether publication fits in one weekend or needs another cycle.

| Milestone | Indicative effort | End demonstration | Exit condition |
| --- | --- | --- | --- |
| **0. Prepare** | 1–2 h | Repository, runnable app, and three starting documents. | Runs locally; scope and criteria recorded. |
| **1. Playable pitch** | 4–8 h | Responsive pitch with shooter, goalkeeper, two defenders, and presets; distance and angle respond to dragging. | Mouse and touch work; pieces stay in bounds; no provisional number is labeled xG. |
| **2. Prove the calculation** | 3–6 h to assess an existing artifact; more if training is needed | Small test takes a scenario state and returns a reproducible estimate. | Model rights and inputs checked; keeper/defenders affect the value if claimed; plausible scenes; limitations documented. |
| **3. Publishable Playground** | 6–10 h after milestone 2 | Live estimate, explanations, six presets, addable attackers and defenders, removal controls, reset, and `pt-BR`/`en` interface. | v0.1 acceptance criteria met on desktop and mobile. |
| **4. Learn and publish** | 4–8 h | Optional 2–3-step tutorial on the same pitch, README, public URL, and short feedback round. | Full flow in both languages; model provenance/limits visible; public link tested. |
| **5. Refine from real use** | Based on feedback | Fixes to confusion, bugs, and friction reported by fans and commentators. | Priorities come from observation rather than a speculative feature list. |

**First observable milestone:** after milestone 1, people can drag pieces and switch presets. This answers “how quickly can we make a working first version?” **Publication gate:** only after milestone 2 may a number be presented as an xG estimate.

## Model decision at milestone 2

Parent issue #3 now selects our own model pipeline: audit legally usable StatsBomb Open Data in #9, define matching offline/browser features in #10, train a regularized logistic regression baseline and constrained XGBoost positional candidate in #11, then evaluate calibration and scene behavior before publication in #13. Record source/model provenance, actual inputs and limitations. The earlier licensed-artifact-first option is superseded.

Export reviewed parameters and metadata for browser inference only after the evaluation and rights gates pass. Keep source and shot-level records local. Open-play foot shots form the learned population; penalties follow the separately declared fixed 0.76 convention in #12, not a learned result.

If a contextual model is not ready immediately, test the pitch as a prototype with **geometry and indicators** but do not publish xG that pretends to react to goalkeeper/defenders. If the fallback only uses shot location, say so plainly and do not attribute other players' effects to it. A complete v0.1 needs an estimate that matches the promised interactions.

## v0.1 scope

**Interface and interaction**

- Playground on entry; a half-pitch with consistent orientation and scale; shooter, goalkeeper, and up to three defenders movable with mouse and touch.
- Presets: penalty, one-on-one, tight angle, long shot, and crowded box; reset to the selected preset.
- `0.xx xG` (or `0,xx xG` by locale) and equivalent percentage, plus distance, angle, and a simple description of shot-cone occupancy.
- “What affects this chance?” panel with current observations; after moving a piece, compare before/after only for factors actually used by the model.
- Learn mode with 2–3 optional experiments: distance and angle; move a defender out of the way; reposition the goalkeeper. Hide any experiment unsupported by the selected model.
- Portuguese / English selector; initial language from browser preference, persisted manual choice, and complete translations including methodology notes.

**Delivery**

- Public URL and repository; concise README with local setup, model/data origin, limitations, credits, screenshot or GIF, and product decisions.
- Comfortable touch targets, mobile layout, basic keyboard access to select and adjust pieces or equivalent alternative controls.
- Manual checks in desktop and mobile browsers, focused tests of geometry and inference, and URL serialization if scenario sharing is included.

## Acceptance criteria

1. A new visitor lands in Playground and can move the shooter without reading extensive instructions.
2. Moving the shot changes distance/angle consistently; pitch drawings match the numeric values.
3. Moving the goalkeeper or a defender changes xG **when the corresponding feature exists in the model**; the UI never suggests an effect that is absent.
4. The value is in [0, 1]; penalties and invalid states follow explicit rules; coordinate errors do not cause absurd jumps.
5. All six presets load in both languages and remain editable. The tutorial can start and stop without reopening the site.
6. Changing language preserves scene and mode, translates every text, and retains the choice on later visits; absent a saved choice, the initial locale follows browser preference.
7. The explanation identifies the result as an estimate and lists included and omitted factors. Descriptions of changes derive from the same features as the prediction.
8. The flow works with mouse and touch on desktop and mobile widths; critical interactions have an accessible alternative if dragging fails.
9. README, attribution, and public URL are ready to send to a commentator or recruiter.

## Open points resolved by the prototype

- **Model:** licensed reuse or an in-house regression; record the choice before showing a value.
- **Scenario link:** desirable for commentators; include in v0.1 if it fits after calculation and accessibility. Otherwise make it the highest-priority next improvement.
- **Penalty:** include a visual preset already on the pitch; show xG only with treatment compatible with the selected model.
- **Mobile pitch:** test a horizontal pitch with framing and touch before investing in a separate vertical representation.

## After v0.1

**v0.2, depending on feedback:** shareable links if deferred; 3–5 sourced historical reconstructions that distinguish observed versus inferred positions, shot type, and context missing from the model. Candidate examples for research, **not yet confirmed**: James Rodríguez in 2014, Van Persie in 2014, Ronaldinho in 2002.

**Later:** other metrics as separate experiments. Work on xA, xThreat, scouting portal, or user accounts is not a dependency of the first release.

## Practical order of the first tasks

1. Create the app and one pitch geometry system; draw goal, cone, and pieces.
2. Implement Pointer Events dragging, boundaries, and presets.
3. Prove `scenario → features → model → xG` and document provenance.
4. Add honest before/after insights and explicit penalty handling.
5. Finish translation, responsiveness, Learn, and essential accessibility.
6. Publish, show real users, and record the three highest-priority improvements.

### Offline training implementation status (#11)

Training contracts/scripts and synthetic verification are implemented; the first owner-run actual-corpus artifacts passed internal review, with successful complete reproduction confirmed by the owner. See the [local training guide](architecture/reference/xg-training.md) and [status report](reports/xg-training-methodology.md). The Methodology and results tab in #4 consumes the same aggregate evidence as the generated report. Final-test evaluation and release remain gated by #13 and final rights QA in #8.

### Browser inference implementation status (#12)

Validated artifact loading, logistic/XGBoost inference, explicit unsupported/unavailable results and the separate 0.76 penalty convention are implemented. Invented-fixture parity is automated; the owner's frozen candidate passed 2,886 cases with zero probability difference, and complete repeat-run comparison passed. See the [inference review](reports/xg-browser-inference.md). The [prediction guide](architecture/reference/prediction.md) provides local commands, optional Chromium checks and repeat-run comparison. Actual weights remain local and the public page still displays geometry only.

## Final evaluation handoff

Issue #13 provides offline final-test evaluation infrastructure and generated aggregate report/model-card/app views. Actual-corpus results, complete reproduction and the dated decision remain pending. This does not close #3 or publish xG. #4 must integrate the Methodology and results tab and finish real production QA with #8.
