export type Dir = "down" | "left" | "right" | "up";

export type Mode = "title" | "intro" | "world" | "battle" | "ending" | "bag" | "party" | "shop" | "choice" | "mercy" | "pause" | "crydex" | "townmap";

export type PartyView = "list" | "act" | "stats" | "moves" | "target" | "release" | "catchSwap" | "settings";

export type ShopTab = "buy" | "sell";

export type SpeakerId =
  | "max" | "anne" | "mason" | "wren" | "mae" | "ivo" | "nell" | "pike"
  | "calder" | "bram" | "cathleen" | "shinigami"
  | "oren" | "tessa" | "birch" | "sable"
  | "cross" | "commander" | "conscript" | "enforcer" | "sentry"
  | "father" | "heavenfall" | "ranger" | "scout" | "keeper" | "warden"
  | "bogwalker" | "reedguard" | "quartz" | "opal" | "driller" | "fenn" | "dray" | "lead" | "system" | "none" | "heavenfallPriestess";

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
  | "veilcap" | "kilnback" | "lead";

export type MapId = "house" | "veld" | "forest" | "grove" | "camp" | "cliffs" | "ruins" | "reach" | "marsh" | "quarry" | "gauntlet" | "gauntlet1" | "gauntlet2" | "gauntlet3" | "gauntlet4" | "gauntlet5" | "gauntlet6" | "malkuth" | "weepingroad" | "yesod" | "tau" | "netzach" | "qoph";

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
  /** Leg 2.11: persists on the player's own CryMon until their next rest
   *  (sleepHeal clears it). "none" if unset. Wild/trainer foes never save,
   *  so this is battle-scoped for them regardless. */
  status?: StatusId;
  /** Burned/Paralyzed countdown; unused by Poisoned/Confused. */
  statusTurns?: number;
  /** Poisoned's linear stack (tick = poisonStack% of maxHp, +1/turn). */
  poisonStack?: number;
}

export type StatusId = "none" | "burned" | "poisoned" | "confused" | "paralyzed" | "exhausted";

export type ItemId = "gem" | "salve" | "bitterroot" | "dust" | "bandage" | "sunbalm" | "warroot" | "smokebomb" | "greatcrystal" | "cageKey" | "megacrystal" | "ultimatecrystal" | "perfectcrystal" | "calmdraft" | "burnsalve" | "antidote" | "clearmind" | "numbroot" | "panacea";

export interface ItemDef {
  id: ItemId;
  name: string;
  desc: string;
  battle: boolean;
  field: boolean;
  buy: number;
  sell: number;
  effect?: {
    kind: "heal" | "buff" | "debuff" | "capture" | "flee" | "cleanse" | "cure";
    amount?: number;
    str?: number;
    agl?: number;
    spc?: number;
    base?: number;
    /** kind === "cure" only: a specific StatusId, or "all". */
    status?: StatusId | "all";
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
  /** Leg 2.11: short suffix describing an nmove/hypeUp's effect, shown by
   *  resolve_hit/resolve_guard in place of a damage number when pendingDmg
   *  is 0 (these moves deal no damage). */
  pendingEffectText: string;
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
  /** Leg 2.11: 0-4 stage counters for Proud Roar/Magebane/Slow Powder/
   *  Overload, battle-scoped (reset every new battle, never saved). Status
   *  conditions themselves live on player/foe.status instead -- see
   *  Monster.status. */
  stage: BattleMods;
  /** Whether each side has used Hype Up this battle (non-stacking, lasts
   *  until battle end -- see CURRENT_WORK.md 2.11). */
  hypeActive: { self: boolean; foe: boolean };
  /** Battle-scoped PP for nmove/hypeUp, keyed by `${monster.id}:nmove` /
   *  `${monster.id}:hype` so a fainted-out-and-swapped-back monster still
   *  has its own count, and a fresh foe/party member starts full. */
  movePpUsed: Record<string, number>;
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
