import type { AtkStat, ItemDef, ItemId, Monster, SpeakerId, Species, SpeciesId, StatusId, TalkBeat } from "./types";
import speciesJson from "../../content/species.json";
import itemsJson from "../../content/items.json";
import mapsJson from "../../content/maps.json";
import dialogueJson from "../../content/dialogue.json";
import worldJson from "../../content/world.json";
import spritesJson from "../../content/sprites.json";
import logicJson from "../../content/logic.json";
import townMapJson from "../../content/town_map.json";

export const PARTY_MAX = (logicJson as { party?: { max?: number } }).party?.max ?? 6;
export const TILE = 32;
export const VIEW_W = 640;
export const VIEW_H = 480;

export const SPECIES = speciesJson as Record<SpeciesId, Species>;

export const ITEM_ORDER = itemsJson.order as ItemId[];
export const ITEMS = itemsJson.defs as Record<ItemId, ItemDef>;

export const SPEAKER_NAME = dialogueJson.speakers as Record<SpeakerId, string>;
export const INTRO = dialogueJson.intro as string[];
export const ENDING_WIN = dialogueJson.endingWin as string[];
export const ENDING_WIN_HEAVENFALL = dialogueJson.endingWinHeavenfall as string[];
export const DEMO_END = ENDING_WIN;
export const TALK = dialogueJson.talk as Record<string, TalkBeat[]>;
export const MERCY_DISMISS = (dialogueJson as { mercyDismissLines?: string[] }).mercyDismissLines
	?? ["I can't believe I was beaten by a kid."];

export const START_BAG = worldJson.startBag as Record<ItemId, number>;
export const START_MARKS = worldJson.startMarks;
export const MAP_NAME = worldJson.mapNames as Record<string, string>;
export const TOWN_MAP = townMapJson as {
  name: string;
  anchor: string;
  nodes: {
    id: string;
    label: string;
    kind: string;
    gem: boolean;
    x: number;
    y: number;
    cellW: number;
    cellH: number;
    playableMaps: string[];
    realSize: { width: number; height: number };
  }[];
  edges: { from: string; to: string; edge: string; need: string | null }[];
  terrain?: { width: number; height: number };
};
export const MAP_IDS = worldJson.mapIds as string[];
export const WARPS = worldJson.warps;
export const ENCOUNTERS = worldJson.encounters;
export const TRAINERS = worldJson.trainers;
export const FORMULAS = worldJson.formulas as typeof worldJson.formulas & {
  captureAgl: number;
  captureVulnerable: number;
  xpBase: number;
  xpPerLevel: number;
  levelXpMul: number;
  levelCap: number;
  wildLevelCap: number;
  levelHp: number;
  levelStat: number;
  mintGrowPerLevel: number;
  mintBaseLevel: number;
  shinyDenom: number;
  encounterPercent: number;
  greatcrystalBonus: number;
  benchXpShare: number;
};

export type NatureDef = { id: string; name: string; str: number; agl: number; spc: number };
export const NATURES = (logicJson.natures || []) as NatureDef[];

export const SPRITES = spritesJson;
export const NPCS = worldJson.npcs;

function normalize(map: string[]) {
  const w = Math.max(...map.map((r) => r.length));
  return map.map((r) => r.padEnd(w, "#"));
}

const raw = mapsJson.rows as Record<string, string[]>;
export const HOUSE = normalize(raw.house);
export const VELD = normalize(raw.veld);
export const FOREST = normalize(raw.forest);
export const GROVE = normalize(raw.grove);
export const CAMP = normalize(raw.camp);
export const CLIFFS = normalize(raw.cliffs);
export const RUINS = normalize(raw.ruins);
export const REACH = normalize(raw.reach);
export const MARSH = normalize(raw.marsh);
export const QUARRY = normalize(raw.quarry);
export const GAUNTLET = normalize(raw.gauntlet);
export const GAUNTLET1 = normalize(raw.gauntlet1);
export const GAUNTLET2 = normalize(raw.gauntlet2);
export const GAUNTLET3 = normalize(raw.gauntlet3);
export const GAUNTLET4 = normalize(raw.gauntlet4);
export const GAUNTLET5 = normalize(raw.gauntlet5);
export const GAUNTLET6 = normalize(raw.gauntlet6);

export const MALKUTH = normalize(raw.malkuth);
export const WEEPINGROAD = normalize(raw.weepingroad);

