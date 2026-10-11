import schema from "../model/model-artifact.schema.json";
import inference from "../model/inference-contract.json";
import { featureContract, featureNames } from "./features";
import { FIELD } from "./scenario";

export type ModelVersion = "geometry_logistic" | "defenders_logistic" | "full_logistic" | "full_xgboost";
type Node = { leaf: number } | { feature: number; threshold: number; left: number; right: number };
type Envelope = {
  artifact_id: string; model_version: ModelVersion; contract_version: string;
  feature_indices: number[]; export_tolerance: number;
  parameters: { kind: "logistic"; mean: number[]; scale: number[]; coefficients: number[]; intercept: number }
    | { kind: "xgboost"; base_margin: number; trees: Node[][] };
  calibration: { method: "identity" } | { method: "sigmoid"; slope: number; intercept: number; clip: number };
};
export type ValidatedModel = Readonly<{
  artifactId: string; modelVersion: ModelVersion; contractVersion: string;
  usedFeatures: readonly string[]; tolerance: number;
}>;
export type ModelLoadResult = { status: "ready"; model: ValidatedModel }
  | { status: "invalid"; reason: "artifact_schema" | "artifact_contract" | "artifact_parameters" };

// Only loader-created handles can execute; callers cannot mutate or forge the captured parameters.
const envelopes = new WeakMap<ValidatedModel, Envelope>();
type Schema = {
  const?: unknown; enum?: unknown[]; oneOf?: Schema[]; type?: string;
  properties?: Record<string, Schema>; required?: string[]; additionalProperties?: boolean | Schema;
  items?: Schema; minItems?: number; maxItems?: number; uniqueItems?: boolean;
  pattern?: string; minimum?: number; maximum?: number; exclusiveMinimum?: number;
};
function object(v: unknown): v is Record<string, unknown> {
  return typeof v === "object" && v !== null && !Array.isArray(v)
    && Object.getPrototypeOf(v) === Object.prototype;
}
function finiteJson(v: unknown, seen = new WeakSet<object>(), depth = 0, budget = { left: 30000 }): boolean {
  if (--budget.left < 0 || depth > 16) return false;
  if (typeof v === "number") return Number.isFinite(v);
  if (v === null || typeof v === "boolean" || typeof v === "string") return true;
  if (!Array.isArray(v) && !object(v)) return false;
  if (seen.has(v)) return false;
  seen.add(v);
  const values = Array.isArray(v) ? v : Object.values(v);
  const valid = values.every(x => finiteJson(x, seen, depth + 1, budget));
  seen.delete(v);
  return valid;
}

// Implements only the keywords used by the committed envelope schema, with finite JSON checked first.
function matches(v: unknown, s: Schema): boolean {
  if ("const" in s && v !== s.const) return false;
  if (s.enum && !s.enum.includes(v)) return false;
  if (s.oneOf && s.oneOf.filter(branch => matches(v, branch)).length !== 1) return false;
  if (s.type === "object") {
    if (!object(v) || s.required?.some(k => !Object.hasOwn(v, k))) return false;
    const properties = s.properties ?? {};
    return Object.entries(v).every(([k, value]) => Object.hasOwn(properties, k)
      ? matches(value, properties[k]) : s.additionalProperties === false ? false
        : typeof s.additionalProperties === "object" ? matches(value, s.additionalProperties) : true);
  }
  if (s.type === "array") {
    if (!Array.isArray(v) || v.length < (s.minItems ?? 0) || v.length > (s.maxItems ?? Infinity)) return false;
    if (s.uniqueItems && new Set(v).size !== v.length) return false;
    return !s.items || v.every(item => matches(item, s.items!));
  }
  if (s.type === "string") return typeof v === "string" && (!s.pattern || new RegExp(s.pattern).test(v));
  if (s.type === "number" || s.type === "integer") return typeof v === "number" && Number.isFinite(v)
    && (s.type !== "integer" || Number.isInteger(v)) && v >= (s.minimum ?? -Infinity)
    && v <= (s.maximum ?? Infinity) && (s.exclusiveMinimum === undefined || v > s.exclusiveMinimum);
  return true;
}
function freeze<T>(v: T): T {
  if (v && typeof v === "object") {
    Object.values(v).forEach(freeze);
    Object.freeze(v);
  }
  return v;
}

