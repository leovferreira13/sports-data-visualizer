# Frozen xG final evaluation and release gate

**Status:** offline tooling and reviewed actual-corpus evidence are implemented; reported local reproduction and independent aggregate inspection remain distinct. #4 integrates the unchanged reviewed model, #24 supplies five locales and #26 owns public release/live checks.

The offline evaluator emits immutable evidence and generated aggregate app/report views, with a complete comparator. Synthetic execution validates software behavior only. Actual held-out evidence and reported local comparator PASS were supplied; aggregate scientific review accepts them with support limitations. Metrics were not independently recomputed from private rows.

## Boundaries and protocol

`model/final-evaluation-protocol.json` is fixed before actual test access. It adds final confirmation checks without changing `model/training-protocol.json`, the split, parameters, preprocessing or calibration. `final-evaluation.schema.json` identifies test evidence separately from the unchanged development evidence embedded within it. `app-evidence.schema.json` validates the aggregate view for #4.

The original preparation/training runs remain valid historical inputs. `final_inputs.py` verifies their manifest identities, inventories, links and unchanged scientific semantics; new evaluation/report files do not require another preparation or fit. Required feature/model/training/protocol changes fail compatibility. Dependencies must match the existing lock. Actual-candidate parity must match the frozen artifact and current browser evaluator. If parity is stale, rerun its command without training again.

`evaluate_final.py` reads development rows for verified counts, training prevalence and training-only support. Only after input verification does it record test opening and parse `test.jsonl`. The record is stored outside completed inventories both under the output root and beside the preparation under `.final-test-access/`. It records opening intent conservatively: even a failed attempt must no longer be casually described as untouched. Deterministic repeats reproduce the same opened test. Private source runs are never edited.

## Local commands

Use the locked Python 3.12 environment in [training](xg-training.md), plus `npm ci` if browser parity must be rerun. Do **not** run `prepare_training.py` or `train_models.py` again for this task.

Supply the complete preparation directory that produced the reviewed training run, the original completed training directory ending in `222909fe801f4865897fea3541e023fed626f6736dca6ef69ceada1f7c57945a`, and the completed browser-parity directory. Each directory contains its own `manifest.json`; output roots are not valid phase inputs.

```bash
.venv-xg/bin/python scripts/xg/evaluate_final.py \
  --prepared-dir <original-completed-preparation-directory> \
  --training-dir <original-completed-training-directory> \
  --parity-dir <completed-actual-candidate-browser-parity-directory> \
  --output-dir data/derived/xg-final/first

.venv-xg/bin/python scripts/xg/evaluate_final.py \
  --prepared-dir <original-completed-preparation-directory> \
  --training-dir <original-completed-training-directory> \
  --parity-dir <completed-actual-candidate-browser-parity-directory> \
  --output-dir data/derived/xg-final/repeat
```

Both commands print `Complete immutable final-evaluation run: <path>`. Use those **exact printed directories**:

```bash
.venv-xg/bin/python scripts/xg/compare_final_runs.py \
  --left-dir <first-completed-final-directory> \
  --right-dir <second-completed-final-directory>

python3 scripts/xg/compare_runs.py \
  --left-dir <first-completed-final-directory> \
  --right-dir <second-completed-final-directory>

.venv-xg/bin/python scripts/xg/report_final.py \
  --run-dir <first-completed-final-directory>
```

The final comparator verifies every declared file, private-prediction scores, report/card/app regeneration, scientific provenance and decisions. Metrics use 1e-8 absolute tolerance; private probabilities use 1e-6. Counts, labels, support categories, release predicates and identities remain exact. It reports Python patch versions and byte differences. `compare_runs.py` is the separate exact-byte check; neither equality of uploaded aggregates nor a comparison against the same directory establishes complete independent reproduction. Record whether the second run used a recreated environment.

The report command regenerates views in memory and checks their bytes without modifying the immutable directory.

## Exit status and recovery

| Code | Meaning | Next action |
| --- | --- | --- |
| 0 | Complete evaluation; automated checks passed; `needs_review` | Compare complete runs and review calibration/slices, support, rights and publication scope |
| 2 | Complete evaluation; candidate `withheld` | Preserve the printed run and failed predicates; compare/review it; do not switch models using the test |
| 1 | Integrity, contract or operational failure; no completed run | Read the error and test-opened record; correct the software/input issue and reproduce into a fresh root |

A completed withheld run is useful evidence, not an operational crash. A new model/protocol after seeing outcomes requires an explicit revised evaluation and defensible independent assessment. Never weaken criteria or call this test untouched again. Atomic publication prevents partial runs from masquerading as complete. OS interruptions may leave a staging directory; preserve opening records, remove only abandoned staging output, then rerun.

## Statistical checks