export const YESOD = normalize(raw.yesod);
export const TAU = normalize(raw.tau);

export const NETZACH = normalize(raw.netzach);
export const QOPH = normalize(raw.qoph);

export const HOD = normalize(raw.hod);
export const SHIN = normalize(raw.shin);

export const PEH = normalize(raw.peh);

export const RESH = normalize(raw.resh);

export const TZADDI = normalize(raw.tzaddi);

export const TIFERET = normalize(raw.tiferet);
export const SAMEKH = normalize(raw.samekh);

export const NUN = normalize(raw.nun);

export const MAPS = {
  house: HOUSE,
  veld: VELD,
  forest: FOREST,
  grove: GROVE,
  camp: CAMP,
  cliffs: CLIFFS,
  ruins: RUINS,
  reach: REACH,
  marsh: MARSH,
  quarry: QUARRY,
  gauntlet: GAUNTLET,
  gauntlet1: GAUNTLET1,
  gauntlet2: GAUNTLET2,
  gauntlet3: GAUNTLET3,
  gauntlet4: GAUNTLET4,
  gauntlet5: GAUNTLET5,
  gauntlet6: GAUNTLET6,
  malkuth: MALKUTH,
  weepingroad: WEEPINGROAD,
  yesod: YESOD,
  tau: TAU,
  netzach: NETZACH,
  qoph: QOPH,
  hod: HOD,
  shin: SHIN,
  peh: PEH,
  resh: RESH,
  tzaddi: TZADDI,
  tiferet: TIFERET,
  samekh: SAMEKH,
  nun: NUN,
} as const;

export const TILE_ART: Record<string, string> = mapsJson.tileArt;
export const SOLID_TILES = mapsJson.solid;

/** Leg 2.5: base% (per crystal tier, default 100) minus the target's
 * level, strength, and current HP, all in raw stat units -- a nearly
 * full-health or high-level/high-STR CryMon reads well under 0% before
 * the clamp, so landing a capture means bringing it down first. A
 * status condition adds a flat +50 points. Replaces the old agl/
 * missing-hp%-based formula (FORMULAS.captureAgl/captureVulnerable in
 * logic.json are retired, kept only as historical baked constants no
 * code reads anymore -- not deleted from logic.json to avoid a second
 * bake-schema churn in the same leg). */
export function captureChance(level: number, str: number, hp: number, vulnerable: boolean, base = 100): number {
  let chance = base - level - str - hp;
  if (vulnerable) chance += 50;
  if (chance < 0) return 0;
  if (chance > 100) return 100;
  return chance;
}

export function natureOf(index: number): NatureDef {
  return NATURES[index] ?? NATURES[0] ?? { id: "hardy", name: "Hardy", str: 0, agl: 0, spc: 0 };
}

/* ------------------------------------------------------------------
 * Crystal matchups. One crystal gives a CryMon both its stat bonuses
 * (above) and its type. The ring, its reach and the multipliers all come
 * from content/logic.json, so the Dreamcast port derives the same table
 * from the same numbers instead of hardcoding a second one.
 * ------------------------------------------------------------------ */
export type NatureTypes = {
  ring: string[];
  beatsAhead: number;
  strongMul: number;
  weakMul: number;
  strongText: string;
  weakText: string;
};
export const NATURE_TYPES = (logicJson.natureTypes || {
  ring: [], beatsAhead: 0, strongMul: 1, weakMul: 1, strongText: "", weakText: "",
}) as NatureTypes;

/** +1 if the attacker's crystal splits the defender's, -1 if split by it, 0 neutral. */
export function natureMatchup(atkSpecies: SpeciesId, defSpecies: SpeciesId): number {
  const atkIndex = speciesNature(atkSpecies);
  const defIndex = speciesNature(defSpecies);
  const ring = NATURE_TYPES.ring;
  const n = ring.length;
  if (!n) return 0;
  const a = ring.indexOf(natureOf(atkIndex).id);
  const d = ring.indexOf(natureOf(defIndex).id);
  if (a < 0 || d < 0) return 0;
  let step = (d - a) % n;
  if (step < 0) step += n;
  if (step >= 1 && step <= NATURE_TYPES.beatsAhead) return 1;
  if (step >= n - NATURE_TYPES.beatsAhead) return -1;
  return 0;
}

