-- src/draw.lua
-- Small rendering helpers: solid-color tile/box/text primitives, mirroring
-- the fill()/box()/text()/text_wrap() helpers in native/crymon.c. Terrain
-- tiles (paintTile below) are genuinely flat-colored rectangles in the web
-- build too, so they stay that way here. Real pixel-art sprites (player,
-- NPCs, monsters, props, portraits, items) are loaded by src/sprites.lua
-- and drawn by src/render.lua's drawSprite/drawActorImg/drawPropImg
-- helpers; draw.actor() below is unused colored-block leftover kept only
-- for reference (render.lua draws its own inset-rectangle placeholder
-- directly when a sprite PNG fails to load).

local data = require("src.data")

local draw = {}

local fontCache = {}
local function fontFor(px)
  px = math.max(8, math.floor(px))
  local f = fontCache[px]
  if not f then
    f = love.graphics.newFont(px)
    fontCache[px] = f
  end
  return f
end

-- scale 1 unit ~= 8px glyph cell in crymon.c's font (TS=4 there -> 32px).
-- We use a 1:1 "scale -> font pixel size * 4" mapping so existing TS=4 call
-- sites read the same visual size.
local function pxSize(scale)
  return scale * 8
end

function draw.setColor(r, g, b, a)
  love.graphics.setColor(r / 255, g / 255, b / 255, (a or 255) / 255)
end

function draw.fill(r, g, b, a, x, y, w, h)
  draw.setColor(r, g, b, a)
  love.graphics.rectangle("fill", x, y, w, h)
end

-- Bordered panel, same colors as crymon.c's box().
function draw.box(x, y, w, h)
  draw.fill(18, 17, 14, 255, x, y, w, h)
  draw.fill(197, 206, 198, 255, x, y, w, 2)
  draw.fill(197, 206, 198, 255, x, y + h - 2, w, 2)
  draw.fill(197, 206, 198, 255, x, y, 2, h)
  draw.fill(197, 206, 198, 255, x + w - 2, y, 2, h)
end

function draw.text(s, x, y, r, g, b, scale)
  scale = scale or 4
  love.graphics.setFont(fontFor(pxSize(scale)))
  draw.setColor(r, g, b, 255)
  love.graphics.print(s, x, y)
end

function draw.textCenter(s, cx, y, r, g, b, scale)
  scale = scale or 4
  local f = fontFor(pxSize(scale))
  love.graphics.setFont(f)
  draw.setColor(r, g, b, 255)
  local w = f:getWidth(s)
  love.graphics.print(s, cx - w / 2, y)
end

-- Word-wrap into lines that fit maxw pixels, drawing up to 7 lines like
-- crymon.c's text_wrap (a battle/dialogue box is only so tall).
function draw.textWrap(s, x, y, maxw, r, g, b, scale)
  scale = scale or 4
  local f = fontFor(pxSize(scale))
  love.graphics.setFont(f)
  draw.setColor(r, g, b, 255)
  local lineH = pxSize(scale) + 8
  local words = {}
  for w in s:gmatch("%S+") do words[#words + 1] = w end
  local line = ""
  local lineNo = 0
  local function flush()
    if lineNo >= 7 then return end
    love.graphics.print(line, x, y + lineNo * lineH)
    lineNo = lineNo + 1
    line = ""
  end
  for _, w in ipairs(words) do
    local candidate = line == "" and w or (line .. " " .. w)
    if f:getWidth(candidate) > maxw and line ~= "" then
      flush()
      line = w
    else
      line = candidate
    end
  end
  if line ~= "" then flush() end
end

-- Tile palette, verbatim from crymon.c's paint_tile().
function draw.paintTile(ch, dx, dy)
  local t = data.TILE
  if ch == "H" then draw.fill(42, 30, 22, 255, dx, dy, t, t); return end
  if ch == "R" then draw.fill(106, 64, 48, 255, dx, dy, t, t); return end
  if ch == "F" or ch == "P" then draw.fill(106, 82, 56, 255, dx, dy, t, t); return end
  if ch == "D" then draw.fill(26, 18, 12, 255, dx, dy, t, t); return end
  if ch == "B" or ch == "U" or ch == "C" or ch == "S" then draw.fill(106, 82, 56, 255, dx, dy, t, t); return end
  if ch == "." then
    draw.fill(61, 90, 56, 255, dx, dy, t, t)
    draw.fill(90, 122, 82, 255, dx + 4, dy + 6, 2, 2)
    return
  end
  if ch == "T" then
    draw.fill(47, 74, 44, 255, dx, dy, t, t)
    draw.fill(106, 138, 58, 255, dx + 6, dy + 4, 4, 24)
    draw.fill(90, 122, 82, 255, dx + 16, dy + 2, 4, 26)
    return
  end
  if ch == "=" or ch == "," or ch == "Z" or ch == "Y" or ch == "3" or ch == "O" or ch == "8" or ch == "9" then
    local rr = ch == "," and 90 or 107
    local gg = ch == "," and 74 or 90
    draw.fill(rr, gg, 58, 255, dx, dy, t, t)
    return
  end
  if ch == "#" then
    draw.fill(28, 36, 24, 255, dx, dy, t, t)
    draw.fill(61, 90, 56, 255, dx + 4, dy + 2, 24, 18)
    return
  end
  if ch == "W" then draw.fill(42, 58, 68, 255, dx, dy, t, t); return end
  if ch == "^" then draw.fill(74, 64, 48, 255, dx, dy, t, t); return end
  if ch == "N" or ch == "E" then draw.fill(90, 70, 48, 255, dx, dy, t, t); return end
  if ch == "*" then
    draw.fill(61, 90, 56, 255, dx, dy, t, t)
    draw.fill(180, 60, 80, 255, dx + 12, dy + 12, 6, 6)
    return
  end
  draw.fill(61, 90, 56, 255, dx, dy, t, t)
end

-- Simple procedural "sprite": a colored body block + a direction wedge, used
-- for the player, NPCs, soldiers and monsters. No image assets are shipped
-- (see love/README.md) — this keeps the port at parity with how crymon.c
-- rendered anything whose gfx_blob sprite was absent (nothing), while still
-- giving every actor a readable, distinct silhouette.
function draw.actor(cx, cy, w, h, r, g, b, dir, frame)
  local x, y = cx - w / 2, cy - h
  draw.fill(20, 18, 16, 160, x + 3, y + h - 6, w - 6, 6) -- shadow
  draw.fill(r, g, b, 255, x, y, w, h)
  draw.fill(math.min(255, r + 30), math.min(255, g + 30), math.min(255, b + 30), 255, x + 4, y + 4, w - 8, h * 0.4)
  -- facing wedge
  local fx, fy = cx, y + h * 0.35
  local size = 6
  draw.setColor(232, 228, 216, 255)
  if dir == "down" then
    love.graphics.polygon("fill", fx - size, fy, fx + size, fy, fx, fy + size)
  elseif dir == "up" then
    love.graphics.polygon("fill", fx - size, fy + size, fx + size, fy + size, fx, fy)
  elseif dir == "left" then
    love.graphics.polygon("fill", fx + size, fy - size, fx + size, fy + size, fx - size, fy)
  else
    love.graphics.polygon("fill", fx - size, fy - size, fx - size, fy + size, fx + size, fy)
  end
  -- walk-cycle leg flicker
  if frame and frame % 2 == 1 then
    draw.fill(0, 0, 0, 80, x + 4, y + h - 4, w - 8, 4)
  end
end

return draw
