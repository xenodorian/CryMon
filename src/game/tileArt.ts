/**
 * Painted overworld ground tiles (public/sprites/tiles, drawn by
 * tools/pixelforge/tiles.py). Engine.paintTile() calls paintTileArt() first;
 * when it returns false (a char this file does not cover, or the image has
 * not loaded yet) the engine's flat-colour tile runs as before.
 */
import { SPRITES, TILE_ART } from "./data";

/** Chars with their own look in Engine.paintTile(): never painted here. */
const OWN_LOOK = "HRr%gkFPDBUCN*X";
const DIRT = "=ZY3cO89Semq";

type Cat = "grass" | "tall" | "dirt" | "dirt2" | "tree" | "water" | "cliff" | null;

export function tileCat(ch: string | undefined): Cat {
	if (!ch) return null;
	if (ch === "T") return "tall";
	if (ch === "#") return "tree";
	if (ch === "W") return "water";
	if (ch === "^") return "cliff";
	if (ch === ",") return "dirt2";
	if (DIRT.includes(ch)) return "dirt";
	if (OWN_LOOK.includes(ch)) return null;
	if (TILE_ART[ch] === "tile-grass") return "grass";
	return null;
}

function hash(x: number, y: number) {
	let h = (x * 374761393 + y * 668265263) | 0;
	h = (h ^ (h >>> 13)) * 1274126177;
	return (h ^ (h >>> 16)) >>> 0;
}

/* Building and room tiles (tools/pixelforge/tiles_town.py), picked by the
 * map's theme in sprites.json tileTheme (default "town"). Indoor themes
 * repaint floors, walls and doors; outdoor themes repaint house walls,
 * roofs and doors. The Dreamcast draw_building_art() mirrors this. */
export type TileTheme = "town" | "wood" | "keep" | "crypt" | "palace" | "seph" | "hollow";
const INDOOR: Record<string, boolean> = { wood: true, keep: true, crypt: true, palace: true };
const DOORS = "Dbw()0";
const FLOORS = "FPBUCSastxz";
const TORCH_THEMES: Record<string, string> = { keep: "torch", crypt: "torch", palace: "torch", wood: "lantern" };

export function mapTheme(mapId: string): TileTheme {
	const t = (SPRITES as { tileTheme?: Record<string, string> }).tileTheme?.[mapId];
	return (t ?? "town") as TileTheme;
}

/** Wall lights drawn this frame (screen coords of the flame), for the glow pass. */
export const LIGHTS: { x: number; y: number; kind: string }[] = [];

function wallish(c: string | undefined) {
	return c === "H" || (c !== undefined && DOORS.includes(c));
}

function blit(ctx: CanvasRenderingContext2D, images: Record<string, HTMLImageElement>, key: string, dx: number, dy: number) {
	const im = images[key];
	if (!im || !im.width) return false;
	ctx.drawImage(im, dx, dy);
	return true;
}

function light(ctx: CanvasRenderingContext2D, images: Record<string, HTMLImageElement>, kind: string, dx: number, dy: number, h: number, now: number) {
	const f = (Math.floor(now / 120) + (h % 4)) % 4;
	if (blit(ctx, images, `fx-${kind}-${f + 1}`, dx, dy)) LIGHTS.push({ x: dx + 8, y: dy + (kind === "torch" ? 4 : 9), kind });
}

