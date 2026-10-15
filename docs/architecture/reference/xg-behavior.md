# Offline xG behavior evaluation

**Status:** #31 phase A has been locally executed and reproduced; submitted aggregate evidence is reviewed as exploratory, with the original retain-current decision preserved. #34 adds a local comparison of the frozen current XGBoost and the already fitted monotonic candidate. The committed [#34 report](../../reports/xg-monotonic-comparison.md) records the owner's posted `pair-identity.json` and `pair-metrics.json`. AC1 proof is the artifact SHA-256 values plus `pair-identity.json`. A screenshot is not required. Phase B is not required for this scoped closure. See the [review](../../reports/xg-behavior-comparison.md). The published artifact and five-language product evidence remain unchanged.

## Boundary and rationale

`model/behavior-protocol.json` and its pinned schema declare the experiment before fitting. The immutable original full logistic and published XGBoost remain references. A new full XGBoost family restricts shot distance negatively and goal-opening angle positively, holding all other inputs fixed. The eight-feature contract is unchanged. Positive-slope sigmoid calibration preserves partial directions. Trees can still plateau; a physical drag changes multiple features and can reverse predictions.

Research has its own historical input loader, manifest phase and output comparator. This avoids weakening the original training, parity and final-evaluation input guards to accept another experiment. The shared parameter schema/browser loader accepts the named research tree envelope for parity; the production asset selection, rights hash and publication gate are unchanged.

The original test was already opened. Phase A uses only original train/calibration/selection rows with adaptive exploratory labeling. Frozen references are also checked against their original native selection predictions. It never parses the original test rows. Manifest verification still reads their bytes to check file hashes. Original feature semantics, split, reviewed training manifest, reference envelopes, dependency lock and exact published artifact must match; research fitting code has a separate identity. An incomplete/mismatched original run fails before fitting.

## Environment and inputs

Use the original Python 3.12 environment and dependency lock, plus Node dependencies:

```bash
npm ci
python3.12 -m venv .venv-xg
.venv-xg/bin/python -m pip install -r scripts/xg/requirements.lock
.venv-xg/bin/python -m pip check
```

Use the **complete original** preparation and training directories. Do not re-prepare/retrain them with the new research code. The actual original training run is `222909fe801f4865897fea3541e023fed626f6736dca6ef69ceada1f7c57945a`; its manifest points to the original preparation run. A folder containing uploaded aggregate files alone is insufficient. Local commands below use placeholders for their exact paths.

For a quick behavioral check of the exact published artifact, with invented scenes and no private rows or fitting:

```bash
.venv-xg/bin/python scripts/xg/diagnose_behavior.py \
  --output-dir data/derived/xg-behavior/published
```

This produces `published-behavior.json`, the frozen protocol and private detailed traces. It cannot evaluate probability quality or empirical scene support. It is not the three-model selection experiment.

## Phase A: exploratory comparison

Before the first fit, accept the protocol's tradeoffs: one-sided 95% paired-match upper degradation bounds of 0.005 log loss and 0.001 Brier; reference improvement under the original constant rules; correct isolated distance/angle directions; and at least 25% fewer >0.02 jumps with no higher p95 on supported ordinary continuous physical segments. If the current large-jump rate is zero, the candidate needs zero rate and strictly smaller p95. No supported segments means insufficient behavioral evidence, not a vacuous pass.

The matrix is frozen: original full logistic, exact current XGBoost and one bounded monotonic XGBoost family. It uses the original eight-combination tree grid, train-only folds/seed and calibration/selection boundary. There is no enlarged search, class reweighting, test tuning or post-selection refit. Inspect coefficients/signs and correlated distance inputs; logistic partial signs are not assumed.

```bash
.venv-xg/bin/python scripts/xg/evaluate_behavior.py \
  --prepared-dir <original-preparation-run-directory> \
  --training-dir <original-training-run-directory> \
  --output-dir data/derived/xg-behavior/first

.venv-xg/bin/python scripts/xg/evaluate_behavior.py \
  --prepared-dir <original-preparation-run-directory> \
  --training-dir <original-training-run-directory> \
  --output-dir data/derived/xg-behavior/repeat

.venv-xg/bin/python scripts/xg/compare_behavior_runs.py \
  --left-dir <first-completed-research-directory> \
  --right-dir <second-completed-research-directory>
```

Use the exact completed directory printed by each command, not its enclosing output root. On the same environment, `compare_runs.py` can also require byte-identical research runs. The research comparator verifies all output hashes/inventories, regenerates the report and checks provenance, decisions, topology and original numeric tolerances. Do not alter output files to make it pass.

