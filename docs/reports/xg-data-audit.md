# StatsBomb data feasibility audit

**Completed:** 2026-10-11. Issue #9: local shot ingestion and population feasibility. No model has been trained or evaluated by this audit.

## Result and population

The complete requested cohort passes every agreed planning minimum: 35,024 position-usable shots, 3,261 goals, 1,813 represented matches and eight distinct competitions across ten competition/seasons. This permits the planned feature and training experiments; it does not establish predictive quality, calibration or suitability for every scene in the playground.

Every selected event file and all 166 corresponding tracked 360 files were available in the owner's completed local runs. The earlier connector download limitation has been resolved by local execution. The absence of a 360 file in the pinned source remains an official availability observation, not an omitted local input.

Embedded shot freeze frames remain the primary positional source. Of 35,057 eligible base shots, all have valid nonempty embedded frames; 35,024 have exactly one identifiable opponent goalkeeper. The other 33 shots (10 goals) remain in the local base corpus and are excluded only from the provisional position-usable cohort.

## Competition inventory and funnel

The table includes zero-shot fixtures in the inventory. All stages below represent all 1,813 matches. Availability is limited to what the pinned release contains: Bundesliga has 34 fixtures and Ligue 1 has 377; do not describe these as complete league seasons.

| Competition/season | Fixtures | All shots | Open play | Foot/base shots | Base goals | Position-usable shots | Usable goals | Matches with 360 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1. Bundesliga 2015/2016 | 34 | 840 | 776 | 625 | 66 | 624 | 66 | 0 |
| Copa America 2024 | 32 | 790 | 709 | 563 | 49 | 563 | 49 | 0 |
| UEFA Euro 2020 | 51 | 1289 | 1193 | 968 | 94 | 968 | 94 | 51 |
| UEFA Euro 2024 | 51 | 1340 | 1257 | 1022 | 79 | 1022 | 79 | 51 |
| La Liga 2015/2016 | 380 | 9168 | 8661 | 7148 | 741 | 7137 | 738 | 0 |
| Ligue 1 2015/2016 | 377 | 8814 | 8260 | 6639 | 660 | 6633 | 658 | 0 |
| Premier League 2015/2016 | 380 | 9908 | 9415 | 7790 | 699 | 7778 | 695 | 0 |
| Serie A 2015/2016 | 380 | 9998 | 9396 | 7953 | 668 | 7951 | 667 | 0 |
| FIFA World Cup 2018 | 64 | 1706 | 1556 | 1232 | 96 | 1231 | 96 | 0 |
| FIFA World Cup 2022 | 64 | 1494 | 1382 | 1117 | 119 | 1117 | 119 | 64 |
| **Total** | 1813 | 45347 | 42605 | 35057 | 3271 | 35024 | 3261 | 166 |

Across 6,380,073 events, all shots contain recognized outcomes: 45,347 shots and 4,713 goals. Open-play selection retains 42,605 shots and 4,093 goals; foot selection retains 35,057 shots and 3,271 goals. The location/outcome gates make no further exclusions in this release. Goal is the sole positive label. StatsBomb xG is neither a feature nor the target.

### Exclusive exclusions

The funnel rejects type before body part, then location and outcome. Reasons are disjoint and sum to 10,290 shots: 2,742 not open play and 7,548 not foot. Missing type/body part/outcome, invalid location and unknown outcome each exclude zero shots. Unknown and missing outcomes across all shots are also zero.

| Competition/season | Not open play | Not foot | Other exclusions | Base shots without an identifiable keeper |
| --- | ---: | ---: | ---: | ---: |
| 1. Bundesliga 2015/2016 | 64 | 151 | 0 | 1 |
| Copa America 2024 | 81 | 146 | 0 | 0 |
| UEFA Euro 2020 | 96 | 225 | 0 | 0 |
| UEFA Euro 2024 | 83 | 235 | 0 | 0 |
| La Liga 2015/2016 | 507 | 1513 | 0 | 11 |
| Ligue 1 2015/2016 | 554 | 1621 | 0 | 6 |
| Premier League 2015/2016 | 493 | 1625 | 0 | 12 |
| Serie A 2015/2016 | 602 | 1443 | 0 | 2 |
| FIFA World Cup 2018 | 150 | 324 | 0 | 1 |
| FIFA World Cup 2022 | 112 | 265 | 0 | 0 |

