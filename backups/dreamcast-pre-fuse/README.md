# Dreamcast snapshot from before the content fuse

Taken from `xenodorian/BeelzFight` commit `518ba2d` (tables still
hardcoded in `main.c`) plus the art pack that lived beside it.

| File | Why it's here |
|---|---|
| `main.c` | Full DC engine with inlined maps / TALK_* / SPECIES / ITEMS |
| `gen_sprites.py` | Old pathing (CryMon checkout arg + local `art/` first) |
| `PROGRESS_REPORT.md` | Claude overnight story/engine notes |
| `CONTENT_EXPANSION_REPORT.md` | New maps/monsters/NPCs notes |
| `art-and-placeholders.tar.gz` | DC `art/sprites` + `tools/placeholder_sprites` |

Canonical live sources are `content/*.json` and `public/sprites/`.
This folder is read-only reference.
