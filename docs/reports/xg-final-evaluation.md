# Actual-corpus final xG evaluation review

**Reviewed:** 2026-10-11. **Scientific outcome:** accepted aggregate evidence with explicit support/transfer limitations. **Publication decision:** pending parameter/export/rights and actual-product QA; no public release authorization.

Final run: `fdfc9df9e8b7c9a565df298d372a262091439fb8fb14a69043c1c904e7379ee4`. Evidence: `e579e10f9699077ddf05e7433af5ed63edf0e03c3ea8c7ca295844951d74ea08`. Frozen model: `758526873b8a3a2681f655c064dee52f8bd33749accd499d015420dbe8e11b9a`. Training run: `222909fe801f4865897fea3541e023fed626f6736dca6ef69ceada1f7c57945a`.

## Verification and reproduction

The assistant validated the final schema, canonical evidence and manifest identities, linked provenance, hashes of all seven submitted files, exact current scientific/browser code hashes, and byte-for-byte regeneration of report, model card, release checks and app evidence. The submitted final protocol matches the predeclared committed contract. Original development evidence remains separately identified and unchanged.

The owner reports that all requested comparators passed, covering final scientific reproduction, complete exact-byte comparison and generated-view verification. This is owner-reported complete local reproduction, not an assistant rerun against private data. Exact terminal logs and recreation of a fresh environment were not independently inspected. Python 3.12.3 is recorded in the actual run; the synthetic implementation suite used 3.12.14 with the same lock.

Private source/preparation rows, test predictions and actual parameter envelopes were not supplied in this review and are not committed. Their manifest-declared output hashes are retained as provenance, but were not independently recomputed. The archived seven-file folder is a public evidence subset, not a complete private run suitable for the complete comparator.

## Final findings

Use the [generated final methodology](xg-final-first-run/methodology.md), [model card](xg-final-first-run/model-card.md), [final evidence](xg-final-first-run/final-evaluation.json) and [app handoff](xg-final-first-run/app-evidence.json) for numeric tables. These were regenerated from the same evidence; this review does not maintain another manually copied score table.

The final holdout has 363 matches, 7,160 shots and 655 goals. All seven predeclared predicates pass. Both paired selected-minus-full-logistic probability-score intervals lie below zero, as do both selected-minus-constant intervals. This adds evidence of a modest average advantage for the frozen XGBoost within the represented cohort; it does not establish universal superiority, competition/period transfer, or an advantage in every slice. The original selection is unchanged and there was no post-test refit or calibration change.

The selected mean probability is close to the observed goal frequency, and no supported calibration bin triggers the declared residual-interval review rule. This is compatible with useful aggregate calibration, not proof of perfect calibration. All bins from 0.5 upwards are sparse; seven outcomes in the 0.9–1.0 bin cannot establish reliable high-probability calibration, even when a bootstrap interval appears narrow because all observed outcomes were goals.

## Slice disposition

- Distance: the 5–30 m groups have substantially more support than shots below 5 m or beyond 30 m. Beyond 30 m only two test goals are observed, and beyond 50 m none. Do not infer calibrated extreme-distance probabilities from those groups.
- Keeper position: 5–10 m has a favorable diagnostic comparison with logistic. The 10–20 m group has only 109 shots/27 goals and an interval crossing zero versus both references; beyond 20 m there are nine shots/no goals. No strong advanced/extreme-keeper claim is accepted.
- Defenders: one/two-visible-defender groups have only 8/62 shots. There are no zero-defender test shots, and only one zero-defender training row. No empty-pitch or low-defender-count calibration claim is accepted.
- Two defenders inside the cone: 815 shots/41 goals show worse observed XGBoost log loss than full logistic, with a diagnostic interval above zero. Record this adverse slice rather than claiming uniform improvement. It does not violate a predeclared global gate; diagnostic comparisons are not multiple-comparison-confirmatory findings.
- Competition/season: average gains do not establish a league-specific improvement everywhere. Bundesliga is represented by seven test matches; small tournament slices have wide intervals, and Copa America has fewer than ten goals. No leave-competition-out or future-period transfer test was performed.

These findings are accepted limitations for a scoped educational portfolio. They do not justify tuning on this test or replacing the frozen candidate. Critical product claims must stay within the actual support.

## Preset and scene-support disposition

Four of the five open-play presets are outside the training-only nearest-neighbor reference: centralChance, oneOnOne, tightAngle and longShot. crowdedBox is within that reference. Individual feature marginals being in range does not establish joint support; the distance diagnostic itself also is not a proof of a realistic or unrealistic scene. Several presets represent very few defenders relative to the embedded-frame cohort.

Controlled keeper/defender changes produce model responses; player-order/reflection invariants pass, missing keeper/invalid coordinate/goal-line inputs are unsupported, and penalty remains the separate fixed 0.76 convention. Individual tree plateaus and nonmonotonic changes remain valid.

Required #4 handoff:

- Surface a visible explanation that probabilities describe an independent model trained on partial embedded-frame observations, with synthetic/represented scenes and uncertainty.
- Flag presets with outside-reference support and disclose that zero/few defenders and extreme keeper/shot positions lack robust calibration evidence. Do not show these as empirically validated scenarios.
- Explain that movement may leave tree predictions unchanged and that before/after changes are within-model comparisons, not causal effects.
- Keep sparse calibration/groups visible in the Methodology and results tab, including the adverse cone-count slice and cohort-transfer limitations.
- Do not derive a runtime support classifier or newly tuned rejection threshold from this final test. Any new support behavior belongs in #4 with a predeclared implementation contract.

## Dated decision and remaining publication work

Reviewer: assistant/implementer, using owner-supplied aggregates and owner-reported comparator PASS. Decision: accept the frozen model's offline predictive evidence for continued #4 integration planning, subject to the limitations above. The unmodified automated record remains needs_review and publication_authorized=false.

Model distribution approval remains pending because actual parameter-only export contents were not independently inspected here. Recheck current official source/agreement/logo guidance and the documented conditional support scope for the actual publication path. Inspect export contents, tracked history and integrated bundles/network assets for source records or recoverable examples.

Before publication, #4/#8 must verify accessible source/logo attribution on /en and /br including small screens, the required Methodology and results tab, accepted-support warnings, the non-commercial scope and final product assets. Finish #8 QA then. Do not claim the epic is fully release-ready or mark #3/#13 closed automatically from this review. The owner controls merge/status/publication.
