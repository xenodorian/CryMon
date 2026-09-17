#!/bin/bash
# CryMon — PortMaster launcher for the LOVE2D port. Native 640x480, no
# platform-specific code (see love/game/README.md). Mirrors the structure
# and robustness of native/portmaster/CryMon.sh, adapted to find a LOVE
# runtime instead of a native binary.

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

ARCH="${DEVICE_ARCH:-$(uname -m)}"
if [ -d "$GAMEDIR/libs.$ARCH" ]; then
  export LD_LIBRARY_PATH="$GAMEDIR/libs.$ARCH:${LD_LIBRARY_PATH:-}"
fi

# Find a LOVE 11.x runtime. PortMaster does not guarantee a system-wide
# `love` binary, and LOVE upstream does not ship an ARM build by default,
# so the preferred path is a `love.<arch>` binary the porter bundles
# alongside this script (same convention native/portmaster/CryMon.sh uses
# for `crymon.<arch>`). Newer PortMaster builds can also provide a shared
# "runtime" package (declared via port.json's "runtime" field, e.g.
# something like "love_11.5.aarch64") that gets unpacked under the
# PortMaster control folder; check a couple of plausible locations for that
# too before falling back to whatever `love`/`love2d` is on PATH.
LOVE_BIN=""
if [ -x "$GAMEDIR/love.$ARCH" ]; then
  LOVE_BIN="$GAMEDIR/love.$ARCH"
elif [ -x "$GAMEDIR/love.aarch64" ] && { [ "$ARCH" = "arm64" ] || [ "$ARCH" = "aarch64" ]; }; then
  LOVE_BIN="$GAMEDIR/love.aarch64"
elif [ -x "$GAMEDIR/love.x86_64" ] && { [ "$ARCH" = "amd64" ] || [ "$ARCH" = "x86_64" ]; }; then
  LOVE_BIN="$GAMEDIR/love.x86_64"
elif [ -n "$controlfolder" ] && [ -x "$controlfolder/libs/love/love" ]; then
  LOVE_BIN="$controlfolder/libs/love/love"
elif [ -n "$controlfolder" ] && [ -x "$controlfolder/love/love" ]; then
  LOVE_BIN="$controlfolder/love/love"
elif command -v love >/dev/null 2>&1; then
  LOVE_BIN="$(command -v love)"
elif command -v love2d >/dev/null 2>&1; then
  LOVE_BIN="$(command -v love2d)"
fi

if [ -z "$LOVE_BIN" ]; then
  echo "CryMon: no LOVE2D runtime found for arch '$ARCH'." >&2
  echo "Place a 'love.$ARCH' binary next to this script's 'crymon' folder," >&2
  echo "or install a system LOVE 11.x build. See portmaster/README.md." >&2
  ls -l "$GAMEDIR"
  exit 1
fi

if [ -n "$GPTOKEYB" ]; then
  $GPTOKEYB "love" -c "$GAMEDIR/crymon.gptk" &
fi
if type pm_platform_helper >/dev/null 2>&1; then
  pm_platform_helper "$LOVE_BIN" || true
fi

# Run the loose-file game directory directly (fastest to iterate on and
# exactly equivalent to a .love since LOVE just needs main.lua at the
# root); prefer a packaged crymon.love next to this script if one exists
# (see love/game/README.md for how that .love is produced).
TARGET="$GAMEDIR/game"
if [ -f "$GAMEDIR/crymon.love" ]; then
  TARGET="$GAMEDIR/crymon.love"
fi

"$LOVE_BIN" "$TARGET"

if type pm_finish >/dev/null 2>&1; then
  pm_finish
fi
