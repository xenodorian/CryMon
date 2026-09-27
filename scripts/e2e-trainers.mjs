#!/usr/bin/env node
// Every scripted trainer fight, on the web build, from the saves that
// ports/dreamcast/tools/trainer_saves.py writes (<dir>/<trainer>-before.bin,
// player next to the NPC, facing it, story flags set so its script reaches
// the fight). Continue, talk, mash confirm through the fight, and check the
// kit's flag, its Marks, and no page errors or stuck talk.
//
//   python3 ports/dreamcast/tools/trainer_saves.py --base e2e-out/quartz-before.bin --out trainers-out
//   npm run dev &   node scripts/e2e-trainers.mjs trainers-out [trainer ...]
import { existsSync, readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { chromium } from "playwright";

const DIR = process.argv[2] || "trainers-out";
const ONLY = process.argv.slice(3);
const PAGE_URL = process.env.CRYMON_URL || "http://localhost:8080/";
const exe =
  process.env.CHROMIUM ||
  (existsSync("/opt/pw-browsers/chromium") ? "/opt/pw-browsers/chromium" : undefined);
const world = JSON.parse(readFileSync(new URL("../content/world.json", import.meta.url)));
const saveJson = JSON.parse(readFileSync(new URL("../content/save.json", import.meta.url)));
const flagOffs = saveJson.flagParts.flatMap(([o, n]) => Array.from({ length: n }, (_, i) => o + i));
const plan = JSON.parse(readFileSync(join(DIR, "plan.json"))).filter(
  (p) => !ONLY.length || ONLY.includes(p.trainer),
);

const results = [];
const browser = await chromium.launch({ executablePath: exe });
const page = await browser.newPage({ viewport: { width: 960, height: 720 } });
let errors = [];
page.on("pageerror", (e) => errors.push(String(e)));
await page.goto(PAGE_URL);
await page.waitForFunction(() => !!window.__crymon, null, { timeout: 60000 });

for (const p of plan) {
  const kit = world.trainers[p.trainer];
  errors = [];
  const b64 = readFileSync(join(DIR, `${p.trainer}-before.bin`)).toString("base64");
  // Flags come from a fresh save blob: flags() only lists a few of them.
  const st = (withFlag = false) =>
    page.evaluate(
      ([flagIdx, offs, withFlag]) => {
        const c = window.__crymon;
        const f = c.flags();
        let won = null;
        if (withFlag && flagIdx >= 0 && c.getMode() === "world" && !c.hud().talk) {
          c.saveNow();
          const raw = atob(localStorage.getItem("crymon.save.v1") || "");
          won = !!((raw.charCodeAt(offs[flagIdx >> 3]) >> (flagIdx & 7)) & 1);
        }
        return {
          mode: c.getMode(),
          talk: c.hud().talk,
          won,
          marks: f.marks,
          battles: f.battles,
          map: c.getMap(),
        };
      },
      [saveJson.flags.indexOf(kit.set), flagOffs, withFlag],
    );
  let r = { trainer: p.trainer, map: p.map };
  try {
    await page.evaluate((s) => localStorage.setItem("crymon.save.v1", s), b64);
    await page.reload();
    await page.waitForFunction(() => !!window.__crymon, null, { timeout: 60000 });
    await page.waitForTimeout(300);
    await page.evaluate(() => window.__crymon.continueSave());
    await page.waitForTimeout(300);
    const before = await st();
    const seen = [];
    const talks = [];
    let now = before;
    for (let i = 0; i < 1200; i++) {
      now = await st();
      if (now.mode !== seen[seen.length - 1]) seen.push(now.mode);
      if (now.talk && talks[talks.length - 1] !== now.talk) talks.push(now.talk);
      if (i > 5 && now.mode === "world" && !now.talk && seen.includes("battle")) break;
      await page.evaluate(() => window.__crymon.tapConfirm());
      await page.waitForTimeout(50);
    }
    // Finish any lines still up after the fight.
    for (let i = 0; i < 30 && (await st()).talk; i++) {
      await page.evaluate(() => window.__crymon.tapConfirm());
      await page.waitForTimeout(80);
    }
    now = await st(true);
    r = {
      ...r,
      fought: seen.includes("battle"),
      won: now.won,
      marks: now.marks - before.marks,
      battles: now.battles - before.battles,
      modes: seen.join(">"),
      end: now.mode,
      firstTalk: talks[0] || "",
      errors: [...errors],
    };
    if (!r.won) await page.screenshot({ path: join(DIR, `${p.trainer}-web.png`) });
  } catch (e) {
    r.errors = [...errors, String(e)];
  }
  const ok = r.fought && (kit.set ? r.won : true) && r.errors.length === 0 && r.end === "world";
  r.ok = ok;
  results.push(r);
  console.log(
    `${ok ? "PASS" : "FAIL"}  ${p.trainer.padEnd(18)} ${p.map.padEnd(12)} fought=${r.fought} won=${r.won} ` +
      `marks=+${r.marks} (kit ${kit.marks ?? 0}) battles=+${r.battles} ${r.modes}` +
      (ok ? "" : `  talk="${(r.firstTalk || "").slice(0, 60)}" ${r.errors?.join(" | ") || ""}`),
  );
}
await browser.close();
writeFileSync(join(DIR, "web-results.json"), JSON.stringify(results, null, 1));
const bad = results.filter((r) => !r.ok).length;
console.log(`${results.length - bad}/${results.length} trainer fights pass on web`);
process.exit(bad ? 1 : 0);
