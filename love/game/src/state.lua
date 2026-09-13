-- src/state.lua
-- The whole game state machine: world movement, NPC/soldier AI, dialogue,
-- battle math, catching, menus. A faithful Lua port of native/crymon.c
-- (primary reference), cross-checked against src/game/engine.ts + data.ts.
-- Disagreements between the two are called out inline where they matter;
-- see also the notes in src/data.lua about the grove door and the shop.

local data = require("src.data")
local input = require("src.input")
local draw = require("src.draw")

local M = {}

local MODE = {
  TITLE = "title", WORLD = "world", BATTLE = "battle", TALK = "talk",
  BAG = "bag", PARTY = "party", SHOP = "shop", ENDING = "ending", DEMOEND = "demoend",
}
M.MODE = MODE

-- map ids (1-based, unlike crymon.c's 0-based house/veld/forest/grove)
local MAP_HOUSE, MAP_VELD, MAP_FOREST, MAP_GROVE = 1, 2, 3, 4

local function irand(a, b) return love.math.random(a, b) end
local function clampf(v, a, b) if v < a then return a elseif v > b then return b else return v end end
local function clampi(v, a, b) if v < a then return a elseif v > b then return b else return v end end

local function shallowcopy(t)
  local r = {}
  for k, v in pairs(t) do r[k] = v end
  return r
end

-- ===== construction =====

function M.new()
  local G = {
    mode = MODE.TITLE,
    mapId = MAP_HOUSE,
    px = 0, py = 0, pdir = "down", pframe = 0, moving = false, panim = 0,
    clockt = 0,
    party = {}, lead = 1,
    bag = shallowcopy(data.START_BAG),
    marks = data.START_MARKS,
    -- NPC/world flags
    talkedWren = false, talkedMae = false, talkedIvo = false, talkedNell = false,
    talkedPike = false, pikeHelped = false, nellBonus = false,
    beatCalder = false, caughtOnce = false, battles = 0, anneGift = false,
    beatShin = false, cathCaught = false, beatMason = false,
    gotHerb = false, gotGem = false, gotStump = false, readCart = false,
    lootedCrate = false, gotShelf = false,
    annePh = 0, ax = 0, ay = 0, aanim = 0, adir = "down", aframe = 0,
    masonPh = 0, mxm = 0, mym = 0, manim = 0, mdir = "down", mframe = 0,
    sols = {}, nsol = 0,
    doorLock = 0, lastTx = -1, lastTy = -1, encLock = 8,
    hud = "", hudT = 0,
    -- talk
    talk = {}, talkI = 1, afterTalk = 0,
    -- battle
    bWild = true, bPhase = 0, bPl = nil, bFoe = nil, bBench = {}, nbench = 0,
    bFoeName = "", bTrainer = "", bMsg = {}, bMsgI = 1, bAfter = 0,
    bCur = 1, bMenu = {}, bDmg = 0,
    modsSelfStr = 0, modsFoeStr = 0, modsFoeAgl = 0, modsFoeSpc = 0,
    bT = 0, mg = 0,
    -- shop
    shopTab = "buy", shopCursor = 1,
    -- party/bag menu cursors
    partyCursor = 1,
    -- intro / ending sequencing
    introI = 1, endingI = 1,
  }
  return G
end

-- ===== small helpers =====

local function curMap(G) return data.MAPS[G.mapId] end
local function mapDims(G) return data.mapDims(curMap(G)) end

local function tileAtPix(G, x, y)
  return data.tileAt(curMap(G), math.floor(x / data.TILE), math.floor(y / data.TILE))
end

local function leader(G)
  if #G.party == 0 then return nil end
  if G.lead >= 1 and G.lead <= #G.party and G.party[G.lead].hp > 0 then return G.party[G.lead] end
  for i, m in ipairs(G.party) do
    if m.hp > 0 then G.lead = i; return m end
  end
  return nil
end

local function note(G, s)
  G.hud = s
  G.hudT = 8
end

local function distSq(x1, y1, x2, y2)
  local dx, dy = x1 - x2, y1 - y2
  return dx * dx + dy * dy
end

local function hitActor(x, y, ax, ay, hw, hh)
  return math.abs(ax - x) < hw and math.abs(ay - y) < hh
end

-- ===== dialogue =====

local function beatsToTalk(beats)
  local out = {}
  for _, b in ipairs(beats) do
    out[#out + 1] = { who = data.SPEAKER_NAME[b.speaker] or "", text = b.text }
  end
  return out
end

local function say1(G, who, text)
  G.talk = { { who = who, text = text } }
  G.talkI = 1
  G.mode = MODE.TALK
  G.afterTalk = 0
end

local function sayn(G, beats, after)
  G.talk = beatsToTalk(beats)
  G.talkI = 1
  G.afterTalk = after or 0
  G.mode = MODE.TALK
end

-- ===== battle setup =====

local function startBattle(G, foe, wild, title, trainer)
  local L = leader(G)
  if not L then return end
  G.bPl = shallowcopy(L)
  G.bFoe = shallowcopy(foe)
  G.bWild = wild
  G.bTrainer = trainer
  G.bFoeName = wild and foe.name or trainer
  G.bPhase = 0
  G.bMsg = { title .. "!" }
  G.bMsgI = 1
  G.bAfter = 1
  G.bT = 0
  G.modsSelfStr, G.modsFoeStr, G.modsFoeAgl, G.modsFoeSpc = 0, 0, 0, 0
  G.mode = MODE.BATTLE
  G.nbench = 0
  G.bBench = {}
end

local function captureChanceNow(G)
  local vulnerable = G.modsFoeStr < 0 or G.modsFoeAgl < 0 or G.modsFoeSpc < 0
  return data.captureChance(G.bFoe.agl, G.bFoe.hp, G.bFoe.maxHp, vulnerable)
end

local function fillItemMenu(G)
  local rows = {}
  rows[#rows + 1] = { label = "Pass", kind = "pass" }
  if G.bag.salve > 0 then rows[#rows + 1] = { label = ("Moss salve x%d"):format(G.bag.salve), kind = "salve" } end
  if G.bag.bandage > 0 then rows[#rows + 1] = { label = ("Linen wrap x%d"):format(G.bag.bandage), kind = "bandage" } end
  if G.bag.bitterroot > 0 then rows[#rows + 1] = { label = ("Bitterroot x%d"):format(G.bag.bitterroot), kind = "bitterroot" } end
  if G.bag.dust > 0 then rows[#rows + 1] = { label = ("Ash dust x%d"):format(G.bag.dust), kind = "dust" } end
  if G.bag.gem > 0 then
    if G.bWild then
      rows[#rows + 1] = { label = ("Capture Crystal %d%% x%d"):format(captureChanceNow(G), G.bag.gem), kind = "gem" }
    else
      rows[#rows + 1] = { label = ("Capture Crystal x%d"):format(G.bag.gem), kind = "gem" }
    end
  end
  G.bMenu = rows
  G.bCur = 1
end

local function fillAtkMenu(G)
  local s = data.specOf(G.bPl.species)
  local rows = {}
  if G.bPl.species == "cathleen" then
    rows = {
      { label = "Fire Bolt", kind = "firebolt" },
      { label = "Ice Beam", kind = "icebeam" },
      { label = "Lightning Strike", kind = "lightning" },
      { label = ("Mana Surge  %d/%d"):format(G.bPl.spp, G.bPl.sppMax), kind = "manasurge" },
    }
  else
    rows = {
      { label = s.basic, kind = "basic" },
      { label = ("%s  %d/%d"):format(s.special, G.bPl.spp, G.bPl.sppMax), kind = "special" },
      { label = "Wait", kind = "wait" },
    }
  end
  G.bMenu = rows
  G.bCur = 1
end

local function setMsg(G, msgs, after)
  G.bMsg = msgs
  G.bMsgI = 1
  G.bPhase = 0
  G.bAfter = after
end

local function maybeAnne(G)
  if G.anneGift or G.annePh ~= 0 then return end
  if G.battles < 1 or G.mapId ~= MAP_VELD then return end
  G.annePh = 1
  G.ax = G.px
  G.ay = G.py + 72
  G.adir = "up"
end

local function finishWin(G)
  G.party[G.lead] = G.bPl
  data.grantXp(G.party[G.lead], G.bFoe.lv)
  G.battles = G.battles + 1
  maybeAnne(G)
  if not G.bWild and G.bTrainer == "Calder" then
    G.beatCalder = true
    G.marks = G.marks + 18
    G.mode = MODE.ENDING
    G.endingI = 1
    return
  end
  local soldierId = G.bTrainer:match("^soldier:(.+)$")
  if soldierId then
    for _, s in ipairs(G.sols) do if s.id == soldierId then s.beaten = true end end
    G.marks = G.marks + 8
    G.mode = MODE.WORLD
    note(G, "The soldier sits.")
    return
  end
  if G.bTrainer == "Mason" then
    G.beatMason = true
    G.masonPh = 3
    G.marks = G.marks + 10
    G.mode = MODE.WORLD
    say1(G, "", "Mason spits in the dirt. The path is yours. Calder still waits south.")
    return
  end
  if G.bTrainer == "Shinigami" then
    -- crymon.c just prints a line and drops you back in the world here;
    -- engine.ts instead ends the demo on a dedicated screen (mode
    -- "demoEnd"). We follow engine.ts since the task calls for a real
    -- ending sequence, not a silent return to free movement.
    G.beatShin = true
    G.marks = G.marks + 14
    G.mode = MODE.DEMOEND
    G.endingI = 1
    return
  end
  G.marks = G.marks + 3
  G.mode = MODE.WORLD
  if G.bFoe.species == "cathleen" and not G.cathCaught then
    say1(G, "Cathleen", "You stand. Come again if you mean to keep me.")
  else
    note(G, "The grass goes still.")
  end
  G.encLock = 3
end

local function applyHit(G)
  G.bFoe.hp = G.bFoe.hp - G.bDmg
  if G.bFoe.hp < 0 then G.bFoe.hp = 0 end
  if G.bFoe.hp <= 0 then
    if G.nbench > 0 then
      data.grantXp(G.bPl, G.bFoe.lv)
      G.bFoe = G.bBench[1]
      if G.nbench == 2 then G.bBench[1] = G.bBench[2] end
      G.nbench = G.nbench - 1
      G.modsFoeStr, G.modsFoeAgl, G.modsFoeSpc = 0, 0, 0
      setMsg(G, { "It falls.", ("%s sends %s."):format(G.bFoeName, G.bFoe.name) }, 1)
      return
    end
    -- NOTE: crymon.c always names the player's *basic* move here even when
    -- a special/spell landed the finishing blow -- preserved verbatim for
    -- fidelity (see README for the full list of such quirks).
    setMsg(G, { ("%s  %d dmg."):format(data.specOf(G.bPl.species).basic, G.bDmg), ("%s falls."):format(G.bFoe.name) }, 5)
    return
  end
  setMsg(G, { ("Hit  %d dmg."):format(G.bDmg), "Choose a guard." }, 3)
end

local ITEM_KIND_FIELD = { salve = "salve", bandage = "bandage", bitterroot = "bitterroot", dust = "dust", gem = "gem" }

local function pickItem(G)
  local row = G.bMenu[G.bCur]
  if row.kind == "pass" then
    G.bPhase = 2
    fillAtkMenu(G)
    return
  end
  if row.kind == "salve" and G.bag.salve > 0 then
    G.bag.salve = G.bag.salve - 1
    local n = math.min(22, G.bPl.maxHp - G.bPl.hp)
    G.bPl.hp = G.bPl.hp + n
    setMsg(G, { ("Moss salve. %d HP."):format(n) }, 2)
    return
  elseif row.kind == "bandage" and G.bag.bandage > 0 then
    G.bag.bandage = G.bag.bandage - 1
    local n = math.min(12, G.bPl.maxHp - G.bPl.hp)
    G.bPl.hp = G.bPl.hp + n
    setMsg(G, { ("Linen wrap. %d HP."):format(n) }, 2)
    return
  elseif row.kind == "bitterroot" and G.bag.bitterroot > 0 then
    G.bag.bitterroot = G.bag.bitterroot - 1
    G.modsSelfStr = G.modsSelfStr + 4
    setMsg(G, { "Bitterroot. STR +4." }, 2)
    return
  elseif row.kind == "dust" and G.bag.dust > 0 then
    G.bag.dust = G.bag.dust - 1
    G.modsFoeStr = G.modsFoeStr - 3
    G.modsFoeAgl = G.modsFoeAgl - 2
    G.modsFoeSpc = G.modsFoeSpc - 2
    setMsg(G, { "Ash dust. Foe stats drop." }, 2)
    return
  elseif row.kind == "gem" and G.bag.gem > 0 then
    G.bag.gem = G.bag.gem - 1
    if not G.bWild then
      G.bag.gem = G.bag.gem + 1
      setMsg(G, { "Crystals will not take a tamer's CryMon." }, 2)
      return
    end
    if #G.party >= data.PARTY_MAX then
      G.bag.gem = G.bag.gem + 1
      setMsg(G, { "Six is all Max can hold." }, 2)
      return
    end
    local chance = captureChanceNow(G)
    if irand(1, 100) <= chance then
      local c = shallowcopy(G.bFoe)
      c.hp = math.max(1, math.floor(c.maxHp * 2 / 5))
      G.party[#G.party + 1] = c
      G.caughtOnce = true
      if c.species == "cathleen" then G.cathCaught = true end
      setMsg(G, { ("The crystal takes. %s is yours."):format(c.name) }, 6)
      return
    end
    setMsg(G, { "The crystal cracks dark. It slips free." }, 2)
    return
  end
  setMsg(G, { "Nothing happens." }, 2)
end

local function pickAtk(G)
  local s = data.specOf(G.bPl.species)
  if G.bPl.species == "cathleen" then
    local kind = G.bMenu[G.bCur].kind
    if kind == "firebolt" then
      G.modsFoeStr = G.modsFoeStr - 4
      G.bDmg = 5 + math.floor(G.bPl.spc / 3)
    elseif kind == "icebeam" then
      G.modsFoeAgl = G.modsFoeAgl - 4
      G.bDmg = 5 + math.floor(G.bPl.spc / 3)
    elseif kind == "lightning" then
      G.modsFoeSpc = G.modsFoeSpc - 4
      G.bDmg = 5 + math.floor(G.bPl.spc / 3)
    else -- manasurge
      if G.bPl.spp <= 0 then
        setMsg(G, { "Mana Surge is spent." }, 2)
        return
      end
      G.bPl.spp = G.bPl.spp - 1
      local deb = (G.modsFoeStr < 0 or G.modsFoeAgl < 0 or G.modsFoeSpc < 0) and 2 or 1
      G.bDmg = math.floor((11 + G.bPl.spc) * deb / 2)
    end
    applyHit(G)
    return
  end
  local kind = G.bMenu[G.bCur].kind
  if kind == "wait" then
    setMsg(G, { "Max holds." }, 3)
    return
  end
  if kind == "special" then
    if G.bPl.spp <= 0 then
      setMsg(G, { ("%s is spent."):format(s.special) }, 2)
      return
    end
    G.bPl.spp = G.bPl.spp - 1
    G.mg = 8
    G.bPhase = 4
    return
  end
  -- basic
  local atk = G.bPl.str + G.modsSelfStr
  local def = G.bFoe.str + G.modsFoeStr
  G.bDmg = math.max(1, 6 + math.floor(atk * 62 / 100) - math.floor(def * 16 / 100) + irand(0, 3))
  applyHit(G)
end

local function pickGuard(G)
  local dmg = math.max(1, 6 + math.floor((G.bFoe.str + G.modsFoeStr) * 6 / 10))
  if G.bCur == 1 and irand(0, 99) < 50 then
    dmg = 0
  elseif G.bCur == 2 then
    dmg = math.floor(dmg / 2) + 1
  else
    dmg = math.floor(dmg * 2 / 5) + 1
  end
  G.bPl.hp = math.max(0, G.bPl.hp - dmg)
  if G.bPl.hp <= 0 then
    G.party[G.lead] = G.bPl
    local nxt = nil
    for i, m in ipairs(G.party) do
      if i ~= G.lead and m.hp > 0 then nxt = i; break end
    end
    if nxt then
      G.lead = nxt
      G.bPl = shallowcopy(G.party[G.lead])
      setMsg(G, { ("%s jumps in."):format(G.bPl.name) }, 1)
      return
    end
    setMsg(G, { ("%s cannot stand."):format(G.bPl.name) }, 7)
    return
  end
  setMsg(G, { ("Took %d. Your turn."):format(dmg) }, 1)
end

-- ===== soldiers (forest) =====

local function ensureSoldiers(G)
  if G.nsol > 0 then return end
  local x, y
  x, y = data.spawnOf(data.FOREST, "1")
  G.sols[1] = { fx = x, fy = y, dir = "right", axis = 1, minv = x - 16, maxv = x + 144, sign = 1, lv = 4,
    id = "patrol", name = "Patrol", spec = "briarfox", beaten = false, chase = false, frame = 0, anim = 0 }
  x, y = data.spawnOf(data.FOREST, "2")
  G.sols[2] = { fx = x, fy = y, dir = "left", axis = 2, minv = y - 80, maxv = y + 80, sign = -1, lv = 4,
    id = "scout", name = "Scout", spec = "mossback", beaten = false, chase = false, frame = 0, anim = 0 }
  x, y = data.spawnOf(data.FOREST, "3")
  G.sols[3] = { fx = x, fy = y, dir = "up", axis = 0, lv = 5,
    id = "sentry", name = "Sentry", spec = "razorbat", beaten = false, chase = false, frame = 0, anim = 0 }
  G.nsol = 3
end

local function soldierLos(G, s)
  if s.beaten or s.chase then return false end
  local stx, sty = math.floor(s.fx / data.TILE), math.floor(s.fy / data.TILE)
  local ptx, pty = math.floor(G.px / data.TILE), math.floor(G.py / data.TILE)
  local dx = (s.dir == "left" and -1) or (s.dir == "right" and 1) or 0
  local dy = (s.dir == "up" and -1) or (s.dir == "down" and 1) or 0
  if dx == 0 and dy == 0 then return false end
  local w, h = mapDims(G)
  local maxr = math.max(w, h)
  for i = 1, maxr do
    local tx, ty = stx + dx * i, sty + dy * i
    local ch = data.tileAt(data.FOREST, tx, ty)
    if data.isSolidTile(ch) then return false end
    if tx == ptx and ty == pty then return true end
  end
  return false
end

-- ===== collision =====

local function blocked(G, x, y)
  local r = 10
  local pts = { { x - r, y }, { x + r, y }, { x, y - 2 }, { x, y + r } }
  for _, p in ipairs(pts) do
    if data.isSolidTile(tileAtPix(G, p[1], p[2])) then return true end
  end
  if G.mapId == MAP_GROVE then
    -- gate row added vs crymon.c (see src/data.lua note on GROVE): blocks
    -- the mid-map door tile until Cathleen is caught.
    if not G.cathCaught then
      for _, p in ipairs(pts) do
        if tileAtPix(G, p[1], p[2]) == "D" then return true end
      end
    end
  end
  if G.mapId == MAP_FOREST then
    ensureSoldiers(G)
    for _, s in ipairs(G.sols) do
      if not s.beaten and not s.chase and hitActor(x, y, s.fx, s.fy, 16, 16) then return true end
    end
  end
  if G.mapId == MAP_GROVE then
    if not G.cathCaught then
      local sx, sy = data.spawnOf(data.GROVE, "8")
      if hitActor(x, y, sx, sy, 18, 20) then return true end
    end
    local sx, sy = data.spawnOf(data.GROVE, "9")
    if hitActor(x, y, sx, sy, 16, 18) then return true end
  end
  if G.mapId == MAP_VELD and G.masonPh ~= 0 and hitActor(x, y, G.mxm, G.mym, 16, 16) then return true end
  if G.mapId == MAP_VELD and G.annePh ~= 0 and G.annePh ~= 3 and hitActor(x, y, G.ax, G.ay, 16, 16) then return true end
  return false
end

-- ===== reset / warp =====

local function resetRun(G)
  G.mapId = MAP_HOUSE
  local sx, sy = data.spawnOf(data.HOUSE, "P")
  G.px, G.py = sx, sy
  G.pdir = "down"
  G.party = {}
  G.lead = 1
  G.bag = shallowcopy(data.START_BAG)
  G.marks = data.START_MARKS
  G.talkedWren, G.talkedMae, G.talkedIvo, G.talkedNell, G.talkedPike, G.pikeHelped, G.nellBonus =
    false, false, false, false, false, false, false
  G.beatCalder, G.caughtOnce, G.battles, G.anneGift, G.beatShin, G.cathCaught, G.beatMason =
    false, false, 0, false, false, false, false
  G.gotHerb, G.gotGem, G.gotStump, G.readCart, G.lootedCrate, G.gotShelf =
    false, false, false, false, false, false
  G.annePh = 0
  G.masonPh = 0
  G.sols = {}
  G.nsol = 0
  G.mode = MODE.WORLD
  G.encLock = 8
  G.hud, G.hudT = "", 0
end

local function warp(G, toMapId, mark, fromSouth)
  G.mapId = toMapId
  local sx, sy = data.spawnOf(curMap(G), mark)
  G.px = sx
  G.py = fromSouth and (sy + data.TILE + 8) or (sy - data.TILE)
  G.pdir = fromSouth and "down" or "up"
  G.doorLock = 20
  G.encLock = 3
  G.lastTx, G.lastTy = -1, -1
end

-- ===== talk resolution =====

local function beginTalkEnd(G)
  G.mode = MODE.WORLD
  local a = G.afterTalk
  if a == 1 then
    G.annePh = 3
    G.adir = "down"
  elseif a == 2 and not G.cathCaught then
    startBattle(G, data.mintMonster("cathleen", 6), true, "Cathleen stands against you", "Cathleen")
  elseif a == 3 and not G.beatShin then
    startBattle(G, data.mintMonster("crymare", 5), false, "Shinigami sends CryMare", "Shinigami")
    G.bBench = { data.mintMonster("crymare", 6), data.mintMonster("crymare", 7) }
    G.nbench = 2
  elseif a == 4 then
    startBattle(G, data.mintMonster("razorbat", 4), false, "Calder sends Razorbat", "Calder")
  elseif a == 5 and not G.beatMason then
    startBattle(G, data.mintMonster("glimmoth", 3), false, "Mason sends Glimmoth", "Mason")
  end
  G.afterTalk = 0
end

-- ===== interact =====

local function interact(G)
  if G.mapId == MAP_HOUSE then
    local best, hit = 36 * 36, nil
    for _, mark in ipairs({ "U", "B", "S", "C" }) do
      local hx, hy = data.spawnOf(data.HOUSE, mark)
      local d = distSq(hx, hy, G.px, G.py)
      if d <= best then best, hit = d, mark end
    end
    if hit == "U" then
      for _, m in ipairs(G.party) do m.hp = m.maxHp; m.spp = m.sppMax end
      say1(G, "Max", "Cuts close. Specials return.")
      return
    end
    if hit == "B" then
      if G.gotShelf then
        sayn(G, data.TALK.fatherAfter, 0)
      else
        sayn(G, data.TALK.father, 0)
      end
      return
    end
    if hit == "S" then
      if not G.gotShelf then
        G.gotShelf = true
        G.party = { data.mintMonster("quillpup", 3) }
        G.lead = 1
        sayn(G, data.TALK.shelf, 0)
      else
        say1(G, "Max", "Dust. The crystal is already open.")
      end
      return
    end
    if hit == "C" then
      if not G.lootedCrate then
        G.lootedCrate = true
        G.bag.bandage = G.bag.bandage + 1
        say1(G, "Max", "A wrap in the crate. Better than nothing.")
      else
        say1(G, "Max", "Splinters and a moth. Empty.")
      end
      return
    end
    return
  end

  if G.mapId == MAP_FOREST then
    ensureSoldiers(G)
    for _, s in ipairs(G.sols) do
      if distSq(s.fx, s.fy, G.px, G.py) <= 1600 then
        if s.beaten then
          say1(G, "", "They already lost.")
          return
        end
        startBattle(G, data.mintMonster(s.spec, s.lv), false, "A soldier sends a CryMon", s.name)
        G.bTrainer = "soldier:" .. s.id
        return
      end
    end
    return
  end

  if G.mapId == MAP_GROVE then
    local cx, cy = data.spawnOf(data.GROVE, "8")
    local d8 = distSq(cx, cy, G.px, G.py)
    local sx, sy = data.spawnOf(data.GROVE, "9")
    local d9 = distSq(sx, sy, G.px, G.py)
    if d9 <= 2704 and (G.cathCaught or d9 <= d8 or d8 > 2704) then
      if G.beatShin then
        say1(G, "Shinigami", "The graves are quiet. Go.")
      else
        sayn(G, data.TALK.shinigamiSpot, 3)
      end
      return
    end
    if not G.cathCaught and d8 <= 2704 then
      sayn(G, data.TALK.cathleenSpot, 2)
      return
    end
    return
  end

  if G.mapId == MAP_VELD then
    if G.annePh == 2 then
      if distSq(G.ax, G.ay, G.px, G.py) < 2704 then
        if not G.anneGift then
          G.anneGift = true
          G.bag.gem = G.bag.gem + 5
          sayn(G, data.TALK.anneGift, 1)
        else
          sayn(G, data.TALK.anneAgain, 0)
        end
        return
      end
    end
    if G.masonPh >= 2 then
      if distSq(G.mxm, G.mym, G.px, G.py) < 2704 then
        if G.beatMason then
          sayn(G, data.TALK.masonAfter, 0)
        else
          startBattle(G, data.mintMonster("glimmoth", 3), false, "Mason sends Glimmoth", "Mason")
        end
        return
      end
    end
    local nx, ny

    nx, ny = data.spawnOf(data.VELD, "K")
    if distSq(nx, ny, G.px, G.py) < 2704 then
      if not G.talkedWren then
        G.talkedWren = true
        G.bag.salve = G.bag.salve + 1
        say1(G, "Wren", "Too young. Take the salve. Calder camps south.")
      else
        for _, m in ipairs(G.party) do m.hp = m.maxHp; m.spp = m.sppMax end
        say1(G, "Wren", "Cuts bound. Specials return.")
      end
      return
    end
    nx, ny = data.spawnOf(data.VELD, "I")
    if distSq(nx, ny, G.px, G.py) < 2704 then
      if not G.talkedMae then
        G.talkedMae = true
        G.bag.bandage = G.bag.bandage + 1
        say1(G, "Mae", "Take the wrap. I didn't want the path empty.")
      else
        say1(G, "Mae", "I'll be here. South still drums.")
      end
      return
    end
    nx, ny = data.spawnOf(data.VELD, "V")
    if distSq(nx, ny, G.px, G.py) < 2704 then
      if not G.talkedIvo then
        G.talkedIvo = true
        G.bag.bitterroot = G.bag.bitterroot + 1
        say1(G, "Ivo", "Camp took my CryMon. Chew this. Calder sits south.")
      else
        say1(G, "Ivo", "Hit first. Run if the bat folds you.")
      end
      return
    end
    nx, ny = data.spawnOf(data.VELD, "A")
    if distSq(nx, ny, G.px, G.py) < 2704 then
      if not G.talkedNell then
        G.talkedNell = true
        G.bag.salve = G.bag.salve + 1
        say1(G, "Nell", "Too young. Drink this anyway. Reeds hide a stone.")
      elseif #G.party > 1 and not G.nellBonus then
        G.nellBonus = true
        G.bag.salve = G.bag.salve + 1
        say1(G, "Nell", "That moth wasn't yours yesterday. Another salve.")
      else
        say1(G, "Nell", "The pond keeps its dead. Don't join them.")
      end
      return
    end
    nx, ny = data.spawnOf(data.VELD, "Q")
    if distSq(nx, ny, G.px, G.py) < 2704 then
      if G.gotGem and not G.pikeHelped then
        G.pikeHelped = true
        G.bag.bandage = G.bag.bandage + 1
        say1(G, "Pike", "You found it. A wrap. Don't tell Calder.")
      elseif not G.talkedPike then
        G.talkedPike = true
        say1(G, "Pike", "I dropped a stone in the east reeds. I'm not going back.")
      elseif G.pikeHelped then
        say1(G, "Pike", "We're even.")
      else
        say1(G, "Pike", "East reeds. Look down.")
      end
      return
    end
    nx, ny = data.spawnOf(data.VELD, "J")
    if distSq(nx, ny, G.px, G.py) < 2704 then
      G.mode = MODE.SHOP
      G.shopTab = "buy"
      G.shopCursor = 1
      return
    end
    nx, ny = data.spawnOf(data.VELD, "E")
    if not G.beatCalder and distSq(nx, ny, G.px, G.py) < 2704 then
      sayn(G, data.TALK.calderFight, 4)
      return
    end
    nx, ny = data.spawnOf(data.VELD, "M")
    if distSq(nx, ny, G.px, G.py) < 2704 then
      if not G.gotHerb then
        G.gotHerb = true
        G.bag.bitterroot = G.bag.bitterroot + 1
        say1(G, "Max", "Bitterroot. It bites back.")
      else
        say1(G, "Max", "Picked clean.")
      end
      return
    end
    nx, ny = data.spawnOf(data.VELD, "G")
    if distSq(nx, ny, G.px, G.py) < 2704 then
      if not G.gotGem then
        G.gotGem = true
        G.bag.gem = G.bag.gem + 1
        say1(G, "Max", G.talkedPike and "Pike's stone. Cold." or "A Capture Crystal.")
      else
        say1(G, "Max", "The mud is empty.")
      end
      return
    end
    nx, ny = data.spawnOf(data.VELD, "L")
    if distSq(nx, ny, G.px, G.py) < 2704 then
      if not G.gotStump then
        G.gotStump = true
        G.bag.bandage = G.bag.bandage + 1
        say1(G, "Max", "A wrap stuffed in the stump.")
      else
        say1(G, "Max", "Just a stump.")
      end
      return
    end
    nx, ny = data.spawnOf(data.VELD, "X")
    if distSq(nx, ny, G.px, G.py) < 2704 then
      G.readCart = true
      say1(G, "Max", "A letter. They already knew her name.")
      return
    end
  end
end

-- ===== encounters =====

local ENC_POOL_FOREST = { "fenwisp", "duskhorn", "needleroot" }

local function tryEncounter(G)
  local tx, ty = math.floor(G.px / data.TILE), math.floor(G.py / data.TILE)
  if tx == G.lastTx and ty == G.lastTy then return end
  G.lastTx, G.lastTy = tx, ty
  if tileAtPix(G, G.px, G.py) ~= "T" then return end
  if G.encLock > 0 then G.encLock = G.encLock - 1; return end
  if irand(0, 99) > 18 then return end
  G.encLock = 3
  local id, lv = "glimmoth", 2 + irand(0, 1)
  if G.mapId == MAP_FOREST then
    id = ENC_POOL_FOREST[irand(1, 3)]
    lv = 3 + irand(0, 2)
  elseif tx > 18 then
    id = "tortcask"
  end
  local title = ("A wild %s"):format(data.specOf(id).name)
  startBattle(G, data.mintMonster(id, lv), true, title, "wild")
end

-- ===== update: world =====

local function updateWorld(G, dt)
  if G.doorLock > 0 then G.doorLock = G.doorLock - 1 end

  if G.annePh == 1 then
    local dx, dy = G.px - G.ax, G.py - G.ay
    local dist = math.sqrt(dx * dx + dy * dy)
    if dist < 36 then
      G.annePh = 2
      if not G.anneGift then
        G.anneGift = true
        G.bag.gem = G.bag.gem + 5
      end
      sayn(G, data.TALK.anneGift, 1)
      return
    end
    local sp = 52 * dt
    G.ax = G.ax + dx / dist * sp
    G.ay = G.ay + dy / dist * sp
    G.adir = math.abs(dx) > math.abs(dy) and (dx < 0 and "left" or "right") or (dy < 0 and "up" or "down")
    G.aanim = G.aanim + dt * 8
    G.aframe = math.floor(G.aanim) % 4
    return
  end
  if G.annePh == 3 then
    if G.mapId ~= MAP_VELD then
      G.annePh = 0
    else
      G.ay = G.ay + 80 * dt
      G.adir = "down"
      G.aanim = G.aanim + dt * 8
      G.aframe = math.floor(G.aanim) % 4
      if G.ay > G.py + 300 then G.annePh = 0 end
    end
  end

  if G.masonPh == 1 and G.mapId == MAP_VELD then
    G.moving = false
    G.pframe = 0
    local dx, dy = G.px - G.mxm, G.py - G.mym
    local dist = math.sqrt(dx * dx + dy * dy)
    if dist < 36 then
      G.masonPh = 2
      sayn(G, data.TALK.masonFight, 5)
      return
    end
    local sp = 52 * dt
    G.mxm = G.mxm + dx / dist * sp
    G.mym = G.mym + dy / dist * sp
    G.mdir = math.abs(dx) > math.abs(dy) and (dx < 0 and "left" or "right") or (dy < 0 and "up" or "down")
    G.manim = G.manim + dt * 8
    G.mframe = math.floor(G.manim) % 4
    return
  end

  if G.mapId == MAP_FOREST then
    ensureSoldiers(G)
    for _, s in ipairs(G.sols) do
      if not s.beaten then
        if s.chase then
          local dx, dy = G.px - s.fx, G.py - s.fy
          local dist = math.sqrt(dx * dx + dy * dy)
          if dist < 36 then
            s.chase = false
            startBattle(G, data.mintMonster(s.spec, s.lv), false, "A soldier sends a CryMon", s.name)
            G.bTrainer = "soldier:" .. s.id
            return
          end
          s.fx = s.fx + dx / dist * 112 * dt
          s.fy = s.fy + dy / dist * 112 * dt
          s.anim = s.anim + dt * 8
          s.frame = math.floor(s.anim) % 4
          goto continue
        end
        if s.axis == 1 then
          s.fx = s.fx + s.sign * 36 * dt
          if s.fx > s.maxv then s.fx = s.maxv; s.sign = -1; s.dir = "left" end
          if s.fx < s.minv then s.fx = s.minv; s.sign = 1; s.dir = "right" end
          s.anim = s.anim + dt * 4
          s.frame = math.floor(s.anim) % 4
        elseif s.axis == 2 then
          s.fy = s.fy + s.sign * 36 * dt
          if s.fy > s.maxv then s.fy = s.maxv; s.sign = -1; s.dir = "up" end
          if s.fy < s.minv then s.fy = s.minv; s.sign = 1; s.dir = "down" end
          s.anim = s.anim + dt * 4
          s.frame = math.floor(s.anim) % 4
        end
        if soldierLos(G, s) then s.chase = true end
      end
      ::continue::
    end
  end

  local dx, dy = 0, 0
  if input.isDown("left") then dx = -1; G.pdir = "left" end
  if input.isDown("right") then dx = 1; G.pdir = "right" end
  if input.isDown("up") then dy = -1; G.pdir = "up" end
  if input.isDown("down") then dy = 1; G.pdir = "down" end
  G.moving = dx ~= 0 or dy ~= 0
  if G.moving then
    local sp = 110
    local nx, ny = G.px + dx * sp * dt, G.py + dy * sp * dt
    if not blocked(G, nx, G.py) then G.px = nx end
    if not blocked(G, G.px, ny) then G.py = ny end
    local mw, mh = mapDims(G)
    G.px = clampf(G.px, 24, mw * data.TILE - 24)
    G.py = clampf(G.py, 40, mh * data.TILE - 16)
    G.panim = G.panim + dt * 6
    G.pframe = math.floor(G.panim) % 4
    tryEncounter(G)
  else
    G.pframe = 0
  end

  local ch = tileAtPix(G, G.px, G.py)
  if G.doorLock <= 0 then
    if G.mapId == MAP_HOUSE and ch == "D" then
      if not G.gotShelf then
        local ddx, ddy = data.spawnOf(data.HOUSE, "D")
        G.py = ddy - data.TILE
        G.pdir = "up"
        G.doorLock = 20
        say1(G, "Max", "Not yet. Father's CryMon is still on the shelf.")
      else
        warp(G, MAP_VELD, "D", true)
        if G.masonPh == 0 then
          G.masonPh = 1
          G.mxm = G.px
          G.mym = G.py + 160
          G.mdir = "up"
          G.mframe = 0
          G.manim = 0
          say1(G, "", "Footsteps on the path. Someone followed you out.")
        else
          say1(G, "Max", "Night air. I can do this.")
        end
      end
    elseif G.mapId == MAP_VELD and ch == "D" then
      warp(G, MAP_HOUSE, "D", false)
    elseif G.mapId == MAP_VELD and ch == "Z" then
      warp(G, MAP_FOREST, "Y", true)
      ensureSoldiers(G)
      say1(G, "Max", "The trees close over the path.")
    elseif G.mapId == MAP_FOREST and ch == "Y" then
      warp(G, MAP_VELD, "Z", false)
    elseif G.mapId == MAP_FOREST and ch == "O" then
      warp(G, MAP_GROVE, "O", true)
      say1(G, "Max", "The grass dies out. Stone and hush.")
    elseif G.mapId == MAP_GROVE and ch == "O" then
      warp(G, MAP_FOREST, "O", false)
    end
  end

  if input.confirmPressed() then interact(G) end
  if input.startPressed() then G.mode = MODE.PARTY end
  if input.selectPressed() then G.mode = MODE.BAG end
  for i = 1, 6 do
    if input.keyPressedRaw(tostring(i)) and #G.party >= i then G.lead = i end
  end
end

-- ===== update: battle =====

local function updateBattle(G, dt)
  G.bT = G.bT + dt
  if G.bPhase == 0 then
    if input.confirmPressed() then
      G.bMsgI = G.bMsgI + 1
      if G.bMsgI > #G.bMsg then
        if G.bAfter == 5 then finishWin(G); return end
        if G.bAfter == 6 then G.mode = MODE.WORLD; G.encLock = 3; return end
        if G.bAfter == 7 then
          G.mode = MODE.WORLD
          local L = leader(G)
          if L then L.hp = math.max(1, math.floor(L.maxHp * 2 / 5)) end
          G.encLock = 3
          say1(G, "Max", "We still breathe. Crawl back.")
          return
        end
        G.bPhase = G.bAfter
        if G.bPhase == 1 then fillItemMenu(G) end
        if G.bPhase == 2 then fillAtkMenu(G) end
        if G.bPhase == 3 then
          G.bMenu = { { label = "Dodge  AGI", kind = "dodge" }, { label = "Block  STR", kind = "block" }, { label = "Barrier  SPC", kind = "barrier" } }
          G.bCur = 1
        end
      end
    end
    return
  end
  if G.bPhase == 4 then
    G.mg = G.mg + dt * 110
    if G.mg > 100 then G.mg = 0 end
    if input.confirmPressed() then
      local mul
      if G.mg >= 46 and G.mg <= 54 then mul = 2.0
      elseif G.mg >= 38 and G.mg <= 62 then mul = 1.45
      else mul = 0.7 end
      G.bDmg = math.max(1, math.floor((11 + G.bPl.spc * 0.75) * mul))
      applyHit(G)
    end
    return
  end
  local n = #G.bMenu
  if input.keyPressedRaw("up") or input.keyPressedRaw("w") then G.bCur = (G.bCur - 2) % n + 1 end
  if input.keyPressedRaw("down") or input.keyPressedRaw("s") then G.bCur = G.bCur % n + 1 end
  if input.cancelPressed() and G.bPhase == 2 then
    G.bPhase = 1
    fillItemMenu(G)
    return
  end
  if input.confirmPressed() then
    if G.bPhase == 1 then pickItem(G)
    elseif G.bPhase == 2 then pickAtk(G)
    else pickGuard(G) end
  end
end

-- ===== update: shop (functional buy/sell -- see src/data.lua's note: =====
-- native/crymon.c only *draws* the shop with no purchase logic at all
-- (mode M_SHOP just closes on cancel/start/select); this is a clear
-- regression vs engine.ts's working buy/sell UI, so we port the TS
-- behaviour here instead.

local function ownedItems(G)
  local rows = {}
  for _, id in ipairs(data.ITEM_ORDER) do
    if (G.bag[id] or 0) > 0 then rows[#rows + 1] = id end
  end
  return rows
end

local function updateShop(G)
  if input.cancelPressed() or input.startPressed() or input.selectPressed() then
    G.mode = MODE.WORLD
    return
  end
  if input.keyPressedRaw("left") or input.keyPressedRaw("right") or input.keyPressedRaw("a") or input.keyPressedRaw("d") then
    G.shopTab = G.shopTab == "buy" and "sell" or "buy"
    G.shopCursor = 1
  end
  local rows = G.shopTab == "buy" and data.ITEM_ORDER or ownedItems(G)
  if #rows == 0 then return end
  if input.keyPressedRaw("up") or input.keyPressedRaw("w") then G.shopCursor = (G.shopCursor - 2) % #rows + 1 end
  if input.keyPressedRaw("down") or input.keyPressedRaw("s") then G.shopCursor = G.shopCursor % #rows + 1 end
  if input.confirmPressed() then
    local id = rows[G.shopCursor]
    if not id then return end
    if G.shopTab == "buy" then
      local cost = data.ITEMS[id].buy
      if G.marks < cost then
        note(G, "Not enough marks.")
        return
      end
      G.marks = G.marks - cost
      G.bag[id] = G.bag[id] + 1
      note(G, "Bought " .. data.ITEMS[id].name .. ".")
    else
      if (G.bag[id] or 0) <= 0 then return end
      G.bag[id] = G.bag[id] - 1
      G.marks = G.marks + data.ITEMS[id].sell
      note(G, "Sold " .. data.ITEMS[id].name .. ".")
      if G.bag[id] <= 0 then G.shopCursor = 1 end
    end
  end
end

-- ===== top-level tick =====

function M.update(G, dt)
  G.clockt = G.clockt + dt
  if G.hudT > 0 then G.hudT = G.hudT - dt end

  if G.mode == MODE.TITLE then
    if input.confirmPressed() or input.startPressed() then resetRun(G) end
    return
  end
  if G.mode == MODE.ENDING then
    if input.confirmPressed() then
      G.endingI = G.endingI + 1
      if G.endingI > #data.ENDING_WIN then G.mode = MODE.TITLE end
    end
    return
  end
  if G.mode == MODE.DEMOEND then
    if input.confirmPressed() then
      G.endingI = G.endingI + 1
      if G.endingI > #data.DEMO_END then G.mode = MODE.TITLE end
    end
    return
  end
  if G.mode == MODE.TALK then
    if input.confirmPressed() then
      G.talkI = G.talkI + 1
      if G.talkI > #G.talk then beginTalkEnd(G) end
    end
    return
  end
  if G.mode == MODE.BATTLE then updateBattle(G, dt); return end
  if G.mode == MODE.SHOP then updateShop(G); return end
  if G.mode == MODE.BAG or G.mode == MODE.PARTY then
    if input.cancelPressed() or input.startPressed() or input.selectPressed() then G.mode = MODE.WORLD end
    return
  end
  updateWorld(G, dt)
end

-- expose internals needed by draw.lua
M._internal = {
  leader = leader, curMap = curMap, mapDims = mapDims, ensureSoldiers = ensureSoldiers,
  captureChanceNow = captureChanceNow, MAP_HOUSE = MAP_HOUSE, MAP_VELD = MAP_VELD,
  MAP_FOREST = MAP_FOREST, MAP_GROVE = MAP_GROVE,
}

return M
