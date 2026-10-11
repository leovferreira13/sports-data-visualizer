# Browser prediction and model loading

**Status:** #12 inference infrastructure is implemented and tested with invented envelopes. Actual frozen-candidate parity needs the owner's completed training directory. The public page still displays geometry; #13/#8 gate release and #4 integrates results and methodology.

## Modules and result contract

`lib/model.ts` exposes `loadModel(unknown)`, `isLoadedModel` and `predictVector`. The loader checks `model/model-artifact.schema.json`, finite JSON, exact feature mapping/checksum, parameter dimensions, positive scaling, calibration, declared precision/tolerance and bounded topology. `model/inference-contract.json` pins the feature file's byte checksum, 300-tree/15-node/depth-3 execution bounds and penalty convention. Tests fail if the checksum or supported schema keywords drift. The narrow schema interpreter implements every keyword used by this schema; it is not a general-purpose JSON Schema library.

Loading returns `ready` with a frozen model handle, or `invalid` with `artifact_schema`, `artifact_contract` or `artifact_parameters`. A private WeakMap captures immutable parameters. Mutation of the original JSON and forged/copy-created handles cannot change inference. Cryptographic identity is checked by the local Python parity path, not recomputed from JavaScript JSON serialization. Runtime validation alone is not proof of provenance or authorization to distribute parameters.

`lib/predict.ts` exposes `predictScenario(unknown, model?)` for browser Scenario objects and `predictMetricScene(unknown, model?)` for metric fixtures. Both reuse `lib/features.ts` and the same evaluator.

| Status/source | Meaning | Probability |
| --- | --- | --- |
| `ok` / `learned-model` | Artifact/model/contract identity, retained features and observation metadata | Finite, in [0,1] |
| `ok` / `penalty-convention` | Explicit convention ID, `learned: false`; no learned artifact identity | Exactly 0.76 |
| `unsupported` | Stable feature/input reason, such as missing keeper or goal-line shot | Absent |
| `unavailable` | `missing_model`, `invalid_model` or `numeric_failure` | Absent |

No heuristic fallback, input clamping or missing-player imputation is used. Full-pitch metric scenes use the existing feature domain; UI scenes keep the Scenario adapter and two base defenders. Empty metric defender arrays use the pitch diagonal sentinel, with `zero_defender_support_unestablished`. Synthetic/browser results also carry `represented_scene_not_empirical_support`. Geometry does not identify sex or body part; the trained population remains male open-play foot shots. Extra attackers are omitted; only retained features have a claimed model effect.

## Numerical semantics

Logistic inference uses exported means/scales, coefficients/intercept and a stable double-precision sigmoid. XGBoost uses float32 inputs, strict `< threshold` branching, the exported base margin, sequential float32 leaf accumulation and float32 base probability (`Math.fround`). Identity or the exported sigmoid-of-clipped-logit calibrator runs afterwards. Nonfinite intermediate arithmetic fails explicitly.

The independent Python reference is `scripts/xg/model_export.py:predict_envelope`. Absolute probability tolerances remain **1e-10 for logistic** and **1e-7 for XGBoost**; feature comparisons use 1e-9 absolute plus 1e-9 relative tolerance. Tree plateaus are expected: a movement need not change a probability. Controlled comparisons do not establish causality or monotonicity.

## Separate penalty route

A plain object explicitly marked `shotType: "penalty"` (Scenario) or `shot_type: "penalty"` (metric adapter) routes before feature/model checks. It returns the fixed 0.76 convention even without geometry or a loaded model. Position changes never modify the value. Unknown types and malformed containers are unsupported. This is discriminator routing, not penalty detection from coordinates. Penalties are excluded from both training and held-out evaluation.

## Local verification

Use the locked Python 3.12 environment from the [training guide](xg-training.md), plus `npm ci`. **No retraining is needed.** Pass the exact immutable directory printed by `train_models.py`, containing `manifest.json`, `selection.json` and `selected-model.json`:

```bash
.venv-xg/bin/python scripts/xg/check_browser_inference.py \
  --training-dir <completed-training-directory> \
  --output-dir data/derived/browser-inference/first

.venv-xg/bin/python scripts/xg/check_browser_inference.py \
  --training-dir <completed-training-directory> \
  --output-dir data/derived/browser-inference/repeat

python3 scripts/xg/compare_runs.py \
  --left-dir <first-completed-browser-inference-directory> \
  --right-dir <second-completed-browser-inference-directory>
```

Success prints `PASS: ... frozen-local-candidate; fixed tolerances agree` and the immutable directory. Compare those printed directories, not output roots. Wrong-phase input, absent candidates, selection/provenance/hash disagreement, contract drift or tolerance failures return nonzero without a completed report. Preserve errors for review; do not change the candidate or tolerance to force a pass.

The command verifies the whole training inventory/hash identity, reads selected parameters and selection/protocol evidence, and generates synthetic cases. It never interprets held-out labels. It builds the production TypeScript modules with pinned esbuild in browser mode, rejects external dependencies, then executes that exact bundle in Node. Six presets (including penalty), movements, invalid scenes, deterministic varied scenes and exported float32 threshold boundaries are compared with Python. Invalid count/domain boundary vectors are negative tests, never rounded into valid inputs.

For test-only verification without the real artifact:

```bash
.venv-xg/bin/python scripts/xg/check_browser_inference.py \
  --synthetic --output-dir data/derived/browser-inference/synthetic
```

`--synthetic` uses eight explicitly invented logistic/tree and calibration fixtures. It proves software parity, not actual model quality or actual-candidate parity.

### Optional actual browser execution

`--browser` executes the same cases in local headless Chromium through a temporary loopback HTTP server. No public debug route is shipped. Install Playwright outside the project dependencies:

```bash
npm install --prefix /tmp/xg-browser-tools --no-package-lock playwright@1.62.1
/tmp/xg-browser-tools/node_modules/.bin/playwright install chromium

NODE_PATH=/tmp/xg-browser-tools/node_modules \
  .venv-xg/bin/python scripts/xg/check_browser_inference.py \
  --synthetic --browser --output-dir data/derived/browser-inference/chromium
```

Replace `--synthetic` with `--training-dir <completed-training-directory>` for the local candidate. Set `INFERENCE_CHROMIUM_EXECUTABLE` only for an intentionally selected compatible Chromium executable. Reports identify engine/version. Node and Chromium reports differ; repeat the same mode/environment for byte comparison.

## Evidence and distribution

Completed verification emits only `parity.json` and `manifest.json`: model/run identity, code/contract hashes, counts, maximum errors, tolerances, engine and command pattern. Share those files plus the comparator result. Detailed cases and actual weights are not emitted. The harness size measures code/schema without real parameters; it is not the final model bundle size.

After #8/#13 review, #4 may load a reviewed parameter-only envelope through `loadModel` and pass the handle to `predictScenario`. Committed JSON, static/downloadable assets and client bundles all distribute parameters and require review. A loader failure leaves predictions unavailable; recover with the correct verified artifact. See [verification status](../../reports/xg-browser-inference.md) and [ADR 007](../adr/007-browser-inference-and-penalty.md).
