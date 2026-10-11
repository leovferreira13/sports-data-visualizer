# Shared shot features

**Status:** implemented for issue #10. Training, empirical support checks and public prediction remain pending #11–#13.

## Boundaries and version

`model/feature-contract.json` defines `positional-features/v1`, pitch dimensions, source conversion, ordered names/types/units, tolerances, missingness and supported context. `lib/features.ts` extracts browser/metric features; `scripts/xg/features.py` independently implements metric extraction and the local StatsBomb corpus adapter. Both fail on incompatible contract constants or feature order. Tests execute both implementations on shared synthetic scenes, rather than trusting a precomputed Python export.

`extractMetricFeatures(unknown)` returns either `ok` with `contract_version`, named `features`, ordered `vector` and observation `metadata`, or `unsupported` with a stable `reason` and no vector. Python uses `extract_metric_features` with the same metric JSON shape:

```json
{
  "contract_version": "positional-features/v1",
  "shot_type": "open-play",
  "shooter": { "x": 84, "y": 34 },
  "goalkeepers": [{ "x": 102, "y": 34 }],
  "defenders": [{ "x": 93, "y": 34 }],
  "observation": "synthetic"
}
```

This example is invented. Observations are `synthetic`, `embedded-frame` or `browser-scene`. Metadata records a known keeper and partial/represented/synthetic defender visibility; it is not included in the vector. The browser adapter `extractScenarioFeatures` uses the designated shooter, goalkeeper, both fixed defenders and all extra defenders. Extra attackers are deliberately ignored.

## Canonical geometry

