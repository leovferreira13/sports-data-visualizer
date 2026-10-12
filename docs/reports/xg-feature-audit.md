# Positional feature extraction audit

**Issue:** #10. **Contract:** `positional-features/v1`.
**Status:** synthetic checks, full-corpus aggregate and feature manifest/provenance review passed on 2026-10-11. Equality of the compared files was confirmed locally; future complete-directory comparisons use the committed comparator.

## Verified implementation evidence

The committed synthetic scenes exercise central/wide/long/near-goal shots, full-pitch positions, the closed cone and its tolerance, zero/ten/eleven defenders, goal-line/post failures and reflection. TypeScript tests execute Python on the same synthetic scene/failure/source inputs, including deterministic varied scenes. Independent analytic central angle/distance checks protect against shared mistakes. Browser preset and movement tests cover fixed/added defenders, goalkeeper position and intentional attacker omission.

Python materialization tests verify input/output hashes, manifest identity, exclusive exclusions, goal labels, deterministic rows and byte-identical reruns, incompatible schemas, duplicate identities, protected output locations, failed-run cleanup and immutable output conflicts. These tests use invented records only. They do not measure the real population's feature distribution.

A separate limited read-only smoke check on one official event file from the pinned source confirmed the +x goal convention for both teams and produced valid feature vectors for its 25 eligible open-play foot shots. No source examples or identifiers were committed. This checks real-format compatibility; it is not the complete feature population audit or an independent predictive evaluation.

The [completed data audit](xg-data-audit.md) supplies the starting evidence: 35,057 eligible base shots, 35,024 provisional position-usable shots and 3,261 usable goals. These are the **starting ingestion counts**. Full feature extraction was executed locally; the reviewed aggregate retains 35,020 shots and 3,259 goals. The four additional exclusions are singular goal-line shots (two goals). No count-cap or malformed-input exclusions appear in this run.

## Reviewed full-corpus result

The submitted local `feature-audit.json` has SHA-256 `fd2cf839e9248e1ff1697704ff7c303af40b0ac53f584d32f67ee39071855864`. The assistant independently checked all competition-to-total sums, shot/goal funnels, exclusive reasons, defender distributions, feature min/max pooling, sentinel value and UI-bound count relationships. The aggregate matches the previous ingestion base totals. Raw source records and private feature rows were not transferred or independently re-extracted.

| Metric | Result |
| --- | ---: |
| Input shots / goals | 35,057 / 3,271 |
| Accepted shots / goals | 35,020 / 3,259 |
| Rejected shots / goals | 37 / 12 |
| Missing-keeper exclusions | 33 shots |
| Goal-line exclusions | 4 shots |
| Represented matches | 1,813 |
| Distinct competitions / competition-seasons | 8 / 10 |
| Accepted goal prevalence | 9.3061% |

All four reported planning minima pass (10,000 shots, 1,000 goals, 200 matches and three competitions). This permits the training experiments; it does not prove predictive performance or holdout quality.

| Competition/season | Accepted shots | Accepted goals | Rejected shots | Missing keeper | Goal line |
| --- | ---: | ---: | ---: | ---: | ---: |
| Premier League 2015/2016 | 7,778 | 695 | 12 | 12 | 0 |
| Ligue 1 2015/2016 | 6,633 | 658 | 6 | 6 | 0 |
| 1. Bundesliga 2015/2016 | 624 | 66 | 1 | 1 | 0 |
| La Liga 2015/2016 | 7,136 | 737 | 12 | 11 | 1 |
| Serie A 2015/2016 | 7,949 | 666 | 4 | 2 | 2 |
| FIFA World Cup 2018 | 1,231 | 96 | 1 | 1 | 0 |
| FIFA World Cup 2022 | 1,117 | 119 | 0 | 0 | 0 |
| UEFA Euro 2020 | 968 | 94 | 0 | 0 | 0 |
| UEFA Euro 2024 | 1,021 | 79 | 1 | 0 | 1 |
| Copa America 2024 | 563 | 49 | 0 | 0 | 0 |

### Geometry and empirical-support diagnostics

All reported feature ranges are finite and match the pooled competition ranges. Accepted shot distance spans 0.5518–78.5993 m, and goal opening angle spans 0.7350–169.5681 degrees. Those extrema are geometrically possible; predictive support must be assessed in #11/#13 rather than inferred from this audit.

The largest nearest-visible-defender distance, 125.0959631642844 m, is exactly the defined pitch-diagonal sentinel for the single accepted zero-defender frame (La Liga). It is not an observed defender position. The visible count distinguishes it. At least one accepted frame has a zero nearest distance, which is allowed for coincident recorded centers.

