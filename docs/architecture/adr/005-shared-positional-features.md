# ADR 005 — Shared positional features

**Date:** 2026-10-11
**Status:** Accepted for feature extraction; predictive support remains pending
**Issue:** #10, under #3

## Context

The ingestion audit has 35,024 provisional position-usable open-play foot shots.
The browser uses a metric pitch and addable defenders. Python training and
browser inference must not interpret the same positions differently. Embedded
shot frames contain observed relevant players; optional separate 360 has much
lower coverage and is not a substitute.

## Decision

Use `model/feature-contract.json` to version eight ordered positional features,
units, domain and missingness. Independently implement pure extraction in Python
and TypeScript; mandatory tests run both on the same synthetic scenes. Reuse
existing TypeScript distance/angle geometry. Keep observed-visibility metadata
outside the vector.

Scale source positions from 120 × 80 to 105 × 68 m and use the application's
physical 7.32 m goal. Do not scale source post annotations into a competing goal
definition. Use a closed finite shooting triangle with dimensionless barycentric
tolerance. Historical positions remain on the full physical pitch; UI marker
bounds must not clamp them.

Require one known opponent keeper and a valid embedded frame. Reject missing
positions instead of inventing absence or substituting 360. A known empty
defender list uses the pitch-diagonal nearest-distance sentinel plus zero count.
Count all represented outfield defenders, including browser additions; ignore
teammates/extra attackers and omit keeper alignment in v1.

Materialize feature rows and manifests locally with input/code hashes, stable
ordering and atomic immutable run directories. Commit synthetic tests and
aggregate evidence only. No fitted preprocessing or prediction is introduced.

## Consequences

The physical-post convention is a deliberate canonical-pitch approximation.
Duplicated math is guarded by executable parity checks and contract validation.
Required-keeper filtering excludes the 33 audited zero-keeper base shots and may
have further geometric exclusions, which the feature audit must measure.
Geometric validity does not establish empirical support or causal movement
effects. Training, calibration, model choice and publication remain #11–#13.