StatsBomb positions are scaled as `x_m = x * 105 / 120`, `y_m = y * 68 / 80`. The attacked goal is on +x, center (105,34); physical posts are (105,30.34)/(105,37.66). See the official [Open Data specification v1.1, Appendices 2–3](https://github.com/hudl/open-data/blob/4b73468fc5b0f1950f9f66fada70ad3a4f9327cb/doc/StatsBomb%20Open%20Data%20Specification%20v1.1.pdf) for source coordinates and relevant-player shot frames. No direction is guessed from the goalkeeper, and no individual player is flipped.

Only source **positions** are scaled. Source post ordinates 36/44 become 30.6/37.4, whereas this project's physical post pair is 30.34/37.66. Mixing the two changes the angle and cone. Using a canonical 105 × 68 pitch with a physical 7.32 m goal is a modeling approximation, not measured stadium dimensions. Geometry is calculated after conversion, in meters; SVG projection never enters feature extraction. There is no clamping, rounding or learned scaling. Any fitted preprocessing belongs to #11 and must be exported with the later model.

## Ordered vector

Let S be the shooter, K the keeper, G the goal center and D the observed opponent outfield players.

| Index | Name | Type/unit | Definition |
| --- | --- | --- | --- |
| 0 | `shot_distance_m` | float/m | Euclidean S–G distance |
| 1 | `goal_opening_angle_deg` | float/degrees | `atan2(abs(cross), dot)` between shooter-to-post vectors, converted to degrees |
| 2 | `absolute_lateral_offset_m` | float/m | `abs(S.y - 34)` |
| 3 | `visible_defender_count` | integer/count | Number of D; excludes the keeper |
| 4 | `defenders_in_cone_count` | integer/count | Defender centers inside the closed finite S/post/post triangle |
| 5 | `nearest_visible_defender_distance_m` | float/m | Minimum S–D distance, or pitch diagonal when a valid observation has zero D |
| 6 | `goalkeeper_distance_to_goal_m` | float/m | Euclidean K–G distance |
| 7 | `goalkeeper_distance_to_shot_m` | float/m | Euclidean K–S distance |

The cone includes its rays, goal segment and shooter vertex. The implementation calculates barycentric weights and accepts all three >= -1e-9. This is a dimensionless boundary tolerance. Defender marker radius, the infinite wedge and a line to goal center do not define this feature. Co-located observed players are valid; nearest distance can be zero.

For a known zero-defender list, nearest distance uses `hypot(105,68)`; the zero count distinguishes this finite sentinel. Missing observations never receive this fallback. Keeper visibility is required metadata, not a constant learned feature. Keeper alignment is omitted in v1. Later model evaluation must decide whether adding it is justified.

## Domain and failures

The metric core accepts a shooter at `0 <= x <105`, `0 <= y <=68`; observed opponents may occupy the full closed pitch. It rejects nonnumeric/boolean/nonfinite/out-of-range positions, unknown version/context, missing or multiple keepers, missing/malformed defenders, more than ten defenders and unknown observation provenance. A goal-line/post shot is unsupported because the triangle is singular. A penalty returns `penalty_separate_route`; it never receives open-play features. #12 owns the fixed penalty convention.

The UI keeps its existing marker-safe attacking-half bounds. Offline players outside those bounds are **not** moved or discarded. The local audit counts accepted shots outside the UI bounds and records represented scenes whose observed players would not fit them. These counts describe geometry compatibility, not probability support.

The source adapter accepts schema-1 **base corpus rows** from [ingestion](statsbomb-ingestion.md), not arbitrary raw events. Ingestion establishes male/Open Play eligibility; schema 1 omits shot type and gender from each row. Feature materialization verifies that corpus's manifest and audit. The adapter additionally validates foot body part, source positions, actual embedded frame state and explicit normalized team/position/keeper roles. Contradictory shot context is rejected when supplied. Missing, empty or invalid frames, unknown roles and zero/multiple opponent keepers have distinct rejection reasons. Diagnostic counters cannot override actual player observations, and separate 360 never repairs an embedded frame.

Relevant players may be only partially visible. Zero visible defenders does not prove no defenders existed. The browser list is the user-represented set, not an estimate of unseen players. Technique, player identity, teammates, extra attackers, unseen pressure and preceding motion have no claimed numerical effect. Sparse scenes and unfamiliar positions may still be outside empirical training support despite producing valid geometry. #11/#13 own that assessment before publication.

## Local extraction and recovery

Run from the project root after producing the pinned ingestion run:

```bash
python3 scripts/xg/extract_features.py \
  --input-dir data/derived/xg-audit/<ingestion-run-id> \
  --output-dir data/derived/xg-features
```

Use the actual ingestion directory containing `shots.jsonl`, `audit.json` and `manifest.json`. The completed issue #9 run ID is `b7d34951959b1b549ea93955c69fd7e60b91468e1ea14a43d3b146f606f2595e`; its enclosing directory is whichever output path was chosen locally.

The extractor validates ingestion run identity and corpus/audit hashes, labels, schema and unique shot identities. It emits an immutable run directory containing:

| Output | Visibility | Contents |
| --- | --- | --- |
| `features.jsonl` | Local only | Accepted vectors/features plus match/competition/season/event IDs and actual goal labels outside the vector |
| `feature-audit.json` | Aggregate review allowed | Accepted/rejected shots/goals, exclusive reasons, competition counts, ranges, visibility/zero-defender diagnostics and UI compatibility counts |
| `manifest.json` | Local provenance | Input/code/contract hashes, ingestion/source identity, Python version and output hashes |

Rows are sorted deterministically. Inputs and code are rechecked before atomic directory publication; a failed run leaves no completed artifact. Repeating identical inputs/code/Python produces identical bytes and the same run ID. A differing pre-existing immutable directory is rejected, never overwritten. Rebuild from the pinned ingestion run into a fresh output directory to recover. Internal project output must stay under ignored `data/derived/`. No source or real feature rows enter Git or a deployed browser bundle.

## Verification

`npm run check:precommit` runs Vitest, the Python unittest suite, types, lint and documentation/script checks. Vitest invokes `python3 scripts/xg/tests/feature_parity_runner.py` and compares shared golden/failure/varied scenes and source conversions. Python must be available in development and CI; a missing interpreter is a failed check.

Counts/status/reasons match exactly. Floating values must satisfy `abs(a-b) <= 1e-9 + 1e-9*max(abs(a),abs(b))`. Independent central-shot angle/distance oracles complement cross-language comparisons. Tests cover closed/near cone boundaries, reflection, defender order, fixed/extra defenders, keeper movement, zero/ten/eleven defenders, full-pitch opponents, context/missingness failures, atomic output, corruption and repeatability. Full-corpus aggregate results and remaining provenance/repeatability QA are tracked in [the feature audit report](../../reports/xg-feature-audit.md).
