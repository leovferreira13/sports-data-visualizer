# ADR 003 — Metric pitch and tab-scoped scene

**Date:** 2026-09-26

**Status:** Accepted

**Supersedes:** None

## Context

Issue #2 needs drawn and numerical geometry to agree on desktop and mobile. The locale route changes when the visitor switches language, which can remount page-local React state. Future model features must use the same coordinates as the prototype.

## Decision

Store player positions once in meters on a 105 × 68 m field, with x increasing toward the attacked goal. Render the attacking half in a uniformly scaled `68 × 52.5` SVG viewBox rotated so the goal is at the top. Use the same goal-post coordinates for the cone and angle calculation, and invert the SVG screen matrix for pointer input. Keep presets and shot type language-independent.

Keep the current scene in client memory across locale route remounts and save a small, versioned, validated snapshot in tab-scoped `sessionStorage` for reloads. Server rendering omits provisional player positions until the client scene is available. The existing cookie continues to store language only. A missing or invalid snapshot loads the default preset.

## Consequences

Measurements, rendering, and later model features can use one physical convention, and resizing does not distort geometry. The goal moves from the scaffold's decorative right edge to the top; this is a deliberate change to preserve uniform scale in a wide half-pitch. Client memory prevents a default-scene flash during locale switches; tab storage preserves the scene on reload but does not share scenes across devices or supply a permanent link. Browser storage may be unavailable; interaction still works for the current page.
