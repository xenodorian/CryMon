"""Battle hit effects, one 4-frame burst per crystal nature, drawn in code.

Writes public/sprites/fx/<nature>-1..4.png (64x64, transparent) through
sprite_root.assert_write. The web battle plays the attacker's nature over the
target when a hit lands. Run:  python3 tools/pixelforge/hitfx.py
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sprite_root import CANON, assert_write  # noqa: E402

S = 64
C = S // 2


def hx(s, a=255):
    s = s.lstrip("#")
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4)) + (a,)


def new():
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    return im, ImageDraw.Draw(im)


def star(d, x, y, r, inner, pts, col, rot=0.0):
    P = []
    for k in range(pts * 2):
        a = rot + k * math.pi / pts - math.pi / 2
        rr = r if k % 2 == 0 else r * inner
        P.append((x + math.cos(a) * rr, y + math.sin(a) * rr))
    d.polygon(P, fill=col)


def blob(d, x, y, r, col):
    d.ellipse([x - r, y - r, x + r, y + r], fill=col)


def sparkle(d, x, y, r, col):
    d.line([(x - r, y), (x + r, y)], fill=col)
    d.line([(x, y - r), (x, y + r)], fill=col)


def ray_ring(d, n, r0, r1, col, rot=0.0, w=1):
    for k in range(n):
        a = rot + k * 2 * math.pi / n
        d.line([(C + math.cos(a) * r0, C + math.sin(a) * r0), (C + math.cos(a) * r1, C + math.sin(a) * r1)], fill=col, width=w)


def quartz(f):
    """Plain impact: a white star that pops, speed lines, then a ring."""
    im, d = new()
    r = [10, 20, 16, 8][f]
    ray_ring(d, 8, r + 2, r + 10 + f * 2, hx("#f4f0e0", 220 - f * 40), rot=0.2)
    star(d, C, C, r, 0.42, 8, hx("#fff8e0", 255 - f * 30))
    star(d, C, C, r * 0.55, 0.5, 8, hx("#ffffff"))
    if f >= 2:
        d.ellipse([C - r - 8, C - r - 8, C + r + 8, C + r + 8], outline=hx("#e8e0c8", 200 - f * 40), width=1)
    return im


def ruby(f):
    """Fire: flame tongues bloom out, then roll up into smoke."""
    im, d = new()
    cols = ["#7a1a0a", "#c8401a", "#f08028", "#ffc850", "#fff4c0"]
    rad = [8, 16, 20, 18][f]
    for k in range(9):
        a = k * 2 * math.pi / 9 + f * 0.3
        L = rad * (0.8 + 0.3 * math.sin(k * 2.3))
        x, y = C + math.cos(a) * L * 0.8, C + math.sin(a) * L * 0.7 - f * 2
        for i, c in enumerate(cols[: 5 - (f == 3) * 2]):
            blob(d, x, y - i * 1.5, max(1, rad * 0.45 - i * 2), hx(c))
    for i, c in enumerate(cols):
        blob(d, C, C - f * 2 - i, max(1, rad * 0.7 - i * 3), hx(c, 255 if f < 3 else 160))
    if f == 3:
        for k in range(5):
            blob(d, C - 12 + k * 6, C - 18 - (k % 2) * 4, 4, hx("#5a5050", 150))
    return im


def citrine(f):
    """Lightning: a forked bolt strikes down, sparks scatter."""
    im, d = new()
    pts = [(C + 6, 0), (C - 4, 18), (C + 5, 22), (C - 6, 40), (C + 3, 44), (C - 2, S - 6)]
    if f < 3:
        for w, c in ((6, "#ffe860"), (3, "#fffbe0")):
            d.line(pts[: 3 + f * 2 if f < 2 else 6], fill=hx(c, 230), width=w, joint="curve")
        if f >= 1:
            d.line([(C + 5, 22), (C + 16, 30), (C + 12, 38)], fill=hx("#ffe860"), width=2)
    for k in range(6 + f * 2):
        a = k * 1.9 + f
        r = 6 + f * 7 + (k % 3) * 3
        x, y = C + math.cos(a) * r, C + 10 + math.sin(a) * r * 0.6
        sparkle(d, x, y, 1 + (k % 2), hx("#fff6a0", 255 - f * 50))
    if f == 1:
        blob(d, C, S - 10, 10, hx("#fffbe0", 200))
    return im


def sapphire(f):
    """Water and frost: a splash crown, droplets, then ice glints."""
    im, d = new()
    r = [8, 16, 22, 24][f]
    d.ellipse([C - r, C + 6 - r * 0.35, C + r, C + 6 + r * 0.35], outline=hx("#9ad0f0", 230 - f * 40), width=2)
    for k in range(10):
        a = math.pi + k * math.pi / 9
        h = r * (0.7 + 0.3 * math.sin(k * 1.7))
        x = C + math.cos(a) * r
        top = C + 6 - h * (1.0 if f < 3 else 0.5)
        d.line([(x, C + 6), (x + math.cos(a) * 2, top)], fill=hx("#5aa8e0", 240 - f * 50), width=2)
        blob(d, x + math.cos(a) * 3, top - 2 - f * 2, 1.6, hx("#d8f0ff"))
    if f >= 2:
        for k in range(4):
            a = k * math.pi / 2 + 0.4
            star(d, C + math.cos(a) * 18, C + math.sin(a) * 12, 4, 0.3, 4, hx("#f0faff"))
    return im


def diamond(f):
    """Starlight: four-point stars twinkle outward in a ring."""
    im, d = new()
    for k in range(7):
        a = k * 2 * math.pi / 7 + f * 0.25
        r = [0, 10, 18, 24][f] + (k % 2) * 3
        s = [2, 5, 6, 3][(f + k) % 4]
        star(d, C + math.cos(a) * r, C + math.sin(a) * r, s, 0.25, 4, hx("#f4f0ff" if k % 2 else "#c8d8ff"))
    star(d, C, C, [12, 16, 8, 3][f], 0.2, 4, hx("#ffffff"))
    d.ellipse([C - 3, C - 3, C + 3, C + 3], fill=hx("#e8e0ff", [255, 220, 120, 60][f]))
    return im


def emerald(f):
    """Leaves: a whirl of leaves spirals in and slices across."""
    im, d = new()
    for k in range(8):
        a = k * 2 * math.pi / 8 + f * 0.6
        r = [22, 16, 12, 20][f] + (k % 3) * 2
        x, y = C + math.cos(a) * r, C + math.sin(a) * r * 0.8
        ang = a + math.pi / 2
        L, W = 6, 2.5
        P = [(x + math.cos(ang) * L, y + math.sin(ang) * L), (x + math.cos(ang + 1.57) * W, y + math.sin(ang + 1.57) * W),
             (x - math.cos(ang) * L, y - math.sin(ang) * L), (x - math.cos(ang + 1.57) * W, y - math.sin(ang + 1.57) * W)]
        d.polygon(P, fill=hx("#4a9a3a" if k % 2 else "#7ac050"))
        d.line([P[0], P[2]], fill=hx("#2a5a24"))
    if f in (1, 2):
        d.line([(8, 14 + f * 8), (S - 8, 30 + f * 8)], fill=hx("#d8f0b0", 220), width=2)
    return im


def jasper(f):
    """Earth: rocks burst up from the ground in a cloud of dust."""
    im, d = new()
    dust = [0, 10, 18, 22][f]
    for k in range(6):
        blob(d, C - 20 + k * 8, S - 12 - (k % 2) * 3, dust * 0.45 + 2, hx("#a08a68", 200 - f * 30))
    for k in range(6):
        a = math.pi + (k + 0.5) * math.pi / 6
        r = [4, 14, 22, 26][f]
        x, y = C + math.cos(a) * r, S - 16 + math.sin(a) * r * 1.1 + (f == 3) * 6
        s = 3 + (k % 3)
        d.polygon([(x - s, y + s * 0.6), (x - s * 0.3, y - s), (x + s, y - s * 0.4), (x + s * 0.6, y + s)], fill=hx("#7a6448"))
        d.line([(x - s * 0.3, y - s), (x + s, y - s * 0.4)], fill=hx("#b09a78"))
    return im


def obsidian(f):
    """Shadow: three claw slashes rip across, trailing violet smoke."""
    im, d = new()
    n = min(3, f + 1)
    for k in range(n):
        off = (k - 1) * 9
        L = [14, 22, 24, 24][f]
        a0, a1 = (C - L + off, C - L - off * 0.3), (C + L + off, C + L - off * 0.3)
        col = hx("#1a0a24") if f < 3 else hx("#3a1a4a", 160)
        d.line([a0, a1], fill=hx("#8a50c0", 200), width=5)
        d.line([a0, a1], fill=col, width=2)
    if f >= 2:
        for k in range(5):
            blob(d, C - 16 + k * 8, C + 16 - (k % 2) * 6, 4 + f, hx("#4a2a60", 120))
    return im


def prism(f):
    """Rainbow: a spinning ring of colored shards and tiny stars."""
    im, d = new()
    cols = ["#d63a3a", "#f2a030", "#f2d830", "#3fa34d", "#3a6fd6", "#8a4fd0"]
    r = [6, 14, 20, 24][f]
    for k, c in enumerate(cols * 2):
        a = k * 2 * math.pi / 12 + f * 0.5
        x, y = C + math.cos(a) * r, C + math.sin(a) * r
        star(d, x, y, 3.5, 0.4, 4, hx(c), rot=a)
    blob(d, C, C, [6, 5, 3, 1][f], hx("#ffffff"))
    return im


NATURES = {"quartz": quartz, "ruby": ruby, "citrine": citrine, "sapphire": sapphire, "diamond": diamond,
           "emerald": emerald, "jasper": jasper, "obsidian": obsidian, "prism": prism}


def build():
    out = CANON / "fx"
    out.mkdir(exist_ok=True)
    for n, fn in NATURES.items():
        for f in range(4):
            fn(f).save(assert_write(out / f"{n}-{f + 1}.png"))
    return sorted(NATURES)


if __name__ == "__main__":
    print("fx:", " ".join(build()))
