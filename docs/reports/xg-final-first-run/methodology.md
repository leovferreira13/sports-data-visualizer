# Frozen xG final evaluation

**Status:** needs_review; final test opened. Automated evidence does not authorize publication.

Evidence: `e579e10f9699077ddf05e7433af5ed63edf0e03c3ea8c7ca295844951d74ea08`. Training run: `222909fe801f4865897fea3541e023fed626f6736dca6ef69ceada1f7c57945a`. Model: `758526873b8a3a2681f655c064dee52f8bd33749accd499d015420dbe8e11b9a`.

## Research question and development decisions

Does positional information improve probability estimation beyond shot geometry, and is the frozen pipeline fit for the defined non-commercial educational use? Actual goal outcomes are the labels; StatsBomb xG is neither an input nor a label. The original development evidence is preserved inside `final-evaluation.json`, and validation tables in `app-evidence.json` use that evidence directly.

Training-only exploration, feature distributions/correlations, bounded group CV, separate calibration and selection validation, coefficient interpretation and the original selection rationale are documented in the linked training report. Those development scores are not final-test scores.

The frozen selection is **full_xgboost**. No refitting, retuning, calibration change or post-test candidate switch occurs. Constant prediction is frozen training prevalence; full logistic retains its previously selected preprocessing/calibration.

## Population, counts and isolation

