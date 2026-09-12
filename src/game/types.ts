export type Dir = "down" | "left" | "right" | "up";

export type Mode = "title" | "intro" | "world" | "battle" | "ending" | "bag" | "party" | "shop";

export type PartyView = "list" | "act" | "stats" | "moves" | "target";

export type ShopTab = "buy" | "sell";

export type SpeakerId = "max" | "anne" | "mason" | "wren" | "ivo" | "nell" | "pike" | "calder" | "bram" | "cathleen" | "shinigami" | "none";

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

export type TrainerId = "wild" | "mason" | "calder" | "soldier" | "shinigami";

export type SpeciesId = "quillpup" | "glimmoth" | "tortcask" | "razorbat" | "mossback" | "briarfox" | "fenwisp" | "duskhorn" | "needleroot" | "cathleen" | "crymare";

export type MapId = "house" | "veld" | "forest" | "grove";

export type SpellId = "firebolt" | "icebeam" | "lightning" | "manasurge";

export interface Spell {
  id: SpellId;
  name: string;
  pp: boolean;
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
  special: string;
  specialPp: number;
  wild: boolean;
  spells?: Spell[];
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
}

export type ItemId = "gem" | "salve" | "bitterroot" | "dust" | "bandage";

export interface ItemDef {
  id: ItemId;
  name: string;
  desc: string;
  battle: boolean;
  field: boolean;
  buy: number;
  sell: number;
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
  minigame: number;
  minigameDir: number;
  minigameHit: number | null;
  pendingDmg: number;
  pendingLabel: string;
  guard: GuardKind | null;
  mods: BattleMods;
  catchUsed: boolean;
  t: number;
  foeBench: Monster[];
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
  beaten: boolean;
  chase: boolean;
  axis: "x" | "y" | "none";
  min: number;
  max: number;
  sign: number;
  species: SpeciesId;
  level: number;
}

export type RivalPhase = "off" | "approach" | "talk" | "done";

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
