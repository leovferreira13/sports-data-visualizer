# Offline xG training

**Status:** #11 training is implemented; actual-corpus aggregate evidence passed review and complete local reproduction was confirmed by the owner. The frozen XGBoost candidate passed owner-run browser-bundle parity and passed final-test automated gates and aggregate scientific review with support limitations; no public estimate is enabled.

## Responsibilities

- `model/training-protocol.json` declares the experiment matrix, seeds, tuning bounds, calibration, selection rules, bins, support checks and tolerances before real fitting.
- `prepare_training.py` verifies the complete immutable feature run and current extraction/contract hashes, then partitions whole matches without using labels to allocate them. It emits separate train, calibration, selection and test files. Test outcomes never appear in the preparation summary.
- `training.py` fits fold-local pipelines and tunes on training only. `evaluation.py` calculates probability scores, fixed bins, slices, training-only exploration and paired match bootstrap comparisons.
- `train_models.py` reads development partitions only, fits calibration separately, compares candidates on selection validation and freezes the exact pipeline. It verifies the held-out file's hash as part of input integrity, but never parses its rows, fits on its outcomes or calculates test metrics. This is a software/procedural boundary, not encryption against the operator.
- `model_export.py` converts parameters and independently evaluates the export. `scene_evaluation.py` uses invented fixtures checked against current browser presets by Vitest.
- `report_training.py` validates aggregate evidence and regenerates the English report. `compare_training_runs.py` checks complete runs with declared tolerances; `compare_runs.py` retains its exact audit/feature meaning.

The workflow is offline. The browser and production build do not install Python ML dependencies. Training tests have a dedicated required CI job using invented data only; the existing pre-commit discovery continues to use the standard library.

## Local environment

Use Python **3.12** on Linux x86-64 (the reference platform) and the existing Node environment for repository checks. The lock pins all resolved Python packages, including the CPU-only XGBoost wheel and schema validation dependencies. The tested Python patch version was 3.12.14. Other platforms need a documented compatibility/reproduction check; do not silently change dependencies.

From the repository root:

```bash
python3.12 -m venv .venv-xg
.venv-xg/bin/python -m pip install -r scripts/xg/requirements.lock
.venv-xg/bin/python -m pip check
.venv-xg/bin/python -m unittest discover -s scripts/xg/training_tests -p 'test_*.py' -v
npm run check:precommit
```

The environment is ignored. Training verifies installed package versions against the lock. Keep the committed protocol and code fixed for all compared runs. A configuration change is a new experiment/protocol with a documented reason, not a retry to improve a result.

## Execute the actual corpus

The reviewed feature directory ends with run ID `fe7c19c44a1101d61a39df586c957a1b85fef523a3c2a03c4c7faea603374517`. Change only the enclosing path if your local extraction used another output root. The directory must contain the complete `features.jsonl`, `feature-audit.json` and `manifest.json`, not just the uploaded aggregate audit.

First verify the two complete feature runs, if available, using the exact comparator from #10. Equal aggregate JSON alone is insufficient:

```bash
python3 scripts/xg/compare_runs.py \
  --left-dir data/derived/xg-features/fe7c19c44a1101d61a39df586c957a1b85fef523a3c2a03c4c7faea603374517 \
  --right-dir data/derived/xg-features-repeat/fe7c19c44a1101d61a39df586c957a1b85fef523a3c2a03c4c7faea603374517
```

Prepare the partitions:

```bash
.venv-xg/bin/python scripts/xg/prepare_training.py \
  --input-dir data/derived/xg-features/fe7c19c44a1101d61a39df586c957a1b85fef523a3c2a03c4c7faea603374517 \
  --output-dir data/derived/xg-training/prepared
```

The script prints `Complete private preparation: <path>; test outcomes unopened`. Substitute that **exact printed directory** below for `<prepared-run-directory>`:

