/**
 * Battle particles, shock rings, screen flash and damage numbers.
 *
 * Everything here is driven by watching the battle state change (hp,
 * status, stat stages, which CryMon is out), not by hooks inside the
 * battle rules, so it cannot change an outcome. The Dreamcast does the
 * same thing in main.c (fx_watch / fx_draw) from the same numbers:
 * content/sprites.json `battleFx`, one style per crystal nature.
 *
 * Coordinates are the 240x160 logical space the battle layout uses;
 * draw() maps them to canvas pixels with the sx/sy it is given.
 */
import { SPRITES, SPECIES, NATURES, natureMatchup } from "./data";
import type { BattleState, Monster } from "./types";

type Side = "foe" | "player";
interface Style {
	colors: string[];
	shape: string;
	count: number;
	dir: "radial" | "up" | "down";
	speed: [number, number];
	gravity: number;
	drag: number;
	life: [number, number];
	size: [number, number];
	sway: number;
	ring: number;
}
interface Part {
	x: number; y: number; vx: number; vy: number;
	g: number; drag: number; t: number; life: number;
	size: number; sway: number; phase: number;
	shape: string; colors: string[];
}
interface Ring { x: number; y: number; t: number; col: string }
interface Pop { x: number; y: number; t: number; text: string; col: string }

const FX = (SPRITES as unknown as { battleFx: Record<string, any> }).battleFx;
const STYLES = FX.natures as Record<string, Style>;
const FALLBACK: Style = STYLES.quartz ?? Object.values(STYLES)[0];

/** Where each CryMon's middle sits in logical px (matches drawBattle()). */
export const FX_CENTER: Record<Side, [number, number]> = { foe: [194, 34], player: [36, 76] };

const rnd = (a: number, b: number) => a + Math.random() * (b - a);
const natOf = (m: Monster) => (SPECIES[m.species] as { nature?: string })?.nature ?? NATURES[0]?.id ?? "quartz";
const styleOf = (nat: string) => STYLES[nat] ?? FALLBACK;

interface Seen { ref: Monster | null; species: string; hp: number; status: string; stage: number }

export class BattleFx {
	parts: Part[] = [];
	rings: Ring[] = [];
	pops: Pop[] = [];
	flashT = 0;
	flashA = 0;
	flashCol = "#FFFFFF";
	/** Screen shake the engine should apply, in logical px. */
	shake = 0;
	private seen: Record<Side, Seen | null> = { foe: null, player: null };
	private battle: BattleState | null = null;

	reset() {
		this.parts = [];
		this.rings = [];
		this.pops = [];
		this.flashT = 0;
		this.shake = 0;
		this.seen = { foe: null, player: null };
	}

	/** Compare against last frame and fire whatever changed. */
	watch(b: BattleState) {
		if (b !== this.battle) {
			this.reset();
			this.battle = b;
		}
		this.watchSide(b, "foe", b.foe, b.player, b.stage.foeStr + b.stage.foeAgl + b.stage.foeSpc);
		this.watchSide(b, "player", b.player, b.foe, b.stage.selfStr + b.stage.selfAgl + b.stage.selfSpc);
	}

	private watchSide(_b: BattleState, side: Side, m: Monster, other: Monster, stage: number) {
		const prev = this.seen[side];
		const now: Seen = { ref: m, species: m.species, hp: m.hp, status: m.status ?? "none", stage };
		this.seen[side] = now;
		if (!prev) return;
		if (prev.species !== m.species || (prev.ref !== m && prev.hp <= 0)) {
			// A new CryMon came out: a small puff of its own crystal.
			this.emit(side, natOf(m), FX.enter?.countMul ?? 0.6, 1);
			return;
		}
		if (m.hp < prev.hp) {
			const dmg = prev.hp - m.hp;
			const sign = natureMatchup(other.species, m.species);
			this.hit(side, natOf(other), dmg, m.maxHp, sign);
			if (m.hp <= 0) this.faint(side, natOf(m));
		} else if (m.hp > prev.hp && prev.hp > 0) {
			this.heal(side, m.hp - prev.hp);
		}
		if (now.status !== prev.status && now.status !== "none") {
			this.emit(side, natOf(other), FX.status?.countMul ?? 0.5, 1);
			this.pop(side, now.status.slice(0, 3).toUpperCase(), FX.popup.weakColor);
		}
		if (stage > prev.stage) {
			this.emit(side, natOf(other), FX.status?.countMul ?? 0.5, 1);
			this.pop(side, "DOWN", FX.popup.weakColor);
		}
	}

