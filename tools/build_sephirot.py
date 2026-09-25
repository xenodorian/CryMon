#!/usr/bin/env python3
"""Sephirot/Tree-of-Life map cluster builder.

Generates blank city + route maps for the CryTown-north expansion, one
topological step at a time (`--step N`), so every commit leaves
check_sync --strict passing (both endpoints of any warp added in a step
already exist). See CURRENT_WORK.md "Tree of Life expansion" for the
design writeup. Re-running an earlier step number is a no-op past what
is already applied (idempotent: only appends ids/warps not already
present; city/corridor row content is written fresh every time it's
touched but content is deterministic so this is safe).
"""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAPS_JSON = ROOT / "content/maps.json"
MAP_META = ROOT / "content/world_parts/map_meta.json"
WARPS_JSON = ROOT / "content/world_parts/warps.json"
SAVE_JSON = ROOT / "content/save.json"
TYPES_TS = ROOT / "src/game/types.ts"
DATA_TS = ROOT / "src/game/data.ts"
LAYOUT_JSON = ROOT / "content/world_map_layout.json"

SEPHIROT = {
    "keter": {"coord": (0, 0), "name": "KETER"},
    "chokmah": {"coord": (2, 1), "name": "CHOKMAH"},
    "binah": {"coord": (-2, 1), "name": "BINAH"},
    "chesed": {"coord": (2, 2), "name": "CHESED"},
    "gevurah": {"coord": (-2, 2), "name": "GEVURAH"},
    "tiferet": {"coord": (0, 3), "name": "TIFERET"},
    "netzach": {"coord": (2, 4), "name": "NETZACH"},
    "hod": {"coord": (-2, 4), "name": "HOD"},
    "yesod": {"coord": (0, 5), "name": "YESOD"},
    "malkuth": {"coord": (0, 6), "name": "MALKUTH"},
}

# (number, id/letter-name, from, to)
PATHS = [
    (11, "aleph", "keter", "chokmah"),
    (12, "beth", "keter", "binah"),
    (13, "gimel", "keter", "tiferet"),
    (14, "daleth", "chokmah", "binah"),
    (15, "he", "chokmah", "tiferet"),
    (16, "vau", "chokmah", "chesed"),
    (17, "zayin", "binah", "tiferet"),
    (18, "heth", "binah", "gevurah"),
    (19, "teth", "chesed", "gevurah"),
    (20, "yod", "chesed", "tiferet"),
    (21, "kaph", "chesed", "netzach"),
    (22, "lamed", "gevurah", "tiferet"),
    (23, "mem", "gevurah", "hod"),
    (24, "nun", "tiferet", "netzach"),
    (25, "samekh", "tiferet", "yesod"),
    (26, "ayin", "tiferet", "hod"),
    (27, "peh", "netzach", "hod"),
    (28, "tzaddi", "netzach", "yesod"),
    (29, "qoph", "netzach", "malkuth"),
    (30, "resh", "hod", "yesod"),
    (31, "shin", "hod", "malkuth"),
    (32, "tau", "yesod", "malkuth"),
]
PATH_BY_ID = {p[1]: p for p in PATHS}

# Extra non-Sephirot connector: CryTown's new north road into the cluster.
WEEPING_ROAD = ("weepingroad", "veld", "malkuth")

# Topological build order: (city_to_introduce_or_None, [path_ids_now_ready])
STEPS = [
    ("malkuth", []),                    # 1: + weeping_road (handled specially)
    ("yesod", ["tau"]),                 # 2
    ("netzach", ["qoph"]),              # 3
    ("hod", ["shin"]),                  # 4
    (None, ["peh"]),                    # 5
    (None, ["resh"]),                   # 6
    (None, ["tzaddi"]),                 # 7
    ("tiferet", ["samekh"]),            # 8
    (None, ["nun"]),                    # 9
    (None, ["ayin"]),                   # 10
    ("chesed", ["kaph"]),               # 11
    (None, ["yod"]),                    # 12
    ("gevurah", ["mem"]),               # 13
    (None, ["lamed"]),                  # 14
    (None, ["teth"]),                   # 15
    ("binah", ["zayin"]),               # 16
    (None, ["heth"]),                   # 17
    ("chokmah", ["he"]),                # 18
    (None, ["vau"]),                    # 19
    (None, ["daleth"]),                 # 20
    ("keter", ["gimel"]),               # 21
    (None, ["aleph"]),                  # 22
    (None, ["beth"]),                   # 23
]

