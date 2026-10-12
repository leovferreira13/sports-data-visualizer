# Architecture decision records

Use an ADR for a consequential, structural or difficult-to-reverse choice. An ADR records **Context**, **Decision** and **Consequences**, with ISO date and status. Keep it concise (around 60 lines or less), link relevant Issues, and update this index when a decision is added or superseded. Do not erase history.

| ADR | Status | Decision |
| --- | --- | --- |
| [001 — Client-side interactive application](001-client-side-playground.md) | Accepted | Next.js, SVG, browser inference subject to model validation |
| [002 — Locale-prefixed routing and persisted preference](002-locale-routing-and-preference.md) | Accepted | Explicit locale URLs, root negotiation, and a server-readable saved preference |
| [003 — Metric pitch and tab-scoped scene](003-metric-pitch-and-tab-scene.md) | Accepted | Uniform metric SVG projection and validated session scene across locale changes |
| [004 — Local shot ingestion](004-local-shot-ingestion.md) | Accepted for ingestion | Embedded shot frames as primary positioning source; deterministic local-only corpus and aggregate audit |
| [005 — Shared positional features](005-shared-positional-features.md) | Accepted for extraction | Versioned metric geometry, required keeper, independent Python/TypeScript parity and private immutable feature runs |

- [006: Offline training and frozen export](006-offline-training-and-frozen-export.md)
- [007: Browser inference and separate penalty convention](007-browser-inference-and-penalty.md)

- [008: Frozen final evaluation and publication gate](008-final-evaluation-and-publication-gate.md) — infrastructure implemented; empirical decision pending.

- [009: Integrated Playground and evidence](009-integrated-playground-and-evidence.md): reviewed browser artifact, scene/persistence bounds and methodology routes.

- [010: Separate xG behavior research](010-xg-behavior-research-boundary.md): research tooling and exploratory phase-A review complete; current model retained, detailed monotonic comparison deferred to #34.
