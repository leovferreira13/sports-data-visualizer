# Six-stage xG implementation and current evidence

**Status:** #8–#12 have implementation and reviewed evidence; #13 final-evaluation infrastructure is implemented. Actual-corpus final scientific review is accepted with limitations; final export/rights/product QA remains pending. This is not an epic-completion or publication announcement.

## Pipeline and responsibilities

| Issue | Delivered boundary | Evidence / remaining work |
| --- | --- | --- |
| #8 | StatsBomb portfolio rights, source/logo attribution and private data containment | Conditional support scope recorded; final actual-product/export/history QA remains open |
| #9 | Pinned local ingestion, shot eligibility and embedded-frame audit | Owner-run full data audit reviewed; no raw records transferred |
| #10 | Independent Python/TypeScript eight-feature extraction | Synthetic parity plus full-corpus aggregate review; local deterministic comparison |
| #11 | Match-isolated split, bounded train-only tuning, separate calibration/selection and frozen candidate | Owner-run actual training/complete reproduction; no test outcome parsing |
| #12 | Validated browser inference, logistic/tree numerical semantics and penalty route | Actual-candidate browser-bundle parity and complete owner comparison passed |
| #13 | Frozen held-out evaluation, uncertainty, support, report/card/app evidence and release checks | Actual-corpus automated gates pass; scientific review accepted with support limitations; distribution/product QA pending |

## Data and feature decisions

The reviewed feature population contains 35,020 male open-play foot shots across 1,813 matches, eight competitions and ten competition-seasons. The base corpus contains 35,057 shots; 33 missing-keeper and four singular goal-line cases are excluded by the feature contract. Headers and non-open-play shots were excluded earlier. Labels are observed goal/non-goal outcomes; StatsBomb xG is never used as the target.

Embedded shot frames are the primary positional observation. Optional 360 availability does not make all defender positions complete. No missing keeper or unseen defender is inferred. Extra attackers are omitted. Field geometry uses metric coordinates, independent of SVG rendering.

Eight inputs: shot distance, goal opening angle, absolute lateral offset, visible defender count, finite-cone count, nearest visible defender distance, keeper-to-goal distance and keeper-to-shot distance. A zero-visible-defender distance uses a separate sentinel with explicit count; the single training example cannot establish broad support for empty represented pitches.

## Learning and leakage control

| Partition | Matches | Shots | Goals reported at #11 |
| --- | ---: | ---: | --- |
| calibration | 183 | 3440 | 314 |
| selection | 180 | 3643 | 324 |
| test | 363 | 7160 | Unopened |
| train | 1087 | 20777 | 1966 |

Whole matches are allocated without label-based partition choice. Five-fold training CV tunes bounded hyperparameters; logistic scaling is fitted within each fold. Calibration fits on its own partition and selection uses a separate partition. No post-selection refit changes the pipeline. The final test is evaluated only by #13.

The three logistic experiments isolate geometry, defender information and the full positional feature group. Shallow XGBoost tests limited nonlinear interactions. Full logistic is retained as the required final baseline, and constant training prevalence supplies the no-positional-information reference. No class balancing changes the probability target.

## Actual selection-validation findings

**These scores are selection validation, not final test.** Metrics below are drawn from the committed reviewed evidence; final-test tables will come from final-evaluation.json.

| Experiment | Retained features | Adopted calibration | Log loss | Brier |
| --- | ---: | --- | ---: | ---: |
| constant | 0 | identity | 0.300265304 | 0.081060109 |
| geometry_logistic | 3 | identity | 0.245876157 | 0.069566584 |
| defenders_logistic | 6 | identity | 0.240203848 | 0.067658297 |
| full_logistic | 8 | identity | 0.238355199 | 0.067611772 |
| full_xgboost | 8 | identity | 0.235208398 | 0.066973915 |

Every frozen experiment improves the constant reference on selection under the predeclared paired rules. Adding defenders improves the observed logistic scores; adding keepers gives a further small improvement. These are conditional predictive associations, not causal effects.

Full XGBoost was frozen with depth 2, learning rate 0.05, minimum child weight 5 and 300 trees. All eight inputs are retained. No fitted sigmoid calibrator met the adoption criteria. In particular, the tiny full-logistic calibration improvement did not meet the declared minimum; it was not adopted after visual judgment.

The full-logistic-minus-XGBoost log-loss difference is 0.003146802 with 95% paired interval [-0.000916787, 0.007320525]. It crosses zero. The Brier difference is 0.000637857 with interval [-0.000841028, 0.002054756], which also crosses zero. The protocol selected XGBoost because the observed Brier deterioration of full logistic exceeded the 0.0001 simplicity guardrail. This is a reproducible rule-driven choice, not conclusive superiority.

## Browser execution and verification

Inference loads parameter-only envelopes after contract/schema/topology validation and captures immutable handles. Logistic evaluates standardized coefficients in double precision. XGBoost preserves float32 feature thresholds and sequential margin accumulation. Missing/invalid/unavailable inputs have explicit statuses; no heuristic is silently relabeled xG. Penalties route separately to fixed 0.76.

Owner-run actual-candidate parity checked 2886 cases, including invented scenes/presets, invalid inputs and tree boundaries. Maximum reported probability error was 0.0; maximum feature error was 1.421e-14. XGBoost tolerance is 1e-7. The executed artifact was a browser-safe bundle in Node; this evidence is distinct from an actual Chromium run. Synthetic Chromium evidence checks infrastructure, not empirical model quality.

The owner reported byte-identical complete training runs (17 files) and complete parity comparison. The assistant reviewed aggregate consistency/provenance and did not independently rerun the actual private rows. Fresh-environment creation was not independently verified.

## What #13 now makes possible

The owner can evaluate the original frozen candidate, full logistic and constant on identical held-out rows, with whole-match uncertainty, calibration, fixed supported/sparse slices and training-only synthetic support diagnostics. Completed withheld evidence survives statistical failures. Report, model card and the future bilingual Methodology and results tab share the same aggregate source. No public xG is enabled by this implementation.

The final evaluation protocol was predeclared. Owner-run final evidence now passes the automated gates and complete comparator checks are reported PASS. Both paired score intervals favor the frozen candidate, and no supported calibration bin is flagged. Scientific review accepts the evidence with explicit sparse-slice/preset/transfer limitations; see the [final review](xg-final-evaluation.md). Final model eligibility requires complete reproduction, dated scientific/rights/export review and an explicit disposition of limitations. #4 still owns actual integrated production/attribution QA; finish #8 QA there and close #3 only after every child passes.

## Evidence and commands

- [Data audit](xg-data-audit.md)
- [Feature audit](xg-feature-audit.md)
- [Training review](xg-training-methodology.md) and [original generated methodology](xg-training-first-run/methodology.md)
- [Browser inference review](xg-browser-inference.md)
- [Final local commands and review contract](../architecture/reference/xg-final-evaluation.md)
- [Rights record](../architecture/reference/statsbomb-rights.md)

- [Final actual-corpus review](xg-final-evaluation.md), [generated report](xg-final-first-run/methodology.md) and [dated decision record](xg-final-review-record.json)

## Rights completion handoff

The owner assigned interface-dependent publication QA to #4. The dated #8 rights/artifact/repository completion review is in `docs/reports/statsbomb-rights-completion.md`. After its documentation is merged, #8 and the completed model epic #3 may close. Actual xG/methodology pages, final build/network content and attribution/logo QA remain mandatory in #4 before #5 publishes with owner authorization. No new training cycle or public release is authorized by this handoff.
