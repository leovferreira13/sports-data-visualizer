# Development process

The Issue is the executable unit. The Project board, when available, displays priority and state; the roadmap gives milestone order.

## States

`unrefined` → `long-term` / `near-term` → `prioritized` → `pending spec` → `spec ready` → `ready for dev` → `in progress` → `review/qa` → `ready to deploy` → `done`

`long-term` and `near-term` describe horizon rather than required consecutive steps. Move a task to `ready for dev` after its acceptance criteria and any material model or UX decision are clear. Small tasks may need only a concise Issue, without a separate plan comment. `done` means merged and checked. The owner controls prioritization, readiness, and merge.

## Issue contract

Use the task template: outcome, context, scope, acceptance criteria, validation, dependencies and references. Keep one observable result per Issue. Suggested labels: `area:ui`, `area:model`, `area:content`, `area:delivery`, plus `milestone:playable`, `milestone:xg`, or `milestone:publish`.

## Delivery

1. Pick the highest priority `ready for dev` Issue and create `task/<number>-<short-name>` from `main`.
2. Implement the smallest useful slice; update tests and docs that explain changed behavior.
3. Open a draft PR linked with `Closes #<number>`, including checks and any remaining limitation.
4. Review on the same branch. Merge after review, then move to `Done`.

Do not add scheduled spec, implementation, or review agents until manual Issue → PR flow reveals a real bottleneck. This keeps the first release fast.
