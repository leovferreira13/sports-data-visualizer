"use client";

import { useEffect, useSyncExternalStore } from "react";
import type { ModelLoadResult } from "./model";
import { loadSelectedModelBytes, selectedModelUrl } from "./selected-model";

type State = { status: "loading" } | ModelLoadResult;
const loading: State = { status: "loading" };
let current: State = loading;
let request: Promise<void> | null = null;
const listeners = new Set<() => void>();
function subscribe(listener: () => void) {
  listeners.add(listener);
  return () => {
    listeners.delete(listener);
  };
}
function snapshot() {
  return current;
}
function serverSnapshot() {
  return loading;
}

export function initializeSelectedModel(): Promise<void> {
  request ??= (async () => {
    try {
      const response = await fetch(selectedModelUrl);
      if (!response.ok) throw new Error("Model asset unavailable");
      current = await loadSelectedModelBytes(await response.arrayBuffer());
    } catch {
      current = { status: "invalid", reason: "artifact_contract" };
    }
    listeners.forEach((listener) => listener());
  })();
  return request;
}

export function useSelectedModel() {
  const state = useSyncExternalStore(subscribe, snapshot, serverSnapshot);
  useEffect(() => {
    void initializeSelectedModel();
  }, []);
  return state;
}
