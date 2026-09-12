import type { ItemDef, ItemId, Monster, SpeakerId, Species, SpeciesId, TalkBeat } from "./types";

export const PARTY_MAX = 6;
export const TILE = 32;
export const VIEW_W = 640;
export const VIEW_H = 480;

export const SPECIES: Record<SpeciesId, Species> = {
  quillpup: {
    id: "quillpup",
    name: "Quillpup",
    blurb: "A bristled hound. Family leftover. Hits like a thrown crate.",
    maxHp: 34,
    str: 15,
    agl: 10,
    spc: 7,
    basic: "Nip",
    special: "Quillburst",
    specialPp: 3,
    wild: false,
  },
  glimmoth: {
    id: "glimmoth",
    name: "Glimmoth",
    blurb: "Lantern-gut moth of the tall grass. Burns what it blesses.",
    maxHp: 26,
    str: 7,
    agl: 13,
    spc: 16,
    basic: "Dustwing",
    special: "Lampflare",
    specialPp: 3,
    wild: true,
  },
  tortcask: {
    id: "tortcask",
    name: "Tortcask",
    blurb: "A walking cask of moss and stubbornness.",
    maxHp: 42,
    str: 13,
    agl: 5,
    spc: 8,
    basic: "Shove",
    special: "Shellslam",
    specialPp: 3,
    wild: true,
  },
  razorbat: {
    id: "razorbat",
    name: "Razorbat",
    blurb: "Camp-bred cutter. Hunts by the whistle of its wings.",
    maxHp: 30,
    str: 14,
    agl: 16,
    spc: 9,
    basic: "Rake",
    special: "Swoopcut",
    specialPp: 3,
    wild: false,
  },
  mossback: {
    id: "mossback",
    name: "Mossback",
    blurb: "A toad in a coat of wet leaves. Absorbs what it sits on.",
    maxHp: 38,
    str: 12,
    agl: 6,
    spc: 11,
    basic: "Squelch",
    special: "Mossguard",
    specialPp: 3,
    wild: true,
  },
  briarfox: {
    id: "briarfox",
    name: "Briarfox",
    blurb: "Thorn-pelt fox of the deep trees. Fast, and it bites last.",
    maxHp: 28,
    str: 13,
    agl: 17,
    spc: 10,
    basic: "Bramble",
    special: "Thornrush",
    specialPp: 3,
    wild: true,
  },
  fenwisp: {
    id: "fenwisp",
    name: "Fenwisp",
    blurb: "A lantern soul of the wet trees. It burns cold.",
    maxHp: 24,
    str: 8,
    agl: 16,
    spc: 17,
    basic: "Glim",
    special: "Fenflare",
    specialPp: 3,
    wild: true,
  },
  duskhorn: {
    id: "duskhorn",
    name: "Duskhorn",
    blurb: "A rust-horned ram of the deep wood. It charges first.",
    maxHp: 36,
    str: 16,
    agl: 8,
    spc: 7,
    basic: "Gore",
    special: "Duskram",
    specialPp: 3,
    wild: true,
  },
  needleroot: {
    id: "needleroot",
    name: "Needleroot",
    blurb: "A walking thorn-stump. Slow, and it drinks blood from cuts.",
    maxHp: 32,
    str: 12,
    agl: 7,
    spc: 14,
    basic: "Prick",
    special: "Sapdrain",
    specialPp: 3,
    wild: true,
  },
  cathleen: {
    id: "cathleen",
    name: "Cathleen",
    blurb: "A sentient CryMon. She fights as herself, in a red hood.",
    maxHp: 38,
    str: 11,
    agl: 13,
    spc: 19,
    basic: "Fire Bolt",
    special: "Mana Surge",
    specialPp: 4,
    wild: true,
    spells: [
      { id: "firebolt", name: "Fire Bolt", pp: false },
      { id: "icebeam", name: "Ice Beam", pp: false },
      { id: "lightning", name: "Lightning Strike", pp: false },
      { id: "manasurge", name: "Mana Surge", pp: true },
    ],
  },
  crymare: {
    id: "crymare",
    name: "CryMare",
    blurb: "A grave-horse of fog. It screams in a voice that isn't a horse.",
    maxHp: 30,
    str: 9,
    agl: 14,
    spc: 18,
    basic: "Wail",
    special: "Nightbridle",
    specialPp: 3,
    wild: false,
  },
};

