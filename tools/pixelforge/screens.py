"""Title and ending backdrops, 240x160, painted with battlebg.py's helpers.

Writes public/sprites/screens/title.png and ending.png through
sprite_root.assert_write. The engines draw Max and the other sprites on
top, so each scene leaves ground where they stand. Run:
    python3 tools/pixelforge/screens.py [--preview out.png]
"""
from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sprite_root import CANON, assert_write  # noqa: E402
from pixelforge.battlebg import (W, H, XX, YY, Noise, finish, hexc, lerp, ramp,  # noqa: E402
                                 conifer_row, trees_row)

np.seterr(all="ignore")


def glow(img, x, y, r, col, amt):
    d = np.clip(1 - np.hypot(XX - x, YY - y) / r, 0, 1)
    img[:] = lerp(img, hexc(col), d ** 2 * amt)


def title():
    """Night over CryTown: moon, stars, the town lit on its ridge, a grassy
    knoll in front where Max (left) and the starter (right) stand."""
    N = Noise(31)
    img = ramp([(0, "#0c0a24"), (0.45, "#2a1e4a"), (0.75, "#6a3a5a"), (1, "#c8704a")], YY / 96)
    r = np.random.default_rng(3)
    for k in range(120):
        x, y = int(r.uniform(0, W)), int(r.uniform(0, 70))
        img[y, x] = lerp(img[y, x], hexc("#ffffff"), 0.5 + 0.5 * (k % 3 == 0))
    glow(img, 184, 30, 60, "#c8c0e8", 0.35)
    moon = np.hypot(XX - 184, YY - 30) < 13
    img[moon] = ramp([(0, "#e8e0c8"), (1, "#fffaf0")], (1 - (XX[moon] - 171) / 26))
    crater = moon & (N.fbm(4, 4, 2) > 0.62)
    img[crater] = lerp(img[crater], hexc("#c8c0a8"), 0.5)
    cl = N.fbm(60, 6, 4)
    band = np.clip((cl - 0.5) * 3, 0, 1) * np.clip(1 - np.abs(YY - 48) / 14, 0, 1)
    img[:] = lerp(img, hexc("#4a3a6a"), band * 0.7)
    far = 70 + N.line(50) * 14
    img[YY >= far[None, :]] = hexc("#2a2244")
    ridge = 86 + N.line(70, 3) * 10 - np.clip(1 - np.abs(np.arange(W) - 120) / 60, 0, 1) * 12
    img[YY >= ridge[None, :]] = hexc("#1a1630")
    # CryTown on the ridge: roofs, a tower, lit windows
    rr = np.random.default_rng(8)
    for k in range(11):
        x = 78 + k * 8 + rr.uniform(-2, 2)
        base = ridge[int(np.clip(x, 0, W - 1))] + 2
        h = rr.uniform(8, 14) + (k == 5) * 12
        body = (abs(XX - x) < 3.6) & (YY > base - h) & (YY < base + 1)
        roof = (YY <= base - h) & (YY > base - h - 5) & (abs(XX - x) < (YY - (base - h - 5)) * 0.9)
        img[body | roof] = hexc("#120e22")
        if k % 2 == 0 or k == 5:
            win = (abs(XX - x) < 0.8) & (abs(YY - (base - h * 0.55)) < 1.0)
            img[win] = hexc("#ffc860")
            glow(img, x, base - h * 0.55, 6, "#ffa040", 0.25)
    # foreground knoll
    hill = 112 - np.sin(np.arange(W) / 38) * 6 - np.clip(1 - np.abs(np.arange(W) - 200) / 50, 0, 1) * 10
    m = YY >= hill[None, :]
    g = ramp([(0, "#1e2a24"), (0.5, "#2a3a2c"), (1, "#3a4a34")], N.fbm(10, 4, 4) * 0.7 + (YY - 110) / 160)
    img[m] = g[m]
    rim = m & (YY < hill[None, :] + 2)
    img[rim] = hexc("#4a5a4a")
    tufts = m & (N.fbm(2, 5, 2) > 0.66)
    img[tufts] = lerp(img[tufts], hexc("#5a6a48"), 0.6)
    # fireflies
    for k in range(14):
        x, y = rr.uniform(10, 230), rr.uniform(96, 150)
        glow(img, x, y, 4, "#e8f070", 0.6)
    return finish(img, 24)


