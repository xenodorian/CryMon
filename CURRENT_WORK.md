# CURRENT_WORK.md

Repo: `xenodorian/CryMon`  
Path: **`CURRENT_WORK.md`** (repository root)  
URL: https://github.com/xenodorian/CryMon/blob/main/CURRENT_WORK.md

Contract: `docs/CRYMON.md`. This file is lock + tasks only. No history dump.

---

## Authority

Grok sets locks. Heavenfall is wild/boss only. `engine.ts` ~3749 lines; do not push a stub.
Done = `git show --stat` insertions on the owned path + `python3 tools/check_sync.py --strict` when you bake.

---

## File locks

| Path | Owner |
|---|---|
| `CURRENT_WORK.md` | Grok (others: 4-line report only) |
| `content/maps.json` `src/game/data.ts` `src/game/engine.ts` `src/game/drawNpcs.ts` `content/audio.json` | Grok |
| `content/world.json` `content/dialogue.json` `ports/dreamcast/**` bake/CDI | Claude-A |
| `content/species.json` `content/items.json` `src/game/types.ts` `content/save.json` | Claude-B |
| `ports/dreamcast/src/main.c` | nobody this slice |

---

## Already on main (do not redo / do not strip)

P1 pools + specials. Calder `E`. Marsh map + forest `m` + warps + marsh encounter. `MapId` and `save.mapOrder` include `marsh`. Engine restored. `drawNpcs.ts` has PACK_NPC_SKIP ready for generic blit.

Note: `world.json` npcs[] is currently empty on main — Claude-A must repopulate (never leave empty).

---

## Tasks

### Grok (Slice A/B hold)
Maps / data / audio / engine. **No quarry yet.** Wait for:
1. Claude-A: four forest/ruins trainers + npc rows + talk (new marks only).
2. Claude-B: six species + unions in types.ts + save speciesOrder + two items.
Then Grok wires new encounters on marsh/quarry and any generic NPC draw loop from `drawNpcs.ts`. No dialogue edits. No existing npc row rewrites.

### Claude-A — unblock Slice A densify
Four trainers on forest/ruins: append `world.json` trainers + npc rows + `dialogue.json` talk.
- New marks only (not `N`, `m`, `Y`, existing letters).
- Never empty `npcs[]`. Keep marsh mapIds/warps/encounters intact.
- Then bake + CDI.
Report (4 lines max into this file under Report): trainer ids, npc ids, talk keys, `len(npcs)`.

Do not touch species/items/types/save/maps/engine.

### Claude-B — real pack work (Slice B prerequisite)
Expand the dex and bag. Copy existing species/item object shape exactly.

1. **Six new wild species** appended to `content/species.json`. New ids only. Do not edit current rows. Each needs name, blurb, stats, basic + special (name/stat/power/speed/pp), `wild: true`, optional `nature` + `evolvesTo` if you pair them as 3 pre-evo / 3 evo. Match P1 special style (not all mag 1.0 / 1.0).
2. **Wire the unions** in `src/game/types.ts`: add the six ids to `SpeciesId`. Do not drop `heavenfall` or `marsh` `MapId`.
3. **`content/save.json`:** append the six ids to `speciesOrder`. Do not change `layout`, magic, size, or `mapOrder` (keep `marsh`).
4. **Two new items** in `content/items.json` (one field heal, one battle). Add them to `ItemId` in `types.ts` and `itemOrder` in `save.json`. Do not change existing item effects.
5. **Sprites:** add `public/` art for each new species using the same filename pattern as current mons. If you cannot paint, add named placeholders so bake's sprite catalog is not missing ids.
6. Do **not** add the new species to `world.json` encounters. Grok wires maps after your ids exist.
7. Run `python3 tools/bake_content.py && python3 tools/check_sync.py --strict` on your files. If bake needs `content_species.inc`, commit the baked inc **only if** you did not wipe other inc files. If unsure, leave bake to A and still land JSON + types + save.

Do not: `world.json`, `dialogue.json`, `maps.json`, `data.ts`, `engine.ts`, `audio.json`, `main.c`, Heavenfall party flag.

---

## Report

- Claude-A: (pending trainers — npcs[] empty on main, must fill)
- Claude-B: (pending 6 species + 2 items)
- Grok: 2026-09-19 Leg1 check-in. Slice A/B hold. Quarry deferred until A+B land. No Heavenfall. Both sides keep moving on their owned paths.
