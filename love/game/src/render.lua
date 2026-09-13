-- src/render.lua
-- All screen drawing. Companion to src/state.lua: reads state, never
-- mutates it. Procedural only (rectangles/polygons/text) -- see
-- src/draw.lua and the love/README.md for why no image assets are bundled.

local data = require("src.data")
local draw = require("src.draw")
local state = require("src.state")

local MODE = state.MODE
local I = state._internal

local render = {}

local SPECIES_COLOR = {
  quillpup = { 156, 108, 72 }, glimmoth = { 214, 186, 74 }, tortcask = { 96, 140, 84 },
  razorbat = { 120, 78, 150 }, mossback = { 74, 122, 96 }, briarfox = { 208, 120, 58 },
  fenwisp = { 92, 196, 196 }, duskhorn = { 150, 76, 60 }, needleroot = { 70, 96, 56 },
  cathleen = { 190, 52, 70 }, crymare = { 70, 46, 92 },
}

local NPC_COLOR = {
  Max = { 92, 138, 198 }, Wren = { 150, 120, 90 }, Mae = { 182, 140, 162 },
  Ivo = { 118, 150, 110 }, Nell = { 140, 180, 190 }, Pike = { 172, 150, 92 },
  Bram = { 202, 170, 112 }, Calder = { 130, 60, 60 }, Mason = { 96, 96, 116 },
  Anne = { 202, 150, 172 }, Cathleen = { 190, 52, 70 }, Shinigami = { 64, 42, 84 },
}

local function camera(G)
  local mw, mh = I.mapDims(G)
  local W, H = mw * data.TILE, mh * data.TILE
  local cx = G.px - data.VIEW_W / 2
  local cy = G.py - data.VIEW_H / 2
  if cx < 0 then cx = 0 end
  if cy < 0 then cy = 0 end
  if cx > W - data.VIEW_W then cx = math.max(0, W - data.VIEW_W) end
  if cy > H - data.VIEW_H then cy = math.max(0, H - data.VIEW_H) end
  return cx, cy
end

local BG_BY_MAP = {
  [1] = { 26, 20, 16 }, [3] = { 18, 24, 16 }, [4] = { 22, 18, 24 },
}

local function drawMap(G, cx, cy)
  local bg = BG_BY_MAP[G.mapId] or { 28, 36, 24 }
  draw.fill(bg[1], bg[2], bg[3], 255, 0, 0, data.VIEW_W, data.VIEW_H)
  local map = I.curMap(G)
  local mw, mh = data.mapDims(map)
  local x0 = math.max(0, math.floor(cx / data.TILE) - 1)
  local y0 = math.max(0, math.floor(cy / data.TILE) - 1)
  local x1 = math.min(mw, math.floor((cx + data.VIEW_W) / data.TILE) + 2)
  local y1 = math.min(mh, math.floor((cy + data.VIEW_H) / data.TILE) + 2)
  for y = y0, y1 - 1 do
    for x = x0, x1 - 1 do
      local ch = data.tileAt(map, x, y)
      draw.paintTile(ch, x * data.TILE - cx, y * data.TILE - cy)
    end
  end
end

local function prop(cx, cy, wx, wy, camx, camy, w, h, r, g, b, label)
  local x, y = wx - camx - w / 2, wy - camy - h
  draw.fill(r, g, b, 255, x, y, w, h)
  draw.fill(18, 17, 14, 255, x, y, w, 3)
  if label then draw.text(label, x, y - 14, 197, 206, 198, 2) end
end

local function drawActorNamed(name, wx, wy, camx, camy, dir, frame)
  local c = NPC_COLOR[name] or { 150, 150, 150 }
  draw.actor(wx - camx, wy - camy, 32, 48, c[1], c[2], c[3], dir, frame)
end

