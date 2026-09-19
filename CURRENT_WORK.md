# CURRENT_WORK.md

https://github.com/xenodorian/CryMon/blob/main/CURRENT_WORK.md

Do not hand-replace `world.json`. Do not empty `npcs`. Heavenfall is wild/boss only.

Grok B is done. All former Grok B work is now **Grok A**.

---

## Locks

| Agent | Does | Does not |
|---|---|---|
| Grok A | sprites `public/sprites/monsters/{peatling,mireback,glowcap,slatekin,gravelurk,cindermite}/1-4.png`; pack species if needed | do not wipe npcs; do not stub engine.ts |
| Claude-B | quarry map + world_parts warps/encounters/map_meta | species, sprites, engine |
| ChatGPT A | 4 trainers in world_parts/trainers.json + dialogue.json | maps, species, sprites, engine |

## Done
34 npcs, marsh, 6 species rows in the pack. Sprite *art* exists in chat; PNG folders not on main yet.

## Grok A next
Commit the 4-frame folders (glimmoth layout). Ids already in `sprites.json` monsters[].
