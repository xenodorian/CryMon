-- conf.lua
-- Native 640x480 resolution, matching native/crymon.c's VW/VH exactly.
-- Non-resizable, non-fullscreen by default (PortMaster launcher can force
-- fullscreen at the OS/window-manager level if desired; see portmaster/).

function love.conf(t)
  t.identity = "crymon"
  t.version = "11.5"
  t.console = false

  t.window.title = "CryMon"
  t.window.width = 640
  t.window.height = 480
  t.window.resizable = false
  t.window.fullscreen = false
  t.window.vsync = 1
  t.window.minwidth = 640
  t.window.minheight = 480

  t.modules.joystick = true
  t.modules.audio = false
  t.modules.sound = false
  t.modules.physics = false
  t.modules.video = false
end