local function drawWorld(G)
  local cx, cy = camera(G)
  drawMap(G, cx, cy)

  if G.mapId == I.MAP_HOUSE then
    local hx, hy
    hx, hy = data.spawnOf(data.HOUSE, "B"); prop(0, 0, hx, hy, cx, cy, 40, 28, 110, 70, 60, "Father")
    hx, hy = data.spawnOf(data.HOUSE, "U"); prop(0, 0, hx, hy, cx, cy, 40, 28, 90, 90, 100)
    hx, hy = data.spawnOf(data.HOUSE, "S"); prop(0, 0, hx, hy, cx, cy, 26, 30, 120, 96, 60, "Shelf")
    hx, hy = data.spawnOf(data.HOUSE, "C"); prop(0, 0, hx, hy, cx, cy, 26, 22, 130, 100, 60, "Crate")
  end

  if G.mapId == I.MAP_VELD then
    local nx, ny
    nx, ny = data.spawnOf(data.VELD, "X"); prop(0, 0, nx, ny, cx, cy, 40, 30, 90, 70, 50, "Cart")
    nx, ny = data.spawnOf(data.VELD, "J"); prop(0, 0, nx, ny, cx, cy, 26, 24, 130, 100, 60)
    if not G.gotHerb then
      nx, ny = data.spawnOf(data.VELD, "M"); prop(0, 0, nx, ny, cx, cy, 18, 20, 90, 130, 70, "Herb")
    end
    if not G.gotGem then
      nx, ny = data.spawnOf(data.VELD, "G"); prop(0, 0, nx, ny, cx, cy, 16, 16, 180, 210, 230, "Gem")
    end
    nx, ny = data.spawnOf(data.VELD, "L"); prop(0, 0, nx, ny, cx, cy, 22, 20, 90, 70, 50, "Stump")

    nx, ny = data.spawnOf(data.VELD, "K"); drawActorNamed("Wren", nx, ny, cx, cy, "down", 0)
    nx, ny = data.spawnOf(data.VELD, "I"); drawActorNamed("Mae", nx, ny, cx, cy, "down", 0)
    nx, ny = data.spawnOf(data.VELD, "V"); drawActorNamed("Ivo", nx, ny, cx, cy, "down", 0)
    nx, ny = data.spawnOf(data.VELD, "A"); drawActorNamed("Nell", nx, ny, cx, cy, "down", 0)
    nx, ny = data.spawnOf(data.VELD, "Q"); drawActorNamed("Pike", nx, ny, cx, cy, "down", 0)
    nx, ny = data.spawnOf(data.VELD, "J"); drawActorNamed("Bram", nx, ny, cx, cy, "down", 0)
    if not G.beatCalder then
      nx, ny = data.spawnOf(data.VELD, "E"); drawActorNamed("Calder", nx, ny, cx, cy, "down", 0)
    end
    if G.masonPh ~= 0 then drawActorNamed("Mason", G.mxm, G.mym, cx, cy, G.mdir, G.mframe) end
    if G.annePh ~= 0 then drawActorNamed("Anne", G.ax, G.ay, cx, cy, G.adir, G.aframe) end
  end

  if G.mapId == I.MAP_FOREST then
    I.ensureSoldiers(G)
    for _, s in ipairs(G.sols) do
      if s.beaten then
        draw.actor(s.fx - cx, s.fy - cy, 32, 48, 80, 80, 80, s.dir, 0)
      else
        draw.actor(s.fx - cx, s.fy - cy, 32, 48, 140, 70, 70, s.dir, s.frame)
      end
    end
  end

  if G.mapId == I.MAP_GROVE then
    if not G.cathCaught then
      local nx, ny = data.spawnOf(data.GROVE, "8")
      drawActorNamed("Cathleen", nx, ny, cx, cy, "down", 0)
    end
    local nx, ny = data.spawnOf(data.GROVE, "9")
    drawActorNamed("Shinigami", nx, ny, cx, cy, "down", math.floor(G.clockt * 4) % 4)
  end

  local fr = G.moving and G.pframe or 0
  draw.actor(G.px - cx, G.py - cy, 32, 48, 92, 138, 198, G.pdir, fr)

  -- HUD
  draw.box(8, 8, 624, 96)
  draw.text("MAX", 20, 16, 232, 228, 216, 4)
  draw.text(("Xtals %d"):format(G.bag.gem), 140, 16, 197, 206, 198, 4)
  draw.text(("M %d"):format(G.marks), 430, 16, 143, 74, 64, 4)
  local L = I.leader(G)
  if L then
    draw.text(("%s Lv%d  %d/%d"):format(L.name, L.lv, L.hp, L.maxHp), 20, 56, 138, 134, 120, 4)
  else
    draw.text("No CryMon yet", 20, 56, 138, 134, 120, 4)
  end

  if G.hudT > 0 then
    draw.box(8, 268, 624, 204)
    draw.textWrap(G.hud, 24, 284, 592, 232, 228, 216, 4)
  end
end
render.drawWorld = drawWorld

local function drawTalk(G)
  drawWorld(G)
  local beat = G.talk[G.talkI]
  if not beat then return end
  if beat.who ~= "" then
    draw.fill(18, 17, 14, 180, 0, 0, data.VIEW_W, data.VIEW_H)
    local c = NPC_COLOR[beat.who] or { 150, 150, 150 }
    draw.fill(c[1], c[2], c[3], 255, 30, 30, 180, 200)
    draw.box(236, 8, 396, 260)
    draw.text(beat.who, 252, 20, 197, 206, 198, 4)
    draw.textWrap(beat.text, 252, 64, 364, 232, 228, 216, 4)
  else
    draw.box(8, 268, 624, 204)
    draw.textWrap(beat.text, 24, 284, 592, 232, 228, 216, 4)
  end
