#!/usr/bin/env node
// Growth redesign (logic.json growth.hypeUpAt / attackSwapAt, attackSwap)
// on the web build:
//
//   1. an evolution-line species knows Hype Up at Lv15, not at Lv14, and
//      never Attack Swap;
//   2. a single-stage species knows Attack Swap at Lv15, not at Lv14, and
//      never Hype Up;
//   3. Attack Swap hits like the basic move, then opens the SWAP IN menu;
//      picking a CryMon switches it in and the foe answers;
//   4. cancelling the SWAP IN menu keeps the lead in.
//
//   npm run dev                 # in another shell
//   npm run test:e2e:growth
//
// Env: CRYMON_URL (default http://localhost:8080/), CHROMIUM.
import { existsSync, readFileSync } from "node:fs";
import { chromium } from "playwright";

const PAGE_URL = process.env.CRYMON_URL || "http://localhost:8080/";
const exe =
  process.env.CHROMIUM ||
  (existsSync("/opt/pw-browsers/chromium") ? "/opt/pw-browsers/chromium" : undefined);

const SPECIES = JSON.parse(readFileSync(new URL("../content/species.json", import.meta.url)));
const LOGIC = JSON.parse(readFileSync(new URL("../content/logic.json", import.meta.url)));
const targets = new Set(Object.values(SPECIES).map((s) => s.evolvesTo).filter(Boolean));
const inLine = (id) => !!SPECIES[id].evolvesTo || targets.has(id);
const lineSp = Object.keys(SPECIES).find((id) => SPECIES[id].evolvesTo && !SPECIES[id].spells);
const soloSp = Object.keys(SPECIES).find((id) => !inLine(id) && !SPECIES[id].spells);
const SWAP = LOGIC.attackSwap.name;
const HYPE = LOGIC.hypeUp.name;

const fails = [];
const check = (ok, what) => {
  console.log(`${ok ? "PASS" : "FAIL"}  ${what}`);
  if (!ok) fails.push(what);
};

const browser = await chromium.launch({ executablePath: exe });
const page = await browser.newPage({ viewport: { width: 960, height: 720 } });
const errors = [];
page.on("pageerror", (e) => errors.push(String(e)));
await page.goto(PAGE_URL);
await page.waitForFunction(() => !!window.__crymon, null, { timeout: 60000 });
await page.evaluate(() => window.__crymon.wipeSave());
await page.evaluate(() => window.__crymon.skipTo("veld"));

const moveNames = (species, level) =>
  page.evaluate(({ species, level }) => {
    const e = window.__crymon.engine();
    const p = { ...e.party[0], species, level };
    return e.partyMoves(p).map((m) => m.name);
  }, { species, level });

// 1-2. Level gates.
for (const [sp, want, never] of [[lineSp, HYPE, SWAP], [soloSp, SWAP, HYPE]]) {
  const at14 = await moveNames(sp, 14);
  const at15 = await moveNames(sp, 15);
  check(!at14.includes(want), `${sp} Lv14 does not know ${want}`);
  check(at15.includes(want), `${sp} Lv15 knows ${want}`);
  check(!at15.includes(never), `${sp} Lv15 never knows ${never}`);
}

// 3-4. Attack Swap in a real battle: a single-stage lead plus one bench
// CryMon, big HP everywhere, a slow foe so the player opens the round.
const start = () =>
  page.evaluate((soloSp) => {
    const e = window.__crymon.engine();
    const p = e.party[0];
    Object.assign(p, { species: soloSp, name: "Lead", level: 20, maxHp: 5000, hp: 5000, str: 20, spc: 20, agl: 999, status: "none" });
    e.party = [p, { ...p, id: "bench-1", name: "Benchmon" }];
    e.partyIndex = 0;
    const foe = { ...p, id: "foe-1", name: "Testfoe", hp: 5000, maxHp: 5000, agl: 1, specialPp: 0 };
    e.startBattle(foe, false, "Test fight", "wsoldier", null, []);
    e.battle.movePpUsed["foe-1:nmove"] = 99;
    e.battle.movePpUsed["foe-1:hype"] = 99;
  }, soloSp);

const toPhase = async (want) => {
  for (let i = 0; i < 40; i++) {
    const ph = await page.evaluate(() => window.__crymon.engine().battle?.phase ?? "over");
    if (want.includes(ph) || ph === "over") return ph;
    await page.evaluate(() => window.__crymon.tapConfirm());
    await page.waitForTimeout(60);
  }
  return "stuck";
};

const swapFlow = async () => {
  await start();
  await toPhase(["item"]);
  await page.evaluate(() => {
    const e = window.__crymon.engine();
    e.pickItem(e.battle.menu.indexOf("Pass"));
  });
  const foeHp0 = await page.evaluate(() => window.__crymon.engine().battle.foe.hp);
  await page.evaluate((SWAP) => {
    const e = window.__crymon.engine();
    e.pickAttack(e.battle.menu.findIndex((r) => r.startsWith(SWAP)));
  }, SWAP);
  // resolve_hit runs on the next frame.
  const ph = await page.evaluate(async () => {
    for (let i = 0; i < 40; i++) {
      const b = window.__crymon.engine().battle;
      if (b.phase !== "resolve_hit") return b.phase;
      await new Promise((r) => setTimeout(r, 30));
    }
    return "stuck";
  });
  const st = await page.evaluate(() => {
    const e = window.__crymon.engine();
    return { foeHp: e.battle.foe.hp, menu: e.battle.menu };
  });
  return { ph, hit: foeHp0 - st.foeHp, menu: st.menu };
};

