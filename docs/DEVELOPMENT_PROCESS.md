# Development process

The Issue is the executable unit. The Project board, when available, displays priority and state; the roadmap gives milestone order.

## States

`unrefined` → `long-term` / `near-term` → `prioritized` → `pending spec` → `spec ready` → `ready for dev` → `in progress` → `review/qa` → `ready to deploy` → `done`

`long-term` and `near-term` describe horizon rather than required consecutive steps. The owner controls prioritization, spec approval, readiness for development, release readiness, and merge. `done` means merged and checked.

## Issue contract

Use the task template: outcome, context, scope, acceptance criteria, validation, dependencies and references. Keep one observable result per Issue. Suggested labels: `area:ui`, `area:model`, `area:content`, `area:delivery`, plus `milestone:playable`, `milestone:xg`, or `milestone:publish`.

## Delivery

1. The owner asks for `spec #N` here. The assistant reads the Issue and repository, uses the shared `write-plan.md` prompt and publishes one canonical Implementation Plan comment. Feedback uses `revise-plan.md` and updates that comment.
2. After the owner accepts the Plan and marks the card `ready for dev`, `dev #N` creates `agent/<number>-<short-name>` from `main`, follows `implement-task.md`, implements a bounded slice and checks it.
3. Open a draft PR linked with `Closes #<number>`, including checks, documentation and remaining limits; move to `review/qa` when the PR exists.
4. `review PR #N` examines feedback on the same branch, follows `address-review.md` for automated findings, validates fixes and replies with evidence. Human choices remain open. The owner controls `ready to deploy` and merge; then mark `done`.

These are chat-invoked workflows, not scheduled GitHub Actions. See [commands and learning protocol](COMMANDS.md). The prompts and output schemas live in `.github/codex/`. Project configuration is a separate manual Action.
