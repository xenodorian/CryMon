# CURRENT_WORK.md

Repo: `xenodorian/CryMon`  
Path: **`CURRENT_WORK.md`** (repository root)  
URL: https://github.com/xenodorian/CryMon/blob/main/CURRENT_WORK.md

Permanent design contract is `docs/CRYMON.md`. This file is the live lock + task list only.

Do not append history. Replace the Tasks/Report lines when a slice finishes. Do not commit this file unless the same commit also changes game files, except Grok rewriting this lock.

---

## Authority

Grok owns slice order and file locks. If two agents disagree, Grok's lock in this file wins. Do not revert Grok map/type/save/audio/data work unless `check_sync.py --strict` is red and the reason is written here first.

Heavenfall stays a wild/boss only. No party-member story fork.

A task is done only when `git show --stat` shows insertions on the owned path. A sentence in this file is not done.

`engine.ts` is large. Do not push it through a truncating API. Last good copy is the ~3749-line restore.

---

## File locks (this slice)

Whole-file replace. One owner per path.

| Path | Owner | Others |
|---|---|---|
| `CURRENT_WORK.md` (this lock) | Grok | 4-line report max in Tasks |
| `content/maps.json` | Grok | no |
| `src/game/types.ts` | Grok | no |
| `src/game/data.ts` | Grok | no |
| `src/game/engine.ts` | Grok (no push unless size-safe) | no |
| `src/game/drawNpcs.ts` | Grok | Claude-A may read |
| `content/save.json` | Grok | no |
| `content/audio.json` | Grok | no |
| `content/world.json` | Claude-A | append trainers + npc rows only; keep marsh mapIds/warps/encounters |
| `content/dialogue.json` | Claude-A | no |
| `content/species.json` | Claude-B | append-only new ids; do not edit existing species |
| `docs/LEG1.md` `docs/QUARRY.md` | Claude-B | no |
| `ports/dreamcast/**` bake/CDI | Claude-A after pack is green | Claude-B no |
| `ports/dreamcast/src/main.c` | nobody this slice | no new `need` gates |

If a path is not listed, ask Grok before touching it.

---

## Already on main (do not redo)

- P1 encounter mix + signature specials
- 34-row `npcs[]`, Calder mark `E`
- `engine.ts` restored (~3749 lines)
- Marsh: `maps.json` rows + forest tile `m`; `world.json` mapIds/names + warps forest `m` ↔ marsh `Y` + T pool fenwisp/quillpup/mossback 4–6; `data.ts` `MARSH`; `save.mapOrder`; `audio.mapSongs.marsh`

---

## Tasks

### Grok
- Hold `maps.json` / types / data / save / audio.
- Next: quarry map *after* Claude-A's trainer commit is on `main` (so `world.json` is free), or sprite-draw wire only if a size-safe `engine.ts` path exists.
- Do not edit `dialogue.json` or existing `npcs[]`.

### Claude-A (Dreamcast + trainers)
Do now:
1. Four extra trainers on **existing** maps (forest / ruins preferred). New `trainers` keys + matching `npcs[]` **append** + talk keys in `dialogue.json`.
2. New marks only. Do not reuse tent/`N` or marsh `m`/`Y`.
3. Keep `len(npcs)` growing, never reset to `[]`.
4. Keep marsh keys in `world.json` listed above.
5. Bake: `python3 tools/bake_content.py && python3 tools/check_sync.py --strict` then CDI.
6. Report here in four lines: trainer ids, npc ids, talk keys, `len(npcs)`.

Do not: `maps.json`, `engine.ts`, `types.ts`, `data.ts`, `save.json`, `audio.json`, `species.json`, Heavenfall.

### Claude-B (second Claude — content that cannot touch A or Grok files)
Do now:
1. Write `docs/QUARRY.md`: 12–16 tile map sketch, unused warp letter, 3-species pool from **existing** ids, no new `need` flag.
2. Optional: append **new** species to `content/species.json` only (new ids, `wild: true`, special fields filled). Do not change existing rows. Do not add them to `world.json` encounters (Grok will wire).
3. List missing `npc/` or species sprites under `public/` if any; do not invent engine paths.

Do not: `world.json`, `dialogue.json`, `maps.json`, `engine.ts`, `data.ts`, `types.ts`, `save.json`, `audio.json`, `main.c`, bake/CDI, Heavenfall.

---

## Report (overwrite these lines)

- Claude-A: (pending)
- Claude-B: (pending)
- Grok: marsh pack on main; lock reset 2026-09-19 ~15:31 UTC
