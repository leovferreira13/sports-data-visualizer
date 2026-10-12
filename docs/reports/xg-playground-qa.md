# Integrated Playground and Methodology QA

**Current-status note (2026-10-12):** #24 extends the reviewed product to five languages; #25 prepares portfolio presentation; #26 owns Railway publication and remaining live/branding checks. Earlier release gates below describe this report's dated scope. Local reviewed-model xG is implemented; no live release is claimed.

**Date:** 2026-10-11. **Reviewer:** assistant/implementer. **Branch:** `agent/4-public-ready-playground`. **Scope:** #4 implementation and local production QA; no public deployment/visibility change.

Machine-readable evidence and exact code/build identities: [QA record](xg-playground-qa.json). The base is `d8469ea88ecccf4e2e41f64f13d8a0e10dbfc539`; the record includes the production build ID and a SHA-256 inventory of application/model/verification code. It does not claim that a deployed public URL was tested.

## Delivered behavior

The Playground executes the unchanged reviewed independent XGBoost with explicit loading, learned, unsupported and unavailable states. Six original editable presets remain unchanged. Zero to three represented defenders can be added/removed, shooter and keeper remain mandatory, and extra attackers are visual only. Deliberate removal changes the Scenario adapter without changing the frozen feature domain/checksum. v3 snapshots preserve locale/navigation/reload behavior and migrate excess legacy defenders with a disclosure.

Following local product review, current xG and eight live input cards replace the last-completed-change panel and expanded observations block. Desktop uses pitch-left/cards-right; mobile uses a compact sticky xG strip, pitch, then two-column cards. Position controls are collapsible. Support, illustrative presets, omitted factors and tree plateaus are explained in Methodology; valid exploration is never gated.

Methodology/results inline at `/en#methodology` and `/br#methodology` shares the reviewed aggregate numerical sources with the reports: match partitions, baseline experiments, selection versus final test, paired score uncertainty, calibration with sparse flags/intervals and the adverse two-defenders-in-cone slice. Tables supply accessible equivalents to the SVG calibration chart; narrative and interface labels are translated. The requested technical-links block is removed from the UI; repository documentation retains those references. Former dedicated routes redirect to the anchors.

## Validation results

- Canonical pre-commit: lint/types, 50 TypeScript tests, 55 Python tests and English Markdown checks PASS. Existing browser-inference harness regression: 7 tests PASS.
- Production build and localized/direct route smoke tests PASS.
- Independent Python versus browser-safe integration bridge: 706 invented scenes/float32 threshold vectors PASS in Node 24.19.0 and Chromium 153.0.8010.0. Maximum probability error: 0.0; feature error: 1.4210854715202004e-14, within fixed tolerances. This supplements original actual-training evidence without new fitting or private-row access.
- Actual production UI: original preset outputs, mouse drag, keyboard movement, touch emulation, add/remove/limit, eight live input cards, penalties, refresh, methodology anchors, locale/view preservation and blocked session storage PASS in both locales. Desktop 1440 × 1000 and mobile 390 × 844 show no document overflow. Logo loading/alternative text/source credit passed on both views/locales. Visual inspection guided layout changes that keep interaction ahead of detailed evidence.
- Pending model load, HTTP failure and mutated bytes have no learned estimate or heuristic fallback. The fixed penalty route remains available during failure. All pass in actual Chromium.
- Tracked JSON/path and production static/prerendered asset inspection PASS: no source-record signatures or forbidden data paths found. Browser requests contain routes, ordinary Next assets/images and the approved parameter-only model; no inference API or source-event/360/per-shot prediction requests.
- Exact model response SHA-256 matches the reviewed original: `c0d91256a2c0f83ede48f1f549b8a0cc379e6ef675ccd4ce9ef10e471bb4350d`. Parameter asset: 96,241 bytes; gzip measurement: 19,029 bytes. These are measured file sizes, not latency or quality claims.

## Important build finding and plan deviation

The proposed numeric JSON import failed exact final-bundle inspection: Turbopack changed some decimal doubles during module serialization. Ordinary preset/parity checks had not exposed it because the standalone inference harness uses esbuild. A tiny upward threshold shift can change strict comparison behavior at equality.

The final implementation copies the original tracked envelope into a generated ignored static asset before dev/build. The browser fetches its exact bytes, verifies Web Crypto SHA-256 before parsing, validates model identity/schema and captures an immutable handle. This avoids compiler rewriting, provides clear load/failure states and introduces no inference API. See [ADR 009](../architecture/adr/009-integrated-playground-and-evidence.md). Frozen parameters and original aggregate evidence were not changed.

## Attribution and release boundary

Official README and agreement Git blobs remain identical to the #8 review on this date. The official Media Pack still resolves to the reachable public **Hudl Statsbomb Logos** collection. The existing official reversed PNG is unchanged, proportionally rendered with source link/alternative text, and accompanied by accurate independent-model/non-commercial wording. The product has no ads, payment, account, source-record download or resale path.

**Still open before publication:** exact current per-asset branding guidance could not be independently verified anonymously. The public collection shell is reachable, but that does not establish detailed per-asset rules. Keep this as an explicit #4 publication review item; do not infer new permission or claim it passed. No new general support inquiry is required for the unchanged scope.

#5 also needs owner publication authorization and a smoke test of the actual public deployment, including final assets/network/attribution. A future build has a new identity and should rerun the concrete checks. Local emulated touch is not a physical-device check. Current content inspection is scoped and does not replace the previously recorded #8 history review or establish a general model-privacy guarantee.

## Layout revision QA

The revised production browser walkthrough verifies desktop orientation, eight cards, live distance updates after keyboard/drag input, zero-defender display, omitted-attacker invariance, independently labeled penalty measurements, both locale anchors, legacy redirects, mobile two-column ordering and sticky result visibility. Removed tabs, last-change panel and expanded observations do not appear. Lazy footer image loading is awaited explicitly after the now-longer inline methodology page. Desktop/mobile screenshots were inspected internally; no screenshots are committed.

The original 706-case independent parity results are retained as prior evidence because the envelope, numeric inference and feature extractor are unchanged. Current build/asset and browser identities are refreshed in the machine-readable record. This revision does not rerun training or claim new empirical performance.

## Repeatable commands

See the [integration reference](../architecture/reference/playground-and-methodology.md) for setup, optional Playwright/Chromium and Python requirements. Run the canonical checks and build, then the localized-route/product-browser and actual-model parity scripts. After staging the intended files, `python3 scripts/audit-product-assets.py` verifies current tracked/build assets and the exact model copy. No private corpus or retraining is required.