```bash
.venv-xg/bin/python scripts/xg/train_models.py \
  --input-dir <prepared-run-directory> \
  --output-dir data/derived/xg-training/first
```

Each model prints its stage; the bounded search has 60 logistic and 40 XGBoost fold fits, followed by four full-training fits. All four estimators are considered, including identity/sigmoid calibration variants; a constant training-prevalence reference is evaluated on the same selection rows. No early stopping, class reweighting or post-selection refit occurs.

The successful output is `Complete immutable training: <path>; test outcomes unopened`. Completion does **not** imply a model was selected: read `selection.json`, whose status is `frozen_candidate` or `no_candidate`. If support is inadequate, preparation fails before fitting with an explicit reason. If no model qualifies, preserve that evidence and discuss remediation; do not open the final test to find a better choice.

The owner ran training on the actual corpus. The submitted aggregate evidence and generated report passed consistency review, and the owner confirmed complete local reproduction. The assistant did not train on private rows. See the [reviewed training results](../../reports/xg-training-methodology.md) for the selected candidate, rationale, uncertainty and verification limits. Synthetic tests validate execution and invariants, not empirical model quality.

## Fresh environment and complete reproduction

Recreate a fresh Python 3.12 environment from the same lock. Use the same code, protocol and feature input; independently prepare into a second output root and train again:

```bash
.venv-xg/bin/python scripts/xg/prepare_training.py \
  --input-dir data/derived/xg-features/fe7c19c44a1101d61a39df586c957a1b85fef523a3c2a03c4c7faea603374517 \
  --output-dir data/derived/xg-training/prepared-repeat

.venv-xg/bin/python scripts/xg/train_models.py \
  --input-dir <second-prepared-run-directory> \
  --output-dir data/derived/xg-training/repeat

.venv-xg/bin/python scripts/xg/compare_training_runs.py \
  --left-dir <first-training-run-directory> \
  --right-dir <second-training-run-directory>
```

On the same environment, also use `compare_runs.py` to require byte-identical complete preparation/training directories. The training comparator verifies each manifest's own identity and every output hash, exact inventory/split/configuration/dependencies/source/decisions and numeric outputs. It allows absolute metric/parameter differences up to 1e-8 and private predicted-probability differences up to 1e-6. Logistic/tree export tolerances remain independently 1e-10/1e-7. Integer counts, labels, topology and decisions must be exact.

Derived artifact/evidence/preparation IDs may differ when their inputs' bytes differ; each remains internally validated. Python patch versions and any byte differences are reported, never called byte-identical. The comparator does not ignore scientific code/configuration changes. A changed selected model or any tolerance failure is a failed reproduction.

The comparator requires two outputs from `train_models.py`, each printed as `Complete immutable training: <path>`. A `prepare_training.py` output is a different phase and must be compared with `compare_runs.py`. Both training manifests must declare `phase: training`. Diagnostics identify an incorrect phase by side, or list the filenames present only on the left/right when training inventories differ. Each run's inventory and hashes are verified before this check, so do not add, delete or edit files to make the lists match. Update the comparator and inspect the existing runs without retraining; the diagnostic update does not change comparison rules.

## Output and review contract

All scientific outputs stay under ignored `data/derived/`. Publication is staged atomically; completed directories cannot be overwritten. A changed input/code/configuration fails the run. Remove an abandoned staging directory if an OS-level interruption leaves one; rerun into a fresh output root. Do not delete or edit the source corpus.

| File | Purpose | Share for review? |
| --- | --- | --- |
| Preparation `preparation-summary.json` | Development class counts, label-blind test counts/composition and UI audit diagnostics | Yes; aggregate only |
| Training `evaluation.json` | Versioned exploration, CV, validation scores/calibration/slices, selection and provenance | Yes; aggregate only |
| Training `selection.json` | Frozen choice or explicit no-candidate decision, paired differences and rationale | Yes; aggregate only |
| Training `methodology.md` | Generated English narrative and tables from the same evaluation evidence | Yes |
| Training `manifest.json` | Run identity, hashes, environment and provenance | Yes; no rows |
| `validation-predictions.json` | Private match identities, outcomes and per-shot model predictions | **No** |
| Preparation `train/calibration/selection/test.jsonl`, `split.json` | Private vectors/outcomes and exact fixture assignments | **No** |
| `*-raw.json`, model envelopes and `selected-model.json` | Parameters/preprocessing/calibration; candidate is not approved for public distribution | Keep local pending #8/#13 export review |

