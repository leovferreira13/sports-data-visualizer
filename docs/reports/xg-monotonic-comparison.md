# Current versus monotonic XGBoost

**Status:** The measured scores and the two rule decisions are copied from `pair-identity.json` and `pair-metrics.json` attached to the owner's comment on pull request #44, [comment 6181026583](https://github.com/leovferreira13/sports-data-visualizer/pull/44#issuecomment-6181026583). That comment did not include `pair-decision.md`. In that comment the owner says he is inclined to keep the current model. The decision to keep the current model, and the confirmation of the coupled path, were stated by the owner in the Engineering Team group chat on 2026-10-14. AC1 proof is the artifact SHA-256 values plus `pair-identity.json`. A screenshot is not required.

`pair-metrics.json` has `decisions` and `summary.decisions`. Those two objects are the same.

## Bindings

`pair-identity.json` confirms the bindings the command enforces.

| Check | Value in `pair-identity.json` |
| --- | --- |
| Evidence id | `f62228e611a9712acaac4abcbc61b0f3ffc1ec0b0880e111bd0aa447f872dee8` |
| Seed | 42 |
| Split SHA-256 | `64f02e169df4b2d176b54ce47ef72a7afa3840d7990ac45b6841008e94aa71d1` |
| Training run | `222909fe801f4865897fea3541e023fed626f6736dca6ef69ceada1f7c57945a` |
| Current artifact | `758526873b8a3a2681f655c064dee52f8bd33749accd499d015420dbe8e11b9a` |
| Monotonic artifact | `e19402c5ba622ebc2775df202956aa5b942dd5e841b647cb7eeb531faf2a12ce` |
| Published file SHA-256 | `c0d91256a2c0f83ede48f1f549b8a0cc379e6ef675ccd4ce9ef10e471bb4350d` |

## Reproduce

Selection vectors live in the preparation run. The training directory alone cannot recompute log loss. Use the complete phase-A directory, not `docs/reports/xg-behavior-first-run/`.

```bash
.venv-xg/bin/python scripts/xg/compare_monotonic_pair.py \
  --prepared-dir <original-preparation-run-directory> \
  --training-dir <original-training-run-directory> \
  --research-dir <complete-phase-A-directory> \
  --output-dir data/derived/xg-behavior/issue-34
```

The command prints seed 42 and the split SHA-256 before scoring. It writes `pair-identity.json`, `pair-metrics.json`, and `pair-decision.md` under the output directory. Those files stay local. This report uses the two JSON files the owner attached.

## Decisions

| Rule | Decision | Why |
| --- | --- | --- |
| Full predeclared gates, including the jump-reduction gate (`jump_reduction_required` 0.25, `includes_jump_reduction_gate` true) | retain the current model | Predeclared gate failed: interactive_improvement |
| Log-loss increase limit of 0.005 and isolated direction checks (`includes_jump_reduction_gate` false) | recommend replacement | Log-loss increase is within 0.005 and isolated directions pass |

Decision depends on the revision: **true**.

Named by content: the full predeclared gates, including the jump-reduction gate, retain the current model because interactive improvement failed. The log-loss increase limit of 0.005 together with the isolated direction checks recommends replacement.

Original limits from `decisions.original_predeclared.limits`: `max_brier_degradation` 0.001, `max_log_loss_degradation` 0.005, `min_jump_rate_reduction` 0.25, `one_sided_confidence` 0.95.

Original predicates from `decisions.original_predeclared.predicates`:

| Predicate | Value |
| --- | --- |
| brier | true |
| constant_reference | true |
| interactive_improvement | false |
| invariants | true |
| log_loss | true |
| native_export | true |
| parity | true |
| partial_directions | true |
| primary_segments_available | true |

## Metrics

| Model | log_loss | brier | distance_violations | angle_violations | large_jump_rate | p95_jump | primary_pairs |
| --- | --- | --- | --- | --- | --- | --- | --- |
| full_xgboost | 0.23520839767656282 | 0.06697391552739276 | 34 | 6 | 0.04462474645030426 | 0.018686586990952492 | 986 |
| full_monotonic_xgboost | 0.2352457526107877 | 0.06694985410830383 | 0 | 0 | 0.04259634888438134 | 0.014600332826375961 | 986 |

