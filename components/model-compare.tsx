"use client";

import { useMemo, useRef, useState, type KeyboardEvent, type PointerEvent } from "react";

import { monotonicArtifactId } from "@/lib/dev-compare";
import { extractScenarioFeatures, featureNames } from "@/lib/features";
import { fromSvg, toSvg, viewBox } from "@/lib/geometry";
import { probabilityLabels } from "@/lib/insights";
import { loadModel } from "@/lib/model";
import { predictScenario, type PredictionResult } from "@/lib/predict";
import { getPreset, isPresetId, presetIds } from "@/lib/presets";
import { initialScene } from "@/lib/scenario-session";
import { loadSelectedModel, selectedArtifactId } from "@/lib/selected-model";
import dictionary from "@/locales/en.json";
import {
  FIELD,
  addPlayer,
  defenderCount,
  goalPosts,
  maxExtraPlayers,
  maxRepresentedDefenders,
  movePlayer,
  playerPosition,
  removePlayer,
  representedPlayerIds,
  type PlayerId,
  type Scenario,
} from "@/lib/scenario";

const copy = dictionary.playground;

type Props = {
  currentText: string;
  candidateText: string;
};

export function nudgePlayer(
  scenario: Scenario,
  id: PlayerId,
  key: string,
  shift: boolean,
): Scenario | null {
  const direction = {
    ArrowUp: ["x", 1],
    ArrowDown: ["x", -1],
    ArrowLeft: ["y", -1],
    ArrowRight: ["y", 1],
  } as const;
  const movement = direction[key as keyof typeof direction];
  if (!movement) return null;
  const position = playerPosition(scenario, id);
  const step = shift ? 5 : 0.5;
  return movePlayer(scenario, id, {
    ...position,
    [movement[0]]: position[movement[0]] + movement[1] * step,
  });
}

function readout(result: PredictionResult) {
  if (result.status !== "ok") return null;
  return probabilityLabels(result.probability, "en");
}

