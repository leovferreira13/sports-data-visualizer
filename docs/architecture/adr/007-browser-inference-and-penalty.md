# ADR 007: Browser-safe inference and a distinct penalty convention

**Date:** 2026-10-11. **Status:** accepted and implemented for #12 infrastructure; actual-candidate parity and release gates remain pending.

## Context

#11 freezes parameter-only logistic or shallow XGBoost envelopes. Browser predictions must retain fitted preprocessing/calibration and match offline semantics without an inference service. The actual candidate remains on the owner's machine. Public xG is gated by #13/#8 and presented by #4.

## Decision

Validate envelope schema, feature mapping/checksum, numerical fields and bounded topology once in `loadModel`. Capture immutable parameters behind a loader-created model handle. Keep the evaluator browser-safe and reuse the scene feature adapter. Expose discriminated learned, penalty-convention, unsupported and unavailable results. Failed inference has no probability and no heuristic fallback.

Implement double-precision logistic scaling/sigmoid and XGBoost float32 input, strict threshold traversal, sequential float32 margin accumulation and base probability. Apply exported calibration unchanged. Keep fixed parity tolerances: logistic 1e-10, XGBoost 1e-7.

Explicit penalty discriminators return the separate fixed 0.76 convention before scene/model checks. Geometry is irrelevant; no learned identity/claim is attached. Penalties remain outside training and held-out test population.

Verify the frozen envelope locally against manifest/selection/protocol identity using the Python reference. Bundle production TypeScript with pinned esbuild's browser target and execute in Node or optional local Chromium. Generate only aggregate immutable evidence, never real source rows or parameter files. Reuse complete-run byte comparison for repeated checks.

## Alternatives and consequences

A server API adds infrastructure without helping this bounded model. A heavy ML runtime or training-object snapshot increases the distribution surface and obscures numerical semantics. Runtime validation is semantic; cryptographic identity is verified by Python, avoiding incompatible Python/JavaScript JSON number serialization.

The shared bundle bridge replaces the planned Vitest subprocess bridge: the same bundle can execute in Node and a browser without a shipped debug route. Vitest still covers public contracts and numerical/error invariants. The schema interpreter supports only committed keywords; tests require support before schema extensions.

Parity proves numerical agreement, not fitness, empirical support, causality or rights. Synthetic checks cannot close real-candidate parity. Zero-defender and represented-scene warnings preserve that distinction. Distribution of real coefficients/trees in Git, static assets or client bundles remains subject to #8/#13 review.
