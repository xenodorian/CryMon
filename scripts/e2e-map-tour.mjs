#!/usr/bin/env node
// Web half of the map tour: load every map from the per-map saves that
// ports/dreamcast/tools/map_tour.py writes (<dir>/blobs/<map>.bin), pick
// Continue, walk a few steps, and fail on page errors or a player left
// standing in a wall. Screenshots go next to the Dreamcast ones.
//
//   python3 ports/dreamcast/tools/map_tour.py --base e2e-out/quartz-before.bin --out tour-out --blobs-only
//   npm run dev &   node scripts/e2e-map-tour.mjs tour-out
import { existsSync, readdirSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { chromium } from "playwright";

const DIR = process.argv[2] || "tour-out";
const PAGE_URL = process.env.CRYMON_URL || "http://localhost:8080/";
const exe =
  process.env.CHROMIUM ||
  (existsSync("/opt/pw-browsers/chromium") ? "/opt/pw-browsers/chromium" : undefined);
const maps = JSON.parse(readFileSync(new URL("../content/maps.json", import.meta.url)));
const names = readdirSync(join(DIR, "blobs"))
  .filter((f) => f.endsWith(".bin"))
  .map((f) => f.slice(0, -4));

const fails = [];
const browser = await chromium.launch({ executablePath: exe });
const page = await browser.newPage({ viewport: { width: 960, height: 720 } });
let errors = [];
page.on("pageerror", (e) => errors.push(String(e)));
await page.goto(PAGE_URL);
await page.waitForFunction(() => !!window.__crymon, null, { timeout: 60000 });
for (const name of names) {
  errors = [];
  const b64 = readFileSync(join(DIR, "blobs", `${name}.bin`)).toString("base64");
  let res;
  try {
    await page.evaluate((s) => localStorage.setItem("crymon.save.v1", s), b64);
    await page.reload();
    await page.waitForFunction(() => !!window.__crymon, null, { timeout: 60000 });
    await page.waitForTimeout(300);
    const ok = await page.evaluate(() => window.__crymon.continueSave());
    for (const k of ["ArrowLeft", "ArrowRight", "ArrowUp", "ArrowDown"]) {
      await page.evaluate((k) => window.__controlsTest.setKeys([k]), k);
      await page.waitForTimeout(200);
    }
    await page.evaluate(() => window.__controlsTest.setKeys([]));
    await page.waitForTimeout(300);
    res = await page.evaluate(() => ({
      map: window.__crymon.getMap(),
      pos: window.__crymon.pos(),
      mode: window.__crymon.getMode(),
    }));
    res.ok = ok;
    await page.screenshot({ path: join(DIR, `${name}-web.png`) });
  } catch (e) {
    errors.push(String(e));
  }
  const rows = maps.rows[res?.map] || [];
  const ch = res ? rows[Math.floor(res.pos.y / 32)]?.[Math.floor(res.pos.x / 32)] : undefined;
  const standing = ch != null && !maps.solid.includes(ch);
  const pass = res?.ok && res.map === name && standing && errors.length === 0;
  console.log(
    `${pass ? "PASS" : "FAIL"}  ${name}` +
      (pass
        ? ""
        : `  (continue=${res?.ok} map=${res?.map} tile='${ch}' mode=${res?.mode} ${errors.join(" | ")})`),
  );
  if (!pass) fails.push(name);
}
await browser.close();
console.log(`${names.length - fails.length}/${names.length} maps load on web`);
process.exit(fails.length ? 1 : 0);
