# Playground and Methodology/results

**Status:** implemented in #4; public deployment remains #5.

## Responsibilities

`components/playable-pitch.tsx` retains the tab-scoped scene store, Pointer Events/capture and arrow-key controls. Number inputs provide an equivalent accessible position control. `lib/scenario.ts` owns deliberate add/remove, represented IDs and the zero-to-three defender UI limit; shooter/keeper cannot be removed. `lib/scenario-session.ts` writes v3 and migrates v1/v2 snapshots with a one-time disclosure for excess legacy defenders. Blocked storage leaves the in-memory scene usable.

`lib/selected-model.ts` verifies exact asset bytes with Web Crypto SHA-256, parses at runtime and creates an immutable handle through `loadModel`. `lib/model-store.ts` fetches the static `/model/selected-model.json` once and exposes loading/ready/invalid states across route/locale changes. The generated asset is copied byte for byte from the tracked model before dev/build; it is ignored to avoid a duplicate committed parameter file. `lib/predict.ts` remains the source of prediction status. `lib/insights.ts` computes full-precision comparisons, and `components/prediction-panel.tsx` formats learned/convention/unavailable/unsupported output and actual feature changes. Numeric inputs commit individually; keyboard bursts complete on blur or 450 ms inactivity; drag completes on up/cancel. Preset/reset clears the last comparison. Comparisons do not persist across refresh/navigation; the scene does.

`components/section-navigation.tsx` uses ordinary links with `aria-current`. Playground remains `/en` or `/br`; Methodology/results is `/en/methodology` or `/br/methodology`. Locale switching retains the active route. Tables and the calibration figure are server-rendered by `app/[locale]/methodology/page.tsx` from `lib/xg-evidence.ts`. The typed adapter uses the original app evidence and training aggregate/manifest, distinct from dated scientific/rights dispositions. Both dictionaries cover the narrative, including sparse high-probability bins and the adverse two-defenders-in-cone slice.

The learned field/feature contract, original presets and model parameters are unchanged. Deliberate removed-marker metadata changes only the UI adapter. No descriptive support warning disables valid inference. Original preset classifications disappear after editing; no training reference rows or per-shot predictions are shipped.

## Local verification

```bash
npm ci
npm run check:precommit
npm run build
npm run check:localization
```

Build runs `scripts/check-model.mjs` before Next.js. A parameter/evidence/checksum mismatch fails explicitly; restore the original reviewed envelope rather than re-exporting it. The application needs no private data directory or Python runtime.

With the locked offline Python environment from the training guide:

```bash
.venv-xg/bin/python scripts/xg/check_integrated_model.py
```

This checks the actual selected-model loader/predictor against independent Python using invented presets, zero-to-three defenders, varied scenes and float32 thresholds. It does not repeat private training or empirical evaluation. Optional Chromium/product QA uses a separately installed Playwright, as in the prediction guide:

```bash
npm install --prefix /tmp/xg-browser-tools --no-package-lock playwright@1.62.1
/tmp/xg-browser-tools/node_modules/.bin/playwright install chromium
NODE_PATH=/tmp/xg-browser-tools/node_modules \
  .venv-xg/bin/python scripts/xg/check_integrated_model.py --browser
NODE_PATH=/tmp/xg-browser-tools/node_modules \
  node scripts/check-playground-browser.mjs
```

`INFERENCE_CHROMIUM_EXECUTABLE` optionally chooses an intentional compatible local executable. The product script starts a local production server itself; `PRODUCT_QA_PORT` defaults to 3010. `PRODUCT_QA_OUTPUT` optionally records aggregate QA/network paths. Browser tools are absent from production dependencies.

See [integrated QA](../../reports/xg-playground-qa.md) and [ADR 009](../adr/009-integrated-playground-and-evidence.md). Public deployment smoke testing is still required in #5; none of these scripts authorize release.

## Exact distribution and asset inspection

Do not replace the static asset with a numeric JSON import: the integrated build audit found Turbopack decimal rewriting, described in ADR 009. The production model response must retain SHA-256 `c0d91256a2c0f83ede48f1f549b8a0cc379e6ef675ccd4ce9ef10e471bb4350d`. HTTPS (or loopback localhost) supplies Web Crypto; if integrity verification is unavailable or fails, learned predictions remain unavailable. Reload retries a failed asset request.

After staging current changes and building, run `python3 scripts/audit-product-assets.py` for the scoped tracked/build content and exact static-model check. It supplements the #8 history review; it is not a formal privacy guarantee.