SOLID = set("#HWRBC^NErUSX%k")
CITY_POOL = ["D", "O", "G", "Z", "P", "Q", "L", "J", "I", "V", "A", "M", "Y"]
assert not (set(CITY_POOL) & SOLID)

OPP = {"up": "down", "down": "up", "left": "right", "right": "left"}
STEP = {"right": (1, 0), "left": (-1, 0), "down": (0, 1), "up": (0, -1)}

# County-map geometry (the Sorrow County sheet). One tile = 8 of those
# pixels, so a path's playable grid is a scale model of its band,
# including the stairstep diagonals. Band thickness is the sheet's
# half-width rule: straight-line length / 8 pixels.
COUNTY_PX = 8
COUNTY_FRAC = {
    "keter": (0.50, 0.145),
    "binah": (0.22, 0.275),
    "chokmah": (0.78, 0.275),
    "gevurah": (0.175, 0.455),
    "tiferet": (0.50, 0.455),
    "chesed": (0.825, 0.455),
    "hod": (0.22, 0.635),
    "netzach": (0.78, 0.635),
    "yesod": (0.50, 0.695),
    "malkuth": (0.50, 0.835),
}
COUNTY_TREE = (30, 36, 780, 860)  # x, y, w, h


def county_node(city_id):
    fx, fy = COUNTY_FRAC[city_id]
    x, y, w, h = COUNTY_TREE
    return (x + fx * w, y + fy * h)


def county_bands(x1, y1, x2, y2):
    """Pixel rects of one county-map path band. Same rule as the sheet:
    axis-aligned when the run is within 0.28 of an axis, otherwise the
    blocky stairstep (this engine has no diagonal step)."""
    import math
    dist = math.hypot(x2 - x1, y2 - y1)
    thick = dist / 8.0
    dx, dy = x2 - x1, y2 - y1
    rects = []
    if abs(dy) < abs(dx) * 0.28:
        rects.append((min(x1, x2), (y1 + y2) / 2 - thick / 2, abs(dx), thick))
    elif abs(dx) < abs(dy) * 0.28:
        rects.append(((x1 + x2) / 2 - thick / 2, min(y1, y2), thick, abs(dy)))
    else:
        n = max(4, int(max(abs(dx), abs(dy)) / 28))
        pts = [(x1, y1)]
        x, y = x1, y1
        sx, sy = dx / n, dy / n
        for _ in range(n):
            x += sx
            pts.append((x, y))
            y += sy
            pts.append((x, y))
        for (ax, ay), (bx, by) in zip(pts, pts[1:]):
            if abs(bx - ax) >= abs(by - ay):
                if abs(bx - ax) < 0.5:
                    continue
                rects.append((min(ax, bx), ay - thick / 2, abs(bx - ax), thick))
            else:
                if abs(by - ay) < 0.5:
                    continue
                rects.append((ax - thick / 2, min(ay, by), thick, abs(by - ay)))
    return rects


def tiles_covered(rects):
    import math
    minx = min(r[0] for r in rects)
    miny = min(r[1] for r in rects)
    maxx = max(r[0] + r[2] for r in rects)
    maxy = max(r[1] + r[3] for r in rects)
    t0x, t0y = math.floor(minx / COUNTY_PX) - 1, math.floor(miny / COUNTY_PX) - 1
    t1x, t1y = math.floor(maxx / COUNTY_PX) + 1, math.floor(maxy / COUNTY_PX) + 1
    walk = set()
    for ty in range(t0y, t1y + 1):
        for tx in range(t0x, t1x + 1):
            x0, y0 = tx * COUNTY_PX, ty * COUNTY_PX
            x1, y1 = x0 + COUNTY_PX, y0 + COUNTY_PX
            area = 0.0
            for rx, ry, rw, rh in rects:
                ix0, iy0 = max(x0, rx), max(y0, ry)
                ix1, iy1 = min(x1, rx + rw), min(y1, ry + rh)
                if ix1 > ix0 and iy1 > iy0:
                    area += (ix1 - ix0) * (iy1 - iy0)
            if area >= 0.35 * COUNTY_PX * COUNTY_PX:
                walk.add((tx, ty))
    return walk


