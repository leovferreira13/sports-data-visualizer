# Public release preparation QA

Current public app: [sports-data.leoferreira.dev.br](https://sports-data.leoferreira.dev.br/en). This dated report and its JSON companion retain the Railway origin and deployment identity actually inspected at the time; use the [deployment guide](../architecture/reference/railway-deployment.md) for current configuration.

**Date:** 2026-10-12. **Issue:** #26. **Branch:** `agent/26-public-release`. **Base:** `6dd3c8570661dbeea40eca723b03f0336349dd2b`. **Outcome:** implementation prepared and checked; final release remains incomplete.

[Machine-readable evidence](public-release-qa.json) distinguishes the existing live deployment from the local changed worktree. It records source-file hashes, local build/browser identity, provider-confirmed remote source/deployment identity, history scope and staged settings. [Deployment and recovery instructions](../architecture/reference/railway-deployment.md) give the repeatable commands and release sequence.

## Implemented and verified

- Production startup binds explicitly to 0.0.0.0 and consumes PORT. A real process listened on 0.0.0.0:4322 and served /en when PORT=4322.
- POSIX prepare/hook setup preserves developer hooks and succeeds in a fresh Git-free package without private source/derived data or an offline training environment. Fresh npm ci completed in both environments; application checks do not become production runtime dependencies.
- Node 24 preference and CI match the locally tested major. CI uses the locked install and configured real-origin metadata checks. Railway runtime changes are staged, not claimed as deployed.
- Canonical pre-commit checks pass: lint/types, 90 JavaScript/TypeScript tests, 55 synthetic xG Python tests, three release-inspection Python tests, English Markdown and shell syntax. Focused regression checks reject malformed QA targets, recognize optimized logo markup and ensure a failed model response cannot report PASS.
- Production build with the actual SITE_URL and localized-route/metadata smoke checks pass. The exact model/contract/aggregate identity check runs before compilation.
- Chromium 153.0.8010.0 local production QA passes all five locales: six presets, reset, eight cards, mouse/keyboard/touch emulation, scene editing/add/remove limits, penalties, locale/query/anchor retention and reload. Desktop 1440×1000, mobile 390×844 and narrow Dutch/German 320×844 pass the existing layout checks. Delayed/failed/mutated model responses and blocked storage/cookies preserve explicit behavior. No page errors were observed.
- Current local production assets and model bytes pass the scoped asset audit. Logged local browser paths are pages, ordinary Next assets/images and the reviewed parameter model, without source-event/360/per-shot requests or an inference API.

No fitting, feature extraction contract, inference parameters, aggregate scientific evidence or generated model reports were changed.

## Language-navigation review follow-up

The PR review reported unclear feedback during public language changes and an apparently English tab title. Local production reproduction confirmed that Next.js already changed the title's description after successful navigation, while the product-name prefix stayed English in every dictionary. The follow-up localizes the full title to each locale's visible brand name and tests direct visits, client navigation and reload.

The selector now warms other locale routes on focus/pointer intent and uses React useTransition to track replacement. Pending navigation immediately displays the chosen target and a localized status overlay, disables repeat selection, and preserves the current scene underneath. Scroll/query/hash remain intact. The indicator respects reduced motion. No guarantee of zero real-network latency is made.

Browser regression held the German route response after an English-page edit: prefetch was observed, the selected target/disabled control/status were verified before completion, the mobile overlay had no overflow, and releasing the response restored the selector with the German title and unchanged scene. This supplements the all-five-locale product regression. These changes are validated in the local production build and are not yet deployed.

Icon provenance was confirmed from source and the #25 record: app/icon.svg is original SVG geometry authored for this project, separate from the official attribution logo. No third-party icon pack or downloaded football logo supplies the browser icon.

## Existing live deployment

The Railway demo at `https://sports-data-visualizer-production.up.railway.app/en` is accessible without application authentication. Railway confirms source main at the base commit, deployment `48884b1e-73cc-4ee4-a4d6-3f9f1a703f2e`, Railpack 0.40.1, Node 20.20.2 and port 8080. This is the prior #25 application, not a deployed #26 candidate.

HTTP smoke passes /br, /en, /nl, /es and /de, matching document languages, Methodology anchors/redirects, source/optimized-logo markup, root preference/fallback and invalid-locale behavior. The public model response is 96,241 bytes with SHA-256 `c0d91256a2c0f83ede48f1f549b8a0cc379e6ef675ccd4ce9ef10e471bb4350d`, identical to the reviewed envelope.

**Actual-domain metadata fails:** /en has no canonical to the public origin; inspected live HTML uses noindex/nofollow. SITE_URL was absent from the inspected service build. A new build with the prepared variable is required; restarting/redeploying the old image cannot fix prerendered metadata. The release checker exits nonzero and records FAIL for this gate.

A separate cloud browser displayed learned xG/eight live cards, verified English keyboard movement and observed the edited lateral coordinate preserved in Dutch and German. This is a limited public UI smoke check. The comprehensive remote harness did not complete: the shell browser could not validate its proxy certificate chain and cloud navigation/wait operations encountered tooling timeouts. TLS verification was retained. Five-locale comprehensive interaction/mobile/failure/network QA is recorded as **local**, not remote.

## Content, history and attribution

All 16 remote branch heads at inspection were either unchanged from the prior #8 inventory or present in the 10-commit extension to current main; there were no tags. Six additional unique trees contained 292 unique blobs inspected with bounded path, structured JSON and credential-signature scans. No forbidden data paths, source/private prediction records or matching credential signatures were found. Earlier reachable history relies on the dated #8 audit; this is not a formal model-privacy or exhaustive secret guarantee.

Four PNG blobs occur in that extension: the two unchanged official logos, the real illustrative Playground capture and the screenshot-based share image. Both portfolio images were visually inspected; the share image is 1200×630 and includes source/illustrative-scene wording. No private correspondence, source rows, historical reconstruction or license PDF was copied into the repository.

Official Open Data README/license blob identities still match the previously reviewed versions. The non-commercial scope and privately retained conditional support response remain applicable to this described use. The official Media Pack still resolves to the public Hudl logo collection; its accessible shell did not establish exact current per-asset guidance. **That check remains unresolved**, not PASS. Local five-locale rendered source/logo/independent-model checks and live HTTP markup checks passed within their stated scope.

## Prepared operations and remaining gates

Seven non-destructive changes are staged on the existing production service: SITE_URL, Node 24, locked install including build dependencies, explicit build/start commands and /en healthcheck with 60-second timeout. Patch `f7ea8f04-a948-4e82-854f-8342ccc1df01` was inspected; no deploy was triggered. No billing thresholds, resource limits, replicas, sleep mode, new services or volumes were changed.

The existing repository is still private. Public portfolio intent was requested on 2026-10-12; `dev 26` accepts implementation through the normal project workflow. It does not authorize automatic merge or imply that release gates passed.

Before marking #26 done:

1. Review/merge the code and resolve exact logo guidance.
2. Reinspect/apply only the prepared Railway changes; perform a **new build** of reviewed main and record its actual deployment/source identity and build logs.
3. Rerun actual-domain metadata/image, full remote interaction/network and source/logo checks. Complete #25 live metadata/share handoff; report unavailable physical-device or social-platform preview/cache coverage honestly.
4. Change repository visibility through GitHub administration only after required checks pass, then verify anonymous README/image access. No code license is selected here.
5. Refresh release evidence after the deployment and any new reachable history. Review actual workspace usage alerts/hard limits; document selected controls without inventing costs.

The prior deployment can be a functional rollback reference but has incomplete metadata. Correcting an origin requires rebuilding; reused images retain their original metadata. See the operational guide for recovery.
