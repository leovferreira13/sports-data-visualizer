# Development process

The Issue is the executable unit. The Project board, when available, displays priority and state; the roadmap gives milestone order.

## States

`unrefined` → `long-term` / `near-term` → `prioritized` → `pending spec` → `spec in progress` → `ready for dev` → `in progress` → `review/qa` → `ready to deploy` → `done`

`long-term` and `near-term` describe horizon rather than required consecutive steps. Who moves a card is defined under Roles and Status entry rules. `done` means merged and checked.

## Roles

- The owner decides scope and priority.
- The PM grooms tasks and moves them up to `pending spec`. The PM does not move a card past `pending spec`.
- Eng writes the tech spec and moves the task from `pending spec` through `review/qa`.
- QA validates while the card is in `review/qa` and moves the card to `ready to deploy` when the PR is merge-ready.

## Status entry rules

- `near-term`: the task should be implemented soon (roughly the same week). Scope may still be open.
- `prioritized`: only after grooming is complete. Scope is closed with the owner, including what is in and out of scope and any decision rules. Each acceptance criterion names its proof, such as a screenshot, URL, API JSON, SHA, or fixture id. Dependencies are registered as native GitHub "blocked by" relationships.
- `pending spec`: a prioritized task with no open blockers. The PM moves it here and notifies Eng.

## Grooming

1. Read the issue and the related docs.
2. Resolve divergences with the owner.
3. Split separate deliverables into their own issues.
4. Rewrite the issue with outcome, context, scope, out of scope, acceptance criteria that each name their proof, and references.
5. Register dependencies as native GitHub "blocked by" links.

## Automatic pull on merge

When a PR merges, the PM checks the issues it unblocked. Prioritized issues with no remaining blockers move to `pending spec`, and the PM notifies Eng. Issues that are not groomed are flagged to the owner for grooming. This is a PM check at merge time. Do not add a GitHub Action for it.

## Sync rule

Any future change to this workcycle must update this document.

## Issue contract

Use the task template: outcome, context, scope, acceptance criteria, validation, dependencies and references. Keep one observable result per Issue. Suggested labels: `area:ui`, `area:model`, `area:content`, `area:delivery`, plus `milestone:playable`, `milestone:xg`, or `milestone:publish`. A card cannot enter `prioritized` until its body matches the grooming rewrite above. The older "validation" field is not a second template for a prioritized issue.

## Delivery

1. `spec #N`: Eng writes the tech spec when the card is in `pending spec`. The assistant reads the Issue and repository, uses the shared `write-plan.md` prompt and publishes one canonical Implementation Plan comment. Feedback uses `revise-plan.md` and updates that comment. Eng moves the card from `pending spec` onward.
2. After Eng marks the card `ready for dev`, `dev #N` creates `agent/<number>-<short-name>` from `main`, follows `implement-task.md`, implements a bounded slice and checks it.
3. Open a PR ready for review (not as a draft) linked with `Closes #<number>`, including checks, documentation and remaining limits; move to `review/qa` when the PR exists.
4. `review PR #N` examines feedback on the same branch, follows `address-review.md` for automated findings, validates fixes and replies with evidence. Human choices remain open. QA validates in `review/qa` and moves the card to `ready to deploy` when the PR is merge-ready. The owner merges; then mark `done`.

These are chat-invoked workflows, not scheduled GitHub Actions. See [commands and learning protocol](COMMANDS.md). The prompts and output schemas live in `.github/codex/`. Project configuration is a separate manual Action.
