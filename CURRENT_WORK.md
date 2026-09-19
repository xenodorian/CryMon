# CURRENT_WORK.md

https://github.com/xenodorian/CryMon/blob/main/CURRENT_WORK.md

Do not hand-replace `world.json`. Do not empty `npcs`. Heavenfall is wild/boss only.

---

## Done on main (do not redo)

- P1 pools + signature specials
- Marsh map + forest `m` warps + marsh grass
- 34 `npcs` restored (`71f76d6`) and copied to `world_parts/npcs.json` (`6186698`). Calder mark `E`.
- Six new species in `species.json` / `SpeciesId` / `speciesOrder` / `sprites.json`: peatling→mireback, slatekin→gravelurk, glowcap, cindermite

## Still open

- Claude-B: quarry map (`maps.json` + `world_parts` warps/map_meta/encounters, then `merge_world.py`). Pool: peatling, slatekin, glowcap lv 5–7. No new `need`.
- Claude-A: four forest/ruins trainers in `world_parts/trainers.json` + `dialogue.json` only. Append npcs, do not reset the 34.
- Sprites: `public/sprites/monsters/<new-id>/1-4.png` not committed (art exists in chat only).
- Do not push `engine.ts` through a truncating API.

## Report
- Grok: pack + NPC restore closed 2026-09-19 ~16:08 UTC
- Claude-B: quarry pending
- Claude-A: extra trainers pending
