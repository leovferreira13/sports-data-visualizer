# Playground and Methodology/results

**Status:** implemented in #4; public deployment remains #5.

## Responsibilities

`components/playable-pitch.tsx` retains the tab-scoped scene store, Pointer Events/capture and arrow-key controls. Number inputs provide an equivalent accessible position control. `lib/scenario.ts` owns deliberate add/remove, represented IDs and the zero-to-three defender UI limit; shooter/keeper cannot be removed. `lib/scenario-session.ts` writes v3 and migrates v1/v2 snapshots with a one-time disclosure for excess legacy defenders. Blocked storage leaves the in-memory scene usable.

`lib/selected-model.ts` verifies exact static asset bytes before parsing. `lib/model-store.ts` fetches the model once and exposes loading/ready/invalid states. `lib/predict.ts` remains the prediction authority. `components/prediction-panel.tsx` shows the current xG/percentage and eight live cards directly from the feature extractor. The owner removed the last-completed-change panel and its interaction bookkeeping; pure comparison helpers remain available for later guided experiments.

The pitch is on the left and results/cards on the right at desktop widths. On mobile, the result becomes a compact sticky strip, followed by the pitch and a two-column card grid. The strip is bounded by the Playground so it does not follow visitors into Methodology. Position inputs are available in a disclosure; mouse, touch and marker keyboard movement remain immediate. Count cards have no distance units. With zero defenders the nearest-defender card shows no value rather than presenting the sentinel as a physical distance. Penalty cards are explicitly scene measurements, while the separately labeled estimate stays fixed.

`components/methodology-content.tsx` server-renders evidence below the Playground on `/en#methodology` and `/br#methodology`, using `lib/xg-evidence.ts`. Plain anchors jump between sections without unmounting the scene. The previous `/en/methodology` and `/br/methodology` routes return 307 redirects to the corresponding anchor, preserving shared links. Locale switching retains the anchor and scene. There are no section tabs or technical-links promotional block. Support/illustration, omitted factors, tree plateaus and scientific limitations remain in Methodology, along with the source credit and shared footer.

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
