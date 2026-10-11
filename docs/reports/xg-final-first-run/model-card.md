# Independent positional xG model card

**Model:** full_xgboost; **artifact:** `758526873b8a3a2681f655c064dee52f8bd33749accd499d015420dbe8e11b9a`.

**Evidence:** `e579e10f9699077ddf05e7433af5ed63edf0e03c3ea8c7ca295844951d74ea08`; **decision:** needs_review; publication requires dated review.

Intended use: free non-commercial professional portfolio and educational scene comparisons. Not a StatsBomb model or endorsement. No claim of individual-player ability or causal effect.

Population: male open-play left/right-foot shots with valid embedded positional observations and one opposing keeper. Headers, penalties and missing/multiple keepers are excluded. Unseen defenders/attackers are not reconstructed.

Source: [StatsBomb Open Data](https://github.com/hudl/open-data), revision `4b73468fc5b0f1950f9f66fada70ad3a4f9327cb`. Conditional Hudl support scope and official source/logo obligations are recorded in docs/architecture/reference/statsbomb-rights.md. Public parameters, code and aggregate reports remain within the reviewed non-commercial scope. No raw source/shot records may be distributed.

Features, training-only exploration and experiment comparison are preserved in final-evaluation.json development_evidence. Training-only scaling/CV, separate calibration and selection validation precede this frozen match-held-out test. No post-selection refit.

Selected retained inputs: shot_distance_m, goal_opening_angle_deg, absolute_lateral_offset_m, visible_defender_count, defenders_in_cone_count, nearest_visible_defender_distance_m, goalkeeper_distance_to_goal_m, goalkeeper_distance_to_shot_m.

Final log loss: 0.239965, 95% interval [0.225625, 0.255290]; Brier: 0.068339, 95% interval [0.063826, 0.072950].

See methodology.md for reference comparisons, paired uncertainty, calibration, supported/sparse slices and scene diagnostics. Those aggregate tables are generated from the same evidence; small differences are not automatically decisive.

Penalty estimates are a separate fixed 0.76 convention and are not learned or evaluated with the open-play model. Browser float32 tree semantics and independent numerical tolerances are retained. Missing/invalid input gives unsupported/unavailable, with no heuristic fallback.

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

## Release and recovery

Statistical failures preserve a withheld result. Successful automated checks require independent complete reproduction, explicit calibration/slice/support review and a dated decision bound to model/evidence hashes. #4 still owns integrated production QA, bilingual attribution/logo and the mandatory methodology tab. Keep xG unpublished while any critical finding remains.

Reproduce with the locked Python environment, original immutable runs, evaluate_final.py and compare_final_runs.py; see docs/architecture/reference/xg-final-evaluation.md. Evidence verification must distinguish owner-run computations from independent recomputation.
