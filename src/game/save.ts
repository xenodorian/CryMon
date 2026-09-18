import saveJson from "../../content/save.json";
import type { Dir, ItemId, MapId, Monster, SpeciesId } from "./types";

export const SAVE_VERSION = saveJson.version;
export const SAVE_SIZE = saveJson.size;
export const SAVE_FLAGS = saveJson.flags as readonly string[];
export const SAVE_ITEMS = saveJson.itemOrder as ItemId[];
export const SAVE_MAPS = saveJson.mapOrder as MapId[];
export const SAVE_DIRS = saveJson.dirOrder as Dir[];
export const SAVE_SPECIES = saveJson.speciesOrder as SpeciesId[];
export const SAVE_KEY = "crymon.save.v1";

export type SaveFlagName = (typeof SAVE_FLAGS)[number];

export interface SaveSnapshot {
	mapId: MapId;
	x: number;
	y: number;
	dir: Dir;
	marks: number;
	partyIndex: number;
	battlesDone: number;
	mason2Map: MapId | null;
	bag: Record<string, number>;
	flags: Record<string, boolean>;
	party: Monster[];
	dexSeen: number;
	dexCaught: number;
}

const SLOT = saveJson.partySlot;

function u16(buf: Uint8Array, i: number, v: number) {
	buf[i] = v & 0xff;
	buf[i + 1] = (v >> 8) & 0xff;
}
function u32(buf: Uint8Array, i: number, v: number) {
	buf[i] = v & 0xff;
	buf[i + 1] = (v >> 8) & 0xff;
	buf[i + 2] = (v >> 16) & 0xff;
	buf[i + 3] = (v >> 24) & 0xff;
}
function ru16(buf: Uint8Array, i: number) {
	return buf[i] | (buf[i + 1] << 8);
}
function ru32(buf: Uint8Array, i: number) {
	return (buf[i] | (buf[i + 1] << 8) | (buf[i + 2] << 16) | (buf[i + 3] << 24)) >>> 0;
}
function checksum(buf: Uint8Array) {
	let s = 0;
	for (let i = 0; i < 132; i++) s = (s + buf[i]) & 0xffff;
	return s;
}

export function packSave(snap: SaveSnapshot): Uint8Array {
	const buf = new Uint8Array(SAVE_SIZE);
	buf[0] = 0x43;
	buf[1] = 0x52;
	buf[2] = 0x59;
	buf[3] = 0x4d;
	buf[4] = SAVE_VERSION;
	buf[5] = Math.max(0, SAVE_MAPS.indexOf(snap.mapId));
	buf[6] = Math.max(0, SAVE_DIRS.indexOf(snap.dir));
	const n = Math.min(6, snap.party.length);
	buf[7] = n;
	u16(buf, 8, Math.round(snap.x) & 0xffff);
	u16(buf, 10, Math.round(snap.y) & 0xffff);
	u16(buf, 12, Math.max(0, snap.marks) & 0xffff);
	buf[14] = Math.max(0, Math.min(n ? n - 1 : 0, snap.partyIndex));
	buf[15] = Math.max(0, Math.min(255, snap.battlesDone));
	buf[16] = snap.mason2Map ? Math.max(0, SAVE_MAPS.indexOf(snap.mason2Map)) : 0xff;
	for (let i = 0; i < SAVE_ITEMS.length; i++) {
		buf[18 + i] = Math.max(0, Math.min(255, snap.bag[SAVE_ITEMS[i]] ?? 0));
	}
	for (let i = 0; i < SAVE_FLAGS.length; i++) {
		if (snap.flags[SAVE_FLAGS[i]]) buf[28 + (i >> 3)] |= 1 << (i & 7);
	}
	for (let p = 0; p < n; p++) {
		const m = snap.party[p];
		const o = 36 + p * SLOT;
		buf[o] = Math.max(0, SAVE_SPECIES.indexOf(m.species));
		buf[o + 1] = Math.max(1, Math.min(99, m.level));
		buf[o + 2] = Math.max(0, Math.min(255, m.hp));
		buf[o + 3] = Math.max(1, Math.min(255, m.maxHp));
		buf[o + 4] = Math.max(0, Math.min(255, m.str));
		buf[o + 5] = Math.max(0, Math.min(255, m.agl));
		buf[o + 6] = Math.max(0, Math.min(255, m.spc));
		buf[o + 7] = Math.max(0, Math.min(255, m.specialPp));
		buf[o + 8] = Math.max(0, Math.min(255, m.specialPpMax));
		buf[o + 9] = m.shiny ? 1 : 0;
		u16(buf, o + 10, Math.max(0, m.xp) & 0xffff);
		buf[o + 12] = Math.max(0, Math.min(255, m.nature ?? 0));
	}
	u16(buf, 132, checksum(buf));
	u32(buf, 134, snap.dexSeen >>> 0);
	u32(buf, 138, snap.dexCaught >>> 0);
	return buf;
}

