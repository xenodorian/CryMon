# Sorrow County Town Map (generated)

Source: `content/world_map_layout.json`
Anchor: **CryTown** (`veld`)

## Player projection

Legend: 💎 town / camp / shrine | ▫ route / travel

```text
💎 The Camp  (-1,0)
💎 CryTown  (0,0)
▫ The Cliffs  (1,0)
▫ The Marsh  (-1,1)
▫ The Forest  (0,1)
▫ The Quarry  (1,1)
▫ Gauntlet  (-1,2)
▫ The Grove  (0,2)
💎 Heavenfall Shrine  (-1,3)
▫ The Ruins  (0,3)
▫ The Reach  (0,4)
```

## Connections (region graph)

- CryTown → The Forest [down] _(veld→forest)_
- The Forest → The Grove [down] _(forest→grove)_
- CryTown → The Camp [down] need:beatCalder _(veld→camp)_
- CryTown → The Cliffs [down] _(veld→cliffs)_
- The Grove → The Ruins [down] need:beatShin _(grove→ruins)_
- The Ruins → The Reach [down] need:hasScroll _(ruins→reach)_
- The Forest → The Marsh [down] _(forest→marsh)_
- The Cliffs → The Quarry [down] _(cliffs→quarry)_
- The Grove → Gauntlet [down] need:choseHeavenfall _(grove→gauntlet1)_
- Gauntlet → Heavenfall Shrine [down] _(gauntlet5→gauntlet6)_

## Collapse rules applied

- house → **CryTown** (`veld`)
- gauntlet1, gauntlet2, gauntlet3, gauntlet4, gauntlet5 → **Gauntlet** (`gauntlet_route`)
- gauntlet6 → **Heavenfall Shrine** (`heavenfall_shrine`)
- Hidden: gauntlet

## Validation

All region nodes reachable from CryTown.

## Developer: playable maps → region

- `camp` → `camp` (The Camp)
- `cliffs` → `cliffs` (The Cliffs)
- `forest` → `forest` (The Forest)
- `gauntlet` → _hidden_
- `gauntlet1` → `gauntlet_route` (Gauntlet)
- `gauntlet2` → `gauntlet_route` (Gauntlet)
- `gauntlet3` → `gauntlet_route` (Gauntlet)
- `gauntlet4` → `gauntlet_route` (Gauntlet)
- `gauntlet5` → `gauntlet_route` (Gauntlet)
- `gauntlet6` → `heavenfall_shrine` (Heavenfall Shrine)
- `grove` → `grove` (The Grove)
- `house` → `veld` (CryTown)
- `marsh` → `marsh` (The Marsh)
- `quarry` → `quarry` (The Quarry)
- `reach` → `reach` (The Reach)
- `ruins` → `ruins` (The Ruins)
- `veld` → `veld` (CryTown)
