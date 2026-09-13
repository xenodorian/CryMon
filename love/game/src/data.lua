-- src/data.lua
-- Static game data: species, items, maps, dialogue, formulas.
-- Ported from native/crymon.c (primary reference) and src/game/data.ts
-- (cross-checked for text/constants). Where the two disagreed, the choice
-- made is noted inline with a comment.

local data = {}

data.TILE = 32
data.VIEW_W = 640
data.VIEW_H = 480
data.PARTY_MAX = 6

-- Species table: id, name, basic move, special move, maxHp, str, agl, spc, specialPp, wild
data.SPECIES = {
  quillpup   = { id = "quillpup",   name = "Quillpup",   basic = "Nip",        special = "Quillburst", maxHp = 34, str = 15, agl = 10, spc = 7,  spp = 3, wild = false },
  glimmoth   = { id = "glimmoth",   name = "Glimmoth",   basic = "Dustwing",   special = "Lampflare",  maxHp = 26, str = 7,  agl = 13, spc = 16, spp = 3, wild = true },
  tortcask   = { id = "tortcask",   name = "Tortcask",   basic = "Shove",      special = "Shellslam",  maxHp = 42, str = 13, agl = 5,  spc = 8,  spp = 3, wild = true },
  razorbat   = { id = "razorbat",   name = "Razorbat",   basic = "Rake",       special = "Swoopcut",   maxHp = 30, str = 14, agl = 16, spc = 9,  spp = 3, wild = false },
  mossback   = { id = "mossback",   name = "Mossback",   basic = "Squelch",    special = "Mossguard",  maxHp = 38, str = 12, agl = 6,  spc = 11, spp = 3, wild = true },
  briarfox   = { id = "briarfox",   name = "Briarfox",   basic = "Bramble",    special = "Thornrush",  maxHp = 28, str = 13, agl = 17, spc = 10, spp = 3, wild = true },
  fenwisp    = { id = "fenwisp",    name = "Fenwisp",    basic = "Glim",       special = "Fenflare",   maxHp = 24, str = 8,  agl = 16, spc = 17, spp = 3, wild = true },
  duskhorn   = { id = "duskhorn",   name = "Duskhorn",   basic = "Gore",       special = "Duskram",    maxHp = 36, str = 16, agl = 8,  spc = 7,  spp = 3, wild = true },
  needleroot = { id = "needleroot", name = "Needleroot", basic = "Prick",      special = "Sapdrain",   maxHp = 32, str = 12, agl = 7,  spc = 14, spp = 3, wild = true },
  cathleen   = { id = "cathleen",   name = "Cathleen",   basic = "Fire Bolt",  special = "Mana Surge", maxHp = 38, str = 11, agl = 13, spc = 19, spp = 4, wild = true },
  crymare    = { id = "crymare",    name = "CryMare",    basic = "Wail",       special = "Nightbridle",maxHp = 30, str = 9,  agl = 14, spc = 18, spp = 3, wild = false },
}

data.ITEM_ORDER = { "salve", "bandage", "bitterroot", "dust", "gem" }
data.ITEMS = {
  gem        = { id = "gem",        name = "Capture Crystal", buy = 20, sell = 10 },
  salve      = { id = "salve",      name = "Moss salve",      buy = 10, sell = 5 },
  bitterroot = { id = "bitterroot", name = "Bitterroot",      buy = 8,  sell = 4 },
  dust       = { id = "dust",       name = "Ash dust",        buy = 8,  sell = 4 },
  bandage    = { id = "bandage",    name = "Linen wrap",      buy = 6,  sell = 3 },
}

function data.healAmount(id)
  if id == "salve" then return 22 end
  if id == "bandage" then return 12 end
  return 0
end

-- ===== Formulas =====

-- Capture chance: 5% per foe agility, +1% per % of foe HP missing, +25%
-- if any foe stat has been lowered this fight. crymon.c and data.ts agree.
function data.captureChance(agl, hp, maxHp, vulnerable)
  local missing = 0
  if maxHp > 0 then missing = math.floor((maxHp - hp) * 100 / maxHp) end
  local chance = 5 * agl + missing
  if vulnerable then chance = chance + 25 end
  if chance < 0 then chance = 0 end
  if chance > 100 then chance = 100 end
  return chance
end

function data.specOf(id)
  return data.SPECIES[id] or data.SPECIES.quillpup
end

