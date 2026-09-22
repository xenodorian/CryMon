# Sorrow County Town Map (generated)

Source: `content/world_map_layout.json` + `content/maps.json` (real tile grids) -> `content/town_map.json`
Anchor: **CryTown** (`veld`)
Scale: 1 cell = 10 real tiles. Grid: 11x32 cells.

## Destinations (gems) vs routes

💎 The Quarry  cell(1,0 2x1)  real(16x13) [cave]
💎 The Camp  cell(0,1 2x1)  real(16x10) [camp]
💎 CryTown  cell(2,1 3x2)  real(30x23) [town]
· The Cliffs  cell(5,1 2x2)  real(18x20) [route]
· The Forest  cell(2,3 3x3)  real(26x32) [route]
· The Marsh  cell(5,3 2x2)  real(18x21) [route]
💎 The Grove  cell(2,6 3x2)  real(26x21) [landmark]
· The Ruins  cell(5,6 2x2)  real(20x19) [route]
· Gauntlet  cell(2,8 2x18)  real(16x180) [route]
💎 The Reach  cell(5,8 2x2)  real(20x16) [landmark]
💎 Heavenfall Shrine  cell(2,26 2x2)  real(16x20) [shrine]

## Connections

- CryTown -> The Forest [south]
- The Forest -> The Grove [south]
- CryTown -> The Camp [south] need:beatCalder
- CryTown -> The Cliffs [east]
- The Grove -> The Ruins [east] need:beatShin
- The Ruins -> The Reach [south] need:hasScroll
- The Forest -> The Marsh [east]
- The Cliffs -> The Quarry [west]
- The Grove -> Gauntlet [south] need:choseHeavenfall
- Gauntlet -> Heavenfall Shrine [south]

## Validation

All region nodes reachable from CryTown, no cell overlaps.
