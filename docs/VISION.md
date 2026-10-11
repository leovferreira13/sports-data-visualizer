# Football, Visualized — product vision

**Status:** portfolio-focused first release · **First module:** Expected Goals (xG) · **Updated:** 2026-10-11

## One-sentence concept

An interactive football pitch where anyone can move the shooter, goalkeeper, and defenders to explore how a shot situation changes its estimated chance of becoming a goal.

## Problem and audience

xG often appears in broadcasts and analysis as a finished number. Fans struggle to see which characteristics of a chance influenced the estimate and why two seemingly similar chances receive different values. Analysts, journalists, and commentators also need to recreate a play and explain it quickly to an audience.

The visitor experience serves a curious football fan without requiring statistical background, an account or preparatory reading. The owner's primary delivery goal is a professional portfolio: recruiters and technical reviewers should be able to explore a complete product and trace its data, ML, browser-inference and product decisions. Broad adoption and maximum predictive accuracy are not first-release goals.

## Proposition

**Playground is the default screen.** Visitors find a prepared chance, a prominent xG estimate, and a short prompt: “Drag the players to try another situation.” They can change presets, move pieces, and see which observable factors changed. An unobtrusive **Learn** control opens an interactive explanation on the same pitch rather than sending them to a theory page.

Working name: **Football, Visualized**. Product message: **Move the players. Understand what changes a goal-scoring chance.** The name does not require building a broader portal in the first release.

## Core experience

1. Open the site in a language suggested by the browser: Brazilian Portuguese or English. A top-level selector can change it at any time.
2. See an initial scene with a shooter, goalkeeper, two defenders, goal, estimate, and brief contextual sentence.
3. Drag a player; the pitch, measurements, and estimate respond during or immediately after movement.
4. Choose and edit a preset: **Penalty, One-on-one, Tight angle, Long shot, Crowded box**.
5. Switch to **Learn** for small experiments, such as moving a defender out of the shooting lane and seeing what changed.
6. Copy a scenario link for someone else if sharing fits the first release; at minimum, presets must be reproducible.

The panel shows **distance**, **shooting angle**, and **opponent/goalkeeper positioning**. Its explanation must distinguish geometric observations (“a defender is inside the shooting cone”) from model effects (“removing this defender raised this model's estimate by 0.04”). Never imply that a movement guarantees a goal.

## Two modes, one simulation

| Mode | Purpose | Behavior |
| --- | --- | --- |
| **Playground — default** | Build and demonstrate chances freely | Editable pitch, presets, estimate, measurements, and concise explanations. |
| **Learn** | Understand xG by experimenting | Short optional steps suggest a pitch change, show before/after values, then return free control. |

Learn uses the same rules, calculation, and controls as Playground. Visitors can leave without losing the scene they built.

## Product principles

- **Show before explaining:** the usable pitch appears without mandatory onboarding.
- **Put the number in context:** identify the model, its inputs, and omissions. “0.20 xG” means roughly 20 goals in 100 comparable shots according to that model; it is not the scoring probability of a specific player.
- **Explain honestly:** changes in the estimate are comparisons within the model, not causal claims about real football. Do not describe a visible factor as a model input if it is not one.
- **Make demonstrations easy:** quick reading, a generous pitch area, fluid movement, and good presentation on mobile and desktop.
- **Permit illustrative exploration:** rare/extreme but valid scenes are intentional. Support diagnostics inform concise explanations, not automatic blocking. Avoid precision or causal promises and explain that tree predictions can remain unchanged after small movements.
- **Expose the decisions:** a visible adjacent Methodology and results tab shares the report's aggregate evidence, separates validation from test and links architecture/ADRs/reproduction for reviewers.
- **Ship a small, complete product:** the first release is an xG module, not a scouting portal.
- **Support both languages from the start:** UI, explanations, and model limitations in `pt-BR` and `en`.

## What success looks like

**Product goal:** someone new to xG can build a chance and explain in their own words why the model evaluated it that way. **Delivery goal:** a public URL and repository usable as a portfolio piece.

Use a small targeted qualitative review to check whether a newcomer can interact without verbal instruction and explain a model response, and whether a technical reader can follow the implementation rationale. Invite a football-interested reader or technical peer if available. Record available feedback and useful follow-ups; a fixed participant quota, traffic target or analytics installation is not a release gate.

## First-release boundaries

One designated shot taker, one goalkeeper, addable attackers and defenders, six presets, two modes, and two languages. No accounts, database, mandatory backend, teams, live matches, tactical editor, other metrics, or generative AI. Famous goals come **after validation**: recreating one requires a reliable source for positions and shot context, and any approximation must be labeled as an illustrative reconstruction.

## Possible evolution

If this module works, the brand can hold independent experiments: famous goals, xA, xThreat, or other visualizations. Add a module based on use and learning from the first one, not on architecture built prematurely for several products.

## Current model and delivery handoff

The frozen shallow XGBoost has accepted actual-corpus scientific evidence with support/transfer limitations. Use it for the educational v0.1 instead of requiring another optimization cycle. #4 integrates inference, proportional support explanations and mandatory methodology/results; #5 adds optional Learn and the shareable portfolio release. #4 may start before #3/#8 close. Actual parameter/export, rights/history and integrated product attribution/assets QA must finish before public distribution. The owner controls publication and board/merge state.
