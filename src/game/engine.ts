// @ts-nocheck
import { Chip, MAP_SONG, TITLE_SONG, BATTLE_SONG, TRAINER_SONG, ENDING_SONG } from "./audio";
import { packSave, unpackSave, writeSaveBlob, readSaveBlob, saveExists, SAVE_FLAGS, SAVE_SPECIES } from "./save";
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
  PARTY_MAX,
  REACH,
  RUINS,
  SPECIES,
  SPEAKER_NAME,
  START_BAG,
  START_MARKS,
  TALK,
  TILE,
  VELD,
  VIEW_H,
  VIEW_W,
  captureChance,
  doorTile,
  grantPartyXp,
  healAmount,
  mintMonster,
  natureOf,
  rollShiny,
  solidTile,
  spawnOf,
  ENDING_WIN,
  MAP_NAME,
  ENCOUNTERS,
  WARPS,
  TRAINERS,
  NPCS,
  artManifest,
  itemEffect,
} from "./data";
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
  RivalState,
  ShopTab,
  Soldier,
  SpeciesId,
  TalkBeat,
  TrainerId,
  WorldState,
} from "./types";

type ImgMap = Record<string, HTMLImageElement>;
type TalkAfter = null | "shop" | "orenShop" | "mason" | "mason2" | "calder" | "soldier" | "cathleen" | "shinigami" | "anneLeave" | "masonLeave" | "choice" | "wsoldier" | "ending" | "bedHeal";

