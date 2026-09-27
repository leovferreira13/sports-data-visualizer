"""Football, Visualized — architecture overview (documentation, not runtime code).

Status: the bilingual shell and first playable pitch are implemented; prediction
and guided Learn remain planned.

The first product is a public xG playground with an optional Learn mode. Next.js
(App Router) supplies pages and locale routes. A React Client Component owns the
interactive scenario, and TypeScript describes its shape. SVG draws the attacking
half; Pointer Events move preset players and added players on mouse and touch. Focusable player markers
accept arrow keys as a keyboard-operable alternative.

The intended data flow is:

    pointer, keyboard or preset -> scenario state -> metric geometry
    -> SVG drawing and distance/angle labels

The later prediction path will extend geometry with model features and a
validated, versioned model. There is no inference or xG value today.

The field uses one coordinate system in meters, with x increasing toward the
attacked goal. A uniform SVG projection rotates the attacking half so the goal
is at the top. SVG coordinates are not the source of truth. Six presets and a
versioned, validated tab-scoped scenario snapshot, including added players, support reset and locale
navigation. The planned Learn mode will reuse this simulation.

Prediction is planned to run in the browser with a small versioned artifact.
This is conditional on finding or training a suitable model: its features must
match the controls and its use rights must be clear. Do not display a number as
xG until that proof is complete. A build-time Python script may train/export a
model, but is not a runtime dependency. There is no planned authentication,
database, or inference API for v0.1.

Locale routes /br and /en are implemented under app/[locale] with /br mapped to the
pt-BR locale and matching server-loaded dictionaries. The root route chooses
the saved cookie preference, then browser language, then en. The selector
retains the rest of the URL; scene state stays in client memory during locale
navigation and in sessionStorage across reloads, independent of the language cookie.

Read reference/ for planned and implemented module responsibilities and adr/ for
consequential decisions. Update these files as implementation settles. Never
describe a proposed component as if it already exists.
"""
