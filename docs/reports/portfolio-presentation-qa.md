# Portfolio presentation QA

**Date:** 2026-10-12. **Issue:** #25. **Branch:** `agent/25-portfolio-presentation`. **Base:** `e9ab2cfed3d2a9b21fbfebc23b12993bc2e2908d`. **Scope:** local pre-release presentation and metadata; no deployment or visibility change.

## Delivered presentation

README now describes the implemented product rather than accumulating obsolete handoffs. It identifies Leonardo Ferreira, explains the product/software/data/ML decisions, links evaluation and reproduction, separates the web runtime from offline tooling, and offers a five-step reviewer walkthrough. GitHub identity matches the connected account; the exact LinkedIn URL was supplied and confirmed on 2026-10-12. URLs rendered in the app match these confirmed values. No automated LinkedIn authentication or independent profile-content audit was performed.

The app adds a compact author line with GitHub, LinkedIn and repository links after the introduction. Labels, title/description and preview alternative text cover all five locales. The original source/logo footer, prediction/features and scene state remain intact. An original SVG football icon and screenshot-based 1200 × 630 preview are included.

## Validation

- `npm ci`: successful fresh dependency install and repository hook setup.
- `npm run check:precommit`: PASS; lint, TypeScript, 77 TypeScript tests, 55 synthetic Python tests, English Markdown and shell checks.
- `npm run build`: PASS without SITE_URL; exact original model/evidence verification passed before compilation. `npm run check:localization`: PASS, including five-locale portfolio HTML, author links, icon/image, noindex metadata, disallowed robots and empty sitemap.
- `SITE_URL=https://portfolio.example.com npm run build` and matching `npm run check:localization`: PASS. This is a test fixture origin, not a live project domain. Rendered canonical/hreflang, localized title/description, OG/Twitter image/alt, index/follow, robots and sitemap matched all five explicit routes.
- A production build with `SITE_URL=http://invalid.example` failed explicitly with the origin-validation message as intended; the configured HTTPS build was then rebuilt and passed. Origin unit checks cover absent values, normalization and malformed/HTTP/local/credential/path/query/fragment/nonstandard-port inputs; invalid supplied origins throw explicitly. No test domain is hardcoded into production metadata.
- Existing `scripts/check-playground-browser.mjs`: PASS in Chromium 153.0.8010.0 across all five locales, covering presets, live eight-feature cards, mouse/keyboard/touch emulation, editing, reload/anchors, mobile sticky xG, model failure handling and evidence/attribution; zero page errors.
- Additional production-browser inspection: ten route/viewport combinations (1440 × 1050 and 390 × 844), confirmed author links, eight cards, no horizontal overflow, visible author placement and decoded footer logo. Keyboard-adjusted scene persisted through all five language choices and reload. Screenshots were inspected, including German/Dutch mobile expansion.
- README/share images were visually inspected. Internal relative links in README, roadmap and the new reference were checked against existing files. All 33 protected model/protocol/evidence and generated scientific files remain unchanged.

No private training/held-out computation was repeated. Browser touch checks are emulated, not physical-device tests. Translation completeness and layout were inspected; independent native-speaker review was not performed. External-site availability, public GitHub access, live crawler/social cache behavior and human qualitative feedback are not claimed.

## Capture provenance

`assets/portfolio/playground.png` captures the English production page at 1440 × 1050 after the reviewed model loads, with the original illustrative centralChance preset. It includes the actual intro, author and eight cards; no source row or historical match is shown. `public/portfolio/share.png` uses a crop of that same screenshot and deterministic text/layout at 1200 × 630. The share card includes source credit and illustrative-scene wording. The capture uses the environment's installed fonts; emoji flags may render as fallback glyphs there. The full product retains its existing native-language/flag selector.

## Editorial review and intentional exceptions

Tracked Markdown was searched for author-attributed reports/decisions, conversational owner phrases and outdated release gates. Current README, roadmap, vision, architecture, module references and review narratives now use impersonal language while preserving dates, rationale, hashes, measurements and responsibilities. Reported local computation remains distinct from independent aggregate/provenance inspection; no rewrite promotes a reported comparison to an independently repeated one.

- `docs/reports/*-first-run/` generated reports/model cards and all scientific JSON/contracts/protocols/model bytes remain immutable. Their original owner-related terms are intentionally retained; current references explain the evidence boundary.
- Dated ADRs and QA/review reports retain their original gate/role context with a clearly dated current-status note. Historical #5 publication wording in those dated records is superseded by #26, not silently rewritten as a historical authorization.
- Operational repository-owner roles remain in AGENTS, COMMANDS, DEVELOPMENT_PROCESS, the release decision contract and dated authorization records. These describe approval/merge responsibilities rather than conversational authorship or personal decision narration.
- No new code license is selected or implied by public visibility. Third-party source/logo rights remain separately documented.

## Plan deviation and remaining release work

Without SITE_URL, social image URL tags are omitted rather than emitted as relative URLs: Next.js requires absolute social metadata URLs and can otherwise resolve them against localhost. The image remains locally accessible; configured builds emit the reviewed public-origin URLs.

#26 must provide the real HTTPS origin, rebuild with SITE_URL, add the live README URL, make and verify public repository access, inspect actual-domain metadata/share preview and refresh release assets/network/history/source-logo QA. The outstanding exact per-asset branding-guidance check remains explicit. #25's final live URL/preview criteria remain open until that coordinated release validation; merging this pre-release PR must not close those criteria prematurely.

The README walkthrough is ready for a recruiter or technical peer. Record qualitative feedback when obtained; no fixed quota is a release gate. Revert the focused presentation commit before release if needed; post-deployment rollback belongs to #26.
