"use client";

import {
  useEffect,
  useRef,
  useState,
  useSyncExternalStore,
  type KeyboardEvent,
  type PointerEvent,
} from "react";

import { PredictionPanel } from "./prediction-panel";
import { compareScenes, type Comparison } from "@/lib/insights";
import { predictScenario } from "@/lib/predict";
import { useSelectedModel } from "@/lib/model-store";
import {
  fromSvg,
  shotAngle,
  shotDistance,
  toSvg,
  viewBox,
} from "@/lib/geometry";
import type { Dictionary } from "@/lib/i18n/dictionaries";
import type { Locale } from "@/lib/i18n/config";
import { getPreset, isPresetId, presetIds } from "@/lib/presets";
import {
  initialScene,
  parseScene,
  scenarioSessionKey,
  serializeScene,
} from "@/lib/scenario-session";
import {
  addPlayer,
  FIELD,
  goalPosts,
  maxExtraPlayers,
  movePlayer,
  defenderCount,
  maxRepresentedDefenders,
  removePlayer,
  representedPlayerIds,
  type Scenario,
  playerPosition,
  type PlayerId,
} from "@/lib/scenario";

type PlaygroundCopy = Dictionary["playground"];
type Props = {
  locale: Locale;
  copy: PlaygroundCopy;
  presetSupport: Record<string, string>;
};

function storageRead() {
  try {
    return parseScene(window.sessionStorage.getItem(scenarioSessionKey));
  } catch {
    return null;
  }
}

function storageWrite(snapshot: ReturnType<typeof initialScene>) {
  try {
    window.sessionStorage.setItem(scenarioSessionKey, serializeScene(snapshot));
  } catch {
    // Browser settings may block storage; the current scene remains usable.
  }
}

// Keep the scene through locale-route remounts, while storage also survives reloads.
let currentScene: ReturnType<typeof initialScene> | null = null;
const sceneListeners = new Set<() => void>();

function subscribeToScene(listener: () => void) {
  sceneListeners.add(listener);
  return () => {
    sceneListeners.delete(listener);
  };
}

function getScene() {
  if (!currentScene) {
    currentScene = storageRead() ?? initialScene();
    if (currentScene.migratedDefenderLimit) storageWrite(currentScene);
  }
  return currentScene;
}

function getServerScene() {
  return null;
}

function changeScene(
  update: (
    previous: ReturnType<typeof initialScene>,
  ) => ReturnType<typeof initialScene>,
) {
  currentScene = update(getScene());
  delete currentScene.migratedDefenderLimit;
  storageWrite(currentScene);
  sceneListeners.forEach((listener) => listener());
}

