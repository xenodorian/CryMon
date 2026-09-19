export type Dir = "down" | "left" | "right" | "up";

export type Mode = "title" | "intro" | "world" | "battle" | "ending" | "bag" | "party" | "shop" | "choice" | "pause" | "crydex";

export type PartyView = "list" | "act" | "stats" | "moves" | "target" | "release" | "catchSwap";

export type ShopTab = "buy" | "sell";
export type BagTab = "items" | "settings";

export type SpeakerId =
  | "max" | "anne" | "mason" | "wren" | "mae" | "ivo" | "nell" | "pike"
  | "calder" | "bram" | "cathleen" | "shinigami"
  | "oren" | "tessa" | "birch" | "sable"
  | "cross" | "commander" | "conscript" | "enforcer" | "sentry"
  | "father" | "heavenfall" | "ranger" | "scout" | "keeper" | "warden"
  | "bogwalker" | "reedguard" | "quartz" | "opal" | "driller" | "none";

export interface TalkBeat {
  speaker: SpeakerId;
  text: string;
}

export type BattlePhase =
  | "enter"
  | "item"
  | "attack"
  | "minigame"
  | "resolve_hit"
  | "guard"
  | "resolve_guard"
  | "msg"
  | "win"
  | "lose";

export type GuardKind = "dodge" | "block" | "barrier";

export type TrainerId = "wild" | "mason" | "calder" | "soldier" | "shinigami" | "wsoldier";

export type SpeciesId =
  | "quillpup" | "glimmoth" | "tortcask" | "razorbat" | "mossback"
  | "briarfox" | "fenwisp" | "duskhorn" | "needleroot" | "cathleen" | "crymare"
  | "emberling" | "frostail" | "boulderam" | "stormwing"
  | "sableclaw" | "thornhide" | "glasswisp" | "ashenmaw" | "heavenfall"
  | "peatling" | "mireback" | "glowcap" | "slatekin" | "gravelurk" | "cindermite"
  | "veilcap" | "kilnback";

export type MapId = "house" | "veld" | "forest" | "grove" | "camp" | "cliffs" | "ruins" | "reach" | "marsh" | "quarry" | "gauntlet";

export type SpellId = "firebolt" | "icebeam" | "lightning" | "manasurge";

export type AtkStat = "str" | "mag";

export interface Spell {
  id: SpellId;
  name: string;
  pp: boolean;
  stat: AtkStat;
  power: number;
  speed: number;
}

export interface Species {
  id: SpeciesId;
  name: string;
  blurb: string;
  maxHp: number;
  str: number;
  agl: number;
  spc: number;
  basic: string;
  basicStat: AtkStat;
  basicPower: number;
  basicSpeed: number;
  special: string;
  specialStat: AtkStat;
  specialPower: number;
  specialSpeed: number;
  specialPp: number;
  wild: boolean;
  spells?: Spell[];
  nature?: string;
  evolvesTo?: SpeciesId;
}

export interface Monster {
  id: string;
  species: SpeciesId;
  name: string;
  hp: number;
  maxHp: number;
  str: number;
  agl: number;
  spc: number;
  specialPp: number;
  specialPpMax: number;
  level: number;
  xp: number;
  shiny: boolean;
  nature: number;
}

export type ItemId = "gem" | "salve" | "bitterroot" | "dust" | "bandage" | "sunbalm" | "warroot" | "smokebomb" | "greatcrystal" | "cageKey";

export interface ItemDef {
  id: ItemId;
  name: string;
  desc: string;
  battle: boolean;
  field: boolean;
  buy: number;
  sell: number;
  effect?: {
    kind: "heal" | "buff" | "debuff" | "capture" | "flee";
    amount?: number;
    str?: number;
    agl?: number;
    spc?: number;
    bonus?: number;
  };
}

export interface BattleMods {
  selfStr: number;
  selfAgl: number;
  selfSpc: number;
  foeStr: number;
  foeAgl: number;
  foeSpc: number;
}

export interface BattleState {
  wild: boolean;
  trainer: TrainerId;
  foeName: string;
  soldierId: string | null;
  player: Monster;
  foe: Monster;
  phase: BattlePhase;
  cursor: number;
  menu: string[];
  msg: string[];
  msgI: number;
  afterMsg: BattlePhase | "end_win" | "end_lose" | "end_catch" | "end_run";
  pendingDmg: number;
  pendingLabel: string;
  pendingMods: { str: number; agl: number; spc: number };
  minigame: number;
  minigameDir: number;
  minigameHit: number | null;
  guard: GuardKind | null;
  mods: BattleMods;
  catchUsed: boolean;
  t: number;
  foeBench: Monster[];
  enterT: number;
  faintT: number;
  foeEnterT: number;
  foeFaintT: number;
  plPoisoned: boolean;
  foePoisoned: boolean;
}

export interface WorldState {
  mapId: MapId;
  x: number;
  y: number;
  dir: Dir;
  moving: boolean;
  frame: number;
  anim: number;
  encounterLock: number;
}

export interface Soldier {
  id: string;
  name: string;
  x: number;
  y: number;
  dir: Dir;
  frame: number;
  anim: number;
  chase: boolean;
  beaten: boolean;
  species: SpeciesId;
  level: number;
  axis: "x" | "y" | "none";
  min: number;
  max: number;
  sign: number;
  bench?: Monster[];
}

export type RivalPhase = "off" | "approach" | "talk" | "done" | "leave";

export interface RivalState {
  phase: RivalPhase;
  x: number;
  y: number;
  dir: Dir;
  frame: number;
  anim: number;
}

export type ControlsProbe = {
  getYaw: () => number;
  getSpeed: () => number;
  getX: () => number;
  getY: () => number;
  setKeys: (codes: string[]) => void;
};
