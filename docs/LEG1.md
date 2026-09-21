# CryMon — Leg 1 expansion plan

North star the user named: a game as expansive as Pokémon FireRed.
That is multi-leg. This file is **only Leg 1**. Story locks in
`docs/CRYMON.md` still win (Heavenfall/father stay narrative-only;
Weeping Army / Anne's 5-crystal gift / Shinigami scroll unchanged).

## Where we are

- 8 maps: house, CryTown, forest, grove, camp, cliffs, ruins, reach
- 20 species, 7 evolve lines, 7 crystals
- Wild grass on CryTown/forest/cliffs/reach plus Claude's grove/camp/ruins patches
- P1 on `main`: unevolved early pools, evolved late pools, 5 signature specials
- Trainers exist (Calder, camp trio, sentry, Cross, Mason, Shinigami, Cathleen)
- Not FireRed-scale: no badge circuit, no boxed PC, few routes, 20 mons

## Leg 1 success (ship this before starting Leg 2)

1. **Route density** — every outdoor map still has ≥3 wild species. Forest and ruins each gain 2 extra trainers (JSON kits + NPC rows + talk).
2. **Two new maps** (append-only `mapIds` / `mapOrder`):
   - `marsh` — optional side route off forest (new warp letter, 3-species grass, 2 trainers).
   - `quarry` — optional side route off cliffs after `beatSentry` (mid levels, 3-species grass, 1 trainer).
3. **+6 species** — 3 unevolved + 3 evos. `PLACEHOLDER_ART` is allowed. Append `speciesOrder`. No Heavenfall as a catch.
4. **Two crystal wardens** — JSON trainers + persist flags (`badgeQuartz`, `badgeOpal` working names). Not named "gyms". Gates are optional side content, not a story fork.
5. **Web NPC draw** iterates `NPCS` (Grok). DC already scripts from JSON; Claude only changes C if a new warp `need` code is required.
6. Every pack edit: bake + `check_sync.py --strict`. CDI rebuild is Claude/CI.

## Not this leg

Elite Four, 8-badge circuit, PC box, HMs, 151 species, new ending,
Heavenfall-in-party, father resurrection as gameplay.

## Turn order

| Slice | Grok (web + JSON) | Claude (DC + bake/CDI) |
|---|---|---|
| A (now) | Plan file. Extra forest/ruins trainer *rows drafted*. NPC blit-list dedup in `engine.ts`. | Pull P1. Confirm `specialStat` in C. CDI after CI. Play-check new pools + 5 specials. Stay off veld/forest/cliffs/reach pools unless broken. |
| B | `marsh` map JSON + warps + talk + `MapId` + `data.ts`. | Bake, wire warp `need` only if a new gate exists, CDI. |
| C | 3 new species JSON + dex order + placeholder sprites. | `gen_sprites.py` if art landed; CDI. |
| D | First warden + flag in `save.json` (append). | DC flag table + compile. |
| E | `quarry` map + 3 more species. | Same bake/CDI path. |
| F | Second warden. Web QA skipTo if needed. | Playtest both side routes on hardware/emulator. |

## File ownership reminder

JSON + `public/sprites/` = both. `src/game/` = Grok. `main.c` = Claude.
Never hand-edit `content_*.inc` / `sprites.h`. Never reorder `mapOrder` or `speciesOrder`.
