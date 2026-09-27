#!/usr/bin/env python3
"""Leg 3 map layout: military bases, Keter's palace, and their doors.

    python3 tools/build_leg3.py
    python3 tools/merge_world.py

Reads content/logic.json `leg3` (the source of truth for which city holds
which General, the medal chain and the palace) and writes:

  - maps.json rows for every base<city> map and palaceketer,
  - the building stamped into each city (also applied by build_sephirot.py,
    which rewrites city rows from scratch, via stamp_city_building()),
  - map registration (map_meta mapIds/mapNames, save mapOrder, types.ts
    MapId, data.ts MAPS), and
  - the door warps both ways, the base door gated on the previous medal.

Safe to re-run: rows and Leg 3 warps are rewritten, everything else is
left alone. Trainers, NPCs and dialogue are authored JSON, not generated.

Tile chars (maps.json tileArt): 'b' base/palace door in a city (tile-door),
'a' the General's / Nero's spot, 's' and 't' the two guards (all floor).
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAPS_JSON = ROOT / "content/maps.json"
LOGIC_JSON = ROOT / "content/logic.json"
MAP_META = ROOT / "content/world_parts/map_meta.json"
WARPS_JSON = ROOT / "content/world_parts/warps.json"
SAVE_JSON = ROOT / "content/save.json"
TYPES_TS = ROOT / "src/game/types.ts"
DATA_TS = ROOT / "src/game/data.ts"

DOOR = "b"
TILE_ART = {"b": "tile-door", "a": "tile-floor", "s": "tile-floor", "t": "tile-floor"}

# Stamped into a 16x12 Sephirot city: roof, roof, wall with the door.
# Rows 3-5, cols 5-10 stay clear of every gate's arrival tile (row 1/10,
# col 1/14), so no gate is ever boxed in.
BUILDING = [
    "rrrrrr",
    "rrrrrr",
    "HH" + DOOR + "HHH",
]
BUILDING_AT = (5, 3)  # col, row of the top-left corner

# Interior. A one-tile hall with a guard in each narrow stretch: you
# cannot reach the General at 'a' without going through 's' then 't'.
INTERIOR = [
    "HHHHHHHHHHH",
    "HFFFFFFFFFH",
    "HFFFFaFFFFH",
    "HFFFFFFFFFH",
    "HHHHFFFHHHH",
    "HHHHHFHHHHH",
    "HHHHHtHHHHH",
    "HHHHHFHHHHH",
    "HFFFFFFFFFH",
    "HFFFFFFFFFH",
    "HHHHHFHHHHH",
    "HHHHHsHHHHH",
    "HHHHHFHHHHH",
    "HFFFFFFFFFH",
    "HFFFFFFFFFH",
    "HHHHHDHHHHH",
]


def load(p: Path):
    return json.loads(p.read_text())


def save(p: Path, data) -> None:
    p.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def leg3() -> dict:
    return load(LOGIC_JSON)["leg3"]


def building_cities() -> set[str]:
    L = leg3()
    return {g["city"] for g in L["generals"]} | {L["palace"]["city"]}


def stamp_city_building(grid: list[list[str]], city_id: str) -> None:
    """Draw the base (or palace) front into a city grid in place."""
    if city_id not in building_cities():
        return
    c0, r0 = BUILDING_AT
    for dy, line in enumerate(BUILDING):
        for dx, ch in enumerate(line):
            grid[r0 + dy][c0 + dx] = ch


def stamp_rows(rows: list[str], city_id: str) -> list[str]:
    grid = [list(r) for r in rows]
    stamp_city_building(grid, city_id)
    return ["".join(r) for r in grid]


def main() -> None:
    L = leg3()
    maps_data = load(MAPS_JSON)
    meta = load(MAP_META)
    warps_data = load(WARPS_JSON)
    save_data = load(SAVE_JSON)
    rows = maps_data["rows"]
    art = maps_data["tileArt"]
    for ch, a in TILE_ART.items():
        art[ch] = a

    sites = [(g["city"], g["base"], g.get("needMedal"), f"{g['city'].upper()} BASE") for g in L["generals"]]
    p = L["palace"]
    sites.append((p["city"], p["map"], p.get("need"), "NERO'S PALACE"))

    leg3_maps = {m for _c, m, _n, _l in sites}
    warps = [w for w in warps_data["warps"]
             if w["from"] not in leg3_maps and w["to"] not in leg3_maps]

    for city, mid, need, label in sites:
        rows[city] = stamp_rows(rows[city], city)
        rows[mid] = list(INTERIOR)
        if mid not in meta["mapIds"]:
            meta["mapIds"].append(mid)
        if mid not in save_data["mapOrder"]:
            save_data["mapOrder"].append(mid)
        meta["mapNames"][mid] = label
        into = {"from": city, "tile": DOOR, "to": mid, "spawn": "D", "dir": "up", "oy": -32}
        if need:
            into["need"] = need
            into["failTalk"] = "baseLocked" if mid.startswith("base") else "palaceLocked"
        warps.append(into)
        warps.append({"from": mid, "tile": "D", "to": city, "spawn": DOOR, "dir": "down", "oy": 40})

    warps_data["warps"] = warps
    save(MAPS_JSON, maps_data)
    save(MAP_META, meta)
    save(WARPS_JSON, warps_data)
    save(SAVE_JSON, save_data)

    types_text = TYPES_TS.read_text()
    m = re.search(r"export type MapId = ([^\n]+);", types_text)
    assert m, "MapId union not found"
    have = set(re.findall(r'"([a-z0-9_]+)"', m.group(1)))
    new_ids = [i for i in meta["mapIds"] if i not in have]
    if new_ids:
        add = "".join(f' | "{i}"' for i in new_ids)
        TYPES_TS.write_text(types_text.replace(m.group(0), f"export type MapId = {m.group(1)}{add};"))

    data_text = DATA_TS.read_text()
    missing = [i for i in meta["mapIds"] if not re.search(rf"raw\.{re.escape(i)}\b", data_text)]
    if missing:
        consts = "\n".join(f"export const {i.upper()} = normalize(raw.{i});" for i in missing)
        at = data_text.index("export const MAPS = {")
        data_text = data_text[:at] + consts + "\n\n" + data_text[at:]
        close = data_text.index("} as const;", data_text.index("export const MAPS = {"))
        data_text = data_text[:close] + "".join(f"  {i}: {i.upper()},\n" for i in missing) + data_text[close:]
        DATA_TS.write_text(data_text)
    print(f"leg3: {len(sites)} buildings, maps {sorted(leg3_maps)}")


if __name__ == "__main__":
    main()