### Observed outcomes across all shots

Outcome counts use all shots before eligibility filtering; base and usable positive labels are separately reported above.

| Competition/season | Blocked | Goal | Off T | Post | Saved | Saved Off Target | Saved to Post | Wayward |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1. Bundesliga 2015/2016 | 189 | 90 | 235 | 26 | 218 | 1 | 9 | 72 |
| Copa America 2024 | 204 | 95 | 243 | 17 | 179 | 0 | 4 | 48 |
| UEFA Euro 2020 | 337 | 155 | 416 | 31 | 283 | 6 | 5 | 56 |
| UEFA Euro 2024 | 386 | 126 | 397 | 25 | 316 | 4 | 5 | 81 |
| La Liga 2015/2016 | 2081 | 1014 | 2981 | 209 | 2216 | 35 | 33 | 599 |
| Ligue 1 2015/2016 | 1984 | 916 | 2984 | 160 | 2157 | 30 | 30 | 553 |
| Premier League 2015/2016 | 2880 | 988 | 3197 | 170 | 2209 | 45 | 23 | 396 |
| Serie A 2015/2016 | 2527 | 951 | 3475 | 171 | 2201 | 35 | 32 | 606 |
| FIFA World Cup 2018 | 457 | 183 | 572 | 24 | 341 | 0 | 0 | 129 |
| FIFA World Cup 2022 | 379 | 195 | 448 | 36 | 346 | 2 | 3 | 85 |

## Visibility and missingness

All 35,057 base shots have valid embedded frames: missing, empty and invalid frames each total zero; invalid player entries, invalid player locations and unknown player roles each total zero. Keeper cases are one: 35,024; zero: 33; multiple: zero; not assessable: zero. No keeper is inferred from an unknown role.

The distribution below counts visible opposing outfield players in valid embedded frames. A zero does not establish that there were no defenders on the pitch. The keeper is excluded from defender counts. Frames expose partial visibility; no unseen positions are reconstructed.

| Competition/season | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | Denominator |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1. Bundesliga 2015/2016 | 0 | 2 | 10 | 19 | 28 | 47 | 106 | 126 | 116 | 86 | 85 | 625 |
| Copa America 2024 | 0 | 2 | 3 | 14 | 19 | 31 | 61 | 87 | 134 | 118 | 94 | 563 |
| UEFA Euro 2020 | 0 | 0 | 5 | 18 | 29 | 60 | 101 | 156 | 248 | 202 | 149 | 968 |
| UEFA Euro 2024 | 0 | 0 | 4 | 9 | 32 | 45 | 89 | 139 | 214 | 267 | 223 | 1022 |
| La Liga 2015/2016 | 1 | 8 | 69 | 203 | 340 | 594 | 1055 | 1467 | 1542 | 1125 | 744 | 7148 |
| Ligue 1 2015/2016 | 0 | 8 | 45 | 170 | 348 | 612 | 956 | 1370 | 1418 | 1165 | 547 | 6639 |
| Premier League 2015/2016 | 0 | 8 | 64 | 173 | 298 | 554 | 1128 | 1619 | 1836 | 1523 | 587 | 7790 |
| Serie A 2015/2016 | 0 | 8 | 90 | 241 | 435 | 679 | 1162 | 1637 | 1781 | 1120 | 800 | 7953 |
| FIFA World Cup 2018 | 0 | 2 | 6 | 27 | 32 | 102 | 136 | 257 | 270 | 254 | 146 | 1232 |
| FIFA World Cup 2022 | 0 | 1 | 5 | 13 | 36 | 66 | 110 | 182 | 248 | 266 | 190 | 1117 |
| **Total** | 1 | 39 | 301 | 887 | 1597 | 2790 | 4904 | 7040 | 7807 | 6126 | 3565 | 35057 |

