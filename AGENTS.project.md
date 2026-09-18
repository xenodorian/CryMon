# CryMon — project standing orders

This file is the game-specific contract. Platform rules in `AGENTS.md` still apply.

**This repo (xenodorian/CryMon) is the only tree, web first.** Both the web game
and the Dreamcast port (`ports/dreamcast/`) live here. The older Dreamcast copy
in `xenodorian/BeelzFight` is frozen and being retired, not a second home.

> **More than one agent works on this project at once.** Read
> [`docs/AGENT_COLLABORATION.md`](docs/AGENT_COLLABORATION.md) first — it is the
> collaboration contract for every agent (Grok, Emergent, Claude). One repo, one
> copy of everything shared, one direction of flow. Run
> `python3 tools/check_shared.py` before you finish.

Read [`docs/CRYMON.md`](docs/CRYMON.md) before changing story, maps, stats, or art.
Read [`CLAUDE.md`](CLAUDE.md) if you are Claude; same rules, DC-focused build steps.

## Do

- Edit **`content/*.json`** for species, items, maps, dialogue, warps, encounters, NPC marks, trainer kits, **and rules** (`logic.json`).
- Edit **`public/sprites/`** for art. Do not duplicate sprite packs per port.
- Keep web playable: `src/game/` loads JSON directly. Preview must keep running.
- After JSON edits that should hit Dreamcast: `python3 tools/bake_content.py --content content --out ports/dreamcast/src`
- After sprite edits that should hit Dreamcast: `python3 ports/dreamcast/tools/gen_sprites.py`

- A feature is not done until **both** engines read the same shared value.
  Content → `logic.json` rules → baker → web → DC, in that order
  (`docs/AGENT_COLLABORATION.md` §5).

## Do not

- Do not re-author maps, talk beats, species tables, **or Mason/fade/warp rules** inside `src/game/engine.ts` or `ports/dreamcast/src/main.c`.
- Do not invent a second logic file "just for DC". Bake `content/logic.json`.
- **Do not create a second copy of anything shared** — no second `content/`,
  no second sprite pack, no second `bake_content.py` / `gen_sprites.py`, no
  per-port data file, and no second repo. Full list and the decision procedure:
  `docs/AGENT_COLLABORATION.md`.
- Do not start or continue CryMon work in another repository. This tree is the
  only one. `BeelzFight/crymon-dreamcast/` is frozen and being retired.
- Do not hand-merge or hand-edit generated files (`content_*.inc`,
  `sprites.h`, `*.elf`, `*.cdi`). Re-run the tool instead.
- Do not revive the SNES port. It was abandoned; do not add `.sfc` / 65816 sources.
- Do not revive the LÖVE2D port. It was abandoned; do not add `love/` sources.
- Do not revive the SDL2 / R36S PortMaster port. It was abandoned; do not add `native/` sources.
- Do not invent a second dialogue file "just for DC". Bake from JSON (uppercase happens in the baker).
- Do not hand-edit `ports/dreamcast/src/content_*.inc` or `ports/dreamcast/src/sprites.h`.

## If you need an old DC-only version

See [`backups/dreamcast-pre-fuse/README.md`](backups/dreamcast-pre-fuse/README.md). That snapshot is reference-only.