export function PlayablePitch({ locale, copy, presetSupport }: Props) {
  const scene = useSyncExternalStore(
    subscribeToScene,
    getScene,
    getServerScene,
  );
  const [selected, setSelected] = useState<PlayerId>("shooter");
  const [comparison, setComparison] = useState<Comparison | null>(null);
  const before = useRef<Scenario | null>(null);
  const keyboardTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const controlsRef = useRef<HTMLSelectElement>(null);
  const svgRef = useRef<SVGSVGElement>(null);
  const dragging = useRef<{ id: PlayerId; pointerId: number } | null>(null);

  const format = new Intl.NumberFormat(locale, { maximumFractionDigits: 1 });
  const postSvg = goalPosts.map(toSvg);

  const selectedModel = useSelectedModel();
  const model =
    selectedModel.status === "ready" ? selectedModel.model : undefined;

  function finishComparison() {
    if (keyboardTimer.current) clearTimeout(keyboardTimer.current);
    keyboardTimer.current = null;
    if (!before.current) return;
    const after = getScene().scenario;
    setComparison(
      compareScenes(
        before.current,
        after,
        predictScenario(before.current, model),
        predictScenario(after, model),
      ),
    );
    before.current = null;
  }
  function beginComparison() {
    if (!before.current) {
      before.current = getScene().scenario;
      setComparison(null);
    }
  }
  function clearComparison() {
    if (keyboardTimer.current) clearTimeout(keyboardTimer.current);
    keyboardTimer.current = null;
    before.current = null;
    dragging.current = null;
    setComparison(null);
  }
  useEffect(
    () => () => {
      if (keyboardTimer.current) clearTimeout(keyboardTimer.current);
    },
    [],
  );

  function applyAction(action: (scenario: Scenario) => Scenario) {
    finishComparison();
    beginComparison();
    changeScene((previous) => ({
      ...previous,
      scenario: action(previous.scenario),
    }));
    finishComparison();
  }

  function playerName(id: PlayerId) {
    return id.startsWith("attacker-")
      ? `${copy.players.shooter} ${Number(id.slice(9)) + 2}`
      : id.startsWith("defender-")
        ? `${copy.defenderName} ${Number(id.slice(9)) + 3}`
        : copy.players[id as keyof typeof copy.players];
  }

  function moveAt(id: PlayerId, event: PointerEvent<SVGGElement>) {
    const svg = svgRef.current;
    const matrix = svg?.getScreenCTM();
    if (!matrix) return;
    const point = new DOMPoint(event.clientX, event.clientY).matrixTransform(
      matrix.inverse(),
    );
    changeScene((previous) => ({
      ...previous,
      scenario: movePlayer(previous.scenario, id, fromSvg(point)),
    }));
  }

  function startDrag(id: PlayerId, event: PointerEvent<SVGGElement>) {
    if (dragging.current !== null) return;
    event.preventDefault();
    finishComparison();
    beginComparison();
    event.currentTarget.setPointerCapture(event.pointerId);
    dragging.current = { id, pointerId: event.pointerId };
    setSelected(id);
    moveAt(id, event);
  }

  function continueDrag(event: PointerEvent<SVGGElement>) {
    if (dragging.current?.pointerId === event.pointerId) {
      moveAt(dragging.current.id, event);
    }
  }

  function stopDrag(event: PointerEvent<SVGGElement>) {
    if (dragging.current?.pointerId === event.pointerId) {
      dragging.current = null;
      finishComparison();
    }
  }

  function updateAxis(id: PlayerId, axis: "x" | "y", value: number) {
    changeScene((previous) => ({
      ...previous,
      scenario: movePlayer(previous.scenario, id, {
        ...playerPosition(previous.scenario, id),
        x: playerPosition(previous.scenario, id).x + (axis === "x" ? value : 0),
        y: playerPosition(previous.scenario, id).y + (axis === "y" ? value : 0),
      }),
    }));
  }

  function moveWithKeyboard(id: PlayerId, event: KeyboardEvent<SVGGElement>) {
    const direction = {
      ArrowUp: ["x", 1],
      ArrowDown: ["x", -1],
      ArrowLeft: ["y", -1],
      ArrowRight: ["y", 1],
    } as const;
    const movement = direction[event.key as keyof typeof direction];
    if (!movement) return;
    event.preventDefault();
    if (dragging.current) return;
    beginComparison();
    updateAxis(id, movement[0], movement[1] * (event.shiftKey ? 5 : 0.5));
    if (keyboardTimer.current) clearTimeout(keyboardTimer.current);
    keyboardTimer.current = setTimeout(finishComparison, 450);
  }

  if (!scene) {
    return (
      <div
        className="pitch-workspace pitch-workspace--loading"
        aria-busy="true"
      />
    );
  }

  const shooter = scene.scenario.players.shooter;
  const shooterSvg = toSvg(shooter);
  const allPlayerIds = representedPlayerIds(scene.scenario);
  const result = predictScenario(scene.scenario, model);
  const originalSupport =
    JSON.stringify(scene.scenario) === JSON.stringify(getPreset(scene.presetId))
      ? presetSupport[scene.presetId]
      : undefined;
  const selectedId = allPlayerIds.includes(selected) ? selected : "shooter";
  const selectedPosition = playerPosition(scene.scenario, selectedId);

  return (
    <div className="pitch-workspace">
      <div className="playground-insights">
        <PredictionPanel
          locale={locale}
          copy={copy.results}
          scenario={scene.scenario}
          result={result}
          loading={selectedModel.status === "loading"}
          comparison={comparison}
          originalSupport={originalSupport}
        />
        {scene.migratedDefenderLimit && (
          <p role="status" className="support-note">
            {copy.results.migration}
          </p>
        )}
        <div className="measurements" aria-live="off">
          <div>
            <span>{copy.distance}</span>
            <strong>
              {format.format(shotDistance(shooter))} {copy.meters}
            </strong>
          </div>
          <div>
            <span>{copy.angle}</span>
            <strong>{format.format(shotAngle(shooter))}°</strong>
          </div>
        </div>
      </div>
      <div className="pitch-editor">
        <div className="scene-actions">
          <label htmlFor="scene-preset">{copy.presetLabel}</label>
          <div className="preset-row">
            <select
              id="scene-preset"
              value={scene.presetId}
              onChange={(event) => {
                clearComparison();
                const presetId = event.target.value;
                if (!isPresetId(presetId)) return;
                changeScene(() => ({
                  presetId,
                  scenario: getPreset(presetId),
                }));
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
            <rect
              className="field-outline"
              x="0.2"
              y="0.2"
              width="67.6"
              height="52.1"
            />
            <line
              className="field-line"
              x1="0.2"
              y1="52.3"
              x2="67.8"
              y2="52.3"
            />
            <rect
              className="field-line"
              x="13.84"
              y="0.2"
              width="40.32"
              height="16.5"
            />
            <rect
              className="field-line"
              x="24.84"
              y="0.2"
              width="18.32"
              height="5.5"
            />
            <circle className="field-spot" cx="34" cy="11" r="0.32" />
            <rect
              className="goal-mark"
              x={postSvg[0].x}
              y="0.25"
              width="7.32"
              height="1.2"
            />

            <polygon
              className="shot-cone"
              points={`${shooterSvg.x},${shooterSvg.y} ${postSvg[0].x},${postSvg[0].y} ${postSvg[1].x},${postSvg[1].y}`}
            />
            {postSvg.map((post) => (
              <line
                key={post.x}
                className="cone-edge"
                x1={shooterSvg.x}
                y1={shooterSvg.y}
                x2={post.x}
                y2={post.y}
              />
            ))}

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
                  className={`pitch-player pitch-player--${role} ${selected === id ? "is-selected" : ""}`}
                  transform={`translate(${point.x} ${point.y})`}
                  role="button"
                  tabIndex={0}
                  aria-label={`${name}: ${copy.forward} ${format.format(position.x)} ${copy.meters}, ${copy.sideways} ${format.format(position.y)} ${copy.meters}. ${copy.keyboardHint}`}
                  onFocus={() => {
                    finishComparison();
                    setSelected(id);
                  }}
                  onBlur={finishComparison}
                  onKeyDown={(event) => moveWithKeyboard(id, event)}
                  onPointerDown={(event) => startDrag(id, event)}
                  onPointerMove={continueDrag}
                  onPointerUp={stopDrag}
                  onPointerCancel={stopDrag}
                  onLostPointerCapture={stopDrag}
                >
                  <circle className="player-hit" r="4.5" />
                  {id === "goalkeeper" && (
                    <circle className="goalkeeper-ring" r="2.05" />
                  )}
                  <circle className="player-body" r={FIELD.markerRadius} />
                  <text
                    className="player-position"
                    textAnchor="middle"
                    dominantBaseline="central"
                  >
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
            disabled={
              scene.scenario.extraAttackers.length >= maxExtraPlayers.attacker
            }
            onClick={() =>
              applyAction((scenario) => addPlayer(scenario, "attacker"))
            }
          >
            {copy.addAttacker}
          </button>
          <button
            type="button"
            disabled={defenderCount(scene.scenario) >= maxRepresentedDefenders}
            onClick={() =>
              applyAction((scenario) => addPlayer(scenario, "defender"))
            }
          >
            {copy.addDefender}
          </button>
          <button
            className="scene-reset"
            type="button"
            onClick={() => {
              clearComparison();
              changeScene((previous) => ({
                presetId: previous.presetId,
                scenario: getPreset(previous.presetId),
              }));
              setSelected("shooter");
            }}
          >
            {copy.reset}
          </button>
        </div>
        <fieldset className="position-controls">
          <legend>{copy.results.position}</legend>
          <label>
            {copy.results.selected}
            <select
              ref={controlsRef}
              value={selectedId}
              onChange={(event) => {
                finishComparison();
                setSelected(event.target.value as PlayerId);
              }}
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
                min={
                  axis === "x"
                    ? FIELD.halfLine + FIELD.markerRadius
                    : FIELD.markerRadius
                }
                max={
                  axis === "x"
                    ? FIELD.length - FIELD.markerRadius
                    : FIELD.width - FIELD.markerRadius
                }
                value={Number(selectedPosition[axis].toFixed(2))}
                onChange={(event) => {
                  const value = event.target.valueAsNumber;
                  if (Number.isFinite(value))
                    applyAction((scenario) =>
                      movePlayer(scenario, selectedId, {
                        ...playerPosition(scenario, selectedId),
                        [axis]: value,
                      }),
                    );
                }}
              />
            </label>
          ))}
          <button
            type="button"
            disabled={selectedId === "shooter" || selectedId === "goalkeeper"}
            onClick={() => {
              dragging.current = null;
              applyAction((scenario) => removePlayer(scenario, selectedId));
              setSelected("shooter");
              controlsRef.current?.focus();
            }}
          >
            {copy.results.remove}
          </button>
        </fieldset>
      </div>
    </div>
  );
}
