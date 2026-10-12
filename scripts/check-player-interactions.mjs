// Focused production-browser regression check and repeatable README capture.
import assert from "node:assert/strict";
import { createRequire } from "node:module";
import { spawn } from "node:child_process";
import { resolveQaTarget } from "./product-qa-target.mjs";
const { chromium } = createRequire(import.meta.url)("playwright");
const target = resolveQaTarget(process.env);
const server = target.serverArgs ? spawn(process.execPath, target.serverArgs, { stdio: "ignore" }) : null;
let browser;
try {
  const base = target.base;
  for (let i = 0; i < 80; i++) {
    try { if ((await fetch(`${base}/en`)).ok) break; } catch { /* Wait for server. */ }
    if (i === 79) throw new Error("Production server unavailable");
    await new Promise(resolve => setTimeout(resolve, 100));
  }
  browser = await chromium.launch({ headless: true,
    ...(process.env.INFERENCE_CHROMIUM_EXECUTABLE ? { executablePath: process.env.INFERENCE_CHROMIUM_EXECUTABLE } : {}),
  });
  const page = await browser.newPage({ viewport: { width: 1440, height: 1050 }, deviceScaleFactor: 1 });
  const errors = [];
  page.on("pageerror", error => errors.push(error.message));
  const seed = async (scenario, presetId = "centralChance") => {
    await page.evaluate(({ scenario, presetId }) => sessionStorage.setItem(
      "football-visualized-scenario", JSON.stringify({ version: 3, presetId, scenario }),
    ), { scenario, presetId });
    await page.reload();
    await page.getByTestId("xg").waitFor();
  };
  const snapshot = () => page.evaluate(() => JSON.parse(sessionStorage.getItem("football-visualized-scenario")).scenario);
  const center = locator => locator.evaluate(el => {
    const point = new DOMPoint(0, 0).matrixTransform(el.getScreenCTM());
    return { x: point.x, y: point.y };
  });
  await page.goto(`${base}/en`);
  await page.getByTestId("xg").waitFor();
  await page.locator("#scene-preset").selectOption("centralChance");
  const initial = await snapshot();
  const nearby = structuredClone(initial);
  nearby.players.defender1 = { x: 84, y: 37.2 };
  await seed(nearby);
  const shooter = page.locator(".pitch-player--attacker").first();
  const before = await center(shooter);
  await page.mouse.move(before.x, before.y);
  await page.mouse.down();
  assert(await shooter.evaluate(el => el.classList.contains("is-selected")));
  await page.mouse.move(before.x - 20, before.y - 20, { steps: 5 });
  await page.mouse.up();
  const moved = await snapshot();
  assert.notDeepEqual(moved.players.shooter, nearby.players.shooter);
  assert.deepEqual(moved.players.defender1, nearby.players.defender1);
  const scale = await page.locator(".pitch-svg").evaluate(el => el.getScreenCTM().a);
  const after = await center(shooter);
  // Outside the visible marker, inside the former invisible hit target.
  const outside = { x: after.x - 2 * scale, y: after.y };
  assert.equal(await page.evaluate(p => Boolean(document.elementFromPoint(p.x, p.y)?.closest(".pitch-player")), outside), false);
  await page.mouse.click(outside.x, outside.y);
  assert.deepEqual(await snapshot(), moved);
  const keeper = await center(page.locator(".pitch-player--goalkeeper"));
  assert.equal(await page.evaluate(p => Boolean(document.elementFromPoint(p.x, p.y)?.closest(".pitch-player")),
    { x: keeper.x + 2.05 * scale, y: keeper.y }), false);

  await page.locator("#scene-preset").selectOption("penalty");
  await page.getByRole("button", { name: "+ Attacker", exact: true }).click();
  await page.getByRole("button", { name: "+ Defender", exact: true }).click();
  const penalty = await snapshot();
  for (const point of [...penalty.extraAttackers, ...penalty.extraDefenders]) assert(point.x + 1.4 < 88.5);
  assert.equal((await page.getByTestId("xg").innerText()).replace(/\s/g, ""), "0.76xG");

  const scene = structuredClone(initial);
  scene.players.shooter = { x: 75, y: 34 };
  scene.players.defender1 = { x: 88, y: 33 };
  scene.players.defender2 = { x: 94, y: 35 };
  await seed(scene, "longShot");
  for (const [feature, value] of [["shot_distance_m", "30"], ["visible_defender_count", "2"], ["defenders_in_cone_count", "2"]]) {
    assert.equal(await page.locator(`[data-feature="${feature}"] .feature-value`).innerText(), value);
  }
  const geometry = await page.locator(".pitch-svg").evaluate(el => {
    const r = el.getBoundingClientRect(), m = el.getScreenCTM();
    return { width: r.width, height: r.height, scaleX: m.a, scaleY: m.d, dpr: devicePixelRatio, viewportScale: visualViewport.scale, zoom: getComputedStyle(document.documentElement).zoom };
  });
  assert(Math.abs(geometry.width / geometry.height - 68 / 52.5) < 0.001);
  assert(Math.abs(geometry.scaleX - geometry.scaleY) < 1e-9);
  assert.equal(geometry.dpr, 1);
  assert.equal(geometry.viewportScale, 1);
  assert.equal(geometry.zoom, "1");
  assert.deepEqual(errors, []);
  if (process.env.README_CAPTURE === "1") {
    await page.evaluate(() => document.fonts.ready);
    await page.screenshot({ path: "assets/portfolio/playground.png" });
  }
  console.log(JSON.stringify({ status: "PASS", checks: "nearby shooter selection, captured drag, exact marker hit bounds, keeper ring, penalty additions, long-shot screenshot", geometry, probability: await page.getByTestId("xg").innerText(), browser: browser.version() }));
} finally {
  if (browser) await browser.close();
  if (server) server.kill();
}