/** Scales a finished damage number by the matchup; `sign` says which way it went. */
export function natureScaleDmg(
  dmg: number,
  atkSpecies: SpeciesId,
  defSpecies: SpeciesId,
): { dmg: number; sign: number } {
  const sign = natureMatchup(atkSpecies, defSpecies);
  if (sign > 0) dmg = Math.round(dmg * NATURE_TYPES.strongMul);
  else if (sign < 0) dmg = Math.round(dmg * NATURE_TYPES.weakMul);
  return { dmg: Math.max(1, dmg), sign };
}

/** " The crystal splits" / " The crystal holds" / "" for the battle log. */
export function natureTag(sign: number): string {
  if (sign > 0) return ` ${NATURE_TYPES.strongText}.`;
  if (sign < 0) return ` ${NATURE_TYPES.weakText}.`;
  return "";
}

/* ------------------------------------------------------------------
 * Combat. Every attack (basic, special, spell, Toxic Burst) is atkStat
 * (str or mag, whichever the move is tagged with) times the move's own
 * power rating (0.5-1.5, shown to the player x10 as 5-15). Speed is the
 * same shape off agility, used only to resolve Dodge. Guard has no
 * percentage roll -- Dodge is a speed contest, Block/Barrier are a flat
 * score subtracted from the incoming hit. See content/logic.json's
 * combat block; neither engine hardcodes these constants.
 * ------------------------------------------------------------------ */
export type CombatConfig = {
  dodgeDefenderRandMin: number;
  dodgeDefenderRandMax: number;
  guardRandMin: number;
  guardRandMax: number;
  barrierHealDivisor: number;
  parriedText: string;
  absorbedText: string;
  minigame: {
    perfectMin: number;
    perfectMax: number;
    perfectMul: number;
    connectedMin: number;
    connectedMax: number;
    connectedMul: number;
    fizzleMul: number;
    needleSpeed: number;
  };
};
export const COMBAT = (logicJson.combat || {
  dodgeDefenderRandMin: 1, dodgeDefenderRandMax: 1,
  guardRandMin: 1, guardRandMax: 1,
  barrierHealDivisor: 1, parriedText: "Parried!", absorbedText: "Absorbed!",
  minigame: {
    perfectMin: 45, perfectMax: 55, perfectMul: 2,
    connectedMin: 30, connectedMax: 70, connectedMul: 1.5,
    fizzleMul: 1, needleSpeed: 110,
  },
}) as CombatConfig;

/** Leg 2.11: stage-based stat drops (Proud Roar/Magebane/Slow Powder/
 *  Overload) + real status conditions (Scorch/Blight/Bind/Veil, plus
 *  Overload's Exhausted), replacing the old damage-dealing secondaries.
 *  See CURRENT_WORK.md 2.11 for the two interpretation calls flagged there
 *  (crystal->status assignment, Exhausted battle-scoped not persisted). */
export type StatStagesConfig = { mult: number[]; maxStage: number; floorAtMaxStage: number };
export const STAT_STAGES = ((logicJson as { statStages?: StatStagesConfig }).statStages || {
  mult: [1, 0.7, 0.4, 0.1, 0], maxStage: 4, floorAtMaxStage: 1,
}) as StatStagesConfig;

/** Effective value of a base stat at the given stage (0 = unaffected). */
export function effectiveStat(base: number, stage: number): number {
  if (stage >= STAT_STAGES.maxStage) return STAT_STAGES.floorAtMaxStage;
  return Math.round(base * (STAT_STAGES.mult[stage] ?? 1));
}

export type StatusEffectsConfig = {
  burned: { hpPercent: number; turnsMin: number; turnsMax: number };
  poisoned: { startPercent: number; stepPercent: number };
  paralyzed: { turnsMin: number; turnsMax: number };
};
export const STATUS_EFFECTS = ((logicJson as { statusEffects?: StatusEffectsConfig }).statusEffects || {
  burned: { hpPercent: 5, turnsMin: 2, turnsMax: 5 },
  poisoned: { startPercent: 1, stepPercent: 1 },
  paralyzed: { turnsMin: 1, turnsMax: 5 },
}) as StatusEffectsConfig;

export type ShinyMoveConfig = { name: string; status: StatusId; maxPp: number };
export const SHINY_MOVE = ((logicJson as { shinyMove?: ShinyMoveConfig }).shinyMove || {
  name: "Overload", status: "exhausted", maxPp: 10,
}) as ShinyMoveConfig;

