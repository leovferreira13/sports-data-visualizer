import { build, version as esbuildVersion } from "esbuild";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { createRequire } from "node:module";
import { createServer } from "node:http";

const entry = fileURLToPath(new URL("./inference_bridge.ts", import.meta.url));
export async function bundle() {
  const result = await build({ entryPoints: [entry], bundle: true, write: false,
    platform: "browser", format: "esm", target: "es2022", metafile: true, minify: true });
  if (Object.values(result.metafile.outputs).some(o => o.imports.length)) throw new Error("External client dependency");
  return { code: result.outputFiles[0].text, bytes: result.outputFiles[0].contents.length, esbuildVersion };
}
async function run(payload, inBrowser) {
  const bundled = await bundle();
  let value, engine;
  if (!inBrowser) {
    const compiled = await import(`data:text/javascript;base64,${Buffer.from(bundled.code).toString("base64")}`);
    value = compiled.evaluate(payload);
    engine = { name: "node-browser-bundle", version: process.versions.node };
  } else {
    // Optional local smoke test dependency. It is never part of the production bundle.
    const { chromium } = createRequire(import.meta.url)("playwright");
    const server = createServer((req, res) => {
      res.setHeader("Content-Type", req.url === "/module.js" ? "text/javascript" : "text/html");
      res.end(req.url === "/module.js" ? bundled.code : "<!doctype html><html><body>Local inference verification</body></html>");
    });
    await new Promise(resolve => server.listen(0, "127.0.0.1", resolve));
    let browser;
    try {
      browser = await chromium.launch({ headless: true,
        ...(process.env.INFERENCE_CHROMIUM_EXECUTABLE ? { executablePath: process.env.INFERENCE_CHROMIUM_EXECUTABLE } : {}) });
      const page = await browser.newPage();
      await page.goto(`http://127.0.0.1:${server.address().port}/`);
      value = await page.evaluate(async input => (await import("/module.js")).evaluate(input), payload);
      engine = { name: "chromium", version: browser.version() };
    } finally {
      if (browser) await browser.close();
      await new Promise(resolve => server.close(resolve));
    }
  }
  return { ...value, engine, bundle_bytes: bundled.bytes, esbuild_version: bundled.esbuildVersion };
}
if (process.argv[1] === fileURLToPath(import.meta.url)) {
  try {
    const payload = JSON.parse(readFileSync(0, "utf8"));
    process.stdout.write(JSON.stringify(await run(payload, process.argv.includes("--browser"))));
  } catch {
    // Never echo payloads, private parameter values or local paths on failure.
    process.stderr.write("Inference bridge failed; check npm ci, Node version and optional browser installation.\n");
    process.exitCode = 1;
  }
}
