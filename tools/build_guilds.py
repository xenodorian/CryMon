#!/usr/bin/env python3
"""Guild halls, haunted buildings and quest spots on hand-built maps.

    python3 tools/build_guilds.py
    python3 tools/merge_world.py

Source of truth is the SITES / MARKS tables below (map layout only; the
NPCs, trainers and dialogue that use these marks are authored JSON). For
every site it:

  - turns one wall tile of an existing decorative building (or a hut it
    stamps) into a door, and writes the interior map's rows,
  - registers the interior (map_meta, save mapOrder, types.ts, data.ts),
  - rewrites the door warps both ways (with an optional `need` gate).

MARKS places single-letter NPC spots (graves, shrines, townsfolk, quest
pickups) on the nearest walkable '.' tile to a target, away from warp
tiles. Safe to re-run: a mark that's already on its map is left alone.

Tile chars (maps.json tileArt): 'w' door, 'x' / 'z' interior floor spots,
'd' 'f' 'i' 'j' 'l' 'n' 'o' 'p' grass spots on outdoor maps.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAPS_JSON = ROOT / "content/maps.json"
MAP_META = ROOT / "content/world_parts/map_meta.json"
WARPS_JSON = ROOT / "content/world_parts/warps.json"
SAVE_JSON = ROOT / "content/save.json"
TYPES_TS = ROOT / "src/game/types.ts"
DATA_TS = ROOT / "src/game/data.ts"

TILE_ART = {"w": "tile-door", "(": "tile-door", ")": "tile-door", "0": "tile-door", "x": "tile-floor", "z": "tile-floor",
            "d": "tile-grass", "f": "tile-grass", "i": "tile-grass", "j": "tile-grass",
            "l": "tile-grass", "n": "tile-grass", "o": "tile-grass", "p": "tile-grass"}

HALL = [
    "HHHHHHHHHHHH",
    "HFFFFFFFFFFH",
    "HFFxFFFFzFFH",
    "HFFFFFFFFFFH",
    "HFFFFFFFFFFH",
    "HFFFFFFFFFFH",
    "HFFFFFFFFFFH",
    "HHHHHDHHHHHH",
]
# Same shape as a Leg 3 base: one-tile hall, spots s/t block it, a at the top.
HAUNTED = [
    "HHHHHHHHHHH",
    "HFFFFFFFFFH",
    "HFFFFaFFFFH",
    "HFFFFFFFFFH",
    "HHHHFFFHHHH",
    "HHHHHFHHHHH",
    "HHHHHtHHHHH",
    "HHHHHFHHHHH",
    "HFFFFFFFFFH",
    "HHHHHFHHHHH",
    "HHHHHsHHHHH",
    "HHHHHFHHHHH",
    "HFFFFFFFFFH",
    "HHHHHDHHHHH",
]
HUT = ["rrr", "HwH"]
# The six once-decorative houses of the Ruins and the Reach.
LIBRARY = [
    "HHHHHHHHHHHH",
    "HCCFCCFCCFCH",
    "HFFxFFFFzFFH",
    "HFFFFFFFFFFH",
    "HCCFFFFFFCCH",
    "HFFFFFFFFFFH",
    "HFFFFFFFFFFH",
    "HHHHHDHHHHHH",
]
INN = [
    "HHHHHHHHHHHH",
    "HBFBFBFFFFFH",
    "HFFFFFFxFFFH",
    "HFFFFFFFFFFH",
    "HFFzFFFFFFFH",
    "HFFFFFFFFCCH",
    "HFFFFFFFFFFH",
    "HHHHHDHHHHHH",
]
COTTAGE = [
    "HHHHHHHHHH",
    "HBFFFFFCCH",
    "HFFFxFFFFH",
    "HFFFFFFFFH",
    "HFFFFFFzFH",
    "HFFFFFFFFH",
    "HHHHDHHHHH",
]
HERMIT = [
    "HHHHHHHHHH",
    "HCFFFFFFBH",
    "HFFFFxFFFH",
    "HFFFFFFFFH",
    "HFFFFFFFFH",
    "HFFFFFFFFH",
    "HHHHDHHHHH",
]

# (outdoor map, door (col,row), stamp hut at door-1/-1?, interior id, label,
#  rows, need flag, fail talk[, door char]). Warps match by tile char, so a
# second door on the same map needs its own char (DOOR_CHARS; 'w' default).
SITES = [
    ("ruins", (4, 4), False, "ghostcrypt", "THE GHOST GUILD", HALL, "talkedReach", "cryptLocked"),
    ("reach", (15, 4), False, "hauntedhall", "THE HAUNTED HALL", HAUNTED, "joinedGhost", "hauntedLocked"),
    ("veld", (4, 10), False, "heroeshall", "THE HEROES GUILD", HALL, None, None),
    ("marsh", (14, 18), True, "thievesden", "THE THIEVES DEN", HALL, None, None),
    ("ruins", (15, 4), False, "ruinslibrary", "THE OLD LIBRARY", LIBRARY, None, None, "("),
    ("ruins", (4, 12), False, "ruinsinn", "THE RUINS INN", INN, None, None, ")"),
    ("ruins", (15, 12), False, "brannhouse", "BRANN'S HOUSE", COTTAGE, None, None, "0"),
    ("reach", (4, 4), False, "hermithut", "THE HERMIT'S HUT", HERMIT, None, None, "("),
    ("reach", (4, 13), False, "sagehouse", "THE SAGE'S HOUSE", COTTAGE, None, None, ")"),
    ("reach", (15, 13), False, "emptyhouse", "THE EMPTY HOUSE", COTTAGE, None, None, "0"),
]
DOOR_CHARS = ("w", "(", ")", "0")

# (map, char, target (col,row)): quest spots on hand-built maps.
MARKS = [
    ("ruins", "d", (16, 14)),   # grave of Ines
    ("grove", "d", (21, 18)),   # grave of Tomas
    ("marsh", "d", (3, 17)),    # grave of Oriel
    ("cliffs", "f", (15, 2)),   # shrine
    ("quarry", "f", (13, 9)),   # shrine
    ("forest", "f", (22, 17)),  # shrine
    # Heroes / Thieves Guild targets (hint NPCs until Max joins a side)
    ("veld", "i", (20, 16)),    # Sir Aldous (Heroes Guild)
    ("ruins", "i", (6, 14)),    # Dame Brin (Heroes Guild)
    ("cliffs", "i", (4, 12)),   # Captain Rook (Heroes Guild)
    ("forest", "i", (7, 18)),   # Red Mallory (wanted)
    ("quarry", "i", (12, 2)),   # Silas the Fence (wanted)
    # CryTown townsfolk and their sidequest spots
    ("veld", "j", (19, 12)),    # the crier
    ("veld", "l", (9, 3)),      # Old Tam
    ("veld", "n", (25, 17)),    # Lina
    ("veld", "o", (26, 17)),    # Rolo, once led home
    ("veld", "p", (8, 14)),     # Collector Juno
    ("grove", "j", (4, 3)),     # Tam's watch (pickup), at the Prison
    ("cliffs", "j", (14, 15)),  # Rolo, lost
    # Sephirot path spots: pickups 'l', lost townsfolk 'p', outlaws 'o'
    ("tau", "p", (2, 13)),      # Pip (Malkuth)
    ("peh", "l", (28, 4)),      # Sera's locket (Netzach)
    ("mem", "o", (2, 11)),      # Knife-Hand Garrow (Hod)
    ("samekh", "p", (2, 14)),   # Tilly (Tiferet)
    ("heth", "l", (2, 11)),     # Lune's map (Gevurah)
    ("daleth", "o", (28, 5)),   # Deserter Kael (Binah)
    ("aleph", "p", (16, 9)),    # Sister Iona (Chokmah)
    ("marsh", "n", (15, 3)),    # Maren's rag doll (the Reach's empty house)
]


def load(p: Path):
    return json.loads(p.read_text())


def save(p: Path, data) -> None:
    p.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def warp_tiles(warps, map_id):
    return {w["tile"] for w in warps if w["from"] == map_id}


def place_mark(rows: list[str], ch: str, target, avoid: set[str]) -> list[str]:
    if any(ch in r for r in rows):
        return rows
    grid = [list(r) for r in rows]
    h, w = len(grid), len(grid[0])
    tx, ty = target
    best = None
    for y in range(1, h - 1):
        for x in range(1, w - 1):
            if grid[y][x] != ".":
                continue
            near = any(grid[y + dy][x + dx] in avoid for dy in (-1, 0, 1) for dx in (-1, 0, 1))
            if near:
                continue
            d = (x - tx) ** 2 + (y - ty) ** 2
            if best is None or d < best[0]:
                best = (d, x, y)
    if best is None:
        raise SystemExit(f"no free tile for mark {ch!r}")
    grid[best[2]][best[1]] = ch
    return ["".join(r) for r in grid]


def main() -> None:
    maps_data = load(MAPS_JSON)
    meta = load(MAP_META)
    warps_data = load(WARPS_JSON)
    save_data = load(SAVE_JSON)
    rows = maps_data["rows"]
    for ch, a in TILE_ART.items():
        maps_data["tileArt"][ch] = a

    interiors = {s[3] for s in SITES}
    warps = [w for w in warps_data["warps"] if w["from"] not in interiors and w["to"] not in interiors]
    for outdoor, (dc, dr), hut, mid, label, tmpl, need, fail, *door in SITES:
        door = door[0] if door else "w"
        grid = [list(r) for r in rows[outdoor]]
        if hut:
            for yy, line in enumerate(HUT):
                for xx, c in enumerate(line):
                    grid[dr - 1 + yy][dc - 1 + xx] = c
        grid[dr][dc] = door
        rows[outdoor] = ["".join(r) for r in grid]
        rows[mid] = list(tmpl)
        if mid not in meta["mapIds"]:
            meta["mapIds"].append(mid)
        if mid not in save_data["mapOrder"]:
            save_data["mapOrder"].append(mid)
        meta["mapNames"][mid] = label
        into = {"from": outdoor, "tile": door, "to": mid, "spawn": "D", "dir": "up", "oy": -32}
        if need:
            into["need"] = need
            into["failTalk"] = fail
        warps.append(into)
        warps.append({"from": mid, "tile": "D", "to": outdoor, "spawn": door, "dir": "down", "oy": 40})

    for m, ch, target in MARKS:
        rows[m] = place_mark(rows[m], ch, target, warp_tiles(warps, m) | set(DOOR_CHARS))

    warps_data["warps"] = warps
    save(MAPS_JSON, maps_data)
    save(MAP_META, meta)
    save(WARPS_JSON, warps_data)
    save(SAVE_JSON, save_data)

    types_text = TYPES_TS.read_text()
    mm = re.search(r"export type MapId = ([^\n]+);", types_text)
    have = set(re.findall(r'"([a-z0-9_]+)"', mm.group(1)))
    new_ids = [i for i in meta["mapIds"] if i not in have]
    if new_ids:
        add = "".join(' | "%s"' % i for i in new_ids)
        types_text = types_text.replace(mm.group(0), f"export type MapId = {mm.group(1)}{add};")
        TYPES_TS.write_text(types_text)
    data_text = DATA_TS.read_text()
    missing = [i for i in meta["mapIds"] if not re.search(rf"raw\.{re.escape(i)}\b", data_text)]
    if missing:
        consts = "\n".join(f"export const {i.upper()} = normalize(raw.{i});" for i in missing)
        at = data_text.index("export const MAPS = {")
        data_text = data_text[:at] + consts + "\n\n" + data_text[at:]
        close = data_text.index("} as const;", data_text.index("export const MAPS = {"))
        data_text = data_text[:close] + "".join(f"  {i}: {i.upper()},\n" for i in missing) + data_text[close:]
        DATA_TS.write_text(data_text)
    print(f"guilds: {len(SITES)} buildings, {len(MARKS)} marks")


if __name__ == "__main__":
    main()