Selection log-loss increase (monotonic minus current), `summary.log_loss_increase`: 3.735493422488134e-05. Limit, `summary.log_loss_limit`: 0.005. The same 0.005 is `decisions.revised.log_loss_increase_limit` and `decisions.original_predeclared.limits.max_log_loss_degradation`.

Paired upper bounds versus current from `summary`: log loss `log_loss_upper` 0.0008807877582937127, Brier `brier_upper` 0.0002560737066460752. The attached files do not include a field named `upper_95`. `one_sided_confidence` in the original limits is 0.95.

## Pair identity

Copied from `pair-identity.json`.

| Field | Value |
| --- | --- |
| current_artifact_id | `758526873b8a3a2681f655c064dee52f8bd33749accd499d015420dbe8e11b9a` |
| current_model_file_sha256 | `c0d91256a2c0f83ede48f1f549b8a0cc379e6ef675ccd4ce9ef10e471bb4350d` |
| evidence_id | `f62228e611a9712acaac4abcbc61b0f3ffc1ec0b0880e111bd0aa447f872dee8` |
| monotonic_artifact_id | `e19402c5ba622ebc2775df202956aa5b942dd5e841b647cb7eeb531faf2a12ce` |
| monotonic_model_file_sha256 | `66326f96854c2a17cb8483651b02db82dd5c5de445249690825b3a70b64e1f7c` |
| published_model_file_sha256 | `c0d91256a2c0f83ede48f1f549b8a0cc379e6ef675ccd4ce9ef10e471bb4350d` |
| published_model_unchanged | true |
| seed | 42 |
| split_sha256 | `64f02e169df4b2d176b54ce47ef72a7afa3840d7990ac45b6841008e94aa71d1` |
| training_run_id | `222909fe801f4865897fea3541e023fed626f6736dca6ef69ceada1f7c57945a` |

## AC1

Proof is the artifact SHA-256 values plus `pair-identity.json`. A screenshot is not required. The current artifact is `758526873b8a3a2681f655c064dee52f8bd33749accd499d015420dbe8e11b9a`, file SHA-256 `c0d91256a2c0f83ede48f1f549b8a0cc379e6ef675ccd4ce9ef10e471bb4350d`. The monotonic artifact is `e19402c5ba622ebc2775df202956aa5b942dd5e841b647cb7eeb531faf2a12ce`, file SHA-256 `66326f96854c2a17cb8483651b02db82dd5c5de445249690825b3a70b64e1f7c`.

## Coupled path

A local comparison page at `/dev/model-compare` was used for the evaluation and then removed. On that page, with the striker far from goal and no defenders nearby, xG for both models can rise slightly before it falls. That observation is in the GitHub comment, where the owner says he is inclined to keep the current model. In the Engineering Team group chat on 2026-10-14, the owner confirmed that this rise is a coupled path: the opening angle shrinks as distance grows, so it is not an isolated violation. It appears in both models.

## Final QA reading

Switching has no measurable accuracy cost and gives direction guarantees by construction. The files contain only violation counts (current 34 distance and 6 angle, monotonic 0 and 0), not sizes or locations, so a user-visible difference is rare and of unknown size, and is not shown to be invisible. An arc drag around the goal is an isolated angle move. The jump rate fell 0.2 percentage points, and the p95 jump went from 0.0187 to 0.0146. Those rounded figures read the `large_jump_rate` and `p95_jump` values in the metrics table.

## Owner decision

In the Engineering Team group chat on 2026-10-14, the owner decision is final: keep the current model, and make no replacement. The card's goal was user experience, and the difference is not shown to be perceptible. The monotonic gain is a direction guarantee by construction, without a proven user-visible improvement. The GitHub comment only says he is inclined to keep the current model.

## Publication

This comparison does not change `model/selected-model.json`, `public/model/selected-model.json`, or deployment configuration. The log-loss and isolated-direction rule recommends replacement, and that status does not publish the candidate. The published model stays the current XGBoost. The 0.8–0.9 probability band remains issue #40 and is not a gate here.
