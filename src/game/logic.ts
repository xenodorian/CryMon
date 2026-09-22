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

export type NpcStep = {
	if?: string;
	ifNot?: string;
	hideIf?: string;
	set?: string;
	grant?: [string, number][];
	grantMonster?: [string, number];
	talk?: string;
	talkIf?: string;
	talkElse?: string;
	after?: string;
	pending?: string;
	heal?: boolean;
	marks?: number;
	takeItem?: string;
	passIf?: string;
	/** [dx, dy] pixel offset applied to a passIf NPC's drawn/interact
	 *  position once passIf's flag is true -- a gate-blocker steps
	 *  aside instead of just standing there passable. */
	passOffset?: [number, number];
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

/** First-match NPC script from content/world.json. hideIf matching means the NPC is gone. */
export function matchNpcScript(script: NpcStep[] | undefined, flags: Record<string, boolean>): NpcStep | null {
	if (!script || !script.length) return null;
	for (const step of script) {
		if (step.hideIf) {
			if (flags[step.hideIf]) return null;
			continue;
		}
		if (step.if && !flags[step.if]) continue;
		if (step.ifNot && flags[step.ifNot]) continue;
		return step;
	}
	return null;
}
