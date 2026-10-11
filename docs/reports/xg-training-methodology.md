# xG training methodology: first actual-corpus review

**Issue:** #11. **Protocol:** `xg-training/v1`.
**Status:** the owner's first actual-corpus training artifacts passed aggregate, provenance and report consistency review. The owner confirmed successful complete local reproduction with the training directories. Final-test evaluation and public release remain pending.

## Evidence and verification limits

The reviewed training run is `222909fe801f4865897fea3541e023fed626f6736dca6ef69ceada1f7c57945a`, with evidence ID `52d8467f8db6064c4bfd565aecbce05857f3869d61b5905490f076adc3a5c0df`. It uses feature run `fe7c19c44a1101d61a39df586c957a1b85fef523a3c2a03c4c7faea603374517`, StatsBomb revision `4b73468fc5b0f1950f9f66fada70ad3a4f9327cb`, Python 3.12.3 and the committed dependency lock.

The assistant verified the submitted manifest's canonical identity, hashes of the three submitted outputs, evaluation schema and aggregate-only fields, evaluation/manifest provenance agreement, selection equality and byte-for-byte report regeneration. Recorded code/configuration hashes matched the implementation at commit `7964494c1fe954b47f6092b4a9e4eec56526095e` before the comparator diagnostics update. The private parameter envelopes, split and per-shot predictions were not supplied, so their manifest-declared hashes and empirical metrics were not independently recomputed from private rows.

The four partitions account for all 35,020 shots and 1,813 represented matches. Training has 20,777 shots/1,966 goals across 1,087 matches; calibration has 3,440 shots/314 goals across 183 matches; selection has 3,643 shots/324 goals across 180 matches. Held-out test reporting contains only 7,160 shots and 363 matches plus label-blind composition. Do not derive or publish held-out goal counts from other aggregate totals.

## Results and interpretation

Read the original [generated methodology](xg-training-first-run/methodology.md), [aggregate evaluation](xg-training-first-run/evaluation.json), [selection record](xg-training-first-run/selection.json) and [manifest](xg-training-first-run/manifest.json). The generated report contains comparison tables sourced from the same evaluation artifact; this review does not maintain a second table of metric values.

All four trained models improve the constant training-prevalence reference on selection validation under the declared paired rules. The XGBoost candidate has the lowest observed log loss and Brier score. Its selected configuration is depth 2, learning rate 0.05, minimum child weight 5 and 300 trees; all eight features are retained. None of the fitted sigmoid calibrators was adopted because none satisfied the predeclared improvement criteria.

The full-logistic-versus-XGBoost log-loss interval includes zero. The selection rule still rejects full logistic as competitive because its observed Brier degradation exceeds the predeclared 0.0001 guardrail. That is a protocol-driven candidate decision, not conclusive proof that XGBoost generalizes better. Selection uncertainty is exploratory and must stay distinct from the final evaluation in #13. Do not alter the protocol after seeing this result.

The submitted export checks pass their recorded tolerances: logistic conversion has zero reported difference and XGBoost's reported error is below 1e-7. This is owner-run evidence of offline export parity, not independent verification of the unsupplied envelopes or browser parity. Controlled synthetic responses are finite and show defender/keeper effects, but sparse/unfamiliar support and the zero-defender sentinel still need #13 review.

## Complete local reproduction and handoff

The initial failures came from comparing preparation directories with the training comparator. They were an input-phase mistake, not evidence of differing fitted models. The CLI now distinguishes incorrect phases from differing training inventories and preserves integrity, provenance, schema and numeric diagnostics without changing scientific thresholds.

After using the completed training directories, the owner reported:

```text
PASS: 17 files verified; 0 files differ byte for byte
PASS: scientific configuration, decisions and numeric tolerances agree
```

This confirms successful owner-run complete comparison, rather than equality of aggregate files alone. The assistant reviewed the submitted aggregates and comparator output; it did not execute this comparison against private rows. Separate creation of a fresh environment was not independently verified here.

The training implementation and actual-corpus selection/reproduction evidence are ready for #11 review. Keep the candidate frozen. Issue #12 must establish browser inference parity, and #13 must evaluate the exact frozen candidate, full-logistic baseline and constant on the unopened final test. Public release still needs #8/#13 review. Do not refit, retune or weaken the protocol using the final test.