Each model runs the browser-targeted TypeScript bundle in Node against the shared behavioral cases, valid threshold probes, invalid inputs and penalty convention. Add `--browser` to execute actual Chromium as well; this requires the optional local Playwright installation documented in [prediction](prediction.md). The report records the engine. Python fitting remains outside the production runtime.

### What the diagnostics mean

- Isolated distance and angle sweeps use full probabilities, 0.1 m/0.1 degree steps, preset anchors and label-blind train anchors. They may be physically inconsistent vectors and are labeled accordingly. Native raw/calibrated and exported monotonic directions are checked independently.
- Physical shooter/keeper/defender paths have at most 0.1 m steps. Full coordinates and all eight per-step deltas stay local. Rounded user examples are synthetic analogues because the complete original scene was not recorded.
- Dense cone crossings and explicit just-inside/on/outside probes distinguish count jumps. Zero through three represented defenders, sentinel/float32 boundaries, reflection/order invariants and invalid scenes are checked.
- Plateaus use `|delta| <= 1e-7`. The longest plateau is reported in meters/degrees. Jump median/p95/max and >2 percentage-point rates use raw probability values, independently of UI rounding.
- Primary physical segments have ordinary context, unchanged count inputs and two endpoints within the train-only reference. Outside/insufficient reference, extreme and count transitions are separately reported, never erased. A nearest-neighbor diagnostic cannot prove calibration or realism.
- Probability scores, calibration residual intervals and sparse/support slices include the adverse cone-count possibilities. Supported review flags remain explicit. Required review does not authorize replacement.

## Issue #34: frozen pair, no new fit

`scripts/xg/compare_monotonic_pair.py` scores the exact current XGBoost and the phase-A monotonic candidate on the same selection rows. It does not call tune or fit, does not score logistic, and does not write the published model or deployment configuration. The revised accuracy rule is a selection log-loss increase, monotonic minus current, of at most `protocol.decision.max_log_loss_degradation` (0.005 in the frozen protocol; mean clipped binary log loss, clip 1e-12). Exactly that limit passes. Brier is reported and is not the pass/fail metric for the revised column. Recomputed log loss must match the phase-A record within 1e-08 or the run fails as an identity mismatch. That check is not the accuracy tolerance.

Intuitive direction is an isolated sweep: the other seven features stay fixed. Distance uses direction -1, so more distance must not raise xG. Opening angle uses direction +1, so a wider angle must not lower xG. A step is a violation when the probability change times that direction is below -1e-7. Features 2–7 stay unconstrained.

Fluidity is the plateau share (`|delta| <= 1e-7`) and the rate of jumps above 0.02 on primary physical pairs. Plateaus may remain. The original column is the full predeclared `gates` result: paired log loss, paired Brier, constant reference, partial directions, primary segments, the jump-reduction gate, invariants, parity, and native export. Every numeric limit is read from `protocol.decision` (`max_log_loss_degradation` 0.005, `max_brier_degradation` 0.001, `min_jump_rate_reduction` 0.25 in the frozen protocol). The revised column does not use that gate set. It retains when identity or primary pairs do not match, when the selection log-loss increase is above `max_log_loss_degradation`, or when an isolated distance or angle sweep has a violation; otherwise the status is recommend replacement. `recommend_replacement` does not publish the candidate. `depends_on_revision` is true when the two statuses differ. The 0.8–0.9 band is issue #40 and is not a gate.

Selection vectors are in the preparation run, so `--prepared-dir` is required. The training directory must be run `222909fe801f4865897fea3541e023fed626f6736dca6ef69ceada1f7c57945a`. The research directory must be the complete phase-A directory, including `candidate-model.json` and `current-model.json`. `docs/reports/xg-behavior-first-run/` is an aggregate subset and is not a runnable input.

```bash
.venv-xg/bin/python scripts/xg/compare_monotonic_pair.py \
  --prepared-dir <original-preparation-run-directory> \
  --training-dir <original-training-run-directory> \
  --research-dir <complete-phase-A-directory> \
  --output-dir data/derived/xg-behavior/issue-34
```

The command prints seed 42 and split SHA-256 `64f02e169df4b2d176b54ce47ef72a7afa3840d7990ac45b6841008e94aa71d1` before scoring. It writes `pair-identity.json`, `pair-metrics.json`, and `pair-decision.md` under ignored `data/derived/`. The committed report copies the posted `pair-identity.json` and `pair-metrics.json`. The owner did not attach `pair-decision.md`. AC1 proof is the artifact SHA-256 values plus `pair-identity.json`. A screenshot is not required.

