# xG training methodology and validation results

**Status:** validation evidence only; final test unopened; public inference is not approved.

Evidence: `52d8467f8db6064c4bfd565aecbce05857f3869d61b5905490f076adc3a5c0df`. Feature run: `fe7c19c44a1101d61a39df586c957a1b85fef523a3c2a03c4c7faea603374517`.

## Research question and data

We test whether observed defender and keeper positions add predictive information beyond shot geometry, and whether shallow boosted trees justify their complexity. Actual goal/non-goal outcomes are labels; StatsBomb xG is never used for training.

The source is StatsBomb Open Data, credited as training data rather than the author of this independent model. Eligible rows are male open-play left/right-foot shots with valid positional frames and an observed opposing keeper. Penalties, headers and unsupported observations are excluded. The penalty value 0.76 is a separate convention reserved for browser integration.

## Partitions and leakage prevention

Match-level, label-blind competition-season allocation uses seed 42 and approximate 60/10/10/20 training/calibration/selection/test proportions. Largest-remainder allocation can change exact ratios in small strata. Train-only five-fold CV tunes hyperparameters; calibration and selection validation have separate roles. The pipeline is frozen without a final refit. Test goal counts, prevalence and predictions are deliberately absent.

| Partition | Matches | Shots | Goals | Prevalence |
| --- | ---: | ---: | ---: | ---: |
| calibration | 183 | 3440 | 314 | 9.127907% |
| selection | 180 | 3643 | 324 | 8.893769% |
| test | 363 | 7160 | Unopened | Unopened |
| train | 1087 | 20777 | 1966 | 9.462386% |

## Features, exploration and preprocessing

Geometry uses distance, physical goal opening angle and absolute lateral offset. The defender group adds visible count, finite-cone count and nearest observed distance. The keeper group adds distances to goal and shooter. Full logistic and XGBoost use all eight; the selected model need not retain every group.

Distances/counts/angles have different scales. Fold-local StandardScaler and L2 regularization make logistic fitting comparable while reducing unstable correlated weights. The scaler is later fitted only on the full training partition, and its mean/scale travel with the model. Trees use raw finite features. Neither family uses class balancing, resampling, automatic clipping of positions, or test feedback.

Training contains 1 zero-visible-defender frames. Their pitch-diagonal distance is a sentinel, excluded from continuous distance distributions/correlations. Zero visible defenders does not establish absence of defenders.

Training-only distributions, quantiles, Pearson/Spearman correlations, goal rates and competition slices are in `evaluation.json`. Correlations omit sentinel rows, and undefined correlations are null. Sparse means fewer than 100 shots or 10 goals; that reporting rule does not certify other slices as reliable. UI incompatibility counts come from the feature audit because accepted vectors omit original player coordinates. Full-pitch positions are retained.

## Tuning and calibration

Logistic C values are 0.01, 0.1, 1 and 10. XGBoost has eight combinations of depth 2/3, learning rate 0.05/0.1 and minimum child weight 5/20, with 300 trees. CPU execution uses one thread, full row/column sampling and no early stopping. Fold-pooled natural-log loss chooses settings; deterministic ties favor the declared simpler configuration.

Each estimator has identity and, when valid, two-parameter sigmoid calibration. The sigmoid is fitted to clipped base-probability logits on calibration rows only, and must have a positive slope. Selection rows decide adoption: at least 0.0001 log-loss improvement with a paired interval below zero and at most 0.0001 Brier degradation. No isotonic variant or post-result grid expansion is used.

## Selection validation comparisons

These metrics belong to selection validation, not the final held-out test. Lower log loss and Brier are better. Calibration tables use ten fixed probability bins and retain counts/empty bins.

| Experiment | Calibration | Log loss | Brier | Mean probability |
| --- | --- | ---: | ---: | ---: |
| constant | identity | 0.3002653039 | 0.0810601088 | 0.0946238629 |
| geometry_logistic | identity | 0.2458761574 | 0.0695665844 | 0.0930445280 |
| geometry_logistic | sigmoid | 0.2461889911 | 0.0696080389 | 0.0883576197 |
| defenders_logistic | identity | 0.2402038478 | 0.0676582974 | 0.0918487372 |
| defenders_logistic | sigmoid | 0.2403275707 | 0.0676903627 | 0.0844907443 |
| full_logistic | identity | 0.2383551993 | 0.0676117723 | 0.0922972845 |
| full_logistic | sigmoid | 0.2383250212 | 0.0675855206 | 0.0852031809 |
| full_xgboost | identity | 0.2352083977 | 0.0669739155 | 0.0904298022 |
| full_xgboost | sigmoid | 0.2354503045 | 0.0670437002 | 0.0842019909 |

## Decision and uncertainty

Decision: **frozen_candidate**. Selected model: **full_xgboost**.

Use simplest reference-improving pipeline competitive under the predeclared paired rules

A candidate must improve the training-prevalence reference under the declared paired rule. Among eligible candidates, choose the simplest competitive model, ordered geometry logistic, defender logistic, full logistic, then XGBoost. Full logistic and the constant are retained for issue #13. A no-candidate result withholds a positional model instead of declaring success.

Comparison intervals use 1000 paired match bootstrap samples, seed 7421, retaining each sampled match's complete shot multiplicity. The 95% intervals are exploratory selection evidence, not a new untouched test or causal inference. Numeric differences, intervals, calibration decisions and hypotheses/consequences are recorded in `selection`.

## Controlled scenes, export and limitations

Invented current presets and controlled geometry/defender/keeper changes check finite probabilities, reflection, defender order and omitted-group invariance. Effects are model comparisons, not real-world causal claims. No universal monotonic rule is imposed on coupled positional features. Sparse or extreme scenes require the final empirical-support review.

The local export contains coefficients/scaler or inference-only tree nodes/base margin plus calibration and provenance. An independent evaluator checks logistic probabilities within 1e-10 and XGBoost within 1e-7, including numeric tree thresholds. Tree inputs and margin accumulation preserve float32 behavior. Browser parity is still issue #12.

- Match holdout does not establish competition or period transfer.
- Partial observed defenders differ from represented browser scenes.
- Marginal feature ranges do not prove joint support.
- Sentinel and extreme keeper positions may be sparsely supported.
- Coefficients and controlled scenes do not demonstrate causality.
- Selection bootstrap is exploratory; final test remains unopened.

## Reproduction and handoff

See `docs/architecture/reference/xg-training.md` for the locked environment, exact commands and complete-run comparison. This report is regenerated from the same versioned `evaluation.json` used by the future bilingual Methodology and results tab. No real feature rows, shot coordinates or match/event identities appear in public evidence. Candidate parameters stay local pending issue #8/#13 review.

Issue #13 must evaluate the exact frozen candidate, full-logistic baseline and constant on the same held-out rows, report match-level uncertainty and relevant slices, and record the final rights/release decision. Do not tune against that test and continue calling it untouched.
