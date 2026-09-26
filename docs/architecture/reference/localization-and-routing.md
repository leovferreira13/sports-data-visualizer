# Localization and routing

**Status:** implemented application shell in Issue #1; future scenario-state preservation remains to be proven by the playable pitch.

The App Router root layout lives at `app/[locale]/layout.tsx`, producing explicit `/en` and `/br` routes. The URL segment `br` maps to the standards-based internal locale `pt-BR`, so document language, dictionaries, and browser-language matching continue to use `pt-BR` while the public route stays concise. `lib/i18n/config.ts` owns this mapping.

`lib/i18n/dictionaries.ts` loads matching `locales/en.json` and `locales/pt-BR.json` resources on the server. The bare root is the only path matched by `proxy.ts`. Locale resolution uses a valid `football-visualized-locale` cookie first, then standards-aware `Accept-Language` negotiation, then `en`. Unsupported route locales, including `/pt-BR`, return the normal not-found response.

`components/language-switcher.tsx` is intentionally a Client Component because it needs the browser cookie and client navigation APIs. It shows a country flag next to each language, changes only the locale path segment, and retains the remaining pathname, query string, and hash. The cookie stores only the semantic locale `en` or `pt-BR`.

The current page has no scenario or mode state, so Issue #1 does not add a speculative state store. Issue #2 must keep scenario state language-independent and add a regression check showing that a locale switch does not lose the active simulation.

**Learning note:** URL route identifiers and localization identifiers serve different concerns. Keeping `br` as the route but `pt-BR` as the locale lets product URLs stay simple without losing the correct HTML `lang`, dictionary, or browser-language semantics. See [ADR 002](../adr/002-locale-routing-and-preference.md).
