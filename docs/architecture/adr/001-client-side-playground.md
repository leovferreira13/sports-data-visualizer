# ADR 001 — Client-side interactive application

**Date:** 2026-09-26  
**Status:** Accepted  
**Supersedes:** None

## Context

The first release is a small bilingual educational xG playground. A user must move pieces and see immediate feedback on desktop and mobile. There is no need for accounts or persistent user data. The model is not selected yet, so inference feasibility remains a gate in Issue #3.

## Decision

Use Next.js App Router with React and TypeScript for the page, routes and state; an SVG pitch with Pointer Events for manipulation; and one metric coordinate system shared by visualization and feature extraction. Prefer browser-side inference with a small versioned model artifact when its license, inputs and runtime fit are validated. A Python build-time training/export script is allowed if a reusable model does not fit. Do not add a runtime backend preemptively.

## Consequences

Dragging can produce low-latency feedback without a network round-trip, and the first deployment remains simple. The model artifact and feature formulas must match training inputs, so a model unable to represent goalkeeper/defender positions cannot fulfill those UI claims. If an adequate model requires a different runtime or size, revisit the inference boundary in a new ADR before adding a server. See [prediction reference](../reference/prediction.md) and [roadmap](../../ROADMAP.md).
