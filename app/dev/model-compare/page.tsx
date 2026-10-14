import { readFileSync } from "node:fs";
import type { Metadata } from "next";
import { connection } from "next/server";
import { notFound } from "next/navigation";

import { ModelCompare } from "@/components/model-compare";
import { loadCompareCandidate } from "@/lib/dev-compare-server";
import { loadSelectedModelBytes } from "@/lib/selected-model";

export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  title: "Current versus monotonic model",
  robots: { index: false, follow: false },
};

const publishedPath = "model/selected-model.json";

export default async function ModelComparePage() {
  // Wait for the request so a production build does not freeze an unset flag.
  await connection();
  const candidate = loadCompareCandidate({
    XG_COMPARE: process.env["XG_COMPARE"],
    XG_CANDIDATE_MODEL: process.env["XG_CANDIDATE_MODEL"],
  });
  if (candidate.status === "disabled") notFound();
  if (candidate.status !== "ready") {
    return (
      <main className="playground">
        <h1>Local model comparison is not ready</h1>
        <p>
          Set <code>XG_COMPARE=1</code> and <code>XG_CANDIDATE_MODEL</code> to
          the phase-A <code>candidate-model.json</code> file. This page does
          not read a model path from the URL.
        </p>
      </main>
    );
  }

  const bytes = readFileSync(publishedPath);
  const current = await loadSelectedModelBytes(
    bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength),
  );
  if (current.status !== "ready") {
    return (
      <main className="playground">
        <h1>Published model failed its local check</h1>
        <p>The comparison stopped. The published file was not replaced.</p>
      </main>
    );
  }

  return (
    <ModelCompare
      currentText={bytes.toString("utf8")}
      candidateText={candidate.text}
    />
  );
}
