# xG behavior comparison

**Scope:** adaptive exploratory selection evidence. The previous final test was opened; it is not re-opened or relabeled untouched.

Evidence: `f62228e611a9712acaac4abcbc61b0f3ffc1ec0b0880e111bd0aa447f872dee8`. Protocol: `43c0cd0f3f3f8f4ad6752ab5b0e604580077c77ba40dd8ed4d9cdbe4d3baf940`.

Disposition: **retain_current**. Recommendation: **none**.

## Probability and interaction comparison

| Model | Log loss | Brier | Isolated direction violations | Primary pairs | >2pp jump rate | p95 jump |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| full_logistic | 0.23835520 | 0.06761177 | 0 | 986 | 0.00000000 | 0.00605654 |
| full_monotonic_xgboost | 0.23524575 | 0.06694985 | 0 | 986 | 0.04259635 | 0.01460033 |
| full_xgboost | 0.23520840 | 0.06697392 | 40 | 986 | 0.04462475 | 0.01868659 |

## Decisions and review flags

Quality margins are absolute score degradations of 0.005 log loss and 0.001 Brier, using one-sided 95% paired-match bootstrap upper bounds. Interactive improvement requires a 25% lower >0.02 jump rate without higher p95 jump size on supported continuous ordinary paths. When the current jump rate is zero, the candidate also needs zero rate and strictly smaller p95. These margins are product tradeoffs, not universal scientific constants.

- **full_logistic:** does not qualify. Failed gates: log_loss, brier. Required reviews: calibration_bin:0, calibration_bin:1, slice:3, slice:32.
- **full_monotonic_xgboost:** does not qualify. Failed gates: interactive_improvement. Required reviews: none.

## Plateaus, discontinuities and support

All full-probability isolated sweeps, plateau share/span and jump summaries are in `behavior-evaluation.json`. Isolated vectors hold six other features fixed and may be physically inconsistent. Physical paths record all eight deltas privately; their reversals are not automatically partial-direction violations. Raw/calibrated/exported candidate directions and native/export errors are recorded separately.

| Model | Segment category | Pairs | >2pp jump rate | p95 jump |
| --- | --- | ---: | ---: | ---: |
| full_logistic | count_transition | 11 | 1.00000000 | 0.05811820 |
| full_logistic | extreme | 276 | 0.01811594 | 0.00059142 |
| full_logistic | outside_reference | 1048 | 0.00000000 | 0.00373540 |
| full_logistic | primary | 986 | 0.00000000 | 0.00605654 |
| full_monotonic_xgboost | count_transition | 11 | 0.72727273 | 0.04711469 |
| full_monotonic_xgboost | extreme | 276 | 0.02173913 | 0.00000000 |
| full_monotonic_xgboost | outside_reference | 1048 | 0.01622137 | 0.00483348 |
| full_monotonic_xgboost | primary | 986 | 0.04259635 | 0.01460033 |
| full_xgboost | count_transition | 11 | 0.72727273 | 0.04284183 |
| full_xgboost | extreme | 276 | 0.02173913 | 0.00000000 |
| full_xgboost | outside_reference | 1048 | 0.02003817 | 0.00645099 |
| full_xgboost | primary | 986 | 0.04462475 | 0.01868659 |

Outside-reference, insufficient-reference, extreme and count-transition segments remain visible above and in per-path summaries. Support is a training-only nearest-neighbor diagnostic, not calibration evidence or a runtime rejection rule. Sparse calibration/slices and supported adverse differences are retained with review flags in the aggregate JSON.

## Logistic interpretation and goalkeeper defaults

Frozen standardized logistic coefficients, scales, calibration and train-only correlations are recorded in `logistic_diagnostics`. Coefficients are conditional associations under correlation/regularization, not causal effects. Continuous inputs give continuous logistic responses; cone/count transitions can still jump. The monotonic tree candidate can still plateau.

Keeper advance/lateral and extreme fixtures use actual retained features. No default keeper position is changed. Any proposed default change needs a separate contextual support review.

## Verification and next boundary

Node executes the browser-targeted TypeScript bundle by default; optional Chromium execution is recorded explicitly. Parity does not establish predictive fitness. Parameters, row predictions, training anchors and complete sweep traces remain local. The entire research run must reproduce before an evidence-backed disposition is accepted.

A genuinely unused holdout must be reserved before fitting through the separate reservation command. Local match overlap can be checked; unknown external prior use cannot be mechanically proved and requires an explicit provenance declaration. No candidate can automatically replace the published model. Without independent evidence, any recommendation is exploratory.

- Selection data and prior final findings informed this follow-up; exploratory evidence only.
- Tree constraints do not imply smoothness or monotonicity on every physical drag.
- Joint support diagnostics and synthetic paths do not establish empirical calibration.
- Rounded reported distance/angle examples lack full coordinates; fixtures are analogues.
- No goalkeeper defaults, published artifact or localized methodology values are changed.
