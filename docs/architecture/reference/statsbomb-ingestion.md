# StatsBomb shot ingestion and audit

**Status:** ingestion and the [full real-data audit](../../reports/xg-data-audit.md) are complete for issue #9. Feature extraction, training and browser prediction remain separate tasks.

## Runtime boundary

`scripts/xg/ingest_statsbomb.py` is an offline Python standard-library CLI. It reads a pinned local checkout of [StatsBomb Open Data](https://github.com/hudl/open-data), extracts a local-only corpus and checks positional coverage before modeling. It is not imported by Next.js, served by the site or run during a production build. Python 3.10 or newer and Git are required; ordinary tests need no dataset or network.

Embedded `shot.freeze_frame` is the primary positional source. Separate 360 records join on event ID for coverage and count/status comparisons only. They do not repair missing embedded frames or change shot eligibility. See [ADR 004](../adr/004-local-shot-ingestion.md).

## Rebuild locally

From the project root, obtain the official checkout under the ignored data directory. The source revision selected for #9 is `4b73468fc5b0f1950f9f66fada70ad3a4f9327cb`. Use an exact revision, not a moving branch, when reproducing a result. A completed aggregate report will record its source and extractor digests.

```bash
mkdir -p data/raw
git clone https://github.com/hudl/open-data.git data/raw/open-data
git -C data/raw/open-data checkout --detach 4b73468fc5b0f1950f9f66fada70ad3a4f9327cb
python3 scripts/xg/ingest_statsbomb.py \
  --source-dir data/raw/open-data \
  --output-dir data/derived/xg-audit
```

The default audits all ten requested men's competition/seasons: World Cup 2022 and Euro 2020; the five 2015/16 Big Five leagues; World Cup 2018, Euro 2024 and Copa América 2024. Selection uses metadata names, gender and non-youth status, not assumed numeric IDs. Missing candidate seasons appear with zero coverage. Women's competitions remain a separate future population.

For a quick local subset, repeat `--competition` using keys shown by `--help`, for example `--competition world-cup-2022`. Its manifest and audit explicitly identify the subset, and its full-cohort planning screen cannot pass.

The source checkout root must be its own Git root. Every consumed file must be tracked in `HEAD` with matching content; changes, untracked optional inputs and missing tracked 360 files fail. A sparse checkout is acceptable only if every requested match/event file and every corresponding tracked 360 file is present. Content hashes and source revision are checked again before finalization.

## Eligibility, label and visibility

The exclusive funnel retains a shot only when its type is Open Play, body part is Left Foot or Right Foot, original location is finite and inside the 120 × 80 source domain, and outcome is recognized. Rejections follow that order, with separate missing-field reasons. The recognized outcomes are Goal, Blocked, Off T, Post, Saved, Wayward, Saved Off Target and Saved to Post. The official v1.1 specification also spells the last outcome Saved To Post; both documented spellings map to the same negative label. Goal alone maps to 1. Unknown outcomes never become negative examples. `shot.statsbomb_xg` is never copied into the corpus or used as a target/input.

The mapping follows the official [Open Data Specification v1.1](https://github.com/hudl/open-data/blob/master/doc/StatsBomb%20Open%20Data%20Specification%20v1.1.pdf); consult the pinned version in the audit. Original source coordinates remain local. Conversion to the browser's 105 × 68 m scene belongs to #10; ingestion never clamps values into that scene.

Every eligible base shot is retained, including shots with missing/unusable positioning. Embedded frame states are `missing`, `empty`, `valid` and `invalid`. Player locations, explicit boolean team membership and known position roles are validated. Separate 360 roles instead use explicit boolean `keeper`, `teammate` and `actor` fields. Invalid rows make the frame unusable and are counted; usable player rows remain available locally for diagnosis.

An opponent goalkeeper has explicit opposing-team membership and the goalkeeper role. A visible defender is an identifiable opposing outfield player. Unknown roles are not assumed to be defenders. The provisional position-usable cohort requires a valid nonempty embedded frame with exactly one identifiable opponent goalkeeper. This is an audit rule; #10 still determines the modeling policy for missing inputs.

Zero visible defenders, zero identifiable goalkeepers and an empty frame do not establish that those players were absent from the pitch. The frame shows visible players only. Defender distributions are computed over valid embedded frames, with that denominator named; invalid-frame counts describe the validated subset only.

Duplicate event IDs across selected matches and duplicate 360 UUIDs within a match fail with occurrence counts. Orphan 360 UUIDs and differences between overlapping frame formats are diagnostic counts. Comparisons concern player counts and validity, not unverified player-by-player identity matching. Separate 360 frames can include the actor/shooter; player-count comparisons deliberately retain that format difference rather than silently normalizing or merging the sources.

## Output schema and failure recovery

Each successful run creates an immutable directory named by its manifest digest under `data/derived/xg-audit/`:

| Local file | Contract |
| --- | --- |
| `shots.jsonl` | Schema version, competition/season/match/event identifiers, goal label, foot, original location, validated embedded/360 players and visibility/status diagnostics. Player names and unrelated event fields are omitted. |
| `match-counts.csv` | One row per discovered match, including zero-shot matches; events, funnel shots/goals/represented matches, exclusions, frame/keeper statuses and 360 coverage. |
| `audit.json` | Selection, available/unavailable competition inventory, competition/overall counts, rates with explicit numerators and denominators, goal/outcome and defender distributions, and feasibility result. No match/event identifiers or shot coordinates. |
| `manifest.json` | Complete-run marker, source URL/full Git SHA, extractor and schema versions, extractor SHA-256, Python version, sorted input content hashes and output hashes, and run ID. |

Counts reconcile from matches to competitions to totals, including every exclusive funnel rejection. A zero denominator yields a null rate. All payloads use deterministic ordering without timestamps or absolute machine paths. Identical source, extractor, Python version and selection reproduce byte-identical outputs. Python version is part of the run identity.

Inside this project, the CLI restricts outputs to `data/derived/`; it rejects `public/`, `docs/reports/` and other project paths before writing source rows. External local output directories are supported for experiments and synthetic tests and must not be published.

Outputs are staged and renamed only after reconciliation and source/extractor revalidation. A failed run returns nonzero, removes its staging directory and preserves previous complete runs. An existing run with modified outputs is never overwritten: use a fresh output directory and investigate the difference. Rebuild from the recorded source revision and extractor contents to recover. The CLI reports aggregates and file/match context, not raw records.

## Feasibility and downstream handoff

The agreed planning screen requires at least 10,000 position-usable shots, 1,000 goals, 200 represented matches and three competitions. A deterministic whole-match diagnostic must have capacity for 2,000 held-out shots and 100 goals while leaving a nonempty complement. It is not the training/test split, and its identifiers are not published. #11 owns the split design and #13 owns model quality/calibration checks.

These minima are not statistical guarantees. A negative screen completes the data audit but requires an owner decision on a narrower population/claim or authorized expansion before training experiments. Passing still requires documenting competition imbalance, partial visibility and exclusions.

## Verification and publication

```bash
python3 -m unittest discover -s scripts/xg/tests -p 'test_*.py'
npm run check:precommit
git check-ignore data/raw/open-data/data/competitions.json data/derived/xg-audit/example/shots.jsonl
```

The tests create tiny synthetic Git repositories; they do not download data or include real shot fixtures. The canonical precommit script runs them alongside existing application checks. The actual dataset must be audited twice, output digests compared and labels/joins/roles privately spot-checked across several competitions before issue #9 is complete.

Only a completed competition-level aggregate report, schema/methodology, synthetic fixtures and code may be committed for this issue. Keep all original, per-match and shot-level outputs inside ignored data paths. Inspect tracked content and `public/` before the PR. Follow the [rights and release record](statsbomb-rights.md); #8 remains open until the final model and deployed product are reviewed.

### Completed execution evidence

On 2026-10-11, the owner completed two full local audits at the pinned revision with Python 3.12.3 and confirmed byte-identical corpus, match counts, audit and manifest. All 1,813 event files and 166 corresponding tracked 360 inputs were present. This resolves the earlier connector transport blocker; locally omitted tracked files must still fail rather than become reported missing coverage.

The aggregate audit hash and competition-to-total counts, exclusions, visibility distributions and pooled rates were independently checked from the uploaded `audit.json`. The repository extractor hash matches the local run. Six source-to-corpus examples (goal and non-goal across Premier League 2015/16, Euro 2020 and World Cup 2022) passed the owner's independent spot check; four also verified separate 360 joins and normalized roles. Original inputs and shot/per-match outputs remain local.

The [completed report](../../reports/xg-data-audit.md) records provenance, competition coverage, denominators, exclusions, visibility and 360 comparisons. Its planning screen passes with 35,024 position-usable shots and 3,261 goals across eight distinct competitions. This is data feasibility evidence only; #10, #11 and #13 still own features, training/splitting and evaluation.
