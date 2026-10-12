// Optional local/remote product QA. Playwright stays outside the app bundle.
import { createHash } from "node:crypto";
import assert from "node:assert/strict";
import { readFileSync, writeFileSync } from "node:fs";
import { createRequire } from "node:module";
import { spawn, execFileSync } from "node:child_process";
import { resolveQaTarget } from "./product-qa-target.mjs";
const { chromium } = createRequire(import.meta.url)("playwright");
const evidence = JSON.parse(
  readFileSync("docs/reports/xg-final-first-run/app-evidence.json", "utf8"),
);
const target = resolveQaTarget(process.env);
const base = target.base;
const server = target.serverArgs
  ? spawn(process.execPath, target.serverArgs, { stdio: "ignore" })
  : null;
let browser;
const requests = new Set(),
  errors = [],
  findings = [];
try {
  for (let attempt = 0; attempt < 80; attempt++) {
    try {
      if ((await fetch(`${base}/en`, { signal: AbortSignal.timeout(10000) })).ok) break;
    } catch {
      /* Wait for the production server. */
    }
    if (attempt === 79) throw new Error("Production server unavailable");
    await new Promise((resolve) => setTimeout(resolve, 100));
  }
  browser = await chromium.launch({
    headless: true,
    ...(process.env.PRODUCT_QA_PROXY ? { proxy: { server: process.env.PRODUCT_QA_PROXY } } : {}),
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
    ["nl", "nl"],
    ["es", "es"],
    ["de", "de"],
  ]) {
    const copy = JSON.parse(readFileSync(`locales/${locale}.json`, "utf8"));
    await page.goto(`${base}/${route}`);
    await page.getByTestId("xg").waitFor();
    assert.equal(await page.locator("html").getAttribute("lang"), locale);
    assert.equal(await page.title(), copy.meta.title);
    assert.equal(await page.locator('meta[name="description"]').getAttribute("content"), copy.meta.description);
    assert.equal(await page.locator(".language-switcher option").count(), 5);
    assert.equal(await page.locator(".data-source-logo").getAttribute("aria-label"), copy.attribution.sourceLink);
    const pitchBox = await page.locator(".pitch-surface").boundingBox();
    const featureBox = await page.locator(".features-section").boundingBox();
    assert(pitchBox.x + pitchBox.width <= featureBox.x);
    assert.equal(await page.locator(".feature-card").count(), 8);
    assert((await page.locator("#methodology").count()) === 1);
    assert.equal(
      await page
        .getByText("Explore the technical decisions", { exact: true })
        .count(),
      0,
    );
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
    const resetScene = (await snapshot()).scenario;
    const shooter = page.locator(".pitch-player--attacker").first();
    await shooter.focus();
    await shooter.press("ArrowUp");
    await page.waitForFunction(
      () =>
        JSON.parse(sessionStorage.getItem("football-visualized-scenario"))
          .scenario.players.shooter.x === 84.5,
    );
    assert.equal(await page.locator(".feature-card").count(), 8);
    assert.equal(
      await page
        .locator('.feature-card[data-feature="shot_distance_m"] .feature-value')
        .innerText(),
      new Intl.NumberFormat(locale, { maximumFractionDigits: 1 }).format(20.5),
    );
    assert.equal(
      await page
        .locator(".comparison-card, .feature-observations, .section-navigation")
        .count(),
      0,
    );
    await page.getByRole("button", { name: copy.playground.reset, exact: true }).click();
    assert.deepEqual((await snapshot()).scenario, resetScene);
    await shooter.press("ArrowUp");
    await page.waitForFunction(
      () => JSON.parse(sessionStorage.getItem("football-visualized-scenario")).scenario.players.shooter.x === 84.5,
    );
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
    await page.locator("#methodology").scrollIntoViewIfNeeded();
    await page
      .getByRole("heading", { name: copy.methodology.title, exact: true })
      .waitFor();
    assert((await page.locator("#slices").innerText()).includes("815"));
    assert.equal(await page.locator("svg[role=img]").count(), 1);
    await page.locator("#playground").scrollIntoViewIfNeeded();
    await page.getByTestId("xg").waitFor();
    assert.deepEqual((await snapshot()).scenario, edited);
    await page.reload();
    await page.getByTestId("xg").waitFor();
    assert.deepEqual((await snapshot()).scenario, edited);
    await page.locator(".position-adjustments > summary").click();
    const selector = page.locator(".position-controls select");
    for (const id of ["defender1", "defender2"]) {
      await selector.selectOption(id);
      await page
        .getByRole("button", { name: copy.playground.results.remove })
        .click();
    }
    assert.equal(await page.locator(".pitch-player--defender").count(), 0);
    assert.equal(
      await page
        .locator(
          '.feature-card[data-feature="visible_defender_count"] .feature-value',
        )
        .innerText(),
      "0",
    );
    assert.equal(
      await page
        .locator(
          '.feature-card[data-feature="nearest_visible_defender_distance_m"] .feature-value',
        )
        .innerText(),
      "—",
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
    await preset.selectOption("penalty");
    await page.locator(".position-controls input").first().fill("70");
    assert.equal(
      (await page.getByTestId("xg").innerText()).replace(/\s/g, ""),
      `${new Intl.NumberFormat(locale, { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(0.76)}xG`,
    );
    assert(
      (await page.locator(".prediction-card").textContent()).includes(
        copy.playground.results.fixedPenalty,
      ),
    );
    await page.setViewportSize({ width: 390, height: 844 });
    await preset.selectOption("centralChance");
    assert.equal(await page.locator(".feature-card").count(), 8);
    const cards = await page.locator(".feature-card").evaluateAll((cards) =>
      cards.map((card) => ({
        x: card.getBoundingClientRect().x,
        y: card.getBoundingClientRect().y,
      })),
    );
    assert(cards[0].x < cards[1].x && Math.abs(cards[0].y - cards[1].y) < 1);
    await page.locator(".features-section").scrollIntoViewIfNeeded();
    const estimateBox = await page.locator(".prediction-card").boundingBox();
    assert(estimateBox.y >= 0 && estimateBox.y < 50);
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
    await page.waitForFunction(() => {
      const img = document.querySelector(".data-source-logo img");
      return img.complete && img.naturalWidth > 0;
    });
    assert(await logo.evaluate((img) => img.complete && img.naturalWidth > 0));
    assert.equal(await logo.getAttribute("alt"), copy.attribution.logoAlt);
    assert((await page.locator(".site-footer").innerText()).includes(copy.attribution.disclaimer));
    await page.locator(".evidence-identity summary").click();
    assert.equal(await page.locator("[data-review-status]").innerText(), copy.methodology.displayValues.acceptedWithLimitations);
    assert.equal(await page.locator("[data-release-status]").innerText(), copy.methodology.displayValues.needsReview);
    if (locale === "nl" || locale === "de") {
      await page.setViewportSize({ width: 320, height: 844 });
      assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
      for (const card of await page.locator(".feature-card").all()) {
        assert(await card.evaluate((el) => el.scrollWidth <= el.clientWidth));
      }
      await page.setViewportSize({ width: 390, height: 844 });
    }
    await page.goto(`${base}/${route}/methodology`);
    await page.waitForURL(`${base}/${route}#methodology`);
    assert(
      await page.evaluate(
        () => document.documentElement.scrollWidth <= innerWidth,
      ),
    );
    assert((await page.locator(".table-scroll").count()) >= 5);
    await page.setViewportSize({ width: 1440, height: 1000 });
    findings.push(
      `${route}: presets, live eight-feature cards, mouse/keyboard/touch, editing, reload/anchors, mobile sticky xG and evidence/attribution PASS`,
    );
  }
  await page.goto(`${base}/en`);
  await page.getByTestId("xg").waitFor();
  await page.locator("#scene-preset").selectOption("tightAngle");
  await page.locator(".position-adjustments > summary").click();
  await page.locator(".position-controls input").first().fill("80");
  await page.getByRole("button", { name: "+ Attacker", exact: true }).click();
  await page.getByRole("button", { name: "+ Defender", exact: true }).click();
  const prior = await snapshot();
  const routeLocales = [["en", "en"], ["br", "pt-BR"], ["nl", "nl"], ["es", "es"], ["de", "de"]];
  // Cycle every locale on an edited scene, retaining query and section hash.
  await page.goto(`${base}/en?qa=locale#methodology`);
  for (const [route, locale] of routeLocales) {
    await page.locator(".language-switcher select").selectOption(locale);
    await page.waitForURL(`${base}/${route}?qa=locale#methodology`);
    await page.getByTestId("xg").waitFor();
    assert.deepEqual(await snapshot(), prior);
    const cookie = (await context.cookies()).find((x) => x.name === "football-visualized-locale");
    if (locale !== "en") assert.equal(cookie?.value, locale);
    await page.reload();
    await page.getByTestId("xg").waitFor();
    assert.deepEqual(await snapshot(), prior);
    if (locale !== "en") {
      await page.goto(`${base}/`);
      await page.waitForURL(`${base}/${route}`);
      await page.getByTestId("xg").waitFor();
      assert.deepEqual(await snapshot(), prior);
      await page.goto(`${base}/${route}?qa=locale#methodology`);
    }
  }
  await page.goto(`${base}/en`);
  const modelResponse = await page.request.get(
    `${base}/model/selected-model.json`,
  );
  assert(modelResponse.ok());
  const modelBytes = await modelResponse.body();
  assert.equal(
    createHash("sha256").update(modelBytes).digest("hex"),
    "c0d91256a2c0f83ede48f1f549b8a0cc379e6ef675ccd4ce9ef10e471bb4350d",
  );
  for (const [routeName, locale] of routeLocales) {
    const copy = JSON.parse(readFileSync(`locales/${locale}.json`, "utf8"));
    for (const failure of ["network", "hash"]) {
      const failedContext = await browser.newContext();
      await failedContext.route("**/model/selected-model.json", (route) =>
        failure === "network"
          ? route.fulfill({ status: 503, body: "Unavailable" })
          : route.fulfill({ status: 200, contentType: "application/json", body: Buffer.concat([modelBytes, Buffer.from(" ")]) }),
      );
      const failed = await failedContext.newPage();
      await failed.goto(`${base}/${routeName}`);
      await failed.getByText(copy.playground.results.unavailable, { exact: true }).waitFor();
      assert.equal(await failed.getByTestId("xg").count(), 0);
      await failed.locator("#scene-preset").selectOption("penalty");
      await failed.getByTestId("xg").waitFor();
      assert.equal((await failed.getByTestId("xg").innerText()).replace(/\s/g, ""), `${new Intl.NumberFormat(locale, { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(0.76)}xG`);
      await failedContext.close();
    }
    const loadingContext = await browser.newContext();
    let releaseModel;
    const delayed = new Promise((resolve) => { releaseModel = resolve; });
    await loadingContext.route("**/model/selected-model.json", async (route) => {
      await delayed;
      await route.fulfill({ status: 200, contentType: "application/json", body: modelBytes });
    });
    const loadingPage = await loadingContext.newPage();
    await loadingPage.goto(`${base}/${routeName}`);
    await loadingPage.getByText(copy.playground.results.loading, { exact: true }).waitFor();
    assert.equal(await loadingPage.getByTestId("xg").count(), 0);
    releaseModel();
    await loadingPage.getByTestId("xg").waitFor();
    await loadingContext.close();
  }
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
  await blocked.locator(".position-adjustments > summary").click();
  assert.equal(
    await blocked.locator(".position-controls input").first().inputValue(),
    "84.5",
  );
  await blocked.locator(".language-switcher select").selectOption("nl");
  await blocked.waitForURL(`${base}/nl`);
  await blocked.getByTestId("xg").waitFor();
  await blocked.locator(".position-adjustments > summary").click();
  assert.equal(await blocked.locator(".position-controls input").first().inputValue(), "84.5");
  await isolated.close();
  const noCookies = await browser.newContext();
  const cookieBlocked = await noCookies.newPage();
  await cookieBlocked.addInitScript(() => {
    Object.defineProperty(document, "cookie", { get: () => "", set: () => {} });
  });
  await cookieBlocked.goto(`${base}/en`);
  await cookieBlocked.getByTestId("xg").waitFor();
  await cookieBlocked.locator(".language-switcher select").selectOption("de");
  await cookieBlocked.waitForURL(`${base}/de`);
  await cookieBlocked.getByTestId("xg").waitFor();
  assert.equal((await noCookies.cookies()).length, 0);
  await noCookies.close();
  assert.deepEqual(errors, []);
  assert(
    ![...requests].some((path) =>
      /events|three-sixty|test-predictions|\/api\//i.test(path),
    ),
  );
  const report = {
    schema_version: 1,
    checked_at: new Date().toISOString(),
    base_url: base,
    mode: target.remote ? "remote" : "local",
    checkout_revision: execFileSync("git", ["rev-parse", "HEAD"], { encoding: "utf8" }).trim(),
    local_build_id: target.remote ? null : readFileSync(".next/BUILD_ID", "utf8").trim(),
    // The remote source/build cannot be inferred from a matching model hash.
    deployed_revision: null,
    remote_build_id: null,
    engine: "Chromium",
    version: browser.version(),
    viewport: [1440, 1000],
    mobile: [390, 844],
    narrow_mobile: [320, 844],
    narrow_mobile_locales: ["nl", "de"],
    locales: ["en", "pt-BR", "nl", "es", "de"],
    findings,
    locale_and_view_retention: "PASS",
    blocked_storage: "PASS",
    blocked_cookie_navigation: "PASS",
    model_loading_network_and_hash_failure: "PASS",
    served_model_sha256: createHash("sha256").update(modelBytes).digest("hex"),
    page_errors: errors,
    network_paths: [...requests].sort(),
    public_deployment_tested: target.remote,
    physical_device_tested: false,
  };
  if (process.env.PRODUCT_QA_OUTPUT)
    writeFileSync(
      process.env.PRODUCT_QA_OUTPUT,
      JSON.stringify(report, null, 2) + "\n",
    );
  console.log(
    JSON.stringify({
      engine: report.engine,
      base_url: base,
      mode: report.mode,
      version: report.version,
      findings,
      requests: requests.size,
      errors: errors.length,
    }),
  );
} finally {
  if (browser) await browser.close();
  if (server) server.kill();
}
