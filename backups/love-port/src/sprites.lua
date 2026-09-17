-- src/sprites.lua
-- Loads the pixel-art sprite set shipped under assets/sprites/ into a
-- key -> love.graphics.Image lookup table, keyed exactly like
-- src/game/engine.ts's `this.images` map (e.g. "max-down-1", "quillpup-2",
-- "port-wren", "item-gem", "prop-shelf", "bg") so render.lua can look up
-- sprites the same way the web build does.
--
-- Any file that fails to load (missing/corrupt) is simply left out of the
-- table; render.lua falls back to its old rectangle placeholder for that
-- one key.

local sprites = { images = {}, missing = {} }

local BASE = "assets/sprites/"

local function add(key, path)
  local full = BASE .. path
  if not love.filesystem.getInfo(full) then
    sprites.missing[#sprites.missing + 1] = key
    return
  end
  local ok, img = pcall(love.graphics.newImage, full)
  if ok and img then
    img:setFilter("nearest", "nearest")
    sprites.images[key] = img
  else
    sprites.missing[#sprites.missing + 1] = key
  end
end

local function dir4(key_prefix, path_prefix)
  for _, dir in ipairs({ "down", "left", "right", "up" }) do
    for f = 1, 4 do
      add(key_prefix .. "-" .. dir .. "-" .. f, path_prefix .. "/" .. dir .. "-" .. f .. ".png")
    end
  end
end

local function idle4(key_prefix, path)
  for f = 1, 4 do
    add(key_prefix .. "-" .. f, path .. "-" .. f .. ".png")
  end
end

function sprites.load()
  add("bg", "battle-bg.png")

  dir4("max", "max")
  dir4("mason", "mason")
  dir4("anne", "anne")
  dir4("shinigami", "shinigami")
  dir4("soldier", "npc/soldier")

  local MONSTERS = {
    "quillpup", "glimmoth", "tortcask", "razorbat", "mossback", "briarfox",
    "fenwisp", "duskhorn", "needleroot", "cathleen", "crymare",
  }
  for _, m in ipairs(MONSTERS) do
    for f = 1, 4 do
      add(m .. "-" .. f, "monsters/" .. m .. "/" .. f .. ".png")
    end
  end
  add("cathleen-ow", "npc/cathleen.png")

  idle4("calder", "npc/calder")
  idle4("wren", "npc/wren")
  idle4("mae", "npc/mae")
  idle4("ivo", "npc/ivo")
  idle4("nell", "npc/nell")
  idle4("pike", "npc/pike")
  idle4("bram", "npc/bram")

  local PORTRAITS = {
    "max", "anne", "mason", "wren", "mae", "ivo", "nell", "pike", "calder",
    "bram", "quillpup", "glimmoth", "tortcask", "razorbat", "mossback",
    "briarfox", "fenwisp", "duskhorn", "needleroot", "cathleen", "shinigami",
    "crymare",
  }
  for _, p in ipairs(PORTRAITS) do
    add("port-" .. p, "portraits/" .. p .. ".png")
  end

  local ITEMS = { "gem", "salve", "bitterroot", "dust", "bandage" }
  for _, it in ipairs(ITEMS) do
    add("item-" .. it, "items/" .. it .. ".png")
  end

  local PROPS = {
    "bed-father", "bed-empty", "shelf", "crate", "door", "herb", "moonstone",
    "stump", "cart",
  }
  for _, p in ipairs(PROPS) do
    add("prop-" .. p, "props/" .. p .. ".png")
  end

  if #sprites.missing > 0 then
    print(("sprites: %d image(s) missing, falling back to rectangles: %s")
      :format(#sprites.missing, table.concat(sprites.missing, ", ")))
  end
end

function sprites.get(key)
  return sprites.images[key]
end

return sprites
