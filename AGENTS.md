# Repository working agreement

## Goal

Ship a small, useful xG playground quickly. Playground is the default; Learn is optional. The UI supports Portuguese and English. See `docs/VISION.md` and `docs/ROADMAP.md`.

## Sources of truth

| Concern | Source |
| --- | --- |
| Product intent | `docs/VISION.md` |
| Planned milestones and acceptance | `docs/ROADMAP.md` and the current Issue |
| Planned technical direction | `docs/ARCHITECTURE.md` |
| Task status and priority | GitHub Project, when connected |
| Implementation and verification | Code, tests, and PR |

Architecture is a proposal until implemented. Update it as actual boundaries become clear.

## Work cycle

- Create one bounded Issue for each outcome; link the roadmap milestone and provide observable acceptance criteria.
- Specify the approach in the Issue before implementing when a meaningful design choice remains. Keep trivial tasks brief.
- Start an isolated branch from current `main`: `task/<issue-number>-<short-name>`.
- Keep each PR focused, link its Issue, describe what changed and how it was checked. Do not merge automatically.
- Update affected docs with code. Record limitations and open questions honestly.
- Follow `docs/DEVELOPMENT_PROCESS.md` for status transitions and backlog conventions.

## Product and data rules

- Never label a provisional geometry heuristic as xG. An xG estimate requires documented model provenance, inputs, limitations, and checks.
- A visual factor only receives a claimed numerical effect if the model actually uses it. Explain before/after changes as comparisons within the model.
- Treat penalties separately if the model does not represent them. Historical scenes require sourcing and clear approximation labels.
- Keep the v0.1 small: no accounts, database, unrelated statistics, or generic platform infrastructure.
- Make drag usable with mouse and touch and offer a keyboard or equivalent accessible control.

Never commit credentials or private user data.