male open-play foot shots with observed keeper; partial defenders. Source: [StatsBomb Open Data](https://github.com/hudl/open-data), independently modeled; no StatsBomb endorsement. Source revision: `4b73468fc5b0f1950f9f66fada70ad3a4f9327cb`.

Final test: **363 matches, 7160 shots, 655 goals**, base rate 9.1480%.

Whole matches are isolated from training/calibration/selection. Historical split and manifest hashes are checked before test parsing. Missing/multiple keepers remain excluded; unseen defenders are not imputed. Coverage refers to partial embedded shot frames, not complete visible-area coverage from optional 360 files.

| Competition | Season | Matches | Shots | Goals | Base rate |
| --- | --- | ---: | ---: | ---: | ---: |
| 2 | 27 | 76 | 1622 | 135 | 8.3231% |
| 7 | 27 | 75 | 1319 | 114 | 8.6429% |
| 9 | 27 | 7 | 136 | 11 | 8.0882% |
| 11 | 27 | 76 | 1412 | 166 | 11.7564% |
| 12 | 27 | 76 | 1591 | 135 | 8.4852% |
| 43 | 3 | 13 | 284 | 31 | 10.9155% |
| 43 | 106 | 13 | 238 | 25 | 10.5042% |
| 55 | 43 | 10 | 209 | 18 | 8.6124% |
| 55 | 282 | 10 | 232 | 12 | 5.1724% |
| 223 | 282 | 7 | 117 | 8 | 6.8376% |

## Final probability scores

Log loss uses natural logarithms with 1e-12 metric-only probability clipping. Brier is mean squared probability error. Lower is better. Intervals are percentile 95% match-bootstrap intervals (1,000 resamples; seed 7421). Each draw samples whole matches with replacement, retains repeated-match multiplicity and weights scores by shots. All comparisons share draws.

| Role | Model | Log loss | 95% interval | Brier | 95% interval | Mean probability |
| --- | --- | ---: | --- | ---: | --- | ---: |
| selected | full_xgboost | 0.239965 | [0.225625, 0.255290] | 0.068339 | [0.063826, 0.072950] | 0.093817 |
| full_logistic | full_logistic | 0.242871 | [0.228548, 0.258067] | 0.069261 | [0.064546, 0.074101] | 0.093947 |
| constant | constant-training-prevalence | 0.306008 | [0.291172, 0.322483] | 0.083122 | [0.077796, 0.089036] | 0.094624 |

Observed goal rate interval: [0.084911, 0.098775].

| Selected minus reference | Metric | Difference | 95% interval | Valid / skipped resamples |
| --- | --- | ---: | --- | --- |
| selected_minus_constant | brier | -0.014783 | [-0.017492, -0.012139] | 1000 / 0 |
| selected_minus_constant | log_loss | -0.066043 | [-0.075388, -0.056869] | 1000 / 0 |
| selected_minus_full_logistic | brier | -0.000922 | [-0.001781, -0.000067] | 1000 / 0 |
| selected_minus_full_logistic | log_loss | -0.002906 | [-0.005424, -0.000343] | 1000 / 0 |

Intervals crossing zero do not establish an advantage. Passing the observed logistic guardrail does not prove equivalence. Validation selection comparisons remain exploratory.

## Calibration and slice support

Fixed tenths include probability 1 in the final bin. Sparse means fewer than 100 shots or 10 goals. Empty bins have null rates/intervals. One-match slices cannot estimate between-match uncertainty; replicates without slice observations are skipped and disclosed. Supported-bin residual intervals excluding zero trigger review, not a newly tuned calibrator. Slice comparisons are diagnostic and not corrected confirmatory tests.

### selected calibration

| Bin | Matches | Shots | Goals | Predicted | Observed | Observed 95% interval | Residual 95% interval | Sparse | Review |
| --- | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| 0.0–0.1 | 363 | 5324 | 195 | 0.035344 | 0.036627 | [0.031419, 0.042324] | [-0.003670, 0.006959] | False | False |
| 0.1–0.2 | 325 | 818 | 111 | 0.142781 | 0.135697 | [0.112463, 0.158769] | [-0.030201, 0.015840] | False | False |
| 0.2–0.3 | 246 | 429 | 93 | 0.247527 | 0.216783 | [0.179177, 0.256424] | [-0.067539, 0.009420] | False | False |
| 0.3–0.4 | 184 | 282 | 95 | 0.344197 | 0.336879 | [0.282034, 0.395992] | [-0.061746, 0.053145] | False | False |
| 0.4–0.5 | 128 | 164 | 77 | 0.443975 | 0.469512 | [0.396419, 0.535215] | [-0.046778, 0.091432] | False | False |
| 0.5–0.6 | 60 | 69 | 34 | 0.547233 | 0.492754 | [0.373134, 0.602757] | [-0.175877, 0.055936] | True | False |
| 0.6–0.7 | 36 | 41 | 24 | 0.639610 | 0.585366 | [0.441843, 0.733367] | [-0.198210, 0.093748] | True | False |
| 0.7–0.8 | 15 | 17 | 14 | 0.741867 | 0.823529 | [0.625000, 1.000000] | [-0.110041, 0.251197] | True | False |
| 0.8–0.9 | 9 | 9 | 5 | 0.853041 | 0.555556 | [0.200000, 0.875347] | [-0.666416, 0.025989] | True | False |
| 0.9–1.0 | 6 | 7 | 7 | 0.918412 | 1.000000 | [1.000000, 1.000000] | [0.070595, 0.090259] | True | False |

### full_logistic calibration

| Bin | Matches | Shots | Goals | Predicted | Observed | Observed 95% interval | Residual 95% interval | Sparse | Review |
| --- | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| 0.0–0.1 | 363 | 5192 | 177 | 0.037032 | 0.034091 | [0.028856, 0.039824] | [-0.007963, 0.002766] | False | False |
| 0.1–0.2 | 347 | 1043 | 160 | 0.140344 | 0.153404 | [0.132759, 0.174503] | [-0.007691, 0.034894] | False | False |
| 0.2–0.3 | 245 | 417 | 108 | 0.244777 | 0.258993 | [0.218007, 0.300018] | [-0.026856, 0.054675] | False | False |
| 0.3–0.4 | 173 | 236 | 70 | 0.349512 | 0.296610 | [0.244437, 0.356523] | [-0.105882, 0.005972] | False | False |
| 0.4–0.5 | 99 | 122 | 56 | 0.444715 | 0.459016 | [0.375860, 0.548678] | [-0.072046, 0.104160] | False | False |
| 0.5–0.6 | 64 | 76 | 35 | 0.542668 | 0.460526 | [0.361111, 0.560011] | [-0.178411, 0.017085] | True | False |
| 0.6–0.7 | 34 | 37 | 20 | 0.645166 | 0.540541 | [0.372521, 0.709699] | [-0.266812, 0.060846] | True | False |
| 0.7–0.8 | 19 | 19 | 11 | 0.748519 | 0.578947 | [0.333333, 0.800000] | [-0.419451, 0.054697] | True | False |
| 0.8–0.9 | 10 | 10 | 10 | 0.846355 | 1.000000 | [1.000000, 1.000000] | [0.138339, 0.169822] | True | False |
| 0.9–1.0 | 7 | 8 | 8 | 0.924861 | 1.000000 | [1.000000, 1.000000] | [0.056420, 0.088049] | True | False |

### constant calibration

| Bin | Matches | Shots | Goals | Predicted | Observed | Observed 95% interval | Residual 95% interval | Sparse | Review |
| --- | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| 0.0–0.1 | 363 | 7160 | 655 | 0.094624 | 0.091480 | [0.084911, 0.098775] | [-0.009712, 0.004152] | False | False |
| 0.1–0.2 | 0 | 0 | 0 | Unavailable | Unavailable | Unavailable | Unavailable | True | False |
| 0.2–0.3 | 0 | 0 | 0 | Unavailable | Unavailable | Unavailable | Unavailable | True | False |
| 0.3–0.4 | 0 | 0 | 0 | Unavailable | Unavailable | Unavailable | Unavailable | True | False |
| 0.4–0.5 | 0 | 0 | 0 | Unavailable | Unavailable | Unavailable | Unavailable | True | False |
| 0.5–0.6 | 0 | 0 | 0 | Unavailable | Unavailable | Unavailable | Unavailable | True | False |
| 0.6–0.7 | 0 | 0 | 0 | Unavailable | Unavailable | Unavailable | Unavailable | True | False |
| 0.7–0.8 | 0 | 0 | 0 | Unavailable | Unavailable | Unavailable | Unavailable | True | False |
| 0.8–0.9 | 0 | 0 | 0 | Unavailable | Unavailable | Unavailable | Unavailable | True | False |
| 0.9–1.0 | 0 | 0 | 0 | Unavailable | Unavailable | Unavailable | Unavailable | True | False |

### Selected-model slices

The zero-defender nearest-distance category is missingness, not a measured pitch-diagonal defender. Detailed uncertainty and paired differences for all predictors are retained in the aggregate JSON.

| Feature / boundary | Matches | Shots | Goals | Log loss | 95% interval | Brier | Sparse |
| --- | ---: | ---: | ---: | ---: | --- | ---: | --- |
| goal_opening_angle_deg / lower=0, upper=5 | 12 | 13 | 0 | 0.039036 | [0.026128, 0.059517] | 0.002121 | True |
| goal_opening_angle_deg / lower=5, upper=10 | 94 | 114 | 3 | 0.136090 | [0.023601, 0.256631] | 0.026456 | True |
| goal_opening_angle_deg / lower=10, upper=20 | 362 | 3812 | 104 | 0.114901 | [0.098485, 0.133464] | 0.025732 | False |
| goal_opening_angle_deg / lower=20, upper=40 | 362 | 2639 | 346 | 0.354407 | [0.329597, 0.379630] | 0.104733 | False |
| goal_opening_angle_deg / lower=40, upper=90 | 269 | 557 | 183 | 0.568007 | [0.535527, 0.599864] | 0.193470 | False |
| goal_opening_angle_deg / lower=90, upper=180 | 23 | 25 | 19 | 0.498506 | [0.280441, 0.769531] | 0.160684 | True |
| goalkeeper_distance_to_goal_m / lower=0, upper=2 | 353 | 1728 | 110 | 0.192369 | [0.164726, 0.221529] | 0.051485 | False |
| goalkeeper_distance_to_goal_m / lower=2, upper=5 | 363 | 4633 | 366 | 0.219462 | [0.203283, 0.237661] | 0.060706 | False |
| goalkeeper_distance_to_goal_m / lower=5, upper=10 | 298 | 681 | 152 | 0.454363 | [0.413924, 0.497319] | 0.147671 | False |
| goalkeeper_distance_to_goal_m / lower=10, upper=20 | 87 | 109 | 27 | 0.539021 | [0.425718, 0.674153] | 0.169257 | False |
| goalkeeper_distance_to_goal_m / lower=20 | 9 | 9 | 0 | 0.087951 | [0.056889, 0.116543] | 0.008478 | True |
| shot_distance_m / lower=0, upper=5 | 79 | 94 | 52 | 0.584974 | [0.503349, 0.670747] | 0.199177 | True |
| shot_distance_m / lower=5, upper=10 | 313 | 781 | 189 | 0.491064 | [0.460248, 0.523504] | 0.161016 | False |
| shot_distance_m / lower=10, upper=15 | 359 | 1610 | 243 | 0.376012 | [0.346706, 0.406148] | 0.114237 | False |
| shot_distance_m / lower=15, upper=20 | 360 | 1826 | 111 | 0.217433 | [0.187099, 0.249263] | 0.056340 | False |
| shot_distance_m / lower=20, upper=30 | 362 | 2570 | 58 | 0.103575 | [0.084172, 0.126448] | 0.021806 | False |
| shot_distance_m / lower=30, upper=50 | 172 | 252 | 2 | 0.041984 | [0.008869, 0.089863] | 0.007823 | True |
| shot_distance_m / lower=50 | 26 | 27 | 0 | 0.017016 | [0.011841, 0.026166] | 0.000627 | True |
| visible_defender_count / value=0 | 0 | 0 | 0 | Unavailable | Unavailable | Unavailable | True |
| visible_defender_count / value=1 | 8 | 8 | 3 | 0.396085 | [0.228381, 0.625379] | 0.116820 | True |
| visible_defender_count / value=2 | 54 | 62 | 15 | 0.469909 | [0.388683, 0.559445] | 0.152735 | True |
| visible_defender_count / value=3 | 141 | 184 | 53 | 0.503903 | [0.421900, 0.593544] | 0.169577 | False |
| visible_defender_count / value=4 | 189 | 282 | 56 | 0.434391 | [0.369279, 0.501282] | 0.141759 | False |
| visible_defender_count / value=5 | 266 | 560 | 88 | 0.356971 | [0.308254, 0.404549] | 0.109944 | False |
| visible_defender_count / value=6 | 330 | 1016 | 119 | 0.307717 | [0.271415, 0.348363] | 0.090574 | False |
| visible_defender_count / value=7 | 350 | 1456 | 116 | 0.223827 | [0.195643, 0.251981] | 0.061714 | False |
| visible_defender_count / value=8 | 359 | 1580 | 101 | 0.182673 | [0.156779, 0.208907] | 0.048446 | False |
| visible_defender_count / value=9 | 346 | 1277 | 68 | 0.173632 | [0.141826, 0.208158] | 0.044932 | False |
| visible_defender_count / value=10 | 295 | 735 | 36 | 0.165769 | [0.129946, 0.210934] | 0.041295 | False |
| competition_season / competition_id=2, season_id=27 | 76 | 1622 | 135 | 0.237492 | [0.204611, 0.273673] | 0.068147 | False |
| competition_season / competition_id=7, season_id=27 | 75 | 1319 | 114 | 0.231327 | [0.193420, 0.269452] | 0.064039 | False |
| competition_season / competition_id=9, season_id=27 | 7 | 136 | 11 | 0.223318 | [0.144651, 0.281580] | 0.060705 | False |
| competition_season / competition_id=11, season_id=27 | 76 | 1412 | 166 | 0.282105 | [0.250125, 0.314612] | 0.083163 | False |
| competition_season / competition_id=12, season_id=27 | 76 | 1591 | 135 | 0.214752 | [0.188264, 0.243976] | 0.061068 | False |
| competition_season / competition_id=43, season_id=3 | 13 | 284 | 31 | 0.257262 | [0.182246, 0.382845] | 0.073203 | False |
| competition_season / competition_id=43, season_id=106 | 13 | 238 | 25 | 0.265244 | [0.192861, 0.345999] | 0.075048 | False |
| competition_season / competition_id=55, season_id=43 | 10 | 209 | 18 | 0.265693 | [0.182954, 0.335002] | 0.071182 | False |
| competition_season / competition_id=55, season_id=282 | 10 | 232 | 12 | 0.188765 | [0.128252, 0.244348] | 0.049533 | False |
| competition_season / competition_id=223, season_id=282 | 7 | 117 | 8 | 0.187411 | [0.123262, 0.267415] | 0.055068 | True |
| defenders_in_cone_count / lower=0, upper=1 | 363 | 3289 | 476 | 0.328967 | [0.308750, 0.348588] | 0.101020 | False |
| defenders_in_cone_count / lower=1, upper=2 | 361 | 2719 | 125 | 0.161990 | [0.140238, 0.183218] | 0.039961 | False |
| defenders_in_cone_count / lower=2, upper=3 | 318 | 815 | 41 | 0.174472 | [0.132016, 0.219058] | 0.043991 | False |
| defenders_in_cone_count / lower=3, upper=5 | 209 | 315 | 12 | 0.156516 | [0.091870, 0.230042] | 0.036629 | False |
| defenders_in_cone_count / lower=5, upper=10 | 22 | 22 | 1 | 0.192274 | [0.032458, 0.586810] | 0.045616 | True |
| nearest_visible_defender_distance_m / lower=0, upper=1 | 294 | 676 | 79 | 0.277173 | [0.240561, 0.318518] | 0.082556 | False |
| nearest_visible_defender_distance_m / lower=1, upper=2 | 360 | 2466 | 226 | 0.256019 | [0.230360, 0.282681] | 0.072552 | False |
| nearest_visible_defender_distance_m / lower=2, upper=5 | 363 | 3433 | 302 | 0.225719 | [0.204993, 0.247371] | 0.063872 | False |
| nearest_visible_defender_distance_m / lower=5, upper=10 | 287 | 577 | 47 | 0.214232 | [0.173460, 0.259770] | 0.060732 | False |
| nearest_visible_defender_distance_m / lower=10, upper=20 | 8 | 8 | 1 | 0.116383 | [0.012423, 0.312843] | 0.033489 | True |
| nearest_visible_defender_distance_m / lower=20, upper=50 | 0 | 0 | 0 | Unavailable | Unavailable | Unavailable | True |
| nearest_visible_defender_distance_m / lower=50 | 0 | 0 | 0 | Unavailable | Unavailable | Unavailable | True |
| nearest_visible_defender_distance_m / value=0 | 0 | 0 | 0 | Unavailable | Unavailable | Unavailable | True |

## Synthetic scenes and support

Training-only standardized retained-feature RMS nearest neighbor; deterministic reference subsample, 99th-percentile leave-one-out threshold. Zero-defender cohort separate; sentinel distance omitted. This diagnostic is not proof of realistic joint scene support or a runtime rejection rule.

Keeper/defender differences measure model response only. Individual tree plateaus, nonmonotonic responses and coordinate symmetry can all be valid. Unrealistic/extreme scenes and training/UI-bound differences need explicit scope/warning review.

| Invented scene | Status | Probability | Training support diagnostic | Outside marginals |
| --- | --- | ---: | --- | --- |
| centralChance | ok | 0.121059 | outside_training_reference | False |
| penalty | penalty-convention | 0.760000 | convention | None |
| oneOnOne | ok | 0.312157 | outside_training_reference | False |
| tightAngle | ok | 0.048172 | outside_training_reference | False |
| longShot | ok | 0.017586 | outside_training_reference | False |
| crowdedBox | ok | 0.367526 | within_training_reference | False |
| zero_defenders | ok | 0.121059 | insufficient_reference | False |
| one_defender | ok | 0.121059 | outside_training_reference | False |
| added_defender | ok | 0.077567 | outside_training_reference | False |
| cone_inside | ok | 0.107172 | outside_training_reference | False |
| cone_outside | ok | 0.121059 | outside_training_reference | False |
| nearest_defender | ok | 0.045726 | within_training_reference | False |
| keeper_advanced | ok | 0.494412 | outside_training_reference | False |
| keeper_lateral | ok | 0.190333 | outside_training_reference | False |
| keeper_extreme | ok | 0.178461 | outside_training_reference | False |
| coincident_defender | ok | 0.045235 | outside_training_reference | False |
| near_goal | ok | 0.925342 | outside_training_reference | True |
| full_pitch_corner | ok | 0.020865 | outside_training_reference | True |
| missing_keeper | unsupported | Unavailable | unsupported | None |
| invalid_coordinate | unsupported | Unavailable | unsupported | None |
| goal_line | unsupported | Unavailable | unsupported | None |
| reordered_defenders | ok | 0.121059 | outside_training_reference | False |
| reflection | ok | 0.121059 | outside_training_reference | False |

## Release checks and remaining review

| Predeclared predicate | Pass |
| --- | --- |
| constant_brier | True |
| constant_log_loss | True |
| invariants | True |
| logistic_guardrail | True |
| parity | True |
| scene_response | True |
| test_support | True |

A failed statistical/scene predicate withholds the candidate. Completed withheld runs preserve evidence and exit with code 2. Passing predicates yields needs_review, not publication. Changes after opening require a revised evaluation protocol and defensible new evaluation; the existing test cannot be described as untouched.

Required review:

- complete independent reproduction and verification limits
- supported calibration/slices and sparse/extreme scene limitations
- parameter-only export and current non-commercial distribution rights
- dated owner/implementer decision bound to evidence/model hashes
- #4 actual product attribution, methodology, production bundles/network assets and #8 final QA

## Limitations

- Match-isolated holdout measures the represented cohort, not unseen league/period transfer.
- Defender observations are partial embedded shot frames; optional 360 coverage is not a test-row covariate.
- Missing/multiple keepers are excluded; no valid prediction is obtained by imputing a keeper.
- Zero observed defenders do not establish an empty pitch; sentinel support can be absent or extremely sparse.
- Support distances are training-only diagnostics, not proof of realistic joint player configurations.
- Full-pitch training scenes differ from current marker-safe UI bounds; historical UI audit is descriptive.
- Extra attackers, technique, identity, preceding movement and unobserved pressure are omitted.
- Controlled responses are within-model comparisons; tree plateaus and nonmonotonic changes can be valid.
- Slice/calibration intervals are diagnostic, sparse bins remain uncertain and multiple comparisons are not confirmatory.
- Penalties, headers and non-open-play shots are excluded; penalty 0.76 is a separate fixed convention.
- StatsBomb supplies Open Data, not this independent model; non-commercial rights/export review and actual-product QA remain required.

## Reproduction and app handoff

Run evaluate_final.py with the exact immutable preparation, training and browser-parity directories, then compare two completed final runs with compare_final_runs.py. A deterministic test-opened record is written before outcome parsing and survives interrupted/failed attempts. Complete byte comparison is separate. Private test-predictions.json never enters public Git or deployed assets.

The bilingual #4 Methodology and results tab consumes app-evidence.json. Its section IDs and aggregate chart/table data derive from the same final evidence as this report. The app must surface model/version, uncertainty/sparse support and accepted limitations. Parameter-only distribution needs the documented non-commercial rights review, source link and official logo. Actual-product footer, bundles and network QA remain #4/#8.

[Training review](../../reports/xg-training-methodology.md) · [Final command guide](../../architecture/reference/xg-final-evaluation.md) · [Rights record](../../architecture/reference/statsbomb-rights.md)