export type HypeUpConfig = { name: string; hypePercent: number; maxPp: number };
export const HYPE_UP = ((logicJson as { hypeUp?: HypeUpConfig }).hypeUp || {
  name: "Hype Up", hypePercent: 35, maxPp: 10,
}) as HypeUpConfig;

export const STAT_MOVE_CAP = (logicJson as { statMoveCap?: number }).statMoveCap ?? 10;
export const STATUS_MOVE_CAP = (logicJson as { statusMoveCap?: number }).statusMoveCap ?? 5;

/** World interact/talk proximity: a box test against the target's own
 *  footprint (npc.w/h, default defaultW/H) plus this buffer on every
 *  side, not a radius -- see content/logic.json's interact block. */
export type InteractConfig = { defaultW: number; defaultH: number; buffer: number };
export const INTERACT = (logicJson.interact || {
  defaultW: 48, defaultH: 52, buffer: 16,
}) as InteractConfig;

export const GROWTH = ((logicJson as { growth?: { secondaryAt: number; specialAt: number; evolveAt: number } }).growth || {
  secondaryAt: 5, specialAt: 10, evolveAt: 10,
});

export type NatureMoveDef = {
  nature: string;
  name: string;
  kind: "stage" | "status";
  stat?: "str" | "agl" | "spc";
  status?: StatusId;
  maxPp: number;
};
export const NATURE_MOVES = ((logicJson as { natureMoves?: NatureMoveDef[] }).natureMoves || []) as NatureMoveDef[];

export type UnlockedMove = {
  kind: "basic" | "special" | "spell" | "nmove" | "hypeUp" | "wait";
  name: string;
  stat: AtkStat;
  power: number;
  speed: number;
  pp?: boolean;
  spellId?: string;
  /** kind === "nmove" only (the crystal secondary, or Overload for shinies). */
  moveKind?: "stage" | "status";
  statTarget?: "str" | "agl" | "spc";
  statusTarget?: StatusId;
  maxPp?: number;
};

export function natureMoveFor(species: SpeciesId): NatureMoveDef | null {
  const nid = (SPECIES[species] as { nature?: string })?.nature;
  return NATURE_MOVES.find((m) => m.nature === nid) ?? NATURE_MOVES[0] ?? null;
}

/** Any species that is some other species' evolvesTo target has evolved
 *  into its current form, and Hype Up is learned on evolving (see 2.11 --
 *  this is deliberately not a persisted flag, just derived from species.json). */
export function knowsHypeUp(species: SpeciesId): boolean {
  return Object.values(SPECIES).some((s) => s.evolvesTo === species);
}

export function unlockedMoves(m: Monster, includeWait = false): UnlockedMove[] {
  const s = SPECIES[m.species];
  const rows: UnlockedMove[] = [{
    kind: "basic",
    name: s.basic,
    stat: s.basicStat,
    power: s.basicPower,
    speed: s.basicSpeed,
  }];
  if (m.level >= GROWTH.secondaryAt) {
    if (m.shiny) {
      rows.push({
        kind: "nmove",
        name: SHINY_MOVE.name,
        stat: "str",
        power: 0,
        speed: 1,
        moveKind: "status",
        statusTarget: SHINY_MOVE.status,
        maxPp: SHINY_MOVE.maxPp,
      });
    } else {
      const nm = natureMoveFor(m.species);
      if (nm) {
        rows.push({
          kind: "nmove",
          name: nm.name,
          stat: "str",
          power: 0,
          speed: 1,
          moveKind: nm.kind,
          statTarget: nm.stat,
          statusTarget: nm.status,
          maxPp: nm.maxPp,
        });
      }
    }
  }
  if (knowsHypeUp(m.species)) {
    rows.push({
      kind: "hypeUp",
      name: HYPE_UP.name,
      stat: "str",
      power: 0,
      speed: 1,
      maxPp: HYPE_UP.maxPp,
    });
  }
  if (m.level >= GROWTH.specialAt) {
    if (s.spells?.length) {
      for (const sp of s.spells) {
        if (sp.name === s.basic) continue;
        rows.push({
          kind: "spell",
          name: sp.name,
          stat: sp.stat,
          power: sp.power,
          speed: sp.speed,
          pp: sp.pp,
          spellId: sp.id,
        });
      }
    } else {
      rows.push({
        kind: "special",
        name: s.special,
        stat: s.specialStat,
        power: s.specialPower,
        speed: s.specialSpeed,
        pp: true,
      });
    }
  }
  if (includeWait) rows.push({ kind: "wait", name: "Wait", stat: "str", power: 0, speed: 0 });
  return rows;
}