-- Mint a monster of species `id` at level `lv`. Growth curve and rounding
-- match crymon.c (round-half-up via +0.5 floor) and data.ts (Math.round) —
-- these agree for all positive values used here.
function data.mintMonster(id, lv)
  local s = data.specOf(id)
  lv = math.max(1, lv or 3)
  local g = 1 + (lv - 3) * 0.12
  local m = {
    id = id .. "-" .. tostring(math.random(1000, 9999)),
    species = id,
    name = s.name,
    maxHp = math.floor(s.maxHp * g + 0.5),
    str = math.floor(s.str * g + 0.5),
    agl = math.floor(s.agl * g + 0.5),
    spc = math.floor(s.spc * g + 0.5),
    spp = s.spp,
    sppMax = s.spp,
    lv = lv,
    xp = 0,
  }
  m.hp = m.maxHp
  return m
end

-- XP curve: +6 + 4*foeLevel per win, level up while xp >= lv*10 (cap lv 12).
-- Matches crymon.c grant() and data.ts grantXp() exactly.
function data.grantXp(m, foeLv)
  m.xp = m.xp + 6 + foeLv * 4
  while m.xp >= m.lv * 10 and m.lv < 12 do
    m.xp = m.xp - m.lv * 10
    m.lv = m.lv + 1
    m.maxHp = m.maxHp + 3
    m.hp = math.min(m.maxHp, m.hp + 3)
    m.str = m.str + 1
    m.agl = m.agl + 1
    m.spc = m.spc + 1
  end
end

-- ===== Maps =====
-- Row-strings identical to crymon.c / data.ts. Index 1 = house, 2 = veld,
-- 3 = forest, 4 = grove (Lua 1-based).

data.HOUSE = {
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
}

data.VELD = {
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
}

data.FOREST = {
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
}

