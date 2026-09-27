#!/usr/bin/env node
// Crystal warden end-to-end check (BUG_LOG BUG-002/003, Opal: BUG-004):
// talk, battle, win line, mercy menu, badge, +marks, save, reload,
// Continue, badge still set, and the warden still on the win line. Then, if a C compiler is present, the
// Dreamcast save code (save.c) must decode the same blob byte-for-byte.
//
//   npm run dev            # in another shell
//   npm run test:e2e:quartz            # Quartz, then Opal
//   node scripts/e2e-quartz.mjs opal   # one warden
//
// Env: CRYMON_URL (default http://localhost:8080/), CHROMIUM (browser path,
// default /opt/pw-browsers/chromium when it exists), E2E_OUT (screenshots).
import { execFileSync } from "node:child_process";
import { existsSync, mkdirSync, mkdtempSync, readFileSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { chromium } from "playwright";

const PAGE_URL = process.env.CRYMON_URL || "http://localhost:8080/";
const exe =
  process.env.CHROMIUM ||
  (existsSync("/opt/pw-browsers/chromium") ? "/opt/pw-browsers/chromium" : undefined);
const OUT = process.env.E2E_OUT || mkdtempSync(join(tmpdir(), "crymon-e2e-"));
mkdirSync(OUT, { recursive: true });
const saveJson = JSON.parse(readFileSync(new URL("../content/save.json", import.meta.url)));
const world = JSON.parse(readFileSync(new URL("../content/world.json", import.meta.url)));
const maps = JSON.parse(readFileSync(new URL("../content/maps.json", import.meta.url)));
const talk = JSON.parse(readFileSync(new URL("../content/dialogue.json", import.meta.url))).talk;
const WARDENS = process.argv.slice(2).length ? process.argv.slice(2) : ["quartz", "opal"];

const fails = [];
const check = (ok, what) => {
  console.log(`${ok ? "PASS" : "FAIL"}  ${what}`);
  if (!ok) fails.push(what);
};

async function runWarden(who) {
  const npc = world.npcs.find((n) => n.script?.some((st) => st.pending === who));
  const kit = world.trainers[who];
  const winLine = talk[kit.winTalk][0].text;
  const spotLines = talk[npc.talk].map((b) => b.text);
  const row = maps.rows[npc.map].findIndex((r) => r.includes(npc.mark));
  const col = maps.rows[npc.map][row].indexOf(npc.mark);
  console.log(`--- ${kit.name} (${npc.map} tile ${col},${row}) ---`);
  const browser = await chromium.launch({ executablePath: exe });
  const page = await browser.newPage({ viewport: { width: 960, height: 720 } });
  const errors = [];
  page.on("pageerror", (e) => errors.push(String(e)));
  const C = (fn, ...a) => page.evaluate(([f, a]) => window.__crymon[f](...a), [fn, a]);
  const state = () =>
    page.evaluate((flag) => {
      const c = window.__crymon;
      const f = c.flags();
      return {
        mode: c.getMode(),
        talk: c.hud().talk,
        badge: f[flag],
        marks: f.marks,
        battles: f.battles,
        map: c.getMap(),
      };
    }, kit.set);
  const boot = async () => {
    await page.waitForFunction(() => !!window.__crymon, null, { timeout: 60000 });
    await page.waitForTimeout(1000);
  };
  /** Stand one tile under the warden, face up, press confirm. */
  const faceQuartz = async () => {
    await C("setPos", col * 32 + 16, (row + 1) * 32 + 20);
    await page.evaluate(() => window.__controlsTest.setKeys(["ArrowUp"]));
    await page.waitForTimeout(150);
    await page.evaluate(() => window.__controlsTest.setKeys([]));
    await page.waitForTimeout(250);
    const s = await state();
    if (!s.talk) {
      await C("tapConfirm");
      await page.waitForTimeout(300);
    }
  };
  const drainTalk = async () => {
    for (let i = 0; i < 20 && (await state()).talk; i++) {
      await C("tapConfirm");
      await page.waitForTimeout(250);
    }
  };

  try {
    await page.goto(PAGE_URL);
    await boot();
    await C("wipeSave");
    if (npc.map !== "reach") throw new Error(`no skip hook for ${npc.map}`);
    await C("skipToReach");
    // Strong lead so mashing confirm wins the real fight (no WinAll).
    await page.evaluate(() => {
      const p = window.__crymon.party()[0];
      Object.assign(p, { level: 40, maxHp: 400, hp: 400, str: 200, agl: 200, spc: 200 });
    });
    const before = await state();
    await faceQuartz();
    check(spotLines.includes((await state()).talk), `${kit.name} opens with ${npc.talk}`);

    const order = [];
    for (let i = 0; i < 1500; i++) {
      const s = await state();
      const tag =
        s.mode === "mercy"
          ? "mercy"
          : s.mode === "battle"
            ? "battle"
            : s.talk === winLine
              ? "winLine"
              : null;
      if (tag && order[order.length - 1] !== tag) order.push(tag);
      if (tag === "mercy" && !existsSync(join(OUT, `${who}-mercy.png`)))
        await page.screenshot({ path: join(OUT, `${who}-mercy.png`) });
      if (s.mode === "world" && !s.talk && s.badge) break;
      await C("tapConfirm");
      await page.waitForTimeout(60);
    }
    const won = await state();
    check(
      order.join(">") === "battle>winLine>mercy",
      `battle, then ${kit.winTalk}, then mercy menu (got ${order.join(">")})`,
    );
    check(won.badge === true, `${kit.set} set`);
    check(
      won.marks - before.marks === kit.marks,
      `+${kit.marks} marks (got +${won.marks - before.marks})`,
    );
    check(
      won.battles - before.battles === 1,
      `one battle counted (got ${won.battles - before.battles})`,
    );

    await faceQuartz();
    check((await state()).talk === winLine, `re-talk gives ${kit.winTalk}`);
    await drainTalk();
    check((await C("saveNow")) === true, "manual save");
    const b64 = await page.evaluate(() => localStorage.getItem("crymon.save.v1"));
    const blob = Buffer.from(b64 || "", "base64");
    writeFileSync(join(OUT, `${who}-save.bin`), blob);
    check(
      blob.length === saveJson.size,
      `save blob is ${saveJson.size} bytes (got ${blob.length})`,
    );

    await page.reload();
    await boot();
    check((await C("continueSave")) === true, "Continue after reload");
    await page.waitForTimeout(400);
    const back = await state();
    check(
      back.badge === true && back.marks === won.marks && back.map === "reach",
      "badge, marks and map survive reload",
    );
    await faceQuartz();
    check((await state()).talk === winLine, `re-talk after reload gives ${kit.winTalk}`);
    await page.screenshot({ path: join(OUT, `${who}-after-reload.png`) });
    check(errors.length === 0, `no page errors ${errors.length ? JSON.stringify(errors) : ""}`);
  } finally {
    await browser.close();
  }

  // Dreamcast save.c must read the web blob identically.
  const cc = ["cc", "gcc", "clang"].find((c) => {
    try {
      execFileSync(c, ["--version"], { stdio: "ignore" });
      return true;
    } catch {
      return false;
    }
  });
  if (cc) {
    const bin = join(OUT, "save_host_check");
    execFileSync(cc, [
      "-w",
      "-Iports/dreamcast/src",
      "ports/dreamcast/tools/save_host_check.c",
      "-o",
      bin,
    ]);
    const flagId = saveJson.flags.indexOf(kit.set);
    try {
      console.log(
        execFileSync(bin, [join(OUT, `${who}-save.bin`), `${flagId}=1`], {
          encoding: "utf8",
        }).trim(),
      );
      check(true, "Dreamcast save.c decodes the web blob, badge set, byte-identical repack");
    } catch (e) {
      console.log(String(e.stdout || e));
      check(false, "Dreamcast save.c decodes the web blob, badge set, byte-identical repack");
    }
  } else {
    console.log("SKIP  no C compiler, Dreamcast save readback not checked");
  }
}
for (const who of WARDENS) await runWarden(who);

// BUG-014: a save made inside a wall loads onto the nearest walkable tile.
{
  const browser = await chromium.launch({ executablePath: exe });
  const page = await browser.newPage();
  try {
    await page.goto(PAGE_URL);
    await page.waitForFunction(() => !!window.__crymon, null, { timeout: 60000 });
    await page.waitForTimeout(1000);
    const res = await page.evaluate(() => {
      const c = window.__crymon;
      c.wipeSave();
      c.skipToReach();
      c.setPos(16, 16); // reach tile 0,0 is '#'
      c.saveNow();
      c.continueSave();
      return c.pos();
    });
    const rows = maps.rows.reach;
    const ch = rows[Math.floor(res.y / 32)]?.[Math.floor(res.x / 32)];
    check(
      ch != null && !maps.solid.includes(ch) && ch !== maps.doors,
      `save in a wall loads on a walkable tile (got ${res.x},${res.y} '${ch}')`,
    );
  } finally {
    await browser.close();
  }
}
console.log(`artifacts: ${OUT}`);
process.exit(fails.length ? 1 : 0);
