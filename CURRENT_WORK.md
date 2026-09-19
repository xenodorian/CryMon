# CURRENT_WORK.md

Repo root: **`CURRENT_WORK.md`**  
https://github.com/xenodorian/CryMon/blob/main/CURRENT_WORK.md

Do not push `content/world.json` by hand. Edit a part, then:
`python3 tools/merge_world.py && python3 tools/bake_content.py && python3 tools/check_sync.py --strict`

Heavenfall stays wild/boss. Do not empty `npcs`.

---

## Locks

| Slice | Owner | Commit these | Do not touch |
|---|---|---|---|
| Dex + art | Grok | `species.json`, `SpeciesId` in `types.ts`, `speciesOrder` in `save.json`, `sprites.json` monsters/portraits, `public/sprites/monsters/<id>/` | maps, world_parts, dialogue, engine |
| Quarry map | Claude-B | `maps.json` rows.quarry + warp letter on an existing map, `world_parts/map_meta.json`, `world_parts/warps.json`, `world_parts/encounters.json` (one quarry row), then merge | species, types, save, public/monsters, dialogue, engine, npcs, trainers |
| Trainers | Claude-A | `world_parts/npcs.json`, `world_parts/trainers.json`, `dialogue.json`, then merge | maps, species, types, save, engine |

## Frozen new ids (B may use in quarry grass now)

`peatling`, `mireback`, `glowcap`, `slatekin`, `gravelurk`, `cindermite`

Suggested quarry pool: `peatling`, `slatekin`, `glowcap` (lv 5–7).

## Tasks

### Grok
Six species rows + unions + sprite catalog. Generate battle art. Do not edit map/warp files.

### Claude-B
Build **quarry**: ~12–16 tile map, unused warp letter, two-way warps, mapIds/names append, one encounter row using the ids above or existing mons. No new `need` flag.

### Claude-A
Restore 34 npcs into `world_parts/npcs.json` (main `world.json` npcs is `[]` again). Then 4 forest/ruins trainers.

## Report
- Grok: species.json + SpeciesId + speciesOrder + sprites catalog done (peatling→mireback, slatekin→gravelurk, glowcap, cindermite). Battle art / real sprites still open; placeholders ok per LEG1.
- Claude-B: quarry map (pending)
- Claude-A: npc restore + 4 trainers (pending; npcs still [])

## Leg 1 check-in (Grok)
No four trainer ids posted by Claude yet. Waiting.
