# Current versus monotonic XGBoost

**Status:** PLACEHOLDER. This commit does not contain measured scores, a decision, or a screenshot. Those values stay empty until the owner runs the comparison locally with the private preparation, training, and phase-A directories, then posts `pair-metrics.json`, `pair-identity.json`, the decision table, and a `/dev/model-compare` screenshot on the pull request.

The bindings below are identity checks the command enforces. They are not measurements from this workspace.

## Bindings

| Check | Required value |
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

The command prints seed 42 and the split SHA-256 before scoring. It writes `pair-identity.json`, `pair-metrics.json`, and `pair-decision.md` under the output directory. Those files are local. This report must be updated from them, not from memory of an earlier review.

## Decisions

| Rule | Decision | Why |
| --- | --- | --- |
| Original predeclared, including the 25% jump-reduction gate | PLACEHOLDER | PLACEHOLDER |
| Revised (log-loss increase at most 0.005 and isolated directions) | PLACEHOLDER | PLACEHOLDER |

Decision depends on the revision: **PLACEHOLDER**.

## Metrics

| Model | Log loss | Brier | Distance violations | Angle violations | Primary >0.02 jump rate | Primary p95 jump |
| --- | --- | --- | --- | --- | --- | --- |
| full_xgboost | PLACEHOLDER | PLACEHOLDER | PLACEHOLDER | PLACEHOLDER | PLACEHOLDER | PLACEHOLDER |
| full_monotonic_xgboost | PLACEHOLDER | PLACEHOLDER | PLACEHOLDER | PLACEHOLDER | PLACEHOLDER | PLACEHOLDER |

Selection log-loss increase (monotonic minus current): PLACEHOLDER. Limit: 0.005.

Paired one-sided 95% upper bounds versus current: log loss PLACEHOLDER, Brier PLACEHOLDER.

## Pair identity

PLACEHOLDER. Copy the local `pair-identity.json` values here after the command succeeds. Do not invent file hashes.

## Screenshot

PLACEHOLDER. Not captured in this commit.

Capture `/dev/model-compare` while `XG_COMPARE=1` and `XG_CANDIDATE_MODEL` points at the phase-A `candidate-model.json`. The current column must show artifact `758526873b8a3a2681f655c064dee52f8bd33749accd499d015420dbe8e11b9a`. The monotonic column must show artifact `e19402c5ba622ebc2775df202956aa5b942dd5e841b647cb7eeb531faf2a12ce`. One scene must feed both estimates, with pointer and keyboard movement still available.

## Publication

This comparison does not change `model/selected-model.json`, `public/model/selected-model.json`, or deployment configuration. A recommendation, if the local run produces one, needs a separate issue before anything is published. The 0.8–0.9 probability band remains issue #40 and is not a gate here.
