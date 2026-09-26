# ADR 002 — Locale-prefixed routing and persisted preference

**Date:** 2026-09-26  
**Status:** Accepted  
**Supersedes:** None

## Context

The first release must support Brazilian Portuguese and English from entry. Direct locale URLs need to be predictable, while a visitor opening the bare root should see a language selected from an explicit prior choice or the browser preference. Future Playground state must not be encoded in translated labels.

## Decision

Use explicit `/en` and `/pt-BR` App Router routes under `app/[lang]`. The bare `/` is the only route handled by `proxy.ts`; it resolves a valid locale cookie first, then `Accept-Language`, then falls back to `en`. A manual selector writes the same non-sensitive, site-wide cookie and replaces only the locale path segment while retaining the remaining URL.

Translations live in matching locale dictionaries and are loaded by Server Components. Stable application state must remain language-independent. No general i18n framework is required while these two small dictionaries cover the product needs.

## Consequences

Locale is visible and shareable in the URL, server rendering can set the correct document language before hydration, and the saved choice is available before rendering the root redirect. Locale-only navigation may remount route content, so future scenario state introduced by Issue #2 must be stored or bridged independently of translated route content and tested across a language switch.
