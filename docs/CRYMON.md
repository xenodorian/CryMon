# CryMon — shared source, two ports

Web is the base. Dreamcast consumes the same content and the same sprites.
Do not keep a second copy of the game in C tables.

```
content/                  JSON source of truth
public/sprites/           art source of truth
src/game/                 web engine (loads JSON)
ports/dreamcast/          Dreamcast runtime (bakes JSON + sprites to C)
backups/                  frozen snapshots of removed ports
```

Repos:

- **xenodorian/CryMon** — canonical. This tree. The Dreamcast port lives here,
  at `ports/dreamcast/`.
- **xenodorian/BeelzFight** `crymon-dreamcast/` — a second DC working copy.
  It has **already drifted** (its `content/` is missing `logic.json`; its
  `main.c`, `Makefile` and `gen_sprites.py` all differ from this tree's).
  Treat it as legacy, not as a place to start new work. See
  [`CONTENT_PLAN.md`](CONTENT_PLAN.md) §8.

Working alongside another agent, or adding a file or folder? Read
[`CONTENT_PLAN.md`](CONTENT_PLAN.md) first — ownership lanes, the
never-create list, and the feature order that reaches both ports.

## What is shared vs what is not

**Shared (edit once):**

- `content/species.json` — stats, moves, spells
- `content/items.json` — bag/shop
- `content/maps.json` — ASCII maps, solid tiles, tile art keys
- `content/dialogue.json` — every talk beat, intro, ending, speaker names
- `content/world.json` — start bag, map names, warps, encounters, trainer kits, NPC marks, formulas
- `content/logic.json` — **canonical game rules** (Dreamcast spec): Mason once-only ambush, Calder rematch, bed fade, party-wipe fade-home
- `public/sprites/` — walk cycles, portraits, monsters, items, props

**Per port (presentation only):**

- Rendering (canvas vs PVR framebuffer)
- Input (keyboard / touch vs Maple)
- Audio

Do not keep a second Mason/fade/warp rule in `engine.ts` or `main.c`.
Those engines **interpret** `content/logic.json`. Formulas in `world.json`
`formulas` are the combat contract.


## Web build

```
npm run dev        # 0.0.0.0:8080
npm run typecheck
npm run build
```

`src/game/data.ts` imports the JSON. `src/game/engine.ts` is the loop.
Change dialogue → save JSON → preview refreshes.

## Dreamcast build

Toolchain: `sh-elf-gcc`, `mkdcdisc`.

```
cd ports/dreamcast
python3 ../../tools/bake_content.py --content ../../content --out src
python3 tools/gen_sprites.py ../../public/sprites
make
make cdi
```

Baker uppercases talk text and folds punctuation for the 8×8 bitmap font.
That is a display transform, not a second script.

`src/content_*.inc` and `src/sprites.h` are generated. Never author them.

## Workflow for a content change

1. Edit `content/*.json` and/or `public/sprites/`.
2. Confirm web preview.
3. Bake DC includes (and sprites.h if art changed).
4. Rebuild DC only if you need a new CDI this turn.
5. If you are on BeelzFight, copy the JSON back to CryMon the same turn.

## Abandoned

- SNES / `.sfc` / 65816. Do not restore.
- LÖVE2D (`love/`). Do not restore. Lua snapshot is in `backups/love-port/`.
- SDL2 / R36S PortMaster (`native/`). Do not restore. C snapshot is in `backups/sdl-port/`.

## Backups

`backups/dreamcast-pre-fuse/` holds the last DC `main.c` with hardcoded
tables, Claude's overnight reports, the old `gen_sprites.py`, and a tar
of `art/` + placeholder sprites. Use it to remember a DC-only quirk.
Do not copy those tables forward.

`backups/love-port/` holds the Lua sources of the removed LÖVE port.
Reference only.

`backups/sdl-port/` holds the C sources of the removed SDL2/R36S port.
Reference only.
