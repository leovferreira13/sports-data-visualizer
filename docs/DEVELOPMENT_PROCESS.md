# Development process

The Issue is the executable unit. The Project board, when available, displays priority and state; the roadmap gives milestone order.

## States

`Backlog` → `Ready to specify` → `Ready to build` → `In progress` → `Review` → `Done`

Move a task to `Ready to build` after its acceptance criteria and any material model or UX decision are clear. Small tasks may need only a concise Issue, without a separate plan comment. `Done` means merged and checked.

## Issue contract

Use the task template: outcome, context, scope, acceptance criteria, validation, dependencies and references. Keep one observable result per Issue. Suggested labels: `area:ui`, `area:model`, `area:content`, `area:delivery`, plus `milestone:playable`, `milestone:xg`, or `milestone:publish`.

## Delivery

1. Pick the highest priority `Ready to build` Issue and create `task/<number>-<short-name>` from `main`.
2. Implement the smallest useful slice; update tests and docs that explain changed behavior.
3. Open a draft PR linked with `Closes #<number>`, including checks and any remaining limitation.
4. Review on the same branch. Merge after review, then move to `Done`.

Do not add scheduled spec, implementation, or review agents until manual Issue → PR flow reveals a real bottleneck. This keeps the first release fast.
