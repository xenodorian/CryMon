#!/usr/bin/env python3
"""Write the pause-menu Map screen into content/logic.json (`mapScreen`).

    python3 tools/build_map_screen.py

Two pages drawn the same way on both engines (web doubles every number):
Sorrow County and the Sephirot. Nodes are dots with a label under them,
links are lines between nodes. Positions are in a 280 x 152 box (the
Dreamcast menu panel, below its title row). A Dreamcast letter is 11 px
wide, so labels on one row need that much room. Sephirot paths are links, and
their endpoints come from warps.json, so they never drift from the world.

Every map id is assigned to one node or one link ("You are here"): the
ids listed below first, then any other map (an interior, a base) takes
whatever the nearest listed map through warps has. Safe to run again.
"""
from __future__ import annotations

import json
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOGIC = ROOT / "content/logic.json"
WARPS = ROOT / "content/world_parts/warps.json"
META = ROOT / "content/world_parts/map_meta.json"

PAGES = [
    {"id": "county", "title": "SORROW COUNTY"},
    {"id": "sephirot", "title": "THE SEPHIROT"},
]

# id, page, x, y, label, gem (a city or a key place), map ids
COUNTY = [
    ("toMalkuth", 0, 140, 0, "MALKUTH", False, []),
    ("weepingroad", 0, 140, 24, "WEEPING ROAD", False, ["weepingroad"]),
    ("reach", 0, 34, 24, "REACH", True, ["reach"]),
    ("hollow", 0, 34, 0, "HOLLOW", False, ["hollow"]),
    ("ruins", 0, 60, 50, "RUINS", False, ["ruins"]),
    ("veld", 0, 140, 50, "CRYTOWN", True, ["veld", "house"]),
    ("cliffs", 0, 222, 50, "CLIFFS", False, ["cliffs"]),
    ("marsh", 0, 240, 76, "MARSH", False, ["marsh"]),
    ("quarry", 0, 240, 102, "QUARRY", False, ["quarry"]),
    ("camp", 0, 240, 128, "CAMP", True, ["camp"]),
    ("forest", 0, 165, 128, "FOREST", False, ["forest"]),
    ("grove", 0, 165, 88, "PRISON", True, ["grove"]),
    ("gauntlet", 0, 75, 90, "GAUNTLET", False,
     ["gauntlet", "gauntlet1", "gauntlet2", "gauntlet3", "gauntlet4", "gauntlet5"]),
    ("shrine", 0, 70, 128, "HEAVENFALL", True, ["gauntlet6"]),
]
COUNTY_LINKS = [
    ("toMalkuth", "weepingroad"), ("weepingroad", "veld"), ("veld", "ruins"), ("ruins", "reach"), ("reach", "hollow"),
    ("veld", "cliffs"), ("cliffs", "marsh"), ("marsh", "quarry"), ("quarry", "camp"),
    ("camp", "forest"), ("forest", "grove"), ("veld", "gauntlet"), ("gauntlet", "shrine"),
]
SEPHIROT = [
    ("keter", 140, 0), ("binah", 40, 20), ("chokmah", 240, 20),
    ("gevurah", 40, 60), ("chesed", 240, 60), ("tiferet", 140, 68),
    ("hod", 40, 100), ("netzach", 240, 100), ("yesod", 140, 108), ("malkuth", 140, 136),
]


def main() -> None:
    logic = json.loads(LOGIC.read_text())
    warps = json.loads(WARPS.read_text())["warps"]
    meta = json.loads(META.read_text())
    names = meta["mapNames"]
    adj: dict[str, set[str]] = {}
    for w in warps:
        adj.setdefault(w["from"], set()).add(w["to"])
        adj.setdefault(w["to"], set()).add(w["from"])

    nodes = [{"id": i, "page": p, "x": x, "y": y, "label": lab, "gem": gem, "maps": list(ms)}
             for i, p, x, y, lab, gem, ms in COUNTY]
    cities = {c for c, _, _ in SEPHIROT}
    for c, x, y in SEPHIROT:
        nodes.append({"id": c, "page": 1, "x": x, "y": y, "label": names.get(c, c).upper(),
                      "gem": True, "maps": [c]})
    idx = {n["id"]: i for i, n in enumerate(nodes)}
    links = [{"a": idx[a], "b": idx[b], "label": "", "maps": []} for a, b in COUNTY_LINKS]
    # A Sephirot path is any map that warps to exactly two cities.
    for m in meta["mapIds"]:
        ends = sorted(adj.get(m, set()) & cities)
        if m not in cities and len(ends) == 2:
            links.append({"a": idx[ends[0]], "b": idx[ends[1]],
                          "label": names.get(m, m).upper(), "maps": [m]})

    # Nearest listed map (through warps) for everything else.
    owner: dict[str, tuple[str, int]] = {}
    for i, n in enumerate(nodes):
        for m in n["maps"]:
            owner[m] = ("node", i)
    for i, l in enumerate(links):
        for m in l["maps"]:
            owner[m] = ("link", i)
    for m in meta["mapIds"]:
        if m in owner:
            continue
        seen, q = {m}, deque([m])
        while q:
            cur = q.popleft()
            if cur in owner:
                kind, i = owner[cur]
                (nodes if kind == "node" else links)[i]["maps"].append(m)
                break
            for nxt in sorted(adj.get(cur, ())):
                if nxt not in seen:
                    seen.add(nxt)
                    q.append(nxt)
        else:
            print(f"map_screen: {m} is not reachable from any node")

    logic["mapScreen"] = {
        "note": "Pause-menu Map screen. See tools/build_map_screen.py for the rules.",
        "pages": PAGES, "nodes": nodes, "links": links,
    }
    LOGIC.write_text(json.dumps(logic, indent=2, ensure_ascii=False) + "\n")
    print(f"map screen: {len(nodes)} nodes, {len(links)} links")


if __name__ == "__main__":
    main()