end

local function battleBlob(species, x, y, w, h, flip)
  local c = SPECIES_COLOR[species] or { 150, 150, 150 }
  draw.fill(20, 18, 16, 120, x + 6, y + h - 10, w - 12, 10)
  draw.fill(c[1], c[2], c[3], 255, x, y, w, h)
  draw.fill(math.min(255, c[1] + 40), math.min(255, c[2] + 40), math.min(255, c[3] + 40), 255, x + 6, y + 6, w - 12, h * 0.3)
  draw.setColor(20, 18, 16, 255)
  local ex = flip and (x + w * 0.25) or (x + w * 0.65)
  love.graphics.circle("fill", ex, y + h * 0.35, 4)
end

local function drawBattle(G)
  draw.fill(42, 36, 24, 255, 0, 0, data.VIEW_W, data.VIEW_H)
  local pf = math.floor(G.bT * 4) % 4
  battleBlob(G.bFoe.species, 424, 40, 168, 150, true)
  battleBlob(G.bPl.species, 40, 220, 150, 150, false)

  draw.box(16, 16, 400, 104)
  draw.text(G.bFoe.name, 28, 24, 232, 228, 216, 4)
  draw.fill(42, 38, 32, 255, 28, 72, 360, 24)
  local fp = G.bFoe.maxHp > 0 and (360 * G.bFoe.hp / G.bFoe.maxHp) or 0
  draw.fill(90, 122, 82, 255, 28, 72, fp, 24)

  draw.box(220, 196, 404, 100)
  draw.text(("%s Lv%d"):format(G.bPl.name, G.bPl.lv), 236, 208, 232, 228, 216, 4)
  draw.fill(42, 38, 32, 255, 236, 252, 360, 24)
  local pp = G.bPl.maxHp > 0 and (360 * G.bPl.hp / G.bPl.maxHp) or 0
  draw.fill(90, 122, 82, 255, 236, 252, pp, 24)

  draw.box(8, 292, 624, 180)
  if G.bPhase == 0 then
    draw.textWrap(G.bMsg[G.bMsgI] or "", 24, 304, 592, 232, 228, 216, 4)
    return
  end
  if G.bPhase == 4 then
    draw.text("SPECIAL", 24, 304, 197, 206, 198, 4)
    draw.fill(42, 38, 32, 255, 24, 360, 592, 28)
    draw.fill(90, 122, 82, 255, 250, 360, 140, 28)
    draw.fill(232, 228, 216, 255, 24 + (G.mg / 100) * 592, 348, 10, 48)
    return
  end
  local ttl = (G.bPhase == 1 and "ITEMS") or (G.bPhase == 2 and "ATTACK") or "GUARD"
  draw.text(ttl, 24, 300, 138, 134, 120, 4)
  for i, row in ipairs(G.bMenu) do
    if i <= 4 then
      local on = i == G.bCur
      local prefix = on and ">" or " "
      if on then
        draw.text(prefix .. row.label, 24, 336 + (i - 1) * 32, 232, 228, 216, 4)
      else
        draw.text(prefix .. row.label, 24, 336 + (i - 1) * 32, 138, 134, 120, 4)
      end
    end
  end
end

