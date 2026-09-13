-- src/input.lua
-- Keyboard polling abstraction, mirroring native/crymon.c's rising-edge
-- helpers (confirm/cancel/start/select) and src/game/input.ts's key sets.
-- Uses only stock love.keyboard / love.keypressed calls (no platform APIs),
-- so it behaves identically on desktop LÖVE and LÖVE for Android.

local input = {}

-- Keys considered "down" for continuous movement (love.keyboard.isDown).
local MOVE_KEYS = {
  left = { "left", "a" },
  right = { "right", "d" },
  up = { "up", "w" },
  down = { "down", "s" },
}

-- Rising-edge (just-pressed) actions, fed by love.keypressed via input.keypressed().
local CONFIRM_KEYS = { z = true, ["return"] = false, space = true } -- return is Start, not confirm (matches crymon.c)
local CANCEL_KEYS = { x = true, c = true, escape = true }
local START_KEYS = { ["return"] = true }
local SELECT_KEYS = { tab = true, q = true }

local pressedThisFrame = {}

function input.keypressed(key)
  pressedThisFrame[key] = true
end

function input.isDown(dir)
  for _, k in ipairs(MOVE_KEYS[dir]) do
    if love.keyboard.isDown(k) then return true end
  end
  return false
end

local function anyRising(set)
  for k, wanted in pairs(set) do
    if wanted and pressedThisFrame[k] then return true end
  end
  return false
end

function input.confirmPressed()
  return anyRising(CONFIRM_KEYS)
end

function input.cancelPressed()
  return anyRising(CANCEL_KEYS)
end

function input.startPressed()
  return anyRising(START_KEYS)
end

function input.selectPressed()
  return anyRising(SELECT_KEYS)
end

function input.keyPressedRaw(key)
  return pressedThisFrame[key] == true
end

-- Call once per frame, after all update logic has consumed this frame's
-- rising-edge presses.
function input.endFrame()
  pressedThisFrame = {}
end

return input
