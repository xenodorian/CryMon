# CURRENT_WORK.md

https://github.com/xenodorian/CryMon/blob/main/CURRENT_WORK.md

Do not hand-replace `world.json`. Do not empty `npcs`. Heavenfall is wild/boss only.

---

## Locks

| Agent | Does | Does not |
|---|---|---|
| Grok B | `public/sprites/monsters/{peatling,mireback,glowcap,slatekin,gravelurk,cindermite}/1-4.png` | maps, world, species.json, types, save, engine |
| Claude-B | quarry map + world_parts warps/encounters/map_meta | species, sprites, engine |
| ChatGPT A | 4 trainers in world_parts/trainers.json + dialogue.json | maps, species, sprites, engine |

## Done
34 npcs, marsh, 6 species rows in the pack.

## Grok B now
Commit 4-frame folders matching `glimmoth` layout. Ids already in `sprites.json` monsters[].