export function unpackSave(buf: Uint8Array): SaveSnapshot | null {
	if (!buf || buf.length < 134) return null;
	if (buf[0] !== 0x43 || buf[1] !== 0x52 || buf[2] !== 0x59 || buf[3] !== 0x4d) return null;
	if (buf[4] !== SAVE_VERSION) return null;
	if (ru16(buf, 132) !== checksum(buf)) return null;
	const mapId = SAVE_MAPS[buf[5]] ?? "house";
	const dir = SAVE_DIRS[buf[6]] ?? "down";
	const n = Math.min(6, buf[7]);
	const bag: Record<string, number> = {};
	for (let i = 0; i < SAVE_ITEMS.length; i++) bag[SAVE_ITEMS[i]] = buf[18 + i] ?? 0;
	const flags: Record<string, boolean> = {};
	for (let i = 0; i < SAVE_FLAGS.length; i++) {
		flags[SAVE_FLAGS[i]] = !!(buf[28 + (i >> 3)] & (1 << (i & 7)));
	}
	const party: Monster[] = [];
	for (let p = 0; p < n; p++) {
		const o = 36 + p * SLOT;
		const species = SAVE_SPECIES[buf[o]] ?? "quillpup";
		party.push({
			id: `s${p}-${species}`,
			species,
			name: species[0].toUpperCase() + species.slice(1),
			level: Math.max(1, buf[o + 1]),
			hp: buf[o + 2],
			maxHp: Math.max(1, buf[o + 3]),
			str: buf[o + 4],
			agl: buf[o + 5],
			spc: buf[o + 6],
			specialPp: buf[o + 7],
			specialPpMax: buf[o + 8],
			shiny: buf[o + 9] === 1,
			xp: ru16(buf, o + 10),
			nature: buf[o + 12] ?? 0,
		});
	}
	const m2 = buf[16];
	return {
		mapId,
		x: ru16(buf, 8),
		y: ru16(buf, 10),
		dir,
		marks: ru16(buf, 12),
		partyIndex: Math.min(Math.max(0, buf[14]), Math.max(0, n - 1)),
		battlesDone: buf[15],
		mason2Map: m2 === 0xff ? null : (SAVE_MAPS[m2] ?? null),
		bag,
		flags,
		party,
		dexSeen: buf.length >= 138 ? ru32(buf, 134) : 0,
		dexCaught: buf.length >= 142 ? ru32(buf, 138) : 0,
	};
}

export function saveExists(): boolean {
	try {
		return !!localStorage.getItem(SAVE_KEY);
	} catch {
		return false;
	}
}

export function writeSaveBlob(buf: Uint8Array): boolean {
	try {
		let s = "";
		for (let i = 0; i < buf.length; i++) s += String.fromCharCode(buf[i]);
		localStorage.setItem(SAVE_KEY, btoa(s));
		return true;
	} catch {
		return false;
	}
}

export function readSaveBlob(): Uint8Array | null {
	try {
		const raw = localStorage.getItem(SAVE_KEY);
		if (!raw) return null;
		const bin = atob(raw);
		const buf = new Uint8Array(bin.length);
		for (let i = 0; i < bin.length; i++) buf[i] = bin.charCodeAt(i);
		return buf;
	} catch {
		return null;
	}
}