export function ModelCompare({ currentText, candidateText }: Props) {
  const current = useMemo(
    () => loadSelectedModel(JSON.parse(currentText)),
    [currentText],
  );
  const candidate = useMemo(() => loadModel(JSON.parse(candidateText)), [candidateText]);
  const [scene, setScene] = useState(initialScene);
  const [selected, setSelected] = useState<PlayerId>("shooter");
  const svgRef = useRef<SVGSVGElement>(null);
  const dragging = useRef<{ id: PlayerId; pointerId: number } | null>(null);
  const format = new Intl.NumberFormat("en", { maximumFractionDigits: 1 });
  const postSvg = goalPosts.map(toSvg);
  const currentModel = current.status === "ready" ? current.model : undefined;
  const candidateModel = candidate.status === "ready" ? candidate.model : undefined;
  const candidateMatches =
    candidateModel?.artifactId === monotonicArtifactId &&
    candidateModel.modelVersion === "full_monotonic_xgboost";
  const currentResult = predictScenario(scene.scenario, currentModel);
  const candidateResult = candidateMatches
    ? predictScenario(scene.scenario, candidateModel)
    : ({ status: "unavailable", reason: "invalid_model" } as const);
  const shooter = scene.scenario.players.shooter;
  const shooterSvg = toSvg(shooter);
  const allPlayerIds = representedPlayerIds(scene.scenario);
  const selectedId = allPlayerIds.includes(selected) ? selected : "shooter";
  const selectedPosition = playerPosition(scene.scenario, selectedId);
  const features = extractScenarioFeatures(scene.scenario);

  function playerName(id: PlayerId) {
    return id.startsWith("attacker-")
      ? `${copy.players.shooter} ${Number(id.slice(9)) + 2}`
      : id.startsWith("defender-")
        ? `${copy.defenderName} ${Number(id.slice(9)) + 3}`
        : copy.players[id as keyof typeof copy.players];
  }

  function moveAt(id: PlayerId, event: PointerEvent<SVGGElement>) {
    const matrix = svgRef.current?.getScreenCTM();
    if (!matrix) return;
    const point = new DOMPoint(event.clientX, event.clientY).matrixTransform(matrix.inverse());
    setScene((previous) => ({
      ...previous,
      scenario: movePlayer(previous.scenario, id, fromSvg(point)),
    }));
  }

  function startDrag(id: PlayerId, event: PointerEvent<SVGGElement>) {
    if (dragging.current !== null) return;
    event.preventDefault();
    event.currentTarget.setPointerCapture(event.pointerId);
    dragging.current = { id, pointerId: event.pointerId };
    setSelected(id);
    moveAt(id, event);
  }

  function continueDrag(event: PointerEvent<SVGGElement>) {
    if (dragging.current?.pointerId === event.pointerId) moveAt(dragging.current.id, event);
  }

  function stopDrag(event: PointerEvent<SVGGElement>) {
    if (dragging.current?.pointerId === event.pointerId) dragging.current = null;
  }

  function onKey(id: PlayerId, event: KeyboardEvent<SVGGElement>) {
    const next = nudgePlayer(scene.scenario, id, event.key, event.shiftKey);
    if (!next || dragging.current) return;
    event.preventDefault();
    setSelected(id);
    setScene((previous) => ({ ...previous, scenario: next }));
  }

  return (
    <main className="playground">
      <header className="playground-copy">
        <p className="eyebrow">Local comparison</p>
        <h1>Current and monotonic models</h1>
        <p className="lead">
          One scene feeds both estimates. Drag a player, or focus a player and
          use the arrow keys. This page does not publish either model.
        </p>
      </header>
      <div className="compare-readouts">
        <Estimate
          title="Current XGBoost"
          testId="compare-current"
          artifactId={currentModel?.artifactId ?? selectedArtifactId}
          expected={selectedArtifactId}
          result={currentResult}
          ready={current.status === "ready"}
        />
        <Estimate
          title="Monotonic XGBoost"
          testId="compare-candidate"
          artifactId={candidateMatches ? monotonicArtifactId : "unavailable"}
          expected={monotonicArtifactId}
          result={candidateResult}
          ready={candidateMatches}
        />
      </div>
      <div className="pitch-workspace">
        <div className="pitch-editor">
          <div className="scene-actions">
            <label htmlFor="compare-preset">{copy.presetLabel}</label>
            <div className="preset-row">
              <select
                id="compare-preset"
                value={scene.presetId}
                onChange={(event) => {
                  const presetId = event.target.value;
                  if (!isPresetId(presetId)) return;
                  setScene({ presetId, scenario: getPreset(presetId) });
                  setSelected("shooter");
                }}
              >
                {presetIds.map((id) => (
                  <option key={id} value={id}>
                    {copy.presets[id]}
                  </option>
                ))}
              </select>
            </div>
          </div>
          <div className="pitch-surface">
            <svg
              ref={svgRef}
              className="pitch-svg"
              viewBox={`0 0 ${viewBox.width} ${viewBox.height}`}
              role="group"
              aria-label={copy.pitchDescription}
            >
              <rect className="field-outline" x="0.2" y="0.2" width="67.6" height="52.1" />
              <line className="field-line" x1="0.2" y1="52.3" x2="67.8" y2="52.3" />
              <rect className="field-line" x="13.84" y="0.2" width="40.32" height="16.5" />
              <rect className="field-line" x="24.84" y="0.2" width="18.32" height="5.5" />
              <circle className="field-spot" cx="34" cy="11" r="0.32" />
              <rect className="goal-mark" x={postSvg[0].x} y="0.25" width="7.32" height="1.2" />
              <polygon
                className="shot-cone"
                points={`${shooterSvg.x},${shooterSvg.y} ${postSvg[0].x},${postSvg[0].y} ${postSvg[1].x},${postSvg[1].y}`}
              />
              {allPlayerIds.map((id) => {
                const position = playerPosition(scene.scenario, id);
                const point = toSvg(position);
                const role =
                  id === "shooter" || id.startsWith("attacker-")
                    ? "attacker"
                    : id === "goalkeeper"
                      ? "goalkeeper"
                      : "defender";
                const name = playerName(id);
                return (
                  <g
                    key={id}
                    className={`pitch-player pitch-player--${role} ${selectedId === id ? "is-selected" : ""}`}
                    transform={`translate(${point.x} ${point.y})`}
                    role="button"
                    tabIndex={0}
                    aria-label={`${name}: ${copy.forward} ${format.format(position.x)} ${copy.meters}, ${copy.sideways} ${format.format(position.y)} ${copy.meters}. ${copy.keyboardHint}`}
                    onFocus={() => setSelected(id)}
                    onKeyDown={(event) => onKey(id, event)}
                    onPointerDown={(event) => startDrag(id, event)}
                    onPointerMove={continueDrag}
                    onPointerUp={stopDrag}
                    onPointerCancel={stopDrag}
                    onLostPointerCapture={stopDrag}
                  >
                    {id === "goalkeeper" && <circle className="goalkeeper-ring" r="2.05" />}
                    <circle className="player-body" r={FIELD.markerRadius} />
                    <text className="player-position" textAnchor="middle" dominantBaseline="central">
                      {role === "attacker"
                        ? copy.playerGlyphs.shooter
                        : role === "goalkeeper"
                          ? copy.playerGlyphs.goalkeeper
                          : copy.playerGlyphs.defender1}
                    </text>
                  </g>
                );
              })}
            </svg>
          </div>
          <div className="player-actions">
            <button
              type="button"
              disabled={scene.scenario.extraAttackers.length >= maxExtraPlayers.attacker}
              onClick={() =>
                setScene((previous) => ({
                  ...previous,
                  scenario: addPlayer(previous.scenario, "attacker"),
                }))
              }
            >
              {copy.addAttacker}
            </button>
            <button
              type="button"
              disabled={defenderCount(scene.scenario) >= maxRepresentedDefenders}
              onClick={() =>
                setScene((previous) => ({
                  ...previous,
                  scenario: addPlayer(previous.scenario, "defender"),
                }))
              }
            >
              {copy.addDefender}
            </button>
            <button
              className="scene-reset"
              type="button"
              onClick={() =>
                setScene((previous) => ({
                  presetId: previous.presetId,
                  scenario: getPreset(previous.presetId),
                }))
              }
            >
              {copy.reset}
            </button>
          </div>
          <details className="position-adjustments">
            <summary>{copy.results.position}</summary>
            <fieldset className="position-controls">
              <legend>{copy.results.position}</legend>
              <label>
                {copy.results.selected}
                <select
                  value={selectedId}
                  onChange={(event) => setSelected(event.target.value as PlayerId)}
                >
                  {allPlayerIds.map((id) => (
                    <option key={id} value={id}>
                      {playerName(id)}
                    </option>
                  ))}
                </select>
              </label>
              {(["x", "y"] as const).map((axis) => (
                <label key={axis}>
                  {axis === "x" ? copy.forward : copy.sideways} ({copy.meters})
                  <input
                    type="number"
                    step="0.5"
                    value={Number(selectedPosition[axis].toFixed(2))}
                    onChange={(event) => {
                      const value = event.target.valueAsNumber;
                      if (!Number.isFinite(value)) return;
                      setScene((previous) => ({
                        ...previous,
                        scenario: movePlayer(previous.scenario, selectedId, {
                          ...playerPosition(previous.scenario, selectedId),
                          [axis]: value,
                        }),
                      }));
                    }}
                  />
                </label>
              ))}
              <button
                type="button"
                disabled={selectedId === "shooter" || selectedId === "goalkeeper"}
                onClick={() => {
                  dragging.current = null;
                  setScene((previous) => ({
                    ...previous,
                    scenario: removePlayer(previous.scenario, selectedId),
                  }));
                  setSelected("shooter");
                }}
              >
                {copy.results.remove}
              </button>
            </fieldset>
          </details>
        </div>
        <section className="features-section" aria-labelledby="compare-features-title">
          <h2 id="compare-features-title">{copy.results.modelFeatures}</h2>
          <div className="feature-cards">
            {featureNames.map((name) => {
              const value = features.status === "ok" ? features.features[name] : null;
              return (
                <article className="feature-card" key={name}>
                  <span className="feature-name">{copy.results.features[name]}</span>
                  <strong>{value === null ? "—" : format.format(value)}</strong>
                </article>
              );
            })}
          </div>
        </section>
      </div>
    </main>
  );
}

function Estimate({
  title,
  testId,
  artifactId,
  expected,
  result,
  ready,
}: {
  title: string;
  testId: string;
  artifactId: string;
  expected: string;
  result: PredictionResult;
  ready: boolean;
}) {
  const labels = readout(result);
  const penalty = result.status === "ok" && result.source === "penalty-convention";
  return (
    <section className="prediction-card" aria-label={title} data-testid={testId}>
      <div className="estimate-heading">
        <p className="eyebrow">{title}</p>
      </div>
      {labels && ready ? (
        <div className="prediction-value">
          <strong data-testid={`${testId}-xg`}>
            {labels.xg} <small>xG</small>
          </strong>
          <span>{labels.percent}</span>
        </div>
      ) : (
        <p role="status">{ready ? copy.results.unsupported : copy.results.unavailable}</p>
      )}
      <p className="model-kind" data-testid={`${testId}-artifact`}>
        Artifact {artifactId}
      </p>
      {artifactId !== expected && (
        <p role="status">Expected artifact {expected}.</p>
      )}
      {penalty && <p className="penalty-note">{copy.results.convention}</p>}
    </section>
  );
}
