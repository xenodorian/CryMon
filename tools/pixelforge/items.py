"""Key item and quest item icons, 64x64, drawn with the pixelforge Canvas.

Writes public/sprites/items/<id>.png through sprite_root.assert_write for the
items in content/items.json that had no icon. Run:
    python3 tools/pixelforge/items.py [--preview out.png]
"""
from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sprite_root import CANON, assert_write  # noqa: E402
from pixelforge.core import M, Mat, Canvas  # noqa: E402

S = 64
STEEL = M("#b8c0cc", spec=0.9)
IRON = M("#5a5a66", spec=0.6)
GOLD = M("#e0b840", spec=0.9)
SILVER = M("#d0d4dc", spec=1.0)
WOOD = M("#7a5030", tex="grain", tex_amp=0.7)
BONE = M("#e8e0c8", spec=0.3)
PAPER = M("#e8dcb8", tex="grain", tex_amp=0.3)
CLOTH = M("#b89a78", tex="fur", tex_amp=0.4)


def ring_chain(c, x0, y0, x1, y1, n, mat, r=2.2, z=0):
    for k in range(n):
        f = k / max(n - 1, 1)
        x, y = x0 + (x1 - x0) * f, y0 + (y1 - y0) * f + math.sin(f * math.pi) * 4
        c.ell(x, y, r * (1.3 if k % 2 else 0.8), r * (0.8 if k % 2 else 1.3), mat, z=z + k % 2, th=1.2)


def bowie_knife():
    c = Canvas(S, S, seed=1)
    c.poly([(14, 50), (40, 20), (52, 10), (50, 18), (46, 26), (20, 54)], STEEL, z=10, bevel=2)
    c.pattern(lambda x, y: (abs((x - 14) * 0.77 + (y - 50) * 0.64) < 40) & (abs(-(x - 14) * 0.64 + (y - 50) * 0.77 + 2) < 0.8), 3)
    c.cap(10, 46, 3.4, 24, 58, 3.4, M("#c8a040", spec=0.8), z=16)
    c.cap(4, 62, 4.2, 15, 51, 4.6, WOOD, z=12)
    c.ell(4, 62, 3.4, 3.4, M("#c8a040", spec=0.8), z=14)
    return c


def shackles(mat):
    c = Canvas(S, S, seed=2)
    for cx, cy in ((18, 38), (46, 26)):
        c.ell(cx, cy, 12, 12, mat, z=6, th=5)
        c.ell(cx + 9, cy - 8, 3, 3, mat, z=12)
    ring_chain(c, 26, 32, 38, 30, 4, mat, z=14)
    return c


def bone(tag):
    c = Canvas(S, S, seed=3)
    c.cap(16, 46, 4.5, 46, 18, 4.5, BONE, z=8)
    for x, y in ((16, 46), (46, 18)):
        c.ell(x - 3, y + 1, 5, 5, BONE, z=10)
        c.ell(x + 1, y + 4 if x < 30 else y - 3, 5, 5, BONE, z=10)
    c.cap(28, 30, 3.2, 36, 34, 2.4, M(tag), z=16)
    c.cap(28, 30, 3.2, 26, 42, 2.0, M(tag), z=15)
    c.ell(29, 31, 3, 3, M(tag), z=18)
    return c


def wraith_lantern():
    c = Canvas(S, S, seed=4)
    glow = Mat(["#1a3a6a", "#3a7ac0", "#7ac0f0", "#c8f0ff", "#ffffff"], emit=True)
    c.ell(32, 8, 6, 5, IRON, z=4, th=1.5)
    c.poly([(20, 16), (44, 16), (40, 12), (24, 12)], IRON, z=8, bevel=1)
    c.poly([(22, 18), (42, 18), (44, 50), (20, 50)], Mat(["#0a1420", "#122030", "#1a2c40", "#223850", "#2a4460"], soft=0.3),
           z=2, bevel=1)
    c.ell(32, 36, 7, 11, glow, z=10)
    c.ell(32, 30, 3, 4, glow, z=12)
    for x in (21, 32, 43):
        c.cap(x, 18, 1.6, x + (1 if x > 32 else -1 if x < 32 else 0), 50, 1.6, IRON, z=16)
    c.poly([(18, 50), (46, 50), (42, 56), (22, 56)], IRON, z=8, bevel=1)
    return c


def pocket_watch():
    c = Canvas(S, S, seed=5)
    ring_chain(c, 34, 4, 56, 18, 5, GOLD, r=1.8, z=2)
    c.ell(32, 10, 4, 4, GOLD, z=6, th=1.5)
    c.ell(30, 36, 20, 20, GOLD, z=6)
    c.ell(30, 36, 16, 16, M("#f4f0e4", spec=0.4), z=20)

    def face(cc):
        for k in range(12):
            a = k * math.pi / 6
            cc.put(30 + math.cos(a) * 13, 36 + math.sin(a) * 13, (60, 50, 40))
        for k in range(10):
            cc.put(30, 36 - k, (30, 26, 22))
        for k in range(7):
            cc.put(30 + k, 36 + k * 0.3, (30, 26, 22))
        # a crack across the glass
        for k in range(12):
            cc.put(22 + k, 28 + k * 0.6 + (k % 3 == 0), (170, 170, 180))
    c.ink(face)
    return c


