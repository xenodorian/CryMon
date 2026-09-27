#!/usr/bin/env python3
"""The Hollow: a post-game wild area west of the Reach.

    python3 tools/build_hollow.py
    python3 tools/merge_world.py
    python3 tools/build_map_screen.py

Opens after the war (`leg3Ended`). Wild monsters are Lv 45-55 so the
Calder rematch (Lv 52-55) has somewhere to train. Rare species are the
same ids listed once in a pool where the common ones are listed three
times (both engines pick uniformly from the pool).

This script owns the map layout and its wiring: maps.json rows, the
Reach's west-edge exit '<', map_meta, save mapOrder, types.ts / data.ts,
warps, the encounter row, the battle background and the map song. The
NPCs, trainer kits, dialogue and flags that use the marks are authored
JSON. Safe to run again.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAPS_JSON = ROOT / "content/maps.json"
MAP_META = ROOT / "content/world_parts/map_meta.json"
WARPS_JSON = ROOT / "content/world_parts/warps.json"
ENC_JSON = ROOT / "content/world_parts/encounters.json"
SAVE_JSON = ROOT / "content/save.json"
SPRITES_JSON = ROOT / "content/sprites.json"
AUDIO_JSON = ROOT / "content/audio.json"
TYPES_TS = ROOT / "src/game/types.ts"
DATA_TS = ROOT / "src/game/data.ts"

MAP_ID = "hollow"
LABEL = "THE HOLLOW"
# Marks: i keeper (lore), f / d / j trainers. > is the exit east to the Reach
# (grass art, like the other edge exits; D would draw a door in the trees).
ROWS = [
    "##########################",
    "#####....TTTT....#########",
    "####..TTTTTTTT..f.########",
    "###..TTTT##TTTT....#######",
    "##..TTT####..TTT....######",
    "##..TT##WWW#...TT....#####",
    "#...TT#WWWW##..TTT....####",
    "#..TTT#WWW##..TTTTT....###",
    "#..TTT##W##..TT##TTT.....#",
    "#...TTT....TTT####TT..i..>",
    "#....TTTTTTTT####..TT....#",
    "##....TTTT..###...TTT....#",
    "###..d...........TTTT...##",
    "####....TTTTTTT....TT..###",
    "#####..TTTTTTTTT..j...####",
    "######...TTTTT......######",
    "########..........########",
    "##########################",
]
# Reach row 8, west edge.
REACH_EXIT = (0, 8)
EXIT_CH = "<"
BACK_CH = ">"

COMMON = ["gloomspider", "gallowcrow", "cryptlamp", "frostchoir", "pyrelion"]
RARE = ["eclipsaur", "starwhale", "deathknell"]
ENCOUNTER = {
    "maps": [MAP_ID], "tile": "T", "rate": 0.2,
    "pool": [s for s in COMMON for _ in range(3)] + RARE,
    "levelMin": 45, "levelMax": 55,
}
WILD_LEVEL_CAP = 60


def load(p: Path):
    return json.loads(p.read_text())


def save(p: Path, data) -> None:
    p.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def main() -> None:
    maps = load(MAPS_JSON)
    maps["rows"][MAP_ID] = list(ROWS)
    maps["tileArt"][EXIT_CH] = "tile-grass"
    maps["tileArt"][BACK_CH] = "tile-grass"
    reach = [list(r) for r in maps["rows"]["reach"]]
    x, y = REACH_EXIT
    reach[y][x] = EXIT_CH
    maps["rows"]["reach"] = ["".join(r) for r in reach]
    save(MAPS_JSON, maps)

    meta = load(MAP_META)
    if MAP_ID not in meta["mapIds"]:
        meta["mapIds"].append(MAP_ID)
    meta["mapNames"][MAP_ID] = LABEL
    save(MAP_META, meta)

    sv = load(SAVE_JSON)
    if MAP_ID not in sv["mapOrder"]:
        sv["mapOrder"].append(MAP_ID)
    save(SAVE_JSON, sv)

    wd = load(WARPS_JSON)
    warps = [w for w in wd["warps"] if MAP_ID not in (w["from"], w["to"])]
    warps.append({"from": "reach", "tile": EXIT_CH, "to": MAP_ID, "spawn": BACK_CH, "dir": "left",
                  "ox": -32, "need": "leg3Ended", "failTalk": "hollowLocked"})
    warps.append({"from": MAP_ID, "tile": BACK_CH, "to": "reach", "spawn": EXIT_CH, "dir": "right", "ox": 40})
    wd["warps"] = warps
    save(WARPS_JSON, wd)

    ed = load(ENC_JSON)
    ed["encounters"] = [e for e in ed["encounters"] if MAP_ID not in e["maps"]] + [ENCOUNTER]
    save(ENC_JSON, ed)

    world_meta = ROOT / "content/world_parts/meta.json"
    wm = load(world_meta)
    wm["formulas"]["wildLevelCap"] = WILD_LEVEL_CAP
    save(world_meta, wm)

    sp = load(SPRITES_JSON)
    sp["battleBgMap"][MAP_ID] = "bg-forest"
    save(SPRITES_JSON, sp)
    au = load(AUDIO_JSON)
    au["mapSongs"][MAP_ID] = "wilds"
    save(AUDIO_JSON, au)

    types_text = TYPES_TS.read_text()
    mm = re.search(r"export type MapId = ([^\n]+);", types_text)
    if f'"{MAP_ID}"' not in mm.group(1):
        TYPES_TS.write_text(types_text.replace(mm.group(0), f'export type MapId = {mm.group(1)} | "{MAP_ID}";'))
    data_text = DATA_TS.read_text()
    if not re.search(rf"raw\.{MAP_ID}\b", data_text):
        at = data_text.index("export const MAPS = {")
        data_text = data_text[:at] + f"export const {MAP_ID.upper()} = normalize(raw.{MAP_ID});\n\n" + data_text[at:]
        close = data_text.index("} as const;", data_text.index("export const MAPS = {"))
        data_text = data_text[:close] + f"  {MAP_ID}: {MAP_ID.upper()},\n" + data_text[close:]
        DATA_TS.write_text(data_text)
    print(f"hollow: {len(ROWS[0])}x{len(ROWS)}, pool {len(ENCOUNTER['pool'])}")


if __name__ == "__main__":
    main()
