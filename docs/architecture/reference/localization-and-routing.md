# Localization and routing

**Status:** proposed; no application code yet.

Next.js App Router uses a route segment such as `app/[lang]/page.tsx` for `/pt-BR` and `/en`. Two small dictionaries hold matching keys. Presets store stable IDs rather than translated labels. The root route chooses a saved language preference, then the browser language, then `en`.

The top-level selector persists a manual choice without discarding scenario or mode. Set `<html lang>`, translated metadata and locale-aware number formatting. Prefer a simple cookie for a preference that the server can read before rendering; confirm behavior during Issue #1.

**Learning note:** App Router maps folders and files to URLs. A dynamic `[lang]` folder captures the language segment, while React state preserves the current interaction in the page. A redirect or navigation needs explicit handling to avoid resetting that state.