def ending():
    """Dawn after the war: the sun clears the far hills over a river valley,
    birds go up, the ground rises on the right where Calder stands."""
    N = Noise(32)
    img = ramp([(0, "#5a7ab0"), (0.4, "#b8a8c0"), (0.7, "#f0c090"), (1, "#ffe0a0")], YY / 88)
    glow(img, 120, 74, 90, "#fff0c0", 0.55)
    sun = np.hypot(XX - 120, YY - 74) < 12
    img[sun] = hexc("#fff8e0")
    for k in range(12):
        a = k * math.pi / 12 + math.pi
        ray = (np.abs(np.arctan2(YY - 74, XX - 120) - a) < 0.03) & (YY < 74)
        img[ray] = lerp(img[ray], hexc("#fff4d0"), 0.3)
    cl = N.fbm(50, 7, 4)
    img[:] = lerp(img, hexc("#f8d8b8"), np.clip((cl - 0.55) * 3, 0, 0.7) * (YY < 50))
    far = 70 + N.line(60) * 10
    img[YY >= far[None, :]] = lerp(hexc("#8a90b0")[None, :], hexc("#a8a0b8")[None, :], 0.4)
    # palace silhouette far off
    for x, h, w in ((58, 22, 3), (64, 30, 4), (70, 22, 3)):
        m = (abs(XX - x) < w) & (YY > 76 - h) & (YY < 78)
        img[m] = hexc("#7a7898")
        sp = (YY <= 76 - h) & (YY > 76 - h - 6) & (abs(XX - x) < (YY - (76 - h - 6)) * 0.5)
        img[sp] = hexc("#7a7898")
    mid = 84 + N.line(50, 3) * 8
    m = YY >= mid[None, :]
    img[m] = ramp([(0, "#6a8a5a"), (1, "#4a6a44")], (YY - 84) / 30)[m]
    conifer_row(img, 14, 90, 10, 16, "#4a6a48", "#5a7a54", 5)
    # river winding toward the sun
    cx = 120 + np.sin((YY - 84) / 12) * (YY - 84) * 0.6
    river = (YY > 84) & (np.abs(XX - cx) < 1 + (YY - 84) * 0.35)
    img[river] = ramp([(0, "#f8e8c0"), (1, "#8ab0d0")], (YY[river] - 84) / 76)
    # foreground: meadow, rising to a ledge on the right under Calder
    t_ = np.clip((np.arange(W) - 120) / 70, 0, 1)
    fg = 118 - (t_ * t_ * (3 - 2 * t_)) * 36 + np.sin(np.arange(W) / 9) * 1.5
    m = YY >= fg[None, :]
    g = ramp([(0, "#4a6a30"), (0.5, "#6a8a38"), (1, "#8aa048")], N.fbm(10, 4, 4) * 0.7 + (YY - 80) / 200)
    img[m] = g[m]
    rim = m & (YY < fg[None, :] + 2)
    img[rim] = hexc("#a8c060")
    fl = m & (N.fbm(2, 2, 2) > 0.8) & (N.fbm(30, 10, 2) > 0.5)
    img[fl] = hexc("#f0e0a0")
    fl2 = m & (N.fbm(2, 2, 2) < 0.14) & (YY > 128)
    img[fl2] = hexc("#e08aa0")
    trees_row(img, 3, 124, 22, 30, "#3a5a2a", "#5a7a3a", 9, (8, 12), trunk="#4a3020")
    # birds
    rr = np.random.default_rng(4)
    for k in range(7):
        x, y = rr.uniform(60, 200), rr.uniform(18, 50)
        for dx in (-3, -2, -1, 1, 2, 3):
            yy = int(y - (3 - abs(dx)) * 0.6)
            img[yy, int(x + dx)] = hexc("#3a3040")
    return finish(img, 24)


SCENES = {"title": title, "ending": ending}


def build(preview=None):
    out = CANON / "screens"
    out.mkdir(exist_ok=True)
    ims = {}
    for n, fn in SCENES.items():
        ims[n] = fn()
        ims[n].save(assert_write(out / f"{n}.png"))
    if preview:
        sheet = Image.new("RGB", (W * 3 * 2, H * 3))
        for i, im in enumerate(ims.values()):
            sheet.paste(im.resize((W * 3, H * 3), Image.NEAREST), (i * W * 3, 0))
        sheet.save(preview)
    return list(ims)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview")
    print("screens:", " ".join(build(ap.parse_args().preview)))
