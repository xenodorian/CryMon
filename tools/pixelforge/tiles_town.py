"""Building and interior tiles, 32x32, drawn in code to match tiles.py.

Writes public/sprites/tiles/*.png (through sprite_root.assert_write), one set
per tile theme (content/sprites.json tileTheme picks a theme per map):
  wood, keep, crypt, palace:  floor-<t>-1..2, wall-<t> (top), wallf-<t> (face), door-<t>
  town, seph:                 wallf-<t>-1..2, roof-<t>-1..2, ridge-<t>, door-<t>
plus bars, gate, flowers-1..2, and the crate and bed overlays for rooms, and the animated wall lights in fx/:
torch-1..4 and lantern-1..4 (16x16).

Floors and roofs wrap seamlessly left to right; floors wrap on all sides.
Run:  python3 tools/pixelforge/tiles_town.py [--preview out.png]
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
from pixelforge.tiles import T, hx, rng, pnoise, shade, put, grass  # noqa: E402

YS, XS = np.mgrid[0:T, 0:T]


def blank():
    return np.zeros((T, T, 4), np.uint8)


def rect(img, x, y, w, h, col, a=255):
    c = hx(col) if isinstance(col, str) else col
    x0, y0 = max(0, int(x)), max(0, int(y))
    x1, y1 = min(T, int(x + w)), min(T, int(y + h))
    if x1 > x0 and y1 > y0:
        img[y0:y1, x0:x1, :3] = c
        img[y0:y1, x0:x1, 3] = a


def darken(img, mask, f):
    img[mask, :3] = (img[mask, :3] * f).astype(np.uint8)


def pal(base, n=6, lo=0.55, hi=1.25):
    b = np.array(hx(base), float)
    return [tuple(int(v) for v in np.clip(b * (lo + (hi - lo) * i / (n - 1)), 0, 255)) for i in range(n)]


# --- floors -----------------------------------------------------------------

def floor_wood(seed):
    """Horizontal planks, 4 per tile, with grain, seams and a knot or two."""
    r = rng(seed)
    P = pal("#8a6440")
    grain = pnoise(seed, 2, 2)
    fine = np.sin(YS * 2.1 + np.sin(XS / 5 + seed) * 1.2) * 0.5 + 0.5
    img = None
    v = np.zeros((T, T))
    for k in range(4):
        tone = 0.35 + r.random() * 0.3
        band = (YS >= k * 8) & (YS < k * 8 + 8)
        v[band] = tone + (grain[band] - 0.5) * 0.25 + (fine[band] - 0.5) * 0.12
    img = shade(np.clip(v, 0, 1), P)
    for k in range(4):
        y = k * 8
        rect(img, 0, y + 7, T, 1, "#3a2616")
        rect(img, 0, y, T, 1, "#a8805a")
        seam = (k * 13 + seed * 7) % T
        rect(img, seam, y, 1, 7, "#3a2616")
        put(img, seam + 1, y + 1, "#a8805a")
        put(img, seam + 3, y + 3, "#4a3220")
        put(img, seam + 11, y + 5, "#4a3220")
    for _ in range(1 + seed % 2):
        x, y = r.integers(2, 30), r.integers(0, 4) * 8 + 3
        for dx, dy in ((0, 0), (1, 0), (0, 1), (1, 1)):
            put(img, x + dx, y + dy, "#4a3018")
        put(img, x - 1, y, "#6a4a2c")
    return img


def flagstones(seed, base, mortar, moss=None, cracks=0, bone=False):
    """Offset square flagstones, 16px, each domed so light catches its top left."""
    r = rng(seed)
    P = pal(base, 6, 0.5, 1.2)
    v = np.zeros((T, T))
    edge = np.zeros((T, T), bool)
    for row in range(2):
        off = 8 if row else 0
        for col in range(3):
            x0, y0 = col * 16 - off, row * 16
            tone = 0.35 + r.random() * 0.25
            m = (XS >= x0) & (XS < x0 + 16) & (YS >= y0) & (YS < y0 + 16)
            lx = (XS - x0) / 16.0
            ly = (YS - y0) / 16.0
            v[m] = tone + (0.5 - lx[m]) * 0.12 + (0.5 - ly[m]) * 0.18
            edge |= m & ((XS == x0) | (YS == y0))
    v += (pnoise(seed + 4, 8, 2) - 0.5) * 0.3
    img = shade(np.clip(v, 0, 1), P)
    img[edge, :3] = hx(mortar)
    lit = np.roll(edge, 1, axis=0) & ~edge
    img[lit, :3] = np.clip(img[lit, :3].astype(int) + 22, 0, 255)
    for _ in range(cracks):
        x, y = r.integers(0, T), r.integers(0, T)
        dx = r.choice([-1, 1])
        for k in range(r.integers(4, 9)):
            put(img, x + (k // 2) * dx, y + k, mortar)
    if moss:
        mm = (pnoise(seed + 9, 4, 3) > 0.6) & (np.roll(edge, 1, 1) | edge | (pnoise(seed + 2, 16, 1) > 0.8))
        img[mm, :3] = (img[mm, :3] * 0.4 + np.array(hx(moss)) * 0.6).astype(np.uint8)
    if bone:
        x, y = r.integers(4, 26), r.integers(4, 26)
        for k in range(5):
            put(img, x + k, y + k // 3, "#d8d0b8")
        put(img, x - 1, y - 1, "#d8d0b8")
        put(img, x - 1, y + 1, "#d8d0b8")
        put(img, x + 5, y + 1, "#d8d0b8")
        put(img, x + 5, y + 3, "#d8d0b8")
    return img


def floor_palace(seed):
    """Cream and rose marble checks with fine veins and gold seams."""
    r = rng(seed)
    chk = ((XS // 16) + (YS // 16)) % 2
    veins = np.abs(np.sin((XS * 0.4 + YS * 0.9) / 3 + pnoise(seed, 4, 3) * 9)) < 0.12
    img = blank()
    A = shade(np.clip(0.55 + (pnoise(seed + 1, 4, 2) - 0.5) * 0.4, 0, 1), pal("#e8dcc8", 6, 0.75, 1.08))
    B = shade(np.clip(0.5 + (pnoise(seed + 2, 4, 2) - 0.5) * 0.4, 0, 1), pal("#b87a78", 6, 0.7, 1.15))
    img[:] = np.where(chk[..., None] == 0, A, B)
    darken(img, veins, 0.82)
    seam = (XS % 16 == 0) | (YS % 16 == 0)
    img[seam, :3] = hx("#c8a050")
    img[(XS % 16 == 0) & (YS % 16 == 0), :3] = hx("#fff0b0")
    for _ in range(3):
        put(img, r.integers(0, T), r.integers(0, T), "#fffaf0")
    return img


# --- interior walls ----------------------------------------------------------

def wall_top(seed, base, rim, pattern="stone", inlay=None):
    """The top of a wall as seen from above: dark, with a lit rim."""
    P = pal(base, 5, 0.6, 1.1)
    v = 0.4 + (pnoise(seed, 4, 2) - 0.5) * 0.4
    img = shade(np.clip(v, 0, 1), P)
    if pattern == "stone":
        seam = ((YS % 8) == 0) | ((XS + (YS // 8) * 8) % 16 == 0)
        darken(img, seam, 0.6)
    else:
        seam = (YS % 16) == 0
        darken(img, seam, 0.6)
        g = np.sin(XS * 1.7 + YS * 0.2) > 0.7
        darken(img, g, 0.85)
    rect(img, 0, 0, T, 1, rim)
    rect(img, 0, T - 1, T, 1, "#0a0806")
    if inlay:
        rect(img, 0, 15, T, 2, inlay)
        rect(img, 0, 15, T, 1, "#fff0b0")
    return img


def wallf_wood(seed):
    """Panelled room wall: striped paper above, a wainscot below, a baseboard."""
    img = blank()
    stripe = ((XS // 4) % 2 == 0)
    rect(img, 0, 0, T, 17, "#c8b088")
    img[:17][stripe[:17], :3] = hx("#b89c74")
    dots = ((XS % 8) == 2) & ((YS % 6) == 3) & (YS < 16)
    img[dots, :3] = hx("#8a6a48")
    rect(img, 0, 0, T, 3, "#3a2616")          # beam shadow along the top
    rect(img, 0, 3, T, 1, "#6a4c30")
    rect(img, 0, 16, T, 2, "#a8805a")         # chair rail
    rect(img, 0, 18, T, 11, "#6a4a2c")
    for x0 in (2, 18):
        rect(img, x0, 20, 12, 7, "#7a5836")
        rect(img, x0, 20, 12, 1, "#9a7450")
        rect(img, x0, 26, 12, 1, "#4a3220")
        rect(img, x0, 20, 1, 7, "#9a7450")
        rect(img, x0 + 11, 20, 1, 7, "#4a3220")
    rect(img, 0, 29, T, 3, "#2a1a0e")
    rect(img, 0, 29, T, 1, "#4a3220")
    return img


def wallf_stone(seed, base, mortar, moss=None, drip=False, banner=None):
    """A wall face of stone courses, shadowed at the top where the cap overhangs."""
    r = rng(seed)
    P = pal(base, 6, 0.55, 1.15)
    v = np.zeros((T, T))
    for row in range(4):
        off = (row % 2) * 8
        for col in range(3):
            x0, y0 = col * 16 - off, row * 8
            m = (XS >= x0) & (XS < x0 + 16) & (YS >= y0) & (YS < y0 + 8)
            v[m] = 0.35 + r.random() * 0.3 + (0.5 - (YS[m] - y0) / 8.0) * 0.2
    v += (pnoise(seed, 8, 2) - 0.5) * 0.25
    img = shade(np.clip(v, 0, 1), P)
    seam = (YS % 8 == 7) | (((XS + (YS // 8 % 2) * 8) % 16) == 0)
    img[seam, :3] = hx(mortar)
    rect(img, 0, 0, T, 2, "#08070a")
    img[2:5, :, :3] = (img[2:5, :, :3] * 0.6).astype(np.uint8)
    img[T - 2:, :, :3] = (img[T - 2:, :, :3] * 0.55).astype(np.uint8)
    if moss:
        mm = (pnoise(seed + 5, 4, 3) > 0.62) & (YS > 18)
        img[mm, :3] = (img[mm, :3] * 0.4 + np.array(hx(moss)) * 0.6).astype(np.uint8)
    if drip:
        for x in (7, 22):
            for y in range(5, 5 + r.integers(6, 14)):
                put(img, x, y, "#1a2420", 255)
    if banner:
        rect(img, 10, 3, 12, 22, banner)
        rect(img, 10, 3, 12, 2, "#e0b840")
        rect(img, 10, 3, 1, 22, "#3a0a10")
        for k in range(6):
            rect(img, 10 + k, 25, 1, 6 - k, banner)
            rect(img, 21 - k, 25, 1, 6 - k, banner)
        rect(img, 14, 10, 4, 4, "#e0b840")
        put(img, 15, 9, "#e0b840")
        put(img, 16, 14, "#e0b840")
    return img


def wallf_palace(seed):
    """Deep red silk wall between gold pilasters, a dark marble dado below."""
    img = blank()
    silk = shade(np.clip(0.5 + (pnoise(seed, 2, 2) - 0.5) * 0.3 + np.sin(XS * 1.1) * 0.05, 0, 1), pal("#7a1a24", 5, 0.6, 1.2))
    img[:] = silk
    dia = (np.abs(((XS + 4) % 12) - 6) + np.abs((YS % 12) - 6)) == 5
    img[dia & (YS < 20), :3] = hx("#a8484a")
    rect(img, 0, 0, T, 2, "#08070a")
    rect(img, 0, 2, T, 2, "#c8a050")
    for x0 in (0, 30):
        rect(img, x0, 2, 2, 20, "#c8a050")
    rect(img, 0, 20, T, 2, "#e0b840")
    rect(img, 0, 22, T, 8, "#2a2230")
    rect(img, 0, 22, T, 1, "#4a3e58")
    rect(img, 0, 30, T, 2, "#141018")
    return img


# --- doors -------------------------------------------------------------------

def door_inner(cap, floor, mat=None, frame="#3a2616", arch=False):
    """Interior exit set into the bottom wall: the cap, an opening, a step."""
    img = cap.copy()
    rect(img, 6, 0, 20, T, frame)
    rect(img, 8, 0, 16, T, "#0c0a08")
    if arch:
        for x in range(8, 24):
            h = int(6 - math.sqrt(max(0, 64 - (x - 15.5) ** 2)) * 0.75)
            rect(img, x, 0, 1, max(0, h), frame)
    grad = np.linspace(0.9, 0.2, 10)[:, None, None]
    img[0:10, 8:24, :3] = (floor[0:10, 8:24, :3] * grad).astype(np.uint8)
    if mat:
        rect(img, 9, 2, 14, 6, mat)
        rect(img, 9, 2, 14, 1, "#fff0c8", 120)
    return img


def door_wood(wall, plank="#6a4428", frame="#3a2616", step="#8a8070", knob="#e0b840"):
    img = wall.copy()
    rect(img, 7, 4, 18, 28, frame)
    rect(img, 9, 6, 14, 24, plank)
    for x in (13, 18):
        rect(img, x, 6, 1, 24, "#3a2616")
    for y in (10, 24):
        rect(img, 9, y, 14, 2, "#2a2a30")
        rect(img, 9, y, 3, 2, "#5a5a66")
    rect(img, 9, 6, 14, 1, "#8a6444")
    put(img, 20, 17, knob)
    put(img, 20, 18, "#8a6a20")
    rect(img, 5, 30, 22, 2, step)
    rect(img, 5, 30, 22, 1, "#b0a890")
    return img


def door_arch(wall, leaf="#2a6a6a", frame="#e8dcc0", trim="#e0b840"):
    img = wall.copy()
    for x in range(6, 26):
        top = 4 + int(8 - math.sqrt(max(0, 100 - (x - 15.5) ** 2)) * 0.8)
        rect(img, x, top, 1, T - top, frame)
    for x in range(8, 24):
        top = 6 + int(8 - math.sqrt(max(0, 64 - (x - 15.5) ** 2)) * 0.9)
        rect(img, x, top, 1, T - top - 2, leaf)
    rect(img, 15, 8, 2, 22, "#143a3a")
    rect(img, 8, 18, 16, 1, trim)
    put(img, 13, 20, trim)
    put(img, 18, 20, trim)
    rect(img, 4, 30, 24, 2, "#c8c0b0")
    return img


# --- outdoor walls and roofs -------------------------------------------------

def wallf_town(seed, window=False):
    """Cream plaster with dark timber framing, a sill at the bottom."""
    img = shade(np.clip(0.55 + (pnoise(seed, 4, 2) - 0.5) * 0.35, 0, 1), pal("#d8c8a0", 5, 0.75, 1.08))
    rect(img, 0, 0, T, 3, "#2a1a10")
    img[3:6, :, :3] = (img[3:6, :, :3] * 0.7).astype(np.uint8)
    for x in (0, 31):
        rect(img, x, 0, 1, T, "#4a3020")
    rect(img, 0, 3, T, 2, "#5a3a24")
    rect(img, 0, 26, T, 2, "#5a3a24")
    if not window:
        for k in range(20):
            put(img, 3 + k * 26 / 20 + (seed % 2), 6 + k, "#5a3a24")
            put(img, 4 + k * 26 / 20 + (seed % 2), 6 + k, "#4a3020")
    else:
        rect(img, 7, 8, 18, 15, "#4a3020")
        rect(img, 9, 10, 14, 11, "#ffcf70")
        grad = np.linspace(1.0, 0.7, 11)[:, None]
        img[10:21, 9:23, :3] = (img[10:21, 9:23, :3] * grad[..., None]).astype(np.uint8)
        rect(img, 15, 10, 2, 11, "#4a3020")
        rect(img, 9, 15, 14, 1, "#4a3020")
        rect(img, 3, 8, 4, 15, "#3a5a3a")
        rect(img, 25, 8, 4, 15, "#3a5a3a")
        for y in (11, 15, 19):
            rect(img, 3, y, 4, 1, "#2a4028")
            rect(img, 25, y, 4, 1, "#2a4028")
        rect(img, 6, 23, 20, 2, "#8a6444")
        for x, c in ((9, "#c84a4a"), (13, "#e8c85a"), (18, "#c84a4a"), (22, "#e8e0c8")):
            put(img, x, 22, c)
            put(img, x + 1, 21, "#4c7a3c")
    rect(img, 0, 28, T, 4, "#7a7060")
    rect(img, 0, 28, T, 1, "#a09880")
    for x in range(0, T, 8):
        rect(img, x, 29, 1, 3, "#5a5448")
    return img


def wallf_seph(seed, window=False):
    """Pale limestone ashlar with a gold band; the window is an arched blue light."""
    r = rng(seed)
    v = np.zeros((T, T))
    for row in range(4):
        off = (row % 2) * 8
        for col in range(3):
            m = (XS >= col * 16 - off) & (XS < col * 16 - off + 16) & (YS >= row * 8) & (YS < row * 8 + 8)
            v[m] = 0.55 + r.random() * 0.2
    v += (pnoise(seed, 8, 2) - 0.5) * 0.15
    img = shade(np.clip(v, 0, 1), pal("#e0d8c8", 5, 0.72, 1.1))
    seam = (YS % 8 == 7) | (((XS + (YS // 8 % 2) * 8) % 16) == 0)
    darken(img, seam, 0.8)
    rect(img, 0, 0, T, 3, "#2a2a38")
    img[3:6, :, :3] = (img[3:6, :, :3] * 0.72).astype(np.uint8)
    rect(img, 0, 24, T, 2, "#c8a050")
    rect(img, 0, 24, T, 1, "#fff0b0")
    if window:
        for x in range(9, 23):
            top = 7 + int(6 - math.sqrt(max(0, 49 - (x - 15.5) ** 2)) * 0.85)
            rect(img, x, top, 1, 21 - top, "#e8dcc0")
        for x in range(11, 21):
            top = 9 + int(5 - math.sqrt(max(0, 25 - (x - 15.5) ** 2)) * 0.9)
            rect(img, x, top, 1, 19 - top, "#4a7ac0")
        rect(img, 15, 9, 2, 10, "#c8a050")
        rect(img, 11, 14, 10, 1, "#c8a050")
        put(img, 12, 11, "#c8e8ff")
        put(img, 13, 12, "#c8e8ff")
    img[T - 2:, :, :3] = (img[T - 2:, :, :3] * 0.7).astype(np.uint8)
    return img


def shingles(seed, base, line, moss=None, scale=False, ridge=False, trim=None):
    """Rows of shingles lit from above; scale=True for rounded slate."""
    r = rng(seed)
    P = pal(base, 6, 0.55, 1.2)
    v = np.zeros((T, T))
    rowh = 6
    for row in range(T // rowh + 1):
        y0 = row * rowh - (2 if not ridge else 0)
        off = 5 if row % 2 else 0
        for col in range(-1, 4):
            x0 = col * 10 + off
            m = (XS >= x0) & (XS < x0 + 10) & (YS >= y0) & (YS < y0 + rowh)
            if scale:
                m &= ((XS - x0 - 5) ** 2 * 0.25 + (YS - y0) ** 2 * 0.2) < 7 + 1e-9
                m |= (XS >= x0) & (XS < x0 + 10) & (YS >= y0) & (YS < y0 + 2)
            t = 0.3 + r.random() * 0.25 + (YS - y0) / rowh * 0.3
            v[m] = t[m]
    v += (pnoise(seed, 8, 2) - 0.5) * 0.2
    img = shade(np.clip(v, 0, 1), P)
    if not scale:
        # each course: shadowed under the course above, a lit lower lip,
        # and short gaps between tiles only on the exposed lower part
        ry = (YS + 2) % rowh
        darken(img, ry == 0, 0.45)
        darken(img, ry == 1, 0.75)
        lip = ry == rowh - 1
        img[lip, :3] = np.clip(img[lip, :3].astype(int) + 30, 0, 255)
        for row in range(T // rowh + 2):
            off = 5 if row % 2 else 0
            y0 = row * rowh - 2
            for x in range(off, T + 10, 10):
                for y in range(y0 + 2, y0 + rowh - 1):
                    if 0 <= y < T:
                        img[y, x % T, :3] = hx(line)
                        if y > y0 + 2:
                            img[y, (x + 1) % T, :3] = np.clip(img[y, (x + 1) % T, :3].astype(int) + 18, 0, 255)
    else:
        lines = ((YS + 2) % rowh == 0)
        img[lines, :3] = hx(line)
    if moss:
        mm = pnoise(seed + 7, 4, 3) > 0.64
        img[mm, :3] = (img[mm, :3] * 0.45 + np.array(hx(moss)) * 0.55).astype(np.uint8)
    if ridge:
        rect(img, 0, 0, T, 7, trim or "#6a2418")
        rect(img, 0, 0, T, 2, "#f0c8a0" if not trim else "#fff0b0")
        for x in range(0, T, 8):
            rect(img, x, 2, 1, 5, line)
        rect(img, 0, 7, T, 1, "#2a0a06")
    return img


# --- props on the ground -----------------------------------------------------

def bars(seed):
    img = shade(np.clip(0.3 + (pnoise(seed, 4, 2) - 0.5) * 0.3, 0, 1), pal("#2a2620", 5, 0.5, 1.1))
    rect(img, 0, 0, T, 3, "#4a4a52")
    rect(img, 0, 29, T, 3, "#4a4a52")
    for x in range(3, T, 7):
        rect(img, x, 0, 3, T, "#3a3a44")
        rect(img, x, 0, 1, T, "#8a8a98")
        rect(img, x + 2, 0, 1, T, "#1a1a20")
    for y in (0, 29):
        rect(img, 0, y, T, 1, "#8a8a98")
    return img


def gate(seed):
    img = bars(seed)
    for y in (8, 20):
        rect(img, 0, y, T, 3, "#3a3a44")
        rect(img, 0, y, T, 1, "#8a8a98")
    for x in range(3, T, 7):
        put(img, x + 1, 0, "#b0b0c0")
    rect(img, 13, 12, 6, 6, "#8a7348")
    rect(img, 15, 14, 2, 3, "#1a1410")
    return img


def flowers(seed):
    r = rng(seed)
    img = grass(seed)
    for _ in range(9):
        x, y = r.integers(2, 30), r.integers(3, 30)
        c = r.choice(["#c84a5a", "#e8c85a", "#e8e0c8", "#9a7ac8", "#e88a5a"])
        for dx, dy in ((0, -1), (-1, 0), (1, 0), (0, 1)):
            put(img, x + dx, y + dy, c)
        put(img, x, y, "#fff0a0")
        put(img, x + 1, y + 2, "#2a4226")
        put(img, x, y + 2, "#4c7a3c")
    return img


def crate_over():
    """A lidded crate on a transparent ground, for C tiles in rooms."""
    img = blank()
    rect(img, 5, 26, 24, 3, "#000000", 90)
    rect(img, 4, 6, 24, 21, "#3a2616")
    rect(img, 5, 7, 22, 19, "#8a6440")
    for y in (12, 18):
        rect(img, 5, y, 22, 1, "#5a3e24")
    rect(img, 5, 7, 22, 1, "#b08a5c")
    rect(img, 5, 7, 2, 19, "#6a4a2c")
    rect(img, 25, 7, 2, 19, "#6a4a2c")
    for k in range(18):
        put(img, 7 + k, 24 - k, "#6a4a2c")
    for x, y in ((6, 8), (25, 8), (6, 24), (25, 24)):
        put(img, x, y, "#c8c0b0")
    return img


def bed_over():
    """A narrow bed seen from above, pillow at the top, for B and U tiles."""
    img = blank()
    rect(img, 4, 30, 25, 2, "#000000", 90)
    rect(img, 3, 1, 26, 30, "#4a3020")
    rect(img, 3, 1, 26, 1, "#7a5836")
    rect(img, 5, 3, 22, 26, "#e8e0cc")
    rect(img, 7, 4, 18, 6, "#fffaf0")
    rect(img, 7, 9, 18, 1, "#c8c0a8")
    rect(img, 5, 12, 22, 17, "#8a3a3a")
    rect(img, 5, 12, 22, 2, "#e8e0cc")
    for y in range(15, 29, 4):
        rect(img, 5, y, 22, 1, "#6a2a2a")
    rect(img, 5, 12, 1, 17, "#5a2020")
    return img


# --- animated wall lights (fx/, 16x16) ---------------------------------------

def flame(img, cx, top, f, h=7):
    wob = [0, 1, 0, -1][f]
    for k in range(h):
        w = max(0.5, (h - k) * 0.45 - (0.3 if k == 0 else 0))
        x = cx + wob * (k / h)
        y = top + h - 1 - k
        col = "#ffffff" if k < 2 and w < 1.3 else ("#ffe070" if k < h * 0.5 else "#ff8a20")
        for dx in range(-int(w), int(w) + 1):
            c = col if abs(dx) < w - 0.6 else "#e04a10"
            if k < 2:
                c = "#fff8c0" if abs(dx) < 1 else "#ffc040"
            put16(img, x + dx, y, c)


def put16(img, x, y, col):
    x, y = int(round(x)), int(round(y))
    if 0 <= x < 16 and 0 <= y < 16:
        img[y, x, :3] = hx(col)
        img[y, x, 3] = 255


def torch(f):
    img = np.zeros((16, 16, 4), np.uint8)
    for y in range(8, 15):
        for x in (7, 8):
            put16(img, x, y, "#5a3a20" if x == 7 else "#3a2410")
    for x in range(5, 11):
        put16(img, x, 8, "#6a6a78")
        put16(img, x, 9, "#3a3a44")
    put16(img, 6, 13, "#3a3a44")
    put16(img, 9, 13, "#3a3a44")
    flame(img, 7.5, 1 - (f % 2), f, 7 + (f % 2))
    return img


def lantern(f):
    img = np.zeros((16, 16, 4), np.uint8)
    for x in range(2, 10):
        put16(img, x, 1, "#2a2a30")
    put16(img, 2, 2, "#2a2a30")
    put16(img, 8, 2, "#2a2a30")
    put16(img, 8, 3, "#2a2a30")
    for x in range(5, 12):
        put16(img, x, 4, "#2a2a30")
        put16(img, x, 13, "#2a2a30")
    for y in range(5, 13):
        put16(img, 5, y, "#2a2a30")
        put16(img, 11, y, "#2a2a30")
    glow = ["#ffe890", "#fff0b0", "#ffe070", "#ffd860"][f]
    for y in range(5, 13):
        for x in range(6, 11):
            put16(img, x, y, glow if 7 <= x <= 9 and 7 <= y <= 11 else "#e8a040")
    put16(img, 8, 9 - (f % 2), "#ffffff")
    put16(img, 8, 14, "#2a2a30")
    return img


# --- build -------------------------------------------------------------------

def build(preview=None):
    tiles = {}
    # wood rooms (homes, guild halls, the inn, the library)
    tiles["floor-wood-1"] = floor_wood(1)
    tiles["floor-wood-2"] = floor_wood(2)
    tiles["wall-wood"] = wall_top(3, "#4a3020", "#8a6444", pattern="wood")
    tiles["wallf-wood"] = wallf_wood(4)
    tiles["door-wood"] = door_inner(tiles["wall-wood"], tiles["floor-wood-1"], mat="#8a3a2a")
    # stone keeps (the Sephirot bases)
    tiles["floor-keep-1"] = flagstones(10, "#7a7468", "#2e2a26")
    tiles["floor-keep-2"] = flagstones(11, "#7a7468", "#2e2a26", cracks=2)
    tiles["wall-keep"] = wall_top(12, "#3a3834", "#8a8478")
    tiles["wallf-keep"] = wallf_stone(13, "#6a665c", "#2a2622", banner=None)
    tiles["door-keep"] = door_inner(tiles["wall-keep"], tiles["floor-keep-1"], frame="#4a4a52")
    # crypts (Ghost Guild, Haunted Hall, the empty house)
    tiles["floor-crypt-1"] = flagstones(20, "#4a5048", "#141814", moss="#2a4a2a", cracks=2)
    tiles["floor-crypt-2"] = flagstones(21, "#4a5048", "#141814", moss="#2a4a2a", cracks=3, bone=True)
    tiles["wall-crypt"] = wall_top(22, "#22261e", "#4a5446")
    tiles["wallf-crypt"] = wallf_stone(23, "#3e4438", "#10140e", moss="#2a4a2a", drip=True)
    tiles["door-crypt"] = door_inner(tiles["wall-crypt"], tiles["floor-crypt-1"], frame="#2a2e26", arch=True)
    # Nero's palace
    tiles["floor-palace-1"] = floor_palace(30)
    tiles["floor-palace-2"] = floor_palace(31)
    tiles["wall-palace"] = wall_top(32, "#2a2230", "#6a5a78", inlay="#c8a050")
    tiles["wallf-palace"] = wallf_palace(33)
    tiles["door-palace"] = door_inner(tiles["wall-palace"], tiles["floor-palace-1"], mat="#a01a2a", frame="#c8a050", arch=True)
    # CryTown and the camps: timber and plaster under terracotta
    tiles["wallf-town-1"] = wallf_town(40)
    tiles["wallf-town-2"] = wallf_town(41, window=True)
    tiles["roof-town-1"] = shingles(42, "#a84a30", "#4a1a10")
    tiles["roof-town-2"] = shingles(43, "#a84a30", "#4a1a10", moss="#5a6a38")
    tiles["ridge-town"] = shingles(44, "#a84a30", "#4a1a10", ridge=True)
    tiles["door-town"] = door_wood(tiles["wallf-town-1"])
    # the Sephirot cities and Keter: limestone under blue slate
    tiles["wallf-seph-1"] = wallf_seph(50)
    tiles["wallf-seph-2"] = wallf_seph(51, window=True)
    tiles["roof-seph-1"] = shingles(52, "#4a6a9a", "#1a2440", scale=True)
    tiles["roof-seph-2"] = shingles(53, "#4a6a9a", "#1a2440", scale=True)
    tiles["ridge-seph"] = shingles(54, "#4a6a9a", "#1a2440", scale=True, ridge=True, trim="#c8a050")
    tiles["door-seph"] = door_arch(tiles["wallf-seph-1"])
    # ground props
    tiles["bars"] = bars(60)
    tiles["gate"] = gate(61)
    tiles["flowers-1"] = flowers(62)
    tiles["flowers-2"] = flowers(63)
    tiles["crate"] = crate_over()
    tiles["bed"] = bed_over()
    out = CANON / "tiles"
    for name, arr in tiles.items():
        Image.fromarray(arr, "RGBA").save(assert_write(out / f"{name}.png"))
    fx = CANON / "fx"
    lights = {}
    for f in range(4):
        lights[f"torch-{f + 1}"] = torch(f)
        lights[f"lantern-{f + 1}"] = lantern(f)
    for name, arr in lights.items():
        Image.fromarray(arr, "RGBA").save(assert_write(fx / f"{name}.png"))
    if preview:
        names = list(tiles)
        cols = 8
        sheet = Image.new("RGBA", (cols * 100, ((len(names) + cols - 1) // cols) * 100 + 60), (40, 40, 48, 255))
        for i, n in enumerate(names):
            sheet.alpha_composite(Image.fromarray(tiles[n]).resize((96, 96), Image.NEAREST), ((i % cols) * 100 + 2, (i // cols) * 100 + 2))
        y = ((len(names) + cols - 1) // cols) * 100 + 4
        for i, n in enumerate(lights):
            sheet.alpha_composite(Image.fromarray(lights[n]).resize((48, 48), Image.NEAREST), (i * 52 + 4, y))
        sheet.save(preview)
    return list(tiles) + list(lights)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview")
    names = build(ap.parse_args().preview)
    print(len(names), "tiles:", " ".join(names))