All predictors use identical test rows: frozen selected model, full logistic with its selected calibration and constant training prevalence. No test fitting occurs.

- Minimum support: 100 goals, 100 non-goals and 50 matches.
- Selected-minus-constant log loss: point estimate and upper paired 95% endpoint both below -0.0001.
- Selected-minus-constant Brier deterioration at most 0.0001.
- Selected-minus-full-logistic observed log loss and Brier deterioration each at most 0.0001. These are guardrails, not an equivalence/superiority test.
- Retained positional groups must respond somewhere in the declared synthetic probe family; invariants and unsupported-input handling must hold. Individual tree plateaus are allowed.

`final_statistics.py` samples whole matches with replacement, preserving repeated-match multiplicity and shot weighting. The 1,000 shared draws use seed 7421 and percentile 95% intervals. Bins retain counts, match support, valid/skipped replicates and null intervals where between-match uncertainty cannot be estimated. Sparse means fewer than 100 shots or 10 goals. Supported calibration-bin residual intervals excluding zero require review. Diagnostic slices do not receive multiple-comparison superiority claims.

Distance, angle, keeper distance, defender counts, cone counts, nearest observed defender distance and competition-season slices are fixed in advance. The nearest-distance zero-defender category represents missingness, not a defender at the sentinel location. Metadata uniformly describes partial embedded frames with an observed keeper; optional 360 visible-area coverage is unavailable as a test covariate. Prior reviewed aggregate audits supply the exclusion/coverage/UI-bound context.

`final_scenes.py` uses training-only standardized retained-feature nearest-neighbor RMS distances. A deterministic sample of up to 2,000 rows and its 99th-percentile leave-one-out distances provide a descriptive reference. Zero-defender rows form a separate cohort and omit the sentinel distance. Sparse/constant cohorts have insufficient reference. These categories do not prove realistic joint scene support, impose monotonicity or introduce a new runtime rejection rule. Accepted limitations and required warnings belong in #4.

## Outputs and review contract

| Output | Meaning | Share/commit? |
| --- | --- | --- |
| `final-evaluation.json` | Final scores, uncertainty, slices, synthetic diagnostics, original development evidence and provenance | Yes, after aggregate review |
| `release-checks.json` | Predeclared predicates and unresolved review requirements | Yes |
| `methodology.md`, `model-card.md` | Generated English narrative and tables | Yes |
| `app-evidence.json` | Versioned aggregate section/chart/table data for #4 | Yes |
| `protocol.json`, `manifest.json` | Scientific policy and immutable run identity/inventory | Yes |
| `test-predictions.json` | Private match IDs, outcomes and per-shot probabilities | **No** |
| Test-opened records | Local accounting of outcome access | Keep local; report their status accurately |
| Frozen parameter envelopes | Inference parameters | Remain local pending distribution review |

Share the seven public files above plus both comparator terminal results. No private rows or predictions are needed for aggregate review. Public schemas reject unknown fields recursively; reports/app views regenerate from the validated evidence. Scientific identities do not replace verification of actual inputs or distribution rights.

## Release handoff and remaining decisions

Automated results are only `needs_review` or `withheld`. A dated owner/implementer record must identify exact final evidence/model IDs, completed reproduction, calibration flags, supported/sparse slice findings, scene support, accepted limitations, current rights sources and parameter-only export inspection. It must state critical findings, their disposition and whether the model is eligible for #4 integration. No generated artifact authorizes publication automatically.

A release record should include: date; reviewer; code commit; training/final/model IDs; quantitative checks; reproduction commands/environment; calibration/slice/support conclusions; current terms/logo and conditional approval scope; export/content/history findings; accepted limitations and required UI warnings; `eligible for integration` or `withheld`; and outstanding #4/#8 publication QA.

Recheck [StatsBomb rights](statsbomb-rights.md) for the documented free non-commercial portfolio and parameter distribution. The recorded support response already covers that scope; a material scope change requires a fresh review. Inspect tracked content/history and proposed assets for source rows or recoverable examples. Before actual publication, #4/#8 must additionally inspect real integrated bundles/network assets and visible accessible attribution/logo on `/en` and `/br`, including small screens; the Methodology and results tab is mandatory. Current geometry-shell QA cannot attest to that later product.

#3/#8 are closed after their scoped completion; final integrated and live release checks are documented separately in #4/#26. Merge, board state and publication remain controlled actions.

## Current integrated delivery

Scientific evidence is accepted with sparse/extreme/preset support limitations. Exact parameter-only content and scoped rights/history review are recorded; local #4 integration QA is complete. Final Railway deployment, refreshed release assets/branding and live verification remain #26. See the [final review](../../reports/xg-final-evaluation.md) and [integration reference](playground-and-methodology.md). Historical pre-integration gates in earlier sections do not describe the current app status.
