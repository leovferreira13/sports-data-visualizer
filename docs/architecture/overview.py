"""Football, Visualized — architecture overview (documentation, not runtime code).

Status: planned architecture; no application modules have been implemented yet.

The first product is a public xG playground with an optional Learn mode. Next.js
(App Router) supplies pages and locale routes, React keeps the interactive view
in sync with scenario state, and TypeScript describes that state and catches
invalid data shapes during development. An SVG draws the half-pitch and its
individually movable pieces. Pointer Events unify mouse, pen, and touch.

The intended data flow is:

    pointer movement or preset -> scenario state -> geometry/features
    -> versioned model -> prediction -> explanation and drawings

The field uses one coordinate system in meters. SVG screen coordinates are a
projection of that system, not the model's source of truth. The Learn mode uses
the same simulation, prediction, and state as Playground.

Prediction is planned to run in the browser with a small versioned artifact.
This is conditional on finding or training a suitable model: its features must
match the controls and its use rights must be clear. Do not display a number as
xG until that proof is complete. A build-time Python script may train/export a
model, but is not a runtime dependency. There is no planned authentication,
database, or inference API for v0.1.

Locale routes /pt-BR and /en use matching dictionaries. The home route chooses
the saved preference or browser language. Switching locales keeps the scene.
Shareable scene URLs are deferred until their scope is confirmed.

Read reference/ for planned module responsibilities and adr/ for consequential
decisions. Update these files as implementation settles. Never describe a
proposed component as if it already exists.
"""
