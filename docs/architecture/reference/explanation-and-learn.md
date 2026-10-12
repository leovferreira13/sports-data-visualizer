# Explanation and Learn mode

**Status:** current xG/eight feature cards and inline Methodology/results implemented in #4; guided comparisons/Learn remain deferred in #5.

An insight layer describes the scenario from the same measured features used by the predictor. A comparison layer may show before/after values and the change in model output. If several elements move, describe the combined scene change instead of assigning the full difference to one cause. A descriptive overlay that is not a model feature must be labeled separately.

`components/prediction-panel.tsx` presents actual output and eight retained features. Pure comparison helpers in `lib/insights.ts` remain available for future guided experiments; no last-change panel is rendered. A future Learn component will own optional 2–3 experiments. Both modes share one `Scenario` and predictor. Playground is the default and the user may leave Learn without losing the scene. Experiments involving goalkeeper or defenders require corresponding model support.

**Learning note:** a counterfactual comparison means evaluating the same model twice while changing an input. It describes the model's response, not proof that the change would cause a goal in a real match.

## First-release portfolio narrative

The purpose is intuitive education and a defensible professional portfolio. #4 connects real inference and layered Methodology/results; #5 adds optional experiments on the same state. Valid rare/extreme scenes stay explorable; concise support/partial-visibility notes explain confidence without demanding a new fit or blocking scenes merely because a descriptive reference flags them. Explain tree plateaus and show actual before/after outputs rather than promising smooth or causal effects.

Methodology uses the same #11/#13 aggregate evidence as the reports and exposes baseline comparison, frozen selection, final paired uncertainty, sparse/adverse slices and source credit; repository documents link architecture/reproduction. Keep the ordinary visitor flow simple while allowing technical reviewers to inspect decisions. Targeted qualitative comprehension/reviewer feedback has no fixed participant quota. Methodology/results is implemented; guided experiments remain #5.

## Integrated #4 delivery

The reviewed parameter envelope is now integrated into the five-language Playground, with explicit prediction states, zero-to-three represented defenders, honest comparisons and inline Methodology/results. The original fitted feature contract, parameters and aggregate evidence remain unchanged. See [Playground and Methodology/results](playground-and-methodology.md) for actual modules and commands.

Earlier statements that actual weights are local-only or that the UI displays geometry only describe the pre-integration state. #8 is closed; #4 owns the dated integrated QA record and any explicitly unresolved logo/publication checks. Learn remains #5; authorized public deployment and final live checks belong to #26. See `docs/reports/xg-playground-qa.md`; no public release is implied.

## Playground layout revision (2026-10-11)

The current #4 UI places the pitch left and eight retained-feature cards plus current xG right. Mobile uses a compact sticky xG strip within the Playground, the pitch, then two-column cards. The last-completed-change panel and expanded observations block are removed; support/illustration explanations remain in Methodology. Secondary position controls are collapsible. Methodology is server-rendered below the pitch on the same localized page, with anchor navigation and redirects from former dedicated URLs. The technical-links block is removed from the product; repository references remain available. This revision supersedes earlier references to adjacent tabs or comparison panels and does not change inference, parameters or scientific evidence.