export const ITEM_ORDER: ItemId[] = ["salve", "bandage", "bitterroot", "dust", "gem"];

export const ITEMS: Record<ItemId, ItemDef> = {
  gem: {
    id: "gem",
    name: "Capture Crystal",
    desc: "Moonstone cage. 5% per agility. Each % of HP missing adds 1%. Status or a lowered stat holds +25%.",
    battle: true,
    field: false,
    buy: 20,
    sell: 10,
  },
  salve: {
    id: "salve",
    name: "Moss salve",
    desc: "Restores 22 HP.",
    battle: true,
    field: true,
    buy: 10,
    sell: 5,
  },
  bitterroot: {
    id: "bitterroot",
    name: "Bitterroot",
    desc: "STR +4 this fight.",
    battle: true,
    field: false,
    buy: 8,
    sell: 4,
  },
  dust: {
    id: "dust",
    name: "Ash dust",
    desc: "Foe STR-3 AGI-2 SPC-2 this fight.",
    battle: true,
    field: false,
    buy: 8,
    sell: 4,
  },
  bandage: {
    id: "bandage",
    name: "Linen wrap",
    desc: "Restores 12 HP.",
    battle: true,
    field: true,
    buy: 6,
    sell: 3,
  },
};

export function captureChance(agl: number, hp: number, maxHp: number, vulnerable: boolean): number {
  const missing = maxHp <= 0 ? 0 : Math.floor(((maxHp - hp) * 100) / maxHp);
  let chance = 5 * agl + missing;
  if (vulnerable) chance += 25;
  if (chance < 0) return 0;
  if (chance > 100) return 100;
  return chance;
}

