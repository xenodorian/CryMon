// @ts-nocheck
import { Chip, MAP_SONG, TITLE_SONG, BATTLE_SONG, TRAINER_SONG, ENDING_SONG, VOLUME } from "./audio";
import { packSave, unpackSave, writeSaveBlob, readSaveBlob, saveExists, clearSave, SAVE_FLAGS, SAVE_SPECIES } from "./save";
import {
  CAMP,
  CLIFFS,
  FOREST,
  GROVE,
  HOUSE,
  INTRO,
  ITEMS,
  ITEM_ORDER,
  MAPS,
  MARSH,
  PARTY_MAX,
  QUARRY,
  REACH,
  RUINS,
  SPECIES,
  SPEAKER_NAME,
  START_BAG,
  START_MARKS,
  TALK,
  TILE,
  TRAINERS,
  SPRITES,
  VELD,
  VIEW_H,
  VIEW_W,
  captureChance,
  doorTile,
  grantPartyXp,
  healAmount,
  mintMonster,
  natureOf,
  speciesNature,
  natureScaleDmg,
  natureTag,
  rollShiny,
  solidTile,
  spawnOf,
  ENDING_WIN,
  ENDING_WIN_HEAVENFALL,
  MAP_NAME,
  ENCOUNTERS,
  WARPS,
  NPCS,
  artManifest,
  itemEffect,
  COMBAT,
  INTERACT,
  atkStatValue,
  frand,
  unlockedMoves,
  natureMatchNames,
  MERCY_DISMISS,
  FORMULAS,
  STAT_STAGES,
  STATUS_EFFECTS,
  SHINY_MOVE,
  HYPE_UP,
  effectiveStat
, TOWN_MAP } from "./data";
import { LOGIC, arrivalAllowed, fadeAlpha, matchNpcScript, pickMason2Map, shouldSpawnMasonRematch } from "./logic";
import { Input } from "./input";
import type {
  BattleState,
  Dir,
  GuardKind,
  ItemId,
  MapId,
  Mode,
  Monster,
  PartyView,
  Roamer,
  RivalState,
  ShopTab,
  Soldier,
  SpeciesId,
  TalkBeat,
  TrainerId,
  WorldState,
} from "./types";

type ImgMap = Record<string, HTMLImageElement>;
type TalkAfter = null | `shop:${string}` | "drayKnifeShop" | "mason" | "mason2" | "calder" | "soldier" | "cathleen" | "shinigami" | "anneLeave" | "masonLeave" | "choice" | "wsoldier" | "ending" | "creditsFinal" | "bedHeal" | "leadThanksGO" | "hfGameOver" | "priestessTeleport";

const SHOP_NAMES: Record<string, string> = { bram: "BRAM'S STALL", oren: "OREN'S STALL", fenn: "FENN'S STALL", dray: "DRAY'S STALL" };
const SHOP_FREE_FLAG: Record<string, string> = { bram: "shopFreeBram", oren: "shopFreeOren", fenn: "shopFreeFenn", dray: "shopFreeDray" };
const STEP = 1 / 60;
function loadImg(src, ms = 8000) {
	return new Promise((res, rej) => {
		const im = new Image();
		let settled = false;
		const done = (ok, val) => {
			if (settled) return;
			settled = true;
			clearTimeout(timer);
			if (ok) res(val);
			else rej(val);
		};
		const timer = setTimeout(() => done(false, new Error("timeout")), ms);
		im.onload = () => done(true, im);
		im.onerror = () => done(false, new Error(src));
		im.src = src;
	});
}
function clamp(n, a, b) {
	return Math.max(a, Math.min(b, n));
}
function randI(a, b) {
	return a + Math.floor(Math.random() * (b - a + 1));
}
function tileAt(map, x, y) {
	const tx = Math.floor(x / TILE);
	const row = map[Math.floor(y / TILE)];
	if (!row || tx < 0 || tx >= row.length) return "#";
	return row[tx] ?? "#";
}
function X(n: number) {
	return Math.round(n * VIEW_W / 240);
}
function Y(n: number) {
	return Math.round(n * VIEW_H / 160);
}
const SPR_W = 48;
const SPR_H = 52;
const FONT = 16;
export class CryMon {
	canvas: HTMLCanvasElement;
	ctx: CanvasRenderingContext2D;
	input = new Input();
	audio = new Chip();
	images: ImgMap = {};
	ready = false;
	mode: Mode = "title";
	introI = 0;
	endI = 0;
	acc = 0;
	last = 0;
	running = false;
	shake = 0;
	clock = 0;
	world = {
		mapId: "house",
		x: 96,
		y: 80,
		dir: "down",
		moving: false,
		frame: 0,
		anim: 0,
		encounterLock: 0
	};
	party: Monster[] = [];
	partyIndex = 0;
	/** Father's 6-slot party (Leg 2.7.3). */
	party2 = [];
	/** 0 = Max, 1 = Father. */
	activeParty = 0;
	party2Index = 0;
	bag: Record<ItemId, number> = { ...START_BAG };
	battle = null;
	talkedFather = false;
	tookStarter = false;
	talkedWren = false;
	talkedMae = false;
	beatCalder = false;
	lootedCrate = false;
	talkedIvo = false;
	talkedNell = false;
	nellBonus = false;
	talkedPike = false;
	pikeHelped = false;
	gotHerb = false;
	gotFieldGem = false;
	gotStump = false;
	readCart = false;
	caughtOnce = false;
	foughtMason = false;
	marks = 16;
	talkQ = [];
	talkI = 0;
	afterTalk = null;
	bagCursor = 0;
	partyCursor = 0;
	partyView = "list";
	actCursor = 0;
	moveCursor = 0;
	pendingItem = null;
	pendingCatch = null;
	shopTab = "buy";
	shopCursor = 0;
	rival = {
		phase: "off",
		x: 0,
		y: 0,
		dir: "up",
		frame: 0,
		anim: 0
	};
	anne = {
		phase: "off",
		x: 0,
		y: 0,
		dir: "up",
		frame: 0,
		anim: 0
	};
	/** Web-preview-only debug console (crymon-app.tsx's "Dev Codes"
	 *  toggle) -- never persisted, never reset on new game, no Dreamcast
	 *  equivalent (there's no dev-code UI to drive it on that engine). */
	devPassAll = false;
	/** WinAll dev mode: once entered, stays passively active for the
	 *  rest of the playthrough (same lifetime as devPassAll above) --
	 *  every mercy-eligible trainer (calder/soldier/wsoldier) engaged
	 *  from here on, outside a Backstab, is resolved as an instant win
	 *  straight into the mercy menu instead of playing dialogue then a
	 *  real battle. See triggerDevWinAllFight(). */
	devWinAllMode = false;
	soldiers: Soldier[] = [];
	pendingSoldier: string | null = null;
	/** Chase state for stationary wsoldier-style trainers -- see
	 *  Roamer's own doc comment. Keyed by npc.id, lazily populated. */
	roamers: Record<string, Roamer> = {};
	battlesDone = 0;
	anneGifted = false;
	cathleenCaught = false;
	beatCathleen = false;
	beatShinigami = false;
	sawShinigamiRock = false;
	hasScroll = false;
	anne2Told = false;
	tessaGifted = false;
	birchGifted = false;
	sableGifted = false;
	chestLooted = false;
	beatCross = false;
	beatConscript = false;
	beatEnforcer = false;
	beatSentry = false;
	beatForestRanger = false;
	beatForestScout = false;
	beatRuinsKeeper = false;
	beatRuinsWarden = false;
	beatMarshBog = false;
	beatMarshReed = false;
	badgeQuartz = false;
	badgeOpal = false;
	beatQuarryDriller = false;
	choseHeavenfall = false;
	beatHeavenfall = false;
	revivedFather = false;
	beatCommander = false;
	beatLieutenantLead = false;
	heavenfallRepWarned = false;
	/** Dray's one-time knife-offer line (Bowie Knife), gated on negative
	 *  reputation the first time his shop opens. Also what unlocks the
	 *  knife in his own shopCatalog(). */
	drayKnifeOffered = false;
	/** Choice presented when interacting with an unspotted roamable
	 *  trainer while carrying the Bowie Knife -- see openBackstabChoice(). */
	backstabCur = 0;
	pendingBackstab: { npc: any; pending: string; after: string; talk: string; levels: number } | null = null;
	quarryCrateLooted = false;
	quarryShelfSearched = false;
	cageOpen = false;
	mason2Map: string | null = null;
	mason2Done = false;
	masonRematch = false;
	talkedReach = false;
	dexSeen = 0;
	dexCaught = 0;
	dexCursor = 0;
	dexView = "list";
	fade = { phase: "off" as "off" | "out" | "hold" | "in", t: 0, action: null as null | "bed" | "loss" | "execute" | "hfGameOver" | "priestessTeleport" };
	pendingWs = null;
	choiceCur = 0;
	shopKeep: string = "bram";
	/** Per-keeper, per-item units left on the shelf (1-10, rolled fresh
	 *  by rollShopStock()). Never persisted -- session/rest-scoped, not
	 *  save state, see CURRENT_WORK.md. */
	shopStock: Record<string, Record<string, number>> = {};
	/** -100..100, see logic.json reputation. */
	reputation = 0;
	/** Post-battle mercy menu (Leg 2.9). */
	mercyCur = 0;
	mercyTrainer = null;
	mercySoldierId = null;
	mercyFoeLevels = 0;
	mercyFoeName = "";
	/** Bitmask of permanently executed trainers (Leg 2.9.4). */
	executedMask = 0;
	shopFreeBram = false;
	shopFreeOren = false;
	shopFreeFenn = false;
	shopFreeDray = false;
	doorLock = 0;
	hudFlash = "";
	hudT = 0;
	mapBanner = "";
	mapBannerT = 0;
	talkLock = 0;
	lastTx = -1;
	lastTy = -1;
	unsub = null;
	raf = 0;
	// pause / continue live on the shared save blob
	titleCursor = 0;
	pauseCursor = 0;
	hasSave = false;
	lastAutosave = 0;
	visHook = null;
	constructor(canvas) {
		this.canvas = canvas;
		const ctx = canvas.getContext("2d");
		if (!ctx) throw new Error("canvas");
		this.ctx = ctx;
		canvas.width = VIEW_W;
		canvas.height = VIEW_H;
	}
	async boot() {
		this.reset();
		this.unsub = this.input.attach(this.canvas);
		this.canvas.addEventListener("pointerdown", () => this.audio.unlock(), { once: true });
		this.wireProbe();
		this.visHook = () => {
			if (document.hidden) this.persist(false);
			else this.audio.unlock();
		};
		document.addEventListener("visibilitychange", this.visHook);
		await this.loadArtCritical();
		this.ready = true;
		void this.loadArtRest();
	}
	criticalArtKeys() {
		return new Set([
			"bg",
			"max-down-1", "max-down-2", "max-down-3", "max-down-4",
			"max-up-1", "max-left-1", "max-right-1",
			"quillpup-1", "quillpup-2",
			"prop-bed-empty", "prop-shelf", "prop-crate",
			"prop-door", "prop-cart", "prop-stump", "prop-herb", "prop-moonstone",
		]);
	}
	async loadArtCritical() {
		const all = artManifest();
		const prefer = this.criticalArtKeys();
		await this.loadArtChunk(all.filter(([k]) => prefer.has(k)));
	}
	async loadArtRest() {
		const all = artManifest();
		const prefer = this.criticalArtKeys();
		await this.loadArtChunk(all.filter(([k]) => !prefer.has(k)));
	}
	async loadArt() {
		await this.loadArtCritical();
		await this.loadArtRest();
	}
	async loadArtChunk(list) {
		const conc = 8;
		for (let i = 0; i < list.length; i += conc) {
			const chunk = list.slice(i, i + conc);
			const loaded = await Promise.all(chunk.map(async ([k, src]) => {
				try {
					return [k, await loadImg(src)];
				} catch {
					return [k, null];
				}
			}));
			for (const [k, im] of loaded) if (im) this.images[k] = im;
		}
	}
	reset() {
		this.acc = 0;
		this.shake = 0;
		this.clock = 0;
		this.lastAutosave = 0;
		this.mode = "title";
		this.introI = 0;
		this.endI = 0;
		this.party = [];
		this.partyIndex = 0;
		this.party2 = [];
		this.activeParty = 0;
		this.party2Index = 0;
		this.bag = { ...START_BAG };
		this.marks = START_MARKS;
		this.talkQ = [];
		this.talkI = 0;
		this.afterTalk = null;
		this.bagCursor = 0;
		this.partyCursor = 0;
		this.partyView = "list";
		this.actCursor = 0;
		this.moveCursor = 0;
		this.pendingItem = null;
		this.pendingCatch = null;
		this.shopTab = "buy";
		this.shopCursor = 0;
		const p = spawnOf(HOUSE, "P");
		this.world = {
			mapId: "house",
			x: p.x,
			y: p.y,
			dir: "down",
			moving: false,
			frame: 0,
			anim: 0,
			encounterLock: 20
		};
		this.battle = null;
		this.talkedFather = false;
		this.tookStarter = false;
		this.talkedWren = false;
		this.talkedMae = false;
		this.beatCalder = false;
		this.lootedCrate = false;
		this.talkedIvo = false;
		this.talkedNell = false;
		this.nellBonus = false;
		this.talkedPike = false;
		this.pikeHelped = false;
		this.gotHerb = false;
		this.gotFieldGem = false;
		this.gotStump = false;
		this.readCart = false;
		this.caughtOnce = false;
		this.foughtMason = false;
		this.battlesDone = 0;
		this.anneGifted = false;
		this.cathleenCaught = false;
		this.beatCathleen = false;
		this.beatShinigami = false;
		this.sawShinigamiRock = false;
		this.hasScroll = false;
		this.anne2Told = false;
		this.tessaGifted = false;
		this.birchGifted = false;
		this.sableGifted = false;
		this.chestLooted = false;
		this.beatCross = false;
		this.beatConscript = false;
		this.beatEnforcer = false;
		this.beatSentry = false;
		this.beatForestRanger = false;
		this.beatForestScout = false;
		this.beatRuinsKeeper = false;
		this.beatRuinsWarden = false;
		this.beatMarshBog = false;
		this.beatMarshReed = false;
		this.badgeQuartz = false;
		this.badgeOpal = false;
		this.beatQuarryDriller = false;
		this.choseHeavenfall = false;
		this.revivedFather = false;
		this.beatCommander = false;
		this.beatLieutenantLead = false;
		this.heavenfallRepWarned = false;
		this.drayKnifeOffered = false;
		this.backstabCur = 0;
		this.pendingBackstab = null;
		this.quarryCrateLooted = false;
		this.quarryShelfSearched = false;
		this.cageOpen = false;
		this.mason2Map = null;
		this.mason2Done = false;
		this.masonRematch = false;
		this.talkedReach = false;
		this.dexSeen = 0;
		this.dexCaught = 0;
		this.dexCursor = 0;
		this.dexView = "list";
		this.fade = { phase: "off", t: 0, action: null };
		this.pendingWs = null;
		this.choiceCur = 0;
		this.shopKeep = "bram";
		this.shopStock = {};
		this.reputation = 0;
		this.executedMask = 0;
		this.shopFreeBram = false;
		this.shopFreeOren = false;
		this.shopFreeFenn = false;
		this.shopFreeDray = false;
		this.rival = {
			phase: "off",
			x: 0,
			y: 0,
			dir: "up",
			frame: 0,
			anim: 0
		};
		this.anne = {
			phase: "off",
			x: 0,
			y: 0,
			dir: "up",
			frame: 0,
			anim: 0
		};
		this.soldiers = [];
		this.pendingSoldier = null;
		this.roamers = {};
		this.doorLock = 0;
		this.hudFlash = "";
		this.hudT = 0;
		this.mapBanner = "";
		this.mapBannerT = 0;
		this.talkLock = 0;
		this.lastTx = -1;
		this.lastTy = -1;
		this.titleCursor = 0;
		this.pauseCursor = 0;
		this.hasSave = saveExists();
		if (!this.hasSave) this.titleCursor = 1;
	}
	snapshot() {
		const flags = {};
		for (const k of SAVE_FLAGS) {
			if (k === "soldierBeaten0") flags[k] = !!this.soldiers[0]?.beaten;
			else if (k === "soldierBeaten1") flags[k] = !!this.soldiers[1]?.beaten;
			else if (k === "soldierBeaten2") flags[k] = !!this.soldiers[2]?.beaten;
			else flags[k] = !!this[k];
		}
		return {
			mapId: this.world.mapId,
			x: this.world.x,
			y: this.world.y,
			dir: this.world.dir,
			marks: this.marks,
			partyIndex: this.partyIndex,
			battlesDone: this.battlesDone,
			mason2Map: this.mason2Map,
			reputation: this.reputation,
			executedMask: this.executedMask,
			bag: { ...this.bag },
			flags,
			party: (this.activeParty === 1 ? this.party2 : this.party).map((m) => ({ ...m })),
			party2: (this.activeParty === 1 ? this.party : this.party2).map((m) => ({ ...m })),
			activeParty: this.activeParty,
			dexSeen: this.dexSeen >>> 0,
			dexCaught: this.dexCaught >>> 0,
		};
	}
	applySave(snap) {
		if (!snap) return false;
		this.world.mapId = snap.mapId;
		this.world.x = snap.x;
		this.world.y = snap.y;
		this.world.dir = snap.dir;
		this.world.moving = false;
		this.world.encounterLock = 8;
		this.marks = snap.marks;
		this.party = snap.party.map((m) => ({
			...m,
			name: SPECIES[m.species]?.name ?? m.name,
			nature: m.nature ?? 0,
		}));
		this.party2 = (snap.party2 || []).map((m) => ({
			...m,
			name: SPECIES[m.species]?.name ?? m.name,
			nature: m.nature ?? 0,
		}));
		this.activeParty = snap.activeParty ? 1 : 0;
		this.party2Index = 0;
		// If save says Father was active, swap so this.party is the controlled set.
		if (this.activeParty === 1 && this.party2.length) {
			const tmp = this.party;
			this.party = this.party2;
			this.party2 = tmp;
		}
		this.partyIndex = Math.min(snap.partyIndex, Math.max(0, this.party.length - 1));
		this.battlesDone = snap.battlesDone;
		this.mason2Map = snap.mason2Map;
		this.reputation = snap.reputation ?? 0;
		this.executedMask = snap.executedMask ?? 0;
		this.adjustReputation(0);
		this.bag = { ...START_BAG, ...snap.bag };
		this.dexSeen = snap.dexSeen >>> 0;
		this.dexCaught = snap.dexCaught >>> 0;
		for (const m of this.party) this.markCaught(m.species);
		for (const k of SAVE_FLAGS) {
			if (k.startsWith("soldierBeaten")) continue;
			if (k in this) this[k] = !!snap.flags[k];
		}
		if (this.world.mapId === "forest" || snap.flags.soldierBeaten0 || snap.flags.soldierBeaten1 || snap.flags.soldierBeaten2) {
			this.ensureSoldiers();
			if (this.soldiers[0]) this.soldiers[0].beaten = !!snap.flags.soldierBeaten0;
			if (this.soldiers[1]) this.soldiers[1].beaten = !!snap.flags.soldierBeaten1;
			if (this.soldiers[2]) this.soldiers[2].beaten = !!snap.flags.soldierBeaten2;
		}
		this.rival.phase = this.foughtMason ? "off" : "off";
		this.anne.phase = "off";
		this.mode = "world";
		this.talkQ = [];
		this.afterTalk = null;
		this.battle = null;
		this.announceMap();
		return true;
	}
	/** Autosave disabled entirely -- every non-manual call is a no-op.
	 *  Loading last save was breaking because the game wrote over the slot
	 *  constantly (on nearly every warp, NPC grant, etc.), so "continue"
	 *  never actually resumed where the player expected. The pause menu's
	 *  explicit Save (and the dev saveNow() hook) still work normally;
	 *  they're the only path that reaches writeSaveBlob() now. */
	persist(manual = false) {
		if (!manual) return false;
		if (this.mode === "battle") return false;
		const ok = writeSaveBlob(packSave(this.snapshot()));
		if (ok) {
			this.hasSave = true;
			this.lastAutosave = this.clock;
			this.note("Saved.");
			this.audio.save();
		} else {
			this.note("Save failed.");
			this.audio.miss();
		}
		return ok;
	}
	tryContinue() {
		const snap = unpackSave(readSaveBlob() || new Uint8Array());
		if (!snap) {
			try { localStorage.removeItem("crymon.save.v1"); } catch { /* ignore */ }
			this.hasSave = false;
			this.audio.miss();
			this.note("No save.");
			return false;
		}
		this.reset();
		this.applySave(snap);
		this.audio.ok();
		return true;
	}
	sceneSong() {
		if (this.mode === "title" || this.mode === "ending") return this.mode === "ending" ? ENDING_SONG : TITLE_SONG;
		if (this.mode === "intro") return "home";
		if (this.mode === "battle") return this.battle && !this.battle.wild ? TRAINER_SONG : BATTLE_SONG;
		return MAP_SONG[this.world.mapId] || TITLE_SONG;
	}
	startLoop() {
		if (this.running) return;
		this.running = true;
		this.last = performance.now();
		const tick = (now) => {
			if (!this.running) return;
			let dt = (now - this.last) / 1e3;
			this.last = now;
			dt = Math.min(dt, .1);
			this.acc += dt;
			this.input.pollGamepad();
			// Turbo button held: queue one extra confirm tap per rendered
			// frame (up to the display's refresh rate) -- each system's own
			// cooldown (talkLock, battle phase transitions) still paces how
			// often that tap actually advances anything, same as it would
			// for a human mashing the real button. Held keyboard T does the
			// same thing as holding the on-screen Turbo button -- checked
			// here rather than folded into turboHeld itself, since that
			// field is also what drives the on-screen button's own visual
			// pressed state (crymon-app.tsx's TurboBtn), which shouldn't
			// light up just because T is held.
			if (this.input.turboHeld || this.input.held("KeyT")) this.input.queueA();
			// stepBegin()/stepEnd() bracket each fixed-timestep tick (not each
			// rendered frame -- see their doc comment in input.ts) so edge
			// detection stays correct regardless of how many logic ticks a
			// given rendered frame contains.
			while (this.acc >= STEP) {
				this.input.stepBegin();
				this.update(STEP);
				this.input.stepEnd();
				this.acc -= STEP;
			}
			this.draw();
			this.raf = requestAnimationFrame(tick);
		};
		this.raf = requestAnimationFrame(tick);
	}
	stop() {
		this.running = false;
		cancelAnimationFrame(this.raf);
		this.unsub?.();
		if (this.visHook) document.removeEventListener("visibilitychange", this.visHook);
	}
	lead() {
		const cur = this.party[this.partyIndex];
		if (cur && cur.hp > 0) return cur;
		const i = this.party.findIndex((m) => m.hp > 0);
		if (i >= 0) this.partyIndex = i;
		return this.party[this.partyIndex];
	}
	skipToWorld(mapId = "veld") {
		this.mode = "world";
		this.world.mapId = mapId;
		this.tookStarter = true;
		if (this.party.length === 0) {
			this.party = [mintMonster("quillpup", 3)];
			this.partyIndex = 0;
			this.markCaught("quillpup");
		}
		if (mapId === "veld") {
			const s = spawnOf(VELD, "D");
			this.world.x = s.x;
			this.world.y = s.y + TILE + 8;
			this.world.dir = "down";
		} else if (mapId === "forest") {
			this.ensureSoldiers();
			const s = spawnOf(FOREST, "Y");
			this.world.x = s.x;
			this.world.y = s.y + TILE + 8;
			this.world.dir = "down";
		} else if (mapId === "grove") {
			const s = spawnOf(GROVE, "O");
			this.world.x = s.x;
			this.world.y = s.y + TILE + 8;
			this.world.dir = "down";
		} else if (mapId === "camp") {
			this.beatCalder = true;
			const s = spawnOf(CAMP, "D");
			this.world.x = s.x;
			this.world.y = s.y + TILE + 8;
			this.world.dir = "down";
		} else if (mapId === "cliffs") {
			const s = spawnOf(CLIFFS, "D");
			this.world.x = s.x + TILE + 8;
			this.world.y = s.y;
			this.world.dir = "right";
		} else if (mapId === "ruins") {
			this.beatShinigami = true;
			this.hasScroll = true;
			const s = spawnOf(RUINS, "D");
			this.world.x = s.x;
			this.world.y = s.y + TILE + 8;
			this.world.dir = "down";
		} else if (mapId === "reach") {
			this.beatShinigami = true;
			this.hasScroll = true;
			const s = spawnOf(REACH, "D");
			this.world.x = s.x;
			this.world.y = s.y + TILE + 8;
			this.world.dir = "down";
		} else if (mapId === "marsh") {
			const s = spawnOf(MARSH, "Y");
			this.world.x = s.x;
			this.world.y = s.y + TILE + 8;
			this.world.dir = "down";
		} else if (mapId === "quarry") {
			const s = spawnOf(QUARRY, "D");
			this.world.x = s.x;
			this.world.y = s.y + TILE + 8;
			this.world.dir = "down";
		} else {
			const s = spawnOf(HOUSE, "P");
			this.world.x = s.x;
			this.world.y = s.y;
			this.world.dir = "down";
		}
		this.world.encounterLock = 3;
		this.battle = null;
		this.lastTx = -1;
		this.lastTy = -1;
		this.hudT = 0;
		this.hudFlash = "";
		this.talkLock = 0;
		this.talkQ = [];
		this.afterTalk = null;
	}
	wireProbe() {
		window.__controlsTest = {
			getYaw: () => -this.world.x * .04,
			getSpeed: () => this.world.moving ? 1 : 0,
			getX: () => this.world.x,
			getY: () => this.world.y,
			setKeys: (codes) => {
				this.input.injected = codes.length ? codes : null;
			},
			skipToWorld: () => this.skipToWorld("veld")
		};
		window.__crymon = {
			getMode: () => this.mode,
			getPhase: () => this.battle?.phase ?? null,
			getMap: () => this.world.mapId,
			skipToWorld: () => this.skipToWorld("veld"),
			skipToHouse: () => this.skipToWorld("house"),
			skipToForest: () => this.skipToWorld("forest"),
			skipToGrove: () => this.skipToWorld("grove"),
			skipToCamp: () => this.skipToWorld("camp"),
			skipToCliffs: () => this.skipToWorld("cliffs"),
			skipToRuins: () => this.skipToWorld("ruins"),
			skipToReach: () => this.skipToWorld("reach"),
			skipToMarsh: () => this.skipToWorld("marsh"),
			skipToQuarry: () => this.skipToWorld("quarry"),
			resetRun: () => {
				this.reset();
				this.skipToWorld("veld");
			},
			tapConfirm: () => this.input.queueA(),
			tapStart: () => this.input.queueStart(),
			tapSelect: () => this.input.queueSelect(),
			pos: () => ({
				x: this.world.x,
				y: this.world.y,
				dir: this.world.dir,
				map: this.world.mapId
			}),
			hud: () => ({
				t: this.hudT,
				text: this.hudFlash,
				talk: this.talkQ[this.talkI]?.text ?? ""
			}),
			setPos: (x, y) => {
				this.world.x = x;
				this.world.y = y;
			},
			spawnRival: () => {
				this.skipToWorld("veld");
				this.rival = {
					phase: "approach",
					x: this.world.x,
					y: this.world.y + 160,
					dir: "up",
					frame: 0,
					anim: 0
				};
			},
			placeMason: () => {
				if (this.world.mapId !== "veld" || this.mode !== "world") this.skipToWorld("veld");
				this.rival = {
					phase: "done",
					x: this.world.x + 48,
					y: this.world.y + 4,
					dir: "down",
					frame: 0,
					anim: 0
				};
			},
			spawnAnne: () => {
				this.skipToWorld("veld");
				this.battlesDone = Math.max(1, this.battlesDone);
				this.anneGifted = false;
				this.anne = {
					phase: "approach",
					x: this.world.x,
					y: this.world.y + 72,
					dir: "up",
					frame: 0,
					anim: 0
				};
			},
			flags: () => ({
				talkedFather: this.talkedFather,
				tookStarter: this.tookStarter,
				talkedWren: this.talkedWren,
				talkedMae: this.talkedMae,
				talkedIvo: this.talkedIvo,
				talkedNell: this.talkedNell,
				talkedPike: this.talkedPike,
				pikeHelped: this.pikeHelped,
				herb: this.gotHerb,
				gem: this.gotFieldGem,
				stump: this.gotStump,
				cart: this.readCart,
				calder: this.beatCalder,
				mason: this.foughtMason,
				rival: this.rival.phase,
				anne: this.anne.phase,
				anneGifted: this.anneGifted,
				battles: this.battlesDone,
				marks: this.marks,
				beatCathleen: this.beatCathleen,
				beatShinigami: this.beatShinigami,
				hasScroll: this.hasScroll,
				talkedReach: this.talkedReach,
				dexSeen: this.dexSeen,
				dexCaught: this.dexCaught,
				anne2Told: this.anne2Told,
				beatSentry: this.beatSentry,
				beatForestRanger: this.beatForestRanger,
				beatForestScout: this.beatForestScout,
				beatRuinsKeeper: this.beatRuinsKeeper,
				beatRuinsWarden: this.beatRuinsWarden,
				beatMarshBog: this.beatMarshBog,
				beatMarshReed: this.beatMarshReed,
				badgeQuartz: this.badgeQuartz,
				badgeOpal: this.badgeOpal,
				beatQuarryDriller: this.beatQuarryDriller,
				choseHeavenfall: this.choseHeavenfall,
				gauntletUnlocked: this.gauntletUnlocked,
				gauntletWipeRegret: this.gauntletWipeRegret,
				titleSlayer: this.titleSlayer,
				titleTamer: this.titleTamer,
				revivedFather: this.revivedFather,
				beatCommander: this.beatCommander,
				beatLieutenantLead: this.beatLieutenantLead,
				beatHeavenfall: this.beatHeavenfall,
				heavenfallRepWarned: this.heavenfallRepWarned,
			quarryCrateLooted: this.quarryCrateLooted,
			quarryShelfSearched: this.quarryShelfSearched,
				beatConscript: this.beatConscript,
				beatEnforcer: this.beatEnforcer,
				beatCross: this.beatCross,
				cageOpen: this.cageOpen,
				chestLooted: this.chestLooted
			}),
			setFlag: (k, v) => {
				this[k] = v;
			},
			forceWild: () => {
				this.skipToWorld("veld");
				this.startBattle(mintMonster("glimmoth", 2), true, "A wild Glimmoth");
			},
			forceWildId: (id) => {
				this.skipToWorld("forest");
				const s = SPECIES[id];
				if (!s) return;
				this.startBattle(mintMonster(id, 4), true, `A wild ${s.name}`);
			},
			forceCalder: () => {
				this.skipToWorld("veld");
				this.startBattle(mintMonster("razorbat", 4), false, "Calder sends Razorbat", "calder");
			},
			forceForest: () => this.skipToWorld("forest"),
			forceSoldier: () => {
				this.skipToWorld("forest");
				const sol = this.soldiers.find((s) => !s.beaten) ?? this.soldiers[0];
				if (sol) {
					this.pendingSoldier = sol.id;
					this.startBattle(mintMonster(sol.species, sol.level), false, `${sol.name} sends ${SPECIES[sol.species].name}`, "soldier", sol.id);
				}
			},
			party: () => this.party,
			bag: () => this.bag,
			fillParty: () => {
				const ids = ["glimmoth", "tortcask", "ashenmaw", "sableclaw", "emberling"];
				for (const id of ids) {
					if (this.party.length >= PARTY_MAX) break;
					this.party.push(mintMonster(id, 4));
					this.markCaught(id);
				}
			},
			openParty: (view = "list") => this.openParty(view),
			pendingCatch: () => this.pendingCatch,
			setPendingCatch: (id = "fenwisp") => {
				this.pendingCatch = mintMonster(id, 5);
			},
			hasSave: () => this.hasSave,
			saveNow: () => this.persist(true),
			continueSave: () => this.tryContinue(),
			openPause: () => this.openPause(),
			openCryDex: () => this.openCryDex(),
			setTitleCursor: (n) => { this.titleCursor = n; },
			sceneSong: () => this.sceneSong(),
			wipeSave: () => {
				try { localStorage.removeItem("crymon.save.v1"); } catch { /* ignore */ }
				this.hasSave = false;
			},
			debug: () => ({
				mode: this.mode,
				cur: this.titleCursor,
				running: this.running,
				clock: Math.round(this.clock * 10) / 10,
			}),
		};
	}
	map() {
		return MAPS[this.world.mapId];
	}
	note(s) {
		this.hudFlash = s;
		this.hudT = 12;
	}
	announceMap() {
		this.mapBanner = MAP_NAME[this.world.mapId] ?? this.world.mapId.toUpperCase();
		this.mapBannerT = 2.4;
	}
	say(beats, after: TalkAfter = null) {
		this.talkQ = beats;
		this.talkI = 0;
		this.afterTalk = after;
		this.hudT = 0;
		this.hudFlash = "";
		this.audio.ui();
	}
	talking() {
		return this.talkI < this.talkQ.length;
	}
	beat() {
		return this.talkQ[this.talkI] ?? null;
	}
	advanceTalk() {
		this.talkI += 1;
		this.talkLock = .15;
		if (this.talkI >= this.talkQ.length) {
			this.talkQ = [];
			this.talkI = 0;
			const next = this.afterTalk;
			this.afterTalk = null;
			if (next && next.startsWith("shop:")) {
				const keep = next.slice("shop:".length);
				const refuseAt = LOGIC.reputation?.refuseAt ?? -100;
				if (this.reputation <= refuseAt) this.say(TALK.shopRefuse);
				else this.openShop(keep);
			} else if (next === "drayKnifeShop") {
				// Complete the offer dialogue, then open Dray's shop with the
				// knife added to his existing stock -- not replacing it.
				// shopCatalog() already includes bowieKnife now that
				// drayKnifeOffered is true, so a fresh roll picks it up on
				// its own; if his stock was already rolled this session
				// (e.g. visited before reputation went negative), merge the
				// knife in rather than re-rolling everything else. Either
				// way there's only ever one in the game, so its quantity is
				// forced to 1 regardless of the roll.
				this.shopKeep = "dray";
				if (!this.shopStock.dray) this.rollShopStock("dray");
				this.shopStock.dray.bowieKnife = 1;
				this.mode = "shop";
				this.shopTab = "buy";
				this.shopCursor = 0;
				this.audio.ui();
			}
			else if (next === "mason") {
				const kit = TRAINERS.mason;
				this.foughtMason = true;
				this.startBattle(mintMonster(kit.lead[0], kit.lead[1]), false, kit.title, "mason");
			} else if (next === "calder") {
				const kit = TRAINERS.calder;
				this.startBattle(mintMonster(kit.lead[0], kit.lead[1]), false, kit.title, "calder");
			} else if (next === "soldier") {
				const sol = this.soldiers.find((s) => s.id === this.pendingSoldier);
				if (sol && !sol.beaten) this.startBattle(mintMonster(sol.species, sol.level), false, `${sol.name} sends ${SPECIES[sol.species].name}`, "soldier", sol.id);
			} else if (next === "cathleen") {
				if (!this.cathleenCaught) {
					const kit = TRAINERS.cathleen;
					this.startBattle(mintMonster(kit.lead[0], kit.lead[1]), true, kit.title, "wild");
				}
			} else if (next === "shinigami") {
				if (!this.beatShinigami) {
					const kit = TRAINERS.shinigami;
					const bench = (kit.bench || []).map((b) => mintMonster(b[0], b[1]));
					this.startBattle(
						mintMonster(kit.lead[0], kit.lead[1]),
						false,
						kit.title,
						"shinigami",
						null,
						bench
					);
				}
			} else if (next === "anneLeave") {
				this.startAnneLeave();
			} else if (next === "masonLeave") {
				this.startMasonLeave();
			} else if (next === "bedHeal") {
				this.startFade("bed");
			} else if (next === "mason2") {
				const kit = LOGIC.masonRematch.battle;
				this.startBattle(
					mintMonster(kit.lead[0], kit.lead[1]),					false,
					kit.title,
					"mason2",
					null,
					kit.bench.map((b) => mintMonster(b[0], b[1]))
				);
			} else if (next === "choice") {
				this.mode = "choice";
				this.choiceCur = 0;
			} else if (next === "wsoldier") {
				this.startWsBattle(this.pendingWs);
			} else if (next === "hfGameOver") {
				this.runHeavenfallGameOverFx();
			} else if (next === "ending") {
				/* 2.4: Father stays in world; Heavenfall path only unlocks gauntlet (choseHeavenfall). */
				if (this.choseHeavenfall) {
					this.gauntletUnlocked = true;
				}
			} else if (next === "creditsFinal") {
				this.mode = "ending";
				this.endI = 0;
			} else if (next === "priestessTeleport") {
				this.startFade("priestessTeleport");
			}
			this.maybeStartAnne();
		}
	}
	ownedItems() {
		return ITEM_ORDER.filter((id) => this.bag[id] > 0);
	}
	openPause() {
		this.mode = "pause";
		this.pauseCursor = 0;
		this.audio.ui();
	}
	updatePause() {
		const rows = ["Party", "Bag", "CryDex", "Map", "Settings", "Save", "Close"];
		if (this.input.up()) {
			this.pauseCursor = (this.pauseCursor + rows.length - 1) % rows.length;
			this.audio.ui();
		}
		if (this.input.down()) {
			this.pauseCursor = (this.pauseCursor + 1) % rows.length;
			this.audio.ui();
		}
		if (this.input.cancel()) {
			this.mode = "world";
			this.audio.ui();
			return;
		}
		if (this.input.confirm() || (this.input.start() && this.pauseCursor === 6)) {
			if (this.pauseCursor === 0) this.openParty();
			else if (this.pauseCursor === 1) this.openBag();
			else if (this.pauseCursor === 2) this.openCryDex();
			else if (this.pauseCursor === 3) this.openTownMap();
			else if (this.pauseCursor === 4) this.openSettings();
			else if (this.pauseCursor === 5) {
				this.mode = "world";
				this.persist(true);
			} else {
				this.mode = "world";
				this.audio.ui();
			}
		} else if (this.input.start()) {
			this.mode = "world";
			this.audio.ui();
		}
	}

