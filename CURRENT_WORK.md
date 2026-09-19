# CURRENT_WORK.md

Repo root: **`CURRENT_WORK.md`**  
https://github.com/xenodorian/CryMon/blob/main/CURRENT_WORK.md

---

## How independent work works now

Do **not** push `content/world.json` by hand. It is assembled.

Edit only your part, then:

```
python3 tools/merge_world.py
python3 tools/bake_content.py && python3 tools/check_sync.py --strict
```

Parts:

| File | Owner | Project |
|---|---|---|
| `content/world_parts/npcs.json` | Claude-A | restore 34 NPCs + append 4 trainer rows |
| `content/world_parts/trainers.json` | Claude-A | 4 new trainer kits |
| `content/dialogue.json` | Claude-A | talk for those 4 |
| `content/world_parts/warps.json` | Grok | new map links |
| `content/world_parts/encounters.json` | Grok | grass pools |
| `content/world_parts/map_meta.json` | Grok | mapIds / names |
| `content/maps.json` `data.ts` `audio.json` | Grok | tiles / runtime |
| `content/species.json` `items.json` `types.ts` `save.json` | Claude-B | 6 species + 2 items |
| `engine.ts` | Grok, no stub push | |

`merge_world.py` writes `world.json` from those parts. Two agents can commit different part files at the same time; only the merge step rebuilds the combined file.

Heavenfall stays wild/boss. Do not empty `npcs`.

---

## Bug on main right now

`content/world.json` `npcs` is `[]` again. Claude-A first job: restore rows into `world_parts/npcs.json` from history, merge, bake.

---

## Tasks

### Claude-A
1. Restore `world_parts/npcs.json` from last good 34-row commit.
2. Append 4 forest/ruins trainers in `world_parts/trainers.json` + matching npc rows + `dialogue.json`.
3. `python3 tools/merge_world.py` then bake + CDI.
4. Report ids + `len(npcs)`.

### Claude-B
Six new species + two items + `SpeciesId`/`ItemId` + `speciesOrder`/`itemOrder` + sprites. Do not edit world parts or `world.json`.

### Grok
Warps/encounters/maps only. Next quarry rows in `maps.json` + `warps.json` + `map_meta.json`, then merge.

## Report
- Claude-A: (pending npc restore + 4 trainers)
- Claude-B: (pending 6 species + 2 items)
- Grok: world_parts + merge script on main 2026-09-19 ~15:38 UTC
