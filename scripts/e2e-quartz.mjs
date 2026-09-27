#!/usr/bin/env node
// Quartz end-to-end check (BUG_LOG BUG-002/003): talk, battle, win line,
// mercy menu, badge, +marks, save, reload, Continue, badge still set, and
// Quartz still on her win line. Then, if a C compiler is present, the
// Dreamcast save code (save.c) must decode the same blob byte-for-byte.
//
//   npm run dev            # in another shell
//   npm run test:e2e:quartz
//
// Env: CRYMON_URL (default http://localhost:8080/), CHROMIUM (browser path,
// default /opt/pw-browsers/chromium when it exists), E2E_OUT (screenshots).
import { execFileSync } from "node:child_process";
import { existsSync, mkdirSync, mkdtempSync, readFileSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { chromium } from "playwright";

const PAGE_URL = process.env.CRYMON_URL || "http://localhost:8080/";
const exe = process.env.CHROMIUM || (existsSync("/opt/pw-browsers/chromium") ? "/opt/pw-browsers/chromium" : undefined);
const OUT = process.env.E2E_OUT || mkdtempSync(join(tmpdir(), "crymon-e2e-"));
mkdirSync(OUT, { recursive: true });
const saveJson = JSON.parse(readFileSync(new URL("../content/save.json", import.meta.url)));
const world = JSON.parse(readFileSync(new URL("../content/world.json", import.meta.url)));
const talk = JSON.parse(readFileSync(new URL("../content/dialogue.json", import.meta.url))).talk;
const kit = world.trainers.quartz;
const winLine = talk[kit.winTalk][0].text;
const spotLine = talk.quartzSpot[0].text;

const fails = [];
const check = (ok, what) => {
	console.log(`${ok ? "PASS" : "FAIL"}  ${what}`);
	if (!ok) fails.push(what);
};

const browser = await chromium.launch({ executablePath: exe });
const page = await browser.newPage({ viewport: { width: 960, height: 720 } });
const errors = [];
page.on("pageerror", (e) => errors.push(String(e)));
const C = (fn, ...a) => page.evaluate(([f, a]) => window.__crymon[f](...a), [fn, a]);
const state = () =>
	page.evaluate(() => {
		const c = window.__crymon;
		const f = c.flags();
		return { mode: c.getMode(), talk: c.hud().talk, badge: f.badgeQuartz, marks: f.marks, battles: f.battles, map: c.getMap() };
	});
const boot = async () => {
	await page.waitForFunction(() => !!window.__crymon, null, { timeout: 60000 });
	await page.waitForTimeout(1000);
};
/** Stand under Quartz (reach tile 8,2), face up, press confirm. */
const faceQuartz = async () => {
	await C("setPos", 8 * 32 + 16, 3 * 32 + 20);
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
	await C("skipToReach");
	// Strong lead so mashing confirm wins the real fight (no WinAll).
	await page.evaluate(() => {
		const p = window.__crymon.party()[0];
		Object.assign(p, { level: 40, maxHp: 400, hp: 400, str: 200, agl: 200, spc: 200 });
	});
	const before = await state();
	await faceQuartz();
	check((await state()).talk === spotLine || (await state()).talk === talk.quartzSpot[1].text, "Quartz opens with quartzSpot");

	const order = [];
	for (let i = 0; i < 1500; i++) {
		const s = await state();
		const tag = s.mode === "mercy" ? "mercy" : s.mode === "battle" ? "battle" : s.talk === winLine ? "winLine" : null;
		if (tag && order[order.length - 1] !== tag) order.push(tag);
		if (tag === "mercy" && !existsSync(join(OUT, "mercy.png"))) await page.screenshot({ path: join(OUT, "mercy.png") });
		if (s.mode === "world" && !s.talk && s.badge) break;
		await C("tapConfirm");
		await page.waitForTimeout(60);
	}
	const won = await state();
	check(order.join(">") === "battle>winLine>mercy", `battle, then ${kit.winTalk}, then mercy menu (got ${order.join(">")})`);
	check(won.badge === true, `${kit.set} set`);
	check(won.marks - before.marks === kit.marks, `+${kit.marks} marks (got +${won.marks - before.marks})`);
	check(won.battles - before.battles === 1, `one battle counted (got ${won.battles - before.battles})`);

	await faceQuartz();
	check((await state()).talk === winLine, "re-talk gives the win line");
	await drainTalk();
	check((await C("saveNow")) === true, "manual save");
	const b64 = await page.evaluate(() => localStorage.getItem("crymon.save.v1"));
	const blob = Buffer.from(b64 || "", "base64");
	writeFileSync(join(OUT, "quartz-save.bin"), blob);
	check(blob.length === saveJson.size, `save blob is ${saveJson.size} bytes (got ${blob.length})`);

	await page.reload();
	await boot();
	check((await C("continueSave")) === true, "Continue after reload");
	await page.waitForTimeout(400);
	const back = await state();
	check(back.badge === true && back.marks === won.marks && back.map === "reach", "badge, marks and map survive reload");
	await faceQuartz();
	check((await state()).talk === winLine, "re-talk after reload gives the win line");
	await page.screenshot({ path: join(OUT, "after-reload.png") });
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
	execFileSync(cc, ["-w", "-Iports/dreamcast/src", "ports/dreamcast/tools/save_host_check.c", "-o", bin]);
	const flagId = saveJson.flags.indexOf(kit.set);
	try {
		console.log(execFileSync(bin, [join(OUT, "quartz-save.bin"), `${flagId}=1`], { encoding: "utf8" }).trim());
		check(true, "Dreamcast save.c decodes the web blob, badge set, byte-identical repack");
	} catch (e) {
		console.log(String(e.stdout || e));
		check(false, "Dreamcast save.c decodes the web blob, badge set, byte-identical repack");
	}
} else {
	console.log("SKIP  no C compiler, Dreamcast save readback not checked");
}
console.log(`artifacts: ${OUT}`);
process.exit(fails.length ? 1 : 0);