{
  const r = await swapFlow();
  check(r.hit > 0, `Attack Swap deals damage (got ${r.hit})`);
  check(r.ph === "swap", `SWAP IN menu opens after the hit (got ${r.ph})`);
  check(r.menu.length === 1 && r.menu[0] === "Benchmon", `menu lists the living bench (got ${r.menu.join(",")})`);
  await page.evaluate(() => window.__crymon.engine().pickSwap(0));
  const after = await page.evaluate(() => {
    const e = window.__crymon.engine();
    return { idx: e.partyIndex, name: e.battle.player.name, phase: e.battle.phase, msg: e.battle.msg };
  });
  check(after.idx === 1 && after.name === "Benchmon", `Benchmon is switched in (got ${after.name})`);
  check(after.msg.some((m) => m.includes("Benchmon out.")), "\"Benchmon out.\" is shown");
  check(after.msg.some((m) => m.includes("answers")), "the foe answers after the swap");
}

{
  const r = await swapFlow();
  check(r.ph === "swap", `SWAP IN opens again (got ${r.ph})`);
  await page.evaluate(() => window.__crymon.engine().input.queueB()); // B = cancel
  await page.waitForTimeout(150);
  const after = await page.evaluate(() => {
    const e = window.__crymon.engine();
    return { idx: e.partyIndex, phase: e.battle.phase };
  });
  check(after.idx === 0 && after.phase === "msg", `cancel keeps the lead in (partyIndex ${after.idx}, phase ${after.phase})`);
}

// 5-7. Lv20 signature / Lv30 finisher (logic.json crystalMoves): gates,
// a real hit with its rider, the finisher through the timing minigame.
const CM = LOGIC.crystalMoves.moves.find((m) => m.nature === SPECIES[lineSp].nature);
{
  const at19 = await moveNames(lineSp, 19), at20 = await moveNames(lineSp, 20);
  const at29 = await moveNames(lineSp, 29), at30 = await moveNames(lineSp, 30);
  check(!at19.includes(CM.signature.name) && at20.includes(CM.signature.name), `${CM.signature.name} unlocks at Lv20`);
  check(!at29.includes(CM.finisher.name) && at30.includes(CM.finisher.name), `${CM.finisher.name} unlocks at Lv30`);
}
const riderOn = (r) =>
  page.evaluate((r) => {
    const b = window.__crymon.engine().battle;
    if (r.kind === "selfHype") return b.hypeActive.self === true;
    if (r.kind === "foeStage") return b.stage["foe" + r.stat[0].toUpperCase() + r.stat.slice(1)] > 0;
    return b.foe.status === r.status;
  }, r);
const crystalHit = async (kind) => {
  await page.evaluate((lineSp) => {
    const e = window.__crymon.engine();
    const p = e.party[0];
    Object.assign(p, { species: lineSp, name: "Lead", level: 30, maxHp: 5000, hp: 5000, str: 20, spc: 20, agl: 999, status: "none" });
    e.party = [p];
    e.partyIndex = 0;
    const foe = { ...p, id: "foe-1", name: "Testfoe", hp: 5000, maxHp: 5000, agl: 1, specialPp: 0 };
    e.startBattle(foe, false, "Test fight", "wsoldier", null, []);
    for (const k of ["nmove", "hype", "signature", "finisher"]) e.battle.movePpUsed["foe-1:" + k] = 99;
  }, lineSp);
  await toPhase(["item"]);
  await page.evaluate(() => { const e = window.__crymon.engine(); e.pickItem(e.battle.menu.indexOf("Pass")); });
  const name = kind === "signature" ? CM.signature.name : CM.finisher.name;
  const hp0 = await page.evaluate(() => window.__crymon.engine().battle.foe.hp);
  await page.evaluate((name) => {
    const e = window.__crymon.engine();
    e.pickAttack(e.battle.menu.findIndex((r) => r.startsWith(name)));
  }, name);
  if (kind === "finisher") {
    const ph = await page.evaluate(() => window.__crymon.engine().battle.phase);
    check(ph === "minigame", `${name} opens the timing minigame (got ${ph})`);
    await page.evaluate(() => window.__crymon.tapConfirm());
  }
  await page.waitForFunction(() => window.__crymon.engine().battle.phase !== "resolve_hit" && window.__crymon.engine().battle.phase !== "minigame", null, { timeout: 5000 });
  const st = await page.evaluate((kind) => {
    const e = window.__crymon.engine();
    const key = `${e.battle.player.id}:${kind}`;
    return { hp: e.battle.foe.hp, used: e.battle.movePpUsed[key], line: e.battle.msg.join(" | ") };
  }, kind);
  check(hp0 - st.hp > 0, `${name} deals damage (got ${hp0 - st.hp})`);
  check(await riderOn(kind === "signature" ? CM.signature.rider : CM.finisher.rider), `${name} applies its rider (${JSON.stringify(kind === "signature" ? CM.signature.rider : CM.finisher.rider)}): ${st.line}`);
  check(st.used === 1, `${name} spends one use (got ${st.used})`);
};
await crystalHit("signature");
await crystalHit("finisher");

check(errors.length === 0, `no page errors ${errors.join(" | ")}`);
await browser.close();
console.log(fails.length ? `\n${fails.length} failed` : "\nall passed");
process.exit(fails.length ? 1 : 0);