def locket():
    c = Canvas(S, S, seed=6)
    ring_chain(c, 12, 6, 52, 6, 9, SILVER, r=1.6, z=2)
    c.ell(32, 14, 3, 3, SILVER, z=6, th=1.2)
    c.ell(32, 38, 15, 19, SILVER, z=6)
    c.ell(32, 38, 11, 15, M("#b8bcc8", spec=0.9), z=16)
    c.ell(32, 36, 4, 4, M("#6a2a8a", spec=1.0), z=24)

    def filigree(cc):
        for k in range(24):
            a = k * math.pi / 12
            cc.put(32 + math.cos(a) * 13, 38 + math.sin(a) * 17, (130, 134, 146))
    c.ink(filigree)
    return c


def old_map():
    c = Canvas(S, S, seed=7)
    c.poly([(8, 16), (48, 10), (52, 50), (12, 56)], PAPER, z=4, bevel=2)
    c.cap(48, 8, 5, 54, 52, 5, M("#d8c8a0", tex="grain", tex_amp=0.3), z=10)
    c.pattern(lambda x, y: ((x - 30) ** 2 + (y - 34) ** 2 > 380), -1)

    def ink(cc):
        for k in range(30):
            cc.put(14 + k, 40 - math.sin(k / 5) * 6 - k * 0.3, (120, 90, 60))
        for dx in range(-3, 4):
            cc.put(36 + dx, 24 + dx, (180, 40, 30))
            cc.put(36 + dx, 24 - dx, (180, 40, 30))
        for k in range(6):
            cc.put(18 + k * 2, 22, (90, 110, 70))
            cc.put(19 + k * 2, 21, (90, 110, 70))
    c.ink(ink)
    return c


def letter(seal, ribbon=None):
    c = Canvas(S, S, seed=8)
    c.poly([(6, 18), (58, 18), (58, 50), (6, 50)], PAPER, z=4, bevel=1.5)

    def flap(cc):
        for k in range(27):
            cc.put(6 + k, 18 + k * 0.6, (160, 140, 110))
            cc.put(58 - k, 18 + k * 0.6, (160, 140, 110))
    c.ink(flap)
    if ribbon:
        c.cap(6, 38, 2.2, 58, 38, 2.2, M(ribbon), z=12)
    c.ell(32, 34, 6, 6, M(seal, spec=0.7), z=16)
    c.ell(30, 32, 2, 2, M(seal, spec=1.0), z=18)
    return c


def rag_doll():
    c = Canvas(S, S, seed=9)
    dress = M("#7a90b8", tex="fur", tex_amp=0.5)
    c.cap(24, 48, 3, 20, 60, 3, CLOTH, z=2)
    c.cap(40, 48, 3, 44, 60, 3, CLOTH, z=2)
    c.poly([(22, 28), (42, 28), (48, 52), (16, 52)], dress, z=6, bevel=3)
    c.cap(22, 30, 3, 12, 42, 3, CLOTH, z=4)
    c.cap(42, 30, 3, 52, 40, 3, CLOTH, z=4)
    c.ell(32, 18, 11, 11, CLOTH, z=10)
    yarn = M("#a84a2a", tex="fur", tex_amp=0.8)
    for dx in (-10, -6, 6, 10):
        c.cap(32 + dx, 10, 2.4, 32 + dx * 1.2, 26, 1.8, yarn, z=12)
    c.ell(32, 9, 10, 4, yarn, z=13)

    def face(cc):
        for x in (28, 36):
            for dx, dy in ((0, 0), (1, 0), (0, 1), (1, 1)):
                cc.put(x + dx, 17 + dy, (30, 30, 40))
        for k in range(5):
            cc.put(30 + k, 23, (140, 60, 60))
        # a stitched patch on the dress
        for k in range(6):
            cc.put(26 + k, 40, (230, 220, 190))
            cc.put(26, 40 + k, (230, 220, 190))
    c.ink(face)
    return c


ICONS = {
    "bowieKnife": bowie_knife,
    "shackles": lambda: shackles(IRON),
    "goldenShackles": lambda: shackles(GOLD),
    "boneInes": lambda: bone("#b83a3a"),
    "boneTomas": lambda: bone("#3a6ab8"),
    "boneOriel": lambda: bone("#4a9a4a"),
    "wraithLantern": wraith_lantern,
    "tamWatch": pocket_watch,
    "silverLocket": locket,
    "oldMap": old_map,
    "brannLetter": lambda: letter("#a82a2a"),
    "marnReply": lambda: letter("#2a5aa8", ribbon="#c8a040"),
    "ragDoll": rag_doll,
}


# open centres punched out after rendering (cuff rings)
HOLES = {k: [(18, 38, 6.5), (46, 26, 6.5)] for k in ("shackles", "goldenShackles")}


def build(preview=None):
    out = CANON / "items"
    ims = {}
    for k, fn in ICONS.items():
        ims[k] = fn().render().convert("RGBA").copy()
        if k in HOLES:
            px = ims[k].load()
            for hx_, hy_, r in HOLES[k]:
                for y in range(S):
                    for x in range(S):
                        if (x - hx_) ** 2 + (y - hy_) ** 2 < r * r:
                            px[x, y] = (0, 0, 0, 0)
        ims[k].save(assert_write(out / f"{k}.png"))
    if preview:
        sheet = Image.new("RGBA", (len(ims) * 136, 136), (90, 90, 100, 255))
        for i, im in enumerate(ims.values()):
            sheet.alpha_composite(im.convert("RGBA").resize((128, 128), Image.NEAREST), (i * 136 + 4, 4))
        sheet.save(preview)
    return list(ims)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview")
    print("items:", " ".join(build(ap.parse_args().preview)))
