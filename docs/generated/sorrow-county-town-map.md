# Sorrow County Town Map (generated)

Source: `content/world_map_layout.json` → `content/town_map.json`
Anchor: **CryTown** (`veld`)

## Player projection

```text
💎 The Camp  (-2,0)
💎 CryTown  (0,0)
· The Cliffs  (2,0)
· The Marsh  (-2,1)
· The Forest  (0,1)
● The Quarry  (2,1)
· The Grove  (0,2)
· The Ruins  (2,2)
● Gauntlet  (0,3)
· The Reach  (2,3)
💎 Heavenfall Shrine  (0,4)
```

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

## Collapse

- house → **CryTown**
- gauntlet1, gauntlet2, gauntlet3, gauntlet4, gauntlet5 → **Gauntlet**
- gauntlet6 → **Heavenfall Shrine**

## Validation

All region nodes reachable from CryTown.
