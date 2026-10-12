# xG behavior comparison — execution status

**Issue:** #31. **Reviewed:** 2026-10-12. **Disposition:** phase A reviewed as adaptive exploratory evidence; retain the current published model under the original protocol.

## Actual-corpus phase A and verification

The local comparison used the original development partitions and the frozen full
logistic/current XGBoost references, plus the bounded monotonic candidate. Selection
contains 3,643 shots and 324 goals. The previous final test remains acknowledged as
already opened; this research does not establish a fresh independent test.

The six submitted aggregate files passed schema, canonical identities, output
hashes, protocol/current-code agreement, decision consistency and exact report
regeneration. Complete local reproduction was reported PASS: 12 files verified,
zero files differing byte for byte, with matching research provenance, decisions,
topology and numeric tolerances. This local private-file verification was reported
by the operator; the submitted aggregate checks were independently performed.

See the unchanged [generated comparison](xg-behavior-first-run/comparison.md),
[aggregate evaluation](xg-behavior-first-run/behavior-evaluation.json) and
[dated review record](xg-behavior-review-record.json). The curated evidence folder
contains only the six submitted shareable files. Its original manifest also lists
private model/row/trace files; this folder is not a complete runnable research run.

| Model | Log loss | Brier | Isolated direction violations | >2pp primary jumps | Primary plateau share |
| --- | ---: | ---: | ---: | ---: | ---: |
| Current XGBoost | 0.23520840 | 0.06697392 | 40 | 44 / 986 | 80.1% |
| Monotonic XGBoost | 0.23524575 | 0.06694985 | 0 | 42 / 986 | 80.9% |
| Full logistic | 0.23835520 | 0.06761177 | 0 | 0 / 986 | 0.1% |

The current model has 34 distance and six angle violations on the isolated probes.
The monotonic candidate has zero, passes the declared probability-quality margins,
and improves primary p95 jump magnitude by about 21.9%. Its large-jump count falls
only 4.55%, below the original 25% interaction gate; its plateaus remain. Logistic
is much more continuous on ordinary paths but fails the quality uncertainty bounds,
with additional supported calibration/slice review flags. Count transitions can
still produce logistic jumps. These trajectory rates describe the declared probes,
not general app usage or calibrated probabilities for every scene.

## Decision and deliberately deferred follow-up

The original protocol and its `retain_current` result remain intact. Phase A is
complete for this investigation; no model or goalkeeper defaults are changed.
Phase B is not required to close this scoped outcome and is not being executed.
This run has no pre-fit unused-match reservation, so it cannot acquire a fresh-test
claim retrospectively by adding a new split of previously used matches.

Correcting isolated distance/angle directions is an important product priority.
A more detailed comparison of exactly the current XGBoost and the existing frozen
monotonic candidate is deliberately deferred to [#34](https://github.com/leovferreira13/sports-data-visualizer/issues/34).
The follow-up will compare identical local scenes and assess whether the direction
improvement justifies proposing a replacement despite the retained tree plateaus.
It does not include logistic or another training matrix expansion.

Any revised weighting of direction compliance versus the original jump gate must
be explicitly recorded as informed by phase A. Physical drags change several
features and are not guaranteed monotonic by isolated constraints. Independent
replacement evidence and publication disposition belong to the later decision;
no retrospective rule change or automatic deployment is implied.

See [local execution and shareable outputs](../architecture/reference/xg-behavior.md).

## Published-artifact diagnostic

The exact currently published envelope was evaluated without fitting or accessing
private training/test rows. The five invented preset anchors generated ten isolated
sweeps (15,255 adjacent pairs); physical paths, float32 tree boundaries and invalid
inputs brought Python/Chromium parity to 20,491 cases. Maximum probability error
was zero. Two complete Node diagnostic runs were byte-identical across all four
files.

There were 14 isolated distance-direction violations and no angle-direction
violations in these specific sweeps. The largest distance increase was
0.0186652839 probability (about 1.87 percentage points). This confirms a property
of the current model on these vectors, not the exact reported physical drag or an
empirical reason to replace it. The tests include physically inconsistent isolated
vectors; without private training rows, joint support is unassessed.

Plateaus and large physical/count-transition jumps are retained in the
[aggregate diagnostic](xg-behavior-published-diagnostic.json). No comparison of
actual candidate probability quality is implied by this diagnostic. The optional
Chromium run and separate Node reproduction are distinct checks.
