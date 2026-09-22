# Sorrow County Town Map (generated)

Source: `content/world_map_layout.json` + `content/maps.json` (real tile grids) -> `content/town_map.json`
Anchor: **CryTown** (`veld`)
Scale: 1 cell = 10 real tiles. Grid: 20x27 cells.

## Destinations (gems) vs routes

💎 The Reach  cell(0,0 2x2)  real(20x16) [landmark]
· The Marsh  cell(9,0 2x2)  real(18x21) [route]
· The Ruins  cell(2,1 2x2)  real(20x19) [route]
💎 CryTown  cell(4,1 3x2)  real(30x23) [town]
· The Cliffs  cell(7,1 2x2)  real(18x20) [route]
· The Quarry  cell(11,1 2x1)  real(16x13) [cave]
💎 The Camp  cell(13,1 2x1)  real(16x10) [camp]
· The Forest  cell(13,2 3x3)  real(26x32) [route]
· Gauntlet  cell(4,3 2x18)  real(16x180) [route]
💎 The Prison  cell(13,5 3x2)  real(26x21) [landmark]
💎 Heavenfall Shrine  cell(4,21 2x2)  real(16x20) [shrine]

## Connections

- The Forest -> The Prison [south]
- CryTown -> The Cliffs [east] need:beatCalder
- Gauntlet -> Heavenfall Shrine [south]
- The Cliffs -> The Marsh [east]
- The Marsh -> The Quarry [east]
- The Quarry -> The Camp [east]
- CryTown -> The Ruins [west] need:beatShin
- The Ruins -> The Reach [west]
- CryTown -> Gauntlet [south] need:hasScroll
- The Camp -> The Forest [south]

## Validation

All region nodes reachable from CryTown, no cell overlaps.
