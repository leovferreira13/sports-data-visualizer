# Football, Visualized — delivery roadmap

**Status:** plan for the first public release · **Updated:** 2026-10-11

## Delivery rule

Build a working first interaction as soon as possible, then complete a small, trustworthy release. The time ranges below are **focused-effort estimates**, not promised deadlines. The model's scientific milestone is complete. Prioritize the intuitive educational portfolio, reviewer-visible reasoning and scoped publication QA; another model optimization cycle is not required for v0.1.

| Milestone | Indicative effort | End demonstration | Exit condition |
| --- | --- | --- | --- |
| **0. Prepare** | 1–2 h | Repository, runnable app, and three starting documents. | Runs locally; scope and criteria recorded. |
| **1. Playable pitch** | 4–8 h | Responsive pitch with shooter, goalkeeper, two defenders, and presets; distance and angle respond to dragging. | Mouse and touch work; pieces stay in bounds; no provisional number is labeled xG. |
| **2. Prove the calculation** | Completed in #9–#13 | Small test takes a scenario state and returns a reproducible estimate. | Model rights and inputs checked; keeper/defenders affect the value if claimed; scientific checks and scene responses recorded; support/transfer limitations documented. |
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
- Free exploration of rare/extreme scenes within valid controls, with proportional support notes and no diagnostic-only blocking.
- Visible, directly accessible Methodology and results section below Playground, with plain-language explanations plus technical evidence/architecture links.
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
3. Moving the goalkeeper or a defender evaluates the actual retained features; some movements can leave tree outputs unchanged. The UI never invents an effect, forces monotonicity or promises real-world causality.
4. The value is in [0, 1]; penalties and invalid states follow explicit rules; coordinate errors do not cause absurd jumps.
5. All six presets load in both languages and remain editable. The tutorial can start and stop without reopening the site.
6. Changing language preserves scene and mode, translates every text, and retains the choice on later visits; absent a saved choice, the initial locale follows browser preference.
7. The explanation identifies the result as an estimate and lists included and omitted factors. Descriptions of changes derive from the same features as the prediction.
8. The flow works with mouse and touch on desktop and mobile widths; critical interactions have an accessible alternative if dragging fails.
9. README, attribution, and public URL are ready to send to a commentator or recruiter.

## Open points resolved by the prototype

- **Model:** resolved: independently trained shallow XGBoost, compared against regularized logistic baselines; final scientific evidence is accepted with limitations.
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
6. Publish with owner authorization after scoped rights/product QA; record targeted qualitative feedback and useful prioritized improvements.

### Offline training implementation status (#11)

Training contracts/scripts and synthetic verification are implemented; the first owner-run actual-corpus artifacts passed internal review, with successful complete reproduction confirmed by the owner. See the [local training guide](architecture/reference/xg-training.md) and [status report](reports/xg-training-methodology.md). The Methodology and results section in #4 consumes the same aggregate evidence as the generated report. Final-test evaluation and release remain gated by #13 and final rights QA in #8.

### Browser inference implementation status (#12)

Validated artifact loading, logistic/XGBoost inference, explicit unsupported/unavailable results and the separate 0.76 penalty convention are implemented. Invented-fixture parity is automated; the owner's frozen candidate passed 2,886 cases with zero probability difference, and complete repeat-run comparison passed. See the [inference review](reports/xg-browser-inference.md). The [prediction guide](architecture/reference/prediction.md) provides local commands, optional Chromium checks and repeat-run comparison. The reviewed weights are now a hash-checked static asset and the local page displays learned estimates; authorized public deployment remains #5.

## Final evaluation handoff

Issue #13 provides offline final-test evaluation infrastructure and generated aggregate report/model-card/app views. Owner-run actual-corpus results pass automated gates and complete comparators are reported PASS. Scientific review accepts the evidence with support limitations; distribution/publication decisions remain pending. This does not close #3 or publish xG. #4 must integrate the Methodology and results section and finish real production QA with #8.

## Actual-corpus final review

The owner-run final evidence passes all automated predicates and the owner reports all requested comparators PASS. Aggregate identity/provenance and report/app consistency were independently checked. Scientific evidence is accepted with sparse/extreme/preset support limitations; actual parameter/export/rights and integrated #4/#8 publication QA remain pending. See `docs/reports/xg-final-evaluation.md` and `docs/reports/xg-final-review-record.json`. Public xG remains disabled.

## Portfolio alignment and completion ownership (2026-10-11)

#4 presents actual model responses, tree plateaus, illustrative presets and layered methodology; #5 provides short optional experiments, a concise interview-ready README/walkthrough and small targeted qualitative review. A fixed 5–8-person feedback cohort, growth/traffic targets and universal scene precision are not release gates. No new training work is required for the educational first release.

#9–#13 are closed and the final-evaluation PR is merged. #3's technical/scientific milestone is complete; #8 is closed following its scoped rights/artifact/history completion; integrated xG/methodology publication checks were explicitly transferred to #4. Start #4 from the accepted scientific handoff without requiring epic closure. #4 collects the concrete QA evidence for #8; #5 publishes afterward with owner authorization. This preserves publication checks without a circular development dependency.

## Rights completion handoff

The owner assigned interface-dependent publication QA to #4. The dated #8 rights/artifact/repository completion review is in `docs/reports/statsbomb-rights-completion.md`. After its documentation is merged, #8 and the completed model epic #3 may close. Actual xG/methodology pages, final build/network content and attribution/logo QA remain mandatory in #4 before #5 publishes with owner authorization. No new training cycle or public release is authorized by this handoff.

## Integrated #4 delivery

The reviewed parameter envelope is now integrated into the bilingual Playground, with explicit prediction states, zero-to-three represented defenders, honest comparisons and inline Methodology/results. The original fitted feature contract, parameters and aggregate evidence remain unchanged. See [Playground and Methodology/results](architecture/reference/playground-and-methodology.md) for actual modules and commands.

Earlier statements that actual weights are local-only or that the UI displays geometry only describe the pre-integration state. #8 is closed; #4 owns the dated integrated QA record and any explicitly unresolved logo/publication checks. Learn and authorized deployment remain #5. See `docs/reports/xg-playground-qa.md`; no public release is implied.

## Owner-directed Playground revision (2026-10-11)

The current #4 UI places the pitch left and eight retained-feature cards plus current xG right. Mobile uses a compact sticky xG strip within the Playground, the pitch, then two-column cards. The last-completed-change panel and expanded observations block are removed; support/illustration explanations remain in Methodology. Secondary position controls are collapsible. Methodology is server-rendered below the pitch on the same localized page, with anchor navigation and redirects from former dedicated URLs. The technical-links block is removed from the product; repository references remain available. This revision supersedes earlier references to adjacent tabs or comparison panels and does not change inference, parameters or scientific evidence.
