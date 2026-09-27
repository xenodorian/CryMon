"""The Hollow's ground tiles: the overworld tiles regraded to its violet
dusk, with glowcaps in the grass, lit tips on the tall grass and light
rippling on the water.

Writes public/sprites/tiles/h-<name>.png (through sprite_root.assert_write)
for grass-1..4, tallgrass-1..2, tree-1..2, tree-s-1..2 and water-1..4.
sprites.json tileTheme "hollow" makes tileArt.ts and main.c use them.
Run:  python3 tools/pixelforge/tiles_hollow.py [--preview out.png]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sprite_root import CANON, assert_write  # noqa: E402
from pixelforge import tiles as base  # noqa: E402

GLOW = np.array([200, 168, 255])
CAP = np.array([154, 224, 200])


def grade_water(img):
    out = img.copy()
    rgb = img[..., :3].astype(float)
    out[..., :3] = np.clip(rgb * np.array([0.72, 0.62, 0.78]) + np.array([16, 6, 20]), 0, 255).astype(np.uint8)
    return out


def grade(img):
    """Darken and push toward teal shadows and violet light."""
    out = img.copy()
    rgb = img[..., :3].astype(float)
    lum = rgb.mean(-1, keepdims=True) / 255.0
    g = rgb * np.array([0.58, 0.86, 0.78]) + np.array([8, 4, 22])
    g = g + lum * np.array([30, -4, 36])
    out[..., :3] = np.clip(g, 0, 255).astype(np.uint8)
    return out


def specks(img, seed, n, col, halo=True):
    r = np.random.default_rng(seed)
    T = img.shape[0]
    for _ in range(n):
        x, y = int(r.integers(1, T - 1)), int(r.integers(1, T - 1))
        if halo:
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                p = img[(y + dy) % T, (x + dx) % T]
                p[:3] = (p[:3] * 0.5 + col * 0.5).astype(np.uint8)
        img[y, x, :3] = np.minimum(col + 40, 255)


def lit_tips(img, src):
    """Tall grass tips (the brightest blades) glow lilac."""
    tip = (src[..., 0] == 0x8a) & (src[..., 1] == 0xac) & (src[..., 2] == 0x5c)
    img[tip, :3] = GLOW


def water_light(img, src):
    hi = (src[..., 0] == 0x6a) & (src[..., 1] == 0x92) & (src[..., 2] == 0xaa)
    top = (src[..., 0] == 0xa8) & (src[..., 1] == 0xc8) & (src[..., 2] == 0xd8)
    img[hi, :3] = np.array([150, 120, 220])
    img[top, :3] = np.array([240, 220, 255])


def build(preview=None):
    tiles = {}
    for i in range(4):
        g = grade(base.grass(10 + i, flowers=0))
        specks(g, 100 + i, (1, 0, 2, 1)[i], CAP)
        if i >= 2:
            specks(g, 110 + i, 2, GLOW, halo=False)
        tiles[f"h-grass-{i + 1}"] = g
        w = base.water(i)
        wg = grade_water(w)
        water_light(wg, w)
        tiles[f"h-water-{i + 1}"] = wg
    for i in range(2):
        t = base.tallgrass(40 + i)
        tg = grade(t)
        lit_tips(tg, t)
        tiles[f"h-tallgrass-{i + 1}"] = tg
        tiles[f"h-tree-{i + 1}"] = grade(base.canopy(50 + i))
        c = grade(base.canopy(60 + i, trunks=True))
        specks(c, 120 + i, 2, CAP)
        tiles[f"h-tree-s-{i + 1}"] = c
    out = CANON / "tiles"
    for name, arr in tiles.items():
        Image.fromarray(arr, "RGBA").save(assert_write(out / f"{name}.png"))
    if preview:
        names = list(tiles)
        sheet = Image.new("RGBA", (len(names) * 100, 100), (40, 40, 48, 255))
        for i, n in enumerate(names):
            sheet.alpha_composite(Image.fromarray(tiles[n]).resize((96, 96), Image.NEAREST), (i * 100 + 2, 2))
        sheet.save(preview)
    return list(tiles)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview")
    print("hollow tiles:", " ".join(build(ap.parse_args().preview)))