def grid_from_walk(walk, a_px, b_px, dir_out):
    """Wall-bounded corridor. '1' is the end nearest city A, '2' nearest B.
    The tile one step dir_out from '1' (and one step back from '2') is
    floor, so the existing warp offsets still land inside the path."""
    xs = [p[0] for p in walk]
    ys = [p[1] for p in walk]
    minx, maxx, miny, maxy = min(xs), max(xs), min(ys), max(ys)

    def loc(tx, ty):
        return (tx - minx + 1, ty - miny + 1)

    width, height = maxx - minx + 3, maxy - miny + 3
    grid = [["#" for _ in range(width)] for _ in range(height)]
    for tx, ty in walk:
        x, y = loc(tx, ty)
        grid[y][x] = "."

    def closest(px, py):
        best, bd = None, 1e18
        for tx, ty in walk:
            cx, cy = (tx + 0.5) * COUNTY_PX, (ty + 0.5) * COUNTY_PX
            d = (cx - px) ** 2 + (cy - py) ** 2
            if d < bd:
                bd, best = d, loc(tx, ty)
        return best

    a = closest(*a_px)
    b = closest(*b_px)
    if a == b:
        raise SystemExit("path ends collapsed onto one tile")
    ax, ay = STEP[dir_out]
    bx, by = STEP[OPP[dir_out]]
    for x, y in ((a[0] + ax, a[1] + ay), (b[0] + bx, b[1] + by)):
        if not (0 <= x < width and 0 <= y < height):
            raise SystemExit(f"arrival step off the map at {x},{y}")
        if grid[y][x] == "#":
            grid[y][x] = "."
    grid[a[1]][a[0]] = "1"
    grid[b[1]][b[0]] = "2"
    return ["".join(r) for r in grid]


def build_scaled_path(city_a, city_b, dir_out):
    x1, y1 = county_node(city_a)
    x2, y2 = county_node(city_b)
    return grid_from_walk(tiles_covered(county_bands(x1, y1, x2, y2)), (x1, y1), (x2, y2), dir_out)


def build_weeping_rows():
    """The sheet's Weeping Road: a vertical band from just under Malkuth
    down to CryTown's north edge. '1' is the CryTown end, '2' is Malkuth."""
    mx, my = county_node("malkuth")
    city_h = 12 * 6.5
    road_w = 6 * 6.5 * 0.5
    road_top = my + city_h / 2 - 8
    # Extended to meet CryTown, same as the county sheet.
    road_h = 172.0
    rects = [(mx - road_w / 2, road_top, road_w, road_h)]
    south = (mx, road_top + road_h)
    north = (mx, road_top)
    # Arrival on '1' steps up; arrival on '2' steps down.
    return grid_from_walk(tiles_covered(rects), south, north, "up")


