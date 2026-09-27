// Battle frames, normalised at load; the PNGs stay as drawn.
// Generated art carries loose, uneven padding, so an evolved form could show
// smaller than its earlier form. Each species is padded to a square it fills
// (by area) by its evolution stage, standing on the bottom edge: three-stage
// lines 0.66/0.83/1.0, two-stage 0.76/1.0, others 0.92. Species whose four
// frames are identical get a breath: frames 2-4 stretch the body up a row or
// two with the feet fixed. ports/dreamcast/tools/gen_sprites.py does the same
// for the Dreamcast; keep the two in step.
import { SPECIES } from "./data";

const STAGE_FILL: Record<number, number[]> = { 3: [0.66, 0.83, 1.0], 2: [0.76, 1.0], 1: [0.92] };

export function stageFill(id: string): number {
	const all = SPECIES as Record<string, { evolvesTo?: string }>;
	let head = id;
	for (;;) {
		const pre = Object.keys(all).find((k) => all[k].evolvesTo === head);
		if (!pre) break;
		head = pre;
	}
	const chain = [head];
	while (all[chain[chain.length - 1]]?.evolvesTo) chain.push(all[chain[chain.length - 1]].evolvesTo as string);
	return STAGE_FILL[Math.min(3, chain.length)][Math.min(chain.indexOf(id), 2)];
}

type Img = HTMLImageElement | HTMLCanvasElement;

function pixels(im: Img): ImageData {
	const c = document.createElement("canvas");
	c.width = im.width;
	c.height = im.height;
	const g = c.getContext("2d")!;
	g.drawImage(im, 0, 0);
	return g.getImageData(0, 0, c.width, c.height);
}

function bbox(d: ImageData): [number, number, number, number] | null {
	let x0 = d.width, y0 = d.height, x1 = -1, y1 = -1;
	for (let y = 0; y < d.height; y++)
		for (let x = 0; x < d.width; x++)
			if (d.data[(y * d.width + x) * 4 + 3] > 0) {
				if (x < x0) x0 = x;
				if (x > x1) x1 = x;
				if (y < y0) y0 = y;
				if (y > y1) y1 = y;
			}
	return x1 < 0 ? null : [x0, y0, x1 + 1, y1 + 1];
}

function same(a: ImageData, b: ImageData): boolean {
	if (a.width !== b.width || a.height !== b.height) return false;
	for (let i = 0; i < a.data.length; i++) if (a.data[i] !== b.data[i]) return false;
	return true;
}

/** Stretch the sprite up by `rows`, feet fixed; rows repeat evenly through
 *  the body so no single seam shows. */
function breathe(src: HTMLCanvasElement, rows: number): HTMLCanvasElement {
	const d = pixels(src);
	const b = bbox(d);
	const out = document.createElement("canvas");
	out.width = src.width;
	out.height = src.height;
	if (!b) return out;
	const [, top, , bot] = b;
	const h = bot - top;
	const g = out.getContext("2d")!;
	for (let y = 0; y < h + rows; y++) {
		const sy = top + Math.min(h - 1, Math.floor((y * h) / (h + rows)));
		g.drawImage(src, 0, sy, src.width, 1, 0, top - rows + y, src.width, 1);
	}
	return out;
}

/** Four square, stage-sized frames for a species, or null if any source
 *  frame has not loaded yet. */
export function battleFrames(species: string, frames: (Img | undefined)[]): HTMLCanvasElement[] | null {
	if (frames.some((f) => !f || !f.width)) return null;
	const data = (frames as Img[]).map(pixels);
	const boxes = data.map(bbox);
	if (boxes.some((b) => !b)) return null;
	const bs = boxes as [number, number, number, number][];
	const x0 = Math.min(...bs.map((b) => b[0])), y0 = Math.min(...bs.map((b) => b[1]));
	const x1 = Math.max(...bs.map((b) => b[2])), y1 = Math.max(...bs.map((b) => b[3]));
	const w = x1 - x0, h = y1 - y0;
	const fill = stageFill(species);
	let side = Math.max(Math.max(w, h) + 2, Math.ceil(Math.sqrt(w * h) / (fill * 0.85)));
	const foot = Math.max(1, Math.round(side * 0.02));
	side = Math.max(side, h + foot + 6);
	const ox = Math.floor((side - w) / 2), oy = side - foot - h;
	const out = (frames as Img[]).map((f) => {
		const c = document.createElement("canvas");
		c.width = c.height = side;
		c.getContext("2d")!.drawImage(f, x0, y0, w, h, ox, oy, w, h);
		return c;
	});
	if (data.slice(1).every((d) => same(d, data[0]))) {
		const r = Math.max(1, Math.round(h / 48));
		return [out[0], breathe(out[0], r), breathe(out[0], 2 * r), breathe(out[0], r)];
	}
	return out;
}