	openSettings() {
		this.mode = "settings";
		this.audio.ui();
	}
	updateSettings() {
		if (this.input.cancel() || this.input.start() || this.input.confirm()) {
			this.mode = "pause";
			this.audio.ui();
			return;
		}
		if (this.input.up()) {
			this.audio.nudgeVolume(1);
			this.audio.ui();
		}
		if (this.input.down()) {
			this.audio.nudgeVolume(-1);
			this.audio.ui();
		}
	}
	drawSettings() {
		this.drawWorld();
		this.ctx.fillStyle = "rgba(18,17,14,0.55)";
		this.ctx.fillRect(0, 0, VIEW_W, VIEW_H);
		this.box(X(8), Y(6), X(224), Y(148));
		this.text("SETTINGS", X(16), Y(10), "#c5cec6", FONT);
		const pct = this.audio.volumePct();
		this.text("VOLUME", X(16), Y(40), "#c5cec6", FONT);
		this.text(`${pct}%`, X(180), Y(40), "#e8e4d8", FONT);
		const bx = X(16), by = Y(58), bw = X(200), bh = Y(10);
		this.ctx.fillStyle = "#2a2620";
		this.ctx.fillRect(bx, by, bw, bh);
		const fill = Math.max(0, Math.min(1, this.audio.volume / VOLUME.max));
		this.ctx.fillStyle = "#5a7a52";
		this.ctx.fillRect(bx, by, Math.round(bw * fill), bh);
		this.text("UP louder   DOWN quieter", X(16), Y(80), "#8a8678", FONT);
		this.text("200% is twice the old max", X(16), Y(96), "#8a8678", FONT);
		this.text("Z / X  back", X(16), Y(148), "#5a7a52", FONT);
	}

	openTownMap() {
		this.mode = "townmap";
		this.audio.ui();
	}
	updateTownMap() {
		if (this.input.cancel() || this.input.start() || this.input.confirm()) {
			this.mode = "pause";
			this.audio.ui();
		}
	}
	townMapRegionId() {
		const mapId = this.world.mapId;
		const nodes = TOWN_MAP?.nodes ?? [];
		for (const n of nodes) {
			if (n.playableMaps?.includes(mapId)) return n.id;
		}
		return TOWN_MAP?.anchor ?? "veld";
	}
	drawTownMap() {
		const nodes = TOWN_MAP?.nodes ?? [];
		if (!nodes.length) {
			this.panel(20, 20, 280, 200);
			this.text("No map data.", X(160), Y(110), "#e8e4d8", FONT, "center");
			return;
		}
		this.panel(12, 12, 296, 216);
		const ctx = this.ctx;
		ctx.save();
		ctx.imageSmoothingEnabled = false;
		this.text(TOWN_MAP?.name ?? "Sorrow County", X(160), Y(26), "#e8f0d8", FONT, "center");

		const mapX = 24;
		const mapY = 36;
		const mapW = 272;
		const mapH = 150;

		// Every cell is the same flat beige -- a colored-by-kind fill or an
		// internal "path stripe" implies a specific correct sub-path through
		// the cell that isn't real (the cell is a simplified proportional
		// footprint, not a tile-traced route). Only the gem markers get color.
		const CELL_FILL = "#d4c49a";
		const CELL_STROKE = "#8a7a55";

		const minX = Math.min(...nodes.map((n) => n.x));
		const minY = Math.min(...nodes.map((n) => n.y));
		const maxX = Math.max(...nodes.map((n) => n.x + (n.cellW ?? 1)));
		const maxY = Math.max(...nodes.map((n) => n.y + (n.cellH ?? 1)));
		const gw = maxX - minX;
		const gh = maxY - minY;
		const cell = Math.max(2, Math.min(Math.floor(mapW / gw), Math.floor(mapH / gh)));
		const ox = mapX + Math.floor((mapW - gw * cell) / 2);
		const oy = mapY + Math.floor((mapH - gh * cell) / 2);
		const here = this.townMapRegionId();

		for (const n of nodes) {
			const cw = n.cellW ?? 1;
			const ch = n.cellH ?? 1;
			const x = ox + (n.x - minX) * cell;
			const y = oy + (n.y - minY) * cell;
			const w = cw * cell;
			const h = ch * cell;
			ctx.fillStyle = CELL_FILL;
			ctx.fillRect(x, y, w, h);
			ctx.strokeStyle = CELL_STROKE;
			ctx.lineWidth = 0.5;
			ctx.strokeRect(x, y, w, h);
		}
		for (const n of nodes) {
			const cw = n.cellW ?? 1;
			const ch = n.cellH ?? 1;
			const x = ox + (n.x - minX) * cell;
			const y = oy + (n.y - minY) * cell;
			const cx = x + (cw * cell) / 2;
			const isHere = n.id === here;
			// Gauntlet's label sits in the vertical middle of the long corridor
			// it represents, not pinned to the top edge.
			const labelInMiddle = n.id === "gauntlet_route";
			const labelY = labelInMiddle ? y + (ch * cell) / 2 + 3 : y + Math.max(4, cell * 0.5);
			this.text(n.label, X(cx), Y(labelY), isHere ? "#ffe08a" : "#f0ecd8", 8, "center");
			if (n.gem) {
				const gy = y + (ch * cell) / 2;
				ctx.fillStyle = "#0a2f52";
				ctx.beginPath();
				ctx.arc(cx, gy, Math.max(3, cell * 0.3), 0, Math.PI * 2);
				ctx.fill();
				ctx.fillStyle = isHere ? "#a0e0ff" : "#29b6ff";
				ctx.beginPath();
				ctx.moveTo(cx, gy - 4);
				ctx.lineTo(cx + 3, gy);
				ctx.lineTo(cx, gy + 4);
				ctx.lineTo(cx - 3, gy);
				ctx.closePath();
				ctx.fill();
			} else if (isHere) {
				const gy = y + (ch * cell) / 2;
				ctx.fillStyle = "#ffe08a";
				ctx.fillRect(cx - 2, gy - 2, 4, 4);
			}
		}
		ctx.restore();
		const hereLabel = nodes.find((n) => n.id === here)?.label ?? here;
		this.text("You are here: " + hereLabel, X(160), Y(210), "#a8c090", 10, "center");
		this.text("B / Start: back", X(160), Y(222), "#7a7868", 10, "center");
	}