	hit(side: Side, nat: string, dmg: number, maxHp: number, sign: number) {
		const big = maxHp > 0 && dmg / maxHp >= (FX.bigHit ?? 0.35);
		const frac = maxHp > 0 ? Math.min(1, dmg / maxHp) : 0.2;
		const st = styleOf(nat);
		this.emit(side, nat, big ? 1.5 : 1, 1);
		const sh = FX.shake;
		let amp = sh.min + (sh.max - sh.min) * frac;
		if (sign > 0) amp *= sh.superMul;
		this.shake = Math.max(this.shake, amp);
		const fl = FX.flash;
		const a = big ? fl.bigAlpha : sign > 0 ? fl.superAlpha : fl.hitAlpha;
		if (a >= this.flashA * Math.max(0, 1 - this.flashT / fl.sec)) {
			this.flashA = a;
			this.flashT = 0;
			this.flashCol = sign > 0 ? st.colors[0] : fl.color;
		}
		const pc = FX.popup;
		this.pop(side, `-${dmg}`, sign > 0 ? pc.superColor : sign < 0 ? pc.weakColor : pc.hitColor);
	}

	faint(side: Side, nat: string) {
		const f = FX.faint ?? {};
		this.emit(side, nat, f.countMul ?? 2, f.lifeMul ?? 1.5);
	}

	heal(side: Side, n: number) {
		const [cx, cy] = FX_CENTER[side];
		const col = FX.popup.healColor;
		for (let i = 0; i < 8; i++) {
			this.parts.push({
				x: cx + rnd(-14, 14), y: cy + rnd(-4, 14), vx: 0, vy: rnd(-40, -20), g: 0, drag: 1,
				t: 0, life: rnd(0.5, 0.8), size: 2, sway: 0, phase: 0, shape: "plus", colors: [col, col, col],
			});
		}
		this.pop(side, `+${n}`, col);
	}

	emit(side: Side, nat: string, countMul: number, lifeMul: number) {
		const st = styleOf(nat);
		const [cx, cy] = FX_CENTER[side];
		const n = Math.max(1, Math.round(st.count * countMul));
		for (let i = 0; i < n; i++) {
			let a: number;
			if (st.dir === "up") a = -Math.PI / 2 + rnd(-0.9, 0.9);
			else if (st.dir === "down") a = Math.PI / 2 + rnd(-0.9, 0.9);
			else a = (i / n) * Math.PI * 2 + rnd(-0.3, 0.3);
			const sp = rnd(st.speed[0], st.speed[1]);
			this.parts.push({
				x: cx + rnd(-4, 4), y: cy + rnd(-4, 4), vx: Math.cos(a) * sp, vy: Math.sin(a) * sp,
				g: st.gravity, drag: st.drag, t: 0, life: rnd(st.life[0], st.life[1]) * lifeMul,
				size: Math.round(rnd(st.size[0], st.size[1])), sway: st.sway, phase: rnd(0, 6.28),
				shape: st.shape, colors: st.colors,
			});
		}
		if (st.ring) this.rings.push({ x: cx, y: cy, t: 0, col: st.colors[1] ?? st.colors[0] });
	}

	pop(side: Side, text: string, col: string) {
		const [cx, cy] = FX_CENTER[side];
		const stack = this.pops.filter((p) => p.x === cx && p.t < 0.3).length;
		this.pops.push({ x: cx, y: cy - 24 - stack * 9, t: 0, text, col });
	}

	update(dt: number) {
		for (const p of this.parts) {
			p.t += dt;
			const k = Math.max(0, 1 - p.drag * dt);
			p.vx *= k;
			p.vy = p.vy * k + p.g * dt;
			p.x += p.vx * dt;
			p.y += p.vy * dt;
		}
		this.parts = this.parts.filter((p) => p.t < p.life);
		for (const r of this.rings) r.t += dt;
		this.rings = this.rings.filter((r) => r.t < 0.28);
		for (const p of this.pops) p.t += dt;
		this.pops = this.pops.filter((p) => p.t < FX.popup.sec);
		this.flashT += dt;
		this.shake = Math.max(0, this.shake - dt * 18);
	}

	get active() {
		return this.parts.length > 0 || this.rings.length > 0 || this.pops.length > 0;
	}

