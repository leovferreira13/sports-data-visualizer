# ADR 010 — Separate xG behavior research from published evidence

**Date:** 2026-10-12
**Status:** Implemented; phase A reviewed as exploratory, current model retained
**Issue:** [#31](https://github.com/leovferreira13/sports-data-visualizer/issues/31)

## Context

The published shallow XGBoost can plateau or reverse on movement. Moving a player
changes several inputs, so intuitive physical directions do not isolate a model
property. Probability quality and interaction behavior both matter for this
educational portfolio. The previous final test has already been opened.

## Decision

Preserve the original model, protocols and evidence. Use a separate research
protocol, historical-reference loader, output phase and comparator. Compare the
frozen full logistic/current XGBoost with a bounded monotonic XGBoost family on
original development partitions, explicitly as adaptive exploratory evidence.

Distance-negative and opening-angle-positive restrictions apply only with other
vector components fixed. Preserve positive calibration and exact browser parity.
Do not smooth frontend predictions or silently move the goalkeeper.

Freeze quality margins (0.005 log loss, 0.001 Brier, one-sided 95% paired-match
upper bounds) and behavioral gates before fitting. Require 25% fewer >0.02 jumps
without higher p95 on supported ordinary continuous paths; retain separate
outside-reference, extreme and count-transition diagnostics. Prefer logistic
when both alternatives qualify. Insufficient primary support is a failed gate.

A genuinely unused whole-match reservation, complete prior-use declaration and
pinned eligibility are required before fitting to claim fresh confirmation.
Reservation identity travels into research provenance. The once-opened evaluator
assesses the frozen choice without refitting. Local access guards do not prove
unknown external prior use or protect against deliberate file copying.

## Consequences

Research model identity is accepted by the shared parameter loader solely to
support exact parity. Production selection/distribution gates remain unchanged.
Original historical verification is not weakened to accept new protocol runs.

An exploratory result can retain the current model, recommend an alternative
pending independent review, or report insufficient evidence. No automatic public
replacement follows any score. Private rows, source anchors and traces remain
local; generated public review artifacts contain aggregate evidence only.

See [execution and review](../reference/xg-behavior.md).

## Phase-A disposition

The original protocol retains the current model. Complete reproduction was
reported locally and submitted aggregates were independently checked. Detailed
comparison of current versus monotonic XGBoost is deferred to #34, with isolated
direction compliance recorded as an important product priority. Phase B and
public replacement are not prerequisites for closing this scoped investigation.
