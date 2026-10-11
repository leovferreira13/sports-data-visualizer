# Positional feature extraction audit

**Issue:** #10. **Contract:** `positional-features/v1`.
**Status:** synthetic checks and full-corpus aggregate review passed on 2026-10-11; feature manifest/provenance and two-run byte comparison remain unconfirmed.

## Verified implementation evidence

The committed synthetic scenes exercise central/wide/long/near-goal shots, full-pitch positions, the closed cone and its tolerance, zero/ten/eleven defenders, goal-line/post failures and reflection. TypeScript tests execute Python on the same synthetic scene/failure/source inputs, including deterministic varied scenes. Independent analytic central angle/distance checks protect against shared mistakes. Browser preset and movement tests cover fixed/added defenders, goalkeeper position and intentional attacker omission.

Python materialization tests verify input/output hashes, manifest identity, exclusive exclusions, goal labels, deterministic rows and byte-identical reruns, incompatible schemas, duplicate identities, protected output locations, failed-run cleanup and immutable output conflicts. These tests use invented records only. They do not measure the real population's feature distribution.

A separate limited read-only smoke check on one official event file from the pinned source confirmed the +x goal convention for both teams and produced valid feature vectors for its 25 eligible open-play foot shots. No source examples or identifiers were committed. This checks real-format compatibility; it is not the complete feature population audit or an independent predictive evaluation.

The [completed data audit](xg-data-audit.md) supplies the starting evidence: 35,057 eligible base shots, 35,024 provisional position-usable shots and 3,261 usable goals. These are the **starting ingestion counts**. The owner has now executed full feature extraction; the reviewed aggregate retains 35,020 shots and 3,259 goals. The four additional exclusions are singular goal-line shots (two goals). No count-cap or malformed-input exclusions appear in this run.

## Reviewed full-corpus result

The owner supplied `feature-audit.json`; its SHA-256 is `fd2cf839e9248e1ff1697704ff7c303af40b0ac53f584d32f67ee39071855864`. The assistant independently checked all competition-to-total sums, shot/goal funnels, exclusive reasons, defender distributions, feature min/max pooling, sentinel value and UI-bound count relationships. The aggregate matches the previous ingestion base totals. Raw source records and private feature rows were not transferred or independently re-extracted.

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

## Remaining provenance and repeatability QA

The aggregate file does not contain the feature run ID, Python version, input/code hashes or a two-run comparison. Its own SHA-256 establishes the identity of the reviewed upload, not its link to a specific extractor/source run. Do not claim those checks passed until the owner confirms the byte comparison and the feature manifest is reviewed.

The full corpus remains local to the owner. To repeat the extraction, use the existing pinned ingestion run:

```bash
python3 scripts/xg/extract_features.py \
  --input-dir data/derived/xg-audit/b7d34951959b1b549ea93955c69fd7e60b91468e1ea14a43d3b146f606f2595e \
  --output-dir data/derived/xg-features

python3 scripts/xg/extract_features.py \
  --input-dir data/derived/xg-audit/b7d34951959b1b549ea93955c69fd7e60b91468e1ea14a43d3b146f606f2595e \
  --output-dir data/derived/xg-features-repeat
```

Replace the enclosing ingestion path if a different `--output-dir` was used in #9. Both calls print their completed immutable run directories. Compare `features.jsonl`, `feature-audit.json` and `manifest.json` byte-for-byte; identical run IDs alone do not replace that comparison. The aggregate has been reviewed. For the remaining provenance check, share the feature run `manifest.json` and confirm byte-identical `features.jsonl`, `feature-audit.json` and `manifest.json` across the two runs; keep real feature rows and identifiers private.

Accepted/rejected counts, ranges, distributions and planning minima have been reconciled above. Match-level split/holdout feasibility remains a #11 check.

Record actual feature run ID, Python version, contract/extractor/input/output hashes and two-run comparison here when verified. Do not insert unmeasured counts or infer predictive quality from geometric parity. #10's aggregate population check passes; final provenance/repeatability QA remains pending until that evidence is reviewed; public inference remains gated by #11–#13 and final rights QA in #8.