function paintBuilding(
	ctx: CanvasRenderingContext2D,
	images: Record<string, HTMLImageElement>,
	map: string[],
	ch: string,
	dx: number,
	dy: number,
	tx: number,
	ty: number,
	now: number,
	theme: TileTheme,
	mapId: string,
): boolean {
	const h = hash(tx, ty);
	const at = (x: number, y: number) => (y >= 0 && y < map.length && x >= 0 && x < map[y].length ? map[y][x] : undefined);
	if (ch === "%") return blit(ctx, images, "tile-bars", dx, dy);
	if (ch === "g") return blit(ctx, images, "tile-gate", dx, dy);
	if (ch === "*") return blit(ctx, images, `tile-flowers-${(h % 2) + 1}`, dx, dy);
	if (INDOOR[theme]) {
		if (FLOORS.includes(ch)) {
			if (!blit(ctx, images, `tile-floor-${theme}-${h % 4 === 0 ? 2 : 1}`, dx, dy)) return false;
			// the home map draws its own bed, shelf and crate props
			if (mapId !== "house" && ch === "C") blit(ctx, images, "tile-crate", dx, dy);
			if (mapId !== "house" && (ch === "B" || ch === "U")) blit(ctx, images, "tile-bed", dx, dy);
			return true;
		}
		if (DOORS.includes(ch)) return blit(ctx, images, `tile-door-${theme}`, dx, dy);
		if (ch === "H") {
			const below = at(tx, ty + 1);
			const face = below !== undefined && !wallish(below);
			if (!blit(ctx, images, face ? `tile-wallf-${theme}` : `tile-wall-${theme}`, dx, dy)) return false;
			if (face && (h >> 4) % (theme === "wood" ? 6 : 4) === 0) light(ctx, images, TORCH_THEMES[theme], dx + 8, dy + 6, h, now);
			return true;
		}
		return false;
	}
	if (ch === "H") {
		const win = (h >> 3) % 3 === 0 && !DOORS.includes(at(tx - 1, ty) ?? "") && !DOORS.includes(at(tx + 1, ty) ?? "");
		if (!blit(ctx, images, `tile-wallf-${theme}-${win ? 2 : 1}`, dx, dy)) return false;
		const l = at(tx - 1, ty), r = at(tx + 1, ty);
		if ((l && DOORS.includes(l)) || (r && DOORS.includes(r))) light(ctx, images, "lantern", dx + 8, dy + 5, h, now);
		return true;
	}
	if (ch === "r" || ch === "R") {
		const above = at(tx, ty - 1);
		const top = ch === "R" || (above !== "r" && above !== "R");
		return blit(ctx, images, top ? `tile-ridge-${theme}` : `tile-roof-${theme}-${h % 5 === 0 ? 2 : 1}`, dx, dy);
	}
	if (DOORS.includes(ch)) return blit(ctx, images, `tile-door-${theme}`, dx, dy);
	return false;
}

const NB: [string, number, number][] = [["n", 0, -1], ["e", 1, 0], ["s", 0, 1], ["w", -1, 0]];

export function paintTileArt(
	ctx: CanvasRenderingContext2D,
	images: Record<string, HTMLImageElement>,
	map: string[] | null,
	ch: string,
	dx: number,
	dy: number,
	tx: number,
	ty: number,
	now: number,
	mapId = "",
): boolean {
	let hollow = false;
	if (map) {
		const theme = mapTheme(mapId);
		hollow = theme === "hollow";
		if (paintBuilding(ctx, images, map, ch, dx, dy, tx, ty, now, theme, mapId)) return true;
		// outdoors, F and P are packed-earth yards and warp marks; C and X
		// are prop spots (chest, crate, cart) on grass, except the Marsh's
		// X, a warp on the path
		if (!INDOOR[theme] && (ch === "F" || ch === "P")) ch = "=";
		if (!INDOOR[theme] && (ch === "C" || ch === "X")) ch = ch === "X" && mapId === "marsh" ? "=" : ".";
	}
	const cat = tileCat(ch);
	if (!cat || !map) return false;
	const h = hash(tx, ty);
	const at = (x: number, y: number) => (y >= 0 && y < map.length && x >= 0 && x < map[y].length ? map[y][x] : undefined);
	let key: string;
	if (cat === "grass") {
		const r = h % 16;
		key = `tile-grass-${r < 7 ? 1 : r < 13 ? 2 : r < 15 ? 3 : 4}`;
	} else if (cat === "tall") key = `tile-tallgrass-${(h % 2) + 1}`;
	else if (cat === "dirt") key = `tile-dirt-${(h % 4) + 1}`;
	else if (cat === "dirt2") key = `tile-dirt2-${(h % 2) + 1}`;
	else if (cat === "cliff") key = `tile-cliff-${(h % 2) + 1}`;
	else if (cat === "water") key = `tile-water-${(Math.floor(now / 320) % 4) + 1}`;
	else {
		const below = at(tx, ty + 1);
		const edge = below !== undefined && tileCat(below) !== "tree";
		key = `${edge ? "tile-tree-s" : "tile-tree"}-${(h % 2) + 1}`;
	}
	// the Hollow's regraded ground (tools/pixelforge/tiles_hollow.py)
	if (hollow && cat !== "dirt" && cat !== "dirt2" && cat !== "cliff") key = key.replace("tile-", "tile-h-");
	const im = images[key];
	if (!im || !im.width) return false;
	ctx.drawImage(im, dx, dy);
	if (cat === "dirt" || cat === "dirt2" || cat === "water") {
		for (const [d, ox, oy] of NB) {
			const n = at(tx + ox, ty + oy);
			if (n === undefined) continue;
			const nc = tileCat(n);
			let over: string | null = null;
			if (cat === "water" && nc !== "water") over = `tile-shore-${d}`;
			else if (cat !== "water" && (nc === "grass" || nc === "tall")) over = `tile-dirtedge-${d}`;
			const oi = over ? images[over] : null;
			if (oi && oi.width) ctx.drawImage(oi, dx, dy);
		}
	}
	return true;
}
