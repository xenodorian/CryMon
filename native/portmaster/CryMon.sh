#!/bin/bash
# CryMon — PortMaster launcher. Native 640x480 SDL2 port for R36S / RK3326.

XDG_DATA_HOME=${XDG_DATA_HOME:-$HOME/.local/share}
controlfolder=""
if [ -d "/opt/system/Tools/PortMaster/" ]; then
  controlfolder="/opt/system/Tools/PortMaster"
elif [ -d "/opt/tools/PortMaster/" ]; then
  controlfolder="/opt/tools/PortMaster"
elif [ -d "$XDG_DATA_HOME/PortMaster/" ]; then
  controlfolder="$XDG_DATA_HOME/PortMaster"
elif [ -d "/roms/ports/PortMaster/" ]; then
  controlfolder="/roms/ports/PortMaster"
fi

PORTDIR="$(cd "$(dirname "$0")" && pwd)"
GAMEDIR="$PORTDIR/crymon"

if [ -n "$controlfolder" ] && [ -f "$controlfolder/control.txt" ]; then
  # shellcheck disable=SC1091
  source "$controlfolder/control.txt"
  [ -f "${controlfolder}/mod_${CFW_NAME}.txt" ] && source "${controlfolder}/mod_${CFW_NAME}.txt"
  get_controls
  GAMEDIR="/$directory/ports/crymon"
  export SDL_GAMECONTROLLERCONFIG="$sdl_controllerconfig"
fi

cd "$GAMEDIR" || exit 1

mkdir -p "$GAMEDIR/conf"
export XDG_DATA_HOME="$GAMEDIR/conf"
export SDL_VIDEO_MINIMIZE_ON_FOCUS_LOSS=0
export SDL_HINT_RENDER_SCALE_QUALITY=0
export SDL_RENDER_SCALE_QUALITY=0

ARCH="${DEVICE_ARCH:-$(uname -m)}"
if [ -d "$GAMEDIR/libs.$ARCH" ]; then
  export LD_LIBRARY_PATH="$GAMEDIR/libs.$ARCH:${LD_LIBRARY_PATH:-}"
fi

BIN=""
if [ -x "$GAMEDIR/crymon.$ARCH" ]; then
  BIN="$GAMEDIR/crymon.$ARCH"
elif [ -x "$GAMEDIR/crymon.aarch64" ] && { [ "$ARCH" = "arm64" ] || [ "$ARCH" = "aarch64" ]; }; then
  BIN="$GAMEDIR/crymon.aarch64"
elif [ -x "$GAMEDIR/crymon.x86_64" ] && { [ "$ARCH" = "amd64" ] || [ "$ARCH" = "x86_64" ]; }; then
  BIN="$GAMEDIR/crymon.x86_64"
elif [ -x "$GAMEDIR/crymon" ]; then
  BIN="$GAMEDIR/crymon"
fi

if [ -z "$BIN" ]; then
  echo "CryMon: no binary for arch '$ARCH'" >&2
  ls -l "$GAMEDIR"
  exit 1
fi

if [ -n "$GPTOKEYB" ]; then
  $GPTOKEYB "$(basename "$BIN")" -c "$GAMEDIR/crymon.gptk" &
fi
if type pm_platform_helper >/dev/null 2>&1; then
  pm_platform_helper "$BIN" || true
fi

# Handhelds: fullscreen at native 640x480. Set CRYMON_WINDOW=1 only on a desktop.
unset CRYMON_WINDOW

"$BIN"

if type pm_finish >/dev/null 2>&1; then
  pm_finish
fi
