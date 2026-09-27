# Localization and routing

**Status:** application shell and scenario-state preservation implemented.

The App Router root layout lives at `app/[locale]/layout.tsx`, producing explicit `/en` and `/br` routes. The URL segment `br` maps to the standards-based internal locale `pt-BR`, so document language, dictionaries, and browser-language matching continue to use `pt-BR` while the public route stays concise. `lib/i18n/config.ts` owns this mapping.

`lib/i18n/dictionaries.ts` loads matching `locales/en.json` and `locales/pt-BR.json` resources on the server. The bare root is the only path matched by `proxy.ts`. Locale resolution uses a valid `football-visualized-locale` cookie first, then standards-aware `Accept-Language` negotiation, then `en`. Unsupported route locales, including `/pt-BR`, return the normal not-found response.

`components/language-switcher.tsx` is intentionally a Client Component because it needs the browser cookie and client navigation APIs. It shows a country flag next to each language, changes only the locale path segment, and retains the remaining pathname, query string, and hash. The cookie stores only the semantic locale `en` or `pt-BR`.

The playable pitch holds a language-independent `Scenario`, added players, and selected preset in a Client Component. It keeps a client-side scene snapshot across locale remounts and stores each change in tab-scoped `sessionStorage` for reloads. `lib/scenario-session.ts` validates snapshots and upgrades version 1 scenes with empty added-player lists; malformed or unavailable storage falls back to the default central scene. Server rendering shows no provisional player positions before the client reads its scene, so locale navigation does not flash the default preset. The language cookie and tab snapshot have distinct purposes. The optional Learn mode does not exist yet.

**Learning note:** URL route identifiers and localization identifiers serve different concerns. Keeping `br` as the route but `pt-BR` as the locale lets product URLs stay simple without losing the correct HTML `lang`, dictionary, or browser-language semantics. See [ADR 002](../adr/002-locale-routing-and-preference.md).
