"use client";

import { useEffect, useRef, useState, type PointerEvent } from "react";

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
  FIELD,
  fieldBounds,
  goalPosts,
  movePlayer,
  playerIds,
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

export function PlayablePitch({ locale, copy }: Props) {
  const [scene, setScene] = useState(initialScene);
  const [selected, setSelected] = useState<PlayerId>("shooter");
  const [loaded, setLoaded] = useState(false);
  const svgRef = useRef<SVGSVGElement>(null);
  const dragging = useRef<{ id: PlayerId; pointerId: number } | null>(null);

  useEffect(() => {
    let active = true;
    queueMicrotask(() => {
      if (!active) return;
      setScene(storageRead() ?? initialScene());
      setLoaded(true);
    });
    return () => { active = false; };
  }, []);

  useEffect(() => {
    if (loaded) storageWrite(scene);
  }, [loaded, scene]);

  const format = new Intl.NumberFormat(locale, { maximumFractionDigits: 1 });
  const shooter = scene.scenario.players.shooter;
  const shooterSvg = toSvg(shooter);
  const postSvg = goalPosts.map(toSvg);
  const selectedPosition = scene.scenario.players[selected];

  function moveAt(id: PlayerId, event: PointerEvent<SVGGElement>) {
    const svg = svgRef.current;
    const matrix = svg?.getScreenCTM();
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
    if (dragging.current?.pointerId === event.pointerId) {
      moveAt(dragging.current.id, event);
    }
  }

  function stopDrag(event: PointerEvent<SVGGElement>) {
    if (dragging.current?.pointerId === event.pointerId) dragging.current = null;
  }

  function updateAxis(axis: "x" | "y", value: number) {
    setScene((previous) => ({
      ...previous,
      scenario: movePlayer(previous.scenario, selected, {
        ...previous.scenario.players[selected],
        [axis]: value,
      }),
    }));
  }

  return (
    <div className="pitch-workspace">
      <div className="pitch-surface">
        <svg
          ref={svgRef}
          className="pitch-svg"
          viewBox={`0 0 ${viewBox.width} ${viewBox.height}`}
          role="img"
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

          {playerIds.map((id) => {
            const point = toSvg(scene.scenario.players[id]);
            return (
              <g
                key={id}
                className={`pitch-player pitch-player--${id} ${selected === id ? "is-selected" : ""}`}
                transform={`translate(${point.x} ${point.y})`}
                onPointerDown={(event) => startDrag(id, event)}
                onPointerMove={continueDrag}
                onPointerUp={stopDrag}
                onPointerCancel={stopDrag}
                onLostPointerCapture={stopDrag}
              >
                <circle className="player-hit" r="4.5" />
                <circle className="player-body" r={FIELD.markerRadius} />
                <text className="player-initial" textAnchor="middle" dominantBaseline="central">
                  {copy.playerGlyphs[id]}
                </text>
              </g>
            );
          })}
        </svg>
      </div>

      <div className="pitch-dashboard">
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
                if (!isPresetId(event.target.value)) return;
                setScene({ presetId: event.target.value, scenario: getPreset(event.target.value) });
                setSelected("shooter");
              }}
            >
              {presetIds.map((id) => <option key={id} value={id}>{copy.presets[id]}</option>)}
            </select>
            <button
              type="button"
              onClick={() => setScene((previous) => ({
                ...previous,
                scenario: getPreset(previous.presetId),
              }))}
            >
              {copy.reset}
            </button>
          </div>
        </div>

        <fieldset className="position-controls">
          <legend>{copy.adjustPosition}</legend>
          <label htmlFor="selected-player">{copy.playerLabel}</label>
          <select
            id="selected-player"
            value={selected}
            onChange={(event) => setSelected(event.target.value as PlayerId)}
          >
            {playerIds.map((id) => <option key={id} value={id}>{copy.players[id]}</option>)}
          </select>
          <label htmlFor="player-forward">{copy.forward}: {format.format(selectedPosition.x)} {copy.meters}</label>
          <input
            id="player-forward"
            type="range"
            min={fieldBounds.xMin}
            max={fieldBounds.xMax}
            step="0.1"
            value={selectedPosition.x}
            onChange={(event) => updateAxis("x", Number(event.target.value))}
          />
          <label htmlFor="player-sideways">{copy.sideways}: {format.format(selectedPosition.y)} {copy.meters}</label>
          <input
            id="player-sideways"
            type="range"
            min={fieldBounds.yMin}
            max={fieldBounds.yMax}
            step="0.1"
            value={selectedPosition.y}
            onChange={(event) => updateAxis("y", Number(event.target.value))}
          />
        </fieldset>
      </div>
    </div>
  );
}
