# CURRENT_WORK.md

This writer is finished. Remaining work is **Grok A** only (plus ChatGPT A trainers if you still want them).

Do not hand-replace `world.json`. Do not empty `npcs`. Heavenfall is wild/boss only.

## Quarry (done on main)

- `maps.json` rows.quarry + cliffs tile `q`
- world + world_parts: mapIds/names, two-way cliffs↔quarry warps, grass pool peatling/slatekin/glowcap lv 5–7
- `MapId` includes quarry (`fc9c83b`)
- `save.mapOrder` includes quarry (`9b22176`)
- npcs still 34

## Grok A leftover

1. `src/game/data.ts` — add `QUARRY = normalize(raw.quarry)` and `quarry: QUARRY` in `MAPS`. File was too large to push from this agent.
2. `public/sprites/monsters/{peatling,mireback,glowcap,slatekin,gravelurk,cindermite}/1-4.png`

## ChatGPT A (optional)
Four forest/ruins trainers. Append npcs only.
