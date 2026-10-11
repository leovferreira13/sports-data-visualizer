# Browser inference verification

**Issue:** #12. **Date:** 2026-10-11. **Status:** implementation and invented-artifact verification pass; actual frozen-candidate parity remains pending owner-local execution. No public xG is enabled.

## Scope and reviewed evidence

The production TypeScript loader/evaluator was exercised with eight explicitly invented parameter envelopes: geometry, defenders and full logistic, plus full XGBoost, each with identity or sigmoid calibration. These are software test fixtures, never empirical training or model-quality evidence.

The exact browser-targeted bundle passed **1,620 cases per engine**, including six presets, controlled movements, unsupported scenes, vector domain failures and float32 threshold boundaries. Original aggregate evidence and immutable manifests are committed under [Node evidence](xg-browser-inference-synthetic/node/parity.json) / [manifest](xg-browser-inference-synthetic/node/manifest.json) and [Chromium evidence](xg-browser-inference-synthetic/chromium/parity.json) / [manifest](xg-browser-inference-synthetic/chromium/manifest.json). These files contain no actual weights, source rows or detailed scene inputs. Both reports pin inference code and feature-contract hashes.

| Check | Observed evidence | Result |
| --- | --- | --- |
| Browser-target bundle in Node 24.19.0 | Maximum probability error 2.220446049250313e-16 | Pass |
| Actual Chromium 153.0.8010.0 | Maximum probability error 1.942890293094024e-16 | Pass |
| Python/TypeScript scene features | Maximum absolute residual 1.4210854715202004e-14 | Pass under existing absolute/relative rule |
| Two complete Chromium runs | Two files verified, no byte differences; same run identity | Pass |
| Canonical pre-commit checks | Lint, TypeScript, 42 Vitest tests, 55 stdlib Python tests, Markdown and shell checks | Pass |
| Locked offline training suite | 17 tests, including inference parity and complete synthetic training/reproduction | Pass |
| Production build and localized routes | Build plus `/en` and `/br` smoke checks | Pass |

Each model's probability check uses its fixed tolerance (logistic 1e-10, XGBoost 1e-7), not a relaxed combined threshold. Supported results are finite/in [0,1]. Penalties return exactly 0.76 with convention metadata and remain invariant under player movement or absent/invalid models. Schema/mapping/preprocessing/calibration errors, invalid topology, forged handles and nonfinite arithmetic have explicit failure behavior. Tests verify omitted feature groups and attackers cannot alter predictions.

The minified synthetic harness is 14,521 bytes, excluding parameter payloads; this is not the actual selected-model bundle size. The Chromium run used Playwright 1.62.1 with a temporary Chromium executable from `@sparticuz/chromium` 153.0.0 because the managed environment could not download the standard browser archive. The executable override is supported by the local runner; no browser binary/package or debug route is added to the project.

## Reproduction and implementation choices

Follow the [prediction guide](../architecture/reference/prediction.md#local-verification). The bridge bundles the production modules once with pinned esbuild's browser target, checks that the bundle has no external imports, and executes the same bundle in Node or local Chromium. This replaces the spec's proposed Vitest subprocess bridge, making actual browser verification possible without a shipped test page. Vitest retains contract/numerical/failure tests. See [ADR 007](../architecture/adr/007-browser-inference-and-penalty.md).

`check_browser_inference.py` validates completed-training phase, manifest/output hashes, frozen selection, experiment-envelope equality, feature/protocol identity and provenance before predicting. It does not refit, tune or interpret held-out labels. Success publishes only aggregate `parity.json` and `manifest.json`; failure publishes no complete run. Repeat comparisons use the existing `compare_runs.py`, including manifest identity and byte equality. Chromium repeat run identity: `cf8ea9106d1ae1827a1dcd9d808d1c0a0b5e4b9ab88123916857130854402166`.

## Canonical protocol identity correction

The first owner-local parity attempt stopped before prediction because the checker compared the recorded canonical protocol digest with the formatted source file digest. Training intentionally identifies `canonical(protocol)`; the feature contract intentionally retains its raw file byte digest. The corrected checker follows those separate identities and reports protocol-content, protocol-identity and feature-identity drift separately. A regression test checks the committed first actual-corpus manifest digest and a synthetic completed training run; negative tests retain rejection of real changes. The synthetic evidence above was regenerated with this correction. No scientific configuration, model parameters or tolerances changed; no retraining is required. Actual-candidate parity still needs the owner rerun.

## Actual-candidate handoff and remaining gates

The reviewed #11 record selects `full_xgboost`, artifact ID `758526873b8a3a2681f655c064dee52f8bd33749accd499d015420dbe8e11b9a`. Its actual parameter envelope remains on the owner's machine and was **not** verified by these invented-artifact checks.

Run the local parity command twice against that existing completed training directory, then compare the printed completed parity directories. Share only both parity/manifest files and the comparison output. If an integrity, unsupported-format or tolerance error occurs, preserve it and investigate the exact frozen artifact rather than changing thresholds or silently substituting a candidate. Actual-candidate parity remains an open #12 acceptance item until that evidence passes.

#13 evaluates the exact frozen candidate on the unopened test, examines empirical scene support and finalizes the model card/release decision. Final #8 QA reviews actual asset/parameter distribution and attribution. #4 integrates the public result and bilingual Methodology and results tab after those gates. Marginal compatibility and synthetic numerical parity do not demonstrate real-world support, transfer, causality or rights to distribute weights.