def direction(a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    if abs(dy) >= abs(dx):
        return "down" if dy > 0 else "up"
    return "right" if dx > 0 else "left"


def edges_for_city(city_id):
    """All (other_city, dir_out_from_city, path_id) touching city_id, sorted."""
    out = []
    for pid, pname, a, b in PATHS:
        if a == city_id:
            out.append((b, direction(SEPHIROT[a]["coord"], SEPHIROT[b]["coord"]), pname))
        elif b == city_id:
            d = direction(SEPHIROT[a]["coord"], SEPHIROT[b]["coord"])
            out.append((a, OPP[d], pname))
    if city_id == "malkuth":
        out.append(("__weeping_road__", "down", "weeping_road"))
    out.sort(key=lambda t: t[2])
    return out


WALL_FOR_DIR = {"up": "north", "down": "south", "left": "west", "right": "east"}

CITY_W, CITY_H = 16, 12


def build_city_rows(city_id):
    edges = edges_for_city(city_id)
    marks = {}  # path_name -> (wall, mark_char)
    pool_i = 0
    by_wall = {"north": [], "south": [], "east": [], "west": []}
    for other, dir_out, pname in edges:
        wall = WALL_FOR_DIR[dir_out]
        ch = CITY_POOL[pool_i]
        pool_i += 1
        marks[pname] = (wall, ch)
        by_wall[wall].append((pname, ch))

    grid = [["." for _ in range(CITY_W)] for _ in range(CITY_H)]
    for x in range(CITY_W):
        grid[0][x] = "#"
        grid[CITY_H - 1][x] = "#"
    for y in range(CITY_H):
        grid[y][0] = "#"
        grid[y][CITY_W - 1] = "#"

    def spaced(n, span):
        return [round((i + 1) * (span - 1) / (n + 1)) for i in range(n)]

    for pname, ch in by_wall["north"]:
        pass
    for wall in ("north", "south"):
        items = by_wall[wall]
        cols = spaced(len(items), CITY_W - 2)
        row = 0 if wall == "north" else CITY_H - 1
        for (pname, ch), c in zip(items, cols):
            grid[row][1 + c] = ch
    for wall in ("east", "west"):
        items = by_wall[wall]
        rows_ = spaced(len(items), CITY_H - 2)
        col = 0 if wall == "west" else CITY_W - 1
        for (pname, ch), r in zip(items, rows_):
            grid[1 + r][col] = ch

    return ["".join(r) for r in grid], marks


def build_corridor_rows(dir_out):
    """Unused straight hall. Paths are now build_scaled_path() scale models
    of the county sheet. Kept so the old shape is still visible."""
    if dir_out in ("up", "down"):
        w, h = 6, 24
        grid = [["." for _ in range(w)] for _ in range(h)]
        for x in range(w):
            grid[0][x] = "#"
            grid[h - 1][x] = "#"
        for y in range(h):
            grid[y][0] = "#"
            grid[y][w - 1] = "#"
        mid = w // 2
        # A end is the "start" of dir_out travel: up => A is south (bottom row); down => A is north (top row)
        if dir_out == "down":
            grid[0][mid] = "1"
            grid[h - 1][mid] = "2"
        else:
            grid[h - 1][mid] = "1"
            grid[0][mid] = "2"
    else:
        w, h = 24, 6
        grid = [["." for _ in range(w)] for _ in range(h)]
        for x in range(w):
            grid[0][x] = "#"
            grid[h - 1][x] = "#"
        for y in range(h):
            grid[y][0] = "#"
            grid[y][w - 1] = "#"
        mid = h // 2
        if dir_out == "right":
            grid[mid][0] = "1"
            grid[mid][w - 1] = "2"
        else:
            grid[mid][w - 1] = "1"
            grid[mid][0] = "2"
    return ["".join(r) for r in grid]


def offsets(dir_out):
    off_key = "oy" if dir_out in ("up", "down") else "ox"
    off_out = -32 if dir_out in ("up", "left") else 40
    off_in = 40 if dir_out in ("up", "left") else -32
    return off_key, off_out, off_in


def warp_pair(map_a, tile_a, map_b, tile_b, dir_out):
    off_key, off_out, off_in = offsets(dir_out)
    return [
        {"from": map_a, "tile": tile_a, "to": map_b, "spawn": tile_b, "dir": dir_out, off_key: off_out},
        {"from": map_b, "tile": tile_b, "to": map_a, "spawn": tile_a, "dir": OPP[dir_out], off_key: off_in},
    ]


def load(p):
    return json.loads(p.read_text())


def save(p, data):
    p.write_text(json.dumps(data, indent=2) + "\n")


def city_marks_cache():
    cache = {}
    for cid in SEPHIROT:
        rows, marks = build_city_rows(cid)
        cache[cid] = (rows, marks)
    return cache


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--step", type=int, help="1..23")
    ap.add_argument("--paths-only", action="store_true",
                    help="rewrite the 22 path maps and the Weeping Road as scale models of the county sheet; do not touch cities or warps")
    args = ap.parse_args()
    if args.paths_only:
        maps_data = load(MAPS_JSON)
        rows = maps_data["rows"]
        for _n, pname, a, b in PATHS:
            dir_out = direction(SEPHIROT[a]["coord"], SEPHIROT[b]["coord"])
            rows[pname] = build_scaled_path(a, b, dir_out)
        rows["weepingroad"] = build_weeping_rows()
        save(MAPS_JSON, maps_data)
        print("rewrote 22 path maps + weepingroad from the county sheet")
        return
    if args.step is None:
        raise SystemExit("pass --step N or --paths-only")
    assert 1 <= args.step <= len(STEPS)

    maps_data = load(MAPS_JSON)
    meta = load(MAP_META)
    warps_data = load(WARPS_JSON)
    save_data = load(SAVE_JSON)
    types_text = TYPES_TS.read_text()
    data_text = DATA_TS.read_text()

    rows = maps_data["rows"]
    mapIds = meta["mapIds"]
    mapNames = meta["mapNames"]
    warps = warps_data["warps"]
    mapOrder = save_data["mapOrder"]

    city_cache = city_marks_cache()

    def ensure_map_registered(map_id, label):
        if map_id not in mapIds:
            mapIds.append(map_id)
            mapOrder.append(map_id)
        mapNames[map_id] = label

    def ensure_city(cid):
        map_rows, _marks = city_cache[cid]
        rows[cid] = map_rows
        ensure_map_registered(cid, SEPHIROT[cid]["name"])

    def ensure_corridor(pname, a, b, dir_out):
        rows[pname] = build_scaled_path(a, b, dir_out)
        ensure_map_registered(pname, "PATH OF " + pname.upper())

    def add_warp_pair_if_new(pair):
        for w in pair:
            exists = any(
                e["from"] == w["from"] and e["to"] == w["to"] and e["tile"] == w["tile"]
                for e in warps
            )
            if not exists:
                warps.append(w)

    active_cities = set()
    active_paths = set()
    weeping_active = False

    for i in range(args.step):
        city, path_ids = STEPS[i]
        if city:
            active_cities.add(city)
        for pid in path_ids:
            active_paths.add(pid)
        if i == 0:
            weeping_active = True

    # Materialize all active cities (full geometry, all eventual exits).
    for cid in active_cities:
        ensure_city(cid)

    # Materialize active corridors + their warp pairs (both endpoints must
    # be active cities by construction of STEPS).
    for pname in active_paths:
        pid, _pname, a, b = PATH_BY_ID[pname]
        assert a in active_cities and b in active_cities, f"{pname}: endpoints not active"
        dir_out = direction(SEPHIROT[a]["coord"], SEPHIROT[b]["coord"])
        ensure_corridor(pname, a, b, dir_out)
        _, marks_a = city_cache[a]
        _, marks_b = city_cache[b]
        tile_a = marks_a[pname][1]
        tile_b = marks_b[pname][1]
        pair1 = warp_pair(a, tile_a, pname, "1", dir_out)
        pair2 = warp_pair(pname, "2", b, tile_b, dir_out)
        add_warp_pair_if_new(pair1)
        add_warp_pair_if_new(pair2)

    if weeping_active:
        rname, va, vb = WEEPING_ROAD
        # veld already exists; malkuth must be active by step 1.
        assert vb in active_cities
        rows[rname] = build_weeping_rows()
        ensure_map_registered(rname, "THE WEEPING ROAD")
        _, marks_malkuth = city_cache["malkuth"]
        tile_malkuth = marks_malkuth["weeping_road"][1]
        # veld's own new north-exit mark: 'O' (unused in veld's existing rows).
        veld_rows = rows["veld"]
        if veld_rows[0][14] != "O":
            r0 = list(veld_rows[0])
            r0[14] = "O"
            veld_rows[0] = "".join(r0)
            rows["veld"] = veld_rows
        pair1 = warp_pair("veld", "O", rname, "1", "up")
        pair2 = warp_pair(rname, "2", "malkuth", tile_malkuth, "up")
        add_warp_pair_if_new(pair1)
        add_warp_pair_if_new(pair2)

    save(MAPS_JSON, maps_data)
    save(MAP_META, meta)
    save(WARPS_JSON, warps_data)
    save(SAVE_JSON, save_data)

    # types.ts MapId union: append any new ids not already present.
    import re
    m = re.search(r'(export type MapId =\n?(?:[^\n]*\n)*?[^;]*;)', types_text)
    # Simpler: locate the union line (single-line union in this file).
    m2 = re.search(r'export type MapId = ([^\n]+);', types_text)
    assert m2, "MapId union not found"
    current = m2.group(1)
    existing_ids = set(re.findall(r'"([a-z0-9_]+)"', current))
    new_ids = [i for i in mapIds if i not in existing_ids]
    if new_ids:
        addition = "".join(f' | "{i}"' for i in new_ids)
        types_text = types_text.replace(m2.group(0), f'export type MapId = {current}{addition};')
        TYPES_TS.write_text(types_text)

    # data.ts: const declarations + MAPS object entries for new ids.
    new_for_data = [i for i in mapIds if not re.search(rf"raw\.{re.escape(i)}\b", data_text)]
    if new_for_data:
        const_lines = "\n".join(f"export const {i.upper()} = normalize(raw.{i});" for i in new_for_data)
        marker = "export const MAPS = {"
        idx = data_text.index(marker)
        data_text = data_text[:idx] + const_lines + "\n\n" + data_text[idx:]
        # insert MAPS entries just before the closing "} as const;" of MAPS
        maps_close = data_text.index("} as const;", data_text.index("export const MAPS = {"))
        entries = "".join(f"  {i}: {i.upper()},\n" for i in new_for_data)
        data_text = data_text[:maps_close] + entries + data_text[maps_close:]
        DATA_TS.write_text(data_text)

    print(f"step {args.step}/{len(STEPS)} applied: cities={sorted(active_cities)} paths={sorted(active_paths)} weeping_road={weeping_active}")
    print(f"new map ids this run: {new_for_data if new_for_data else '(none)'}")


if __name__ == "__main__":
    main()