| Diagnostic | Count | Denominator | Rate |
| --- | ---: | ---: | ---: |
| Shooter outside current UI bounds | 186 | 35,020 accepted shots | 0.5311% |
| Shooter in defensive half | 58 | 35,020 accepted shots | 0.1656% |
| Represented scene with some opponent/shooter outside UI bounds | 8,753 | 35,020 accepted shots | 24.9943% |
| Zero-defender sentinel | 1 | 35,020 accepted shots | 0.0029% |

The scene diagnostic includes the shooter, keeper and observed opposing outfield players; it does not count teammates or unseen players. The 24.99% rate is not an invalid-data or unsupported-prediction rate. Offline positions were correctly retained on the full physical pitch, while current UI controls remain in the marker-safe attacking half. Keep this distinction explicit during training and controlled scene evaluation. Keeper-to-goal distances reach 61.5522 m; inspect sparse/extreme positional slices before defining empirical support, without silently deleting legitimate advanced-keeper cases or clipping positions.

## Provenance and reproducibility record

The submitted feature manifest was checked against the reviewed upload, the current extraction code and contract, and the pinned ingestion provenance. The run ID also matches the canonical hash of the manifest contents excluding `run_id`.

| Provenance item | Verified value |
| --- | --- |
| Feature run ID | `fe7c19c44a1101d61a39df586c957a1b85fef523a3c2a03c4c7faea603374517` |
| Python / extractor version | `3.12.3` / `1.0.0` |
| Feature contract SHA-256 | `7997e82634ffb78bac9d40b21c6715c8bb10cd8934e629a7a5fa09aed066bb67` |
| Feature CLI SHA-256 | `c05c78fa790474fb8e8e25d75652aff09d3e213da250f3d4554233a004e00bed` |
| Python feature module SHA-256 | `a51616d3b9377c81f3dd39d42709a509e5757bcd0936d31bfa685b6d8120195b` |
| Reviewed feature manifest SHA-256 | `c84bb97394ed8d1f88d0205e1c289c3d6fadb9b997e04981ce2a336234c112f3` |
| Private feature rows SHA-256 (manifest-declared) | `282f0c0fc781d3399015794fc2d8aa8e75928c68c255826e35d792899e22d976` |
| Source Git revision | `4b73468fc5b0f1950f9f66fada70ad3a4f9327cb` |
| Ingestion run ID | `b7d34951959b1b549ea93955c69fd7e60b91468e1ea14a43d3b146f606f2595e` |

Ingestion corpus/audit hashes match the prior reviewed record. The uploaded feature audit matches the manifest's declared output hash. Private feature rows and the two full run directories were not transferred, so their hash and byte comparison were not independently recomputed by the assistant. Equality of the compared files was confirmed locally. The comparator below provides an executable check of the complete file set, including the private feature rows, for subsequent comparisons; do not describe it as already executed on this full corpus.

The full corpus remains on the local training machine. To repeat the extraction, use the existing pinned ingestion run:

```bash
python3 scripts/xg/extract_features.py \
  --input-dir data/derived/xg-audit/b7d34951959b1b549ea93955c69fd7e60b91468e1ea14a43d3b146f606f2595e \
  --output-dir data/derived/xg-features

python3 scripts/xg/extract_features.py \
  --input-dir data/derived/xg-audit/b7d34951959b1b549ea93955c69fd7e60b91468e1ea14a43d3b146f606f2595e \
  --output-dir data/derived/xg-features-repeat
```

Replace the enclosing ingestion path if a different `--output-dir` was used in #9. After both runs, compare their complete immutable directories:

```bash
python3 scripts/xg/compare_runs.py \
  --left-dir data/derived/xg-features/fe7c19c44a1101d61a39df586c957a1b85fef523a3c2a03c4c7faea603374517 \
  --right-dir data/derived/xg-features-repeat/fe7c19c44a1101d61a39df586c957a1b85fef523a3c2a03c4c7faea603374517
```

Use the directories printed by the extractor when code/Python/input changes produce another run ID. The comparator verifies both manifest identities, exact declared file inventories and SHA-256 hashes, then compares `features.jsonl`, `feature-audit.json` and `manifest.json` byte for byte. It rejects comparing a directory with itself, missing/extra files, links, incomplete/corrupt manifests, differing metadata and changed outputs. `PASS` with exit status zero means every declared output and both manifests were verified and byte-identical. It never changes data. A failure returns exit status one and names the failed check without printing shot records.

Accepted/rejected counts, ranges, distributions, provenance and planning minima have been reconciled above. Match-level split/holdout feasibility remains a #11 check. Public inference remains gated by #11–#13 and final rights QA in #8.
