#!/usr/bin/env python3
"""Load every map on the real Dreamcast build (Flycast) from a save.

For each map in content/save.json mapOrder, patch a base save (map id and
a walkable tile near the map's middle, checksum redone), put it in the
VMU, boot, pick Continue, walk a few steps, and screenshot. A map fails
if Flycast dies or the screen is black. Writes <out>/<map>.png, the save
blobs (<out>/blobs/<map>.bin, reused by scripts/e2e-map-tour.mjs for the
web side) and <out>/sheet-N.png contact sheets for a quick look.

  map_tour.py --cdi <cdi> --flycast <AppRun> --base e2e-out/quartz-before.bin \
              [--out tour-out] [--blobs-only] [map ...]
"""
import argparse
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(HERE))

SAVE = json.loads((REPO / "content" / "save.json").read_text())
MAPS = json.loads((REPO / "content" / "maps.json").read_text())
WORLD = json.loads((REPO / "content" / "world.json").read_text())
TILE = 32


def stand_tile(rows, warps=""):
    """Walkable tile nearest the middle, two tiles clear of any door or
    warp tile (the walk-around step must not change maps)."""
    solid, doors = set(MAPS["solid"]), set(MAPS["doors"]) | set(warps)
    h, w = len(rows), max(len(r) for r in rows)

    def at(c, r):
        return rows[r][c] if 0 <= r < h and 0 <= c < len(rows[r]) else "#"

    def ok(c, r):
        ch = at(c, r)
        return ch not in solid and ch not in doors

    def clear(c, r):
        return all(at(c + dc, r + dr) not in doors for dc in range(-2, 3) for dr in range(-2, 3))

    best = None
    for r in range(h):
        for c in range(len(rows[r])):
            if not ok(c, r):
                continue
            score = ((c - w / 2) ** 2 + (r - h / 2) ** 2
                     + (0 if clear(c, r) else 10000)
                     + 100 * sum(not ok(c + dc, r + dr) for dc, dr in ((1, 0), (-1, 0), (0, 1), (0, -1))))
            if best is None or score < best[0]:
                best = (score, c, r)
    return (best[1], best[2]) if best else (1, 1)


def patch(base, map_name):
    b = bytearray(base)
    rows = MAPS["rows"][map_name]
    warps = "".join(wp["tile"] for wp in WORLD.get("warps", []) if wp.get("from") == map_name)
    c, r = stand_tile(rows, warps)
    b[SAVE["layout"]["mapId"][0]] = SAVE["mapOrder"].index(map_name)
    x, y = c * TILE + TILE // 2, r * TILE + TILE // 2
    b[8], b[9], b[10], b[11] = x & 0xFF, x >> 8, y & 0xFF, y >> 8
    s = sum(b[:142]) & 0xFFFF
    b[142], b[143] = s & 0xFF, s >> 8
    return bytes(b), (c, r)


def sheets(out, names):
    from PIL import Image, ImageDraw
    per = 12
    for k in range(0, len(names), per):
        chunk = names[k:k + per]
        sheet = Image.new("RGB", (4 * 320, 3 * 250), "black")
        for i, n in enumerate(chunk):
            p = out / f"{n}.png"
            if not p.exists():
                continue
            im = Image.open(p).convert("RGB").resize((320, 240))
            x, y = (i % 4) * 320, (i // 4) * 250
            sheet.paste(im, (x, y + 10))
            ImageDraw.Draw(sheet).text((x + 2, y), n, fill="yellow")
        sheet.save(out / f"sheet-{k // per + 1}.png")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cdi")
    ap.add_argument("--flycast")
    ap.add_argument("--base", required=True, help="a 332-byte save from the web e2e")
    ap.add_argument("--out", default="tour-out")
    ap.add_argument("--blobs-only", action="store_true", help="just write the per-map saves")
    ap.add_argument("maps", nargs="*")
    args = ap.parse_args()
    out = Path(args.out)
    (out / "blobs").mkdir(parents=True, exist_ok=True)
    base = Path(args.base).read_bytes()
    names = args.maps or SAVE["mapOrder"]
    for n in names:
        blob, _ = patch(base, n)
        (out / "blobs" / f"{n}.bin").write_bytes(blob)
    if args.blobs_only:
        return

    import vmu_tool
    from emu_warden import Emu

    fails = []
    emu = Emu(args.flycast, args.cdi, out)
    try:
        emu.start()
        emu.stop()
        emu.vmu = sorted(emu.data.glob("*vmu_save_A1.bin"))[0]
        fresh = emu.vmu.read_bytes()
        for n in names:
            img = bytearray(fresh)
            vmu_tool.inject(img, (out / "blobs" / f"{n}.bin").read_bytes())
            emu.vmu.write_bytes(img)
            emu.start()
            emu.key("x", after=2.5)  # Continue
            for k in ("Left", "Right", "Up", "Down"):
                emu.key(k, ms=250, after=0.1)
            time.sleep(0.5)
            alive = emu.proc.poll() is None
            im = emu.shot(f"{n}.png") if alive else None
            lit = im is not None and sum(im.convert("L").histogram()[16:]) > (640 * 480) // 20
            emu.stop()
            ok = alive and lit
            print(("PASS  " if ok else "FAIL  ") + f"{n}" + ("" if alive else " (Flycast died)")
                  + ("" if lit or not alive else " (black screen)"), flush=True)
            if not ok:
                fails.append(n)
    finally:
        emu.stop()
    sheets(out, names)
    print(f"{len(names) - len(fails)}/{len(names)} maps load on Dreamcast; screenshots in {out}")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