	openCryDex() {
		this.mode = "crydex";
		this.dexCursor = 0;
		this.dexView = "list";
		this.audio.ui();
	}
	dexBit(id) {
		const i = SAVE_SPECIES.indexOf(id);
		return i >= 0 && i < 32 ? (1 << i) : 0;
	}
	markSeen(id) {
		this.dexSeen |= this.dexBit(id);
	}
	markCaught(id) {
		this.markSeen(id);
		this.dexCaught |= this.dexBit(id);
	}
	updateCryDex() {
		const n = SAVE_SPECIES.length;
		if (this.dexView === "entry") {
			if (this.input.cancel() || this.input.confirm() || this.input.start()) {
				this.dexView = "list";
				this.audio.ui();
			}
			return;
		}
		if (this.input.up()) {
			this.dexCursor = (this.dexCursor + n - 1) % n;
			this.audio.ui();
		}
		if (this.input.down()) {
			this.dexCursor = (this.dexCursor + 1) % n;
			this.audio.ui();
		}
		if (this.input.confirm()) {
			const id = SAVE_SPECIES[this.dexCursor];
			if (id && (this.dexCaught & this.dexBit(id))) {
				this.dexView = "entry";
				this.audio.ui();
			} else this.audio.miss();
		}
		if (this.input.cancel() || this.input.start()) {
			this.mode = "world";
			this.audio.ui();
		}
	}
	openBag() {
		this.mode = "bag";
		this.bagCursor = 0;
		this.pendingItem = null;
		this.audio.ui();
	}
	openParty(view = "list") {
		this.mode = "party";
		this.partyView = view;
		this.partyCursor = clamp(this.partyCursor, 0, Math.max(0, this.party.length - 1));
		this.actCursor = 0;
		this.audio.ui();
	}
	/** Every item a keeper CAN carry, independent of current stock
	 *  levels -- the set rollShopStock() rolls quantities for. */
	shopCatalog(keeper: string) {
		const stock = LOGIC.shops?.crystalStock ?? {};
		const allowed: string[] = stock[keeper] ?? stock.default ?? [];
		const list = ITEM_ORDER.filter((id) => {
			if (ITEMS[id].buy <= 0) return false;
			if (ITEMS[id].effect?.kind === "capture") return allowed.includes(id);
			// Only Dray sells the Bowie Knife, only after his one-time
			// reputation-warning line has fired, and only until the
			// player actually owns one -- there's only ever one in the
			// game (see openShop()/openBackstabChoice()).
			if (id === "bowieKnife") return keeper === "dray" && this.drayKnifeOffered && !this.bag.bowieKnife;
			return true;
		});
		// Bowie Knife always leads Dray's shelf when it is in stock.
		if (list.includes("bowieKnife")) {
			return ["bowieKnife", ...list.filter((id) => id !== "bowieKnife")];
		}
		return list;
	}
	/** 1-10 units of every item this keeper carries. Called on every
	 *  rest (sleepHeal) for all keepers at once, and lazily the first
	 *  time a given keeper's shop is opened this session. */
	rollShopStock(keeper: string) {
		const s: Record<string, number> = {};
		for (const id of this.shopCatalog(keeper)) s[id] = 1 + Math.floor(Math.random() * 10);
		this.shopStock[keeper] = s;
	}
	rollAllShopStock() {
		for (const k of Object.keys(SHOP_FREE_FLAG)) this.rollShopStock(k);
	}
	shopBuyRows() {
		if (!this.shopStock[this.shopKeep]) this.rollShopStock(this.shopKeep);
		const s = this.shopStock[this.shopKeep];
		return this.shopCatalog(this.shopKeep).filter((id) => (s[id] ?? 0) > 0);
	}
	shopBuyPrice(id) {
		const base = ITEMS[id].buy;
		const r = LOGIC.reputation || {};
		const pos = r.pricePosPct ?? 1;
		const neg = r.priceNegPct ?? 5;
		const minP = r.minPrice ?? 1;
		if (this.reputation > 0) return Math.max(minP, Math.floor(base * (100 - this.reputation * pos) / 100));
		if (this.reputation < 0) return Math.max(minP, Math.floor(base * (100 + (-this.reputation) * neg) / 100));
		return base;
	}
	/** Half of list buy price, then +1% per +rep / -1% per -rep. Never below 1 mark. */
	shopSellPrice(id) {
		const base = Math.floor((ITEMS[id].buy || 0) / 2);
		const minP = LOGIC.reputation?.minPrice ?? 1;
		const r = this.reputation | 0;
		return Math.max(minP, Math.floor(base * (100 + r) / 100));
	}
	shopGiftPending() {
		const need = LOGIC.reputation?.freeAt ?? 100;
		if (this.reputation < need) return false;
		const flag = SHOP_FREE_FLAG[this.shopKeep];
		return flag ? !this[flag] : false;
	}
	markShopGiftTaken() {
		const flag = SHOP_FREE_FLAG[this.shopKeep];
		if (flag) this[flag] = true;
	}
	openShop(keep: string = "bram") {
		if (this.beatHeavenfall && !this.heavenfallRepWarned) {
			this.heavenfallRepWarned = true;
			this.say(TALK.heavenfallShopWarn || [{ speaker: "none", text: "You revived Heavenfall, who knows what other horrors you are capable of." }]);
		}
		if (keep === "dray" && this.reputation < 0 && !this.bag.bowieKnife) {
			// Complete the offer dialogue before opening Dray's one-item knife shop.
			this.drayKnifeOffered = true;
			this.say(TALK.drayKnifeOffer || [
				{ speaker: "dray", text: "I've heard of your reputation. Can I interest you in a knife?" },
				{ speaker: "dray", text: "Sickos like you sometimes prefer up close and personal action." }
			], "drayKnifeShop");
			return;
		}
		this.mode = "shop";
		this.shopKeep = keep;
		this.shopTab = "buy";
		this.shopCursor = 0;
		this.audio.ui();
	}
	closeMenu() {
		this.mode = "world";
		this.pendingItem = null;
		if (this.partyView === "catchSwap" && this.pendingCatch) {
			this.note(`${this.pendingCatch.name} slips back into the wild.`);
			this.pendingCatch = null;
		}
		this.partyView = "list";
		this.audio.ui();
	}
	releaseMember(idx) {
		const keepLast = LOGIC.party?.keepLast !== false;
		if (keepLast && this.party.length <= 1) {
			this.note(`${this.playerDisplayName()} will not send her last CryMon away.`);
			this.audio.miss();
			return false;
		}
		const gone = this.party[idx];
		if (!gone) return false;
		this.party.splice(idx, 1);
		if (this.partyIndex === idx) this.partyIndex = 0;
		else if (this.partyIndex > idx) this.partyIndex -= 1;
		this.partyCursor = clamp(this.partyCursor, 0, this.party.length - 1);
		this.note(`${gone.name} was released.`);
		this.audio.ok();
		return true;
	}
	applyFieldItem(id, idx) {
		const m = this.party[idx];
		if (!m) return false;
		if (this.bag[id] <= 0) return false;
		const fx = itemEffect(id);
		if (fx?.kind === "cure") {
			if (!m.status || m.status === "none") {
				this.note(`${m.name} has nothing to cure.`);
				return false;
			}
			if (fx.status !== "all" && m.status !== fx.status) {
				this.note(`${m.name} isn't affected by that.`);
				return false;
			}
			this.clearStatus(m);
			this.bag[id] -= 1;
			this.note(`${ITEMS[id].name}. ${m.name} is cured.`);
			this.audio.ok();
			return true;
		}
		const amt = healAmount(id);
		if (amt <= 0) {
			this.note("Use that in battle.");
			return false;
		}
		if (m.hp >= m.maxHp) {
			this.note(`${m.name} is already whole.`);
			return false;
		}
		const n = Math.min(amt, m.maxHp - m.hp);
		m.hp += n;
		this.bag[id] -= 1;
		this.note(`${ITEMS[id].name}. ${m.name} +${n} HP.`);
		this.audio.ok();
		return true;
	}
	sleepHeal() {
		this.rollAllShopStock();
		this.party.forEach((m) => {
			m.hp = m.maxHp;
			m.specialPp = m.specialPpMax;
			// Leg 2.11: Burned/Poisoned/Confused/Paralyzed persist on the
			// player's own CryMon until their next rest -- this is that rest.
			m.status = "none";
			m.statusTurns = 0;
			m.poisonStack = 0;
		});
	}
	giveAnneGems() {
		if (this.anneGifted) return;
		this.anneGifted = true;
		const g = LOGIC.anneGift;
		const id = (g?.item ?? "gem") as ItemId;
		this.bag[id] = (this.bag[id] ?? 0) + (g?.qty ?? 5);
	}
	startAnneLeave() {
		this.anne.phase = "leave";
		this.anne.dir = "down";
		this.anne.frame = 0;
	}
	startMasonLeave() {
		this.rival.phase = "leave";
		this.rival.dir = "down";
		this.rival.frame = 0;
		this.rival.anim = 0;
	}
	maybeStartAnne() {
		if (this.anne.phase !== "off") return;
		if (this.talking() || this.hudT > 0) return;
		if (!this.anneGifted && this.battlesDone >= (LOGIC.anneGift?.afterBattles ?? 1) && this.world.mapId === (LOGIC.anneGift?.map ?? "veld")) {
			this.anne = {
				phase: "approach",
				x: this.world.x,
				y: this.world.y + 72,
				dir: "up",
				frame: 0,
				anim: 0
			};
			return;
		}
		if (!this.anne2Told && this.anneGifted && (this.beatCathleen || this.cathleenCaught)) {
			this.anne2Told = true;
			this.anne = {
				phase: "approach2",
				x: this.world.x,
				y: this.world.y + 72,
				dir: "up",
				frame: 0,
				anim: 0
			};
		}
	}
	onBattleOver() {
		this.battlesDone += 1;
		this.persist(false);
	}
	cycleParty(to) {
		if (to != null) {
			const m = this.party[to];
			if (!m || m.hp <= 0 || to === this.partyIndex) return;
			this.partyIndex = to;
			this.note(`${m.name} takes the lead.`);
			this.audio.ui();
			return;
		}
		if (this.party.length < 2) return;
		const start = this.partyIndex;
		for (let i = 1; i <= this.party.length; i++) {
			const n = (start + i) % this.party.length;
			if (this.party[n].hp > 0) {
				this.partyIndex = n;
				this.note(`${this.party[n].name} takes the lead.`);
				this.audio.ui();
				return;
			}
		}
	}
	update(dt) {
		this.clock += dt;
		this.tickFade(dt);
		if (this.shake > 0) this.shake = Math.max(0, this.shake - dt * 8);
		if (this.hudT > 0) this.hudT -= dt;
		if (this.input.tapA || this.input.tapStart || this.input.keys.has("KeyZ") || this.input.keys.has("Enter")) this.audio.unlock();
		try {
			this.audio.tick(dt);
			this.audio.setSong(this.sceneSong());
		} catch {
			/* audio hardware optional */
		}
		if (this.mode === "title") {
			if (this.input.up() || this.input.down()) {
				this.titleCursor = 1 - this.titleCursor;
				this.audio.ui();
			}
			if (this.input.confirm() || this.input.start()) {
				if (this.titleCursor === 0) {
					if (!this.tryContinue()) {
						if (!this.hasSave) this.audio.miss();
					}
				} else {
					clearSave();
					this.reset();
					this.hasSave = false;
					this.mode = "intro";
					this.introI = 0;
					this.audio.ok();
				}
			}
			return;
		}
		if (this.mode === "intro") {
			if (this.input.confirm()) {
				this.audio.ui();
				this.introI += 1;
				if (this.introI >= INTRO.length) {
					this.mode = "world";
					this.note("Stand next to the shelf or the crate. Press Z.");
				}
			}
			return;
		}
		if (this.mode === "ending") {
			if (this.input.confirm()) {
				this.audio.ui();
				this.endI += 1;
				if (this.endI >= this.endingText().length) {
					this.reset();
				}
			}
			return;
		}
		if (this.mode === "choice") {
			this.updateChoice();
			return;
		}
		if (this.mode === "mercy") {
			this.updateMercy();
			return;
		}
		if (this.mode === "backstab") {
			this.updateBackstabChoice();
			return;
		}
		if (this.mode === "bag") {
			this.updateBag();
			return;
		}
		if (this.mode === "party") {
			this.updateParty();
			return;
		}
		if (this.mode === "shop") {
			this.updateShop();
			return;
		}
		if (this.mode === "pause") {
			this.updatePause();
			return;
		}
		if (this.mode === "crydex") {
			this.updateCryDex();
			return;
		}
		if (this.mode === "townmap") {
			this.updateTownMap();
			return;
		}
		if (this.mode === "settings") {
			this.updateSettings();
			return;
		}
		if (this.mode === "world") {
			if (!this.talking() && this.rival.phase !== "approach" && this.anne.phase !== "approach" && this.hudT <= 0) {
				if (this.input.start()) {
					this.openPause();
					return;
				}
				if (this.input.select()) {
					this.openBag();
					return;
				}
			}
		}
		if (this.mode === "battle" && this.battle) {
			this.updateBattle(dt);
			return;
		}
		this.updateWorld(dt);
	}
	updateBag() {
		const items = this.ownedItems();
		if (this.input.select() || this.input.cancel() || this.input.start()) {
			this.closeMenu();
			return;
		}
		if (items.length === 0) return;
		if (this.input.up()) {
			this.bagCursor = (this.bagCursor + items.length - 1) % items.length;
			this.audio.ui();
		}
		if (this.input.down()) {
			this.bagCursor = (this.bagCursor + 1) % items.length;
			this.audio.ui();
		}
		if (this.input.confirm()) {
			const id = items[this.bagCursor];
			if (!id) return;
			if (!ITEMS[id].field) {
				this.audio.miss();
				this.note("Use that in battle.");
				return;
			}
			this.pendingItem = id;
			this.openParty("target");
		}
	}
	updateParty() {
		if (this.partyView === "target") {
			if (this.input.cancel() || this.input.select()) {
				this.pendingItem = null;
				this.openBag();
				return;
			}
			if (this.input.start()) {
				this.pendingItem = null;
				this.closeMenu();
				return;
			}
			if (this.party.length === 0) return;
			if (this.input.up()) {
				this.partyCursor = (this.partyCursor + this.party.length - 1) % this.party.length;
				this.audio.ui();
			}
			if (this.input.down()) {
				this.partyCursor = (this.partyCursor + 1) % this.party.length;
				this.audio.ui();
			}
			if (this.input.confirm() && this.pendingItem) {
				if (this.applyFieldItem(this.pendingItem, this.partyCursor)) {
					if (this.bag[this.pendingItem] <= 0) {
						this.pendingItem = null;
						this.openBag();
					}
				}
			}
			return;
		}
		if (this.partyView === "stats") {
			if (this.input.cancel() || this.input.confirm() || this.input.start()) {
				this.partyView = "list";
				this.audio.ui();
			}
			return;
		}
		if (this.partyView === "moves") {
			const m = this.party[this.partyCursor] ?? this.lead();
			const moves = this.partyMoves(m);
			if (this.input.cancel() || this.input.start()) {
				this.partyView = "list";
				this.audio.ui();
				return;
			}
			if (moves.length && this.input.up()) {
				this.moveCursor = (this.moveCursor + moves.length - 1) % moves.length;
				this.audio.ui();
			}
			if (moves.length && this.input.down()) {
				this.moveCursor = (this.moveCursor + 1) % moves.length;
				this.audio.ui();
			}
			if (this.input.confirm()) {
				this.partyView = "list";
				this.audio.ui();
			}
			return;
		}
		if (this.partyView === "release") {
			if (this.input.cancel()) {
				this.partyView = "act";
				this.audio.ui();
				return;
			}
			if (this.input.confirm()) {
				this.releaseMember(this.partyCursor);
				this.partyView = "list";
			}
			return;
		}
		if (this.partyView === "catchSwap") {
			if (this.input.cancel() || this.input.start()) {
				this.closeMenu();
				return;
			}
			if (this.party.length === 0) return;
			if (this.input.up()) {
				this.partyCursor = (this.partyCursor + this.party.length - 1) % this.party.length;
				this.audio.ui();
			}
			if (this.input.down()) {
				this.partyCursor = (this.partyCursor + 1) % this.party.length;
				this.audio.ui();
			}
			if (this.input.confirm() && this.pendingCatch) {
				const gone = this.party[this.partyCursor];
				this.party[this.partyCursor] = this.pendingCatch;
				this.note(`Released ${gone.name}. ${this.pendingCatch.name} stays.`);
				this.pendingCatch = null;
				this.partyView = "list";
				this.mode = "world";
				this.audio.ok();
			}
			return;
		}
		if (this.partyView === "act") {
			const acts = [
				"Send out",
				"Stats",
				"Moves",
				"Release"
			];
			if (this.input.cancel()) {
				this.partyView = "list";
				this.audio.ui();
				return;
			}
			if (this.input.up()) {
				this.actCursor = (this.actCursor + acts.length - 1) % acts.length;
				this.audio.ui();
			}
			if (this.input.down()) {
				this.actCursor = (this.actCursor + 1) % acts.length;
				this.audio.ui();
			}
			if (this.input.confirm()) {
				const m = this.party[this.partyCursor];
				if (!m) return;
				if (this.actCursor === 0) {
					if (m.hp <= 0) this.note(`${m.name} cannot stand.`);
					else {
						this.partyIndex = this.partyCursor;
						this.note(`${m.name} will be sent to battle.`);
						this.audio.ok();
					}
					this.partyView = "list";
				} else if (this.actCursor === 1) {
					this.partyView = "stats";
					this.audio.ui();
				} else if (this.actCursor === 2) {
					this.partyView = "moves";
					this.moveCursor = 0;
					this.audio.ui();
				} else {
					if (this.party.length <= 1) {
						this.note(`${this.playerDisplayName()} will not send her last CryMon away.`);
						this.audio.miss();
						this.partyView = "list";
					} else {
						this.partyView = "release";
						this.audio.ui();
					}
				}
			}
			return;
		}
		if (this.input.start() || this.input.cancel()) {
			this.closeMenu();
			return;
		}
		if (this.input.pressed("Tab") || this.input.pressed("KeyQ") || this.input.left() || this.input.right()) {
			this.swapParties();
			return;
		}
		if (this.input.select()) {
			this.openBag();
			return;
		}
		if (this.party.length === 0) return;
		if (this.input.up()) {
			this.partyCursor = (this.partyCursor + this.party.length - 1) % this.party.length;
			this.audio.ui();
		}
		if (this.input.down()) {
			this.partyCursor = (this.partyCursor + 1) % this.party.length;
			this.audio.ui();
		}
		if (this.input.pressed("Digit1")) this.cycleParty(0);
		if (this.input.pressed("Digit2")) this.cycleParty(1);
		if (this.input.pressed("Digit3")) this.cycleParty(2);
		if (this.input.pressed("Digit4")) this.cycleParty(3);
		if (this.input.pressed("Digit5")) this.cycleParty(4);
		if (this.input.pressed("Digit6")) this.cycleParty(5);
		if (this.input.confirm()) {
			this.partyView = "act";
			this.actCursor = 0;
			this.audio.ui();
		}
	}
	updateShop() {
		if (this.input.cancel() || this.input.start() || this.input.select()) {
			this.closeMenu();
			return;
		}
		if (this.input.left() || this.input.right()) {
			this.shopTab = this.shopTab === "buy" ? "sell" : "buy";
			this.shopCursor = 0;
			this.audio.ui();
		}
		const rows = this.shopTab === "buy" ? this.shopBuyRows() : this.ownedItems().filter((id) => ITEMS[id].sell > 0);
		if (rows.length === 0) return;
		if (this.input.up()) {
			this.shopCursor = (this.shopCursor + rows.length - 1) % rows.length;
			this.audio.ui();
		}
		if (this.input.down()) {
			this.shopCursor = (this.shopCursor + 1) % rows.length;
			this.audio.ui();
		}
		if (this.input.confirm()) {
			const id = rows[this.shopCursor];
			if (!id) return;
			if (this.shopTab === "buy") {
				const stockLeft = this.shopStock[this.shopKeep]?.[id] ?? 0;
				if (stockLeft <= 0) return;
				const gift = this.shopGiftPending();
				const cost = gift ? 0 : this.shopBuyPrice(id);
				if (this.marks < cost) {
					this.audio.miss();
					this.note("Not enough marks.");
					return;
				}
				this.marks -= cost;
				// Not every buyable item starts in the player's bag (the
				// higher capture-crystal tiers never do) -- `bag[id] += 1`
				// on an unset key is `undefined + 1 = NaN`, permanently
				// corrupting that slot. This is the root cause behind the
				// "0 or undefined" quantities reported for greater/mega/
				// ultimate crystals.
				this.bag[id] = (this.bag[id] ?? 0) + 1;
				this.shopStock[this.shopKeep][id] = stockLeft - 1;
				this.audio.ok();
				if (gift) {
					this.markShopGiftTaken();
					this.note(`A gift. ${ITEMS[id].name}.`);
				} else this.note(`Bought ${ITEMS[id].name}.`);
				if (stockLeft - 1 <= 0) this.shopCursor = 0;
			} else {
				if (this.bag[id] <= 0) return;
				this.bag[id] -= 1;
				this.marks += this.shopSellPrice(id);
				this.audio.ok();
				this.note(`Sold ${ITEMS[id].name}.`);
				if (this.bag[id] <= 0) this.shopCursor = 0;
			}
		}
	}
	updateWorld(dt) {
		if (this.fade.phase !== "off") {
			this.world.moving = false;
			return;
		}
		if (this.talkLock > 0) this.talkLock = Math.max(0, this.talkLock - dt);
		if (this.doorLock > 0) this.doorLock -= dt;
		if (this.mapBannerT > 0) this.mapBannerT = Math.max(0, this.mapBannerT - dt);
		if (!this.talking() && this.hudT <= 0) this.maybeStartAnne();
		this.maybeStartMasonRematch();
		if (this.rival.phase === "approach") {
			this.world.moving = false;
			this.world.frame = 0;
			const dx = this.world.x - this.rival.x;
			const dy = this.world.y - this.rival.y;
			const dist = Math.hypot(dx, dy);
			if (dist < 36) {
				this.rival.phase = "talk";
				this.rival.frame = 0;
				this.say(this.masonRematch ? TALK.masonFight2 : TALK.masonFight, this.masonRematch ? "mason2" : "mason");
				return;
			}
			const sp = 52 * dt;
			this.rival.x += dx / dist * sp;
			this.rival.y += dy / dist * sp;
			this.rival.dir = Math.abs(dx) > Math.abs(dy) ? dx < 0 ? "left" : "right" : dy < 0 ? "up" : "down";
			this.rival.anim += dt * 8;
			this.rival.frame = Math.floor(this.rival.anim) % 4;
			return;
		}
		if (this.anne.phase === "approach" || this.anne.phase === "approach2") {
			this.world.moving = false;
			this.world.frame = 0;
			const dx = this.world.x - this.anne.x;
			const dy = this.world.y - this.anne.y;
			const dist = Math.hypot(dx, dy);
			if (dist < 36) {
				const second = this.anne.phase === "approach2";
				this.anne.phase = "done";
				this.anne.frame = 0;
				if (second) this.say(TALK.anneReturn, "anneLeave");
				else {
					this.giveAnneGems();
					this.say(TALK.anneGift, "anneLeave");
					this.audio.ok();
				}
				return;
			}
			const sp = 52 * dt;
			this.anne.x += dx / dist * sp;
			this.anne.y += dy / dist * sp;
			this.anne.dir = Math.abs(dx) > Math.abs(dy) ? dx < 0 ? "left" : "right" : dy < 0 ? "up" : "down";
			this.anne.anim += dt * 8;
			this.anne.frame = Math.floor(this.anne.anim) % 4;
			return;
		}
		if (this.talking()) {
			this.world.moving = false;
			this.world.frame = 0;
			if (this.talkLock <= 0 && (this.input.confirm() || this.input.cancel())) this.advanceTalk();
			return;
		}
		if (this.hudT > 0) {
			this.world.moving = false;
			this.world.frame = 0;
			if (this.input.confirm() || this.input.cancel()) {
				this.hudT = 0;
				this.hudFlash = "";
				this.talkLock = .2;
			}
			return;
		}
		if (this.anne.phase === "leave") {
			this.anne.y += 80 * dt;
			this.anne.dir = "down";
			this.anne.anim += dt * 8;
			this.anne.frame = Math.floor(this.anne.anim) % 4;
			if (this.anne.y > this.world.y + VIEW_H / 2 + 48) this.anne.phase = "off";
		}
		if (this.rival.phase === "leave") {
			if (this.world.mapId !== "veld") this.rival.phase = "off";
			else {
				this.rival.y += 90 * dt;
				this.rival.dir = "down";
				this.rival.anim += dt * 8;
				this.rival.frame = Math.floor(this.rival.anim) % 4;
				if (this.rival.y > this.world.y + VIEW_H / 2 + 48) this.rival.phase = "off";
			}
		}
		if (this.updateSoldiers(dt) || this.updateRoamers(dt)) {
			this.world.moving = false;
			this.world.frame = 0;
			return;
		}
		const ax = this.input.axis();
		this.world.moving = Math.abs(ax.x) + Math.abs(ax.y) > .2;
		if (this.world.moving) {
			if (Math.abs(ax.x) > Math.abs(ax.y)) this.world.dir = ax.x < 0 ? "left" : "right";
			else this.world.dir = ax.y < 0 ? "up" : "down";
			const sp = 84;
			const nx = this.world.x + ax.x * sp * dt;
			const ny = this.world.y + ax.y * sp * dt;
			const stuck = this.blocked(this.world.x, this.world.y);
			if (stuck || !this.blocked(nx, this.world.y)) this.world.x = nx;
			if (stuck || !this.blocked(this.world.x, ny)) this.world.y = ny;
			const map = this.map();
			const mw = (map[0]?.length ?? 1) * TILE;
			const mh = map.length * TILE;
			this.world.x = clamp(this.world.x, 24, mw - 24);
			this.world.y = clamp(this.world.y, 40, mh - 16);
			this.world.anim += dt * 6;
			this.world.frame = Math.floor(this.world.anim) % 4;
			this.tryEncounter();
		} else this.world.frame = 0;
		this.tryDoor();
		this.tryMapWarp();
		if (this.input.pressed("Digit1")) this.cycleParty(0);
		if (this.input.pressed("Digit2")) this.cycleParty(1);
		if (this.input.pressed("Digit3")) this.cycleParty(2);
		if (this.input.pressed("Digit4")) this.cycleParty(3);
		if (this.input.pressed("Digit5")) this.cycleParty(4);
		if (this.input.pressed("Digit6")) this.cycleParty(5);
		if (this.talkLock <= 0 && this.input.confirm()) this.interact();
		if (this.input.cancel()) this.cycleParty();	}
	blocked(x, y) {
		if (this.devPassAll) return false;
		const r = 10;
		if ([
			[x - r, y],
			[x + r, y],
			[x, y - 2],
			[x, y + r]
		].some(([px, py]) => {
			const ch = tileAt(this.map(), px, py);
			if (ch === "k" && this.cageOpen) return false;
			return solidTile(ch);
		})) return true;
		if (this.world.mapId === "forest") {
			for (const sol of this.soldiers) {
				if (sol.beaten || sol.chase) continue;
				if (Math.abs(sol.x - x) < 16 && Math.abs(sol.y - y) < 16) return true;
			}
		}
		if (this.world.mapId === "grove" && !(this.cathleenCaught || this.beatCathleen)) {
			const c = spawnOf(GROVE, "8");
			if (Math.abs(c.x - x) < 18 && Math.abs(c.y - y) < 20) return true;
			if (tileAt(this.map(), x, y) === "D" || tileAt(this.map(), x, y + 8) === "D") return true;
		}
		if (this.world.mapId === "grove" && !this.beatShinigami) {
			const s = spawnOf(GROVE, "9");
			if (Math.abs(s.x - x) < 16 && Math.abs(s.y - y) < 18) return true;
		}
		const blockFlags = this.npcFlags();
		for (const npc of NPCS) {
			if (npc.map !== this.world.mapId || !npc.sprite) continue;
			if (this.npcHidden(npc, blockFlags)) continue;
			if (this.npcPassable(npc, blockFlags)) continue;
			if (this.npcIsExecuted(npc.id)) continue;
			// A roamer mid-chase isn't solid -- same as FOREST's patrol
			// soldiers (see the sol.chase check above): it catches the
			// player by proximity, not by blocking their tile.
			const roamer = this.roamableNpc(npc) ? this.roamers[npc.id] : null;
			if (roamer?.chase) continue;
			for (const mark of this.npcMarks(npc)) {
				const s = roamer ? { x: roamer.x, y: roamer.y } : spawnOf(this.map(), mark);
				if (Math.abs(s.x - x) < 16 && Math.abs(s.y - y) < 16) return true;
			}
		}
		return false;
	}
	tryEncounter() {
		const tx = Math.floor(this.world.x / TILE);
		const ty = Math.floor(this.world.y / TILE);
		if (tx === this.lastTx && ty === this.lastTy) return;
		this.lastTx = tx;
		this.lastTy = ty;
		const rule = ENCOUNTERS.find((e) => e.maps.includes(this.world.mapId));
		if (!rule) return;
		if (tileAt(this.map(), this.world.x, this.world.y) !== rule.tile) return;
		if (this.world.encounterLock > 0) {
			this.world.encounterLock -= 1;
			return;
		}
		if (Math.random() > rule.rate) return;
		this.world.encounterLock = 3;
		const pool = rule.pool as SpeciesId[];
		const id = pool[randI(0, pool.length - 1)];
		let lv = rule.levelMin + randI(0, Math.max(0, rule.levelMax - rule.levelMin));
		if (rule.levelBonusIfTyGt && ty > rule.levelBonusIfTyGt) lv += 1;
		const shiny = rollShiny();
		/* mintMonster doubles the level it's given when shiny=true (see its
		   own body), so the pre-mint cap must already account for that
		   doubling -- halve WILD_LEVEL_CAP going in, not after, or a shiny
		   roll could still come out above the cap. */
		const cap = shiny ? Math.floor(FORMULAS.wildLevelCap / 2) : FORMULAS.wildLevelCap;
		lv = Math.min(lv, cap);
		this.startBattle(mintMonster(id, lv, shiny), true, `A ${shiny ? "shiny " : "wild "}${SPECIES[id].name}`);
	}
	nearMark(map, mark, radius = 52) {
		const s = spawnOf(map, mark);
		const dx = s.x - this.world.x;
		const dy = s.y - this.world.y;
		return dx * dx + dy * dy <= radius * radius;
	}
	closestMark(map, marks, radius = 52) {
		let best = null;
		let bestD = radius * radius;
		for (const mark of marks) {
			const s = spawnOf(map, mark);
			const dx = s.x - this.world.x;
			const dy = s.y - this.world.y;
			const d = dx * dx + dy * dy;
			if (d <= bestD) {
				bestD = d;
				best = mark;
			}
		}
		return best;
	}
	closestVeldMark(marks, radius = 26) {
		return this.closestMark(VELD, marks, radius);
	}
	tryDoor() {
		if (this.doorLock > 0) return;
		const d = this.world.dir;
		const ox = d === "left" ? -20 : d === "right" ? 20 : 0;
		const oy = d === "up" ? -20 : d === "down" ? 20 : 0;
		const here = tileAt(this.map(), this.world.x, this.world.y);
		const ahead = tileAt(this.map(), this.world.x + ox, this.world.y + oy);
		if ((this.world.mapId === "house" || this.world.mapId === "veld") && (doorTile(here) || this.world.moving && doorTile(ahead))) this.useDoor();
	}
	useDoor() {
		this.applyWarp("D");
	}
	flagFor(need: string | undefined) {
		if (!need) return true;
		if (need === "tookStarter") return this.tookStarter;
		if (need === "beatCalder") return this.beatCalder;
		if (need === "beatShin") return this.beatShinigami;
		if (need === "hasScroll") return this.hasScroll;
		if (need === "choseHeavenfall") return this.choseHeavenfall || this.gauntletUnlocked;
		if (need === "foughtMason") return this.foughtMason;
		if (need === "hasParty") return this.party.length >= 1;
		return true;
	}
	npcFlags(): Record<string, boolean> {
		return {
			tookStarter: this.tookStarter,
			talkedFather: this.talkedFather,
			lootedCrate: this.lootedCrate,
			talkedWren: this.talkedWren,
			beatCalder: this.beatCalder,
			readCart: this.readCart,
			talkedMae: this.talkedMae,
			talkedIvo: this.talkedIvo,
			talkedNell: this.talkedNell,
			nellBonus: this.nellBonus,
			hasParty2: this.party.length > 1,
			gotFieldGem: this.gotFieldGem,
			pikeHelped: this.pikeHelped,
			talkedPike: this.talkedPike,
			gotHerb: this.gotHerb,
			gotStump: this.gotStump,
			cathleenCaught: this.cathleenCaught,
			beatShinigami: this.beatShinigami,
			sawShinigamiRock: this.sawShinigamiRock,
			hasScroll: this.hasScroll,
			beatCross: this.beatCross,
			beatConscript: this.beatConscript,
			beatEnforcer: this.beatEnforcer,
			beatSentry: this.beatSentry,
			tessaGifted: this.tessaGifted,
			chestLooted: this.chestLooted,
			birchGifted: this.birchGifted,
			sableGifted: this.sableGifted,
			cageOpen: this.cageOpen,
			hasCageKey: (this.bag.cageKey ?? 0) > 0,
			talkedReach: this.talkedReach,
			beatForestRanger: this.beatForestRanger,
			beatForestScout: this.beatForestScout,
			beatRuinsKeeper: this.beatRuinsKeeper,
			beatRuinsWarden: this.beatRuinsWarden,
			beatMarshBog: this.beatMarshBog,
			beatMarshReed: this.beatMarshReed,
			badgeQuartz: this.badgeQuartz,
				badgeOpal: this.badgeOpal,
				beatQuarryDriller: this.beatQuarryDriller,
				choseHeavenfall: this.choseHeavenfall,
				revivedFather: this.revivedFather,
				beatCommander: this.beatCommander,
				beatLieutenantLead: this.beatLieutenantLead,
				quarryCrateLooted: this.quarryCrateLooted,
				quarryShelfSearched: this.quarryShelfSearched,
		};
	}
	setNpcFlag(name: string) {
		if (name === "hasParty2") return;
		if (typeof this[name] === "boolean") this[name] = true;
	}
	npcMarks(npc) {
		if (Array.isArray(npc.marks) && npc.marks.length) return npc.marks;
		return npc.mark ? [npc.mark] : [];
	}
	/** Shared by the draw loop and blocked()'s collision loop so an NPC's
	 *  visibility and solidity never disagree -- a hidden gate-blocker
	 *  (like shinigamiBoulder once beatShin flips) must also stop
	 *  blocking movement in the same frame it stops being drawn.
	 *  `hideIf`: hide once the flag is true. `if`: hide until the flag
	 *  is true. Either can appear on any script step. */
	npcHidden(npc, flags) {
		// A step's `if` only gates visibility when the step is otherwise
		// empty (no `talk`) -- e.g. shinigamiRock's {if: beatShinigami}.
		// On a step that also carries dialogue (calder, the Priestess),
		// `if` instead picks which line to show and must not hide the
		// NPC just because that particular branch didn't match.
		return !!npc.script?.some((s) => (s.hideIf && flags[s.hideIf as string]) || (s.if && !s.talk && !flags[s.if as string]));
	}
	/** A gate-blocking NPC that should stay visible but step out of the
	 *  way once beaten/satisfied (Calder, the Heavenfall Priestess) --
	 *  distinct from npcHidden(), which also removes the sprite. `passIf`
	 *  can sit on any existing script step alongside its talk/if keys. */
	npcPassable(npc, flags) {
		return !!npc.script?.some((s) => s.passIf && flags[s.passIf as string]);
	}
	/** [dx, dy] pixel offset for a passable gate-blocker's drawn/interact
	 *  position -- [0, 0] once not passable, or if the matching step
	 *  carries no passOffset. Keeps the sprite/hitbox off the spot it
	 *  used to block instead of leaving it standing there passable. */
	npcPassOffset(npc, flags): [number, number] {
		const step = npc.script?.find((s) => s.passIf && flags[s.passIf as string]);
		return step?.passOffset ?? [0, 0];
	}
	runNpc(npc) {
		const flags = this.npcFlags();
		const step = matchNpcScript(npc.script, flags);
		if (!step) return false;
		if (step.set) this.setNpcFlag(step.set);
		if (step.grant) {
			for (const [id, n] of step.grant) {
				if (id in this.bag) this.bag[id] += n;
			}
		}
		if (step.takeItem && step.takeItem in this.bag) {
			this.bag[step.takeItem] = Math.max(0, this.bag[step.takeItem] - 1);
		}
		if (step.grantMonster) {
			const [sp, lv] = step.grantMonster;
			if (this.party.length === 0) {
				this.party = [mintMonster(sp, lv)];
				this.partyIndex = 0;
			}
			this.markCaught(sp);
		}
		if (step.heal) this.sleepHeal();
		if (step.marks) this.marks += step.marks;
		if (step.pending) this.pendingWs = step.pending;
		let talkKey = step.talk;
		if (step.talkIf) talkKey = flags[step.talkIf] ? step.talk : step.talkElse;
		const lines = talkKey ? TALK[talkKey] : null;
		if (lines) {
			if (this.devWinAllMode && this.isMercyFightAfter(step.after)) this.triggerDevWinAllFight(step.after);
			else this.say(lines, step.after ?? null);
		}
		if (step.grant || step.heal || step.grantMonster || step.marks) {
			this.audio.ok();
			this.persist(false);
		}
		return true;
	}
	runClosestNpc() {
		const map = this.map();
		const flags = this.npcFlags();
		let best = null;
		let bestD = Infinity;
		for (const npc of NPCS) {
			if (npc.map !== this.world.mapId || !npc.script?.length) continue;
			if (this.npcIsExecuted(npc.id)) continue;
			if (!matchNpcScript(npc.script, flags)) continue;
			const [poX, poY] = this.npcPassOffset(npc, flags);
			const roamer = this.roamableNpc(npc) ? this.roamers[npc.id] : null;
			for (const mark of this.npcMarks(npc)) {
				const s = roamer ? { x: roamer.x, y: roamer.y } : spawnOf(map, mark);
				s.x += poX;
				s.y += poY;
				// Box test against the target's own footprint (npc.w/h,
				// default the human sprite size) plus INTERACT.buffer on
				// every side, feet-anchored the same way it's drawn: box
				// bottom = mark y, box top = mark y - h. Not a radius --
				// see content/logic.json's interact block. Dreamcast's
				// try_npc_script() mirrors this exactly, scaled for its
				// own tile size.
				const w = npc.w ?? INTERACT.defaultW;
				const h = npc.h ?? INTERACT.defaultH;
				const halfW = w / 2 + INTERACT.buffer;
				const left = s.x - halfW;
				const right = s.x + halfW;
				const bottom = s.y + INTERACT.buffer;
				const top = s.y - h - INTERACT.buffer;
				if (this.world.x < left || this.world.x > right || this.world.y < top || this.world.y > bottom) continue;
				const dx = s.x - this.world.x;
				const dy = s.y - this.world.y;
				const d = dx * dx + dy * dy;
				if (d <= bestD) {
					bestD = d;
					best = npc;
				}
			}
		}
		if (!best) return false;
		const bestStep = matchNpcScript(best.script, flags);
		if (bestStep && this.canBackstab(best, bestStep)) {
			this.openBackstabChoice(best, bestStep);
			return true;
		}
		return this.runNpc(best);
	}
	logicFlags() {
		return {
			foughtMason: this.foughtMason,
			beatCalder: this.beatCalder,
			hasParty: this.party.length >= 1,
			mason2Done: this.mason2Done,
			mason2Map: this.mason2Map,
			mapId: this.world.mapId,
			rivalOff: this.rival.phase === "off"
		};
	}
	spawnMasonApproach(rematch: boolean) {
		const oy = rematch ? LOGIC.masonRematch.oy : LOGIC.arrivals.masonAmbush.spawn.oy;
		const dir = rematch ? LOGIC.masonRematch.dir : LOGIC.arrivals.masonAmbush.spawn.dir;
		this.masonRematch = rematch;
		this.rival = {
			phase: "approach",
			x: this.world.x,
			y: this.world.y + oy,
			dir,
			frame: 0,
			anim: 0
		};
	}
	runArrival(name: string | undefined) {
		if (!name) return;
		if (name === "ensureSoldiers") {
			this.ensureSoldiers();
			return;
		}
		if (!arrivalAllowed(this.logicFlags(), name)) return;
		const spec = LOGIC.arrivals[name];
		if (spec && "spawn" in spec && spec.spawn.actor === "mason") this.spawnMasonApproach(false);
	}
	startFade(action: "bed" | "loss" | "execute" | "priestessTeleport") {
		this.fade = { phase: "out", t: 0, action };
	}
	applyFadeHold() {
		if (this.fade.action === "bed" && LOGIC.bed.healParty) this.sleepHeal();
		if (this.fade.action === "loss") {
			const fromGauntlet = String(this.world.mapId).startsWith("gauntlet");
			if (LOGIC.partyWipe.healParty) this.sleepHeal();
			if (fromGauntlet && this.choseHeavenfall && !this.gauntletWipeRegret) {
				this.gauntletWipeRegret = true;
				this.say(TALK.gauntletWipeRegret);
			}
			const mark = spawnOf(HOUSE, LOGIC.partyWipe.mark);
			this.world.mapId = LOGIC.partyWipe.map;
			this.world.x = mark.x + TILE;
			this.world.y = mark.y;
			this.world.dir = LOGIC.partyWipe.dir;
			this.doorLock = 0.4;
			this.announceMap();
		}
		if (this.fade.action === "hfGameOver") {
			this.reloadLastSaveOrTitle();
		}
		if (this.fade.action === "priestessTeleport") {
			const mark = spawnOf(HOUSE, LOGIC.partyWipe.mark);
			this.world.mapId = LOGIC.partyWipe.map;
			this.world.x = mark.x + TILE;
			this.world.y = mark.y;
			this.world.dir = LOGIC.partyWipe.dir;
			this.doorLock = 0.4;
			this.announceMap();
		}
	}
	tickFade(dt: number) {
		if (this.fade.phase === "off") return;
		const { outSec, holdSec, inSec } = LOGIC.screenFade;
		this.fade.t += dt;
		if (this.fade.phase === "out" && this.fade.t >= outSec) {
			this.fade.phase = "hold";
			this.fade.t = 0;
			this.applyFadeHold();
		} else if (this.fade.phase === "hold" && this.fade.t >= holdSec) {
			this.fade.phase = "in";
			this.fade.t = 0;
		} else if (this.fade.phase === "in" && this.fade.t >= inSec) {
			this.fade = { phase: "off", t: 0, action: null };
		}
	}
	// Shinigami rock event: only on direct interact with shinigamiRock NPC (veld mark 9).
	}
	maybeStartMasonRematch() {
		if (!this.mason2Map && this.beatCalder && !this.mason2Done) {
			this.mason2Map = pickMason2Map(Math.random());
		}
		if (!shouldSpawnMasonRematch(this.logicFlags())) return;
		this.spawnMasonApproach(true);
	}
	applyWarp(ch: string) {
		const warp = WARPS.find((w) => w.from === this.world.mapId && w.tile === ch);
		if (!warp) return false;
		if (warp.need && !this.devPassAll && !this.flagFor(warp.need)) {
			if (warp.failTalk) {
				const d = spawnOf(this.map(), ch);
				if (warp.dir === "down") this.world.y = Math.min(this.world.y, d.y - TILE);
				else if (warp.dir === "up") this.world.y = Math.max(this.world.y, d.y + TILE);
				else if (warp.dir === "right") this.world.x = Math.min(this.world.x, d.x - TILE);
				else if (warp.dir === "left") this.world.x = Math.max(this.world.x, d.x + TILE);
				this.doorLock = .5;
				this.say(TALK[warp.failTalk] || TALK.doorLocked);
			}
			return true;
		}
		if (warp.onArrive === "ensureSoldiers") this.ensureSoldiers();
		this.warpTo(warp.to, warp.spawn, warp.dir, warp.oy, warp.ox);
		if (warp.onArrive && warp.onArrive !== "ensureSoldiers") this.runArrival(warp.onArrive);
		this.maybeStartAnne();
		return true;
	}
	interact() {
		if (this.world.mapId === "forest") {
			this.ensureSoldiers();
			for (const sol of this.soldiers) {
				const dx = sol.x - this.world.x;
				const dy = sol.y - this.world.y;
				if (dx * dx + dy * dy > 676) continue;
				if (sol.beaten) {
					this.say(TALK.soldierDone);
					return;
				}
				if (this.canBackstabSoldier(sol)) {
					this.openBackstabChoiceForSoldier(sol);
					return;
				}
				this.pendingSoldier = sol.id;
				if (this.devWinAllMode) this.triggerDevWinAllFight("soldier");
				else this.say(TALK.soldierSpot, "soldier");
				return;
			}
		}
		if (this.world.mapId === "veld") {
			if (this.anne.phase === "done") {
				const dx = this.anne.x - this.world.x;
				const dy = this.anne.y - this.world.y;
				if (dx * dx + dy * dy <= 676) {
					if (!this.anneGifted) {
						this.giveAnneGems();
						this.say(TALK.anneGift, "anneLeave");
						this.audio.ok();
					} else this.startAnneLeave();
					return;
				}
			}
			if (this.rival.phase === "done") {
				const dx = this.rival.x - this.world.x;
				const dy = this.rival.y - this.world.y;
				if (dx * dx + dy * dy <= 676) {
					if (this.foughtMason) this.say(TALK.masonAfter);
					else {
						const kit = TRAINERS.mason;
						this.startBattle(mintMonster(kit.lead[0], kit.lead[1]), false, kit.title, "mason");
					}
					return;
				}
			}
		}
		if (this.runClosestNpc()) return;
	}
	ensureSoldiers() {
		if (this.soldiers.length) return;
		const kits = TRAINERS.forestSoldiers || [];
		const marks = ["1", "2", "3"];
		this.soldiers = kits.map((kit, i) => {
			const mark = kit.mark || marks[i];
			const pos = spawnOf(FOREST, mark);
			const axis = i === 0 ? "x" : i === 1 ? "y" : "none";
			return {
				id: kit.id,
				name: kit.name,
				x: pos.x,
				y: pos.y,
				dir: i === 0 ? "right" : i === 1 ? "left" : "up",
				frame: 0,
				anim: 0,
				beaten: false,
				chase: false,
				axis,
				min: axis === "x" ? pos.x - 16 : axis === "y" ? pos.y - 80 : 0,
				max: axis === "x" ? pos.x + 144 : axis === "y" ? pos.y + 80 : 0,
				sign: i === 0 ? 1 : i === 1 ? -1 : 0,
				species: kit.species,
				level: kit.level,
				marks: kit.marks ?? 8,
				winTalk: kit.winTalk || "soldierAfter",
			};
		});
	}
	soldierLos(sol) {
		if (sol.beaten || sol.chase) return false;
		const stx = Math.floor(sol.x / TILE);
		const sty = Math.floor(sol.y / TILE);
		const ptx = Math.floor(this.world.x / TILE);
		const pty = Math.floor(this.world.y / TILE);
		const dx = sol.dir === "left" ? -1 : sol.dir === "right" ? 1 : 0;
		const dy = sol.dir === "up" ? -1 : sol.dir === "down" ? 1 : 0;
		if (dx === 0 && dy === 0) return false;
		const map = this.map();
		const h = map.length;
		const w = map[0]?.length ?? 0;
		const max = Math.max(w, h);
		for (let i = 1; i <= max; i++) {
			const tx = stx + dx * i;
			const ty = sty + dy * i;
			const row = map[ty];
			if (!row || tx < 0 || tx >= row.length) return false;
			const ch = row[tx] ?? "#";
			if (solidTile(ch)) return false;
			if (tx === ptx && ty === pty) return true;
		}
		return false;
	}
	updateSoldiers(dt) {
		if (this.world.mapId !== "forest") return false;
		this.ensureSoldiers();
		let chasing = false;
		for (const sol of this.soldiers) {
			if (sol.beaten) continue;
			if (sol.chase) {
				chasing = true;
				const dx = this.world.x - sol.x;
				const dy = this.world.y - sol.y;
				const dist = Math.hypot(dx, dy) || 1;
				if (dist < 36) {
					sol.chase = false;
					this.pendingSoldier = sol.id;
					if (this.devWinAllMode) this.triggerDevWinAllFight("soldier");
					else this.say(TALK.soldierSpot, "soldier");
					this.audio.ok();
					return true;
				}
				const sp = 112 * dt;
				sol.x += dx / dist * sp;
				sol.y += dy / dist * sp;
				sol.dir = Math.abs(dx) > Math.abs(dy) ? dx < 0 ? "left" : "right" : dy < 0 ? "up" : "down";
				sol.anim += dt * 8;
				sol.frame = Math.floor(sol.anim) % 4;
				continue;
			}
			if (sol.axis === "x") {
				sol.x += sol.sign * 36 * dt;
				if (sol.x > sol.max) {
					sol.x = sol.max;
					sol.sign = -1;
					sol.dir = "left";
				} else if (sol.x < sol.min) {
					sol.x = sol.min;
					sol.sign = 1;
					sol.dir = "right";
				}
				sol.anim += dt * 4;
				sol.frame = Math.floor(sol.anim) % 4;
			} else if (sol.axis === "y") {
				sol.y += sol.sign * 36 * dt;
				if (sol.y > sol.max) {
					sol.y = sol.max;
					sol.sign = -1;
					sol.dir = "up";
				} else if (sol.y < sol.min) {
					sol.y = sol.min;
					sol.sign = 1;
					sol.dir = "down";
				}
				sol.anim += dt * 4;
				sol.frame = Math.floor(sol.anim) % 4;
			}
			if (this.soldierLos(sol)) {
				sol.chase = true;
				chasing = true;
				this.audio.ui();
			}
		}
		return chasing;
	}
	/** Any NPC whose script leads to a wsoldier battle is a roaming
	 *  hostile once beaten it just stops (matchNpcScript() picks a
	 *  different, no-battle step) -- gate-blockers (Calder, the
	 *  Priestess) never have this step at all, so they're excluded
	 *  automatically, no separate passIf check needed here. */
	roamableNpc(npc) {
		// Lieutenant Lead uses the same "wsoldier" battle-trigger as every
		// roaming ambush trainer (marshBog, forest soldiers, etc.) but is
		// meant to be stationary -- he only speaks or fights when the
		// player walks up and interacts, never chases. Excluded by id here
		// rather than dropping "wsoldier" from his script, which would also
		// break the shared battle-trigger wiring (startWsBattle()).
		if (npc.id === "lieutenantLead") return false;
		return !!npc.script?.some((s) => s.after === "wsoldier");
	}
	ensureRoamer(npc): Roamer {
		let r = this.roamers[npc.id];
		if (!r) {
			const mark = this.npcMarks(npc)[0];
			const s = mark ? spawnOf(this.map(), mark) : { x: 0, y: 0 };
			const dir = this.roamerFacing(npc, s.x, s.y);
			r = { x: s.x, y: s.y, chase: false, dir };
			this.roamers[npc.id] = r;
		}
		return r;
	}
	/** Prefer explicit npc.dir; else face toward map center so edge posts look inward. */
	roamerFacing(npc, x, y): Dir {
		const explicit = (npc as { dir?: Dir }).dir;
		if (explicit === "up" || explicit === "down" || explicit === "left" || explicit === "right") return explicit;
		const map = this.map();
		const midX = ((map[0]?.length ?? 1) * TILE) / 2;
		const midY = (map.length * TILE) / 2;
		const dx = midX - x;
		const dy = midY - y;
		if (Math.abs(dx) >= Math.abs(dy)) return dx < 0 ? "left" : "right";
		return dy < 0 ? "up" : "down";
	}
	/** Facing-only LOS, same ray shape as soldierLos(): true only when
	 *  the player is somewhere along the single straight line the
	 *  guard's `dir` faces (roamer.dir, set at spawn via
	 *  roamerFacing() and updated only while actively chasing), with
	 *  no solid tile blocking the way. A guard never sees behind or to
	 *  either side of itself. */
	roamerLos(x, y, dir: Dir) {
		const stx = Math.floor(x / TILE);
		const sty = Math.floor(y / TILE);
		const ptx = Math.floor(this.world.x / TILE);
		const pty = Math.floor(this.world.y / TILE);
		const dx = dir === "left" ? -1 : dir === "right" ? 1 : 0;
		const dy = dir === "up" ? -1 : dir === "down" ? 1 : 0;
		if (dx === 0 && dy === 0) return false;
		const map = this.map();
		const max = Math.max(map[0]?.length ?? 0, map.length);
		for (let i = 1; i <= max; i++) {
			const tx = stx + dx * i;
			const ty = sty + dy * i;
			const row = map[ty];
			if (!row || tx < 0 || tx >= row.length) return false;
			const ch = row[tx] ?? "#";
			if (solidTile(ch)) return false;
			if (tx === ptx && ty === pty) return true;
		}
		return false;
	}
	/** Generalizes updateSoldiers() to every non-gate-blocking wsoldier
	 *  trainer across every map instead of hardcoding the 3 FOREST
	 *  patrol soldiers. Stationary until it spots the player (no
	 *  patrol movement -- these NPCs never had any to begin with),
	 *  then closes in and triggers its own battle the same way a
	 *  manual walk-up-and-talk would (same TALK line, same
	 *  pendingWs/"wsoldier" handoff). */
	updateRoamers(dt) {
		const flags = this.npcFlags();
		let chasing = false;
		for (const npc of NPCS) {
			if (npc.map !== this.world.mapId || !this.roamableNpc(npc)) continue;
			if (this.npcHidden(npc, flags) || this.npcIsExecuted(npc.id)) continue;
			const step = matchNpcScript(npc.script, flags);
			const canFight = step?.after === "wsoldier";
			const r = this.ensureRoamer(npc);
			if (!canFight) {
				r.chase = false;
				continue;
			}
			if (r.chase) {
				chasing = true;
				const dx = this.world.x - r.x;
				const dy = this.world.y - r.y;
				const dist = Math.hypot(dx, dy) || 1;
				if (dist < 36) {
					r.chase = false;
					this.pendingWs = step?.pending ?? null;
					if (this.devWinAllMode) this.triggerDevWinAllFight("wsoldier");
					else this.say(TALK[step?.talk ?? npc.talk] || TALK.soldierSpot, "wsoldier");
					this.audio.ok();
					return true;
				}
				const sp = 112 * dt;
				r.x += dx / dist * sp;
				r.y += dy / dist * sp;
				r.dir = Math.abs(dx) > Math.abs(dy) ? (dx < 0 ? "left" : "right") : (dy < 0 ? "up" : "down");
				continue;
			}
			if (this.roamerLos(r.x, r.y, r.dir)) {
				r.chase = true;
				chasing = true;
				this.audio.ui();
			}
		}
		return chasing;
	}
	/** Checks the player's whole collision footprint (same r=10 box
	 *  blocked() uses), not just the single center-anchor pixel, so a warp
	 *  gate fires as soon as any part of the player overlaps its tile --
	 *  matching the full tile, not a pinpoint sub-region of it. Doors get
	 *  this same treatment now too, on top of tryDoor()'s own "ahead of
	 *  facing direction" pre-trigger. */
	tryMapWarp() {
		if (this.doorLock > 0) return;
		const { x, y } = this.world;
		const r = 10;
		const pts: [number, number][] = [[x, y], [x - r, y], [x + r, y], [x, y - r], [x, y + r]];
		for (const [px, py] of pts) {
			if (this.applyWarp(tileAt(this.map(), px, py))) return;
		}
	}
	warpTo(mapId, mark, dir, yOff = 0, xOff = 0) {
		const rows = MAPS[mapId];
		const s = spawnOf(rows, mark);
		this.world.mapId = mapId;
		this.world.x = s.x + xOff;
		this.world.y = s.y + yOff;
		this.world.dir = dir;
		this.world.encounterLock = 3;
		this.lastTx = -1;
		this.lastTy = -1;
		this.doorLock = .5;
		this.audio.ui();
		this.announceMap();
		if (this.clock - this.lastAutosave > 4) this.persist(false);
	}
	endingText() {
		return this.choseHeavenfall ? ENDING_WIN_HEAVENFALL : ENDING_WIN;
	}
	startWsBattle(who) {
		const kit = TRAINERS[who];
		if (!kit) return;
		this.pendingWs = who;
		this.startBattle(
			mintMonster(kit.lead[0], kit.lead[1]),
			false,
			kit.title,
			"wsoldier",
			who,
			kit.bench.map((b) => mintMonster(b[0], b[1]))
		);
	}
	startBattle(foe, wild, title, trainer = wild ? "wild" : "calder", soldierId = null, bench = []) {
		const lead = this.lead();
		if (!lead) return;
		this.markSeen(foe.species);
		for (const m of bench) this.markSeen(m.species);
		const player = { ...lead };
		const soldierName = soldierId ? (this.soldiers.find((s) => s.id === soldierId)?.name ?? soldierId) : "Soldier";
		const wsName = { sentry: "Sentry", conscript: "Conscript", enforcer: "Enforcer", cross: "Warden Cross", forestRanger: "Ranger", forestScout: "Scout", ruinsKeeper: "Keeper", ruinsWarden: "Warden", marshBog: "Bogwalker", marshReed: "Reedguard", quartz: "Quartz", opal: "Opal", quarryDriller: "Driller", commanderFinal: "Commander" };
		const foeName = wild
			? foe.name
			: trainer === "mason" || trainer === "mason2"
				? "Mason"
				: trainer === "soldier"
					? soldierName
					: trainer === "shinigami"
						? "Shinigami"
						: trainer === "wsoldier"
							? (wsName[soldierId] ?? "Soldier")
							: "Calder";
		this.battle = {
			wild,
			trainer,
			foeName,
			soldierId,
			player,
			foe,
			phase: "msg",
			cursor: 0,
			menu: [],
			msg: [`${title}!`],
			msgI: 0,
			afterMsg: "item",
			pendingDmg: 0,
			pendingLabel: "",
			pendingMods: { str: 0, agl: 0, spc: 0 },
			pendingEffectText: "",
			minigame: 0,
			minigameDir: 1,
			minigameHit: null,
			guard: null,
			mods: {
				selfStr: 0,
				selfAgl: 0,
				selfSpc: 0,
				foeStr: 0,
				foeAgl: 0,
				foeSpc: 0
			},
			catchUsed: false,
			t: 0,
			foeBench: bench,
			enterT: 0,
			faintT: 0,
			foeEnterT: 0,
			foeFaintT: 0,
			stage: { selfStr: 0, selfAgl: 0, selfSpc: 0, foeStr: 0, foeAgl: 0, foeSpc: 0 },
			hypeActive: { self: false, foe: false },
			movePpUsed: {},
		};
		
		if (foe && foe.species === "lead") {
			foe.name = "Lieutenant Lead";
			foe.level = 20;
			foe.maxHp = 60; foe.hp = 60;
			foe.str = 20; foe.agl = 20; foe.spc = 10;
		}
		this.mode = "battle";
		this.audio.ok();
	}
	leaveBattle() {
		const b = this.battle;
		if (b) this.party[this.partyIndex] = { ...b.player };
		this.mode = "world";
		this.battle = null;
		this.world.encounterLock = 3;
	}
	itemMenu() {
		const rows = ["Pass"];
		if (this.party.filter((m) => m.hp > 0).length > 1) {
			const nxt = this.party.find((m, i) => i !== this.partyIndex && m.hp > 0);
			if (nxt) rows.push(`Switch ${nxt.name}`);
		}
		ITEM_ORDER.forEach((id) => {
			if (this.bag[id] > 0 && ITEMS[id].battle) rows.push(this.itemBattleLabel(id));
		});
		return rows;
	}
	itemBattleLabel(id) {
		const n = this.bag[id];
		if (id === "bitterroot") return `Bitterroot +4 STR x${n}`;
		if (id === "dust") return `Ash dust -3/-2/-2 x${n}`;
		if (id === "salve") return `Moss salve +22 HP x${n}`;
		if (id === "bandage") return `Linen wrap +12 HP x${n}`;
		if (id === "sunbalm") return `Sunbalm +40 HP x${n}`;
		if (id === "warroot") return `Warroot +4 AGL x${n}`;
		if (id === "smokebomb") return `Smoke Bomb flee x${n}`;
		if (ITEMS[id].effect?.kind === "capture") {
			const b = this.battle;
			if (b?.wild) {
				const chance = captureChance(b.foe.level, b.foe.str, b.foe.hp, this.foeVulnerable(), ITEMS[id].effect.base ?? 100);
				return `${ITEMS[id].name} ${chance}% x${n}`;
			}
			return `${ITEMS[id].name} x${n}`;
		}
		return `${ITEMS[id].name} x${n}`;
	}
	/* "should be apparent when selecting an attack" -- a move's power/speed
	 * design values (0.5-1.5) are shown x10 as friendly 5-15 integers, right
	 * on the row (the web menu has plenty of width, unlike the Dreamcast's
	 * narrow battle content box, which uses a shared detail line instead). */
	atkDetail(stat, power, speed) {
		const statLabel = stat === "str" ? "STR" : "MAG";
		return `${statLabel} PWR${Math.round(power * 10)} SPD${Math.round(speed * 10)}`;
	}
	partyMoves(m) {
		return unlockedMoves(m, false).map((mv) => {
			if (mv.kind === "nmove" || mv.kind === "hypeUp") {
				const effect =
					mv.kind === "hypeUp"
						? `Raises all stats +${HYPE_UP.hypePercent}%`
						: mv.moveKind === "stage"
							? `Lowers foe ${(mv.statTarget || "").toUpperCase()}`
							: `Inflicts ${mv.statusTarget}`;
				return { name: mv.name, stat: mv.stat, power: 0, speed: mv.speed, pp: `${mv.maxPp}/battle`, dmg: 0, kind: mv.kind, effect };
			}
			const atk = atkStatValue(m, 0, 0, mv.stat);
			const dmg = Math.max(1, Math.round(atk * (mv.power || 0)));
			const pp = mv.pp ? `${m.specialPp}/${m.specialPpMax}` : null;
			return { name: mv.name, stat: mv.stat, power: mv.power, speed: mv.speed, pp, dmg, kind: mv.kind };
		});
	}
	attackMenu(p) {
		const b = this.battle;
		return unlockedMoves(p, true).map((mv) => {
			if (mv.kind === "wait") return "Wait";
			if (mv.kind === "nmove" || mv.kind === "hypeUp") {
				const remain = b ? this.movePpRemaining(b, p, mv) : mv.maxPp;
				const effect =
					mv.kind === "hypeUp"
						? "ALL STATS UP"
						: mv.moveKind === "stage"
							? `${(mv.statTarget || "").toUpperCase()} DOWN`
							: `${(mv.statusTarget || "").toUpperCase()}`;
				return `${mv.name}  ${remain}/${mv.maxPp}  ${effect}`;
			}
			const detail = this.atkDetail(mv.stat, mv.power, mv.speed);
			if (mv.pp) return `${mv.name}  ${p.specialPp}/${p.specialPpMax}  ${detail}`;
			return `${mv.name}  ${detail}`;
		});
	}
	updateBattle(dt) {
		const b = this.battle;
		b.t += dt;
		if (b.enterT < 10) b.enterT += dt;
		if (b.foeEnterT < 10) b.foeEnterT += dt;
		if (b.player.hp <= 0) b.faintT += dt;
		if (b.foe.hp <= 0 || b.afterMsg === "end_catch") b.foeFaintT += dt;
		if (b.phase === "msg") {
			if (this.input.confirm()) {
				this.audio.ui();
				b.msgI += 1;
				if (b.msgI >= b.msg.length) {
					if (b.afterMsg === "end_win") {
						this.finishWin();
						return;
					}
					if (b.afterMsg === "end_lose") {
						this.leaveBattle();
						this.world.encounterLock = 3;
						this.onBattleOver();
						if (this.choseHeavenfall) {
							this.beginHeavenfallGameOver();
						} else {
							this.startFade("loss");
						}
						return;
					}
					if (b.afterMsg === "end_catch" || b.afterMsg === "end_run") {
						this.leaveBattle();
						this.onBattleOver();
						return;
					}
					if (b.afterMsg === "catch_swap") {
						this.leaveBattle();
						this.onBattleOver();
						this.openParty("catchSwap");
						return;
					}
					b.phase = b.afterMsg;
					b.msg = [];
					b.msgI = 0;
					if (b.phase === "item") {
						b.menu = this.itemMenu();
						b.cursor = 0;
					}
					if (b.phase === "attack") {
						b.menu = this.attackMenu(b.player);
						b.cursor = 0;
					}
					if (b.phase === "guard") {
						b.menu = [
							"Dodge  AGI",
							"Block  STR",
							"Barrier  MAG"
						];
						b.cursor = 0;
					}
				}
			}
			return;
		}
		if (b.phase === "minigame") {
			const mg = COMBAT.minigame;
			const speed = mg?.needleSpeed ?? 110;
			b.minigame += b.minigameDir * dt * speed;
			if (b.minigame > 100) {
				b.minigame = 100;
				b.minigameDir = -1;
			}
			if (b.minigame < 0) {
				b.minigame = 0;
				b.minigameDir = 1;
			}
			if (this.input.confirm()) {
				b.minigameHit = b.minigame;
				const hit = b.minigame;
				let mul = mg?.fizzleMul ?? 1;
				let tag = "fizzled";
				if (hit >= (mg?.perfectMin ?? 45) && hit <= (mg?.perfectMax ?? 55)) {
					mul = mg?.perfectMul ?? 2;
					tag = "perfect";
					this.audio.special();
				} else if (hit >= (mg?.connectedMin ?? 30) && hit <= (mg?.connectedMax ?? 70)) {
					mul = mg?.connectedMul ?? 1.5;
					tag = "connected";
					this.audio.ok();
				} else this.audio.miss();
				const s = SPECIES[b.player.species];
				const atk = this.dmgStat(b, b.player, "self", s.specialStat);
				b.pendingDmg = Math.max(1, Math.round(atk * s.specialPower * mul));
				b.pendingLabel = `${s.special} ${tag}`;
				b.phase = "resolve_hit";
			}
			return;
		}
		if (b.phase === "resolve_hit") {
			const foeTick = this.tickStatus(b.foe);
			let line;
			if (b.pendingDmg > 0) {
				// Crystal matchup, applied once here rather than in each move
				// branch that sets pendingDmg, so every player attack is scaled
				// exactly once and by the same rule the foe's attacks get below.
				const hit = natureScaleDmg(b.pendingDmg, b.player.species, b.foe.species);
				b.foe.hp = Math.max(0, b.foe.hp - hit.dmg);
				this.shake = .25;
				this.audio.hit();
				line = `${b.pendingLabel}  ${hit.dmg} dmg.${natureTag(hit.sign)}${foeTick}`;
			} else {
				this.shake = .1;
				this.audio.ok();
				line = `${b.pendingLabel}${b.pendingEffectText ? ` ${b.pendingEffectText}` : ""}${foeTick}`;
			}
			b.pendingEffectText = "";
			const lines = [line];
			if (b.foe.hp <= 0) {
				const lines2 = [...lines, `${b.foe.name} falls.`];
				if (b.foeBench.length) {
					this.party[this.partyIndex] = { ...b.player };
					const xp = grantPartyXp(this.party, this.partyIndex, b.foe.level);
					for (const p of this.party) this.markCaught(p.species);
					b.player = { ...this.party[this.partyIndex] };
					const nxt = b.foeBench.shift();
					b.foe = nxt;
					b.mods.foeStr = 0;
					b.mods.foeAgl = 0;
					b.mods.foeSpc = 0;
					b.stage.foeStr = 0;
					b.stage.foeAgl = 0;
					b.stage.foeSpc = 0;
					b.hypeActive.foe = false;
					b.foeEnterT = 0;
					b.foeFaintT = 0;
					const evo = xp.notes[0] ? ` ${xp.notes[0]}` : "";
					b.msg = [...lines2, `${b.foeName} sends ${nxt.name}.${evo}`];
					b.msgI = 0;
					b.phase = "msg";
					b.afterMsg = "item";
					return;
				}
				b.msg = lines2;
				b.msgI = 0;
				b.phase = "msg";
				b.afterMsg = "end_win";
				return;
			}
			b.msg = [...lines, `${b.foeName} answers. Choose a guard.`];
			b.msgI = 0;
			b.phase = "msg";
			b.afterMsg = "guard";			return;
		}
		if (b.phase === "resolve_guard") {
			const selfTick = this.tickStatus(b.player);
			if (b.player.hp <= 0) {
				this.party[this.partyIndex] = { ...b.player };
				const next = this.party.findIndex((m, i) => i !== this.partyIndex && m.hp > 0);
				const line = `${b.player.name}${selfTick}`;
				if (next >= 0) {
					this.partyIndex = next;
					b.player = { ...this.party[next] };
					b.mods.selfStr = 0;
					b.mods.selfAgl = 0;
					b.mods.selfSpc = 0;
					b.stage.selfStr = 0;
					b.stage.selfAgl = 0;
					b.stage.selfSpc = 0;
					b.hypeActive.self = false;
					b.enterT = 0;
					b.faintT = 0;
					b.msg = [line, `${b.player.name} jumps in.`];
					b.msgI = 0;
					b.phase = "msg";
					b.afterMsg = "item";
					return;
				}
				b.msg = [line, `${b.player.name} cannot stand.`];
				b.msgI = 0;
				b.phase = "msg";
				b.afterMsg = "end_lose";
				return;
			}
			if (b.foe.status === "paralyzed") {
				this.tickStatus(b.foe);
				b.msg = [`${b.foe.name} is paralyzed and can't move.${selfTick}`];
				b.msgI = 0;
				b.phase = "msg";
				b.afterMsg = "item";
				return;
			}
			const confused = this.confusionOutcome(b.foe, false);
			if (confused && confused.kind !== "normal") {
				if (confused.kind === "none") {
					b.msg = [`${b.foe.name} is too confused to act.${selfTick}`];
				} else if (confused.kind === "self") {
					const dmg = Math.min(b.foe.hp - 1, confused.dmg);
					b.foe.hp = Math.max(1, b.foe.hp - Math.max(0, dmg));
					b.msg = [`${b.foe.name} is confused and hits itself!${selfTick}`];
				} else {
					const target = b.foeBench[confused.targetIdx];
					if (target) target.hp = Math.max(0, target.hp - confused.dmg);
					b.msg = [`${b.foe.name} is confused and hits ${target?.name ?? "an ally"}!${selfTick}`];
				}
				b.msgI = 0;
				b.phase = "msg";
				b.afterMsg = "item";
				return;
			}
			const g = b.guard ?? "block";
			const foeS = SPECIES[b.foe.species];
			let moveName = foeS.basic;
			let dmg = 0;
			let moveSpeed = foeS.basicSpeed;
			let pick = null;
			let effectText = "";
			const foeMoves = unlockedMoves(b.foe, false);
			const specials = foeMoves.filter((mv) => mv.kind === "special" || (mv.kind === "spell" && mv.pp));
			const nmoves = foeMoves.filter((mv) => mv.kind === "nmove" && this.movePpRemaining(b, b.foe, mv) > 0);
			const hypeMoves = foeMoves.filter((mv) => mv.kind === "hypeUp" && this.movePpRemaining(b, b.foe, mv) > 0);
			const basics = foeMoves.filter((mv) => mv.kind === "basic" || (mv.kind === "spell" && !mv.pp));
			pick = basics[0] || foeMoves[0];
			if (specials.length && b.foe.specialPp > 0 && Math.random() < 0.28) {
				pick = specials[randI(0, specials.length - 1)];
			} else if (hypeMoves.length && !b.hypeActive.foe && Math.random() < 0.15) {
				pick = hypeMoves[0];
			} else if (nmoves.length && Math.random() < 0.35) {
				pick = nmoves[randI(0, nmoves.length - 1)];
			} else if (basics.length) {
				pick = basics[randI(0, basics.length - 1)];
			}
			if (pick?.kind === "spell") {
				const result = this.castSpell(pick.spellId, false) ?? { dmg: 1, label: pick.name };
				dmg = result.dmg;
				moveName = result.label;
				moveSpeed = pick.speed;
			} else if (pick?.kind === "nmove") {
				this.spendMovePp(b, b.foe, pick);
				moveName = pick.name;
				moveSpeed = pick.speed;
				if (pick.moveKind === "stage") {
					effectText = `${(pick.statTarget || "").toUpperCase()} FALLS`;
				} else {
					effectText = `${(pick.statusTarget || "").toUpperCase()}`;
				}
			} else if (pick?.kind === "hypeUp") {
				// Self-buff -- always takes effect regardless of the player's
				// guard choice, unlike Proud Roar etc. which target the player
				// and can be dodged (see the `landed` gate below).
				this.spendMovePp(b, b.foe, pick);
				b.hypeActive.foe = true;
				moveName = pick.name;
				moveSpeed = pick.speed;
				effectText = "STATS UP";
			} else if (pick?.kind === "special") {
				b.foe.specialPp -= 1;
				const atk = this.dmgStat(b, b.foe, "foe", pick.stat);
				dmg = Math.max(1, Math.round(atk * pick.power));
				moveSpeed = pick.speed;
				moveName = pick.name;
			} else {
				const atk = this.dmgStat(b, b.foe, "foe", pick?.stat || foeS.basicStat);
				dmg = Math.max(1, Math.round(atk * (pick?.power || foeS.basicPower)));
				moveSpeed = pick?.speed || foeS.basicSpeed;
				moveName = pick?.name || foeS.basic;
			}
			// Matchup decides how hard the blow lands; the guard below decides
			// how much of it the player eats. Zero-damage nmove/hypeUp moves
			// scale to 0 harmlessly.
			const incoming = natureScaleDmg(dmg, b.foe.species, b.player.species);
			dmg = incoming.dmg;
			let line = "";
			let counterDmg = 0;
			let landed = true;
			if (g === "dodge") {
				const atkSpeed = this.effStat(b.foe, "agl", b.stage.foeAgl, b.hypeActive.foe, b.mods.foeAgl) * moveSpeed;
				const defSpeed = this.effStat(b.player, "agl", b.stage.selfAgl, b.hypeActive.self, b.mods.selfAgl) * frand(COMBAT.dodgeDefenderRandMin, COMBAT.dodgeDefenderRandMax);
				if (atkSpeed - defSpeed > 0) {
					line = dmg > 0 ? `The dodge fails. ${dmg} dmg.` : "The dodge fails.";
					this.audio.hit();
				} else {
					dmg = 0;
					landed = false;
					line = `${b.player.name} slips aside.`;
					this.audio.ok();
				}
			} else if (g === "block") {
				const blockScore = Math.round(this.dmgStat(b, b.player, "self", "str") * frand(COMBAT.guardRandMin, COMBAT.guardRandMax));
				const reduced = dmg - blockScore;
				if (reduced <= 0) {
					counterDmg = dmg;
					dmg = 0;
					line = counterDmg > 0 ? `${COMBAT.parriedText} Foe takes ${counterDmg} dmg.` : "";
					this.audio.ok();
				} else {
					dmg = reduced;
					line = `Blocked. ${dmg} dmg leaks through.`;
					this.audio.hit();
				}
			} else {
				const barrierScore = Math.round(this.dmgStat(b, b.player, "self", "mag") * frand(COMBAT.guardRandMin, COMBAT.guardRandMax));
				const reduced = dmg - barrierScore;
				if (reduced <= 0) {
					const heal = Math.floor(dmg / COMBAT.barrierHealDivisor);
					dmg = 0;
					b.player.hp = Math.min(b.player.maxHp, b.player.hp + heal);
					line = heal > 0 ? `${COMBAT.absorbedText} +${heal} HP.` : "";
					this.audio.ok();
				} else {
					dmg = reduced;
					line = `A thin barrier holds. ${dmg} dmg.`;
					this.audio.hit();
				}
			}
			// Only tag a hit that actually landed: a clean dodge/parry/absorb
			// zeroes dmg, and an effectiveness note on a blow that never
			// connected reads as a contradiction.
			if (dmg > 0) line += natureTag(incoming.sign);
			if (pick?.kind === "hypeUp") {
				// Already applied above (self-buff, not dodgeable) -- just show it.
				line = line ? `${line} ${effectText}` : effectText;
			} else if (landed && pick?.kind === "nmove") {
				if (pick.moveKind === "stage") this.advanceStage(b, "self", pick.statTarget);
				else this.inflictStatus(b.player, pick.statusTarget);
				line = line ? `${line} ${effectText}` : effectText;
			}
			b.player.hp = Math.max(0, b.player.hp - dmg);
			this.shake = dmg === 0 ? .05 : .28;
			if (b.player.hp <= 0) {
				this.party[this.partyIndex] = { ...b.player };
				const next = this.party.findIndex((m, i) => i !== this.partyIndex && m.hp > 0);
				if (next >= 0) {
					this.partyIndex = next;
					b.player = { ...this.party[next] };
					b.mods.selfStr = 0;
					b.mods.selfAgl = 0;
					b.mods.selfSpc = 0;
					b.stage.selfStr = 0;
					b.stage.selfAgl = 0;
					b.stage.selfSpc = 0;
					b.hypeActive.self = false;
					b.enterT = 0;
					b.faintT = 0;
					b.msg = [`${line}${selfTick}`, `${b.player.name} jumps in.`];
					b.msgI = 0;
					b.phase = "msg";
					b.afterMsg = "item";
					return;
				}
				b.msg = [`${line}${selfTick}`, `${b.player.name} cannot stand.`];
				b.msgI = 0;
				b.phase = "msg";
				b.afterMsg = "end_lose";
				return;
			}
			// A Parry's counter-blow can itself finish the foe.
			if (counterDmg > 0) {
				b.foe.hp = Math.max(0, b.foe.hp - counterDmg);
				if (b.foe.hp <= 0) {
					const lines = [`${b.foe.name} uses ${moveName}.`, `Parried! ${b.foe.name} falls.`];
					if (b.foeBench.length) {
						this.party[this.partyIndex] = { ...b.player };
						const xp = grantPartyXp(this.party, this.partyIndex, b.foe.level);
						for (const p of this.party) this.markCaught(p.species);
						b.player = { ...this.party[this.partyIndex] };
						const nxt = b.foeBench.shift();
						b.foe = nxt;
						b.mods.foeStr = 0;
						b.mods.foeAgl = 0;
						b.mods.foeSpc = 0;
						b.stage.foeStr = 0;
						b.stage.foeAgl = 0;
						b.stage.foeSpc = 0;
						b.hypeActive.foe = false;
						b.foeEnterT = 0;
						b.foeFaintT = 0;
						const evo = xp.notes[0] ? ` ${xp.notes[0]}` : "";
						b.msg = [...lines, `${b.foeName} sends ${nxt.name}.${evo}`];
						b.msgI = 0;
						b.phase = "msg";
						b.afterMsg = "item";
						return;
					}
					b.msg = lines;
					b.msgI = 0;
					b.phase = "msg";
					b.afterMsg = "end_win";
					return;
				}
			}
			b.msg = [`${b.foe.name} uses ${moveName}.`, `${line}${selfTick}`];
			b.msgI = 0;
			b.phase = "msg";
			b.afterMsg = "item";
			return;
		}
		if (b.phase === "item" || b.phase === "attack" || b.phase === "guard") {
			if (this.input.up()) {
				b.cursor = (b.cursor + b.menu.length - 1) % b.menu.length;
				this.audio.ui();
			}
			if (this.input.down()) {
				b.cursor = (b.cursor + 1) % b.menu.length;
				this.audio.ui();
			}
			if (this.input.cancel() && b.phase === "attack") {
				b.phase = "item";
				b.menu = this.itemMenu();
				b.cursor = 0;
				return;
			}
			if (this.input.confirm()) {
				if (b.phase === "item") this.pickItem(b.cursor);
				else if (b.phase === "attack") this.pickAttack(b.cursor);
				else this.pickGuard(b.cursor);
			}
		}
	}
	pickItem(i) {
		const b = this.battle;
		const label = b.menu[i] ?? "Pass";
		if (label === "Pass") {
			b.phase = "attack";
			b.menu = this.attackMenu(b.player);
			b.cursor = 0;
			this.audio.ui();
			return;
		}
		if (label.startsWith("Switch")) {
			const next = this.party.findIndex((m, idx) => idx !== this.partyIndex && m.hp > 0);
			if (next < 0) {
				b.msg = ["No other CryMon can stand."];
				b.msgI = 0;
				b.phase = "msg";
				b.afterMsg = "item";
				return;
			}
			this.party[this.partyIndex] = { ...b.player };
			this.partyIndex = next;
			b.player = { ...this.party[next] };
			b.msg = [`${b.player.name} out.`];
			b.msgI = 0;
			b.phase = "msg";
			b.afterMsg = "attack";
			this.audio.ok();
			return;
		}
		const id = Object.keys(ITEMS).find((k) => label.startsWith(ITEMS[k].name));
		if (!id || this.bag[id] <= 0) return;
		const fx = itemEffect(id);
		if (!fx) return;
		this.bag[id] -= 1;
		if (fx.kind === "heal") {
			const cap = fx.amount ?? healAmount(id);
			const n = Math.min(cap, b.player.maxHp - b.player.hp);
			b.player.hp += n;
			b.msg = [`${ITEMS[id].name}. ${n} HP.`];
		} else if (fx.kind === "buff") {
			b.mods.selfStr += fx.str ?? 0;
			b.mods.selfAgl += fx.agl ?? 0;
			b.mods.selfSpc += fx.spc ?? 0;
			b.msg = [ITEMS[id].desc];
		} else if (fx.kind === "debuff") {
			b.mods.foeStr += fx.str ?? 0;
			b.mods.foeAgl += fx.agl ?? 0;
			b.mods.foeSpc += fx.spc ?? 0;
			b.msg = [ITEMS[id].desc];
		} else if (fx.kind === "cleanse") {
			b.mods.selfStr = 0;
			b.mods.selfAgl = 0;
			b.mods.selfSpc = 0;
			b.stage.selfStr = 0;
			b.stage.selfAgl = 0;
			b.stage.selfSpc = 0;
			b.hypeActive.self = false;
			b.msg = [`${ITEMS[id].name}. Temporary changes cleared.`];
		} else if (fx.kind === "cure") {
			const had = b.player.status;
			if ((!had || had === "none") || (fx.status !== "all" && had !== fx.status)) {
				b.msg = [`${ITEMS[id].name} has no effect.`];
			} else {
				this.clearStatus(b.player);
				b.msg = [`${ITEMS[id].name}. Cured.`];
			}
		} else if (fx.kind === "flee") {
			if (!b.wild) {
				this.bag[id] += 1;
				b.msg = ["Cannot flee a tamer's fight."];
			} else {
				b.msg = [`${ITEMS[id].name}. ${this.playerDisplayName()} slips away.`];
				b.msgI = 0;
				b.phase = "msg";
				b.afterMsg = "end_run";
				this.audio.ok();
				return;
			}
		} else if (fx.kind === "capture") {
			if (!b.wild) {
				this.bag[id] += 1;
				b.msg = ["Crystals will not take a tamer's CryMon."];
			} else {
				const chance = captureChance(b.foe.level, b.foe.str, b.foe.hp, this.foeVulnerable(), fx.base ?? 100);
				if (randI(1, 100) <= chance) {
					const caught = {
						...b.foe,
						hp: Math.max(1, Math.floor(b.foe.maxHp * .4))
					};
					this.caughtOnce = true;
					this.markCaught(b.foe.species);
					if (b.foe.species === "cathleen") {
						this.cathleenCaught = true;
						this.beatCathleen = true;
					}
					if (b.foe.species === "heavenfall") {
						this.titleTamer = true;
						this.titleSlayer = false;
						this.beatHeavenfall = true;
						this.applyHeavenfallReviveRep();
						this.note("The world will know you as Heaven Tamer.");
					}
					if (this.party.length < PARTY_MAX) {
						this.party.push(caught);
						b.msg = [`${ITEMS[id].name} takes. ${b.foe.name} is yours.`];
						b.afterMsg = "end_catch";
					} else {
						this.pendingCatch = caught;
						b.msg = [
							`${ITEMS[id].name} takes. ${b.foe.name} is yours.`,
							`Six already travel with ${this.playerDisplayName()}. Release one to keep the new CryMon, or let it go.`
						];
						b.afterMsg = "catch_swap";
					}
					b.msgI = 0;
					b.phase = "msg";
					this.audio.catch();
					return;
				}
				b.msg = [`${ITEMS[id].name} cracks dark. It slips free.`];
			}
		}
		b.msgI = 0;
		b.phase = "msg";
		b.afterMsg = "attack";
		this.audio.ok();
	}
	pickAttack(i) {
		const b = this.battle;
		const mv = unlockedMoves(b.player, true)[i];
		if (!mv) return;
		b.pendingMods = { str: 0, agl: 0, spc: 0 };
		b.pendingEffectText = "";
		// Paralysis/confusion intercept before the chosen move even runs --
		// the turn-countdown/HP-tick itself happens once per round in
		// resolve_guard, not here, so this only checks and bypasses.
		if (b.player.status === "paralyzed") {
			b.pendingDmg = 0;
			b.pendingLabel = `${b.player.name} is paralyzed and can't move.`;
			b.phase = "resolve_hit";
			this.audio.miss();
			return;
		}
		const confused = this.confusionOutcome(b.player, true);
		if (confused && confused.kind !== "normal") {
			b.pendingDmg = 0;
			if (confused.kind === "none") {
				b.pendingLabel = `${b.player.name} is too confused to act.`;
			} else if (confused.kind === "self") {
				const dmg = Math.max(0, Math.min(b.player.hp - 1, confused.dmg));
				b.player.hp = Math.max(1, b.player.hp - dmg);
				b.pendingLabel = `${b.player.name} is confused and hits itself!`;
			} else {
				const target = this.party[confused.targetIdx];
				if (target) target.hp = Math.max(0, target.hp - confused.dmg);
				b.pendingLabel = `${b.player.name} is confused and hits ${target?.name ?? "an ally"}!`;
			}
			b.phase = "resolve_hit";
			this.audio.miss();
			return;
		}
		if (mv.kind === "wait") {
			b.msg = [`${b.player.name} holds.`];
			b.msgI = 0;
			b.phase = "msg";
			b.afterMsg = "guard";
			this.audio.ui();
			return;
		}
		if (mv.kind === "spell") {
			this.castSpell(mv.spellId, true);
			return;
		}
		if (mv.kind === "nmove" || mv.kind === "hypeUp") {
			if (!this.spendMovePp(b, b.player, mv)) {
				b.msg = [`${mv.name} is spent.`];
				b.msgI = 0;
				b.phase = "msg";
				b.afterMsg = "attack";
				return;
			}
			b.pendingDmg = 0;
			b.pendingLabel = mv.name;
			if (mv.kind === "hypeUp") {
				b.hypeActive.self = true;
				b.pendingEffectText = "STATS UP";
			} else if (mv.moveKind === "stage") {
				this.advanceStage(b, "foe", mv.statTarget);
				b.pendingEffectText = `${(mv.statTarget || "").toUpperCase()} FALLS`;
			} else {
				this.inflictStatus(b.foe, mv.statusTarget);
				b.pendingEffectText = `${(mv.statusTarget || "").toUpperCase()}`;
			}
			b.phase = "resolve_hit";
			this.audio.special();
			return;
		}
		if (mv.kind === "special") {
			if (b.player.specialPp <= 0) {
				b.msg = [`${mv.name} is spent.`];
				b.msgI = 0;
				b.phase = "msg";
				b.afterMsg = "attack";
				return;
			}
			b.player.specialPp -= 1;
			b.minigame = 8;
			b.minigameDir = 1;
			b.minigameHit = null;
			b.phase = "minigame";
			this.audio.special();
			return;
		}
		const atk = this.dmgStat(b, b.player, "self", mv.stat);
		b.pendingDmg = Math.max(1, Math.round(atk * mv.power));
		b.pendingLabel = mv.name;
		b.phase = "resolve_hit";
	}
	foeDebuffed() {
		const m = this.battle.mods, s = this.battle.stage;
		return m.foeStr < 0 || m.foeAgl < 0 || m.foeSpc < 0 || s.foeStr > 0 || s.foeAgl > 0 || s.foeSpc > 0;
	}
	/** Capture-chance-only: a stat debuff OR any status condition
	 *  (burned/poisoned/paralyzed/confused/exhausted) both count as
	 *  "vulnerable" for the crystal's flat +50, matching every capture
	 *  item's own description text ("Status adds +50"). Kept separate
	 *  from foeDebuffed() itself, which Mana Surge's own 2x-damage check
	 *  also reads -- status conditions shouldn't widen that unrelated
	 *  mechanic just because they now count here. */
	foeVulnerable() {
		const status = this.battle.foe.status;
		return this.foeDebuffed() || (!!status && status !== "none");
	}
	selfDebuffed() {
		const m = this.battle.mods, s = this.battle.stage;
		return m.selfStr < 0 || m.selfAgl < 0 || m.selfSpc < 0 || s.selfStr > 0 || s.selfAgl > 0 || s.selfSpc > 0;
	}
	/* Leg 2.11: stage-based stat drops + real status conditions.
	 * effStat() composes base -> statStages multiplier -> Hype Up's flat
	 * +35%-of-base -> the pre-existing flat item mod, in that order. */
	effStat(m, stat, stageVal, hyped, flatMod) {
		const base = stat === "str" ? m.str : stat === "agl" ? m.agl : m.spc;
		let v = effectiveStat(base, stageVal);
		if (hyped) v += Math.round((base * HYPE_UP.hypePercent) / 100);
		return v + flatMod;
	}
	/** atkStatValue's replacement for in-battle damage: folds in this side's
	 *  stat stage (Proud Roar/Magebane/etc knocked it down) and Hype Up on
	 *  top of the pre-existing flat item mod. atkStat is "str"|"mag" (mag
	 *  reads the spc stat, matching atkStatValue's own convention). */
	dmgStat(b, m, side, atkStat) {
		const statKey = atkStat === "str" ? "str" : "spc";
		const stage = side === "self" ? (statKey === "str" ? b.stage.selfStr : b.stage.selfSpc) : (statKey === "str" ? b.stage.foeStr : b.stage.foeSpc);
		const hyped = side === "self" ? b.hypeActive.self : b.hypeActive.foe;
		const flat = side === "self" ? (statKey === "str" ? b.mods.selfStr : b.mods.selfSpc) : (statKey === "str" ? b.mods.foeStr : b.mods.foeSpc);
		return this.effStat(m, statKey, stage, hyped, flat);
	}
	movePpKey(m, mv) {
		return `${m.id}:${mv.kind === "hypeUp" ? "hype" : "nmove"}`;
	}
	movePpRemaining(b, m, mv) {
		return (mv.maxPp ?? 0) - (b.movePpUsed[this.movePpKey(m, mv)] ?? 0);
	}
	spendMovePp(b, m, mv) {
		const key = this.movePpKey(m, mv);
		const used = b.movePpUsed[key] ?? 0;
		if (used >= (mv.maxPp ?? 0)) return false;
		b.movePpUsed[key] = used + 1;
		return true;
	}
	/** Advances one stat's stage on the given side by 1 (capped). side is
	 *  "self" or "foe" as seen from the CryMon whose stat is dropping. */
	advanceStage(b, side, stat) {
		const key = `${side}${stat === "str" ? "Str" : stat === "agl" ? "Agl" : "Spc"}`;
		b.stage[key] = Math.min(STAT_STAGES.maxStage, b.stage[key] + 1);
	}
	/** Inflicts a status on a Monster, replacing whatever was active. Rolls
	 *  the burn/paralysis turn count once here, at inflict time. */
	inflictStatus(m, status) {
		m.status = status;
		if (status === "burned") {
			const e = STATUS_EFFECTS.burned;
			m.statusTurns = randI(e.turnsMin, e.turnsMax);
			m.poisonStack = 0;
		} else if (status === "paralyzed") {
			const e = STATUS_EFFECTS.paralyzed;
			m.statusTurns = randI(e.turnsMin, e.turnsMax);
			m.poisonStack = 0;
		} else if (status === "poisoned") {
			m.statusTurns = 0;
			m.poisonStack = 0;
		} else {
			m.statusTurns = 0;
			m.poisonStack = 0;
		}
	}
	clearStatus(m) {
		m.status = "none";
		m.statusTurns = 0;
		m.poisonStack = 0;
	}
	/** One status tick (HP drain + turn countdown), called once per side per
	 *  round. Returns a short message suffix, or "" if nothing happened. */
	tickStatus(m) {
		if (!m.status || m.status === "none" || m.hp <= 0) return "";
		if (m.status === "burned") {
			const tick = Math.max(1, Math.round((m.maxHp * STATUS_EFFECTS.burned.hpPercent) / 100));
			m.hp = Math.max(0, m.hp - tick);
			m.statusTurns = (m.statusTurns ?? 1) - 1;
			if (m.statusTurns <= 0) this.clearStatus(m);
			return ` Burn-${tick}`;
		}
		if (m.status === "poisoned") {
			m.poisonStack = (m.poisonStack ?? 0) + 1;
			const pct = STATUS_EFFECTS.poisoned.startPercent + (m.poisonStack - 1) * STATUS_EFFECTS.poisoned.stepPercent;
			const tick = Math.max(1, Math.round((m.maxHp * pct) / 100));
			m.hp = Math.max(0, m.hp - tick);
			return ` Psn-${tick}`;
		}
		if (m.status === "paralyzed") {
			m.statusTurns = (m.statusTurns ?? 1) - 1;
			if (m.statusTurns <= 0) this.clearStatus(m);
			return "";
		}
		return "";
	}
	/** Confusion's 4-way roll. self=true for the player's own side. Returns
	 *  null if the CryMon isn't confused (caller proceeds normally), or a
	 *  {kind, dmg?, targetIdx?} describing what confusion did instead. */
	confusionOutcome(m, self) {
		if (m.status !== "confused") return null;
		const roll = randI(0, 3);
		if (roll === 0) return { kind: "normal" };
		if (roll === 1) return { kind: "none" };
		const basic = SPECIES[m.species];
		const selfDmg = Math.max(1, Math.round(m.str * basic.basicPower));
		if (roll === 2) return { kind: "self", dmg: selfDmg };
		if (self) {
			const others = this.party.map((_, i) => i).filter((i) => i !== this.partyIndex && this.party[i].hp > 0);
			if (!others.length) return { kind: "self", dmg: selfDmg };
			const idx = others[randI(0, others.length - 1)];
			return { kind: "ally", dmg: selfDmg, targetIdx: idx };
		}
		const bench = this.battle.foeBench.map((_, i) => i).filter((i) => this.battle.foeBench[i].hp > 0);
		if (!bench.length) return { kind: "self", dmg: selfDmg };
		const idx = bench[randI(0, bench.length - 1)];
		return { kind: "ally", dmg: selfDmg, targetIdx: idx };
	}
	castSpell(id, fromPlayer) {
		const b = this.battle;
		const caster = fromPlayer ? b.player : b.foe;
		const s = SPECIES[caster.species];
		let dmg = 0;
		let label = "";
		const spell = s.spells?.find((sp) => sp.id === id);
		const power = spell?.power ?? 1;
		if (id === "firebolt") {
			if (fromPlayer) b.mods.foeStr -= 4;
			else b.mods.selfStr -= 4;
			dmg = Math.max(1, Math.round(caster.spc * power));
			label = "Fire Bolt  STR-4";
		} else if (id === "icebeam") {
			if (fromPlayer) b.mods.foeAgl -= 4;
			else b.mods.selfAgl -= 4;
			dmg = Math.max(1, Math.round(caster.spc * power));
			label = "Ice Beam  AGI-4";
		} else if (id === "lightning") {
			if (fromPlayer) b.mods.foeSpc -= 4;
			else b.mods.selfSpc -= 4;
			dmg = Math.max(1, Math.round(caster.spc * power));
			label = "Lightning Strike  MAG-4";
		} else if (id === "manasurge") {
			if (caster.specialPp <= 0) {
				if (fromPlayer) {
					b.msg = [`${s.special} is spent.`];
					b.msgI = 0;
					b.phase = "msg";
					b.afterMsg = "attack";
				}
				return;
			}
			caster.specialPp -= 1;
			const debuffed = fromPlayer ? this.foeDebuffed() : this.selfDebuffed();
			const mul = debuffed ? 2 : 1;
			dmg = Math.max(1, Math.round(caster.spc * power * mul));
			label = debuffed ? "Mana Surge  2x" : "Mana Surge";
		}
		if (fromPlayer) {
			b.pendingDmg = dmg;
			b.pendingLabel = label;
			b.phase = "resolve_hit";
			this.audio.special();
			return;
		}
		return { dmg, label };
	}
	pickGuard(i) {
		const kinds = [
			"dodge",
			"block",
			"barrier"
		];
		const b = this.battle;
		b.guard = kinds[i] ?? "block";
		b.phase = "resolve_guard";
	}
	/** Dev Codes console (web preview only, see devPassAll above).
	 *  Returns a short status string for the UI to display. */
	submitDevCode(raw: string): string {
		const code = raw.trim().toLowerCase();
		if (code === "winall") {
			this.devWinAllMode = true;
			if (this.mode === "battle" && this.battle) {
				this.devWinAll();
				return "WinAll: battle won, and active for every fight from now on.";
			}
			if (this.mode === "mercy" && this.battle) {
				this.mode = "world";
				this.battle = null;
				this.world.encounterLock = 3;
				this.onBattleOver();
				return "WinAll: left mercy, and active for every fight from now on.";
			}
			return "WinAll: active. Every trainer you engage (not a Backstab) is now an instant win.";
		}
		if (code === "passall") {
			this.devPassAll = true;
			return "PassAll: all warp gates open, noclip on.";
		}
		return `Unknown dev code: "${raw}"`;
	}
	/** Skips straight to the end of the current battle as a win, exactly
	 *  as if every enemy CryMon had just fainted -- reuses finishWin()
	 *  (trainer/story-flag handling, mercy prompts, XP) rather than
	 *  faking a simpler ending, so it can't drift from a real win. */
	devWinAll() {
		const b = this.battle;
		if (!b) return;
		b.foe.hp = 0;
		b.foeBench = [];
		this.finishWin();
	}
	/** Whether an `after` leads to the mercy menu on a real win -- the
	 *  set devWinAllMode auto-resolves. Narrower than isFightAfter()
	 *  (used for Backstab eligibility, which also covers cathleen/
	 *  shinigami/mason -- those never open mercy even on a real win,
	 *  so "go straight to the mercy menu" doesn't apply to them; they
	 *  keep their own one-off win dialogue/flow untouched). */
	isMercyFightAfter(after: string | null | undefined): after is "calder" | "soldier" | "wsoldier" {
		return after === "calder" || after === "soldier" || after === "wsoldier";
	}
	/** devWinAllMode: builds the same battle a real encounter would
	 *  (mirrors advanceTalk()'s "calder"/"soldier"/"wsoldier" dispatch)
	 *  and instantly resolves it as a win via devWinAll(), landing
	 *  straight in the mercy menu these three trainer types already
	 *  open on a real win -- skips both the pre-fight dialogue and the
	 *  battle itself. Callers set pendingSoldier/pendingWs first, same
	 *  as they would before showing that dialogue normally. */
	triggerDevWinAllFight(after: "calder" | "soldier" | "wsoldier") {
		if (after === "calder") {
			const kit = TRAINERS.calder;
			this.startBattle(mintMonster(kit.lead[0], kit.lead[1]), false, kit.title, "calder");
		} else if (after === "soldier") {
			const sol = this.soldiers.find((s) => s.id === this.pendingSoldier);
			if (sol && !sol.beaten) this.startBattle(mintMonster(sol.species, sol.level), false, `${sol.name} sends ${SPECIES[sol.species].name}`, "soldier", sol.id);
		} else if (after === "wsoldier") {
			this.startWsBattle(this.pendingWs);
		}
		if (this.mode === "battle" && this.battle) this.devWinAll();
	}
	finishWin() {
		const b = this.battle;
		this.party[this.partyIndex] = { ...b.player };
		const m = this.party[this.partyIndex];
		const { grew, notes } = grantPartyXp(this.party, this.partyIndex, b.foe.level);
		for (const p of this.party) this.markCaught(p.species);
		if (notes[0]) this.note(notes[0]);
		if (!b.wild) {
			if (b.trainer === "calder") {
				const kit = TRAINERS.calder;
				this.beatCalder = true;
				if (!this.mason2Done && !this.mason2Map) this.mason2Map = pickMason2Map(Math.random());
				this.marks += kit.marks ?? 18;
				this.audio.ok();
				this.openMercy(b);
				return;
			}
			if (b.trainer === "soldier") {
				const sol = this.soldiers.find((s) => s.id === b.soldierId);
				if (sol) sol.beaten = true;
				this.marks += sol?.marks ?? 8;
				this.audio.ok();
				this.openMercy(b);
				return;
			}
			if (b.trainer === "wsoldier") {
				const who = b.soldierId || this.pendingWs;
				this.mode = "world";
				this.battle = null;
				this.world.encounterLock = 3;
				this.onBattleOver();
				const kit = TRAINERS[who];
				if (kit?.grant) {
					for (const [iid, qty] of kit.grant) {
						this.bag[iid] = (this.bag[iid] ?? 0) + qty;
					}
				}
				if (who === "sentry") this.beatSentry = true;
				else if (who === "conscript") this.beatConscript = true;
				else if (who === "enforcer") this.beatEnforcer = true;
				else if (who === "cross") this.beatCross = true;
				else if (who === "forestRanger") this.beatForestRanger = true;
				else if (who === "forestScout") this.beatForestScout = true;
				else if (who === "ruinsKeeper") this.beatRuinsKeeper = true;
				else if (who === "ruinsWarden") this.beatRuinsWarden = true;
				else if (who === "marshBog") this.beatMarshBog = true;
				else if (who === "marshReed") this.beatMarshReed = true;
				else if (who === "quartz") this.badgeQuartz = true;
				else if (who === "opal") this.badgeOpal = true;
				else if (who === "quarryDriller") this.beatQuarryDriller = true;
				else if (who === "commanderFinal") this.beatCommander = true;
				else if (who === "lieutenantLead") {
					this.beatLieutenantLead = true;
					this.say(TALK.leadWinPlaceholder || [{ speaker: "none", text: "Thank you for playing." }], "leadThanksGO");
					return;
				}
				else if (who === "heavenfallGrave") {
					this.beatHeavenfall = true;
						this.applyHeavenfallReviveRep();
					this.titleSlayer = true;
					this.titleTamer = false;
					this.marks += kit?.marks ?? 12;
					this.audio.ok();
					this.note("The world will know you as Heaven Slayer.");
					this.say(TALK.gauntletGraveWin || [{ speaker: "max", text: "Heavenfall falls." }], "creditsFinal");
					return;
				}
				this.marks += kit?.marks ?? 12;
				// Win talk deferred; mercy menu first (not mason/shinigami).
				this.audio.ok();
				this.openMercy(b);
				return;
			}
			if (b.trainer === "shinigami") {
				const kit = TRAINERS.shinigami;
				this.beatShinigami = true;
				this.hasScroll = true;
				this.marks += kit.marks ?? 14;
				this.mode = "world";
				this.battle = null;
				this.world.encounterLock = 3;
				this.onBattleOver();
				this.say(TALK[kit.winTalk] || TALK.shinigamiAfter, "choice");
				this.audio.ok();
				return;
			}
			if (b.trainer === "mason2") {
				this.mason2Done = true;
				this.masonRematch = false;
				this.marks += LOGIC.masonRematch.battle.marks;
				this.mode = "world";
				this.battle = null;
				this.world.encounterLock = 3;
				this.onBattleOver();
				this.say(TALK[LOGIC.masonRematch.battle.winTalk], "masonLeave");
				this.audio.ok();
				return;
			}
			const kit = TRAINERS.mason;
			this.foughtMason = true;
			this.rival.phase = "done";
			this.marks += kit.marks ?? 10;
			this.mode = "world";
			this.battle = null;
			this.world.encounterLock = 3;
			this.onBattleOver();
			this.say(TALK[kit.winTalk] || TALK.masonWin, "masonLeave");
			this.audio.ok();
			return;
		}
		this.marks += 3;
		this.mode = "world";
		this.battle = null;
		this.world.encounterLock = 3;
		this.onBattleOver();
		if (b.foe.species === "cathleen" && !this.cathleenCaught) {
			this.beatCathleen = true;
			this.say(TALK.cathleenAfter);
			return;
		}
		this.note(notes[0] || (grew ? `${m.name} grew to lv ${m.level}.` : `${m.name} stands over the grass.`));
	}

	/** Combined level of the defeated trainer's CryMon (lead + bench). */

	/** Bit index for permanent execute-delete (Leg 2.9.4). */

	npcIsExecuted(npcId) {
		const map = {
			calder: ["calder", null],
			cross: ["wsoldier", "cross"],
			conscript: ["wsoldier", "conscript"],
			enforcer: ["wsoldier", "enforcer"],
			sentry: ["wsoldier", "sentry"],
			forestRanger: ["wsoldier", "forestRanger"],
			forestScout: ["wsoldier", "forestScout"],
			ruinsKeeper: ["wsoldier", "ruinsKeeper"],
			ruinsWarden: ["wsoldier", "ruinsWarden"],
			marshBog: ["wsoldier", "marshBog"],
			marshReed: ["wsoldier", "marshReed"],
			quartz: ["wsoldier", "quartz"],
			opal: ["wsoldier", "opal"],
			quarryDriller: ["wsoldier", "quarryDriller"],
			commanderFinal: ["wsoldier", "commanderFinal"],
			heavenfallGrave: ["wsoldier", "heavenfallGrave"],
			soldier1: ["soldier", "soldier1"],
			soldier2: ["soldier", "soldier2"],
			soldier3: ["soldier", "soldier3"]
		};
		const pair = map[npcId];
		if (!pair) return false;
		return this.isExecuted(pair[0], pair[1]);
	}

	mercyExecBit(trainer, soldierId) {
		if (trainer === "calder") return 0;
		if (trainer === "soldier") {
			const id = soldierId || "";
			if (id.includes("1") || id === "soldier1") return 1;
			if (id.includes("2") || id === "soldier2") return 2;
			return 3;
		}
		const map = {
			sentry: 4, conscript: 5, enforcer: 6, cross: 7,
			forestRanger: 8, forestScout: 9, ruinsKeeper: 10, ruinsWarden: 11,
			marshBog: 12, marshReed: 13, quartz: 14, opal: 15,
			quarryDriller: 16, commanderFinal: 17
		};
		if (trainer === "wsoldier") return map[soldierId] ?? 18;
		return map[trainer] ?? -1;
	}
	isExecuted(trainer, soldierId) {
		const bit = this.mercyExecBit(trainer, soldierId);
		if (bit < 0) return false;
		return (this.executedMask & (1 << bit)) !== 0;
	}
	markExecuted(trainer, soldierId) {
		const bit = this.mercyExecBit(trainer, soldierId);
		if (bit >= 0) this.executedMask |= 1 << bit;
	}

	foePartyLevels(b) {
		if (!b) return 0;
		let n = b.foe?.level ?? 0;
		for (const m of b.foeBench || []) n += m.level || 0;
		return n;
	}
	/** Open Leg 2.9 mercy menu after a human trainer win (not Mason/Shinigami). */
	openMercy(b) {
		this.mercyCur = 0;
		this.mercyTrainer = b.trainer;
		this.mercySoldierId = b.soldierId;
		this.mercyFoeLevels = this.foePartyLevels(b);
		this.mercyFoeName = b.foeName || "Trainer";
		this.mode = "mercy";
		this.battle = null;
		this.world.encounterLock = 3;
		this.onBattleOver();
	}
	updateMercy() {
		if (this.input.up()) {
			this.mercyCur = (this.mercyCur + 3) % 4;
			this.audio.ui();
		} else if (this.input.down()) {
			this.mercyCur = (this.mercyCur + 1) % 4;
			this.audio.ui();
		}
		if (this.input.confirm()) {
			this.audio.ok();
			this.resolveMercy(this.mercyCur);
		}
	}
	/** Random baggable item id (excludes quest-only cageKey). */
	randomMercyItem() {
		const pool = Object.keys(ITEMS).filter((id) => id !== "cageKey");
		return pool[Math.floor(Math.random() * pool.length)] || "salve";
	}
	resolveMercy(choice) {
		const levels = this.mercyFoeLevels || 1;
		this.mode = "world";
		if (choice === 0) {
			// Let them go: +1 rep, random dismiss line
			this.adjustReputation(1);
			const lines = MERCY_DISMISS;
			const line = lines[Math.floor(Math.random() * lines.length)] || lines[0];
			this.say([{ speaker: "none", text: line }]);
		} else if (choice === 1) {
			// Threaten for marks: -1 rep, marks = combined levels
			this.adjustReputation(-1);
			this.marks += levels;
			this.say(TALK.mercyThreaten || [{ speaker: "none", text: "Don't hurt me, just take it!" }]);
			this.note(`Took ${levels} marks.`);
		} else if (choice === 2) {
			// Threaten for item: -2 rep, one random item
			this.adjustReputation(-2);
			const id = this.randomMercyItem();
			this.bag[id] = (this.bag[id] ?? 0) + 1;
			this.say(TALK.mercyThreaten || [{ speaker: "none", text: "Don't hurt me, just take it!" }]);
			this.note(`Took ${ITEMS[id]?.name || id}.`);
		} else {
			// Execute: -10 rep, marks = levels*10, 2 items, permanent delete
			this.adjustReputation(-10);
			const gain = levels * 10;
			this.marks += gain;
			const a = this.randomMercyItem();
			const b = this.randomMercyItem();
			this.bag[a] = (this.bag[a] ?? 0) + 1;
			this.bag[b] = (this.bag[b] ?? 0) + 1;
			this.markExecuted(this.mercyTrainer, this.mercySoldierId);
			this.audio.scream();
			this.startFade("execute");
			this.say(TALK.mercyExecute || [{ speaker: "max", text: "No survivors, no witnesses." }]);
			this.note(`Took ${gain} marks and loot.`);
		}
	}
	drawMercy() {
		this.drawWorld();
		this.ctx.fillStyle = "rgba(18,17,14,0.55)";
		this.ctx.fillRect(0, 0, VIEW_W, VIEW_H);
		this.box(X(16), Y(16), X(208), Y(128));
		this.text("AFTER THE FIGHT", X(120), Y(22), "#c5cec6", FONT, "center");
		this.text(`${this.mercyFoeName} is beaten.`, X(28), Y(38), "#8a8678", FONT);
		const rows = [
			"Let Them Go",
			"Threaten For Marks",
			"Threaten For An Item",
			"Execute"
		];
		rows.forEach((row, i) => {
			const on = i === this.mercyCur;
			this.text(on ? `> ${row}` : `  ${row}`, X(28), Y(56 + i * 14), on ? "#e8e4d8" : "#8a8678", FONT);
		});
		this.text("Z  choose", X(28), Y(128), "#5a7a52", FONT);
	}
	/** Whether a script step's `after` leads to an actual fight (as
	 *  opposed to a shop, heal, or plain-talk step) -- the set of
	 *  trainer types Backstab is offered against. */
	/** The set of trainer types Backstab is offered against -- this
	 *  function's only caller is canBackstab(). Cathleen and Shinigami are
	 *  deliberately excluded (per request): both still fight normally via
	 *  the ordinary talk-then-battle path, just never through Backstab. */
	isFightAfter(after: string | undefined | null): boolean {
		if (!after) return false;
		return (
			after === "wsoldier" ||
			after === "calder" ||
			after === "soldier" ||
			after === "mason" ||
			after === "mason2"
		);
	}
	npcOnWarpGate(npc): boolean {
		const marks = this.npcMarks(npc);
		if (!marks.length) return false;
		const mapId = npc.map;
		return WARPS.some((w) => w.from === mapId && marks.includes(w.tile));
	}
	/** Whether npc (with its currently-matched script step) is a valid
	 *  Backstab target: a roamable wsoldier trainer that hasn't spotted
	 *  the player yet (no active chase), still fightable, not standing
	 *  on a warp gate tile, while the player carries the Bowie Knife.
	 *  FOREST patrol/scout/sentry aren't NPCS-table entries, so they
	 *  never reach this check -- see canBackstabSoldier() below. */
	canBackstab(npc, step) {
		// Stationary and always facing the road he blocks -- never eligible.
		if (npc.id === "lieutenantLead") return false;
		if (!(this.bag.bowieKnife > 0)) return false;
		if (!step || !this.isFightAfter(step.after)) return false;
		if (this.npcIsExecuted(npc.id)) return false;
		if (this.npcOnWarpGate(npc)) return false;
		if (this.roamableNpc(npc)) {
			const r = this.ensureRoamer(npc);
			if (r.chase) return false;
			if (this.roamerLos(r.x, r.y, r.dir)) return false;
		}
		return true;
	}
	/** The 3 FOREST patrol/scout/sentry trainers live in their own
	 *  this.soldiers array (ensureSoldiers()), not the generic NPCS/
	 *  script table runClosestNpc() walks -- canBackstab() never sees
	 *  them, so interact()'s forest branch checks this directly before
	 *  falling into its normal always-confront flow. Same three gates
	 *  as canBackstab(): knife carried, not already dealt with, hasn't
	 *  spotted the player (soldierLos(), same one-direction facing ray
	 *  chase detection uses). No warp-gate check needed -- none of the
	 *  forest soldier marks ('1'/'2'/'3') are ever a warp tile. */
	canBackstabSoldier(sol): boolean {
		if (!(this.bag.bowieKnife > 0)) return false;
		if (sol.beaten || sol.chase) return false;
		if (this.soldierLos(sol)) return false;
		return true;
	}
	openBackstabChoiceForSoldier(sol) {
		this.pendingBackstab = {
			npc: null,
			pending: sol.id,
			after: "soldier",
			talk: "soldierSpot",
			levels: sol.level || 1,
		};
		this.backstabCur = 0;
		this.mode = "backstab";
		this.audio.ui();
	}
	openBackstabChoice(npc, step) {
		const kitKey =
			step.pending ||
			(step.after === "calder"
				? "calder"
				: step.after === "shinigami"
					? "shinigami"
					: step.after === "cathleen"
						? "cathleen"
						: step.after === "mason" || step.after === "mason2"
							? "mason"
							: step.pending);
		const kit = kitKey ? TRAINERS[kitKey] : null;
		const levels = kit ? (kit.lead?.[1] || 0) + (kit.bench || []).reduce((s, b) => s + (b[1] || 0), 0) : 1;
		this.pendingBackstab = {
			npc,
			pending: step.pending || kitKey || "",
			after: step.after || "",
			talk: step.talk,
			levels,
		};
		this.backstabCur = 0;
		this.mode = "backstab";
		this.audio.ui();
	}

	updateBackstabChoice() {
		if (this.input.up() || this.input.down()) {
			this.backstabCur = 1 - this.backstabCur;
			this.audio.ui();
		}
		if (this.input.cancel()) {
			this.mode = "world";
			this.pendingBackstab = null;
			this.audio.ui();
			return;
		}
		if (this.input.confirm()) {
			const pb = this.pendingBackstab;
			this.mode = "world";
			this.pendingBackstab = null;
			if (!pb) return;
			this.audio.ok();
			if (this.backstabCur === 0) {
				// pb.npc is null for a forest soldier target (they aren't
				// in the NPCS/script table runNpc() expects) -- Approach
				// just re-runs the same "spotted" confrontation interact()
				// would've triggered directly.
				if (pb.npc) this.runNpc(pb.npc);
				else if (pb.after === "soldier") {
					this.pendingSoldier = pb.pending;
					if (this.devWinAllMode) this.triggerDevWinAllFight("soldier");
					else this.say(TALK.soldierSpot, "soldier");
				}
			}
			else this.resolveBackstab(pb);
		}
	}
	/** Same "execute" resolution resolveMercy() reaches after a real
	 *  battle win (permanent delete, loot, scream/red fade), but -25
	 *  reputation instead of -10 since it's an unprovoked kill, not a
	 *  post-fight choice. */
	resolveBackstab(pb) {
		const levels = pb.levels || 1;
		this.adjustReputation(-25);
		const gain = levels * 10;
		this.marks += gain;
		const a = this.randomMercyItem();
		const b = this.randomMercyItem();
		this.bag[a] = (this.bag[a] ?? 0) + 1;
		this.bag[b] = (this.bag[b] ?? 0) + 1;
		const after = pb.after || "wsoldier";
		const pending = pb.pending || "";
		if (after === "calder") this.markExecuted("calder", null);
		else if (after === "soldier") {
			// Forest patrol/scout/sentry live in their own this.soldiers
			// array and share id-space with unrelated wsoldier trainers
			// ("sentry" is also the Cliffs wsoldier's pending id) --
			// resolve sol.beaten directly here and skip the shared
			// TRAINERS[pending]/applyWsBeatFlags() lookups below
			// entirely, since those are keyed by that same string for a
			// different NPC.
			const sol = this.soldiers.find((s) => s.id === pending);
			if (sol) sol.beaten = true;
			this.markExecuted("soldier", pending || this.pendingSoldier);
		}
		else if (after === "cathleen") {
			this.beatCathleen = true;
			this.cathleenCaught = true;
		} else if (after === "shinigami") this.beatShinigami = true;
		else if (after === "mason" || after === "mason2") this.foughtMason = true;
		else this.markExecuted("wsoldier", pending);
		if (after !== "soldier") {
			const kit = TRAINERS[pending] || (after === "calder" ? TRAINERS.calder : undefined);
			if (kit?.grant) {
				for (const [iid, qty] of kit.grant) {
					this.bag[iid] = (this.bag[iid] ?? 0) + qty;
				}
			}
			if (after === "calder") this.beatCalder = true;
			else if (after === "wsoldier") this.applyWsBeatFlags(pending);
			if (pb.npc?.id && this.roamers[pb.npc.id]) this.roamers[pb.npc.id].chase = false;
		}

		this.world.encounterLock = 3;
		this.audio.scream();
		this.startFade("execute");
		this.say(TALK.backstabExecute || [{ speaker: "none", text: "The blade is quick. They never see it coming." }]);
		this.note(`Took ${gain} marks and loot.`);
	}
	applyWsBeatFlags(who: string) {
		if (who === "sentry") this.beatSentry = true;
		else if (who === "conscript") this.beatConscript = true;
		else if (who === "enforcer") this.beatEnforcer = true;
		else if (who === "cross") this.beatCross = true;
		else if (who === "forestRanger") this.beatForestRanger = true;
		else if (who === "forestScout") this.beatForestScout = true;
		else if (who === "ruinsKeeper") this.beatRuinsKeeper = true;
		else if (who === "ruinsWarden") this.beatRuinsWarden = true;
		else if (who === "marshBog") this.beatMarshBog = true;
		else if (who === "marshReed") this.beatMarshReed = true;
		else if (who === "quartz") this.badgeQuartz = true;
		else if (who === "opal") this.badgeOpal = true;
		else if (who === "quarryDriller") this.beatQuarryDriller = true;
		else if (who === "commanderFinal") this.beatCommander = true;
		else if (who === "lieutenantLead") this.beatLieutenantLead = true;
	}
	drawBackstabChoice() {
		this.drawWorld();
		this.ctx.fillStyle = "rgba(18,17,14,0.55)";
		this.ctx.fillRect(0, 0, VIEW_W, VIEW_H);
		this.box(X(16), Y(16), X(208), Y(80));
		this.text("BOWIE KNIFE", X(120), Y(22), "#c5cec6", FONT, "center");
		this.text("They haven't seen you.", X(28), Y(38), "#8a8678", FONT);
		const rows = ["Approach", "Backstab"];
		rows.forEach((row, i) => {
			const on = i === this.backstabCur;
			this.text(on ? `> ${row}` : `  ${row}`, X(28), Y(56 + i * 14), on ? "#e8e4d8" : "#8a8678", FONT);
		});
		this.text("Z choose  X cancel", X(28), Y(88), "#5a7a52", FONT);
	}

	updateChoice() {
		if (this.input.up() || this.input.down()) {
			this.choiceCur = 1 - this.choiceCur;
			this.audio.ui();
		}
		if (this.input.confirm()) {
			this.audio.ok();
			this.mode = "world";
			this.choseHeavenfall = this.choiceCur === 1;
			if (this.choiceCur === 0) {
				this.revivedFather = true;
				this.adjustReputation(LOGIC.reputation?.fatherRevive ?? 25);
				this.seedFatherParty();
				this.warpTo("house", "P", "up");
				this.say(TALK.choiceFather, "ending");
			} else {
				this.say(TALK.choiceHeavenfall, "ending");
			}
		}
	}

	/** Swap Max <-> Father party in place so existing this.party battle code keeps working. */
	swapParties() {
		if (!this.revivedFather) {
			this.note("Father is not with you.");
			return;
		}
		const tmp = this.party;
		this.party = this.party2;
		this.party2 = tmp;
		const ti = this.partyIndex;
		this.partyIndex = this.party2Index;
		this.party2Index = ti;
		this.activeParty = this.activeParty ? 0 : 1;
		const who = this.activeParty === 1 ? "Father" : "Max";
		this.note(`${who}'s party takes the field.`);
		this.audio.ui();
	}
	seedFatherParty() {
		if (this.party2.length > 0) return;
		// Independent starter set for Father (does not touch Max's party).
		this.party2 = [
			mintMonster("mossback", 8),
			mintMonster("quillpup", 7),
		];
		for (const m of this.party2) this.markCaught(m.species);
	}

	beginHeavenfallGameOver() {
		this.say(TALK.heavenfallDevour || [
			{ speaker: "system", text: "Heavenfall descends. There is no path home from this." },
		], "hfGameOver");
	}
	runHeavenfallGameOverFx() {
		try { this.audio.scream(); } catch {}
		this.startFade("hfGameOver");
	}
	reloadLastSaveOrTitle() {
		const buf = typeof readSaveBlob === "function" ? readSaveBlob() : null;
		const snap = buf ? unpackSave(buf) : null;
		if (snap && this.applySave(snap)) {
			this.mode = "world";
			this.note("Loaded last save.");
			return;
		}
		this.reset();
		this.mode = "title";
	}

	applyHeavenfallReviveRep() {
		if (!this.beatHeavenfall) return;
		// 2.8: apply once when Heavenfall is first beaten/caught at the grave.
		// Merchant warning uses heavenfallRepWarned separately.
		const already = (this as { _hfRepApplied?: boolean })._hfRepApplied;
		if (already) return;
		(this as { _hfRepApplied?: boolean })._hfRepApplied = true;
		const delta =
			(LOGIC as { reputation?: { heavenfallRevive?: number } }).reputation?.heavenfallRevive ?? -25;
		this.adjustReputation(delta);
	}
	playerDisplayName() {
		if (this.titleSlayer) return "Heaven Slayer";
		if (this.titleTamer) return "Heaven Tamer";
		if (this.titleTamer) return "Heaven Tamer";
		if (this.titleSlayer) return "Heaven Slayer";
		if (this.revivedFather) return LOGIC.reputation?.kindName || "Max The Kind";
		return SPEAKER_NAME.max || "Max";
	}
	adjustReputation(delta) {
		const min = LOGIC.reputation?.min ?? -100;
		const max = LOGIC.reputation?.max ?? 100;
		this.reputation = Math.max(min, Math.min(max, this.reputation + delta));
	}
	draw() {
		const ctx = this.ctx;
		ctx.save();
		ctx.imageSmoothingEnabled = false;
		ctx.webkitImageSmoothingEnabled = false;
		if (this.shake > 0) ctx.translate((Math.random() - .5) * 6 * this.shake, (Math.random() - .5) * 4 * this.shake);
		if (this.mode === "title") this.drawTitle();
		else if (this.mode === "intro") this.drawStory(INTRO[this.introI] ?? "", "The leaving");
		else if (this.mode === "ending") this.drawStory(this.endingText()[this.endI] ?? "", "The war");
		else if (this.mode === "battle") this.drawBattle();
		else if (this.mode === "bag") this.drawBag();
		else if (this.mode === "party") this.drawParty();
		else if (this.mode === "shop") this.drawShop();
		else if (this.mode === "choice") this.drawChoice();
		else if (this.mode === "mercy") this.drawMercy();
		else if (this.mode === "backstab") this.drawBackstabChoice();
		else if (this.mode === "pause") this.drawPause();
		else if (this.mode === "crydex") this.drawCryDex();
		else if (this.mode === "townmap") this.drawTownMap();
		else if (this.mode === "settings") this.drawSettings();
		else this.drawWorld();
		this.drawFade();
		ctx.restore();
	}
	drawFade() {
		const a = fadeAlpha(this.fade.phase, this.fade.t);
		if (a <= 0) return;
		this.ctx.save();
		this.ctx.globalAlpha = a;
		this.ctx.fillStyle = this.fade.action === "execute" || this.fade.action === "hfGameOver" ? "#8b1010" : "#000";
		this.ctx.fillRect(0, 0, VIEW_W, VIEW_H);
		this.ctx.restore();
	}
	fill(c) {
		this.ctx.fillStyle = c;
		this.ctx.fillRect(0, 0, VIEW_W, VIEW_H);
	}
	text(s, x, y, color, size = FONT, align = "left") {
		const ctx = this.ctx;
		ctx.fillStyle = color;
		ctx.font = `${size}px Silkscreen, ui-monospace, monospace`;
		ctx.textAlign = align;
		ctx.textBaseline = "top";
		ctx.fillText(s, x, y);
	}
	wrap(s, max) {
		const words = s.split(" ");
		const lines = [];
		let cur = "";
		for (const w of words) {
			const n = cur ? `${cur} ${w}` : w;
			if (n.length > max) {
				if (cur) lines.push(cur);
				cur = w;
			} else cur = n;
		}
		if (cur) lines.push(cur);
		return lines;
	}
	box(x, y, w, h) {
		const ctx = this.ctx;
		ctx.fillStyle = "#12110e";
		ctx.fillRect(x, y, w, h);
		ctx.strokeStyle = "#c5cec6";
		ctx.lineWidth = 2;
		ctx.strokeRect(x + 1, y + 1, w - 2, h - 2);
		ctx.strokeStyle = "#3d3a34";
		ctx.lineWidth = 1;
		ctx.strokeRect(x + 3, y + 3, w - 6, h - 6);
	}
	drawMap(map, camx, camy) {
		const mw = (map[0]?.length ?? 1) * TILE;
		const mh = map.length * TILE;
		this.fill(map === HOUSE ? "#1a1410" : map === FOREST ? "#121810" : map === GROVE ? "#161218" : map === CAMP ? "#241810" : map === CLIFFS ? "#2a2418" : map === RUINS ? "#1a1814" : "#1c2418");
		const x0 = Math.max(0, Math.floor(camx / TILE) - 1);
		const y0 = Math.max(0, Math.floor(camy / TILE) - 1);
		const x1 = Math.min(mw / TILE, Math.ceil((camx + VIEW_W) / TILE) + 1);
		const y1 = Math.min(mh / TILE, Math.ceil((camy + VIEW_H) / TILE) + 1);
		for (let y = y0; y < y1; y++) {
			const row = map[y];
			if (!row) continue;
			for (let x = x0; x < x1; x++) {
				const ch = row[x];
				if (!ch) continue;
				this.paintTile(ch, x * TILE - camx, y * TILE - camy);
			}
		}
	}
	drawTitle() {
		this.drawMap(VELD, 8 * TILE, 0);
		this.ctx.fillStyle = "rgba(18,17,14,0.28)";
		this.ctx.fillRect(0, 0, VIEW_W, VIEW_H);
		this.drawSprite("max-down-1", X(28), Y(62), SPR_W, SPR_H);
		this.drawSprite("quillpup-1", X(168), Y(48), X(96), Y(96), false);
		this.box(X(48), Y(28), X(144), Y(28));
		this.text("CRYMON", X(120), Y(32), "#e8e4d8", 48, "center");
		this.box(X(64), Y(100), X(112), Y(36));
		const cont = this.hasSave ? "#e8e4d8" : "#5a584e";
		this.text(this.titleCursor === 0 ? "> Continue" : "Continue", X(120), Y(104), this.titleCursor === 0 ? "#5a7a52" : cont, FONT, "center");
		this.text(this.titleCursor === 1 ? "> New game" : "New game", X(120), Y(118), this.titleCursor === 1 ? "#5a7a52" : "#c5cec6", FONT, "center");
		this.box(X(40), Y(140), X(160), Y(16));
		this.text("Z / A  confirm", X(120), Y(142), "#5a7a52", FONT, "center");
	}
	drawPause() {
		this.drawWorld();
		this.box(X(64), Y(28), X(112), Y(100));
		this.text("PAUSE", X(120), Y(34), "#e8e4d8", FONT, "center");
		const rows = ["Party", "Bag", "CryDex", "Map", "Settings", "Save", "Close"];
		rows.forEach((r, i) => {
			const on = i === this.pauseCursor;
			this.text(on ? `> ${r}` : r, X(120), Y(48 + i * 11), on ? "#5a7a52" : "#c5cec6", FONT, "center");
		});
	}
	drawCryDex() {
		this.drawWorld();
		this.ctx.fillStyle = "rgba(18,17,14,0.55)";
		this.ctx.fillRect(0, 0, VIEW_W, VIEW_H);
		this.box(X(8), Y(6), X(224), Y(148));
		const ids = SAVE_SPECIES;
		let caughtN = 0;
		let seenN = 0;
		for (const id of ids) {
			const bit = this.dexBit(id);
			if (this.dexCaught & bit) caughtN++;
			if (this.dexSeen & bit) seenN++;
		}
		this.text(`CRYDEX  ${caughtN}/${ids.length} caught  ${seenN} seen`, X(16), Y(10), "#c5cec6", FONT);
		if (this.dexView === "entry") {
			const cur = ids[this.dexCursor];
			const s = SPECIES[cur];
			const nat = natureOf(speciesNature(cur));
			const match = natureMatchNames(nat.id);
			this.drawMonIcon({ species: cur, shiny: false, name: s.name }, X(16), Y(28), X(72), Y(88));
			this.text(s.name.toUpperCase(), X(96), Y(28), "#e8e4d8", FONT);
			this.text(`${nat.name} crystal`, X(96), Y(42), "#c5cec6", FONT);
			this.text("Weak to", X(96), Y(58), "#8f4a40", FONT);
			this.text(match.weakTo.join(", ") || "none", X(96), Y(70), "#e8e4d8", FONT);
			this.text("Resists", X(96), Y(86), "#5a7a52", FONT);
			this.text(match.resists.join(", ") || "none", X(96), Y(98), "#e8e4d8", FONT);
			this.wrap(s.blurb, 38).slice(0, 2).forEach((ln, i) => this.text(ln, X(16), Y(122 + i * 12), "#8a8678", FONT));
			this.text("Z / X  back", X(16), Y(148), "#5a7a52", FONT);
			return;
		}
		const vis = 8;
		const start = Math.max(0, Math.min(this.dexCursor - 4, Math.max(0, ids.length - vis)));
		for (let i = 0; i < vis; i++) {
			const idx = start + i;
			if (idx >= ids.length) break;
			const id = ids[idx];
			const bit = this.dexBit(id);
			const on = idx === this.dexCursor;
			const caught = !!(this.dexCaught & bit);
			const seen = !!(this.dexSeen & bit);
			const s = SPECIES[id];
			const y = Y(24 + i * 12);
			if (on) {
				this.ctx.fillStyle = "rgba(143,74,64,0.28)";
				this.ctx.fillRect(X(14), y - 2, X(204), Y(12));
			}
			let label = "?????";
			let color = "#5a584e";
			if (caught) {
				const nat = natureOf(speciesNature(id)).name;
				label = `${s.name}  ${nat}`;
				color = on ? "#e8e4d8" : "#c5cec6";
			} else if (seen) {
				label = `${s.name}  seen`;
				color = on ? "#e8e4d8" : "#8a8678";
			}
			this.text(`${on ? ">" : " "}${String(idx + 1).padStart(2, "0")}  ${label}`, X(16), y, color, FONT);
		}
		const cur = ids[this.dexCursor];
		const bit = this.dexBit(cur);
		const s = SPECIES[cur];
		if (this.dexCaught & bit) this.text(s.blurb.slice(0, 42), X(16), Y(140), "#8a8678", FONT);
		else if (this.dexSeen & bit) this.text("Seen in the field. Not yet yours.", X(16), Y(140), "#8a8678", FONT);
		else this.text("An unknown CryMon.", X(16), Y(140), "#5a584e", FONT);
		this.text(this.dexCaught & bit ? "Z  matchup   X  back" : "Z / X  back", X(16), Y(148), "#5a7a52", FONT);
	}
	drawStory(body, tag) {
		if (tag === "The leaving") {
			this.drawMap(HOUSE, 0, 0);
			const bed = spawnOf(HOUSE, "B");
			const mine = spawnOf(HOUSE, "U");
			const shelf = spawnOf(HOUSE, "S");
			const crate = spawnOf(HOUSE, "C");
			this.drawSprite("prop-bed-empty", bed.x - 32, bed.y - 44, 64, 56);
			this.drawSprite("prop-bed-empty", mine.x - 32, mine.y - 44, 64, 56);
			this.drawSprite("prop-shelf", shelf.x - 20, shelf.y - 32, 40, 44);
			this.drawSprite("prop-crate", crate.x - 16, crate.y - 20, 32, 32);
			this.drawSprite("max-down-1", X(80), Y(72), SPR_W, SPR_H);
		} else {
			this.drawMap(VELD, 14 * TILE, 12 * TILE);
			this.drawSprite("calder-1", X(160), Y(28), SPR_W, SPR_H);
			this.drawSprite("max-down-1", X(40), Y(72), SPR_W, SPR_H);
		}
		this.ctx.fillStyle = "rgba(18,17,14,0.2)";
		this.ctx.fillRect(0, 0, VIEW_W, VIEW_H);
		this.text(tag.toUpperCase(), X(12), Y(6), "#c5cec6", FONT);
		this.box(X(8), Y(112), X(224), Y(42));
		this.wrap(body, 42).slice(0, 3).forEach((ln, i) => this.text(ln, X(14), Y(118 + i * 10), "#e8e4d8", FONT));
	}
	cam() {
		// Unclamped: always centers exactly on the player, even past a map
		// edge (drawMap()'s tile loop already skips anything outside the
		// grid, so this just reveals plain background there). Clamping to
		// the map bounds used to push small/near-edge maps like veld's
		// upper rows up under the fixed HUD box (drawWorldHud() is ~40px
		// tall at the screen's top-left) whenever the player was anywhere
		// in the map's top VIEW_H/2 (240px) -- the door/roof near row1
		// rendered right behind it. Free camera panning keeps the player
		// centered instead, so nothing near an edge sits under the HUD.
		return {
			cx: this.world.x - VIEW_W / 2,
			cy: this.world.y - VIEW_H / 2
		};
	}
	paintTile(ch, dx, dy) {
		const ctx = this.ctx;
		const t = TILE;
		const fill = (c, x = dx, y = dy, w = t, h = t) => {
			ctx.fillStyle = c;
			ctx.fillRect(x, y, w, h);
		};
		if (ch === "H") {
			fill("#2a1e16");
			fill("#3d2c22", dx, dy, t, 1);
			fill("#1a120c", dx, dy + t - 1, t, 1);
			fill("#4a382c", dx + 2, dy + 3, 5, 3);
			fill("#4a382c", dx + 9, dy + 9, 5, 3);
			return;
		}
		if (ch === "R" || ch === "r") {
			// Terracotta shingles. R = ridge cap on Max's house; r = eaves.
			const ridge = ch === "R";
			fill(ridge ? "#a34a32" : "#8a3018");
			const rowH = 6;
			for (let i = 0; i < t; i += rowH) {
				const even = ((i / rowH) | 0) % 2 === 0;
				fill(even ? "#b45438" : "#8a3824", dx, dy + i, t, rowH);
				fill("#5a1c12", dx, dy + i + rowH - 1, t, 1);
				const off = even ? 3 : 8;
				for (let sx = off; sx < t; sx += 10) {
					fill("#5a1c12", dx + sx, dy + i, 1, rowH - 1);
				}
			}
			if (ridge) {
				fill("#d48858", dx, dy, t, 3);
				fill("#6a2418", dx, dy + 3, t, 1);
				fill("#e8a878", dx + 14, dy, 4, 2);
			} else {
				fill("#c46840", dx, dy, t, 2);
				fill("#3a140c", dx, dy + t - 3, t, 3);
			}
			return;
		}
		if (ch === "%" || ch === "g" || (ch === "k" && !this.cageOpen)) {
			fill("#3a3428");
			fill("#12100c", dx + 2, dy, 5, t);
			fill("#1c1814", dx + 13, dy, 5, t);
			fill("#0e0c0a", dx + 24, dy, 5, t);
			fill("#6a6050", dx + 3, dy + 5, 3, 3);
			fill("#6a6050", dx + 14, dy + 16, 3, 3);
			if (ch === "g") {
				fill("#1a1814", dx, dy + 4, t, 4);
				fill("#1a1814", dx, dy + 20, t, 4);
			}
			if (ch === "k") {
				fill("#8a7348", dx + 8, dy + 10, 16, 14);
				fill("#2a1c14", dx + 14, dy + 15, 5, 5);
			}
			return;
		}
		if (ch === "F" && this.world.mapId !== "house") {
			fill("#6b5a3a");
			fill("#8a7348", dx + 2, dy + 4, 1, 1);
			fill("#4a3a28", dx + 9, dy + 11, 1, 1);
			fill("#8a7348", dx + 13, dy + 6, 1, 1);
			return;
		}
		if (ch === "F" || ch === "P") {
			fill("#6a5238");
			fill("#4a3a28", dx, dy + 5, t, 1);
			fill("#4a3a28", dx, dy + 12, t, 1);
			fill("#7a6248", dx + 3, dy + 2, 1, 1);
			fill("#7a6248", dx + 11, dy + 8, 1, 1);
			return;
		}
		if (ch === "D") {
			fill("#1a120c");
			fill("#2a1c14", dx + 1, dy, 14, t);
			fill("#0e0a08", dx + 4, dy + 2, 8, 13);
			return;
		}
		if (ch === "B" || ch === "U") {
			fill("#6a5238");
			fill("#4a3a28", dx, dy + 5, t, 1);
			return;
		}
		if (ch === "C") {
			fill("#6a5238");
			fill("#4a3a28", dx, dy + 12, t, 1);
			return;
		}
		// S = Lieutenant Lead mark on CryTown north path — dirt, not crate/stump
		if (ch === "S") {
			fill("#6b5a3a");
			fill("#8a7348", dx + 2, dy + 4, 1, 1);
			fill("#4a3a28", dx + 9, dy + 11, 1, 1);
			return;
		}
		if (ch === ".") {
			fill("#3d5a38");
			fill("#4a6b42", dx + 2, dy + 4, 1, 1);
			fill("#2f4a2c", dx + 9, dy + 11, 1, 1);
			fill("#5a7a52", dx + 13, dy + 6, 1, 1);
			return;
		}
		if (ch === "T") {
			fill("#2f4a2c");
			fill("#6a8a3a", dx + 3, dy + 2, 2, 12);
			fill("#5a7a52", dx + 8, dy + 1, 2, 13);
			fill("#6a8a3a", dx + 12, dy + 3, 2, 10);
			return;
		}
		if (ch === "=" || ch === "," || ch === "Z" || ch === "Y" || ch === "3" || ch === "c" || ch === "k" || ch === "O" || ch === "8" || ch === "9") {
			fill(ch === "," ? "#5a4a32" : "#6b5a3a");
			fill("#8a7348", dx + 2, dy + 4, 1, 1);
			fill("#4a3a28", dx + 9, dy + 11, 1, 1);
			fill("#8a7348", dx + 13, dy + 6, 1, 1);
			return;
		}
		if (ch === "#") {
			fill("#1c2418");
			fill("#2a3824", dx + 5, dy + 9, 6, 7);
			fill("#3d5a38", dx + 2, dy + 1, 12, 10);
			fill("#2f4a2c", dx + 5, dy + 4, 6, 5);
			return;
		}
		if (ch === "W") {
			fill("#2a3a44");
			fill("#3a5460", dx, dy + 5, t, 2);
			fill("#4a6470", dx, dy + 11, t, 1);
			return;
		}
		if (ch === "^") {
			fill("#4a4030");
			fill("#2a2418", dx, dy + 8, t, 8);
			fill("#6a6050", dx + 3, dy + 4, 10, 4);
			return;
		}
		if (ch === "N") {
			// tent footprint (camp)
			fill("#3d5a38");
			fill("#8a7348", dx + 2, dy + 7, 12, 9);
			fill("#6a4030", dx + 1, dy + 2, 14, 6);
			fill("#3a2c22", dx + 7, dy, 2, 4);
			return;
		}
		// E = Calder mark — grass only (was shared with tent and looked like a stump/acorn)
		if (ch === "E") {
			fill("#3d5a38");
			fill("#4a6b42", dx + 2, dy + 4, 1, 1);
			fill("#2f4a2c", dx + 9, dy + 11, 1, 1);
			return;
		}
		if (ch === "K" || ch === "V" || ch === "A" || ch === "Q" || ch === "M" || ch === "G" || ch === "L" || ch === "J" || ch === "1" || ch === "2") {
			fill("#3d5a38");
			fill("#4a6b42", dx + 2, dy + 4, 1, 1);
			return;
		}
		if (ch === "*") {
			fill("#3d5a38");
			fill("#8f4a40", dx + 4, dy + 5, 2, 2);
			fill("#c5cec6", dx + 10, dy + 9, 2, 2);
			fill("#5a7a52", dx + 7, dy + 3, 1, 1);
			return;
		}
		// X's default rendering below is a crate/chest-shaped blob -- fine
		// everywhere else it's used (veld's cart, cliffs' chest), since a
		// prop sprite always draws on top of it there. Marsh uses X as a
		// plain warp tile to Quarry with no prop drawn over it, so that
		// blob was left sitting bare in the middle of the path. Same
		// plain path-tile look every other warp character (O, =, etc.)
		// already gets.
		if (ch === "X" && this.world.mapId === "marsh") {
			fill("#6b5a3a");
			fill("#8a7348", dx + 2, dy + 4, 1, 1);
			fill("#4a3a28", dx + 9, dy + 11, 1, 1);
			fill("#8a7348", dx + 13, dy + 6, 1, 1);
			return;
		}
		if (ch === "X") {
			fill("#3d5a38");
			fill("#6a4030", dx + 2, dy + 6, 12, 8);
			fill("#4a2a20", dx + 1, dy + 10, 3, 5);
			fill("#8a7348", dx + 11, dy + 4, 4, 4);
			return;
		}
		fill("#3d5a38");
	}
	drawSprite(key, x, y, w, h, feet = true, pixel = false) {
		const im = this.images[key];
		const ctx = this.ctx;
		ctx.imageSmoothingEnabled = false;
		ctx.imageSmoothingQuality = "low";
		if (!im || !im.width) {
			// Never flash a white plate — leave transparent until the asset arrives.
			return;
		}
		let dw = w;
		let dh = h;
		if (pixel) {
			const fit = Math.min(w / im.width, h / im.height);
			let s = Math.max(1, Math.round(fit) || 1);
			if (s < 2 && im.height * 2 <= h + 24) s = 2;
			dw = im.width * s;
			dh = im.height * s;
		} else {
			const ar = im.width / im.height;
			if (w / h > ar) dw = h * ar;
			else dh = w / ar;
		}
		const dx = x + (w - dw) / 2;
		let dy;
		if (feet === "top") dy = y;
		else if (feet) dy = y + (h - dh);
		else dy = y + (h - dh) / 2;
		ctx.drawImage(im, dx, dy, dw, dh);
	}
	drawBattleMon(key, x, y, w, h, enterT, faintT, shiny) {
		const ctx = this.ctx;
		const enter = Math.min(1, (enterT ?? 1) / 0.3);
		const faint = faintT > 0 ? Math.max(0, 1 - faintT / 0.4) : 1;
		ctx.save();
		ctx.globalAlpha *= faint;
		if (shiny) ctx.filter = "hue-rotate(38deg) saturate(1.45) brightness(1.12)";
		const visH = Math.max(1, h * enter);
		ctx.beginPath();
		ctx.rect(x, y + h - visH, w, visH);
		ctx.clip();
		this.drawSprite(key, x, y, w, h, false);
		ctx.restore();
		ctx.filter = "none";
	}
	drawActor(key, wx, wy) {
		const { cx, cy } = this.cam();
		const who = String(key).split("-")[0];
		const scale = Number((SPRITES as { drawScale?: Record<string, number> }).drawScale?.[who] ?? 1) || 1;
		const w = SPR_W * scale;
		const h = SPR_H * scale;
		this.drawSprite(key, wx - cx - w / 2, wy - cy - h + 4, w, h);
	}
	drawWorldHud() {
		const lead = this.lead();
		const name = this.playerDisplayName().toUpperCase();
		this.ctx.font = `${FONT}px Silkscreen, ui-monospace, monospace`;
		this.ctx.textAlign = "left";
		const nameW = Math.ceil(this.ctx.measureText(name).width);
		const statsX = Math.max(88, 16 + nameW + 12);
		const boxW = Math.max(340, statsX + 230);
		this.box(8, 8, boxW, 40);
		this.text(name, 16, 12, "#e8e4d8", FONT);
		if (this.revivedFather) {
			const tag = this.activeParty === 1 ? "FATHER" : "MAX";
			this.text(tag, 16 + Math.ceil(this.ctx.measureText(name).width) + 8, 12, this.activeParty === 1 ? "#c5a06a" : "#8a9eb0", FONT);
		}
		this.text(`Xtals ${this.bag.gem}`, statsX, 12, "#c5cec6", FONT);
		this.text(`M ${this.marks}`, statsX + 112, 12, "#8f4a40", FONT);
		{
			const r = this.reputation | 0;
			const repStr = r > 0 ? `Rep +${r}` : r < 0 ? `Rep ${r}` : "Rep 0";
			const repCol = r > 0 ? "#6a9e6a" : r < 0 ? "#c05050" : "#8a8678";
			this.text(repStr, statsX + 168, 12, repCol, FONT);
		}
		this.text(lead ? `${lead.name} Lv${lead.level}  ${lead.hp}/${lead.maxHp}` : "No CryMon yet", 16, 28, "#8a8678", FONT);
		if (this.hasScroll) this.text("SCROLL", statsX + 112, 28, "#c5cec6", FONT);
	}
	drawMapTitle() {
		const name = MAP_NAME[this.world.mapId] ?? this.world.mapId.toUpperCase();
		this.ctx.font = `${FONT}px Silkscreen, ui-monospace, monospace`;
		this.ctx.textAlign = "left";
		const tw = Math.ceil(this.ctx.measureText(name).width);
		const w = tw + 16;
		const x = VIEW_W - 8 - w;
		this.box(x, 8, w, 24);
		this.text(name, x + 8, 12, "#e8e4d8", FONT, "left");
	}
	drawProp(key, wx, wy, w, h) {
		const { cx, cy } = this.cam();
		this.drawSprite(key, wx - cx - w / 2, wy - cy - h + 6, w, h);
	}
	/** No interaction-prompt popup wanted. Kept as a no-op instead of
	 *  removing every drawWorld() call site -- interact()'s own
	 *  proximity checks are separate and unaffected. */
	hintZ(_wx: number, _wy: number, _radius = 52) {}
	drawWorld() {
		const { cx, cy } = this.cam();
		const map = this.map();
		this.fill(this.world.mapId === "house" ? "#1a1410" : this.world.mapId === "forest" ? "#121810" : this.world.mapId === "grove" ? "#161218" : this.world.mapId === "camp" ? "#241810" : this.world.mapId === "cliffs" ? "#2a2418" : this.world.mapId === "ruins" ? "#1a1814" : "#1c2418");
		this.drawMap(map, cx, cy);
		if (this.world.mapId === "house") {
			const bed = spawnOf(HOUSE, "B");
			const mine = spawnOf(HOUSE, "U");
			const shelf = spawnOf(HOUSE, "S");
			const crate = spawnOf(HOUSE, "C");
			this.drawProp("prop-bed-empty", bed.x, bed.y + 8, 64, 56);
			this.drawProp("prop-bed-empty", mine.x, mine.y + 8, 64, 56);
			this.drawProp("prop-shelf", shelf.x, shelf.y + 4, 40, 44);
			if (!this.lootedCrate) this.drawProp("prop-crate", crate.x, crate.y + 4, 32, 32);
			this.text("...", bed.x - cx - 6, bed.y - cy - 20, "#8a8678", FONT);
			this.hintZ(bed.x, bed.y, 36);
			this.hintZ(mine.x, mine.y, 36);
			this.hintZ(shelf.x, shelf.y, 36);
			if (!this.lootedCrate) this.hintZ(crate.x, crate.y, 36);
		}
		if (this.world.mapId === "veld") {
			const door = spawnOf(VELD, "D");
			this.drawProp("prop-door", door.x, door.y + 8, 32, 48);
			const cart = spawnOf(VELD, "X");
			this.drawProp("prop-cart", cart.x, cart.y + 8, 56, 48);
			this.hintZ(cart.x, cart.y);
			const stall = spawnOf(VELD, "J");
			this.drawProp("prop-crate", stall.x - 20, stall.y + 12, 32, 32);
			if (!this.gotHerb) {
				const herb = spawnOf(VELD, "M");
				this.drawProp("prop-herb", herb.x, herb.y + 4, 32, 32);
				this.hintZ(herb.x, herb.y);
			}
			if (!this.gotFieldGem) {
				const gem = spawnOf(VELD, "G");
				this.drawProp("prop-moonstone", gem.x, gem.y + 4, 28, 28);
				this.hintZ(gem.x, gem.y);
			}
		}
		const wf = Math.floor(this.clock * 4) % 4 + 1;
		const flags = this.npcFlags();
		// Depth-sorted actor draw: every character sprite (NPCs, rival, anne,
		// forest soldiers, Cathleen, Max) is queued as a {y, draw} entry
		// instead of drawn immediately, then the whole queue is drawn in
		// ascending world-y order once everything's collected. In this
		// top-down/orthographic view, a physically lower sprite (larger
		// world.y, closer to "camera") is meant to be drawn in front of one
		// that's higher up -- drawing strictly in a fixed list order (as
		// before, with Max always drawn dead last) instead put Max in front
		// of anyone she was standing above, regardless of which was really
		// closer. Props stay outside this queue and keep drawing first
		// (always behind every character), unchanged from before.
		const actorQueue: { y: number; draw: () => void }[] = [];
		// Task 4: draw map NPCs from JSON (NPCS / npc.sprite) instead of a
		// per-map hardcoded drawActor list. Props, rivals, soldiers, and
		// Cathleen's special overworld sprite stay special-cased.
		for (const npc of NPCS) {
			if (npc.map !== this.world.mapId || !npc.sprite) continue;
			if (npc.sprite === "npc/soldier" || String(npc.id || "").startsWith("soldier")) continue;
			if (this.npcHidden(npc, flags)) continue;
			if (this.npcIsExecuted(npc.id)) continue;
			const [poX, poY] = this.npcPassOffset(npc, flags);
			const roamer = this.roamableNpc(npc) ? this.roamers[npc.id] : null;
			for (const mark of this.npcMarks(npc)) {
				const s = roamer ? { x: roamer.x, y: roamer.y } : spawnOf(this.map(), mark);
				s.x += poX;
				s.y += poY;
				const base = String(npc.sprite).includes("/")
					? String(npc.sprite).split("/").pop()!
					: String(npc.sprite);
				const walkers = (SPRITES as { walkers?: Record<string, string> }).walkers || {};
				actorQueue.push({
					y: s.y,
					draw: () => {
						if (base in walkers || npc.sprite === "shinigami") {
							const sf = Math.floor(this.clock * 3) % 4 + 1;
							this.drawActor(`${base}-${roamer?.dir || "down"}-${sf}`, s.x, s.y);
						} else {
							this.drawActor(`${base}-${wf}`, s.x, s.y);
						}
						this.hintZ(s.x, s.y);
					}
				});
			}
		}
		if (this.world.mapId === "veld" && this.rival.phase !== "off") {
			const walking = this.rival.phase === "approach" || this.rival.phase === "leave";
			const rf = walking ? this.rival.frame % 4 + 1 : 1;
			actorQueue.push({
				y: this.rival.y,
				draw: () => {
					this.drawActor(`mason-${this.rival.dir}-${rf}`, this.rival.x, this.rival.y);
					if (this.rival.phase === "done") this.hintZ(this.rival.x, this.rival.y);
				}
			});
		}
		if (this.anne.phase !== "off") {
			const walking = this.anne.phase === "approach" || this.anne.phase === "approach2" || this.anne.phase === "leave";
			const af = walking ? this.anne.frame % 4 + 1 : 1;
			actorQueue.push({ y: this.anne.y, draw: () => this.drawActor(`anne-${this.anne.dir}-${af}`, this.anne.x, this.anne.y) });
		}
		if (this.world.mapId === "forest") {
			this.ensureSoldiers();
			for (const sol of this.soldiers) {
				const sf = sol.beaten ? 1 : sol.frame % 4 + 1;
				actorQueue.push({
					y: sol.y,
					draw: () => {
						this.drawActor(`soldier-${sol.dir}-${sf}`, sol.x, sol.y);
						this.hintZ(sol.x, sol.y);
					}
				});
			}
		}
		if (this.world.mapId === "grove" && !this.cathleenCaught) {
			const c = spawnOf(GROVE, "8");
			actorQueue.push({
				y: c.y,
				draw: () => {
					const { cx, cy } = this.cam();
					this.drawSprite("cathleen-ow", c.x - cx - 36, c.y - cy - 68, 72, 72, true);
					this.hintZ(c.x, c.y);
				}
			});
		}
		if (this.world.mapId === "cliffs" && !this.chestLooted) {
			const chest = spawnOf(CLIFFS, "C");
			this.drawProp("prop-crate", chest.x, chest.y + 4, 32, 32);
			this.hintZ(chest.x, chest.y);
		}
		const frame = this.world.moving ? this.world.frame % 4 + 1 : 1;
		actorQueue.push({ y: this.world.y, draw: () => this.drawActor(`max-${this.world.dir}-${frame}`, this.world.x, this.world.y) });
		actorQueue.sort((a, b) => a.y - b.y);
		for (const entry of actorQueue) entry.draw();
		if (this.talking()) {
			this.drawTalk();
			this.drawMapTitle();
			return;
		}
		this.drawWorldHud();
		this.drawMapTitle();
		if (this.hudT > 0) {
			this.box(X(8), Y(116), X(224), Y(40));
			this.wrap(this.hudFlash, 40).slice(0, 3).forEach((ln, i) => this.text(ln, X(14), Y(122 + i * 10), "#e8e4d8", FONT));
			this.text("Z", X(218), Y(144), "#8a8678", FONT);
		}
	}
	drawTalk() {
		const beat = this.beat();
		if (!beat) return;
		const sp = beat.speaker;
		const showPort = sp && sp !== "none" && sp !== "system";
		if (showPort) {
			this.drawSprite(`port-${sp}`, X(-4), Y(6), X(120), Y(150), "top", true);
			this.ctx.fillStyle = "rgba(18,17,14,0.45)";
			this.ctx.fillRect(X(108), 0, VIEW_W - X(108), VIEW_H);
			this.box(X(112), Y(6), X(122), Y(62));
			const who = sp === "max" ? this.playerDisplayName() : (SPEAKER_NAME[sp] || sp);
			if (who) this.text(String(who).toUpperCase(), X(118), Y(10), "#c5cec6", FONT);
			this.wrap(beat.text, 20).slice(0, 4).forEach((ln, i) => this.text(ln, X(118), Y(22 + i * 10), "#e8e4d8", FONT));
			this.text("Z", X(216), Y(52), "#8a8678", FONT);
		} else {
			this.box(X(8), Y(116), X(224), Y(40));
			this.wrap(beat.text, 40).slice(0, 3).forEach((ln, i) => this.text(ln, X(14), Y(122 + i * 10), "#e8e4d8", FONT));
			this.text("Z", X(218), Y(144), "#8a8678", FONT);
		}
	}
	drawChoice() {
		this.drawWorld();
		this.ctx.fillStyle = "rgba(18,17,14,0.55)";
		this.ctx.fillRect(0, 0, VIEW_W, VIEW_H);
		this.box(X(20), Y(24), X(200), Y(112));
		this.text("THE SCROLL", X(120), Y(32), "#c5cec6", FONT, "center");
		this.text("The scroll can wake one of the dead.", X(32), Y(48), "#8a8678", FONT);
		const rows = ["Resurrect Father", "Resurrect Heavenfall"];
		rows.forEach((row, i) => {
			const on = i === this.choiceCur;
			this.text(on ? `> ${row}` : `  ${row}`, X(32), Y(68 + i * 16), on ? "#e8e4d8" : "#8a8678", FONT);
		});
		this.text(this.choiceCur === 0 ? "He comes back as he was. Human, and hers." : "An ancient CryMon wakes. Vast and unknown.", X(32), Y(108), "#8a8678", FONT);
		this.text("Z  choose", X(32), Y(122), "#5a7a52", FONT);
	}
	drawBag() {
		this.drawWorld();
		this.ctx.fillStyle = "rgba(18,17,14,0.55)";
		this.ctx.fillRect(0, 0, VIEW_W, VIEW_H);
		this.box(X(10), Y(8), X(220), Y(144));
		this.text("BAG", X(18), Y(14), "#c5cec6", FONT);
		this.text(`Marks ${this.marks}`, X(150), Y(14), "#8f4a40", FONT);
		const items = this.ownedItems();
		if (items.length === 0) this.text("The pouch is empty.", X(18), Y(48), "#8a8678", FONT);
		else {
			const shown = 4;
			const start = Math.max(0, Math.min(this.bagCursor, Math.max(0, items.length - shown)));
			for (let i = 0; i < shown; i++) {
				const idx = start + i;
				const id = items[idx];
				if (!id) break;
				const y = Y(46 + i * 18);
				const on = idx === this.bagCursor;
				this.text(on ? ">" : " ", X(18), y, "#e8e4d8", FONT);
				this.drawSprite(`item-${id}`, X(30), y - 2, X(14), X(14), false);
				this.text(`${ITEMS[id].name}  x${this.bag[id]}`, X(48), y, on ? "#e8e4d8" : "#8a8678", FONT);
			}
			const cur = items[this.bagCursor];
			if (cur) {
				this.wrap(ITEMS[cur].desc, 40).slice(0, 1).forEach((ln) => this.text(ln, X(18), Y(124), "#8a8678", FONT));
				this.text(ITEMS[cur].field ? "Z use on a CryMon" : "Battle only", X(18), Y(136), "#5a7a52", FONT);
			}
		}
		if (this.hudT > 0) this.text(this.hudFlash.slice(0, 34), X(18), Y(148), "#e8e4d8", FONT);
	}
	drawMonIcon(m, x, y, w, h) {
		const battle = `${m.species}-1`;
		const port = `port-${m.species}`;
		const key = this.images[battle] ? battle : port;
		const ctx = this.ctx;
		if (m.shiny) ctx.filter = "hue-rotate(38deg) saturate(1.45) brightness(1.12)";
		this.drawSprite(key, x, y, w, h, false);
		ctx.filter = "none";
	}
	drawParty() {
		this.drawWorld();
		this.ctx.fillStyle = "rgba(18,17,14,0.55)";
		this.ctx.fillRect(0, 0, VIEW_W, VIEW_H);
		this.box(X(8), Y(6), X(224), Y(148));
		const title = this.partyView === "target"
			? `USE ${this.pendingItem ? ITEMS[this.pendingItem].name.toUpperCase() : "ITEM"}`
			: this.partyView === "stats" ? "STATS"
			: this.partyView === "moves" ? "MOVES"
			: this.partyView === "release" ? `RELEASE ${this.party[this.partyCursor]?.name.toUpperCase() ?? ""}?`
			: this.partyView === "catchSwap" ? `KEEP ${this.pendingCatch?.name.toUpperCase() ?? "CRYMON"}`
			: "CRYMON";
		this.text(title, X(16), Y(10), "#c5cec6", FONT);
		if (this.partyView === "stats" || this.partyView === "moves") {
			const m = this.party[this.partyCursor] ?? this.lead();
			this.drawMonIcon(m, X(12), Y(24), X(88), Y(110));
			this.text(m.name.toUpperCase(), X(108), Y(28), "#e8e4d8", FONT);
			this.text(`Lv${m.level}  ${natureOf(speciesNature(m.species)).name}`, X(108), Y(40), "#8a8678", FONT);
			if (this.partyView === "stats") {
				this.text(`HP  ${m.hp}/${m.maxHp}`, X(108), Y(56), "#e8e4d8", FONT);
				this.hpBar(X(108), Y(68), X(100), m.hp, m.maxHp);
				this.text(`STR ${m.str}`, X(108), Y(80), "#c5cec6", FONT);
				this.text(`AGL ${m.agl}`, X(108), Y(92), "#c5cec6", FONT);
				this.text(`MAG ${m.spc}`, X(108), Y(104), "#c5cec6", FONT);
				this.text(`XP  ${m.xp}/${m.level * 10}`, X(108), Y(116), "#8a8678", FONT);
				if (m.status && m.status !== "none") this.text(m.status.toUpperCase(), X(190), Y(80), "#8f4a40", FONT);
				this.text("Z / X  back", X(16), Y(148), "#5a7a52", FONT);
			} else {
				const moves = this.partyMoves(m);
				const cur = clamp(this.moveCursor, 0, Math.max(0, moves.length - 1));
				const shown = 3;
				const start = Math.max(0, Math.min(cur, Math.max(0, moves.length - shown)));
				for (let i = 0; i < shown; i++) {
					const idx = start + i;
					const mv = moves[idx];
					if (!mv) break;
					const on = idx === cur;
					const pp = mv.pp ? `  ${mv.pp}` : "";
					this.text(`${on ? ">" : " "}${mv.name}${pp}`, X(108), Y(54 + i * 12), on ? "#e8e4d8" : "#8a8678", FONT);
				}
				const mv = moves[cur];
				if (mv && (mv.kind === "nmove" || mv.kind === "hypeUp")) {
					this.text(mv.effect, X(16), Y(100), "#8f4a40", FONT);
					this.text(`Uses    ${mv.pp}`, X(16), Y(112), "#e8e4d8", FONT);
				} else if (mv) {
					this.text(mv.stat === "str" ? "STRENGTH based" : "MAGIC based", X(16), Y(100), "#c5cec6", FONT);
					this.text(`Damage  ${mv.dmg}`, X(16), Y(112), "#e8e4d8", FONT);
					this.text(`Speed   ${Math.round(mv.speed * 10)}`, X(16), Y(124), "#e8e4d8", FONT);
					this.text(`Power   ${Math.round(mv.power * 10)}`, X(108), Y(112), "#8a8678", FONT);
				}
				this.text("UP/DOWN  inspect", X(16), Y(138), "#5a7a52", FONT);
				this.text("Z / X  back", X(16), Y(148), "#5a7a52", FONT);
			}
			return;
		}
		this.party.forEach((m, i) => {
			const y = Y(22 + i * 20);
			const on = i === this.partyCursor;
			if (on) {
				this.ctx.fillStyle = "rgba(143,74,64,0.28)";
				this.ctx.fillRect(X(14), y - 2, X(204), Y(20));
			}
			this.drawMonIcon(m, X(16), y - 2, X(22), Y(18));
			const lead = i === this.partyIndex ? "LEAD" : "";
			this.text(`${on ? ">" : " "}${m.name}  Lv${m.level}  ${m.hp}/${m.maxHp}  ${lead}`, X(42), y, on ? "#e8e4d8" : "#8a8678", FONT);
		});
		if (this.partyView === "act") {
			const acts = [
				"Send out",
				"Stats",
				"Moves",
				"Release"
			];
			this.box(X(148), Y(58), X(82), Y(70));
			acts.forEach((a, i) => {
				this.text(i === this.actCursor ? `> ${a}` : `  ${a}`, X(154), Y(64 + i * 14), i === this.actCursor ? "#e8e4d8" : "#8a8678", FONT);
			});
		} else if (this.partyView === "release") {
			this.text("Z  release forever   X  back", X(16), Y(148), "#8f4a40", FONT);
		} else if (this.partyView === "catchSwap") {
			this.text("Z  release this one   X  let the new one go", X(16), Y(148), "#c5cec6", FONT);
		} else this.text(this.partyView === "target" ? "Z  use   X  bag" : "Z  choose   Left/Right swap party   Start close", X(16), Y(148), "#5a7a52", FONT);
		if (this.hudT > 0) this.text(this.hudFlash.slice(0, 34), X(16), Y(148), "#e8e4d8", FONT);
	}
	drawShop() {
		this.drawWorld();
		this.ctx.fillStyle = "rgba(18,17,14,0.55)";
		this.ctx.fillRect(0, 0, VIEW_W, VIEW_H);
		this.box(X(10), Y(8), X(220), Y(144));
		this.text(SHOP_NAMES[this.shopKeep] ?? "TRADER'S STALL", X(18), Y(14), "#c5cec6", FONT);
		this.text(`Marks ${this.marks}`, X(150), Y(14), "#8f4a40", FONT);
		this.text(this.shopTab === "buy" ? ">BUY   sell" : " buy   >SELL", X(18), Y(28), "#e8e4d8", FONT);
		const rows = this.shopTab === "buy" ? this.shopBuyRows() : this.ownedItems().filter((id) => ITEMS[id].sell > 0);
		if (rows.length === 0) this.text("Nothing to sell.", X(18), Y(48), "#8a8678", FONT);
		else {
			const shown = 6;
			const start = Math.max(0, Math.min(this.shopCursor, Math.max(0, rows.length - shown)));
			for (let i = 0; i < shown; i++) {
				const idx = start + i;
				const id = rows[idx];
				if (!id) break;
				const y = Y(44 + i * 14);
				const on = idx === this.shopCursor;
				const price = this.shopTab === "buy"
					? (this.shopGiftPending() ? "FREE" : `${this.shopBuyPrice(id)}m`)
					: `${this.shopSellPrice(id)}m`;
				// Buy tab: units left on the shelf. Sell tab: how many
				// you own (what you're selling from) -- different numbers.
				const qty = this.shopTab === "buy" ? (this.shopStock[this.shopKeep]?.[id] ?? 0) : this.bag[id];
				this.text(`${on ? ">" : " "}${ITEMS[id].name}  ${price}  x${qty}`, X(18), y, on ? "#e8e4d8" : "#8a8678", FONT);
			}
		}
		this.text("A/D tab   Z trade   X leave", X(18), Y(140), "#5a7a52", FONT);
		if (this.hudT > 0) this.text(this.hudFlash.slice(0, 34), X(18), Y(148), "#e8e4d8", FONT);
	}
	hpBar(x, y, w, hp, max) {
		const ctx = this.ctx;
		ctx.fillStyle = "#2a2620";
		ctx.fillRect(x, y, w, 12);
		const r = max <= 0 ? 0 : hp / max;
		ctx.fillStyle = r > .5 ? "#5a7a52" : "#8f4a40";
		ctx.fillRect(x, y, Math.floor(w * r), 12);
		ctx.strokeStyle = "#c5cec6";
		ctx.strokeRect(x, y, w, 6);
	}
	drawBattle() {
		const b = this.battle;
		if (!b) return;
		const bg = this.images.bg;
		if (bg) this.ctx.drawImage(bg, 0, 0, VIEW_W, VIEW_H);
		else this.fill("#2a2418");
		const pf = Math.floor(b.t * 4) % 4 + 1;
		this.drawBattleMon(`${b.foe.species}-${pf}`, X(168), Y(8), X(52), Y(52), b.foeEnterT, b.foeFaintT, b.foe.shiny);
		this.drawBattleMon(`${b.player.species}-${pf}`, X(12), Y(52), X(48), Y(48), b.enterT, b.faintT, b.player.shiny);
		this.box(X(6), Y(6), X(124), Y(32));
		this.text(`${b.foe.shiny ? "*" : ""}${b.foe.name.toUpperCase()}`, X(10), Y(9), b.foe.shiny ? "#d4c06a" : "#e8e4d8", FONT);
		this.hpBar(X(10), Y(22), X(96), b.foe.hp, b.foe.maxHp);
		this.text(`${b.foe.hp}`, X(110), Y(20), "#8a8678", FONT);
		if (b.foe.status && b.foe.status !== "none") this.text(b.foe.status.slice(0, 3).toUpperCase(), X(10), Y(28), "#8f4a40", FONT);
		this.box(X(108), Y(78), X(126), Y(28));
		this.text(`${b.player.shiny ? "*" : ""}${b.player.name.toUpperCase()} Lv${b.player.level}`, X(112), Y(80), b.player.shiny ? "#d4c06a" : "#e8e4d8", FONT);
		this.hpBar(X(112), Y(92), X(96), b.player.hp, b.player.maxHp);
		this.text(`${b.player.hp}`, X(212), Y(90), "#8a8678", FONT);
		if (b.player.status && b.player.status !== "none") this.text(b.player.status.slice(0, 3).toUpperCase(), X(112), Y(100), "#8f4a40", FONT);
		if (b.phase === "msg") {
			this.box(X(6), Y(110), X(228), Y(46));
			const line = b.msg[b.msgI] ?? "";
			this.wrap(line, 42).forEach((ln, i) => this.text(ln, X(12), Y(116 + i * 10), "#e8e4d8", FONT));
			return;
		}
		if (b.phase === "minigame") {
			this.box(X(16), Y(110), X(208), Y(44));
			this.text("SPECIAL  hit the mark", X(24), Y(114), "#c5cec6", FONT);
			const bx = X(24), by = Y(132), bw = X(192), bh = Y(10);
			const mg = COMBAT.minigame;
			const c0 = (mg?.connectedMin ?? 30) / 100;
			const c1 = (mg?.connectedMax ?? 70) / 100;
			const p0 = (mg?.perfectMin ?? 45) / 100;
			const p1 = (mg?.perfectMax ?? 55) / 100;
			this.ctx.fillStyle = "#8b3030";
			this.ctx.fillRect(bx, by, bw, bh);
			this.ctx.fillStyle = "#c9a227";
			this.ctx.fillRect(bx + c0 * bw, by, (c1 - c0) * bw, bh);
			this.ctx.fillStyle = "#4a9a4a";
			this.ctx.fillRect(bx + p0 * bw, by, (p1 - p0) * bw, bh);
			this.ctx.fillStyle = "#e8e4d8";
			this.ctx.fillRect(bx + b.minigame / 100 * bw - 2, Y(128), 6, Y(18));
			return;		}
		this.box(X(6), Y(110), X(228), Y(46));
		const title = b.phase === "item" ? "ITEMS" : b.phase === "attack" ? "ATTACK" : "GUARD";
		this.text(title, X(12), Y(114), "#8a8678", FONT);
		const shown = 3;
		const start = Math.max(0, Math.min(b.cursor, Math.max(0, b.menu.length - shown)));
		for (let i = 0; i < shown; i++) {
			const idx = start + i;
			const row = b.menu[idx];
			if (!row) break;
			const active = idx === b.cursor;
			this.text(active ? `> ${row}` : `  ${row}`, X(70), Y(114 + i * 12), active ? "#e8e4d8" : "#8a8678", FONT);
		}
	}
}