# Five-language localization QA (#24)

**Date:** 2026-10-12

**Scope:** local production application; no public deployment or native-speaker review.

## Implemented outcome

The existing English and Brazilian Portuguese interface now also supports Dutch,
Spanish and German at `/nl`, `/es` and `/de`. All five dictionaries cover brand
and metadata, controls, player labels/glyphs, presets, the eight feature cards,
prediction states, methodology/results, accessibility and attribution. Native
language names and flag characters come from one typed selector registry.

The locale cookie, scene store and version 3 snapshot contract are unchanged.
Regional browser preferences match base languages; malformed language tags and
HTTP wildcards no longer cause matching errors. Display formatting uses Intl;
evidence status/calibration labels and dates are translated only at rendering.
Model parameters, feature definitions, private-data boundaries and aggregate
scientific evidence remain unchanged.

## Observed checks

| Check | Result |
| --- | --- |
| `npm run check:precommit` | PASS: lint, TypeScript, 74 application tests, 55 Python tests, Markdown language and shell syntax |
| `npm run build` | PASS: exact model/evidence checks and all five localized static routes |
| `npm run check:localization` | PASS: five direct routes and legacy methodology redirects, document languages, explicit-route precedence, saved preferences, regional/weighted headers, fallback and 404 routes |
| `node scripts/check-playground-browser.mjs` | PASS: Chromium 153.0.8010.0 on the local production build; zero observed page errors |
| `python3 scripts/audit-product-assets.py` | PASS: 176 tracked files and 121 generated build assets; no forbidden data paths or source-record signatures; exact served model bytes |
| Visual inspection | English desktop, all five mobile captures, and German methodology reviewed; long labels wrap and tables remain locally scrollable |

Browser automation covers all six preset probabilities against the original
aggregate diagnostics, locale-formatted percentages and measurements, eight cards,
mouse/keyboard/touch edits, zero-to-three defenders, extra attackers, the fixed
penalty convention, reloads, methodology anchors, footer logo/credit and localized
document title/description. It checks 1440px desktop and 390px mobile for all five
locales and 320px for Dutch/German, including page/card overflow predicates.

An edited scene is retained while cycling through all five locale routes, including
query/hash preservation, cookies and subsequent root navigation. Separate fresh
contexts check translated model loading and both network/hash failure messages
in every locale. Component rendering checks unavailable/unsupported/loading states
without a substitute xG value in all five languages. Browser checks also cover
manual navigation with blocked cookie writes and locale switching with blocked
sessionStorage.

The browser output is stored in [the QA record](localization-browser-qa.json).
The original model SHA-256 is
`c0d91256a2c0f83ede48f1f549b8a0cc379e6ef675ccd4ce9ef10e471bb4350d`;
the original aggregate-evidence SHA-256 is
`4940016cda64e1d639f11cd592b9fb32e1b481aedd79350d5ddbdf574c068c96`.

## Translation and environment limitations

Translations were authored and reviewed for football/statistical meaning during
implementation; they have not been reviewed by native speakers. Completeness tests
verify structure, value types and nonempty text, not linguistic correctness.
Standard technical names (xG, XGBoost, Log loss, Brier, TypeScript, Python and
StatsBomb Open Data), units and evidence identifiers intentionally remain shared.
Scientific qualifiers, sparse-sample warnings, the adverse cone-count result and
the distinction between reported local reproduction and independently reviewed
aggregates are preserved. Four illustrative open-play presets remain outside the
descriptive reference; no translation claims a newly validated population.

The normal Playwright browser download returned an invalid archive in this
environment. QA used a separately installed Chromium headless binary from the
`@sparticuz/chromium` npm package, outside application dependencies. Its font set
renders flag emoji as missing glyphs in screenshots; the actual flag code points
and native names are present in each option. Flag appearance remains dependent on
the operating system's emoji support, as in the previous selector. This was not a
physical mobile-device, Safari/Firefox or assistive-technology session.

The mobile language selector was widened to retain the full Brazilian Portuguese
name; the brand can shrink and wrap alongside it. The existing two-dictionary test was replaced by a
stronger five-dictionary check; a small Vitest config supplies the same `@` alias
and automatic JSX transform needed to test actual prediction-component rendering.

Portfolio presentation and the broad professional editorial review remain #25.
Railway URL/domain metadata and live-device checks remain #26. Learn (#5) is
deferred. This record does not authorize or claim public release.