-- Grove: data.ts inserts a locked door row ("#############D############")
-- splitting the Cathleen half from the Shinigami half, opened only after
-- Cathleen is caught (useDoor() in engine.ts). crymon.c dropped that row
-- entirely (no lock at all — you can walk straight to Shinigami). We keep
-- the TS behaviour: it reads as an intentional gate ("She fights as
-- herself" / graves finale should come after), and crymon.c's inspect
-- harness never exercises that door, so the omission looks like a
-- simplification rather than a deliberate fix. See warp/door handling in
-- state.lua (groveDoorLocked).
data.GROVE = {
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
  "#############D############",
  "##.........=====........##",
  "##..........===.........##",
  "##.........=====........##",
  "##..........===.........##",
  "##...........9..........##",
  "###....................###",
  "##########################",
}

data.MAPS = { data.HOUSE, data.VELD, data.FOREST, data.GROVE }
-- map ids: 1=house 2=veld 3=forest 4=grove

function data.mapDims(map)
  local w, h = 0, #map
  for _, row in ipairs(map) do if #row > w then w = #row end end
  return w, h
end

-- Exact solid-tile set from crymon.c's solid(): note 'D' (door) is
-- deliberately absent -- doors must be walkable so stepping onto them
-- triggers a warp. Grove's extra door-gate ('D' mid-map, see GROVE above)
-- is handled specially in state.lua instead of here.
local SOLID_SET = {}
for c in string.gmatch("#HWRBC^NKEVAQXUJSLI", ".") do SOLID_SET[c] = true end
function data.isSolidTile(ch)
  return SOLID_SET[ch] == true
end

function data.tileAt(map, tx, ty)
  local w, h = data.mapDims(map)
  if ty < 0 or ty >= h or tx < 0 or tx >= w then return "#" end
  local row = map[ty + 1]
  if tx + 1 > #row then return "#" end
  return row:sub(tx + 1, tx + 1)
end

function data.spawnOf(map, mark)
  for y, row in ipairs(map) do
    local x = row:find(mark, 1, true)
    if x then
      return (x - 1) * data.TILE + data.TILE / 2, (y - 1) * data.TILE + data.TILE / 2
    end
  end
  return data.TILE * 2, data.TILE * 2
end

data.START_BAG = { gem = 0, salve = 2, bitterroot = 1, dust = 1, bandage = 2 }
data.START_MARKS = 16

data.SPEAKER_NAME = {
  max = "Max", anne = "Anne", mason = "Mason", wren = "Wren", mae = "Mae",
  ivo = "Ivo", nell = "Nell", pike = "Pike", calder = "Calder", bram = "Bram",
  cathleen = "Cathleen", shinigami = "Shinigami", soldier = "", none = "",
}

-- ===== Dialogue (verbatim from src/game/data.ts TALK table) =====
-- Each entry is a list of {speaker=, text=} beats. speaker "none" / "" means
-- a narration line with no portrait, matching crymon.c's say/sayn.

data.TALK = {
  father = {
    { speaker = "max", text = "There's a war. CryTown is already bleeding." },
    { speaker = "max", text = "You're too sick to defend it from the soldiers. I know that." },
    { speaker = "max", text = "So I'm stealing your CryMon." },
    { speaker = "none", text = "Father does not wake. The Capture Crystal is still on the shelf." },
  },
  fatherAfter = {
    { speaker = "max", text = "I already took Quillpup. Sleep. I'll do the fighting." },
    { speaker = "none", text = "His breath is thin. He does not answer." },
  },
  bed = {
    { speaker = "max", text = "Just until they breathe again." },
    { speaker = "none", text = "Max's empty bed. The CryMon sleep. Cuts close. Specials return." },
  },
  shelf = {
    { speaker = "max", text = "This is it. Father's crystal. Quillpup is inside." },
    { speaker = "none", text = "The crystal breaks warm in her hands. Quillpup shakes out onto the floorboards." },
    { speaker = "max", text = "You're coming. CryTown doesn't get to fall." },
  },
  shelfEmpty = { { speaker = "max", text = "Dust. The crystal is already open." } },
  doorLocked = { { speaker = "max", text = "Not yet. Father's CryMon is still on the shelf." } },
  crate = {
    { speaker = "max", text = "A wrap. He won't miss it." },
    { speaker = "none", text = "A linen wrap under the lid. You take it." },
  },
  crateEmpty = { { speaker = "max", text = "Splinters and a moth. Empty." } },
  doorOut = {
    { speaker = "max", text = "Night air. I can do this." },
    { speaker = "none", text = "Tall grass hides CryMon. Wren west. Pond east. Bram on the path. Calder south." },
  },
  footsteps = { { speaker = "none", text = "Footsteps on the path. Someone followed you out." } },
  masonFight = {
    { speaker = "mason", text = "You walked out with that hound." },
    { speaker = "max", text = "He's mine." },
    { speaker = "mason", text = "I already caught a CryMon. Fight me." },
  },
  masonAfter = {
    { speaker = "mason", text = "Fine. Calder is still south." },
    { speaker = "max", text = "I won't die first." },
  },
  masonWin = { { speaker = "none", text = "Mason spits in the dirt. The path is yours. Calder still waits south." } },
  wrenFirst = {
    { speaker = "wren", text = "Too young. Take the salve. Calder camps south." },
    { speaker = "max", text = "I'm not too young." },
    { speaker = "wren", text = "West is Ivo. East is Nell. Keep that hound fed." },
  },
  wrenBeat = {
    { speaker = "wren", text = "You beat him. The war still wants more of us." },
    { speaker = "max", text = "Then it can wait." },
  },
  wrenCart = {
    { speaker = "wren", text = "You found their letter. They already knew your name." },
    { speaker = "max", text = "I read it anyway." },
  },
  wrenHeal = {
    { speaker = "wren", text = "Cuts bound. Specials return. Keep them fed." },
    { speaker = "max", text = "Thank you." },
  },
  maeFirst = {
    { speaker = "mae", text = "You're Max. I watched you leave the house." },
    { speaker = "max", text = "Don't follow me." },
    { speaker = "mae", text = "I won't. Take the wrap. Wren heals. I just didn't want the path empty." },
  },
  maeAgain = {
    { speaker = "mae", text = "I'll be here. South still drums." },
    { speaker = "max", text = "I hear them." },
  },
  ivoFirst = {
    { speaker = "ivo", text = "Camp took my CryMon. Chew this. Calder sits south." },
    { speaker = "max", text = "I'm going south anyway." },
    { speaker = "ivo", text = "Don't give him a clean fight." },
  },
  ivoAgain = {
    { speaker = "ivo", text = "Hit first. Run if the bat folds you." },
    { speaker = "max", text = "I don't run yet." },
  },
  nellFirst = {
    { speaker = "nell", text = "Too young. Drink this anyway. Reeds hide a stone." },
    { speaker = "max", text = "I can hold a crystal." },
  },
  nellBonus = {
    { speaker = "nell", text = "That moth wasn't yours yesterday. Another salve." },
    { speaker = "max", text = "I caught it fair." },
  },
  nellAgain = {
    { speaker = "nell", text = "The pond keeps secrets. South still drums." },
    { speaker = "max", text = "I hear them." },
  },
  pikeFirst = {
    { speaker = "pike", text = "I dropped a moonstone in the east reeds. Don't tell Wren." },
    { speaker = "max", text = "I won't tell Wren." },
  },
  pikeHelp = {
    { speaker = "pike", text = "You found it? Keep the stone. Take this wrap." },
    { speaker = "max", text = "I was only looking." },
  },
  pikeDone = {
    { speaker = "pike", text = "The cliffs are just rocks. The war is the scary part." },
    { speaker = "max", text = "I know." },
  },
  pikeHint = { { speaker = "pike", text = "East of the path. In the tall grass by the water." } },
  herb = { { speaker = "max", text = "Bitterroot. STR +4 if I last." } },
  herbGone = { { speaker = "max", text = "A hole where the herb was. Only grit." } },
  gemPike = { { speaker = "max", text = "Pike's moonstone. He said keep it." } },
  gemWild = { { speaker = "max", text = "A Capture Crystal. Someone small lost this." } },
  gemGone = { { speaker = "max", text = "Mud and a frog. The stone is already mine." } },
  stump = { { speaker = "max", text = "A wrap jammed in the stump. I take it." } },
  stumpGone = { { speaker = "max", text = "Just a stump. Ants. No more cloth." } },
  cart = {
    { speaker = "max", text = "They already knew my name." },
    { speaker = "none", text = "A camp letter on the wreck: send the cottage girl south. We need bodies." },
  },
  calderAfter = {
    { speaker = "calder", text = "South is the camp. Don't die stupid." },
    { speaker = "max", text = "I don't plan to." },
  },
  calderFight = {
    { speaker = "calder", text = "The camp takes strays." },
    { speaker = "max", text = "I'm not stray." },
  },
  forestEnter = {
    { speaker = "max", text = "The trees close over the path." },
    { speaker = "none", text = "Tall grass. Patrols. If they see you, they will come. The path keeps south." },
  },
  forestLeave = { { speaker = "max", text = "Back toward the cottage path." } },
  groveEnter = {
    { speaker = "max", text = "The grass dies out. Stone and hush." },
    { speaker = "none", text = "No tall grass. Something waits on the path." },
  },
  groveLeave = { { speaker = "max", text = "Back under the trees." } },
  groveDoorLocked = { { speaker = "max", text = "Barred shut. Not while she's still standing between us." } },
  cathleenSpot = {
    { speaker = "cathleen", text = "You walked the path. I am the path's answer." },
    { speaker = "max", text = "You're a CryMon." },
    { speaker = "cathleen", text = "I am Cathleen. I fight as myself." },
  },
  cathleenAfter = {
    { speaker = "cathleen", text = "You stand. Come again if you mean to keep me." },
    { speaker = "max", text = "I might." },
  },
  cathleenGone = { { speaker = "max", text = "Only the hood's shadow. She's with me now." } },
  shinigamiSpot = {
    { speaker = "shinigami", text = "Three names. Three graves. I keep them." },
    { speaker = "max", text = "You're in the way." },
    { speaker = "shinigami", text = "CryMare. Come." },
  },
  shinigamiAfter = {
    { speaker = "shinigami", text = "The mares return to fog. You may pass." },
    { speaker = "max", text = "I will." },
  },
  shinigamiDone = { { speaker = "shinigami", text = "The graves are quiet. Go." } },
  soldierSpot = {
    { speaker = "none", text = "A soldier sees you. \"You there! This wood is camp ground.\"" },
    { speaker = "max", text = "I'm passing through." },
  },
  soldierAfter = { { speaker = "none", text = "The soldier sits. \"Go. Before I change my mind.\"" } },
  soldierDone = { { speaker = "none", text = "They already lost. They will not rise." } },
  bramOpen = {
    { speaker = "bram", text = "Marks for moss, wraps, stones. Buy or sell." },
    { speaker = "max", text = "I have cuts. I need stones." },
  },
  anneGift = {
    { speaker = "anne", text = "Max. You actually fought." },
    { speaker = "anne", text = "Take these. Five crystals. Don't waste them on the first moth." },
    { speaker = "max", text = "I won't." },
    { speaker = "none", text = "Anne presses five Capture Crystals into Max's palm. Xtals +5." },
  },
  anneAgain = {
    { speaker = "anne", text = "Don't lose those. Calder is still south." },
    { speaker = "max", text = "I know the way." },
  },
  cottage = { { speaker = "max", text = "The cottage. Father in the bed. My bed. South door leaves." } },
  lose = { { speaker = "max", text = "We still breathe. Crawl back." } },
}

data.INTRO = {
  "The cottage is quiet. Father sleeps. CryTown drums like a fever.",
  "Max is eight. Enemy soldiers are already in the grass.",
  "Father is too sick to stand. His Capture Crystal sits on the shelf.",
  "Quillpup is inside it. She will take the CryMon. The door can wait.",
}

data.ENDING_WIN = {
  "Calder sits in the mud and laughs once, without humour.",
  "\"Fine. The camp takes strays. Keep that hound close. The war does not care that you are eight.\"",
  "South, drums. Max checks the crystals. They are fewer than she thought.",
  "CRYMON -- the road continues. Walk. Catch. Survive.",
}

data.DEMO_END = {
  "Shinigami kneels. The mares fade back into fog.",
  "The grove goes quiet. The graves keep their names.",
  "Thank you for playing the demo of CryMon.",
}

return data
