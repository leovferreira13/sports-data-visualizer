# Repository working agreement

## Goal

Ship a small, useful xG playground quickly. Playground is the default; Learn is optional. The UI supports Portuguese and English. See `docs/VISION.md` and `docs/ROADMAP.md`.

## Sources of truth

| Concern | Source |
| --- | --- |
| Product intent | `docs/VISION.md` |
| Planned milestones and acceptance | `docs/ROADMAP.md` and the current Issue |
| Planned technical direction and module references | `docs/architecture/overview.md` and `docs/architecture/reference/` |
| Structural decisions | `docs/architecture/adr/` |
| Task status and priority | GitHub Project #3 |
| Implementation and verification | Code, tests, and PR |

Architecture is a proposal until implemented. Update it as actual boundaries become clear.

## Work cycle

- Create one bounded Issue for each outcome; link the roadmap milestone and provide observable acceptance criteria.
- Specify the approach in the Issue before implementing when a meaningful design choice remains. Keep trivial tasks brief.
- Use the chat commands in `docs/COMMANDS.md` for spec, dev and review; never run those phases on a schedule.
- Start an isolated branch from current `main`: `agent/<issue-number>-<short-name>`.
- Keep each PR focused, link its Issue, describe what changed and how it was checked. Do not merge automatically.
- Update affected docs with code. Record limitations and open questions honestly.
- Follow `docs/DEVELOPMENT_PROCESS.md` for status transitions and backlog conventions.
- Explain material technical choices before implementation: what the framework feature does, its role here, rationale, tradeoff and a concrete example. Afterwards walk through changed files and checks so the owner can learn the stack.
- Write an ADR for consequential structural choices, update its index, and distinguish planned from implemented behavior.
- Before every commit, run the canonical `npm run check:precommit` verification script and fix failures rather than bypassing the hook. It must cover lint, TypeScript checking, Markdown language validation, and lightweight script validation. `npm install` configures `.githooks/pre-commit` through the package `prepare` script. Keep slower integration checks such as the production build and localized-route smoke test in CI unless a task specifically requires them locally.

## Product and data rules

- Use `python3 scripts/xg/compare_runs.py --left-dir <first-run-directory> --right-dir <second-run-directory>` for local audit/feature reproducibility comparisons. Record its result and keep private rows local; equal aggregate JSON alone does not verify the complete run.
- Never label a provisional geometry heuristic as xG. An xG estimate requires documented model provenance, inputs, limitations, and checks.
- A visual factor only receives a claimed numerical effect if the model actually uses it. Explain before/after changes as comparisons within the model.
- Treat penalties separately if the model does not represent them. Historical scenes require sourcing and clear approximation labels.
- Keep the v0.1 small: no accounts, database, unrelated statistics, or generic platform infrastructure.
- Make drag usable with mouse and touch and offer a keyboard or equivalent accessible control.

## Documentation language

- Write every repository Markdown file in English, including Issues-derived plans copied into Markdown, ADRs, README, prompts, and PR templates. Do not add Portuguese prose to any `.md` file.
- Keep the bilingual product interface in locale resources (`pt-BR` and `en`); the English-only Markdown rule does not restrict translations shown to users.
- `npm run check:precommit` includes the Markdown language check; still review short passages manually before publishing a PR. CI runs the same canonical pre-commit checks on pushes and PRs.

Never commit credentials or private user data.

<!-- BEGIN:nextjs-agent-rules -->

# This is NOT the Next.js you know

This version has breaking changes — APIs, conventions, and file structure may all differ from your training data. Read the relevant guide in `node_modules/next/dist/docs/` (resolved from this file's directory; in monorepos the `next` package may not be visible from the repo root) before writing any code. Heed deprecation notices.

This block is written and re-added by `next dev` — verify at `node_modules/next/dist/server/lib/generate-agent-files.js`. Removing it from a diff only re-creates the uncommitted change; committing it with your work keeps the tree clean.

<!-- END:nextjs-agent-rules -->
