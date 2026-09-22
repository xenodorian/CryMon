# Sorrow County Town Map (generated)

Source: `content/world_map_layout.json` + `content/maps.json` (real tile grids) -> `content/town_map.json`
Anchor: **CryTown** (`veld`)
Scale: 1 cell = 10 real tiles. Grid: 15x32 cells.

## Destinations (gems) vs routes

· The Marsh  cell(5,0 2x2)  real(18x21) [route]
💎 CryTown  cell(0,1 3x2)  real(30x23) [town]
· The Cliffs  cell(3,1 2x2)  real(18x20) [route]
· The Quarry  cell(7,1 2x1)  real(16x13) [cave]
💎 The Camp  cell(9,1 2x1)  real(16x10) [camp]
· The Forest  cell(0,3 3x3)  real(26x32) [route]
💎 The Grove  cell(0,6 3x2)  real(26x21) [landmark]
· The Ruins  cell(3,6 2x2)  real(20x19) [route]
· Gauntlet  cell(0,8 2x18)  real(16x180) [route]
💎 The Reach  cell(3,8 2x2)  real(20x16) [landmark]
💎 Heavenfall Shrine  cell(0,26 2x2)  real(16x20) [shrine]

## Connections

- CryTown -> The Forest [south]
- The Forest -> The Grove [south]
- CryTown -> The Cliffs [east]
- The Grove -> The Ruins [east] need:beatShin
- The Ruins -> The Reach [south] need:hasScroll
- The Grove -> Gauntlet [south] need:choseHeavenfall
- Gauntlet -> Heavenfall Shrine [south]
- The Cliffs -> The Marsh [east]
- The Marsh -> The Quarry [east]
- The Quarry -> The Camp [east] need:beatCalder

## Validation

All region nodes reachable from CryTown, no cell overlaps.
