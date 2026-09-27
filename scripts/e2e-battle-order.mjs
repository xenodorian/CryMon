#!/usr/bin/env node
// Speed-based turn order (logic.json combat.initiative) on the web build.
// Drives real battles through the engine and checks who strikes first:
//
//   1. a much faster foe opens every round ("is quicker. Choose a guard."),
//      the player then gets exactly one action, and the foe does not
//      answer again in that round;
//   2. a much faster player opens every round and the foe answers;
//   3. a foe that knocks out the lead with its first strike still owes the
//      player that round: the next CryMon jumps in and acts first.
//
//   npm run dev                 # in another shell
//   npm run test:e2e:battle
//
// Env: CRYMON_URL (default http://localhost:8080/), CHROMIUM.
import { existsSync } from "node:fs";
import { chromium } from "playwright";

const PAGE_URL = process.env.CRYMON_URL || "http://localhost:8080/";
const exe =
  process.env.CHROMIUM ||
  (existsSync("/opt/pw-browsers/chromium") ? "/opt/pw-browsers/chromium" : undefined);

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

// Start a trainer-style fight (no fleeing, no catching) with set agility.
// Big HP on both sides so nobody faints unless a case wants it.
const start = (o) =>
  page.evaluate((o) => {
    const e = window.__crymon.engine();
    const p = e.party[0];
    Object.assign(p, { level: 20, maxHp: o.plHp ?? 5000, hp: o.plHp ?? 5000, str: 20, spc: 20, agl: o.plAgl, status: "none" });
    e.party = [p, ...(o.bench ? [{ ...p, id: "bench-1", name: "Benchmon", hp: 5000, maxHp: 5000, agl: o.plAgl }] : [])];
    e.partyIndex = 0;
    const foe = { ...p, id: "foe-1", name: "Testfoe", species: p.species, hp: 5000, maxHp: 5000, str: o.foeStr ?? 20, spc: 1, agl: o.foeAgl, specialPp: 0 };
    e.startBattle(foe, false, "Test fight", "wsoldier", null, []);
  }, o);

// Advance until the battle waits on a menu (item / guard / attack) or ends.
// Returns the messages seen on the way.
const toMenu = async () => {
  const seen = [];
  for (let i = 0; i < 60; i++) {
    const st = await page.evaluate(() => {
      const e = window.__crymon.engine();
      const b = e.battle;
      if (!b || e.mode !== "battle") return { phase: "over" };
      return { phase: b.phase, msg: b.phase === "msg" ? b.msg[b.msgI] : null };
    });
    if (st.phase === "over" || st.phase === "item" || st.phase === "guard" || st.phase === "attack") return { phase: st.phase, seen };
    if (st.msg && seen[seen.length - 1] !== st.msg) seen.push(st.msg);
    await page.evaluate(() => window.__crymon.tapConfirm());
    await page.waitForTimeout(60);
  }
  return { phase: "stuck", seen };
};

const act = (what) =>
  page.evaluate((what) => {
    const e = window.__crymon.engine();
    const b = e.battle;
    if (what === "pass") e.pickItem(b.menu.indexOf("Pass"));
    else if (what === "basic") e.pickAttack(0);
    else if (what === "block") e.pickGuard(1);
  }, what).then(() => page.waitForTimeout(120));

// 1. Fast foe.
await start({ plAgl: 1, foeAgl: 999 });
let r = await toMenu();
check(r.phase === "guard" && r.seen.some((m) => /is quicker\. Choose a guard\./.test(m)),
  `fast foe opens the round (got ${r.phase}: ${r.seen.join(" | ")})`);
let foeStrikes = 0;
for (let round = 0; round < 3; round++) {
  if (r.phase !== "guard") break;
  await act("block");
  r = await toMenu();
  foeStrikes += 1;
  check(r.phase === "item", `round ${round + 1}: after the foe's strike the player acts (got ${r.phase})`);
  await act("pass");
  await act("basic");
  r = await toMenu();
  check(!r.seen.some((m) => /answers/.test(m)), `round ${round + 1}: the foe does not answer again (${r.seen.join(" | ")})`);
  check(r.phase === "guard" && r.seen.some((m) => /is quicker/.test(m)), `round ${round + 1}: next round opens with the fast foe again`);
}
check(foeStrikes === 3, "three rounds, foe first each time");

// 2. Fast player.
await start({ plAgl: 999, foeAgl: 1 });
r = await toMenu();
check(r.phase === "item" && !r.seen.some((m) => /quicker/.test(m)), `fast player opens the round (got ${r.phase})`);
await act("pass");
await act("basic");
r = await toMenu();
check(r.phase === "guard" && r.seen.some((m) => /answers\. Choose a guard\./.test(m)), "the foe answers the player");
await act("block");
r = await toMenu();
check(r.phase === "item", `then a new round, player first again (got ${r.phase})`);

// 3. First strike knocks out the lead: the next CryMon still acts this round.
await start({ plAgl: 1, foeAgl: 999, plHp: 1, foeStr: 500, bench: true });
r = await toMenu();
check(r.phase === "guard", "fast foe opens");
await act("block");
r = await toMenu();
check(r.seen.some((m) => /jumps in/.test(m)) && r.phase === "item",
  `lead falls, the bench CryMon jumps in and acts (got ${r.phase}: ${r.seen.join(" | ")})`);

// 4. Ties go to the player.
const tie = await page.evaluate(async () => {
  const d = await import("/src/game/data.ts");
  return [d.foeStrikesFirst(10, 10, 1, 1), d.foeStrikesFirst(10, 11, 1, 1), d.foeStrikesFirst(11, 10, 1, 1)];
});
check(JSON.stringify(tie) === "[false,true,false]", `foeStrikesFirst: tie -> player, faster -> first (got ${tie})`);

check(errors.length === 0, `no page errors ${errors.slice(0, 2).join(" ")}`);
await browser.close();
if (fails.length) {
  console.log(`\n${fails.length} failed`);
  process.exit(1);
}
console.log("\nall passed");
