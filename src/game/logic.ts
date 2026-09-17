import logicJson from "../../content/logic.json";
import type { MapId } from "./types";

export const LOGIC = logicJson;

export type FadeAction = "bed" | "loss" | null;
export type FadePhase = "off" | "out" | "hold" | "in";

export type LogicFlags = {
	foughtMason: boolean;
	beatCalder: boolean;
	hasParty: boolean;
	mason2Done: boolean;
	mason2Map: string | null;
	mapId: string;
	rivalOff: boolean;
};

export function arrivalAllowed(flags: LogicFlags, name: string): boolean {
	const spec = LOGIC.arrivals[name as keyof typeof LOGIC.arrivals];
	if (!spec) return false;
	if ("call" in spec) return true;
	if ("needParty" in spec && spec.needParty && !flags.hasParty) return false;
	if ("unless" in spec && spec.unless === "foughtMason" && flags.foughtMason) return false;
	if (!flags.rivalOff) return false;
	return true;
}

export function pickMason2Map(rand01: number): MapId {
	const maps = LOGIC.masonRematch.maps;
	const i = Math.min(maps.length - 1, Math.floor(rand01 * maps.length));
	return maps[i] as MapId;
}

export function shouldSpawnMasonRematch(flags: LogicFlags): boolean {
	const r = LOGIC.masonRematch;
	if (flags.mason2Done) return false;
	if (!flags.mason2Map) return false;
	if (flags.mapId !== flags.mason2Map) return false;
	if (!flags.rivalOff) return false;
	return true;
}

export function fadeAlpha(phase: FadePhase, t: number): number {
	const { outSec, inSec } = LOGIC.screenFade;
	if (phase === "out") return Math.min(1, t / outSec);
	if (phase === "hold") return 1;
	if (phase === "in") return Math.max(0, 1 - t / inSec);
	return 0;
}