export function natureMatchNames(natureId: string): { weakTo: string[]; resists: string[] } {
  const ring = NATURE_TYPES.ring;
  const i = ring.indexOf(natureId);
  const weakTo: string[] = [];
  const resists: string[] = [];
  if (i < 0 || !ring.length) return { weakTo, resists };
  const n = ring.length;
  const ahead = NATURE_TYPES.beatsAhead;
  for (let k = 1; k <= ahead; k++) {
    const atk = ring[(i - k + n) % n];
    const res = ring[(i + k) % n];
    const atkName = NATURES.find((x) => x.id === atk)?.name ?? atk;
    const resName = NATURES.find((x) => x.id === res)?.name ?? res;
    weakTo.push(atkName);
    resists.push(resName);
  }
  return { weakTo, resists };
}

/** Uniform float in [lo, hi]. Used for the Dodge/Block/Barrier rolls. */
export function frand(lo: number, hi: number): number {
  return lo + (hi - lo) * Math.random();
}

/** Raw stat a move draws on (str or mag), mods included -- the one shared
 *  lookup every attacker-side move and every guard-side foe move go
 *  through. Agility is never an attack stat, only a speed one. */
export function atkStatValue(m: Monster, modsStr: number, modsSpc: number, stat: AtkStat): number {
  return stat === "str" ? m.str + modsStr : m.spc + modsSpc;
}

/** Index into NATURES for a species' crystal. A crystal is a property of the
 *  species, so every CryMon of that species shares it. */
export function speciesNature(species: SpeciesId): number {
  const nid = (SPECIES[species] as { nature?: string })?.nature;
  if (!nid) return 0;
  const i = NATURES.findIndex((n) => n.id === nid);
  return i < 0 ? 0 : i;
}

export function mintMonster(species: SpeciesId, level = 3, shiny = false, nature?: number): Monster {
  const s = SPECIES[species];
  let lv = Math.max(1, level);
  if (shiny) lv = Math.min(FORMULAS.levelCap, Math.max(lv, lv * 2));
  const grow = 1 + (lv - FORMULAS.mintBaseLevel) * FORMULAS.mintGrowPerLevel;
  const maxHp = Math.round(s.maxHp * grow);
  const ni = nature ?? speciesNature(species);
  const nat = natureOf(ni);
  return {
    id: `${species}-${Math.random().toString(36).slice(2, 7)}`,
    species,
    name: shiny ? `Shiny ${s.name}` : s.name,
    hp: maxHp,
    maxHp,
    str: Math.round(s.str * grow) + nat.str,
    agl: Math.round(s.agl * grow) + nat.agl,
    spc: Math.round(s.spc * grow) + nat.spc,
    specialPp: s.specialPp,
    specialPpMax: s.specialPp,
    level: lv,
    xp: 0,
    shiny,
    nature: ni,
    status: "none",
    statusTurns: 0,
    poisonStack: 0,
  };
}

export function rollShiny() {
  return Math.random() < 1 / FORMULAS.shinyDenom;
}

export function tryEvolve(m: Monster): string | null {
  const s = SPECIES[m.species];
  const to = s.evolvesTo;
  if (!to || !SPECIES[to] || m.level < GROWTH.evolveAt) return null;
  const from = m.name;
  const ratio = m.maxHp > 0 ? m.hp / m.maxHp : 1;
  const xp = m.xp;
  /* Mint the new form at the current level. Do not pass shiny into
     mintMonster — that would re-apply the wild shiny level boost. */
  const next = mintMonster(to, m.level, false);
  if (m.shiny) {
    next.shiny = true;
    next.name = `Shiny ${SPECIES[to].name}`;
  }
  m.species = next.species;
  m.name = next.name;
  m.maxHp = next.maxHp;
  m.hp = Math.max(1, Math.min(next.maxHp, Math.round(next.maxHp * ratio)));
  m.str = next.str;
  m.agl = next.agl;
  m.spc = next.spc;
  m.specialPp = next.specialPp;
  m.specialPpMax = next.specialPpMax;
  m.nature = next.nature;
  m.shiny = next.shiny;
  m.xp = xp;
  return `${from} evolved into ${m.name}!`;
}

