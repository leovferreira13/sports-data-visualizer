# xG training methodology: execution status

**Issue:** #11. **Protocol:** `xg-training/v1`.
**Status:** training contracts and local scripts implemented; actual-corpus fitting, model selection and fresh-environment reproduction are pending owner execution. No final-test outcomes have been inspected and no public model is approved.

The [offline training guide](../architecture/reference/xg-training.md) provides exact setup, preparation, training, comparison and review instructions. `model/training-protocol.json` declares the complete experiment matrix and decision rules before real fitting. Five experiments compare constant prevalence, geometry logistic, geometry plus defenders logistic, full logistic and full XGBoost on the same match partitions.

The verified input audit records 35,020 eligible positional shots and 3,259 goals from 1,813 matches. Those figures establish corpus feasibility, not model quality. The private feature rows remain on the owner's machine; they have not been transferred or trained here.

Synthetic verification exercises the complete workflow, train-only preprocessing, match isolation, export probability parity, full-run reproduction and held-out-label mutation. Altering test outcomes does not change training exploration, validation predictions or model selection. Invented data cannot establish real predictive quality, calibration, feature contribution or empirical support.

The workflow writes a complete English `methodology.md` from its versioned aggregate `evaluation.json`, including data/exclusions, feature-group rationale, preprocessing, tuning, calibration, validation comparisons, paired uncertainty, selected/no-candidate decision and limitations. After the owner executes and shares aggregate evidence, replace this status record with the reviewed generated report and its aggregate evidence; do not enter example performance numbers or pick a winning model beforehand.

The [aggregate evaluation contract](../../model/evaluation-contract.json) supports the Methodology and results tab in #4. Validation results remain distinct from the final held-out evaluation in #13. Candidate parameters stay local until export/rights review, and public xG remains gated by #8/#12/#13.
