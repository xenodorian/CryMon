# Sorrow County Town Map (generated)

Source: `content/world_map_layout.json` → `content/town_map.json`
Anchor: **CryTown** (`veld`)
Terrain grid: 46×46 tiles (procedural)

## Destinations (gems) vs routes

💎 The Camp  (-2,0) [camp]
💎 CryTown  (0,0) [town]
· The Cliffs  (2,0) [route]
· The Marsh  (-2,1) [route]
· The Forest  (0,1) [route]
· The Quarry  (2,1) [route]
💎 The Grove  (0,2) [landmark]
· The Ruins  (2,2) [route]
· Gauntlet  (0,3) [route]
💎 The Reach  (2,3) [landmark]
💎 Heavenfall Shrine  (0,4) [shrine]

## Connections

- CryTown → The Forest [down]
- The Forest → The Grove [down]
- CryTown → The Camp [down] need:beatCalder
- CryTown → The Cliffs [down]
- The Grove → The Ruins [right] need:beatShin
- The Ruins → The Reach [down] need:hasScroll
- The Forest → The Marsh [down]
- The Cliffs → The Quarry [down]
- The Grove → Gauntlet [down] need:choseHeavenfall
- Gauntlet → Heavenfall Shrine [down]

## Validation

All region nodes reachable from CryTown.
