# Localization and routing

**Status:** five-language application and scenario-state preservation implemented.

| Route | Semantic locale and dictionary |
| --- | --- |
| `/en` | `en`, `locales/en.json` |
| `/br` | `pt-BR`, `locales/pt-BR.json` |
| `/nl` | `nl`, `locales/nl.json` |
| `/es` | `es`, `locales/es.json` |
| `/de` | `de`, `locales/de.json` |

`lib/i18n/config.ts` owns the route mappings and native selector options.
`lib/i18n/dictionaries.ts` loads the selected dictionary on the server; its type
comes from English, while tests enforce identical recursive structure and nonempty
strings for every locale. Missing translations do not fall back at runtime.

`app/[locale]/layout.tsx` statically generates the five routes, document language,
title, description and localized attribution. Former methodology routes redirect
to the same locale's inline `#methodology` section. Unsupported routes (including
`/pt-BR`, `/de-DE` and `/fr`) return 404.

Only the bare root matches `proxy.ts`. `resolveLocale` prefers a valid
`football-visualized-locale` cookie, then standards-aware weighted Accept-Language,
then English. Regional Dutch, Spanish and German tags match their base language.
Invalid saved choices are ignored; missing/unsupported/malformed headers safely
fall back. HTTP wildcards are filtered before BCP 47 matching. An explicit locale
URL is never overridden by a cookie or browser preference.

`components/language-switcher.tsx` is a Client Component using the existing native
select and client navigation. It writes the semantic locale to a one-year,
site-wide SameSite=Lax cookie, replaces only the locale path segment and retains
the pathname suffix, query and hash. Flags accompany readable native names and
are never the only language identification. The selector's own label is localized.

The playable pitch maintains a language-independent Scenario, added/removed
players and selected preset in its existing scene store. Changes are serialized
to tab-scoped sessionStorage using the unchanged version 3 contract; legacy
versions 1 and 2 remain supported. Invalid/blocked storage falls back to the
default scene; module state still preserves edits through locale remounts within
the tab when storage is blocked. Selected-player UI focus is not persisted.
Server rendering waits for scene restoration before showing player positions.

Intl.NumberFormat formats measurements, xG, percentages and aggregate tables;
Intl.DateTimeFormat formats the scientific review date in UTC to avoid day shifts.
Calibration, review status and publication boolean have translated display labels;
machine IDs and scientific JSON remain unchanged. Stable feature/preset IDs and
numeric values never derive from translated labels. Standard technical names
(xG, XGBoost, TypeScript, Python, StatsBomb Open Data, Log loss and Brier) are
intentionally retained, alongside hashes and identifiers.

## Language navigation feedback (#26)

The selector warms other supported locale routes when focused or approached with a pointer, rather than fetching all translations on every initial visit. Prefetching adds background page requests only after interaction intent and can reduce a later navigation wait; it does not guarantee zero latency.

React useTransition tracks router replacement. The selected target appears immediately, the selector is disabled against duplicate changes, and a localized full-screen status overlay remains visible until the navigation settles. Existing page/scene state remains underneath; query, hash and scroll position are retained. A non-animated indicator respects prefers-reduced-motion. The status uses the language of the current page so its message is understandable before the destination has loaded.

Titles use each locale's visible product name plus its translated description. Next.js metadata remains the source of truth; no competing manual document.title assignment is added. Browser regression checks titles after language selection and reload, as well as direct route visits, and holds a destination response to verify pending feedback and scene retention.

## Verification and scope

`npm run check:precommit` includes dictionary, negotiation and localized failure
rendering tests. After `npm run build`, `npm run check:localization` checks all five
routes, legacy methodology redirects, preference precedence, document languages
and unsupported routes. `node scripts/check-playground-browser.mjs` performs
optional Chromium product QA with Playwright installed outside the app bundle;
`INFERENCE_CHROMIUM_EXECUTABLE` can select an existing Chromium binary and
`PRODUCT_QA_OUTPUT` can write a JSON result. See [QA](../../reports/localization-qa.md)
for observed results and language-review limitations.

This extends [ADR 002](../adr/002-locale-routing-and-preference.md). New author/share
copy follows this locale contract in #25; #26 verifies actual Railway URLs. Learn
is deferred in #5. No public deployment is implied by localized local QA.
