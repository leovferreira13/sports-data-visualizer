# Pitch and geometry

**Status:** first playable pitch implemented; prediction remains planned.

`lib/scenario.ts` defines a typed four-player `Scenario`, metric field constants, valid bounds, and immutable player movement. The full field is 105 × 68 m; the visible attacking half is x = 52.5–105 m, with x increasing toward the attacked goal and y spanning the width. Player centers stay at least one marker radius inside the playing area. The goal center is (105, 34), and its posts are 7.32 m apart. `shotType` marks a penalty without assigning it an estimate.

`lib/geometry.ts` owns distance to goal center, the angle between shooter-to-post vectors, and the reversible projection to SVG. The `68 × 52.5` viewBox rotates the field: lateral y maps to screen x; distance from the attacked goal maps to screen y. Both axes keep one SVG unit per meter. The goal is at the top, so the cone, post markers, and numerical measurements share the same physical geometry. Pointer coordinates pass through the inverse of `getScreenCTM()`, including the SVG's responsive scaling.

`lib/presets.ts` supplies six distinct four-piece scenarios. The default central chance places the striker on the field centerline, closer than in the long-shot preset, with two center-backs symmetrically between the striker and the goal. Selecting a preset creates a fresh copy, and reset restores that preset after edits. `components/playable-pitch.tsx` owns scene updates, SVG drawings, pointer capture, and measurements above the field. Pointer capture continues a drag outside the marker and clears on release/cancellation. Focusable player markers accept arrow keys, with Shift for larger steps. `app/[locale]/globals.css` styles the responsive pitch and distinct team colors; `locales/` supplies localized position codes and labels.

`lib/scenario-session.ts` validates a versioned tab snapshot for reloads. An in-memory scene store preserves positions across locale remounts, so the old default does not flash before the saved scene appears. Invalid, stale, or out-of-bounds snapshots fall back to the default central chance. There is no xG value, model feature extraction, URL scenario format, or third defender yet.

**Learning note:** SVG elements are individual DOM objects, so React can redraw the cone and pieces from scenario state. Pointer Events unify mouse and touch, while the browser's SVG matrix handles responsive coordinate conversion. State remains in meters; the browser projection never becomes a second source of positions.
