"""Overworld ground tiles, 32x32, drawn in code.

Writes public/sprites/tiles/*.png (through sprite_root.assert_write):
  grass-1..4, tallgrass-1..2, dirt-1..4, tree-1..2, tree-s-1..2, water-1..4,
  cliff-1..2, and edge overlays (transparent) dirtedge-n/e/s/w, shore-n/e/s/w.

Every base tile wraps seamlessly on all sides, so any mix of variants lines
up. Run:  python3 tools/pixelforge/tiles.py
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sprite_root import CANON, assert_write  # noqa: E402

T = 32


def hx(s):
    s = s.lstrip("#")
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))


def rng(seed):
    return np.random.default_rng(seed)


def pnoise(seed, cells=4, octaves=3):
    """Periodic value noise on a 32x32 torus, 0..1."""
    out = np.zeros((T, T))
    amp, tot = 1.0, 0.0
    r = rng(seed)
    for o in range(octaves):
        n = cells * (2 ** o)
        g = r.random((n, n))
        ys, xs = np.mgrid[0:T, 0:T] / T * n
        x0, y0 = np.floor(xs).astype(int), np.floor(ys).astype(int)
        fx, fy = xs - x0, ys - y0
        fx, fy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)
        x1, y1 = (x0 + 1) % n, (y0 + 1) % n
        x0, y0 = x0 % n, y0 % n
        v = (g[y0, x0] * (1 - fx) * (1 - fy) + g[y0, x1] * fx * (1 - fy) + g[y1, x0] * (1 - fx) * fy + g[y1, x1] * fx * fy)
        out += v * amp
        tot += amp
        amp *= 0.5
    return out / tot


BAYER = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0


def shade(v, pal):
    """Map 0..1 values to a palette with ordered dithering between steps."""
    n = len(pal)
    ys, xs = np.mgrid[0:T, 0:T]
    d = BAYER[ys % 4, xs % 4] - 0.5
    idx = np.clip(np.floor(v * (n - 1) + 0.5 + d * 0.7), 0, n - 1).astype(int)
    P = np.array([hx(c) if isinstance(c, str) else c for c in pal], dtype=np.uint8)
    img = np.zeros((T, T, 4), np.uint8)
    img[..., :3] = P[idx]
    img[..., 3] = 255
    return img


def put(img, x, y, col, a=255):
    x, y = int(x) % T, int(y) % T
    c = hx(col) if isinstance(col, str) else col
    img[y, x, :3] = c
    img[y, x, 3] = a


GRASS = ["#253a22", "#2e4629", "#375330", "#406137", "#4c6f3f", "#5a7f48"]
BLADE_D, BLADE_M, BLADE_L = "#2a4226", "#5a7f48", "#7a9c58"


def blades(img, r, n, hmin=2, hmax=4, cols=(BLADE_D, BLADE_M, BLADE_L)):
    for _ in range(n):
        x, y = r.integers(0, T), r.integers(0, T)
        h = r.integers(hmin, hmax + 1)
        lean = r.choice([-1, 0, 0, 1])
        for k in range(h):
            c = cols[0] if k == 0 else (cols[2] if k == h - 1 else cols[1])
            put(img, x + (lean if k >= h // 2 + 1 else 0), y - k, c)


def grass(seed, flowers=0):
    r = rng(seed)
    v = pnoise(seed, 4) * 0.8 + pnoise(seed + 50, 8, 1) * 0.2
    img = shade(v * 0.75 + 0.1, GRASS)
    blades(img, r, 46)
    for _ in range(flowers):
        x, y = r.integers(2, T - 2), r.integers(2, T - 2)
        c = r.choice(["#e8e0c8", "#e8c85a", "#c87a9a", "#9ab0e0"])
        for dx, dy in ((0, -1), (-1, 0), (1, 0), (0, 1)):
            put(img, x + dx, y + dy, c)
        put(img, x, y, "#e8b030")
        put(img, x, y + 2, BLADE_D)
    return img


def tallgrass(seed):
    r = rng(seed)
    v = pnoise(seed, 4)
    img = shade(v * 0.4, GRASS)
    # dense tall tufts in staggered rows so each one reads on its own
    for row in range(4):
        for col in range(4):
            bx = col * 8 + (4 if row % 2 else 0) + r.integers(-1, 2)
            by = row * 8 + 7 + r.integers(-1, 1)
            for k in range(5):
                x = bx + k - 2
                h = 6 - abs(k - 2) + r.integers(0, 2)
                lean = (k - 2) * 0.35
                for j in range(h):
                    c = "#1c2e1a" if j == 0 else ("#8aac5c" if j == h - 1 else ("#4c7a3c" if j < h - 2 else "#6a9448"))
                    put(img, x + lean * j, by - j, c)
    return img


DIRT = ["#4a3a28", "#56442e", "#645036", "#6f5a3c", "#7c6644", "#8a7450"]


def dirt(seed, dark=False):
    r = rng(seed)
    v = pnoise(seed, 3) * 0.7 + pnoise(seed + 9, 8, 1) * 0.3
    pal = DIRT if not dark else [tuple(int(c * 0.85) for c in hx(p)) for p in DIRT]
    img = shade(v * 0.7 + 0.12, pal)
    # pebbles: lit top-left, shadow bottom-right
    for _ in range(5):
        x, y = r.integers(0, T), r.integers(0, T)
        s = r.integers(1, 3)
        for dx in range(s + 1):
            for dy in range(s):
                put(img, x + dx, y + dy, "#8a7c68")
        put(img, x, y, "#b0a48c")
        for dx in range(s + 1):
            put(img, x + dx + 1, y + s, "#3a2c1e")
    # a few ruts and cracks
    for _ in range(2):
        x, y = r.integers(0, T), r.integers(0, T)
        for k in range(r.integers(3, 7)):
            put(img, x + k, y + (k // 3) * (1 if r.random() < 0.5 else -1), "#3e3020")
    for _ in range(3):
        x, y = r.integers(0, T), r.integers(0, T)
        put(img, x, y, "#9a8660")
    return img


LEAF = ["#0e1a10", "#16261a", "#1e3420", "#284428", "#335430", "#40663a", "#52784a"]


def canopy(seed, trunks=False):
    """Seamless forest canopy made of lit leaf clumps; trunks=True shows the
    edge of the wood, trunks and roots over grass in the lower third."""
    r = rng(seed)
    base = np.zeros((T, T))
    ys, xs = np.mgrid[0:T, 0:T]
    L = np.array([-0.6, -0.7])
    clumps = [(r.uniform(0, T), r.uniform(0, T), r.uniform(6, 10)) for _ in range(9)]
    height = np.full((T, T), -1.0)
    light = np.zeros((T, T))
    for cx, cy, rad in clumps:
        for ox in (-T, 0, T):
            for oy in (-T, 0, T):
                dx, dy = (xs - cx - ox) / rad, (ys - cy - oy) / rad
                d2 = dx * dx + dy * dy
                inside = d2 < 1
                h = np.sqrt(np.clip(1 - d2, 0, 1)) + cy / T * 0.4
                m = inside & (h > height)
                height[m] = h[m]
                nz = np.sqrt(np.clip(1 - d2, 0, 1))
                ndl = dx * L[0] + dy * L[1] + nz * 0.5
                light[m] = np.clip(0.35 + ndl[m] * 0.55, 0, 1)
    base = np.where(height < 0, 0.05, light)
    # leaf speckle
    base = base + (pnoise(seed + 3, 16, 1) - 0.5) * 0.25
    img = shade(np.clip(base, 0, 1), LEAF)
    if trunks:
        g = grass(seed + 100)
        cut = 21
        edge = cut + (np.sin(xs[0] / T * math.pi * 4 + seed) * 2).astype(int)
        for x in range(T):
            for y in range(edge[x], T):
                img[y, x] = g[y, x]
            # shadow the canopy casts on the grass
            for y in range(edge[x], min(T, edge[x] + 4)):
                img[y, x, :3] = (img[y, x, :3] * 0.6).astype(np.uint8)
            img[edge[x] - 1, x, :3] = hx("#0a140c")
        for tx_ in (6 + seed % 5, 22 - seed % 4):
            for y in range(edge[tx_] - 2, min(T, edge[tx_] + 6)):
                for dx in range(-1, 2):
                    c = "#3a2a1c" if dx < 0 else ("#5a4430" if dx == 0 else "#2a1e14")
                    put(img, tx_ + dx, y, c)
            put(img, tx_ - 2, min(T - 1, edge[tx_] + 5), "#2a1e14")
            put(img, tx_ + 2, min(T - 1, edge[tx_] + 5), "#2a1e14")
    return img


WATER = ["#1a2c3a", "#20384a", "#284658", "#325468", "#3e6478", "#56809a"]


def water(frame):
    v = pnoise(77, 2, 2) * 0.6 + 0.2
    img = shade(v * 0.7, WATER)
    ph = frame * math.pi / 2
    for band in range(4):
        y0 = band * 8 + 3
        for x in range(T):
            y = y0 + math.sin(x / T * math.pi * 2 * 2 + ph + band) * 1.5
            if (x + band * 5 + frame * 2) % 11 < 5:
                put(img, x, y, "#6a92aa")
                if (x + band * 3 + frame) % 11 == 2:
                    put(img, x, y - 1, "#a8c8d8")
    return img


ROCK = ["#2a2418", "#3a3224", "#4a4030", "#5a503c", "#6a604a", "#807458"]


def cliff(seed):
    """A rock face of wrapped Voronoi boulders, each lit from the top left."""
    r = rng(seed)
    ys, xs = np.mgrid[0:T, 0:T]
    pts = [(r.uniform(0, T), r.uniform(0, T)) for _ in range(7)]
    d1 = np.full((T, T), 1e9)
    d2 = np.full((T, T), 1e9)
    cx_ = np.zeros((T, T))
    cy_ = np.zeros((T, T))
    for px, py in pts:
        for ox in (-T, 0, T):
            for oy in (-T, 0, T):
                d = np.hypot((xs - px - ox) * 0.8, ys - py - oy)
                closer = d < d1
                d2 = np.where(closer, d1, np.minimum(d2, d))
                cx_ = np.where(closer, px + ox, cx_)
                cy_ = np.where(closer, py + oy, cy_)
                d1 = np.where(closer, d, d1)
    # dome each stone: brighter toward its upper-left
    lit = ((cx_ - xs) * 0.6 + (cy_ - ys) * 0.8) / 8.0
    v = 0.45 + lit * 0.35 + (pnoise(seed, 8, 1) - 0.5) * 0.2
    v = np.where(d2 - d1 < 1.3, 0.02, v)       # dark mortar-like cracks between stones
    img = shade(np.clip(v, 0, 1), ROCK)
    # the top edge of each stone catches light
    edge = (d2 - d1 >= 1.3) & (np.roll(d2 - d1, 1, axis=0) < 1.3)
    img[edge, :3] = hx("#948868")
    return img


def rot(img, k):
    return np.ascontiguousarray(np.rot90(img, k))


def dirt_edge_n(seed=5):
    """Grass fringe along the top edge of a dirt tile (the grass is north)."""
    r = rng(seed)
    img = np.zeros((T, T, 4), np.uint8)
    g = grass(seed + 1)
    for x in range(T):
        depth = 3 + int(1.5 * math.sin(x * 0.7) + 1.2 * math.sin(x * 0.23 + 1))
        for y in range(depth):
            img[y, x] = g[y, x]
        # blades hanging over the dirt
        if r.random() < 0.55:
            h = r.integers(1, 4)
            for k in range(h):
                put(img, x, depth + k, BLADE_M if k < h - 1 else BLADE_L)
        put(img, x, depth + (0 if r.random() < 0.5 else 1), "#3e3020", 200)
    return img


def shore_n(seed=8):
    """Bank, foam and a lighter shallows line where land is north of water."""
    img = np.zeros((T, T, 4), np.uint8)
    for x in range(T):
        d = 2 + int(1.2 * math.sin(x * 0.5) + math.sin(x * 0.19 + 2))
        for y in range(d):
            put(img, x, y, "#4a3a28" if y < d - 1 else "#2a2018")
        put(img, x, d, "#c8dce4" if x % 5 else "#8ab0c4")
        put(img, x, d + 1, "#6a92aa", 220)
        put(img, x, d + 2, "#3e6478", 160)
    return img


def build():
    out = CANON / "tiles"
    tiles = {}
    for i in range(4):
        tiles[f"grass-{i + 1}"] = grass(10 + i, flowers=(0, 0, 1, 2)[i])
        tiles[f"dirt-{i + 1}"] = dirt(20 + i)
        tiles[f"water-{i + 1}"] = water(i)
    tiles["dirt2-1"] = dirt(30, dark=True)
    tiles["dirt2-2"] = dirt(31, dark=True)
    for i in range(2):
        tiles[f"tallgrass-{i + 1}"] = tallgrass(40 + i)
        tiles[f"tree-{i + 1}"] = canopy(50 + i)
        tiles[f"tree-s-{i + 1}"] = canopy(60 + i, trunks=True)
        tiles[f"cliff-{i + 1}"] = cliff(70 + i)
    en = dirt_edge_n()
    sn = shore_n()
    # rot90 turns counter-clockwise: n -> w -> s -> e
    for k, d in enumerate("nwse"):
        tiles[f"dirtedge-{d}"] = rot(en, k)
        tiles[f"shore-{d}"] = rot(sn, k)
    out.mkdir(exist_ok=True)
    for name, arr in tiles.items():
        Image.fromarray(arr, "RGBA").save(assert_write(out / f"{name}.png"))
    return sorted(tiles)


if __name__ == "__main__":
    names = build()
    print(len(names), "tiles:", " ".join(names))