const STEP = 1 / 60;
function loadImg(src, ms = 8000) {
	return new Promise((res, rej) => {
		const im = new Image();
		im.crossOrigin = "anonymous";
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
	soldiers: Soldier[] = [];
	pendingSoldier: string | null = null;
	battlesDone = 0;
	anneGifted = false;
	cathleenCaught = false;
	beatCathleen = false;
	beatShinigami = false;
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
	cageOpen = false;
	mason2Map: string | null = null;
	mason2Done = false;
	masonRematch = false;
	talkedReach = false;
	dexSeen = 0;
	dexCaught = 0;
	dexCursor = 0;
	fade = { phase: "off" as "off" | "out" | "hold" | "in", t: 0, action: null as null | "bed" | "loss" };
	pendingWs = null;
	choiceCur = 0;
	shopKeep = "bram";
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
		this.ready = true;
		this.visHook = () => {
			if (document.hidden) this.persist(false);
			else this.audio.unlock();
		};
		document.addEventListener("visibilitychange", this.visHook);
		// Title draws without sprites. Never stall the cart on 272 portraits.
		void this.loadArt();
	}
	async loadArt() {
		const all = artManifest();
		const prefer = new Set(["max-down-1", "max-down-2", "quillpup-1", "quillpup-2", "bg"]);
		const first = all.filter(([k]) => prefer.has(k));
		const rest = all.filter(([k]) => !prefer.has(k));
		await this.loadArtChunk(first);
		await this.loadArtChunk(rest);
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
		this.mode = "title";
		this.introI = 0;
		this.endI = 0;
		this.party = [];
		this.partyIndex = 0;
		this.bag = { ...START_BAG };
		this.marks = START_MARKS;
		this.talkQ = [];
		this.talkI = 0;
		this.afterTalk = null;
		this.bagCursor = 0;
		this.partyCursor = 0;
		this.partyView = "list";
		this.actCursor = 0;
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
		this.cageOpen = false;
		this.mason2Map = null;
		this.mason2Done = false;
		this.masonRematch = false;
		this.talkedReach = false;
		this.dexSeen = 0;
		this.dexCaught = 0;
		this.dexCursor = 0;
		this.fade = { phase: "off", t: 0, action: null };
		this.pendingWs = null;
		this.choiceCur = 0;
		this.shopKeep = "bram";
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
			bag: { ...this.bag },
			flags,
			party: this.party.map((m) => ({ ...m })),
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
		this.partyIndex = Math.min(snap.partyIndex, Math.max(0, this.party.length - 1));
		this.battlesDone = snap.battlesDone;
		this.mason2Map = snap.mason2Map;
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
	persist(manual = false) {
		if (this.mode === "title" || this.mode === "intro" || this.mode === "battle") {
			if (!manual) return false;
		}
		if (this.mode === "battle") return false;
		const ok = writeSaveBlob(packSave(this.snapshot()));
		if (ok) {
			this.hasSave = true;
			this.lastAutosave = this.clock;
			if (manual) {
				this.note("Saved.");
				this.audio.save();
			}
		} else if (manual) {
			this.note("Save failed.");
			this.audio.miss();
		}
		return ok;
	}
	tryContinue() {
		const snap = unpackSave(readSaveBlob() || new Uint8Array());
		if (!snap) {
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
			this.input.beginFrame();
			this.input.pollGamepad();
			while (this.acc >= STEP) {
				this.update(STEP);
				this.acc -= STEP;
			}
			this.draw();
			this.input.endFrame();
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
			this.world.x = s.x;
			this.world.y = s.y + TILE + 8;
			this.world.dir = "down";
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
			if (next === "shop") this.openShop("bram");
			else if (next === "orenShop") this.openShop("oren");
			else if (next === "mason") {
				this.foughtMason = true;
				this.startBattle(mintMonster("glimmoth", 3), false, "Mason sends Glimmoth", "mason");
			} else if (next === "calder") this.startBattle(mintMonster("razorbat", 4), false, "Calder sends Razorbat", "calder");
			else if (next === "soldier") {
				const sol = this.soldiers.find((s) => s.id === this.pendingSoldier);
				if (sol && !sol.beaten) this.startBattle(mintMonster(sol.species, sol.level), false, `${sol.name} sends ${SPECIES[sol.species].name}`, "soldier", sol.id);
			} else if (next === "cathleen") {
				if (!this.cathleenCaught) this.startBattle(mintMonster("cathleen", 6), true, "Cathleen stands against you", "wild");
			} else if (next === "shinigami") {
				if (!this.beatShinigami) {
					this.startBattle(
						mintMonster("crymare", 5),
						false,
						"Shinigami sends CryMare",
						"shinigami",
						null,
						[mintMonster("crymare", 6), mintMonster("crymare", 7)]
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
					mintMonster(kit.lead[0], kit.lead[1]),
					false,
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
			} else if (next === "ending") {
				this.mode = "ending";
				this.endI = 0;
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
		const rows = ["Party", "Bag", "CryDex", "Save", "Close"];
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
		if (this.input.confirm() || (this.input.start() && this.pauseCursor === 4)) {
			if (this.pauseCursor === 0) this.openParty();
			else if (this.pauseCursor === 1) this.openBag();
			else if (this.pauseCursor === 2) this.openCryDex();
			else if (this.pauseCursor === 3) {
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
	openCryDex() {
		this.mode = "crydex";
		this.dexCursor = 0;
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
		if (this.input.up()) {
			this.dexCursor = (this.dexCursor + n - 1) % n;
			this.audio.ui();
		}
		if (this.input.down()) {
			this.dexCursor = (this.dexCursor + 1) % n;
			this.audio.ui();
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
	openShop(keep = "bram") {
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
		if (this.party.length <= 1) {
			this.note("Max will not send her last CryMon away.");
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
		const amt = healAmount(id);
		if (amt <= 0) {
			this.note("Use that in battle.");
			return false;
		}
		if (this.bag[id] <= 0) return false;
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
		this.party.forEach((m) => {
			m.hp = m.maxHp;
			m.specialPp = m.specialPpMax;
		});
	}
	giveAnneGems() {
		if (this.anneGifted) return;
		this.anneGifted = true;
		this.bag.gem += 5;
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
		if (!this.anneGifted && this.battlesDone >= 1 && this.world.mapId === "veld") {
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
					this.reset();
					this.hasSave = saveExists();
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
					this.note("Stand next to Father, the shelf, or the crate. Press Z.");
				}
			}
			return;
		}
		if (this.mode === "ending") {
			if (this.input.confirm()) {
				this.audio.ui();
				this.endI += 1;
				if (this.endI >= ENDING_WIN.length) {
					this.reset();
				}
			}
			return;
		}
		if (this.mode === "choice") {
			this.updateChoice();
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
		if (this.partyView === "stats" || this.partyView === "moves") {
			if (this.input.cancel() || this.input.confirm() || this.input.start()) {
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
					this.audio.ui();
				} else {
					if (this.party.length <= 1) {
						this.note("Max will not send her last CryMon away.");
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
		const rows = this.shopTab === "buy" ? ITEM_ORDER.filter((id) => ITEMS[id].buy > 0) : this.ownedItems().filter((id) => ITEMS[id].sell > 0);
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
				const cost = ITEMS[id].buy;
				if (this.marks < cost) {
					this.audio.miss();
					this.note("Not enough marks.");
					return;
				}
				this.marks -= cost;
				this.bag[id] += 1;
				this.audio.ok();
				this.note(`Bought ${ITEMS[id].name}.`);
			} else {
				if (this.bag[id] <= 0) return;
				this.bag[id] -= 1;
				this.marks += ITEMS[id].sell;
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
		if (this.updateSoldiers(dt)) {
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
		if (this.input.cancel()) this.cycleParty();
	}
	blocked(x, y) {
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
		for (const npc of NPCS) {
			if (npc.map !== this.world.mapId || !npc.sprite) continue;
			if (npc.id === "shinigami" && this.beatShinigami) continue;
			for (const mark of this.npcMarks(npc)) {
				const s = spawnOf(this.map(), mark);
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
	nearbyTiles() {
		const { x, y } = this.world;
		const d = TILE;
		return [
			tileAt(this.map(), x, y),
			tileAt(this.map(), x - d, y),
			tileAt(this.map(), x + d, y),
			tileAt(this.map(), x, y - d),
			tileAt(this.map(), x, y + d)
		];
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
	npcRadius() {
		if (this.world.mapId === "house") return 36;
		if (this.world.mapId === "veld") return 26;
		return 52;
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
		if (lines) this.say(lines, step.after ?? null);
		if (step.grant || step.heal || step.grantMonster || step.marks) {
			this.audio.ok();
			this.persist(false);
		}
		return true;
	}
	runClosestNpc() {
		const map = this.map();
		const radius = this.npcRadius();
		const flags = this.npcFlags();
		let best = null;
		let bestD = radius * radius;
		for (const npc of NPCS) {
			if (npc.map !== this.world.mapId || !npc.script?.length) continue;
			if (!matchNpcScript(npc.script, flags)) continue;
			for (const mark of this.npcMarks(npc)) {
				const s = spawnOf(map, mark);
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
	startFade(action: "bed" | "loss") {
		this.fade = { phase: "out", t: 0, action };
	}
	applyFadeHold() {
		if (this.fade.action === "bed" && LOGIC.bed.healParty) this.sleepHeal();
		if (this.fade.action === "loss") {
			if (LOGIC.partyWipe.healParty) this.sleepHeal();
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
		if (warp.need && !this.flagFor(warp.need)) {
			if (warp.failTalk) {
				const d = spawnOf(this.map(), ch);
				if (warp.dir === "down") this.world.y = Math.min(this.world.y, d.y - TILE);
				else if (warp.dir === "up") this.world.y = Math.max(this.world.y, d.y + TILE);
				this.doorLock = .5;
				this.say(TALK[warp.failTalk] || TALK.doorLocked);
			}
			return true;
		}
		if (warp.onArrive === "ensureSoldiers") this.ensureSoldiers();
		this.warpTo(warp.to, warp.spawn, warp.dir, warp.oy);
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
				this.pendingSoldier = sol.id;
				this.say(TALK.soldierSpot, "soldier");
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
					else this.startBattle(mintMonster("glimmoth", 3), false, "Mason sends Glimmoth", "mason");
					return;
				}
			}
		}
		if (this.runClosestNpc()) return;
		if (this.nearbyTiles().some((ch) => doorTile(ch))) this.useDoor();
	}
	ensureSoldiers() {
		if (this.soldiers.length) return;
		const m1 = spawnOf(FOREST, "1");
		const m2 = spawnOf(FOREST, "2");
		const m3 = spawnOf(FOREST, "3");
		this.soldiers = [
			{
				id: "patrol",
				name: "Patrol",
				x: m1.x,
				y: m1.y,
				dir: "right",
				frame: 0,
				anim: 0,
				beaten: false,
				chase: false,
				axis: "x",
				min: m1.x - 16,
				max: m1.x + 144,
				sign: 1,
				species: "briarfox",
				level: 4
			},
			{
				id: "scout",
				name: "Scout",
				x: m2.x,
				y: m2.y,
				dir: "left",
				frame: 0,
				anim: 0,
				beaten: false,
				chase: false,
				axis: "y",
				min: m2.y - 80,
				max: m2.y + 80,
				sign: -1,
				species: "mossback",
				level: 4
			},
			{
				id: "sentry",
				name: "Sentry",
				x: m3.x,
				y: m3.y,
				dir: "up",
				frame: 0,
				anim: 0,
				beaten: false,
				chase: false,
				axis: "none",
				min: 0,
				max: 0,
				sign: 0,
				species: "razorbat",
				level: 5
			}
		];
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
					this.say(TALK.soldierSpot, "soldier");
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
	tryMapWarp() {
		if (this.doorLock > 0) return;
		const ch = tileAt(this.map(), this.world.x, this.world.y);
		this.applyWarp(ch);
	}
	warpTo(mapId, mark, dir, yOff = 0) {
		const rows = MAPS[mapId];
		const s = spawnOf(rows, mark);
		this.world.mapId = mapId;
		this.world.x = s.x;
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
		const wsName = { sentry: "Sentry", conscript: "Conscript", enforcer: "Enforcer", cross: "Warden Cross" };
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
			minigame: 0,
			minigameDir: 1,
			minigameHit: null,
			pendingDmg: 0,
			pendingLabel: "",
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
			plPoisoned: false,
			foePoisoned: false
		};
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
		if (id === "gem") {
			const b = this.battle;
			if (b?.wild) {
				const chance = captureChance(b.foe.agl, b.foe.hp, b.foe.maxHp, this.foeDebuffed());
				return `Capture Crystal ${chance}% x${n}`;
			}
			return `Capture Crystal x${n}`;
		}
		if (id === "greatcrystal") {
			const b = this.battle;
			if (b?.wild) {
				const chance = captureChance(b.foe.agl, b.foe.hp, b.foe.maxHp, this.foeDebuffed(), 25);
				return `Greater Crystal ${chance}% x${n}`;
			}
			return `Greater Crystal x${n}`;
		}
		return `${ITEMS[id].name} x${n}`;
	}
	attackMenu(p) {
		const s = SPECIES[p.species];
		if (s.spells?.length) {
			return s.spells.map((sp) => sp.pp ? `${sp.name}  ${p.specialPp}/${p.specialPpMax}` : sp.name);
		}
		const rows = [`${s.basic}`, `${s.special}  ${p.specialPp}/${p.specialPpMax}`];
		if (p.shiny) rows.push("Toxic Burst");
		rows.push("Wait");
		return rows;
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
						this.startFade("loss");
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
							"Barrier  SPC"
						];
						b.cursor = 0;
					}
				}
			}
			return;
		}
		if (b.phase === "minigame") {
			b.minigame += b.minigameDir * dt * 110;
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
				let mul = .7;
				let label = "fizzled";
				if (hit >= 46 && hit <= 54) {
					mul = 2;
					label = "perfect";
					this.audio.special();
				} else if (hit >= 38 && hit <= 62) {
					mul = 1.45;
					label = "connected";
					this.audio.ok();
				} else this.audio.miss();
				const s = SPECIES[b.player.species];
				const atk = b.player.spc + b.mods.selfStr * .2;
				const def = b.foe.spc + b.mods.foeSpc;
				b.pendingDmg = Math.max(1, Math.round((11 + atk * .75 - def * .18) * mul + randI(0, 2)));
				b.pendingLabel = `${s.special} ${label}`;
				b.phase = "resolve_hit";
			}
			return;
		}
		if (b.phase === "resolve_hit") {
			let poisonLine = "";
			if (b.foePoisoned && b.foe.hp > 0) {
				const tick = Math.max(1, Math.floor(b.foe.maxHp / 16));
				b.foe.hp = Math.max(0, b.foe.hp - tick);
				poisonLine = ` Psn-${tick}`;
			}
			b.foe.hp = Math.max(0, b.foe.hp - b.pendingDmg);
			this.shake = .25;
			this.audio.hit();
			const lines = [`${b.pendingLabel}  ${b.pendingDmg} dmg.${poisonLine}`];
			if (b.foe.hp <= 0) {
				const lines2 = [...lines, `${b.foe.name} falls.`];
				if (b.foeBench.length) {
					this.party[this.partyIndex] = { ...b.player };
					grantPartyXp(this.party, this.partyIndex, b.foe.level);
					b.player = { ...this.party[this.partyIndex] };
					const nxt = b.foeBench.shift();
					b.foe = nxt;
					b.mods.foeStr = 0;
					b.mods.foeAgl = 0;
					b.mods.foeSpc = 0;
					b.foeEnterT = 0;
					b.foeFaintT = 0;
					b.msg = [...lines2, `${b.foeName} sends ${nxt.name}.`];
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
			b.afterMsg = "guard";
			return;
		}
		if (b.phase === "resolve_guard") {
			if (b.plPoisoned && b.player.hp > 0) {
				const tick = Math.max(1, Math.floor(b.player.maxHp / 16));
				b.player.hp = Math.max(0, b.player.hp - tick);
			}
			const g = b.guard ?? "block";
			const foeS = SPECIES[b.foe.species];
			let useSpecial = false;
			let moveName = foeS.basic;
			let base;
			if (foeS.spells?.length) {
				let spell = foeS.spells[randI(0, Math.min(2, foeS.spells.length - 1))];
				if (this.selfDebuffed() && b.foe.specialPp > 0 && Math.random() < .55) {
					spell = foeS.spells.find((sp) => sp.id === "manasurge") ?? spell;
				}
				const result = this.castSpell(spell.id, false) ?? { dmg: 1, label: spell.name };
				base = result.dmg;
				moveName = result.label;
			} else {
				useSpecial = b.foe.specialPp > 0 && Math.random() < .28;
				if (useSpecial) b.foe.specialPp -= 1;
				moveName = useSpecial ? foeS.special : foeS.basic;
				const atkStat = useSpecial ? b.foe.spc + b.mods.foeSpc : b.foe.str + b.mods.foeStr;
				base = useSpecial ? 10 + (b.foe.spc + b.mods.foeSpc) * .7 - (b.player.spc + b.mods.selfSpc) * .12 : 6 + (b.foe.str + b.mods.foeStr) * .6 - (b.player.str + b.mods.selfStr) * .15;
			}
			let atkStat = useSpecial ? b.foe.spc + b.mods.foeSpc : b.foe.str + b.mods.foeStr;
			if (b.foe.shiny && !b.plPoisoned && randI(0, 99) < 30) {
				useSpecial = false;
				moveName = "Toxic Burst";
				base = 4 + (b.foe.str + b.mods.foeStr) * .5 - (b.player.str + b.mods.selfStr) * .16;
				atkStat = b.foe.str + b.mods.foeStr;
				b.plPoisoned = true;
			}
			const defStat = g === "dodge" ? b.player.agl + b.mods.selfAgl : g === "block" ? b.player.str + b.mods.selfStr : b.player.spc + b.mods.selfSpc;
			const chance = clamp(50 + (defStat - atkStat) * 5 + randI(-10, 10), 12, 88);
			const success = randI(1, 100) <= chance;
			let dmg = Math.max(1, Math.round(base + randI(0, 3)));
			let line = "";
			if (g === "dodge") {
				if (success) {
					dmg = 0;
					line = `${b.player.name} slips aside.`;
					this.audio.ok();
				} else {
					line = `The dodge fails. ${dmg} dmg.`;
					this.audio.hit();
				}
			} else if (g === "block") {
				if (success) {
					dmg = Math.max(1, Math.round(dmg * .5));
					line = `Blocked. ${dmg} dmg leaks through.`;
				} else {
					line = `The block breaks. ${dmg} dmg.`;
					this.audio.hit();
				}
			} else if (success) {
				dmg = Math.max(1, Math.round(dmg * .4));
				line = `A thin barrier holds. ${dmg} dmg.`;
				this.audio.ok();
			} else {
				line = `The barrier shivers apart. ${dmg} dmg.`;
				this.audio.hit();
			}
			b.player.hp = Math.max(0, b.player.hp - dmg);
			this.shake = success && dmg === 0 ? .05 : .28;
			if (b.player.hp <= 0) {
				this.party[this.partyIndex] = { ...b.player };
				const next = this.party.findIndex((m, i) => i !== this.partyIndex && m.hp > 0);
				if (next >= 0) {
					this.partyIndex = next;
					b.player = { ...this.party[next] };
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
			b.msg = [`${b.foe.name} uses ${moveName}.`, line];
			b.msgI = 0;
			b.phase = "msg";
			b.afterMsg = "item";
			return;
		}
		if (b.phase === "item" || b.phase === "attack" || b.phase === "guard") {
			if (this.input.pressed("ArrowUp") || this.input.pressed("KeyW")) {
				b.cursor = (b.cursor + b.menu.length - 1) % b.menu.length;
				this.audio.ui();
			}
			if (this.input.pressed("ArrowDown") || this.input.pressed("KeyS")) {
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
		} else if (fx.kind === "flee") {
			if (!b.wild) {
				this.bag[id] += 1;
				b.msg = ["Cannot flee a tamer's fight."];
			} else {
				b.msg = [`${ITEMS[id].name}. Max slips away.`];
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
				const chance = captureChance(b.foe.agl, b.foe.hp, b.foe.maxHp, this.foeDebuffed(), fx.bonus ?? 0);
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
					if (this.party.length < PARTY_MAX) {
						this.party.push(caught);
						b.msg = [`${ITEMS[id].name} takes. ${b.foe.name} is yours.`];
						b.afterMsg = "end_catch";
					} else {
						this.pendingCatch = caught;
						b.msg = [
							`${ITEMS[id].name} takes. ${b.foe.name} is yours.`,
							"Six already travel with Max. Release one to keep the new CryMon, or let it go."
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
		const s = SPECIES[b.player.species];
		if (s.spells?.length) {
			const spell = s.spells[i];
			if (!spell) return;
			this.castSpell(spell.id, true);
			return;
		}
		const waitI = b.player.shiny ? 3 : 2;
		const toxicI = b.player.shiny ? 2 : -1;
		if (i === waitI) {
			b.msg = ["Max holds."];
			b.msgI = 0;
			b.phase = "msg";
			b.afterMsg = "guard";
			this.audio.ui();
			return;
		}
		if (i === toxicI) {
			const atk = b.player.str + b.mods.selfStr;
			const def = b.foe.str + b.mods.foeStr;
			b.pendingDmg = Math.max(1, Math.round(4 + atk * .5 - def * .16 + randI(0, 2)));
			b.pendingLabel = "Toxic Burst";
			b.foePoisoned = true;
			b.phase = "resolve_hit";
			this.audio.special();
			return;
		}
		if (i === 1) {
			if (b.player.specialPp <= 0) {
				b.msg = [`${s.special} is spent.`];
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
		const atk = b.player.str + b.mods.selfStr;
		const def = b.foe.str + b.mods.foeStr;
		b.pendingDmg = Math.max(1, Math.round(6 + atk * .62 - def * .16 + randI(0, 3)));
		b.pendingLabel = s.basic;
		b.phase = "resolve_hit";
	}
	foeDebuffed() {
		const m = this.battle.mods;
		return m.foeStr < 0 || m.foeAgl < 0 || m.foeSpc < 0;
	}
	selfDebuffed() {
		const m = this.battle.mods;
		return m.selfStr < 0 || m.selfAgl < 0 || m.selfSpc < 0;
	}
	castSpell(id, fromPlayer) {
		const b = this.battle;
		const caster = fromPlayer ? b.player : b.foe;
		const s = SPECIES[caster.species];
		let dmg = 0;
		let label = "";
		if (id === "firebolt") {
			if (fromPlayer) b.mods.foeStr -= 4;
			else b.mods.selfStr -= 4;
			dmg = Math.max(1, Math.round(5 + caster.spc * .35 + randI(0, 2)));
			label = "Fire Bolt  STR-4";
		} else if (id === "icebeam") {
			if (fromPlayer) b.mods.foeAgl -= 4;
			else b.mods.selfAgl -= 4;
			dmg = Math.max(1, Math.round(5 + caster.spc * .35 + randI(0, 2)));
			label = "Ice Beam  AGI-4";
		} else if (id === "lightning") {
			if (fromPlayer) b.mods.foeSpc -= 4;
			else b.mods.selfSpc -= 4;
			dmg = Math.max(1, Math.round(5 + caster.spc * .35 + randI(0, 2)));
			label = "Lightning Strike  SPC-4";
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
			const atk = caster.spc;
			const def = fromPlayer ? b.foe.spc + b.mods.foeSpc : b.player.spc + b.mods.selfSpc;
			dmg = Math.max(1, Math.round((11 + atk * .75 - def * .18) * mul + randI(0, 2)));
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
	finishWin() {
		const b = this.battle;
		this.party[this.partyIndex] = { ...b.player };
		const m = this.party[this.partyIndex];
		const grew = grantPartyXp(this.party, this.partyIndex, b.foe.level);
		if (!b.wild) {
			if (b.trainer === "calder") {
				this.beatCalder = true;
				if (!this.mason2Done && !this.mason2Map) this.mason2Map = pickMason2Map(Math.random());
				this.marks += 18;
				this.mode = "world";
				this.battle = null;
				this.world.encounterLock = 3;
				this.onBattleOver();
				this.say(TALK.calderWin);
				this.audio.ok();
				return;
			}
			if (b.trainer === "soldier") {
				const sol = this.soldiers.find((s) => s.id === b.soldierId);
				if (sol) sol.beaten = true;
				this.marks += 8;
				this.mode = "world";
				this.battle = null;
				this.world.encounterLock = 3;
				this.onBattleOver();
				this.say(TALK.soldierAfter);
				this.audio.ok();
				return;
			}
			if (b.trainer === "wsoldier") {
				const who = b.soldierId || this.pendingWs;
				this.mode = "world";
				this.battle = null;
				this.world.encounterLock = 3;
				this.onBattleOver();
				if (who === "sentry") {
					this.beatSentry = true;
					this.bag.cageKey = (this.bag.cageKey ?? 0) + 1;
					this.marks += 12;
					this.say(TALK.sentryWin);
				} else if (who === "conscript") {
					this.beatConscript = true;
					this.marks += 14;
					this.say(TALK.conscriptWin);
				} else if (who === "enforcer") {
					this.beatEnforcer = true;
					this.marks += 15;
					this.say(TALK.enforcerWin);
				} else {
					this.beatCross = true;
					this.marks += 18;
					this.say(TALK.crossWin);
				}
				this.audio.ok();
				return;
			}
			if (b.trainer === "shinigami") {
				this.beatShinigami = true;
				this.hasScroll = true;
				this.marks += 14;
				this.mode = "world";
				this.battle = null;
				this.world.encounterLock = 3;
				this.onBattleOver();
				this.say(TALK.shinigamiAfter, "choice");
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
			this.foughtMason = true;
			this.rival.phase = "done";
			this.marks += 10;
			this.mode = "world";
			this.battle = null;
			this.world.encounterLock = 3;
			this.onBattleOver();
			this.say(TALK.masonWin, "masonLeave");
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
		this.note(grew ? `${m.name} grew to lv ${m.level}.` : `${m.name} stands over the grass.`);
	}
	updateChoice() {
		if (this.input.up() || this.input.down()) {
			this.choiceCur = 1 - this.choiceCur;
			this.audio.ui();
		}
		if (this.input.confirm()) {
			this.audio.ok();
			this.mode = "world";
			if (this.choiceCur === 0) this.say(TALK.choiceFather, "ending");
			else this.say(TALK.choiceHeavenfall, "ending");
		}
	}
	draw() {
		const ctx = this.ctx;
		ctx.save();
		ctx.imageSmoothingEnabled = false;
		ctx.webkitImageSmoothingEnabled = false;
		if (this.shake > 0) ctx.translate((Math.random() - .5) * 6 * this.shake, (Math.random() - .5) * 4 * this.shake);
		if (this.mode === "title") this.drawTitle();
		else if (this.mode === "intro") this.drawStory(INTRO[this.introI] ?? "", "The leaving");
		else if (this.mode === "ending") this.drawStory(ENDING_WIN[this.endI] ?? "", "The war");
		else if (this.mode === "battle") this.drawBattle();
		else if (this.mode === "bag") this.drawBag();
		else if (this.mode === "party") this.drawParty();
		else if (this.mode === "shop") this.drawShop();
		else if (this.mode === "choice") this.drawChoice();
		else if (this.mode === "pause") this.drawPause();
		else if (this.mode === "crydex") this.drawCryDex();
		else this.drawWorld();
		this.drawFade();
		ctx.restore();
	}
	drawFade() {
		const a = fadeAlpha(this.fade.phase, this.fade.t);
		if (a <= 0) return;
		this.ctx.save();
		this.ctx.globalAlpha = a;
		this.ctx.fillStyle = "#000";
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
		this.box(X(64), Y(28), X(112), Y(92));
		this.text("PAUSE", X(120), Y(34), "#e8e4d8", FONT, "center");
		const rows = ["Party", "Bag", "CryDex", "Save", "Close"];
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
		const vis = 9;
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
				label = `${s.name}  owned`;
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
		this.text("Z / X  back", X(16), Y(148), "#5a7a52", FONT);
	}
	drawStory(body, tag) {
		if (tag === "The leaving") {
			this.drawMap(HOUSE, 0, 0);
			const bed = spawnOf(HOUSE, "B");
			const mine = spawnOf(HOUSE, "U");
			const shelf = spawnOf(HOUSE, "S");
			const crate = spawnOf(HOUSE, "C");
			this.drawSprite("prop-bed-father", bed.x - 32, bed.y - 44, 64, 56);
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
		const map = this.map();
		const mw = (map[0]?.length ?? 1) * TILE;
		const mh = map.length * TILE;
		let cx = this.world.x - VIEW_W / 2;
		let cy = this.world.y - VIEW_H / 2;
		cx = clamp(cx, 0, Math.max(0, mw - VIEW_W));
		cy = clamp(cy, 0, Math.max(0, mh - VIEW_H));
		return {
			cx,
			cy
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
		if (ch === "C" || ch === "S") {
			fill("#6a5238");
			fill("#4a3a28", dx, dy + 12, t, 1);
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
		if (ch === "N" || ch === "E") {
			fill("#3d5a38");
			fill("#8a7348", dx + 2, dy + 7, 12, 9);
			fill("#6a4030", dx + 1, dy + 2, 14, 6);
			fill("#3a2c22", dx + 7, dy, 2, 4);
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
			ctx.fillStyle = "#c5cec6";
			ctx.fillRect(x + 4, y + 4, w - 8, h - 6);
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
		let w = SPR_W;
		let h = SPR_H;
		if (String(key).startsWith("mason-")) {
			w *= 2;
			h *= 2;
		}
		this.drawSprite(key, wx - cx - w / 2, wy - cy - h + 4, w, h);
	}
	drawWorldHud() {
		const lead = this.lead();
		this.box(8, 8, 300, 40);
		this.text("MAX", 16, 12, "#e8e4d8", FONT);
		this.text(`Xtals ${this.bag.gem}`, 88, 12, "#c5cec6", FONT);
		this.text(`M ${this.marks}`, 200, 12, "#8f4a40", FONT);
		this.text(lead ? `${lead.name} Lv${lead.level}  ${lead.hp}/${lead.maxHp}` : "No CryMon yet", 16, 28, "#8a8678", FONT);
		if (this.hasScroll) this.text("SCROLL", 200, 28, "#c5cec6", FONT);
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
	hintZ(wx, wy, radius = 52) {
		const { cx, cy } = this.cam();
		const dx = wx - this.world.x;
		const dy = wy - this.world.y;
		if (dx * dx + dy * dy > radius * radius) return;
		this.text("Z", wx - cx - 2, wy - cy - 22, "#e8e4d8", FONT);
	}
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
			this.drawProp("prop-bed-father", bed.x, bed.y + 8, 64, 56);
			this.drawProp("prop-bed-empty", mine.x, mine.y + 8, 64, 56);
			this.drawProp("prop-shelf", shelf.x, shelf.y + 4, 40, 44);
			this.drawProp("prop-crate", crate.x, crate.y + 4, 32, 32);
			this.text("...", bed.x - cx - 6, bed.y - cy - 20, "#8a8678", FONT);
			this.hintZ(bed.x, bed.y, 36);
			this.hintZ(mine.x, mine.y, 36);
			this.hintZ(shelf.x, shelf.y, 36);
			this.hintZ(crate.x, crate.y, 36);
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
			if (!this.gotStump) {
				const stump = spawnOf(VELD, "L");
				this.drawProp("prop-stump", stump.x, stump.y + 4, 32, 32);
				this.hintZ(stump.x, stump.y);
			}
		}
		const wf = Math.floor(this.clock * 4) % 4 + 1;
		if (this.world.mapId === "veld") {
			const k = spawnOf(VELD, "K");
			this.drawActor(`wren-${wf}`, k.x, k.y);
			this.hintZ(k.x, k.y);
			const mae = spawnOf(VELD, "I");
			this.drawActor(`mae-${wf}`, mae.x, mae.y);
			this.hintZ(mae.x, mae.y);
			const ivo = spawnOf(VELD, "V");
			this.drawActor(`ivo-${wf}`, ivo.x, ivo.y);
			this.hintZ(ivo.x, ivo.y);
			const nell = spawnOf(VELD, "A");
			this.drawActor(`nell-${wf}`, nell.x, nell.y);
			this.hintZ(nell.x, nell.y);
			const pike = spawnOf(VELD, "Q");
			this.drawActor(`pike-${wf}`, pike.x, pike.y);
			this.hintZ(pike.x, pike.y);
			const bram = spawnOf(VELD, "J");
			this.drawActor(`bram-${wf}`, bram.x, bram.y);
			this.hintZ(bram.x, bram.y);
			const e = spawnOf(VELD, "E");
			this.drawActor(`calder-${wf}`, e.x, e.y);
			this.hintZ(e.x, e.y);
			if (this.rival.phase !== "off") {
				const walking = this.rival.phase === "approach" || this.rival.phase === "leave";
				const rf = walking ? this.rival.frame % 4 + 1 : 1;
				this.drawActor(`mason-${this.rival.dir}-${rf}`, this.rival.x, this.rival.y);
				if (this.rival.phase === "done") this.hintZ(this.rival.x, this.rival.y);
			}
		}
		if (this.anne.phase !== "off") {
			const walking = this.anne.phase === "approach" || this.anne.phase === "approach2" || this.anne.phase === "leave";
			const af = walking ? this.anne.frame % 4 + 1 : 1;
			this.drawActor(`anne-${this.anne.dir}-${af}`, this.anne.x, this.anne.y);
		}
		if (this.world.mapId === "forest") {
			this.ensureSoldiers();
			for (const sol of this.soldiers) {
				const sf = sol.beaten ? 1 : sol.frame % 4 + 1;
				this.drawActor(`soldier-${sol.dir}-${sf}`, sol.x, sol.y);
				this.hintZ(sol.x, sol.y);
			}
		}
		if (this.world.mapId === "grove") {
			const k = spawnOf(GROVE, "K");
			this.drawActor(`cross-${wf}`, k.x, k.y);
			this.hintZ(k.x, k.y);
			if (!this.cathleenCaught) {
				const c = spawnOf(GROVE, "8");
				this.drawSprite("cathleen-ow", c.x - cx - 36, c.y - cy - 68, 72, 72, true);
				this.hintZ(c.x, c.y);
			}
			if (!this.beatShinigami) {
				const s = spawnOf(GROVE, "9");
				const sf = Math.floor(this.clock * 3) % 4 + 1;
				this.drawActor(`shinigami-down-${sf}`, s.x, s.y);
				this.hintZ(s.x, s.y);
			}
		}
		if (this.world.mapId === "camp") {
			const commander = spawnOf(CAMP, "I");
			this.drawActor(`commander-${wf}`, commander.x, commander.y);
			this.hintZ(commander.x, commander.y);
			const conscript = spawnOf(CAMP, "K");
			this.drawActor(`conscript-${wf}`, conscript.x, conscript.y);
			this.hintZ(conscript.x, conscript.y);
			const enforcer = spawnOf(CAMP, "A");
			this.drawActor(`enforcer-${wf}`, enforcer.x, enforcer.y);
			this.hintZ(enforcer.x, enforcer.y);
		}
		if (this.world.mapId === "cliffs") {
			const sentry = spawnOf(CLIFFS, "V");
			this.drawActor(`sentry-${wf}`, sentry.x, sentry.y);
			this.hintZ(sentry.x, sentry.y);
			const tessa = spawnOf(CLIFFS, "Y");
			this.drawActor(`tessa-${wf}`, tessa.x, tessa.y);
			this.hintZ(tessa.x, tessa.y);
			const chest = spawnOf(CLIFFS, "C");
			this.drawProp("prop-crate", chest.x, chest.y + 4, 32, 32);
			this.hintZ(chest.x, chest.y);
		}
		if (this.world.mapId === "ruins") {
			const oren = spawnOf(RUINS, "J");
			this.drawActor(`oren-${wf}`, oren.x, oren.y);
			this.hintZ(oren.x, oren.y);
			const birch = spawnOf(RUINS, "K");
			this.drawActor(`birch-${wf}`, birch.x, birch.y);
			this.hintZ(birch.x, birch.y);
			const sable = spawnOf(RUINS, "A");
			this.drawActor(`sable-${wf}`, sable.x, sable.y);
			this.hintZ(sable.x, sable.y);
		}
		const frame = this.world.moving ? this.world.frame % 4 + 1 : 1;
		this.drawActor(`max-${this.world.dir}-${frame}`, this.world.x, this.world.y);
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
		if (beat.speaker !== "none") {
			this.drawSprite(`port-${beat.speaker}`, X(-4), Y(6), X(120), Y(150), "top", true);
			this.ctx.fillStyle = "rgba(18,17,14,0.45)";
			this.ctx.fillRect(X(108), 0, VIEW_W - X(108), VIEW_H);
			this.box(X(112), Y(6), X(122), Y(62));
			const who = SPEAKER_NAME[beat.speaker];
			this.text(who.toUpperCase(), X(118), Y(10), "#c5cec6", FONT);
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
		if (items.length === 0) this.text("The pouch is empty.", X(18), Y(36), "#8a8678", FONT);
		else {
			const shown = 5;
			const start = Math.max(0, Math.min(this.bagCursor, Math.max(0, items.length - shown)));
			for (let i = 0; i < shown; i++) {
				const idx = start + i;
				const id = items[idx];
				if (!id) break;
				const y = Y(32 + i * 18);
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
			const s = SPECIES[m.species];
			this.drawMonIcon(m, X(12), Y(24), X(88), Y(110));
			this.text(m.name.toUpperCase(), X(108), Y(28), "#e8e4d8", FONT);
			this.text(`Lv${m.level}  ${natureOf(m.nature ?? 0).name}`, X(108), Y(40), "#8a8678", FONT);
			if (this.partyView === "stats") {
				this.text(`HP  ${m.hp}/${m.maxHp}`, X(108), Y(56), "#e8e4d8", FONT);
				this.hpBar(X(108), Y(68), X(100), m.hp, m.maxHp);
				this.text(`STR ${m.str}`, X(108), Y(80), "#c5cec6", FONT);
				this.text(`AGL ${m.agl}`, X(108), Y(92), "#c5cec6", FONT);
				this.text(`SPC ${m.spc}`, X(108), Y(104), "#c5cec6", FONT);
				this.text(`XP  ${m.xp}/${m.level * 10}`, X(108), Y(116), "#8a8678", FONT);
			} else {
				this.text("BASIC", X(108), Y(56), "#8a8678", FONT);
				if (s.spells?.length) {
					s.spells.forEach((sp, i) => {
						const extra = sp.pp ? `  ${m.specialPp}/${m.specialPpMax}` : "";
						this.text(sp.name + extra, X(108), Y(68 + i * 12), "#e8e4d8", FONT);
					});
				} else {
					this.text(s.basic, X(108), Y(68), "#e8e4d8", FONT);
					this.text("SPECIAL", X(108), Y(84), "#8a8678", FONT);
					this.text(`${s.special}  ${m.specialPp}/${m.specialPpMax}`, X(108), Y(96), "#e8e4d8", FONT);
				}
				this.text(s.blurb.slice(0, 28), X(16), Y(140), "#8a8678", FONT);
			}
			this.text("Z / X  back", X(16), Y(148), "#5a7a52", FONT);
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
		} else this.text(this.partyView === "target" ? "Z  use   X  bag" : "Z  choose   Start  close", X(16), Y(148), "#5a7a52", FONT);
		if (this.hudT > 0) this.text(this.hudFlash.slice(0, 34), X(16), Y(148), "#e8e4d8", FONT);
	}
	drawShop() {
		this.drawWorld();
		this.ctx.fillStyle = "rgba(18,17,14,0.55)";
		this.ctx.fillRect(0, 0, VIEW_W, VIEW_H);
		this.box(X(10), Y(8), X(220), Y(144));
		this.text(this.shopKeep === "oren" ? "OREN'S STALL" : "BRAM'S STALL", X(18), Y(14), "#c5cec6", FONT);
		this.text(`Marks ${this.marks}`, X(150), Y(14), "#8f4a40", FONT);
		this.text(this.shopTab === "buy" ? ">BUY   sell" : " buy   >SELL", X(18), Y(28), "#e8e4d8", FONT);
		const rows = this.shopTab === "buy" ? ITEM_ORDER.filter((id) => ITEMS[id].buy > 0) : this.ownedItems().filter((id) => ITEMS[id].sell > 0);
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
				const price = this.shopTab === "buy" ? ITEMS[id].buy : ITEMS[id].sell;
				this.text(`${on ? ">" : " "}${ITEMS[id].name}  ${price}m  x${this.bag[id]}`, X(18), y, on ? "#e8e4d8" : "#8a8678", FONT);
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
		this.box(X(108), Y(78), X(126), Y(28));
		this.text(`${b.player.shiny ? "*" : ""}${b.player.name.toUpperCase()} Lv${b.player.level}`, X(112), Y(80), b.player.shiny ? "#d4c06a" : "#e8e4d8", FONT);
		this.hpBar(X(112), Y(92), X(96), b.player.hp, b.player.maxHp);
		this.text(`${b.player.hp}`, X(212), Y(90), "#8a8678", FONT);
		if (b.phase === "msg") {
			this.box(X(6), Y(110), X(228), Y(46));
			const line = b.msg[b.msgI] ?? "";
			this.wrap(line, 42).forEach((ln, i) => this.text(ln, X(12), Y(116 + i * 10), "#e8e4d8", FONT));
			return;
		}
		if (b.phase === "minigame") {
			this.box(X(16), Y(110), X(208), Y(44));
			this.text("SPECIAL  hit the mark", X(24), Y(114), "#c5cec6", FONT);
			this.ctx.fillStyle = "#2a2620";
			this.ctx.fillRect(X(24), Y(132), X(192), Y(10));
			this.ctx.fillStyle = "#5a7a52";
			this.ctx.fillRect(X(98), Y(132), X(44), Y(10));
			this.ctx.fillStyle = "#e8e4d8";
			this.ctx.fillRect(X(24) + b.minigame / 100 * X(192) - 2, Y(128), 6, Y(18));
			return;
		}
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
