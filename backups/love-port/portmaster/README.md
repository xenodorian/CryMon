# CryMon — LOVE2D PortMaster port

This is the PortMaster packaging for the LOVE2D (Lua) build of CryMon, a
sibling to `native/portmaster/` (the SDL2/C build). The actual game lives
in `love/game/` at the repo root — see `love/game/README.md` for how it's
organized and how to run/package it.

## Layout this folder expects on-device

```
ports/
  CryMon.sh              <- this folder's CryMon.sh
  crymon/
    game/                <- a copy of love/game/ (loose files: main.lua at
                             the root, conf.lua, src/, assets/), OR
    crymon.love           <- a zipped-and-renamed .love (see below); if
                             present, CryMon.sh prefers this over game/
    love.aarch64          <- OPTIONAL: a LOVE 11.x binary for arm64 devices
    love.x86_64           <- OPTIONAL: a LOVE 11.x binary for x86_64 devices
    crymon.gptk           <- gptokeyb mapping (same layout as native's)
    conf/                 <- created at runtime for LOVE's save directory
```

`CryMon.sh` does **not** assume PortMaster ships a system-wide `love`
binary — it does not, in general. In order of preference it looks for:

1. `crymon/love.$ARCH` (or `love.aarch64` / `love.x86_64`) bundled next to
   the game — the porter must supply this, since upstream LOVE does not
   publish an official ARM (aarch64) build. Build one from
   https://github.com/love2d/love (11.5) for the target device's libc/arch,
   or use a community RK3326/ARM64 LOVE build if one is available for the
   handheld in question.
2. A couple of plausible locations for a PortMaster-provided shared LOVE
   "runtime" package (some newer PortMaster builds support declaring a
   `"runtime"` in `port.json`, unpacked under the PortMaster control
   folder, similar to how Godot/other engine ports are distributed). This
   repo intentionally leaves `port.json`'s `"runtime"` field empty because
   the exact current runtime id (e.g. whatever LOVE runtime package name
   PortMaster's runtimes list uses this month) is a moving target — a
   porter publishing this for real should check
   https://github.com/PortsMaster/PortMaster-GUI (or whatever the current
   runtimes source is) for the live convention and fill that field in,
   which lets PortMaster auto-download the runtime instead of requiring a
   bundled binary.
3. A system `love` or `love2d` on `PATH`, if the device already has one
   installed (e.g. via a separate PortMaster "port" that installs LOVE, or
   a custom firmware image that bundles it).

If none of those are found, the script prints where to put a binary and
exits non-zero instead of silently failing.

## Packaging steps (what a human/CI does — not automated here)

1. **Zip-and-rename to a `.love`** (optional but recommended for a real
   release — LOVE can also run directly against a directory, which is what
   `CryMon.sh` does by default against `crymon/game/`):

   ```sh
   cd love/game
   zip -9 -r ../../crymon.love . -x '*.DS_Store'
   ```

   The `.love` file is just a zip with `main.lua` at its root — that's why
   `main.lua` must stay at the top of `love/game/` and not inside `src/`.
   Drop the resulting `crymon.love` into `crymon/` on-device (next to
   `game/`) and `CryMon.sh` will prefer it automatically.

2. **Assemble the PortMaster zip**:

   ```sh
   mkdir -p dist/crymon
   cp -r love/game dist/crymon/game
   cp love/portmaster/crymon.gptk dist/crymon/
   # optionally: cp your love.aarch64 / love.x86_64 build(s) into dist/crymon/
   cp love/portmaster/CryMon.sh dist/CryMon.sh
   cp love/portmaster/port.json dist/port.json
   cp love/portmaster/cover.png love/portmaster/screenshot.png dist/
   cd dist && zip -9 -r ../crymon-love.zip CryMon.sh crymon port.json cover.png screenshot.png
   ```

3. Test locally before shipping either artifact:

   ```sh
   love love/game                 # run the loose directory
   love crymon.love                # run the packaged .love
   ```

## Controls

Same as the native port (see `native/portmaster/README.md` /
`crymon.gptk`): D-pad/arrows to move, A/Z to confirm, B/X to cancel,
Y/Tab to open the bag, Start/Enter for the party menu.

## Assets

CryMon's web and native builds both load real pixel-art sprites, but this
LOVE port draws everything procedurally (colored rectangles/polygons plus
`love.graphics.print`) — see `love/game/README.md` for why, and how to
swap in `love/game/assets/` art later without touching game logic if
someone wants to port the original sprites over.
