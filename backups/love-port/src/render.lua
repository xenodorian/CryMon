-- src/render.lua
-- All screen drawing. Companion to src/state.lua: reads state, never
-- mutates it. Terrain tiles stay flat-colored rectangles (matches the web
-- build); every character, monster, NPC, prop, portrait and item is drawn
-- from the real pixel-art sprites in assets/sprites/ (see src/sprites.lua),
-- with the same nearest-neighbor scale-to-fit / anchor rules as
-- src/game/engine.ts's drawSprite/drawActor/drawProp. A sprite that failed
-- to load falls back to the old rectangle placeholder for that one key.

local data = require("src.data")
local draw = require("src.draw")
local state = require("src.state")
local sprites = require("src.sprites")

local MODE = state.MODE
local I = state._internal

local render = {}

-- World-space actor box, identical to SPR_W/SPR_H in engine.ts (world
-- coordinates and TILE are both 32px in Lua and in the web build, so these
-- sizes translate 1:1).
local SPR_W, SPR_H = 48, 52

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

--- Draws image `key` scaled to fit inside the x,y,w,h box, nearest-neighbor,
--- horizontally centered. `feet` may be true (anchor bottom, like an actor
--- standing on a tile), "top" (anchor top, like a portrait panel), or false
--- (center vertically). `pixel` mode rounds the scale to an integer (like
--- engine.ts's drawSprite(..., pixel=true)) for crisp small icons/portraits;
--- non-pixel mode fits the box exactly, preserving aspect ratio.
--- Mirrors src/game/engine.ts's Gemwar.drawSprite() exactly.
local function drawSprite(key, x, y, w, h, feet, pixel)
  if feet == nil then feet = true end
  local img = sprites.get(key)
  if not img then
    -- Fallback: same inset gray placeholder engine.ts draws for a missing
    -- image, so a missing sprite degrades gracefully instead of vanishing.
    draw.fill(197, 206, 198, 255, x + 4, y + 4, w - 8, h - 6)
    return
  end
  local iw, ih = img:getWidth(), img:getHeight()
  local dw, dh
  if pixel then
    local fit = math.min(w / iw, h / ih)
    local s = math.max(1, math.floor(fit + 0.5))
    if s < 2 and ih * 2 <= h + 24 then s = 2 end
    dw, dh = iw * s, ih * s
  else
    local ar = iw / ih
    if w / h > ar then dw, dh = h * ar, h
    else dw, dh = w, w / ar end
  end
  local dx = x + (w - dw) / 2
  local dy
  if feet == "top" then dy = y
  elseif feet then dy = y + (h - dh)
  else dy = y + (h - dh) / 2 end
  love.graphics.setColor(1, 1, 1, 1)
  love.graphics.draw(img, dx, dy, 0, dw / iw, dh / ih)
end
render.drawSprite = drawSprite

--- Draws a world actor (player/NPC/monster overworld sprite) anchored at
--- its feet, camera-relative. Mirrors engine.ts's drawActor().
local function drawActorImg(key, wx, wy, camx, camy)
  drawSprite(key, wx - camx - SPR_W / 2, wy - camy - SPR_H + 4, SPR_W, SPR_H)
end

--- Draws a world prop, camera-relative, anchored near its feet. Mirrors
--- engine.ts's drawProp().
local function drawPropImg(key, wx, wy, camx, camy, w, h)
  drawSprite(key, wx - camx - w / 2, wy - camy - h + 6, w, h)
end

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

local function drawWorld(G)
  local cx, cy = camera(G)
  drawMap(G, cx, cy)

  if G.mapId == I.MAP_HOUSE then
    local hx, hy
    hx, hy = data.spawnOf(data.HOUSE, "B")
    drawPropImg("prop-bed-father", hx, hy + 8, cx, cy, 64, 56)
    draw.text("...", hx - cx - 6, hy - cy - 60, 138, 134, 120, 2)
    hx, hy = data.spawnOf(data.HOUSE, "U"); drawPropImg("prop-bed-empty", hx, hy + 8, cx, cy, 64, 56)
    hx, hy = data.spawnOf(data.HOUSE, "S"); drawPropImg("prop-shelf", hx, hy + 4, cx, cy, 40, 44)
    hx, hy = data.spawnOf(data.HOUSE, "C"); drawPropImg("prop-crate", hx, hy + 4, cx, cy, 32, 32)
  end

  if G.mapId == I.MAP_VELD then
    local nx, ny
    nx, ny = data.spawnOf(data.VELD, "D"); drawPropImg("prop-door", nx, ny + 8, cx, cy, 32, 48)
    nx, ny = data.spawnOf(data.VELD, "X"); drawPropImg("prop-cart", nx, ny + 8, cx, cy, 56, 48)
    nx, ny = data.spawnOf(data.VELD, "J"); drawPropImg("prop-crate", nx - 20, ny + 12, cx, cy, 32, 32)
    if not G.gotHerb then
      nx, ny = data.spawnOf(data.VELD, "M"); drawPropImg("prop-herb", nx, ny + 4, cx, cy, 32, 32)
    end
    if not G.gotGem then
      nx, ny = data.spawnOf(data.VELD, "G"); drawPropImg("prop-moonstone", nx, ny + 4, cx, cy, 28, 28)
    end
    if not G.gotStump then
      nx, ny = data.spawnOf(data.VELD, "L"); drawPropImg("prop-stump", nx, ny + 4, cx, cy, 32, 32)
    end
  end

  -- 4-frame idle/walk animation shared by all clock-driven NPCs, matching
  -- engine.ts's `wf = Math.floor(this.clock * 4) % 4 + 1`.
  local wf = math.floor(G.clockt * 4) % 4 + 1

  if G.mapId == I.MAP_VELD then
    local nx, ny
    nx, ny = data.spawnOf(data.VELD, "K"); drawActorImg("wren-" .. wf, nx, ny, cx, cy)
    nx, ny = data.spawnOf(data.VELD, "I"); drawActorImg("mae-" .. wf, nx, ny, cx, cy)
    nx, ny = data.spawnOf(data.VELD, "V"); drawActorImg("ivo-" .. wf, nx, ny, cx, cy)
    nx, ny = data.spawnOf(data.VELD, "A"); drawActorImg("nell-" .. wf, nx, ny, cx, cy)
    nx, ny = data.spawnOf(data.VELD, "Q"); drawActorImg("pike-" .. wf, nx, ny, cx, cy)
    nx, ny = data.spawnOf(data.VELD, "J"); drawActorImg("bram-" .. wf, nx, ny, cx, cy)
    if not G.beatCalder then
      nx, ny = data.spawnOf(data.VELD, "E"); drawActorImg("calder-" .. wf, nx, ny, cx, cy)
    end
    if G.masonPh ~= 0 then
      local mf = (G.mframe % 4) + 1
      drawActorImg("mason-" .. G.mdir .. "-" .. mf, G.mxm, G.mym, cx, cy)
    end
    if G.annePh ~= 0 then
      local af = (G.aframe % 4) + 1
      drawActorImg("anne-" .. G.adir .. "-" .. af, G.ax, G.ay, cx, cy)
    end
  end

  if G.mapId == I.MAP_FOREST then
    I.ensureSoldiers(G)
    for _, s in ipairs(G.sols) do
      local sf = s.beaten and 1 or ((s.frame % 4) + 1)
      drawActorImg("soldier-" .. s.dir .. "-" .. sf, s.fx, s.fy, cx, cy)
    end
  end

  if G.mapId == I.MAP_GROVE then
    if not G.cathCaught then
      local nx, ny = data.spawnOf(data.GROVE, "8")
      drawSprite("cathleen-ow", nx - cx - 36, ny - cy - 68, 72, 72, true)
    end
    local nx, ny = data.spawnOf(data.GROVE, "9")
    local sf = math.floor(G.clockt * 3) % 4 + 1
    drawActorImg("shinigami-down-" .. sf, nx, ny, cx, cy)
  end

  local pf = (G.moving and G.pframe or 0) % 4 + 1
  drawActorImg("max-" .. G.pdir .. "-" .. pf, G.px, G.py, cx, cy)

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
    draw.box(236, 8, 396, 260)
    local speaker = beat.who:lower()
    drawSprite("port-" .. speaker, 30, 30, 180, 200, "top", true)
    draw.text(beat.who, 252, 20, 197, 206, 198, 4)
    draw.textWrap(beat.text, 252, 64, 364, 232, 228, 216, 4)
  else
    draw.box(8, 268, 624, 204)
    draw.textWrap(beat.text, 24, 284, 592, 232, 228, 216, 4)
  end
end

local function battleBlob(species, x, y, w, h, frame)
  local key = species and (species .. "-" .. frame)
  if key and sprites.get(key) then
    drawSprite(key, x, y, w, h, false)
    return
  end
  local c = SPECIES_COLOR[species] or { 150, 150, 150 }
  draw.fill(20, 18, 16, 120, x + 6, y + h - 10, w - 12, 10)
  draw.fill(c[1], c[2], c[3], 255, x, y, w, h)
  draw.fill(math.min(255, c[1] + 40), math.min(255, c[2] + 40), math.min(255, c[3] + 40), 255, x + 6, y + 6, w - 12, h * 0.3)
end

local function drawBattle(G)
  local bg = sprites.get("bg")
  if bg then
    love.graphics.setColor(1, 1, 1, 1)
    love.graphics.draw(bg, 0, 0, 0, data.VIEW_W / bg:getWidth(), data.VIEW_H / bg:getHeight())
  else
    draw.fill(42, 36, 24, 255, 0, 0, data.VIEW_W, data.VIEW_H)
  end
  local pf = math.floor(G.bT * 4) % 4 + 1
  battleBlob(G.bFoe.species, 424, 40, 168, 150, pf)
  battleBlob(G.bPl.species, 40, 220, 150, 150, pf)

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
  drawSprite("max-down-1", 96 - SPR_W / 2, 480 - SPR_H, SPR_W, SPR_H)
  battleBlob("quillpup", 452, 268, 132, 96, 1)
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
  local rows = {
    { id = "salve", label = "Moss salve" }, { id = "bandage", label = "Linen wrap" },
    { id = "bitterroot", label = "Bitterroot" }, { id = "dust", label = "Ash dust" },
    { id = "gem", label = "Capture Crystal" },
  }
  for i, row in ipairs(rows) do
    local y = 84 + (i - 1) * 44
    drawSprite("item-" .. row.id, 32, y - 4, 32, 32, false)
    draw.text(("%s x%d"):format(row.label, G.bag[row.id]), 76, y, 232, 228, 216, 4)
  end
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
    drawSprite("port-" .. m.species, 24, y - 4, 40, 40, false)
    draw.text(("%s%s Lv%d %d/%d"):format(prefix, m.name, m.lv, m.hp, m.maxHp), 72, y, col[1], col[2], col[3], 4)
  end
  draw.text("1-6 lead  X close", 24, 420, 90, 122, 82, 4)
end

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
    drawSprite("item-" .. id, 32, 84 + (i - 1) * 44 - 4, 28, 28, false)
    draw.text(("%s%-16s %2dm  (have %d)"):format(prefix, data.ITEMS[id].name, price, owned), 68, 84 + (i - 1) * 44, col[1], col[2], col[3], 4)
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
