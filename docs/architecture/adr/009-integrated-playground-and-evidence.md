# ADR 009: Integrated frozen model, bounded scenes and inline evidence

**Status:** implemented in #4; merge and public release remain owner-controlled.

## Context

The positional model has accepted scientific evidence and a scoped parameter-only distribution review. The playable UI still needs to connect that evidence to its actual behavior. Visitors need immediate interaction; technical readers need methodology without a second metric source. The current Scenario requires two base defenders, while free educational exploration needs deliberate removal and a three-defender UI bound.

## Decision

- Serve the original reviewed envelope as an exact static JSON asset. Dev/build checks copy the tracked source bytes into a generated ignored public asset after provenance verification. The browser checks SHA-256 before parsing, validates the selected artifact and captures its immutable handle once. Infer locally with the existing predictor; never use a heuristic fallback. Loading, network failures and mismatched bytes are explicit states; penalties remain available without the model.
- Keep the learned eight-feature contract and ten-defender model domain unchanged. The UI permits zero to three represented defenders. Preserve base marker IDs/coordinates and explicitly exclude deliberately removed base defenders in the Scenario adapter. Missing coordinates are still errors; shooter and keeper remain mandatory. Extra attackers are visual only.
- Write v3 session snapshots. Read valid v1/v2 snapshots, retain base coordinates and the first extra defender when a legacy snapshot exceeds the new UI limit, disclose the migration once, and retain coordinates across route/locale navigation. This migration is not inference clamping or a support-based rejection.
- Owner revision (2026-10-11): show eight retained feature inputs as compact live cards beside the pitch, with the estimate above them. Remove the last-completed-change panel and related event bookkeeping. The math, feature contract and static envelope remain unchanged.
- Render Methodology below Playground on the same page. Scrolling preserves the mounted scene without jump or return links; old `/methodology` routes redirect to the localized anchor. Server-render aggregate tables, calibration SVG/table, paired uncertainty and the adverse cone-count slice. Remove the technical-links block while retaining repository documentation.
- Keep descriptive preset/support explanations in Methodology, not above the interaction. No private reference rows or invented joint-support classifier are exported. Rare valid scenes remain computable.

## Consequences

Parameters are distributed as a downloadable static asset, under the exact scoped rights disposition. Aggregate evidence remains server-side except for the rendered view. No Python, database or inference API is required in production.

Zero-defender inference is mathematically defined but empirical support is unestablished. UI limits do not imply supported scene accuracy. Tree outputs remain discontinuous. Optional local browser QA and actual-envelope parity supplement the original private-training evidence without reopening labels or fitting a model.

Actual production build/network/attribution review is recorded separately. Detailed anonymous per-asset Media Pack guidance remains a documented release check if inaccessible; publication, public URL verification and visibility changes belong to #5 with owner authorization. Reverting the focused PR restores the prior geometry-only UI; frozen evidence is not rewritten.

## Evidence-based deviation from the spec

The first implementation followed the proposed static JSON import. Final asset inspection found that Next.js 16.3.6/Turbopack changed some exported decimal doubles by roughly one double ULP when serializing JSON modules. Ordinary preset outputs still passed, but an exported float32 threshold must remain exact: a threshold moved slightly upward can route an equal float32 input to the wrong leaf under strict `<`. Normalizing parameters or loosening tolerance would hide the distribution mismatch.

The static byte-preserving asset is the smallest robust alternative. The source envelope remains unchanged; build and browser hashes verify it. Production QA covers pending loading, failed download, mutated bytes and independent penalty routing. No inference endpoint or private reference data is introduced.

## Responsive interaction revision

At desktop widths the pitch is left and all eight cards/results are right. Mobile uses a compact sticky xG strip within the Playground, then the pitch and two-column cards; secondary coordinate controls are collapsible. This preserves live feedback within narrow screens without introducing an alternative model or separate mobile scene. The owner requested this single-page layout after running the initial draft locally.