### Rates with explicit denominators

Rates are pooled across the selected population; competition counts above provide the stratification. Frame state, keeper case and 360 state rates use all eligible base shots as their denominator, including unmatched 360 shots. Null is used for a zero denominator in the machine audit.

| Metric | Numerator | Denominator | Rate |
| --- | ---: | ---: | ---: |
| all_shot_360_join_coverage | 3960 | 45347 | 8.7327% |
| all_shot_360_valid_coverage | 3822 | 45347 | 8.4283% |
| base_360_frame_empty_rate | 0 | 35057 | 0.0000% |
| base_360_frame_invalid_rate | 78 | 35057 | 0.2225% |
| base_360_frame_missing_rate | 32040 | 35057 | 91.3940% |
| base_360_frame_valid_rate | 2939 | 35057 | 8.3835% |
| base_360_join_coverage | 3017 | 35057 | 8.6060% |
| base_360_valid_coverage | 2939 | 35057 | 8.3835% |
| base_goal_prevalence | 3271 | 35057 | 9.3305% |
| embedded_frame_empty_rate | 0 | 35057 | 0.0000% |
| embedded_frame_invalid_rate | 0 | 35057 | 0.0000% |
| embedded_frame_missing_rate | 0 | 35057 | 0.0000% |
| embedded_frame_valid_rate | 35057 | 35057 | 100.0000% |
| embedded_keeper_multiple_rate | 0 | 35057 | 0.0000% |
| embedded_keeper_not_assessable_rate | 0 | 35057 | 0.0000% |
| embedded_keeper_one_rate | 35024 | 35057 | 99.9059% |
| embedded_keeper_zero_rate | 33 | 35057 | 0.0941% |
| embedded_position_usable_coverage | 35024 | 35057 | 99.9059% |
| embedded_valid_coverage | 35057 | 35057 | 100.0000% |
| match_360_availability | 166 | 1813 | 9.1561% |

## Separate 360 coverage and comparison

360 files cover Euro 2020 (51 matches), Euro 2024 (51) and World Cup 2022 (64). Across all shots, 3,960 join a separate 360 record and 3,822 have valid separate frames. Among base shots, 3,017 join: 2,939 valid frames, 78 invalid frames, zero empty frames and 32,040 missing frames. Of the valid separate frames, 2,740 satisfy the same provisional keeper rule. Separate 360 is diagnostic only and never repairs or gates embedded-frame eligibility.

| Competition/season | All-shot joins | All-shot valid 360 | Base joins | Base valid 360 | Base invalid 360 | Base missing 360 | Base position-usable 360 | Count/status discrepancies |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1. Bundesliga 2015/2016 | 0 | 0 | 0 | 0 | 0 | 625 | 0 | 0 |
| Copa America 2024 | 0 | 0 | 0 | 0 | 0 | 563 | 0 | 0 |
| UEFA Euro 2020 | 1215 | 1179 | 942 | 923 | 19 | 26 | 838 | 909 |
| UEFA Euro 2024 | 1299 | 1259 | 992 | 973 | 19 | 30 | 928 | 934 |
| La Liga 2015/2016 | 0 | 0 | 0 | 0 | 0 | 7148 | 0 | 0 |
| Ligue 1 2015/2016 | 0 | 0 | 0 | 0 | 0 | 6639 | 0 | 0 |
| Premier League 2015/2016 | 0 | 0 | 0 | 0 | 0 | 7790 | 0 | 0 |
| Serie A 2015/2016 | 0 | 0 | 0 | 0 | 0 | 7953 | 0 | 0 |
| FIFA World Cup 2018 | 0 | 0 | 0 | 0 | 0 | 1232 | 0 | 0 |
| FIFA World Cup 2022 | 1446 | 1384 | 1083 | 1043 | 40 | 34 | 974 | 1045 |

There are 2,888 count/status discrepancies among 3,017 comparisons. This is not a measured positional-error rate: comparisons use frame validity, visible player/defender counts and keeper counts; separate frames can include the shooter actor. Formats are deliberately not merged or normalized to hide that difference. There are zero orphan 360 UUIDs. Duplicate event IDs and duplicate within-match 360 UUIDs are fatal in the CLI; both complete runs succeeded.