A local comparison page at `/dev/model-compare` showed one scene against both envelopes, with pointer drag and arrow keys. It was used for the evaluation and then removed.

The owner confirmed that a rise far from goal, with no defenders nearby, is a coupled path: the opening angle shrinks as distance grows, so it is not an isolated violation. It appears in both models. The final QA reading is that switching has no measurable accuracy cost and gives direction guarantees by construction. The posted files contain only violation counts (current 34 distance and 6 angle, monotonic 0 and 0), not sizes or locations, so a user-visible difference is rare and of unknown size, and is not shown to be invisible. An arc drag around the goal is an isolated angle move. The jump rate fell 0.2 percentage points, and the p95 jump went from 0.0187 to 0.0146. The model decision belongs to the owner.

## Phase B: optional genuinely unused matches

If no such matches are available, stop at the exploratory disposition. A new seed or repartition of the used corpus cannot create an untouched test.

Reservation must happen **before the first candidate fit** and be passed into both Phase A runs. Obtain a complete fresh feature run pinned to the same eligible population/feature semantics. All accepted matches in that run must be unused; the command rejects overlap rather than silently filtering matches. A feature run can physically contain labels; reservation decodes rows but examines only match identities, not outcome values or performance. Do not use new outcome summaries to select the cohort.

Prepare a private JSON declaration under ignored `data/derived/`, with exactly these fields:

```json
{
  "prior_use_complete": true,
  "outcomes_not_used_for_choice": true,
  "prior_match_ids": [1, 2, 3],
  "eligibility": "Describe the pinned cohort and how prior use was audited"
}
```

Replace the example IDs with the **complete** prior-use ledger: all original train/calibration/selection/test matches and any other matches previously ingested, explored, trained, calibrated, selected or evaluated. The tool requires coverage of all original split IDs and rejects overlaps. Unknown external prior use cannot be mechanically proved; the declaration is a provenance requirement, not a software guarantee. Never upload this ledger.

```bash
.venv-xg/bin/python scripts/xg/behavior_holdout.py reserve \
  --prepared-dir <original-preparation-run-directory> \
  --training-dir <original-training-run-directory> \
  --feature-dir <complete-unused-feature-run-directory> \
  --usage-declaration data/derived/xg-behavior/prior-use.json \
  --output-dir data/derived/xg-behavior/reserved
```

Add `--reservation-dir <completed-reservation-directory>` to **both** Phase A commands above. Changing protocol, scientific code or reserved membership after sealing requires a new documented experiment; do not reuse the opened holdout. The research run binds the reservation identity before tuning.

Only if an alternative passes the exploratory gates, open the reserved matches once:

```bash
.venv-xg/bin/python scripts/xg/behavior_holdout.py evaluate \
  --research-dir <completed-research-directory> \
  --reservation-dir <completed-reservation-directory> \
  --output-dir data/derived/xg-behavior/fresh
```

The fresh evaluator uses the frozen choice/calibration and the same quality margins, with minima of 50 matches and 100 goals/non-goals. It does not refit or select another model. A marker under the reservation parent's `.behavior-test-access` directory is created **before** loading labels, survives failure and prevents a second opening. This is a local procedural guard, not security against copying/deleting files. A failed test/support check withholds replacement. Do not remove access records or retune against opened matches. A recovery after operational failure needs an explicit reviewed record acknowledging prior opening.

## Shareable outputs and completion

| File | Role | Share for review? |
| --- | --- | --- |
| `behavior-evaluation.json` | Aggregate three-model scores, behavior, support and gate dispositions | Yes |
| `selection.json` | Retain/recommend disposition and failures/reviews | Yes |
| `protocol.json` | Frozen declared experiment | Yes |
| `comparison.md` | Generated English comparison | Yes |
| `parity.json`, `manifest.json` | Engines, numerical evidence and identities | Yes |
| `fresh-evaluation.json` | Optional once-opened aggregate confirmation | Yes |
| `*-model.json`, `candidate-raw.json` | Frozen parameter envelopes | Keep local pending replacement review |
| `sweep-details.json` | Complete coordinates/vectors/probabilities, including private train anchors | **No** |
| `validation-predictions.json`, reservation files/ledger | Private shot predictions/outcomes/membership | **No** |

Share the aggregate outputs and complete comparator terminal result after local execution. Until then, tooling success is not evidence of actual candidate quality. Synthetic CI tests validate software only. A recommendation needs independent-evidence disposition, supported calibration/slice review, rights/export review, reproduction and an explicit publication decision, followed by updated five-language Methodology and product QA. #31 never writes the published model or adjusts goalkeeper defaults.