export function loadModel(value: unknown): ModelLoadResult {
  if (!finiteJson(value) || !matches(value, schema as unknown as Schema)) return { status: "invalid", reason: "artifact_schema" };
  const raw = value as Record<string, unknown>;
  const envelope = value as Envelope;
  const expected = envelope.model_version === "geometry_logistic" ? [0, 1, 2]
    : envelope.model_version === "defenders_logistic" ? [0, 1, 2, 3, 4, 5] : [...Array(8).keys()];
  if (raw.contract_version !== featureContract.version || raw.feature_contract_sha256 !== inference.feature_contract_sha256
    || JSON.stringify(raw.feature_order) !== JSON.stringify(featureNames)
    || JSON.stringify(envelope.feature_indices) !== JSON.stringify(expected)) return { status: "invalid", reason: "artifact_contract" };
  const p = envelope.parameters;
  if ((envelope.model_version === "full_xgboost") !== (p.kind === "xgboost")
    || envelope.export_tolerance !== (p.kind === "logistic" ? 1e-10 : 1e-7)) return { status: "invalid", reason: "artifact_parameters" };
  if (p.kind === "logistic") {
    if ([p.mean, p.scale, p.coefficients].some(a => a.length !== expected.length) || p.scale.some(x => x <= 0)) {
      return { status: "invalid", reason: "artifact_parameters" };
    }
  } else {
    if (p.trees.length > inference.max_trees) return { status: "invalid", reason: "artifact_parameters" };
    for (const nodes of p.trees) {
      const seen = new Set<number>();
      function visit(i: number, depth: number): boolean {
        if (seen.has(i) || i < 0 || i >= nodes.length || depth > inference.max_depth) return false;
        seen.add(i);
        const n = nodes[i];
        return "leaf" in n || (n.feature < expected.length && visit(n.left, depth + 1) && visit(n.right, depth + 1));
      }
      if (nodes.length > inference.max_nodes_per_tree || !visit(0, 0) || seen.size !== nodes.length) {
        return { status: "invalid", reason: "artifact_parameters" };
      }
    }
  }
  const captured = freeze(JSON.parse(JSON.stringify(value)) as Envelope);
  const model = freeze({ artifactId: envelope.artifact_id, modelVersion: envelope.model_version,
    contractVersion: envelope.contract_version, usedFeatures: expected.map(i => featureNames[i]), tolerance: envelope.export_tolerance });
  envelopes.set(model, captured);
  return { status: "ready", model };
}

export function isLoadedModel(model: unknown): model is ValidatedModel {
  return object(model) && envelopes.has(model as ValidatedModel);
}
export function validVector(v: unknown): v is number[] {
  if (!Array.isArray(v) || v.length !== 8 || v.some(x => typeof x !== "number" || !Number.isFinite(x) || x < 0)) return false;
  const diagonal = Math.hypot(FIELD.length, FIELD.width);
  return v[1] <= 180 && v[2] <= 34 && v[3] <= 10 && v[4] <= v[3]
    && Number.isInteger(v[3]) && Number.isInteger(v[4])
    && [0, 5, 6, 7].every(i => v[i] <= diagonal) && (v[3] !== 0 || v[5] === diagonal);
}
function sigmoid(x: number): number {
  return x >= 0 ? 1 / (1 + Math.exp(-x)) : Math.exp(x) / (1 + Math.exp(x));
}

/** Full-contract vectors only. Null signals invalid/unavailable input or numeric failure. */
export function predictVector(vector: unknown, model: ValidatedModel): number | null {
  if (!isLoadedModel(model) || !validVector(vector)) return null;
  const envelope = envelopes.get(model)!;
  const p = envelope.parameters;
  const x = envelope.feature_indices.map(i => vector[i]);
  let base: number;
  if (p.kind === "logistic") {
    let margin = p.intercept;
    for (let i = 0; i < x.length; i++) margin += ((x[i] - p.mean[i]) / p.scale[i]) * p.coefficients[i];
    if (!Number.isFinite(margin)) return null;
    base = sigmoid(margin);
  } else {
    const row = x.map(Math.fround);
    let margin = p.base_margin;
    for (const nodes of p.trees) {
      let i = 0;
      while (!("leaf" in nodes[i])) {
        const n = nodes[i] as Exclude<Node, { leaf: number }>;
        i = row[n.feature] < n.threshold ? n.left : n.right;
      }
      margin = Math.fround(margin + (nodes[i] as { leaf: number }).leaf);
    }
    if (!Number.isFinite(margin)) return null;
    base = Math.fround(sigmoid(margin));
  }
  const c = envelope.calibration;
  let result = base;
  if (c.method === "sigmoid") {
    const q = Math.min(1 - c.clip, Math.max(c.clip, base));
    const margin = c.slope * (Math.log(q) - Math.log1p(-q)) + c.intercept;
    if (!Number.isFinite(margin)) return null;
    result = sigmoid(margin);
  }
  return Number.isFinite(result) && result >= 0 && result <= 1 ? result : null;
}
