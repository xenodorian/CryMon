-- main.lua
-- CryMon -- LOVE2D port. Entry point only: wires love.* callbacks to the
-- state machine (src/state.lua) and renderer (src/render.lua). All game
-- logic lives in src/; see love/README.md and love/portmaster/README.md
-- for how this is packaged as a PortMaster port.
--
-- Only stock love.* calls are used anywhere in this game (no io/os/ffi/
-- platform-specific APIs), so it runs identically under desktop LOVE and
-- LOVE for Android.

local state = require("src.state")
local render = require("src.render")
local input = require("src.input")

local G

function love.load()
  love.graphics.setDefaultFilter("nearest", "nearest")
  love.graphics.setBackgroundColor(18 / 255, 17 / 255, 14 / 255)
  love.math.setRandomSeed(os.time())
  G = state.new()
end

function love.update(dt)
  -- Clamp like crymon.c does (its `if (dt > 0.05f) dt = 0.05f;`) so a big
  -- stall (e.g. a slow frame on the handheld) can't teleport actors.
  if dt > 0.05 then dt = 0.05 end
  state.update(G, dt)
  input.endFrame()
end

function love.draw()
  render.draw(G)
end

function love.keypressed(key)
  input.keypressed(key)
end

function love.resize() end
