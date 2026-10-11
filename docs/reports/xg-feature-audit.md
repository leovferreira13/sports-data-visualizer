# Positional feature extraction audit

**Issue:** #10. **Contract:** `positional-features/v1`.
**Status:** synthetic validation complete; complete licensed-corpus run pending.

## Verified implementation evidence

The committed synthetic scenes exercise central/wide/long/near-goal shots, full-pitch positions, the closed cone and its tolerance, zero/ten/eleven defenders, goal-line/post failures and reflection. TypeScript tests execute Python on the same synthetic scene/failure/source inputs, including deterministic varied scenes. Independent analytic central angle/distance checks protect against shared mistakes. Browser preset and movement tests cover fixed/added defenders, goalkeeper position and intentional attacker omission.

Python materialization tests verify input/output hashes, manifest identity, exclusive exclusions, goal labels, deterministic rows and byte-identical reruns, incompatible schemas, duplicate identities, protected output locations, failed-run cleanup and immutable output conflicts. These tests use invented records only. They do not measure the real population's feature distribution.

A separate limited read-only smoke check on one official event file from the pinned source confirmed the +x goal convention for both teams and produced valid feature vectors for its 25 eligible open-play foot shots. No source examples or identifiers were committed. This checks real-format compatibility; it is not the complete feature population audit or an independent predictive evaluation.

The [completed data audit](xg-data-audit.md) supplies the starting evidence: 35,057 eligible base shots, 35,024 provisional position-usable shots and 3,261 usable goals. These are **ingestion counts**, not a completed feature run. Feature-v1 additionally rejects singular goal-line geometry and enforces at most ten observed outfield defenders. The final retained counts must be measured rather than assumed.

## Complete local validation required

The complete ingestion corpus was not available in the implementation environment. On the owner's checkout, use the existing pinned ingestion run:

```bash
python3 scripts/xg/extract_features.py \
  --input-dir data/derived/xg-audit/b7d34951959b1b549ea93955c69fd7e60b91468e1ea14a43d3b146f606f2595e \
  --output-dir data/derived/xg-features

python3 scripts/xg/extract_features.py \
  --input-dir data/derived/xg-audit/b7d34951959b1b549ea93955c69fd7e60b91468e1ea14a43d3b146f606f2595e \
  --output-dir data/derived/xg-features-repeat
```

Replace the enclosing ingestion path if a different `--output-dir` was used in #9. Both calls print their completed immutable run directories. Compare `features.jsonl`, `feature-audit.json` and `manifest.json` byte-for-byte; identical run IDs alone do not replace that comparison. Upload/share only the aggregate `feature-audit.json` for review, keeping real feature rows and identifiers private.

The completed aggregate review must record accepted/rejected shots and goals per competition/season, exclusive reasons, represented matches, visible defender distribution, zero-defender sentinel frequency, finite feature ranges and UI-bound differences. Reconcile accepted + rejected with the ingestion base population. Review the reported planning minima; if any fails, revisit scope before #11. Match-level split/holdout feasibility is still checked during #11 rather than inferred from synthetic tests.

Record actual feature run ID, Python version, contract/extractor/input/output hashes and two-run comparison here when verified. Do not insert unmeasured counts or infer predictive quality from geometric parity. #10's complete-corpus validation remains pending until that evidence is reviewed; public inference remains gated by #11–#13 and final rights QA in #8.
