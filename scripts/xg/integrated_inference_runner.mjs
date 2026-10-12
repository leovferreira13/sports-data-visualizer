import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { run } from "./browser_inference_runner.mjs";
const entry = fileURLToPath(
  new URL("./integrated_inference_bridge.ts", import.meta.url),
);
try {
  const result = await run(
    JSON.parse(readFileSync(0, "utf8")),
    process.argv.includes("--browser"),
    entry,
  );
  process.stdout.write(JSON.stringify(result));
} catch {
  process.stderr.write("Integrated frozen-model inference failed.\n");
  process.exitCode = 1;
}