export function grantXp(m: Monster, foeLevel: number, share = 1) {
  const gain = Math.floor((FORMULAS.xpBase + foeLevel * FORMULAS.xpPerLevel) * share);
  m.xp += gain;
  let grew = false;
  const notes: string[] = [];
  while (m.xp >= m.level * FORMULAS.levelXpMul && m.level < FORMULAS.levelCap) {
    m.xp -= m.level * FORMULAS.levelXpMul;
    m.level += 1;
    m.maxHp += FORMULAS.levelHp;
    m.hp = Math.min(m.maxHp, m.hp + FORMULAS.levelHp);
    m.str += FORMULAS.levelStat;
    m.agl += FORMULAS.levelStat;
    m.spc += FORMULAS.levelStat;
    grew = true;
  }
  const evo = tryEvolve(m);
  if (evo) notes.push(evo);
  return { grew, notes };
}

export function grantPartyXp(party: Monster[], leadIndex: number, foeLevel: number) {
  const share = FORMULAS.benchXpShare ?? 0.5;
  let grew = false;
  const notes: string[] = [];
  for (let i = 0; i < party.length; i++) {
    const m = party[i];
    if (!m || m.hp <= 0) continue;
    const r = grantXp(m, foeLevel, i === leadIndex ? 1 : share);
    if (r.grew) grew = true;
    notes.push(...r.notes);
  }
  return { grew, notes };
}

export function solidTile(ch: string) {
  return SOLID_TILES.includes(ch);
}

export function doorTile(ch: string) {
  return ch === "D" || ch === mapsJson.doors;
}

export function spawnOf(map: string[], mark: string) {
  for (let y = 0; y < map.length; y++) {
    const x = map[y]!.indexOf(mark);
    if (x >= 0) return { x: x * TILE + TILE / 2, y: y * TILE + TILE / 2 };
  }
  return { x: TILE * 2, y: TILE * 2 };
}

export function healAmount(id: ItemId) {
  const fx = itemEffect(id);
  if (fx?.kind === "heal" && typeof fx.amount === "number") return fx.amount;
  const table = FORMULAS.heal as Record<string, number>;
  return table[id] ?? 0;
}

export function itemEffect(id: ItemId) {
  return ITEMS[id]?.effect;
}

export function artManifest(): [string, string][] {
  const v = SPRITES.cache;
  // Sprite paths are root-absolute ("/sprites/..."), but GitHub Pages serves
  // this app under a subpath (base "/CryMon/"). import.meta.env.BASE_URL
  // always has a trailing slash, so strip the leading slash off p before
  // joining rather than string-replacing it in.
  const q = (p: string) => `${import.meta.env.BASE_URL}${p.replace(/^\//, "")}?v=${v}`;
  const out: [string, string][] = [];
  const dirs = ["down", "up", "left", "right"] as const;
  // Title + battle sprites first; 1MB portraits last so the cart can paint.
  for (const pair of SPRITES.extra as [string, string][]) out.push([pair[0], q(pair[1])]);
  const maxFolder = SPRITES.walkers.max;
  if (maxFolder) {
    for (const d of dirs) {
      for (let i = 1; i <= 4; i++) out.push([`max-${d}-${i}`, q(`/sprites/${maxFolder}/${d}-${i}.png`)]);
    }
  }
  for (const m of SPRITES.monsters) {
    for (let i = 1; i <= 4; i++) out.push([`${m}-${i}`, q(`/sprites/monsters/${m}/${i}.png`)]);
  }
  for (const it of SPRITES.items) out.push([`item-${it}`, q(`/sprites/items/${it}.png`)]);
  for (const [key, rel] of Object.entries(SPRITES.props)) {
    out.push([`prop-${key}`, q(`/sprites/${rel}`)]);
  }
  for (const [id, folder] of Object.entries(SPRITES.walkers)) {
    if (id === "max") continue;
    for (const d of dirs) {
      for (let i = 1; i <= 4; i++) out.push([`${id}-${d}-${i}`, q(`/sprites/${folder}/${d}-${i}.png`)]);
    }
  }
  for (const n of SPRITES.npcs) {
    for (let i = 1; i <= 4; i++) out.push([`${n}-${i}`, q(`/sprites/npc/${n}-${i}.png`)]);
  }
  for (const p of SPRITES.portraits) out.push([`port-${p}`, q(`/sprites/portraits/${p}.png`)]);
  return out;
}
