# ADR 008: Frozen final evaluation and an explicit publication gate

**Current-status note (2026-10-12):** the original decision below retains its implementation-stage context. #4 integrates the reviewed model; #24 provides five locales; #26 owns public release. See the [current architecture](../overview.md).

**Status:** implemented infrastructure for #13; actual-corpus scientific review accepted with limitations; distribution/publication decision pending.

## Context

The frozen candidate and browser-bundle parity have locally executed evidence. The final match-held-out test must independently assess the exact pipeline before public xG. Data stays local, and the future Methodology and results tab must expose the same evidence as the technical report.

## Decision

Keep the original training protocol, split, parameters, preprocessing and calibration immutable. Add a separate predeclared final-evaluation protocol and aggregate schema. Compare the candidate, preserved full logistic and training-prevalence reference on identical test rows. Whole-match paired bootstrap preserves correlation and shot weighting. Calibration, sparse slices and training-only synthetic scene-support diagnostics are explicit review inputs.

Verify historical manifest/linkage integrity and unchanged scientific semantics rather than requiring old broad code hashes to equal newly added evaluation files. Record current evaluation/browser hashes separately. Record opening intent before test parsing and preserve it across failures; deterministic reruns reproduce an opened test rather than an untouched holdout.

Generate report, model card and schema-validated app evidence from one immutable aggregate artifact. Private outcomes/predictions stay under ignored derived paths. Automated results are needs_review or withheld; quantitative failures preserve completed evidence. A dated decision bound to evidence/model hashes and distribution review is required before model integration eligibility. Actual integrated production/bilingual attribution/methodology and assets QA remain #4/#8 publication requirements.

## Consequences and alternatives

Retuning against the test would invalidate its independent role. Quietly changing the candidate to the logistic baseline after failure would be another selection step. Treating every shot as independent would underrepresent shared match context. Manually maintained report/app metric tables could drift. Automatic publication based on statistical checks would omit support, rights and product review.

Feature-space support is descriptive, not a proof of realistic joint player configurations or a new runtime exclusion. Passing an observed baseline guardrail does not prove equivalence. Scientific or critical qualitative failures withhold release; a later model change needs an explicitly revised independent evaluation. The final empirical selection/release decision will be appended only after actual local execution and evidence review.

## Actual-corpus review (2026-10-11)

Final aggregate evidence was submitted and all requested comparators were reported PASS locally. All automated predicates pass; paired final scores favor the frozen XGBoost within the represented cohort. Sparse/extreme calibration, an adverse cone-count slice, partial visibility and four outside-reference open-play presets require explicit app explanations. See the [dated review](../../reports/xg-final-evaluation.md) and [review record](../../reports/xg-final-review-record.json). The original needs_review artifact is preserved; actual parameter/export/rights and integrated publication QA remain pending. No model or evaluation rule changed.