export function mintMonster(species: SpeciesId, level = 3): Monster {
  const s = SPECIES[species];
  const lv = Math.max(1, level);
  const grow = 1 + (lv - 3) * 0.12;
  const maxHp = Math.round(s.maxHp * grow);
  return {
    id: `${species}-${Math.random().toString(36).slice(2, 7)}`,
    species,
    name: s.name,
    hp: maxHp,
    maxHp,
    str: Math.round(s.str * grow),
    agl: Math.round(s.agl * grow),
    spc: Math.round(s.spc * grow),
    specialPp: s.specialPp,
    specialPpMax: s.specialPp,
    level: lv,
    xp: 0,
  };
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

export const HOUSE_MAP = [
  "HHHHHHHHHHHHHH",
  "HFFFFFFFFFFFFH",
  "HFFFFFFFFFFFFH",
  "HFFFFFFFFFFFFH",
  "HFBFFFFSFFFCFH",
  "HFFFFFFFFFFFFH",
  "HUFFFFFFFFFFFH",
  "HFFFFPFFFFFFFH",
  "HFFFFFFFFFFFFH",
  "HFFFFFFFFFFFFH",
  "HHHHHHDHHHHHHH",
];

export const VELD_MAP = [
  "##############################",
  "####..........RRRR..........##",
  "##.Q.^^.......HHHH......WWW.##",
  "##............HDH......WWA..##",
  "##..K.........===...I...W....#",
  "##...TTT.....=====.....TTT..G#",
  "##...TTT....===,===....TTT...#",
  "##....M......=====....**.....#",
  "##.V.TTT......===......TTT...#",
  "##............===............#",
  "###....X...J.=====...........#",
  "##...TTT......===............#",
  "##............===.......L....#",
  "##...TTT.....=====......TTT..#",
  "##............===......^^....#",
  "##....TTT....=====......TTT..#",
  "##....TTT.....===......TTT...#",
  "##............===............#",
  "##...........=====.....NNNN..#",
  "##............===.......NE...#",
  "###...........===...........##",
  "#############=Z=##############",
];

export const FOREST_MAP = [
  "##########################",
  "####.........Y.........###",
  "###.........===.........##",
  "##...TTT....===....TTT..##",
  "##...TTT...=====...TTT..##",
  "##.1........===.......2.##",
  "##...TTT....===....TTT..##",
  "##..........=====.......##",
  "##...TTT....===....TTT..##",
  "##...........===........##",
  "##...TTT....=====..TTT..##",
  "##...........===........##",
  "##...TTT.....===...TTT..##",
  "##...........=====......##",
  "##....TTT....===...TTT..##",
  "##............===.......##",
  "##...TTT......===..TTT..##",
  "##............===....3..##",
  "###...........===......###",
  "#############=O=##########",
];

export const GROVE_MAP = [
  "##########################",
  "####.........O.........###",
  "###.........===.........##",
  "##..........===.........##",
  "##.........=====........##",
  "##..........===.........##",
  "##.........=====........##",
  "##..........===.........##",
  "##.........=====........##",
  "##..........===.........##",
  "##........=======.......##",
  "##........===8===.......##",
  "##........=======.......##",
  "##.........=====........##",
  "##..........===.........##",
  "##.........=====........##",
  "##..........===.........##",
  "##...........9..........##",
  "###....................###",
  "##########################",
];

function normalize(map: string[]) {
  const w = Math.max(...map.map((r) => r.length));
  return map.map((r) => r.padEnd(w, "#"));
}

export const HOUSE = normalize(HOUSE_MAP);
export const VELD = normalize(VELD_MAP);
export const FOREST = normalize(FOREST_MAP);
export const GROVE = normalize(GROVE_MAP);

export const MAPS = { house: HOUSE, veld: VELD, forest: FOREST, grove: GROVE } as const;

export const TILE_ART: Record<string, string> = {
  ".": "tile-grass",
  T: "tile-tallgrass",
  "=": "tile-dirt",
  ",": "tile-dirt2",
  "#": "tile-tree",
  H: "tile-wall",
  R: "tile-roof",
  D: "tile-door",
  W: "tile-water",
  B: "tile-bed",
  U: "tile-bed",
  C: "tile-crate",
  S: "tile-crate",
  F: "tile-floor",
  "^": "tile-cliff",
  N: "tile-tent",
  E: "tile-tent",
  P: "tile-floor",
  K: "tile-grass",
  I: "tile-grass",
  V: "tile-grass",
  A: "tile-grass",
  Q: "tile-grass",
  M: "tile-grass",
  G: "tile-grass",
  L: "tile-grass",
  X: "tile-grass",
  J: "tile-grass",
  "*": "tile-flower",
  Z: "tile-dirt",
  Y: "tile-dirt",
  O: "tile-dirt",
  "1": "tile-grass",
  "2": "tile-grass",
  "3": "tile-dirt",
  "8": "tile-dirt",
  "9": "tile-dirt",
};

export const SPEAKER_NAME: Record<SpeakerId, string> = {
  max: "Max",
  anne: "Anne",
  mason: "Mason",
  wren: "Wren",
  mae: "Mae",
  ivo: "Ivo",
  nell: "Nell",
  pike: "Pike",
  calder: "Calder",
  bram: "Bram",
  cathleen: "Cathleen",
  shinigami: "Shinigami",
  none: "",
};

export const INTRO = [
  "The cottage is quiet. Father sleeps. CryTown drums like a fever.",
  "Max is eight. Enemy soldiers are already in the grass.",
  "Father is too sick to stand. His Capture Crystal sits on the shelf.",
  "Quillpup is inside it. She will take the CryMon. The door can wait.",
];

export const ENDING_WIN = [
  "Calder sits in the mud and laughs once, without humour.",
  '"Fine. The camp takes strays. Keep that hound close. The war does not care that you are eight."',
  "South, drums. Max checks the crystals. They are fewer than she thought.",
  "CRYMON — the road continues. Walk. Catch. Survive.",
];

export function solidTile(ch: string) {
  return "#HWRBC^NKEVAQXUJI".includes(ch);
}

export function doorTile(ch: string) {
  return ch === "D";
}

export function spawnOf(map: string[], mark: string) {
  for (let y = 0; y < map.length; y++) {
    const x = map[y]!.indexOf(mark);
    if (x >= 0) return { x: x * TILE + TILE / 2, y: y * TILE + TILE / 2 };
  }
  return { x: TILE * 2, y: TILE * 2 };
}

export const START_BAG: Record<ItemId, number> = {
  gem: 0,
  salve: 2,
  bitterroot: 1,
  dust: 1,
  bandage: 2,
};

export const START_MARKS = 16;

export function healAmount(id: ItemId) {
  if (id === "salve") return 22;
  if (id === "bandage") return 12;
  return 0;
}

export const TALK = {
  father: [
    { speaker: "max", text: "There's a war. CryTown is already bleeding." },
    { speaker: "max", text: "You're too sick to defend it from the soldiers. I know that." },
    { speaker: "max", text: "So I'm stealing your CryMon." },
    { speaker: "none", text: "Father does not wake. The Capture Crystal is still on the shelf." },
  ],
  fatherAfter: [
    { speaker: "max", text: "I already took Quillpup. Sleep. I'll do the fighting." },
    { speaker: "none", text: "His breath is thin. He does not answer." },
  ],
  bed: [
    { speaker: "max", text: "Just until they breathe again." },
    { speaker: "none", text: "Max's empty bed. The CryMon sleep. Cuts close. Specials return." },
  ],
  shelf: [
    { speaker: "max", text: "This is it. Father's crystal. Quillpup is inside." },
    { speaker: "none", text: "The crystal breaks warm in her hands. Quillpup shakes out onto the floorboards." },
    { speaker: "max", text: "You're coming. CryTown doesn't get to fall." },
  ],
  shelfEmpty: [{ speaker: "max", text: "Dust. The crystal is already open." }],
  doorLocked: [
    { speaker: "max", text: "Not yet. Father's CryMon is still on the shelf." },
  ],
  crate: [
    { speaker: "max", text: "A wrap. He won't miss it." },
    { speaker: "none", text: "A linen wrap under the lid. You take it." },
  ],
  crateEmpty: [{ speaker: "max", text: "Splinters and a moth. Empty." }],
  doorOut: [
    { speaker: "max", text: "Night air. I can do this." },
    { speaker: "none", text: "Tall grass hides CryMon. Wren west. Pond east. Bram on the path. Calder south." },
  ],
  footsteps: [{ speaker: "none", text: "Footsteps on the path. Someone followed you out." }],
  masonFight: [
    { speaker: "mason", text: "You walked out with that hound." },
    { speaker: "max", text: "He's mine." },
    { speaker: "mason", text: "I already caught a CryMon. Fight me." },
  ],
  masonAfter: [
    { speaker: "mason", text: "Fine. Calder is still south." },
    { speaker: "max", text: "I won't die first." },
  ],
  masonWin: [{ speaker: "none", text: "Mason spits in the dirt. The path is yours. Calder still waits south." }],
  wrenFirst: [
    { speaker: "wren", text: "Too young. Take the salve. Calder camps south." },
    { speaker: "max", text: "I'm not too young." },
    { speaker: "wren", text: "West is Ivo. East is Nell. Keep that hound fed." },
  ],
  wrenBeat: [
    { speaker: "wren", text: "You beat him. The war still wants more of us." },
    { speaker: "max", text: "Then it can wait." },
  ],
  wrenCart: [
    { speaker: "wren", text: "You found their letter. They already knew your name." },
    { speaker: "max", text: "I read it anyway." },
  ],
  wrenHeal: [
    { speaker: "wren", text: "Cuts bound. Specials return. Keep them fed." },
    { speaker: "max", text: "Thank you." },
  ],
  maeFirst: [
    { speaker: "mae", text: "You're Max. I watched you leave the house." },
    { speaker: "max", text: "Don't follow me." },
    { speaker: "mae", text: "I won't. Take the wrap. Wren heals. I just didn't want the path empty." },
  ],
  maeAgain: [
    { speaker: "mae", text: "I'll be here. South still drums." },
    { speaker: "max", text: "I hear them." },
  ],
  ivoFirst: [
    { speaker: "ivo", text: "Camp took my CryMon. Chew this. Calder sits south." },
    { speaker: "max", text: "I'm going south anyway." },
    { speaker: "ivo", text: "Don't give him a clean fight." },
  ],
  ivoAgain: [
    { speaker: "ivo", text: "Hit first. Run if the bat folds you." },
    { speaker: "max", text: "I don't run yet." },
  ],
  nellFirst: [
    { speaker: "nell", text: "Too young. Drink this anyway. Reeds hide a stone." },
    { speaker: "max", text: "I can hold a crystal." },
  ],
  nellBonus: [
    { speaker: "nell", text: "That moth wasn't yours yesterday. Another salve." },
    { speaker: "max", text: "I caught it fair." },
  ],
  nellAgain: [
    { speaker: "nell", text: "The pond keeps secrets. South still drums." },
    { speaker: "max", text: "I hear them." },
  ],
  pikeFirst: [
    { speaker: "pike", text: "I dropped a moonstone in the east reeds. Don't tell Wren." },
    { speaker: "max", text: "I won't tell Wren." },
  ],
  pikeHelp: [
    { speaker: "pike", text: "You found it? Keep the stone. Take this wrap." },
    { speaker: "max", text: "I was only looking." },
  ],
  pikeDone: [
    { speaker: "pike", text: "The cliffs are just rocks. The war is the scary part." },
    { speaker: "max", text: "I know." },
  ],
  pikeHint: [{ speaker: "pike", text: "East of the path. In the tall grass by the water." }],
  herb: [{ speaker: "max", text: "Bitterroot. STR +4 if I last." }],
  herbGone: [{ speaker: "max", text: "A hole where the herb was. Only grit." }],
  gemPike: [{ speaker: "max", text: "Pike's moonstone. He said keep it." }],
  gemWild: [{ speaker: "max", text: "A Capture Crystal. Someone small lost this." }],
  gemGone: [{ speaker: "max", text: "Mud and a frog. The stone is already mine." }],
  stump: [{ speaker: "max", text: "A wrap jammed in the stump. I take it." }],
  stumpGone: [{ speaker: "max", text: "Just a stump. Ants. No more cloth." }],
  cart: [
    { speaker: "max", text: "They already knew my name." },
    { speaker: "none", text: "A camp letter on the wreck: send the cottage girl south. We need bodies." },
  ],
  calderAfter: [
    { speaker: "calder", text: "South is the camp. Don't die stupid." },
    { speaker: "max", text: "I don't plan to." },
  ],
  calderFight: [
    { speaker: "calder", text: "The camp takes strays." },
    { speaker: "max", text: "I'm not stray." },
  ],
  forestEnter: [
    { speaker: "max", text: "The trees close over the path." },
    { speaker: "none", text: "Tall grass. Patrols. If they see you, they will come. The path keeps south." },
  ],
  forestLeave: [{ speaker: "max", text: "Back toward the cottage path." }],
  groveEnter: [
    { speaker: "max", text: "The grass dies out. Stone and hush." },
    { speaker: "none", text: "No tall grass. Something waits on the path." },
  ],
  groveLeave: [{ speaker: "max", text: "Back under the trees." }],
  cathleenSpot: [
    { speaker: "cathleen", text: "You walked the path. I am the path's answer." },
    { speaker: "max", text: "You're a CryMon." },
    { speaker: "cathleen", text: "I am Cathleen. I fight as myself." },
  ],
  cathleenAfter: [
    { speaker: "cathleen", text: "You stand. Come again if you mean to keep me." },
    { speaker: "max", text: "I might." },
  ],
  cathleenGone: [{ speaker: "max", text: "Only the hood's shadow. She's with me now." }],
  shinigamiSpot: [
    { speaker: "shinigami", text: "Three names. Three graves. I keep them." },
    { speaker: "max", text: "You're in the way." },
    { speaker: "shinigami", text: "CryMare. Come." },
  ],
  shinigamiAfter: [
    { speaker: "shinigami", text: "The mares return to fog. You may pass." },
    { speaker: "max", text: "I will." },
  ],
  shinigamiDone: [{ speaker: "shinigami", text: "The graves are quiet. Go." }],
  soldierSpot: [
    { speaker: "none", text: "A soldier sees you. \"You there! This wood is camp ground.\"" },
    { speaker: "max", text: "I'm passing through." },
  ],
  soldierAfter: [{ speaker: "none", text: "The soldier sits. \"Go. Before I change my mind.\"" }],
  soldierDone: [{ speaker: "none", text: "They already lost. They will not rise." }],
  bramOpen: [
    { speaker: "bram", text: "Marks for moss, wraps, stones. Buy or sell." },
    { speaker: "max", text: "I have cuts. I need stones." },
  ],
  anneGift: [
    { speaker: "anne", text: "Max. You actually fought." },
    { speaker: "anne", text: "Take these. Five crystals. Don't waste them on the first moth." },
    { speaker: "max", text: "I won't." },
    { speaker: "none", text: "Anne presses five Capture Crystals into Max's palm. Xtals +5." },
  ],
  anneAgain: [
    { speaker: "anne", text: "Don't lose those. Calder is still south." },
    { speaker: "max", text: "I know the way." },
  ],
  cottage: [{ speaker: "max", text: "The cottage. Father in the bed. My bed. South door leaves." }],
  lose: [{ speaker: "max", text: "We still breathe. Crawl back." }],
} satisfies Record<string, TalkBeat[]>;