After both runs, share **`evaluation.json`, `selection.json`, `methodology.md`, `manifest.json` and the comparator's terminal result**. Include `preparation-summary.json` if preparation succeeds but training fails. A failure before preparation completes needs only its terminal error. These are the review inputs needed before #13; do not upload shot-level files or browse the held-out file.

`model/evaluation.schema.json` disallows unknown fields, including held-out goal counts. Additional checks reject shot-level keys. `model/evaluation-contract.json` identifies aggregate evidence consumed by the later bilingual app tab; #13 adds separate final-test evidence rather than replacing validation comparisons. The technical report is regenerated directly from `evaluation.json`, so it has no manually copied metric values. Reviewed aggregate evidence/report can later be committed under `docs/reports/`.

## Modeling choices and limitations

Largest-remainder allocation implements approximate 60% train, 20% validation (10% calibration and 10% selection), 20% test in four physical files. All competition-season strata must be represented. Training CV is label-blind and match-isolated; each holdout needs 50 goals/non-goals, each validation subdivision 100. These are operational support gates, not assurances of predictive quality.

Logistic scaling is learned only inside each training fold and on training for the final estimator. Standardized coefficients describe conditional association under correlation/regularization. An omitted feature group produces no claimed numeric effect; full logistic remains the comparison baseline. The full-vs-no-keeper experiment isolates incremental keeper information.

Sigmoid calibration uses two fitted parameters on calibration data only. A nonpositive/degenerate slope is declined. Selection uses log loss first, Brier as a guardrail, 1,000 paired match bootstrap resamples and the predeclared 0.0001 rules. Simplicity wins unresolved differences. These exploratory comparisons are not an independent final test.

A zero observed defender list uses a sentinel, never an inferred empty pitch. Continuous distance distributions/correlations omit sentinel rows. Keeper extremes, full-pitch/UI differences and partial visibility need empirical-support review. Marginal ranges alone cannot establish joint support; the model does not represent extra attackers, keeper alignment, identity, technique or motion. Scene changes are comparisons within the model, not causal claims or mandatory monotonic relationships.

The export validator checks full feature order/checksum, retained indices, fitted scale, model kind, calibration and topology. Logistic evaluation uses double precision; XGBoost conversion preserves float32 inputs/thresholds and sequential float32 margin accumulation. Only inference-relevant parameters survive conversion from the documented save-model JSON. Synthetic scene references contain no source examples. #12 implements browser-safe inference and a [local parity command](prediction.md#local-verification); use the existing completed training directory without refitting. Actual-candidate parity and complete local comparison passed with owner-run evidence; see the [inference review](../../reports/xg-browser-inference.md). Final evaluation/rights/public release remain #13/#8.

## Final-test handoff

Issue #13 now provides a [separate final evaluator](xg-final-evaluation.md). Use the original complete preparation/training runs and matching actual-candidate parity without another fit. Actual-corpus scientific review is accepted with limitations; the final publication decision remains pending.

## Actual-corpus final review

The owner-run final evidence passes all automated predicates and the owner reports all requested comparators PASS. Aggregate identity/provenance and report/app consistency were independently checked. Scientific evidence is accepted with sparse/extreme/preset support limitations; actual parameter/export/rights and integrated #4/#8 publication QA remain pending. See `docs/reports/xg-final-evaluation.md` and `docs/reports/xg-final-review-record.json`. Public xG remains disabled.
