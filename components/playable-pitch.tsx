"use client";

import { useRef, useState, useSyncExternalStore, type KeyboardEvent, type PointerEvent } from "react";

import { fromSvg, shotAngle, shotDistance, toSvg, viewBox } from "@/lib/geometry";
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
  playerIds,
  playerPosition,
  type PlayerId,
} from "@/lib/scenario";

type PlaygroundCopy = Dictionary["playground"];
type Props = { locale: Locale; copy: PlaygroundCopy };

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
  return () => { sceneListeners.delete(listener); };
}

function getScene() {
  currentScene ??= storageRead() ?? initialScene();
  return currentScene;
}

function getServerScene() {
  return null;
}

function changeScene(update: (previous: ReturnType<typeof initialScene>) => ReturnType<typeof initialScene>) {
  currentScene = update(getScene());
  storageWrite(currentScene);
  sceneListeners.forEach((listener) => listener());
}

export function PlayablePitch({ locale, copy }: Props) {
  const scene = useSyncExternalStore(subscribeToScene, getScene, getServerScene);
  const [selected, setSelected] = useState<PlayerId>("shooter");
  const svgRef = useRef<SVGSVGElement>(null);
  const dragging = useRef<{ id: PlayerId; pointerId: number } | null>(null);

  const format = new Intl.NumberFormat(locale, { maximumFractionDigits: 1 });
  const postSvg = goalPosts.map(toSvg);

  function moveAt(id: PlayerId, event: PointerEvent<SVGGElement>) {
    const svg = svgRef.current;
    const matrix = svg?.getScreenCTM();
    if (!matrix) return;
    const point = new DOMPoint(event.clientX, event.clientY).matrixTransform(matrix.inverse());
    changeScene((previous) => ({
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
    if (dragging.current?.pointerId === event.pointerId) {
      moveAt(dragging.current.id, event);
    }
  }

  function stopDrag(event: PointerEvent<SVGGElement>) {
    if (dragging.current?.pointerId === event.pointerId) dragging.current = null;
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
      ArrowUp: ["x", 1], ArrowDown: ["x", -1],
      ArrowLeft: ["y", -1], ArrowRight: ["y", 1],
    } as const;
    const movement = direction[event.key as keyof typeof direction];
    if (!movement) return;
    event.preventDefault();
    updateAxis(id, movement[0], movement[1] * (event.shiftKey ? 5 : 0.5));
  }

  if (!scene) {
    return <div className="pitch-workspace pitch-workspace--loading" aria-busy="true" />;
  }

  const shooter = scene.scenario.players.shooter;
  const shooterSvg = toSvg(shooter);
  const allPlayerIds: PlayerId[] = [
    ...playerIds,
    ...scene.scenario.extraAttackers.map((_, index) => `attacker-${index}` as const),
    ...scene.scenario.extraDefenders.map((_, index) => `defender-${index}` as const),
  ];

  return (
    <div className="pitch-workspace">
      <div className="measurements" aria-live="off">
        <div><span>{copy.distance}</span><strong>{format.format(shotDistance(shooter))} {copy.meters}</strong></div>
        <div><span>{copy.angle}</span><strong>{format.format(shotAngle(shooter))}°</strong></div>
      </div>
      <div className="scene-actions">
        <label htmlFor="scene-preset">{copy.presetLabel}</label>
        <div className="preset-row">
          <select
            id="scene-preset"
            value={scene.presetId}
            onChange={(event) => {
              const presetId = event.target.value;
              if (!isPresetId(presetId)) return;
              changeScene(() => ({ presetId, scenario: getPreset(presetId) }));
              setSelected("shooter");
            }}
          >
            {presetIds.map((id) => <option key={id} value={id}>{copy.presets[id]}</option>)}
          </select>
          <button type="button" disabled={scene.scenario.extraAttackers.length >= maxExtraPlayers.attacker}
            onClick={() => changeScene((previous) => ({ ...previous, scenario: addPlayer(previous.scenario, "attacker") }))}>
            {copy.addAttacker}
          </button>
          <button type="button" disabled={scene.scenario.extraDefenders.length >= maxExtraPlayers.defender}
            onClick={() => changeScene((previous) => ({ ...previous, scenario: addPlayer(previous.scenario, "defender") }))}>
            {copy.addDefender}
          </button>
          <button className="scene-reset" type="button" onClick={() => {
            changeScene((previous) => ({ ...previous, scenario: getPreset(previous.presetId) }));
            setSelected("shooter");
          }}>
            {copy.reset}
          </button>
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
            const role = id === "shooter" || id.startsWith("attacker-") ? "attacker" : id === "goalkeeper" ? "goalkeeper" : "defender";
            const name = id.startsWith("attacker-") ? `${copy.players.shooter} ${Number(id.slice(9)) + 2}`
              : id.startsWith("defender-") ? `${copy.defenderName} ${Number(id.slice(9)) + 3}`
                : copy.players[id as (typeof playerIds)[number]];
            return (
              <g
                key={id}
                className={`pitch-player pitch-player--${role} ${selected === id ? "is-selected" : ""}`}
                transform={`translate(${point.x} ${point.y})`}
                role="button"
                tabIndex={0}
                aria-label={`${name}: ${copy.forward} ${format.format(position.x)} ${copy.meters}, ${copy.sideways} ${format.format(position.y)} ${copy.meters}. ${copy.keyboardHint}`}
                onFocus={() => setSelected(id)}
                onKeyDown={(event) => moveWithKeyboard(id, event)}
                onPointerDown={(event) => startDrag(id, event)}
                onPointerMove={continueDrag}
                onPointerUp={stopDrag}
                onPointerCancel={stopDrag}
                onLostPointerCapture={stopDrag}
              >
                <circle className="player-hit" r="4.5" />
                {id === "goalkeeper" && <circle className="goalkeeper-ring" r="2.05" />}
                <circle className="player-body" r={FIELD.markerRadius} />
                <text className="player-position" textAnchor="middle" dominantBaseline="central">
                  {role === "attacker" ? copy.playerGlyphs.shooter : role === "goalkeeper" ? copy.playerGlyphs.goalkeeper : copy.playerGlyphs.defender1}
                </text>
              </g>
            );
          })}
        </svg>
      </div>
    </div>
  );
}
