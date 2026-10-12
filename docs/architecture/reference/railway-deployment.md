# Railway deployment and recovery

**Status (2026-10-12):** the existing service serves the five-language app. #26 prepares repeatable production settings and release checks; final release is still pending. See [release QA](../../reports/public-release-qa.md).

## Existing service

Reuse project **adaptable-heart**, service **sports-data-visualizer**, environment **production** and the existing [HTTPS origin](https://sports-data-visualizer-production.up.railway.app/en). The connected source is `leovferreira13/sports-data-visualizer`, branch `main`, repository root. No new service, database, volume, inference backend or dataset upload is required.

The inspected deployment `48884b1e-73cc-4ee4-a4d6-3f9f1a703f2e` runs commit `6dd3c8570661dbeea40eca723b03f0336349dd2b`, using Railpack 0.40.1, Node 20.20.2, one replica in `europe-west4-drams3a` and the assigned port 8080. Those are dated observations, not fixed values to copy into a new service. The domain targets 8080; keep the platform's assigned PORT aligned with its target port.

## Production contract

| Setting | Prepared value |
| --- | --- |
| Builder/source/root | Existing Railpack service, main branch, repository root |
| RAILPACK_NODE_VERSION | `24`; local preference and application CI use `.node-version` |
| RAILPACK_INSTALL_CMD | `npm ci --include=dev`; builds need the locked development dependencies |
| Build command | `npm run build` |
| Start command | `npm start` |
| Healthcheck | `/en`, timeout 60 seconds |
| SITE_URL | `https://sports-data-visualizer-production.up.railway.app`, available **before build** |
| PORT | Railway-managed; no application-specific hardcoded port |

These three variables and four command/health settings are **staged**, not applied. Patch `f7ea8f04-a948-4e82-854f-8342ccc1df01` contains seven reviewed changes to this service and no destructive action. Reinspect the pending patch before applying it because another action may add changes.

`npm start` explicitly binds Next.js to `0.0.0.0`; the installed CLI reads PORT from the environment. `npm run build` verifies original model/contract/evidence identities and copies the exact parameter bytes before compiling. Preserve that check. Do not install the offline Python training environment in the production image. Public parameters and reviewed aggregate reports are already tracked; the source/shot corpus stays local.

`npm ci` runs `prepare` through a POSIX shell. Hook setup exits successfully when Git or checkout metadata is absent and installs the hook in a developer checkout. Do not disable installation scripts globally to avoid hook setup.

SITE_URL is public configuration. It must be the HTTPS origin without credentials, paths, query or fragments. Next.js prerenders canonical/social/robots/sitemap metadata: changing a variable on a running container or restarting an old image does not update that output. **Perform a new build** after changing SITE_URL. Missing configuration deliberately produces noindex and an empty sitemap.

Settings are documented and staged through the existing service rather than adding a legacy railway.json/railway.toml file. The official configuration reference currently marks that format deprecated. No new hosting abstraction or Docker migration is needed for this release.

## Verify and publish

1. Review/merge the #26 PR through the normal project process. No automatic merge is part of this implementation.
2. Resolve the exact logo-guidance gate and inspect current history/content. Preserve the non-commercial scope and reviewed parameters.
3. Review the existing production patch and apply only the documented changes. Confirm a **build** of the reviewed main commit starts; an old-image redeploy is insufficient for SITE_URL. Check build logs for Node 24, the locked install, the model check and the production build.
4. Confirm SUCCESS and the /en healthcheck, then record the actual commit and deployment ID from Railway. A successful healthcheck proves page availability, not browser model execution.
5. Run the checks below from the matching checkout; inspect all five live pages, image preview and attribution. Refresh the release record with the actual deployment identity and observed results.
6. After all required release checks pass, change GitHub repository visibility under **Settings → General → Danger Zone → Change repository visibility → Public**, using administration access. Verify the repository, README and images in an unauthenticated browser. Public visibility does not select a code license.

The existing automatic source connection follows main. Recheck whether staged settings were applied when merging: do not assume a code push commits a separate pending environment patch.

```bash
npm ci --include=dev
npm run check:precommit
SITE_URL=https://sports-data-visualizer-production.up.railway.app npm run build
SITE_URL=https://sports-data-visualizer-production.up.railway.app npm run check:localization

SITE_URL=https://sports-data-visualizer-production.up.railway.app npm run check:release -- \
  --base-url https://sports-data-visualizer-production.up.railway.app \
  --output /tmp/public-release-http.json
```

Browser regression uses separately installed Playwright/Chromium, outside the app dependency lock. Follow the setup in [integrated QA](playground-and-methodology.md).

```bash
# Local production server is started and stopped by this command.
npm run check:browser

# Remote mode never starts or kills a local server.
PRODUCT_QA_BASE_URL=https://sports-data-visualizer-production.up.railway.app \
PRODUCT_QA_OUTPUT=/tmp/public-release-browser.json npm run check:browser
```

An existing browser executable can be selected with INFERENCE_CHROMIUM_EXECUTABLE. PRODUCT_QA_PROXY optionally selects a transport proxy; do not publish its credentials. Keep TLS verification enabled and use a browser environment that trusts its required certificate chain. Report physical-device QA separately from emulated touch/mobile tests.

HTTP QA checks routes, preferences, anchor redirects, source/logo markup, the exact model response and domain metadata/image/robots/sitemap. It exits nonzero on failure, records no application credentials and never authorizes publication. A matching model hash alone cannot identify the running app commit. Browser reports identify the checked origin, checkout and local build separately; confirm remote source identity from Railway.

## Recovery and resource controls

Capture the previous reviewed healthy deployment ID and service settings before release. Railway currently reports that `48884b1e-73cc-4ee4-a4d6-3f9f1a703f2e` can be rolled back/redeployed; it has known incomplete metadata and is a functional recovery reference, not an accepted final release.

For a broken candidate, restore a known healthy deployment through its deployment menu and rerun locale/model checks. Reusing an image preserves that image's build-time metadata. To repair a wrong origin, correct SITE_URL and **rebuild** the reviewed commit. Reverting source requires a reviewed commit/PR. Leave private data and original scientific evidence unchanged. If content or rights review fails, halt wider publication and correct the finding; making a repository private later cannot retract a disclosure.

Keep the current single replica until observed traffic justifies more. The inspected one-hour window showed approximately 0.101 GB current memory and 0.146 GB maximum, with low CPU usage; this is an early operational observation, not a capacity or monthly-cost estimate. Inspect Metrics after deployment and choose limits with headroom for measured peaks. Replica resource limits cap resource allocation; they do not make idle usage free.

Under workspace Usage, review compute usage alerts and hard limits separately from any agent usage limits. Alerts notify; a compute hard limit may stop workloads and affect availability. No billing plan, spending threshold, sleep mode, replicas or resource limits were changed by this task. Actual account thresholds still need review. Sleeping can reduce idle usage with a cold-start tradeoff and is optional for this small portfolio.

## Official references

- [Railway build configuration](https://docs.railway.com/builds/build-configuration): custom install/build commands.
- [Railpack Node](https://railpack.com/languages/node): runtime selection and package installation.
- [Railway configuration reference](https://docs.railway.com/config-as-code/reference): dated legacy configuration status.
- [Cost controls](https://docs.railway.com/pricing/cost-control) and [deployment healthchecks](https://docs.railway.com/deployments/healthchecks).
- Installed Next.js 16.3.6 guides: `node_modules/next/dist/docs/01-app/01-getting-started/17-deploying.md` and `03-api-reference/06-cli/next.md`.
