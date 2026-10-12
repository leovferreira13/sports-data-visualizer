# ADR 006: Offline training and a frozen parameter export

**Current-status note (2026-10-12):** the original decision below retains its implementation-stage context. #4 integrates the reviewed model; #24 provides five locales; #26 owns public release. See the [current architecture](../overview.md).

**Status:** accepted and implemented for issue #11. Actual-corpus selection and locally confirmed complete reproduction are recorded in the [training review](../../reports/xg-training-methodology.md); browser parity and final-test/public-release review remain #12/#13 responsibilities.

## Context

The project needs reproducible probability estimates from eight positional features without a production inference service. Data remains private on the local training machine. Feature contributions, calibration and model complexity must be examined carefully and exposed through the future app methodology tab.

## Decision

Use a locked Python 3.12 CPU environment for offline fitting. The committed protocol fixes match-isolated, competition-season allocation into training, calibration validation, selection validation and an unopened final test. Fold-local logistic scaling and bounded train-only CV tune three logistic feature groups and one shallow XGBoost candidate. Separate calibration fitting prevents reuse of its outcomes for the reported selection score.

Compare natural-log loss, Brier, calibration and paired match-bootstrap evidence on identical selection rows. Prefer the simplest competitive candidate; allow an explicit no-candidate result. Freeze the exact trained/preprocessed/calibrated pipeline without refitting on validation. Preserve full logistic and training-prevalence reference for final evaluation.

Export parameter-only versioned JSON, independently verify its predictions, and keep candidate exports local. Logistic parameters include fitted scaling; XGBoost nodes retain objective/base-margin and float32 inference semantics. Browser parity is a separate #12 responsibility.

Emit versioned aggregate evaluation evidence and generate report tables from it. The later bilingual Methodology and results tab consumes the same evidence; final-test results are a separate #13 artifact. No real rows, coordinates, match/event identities or per-shot predictions enter public evidence.

## Alternatives and consequences

A training API or runtime Python service would introduce infrastructure unrelated to v0.1. Unbounded tuning would make selection less auditable. Reusing calibration rows for selection would produce an optimistic assessment of calibration. Automatic class balancing would change the natural probability-estimation target; it is omitted.

Splitting validation reduces each subdivision's sample size, so explicit support gates can stop the workflow. Match holdout does not prove league/period transfer. Partial shot-frame visibility differs from user-represented browser scenes, and correlated features do not imply causal effects. Local execution/reproduction must be reviewed before selecting a real model; a correct script does not establish model fitness or rights to publish its actual parameters.
