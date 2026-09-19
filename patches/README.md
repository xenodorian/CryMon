# Combat rewrite patches

Full rewritten files are large for the API; apply these or copy from a local build.

## Already on main
- content/species.json (power/speed/stat)
- content/logic.json (combat constants)
- src/game/data.ts (mint grow = str/100)
- src/game/types.ts
- tools/bake_content.py
- ports/dreamcast/src/content_species.inc
- ports/dreamcast/src/content_logic.inc

## Still needed
- src/game/engine.ts — remove minigame; damage = stat * power; dodge/block/barrier formulas
- ports/dreamcast/src/main.c — same combat + mint grow = str/100

Copy from your local working tree if you have the rewritten files, or ask the agent to retry the large-file push.
