import { i as __toESM } from "../_runtime.mjs";
import { L as require_react, v as require_jsx_runtime } from "../_libs/@tanstack/react-router+[...].mjs";
import { i as Download, n as Volume2, t as VolumeX } from "../_libs/lucide-react.mjs";
import { n as clsx, t as cva } from "../_libs/class-variance-authority+clsx.mjs";
import { t as twMerge } from "../_libs/tailwind-merge.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/routes-BlcnZOll.js
var import_react = /* @__PURE__ */ __toESM(require_react());
var import_jsx_runtime = require_jsx_runtime();
function cn(...inputs) {
	return twMerge(clsx(inputs));
}
var buttonVariants = cva("inline-flex items-center justify-center gap-2 whitespace-nowrap font-medium transition-[opacity,transform,background-color,color] duration-150 ease-out focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring/70 disabled:pointer-events-none disabled:opacity-40 [&_svg]:pointer-events-none [&_svg]:size-4 [&_svg]:shrink-0 active:scale-[0.98] cursor-pointer", {
	variants: {
		variant: {
			default: "bg-fg text-bg hover:opacity-90",
			accent: "bg-accent text-accent-fg hover:opacity-90",
			outline: "border border-border bg-transparent text-fg hover:bg-raised",
			ghost: "text-muted hover:text-fg hover:bg-raised",
			danger: "bg-danger text-bg hover:opacity-90"
		},
		size: {
			sm: "h-9 rounded-sm px-3 text-sm",
			md: "h-11 rounded-md px-4 text-sm",
			lg: "h-12 rounded-md px-5 text-base",
			icon: "size-11 rounded-md"
		}
	},
	defaultVariants: {
		variant: "default",
		size: "md"
	}
});
var Button = import_react.forwardRef(({ className, variant, size, type = "button", ...props }, ref) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
	ref,
	type,
	className: cn(buttonVariants({
		variant,
		size
	}), className),
	...props
}));
Button.displayName = "Button";
var Chip = class {
	ctx = null;
	muted = false;
	unlock() {
		if (this.ctx) {
			this.ctx.resume();
			return;
		}
		const C = window.AudioContext || window.webkitAudioContext;
		this.ctx = new C();
	}
	beep(freq, dur, type, gain = .05) {
		if (this.muted) return;
		this.unlock();
		const ctx = this.ctx;
		if (!ctx) return;
		const o = ctx.createOscillator();
		const g = ctx.createGain();
		o.type = type;
		o.frequency.value = freq;
		g.gain.value = gain;
		g.gain.exponentialRampToValueAtTime(1e-4, ctx.currentTime + dur);
		o.connect(g);
		g.connect(ctx.destination);
		o.start();
		o.stop(ctx.currentTime + dur);
	}
	ui() {
		this.beep(520, .05, "square", .03);
	}
	ok() {
		this.beep(720, .07, "square", .04);
		this.beep(980, .09, "square", .03);
	}
	hit() {
		this.beep(180, .09, "sawtooth", .05);
	}
	special() {
		this.beep(440, .06, "square", .04);
		this.beep(660, .1, "square", .04);
	}
	miss() {
		this.beep(140, .12, "triangle", .04);
	}
	catch() {
		this.beep(520, .08, "square", .04);
		this.beep(780, .12, "square", .04);
	}
	step() {
		this.beep(90, .03, "square", .02);
	}
};
var SPECIES = {
	quillpup: {
		id: "quillpup",
		name: "Quillpup",
		blurb: "A bristled hound. Family leftover. Hits like a thrown crate.",
		maxHp: 34,
		str: 15,
		agl: 10,
		spc: 7,
		basic: "Nip",
		special: "Quillburst",
		specialPp: 3,
		wild: false
	},
	glimmoth: {
		id: "glimmoth",
		name: "Glimmoth",
		blurb: "Lantern-gut moth of the tall grass. Burns what it blesses.",
		maxHp: 26,
		str: 7,
		agl: 13,
		spc: 16,
		basic: "Dustwing",
		special: "Lampflare",
		specialPp: 3,
		wild: true
	},
	tortcask: {
		id: "tortcask",
		name: "Tortcask",
		blurb: "A walking cask of moss and stubbornness.",
		maxHp: 42,
		str: 13,
		agl: 5,
		spc: 8,
		basic: "Shove",
		special: "Shellslam",
		specialPp: 3,
		wild: true
	},
	razorbat: {
		id: "razorbat",
		name: "Razorbat",
		blurb: "Camp-bred cutter. Hunts by the whistle of its wings.",
		maxHp: 30,
		str: 14,
		agl: 16,
		spc: 9,
		basic: "Rake",
		special: "Swoopcut",
		specialPp: 3,
		wild: false
	},
	mossback: {
		id: "mossback",
		name: "Mossback",
		blurb: "A toad in a coat of wet leaves. Absorbs what it sits on.",
		maxHp: 38,
		str: 12,
		agl: 6,
		spc: 11,
		basic: "Squelch",
		special: "Mossguard",
		specialPp: 3,
		wild: true
	},
	briarfox: {
		id: "briarfox",
		name: "Briarfox",
		blurb: "Thorn-pelt fox of the deep trees. Fast, and it bites last.",
		maxHp: 28,
		str: 13,
		agl: 17,
		spc: 10,
		basic: "Bramble",
		special: "Thornrush",
		specialPp: 3,
		wild: true
	}
};
var ITEM_ORDER = [
	"salve",
	"bandage",
	"bitterroot",
	"dust",
	"gem"
];
var ITEMS = {
	gem: {
		id: "gem",
		name: "Capture Crystal",
		desc: "Moonstone cage. Seals a worn-down wild CryMon.",
		battle: true,
		field: false,
		buy: 20,
		sell: 10
	},
	salve: {
		id: "salve",
		name: "Moss salve",
		desc: "Restores 22 HP.",
		battle: true,
		field: true,
		buy: 10,
		sell: 5
	},
	bitterroot: {
		id: "bitterroot",
		name: "Bitterroot",
		desc: "STR +4 this fight.",
		battle: true,
		field: false,
		buy: 8,
		sell: 4
	},
	dust: {
		id: "dust",
		name: "Ash dust",
		desc: "Foe STR-3 AGI-2 SPC-2 this fight.",
		battle: true,
		field: false,
		buy: 8,
		sell: 4
	},
	bandage: {
		id: "bandage",
		name: "Linen wrap",
		desc: "Restores 12 HP.",
		battle: true,
		field: true,
		buy: 6,
		sell: 3
	}
};
function mintMonster(species, level = 3) {
	const s = SPECIES[species];
	const lv = Math.max(1, level);
	const grow = 1 + (lv - 3) * .12;
	const maxHp = Math.round(s.maxHp * grow);
	return {
		id: `${species}-${Math.random().toString(36).slice(2, 7)}`,
		species,
		name: s.name,
		hp: maxHp,
		maxHp,
		str: Math.round(s.str * grow),
		agl: Math.round(s.agl * grow),
		spc: Math.round(s.spc * grow),
		specialPp: s.specialPp,
		specialPpMax: s.specialPp,
		level: lv,
		xp: 0
	};
}
function grantXp(m, foeLevel) {
	m.xp += 6 + foeLevel * 4;
	let grew = false;
	while (m.xp >= m.level * 10 && m.level < 12) {
		m.xp -= m.level * 10;
		m.level += 1;
		m.maxHp += 3;
		m.hp = Math.min(m.maxHp, m.hp + 3);
		m.str += 1;
		m.agl += 1;
		m.spc += 1;
		grew = true;
	}
	return grew;
}
var HOUSE_MAP = [
	"HHHHHHHHHHHHHH",
	"HFFFFFFFFFFFFH",
	"HFFFFFFFFFFFFH",
	"HFFFFFFFFFFFFH",
	"HFBFFFFSFFFCFH",
	"HFFFFFFFFFFFFH",
	"HUFFFFFFFFFFFH",
	"HFFFFPFFFFFFFH",
	"HFFFFFFFFFFFFH",
	"HFFFFFFFFFFFFH",
	"HHHHHHDHHHHHHH"
];
var VELD_MAP = [
	"##############################",
	"####..........RRRR..........##",
	"##.Q.^^.......HHHH......WWW.##",
	"##............HDH......WWA..##",
	"##..K.........===.......W....#",
	"##...TTT.....=====.....TTT..G#",
	"##...TTT....===,===....TTT...#",
	"##....M......=====....**.....#",
	"##.V.TTT......===......TTT...#",
	"##............===............#",
	"###....X...J.=====...........#",
	"##...TTT......===............#",
	"##............===.......L....#",
	"##...TTT.....=====......TTT..#",
	"##............===......^^....#",
	"##....TTT....=====......TTT..#",
	"##....TTT.....===......TTT...#",
	"##............===............#",
	"##...........=====.....NNNN..#",
	"##............===.......NE...#",
	"###...........===...........##",
	"#############=Z=##############"
];
var FOREST_MAP = [
	"##########################",
	"####.........Y.........###",
	"###.........===.........##",
	"##...TTT....===....TTT..##",
	"##...TTT...=====...TTT..##",
	"##.1........===.......2.##",
	"##...TTT....===....TTT..##",
	"##..........=====.......##",
	"##...TTT....===....TTT..##",
	"##...........===........##",
	"##...TTT....=====..TTT..##",
	"##...........===........##",
	"##...TTT.....===...TTT..##",
	"##...........=====......##",
	"##....TTT....===...TTT..##",
	"##............===.......##",
	"##...TTT......===..TTT..##",
	"##............===....3..##",
	"###...........===......###",
	"##########################"
];
function normalize(map) {
	const w = Math.max(...map.map((r) => r.length));
	return map.map((r) => r.padEnd(w, "#"));
}
var HOUSE = normalize(HOUSE_MAP);
var VELD = normalize(VELD_MAP);
var FOREST = normalize(FOREST_MAP);
var MAPS = {
	house: HOUSE,
	veld: VELD,
	forest: FOREST
};
var SPEAKER_NAME = {
	max: "Max",
	anne: "Anne",
	mason: "Mason",
	wren: "Wren",
	ivo: "Ivo",
	nell: "Nell",
	pike: "Pike",
	calder: "Calder",
	bram: "Bram",
	none: ""
};
var INTRO = [
	"The cottage is quiet. Father sleeps poorly. Quillpup ticks on the floorboards.",
	"Max is eight. She has already decided. If the war pays in medicine, she will take it.",
	"The shelf is empty. No Capture Crystals. Only the family hound and a dress she should have grown out of.",
	"No note. No permission. The door takes the rest of the night."
];
var ENDING_WIN = [
	"Calder sits in the mud and laughs once, without humour.",
	"\"Fine. The camp takes strays. Keep that hound close. The war does not care that you are eight.\"",
	"South, drums. Max checks the crystals. They are fewer than she thought.",
	"GEMWAR — the road continues. Walk. Catch. Survive."
];
function solidTile(ch) {
	return "#HWRBC^NKEVAQXUJ".includes(ch);
}
function doorTile(ch) {
	return ch === "D";
}
function spawnOf(map, mark) {
	for (let y = 0; y < map.length; y++) {
		const x = map[y].indexOf(mark);
		if (x >= 0) return {
			x: x * 32 + 16,
			y: y * 32 + 16
		};
	}
	return {
		x: 64,
		y: 64
	};
}
var START_BAG = {
	gem: 0,
	salve: 2,
	bitterroot: 1,
	dust: 1,
	bandage: 2
};
function healAmount(id) {
	if (id === "salve") return 22;
	if (id === "bandage") return 12;
	return 0;
}
var TALK = {
	father: [{
		speaker: "max",
		text: "I'll bring the medicine. Sleep."
	}, {
		speaker: "none",
		text: "Father's breath is thin. He does not wake. The war is the medicine, you told yourself."
	}],
	bed: [{
		speaker: "max",
		text: "Just until they breathe again."
	}, {
		speaker: "none",
		text: "Max's empty bed. The CryMon sleep. Cuts close. Specials return."
	}],
	shelf: [{
		speaker: "max",
		text: "Gone. Father sold the last ones for fever-tea."
	}, {
		speaker: "none",
		text: "Dust on the shelf. No Capture Crystals. You go out empty-handed."
	}],
	crate: [{
		speaker: "max",
		text: "A wrap. He won't miss it."
	}, {
		speaker: "none",
		text: "A linen wrap under the lid. You take it."
	}],
	crateEmpty: [{
		speaker: "max",
		text: "Splinters and a moth. Empty."
	}],
	doorOut: [{
		speaker: "max",
		text: "Night air. I can do this."
	}, {
		speaker: "none",
		text: "Tall grass hides CryMon. Wren west. Pond east. Bram on the path. Calder south."
	}],
	footsteps: [{
		speaker: "none",
		text: "Footsteps on the path. Someone followed you out."
	}],
	masonFight: [
		{
			speaker: "mason",
			text: "You walked out with that hound."
		},
		{
			speaker: "max",
			text: "He's mine."
		},
		{
			speaker: "mason",
			text: "I already caught a CryMon. Fight me."
		}
	],
	masonAfter: [{
		speaker: "mason",
		text: "Fine. Calder is still south."
	}, {
		speaker: "max",
		text: "I won't die first."
	}],
	masonWin: [{
		speaker: "none",
		text: "Mason spits in the dirt. The path is yours. Calder still waits south."
	}],
	wrenFirst: [
		{
			speaker: "wren",
			text: "Too young. Take the salve. Calder camps south."
		},
		{
			speaker: "max",
			text: "I'm not too young."
		},
		{
			speaker: "wren",
			text: "West is Ivo. East is Nell. Keep that hound fed."
		}
	],
	wrenBeat: [{
		speaker: "wren",
		text: "You beat him. The war still wants more of us."
	}, {
		speaker: "max",
		text: "Then it can wait."
	}],
	wrenCart: [{
		speaker: "wren",
		text: "You found their letter. They already knew your name."
	}, {
		speaker: "max",
		text: "I read it anyway."
	}],
	wrenHeal: [{
		speaker: "wren",
		text: "Cuts bound. Specials return. Keep them fed."
	}, {
		speaker: "max",
		text: "Thank you."
	}],
	ivoFirst: [
		{
			speaker: "ivo",
			text: "Camp took my CryMon. Chew this. Calder sits south."
		},
		{
			speaker: "max",
			text: "I'm going south anyway."
		},
		{
			speaker: "ivo",
			text: "Don't give him a clean fight."
		}
	],
	ivoAgain: [{
		speaker: "ivo",
		text: "Hit first. Run if the bat folds you."
	}, {
		speaker: "max",
		text: "I don't run yet."
	}],
	nellFirst: [{
		speaker: "nell",
		text: "Too young. Drink this anyway. Reeds hide a stone."
	}, {
		speaker: "max",
		text: "I can hold a crystal."
	}],
	nellBonus: [{
		speaker: "nell",
		text: "That moth wasn't yours yesterday. Another salve."
	}, {
		speaker: "max",
		text: "I caught it fair."
	}],
	nellAgain: [{
		speaker: "nell",
		text: "The pond keeps secrets. South still drums."
	}, {
		speaker: "max",
		text: "I hear them."
	}],
	pikeFirst: [{
		speaker: "pike",
		text: "I dropped a moonstone in the east reeds. Don't tell Wren."
	}, {
		speaker: "max",
		text: "I won't tell Wren."
	}],
	pikeHelp: [{
		speaker: "pike",
		text: "You found it? Keep the stone. Take this wrap."
	}, {
		speaker: "max",
		text: "I was only looking."
	}],
	pikeDone: [{
		speaker: "pike",
		text: "The cliffs are just rocks. The war is the scary part."
	}, {
		speaker: "max",
		text: "I know."
	}],
	pikeHint: [{
		speaker: "pike",
		text: "East of the path. In the tall grass by the water."
	}],
	herb: [{
		speaker: "max",
		text: "Bitterroot. STR +4 if I last."
	}],
	herbGone: [{
		speaker: "max",
		text: "A hole where the herb was. Only grit."
	}],
	gemPike: [{
		speaker: "max",
		text: "Pike's moonstone. He said keep it."
	}],
	gemWild: [{
		speaker: "max",
		text: "A Capture Crystal. Someone small lost this."
	}],
	gemGone: [{
		speaker: "max",
		text: "Mud and a frog. The stone is already mine."
	}],
	stump: [{
		speaker: "max",
		text: "A wrap jammed in the stump. I take it."
	}],
	stumpGone: [{
		speaker: "max",
		text: "Just a stump. Ants. No more cloth."
	}],
	cart: [{
		speaker: "max",
		text: "They already knew my name."
	}, {
		speaker: "none",
		text: "A camp letter on the wreck: send the cottage girl south. We need bodies."
	}],
	calderAfter: [{
		speaker: "calder",
		text: "South is the camp. Don't die stupid."
	}, {
		speaker: "max",
		text: "I don't plan to."
	}],
	calderFight: [{
		speaker: "calder",
		text: "The camp takes strays."
	}, {
		speaker: "max",
		text: "I'm not stray."
	}],
	forestEnter: [{
		speaker: "max",
		text: "The trees close over the path."
	}, {
		speaker: "none",
		text: "Tall grass. Patrols. If they see you, they will come."
	}],
	forestLeave: [{
		speaker: "max",
		text: "Back toward the cottage path."
	}],
	soldierSpot: [{
		speaker: "none",
		text: "A soldier sees you. \"You there! This wood is camp ground.\""
	}, {
		speaker: "max",
		text: "I'm passing through."
	}],
	soldierAfter: [{
		speaker: "none",
		text: "The soldier sits. \"Go. Before I change my mind.\""
	}],
	soldierDone: [{
		speaker: "none",
		text: "They already lost. They will not rise."
	}],
	bramOpen: [{
		speaker: "bram",
		text: "Marks for moss, wraps, stones. Buy or sell."
	}, {
		speaker: "max",
		text: "I have cuts. I need stones."
	}],
	anneGift: [
		{
			speaker: "anne",
			text: "Max. You actually fought."
		},
		{
			speaker: "anne",
			text: "Take these. Five crystals. Don't waste them on the first moth."
		},
		{
			speaker: "max",
			text: "I won't."
		},
		{
			speaker: "none",
			text: "Anne presses five Capture Crystals into Max's palm."
		}
	],
	anneAgain: [{
		speaker: "anne",
		text: "Don't lose those. Calder is still south."
	}, {
		speaker: "max",
		text: "I know the way."
	}],
	cottage: [{
		speaker: "max",
		text: "The cottage. Father in the bed. My bed. South door leaves."
	}],
	lose: [{
		speaker: "max",
		text: "We still breathe. Crawl back."
	}]
};
var GAME_KEYS = /* @__PURE__ */ new Set([
	"ArrowUp",
	"ArrowDown",
	"ArrowLeft",
	"ArrowRight",
	"KeyW",
	"KeyA",
	"KeyS",
	"KeyD",
	"KeyZ",
	"KeyX",
	"Space",
	"Enter",
	"Escape",
	"KeyC",
	"KeyQ",
	"Tab",
	"Backspace",
	"Digit1",
	"Digit2",
	"Digit3"
]);
var Input = class {
	keys = /* @__PURE__ */ new Set();
	injected = null;
	prev = /* @__PURE__ */ new Set();
	padX = 0;
	padY = 0;
	padA = false;
	padB = false;
	padStart = false;
	padSelect = false;
	tapA = false;
	tapB = false;
	tapStart = false;
	tapSelect = false;
	touchPad = {
		x: 0,
		y: 0
	};
	tapAQueued = false;
	tapBQueued = false;
	tapStartQueued = false;
	tapSelectQueued = false;
	used = /* @__PURE__ */ new Set();
	attach(el) {
		const down = (e) => {
			if (GAME_KEYS.has(e.code)) e.preventDefault();
			this.keys.add(e.code);
		};
		const up = (e) => this.keys.delete(e.code);
		const clear = () => this.keys.clear();
		window.addEventListener("keydown", down);
		window.addEventListener("keyup", up);
		window.addEventListener("blur", clear);
		document.addEventListener("visibilitychange", () => {
			if (document.hidden) clear();
		});
		el.style.touchAction = "none";
		return () => {
			window.removeEventListener("keydown", down);
			window.removeEventListener("keyup", up);
			window.removeEventListener("blur", clear);
		};
	}
	beginFrame() {
		this.used.clear();
		if (this.tapAQueued) {
			this.tapA = true;
			this.tapAQueued = false;
		} else this.tapA = false;
		if (this.tapBQueued) {
			this.tapB = true;
			this.tapBQueued = false;
		} else this.tapB = false;
		if (this.tapStartQueued) {
			this.tapStart = true;
			this.tapStartQueued = false;
		} else this.tapStart = false;
		if (this.tapSelectQueued) {
			this.tapSelect = true;
			this.tapSelectQueued = false;
		} else this.tapSelect = false;
	}
	endFrame() {
		this.prev = new Set(this.live());
	}
	live() {
		if (this.injected) return new Set(this.injected);
		return this.keys;
	}
	held(code) {
		return this.live().has(code);
	}
	pressed(code) {
		return this.live().has(code) && !this.prev.has(code);
	}
	axis() {
		let x = this.padX + this.touchPad.x;
		let y = this.padY + this.touchPad.y;
		if (this.held("KeyA") || this.held("ArrowLeft")) x -= 1;
		if (this.held("KeyD") || this.held("ArrowRight")) x += 1;
		if (this.held("KeyW") || this.held("ArrowUp")) y -= 1;
		if (this.held("KeyS") || this.held("ArrowDown")) y += 1;
		const m = Math.hypot(x, y);
		if (m > 1) {
			x /= m;
			y /= m;
		}
		return {
			x,
			y
		};
	}
	confirm() {
		if (this.used.has("_confirm")) return false;
		const v = this.pressed("KeyZ") || this.pressed("Space") || this.tapA;
		if (v) this.used.add("_confirm");
		return v;
	}
	cancel() {
		if (this.used.has("_cancel")) return false;
		const v = this.pressed("KeyX") || this.pressed("Escape") || this.pressed("KeyC") || this.tapB;
		if (v) this.used.add("_cancel");
		return v;
	}
	start() {
		if (this.used.has("_start")) return false;
		const v = this.pressed("Enter") || this.tapStart;
		if (v) this.used.add("_start");
		return v;
	}
	select() {
		if (this.used.has("_select")) return false;
		const v = this.pressed("KeyQ") || this.pressed("Tab") || this.pressed("Backspace") || this.tapSelect;
		if (v) this.used.add("_select");
		return v;
	}
	up() {
		return this.pressed("ArrowUp") || this.pressed("KeyW");
	}
	down() {
		return this.pressed("ArrowDown") || this.pressed("KeyS");
	}
	left() {
		return this.pressed("ArrowLeft") || this.pressed("KeyA");
	}
	right() {
		return this.pressed("ArrowRight") || this.pressed("KeyD");
	}
	queueA() {
		this.tapAQueued = true;
	}
	queueB() {
		this.tapBQueued = true;
	}
	queueStart() {
		this.tapStartQueued = true;
	}
	queueSelect() {
		this.tapSelectQueued = true;
	}
	setPad(x, y) {
		this.touchPad = {
			x,
			y
		};
	}
	pollGamepad() {
		const pads = navigator.getGamepads?.() ?? [];
		let any = false;
		let x = 0;
		let y = 0;
		for (const p of pads) {
			if (!p) continue;
			any = true;
			const ax = p.axes[0] ?? 0;
			const ay = p.axes[1] ?? 0;
			const m = Math.hypot(ax, ay);
			if (m > .18) {
				const s = (m - .18) / .82 / m;
				x += ax * s;
				y += ay * s;
			}
			if (p.buttons[12]?.pressed) y -= 1;
			if (p.buttons[13]?.pressed) y += 1;
			if (p.buttons[14]?.pressed) x -= 1;
			if (p.buttons[15]?.pressed) x += 1;
			const aBtn = Boolean(p.buttons[0]?.pressed);
			const bBtn = Boolean(p.buttons[1]?.pressed);
			const startBtn = Boolean(p.buttons[9]?.pressed);
			const selectBtn = Boolean(p.buttons[8]?.pressed);
			if (aBtn && !this.padA) this.tapAQueued = true;
			if (bBtn && !this.padB) this.tapBQueued = true;
			if (startBtn && !this.padStart) this.tapStartQueued = true;
			if (selectBtn && !this.padSelect) this.tapSelectQueued = true;
			this.padA = aBtn;
			this.padB = bBtn;
			this.padStart = startBtn;
			this.padSelect = selectBtn;
		}
		if (any) {
			this.padX = x;
			this.padY = y;
		}
	}
};
var STEP = 1 / 60;
function loadImg(src) {
	return new Promise((res, rej) => {
		const im = new Image();
		im.crossOrigin = "anonymous";
		im.onload = () => res(im);
		im.onerror = () => rej(new Error(src));
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
	const tx = Math.floor(x / 32);
	const row = map[Math.floor(y / 32)];
	if (!row || tx < 0 || tx >= row.length) return "#";
	return row[tx] ?? "#";
}
function X(n) {
	return Math.round(n * 640 / 240);
}
function Y(n) {
	return Math.round(n * 480 / 160);
}
var SPR_W = 48;
var SPR_H = 52;
var FONT = 16;
var Gemwar = class {
	canvas;
	ctx;
	input = new Input();
	audio = new Chip();
	images = {};
	ready = false;
	mode = "title";
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
	party = [];
	partyIndex = 0;
	bag = { ...START_BAG };
	battle = null;
	talkedFather = false;
	talkedWren = false;
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
	soldiers = [];
	pendingSoldier = null;
	battlesDone = 0;
	anneGifted = false;
	doorLock = 0;
	hudFlash = "";
	hudT = 0;
	talkLock = 0;
	lastTx = -1;
	lastTy = -1;
	unsub = null;
	raf = 0;
	constructor(canvas) {
		this.canvas = canvas;
		const ctx = canvas.getContext("2d");
		if (!ctx) throw new Error("canvas");
		this.ctx = ctx;
		canvas.width = 640;
		canvas.height = 480;
	}
	async boot() {
		this.reset();
		this.unsub = this.input.attach(this.canvas);
		this.wireProbe();
		this.ready = true;
		await this.loadArt();
	}
	async loadArt() {
		const loaded = await Promise.all([
			["bg", "/sprites/battle-bg.png"],
			["max-down-1", "/sprites/max/down-1.png?v=max4"],
			["max-down-2", "/sprites/max/down-2.png?v=max4"],
			["max-down-3", "/sprites/max/down-3.png?v=max4"],
			["max-down-4", "/sprites/max/down-4.png?v=max4"],
			["max-left-1", "/sprites/max/left-1.png?v=max4"],
			["max-left-2", "/sprites/max/left-2.png?v=max4"],
			["max-left-3", "/sprites/max/left-3.png?v=max4"],
			["max-left-4", "/sprites/max/left-4.png?v=max4"],
			["max-right-1", "/sprites/max/right-1.png?v=max4"],
			["max-right-2", "/sprites/max/right-2.png?v=max4"],
			["max-right-3", "/sprites/max/right-3.png?v=max4"],
			["max-right-4", "/sprites/max/right-4.png?v=max4"],
			["max-up-1", "/sprites/max/up-1.png?v=max4"],
			["max-up-2", "/sprites/max/up-2.png?v=max4"],
			["max-up-3", "/sprites/max/up-3.png?v=max4"],
			["max-up-4", "/sprites/max/up-4.png?v=max4"],
			["mason-down-1", "/sprites/mason/down-1.png?v=ow2"],
			["mason-down-2", "/sprites/mason/down-2.png?v=ow2"],
			["mason-down-3", "/sprites/mason/down-3.png?v=ow2"],
			["mason-down-4", "/sprites/mason/down-4.png?v=ow2"],
			["mason-left-1", "/sprites/mason/left-1.png?v=ow2"],
			["mason-left-2", "/sprites/mason/left-2.png?v=ow2"],
			["mason-left-3", "/sprites/mason/left-3.png?v=ow2"],
			["mason-left-4", "/sprites/mason/left-4.png?v=ow2"],
			["mason-right-1", "/sprites/mason/right-1.png?v=ow2"],
			["mason-right-2", "/sprites/mason/right-2.png?v=ow2"],
			["mason-right-3", "/sprites/mason/right-3.png?v=ow2"],
			["mason-right-4", "/sprites/mason/right-4.png?v=ow2"],
			["mason-up-1", "/sprites/mason/up-1.png?v=ow2"],
			["mason-up-2", "/sprites/mason/up-2.png?v=ow2"],
			["mason-up-3", "/sprites/mason/up-3.png?v=ow2"],
			["mason-up-4", "/sprites/mason/up-4.png?v=ow2"],
			["anne-down-1", "/sprites/anne/down-1.png?v=anne1"],
			["anne-down-2", "/sprites/anne/down-2.png?v=anne1"],
			["anne-down-3", "/sprites/anne/down-3.png?v=anne1"],
			["anne-down-4", "/sprites/anne/down-4.png?v=anne1"],
			["anne-left-1", "/sprites/anne/left-1.png?v=anne1"],
			["anne-left-2", "/sprites/anne/left-2.png?v=anne1"],
			["anne-left-3", "/sprites/anne/left-3.png?v=anne1"],
			["anne-left-4", "/sprites/anne/left-4.png?v=anne1"],
			["anne-right-1", "/sprites/anne/right-1.png?v=anne1"],
			["anne-right-2", "/sprites/anne/right-2.png?v=anne1"],
			["anne-right-3", "/sprites/anne/right-3.png?v=anne1"],
			["anne-right-4", "/sprites/anne/right-4.png?v=anne1"],
			["anne-up-1", "/sprites/anne/up-1.png?v=anne1"],
			["anne-up-2", "/sprites/anne/up-2.png?v=anne1"],
			["anne-up-3", "/sprites/anne/up-3.png?v=anne1"],
			["anne-up-4", "/sprites/anne/up-4.png?v=anne1"],
			["quillpup-1", "/sprites/monsters/quillpup/1.png"],
			["quillpup-2", "/sprites/monsters/quillpup/2.png"],
			["quillpup-3", "/sprites/monsters/quillpup/3.png"],
			["quillpup-4", "/sprites/monsters/quillpup/4.png"],
			["glimmoth-1", "/sprites/monsters/glimmoth/1.png"],
			["glimmoth-2", "/sprites/monsters/glimmoth/2.png"],
			["glimmoth-3", "/sprites/monsters/glimmoth/3.png"],
			["glimmoth-4", "/sprites/monsters/glimmoth/4.png"],
			["tortcask-1", "/sprites/monsters/tortcask/1.png"],
			["tortcask-2", "/sprites/monsters/tortcask/2.png"],
			["tortcask-3", "/sprites/monsters/tortcask/3.png"],
			["tortcask-4", "/sprites/monsters/tortcask/4.png"],
			["razorbat-1", "/sprites/monsters/razorbat/1.png"],
			["razorbat-2", "/sprites/monsters/razorbat/2.png"],
			["razorbat-3", "/sprites/monsters/razorbat/3.png"],
			["razorbat-4", "/sprites/monsters/razorbat/4.png"],
			["mossback-1", "/sprites/monsters/mossback/1.png?v=for1"],
			["mossback-2", "/sprites/monsters/mossback/2.png?v=for1"],
			["mossback-3", "/sprites/monsters/mossback/3.png?v=for1"],
			["mossback-4", "/sprites/monsters/mossback/4.png?v=for1"],
			["briarfox-1", "/sprites/monsters/briarfox/1.png?v=for1"],
			["briarfox-2", "/sprites/monsters/briarfox/2.png?v=for1"],
			["briarfox-3", "/sprites/monsters/briarfox/3.png?v=for1"],
			["briarfox-4", "/sprites/monsters/briarfox/4.png?v=for1"],
			["calder-1", "/sprites/npc/calder-1.png"],
			["calder-2", "/sprites/npc/calder-2.png"],
			["calder-3", "/sprites/npc/calder-3.png"],
			["calder-4", "/sprites/npc/calder-4.png"],
			["wren-1", "/sprites/npc/wren-1.png"],
			["wren-2", "/sprites/npc/wren-2.png"],
			["wren-3", "/sprites/npc/wren-3.png"],
			["wren-4", "/sprites/npc/wren-4.png"],
			["ivo-1", "/sprites/npc/ivo-1.png"],
			["ivo-2", "/sprites/npc/ivo-2.png"],
			["ivo-3", "/sprites/npc/ivo-3.png"],
			["ivo-4", "/sprites/npc/ivo-4.png"],
			["nell-1", "/sprites/npc/nell-1.png"],
			["nell-2", "/sprites/npc/nell-2.png"],
			["nell-3", "/sprites/npc/nell-3.png"],
			["nell-4", "/sprites/npc/nell-4.png"],
			["pike-1", "/sprites/npc/pike-1.png?v=ow2"],
			["pike-2", "/sprites/npc/pike-2.png?v=ow2"],
			["pike-3", "/sprites/npc/pike-3.png?v=ow2"],
			["pike-4", "/sprites/npc/pike-4.png?v=ow2"],
			["bram-1", "/sprites/npc/bram-1.png"],
			["bram-2", "/sprites/npc/bram-2.png"],
			["bram-3", "/sprites/npc/bram-3.png"],
			["bram-4", "/sprites/npc/bram-4.png"],
			["soldier-down-1", "/sprites/npc/soldier/down-1.png?v=for1"],
			["soldier-down-2", "/sprites/npc/soldier/down-2.png?v=for1"],
			["soldier-down-3", "/sprites/npc/soldier/down-3.png?v=for1"],
			["soldier-down-4", "/sprites/npc/soldier/down-4.png?v=for1"],
			["soldier-left-1", "/sprites/npc/soldier/left-1.png?v=for1"],
			["soldier-left-2", "/sprites/npc/soldier/left-2.png?v=for1"],
			["soldier-left-3", "/sprites/npc/soldier/left-3.png?v=for1"],
			["soldier-left-4", "/sprites/npc/soldier/left-4.png?v=for1"],
			["soldier-right-1", "/sprites/npc/soldier/right-1.png?v=for1"],
			["soldier-right-2", "/sprites/npc/soldier/right-2.png?v=for1"],
			["soldier-right-3", "/sprites/npc/soldier/right-3.png?v=for1"],
			["soldier-right-4", "/sprites/npc/soldier/right-4.png?v=for1"],
			["soldier-up-1", "/sprites/npc/soldier/up-1.png?v=for1"],
			["soldier-up-2", "/sprites/npc/soldier/up-2.png?v=for1"],
			["soldier-up-3", "/sprites/npc/soldier/up-3.png?v=for1"],
			["soldier-up-4", "/sprites/npc/soldier/up-4.png?v=for1"],
			["port-max", "/sprites/portraits/max.png?v=max4"],
			["port-anne", "/sprites/portraits/anne.png?v=anne2"],
			["port-mason", "/sprites/portraits/mason.png?v=port1"],
			["port-wren", "/sprites/portraits/wren.png?v=port1"],
			["port-ivo", "/sprites/portraits/ivo.png?v=port1"],
			["port-nell", "/sprites/portraits/nell.png?v=port1"],
			["port-pike", "/sprites/portraits/pike.png?v=port1"],
			["port-calder", "/sprites/portraits/calder.png?v=port1"],
			["port-bram", "/sprites/portraits/bram.png?v=port1"],
			["port-quillpup", "/sprites/portraits/quillpup.png?v=port1"],
			["port-glimmoth", "/sprites/portraits/glimmoth.png?v=port1"],
			["port-tortcask", "/sprites/portraits/tortcask.png?v=port1"],
			["port-razorbat", "/sprites/portraits/razorbat.png?v=port1"],
			["port-mossback", "/sprites/portraits/mossback.png?v=for1"],
			["port-briarfox", "/sprites/portraits/briarfox.png?v=for1"],
			["item-gem", "/sprites/items/gem.png"],
			["item-salve", "/sprites/items/salve.png"],
			["item-bitterroot", "/sprites/items/bitterroot.png"],
			["item-dust", "/sprites/items/dust.png"],
			["item-bandage", "/sprites/items/bandage.png"],
			["prop-bed-father", "/sprites/props/bed-father.png?v=bed3"],
			["prop-bed-empty", "/sprites/props/bed-empty.png?v=bed3"],
			["prop-shelf", "/sprites/props/shelf.png"],
			["prop-crate", "/sprites/props/crate.png"],
			["prop-door", "/sprites/props/door.png"],
			["prop-herb", "/sprites/props/herb.png"],
			["prop-moonstone", "/sprites/props/moonstone.png"],
			["prop-stump", "/sprites/props/stump.png"],
			["prop-cart", "/sprites/props/cart.png"]
		].map(async ([k, u]) => {
			try {
				return [k, await loadImg(u)];
			} catch {
				return [k, null];
			}
		}));
		for (const [k, im] of loaded) if (im) this.images[k] = im;
	}
	reset() {
		this.mode = "title";
		this.introI = 0;
		this.endI = 0;
		this.party = [mintMonster("quillpup", 3)];
		this.partyIndex = 0;
		this.bag = { ...START_BAG };
		this.marks = 16;
		this.talkQ = [];
		this.talkI = 0;
		this.afterTalk = null;
		this.bagCursor = 0;
		this.partyCursor = 0;
		this.partyView = "list";
		this.actCursor = 0;
		this.pendingItem = null;
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
		this.talkedWren = false;
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
		this.talkLock = 0;
		this.lastTx = -1;
		this.lastTy = -1;
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
		if (mapId === "veld") {
			const s = spawnOf(VELD, "D");
			this.world.x = s.x;
			this.world.y = s.y + 32 + 8;
			this.world.dir = "down";
		} else if (mapId === "forest") {
			this.ensureSoldiers();
			const s = spawnOf(FOREST, "Y");
			this.world.x = s.x;
			this.world.y = s.y + 32 + 8;
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
		window.__gemwar = {
			getMode: () => this.mode,
			getPhase: () => this.battle?.phase ?? null,
			getMap: () => this.world.mapId,
			skipToWorld: () => this.skipToWorld("veld"),
			skipToHouse: () => this.skipToWorld("house"),
			skipToForest: () => this.skipToWorld("forest"),
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
				talkedWren: this.talkedWren,
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
				marks: this.marks
			}),
			forceWild: () => {
				this.skipToWorld("veld");
				this.startBattle(mintMonster("glimmoth", 2), true, "A wild Glimmoth");
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
			bag: () => this.bag
		};
	}
	map() {
		return MAPS[this.world.mapId];
	}
	note(s) {
		this.hudFlash = s;
		this.hudT = 12;
	}
	say(beats, after = null) {
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
			if (next === "shop") this.openShop();
			else if (next === "mason") {
				this.foughtMason = true;
				this.startBattle(mintMonster("glimmoth", 3), false, "Mason sends Glimmoth", "mason");
			} else if (next === "calder") this.startBattle(mintMonster("razorbat", 4), false, "Calder sends Razorbat", "calder");
			else if (next === "soldier") {
				const sol = this.soldiers.find((s) => s.id === this.pendingSoldier);
				if (sol && !sol.beaten) this.startBattle(mintMonster(sol.species, sol.level), false, `${sol.name} sends ${SPECIES[sol.species].name}`, "soldier", sol.id);
			}
			this.maybeStartAnne();
		}
	}
	ownedItems() {
		return ITEM_ORDER.filter((id) => this.bag[id] > 0);
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
	openShop() {
		this.mode = "shop";
		this.shopTab = "buy";
		this.shopCursor = 0;
		this.audio.ui();
	}
	closeMenu() {
		this.mode = "world";
		this.pendingItem = null;
		this.partyView = "list";
		this.audio.ui();
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
	maybeStartAnne() {
		if (this.anneGifted || this.anne.phase !== "off") return;
		if (this.battlesDone < 1) return;
		if (this.talking() || this.hudT > 0) return;
		if (this.world.mapId !== "veld") return;
		this.anne = {
			phase: "approach",
			x: this.world.x,
			y: this.world.y + 72,
			dir: "up",
			frame: 0,
			anim: 0
		};
	}
	onBattleOver() {
		this.battlesDone += 1;
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
		if (this.shake > 0) this.shake = Math.max(0, this.shake - dt * 8);
		if (this.hudT > 0) this.hudT -= dt;
		if (this.mode === "title") {
			if (this.input.confirm() || this.input.start()) {
				this.audio.ok();
				this.mode = "intro";
				this.introI = 0;
			}
			return;
		}
		if (this.mode === "intro") {
			if (this.input.confirm()) {
				this.audio.ui();
				this.introI += 1;
				if (this.introI >= INTRO.length) {
					this.mode = "world";
					this.note("Face the beds, the shelf, or the crate and press Z. Walk south through the door.");
				}
			}
			return;
		}
		if (this.mode === "ending") {
			if (this.input.confirm()) {
				this.audio.ui();
				this.endI += 1;
				if (this.endI >= ENDING_WIN.length) {
					this.mode = "world";
					this.note("The camp takes strays. South still drums.");
				}
			}
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
		if (this.mode === "world") {
			if (!this.talking() && this.rival.phase !== "approach" && this.anne.phase !== "approach" && this.hudT <= 0) {
				if (this.input.start()) {
					this.openParty();
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
		if (this.partyView === "act") {
			const acts = [
				"Send out",
				"Stats",
				"Moves"
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
				} else {
					this.partyView = "moves";
					this.audio.ui();
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
		const rows = this.shopTab === "buy" ? ITEM_ORDER : this.ownedItems();
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
		if (this.talkLock > 0) this.talkLock = Math.max(0, this.talkLock - dt);
		if (this.doorLock > 0) this.doorLock -= dt;
		if (!this.talking() && this.hudT <= 0) this.maybeStartAnne();
		if (this.rival.phase === "approach") {
			this.world.moving = false;
			this.world.frame = 0;
			const dx = this.world.x - this.rival.x;
			const dy = this.world.y - this.rival.y;
			const dist = Math.hypot(dx, dy);
			if (dist < 36) {
				this.rival.phase = "talk";
				this.rival.frame = 0;
				this.say(TALK.masonFight, "mason");
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
		if (this.anne.phase === "approach") {
			this.world.moving = false;
			this.world.frame = 0;
			const dx = this.world.x - this.anne.x;
			const dy = this.world.y - this.anne.y;
			const dist = Math.hypot(dx, dy);
			if (dist < 36) {
				this.anne.phase = "done";
				this.anne.frame = 0;
				this.anneGifted = true;
				this.bag.gem += 5;
				this.say(TALK.anneGift);
				this.audio.ok();
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
			const mw = (map[0]?.length ?? 1) * 32;
			const mh = map.length * 32;
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
		].some(([px, py]) => solidTile(tileAt(this.map(), px, py)))) return true;
		if (this.world.mapId === "forest") for (const sol of this.soldiers) {
			if (sol.beaten || sol.chase) continue;
			if (Math.abs(sol.x - x) < 16 && Math.abs(sol.y - y) < 16) return true;
		}
		return false;
	}
	tryEncounter() {
		const tx = Math.floor(this.world.x / 32);
		const ty = Math.floor(this.world.y / 32);
		if (tx === this.lastTx && ty === this.lastTy) return;
		this.lastTx = tx;
		this.lastTy = ty;
		if (tileAt(this.map(), this.world.x, this.world.y) !== "T") return;
		if (this.world.encounterLock > 0) {
			this.world.encounterLock -= 1;
			return;
		}
		if (Math.random() > .18) return;
		this.world.encounterLock = 3;
		let id;
		let lv;
		if (this.world.mapId === "forest") {
			id = Math.random() < .5 ? "mossback" : "briarfox";
			lv = 3 + randI(0, 2);
		} else {
			if (tx < 12) id = "glimmoth";
			else if (tx > 18) id = "tortcask";
			else id = Math.random() < .5 ? "glimmoth" : "tortcask";
			lv = 2 + (ty > 14 ? 1 : 0) + randI(0, 1);
		}
		this.startBattle(mintMonster(id, lv), true, `A wild ${SPECIES[id].name}`);
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
		if (doorTile(here) || this.world.moving && doorTile(ahead)) this.useDoor();
	}
	nearbyTiles() {
		const { x, y } = this.world;
		const d = 32;
		return [
			tileAt(this.map(), x, y),
			tileAt(this.map(), x - d, y),
			tileAt(this.map(), x + d, y),
			tileAt(this.map(), x, y - d),
			tileAt(this.map(), x, y + d)
		];
	}
	useDoor() {
		this.audio.ui();
		this.doorLock = .5;
		if (this.world.mapId === "house") {
			const s = spawnOf(VELD, "D");
			this.world.mapId = "veld";
			this.world.x = s.x;
			this.world.y = s.y + 32 + 12;
			this.world.dir = "down";
			this.world.encounterLock = 3;
			this.lastTx = -1;
			this.lastTy = -1;
			if (this.party.length >= 1 && this.rival.phase === "off") {
				this.rival = {
					phase: "approach",
					x: this.world.x,
					y: this.world.y + 160,
					dir: "up",
					frame: 0,
					anim: 0
				};
				this.say(TALK.footsteps);
			} else this.say(TALK.doorOut);
		} else {
			const s = spawnOf(HOUSE, "D");
			this.world.mapId = "house";
			this.world.x = s.x;
			this.world.y = s.y - 32;
			this.world.dir = "up";
			this.lastTx = -1;
			this.lastTy = -1;
			this.say(TALK.cottage);
		}
		this.maybeStartAnne();
	}
	interact() {
		if (this.nearbyTiles().some((ch) => doorTile(ch))) {
			this.useDoor();
			return;
		}
		if (this.world.mapId === "house") {
			const hit = this.closestMark(HOUSE, [
				"U",
				"B",
				"S",
				"C"
			]);
			if (hit === "U") {
				this.sleepHeal();
				this.say(TALK.bed);
				this.audio.ok();
				return;
			}
			if (hit === "B") {
				this.talkedFather = true;
				this.say(TALK.father);
				return;
			}
			if (hit === "S") {
				this.say(TALK.shelf);
				return;
			}
			if (hit === "C") {
				if (!this.lootedCrate) {
					this.lootedCrate = true;
					this.bag.bandage += 1;
					this.say(TALK.crate);
					this.audio.ok();
				} else this.say(TALK.crateEmpty);
				return;
			}
		}
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
			return;
		}
		if (this.world.mapId !== "veld") return;
		if (this.anne.phase === "done") {
			const dx = this.anne.x - this.world.x;
			const dy = this.anne.y - this.world.y;
			if (dx * dx + dy * dy <= 676) {
				this.say(TALK.anneAgain);
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
		const mark = this.closestVeldMark([
			"K",
			"V",
			"A",
			"Q",
			"M",
			"G",
			"L",
			"X",
			"E",
			"N",
			"J"
		]);
		if (!mark) return;
		if (mark === "J") {
			this.say(TALK.bramOpen, "shop");
			return;
		}
		if (mark === "K") {
			if (!this.talkedWren) {
				this.talkedWren = true;
				this.bag.salve += 1;
				this.say(TALK.wrenFirst);
				this.audio.ok();
			} else if (this.beatCalder) this.say(TALK.wrenBeat);
			else if (this.readCart) this.say(TALK.wrenCart);
			else {
				this.sleepHeal();
				this.say(TALK.wrenHeal);
				this.audio.ok();
			}
			return;
		}
		if (mark === "V") {
			if (!this.talkedIvo) {
				this.talkedIvo = true;
				this.bag.bitterroot += 1;
				this.say(TALK.ivoFirst);
				this.audio.ok();
			} else this.say(TALK.ivoAgain);
			return;
		}
		if (mark === "A") {
			if (!this.talkedNell) {
				this.talkedNell = true;
				this.bag.salve += 1;
				this.say(TALK.nellFirst);
				this.audio.ok();
			} else if (this.party.length > 1 && !this.nellBonus) {
				this.nellBonus = true;
				this.bag.salve += 1;
				this.say(TALK.nellBonus);
				this.audio.ok();
			} else this.say(TALK.nellAgain);
			return;
		}
		if (mark === "Q") {
			if (this.gotFieldGem && !this.pikeHelped) {
				this.pikeHelped = true;
				this.bag.bandage += 1;
				this.say(TALK.pikeHelp);
				this.audio.ok();
			} else if (!this.talkedPike) {
				this.talkedPike = true;
				this.say(TALK.pikeFirst);
			} else if (this.pikeHelped) this.say(TALK.pikeDone);
			else this.say(TALK.pikeHint);
			return;
		}
		if (mark === "M") {
			if (!this.gotHerb) {
				this.gotHerb = true;
				this.bag.bitterroot += 1;
				this.say(TALK.herb);
				this.audio.ok();
			} else this.say(TALK.herbGone);
			return;
		}
		if (mark === "G") {
			if (!this.gotFieldGem) {
				this.gotFieldGem = true;
				this.bag.gem += 1;
				this.say(this.talkedPike ? TALK.gemPike : TALK.gemWild);
				this.audio.ok();
			} else this.say(TALK.gemGone);
			return;
		}
		if (mark === "L") {
			if (!this.gotStump) {
				this.gotStump = true;
				this.bag.bandage += 1;
				this.say(TALK.stump);
				this.audio.ok();
			} else this.say(TALK.stumpGone);
			return;
		}
		if (mark === "X") {
			this.readCart = true;
			this.say(TALK.cart);
			return;
		}
		if (mark === "E" || mark === "N") {
			if (this.beatCalder) {
				this.say(TALK.calderAfter);
				return;
			}
			this.say(TALK.calderFight, "calder");
		}
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
		const stx = Math.floor(sol.x / 32);
		const sty = Math.floor(sol.y / 32);
		const ptx = Math.floor(this.world.x / 32);
		const pty = Math.floor(this.world.y / 32);
		const dx = sol.dir === "left" ? -1 : sol.dir === "right" ? 1 : 0;
		const dy = sol.dir === "up" ? -1 : sol.dir === "down" ? 1 : 0;
		const map = this.map();
		for (let i = 1; i <= 7; i++) {
			const tx = stx + dx * i;
			const ty = sty + dy * i;
			const row = map[ty];
			if (!row || tx < 0 || tx >= row.length) return false;
			if (solidTile(row[tx] ?? "#")) return false;
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
		if (this.world.mapId === "veld" && ch === "Z") {
			this.audio.ui();
			this.doorLock = .5;
			this.ensureSoldiers();
			const s = spawnOf(FOREST, "Y");
			this.world.mapId = "forest";
			this.world.x = s.x;
			this.world.y = s.y + 32 + 8;
			this.world.dir = "down";
			this.world.encounterLock = 3;
			this.lastTx = -1;
			this.lastTy = -1;
			this.say(TALK.forestEnter);
			return;
		}
		if (this.world.mapId === "forest" && ch === "Y") {
			this.audio.ui();
			this.doorLock = .5;
			const s = spawnOf(VELD, "Z");
			this.world.mapId = "veld";
			this.world.x = s.x;
			this.world.y = s.y - 32;
			this.world.dir = "up";
			this.world.encounterLock = 3;
			this.lastTx = -1;
			this.lastTy = -1;
			this.say(TALK.forestLeave);
		}
	}
	startBattle(foe, wild, title, trainer = wild ? "wild" : "calder", soldierId = null) {
		const player = { ...this.lead() };
		const soldierName = soldierId ? this.soldiers.find((s) => s.id === soldierId)?.name ?? "Soldier" : "Soldier";
		this.battle = {
			wild,
			trainer,
			foeName: wild ? foe.name : trainer === "mason" ? "Mason" : trainer === "soldier" ? soldierName : "Calder",
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
				foeStr: 0,
				foeAgl: 0,
				foeSpc: 0
			},
			catchUsed: false,
			t: 0
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
			if (this.bag[id] > 0) rows.push(this.itemBattleLabel(id));
		});
		return rows;
	}
	itemBattleLabel(id) {
		const n = this.bag[id];
		if (id === "bitterroot") return `Bitterroot +4 STR x${n}`;
		if (id === "dust") return `Ash dust -3/-2/-2 x${n}`;
		if (id === "salve") return `Moss salve +22 HP x${n}`;
		if (id === "bandage") return `Linen wrap +12 HP x${n}`;
		return `${ITEMS[id].name} x${n}`;
	}
	attackMenu(p) {
		const s = SPECIES[p.species];
		return [
			`${s.basic}`,
			`${s.special}  ${p.specialPp}/${p.specialPpMax}`,
			"Wait"
		];
	}
	updateBattle(dt) {
		const b = this.battle;
		b.t += dt;
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
						const m = this.lead();
						m.hp = Math.max(1, Math.floor(m.maxHp * .4));
						this.world.encounterLock = 3;
						this.onBattleOver();
						this.say(TALK.lose);
						return;
					}
					if (b.afterMsg === "end_catch") {
						this.leaveBattle();
						this.onBattleOver();
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
			b.foe.hp = Math.max(0, b.foe.hp - b.pendingDmg);
			this.shake = .25;
			this.audio.hit();
			const lines = [`${b.pendingLabel}  ${b.pendingDmg} dmg.`];
			if (b.foe.hp <= 0) {
				b.msg = [...lines, `${b.foe.name} falls.`];
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
			const g = b.guard ?? "block";
			const foeS = SPECIES[b.foe.species];
			const useSpecial = b.foe.specialPp > 0 && Math.random() < .28;
			if (useSpecial) b.foe.specialPp -= 1;
			const atkStat = useSpecial ? b.foe.spc + b.mods.foeSpc : b.foe.str + b.mods.foeStr;
			const chance = clamp(50 + ((g === "dodge" ? b.player.agl : g === "block" ? b.player.str + b.mods.selfStr : b.player.spc) - atkStat) * 5 + randI(-10, 10), 12, 88);
			const success = randI(1, 100) <= chance;
			const base = useSpecial ? 10 + (b.foe.spc + b.mods.foeSpc) * .7 - b.player.spc * .12 : 6 + (b.foe.str + b.mods.foeStr) * .6 - (b.player.str + b.mods.selfStr) * .15;
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
			b.msg = [`${b.foe.name} uses ${useSpecial ? foeS.special : foeS.basic}.`, line];
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
		this.bag[id] -= 1;
		if (id === "salve") {
			const n = Math.min(22, b.player.maxHp - b.player.hp);
			b.player.hp += n;
			b.msg = [`Moss salve. ${n} HP.`];
		} else if (id === "bandage") {
			const n = Math.min(12, b.player.maxHp - b.player.hp);
			b.player.hp += n;
			b.msg = [`Linen wrap. ${n} HP.`];
		} else if (id === "bitterroot") {
			b.mods.selfStr += 4;
			b.msg = ["Bitterroot. STR +4 this fight."];
		} else if (id === "dust") {
			b.mods.foeStr -= 3;
			b.mods.foeAgl -= 2;
			b.mods.foeSpc -= 2;
			b.msg = ["Ash dust. Foe STR-3 AGI-2 SPC-2."];
		} else if (id === "gem") {
			if (!b.wild) {
				this.bag.gem += 1;
				b.msg = ["Crystals will not take a tamer's CryMon."];
			} else {
				const chance = clamp(48 + (1 - b.foe.hp / b.foe.maxHp) * 42, 18, 92);
				if (randI(1, 100) <= chance && this.party.length < 3) {
					this.party.push({
						...b.foe,
						hp: Math.max(1, Math.floor(b.foe.maxHp * .4))
					});
					this.caughtOnce = true;
					b.msg = [`The crystal takes. ${b.foe.name} is yours.`];
					b.msgI = 0;
					b.phase = "msg";
					b.afterMsg = "end_catch";
					this.audio.catch();
					return;
				}
				if (this.party.length >= 3) {
					this.bag.gem += 1;
					b.msg = ["Three is all Max can hold."];
				} else b.msg = ["The crystal cracks dark. It slips free."];
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
		if (i === 2) {
			b.msg = ["Max holds."];
			b.msgI = 0;
			b.phase = "msg";
			b.afterMsg = "guard";
			this.audio.ui();
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
		const grew = grantXp(m, b.foe.level);
		if (!b.wild) {
			if (b.trainer === "calder") {
				this.beatCalder = true;
				this.marks += 18;
				this.mode = "ending";
				this.endI = 0;
				this.battle = null;
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
			this.foughtMason = true;
			this.rival.phase = "done";
			this.marks += 10;
			this.mode = "world";
			this.battle = null;
			this.world.encounterLock = 3;
			this.onBattleOver();
			this.say(TALK.masonWin);
			this.audio.ok();
			return;
		}
		this.marks += 3;
		this.mode = "world";
		this.battle = null;
		this.world.encounterLock = 3;
		this.onBattleOver();
		this.note(grew ? `${m.name} grew to lv ${m.level}.` : `${m.name} stands over the grass.`);
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
		else this.drawWorld();
		ctx.restore();
	}
	fill(c) {
		this.ctx.fillStyle = c;
		this.ctx.fillRect(0, 0, 640, 480);
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
		const mw = (map[0]?.length ?? 1) * 32;
		const mh = map.length * 32;
		this.fill(map === HOUSE ? "#1a1410" : map === FOREST ? "#121810" : "#1c2418");
		const x0 = Math.max(0, Math.floor(camx / 32) - 1);
		const y0 = Math.max(0, Math.floor(camy / 32) - 1);
		const x1 = Math.min(mw / 32, Math.ceil((camx + 640) / 32) + 1);
		const y1 = Math.min(mh / 32, Math.ceil((camy + 480) / 32) + 1);
		for (let y = y0; y < y1; y++) {
			const row = map[y];
			if (!row) continue;
			for (let x = x0; x < x1; x++) {
				const ch = row[x];
				if (!ch) continue;
				this.paintTile(ch, x * 32 - camx, y * 32 - camy);
			}
		}
	}
	drawTitle() {
		this.drawMap(VELD, 256, 0);
		this.ctx.fillStyle = "rgba(18,17,14,0.28)";
		this.ctx.fillRect(0, 0, 640, 480);
		this.drawSprite("max-down-1", X(36), Y(88), SPR_W, SPR_H);
		this.drawSprite("quillpup-1", X(168), Y(64), X(96), Y(96), false);
		this.box(X(48), Y(36), X(144), Y(48));
		this.text("GEMWAR", X(120), Y(40), "#e8e4d8", 48, "center");
		this.text("MAX'S RUN", X(120), Y(64), "#c5cec6", 20, "center");
		this.box(X(40), Y(128), X(160), Y(24));
		this.text("Z / A  begin", X(120), Y(134), "#5a7a52", FONT, "center");
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
			this.drawMap(VELD, 448, 384);
			this.drawSprite("calder-1", X(160), Y(28), SPR_W, SPR_H);
			this.drawSprite("max-down-1", X(40), Y(72), SPR_W, SPR_H);
		}
		this.ctx.fillStyle = "rgba(18,17,14,0.2)";
		this.ctx.fillRect(0, 0, 640, 480);
		this.text(tag.toUpperCase(), X(12), Y(6), "#c5cec6", FONT);
		this.box(X(8), Y(112), X(224), Y(42));
		this.wrap(body, 42).slice(0, 3).forEach((ln, i) => this.text(ln, X(14), Y(118 + i * 10), "#e8e4d8", FONT));
	}
	cam() {
		const map = this.map();
		const mw = (map[0]?.length ?? 1) * 32;
		const mh = map.length * 32;
		let cx = this.world.x - 320;
		let cy = this.world.y - 240;
		cx = clamp(cx, 0, Math.max(0, mw - 640));
		cy = clamp(cy, 0, Math.max(0, mh - 480));
		return {
			cx,
			cy
		};
	}
	paintTile(ch, dx, dy) {
		const ctx = this.ctx;
		const t = 32;
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
		if (ch === "R") {
			fill("#6a4030");
			fill("#4a2a20", dx, dy + 7, t, 1);
			fill("#8a5040", dx + 3, dy + 3, 2, 2);
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
		if (ch === "=" || ch === "," || ch === "Z" || ch === "Y" || ch === "3") {
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
	drawSprite(key, x, y, w, h, feet = true) {
		const im = this.images[key];
		const ctx = this.ctx;
		ctx.imageSmoothingEnabled = false;
		if (!im || !im.width) {
			ctx.fillStyle = "#c5cec6";
			ctx.fillRect(x + 4, y + 4, w - 8, h - 6);
			return;
		}
		const ar = im.width / im.height;
		let dw = w;
		let dh = h;
		if (w / h > ar) dw = h * ar;
		else dh = w / ar;
		const dx = x + (w - dw) / 2;
		const dy = feet ? y + (h - dh) : y + (h - dh) / 2;
		ctx.drawImage(im, dx, dy, dw, dh);
	}
	drawActor(key, wx, wy) {
		const { cx, cy } = this.cam();
		this.drawSprite(key, wx - cx - SPR_W / 2, wy - cy - SPR_H + 4, SPR_W, SPR_H);
	}
	drawWorldHud() {
		const lead = this.lead();
		this.box(8, 8, 404, 40);
		this.text("MAX", 16, 12, "#e8e4d8", FONT);
		this.text(`Xtals ${this.bag.gem}`, 88, 12, "#c5cec6", FONT);
		this.text(`M ${this.marks}`, 250, 12, "#8f4a40", FONT);
		this.text(`${lead.name} Lv${lead.level}  ${lead.hp}/${lead.maxHp}`, 16, 28, "#8a8678", FONT);
	}
	drawProp(key, wx, wy, w, h) {
		const { cx, cy } = this.cam();
		this.drawSprite(key, wx - cx - w / 2, wy - cy - h + 6, w, h);
	}
	hintZ(wx, wy) {
		const { cx, cy } = this.cam();
		const dx = wx - this.world.x;
		const dy = wy - this.world.y;
		if (dx * dx + dy * dy > 2704) return;
		this.text("Z", wx - cx - 2, wy - cy - 22, "#e8e4d8", FONT);
	}
	drawWorld() {
		const { cx, cy } = this.cam();
		const map = this.map();
		this.fill(this.world.mapId === "house" ? "#1a1410" : this.world.mapId === "forest" ? "#121810" : "#1c2418");
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
			this.hintZ(bed.x, bed.y);
			this.hintZ(mine.x, mine.y);
			this.hintZ(shelf.x, shelf.y);
			this.hintZ(crate.x, crate.y);
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
			if (!this.beatCalder) {
				const e = spawnOf(VELD, "E");
				this.drawActor(`calder-${wf}`, e.x, e.y);
				this.hintZ(e.x, e.y);
			}
			if (this.rival.phase !== "off") {
				const rf = this.rival.phase === "approach" ? this.rival.frame % 4 + 1 : 1;
				this.drawActor(`mason-${this.rival.dir}-${rf}`, this.rival.x, this.rival.y);
				if (this.rival.phase === "done") this.hintZ(this.rival.x, this.rival.y);
			}
			if (this.anne.phase !== "off") {
				const af = this.anne.phase === "approach" ? this.anne.frame % 4 + 1 : 1;
				this.drawActor(`anne-${this.anne.dir}-${af}`, this.anne.x, this.anne.y);
				if (this.anne.phase === "done") this.hintZ(this.anne.x, this.anne.y);
			}
		}
		if (this.world.mapId === "forest") {
			this.ensureSoldiers();
			for (const sol of this.soldiers) {
				const sf = sol.beaten ? 1 : sol.frame % 4 + 1;
				this.drawActor(`soldier-${sol.dir}-${sf}`, sol.x, sol.y);
				this.hintZ(sol.x, sol.y);
			}
		}
		const frame = this.world.moving ? this.world.frame % 4 + 1 : 1;
		this.drawActor(`max-${this.world.dir}-${frame}`, this.world.x, this.world.y);
		if (this.talking()) {
			this.drawTalk();
			return;
		}
		this.drawWorldHud();
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
			this.ctx.fillStyle = "rgba(18,17,14,0.35)";
			this.ctx.fillRect(0, 0, 640, 480);
			this.drawSprite(`port-${beat.speaker}`, X(-4), Y(20), X(120), Y(150), true);
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
	drawBag() {
		this.drawWorld();
		this.ctx.fillStyle = "rgba(18,17,14,0.55)";
		this.ctx.fillRect(0, 0, 640, 480);
		this.box(X(10), Y(8), X(220), Y(144));
		this.text("BAG", X(18), Y(14), "#c5cec6", FONT);
		this.text(`Marks ${this.marks}`, X(150), Y(14), "#8f4a40", FONT);
		const items = this.ownedItems();
		if (items.length === 0) this.text("The pouch is empty.", X(18), Y(36), "#8a8678", FONT);
		else {
			items.forEach((id, i) => {
				const y = Y(32 + i * 18);
				const on = i === this.bagCursor;
				this.text(on ? ">" : " ", X(18), y, "#e8e4d8", FONT);
				this.drawSprite(`item-${id}`, X(30), y - 2, X(14), X(14), false);
				this.text(`${ITEMS[id].name}  x${this.bag[id]}`, X(48), y, on ? "#e8e4d8" : "#8a8678", FONT);
			});
			const cur = items[this.bagCursor];
			if (cur) {
				this.wrap(ITEMS[cur].desc, 40).slice(0, 1).forEach((ln) => this.text(ln, X(18), Y(124), "#8a8678", FONT));
				this.text(ITEMS[cur].field ? "Z use on a CryMon" : "Battle only", X(18), Y(136), "#5a7a52", FONT);
			}
		}
		if (this.hudT > 0) this.text(this.hudFlash.slice(0, 34), X(18), Y(148), "#e8e4d8", FONT);
	}
	drawParty() {
		this.drawWorld();
		this.ctx.fillStyle = "rgba(18,17,14,0.55)";
		this.ctx.fillRect(0, 0, 640, 480);
		this.box(X(8), Y(6), X(224), Y(148));
		const title = this.partyView === "target" ? `USE ${this.pendingItem ? ITEMS[this.pendingItem].name.toUpperCase() : "ITEM"}` : this.partyView === "stats" ? "STATS" : this.partyView === "moves" ? "MOVES" : "CRYMON";
		this.text(title, X(16), Y(10), "#c5cec6", FONT);
		if (this.partyView === "stats" || this.partyView === "moves") {
			const m = this.party[this.partyCursor] ?? this.lead();
			const s = SPECIES[m.species];
			this.drawSprite(`port-${m.species}`, X(12), Y(24), X(88), Y(110), true);
			this.text(m.name.toUpperCase(), X(108), Y(28), "#e8e4d8", FONT);
			this.text(`Lv${m.level}`, X(108), Y(40), "#8a8678", FONT);
			if (this.partyView === "stats") {
				this.text(`HP  ${m.hp}/${m.maxHp}`, X(108), Y(56), "#e8e4d8", FONT);
				this.hpBar(X(108), Y(68), X(100), m.hp, m.maxHp);
				this.text(`STR ${m.str}`, X(108), Y(80), "#c5cec6", FONT);
				this.text(`AGL ${m.agl}`, X(108), Y(92), "#c5cec6", FONT);
				this.text(`SPC ${m.spc}`, X(108), Y(104), "#c5cec6", FONT);
				this.text(`XP  ${m.xp}/${m.level * 10}`, X(108), Y(116), "#8a8678", FONT);
			} else {
				this.text("BASIC", X(108), Y(56), "#8a8678", FONT);
				this.text(s.basic, X(108), Y(68), "#e8e4d8", FONT);
				this.text("SPECIAL", X(108), Y(84), "#8a8678", FONT);
				this.text(`${s.special}  ${m.specialPp}/${m.specialPpMax}`, X(108), Y(96), "#e8e4d8", FONT);
				this.text(s.blurb.slice(0, 28), X(16), Y(140), "#8a8678", FONT);
			}
			this.text("Z / X  back", X(16), Y(148), "#5a7a52", FONT);
			return;
		}
		this.party.forEach((m, i) => {
			const y = Y(26 + i * 40);
			const on = i === this.partyCursor;
			if (on) {
				this.ctx.fillStyle = "rgba(143,74,64,0.28)";
				this.ctx.fillRect(X(14), y - 2, X(204), Y(38));
			}
			this.drawSprite(`port-${m.species}`, X(16), y - 2, X(36), X(36), false);
			const lead = i === this.partyIndex ? "LEAD" : "";
			this.text(`${on ? ">" : " "}${m.name}  Lv${m.level}`, X(56), y, on ? "#e8e4d8" : "#8a8678", FONT);
			this.text(`${m.hp}/${m.maxHp}  ${lead}`, X(56), y + Y(12), "#c5cec6", FONT);
			this.hpBar(X(56), y + Y(24), X(90), m.hp, m.maxHp);
		});
		if (this.partyView === "act") {
			const acts = [
				"Send out",
				"Stats",
				"Moves"
			];
			this.box(X(150), Y(70), X(78), Y(52));
			acts.forEach((a, i) => {
				this.text(i === this.actCursor ? `> ${a}` : `  ${a}`, X(156), Y(76 + i * 14), i === this.actCursor ? "#e8e4d8" : "#8a8678", FONT);
			});
		} else this.text(this.partyView === "target" ? "Z  use   X  bag" : "Z  choose   Start  close", X(16), Y(148), "#5a7a52", FONT);
		if (this.hudT > 0) this.text(this.hudFlash.slice(0, 34), X(16), Y(148), "#e8e4d8", FONT);
	}
	drawShop() {
		this.drawWorld();
		this.ctx.fillStyle = "rgba(18,17,14,0.55)";
		this.ctx.fillRect(0, 0, 640, 480);
		this.box(X(10), Y(8), X(220), Y(144));
		this.text("BRAM'S STALL", X(18), Y(14), "#c5cec6", FONT);
		this.text(`Marks ${this.marks}`, X(150), Y(14), "#8f4a40", FONT);
		this.text(this.shopTab === "buy" ? ">BUY   sell" : " buy   >SELL", X(18), Y(28), "#e8e4d8", FONT);
		const rows = this.shopTab === "buy" ? ITEM_ORDER : this.ownedItems();
		if (rows.length === 0) this.text("Nothing to sell.", X(18), Y(48), "#8a8678", FONT);
		else rows.forEach((id, i) => {
			const y = Y(44 + i * 16);
			const on = i === this.shopCursor;
			const price = this.shopTab === "buy" ? ITEMS[id].buy : ITEMS[id].sell;
			this.text(`${on ? ">" : " "}${ITEMS[id].name}  ${price}m  x${this.bag[id]}`, X(18), y, on ? "#e8e4d8" : "#8a8678", FONT);
		});
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
		if (bg) this.ctx.drawImage(bg, 0, 0, 640, 480);
		else this.fill("#2a2418");
		const pf = Math.floor(b.t * 4) % 4 + 1;
		this.drawSprite(`${b.foe.species}-${pf}`, X(168), Y(8), X(52), Y(52), false);
		this.drawSprite(`${b.player.species}-${pf}`, X(12), Y(52), X(48), Y(48), false);
		this.box(X(6), Y(6), X(124), Y(32));
		this.text(b.foe.name.toUpperCase(), X(10), Y(9), "#e8e4d8", FONT);
		this.hpBar(X(10), Y(22), X(96), b.foe.hp, b.foe.maxHp);
		this.text(`${b.foe.hp}`, X(110), Y(20), "#8a8678", FONT);
		this.box(X(108), Y(78), X(126), Y(28));
		this.text(`${b.player.name.toUpperCase()} Lv${b.player.level}`, X(112), Y(80), "#e8e4d8", FONT);
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
};
function RomFile({ href, filename, children, variant = "outline" }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("a", {
		className: cn(buttonVariants({
			variant,
			size: "sm"
		})),
		href,
		download: filename,
		rel: "noopener",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Download, { className: "size-4" }), children]
	});
}
function GemwarApp() {
	const ref = (0, import_react.useRef)(null);
	const gameRef = (0, import_react.useRef)(null);
	const [ready, setReady] = (0, import_react.useState)(false);
	const [muted, setMuted] = (0, import_react.useState)(false);
	const [pad, setPad] = (0, import_react.useState)({
		x: 0,
		y: 0
	});
	(0, import_react.useEffect)(() => {
		const canvas = ref.current;
		if (!canvas) return;
		const g = new Gemwar(canvas);
		gameRef.current = g;
		let live = true;
		g.boot().then(() => {
			if (!live) return;
			g.startLoop();
			setReady(true);
		}).catch(() => {
			if (!live) return;
			g.startLoop();
			setReady(true);
		});
		return () => {
			live = false;
			g.stop();
		};
	}, []);
	(0, import_react.useEffect)(() => {
		const g = gameRef.current;
		if (!g) return;
		g.audio.muted = muted;
	}, [muted]);
	(0, import_react.useEffect)(() => {
		gameRef.current?.input.setPad(pad.x, pad.y);
	}, [pad]);
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "min-h-dvh bg-bg text-fg",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("header", {
			className: "border-b border-border",
			children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "mx-auto flex max-w-5xl flex-wrap items-center justify-between gap-3 px-4 py-4 sm:px-6",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
					className: "text-xs uppercase tracking-[0.2em] text-muted",
					children: "480p homebrew"
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("h1", {
					className: "font-display text-2xl font-medium tracking-tight",
					children: "GEMWAR"
				})] }), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "flex flex-wrap items-center gap-2",
					children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Button, {
							size: "sm",
							variant: "ghost",
							onClick: () => setMuted((m) => !m),
							"aria-label": muted ? "Unmute" : "Mute",
							children: [muted ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)(VolumeX, { className: "size-4" }) : /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Volume2, { className: "size-4" }), muted ? "Muted" : "Sound"]
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)(RomFile, {
							href: "/rom/gemwar-ports.zip?v=pm3",
							filename: "gemwar-ports.zip",
							variant: "default",
							children: "Copy into Ports"
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)(RomFile, {
							href: "/rom/gemwar-480p.cdi?v=dc6",
							filename: "gemwar-480p.cdi",
							children: "480p disc"
						})
					]
				})]
			})
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("main", {
			className: "mx-auto grid max-w-5xl gap-6 px-4 py-6 sm:px-6 lg:grid-cols-[minmax(0,1fr)_220px]",
			children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", {
				className: "flex flex-col items-center gap-4",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "relative w-full max-w-[960px] overflow-hidden rounded-lg border border-border bg-inset p-2 shadow-panel",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("canvas", {
						ref,
						className: "mx-auto block h-auto w-full max-w-[960px] touch-none bg-bg",
						style: {
							imageRendering: "pixelated",
							aspectRatio: "640 / 480"
						},
						width: 640,
						height: 480
					}), !ready && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "absolute inset-0 grid place-items-center text-sm text-muted",
						children: "Loading cart…"
					})]
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "flex w-full max-w-[960px] items-end justify-between gap-3 overflow-x-hidden lg:hidden",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Dpad, { onPad: setPad }), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "grid grid-cols-2 gap-2 pb-2",
						children: [
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Face, {
								label: "B",
								onClick: () => gameRef.current?.input.queueB()
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Face, {
								label: "A",
								primary: true,
								onClick: () => gameRef.current?.input.queueA()
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Face, {
								label: "SEL",
								onClick: () => gameRef.current?.input.queueSelect()
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Face, {
								label: "S",
								onClick: () => gameRef.current?.input.queueStart()
							})
						]
					})]
				})]
			}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("aside", {
				className: "flex flex-col gap-4 text-sm leading-relaxed text-muted",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
						className: "font-display text-lg text-fg",
						children: "If Ports vanished on the R36S"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", { children: "The old zip had a game-list XML in it. Dumping the whole archive into ports can replace the Ports list. Deleting GEMWAR afterwards leaves that list empty, so the carousel hides Ports. The firmware is not bricked." }),
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("ol", {
						className: "list-decimal space-y-2 pl-5 text-fg",
						children: [
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("li", { children: "Power off. Take out the ROMs SD card and open it on a computer." }),
							/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("li", { children: [
								"Open the existing ",
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
									className: "text-muted",
									children: "ports"
								}),
								" folder (EASYROMS/ports or roms/ports)."
							] }),
							/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("li", { children: [
								"Delete ",
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
									className: "text-muted",
									children: "gamelist.xml"
								}),
								" and ",
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
									className: "text-muted",
									children: "gameinfo.xml"
								}),
								" ",
								"if they are there. Delete leftover GEMWAR.sh and the gemwar folder."
							] }),
							/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("li", { children: [
								"Do not delete the ",
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
									className: "text-muted",
									children: "PortMaster"
								}),
								" folder. If other ports still have their folders, leave those too."
							] }),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("li", { children: "On the device: Start → UI Settings → Visible Systems → turn Ports on (or Select All)." }),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("li", { children: "Start → Advanced Settings → Parse Gamelists Only → Off." }),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("li", { children: "Start → Game Settings → Update Gamelists. Then reboot." })
						]
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", { children: "If PortMaster itself is gone from Tools, run Options → Tools → Install PortMaster, then reboot." }),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
						className: "font-display text-lg text-fg",
						children: "Install GEMWAR after that"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", { children: [
						"Use ",
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
							className: "text-fg",
							children: "Copy into Ports"
						}),
						". Unzip, then copy only GEMWAR.sh and the gemwar folder into the existing ports folder. Do not replace the folder. Do not copy any XML."
					] }),
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", { children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("a", {
							className: "text-fg underline underline-offset-4 hover:text-accent",
							href: "/rom/gemwar-ports.zip?v=pm3",
							download: "gemwar-ports.zip",
							rel: "noopener",
							children: "gemwar-ports.zip"
						}),
						" — ",
						"launcher plus game folder only."
					] }),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
						className: "font-display text-lg text-fg",
						children: "How to play"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", { children: "Max walks out with Quillpup and no Capture Crystals. Anne presses five into her hand after the first fight. Tall grass hides wild CryMon. Tamers will not." }),
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("ul", {
						className: "space-y-2 text-fg",
						children: [
							/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("li", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
								className: "text-muted",
								children: "Move"
							}), " WASD / arrows"] }),
							/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("li", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
								className: "text-muted",
								children: "Talk / confirm"
							}), " Z Space · people, herbs, the wrecked cart"] }),
							/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("li", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
								className: "text-muted",
								children: "CryMon (Start)"
							}), " Enter · Start on a pad · S on touch — portraits, HP, send out, stats, moves"] }),
							/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("li", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
								className: "text-muted",
								children: "Bag (Select)"
							}), " Q Tab · Select on a pad · SEL on touch — use salves and wraps on a CryMon"] }),
							/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("li", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
								className: "text-muted",
								children: "Sleep"
							}), " Max's empty bed in the cottage restores every CryMon. Father's bed is the occupied one."] }),
							/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("li", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
								className: "text-muted",
								children: "Shop"
							}), " Bram on the dirt path — buy and sell for marks"] }),
							/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("li", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
								className: "text-muted",
								children: "Doors"
							}), " walk onto them — no button"] }),
							/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("li", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
								className: "text-muted",
								children: "Back / switch CryMon"
							}), " X C Esc · 1 2 3"] })
						]
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", { children: "In battle: items first, then a strike. Specials spend PP and open a timing bar. When the foe answers, dodge on agility, block on strength, or raise a barrier on special. Capture Crystals only take wild CryMon." }),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", { children: "Mason waits outside the cottage. Wren is west, Ivo in the grove, Nell by the pond. Bram keeps a stall on the path. Pike lost a crystal in the east reeds. Tall grass west hides Glimmoth; east hides Tortcask; south hits harder. Calder waits at the south tent." }),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "text-xs text-subtle",
						children: "Copy into Ports is only GEMWAR.sh and the gemwar folder. This screen is the same 640×480 game."
					})
				]
			})]
		})]
	});
}
function Dpad({ onPad }) {
	const hold = (x, y) => ({
		onPointerDown: (e) => {
			e.currentTarget.setPointerCapture(e.pointerId);
			onPad({
				x,
				y
			});
		},
		onPointerUp: () => onPad({
			x: 0,
			y: 0
		}),
		onPointerCancel: () => onPad({
			x: 0,
			y: 0
		})
	});
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "grid w-[132px] grid-cols-3 grid-rows-3 gap-1",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)(PadBtn, {
				...hold(0, -1),
				children: "↑"
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)(PadBtn, {
				...hold(-1, 0),
				children: "←"
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)(PadBtn, {
				...hold(1, 0),
				children: "→"
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)(PadBtn, {
				...hold(0, 1),
				children: "↓"
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {})
		]
	});
}
function PadBtn({ children, ...rest }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
		type: "button",
		className: "grid size-11 place-items-center rounded-md border border-border bg-raised text-sm text-fg active:bg-fg active:text-bg",
		...rest,
		children
	});
}
function Face({ label, onClick, primary }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
		type: "button",
		onClick,
		className: cn("min-h-11 min-w-12 rounded-md border px-3 py-2 text-xs font-medium", primary ? "border-fg bg-fg text-bg" : "border-border bg-raised text-fg"),
		children: label
	});
}
function Home() {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)(GemwarApp, {});
}
//#endregion
export { Home as component };