	/** Particles and rings (under the HUD boxes). */
	draw(ctx: CanvasRenderingContext2D, sx: number, sy: number) {
		for (const r of this.rings) {
			const k = r.t / 0.28;
			ctx.strokeStyle = r.col;
			ctx.lineWidth = Math.max(1, Math.round(sx * (2 - k * 1.5)));
			ctx.beginPath();
			ctx.ellipse(r.x * sx, r.y * sy, (6 + 24 * k) * sx, (6 + 24 * k) * sy * 0.8, 0, 0, Math.PI * 2);
			ctx.stroke();
		}
		for (const p of this.parts) {
			const u = p.t / p.life;
			if (u > 0.8 && Math.floor(p.t * 30) % 2) continue;   // blink out, no alpha
			const x = Math.round((p.x + (p.sway ? Math.sin(p.t * 9 + p.phase) * p.sway : 0)) * sx);
			const y = Math.round(p.y * sy);
			const s = Math.max(2, Math.round(p.size * sx));
			const c = p.colors;
			switch (p.shape) {
			case "spark": {
				ctx.strokeStyle = c[1] ?? c[0];
				ctx.lineWidth = Math.max(1, s * 0.6);
				ctx.beginPath();
				ctx.moveTo(x, y);
				ctx.lineTo(x - p.vx * 0.04 * sx, y - p.vy * 0.04 * sy);
				ctx.stroke();
				ctx.fillStyle = c[0];
				ctx.fillRect(x - s / 2, y - s / 2, s, s);
				break;
			}
			case "chunk":
				ctx.fillStyle = c[2] ?? c[0];
				ctx.fillRect(x - s / 2, y - s / 2 + 2, s, s);
				ctx.fillStyle = u < 0.5 ? c[1] ?? c[0] : c[0];
				ctx.fillRect(x - s / 2, y - s / 2, s, s);
				break;
			case "glint": {
				const on = Math.floor(p.t * 14 + p.phase) % 3 !== 0;
				ctx.fillStyle = on ? c[0] : c[1] ?? c[0];
				const arm = s * (on ? 1.6 : 1);
				ctx.fillRect(x - arm, y - 1, arm * 2, 3);
				ctx.fillRect(x - 1, y - arm, 3, arm * 2);
				break;
			}
			case "bolt": {
				ctx.strokeStyle = Math.floor(p.t * 30) % 2 ? c[0] : c[1] ?? c[0];
				ctx.lineWidth = Math.max(2, sx);
				const len = 0.05;
				const mx = x - p.vx * len * 0.5 * sx + p.vy * 0.015 * sx, my = y - p.vy * len * 0.5 * sy - p.vx * 0.015 * sy;
				ctx.beginPath();
				ctx.moveTo(x, y);
				ctx.lineTo(mx, my);
				ctx.lineTo(x - p.vx * len * sx, y - p.vy * len * sy);
				ctx.stroke();
				break;
			}
			case "wisp": {
				const r = s * (1 + u * 1.2);
				ctx.fillStyle = u < 0.5 ? c[1] ?? c[0] : c[0];
				ctx.beginPath();
				ctx.arc(x, y, r, 0, Math.PI * 2);
				ctx.fill();
				ctx.fillStyle = c[2] ?? c[0];
				ctx.fillRect(x - 1, y - r * 0.6, 2, 2);
				break;
			}
			case "rainbow":
				ctx.fillStyle = c[Math.floor(p.t * 20 + p.phase) % c.length];
				ctx.fillRect(x - s / 2, y - s / 2, s + 1, s + 1);
				break;
			case "leaf": {
				const tilt = Math.sin(p.t * 8 + p.phase);
				ctx.fillStyle = tilt > 0 ? c[0] : c[1] ?? c[0];
				ctx.beginPath();
				ctx.moveTo(x - s * 1.4 * tilt, y - s * 0.6);
				ctx.lineTo(x + s * 0.6, y);
				ctx.lineTo(x + s * 1.4 * tilt, y + s * 0.6);
				ctx.lineTo(x - s * 0.6, y);
				ctx.closePath();
				ctx.fill();
				break;
			}
			case "ember":
				ctx.fillStyle = u < 0.3 ? c[2] ?? c[0] : u < 0.65 ? c[1] ?? c[0] : c[0];
				ctx.fillRect(x - s / 2, y - s / 2, s, s);
				break;
			case "shard":
				ctx.fillStyle = c[0];
				ctx.beginPath();
				ctx.moveTo(x, y - s * 1.5);
				ctx.lineTo(x + s * 0.5, y);
				ctx.lineTo(x, y + s * 1.5);
				ctx.lineTo(x - s * 0.5, y);
				ctx.closePath();
				ctx.fill();
				ctx.fillStyle = c[2] ?? c[1] ?? c[0];
				ctx.fillRect(x - 1, y - s * 0.6, 2, s * 0.8);
				break;
			case "plus":
				ctx.fillStyle = c[0];
				ctx.fillRect(x - s, y - 1, s * 2, 3);
				ctx.fillRect(x - 1, y - s, 3, s * 2);
				break;
			default:
				ctx.fillStyle = c[0];
				ctx.fillRect(x - s / 2, y - s / 2, s, s);
			}
		}
	}

	/** Whole-screen flash and the damage numbers (over everything). */
	drawOver(ctx: CanvasRenderingContext2D, sx: number, sy: number, w: number, h: number,
		text: (s: string, x: number, y: number, col: string) => void) {
		// text() draws centred on x.
		const fl = FX.flash;
		if (this.flashT < fl.sec) {
			ctx.save();
			ctx.globalAlpha = this.flashA * (1 - this.flashT / fl.sec);
			ctx.fillStyle = this.flashCol;
			ctx.fillRect(0, 0, w, h);
			ctx.restore();
		}
		const pc = FX.popup;
		for (const p of this.pops) {
			const u = p.t / pc.sec;
			if (u > 0.75 && Math.floor(p.t * 20) % 2) continue;
			// Pop up fast, then drift: an ease-out on the rise.
			const rise = pc.rise * (1 - (1 - Math.min(1, u * 1.6)) ** 2);
			const x = Math.round(p.x * sx);
			const y = Math.round((p.y - rise) * sy);
			text(p.text, x + 3, y + 3, "#141018");
			text(p.text, x, y, p.col);
		}
	}
}