local function drawTitle(G)
  draw.fill(28, 36, 24, 255, 0, 0, data.VIEW_W, data.VIEW_H)
  local map = data.VELD
  local mw = data.mapDims(map)
  for y = 0, math.min(#map, 15) - 1 do
    for x = 8, math.min(mw, 28) - 1 do
      draw.paintTile(data.tileAt(map, x, y), (x - 8) * data.TILE, y * data.TILE)
    end
  end
  draw.fill(18, 17, 14, 70, 0, 0, data.VIEW_W, data.VIEW_H)
  draw.actor(90, 312, 32, 48, 92, 138, 198, "down", 0)
  battleBlob("quillpup", 400, 150, 180, 180, true)
  draw.box(80, 72, 480, 176)
  draw.textCenter("CRYMON", 320, 88, 232, 228, 216, 8)
  draw.textCenter("MAX'S RUN", 320, 176, 197, 206, 198, 4)
  draw.box(96, 372, 448, 72)
  draw.textCenter("Z / A / Space  begin", 320, 392, 90, 122, 82, 4)
end

local function drawBag(G)
  drawWorld(G)
  draw.fill(18, 17, 14, 140, 0, 0, data.VIEW_W, data.VIEW_H)
  draw.box(16, 16, 608, 448)
  draw.text("BAG", 32, 28, 197, 206, 198, 4)
  draw.text(("M %d"):format(G.marks), 360, 28, 143, 74, 64, 4)
  draw.text(("Moss salve x%d"):format(G.bag.salve), 32, 84, 232, 228, 216, 4)
  draw.text(("Linen wrap x%d"):format(G.bag.bandage), 32, 128, 232, 228, 216, 4)
  draw.text(("Bitterroot x%d"):format(G.bag.bitterroot), 32, 172, 232, 228, 216, 4)
  draw.text(("Ash dust x%d"):format(G.bag.dust), 32, 216, 232, 228, 216, 4)
  draw.text(("Capture Crystal x%d"):format(G.bag.gem), 32, 260, 232, 228, 216, 4)
  draw.text("X close", 32, 400, 90, 122, 82, 4)
end

local function drawParty(G)
  drawWorld(G)
  draw.fill(18, 17, 14, 140, 0, 0, data.VIEW_W, data.VIEW_H)
  draw.box(8, 8, 624, 464)
  draw.text("CRYMON", 24, 20, 197, 206, 198, 4)
  for i, m in ipairs(G.party) do
    local y = 72 + (i - 1) * 52
    local prefix = i == G.lead and ">" or " "
    local col = i == G.lead and { 232, 228, 216 } or { 138, 134, 120 }
    draw.text(("%s%s Lv%d %d/%d"):format(prefix, m.name, m.lv, m.hp, m.maxHp), 24, y, col[1], col[2], col[3], 4)
  end
  draw.text("1-6 lead  X close", 24, 420, 90, 122, 82, 4)
end

local SHOP_LINES = {
  { id = "salve", label = "Moss salve" }, { id = "bandage", label = "Linen wrap" },
  { id = "bitterroot", label = "Bitterroot" }, { id = "dust", label = "Ash dust" },
  { id = "gem", label = "Capture Crystal" },
}

local function drawShop(G)
  drawWorld(G)
  draw.fill(18, 17, 14, 140, 0, 0, data.VIEW_W, data.VIEW_H)
  draw.box(16, 16, 608, 448)
  draw.text("BRAM'S STALL", 32, 28, 197, 206, 198, 4)
  draw.text(G.shopTab == "buy" and ">BUY   sell" or " buy   >SELL", 360, 28, 197, 206, 198, 4)
  draw.text(("M %d"):format(G.marks), 360, 60, 143, 74, 64, 4)
  local rows = G.shopTab == "buy" and data.ITEM_ORDER or (function()
    local r = {}
    for _, id in ipairs(data.ITEM_ORDER) do if (G.bag[id] or 0) > 0 then r[#r + 1] = id end end
    return r
  end)()
  for i, id in ipairs(rows) do
    local price = G.shopTab == "buy" and data.ITEMS[id].buy or data.ITEMS[id].sell
    local owned = G.bag[id] or 0
    local on = i == G.shopCursor
    local col = on and { 232, 228, 216 } or { 197, 206, 198 }
    local prefix = on and ">" or " "
    draw.text(("%s%-16s %2dm  (have %d)"):format(prefix, data.ITEMS[id].name, price, owned), 32, 84 + (i - 1) * 44, col[1], col[2], col[3], 4)
  end
  draw.text("Left/Right tab  Z buy/sell  X leave", 32, 410, 90, 122, 82, 4)
end

local function drawEnding(G)
  draw.fill(18, 17, 14, 255, 0, 0, data.VIEW_W, data.VIEW_H)
  draw.textCenter("CRYMON", 320, 60, 232, 228, 216, 8)
  local line = data.ENDING_WIN[G.endingI] or ""
  draw.textWrap(line, 60, 200, 520, 197, 206, 198, 4)
  draw.textCenter("Z / A / Space  continue", 320, 420, 90, 122, 82, 4)
end

local function drawDemoEnd(G)
  draw.fill(18, 17, 14, 255, 0, 0, data.VIEW_W, data.VIEW_H)
  draw.textCenter("CRYMON", 320, 60, 232, 228, 216, 8)
  local line = data.DEMO_END[G.endingI] or ""
  draw.textWrap(line, 60, 200, 520, 197, 206, 198, 4)
  draw.textCenter("Z / A / Space  continue", 320, 420, 90, 122, 82, 4)
end

function render.draw(G)
  if G.mode == MODE.TITLE then drawTitle(G)
  elseif G.mode == MODE.ENDING then drawEnding(G)
  elseif G.mode == MODE.DEMOEND then drawDemoEnd(G)
  elseif G.mode == MODE.BATTLE then drawBattle(G)
  elseif G.mode == MODE.TALK then drawTalk(G)
  elseif G.mode == MODE.BAG then drawBag(G)
  elseif G.mode == MODE.PARTY then drawParty(G)
  elseif G.mode == MODE.SHOP then drawShop(G)
  else drawWorld(G) end
end

return render
