import type { ItemDef, ItemId, Monster, SpeakerId, Species, SpeciesId, TalkBeat } from "./types";
import speciesJson from "../../content/species.json";
import itemsJson from "../../content/items.json";
import mapsJson from "../../content/maps.json";
import dialogueJson from "../../content/dialogue.json";
import worldJson from "../../content/world.json";

export const PARTY_MAX = 6;
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
export const FORMULAS = worldJson.formulas;
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

export const HOUSE_MAP = raw.house;
export const VELD_MAP = raw.veld;
export const FOREST_MAP = raw.forest;
export const GROVE_MAP = raw.grove;
export const CAMP_MAP = raw.camp;
export const CLIFFS_MAP = raw.cliffs;
export const RUINS_MAP = raw.ruins;

export const MAPS = {
  house: HOUSE,
  veld: VELD,
  forest: FOREST,
  grove: GROVE,
  camp: CAMP,
  cliffs: CLIFFS,
  ruins: RUINS,
} as const;

export const TILE_ART: Record<string, string> = mapsJson.tileArt;
export const SOLID_TILES = mapsJson.solid;

export function captureChance(agl: number, hp: number, maxHp: number, vulnerable: boolean, bonus = 0): number {
  const missing = maxHp <= 0 ? 0 : Math.floor(((maxHp - hp) * 100) / maxHp);
  let chance = 5 * agl + missing + bonus;
  if (vulnerable) chance += 25;
  if (chance < 0) return 0;
  if (chance > 100) return 100;
  return chance;
}

export function mintMonster(species: SpeciesId, level = 3, shiny = false): Monster {
  const s = SPECIES[species];
  let lv = Math.max(1, level);
  if (shiny) lv = Math.max(lv, lv * 2 > 12 ? 12 : lv * 2);
  const grow = 1 + (lv - 3) * 0.12;
  const maxHp = Math.round(s.maxHp * grow);
  return {
    id: `${species}-${Math.random().toString(36).slice(2, 7)}`,
    species,
    name: shiny ? `Shiny ${s.name}` : s.name,
    hp: maxHp,
    maxHp,
    str: Math.round(s.str * grow),
    agl: Math.round(s.agl * grow),
    spc: Math.round(s.spc * grow),
    specialPp: s.specialPp,
    specialPpMax: s.specialPp,
    level: lv,
    xp: 0,
    shiny,
  };
}

export function rollShiny() {
  return Math.random() < 1 / 64;
}

export function grantXp(m: Monster, foeLevel: number) {
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
  const table = FORMULAS.heal as Record<string, number>;
  return table[id] ?? 0;
}