## Planning screen and downstream decisions

| Check | Observed | Minimum/result |
| --- | ---: | --- |
| Complete requested cohort | Ten competition/seasons | Pass |
| Position-usable shots | 35,024 | 10,000: pass |
| Position-usable goals | 3,261 | 1,000: pass |
| Represented matches | 1,813 | 200: pass |
| Distinct competitions | 8 | 3: pass |
| Whole-match diagnostic holdout capacity | 2,020 shots; 191 goals; 109 matches | 2,000 shots and 100 goals, with nonempty complement: pass |

The diagnostic leaves 33,004 usable shots, 3,070 goals and 1,704 matches in the complement. It is not the training/test split and no match identifiers are published. Issue #11 owns split design; #13 owns discrimination, calibration and population-specific performance.

Four substantially available 2015/16 leagues contribute 29,499 of the 35,024 usable shots (84.23%): La Liga, Ligue 1, Premier League and Serie A. The population is therefore imbalanced across competition and era. Tournament coverage and partial Bundesliga coverage do not justify treating this sample as universal football. Issue #10 must define feature/missing-input policy and coordinate conversion; #11 must address grouping and imbalance. Player identity, technique, preceding movement and unseen pressure are not validated browser inputs by this audit.

## Provenance and verification

The owner executed both full runs locally with Python 3.12.3 and confirmed byte-identical `shots.jsonl`, `match-counts.csv`, `audit.json` and `manifest.json`. The assistant independently verified the uploaded aggregate audit hash, all competition-to-total count sums, disjoint exclusions, defender-distribution sums and pooled rate calculations. The extractor SHA-256 also matches the repository file. Full input and corpus files were not transferred to the assistant environment.

The owner also ran an independent source-to-corpus spot check: one goal and one non-goal each from Premier League 2015/16, Euro 2020 and World Cup 2022. All six passed type, body-part, outcome/label, original-location and normalized embedded-role checks; four matched 360 event IDs and normalized separate-frame players. These samples support semantic correctness but are not exhaustive manual validation. Synthetic tests cover failure boundaries and mapping behavior.

| Provenance item | Value |
| --- | --- |
| Official source | [Hudl StatsBomb Open Data](https://github.com/hudl/open-data) |
| Source Git revision | `4b73468fc5b0f1950f9f66fada70ad3a4f9327cb` |
| Extractor version / schema | `1.0.0` / `1` |
| Extractor SHA-256 | `f7e04df773baef31e96559c45d6b1b1a95cc177c8450f6fa4f5d0f0ad55fd7a2` |
| Python | `3.12.3` |
| Run ID | `b7d34951959b1b549ea93955c69fd7e60b91468e1ea14a43d3b146f606f2595e` |
| audit.json SHA-256 | `92bb79aec6321ca5147fc33375054e4d8c4cf8d04151bfb3f61f72f7125618a0` |
| match-counts.csv SHA-256 | `de1ab9e3cb2a0d6ad7efb4459df3d35a5f89e636f1bab277f193b898a1a7d066` |
| shots.jsonl SHA-256 | `c31b3735eb164e5b9fbd3c59d6c809a5d74b957176229828556e652df7301f2a` |

Reproduce using the [ingestion guide](../architecture/reference/statsbomb-ingestion.md) with the pinned source and extractor. Python version participates in run identity. Manifests retain the sorted input hash inventory locally; this report publishes aggregate evidence only. No raw records, match/event identifiers, player positions, shot-level examples or per-match tables are redistributed.

## Attribution and release boundary

![Hudl Statsbomb logo](../../assets/hudl-statsbomb-logo.png)

Data source: Hudl StatsBomb Open Data. This is an independent project; StatsBomb does not create or endorse its model. Follow the [rights and release record](../architecture/reference/statsbomb-rights.md). Issue #8 remains in review/QA until the final model artifact and deployed product satisfy the release checks. Completing this data audit does not close that publication gate.
