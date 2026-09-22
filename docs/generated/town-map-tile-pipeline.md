# Sorrow County Town Map — tile pipeline

## Three tracks (2026-09-21)

### 1. Procedural map generation
`tools/generate-town-map.mjs` still takes `content/world_map_layout.json` as
source of truth, then:

1. Builds the region graph (collapse interiors / gauntlet floors)
2. Places destination + route nodes
3. **Paints a procedural terrain grid** (`terrain` in `content/town_map.json`):
   - water border + irregular coast
   - landmass covering the graph
   - biome stamps from node kind (forest, marsh, cliff, sand, grass)
   - Bresenham **road** carve along edges

### 2. Tile-based rendering
Terrain is a `width × height` grid of tile codes:

| Code | Meaning |
|------|---------|
| W | water |
| L | land |
| G | grass |
| F | forest |
| M | marsh |
| C | cliff |
| R | road |
| S | sand |

- Static art: `public/maps/sorrow-county-town-map.svg` draws one crisp rect per tile (with 2×2 micro-dither on F/M/C).
- In-game: Pause → Map draws the same grid on canvas (`imageSmoothingEnabled = false`).

### 3. Pixel art terrain details
- Checker dither on adjacent tiles
- Forest/marsh/cliff use 2×2 sub-pixels in SVG
- Roads are 3-wide plus-shaped carves so corridors read like FireRed routes
- **Gems only** on destinations (CryTown, Camp, Grove, Reach, Heavenfall Shrine)

Regenerate:

```bash
node tools/generate-town-map.mjs
```
