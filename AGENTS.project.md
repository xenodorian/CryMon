# CryMon — project standing orders

This file is the game-specific contract. Platform rules in `AGENTS.md` still apply.

**Canonical tree is this repo (xenodorian/CryMon), web first.**
Claude's Dreamcast work in `xenodorian/BeelzFight` is a port of this tree, not a second game.

Read [`docs/CRYMON.md`](docs/CRYMON.md) before changing story, maps, stats, or art.
Read [`docs/CONTENT_PLAN.md`](docs/CONTENT_PLAN.md) before adding a **feature, file, or folder**,
or when another agent is working at the same time — it holds the ownership
lanes, the never-create-this-folder list, and the order that gets a feature
into *both* ports.
Read [`CLAUDE.md`](CLAUDE.md) if you are Claude; same rules, DC-focused build steps.

## Do

- Edit **`content/*.json`** for species, items, maps, dialogue, warps, encounters, NPC marks, trainer kits, **and rules** (`logic.json`).
- Edit **`public/sprites/`** for art. Do not duplicate sprite packs per port.
- Keep web playable: `src/game/` loads JSON directly. Preview must keep running.
- After JSON edits that should hit Dreamcast: `python3 tools/bake_content.py --content content --out ports/dreamcast/src`
- After sprite edits that should hit Dreamcast: `python3 ports/dreamcast/tools/gen_sprites.py`

- A feature is not done until **both** engines read the same shared value.
  Content → `logic.json` rules → baker → web → DC, in that order
  (`docs/CONTENT_PLAN.md` §5).

## Do not

- Do not re-author maps, talk beats, species tables, **or Mason/fade/warp rules** inside `src/game/engine.ts` or `ports/dreamcast/src/main.c`.
- Do not invent a second logic file "just for DC". Bake `content/logic.json`.
- **Do not create a second copy of anything shared** — no second `content/`,
  no second sprite pack, no second `bake_content.py` / `gen_sprites.py`, no
  per-port data file. Full list and the reasons: `docs/CONTENT_PLAN.md` §3.
- Do not hand-merge or hand-edit generated files (`content_*.inc`,
  `sprites.h`, `*.elf`, `*.cdi`). Re-run the tool instead.
- Do not revive the SNES port. It was abandoned; do not add `.sfc` / 65816 sources.
- Do not revive the LÖVE2D port. It was abandoned; do not add `love/` sources.
- Do not revive the SDL2 / R36S PortMaster port. It was abandoned; do not add `native/` sources.
- Do not invent a second dialogue file "just for DC". Bake from JSON (uppercase happens in the baker).
- Do not hand-edit `ports/dreamcast/src/content_*.inc` or `ports/dreamcast/src/sprites.h`.

## If you need an old DC-only version

See [`backups/dreamcast-pre-fuse/README.md`](backups/dreamcast-pre-fuse/README.md). That snapshot is reference-only.
