# Football, Visualized — delivery roadmap

**Status:** first public release preparation · **Updated:** 2026-10-12

**#26 progress:** the existing Railway demo is accessible. Repeatable production settings and release checks are prepared; real-origin rebuild, final branding guidance and public repository access remain release gates. See [release QA](reports/public-release-qa.md).

## Delivery rule

Ship a small, trustworthy educational portfolio with intuitive interaction and reviewer-visible reasoning. The scientific milestone is complete; another optimization cycle, Learn experiments, traffic targets and a fixed feedback quota are not release prerequisites.

| Milestone | Delivered or planned result | Exit condition |
| --- | --- | --- |
| 0. Prepare | Repository, local app and working agreement | Runnable shell and documented scope |
| 1. Playable pitch | Metric SVG geometry, presets and accessible movement (#2) | Mouse/touch/keyboard controls and geometry checks |
| 2. Prove the calculation | Pinned source audit, shared features, training, parity and final review (#9–#13) | Accepted scientific evidence with explicit support/transfer limitations |
| 3. Reviewed-model Playground | Exact browser model asset, eight live cards and inline Methodology/results (#4) | Local product QA recorded; release-specific gaps remain explicit |
| 4. Portfolio release | Five locales (#24, complete), presentation (#25), Railway hosting/public repository (#26) | Final public URL, metadata and scoped asset/attribution checks pass |
| 5. Refine from use | Optional Learn (#5), scenario links and observed improvements | Priorities follow actual feedback |

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

#3 and #8 are closed after their scoped scientific/rights handoffs. #4 integrates the exact reviewed parameter envelope and records local build/network/attribution QA. #24 extends the product to five locales. These completed checks are dated; #26 refreshes relevant assets/content for the exact release build and resolves the outstanding detailed per-asset logo-guidance review. Local QA does not prove a public deployment.

## Portfolio release sequence

1. **#24 — localization:** delivered. [Localization QA](reports/localization-qa.md) records checks and translation-review limits.
2. **#25 — presentation:** concise README, confirmed author links, screenshots/share image, localized metadata and professional impersonal documentation. [Portfolio QA](reports/portfolio-presentation-qa.md) distinguishes completed local work from live checks.
3. **#26 — publication:** build/start in the selected Railway account, confirmed HTTPS origin, public repository, refreshed content/history/asset/attribution checks, live smoke tests and rollback instructions.

#25 can be reviewed before deployment. Configure `SITE_URL`, rebuild and add the actual live link when #26 supplies the domain; deployed metadata/share-preview checks finish both tasks without a circular dependency. Publication does not depend on Learn.

## First-release acceptance

1. A new visitor can move the shooter without preparatory reading.
2. Distances, angles and drawn geometry agree; current cards reflect the retained inputs.
3. Goalkeeper/defender movements evaluate actual features without invented causal/monotonic claims.
4. Probabilities remain bounded; penalties, unavailable assets and invalid inputs follow explicit rules.
5. All six presets are editable in all five languages; language changes preserve the scene.
6. Mouse/touch and accessible alternatives work at desktop/mobile widths.
7. Model provenance, omitted factors, calibration/support and adverse findings are visible in Methodology.
8. A recruiter can identify author/purpose quickly; technical readers can find evidence, architecture and reproduction.
9. Public app/repository links, share metadata and attribution are checked on the actual release.

## Behavior research follow-up

#31 adds predeclared offline comparisons of frozen full logistic, current XGBoost and a monotonic XGBoost candidate. Dense isolated/physical sweeps, quality margins, separate research evidence and optional unused-match confirmation are implemented as tooling. Actual-corpus phase A has been locally executed and reproduced, with submitted aggregate consistency reviewed. Its original disposition is retain-current; no new model or goalkeeper defaults are published. Correcting isolated distance/angle directions is an important product priority; a detailed comparison of exactly current and monotonic XGBoost is deferred to #34. Phase B is not required for this scoped closure. See [the research guide](architecture/reference/xg-behavior.md). This refinement is separate from #30 interaction fixes and does not reopen the first-release dependency chain.

## Deferred work

Learn (#5) may add two or three optional experiments using the same scene/features; it must preserve free control and does not own publication. Scenario links are a useful next improvement if not included in v0.1. Historical reconstructions require sourced positions/context and clear approximation labels. Famous goals, other metrics, accounts and a broader platform are outside the release dependency chain.

Use targeted qualitative review when readers are available. Record real feedback and follow-ups; no fixed participant quota or analytics requirement applies.
