# Football, Visualized — delivery roadmap

**Status:** milestones 0–4 complete · **Updated:** 2026-10-14

Future delivery is tracked in **GitHub Projects**. This document will no longer be updated per task.

## Delivery rule

Ship a small, trustworthy educational portfolio with intuitive interaction and reviewer-visible reasoning. Milestones 0–4 are complete. Another optimization cycle, Learn experiments, traffic targets and a fixed feedback quota were not required for that completion.

| Milestone | Result | Status |
| --- | --- | --- |
| 0. Prepare | Repository, local app and working agreement (#1) | Complete |
| 1. Playable pitch | Metric SVG geometry, presets and accessible movement (#2) | Complete |
| 2. Prove the calculation | Pinned source audit, shared features, training, parity and final review (#9–#13) | Complete |
| 3. Reviewed-model Playground | Exact browser model asset, eight live cards and inline Methodology/results (#4) | Complete |
| 4. Portfolio release | Five locales (#24), presentation (#25), and public Railway hosting (#26) | Complete |
| 5. Refine from use | Optional Learn (#5), scenario links, historical reconstructions and feedback | Future work, not a commitment |

## Implemented product

- Playground opens directly: half-pitch, six editable presets, shooter, goalkeeper and zero to three represented defenders. Extra attackers are visual only.
- Desktop places the pitch left and xG/eight input cards right. Mobile uses a compact sticky xG strip inside the Playground followed by pitch and cards. Secondary position inputs are collapsible; drag and keyboard controls remain immediate.
- Predictions use the independently trained, frozen shallow XGBoost. Tree plateaus/nonmonotonic responses are valid; movement does not imply causal effects. Invalid/unavailable learned predictions have no heuristic fallback.
- Penalties use a separate fixed 0.76 convention. Rare/extreme scenes stay explorable with their limitations explained in Methodology.
- Methodology/results is server-rendered below the pitch and shares reviewed aggregate evidence with the reports. Former dedicated URLs redirect to the same locale's anchor. No section-jump links, last-change panel or technical-links promotional panel is shown.
- `/en`, `/br`, `/nl`, `/es`, `/de` use complete locale resources, browser/saved preferences and locale-aware formatting. Scene state survives language changes and reload within the same tab.

## Model rationale and completion

The licensed-artifact-first proposal was superseded by the independent model pipeline: audit legally usable StatsBomb Open Data (#9), define matching offline/browser features (#10), compare regularized logistic baselines and a constrained XGBoost positional candidate (#11), verify numerical parity (#12), then inspect final calibration, probability scores and scene support (#13). Train-only tuning, separate calibration/selection and match-held-out final test protect the evaluation boundary.

The actual-corpus final aggregates pass the predeclared gates; complete local comparators were reported PASS. Aggregate identities/provenance and generated-view consistency were independently checked. Sparse/extreme/low-defender support, partial visibility, cohort transfer and an adverse cone-count slice remain accepted limitations. No source rows or shot-level examples are distributed. See the [final review](reports/xg-final-evaluation.md) and [implementation summary](reports/xg-implementation-summary.md).

#3 and #8 are closed after their scoped scientific/rights handoffs. #4 integrates the exact reviewed parameter envelope and records local build/network/attribution QA. #24 extends the product to five locales. #25 and #26 are closed. The repository is public, and the README links the live Railway Playground. Dated preparation notes stay in the [release QA report](reports/public-release-qa.md) as a historical record, not as an open item in this roadmap.

## Completed portfolio release

1. **#24 — localization:** closed. [Localization QA](reports/localization-qa.md) records checks and translation-review limits.
2. **#25 — presentation:** closed. The work covers a concise README, confirmed author links, screenshots and a share image, localized metadata, and professional impersonal documentation. [Portfolio QA](reports/portfolio-presentation-qa.md) records that local presentation work.
3. **#26 — publication:** closed. The repository is public, and the README links the existing Railway Playground.

## Completed first-release acceptance

Milestones 0–4 delivered these outcomes:

1. A new visitor can move the shooter without preparatory reading.
2. Distances, angles and drawn geometry agree; current cards reflect the retained inputs.
3. Goalkeeper/defender movements evaluate actual features without invented causal/monotonic claims.
4. Probabilities remain bounded; penalties, unavailable assets and invalid inputs follow explicit rules.
5. All six presets are editable in all five languages; language changes preserve the scene.
6. Mouse/touch and accessible alternatives work at desktop/mobile widths.
7. Model provenance, omitted factors, calibration/support and adverse findings are visible in Methodology.
8. A recruiter can identify author/purpose quickly; technical readers can find evidence, architecture and reproduction.
9. The repository is public, and the README links the live Playground. The dated release preparation record is historical and is not an open check in this roadmap.

## Future work (not commitments)

GitHub Projects tracks the items below. This document will no longer be updated per task.

### Milestone 5 — refine from use

- Optional Learn experiments (#5) may add two or three steps using the same scene and features. They must preserve free control.
- Shareable scenario links (#36).
- Historical reconstructions from a reliable source (#37), with sourced positions and context and clear approximation labels.
- Qualitative feedback without analytics (#38). Record available feedback and follow-ups. No fixed participant quota or analytics requirement applies.

These items are not commitments. Famous goals without a reliable source, other metrics, accounts and a broader platform stay outside this record.

### Model-behavior research track

#31 is closed, and [PR #33](https://github.com/leovferreira13/sports-data-visualizer/pull/33) is merged. Phase A was locally executed and reproduced; its disposition is retain-current, and no new model or goalkeeper defaults were published. Phase B was not required for that closure. #34 is a possible follow-up comparison of the current and monotonic XGBoost models and is not a commitment. This track sits outside completed milestones 0–4. See [the research guide](architecture/reference/xg-behavior.md).
