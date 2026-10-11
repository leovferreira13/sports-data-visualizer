# Explanation and Learn mode

**Status:** proposed; no application code yet.

An insight layer describes the scenario from the same measured features used by the predictor. A comparison layer may show before/after values and the change in model output. If several elements move, describe the combined scene change instead of assigning the full difference to one cause. A descriptive overlay that is not a model feature must be labeled separately.

`components/InsightPanel.tsx` may own the current estimate and measurements; `components/LearnMode.tsx` may own optional 2–3 experiments. Both modes share one `Scenario` and predictor. Playground is the default and the user may leave Learn without losing the scene. Experiments involving goalkeeper or defenders require corresponding model support.

**Learning note:** a counterfactual comparison means evaluating the same model twice while changing an input. It describes the model's response, not proof that the change would cause a goal in a real match.

## First-release portfolio narrative

The purpose is intuitive education and a defensible professional portfolio. #4 connects real inference and layered Methodology/results; #5 adds optional experiments on the same state. Valid rare/extreme scenes stay explorable; concise support/partial-visibility notes explain confidence without demanding a new fit or blocking scenes merely because a descriptive reference flags them. Explain tree plateaus and show actual before/after outputs rather than promising smooth or causal effects.

Methodology uses the same #11/#13 aggregate evidence as the reports and exposes baseline comparison, frozen selection, final paired uncertainty, sparse/adverse slices and source/architecture/reproduction links. Keep the ordinary visitor flow simple while allowing technical reviewers to inspect decisions. Targeted qualitative comprehension/reviewer feedback has no fixed participant quota. These are planned UI responsibilities, not implemented behavior.
