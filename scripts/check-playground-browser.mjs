// Optional local product QA. Playwright is installed separately, never in the app bundle.
import { createHash } from "node:crypto";
import assert from "node:assert/strict";
import { readFileSync, writeFileSync } from "node:fs";
import { createRequire } from "node:module";
import { spawn } from "node:child_process";
const { chromium } = createRequire(import.meta.url)("playwright");
const evidence = JSON.parse(
  readFileSync("docs/reports/xg-final-first-run/app-evidence.json", "utf8"),
);
const port = Number(process.env.PRODUCT_QA_PORT || 3010);
const base = `http://127.0.0.1:${port}`;
const server = spawn(
  process.execPath,
  [
    "node_modules/next/dist/bin/next",
    "start",
    "--hostname",
    "127.0.0.1",
    "--port",
    String(port),
  ],
  { stdio: "ignore" },
);
let browser;
const requests = new Set(),
  errors = [],
  findings = [];
try {
  for (let attempt = 0; attempt < 80; attempt++) {
    try {
      if ((await fetch(`${base}/en`)).ok) break;
    } catch {
      /* Wait for the local production server. */
    }
    if (attempt === 79) throw new Error("Production server unavailable");
    await new Promise((resolve) => setTimeout(resolve, 100));
  }
  browser = await chromium.launch({
    headless: true,
    ...(process.env.INFERENCE_CHROMIUM_EXECUTABLE
      ? { executablePath: process.env.INFERENCE_CHROMIUM_EXECUTABLE }
      : {}),
  });
  const context = await browser.newContext({
    viewport: { width: 1440, height: 1000 },
    hasTouch: true,
  });
  const page = await context.newPage();
  page.on("pageerror", (error) => errors.push(error.message));
  page.on("request", (request) =>
    requests.add(new URL(request.url()).pathname),
  );
  const snapshot = () =>
    page.evaluate(() =>
      JSON.parse(sessionStorage.getItem("football-visualized-scenario")),
    );
  for (const [route, locale] of [
    ["en", "en"],
    ["br", "pt-BR"],
  ]) {
    const copy = JSON.parse(readFileSync(`locales/${locale}.json`, "utf8"));
    await page.goto(`${base}/${route}`);
    await page.getByTestId("xg").waitFor();
    const preset = page.locator("#scene-preset");
    for (const id of [
      "centralChance",
      "oneOnOne",
      "tightAngle",
      "longShot",
      "crowdedBox",
      "penalty",
    ]) {
      await preset.selectOption(id);
      const diagnostic = evidence.scene_audit.diagnostics.find(
        (row) => row.scene === id,
      );
      const expected = new Intl.NumberFormat(locale, {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
      }).format(diagnostic.probability);
      await page.waitForFunction(
        (expected) =>
          document
            .querySelector('[data-testid="xg"]')
            .textContent.replace(/\s/g, "") === `${expected}xG`,
        expected,
      );
      assert(
        (await page.getByTestId("percentage").innerText()).includes(
          new Intl.NumberFormat(locale, {
            style: "percent",
            minimumFractionDigits: 1,
            maximumFractionDigits: 1,
          }).format(diagnostic.probability),
        ),
      );
    }
    await preset.selectOption("centralChance");
    const shooter = page.locator(".pitch-player--attacker").first();
    await shooter.focus();
    await shooter.press("ArrowUp");
    await page.waitForFunction(
      () =>
        JSON.parse(sessionStorage.getItem("football-visualized-scenario"))
          .scenario.players.shooter.x === 84.5,
    );
    // Blur explicitly completes a keyboard comparison without a test-only timeout.
    await preset.focus();
    await page
      .getByRole("heading", { name: copy.playground.results.comparison })
      .waitFor();
    let marker = await shooter.boundingBox();
    await page.mouse.move(
      marker.x + marker.width / 2,
      marker.y + marker.height / 2,
    );
    await page.mouse.down();
    await page.mouse.move(
      marker.x + marker.width / 2 + 24,
      marker.y + marker.height / 2 - 24,
      { steps: 8 },
    );
    await page.mouse.up();
    assert.notEqual((await snapshot()).scenario.players.shooter.y, 34);
    const edited = (await snapshot()).scenario;
    await page
      .getByRole("link", { name: copy.navigation.methodology, exact: true })
      .click();
    await page
      .getByRole("heading", { name: copy.methodology.title, exact: true })
      .waitFor();
    assert.equal(
      await page
        .locator('nav.section-navigation [aria-current="page"]')
        .innerText(),
      copy.navigation.methodology,
    );
    assert((await page.locator("#slices").innerText()).includes("815"));
    assert.equal(await page.locator("svg[role=img]").count(), 1);
    await page
      .getByRole("link", { name: copy.navigation.playground, exact: true })
      .click();
    await page.getByTestId("xg").waitFor();
    assert.deepEqual((await snapshot()).scenario, edited);
    await page.reload();
    await page.getByTestId("xg").waitFor();
    assert.deepEqual((await snapshot()).scenario, edited);
    const selector = page.locator(".position-controls select");
    for (const id of ["defender1", "defender2"]) {
      await selector.selectOption(id);
      await page
        .getByRole("button", { name: copy.playground.results.remove })
        .click();
    }
    assert.equal(await page.locator(".pitch-player--defender").count(), 0);
    assert(
      (await page.locator(".support-note").allTextContents())
        .join(" ")
        .includes(copy.playground.results.zero),
    );
    for (let i = 0; i < 3; i++)
      await page
        .getByRole("button", { name: copy.playground.addDefender, exact: true })
        .click();
    assert.equal(await page.locator(".pitch-player--defender").count(), 3);
    assert(
      await page
        .getByRole("button", { name: copy.playground.addDefender, exact: true })
        .isDisabled(),
    );
    await page
      .getByRole("button", { name: copy.playground.addAttacker, exact: true })
      .click();
    const beforeAttacker = await page.getByTestId("xg").innerText();
    await selector.selectOption("attacker-0");
    await page.locator(".position-controls input").first().fill("70");
    assert.equal(await page.getByTestId("xg").innerText(), beforeAttacker);
    assert(
      (await page.locator(".comparison-card").innerText()).includes(
        copy.playground.results.omitted,
      ),
    );
    await preset.selectOption("penalty");
    await page.locator(".position-controls input").first().fill("70");
    assert.equal(
      (await page.getByTestId("xg").innerText()).replace(/\s/g, ""),
      `${locale === "en" ? "0.76" : "0,76"}xG`,
    );
    assert(
      (await page.locator(".prediction-card").textContent()).includes(
        copy.playground.results.penalty,
      ),
    );
    await page.setViewportSize({ width: 390, height: 844 });
    await preset.selectOption("centralChance");
    const svg = page.locator(".pitch-svg");
    await svg.scrollIntoViewIfNeeded();
    marker = await page
      .locator(".pitch-player--attacker")
      .first()
      .boundingBox();
    const session = await context.newCDPSession(page);
    await session.send("Input.dispatchTouchEvent", {
      type: "touchStart",
      touchPoints: [
        { x: marker.x + marker.width / 2, y: marker.y + marker.height / 2 },
      ],
    });
    await session.send("Input.dispatchTouchEvent", {
      type: "touchMove",
      touchPoints: [
        {
          x: marker.x + marker.width / 2 + 15,
          y: marker.y + marker.height / 2 - 15,
        },
      ],
    });
    await session.send("Input.dispatchTouchEvent", {
      type: "touchEnd",
      touchPoints: [],
    });
    assert.notEqual((await snapshot()).scenario.players.shooter.y, 34);
    assert(
      await page.evaluate(
        () => document.documentElement.scrollWidth <= innerWidth,
      ),
    );
    const logo = page.locator(".data-source-logo img");
    await logo.scrollIntoViewIfNeeded();
    assert(await logo.evaluate((img) => img.complete && img.naturalWidth > 0));
    assert((await logo.getAttribute("alt")).length > 0);
    await page.goto(`${base}/${route}/methodology`);
    assert(
      await page.evaluate(
        () => document.documentElement.scrollWidth <= innerWidth,
      ),
    );
    assert((await page.locator(".table-scroll").count()) >= 5);
    await page.setViewportSize({ width: 1440, height: 1000 });
    findings.push(
      `${route}: presets, mouse/keyboard/touch, comparisons, editing, reload/navigation, mobile evidence/attribution PASS`,
    );
  }
  await page.goto(`${base}/en`);
  await page.getByTestId("xg").waitFor();
  await page.locator("#scene-preset").selectOption("tightAngle");
  const prior = (await snapshot()).scenario;
  await page.locator(".language-switcher select").selectOption("pt-BR");
  await page.waitForURL(`${base}/br`);
  await page.getByTestId("xg").waitFor();
  assert.deepEqual((await snapshot()).scenario, prior);
  await page
    .getByRole("link", { name: "Metodologia e resultados", exact: true })
    .click();
  await page.waitForURL(`${base}/br/methodology`);
  await page.locator(".language-switcher select").selectOption("en");
  await page.waitForURL(`${base}/en/methodology`);
  assert.deepEqual((await snapshot()).scenario, prior);
  const modelResponse = await page.request.get(
    `${base}/model/selected-model.json`,
  );
  assert(modelResponse.ok());
  const modelBytes = await modelResponse.body();
  assert.equal(
    createHash("sha256").update(modelBytes).digest("hex"),
    "c0d91256a2c0f83ede48f1f549b8a0cc379e6ef675ccd4ce9ef10e471bb4350d",
  );
  for (const failure of ["network", "hash"]) {
    const failedContext = await browser.newContext();
    await failedContext.route("**/model/selected-model.json", (route) =>
      failure === "network"
        ? route.fulfill({ status: 503, body: "Unavailable" })
        : route.fulfill({
            status: 200,
            contentType: "application/json",
            body: Buffer.concat([modelBytes, Buffer.from(" ")]),
          }),
    );
    const failed = await failedContext.newPage();
    await failed.goto(`${base}/en`);
    await failed.getByText("Model unavailable.", { exact: false }).waitFor();
    assert.equal(await failed.getByTestId("xg").count(), 0);
    await failed.locator("#scene-preset").selectOption("penalty");
    await failed.getByTestId("xg").waitFor();
    assert.equal(
      (await failed.getByTestId("xg").innerText()).replace(/\s/g, ""),
      "0.76xG",
    );
    await failedContext.close();
  }
  const loadingContext = await browser.newContext();
  let releaseModel;
  const delayed = new Promise((resolve) => {
    releaseModel = resolve;
  });
  await loadingContext.route("**/model/selected-model.json", async (route) => {
    await delayed;
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: modelBytes,
    });
  });
  const loadingPage = await loadingContext.newPage();
  await loadingPage.goto(`${base}/en`);
  await loadingPage
    .getByText("Loading the reviewed model…", { exact: true })
    .waitFor();
  assert.equal(await loadingPage.getByTestId("xg").count(), 0);
  releaseModel();
  await loadingPage.getByTestId("xg").waitFor();
  await loadingContext.close();
  const isolated = await browser.newContext();
  const blocked = await isolated.newPage();
  await blocked.addInitScript(() => {
    Object.defineProperty(window, "sessionStorage", {
      get() {
        throw new Error("Storage blocked");
      },
    });
  });
  await blocked.goto(`${base}/en`);
  await blocked.getByTestId("xg").waitFor();
  await blocked.locator(".pitch-player--attacker").first().focus();
  await blocked.locator(".pitch-player--attacker").first().press("ArrowUp");
  assert.equal(
    await blocked.locator(".position-controls input").first().inputValue(),
    "84.5",
  );
  await isolated.close();
  assert.deepEqual(errors, []);
  assert(
    ![...requests].some((path) =>
      /events|three-sixty|test-predictions|\/api\//i.test(path),
    ),
  );
  const report = {
    schema_version: 1,
    engine: "Chromium",
    version: browser.version(),
    viewport: [1440, 1000],
    mobile: [390, 844],
    findings,
    locale_and_view_retention: "PASS",
    blocked_storage: "PASS",
    model_loading_network_and_hash_failure: "PASS",
    served_model_sha256: createHash("sha256").update(modelBytes).digest("hex"),
    page_errors: errors,
    network_paths: [...requests].sort(),
    public_deployment_tested: false,
  };
  if (process.env.PRODUCT_QA_OUTPUT)
    writeFileSync(
      process.env.PRODUCT_QA_OUTPUT,
      JSON.stringify(report, null, 2) + "\n",
    );
  console.log(
    JSON.stringify({
      engine: report.engine,
      version: report.version,
      findings,
      requests: requests.size,
      errors: errors.length,
    }),
  );
} finally {
  if (browser) await browser.close();
  server.kill();
}
