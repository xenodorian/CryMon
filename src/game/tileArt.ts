/**
 * Painted overworld ground tiles (public/sprites/tiles, drawn by
 * tools/pixelforge/tiles.py). Engine.paintTile() calls paintTileArt() first;
 * when it returns false (a char this file does not cover, or the image has
 * not loaded yet) the engine's flat-colour tile runs as before.
 */
import { TILE_ART } from "./data";

/** Chars with their own look in Engine.paintTile(): never painted here. */
const OWN_LOOK = "HRr%gkFPDBUCN*X";
const DIRT = "=ZY3cO89S";

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
): boolean {
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
