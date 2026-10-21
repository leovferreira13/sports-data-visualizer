# Work with the project through chat

These are conversational commands for the assistant, **not GitHub Actions triggers**. The owner can use natural language; these short forms simply remove ambiguity. One command targets one Issue or PR. Nothing scans the board on a timer.

| Say here | Work performed |
| --- | --- |
| `spec #N` | Read Issue, discussion, relevant docs/code and `.github/codex/prompts/write-plan.md`; publish one canonical `Implementation Plan` comment; report blockers. |
| `revise spec #N` | Read the current Plan and latest owner feedback; use `revise-plan.md`; update the same Plan comment and answer the feedback. |
| `dev #N` | Confirm the Issue is ready and Plan accepted; use `implement-task.md`; create `agent/N-short-name` from current `main`, implement, validate and open a PR ready for review (not as a draft). |
| `review PR #N` | Inspect the PR and all relevant review findings; use `address-review.md` for actionable automated threads; validate fixes, reply with evidence, leave unresolved decisions open. |

The assistant orchestrates GitHub reads and writes around each prompt. The prompts' references to `.agent-context.md` and `.review-agent/` describe **temporary task context** to prepare for an isolated agent run; these files are never committed. Instructions in the prompts forbidding GitHub writes apply to the isolated planning/implementation/review phase; publication happens outside that phase in this chat workflow. The same JSON schemas under `.github/codex/schemas/` can validate structured agent output when used.

The GitHub Project is the source of delivery state. Status order is `unrefined` → `long-term` / `near-term` → `prioritized` → `pending spec` → `spec in progress` → `ready for dev` → `in progress` → `review/qa` → `ready to deploy` → `done`. The owner decides scope and priority. The PM grooms tasks and moves them up to `pending spec`. The PM does not move a card past `pending spec`. A card enters `pending spec` only when it is prioritized and has no open blockers; the PM moves it to `pending spec` and notifies Eng. Eng writes the tech spec when the card is in `pending spec` and moves the task from `pending spec` through `review/qa`, including `spec in progress`, `ready for dev`, and `in progress`. QA validates while the card is in `review/qa` and moves the card to `ready to deploy` when the PR is merge-ready. The owner merges; then mark `done`. The assistant can prepare a Plan for a named Issue even when the card is earlier in the board, but must not imply approval and must not move the card. A missing or disputed Plan blocks `dev` until resolved.

## Learn while building

For each material technical decision, the assistant should explain **what the choice does in this app**, **how the relevant framework/browser feature works**, **why it fits the requirement**, and **its tradeoff**. Use a small concrete example from the current task. Before substantial implementation, explain the intended approach; after implementation, walk through key files and actual checks. Keep learning notes proportional to the task and distinguish existing behavior from a proposal. The owner can ask to go deeper at any point.

We will not create scheduled spec/dev/review Actions. The manually triggered Project configuration workflow is separate from task execution.
