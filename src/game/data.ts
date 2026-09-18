import type { ItemDef, ItemId, Monster, SpeakerId, Species, SpeciesId, TalkBeat } from "./types";
import speciesJson from "../../content/species.json";
import itemsJson from "../../content/items.json";
import mapsJson from "../../content/maps.json";
import dialogueJson from "../../content/dialogue.json";
import worldJson from "../../content/world.json";
import spritesJson from "../../content/sprites.json";
import logicJson from "../../content/logic.json";

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
export const DEMO_END = ENDING_WIN;
export const TALK = dialogueJson.talk as Record<string, TalkBeat[]>;

export const START_BAG = worldJson.startBag as Record<ItemId, number>;
export const START_MARKS = worldJson.startMarks;
export const MAP_NAME = worldJson.mapNames as Record<string, string>;
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

export const MAPS = {
  house: HOUSE,
  veld: VELD,
  forest: FOREST,
  grove: GROVE,
  camp: CAMP,
  cliffs: CLIFFS,
  ruins: RUINS,
  reach: REACH,
} as const;

export const TILE_ART: Record<string, string> = mapsJson.tileArt;
export const SOLID_TILES = mapsJson.solid;

export function captureChance(agl: number, hp: number, maxHp: number, vulnerable: boolean, bonus = 0): number {
  const missing = maxHp <= 0 ? 0 : Math.floor(((maxHp - hp) * 100) / maxHp);
  let chance = FORMULAS.captureAgl * agl + missing + bonus;
  if (vulnerable) chance += FORMULAS.captureVulnerable;
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
  if (shiny) lv = Math.max(lv, lv * 2 > 12 ? 12 : lv * 2);
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
  };
}

export function rollShiny() {
  return Math.random() < 1 / FORMULAS.shinyDenom;
}

export function grantXp(m: Monster, foeLevel: number, share = 1) {
  const gain = Math.floor((FORMULAS.xpBase + foeLevel * FORMULAS.xpPerLevel) * share);
  m.xp += gain;
  let grew = false;
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
  return grew;
}

export function grantPartyXp(party: Monster[], leadIndex: number, foeLevel: number) {
  const share = FORMULAS.benchXpShare ?? 0.5;
  let grew = false;
  for (let i = 0; i < party.length; i++) {
    const m = party[i];
    if (!m || m.hp <= 0) continue;
    if (grantXp(m, foeLevel, i === leadIndex ? 1 : share)) grew = true;
  }
  return grew;
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
  const q = (p: string) => `${p}?v=${v}`;
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
