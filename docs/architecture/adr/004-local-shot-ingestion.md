# ADR 004 — Local shot ingestion and primary positional source

- Date: 2026-10-10
- Status: Accepted for ingestion; model feature/missingness policy remains pending
- Related: #3, #8, #9, #10

## Context

The pitch is implemented, but we need measured shot coverage before training our own model. StatsBomb event shots contain embedded freeze frames, while separate 360 coverage varies by match. Visible players do not necessarily represent every player on the pitch. The rights record requires keeping raw and shot-level data out of Git and deployed assets.

## Decision

Use a Python standard-library CLI outside the Next.js runtime to read a pinned official local Git checkout. Use embedded shot frames as the primary positional source and join separate 360 frames only for coverage/status comparisons. Do not silently repair one format with the other or require 360 for base-shot eligibility.

Preserve every eligible open-play foot shot locally, with explicit missing/invalid/empty frame and goalkeeper ambiguity diagnostics. Define a provisional position-usable audit cohort with one identifiable opponent goalkeeper; #10 will define model missingness and feature parity.

Write versioned shot-level and per-match files only under ignored data paths. Publish aggregate competition counts and methodology. Finalize deterministic run directories atomically after reconciliation and source-content revalidation; retain complete prior runs on failures.

## Consequences

Older competitions with embedded shot frames remain measurable even without 360. The audit cannot claim full defensive visibility or model quality. Ingestion introduces no server, database, Python web-runtime dependency or training library. Subsequent feature/training work consumes the local manifest and corpus and must preserve their population/provenance boundary. Public release still requires #8's final review.
