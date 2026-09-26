# Pitch and geometry

**Status:** proposed; no application code yet.

`components/Pitch.tsx` is planned to draw a responsive half-pitch as SVG and handle Pointer Events for a shooter, goalkeeper and up to three defenders. `lib/geometry.ts` owns metric calculations, bounds and the screen-to-field transformation. `lib/presets.ts` supplies five starting situations. Exact file boundaries can change when implementation begins.

Use field coordinates in meters (proposed full pitch 105 × 68 m, goal 7.32 m wide). Increase `x` toward the attacked goal; `y` crosses the field. The visible half-pitch must not alter feature calculations. A `Scenario` holds shot position, goalkeeper, defender IDs/positions and an explicit `shotType` for open play versus penalty.

Distance is from shot to goal center; angle is the angle between vectors from shot to each post. The SVG cone, numerical values and model features must use the same geometry. Clamp drags to valid positions; provide an alternative to dragging for keyboard users. Moving a piece updates state first, then drawings and measurements derive from it.

**Learning note:** SVG is a collection of browser elements, so each player and geometry line can be addressed and styled separately. React rerenders those elements from state; Pointer Events provide one interaction API across mouse and touch. This does not imply that every SVG shape should be exposed to assistive technology.
