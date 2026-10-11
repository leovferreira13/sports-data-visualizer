# Browser inference verification

**Issue:** #12. **Date:** 2026-10-11. **Status:** implementation, invented-artifact checks and owner-run frozen-candidate parity pass; complete local comparison is owner-confirmed. No public xG is enabled.

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

The first owner-local parity attempt stopped before prediction because the checker compared the recorded canonical protocol digest with the formatted source file digest. Training intentionally identifies `canonical(protocol)`; the feature contract intentionally retains its raw file byte digest. The corrected checker follows those separate identities and reports protocol-content, protocol-identity and feature-identity drift separately. A regression test checks the committed first actual-corpus manifest digest and a synthetic completed training run; negative tests retain rejection of real changes. The synthetic evidence above was regenerated with this correction. No scientific configuration, model parameters or tolerances changed; no retraining is required. The owner rerun passed; its reviewed evidence is recorded below.

## Actual-candidate review and remaining gates

The owner supplied [parity.json](xg-browser-inference-first-run/parity.json) and [manifest.json](xg-browser-inference-first-run/manifest.json) from completed inference run `2bb3480ed11edf50a166e4a2328bfb4171ceba36a547ef1abfd53128cca12770`. It verifies the exact #11 `full_xgboost` candidate `758526873b8a3a2681f655c064dee52f8bd33749accd499d015420dbe8e11b9a`, from training run `222909fe801f4865897fea3541e023fed626f6736dca6ef69ceada1f7c57945a`.

The run checked **2,886 cases**: 184 learned scenes, three penalty cases, ten unsupported scenes and 2,689 vector cases (189 invalid vectors are a subset). The maximum probability difference was **0**, against the fixed 1e-7 tolerance. The maximum feature residual was 1.4210854715202004e-14. Execution used the browser-target bundle in Node 22.22.2, esbuild 0.28.2 and Python 3.12.3. This is actual-candidate Node execution; the separately recorded actual Chromium checks used invented envelopes. Do not describe it as an actual-candidate Chromium run.

The assistant verified the submitted manifest's canonical identity, report byte hash, complete two-file inventory, report/manifest agreement, exact inference code hashes against the PR implementation, frozen artifact/training identity, counts and declared tolerance. The report records no held-out label interpretation or parameter publication. The actual envelope and private training rows were not supplied; the assistant did not independently recompute its probabilities.

The owner also reported **PASS from the complete-run comparator** for repeated local parity runs. This is owner-confirmed complete comparison, not an assistant rerun against both private directories. No second run artifact or verbatim terminal log was supplied. The reviewed first-run aggregates and owner confirmation satisfy the #12 numerical-parity handoff; the implementation is ready for review/QA. Issue closure remains subject to merge and checks.

#13 evaluates the exact frozen candidate on the unopened test, examines empirical scene support and finalizes the model card/release decision. Final #8 QA reviews actual asset/parameter distribution and attribution. #4 integrates the public result and bilingual Methodology and results tab after those gates. Numerical parity does not demonstrate empirical support, transfer, causality or rights to distribute weights.
