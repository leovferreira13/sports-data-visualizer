# Localization and routing

**Status:** implemented application shell in Issue #1; future scenario-state preservation remains to be proven by the playable pitch.

The App Router root layout lives at `app/[lang]/layout.tsx`, producing explicit `/en` and `/pt-BR` routes. `lib/i18n/config.ts` is the locale source of truth. `lib/i18n/dictionaries.ts` loads matching `locales/en.json` and `locales/pt-BR.json` resources on the server.

The bare root is the only path matched by `proxy.ts`. Locale resolution uses a valid `football-visualized-locale` cookie first, then standards-aware `Accept-Language` negotiation, then `en`. Unsupported route locales return the normal not-found response instead of silently rendering another language.

`components/language-switcher.tsx` is intentionally a Client Component because it needs the browser cookie and client navigation APIs. It changes only the locale path segment and retains the remaining pathname, query string, and hash. The cookie stores only `en` or `pt-BR`.

The current page has no scenario or mode state, so Issue #1 does not add a speculative state store. Issue #2 must keep scenario state language-independent and add a regression check showing that a locale switch does not lose the active simulation.

**Learning note:** App Router components are Server Components by default. The localization shell keeps routing, validation, metadata, and dictionary loading on the server, then creates a client boundary only around the interactive language selector. See [ADR 002](../adr/002-locale-routing-and-preference.md).
