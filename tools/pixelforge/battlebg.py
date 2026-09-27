"""Battle backdrops, one per kind of place, painted in code.

Writes public/sprites/bg/<name>.png (240x160, the size of battle-bg.png)
through sprite_root.assert_write. content/sprites.json "battleBgMap" says
which map uses which backdrop; maps it leaves out keep battle-bg.png.
Run:  python3 tools/pixelforge/battlebg.py [--preview out.png]
"""
from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import numpy as np

np.seterr(all="ignore")
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sprite_root import CANON, assert_write  # noqa: E402

W, H = 240, 160
YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)
# where the two monsters stand (engine.ts drawBattle, in 240x160 units)
FOE = (194, 54, 30, 6)
PLAYER = (36, 100, 30, 7)
BAYER = (np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]], np.float32) / 16 - 0.47)


def hexc(s):
    s = s.lstrip("#")
    return np.array([int(s[i:i + 2], 16) for i in (0, 2, 4)], np.float32)


def lerp(a, b, t):
    t = np.clip(t, 0, 1)[..., None] if np.ndim(t) else np.clip(t, 0, 1)
    return a + (b - a) * t


def ramp(stops, t):
    """Color ramp: stops = [(pos, '#hex'), ...], t array in 0..1."""
    t = np.clip(t, 0, 1)
    out = np.zeros(t.shape + (3,), np.float32)
    for (p0, c0), (p1, c1) in zip(stops, stops[1:]):
        m = (t >= p0) & (t <= p1)
        f = (t[m] - p0) / max(p1 - p0, 1e-6)
        out[m] = hexc(c0) + (hexc(c1) - hexc(c0)) * f[:, None]
    return out


class Noise:
    def __init__(self, seed):
        self.r = np.random.default_rng(seed)

    def value(self, sx, sy, w=W, h=H):
        gw, gh = int(w / sx) + 3, int(h / sy) + 3
        g = self.r.random((gh, gw)).astype(np.float32)
        y, x = np.mgrid[0:h, 0:w].astype(np.float32)
        fx, fy = x / sx, y / sy
        x0, y0 = fx.astype(int), fy.astype(int)
        tx, ty = fx - x0, fy - y0
        tx, ty = tx * tx * (3 - 2 * tx), ty * ty * (3 - 2 * ty)
        a = g[y0, x0] + (g[y0, x0 + 1] - g[y0, x0]) * tx
        b = g[y0 + 1, x0] + (g[y0 + 1, x0 + 1] - g[y0 + 1, x0]) * tx
        return a + (b - a) * ty

    def fbm(self, sx, sy, oct=4, w=W, h=H):
        tot, amp, norm = 0, 1.0, 0
        for o in range(oct):
            tot = tot + self.value(sx / 2 ** o, sy / 2 ** o, w, h) * amp
            norm += amp
            amp *= 0.5
        return tot / norm

    def line(self, scale, oct=4):
        """1D fbm across the width, 0..1."""
        return self.fbm(scale, 1000, oct, W, 1)[0]


def shade_blob(img, cx, cy, rx, ry, col, alpha=0.45):
    d = ((XX - cx) / rx) ** 2 + ((YY - cy) / ry) ** 2
    a = np.clip(1 - d, 0, 1) ** 0.6 * alpha
    img[:] = lerp(img, hexc(col), a)


def stand_spots(img, col="#000000", alpha=0.35, top=None, rim=None, seed=0, side=True):
    """Ground under each monster. With top/rim colors the foe (and player)
    get a raised patch of the scene's ground, so the foe does not float over
    the horizon; the monster's own shadow sits in the middle of it."""
    N = Noise(seed + 50)
    tex = N.fbm(4, 3, 2)
    for i, (cx, cy, rx, ry) in enumerate((FOE, PLAYER)):
        if top:
            px, py = rx + 8, ry + 4
            d = ((XX - cx) / px) ** 2 + ((YY - cy) / py) ** 2
            side_m = (abs(XX - cx) < px * np.sqrt(np.clip(1 - ((YY - cy - 3) / py) ** 2, 0, 1))) & (YY > cy) & \
                (((XX - cx) / px) ** 2 + ((YY - cy - 3) / py) ** 2 < 1)
            if side:
                img[side_m & ~(d < 1)] = hexc(rim)
            m = d < 1
            img[m] = lerp(hexc(top)[None, :] * (0.88 + 0.24 * tex[m][:, None]), hexc("#ffffff")[None, :],
                          np.clip((cy - YY[m]) / py - 0.1, 0, 1) * 0.12)
            edge = m & (d > 0.86) & (YY > cy)
            img[edge] = lerp(img[edge], hexc(rim), 0.6)
        shade_blob(img, cx, cy, rx * 0.8, ry * 0.8, col, alpha)


def silhouette(img, top, col, soft=0.0):
    """Fill everything below the per-column height line `top`."""
    m = YY >= top[None, :]
    img[m] = hexc(col) if not soft else img[m]
    return m


def finish(img, levels=20, seed=0):
    """Posterize with ordered dither so it reads as pixel art."""
    th = np.tile(BAYER, (H // 4 + 1, W // 4 + 1))[:H, :W][..., None]
    q = np.floor(img / 255 * levels + th + 0.5) / levels * 255
    return Image.fromarray(np.clip(q, 0, 255).astype(np.uint8), "RGB")


HORIZON = 50


def grounded(img, hz, spots, levels):
    """Squeeze the sky above the scene's horizon row `hz` and stretch the
    ground below it so the horizon sits at HORIZON, just behind where the foe
    stands; then lay the stand spots and posterize."""
    src = np.where(np.arange(H) < HORIZON, np.arange(H) * hz / HORIZON,
                   hz + (np.arange(H) - HORIZON) * (H - 1 - hz) / (H - 1 - HORIZON))
    y0 = np.floor(src).astype(int)
    f = (src - y0)[:, None, None]
    y1 = np.clip(y0 + 1, 0, H - 1)
    img = img[y0] * (1 - f) + img[y1] * f
    spots(img)
    return finish(img, levels)


def trees_row(img, n, base, h0, h1, col, hi, seed, width=(8, 16), trunk=None):
    r = np.random.default_rng(seed)
    for k in range(n):
        x = r.uniform(-10, W + 10)
        h = r.uniform(h0, h1)
        w = r.uniform(*width)
        yb = base + r.uniform(-3, 3)
        if trunk:
            m = (abs(XX - x) < max(1.2, w * 0.12)) & (YY > yb - h * 0.4) & (YY < yb + 4)
            img[m] = hexc(trunk)
        for j in range(4):
            cy = yb - h * (0.35 + j * 0.2)
            rr = w * (1 - j * 0.18)
            d = ((XX - x - r.uniform(-2, 2)) / rr) ** 2 + ((YY - cy) / (rr * 0.8)) ** 2
            m = d < 1
            lit = np.clip((XX - x) / rr * -0.6 + (cy - YY) / rr * 0.6, 0, 1)
            img[m] = lerp(hexc(col)[None, :], hexc(hi)[None, :], (lit[m] > 0.45) * 0.7)


def conifer_row(img, n, base, h0, h1, col, hi, seed):
    r = np.random.default_rng(seed)
    for k in range(n):
        x = r.uniform(-8, W + 8)
        h = r.uniform(h0, h1)
        w = h * r.uniform(0.28, 0.36)
        yb = base + r.uniform(-2, 2)
        ty = (yb - YY) / h
        half = w * (1 - ty) * (0.75 + 0.25 * ((ty * 5) % 1))
        m = (ty > 0) & (ty < 1) & (abs(XX - x) < half)
        img[m] = hexc(col)
        m2 = m & (XX - x < -half * 0.25)
        img[m2] = hexc(hi)


# ---------------------------------------------------------------- scenes
def forest():
    N = Noise(11)
    img = ramp([(0, "#9ec8b0"), (0.5, "#6e9e7e"), (1, "#3e6a4e")], YY / 70)
    img[YY > 70] = hexc("#3e6a4e")
    conifer_row(img, 26, 68, 30, 50, "#48735a", "#5a8a6a", 1)
    trees_row(img, 16, 78, 24, 40, "#2f5a3a", "#3f7048", 2, (10, 18), trunk="#2a2018")
    # god rays
    for x0 in (60, 120, 170):
        m = (abs(XX - x0 - (YY) * 0.35) < 6 + YY * 0.04) & (YY < 110)
        img[m] = lerp(img[m], hexc("#e8f0c0"), 0.14)
    g = N.fbm(30, 10, 4)
    ground = ramp([(0, "#2e4a24"), (0.45, "#476a30"), (0.8, "#6a8a3a"), (1, "#8aa048")], g * 0.9 + (YY - 80) / 200)
    m = YY > 80
    img[m] = ground[m]
    # leaf litter path
    p = np.abs(XX - 120 - (YY - 80) * 0.6 + np.sin(YY / 14) * 10) < 16 + (YY - 80) * 0.7
    pm = m & p & (N.fbm(6, 4, 3) > 0.35)
    img[pm] = lerp(img[pm], hexc("#7a6040"), 0.7)
    tufts = m & (N.fbm(3, 2, 2) > 0.66)
    img[tufts] = lerp(img[tufts], hexc("#9ab050"), 0.6)
    # foreground boughs framing the top corners
    for cx, cy, rr in ((-10, -6, 46), (250, -10, 50), (20, 150, 34), (228, 156, 30)):
        d = ((XX - cx) / rr) ** 2 + ((YY - cy) / (rr * 0.7)) ** 2
        leafy = (d < 1) & (N.fbm(4, 4, 2) > 0.3 + d * 0.35)
        img[leafy] = lerp(hexc("#16301c")[None, :], hexc("#244a2a")[None, :], (N.fbm(3, 3, 2)[leafy] > 0.55) * 1.0)
    return grounded(img, 80, lambda im: stand_spots(im, "#10200c", 0.4, top="#5a7a34", rim="#2e4a24", side=False), 22)


def marsh():
    N = Noise(12)
    img = ramp([(0, "#c8c8b0"), (0.6, "#9aa890"), (1, "#7a8a70")], YY / 72)
    trees_row(img, 10, 72, 20, 34, "#6a7866", "#768472", 3, (8, 14), trunk="#5a6456")
    fog = N.fbm(50, 8, 3)
    img[:] = lerp(img, hexc("#d8dcc8"), np.clip((fog - 0.4) * 1.2, 0, 0.5) * (YY < 90))
    m = YY > 72
    water = ramp([(0, "#4a5a48"), (0.5, "#3a4a3a"), (1, "#2a3a2c")], (YY - 72) / 88)
    rip = np.sin(XX / 3 + N.fbm(20, 3, 2) * 10) * (N.fbm(40, 4, 2) > 0.5)
    water = water + rip[..., None] * 6
    img[m] = water[m]
    # reflected sky streaks
    st = m & ((YY.astype(int) % 5) == 0) & (N.fbm(24, 2, 2) > 0.58)
    img[st] = lerp(img[st], hexc("#a8b4a0"), 0.5)
    # mud banks and lily pads
    bank = (N.fbm(40, 14, 4) + (YY - 72) / 180) > 0.62
    bm = m & bank
    img[bm] = ramp([(0, "#4a4030"), (1, "#6a5a3c")], N.fbm(5, 3, 2))[bm]
    r = np.random.default_rng(5)
    for k in range(18):
        x, y = r.uniform(0, W), r.uniform(84, 158)
        rx = r.uniform(3, 6) * (0.6 + (y - 72) / 90)
        d = ((XX - x) / rx) ** 2 + ((YY - y) / (rx * 0.45)) ** 2
        lp = (d < 1) & ~((XX > x) & (abs(YY - y) < 0.8))
        img[lp] = hexc("#5a8040") if k % 3 else hexc("#6a9048")
    # reeds
    for k in range(60):
        x = r.uniform(0, W)
        yb = r.choice([r.uniform(76, 90), r.uniform(140, 162)])
        h = r.uniform(10, 26) * (0.6 + (yb - 72) / 90)
        lean = r.uniform(-0.2, 0.2)
        m2 = (abs(XX - x - (yb - YY) * lean) < 0.8) & (YY < yb) & (YY > yb - h)
        img[m2] = hexc("#6a7a3a" if k % 2 else "#8a8a48")
        m3 = (abs(XX - x - h * lean) < 1.4) & (abs(YY - (yb - h + 3)) < 3)
        if k % 3 == 0:
            img[m3] = hexc("#5a3a20")
    return grounded(img, 72, lambda im: stand_spots(im, "#1a2418", 0.35, top="#5a5038", rim="#3a3426", side=False), 22)


def cliffs():
    N = Noise(13)
    img = ramp([(0, "#7aa8d8"), (0.7, "#b8d0e0"), (1, "#e0d8c8")], YY / 80)
    cl = N.fbm(60, 12, 4)
    img[:] = lerp(img, hexc("#f4f4f0"), np.clip((cl - 0.52) * 3, 0, 0.8) * (YY < 60))
    far = 44 + N.line(40) * 26
    m = YY >= far[None, :]
    img[m] = lerp(hexc("#8a90a8")[None, :], hexc("#a8acbc")[None, :], (N.fbm(10, 30, 3)[m] > 0.5) * 0.6)
    mid = 58 + N.line(26, 5) * 34
    m = YY >= mid[None, :]
    strata = ((YY + N.fbm(30, 6, 2) * 8) % 9) < 1.4
    rock = ramp([(0, "#5a5048"), (0.5, "#8a7a68"), (1, "#b0a088")], N.fbm(8, 14, 4))
    img[m] = rock[m]
    img[m & strata] = lerp(img[m & strata], hexc("#403830"), 0.6)
    # plateau top: dry grass and scree
    top = 92 + N.line(80, 2) * 6
    m = YY >= top[None, :]
    g = ramp([(0, "#7a6a48"), (0.5, "#9a8a58"), (1, "#b8a468")], N.fbm(12, 5, 4) * 0.8 + (YY - 92) / 300)
    img[m] = g[m]
    sc = m & (N.fbm(3, 2, 2) > 0.7)
    img[sc] = lerp(img[sc], hexc("#6a6258"), 0.7)
    grass = m & (N.fbm(2, 5, 2) > 0.62)
    img[grass] = lerp(img[grass], hexc("#8a9a50"), 0.6)
    # boulders
    r = np.random.default_rng(7)
    for k in range(9):
        x, y = r.uniform(0, W), r.uniform(100, 158)
        s = r.uniform(4, 11) * (0.5 + (y - 92) / 70)
        d = ((XX - x) / s) ** 2 + ((YY - y) / (s * 0.7)) ** 2
        b = d < 1
        lit = (XX - x) / s * -0.5 + (y - YY) / s
        img[b] = ramp([(0, "#4a4038"), (0.5, "#7a6e60"), (1, "#a89a88")], (lit[b] + 1) / 2)
    return grounded(img, 92, lambda im: stand_spots(im, "#2a2018", 0.35, top="#a8966a", rim="#6a5a44", side=False), 22)


def ruins():
    N = Noise(14)
    img = ramp([(0, "#3a2a48"), (0.4, "#a0506a"), (0.75, "#e0905a"), (1, "#f0c078")], YY / 84)
    far = 70 + N.line(50) * 12
    img[YY >= far[None, :]] = hexc("#5a3a4a")
    # broken colonnade and walls in silhouette
    r = np.random.default_rng(9)
    for k in range(8):
        x = 10 + k * 30 + r.uniform(-6, 6)
        h = r.uniform(20, 48)
        m = (abs(XX - x) < 4) & (YY > 84 - h) & (YY < 86)
        brk = (YY < 84 - h + 4) & (XX > x + (r.uniform(-2, 2)))
        img[m & ~brk] = hexc("#3a2436")
        cap = (abs(XX - x) < 6) & (abs(YY - (84 - h)) < 1.5)
        if k % 3:
            img[cap & ~brk] = hexc("#3a2436")
    # tents with banners
    for x, s in ((40, 14), (206, 18)):
        m = (YY > 88 - s) & (YY < 90) & (abs(XX - x) < (YY - (88 - s)) * 0.9)
        img[m] = hexc("#6a5040")
        img[m & (XX > x)] = hexc("#8a6a50")
        pole = (abs(XX - x) < 0.8) & (YY > 88 - s - 10) & (YY < 88 - s)
        img[pole] = hexc("#2a1a18")
        fl = (XX > x) & (XX < x + 9) & (YY > 88 - s - 10) & (YY < 88 - s - 10 + 5 - (XX - x) * 0.3)
        img[fl] = hexc("#a02a2a")
    m = YY > 86
    g = ramp([(0, "#5a4038"), (0.5, "#7a5a44"), (1, "#9a7858")], N.fbm(14, 6, 4) * 0.7 + (YY - 86) / 250)
    img[m] = g[m]
    # flagstones
    fx = (XX + (YY // 7) * 9) % 18
    stones = m & ((fx < 1.0) | ((YY % 7) < 0.8)) & (N.fbm(20, 10, 2) > 0.58)
    img[stones] = lerp(img[stones], hexc("#3a2a24"), 0.35)
    rub = m & (N.fbm(3, 2, 2) > 0.7)
    img[rub] = lerp(img[rub], hexc("#8a7a70"), 0.6)
    # warm rim light
    img[:] = lerp(img, hexc("#ffb060"), np.clip(1 - np.abs(YY - 86) / 12, 0, 1) * 0.18)
    return grounded(img, 86, lambda im: stand_spots(im, "#1a1010", 0.4, top="#8a6a50", rim="#4a3430", side=False), 22)


def road():
    N = Noise(15)
    img = ramp([(0, "#2a2a40"), (0.5, "#5a5070"), (0.9, "#a88a90"), (1, "#c8a090")], YY / 78)
    moon = ((XX - 180) ** 2 + (YY - 26) ** 2) < 64
    img[moon] = hexc("#f0e8d8")
    img[:] = lerp(img, hexc("#e0d0c8"), np.clip(1 - np.sqrt((XX - 180) ** 2 + (YY - 26) ** 2) / 40, 0, 1) * 0.25)
    hill = 68 + N.line(60) * 16
    img[YY >= hill[None, :]] = hexc("#3a3448")
    # dead trees
    r = np.random.default_rng(4)
    for k in range(7):
        x, yb, h = r.uniform(0, W), r.uniform(74, 84), r.uniform(16, 34)
        m = (abs(XX - x - np.sin((yb - YY) / 6) * 1.5) < 1.2 + (yb - YY < 6)) & (YY > yb - h) & (YY < yb)
        img[m] = hexc("#1e1a24")
        for j in range(3):
            by, d = yb - h * (0.5 + j * 0.18), (1 if j % 2 else -1)
            m = (abs(YY - by + (XX - x) * d * 0.6) < 0.8) & ((XX - x) * d > 0) & ((XX - x) * d < h * 0.3)
            img[m] = hexc("#1e1a24")
    m = YY > 80
    g = ramp([(0, "#3a3a34"), (1, "#5a584a")], N.fbm(16, 6, 4) * 0.8 + (YY - 80) / 300)
    img[m] = g[m]
    # cobbled road curving into the distance
    cx = 120 + np.sin((YY - 80) / 30) * 20
    half = 8 + (YY - 80) * 0.9
    rm = m & (abs(XX - cx) < half)
    cob = ramp([(0, "#5a5450"), (1, "#8a8278")], N.fbm(3, 2, 2))
    img[rm] = cob[rm]
    joints = rm & ((((XX + (YY // 5) * 3) % 7) < 1) | ((YY % 5) < 1))
    img[joints] = lerp(img[joints], hexc("#2a2826"), 0.5)
    edge = m & (abs(abs(XX - cx) - half) < 1.2)
    img[edge] = hexc("#2a2826")
    grass = m & ~rm & (N.fbm(2, 5, 2) > 0.6)
    img[grass] = lerp(img[grass], hexc("#6a6a48"), 0.6)
    return grounded(img, 80, lambda im: stand_spots(im, "#101014", 0.4, top="#6a6450", rim="#3a3830", side=False), 22)


def crypt():
    N = Noise(16)
    img = ramp([(0, "#141218"), (1, "#2a2630")], YY / 90)
    # back wall of stone blocks
    m = YY < 88
    bx = (XX + (YY // 12) % 2 * 10) % 20
    blocks = ramp([(0, "#2a2630"), (1, "#3e3844")], N.fbm(10, 8, 3))
    img[m] = blocks[m]
    mort = m & ((bx < 1) | ((YY % 12) < 1))
    img[mort] = hexc("#18161c")
    # arched alcoves with skulls
    for x in (40, 120, 200):
        a = ((XX - x) / 14) ** 2 + ((YY - 50) / 20) ** 2 < 1
        a |= (abs(XX - x) < 14) & (YY > 50) & (YY < 76)
        img[a & m] = hexc("#0c0a10")
        sk = ((XX - x) ** 2 + ((YY - 66) * 1.3) ** 2) < 20
        img[sk] = hexc("#b8b0a0")
        for dx in (-2, 2):
            img[((XX - x - dx) ** 2 + (YY - 65) ** 2) < 1.6] = hexc("#1a1618")
    # candle glow
    for x, y in ((80, 70), (160, 70), (12, 80), (228, 80)):
        glow = np.clip(1 - np.sqrt((XX - x) ** 2 + ((YY - y) * 1.2) ** 2) / 48, 0, 1)
        img[:] = lerp(img, hexc("#e0a050"), glow ** 2 * 0.5)
        c = (abs(XX - x) < 2) & (YY > y) & (YY < y + 8)
        img[c] = hexc("#d8d0b8")
        f = ((XX - x) ** 2 + ((YY - y + 2) * 0.6) ** 2) < 3
        img[f] = hexc("#fff0a0")
    m = YY >= 88
    fl = ramp([(0, "#201c24"), (1, "#3a3440")], N.fbm(12, 5, 3) * 0.6 + (YY - 88) / 150)
    img[m] = fl[m]
    tiles = m & ((((XX - 120) / (1 + (YY - 88) / 30)) % 16 < 0.8) | (((YY - 88) ** 0.8) % 7 < 0.8))
    img[tiles] = lerp(img[tiles], hexc("#100e14"), 0.6)
    bones = m & (N.fbm(3, 2, 2) > 0.74)
    img[bones] = lerp(img[bones], hexc("#9a9282"), 0.5)
    img[:] = img * (1 - np.clip(((XX - 120) / 150) ** 2 + ((YY - 80) / 110) ** 2 - 0.3, 0, 0.6))[..., None]
    return grounded(img, 88, lambda im: stand_spots(im, "#000000", 0.45, top="#3a3440", rim="#1a161e", side=False), 20)


def sephirot():
    N = Noise(17)
    img = ramp([(0, "#0a0620"), (0.6, "#221450"), (1, "#3a2070")], YY / 160)
    neb = N.fbm(50, 30, 5)
    img[:] = lerp(img, hexc("#6a3a9a"), np.clip((neb - 0.45) * 2, 0, 0.6))
    neb2 = N.fbm(40, 40, 4)
    img[:] = lerp(img, hexc("#2a6a9a"), np.clip((neb2 - 0.55) * 2, 0, 0.4))
    r = np.random.default_rng(8)
    for k in range(140):
        x, y = int(r.uniform(0, W)), int(r.uniform(0, H))
        img[y, x] = hexc("#ffffff") if k % 4 else hexc("#c8d8ff")
    # tree of life: glowing paths between spheres
    nodes = [(120, 8), (150, 22), (90, 22), (150, 44), (90, 44), (120, 56), (150, 70), (90, 70), (120, 82)]
    edges = [(0, 1), (0, 2), (1, 2), (1, 3), (2, 4), (3, 4), (3, 5), (4, 5), (5, 6), (5, 7), (6, 7), (6, 8), (7, 8),
             (1, 5), (2, 5), (0, 5)]
    for a, b in edges:
        (x0, y0), (x1, y1) = nodes[a], nodes[b]
        L = math.hypot(x1 - x0, y1 - y0)
        t = np.clip(((XX - x0) * (x1 - x0) + (YY - y0) * (y1 - y0)) / L ** 2, 0, 1)
        d = np.hypot(XX - x0 - t * (x1 - x0), YY - y0 - t * (y1 - y0))
        img[:] = lerp(img, hexc("#b8a0ff"), np.clip(1 - d / 2.5, 0, 1) * 0.45)
    for x, y in nodes:
        d = np.hypot(XX - x, YY - y)
        img[:] = lerp(img, hexc("#e8d8ff"), np.clip(1 - d / 9, 0, 1) ** 2)
    # floating platforms under each monster
    for cx, cy, rx, ry in (FOE, PLAYER):
        top = (((XX - cx) / (rx + 6)) ** 2 + ((YY - cy) / (ry + 2)) ** 2) < 1
        under = (abs(XX - cx) < (rx + 6) * (1 - (YY - cy) / (ry * 3.4))) & (YY > cy) & (YY < cy + ry * 3.4)
        img[under] = ramp([(0, "#4a3a6a"), (1, "#1a1030")], (YY - cy) / (ry * 3.4))[under]
        img[top] = ramp([(0, "#8a7ac0"), (1, "#c8b8f0")], (1 - np.abs(XX - cx) / (rx + 6)))[top]
        ring = np.abs((((XX - cx) / (rx + 3)) ** 2 + ((YY - cy) / (ry + 0.6)) ** 2) - 1) < 0.12
        img[ring] = hexc("#fff4c0")
    return finish(img, 24)


def palace():
    N = Noise(18)
    img = ramp([(0, "#f4ecd8"), (0.5, "#e0d0a8"), (1, "#c8b080")], YY / 100)
    # vaulted ceiling light
    img[:] = lerp(img, hexc("#fffaf0"), np.clip(1 - np.hypot(XX - 120, YY * 1.4) / 90, 0, 1) * 0.6)
    # pillars in perspective
    for x in (14, 58, 182, 226):
        w = 9 if x in (14, 226) else 6
        m = (abs(XX - x) < w) & (YY < 100)
        shade = (XX - x) / w
        img[m] = ramp([(0, "#fff8e8"), (0.5, "#e8dcc0"), (1, "#a8946a")], (shade[m] + 1) / 2)
        flute = m & ((np.abs(XX - x) % 3) < 0.6)
        img[flute] = lerp(img[flute], hexc("#b8a478"), 0.4)
        for yc in (6, 94):
            cap = (abs(XX - x) < w + 3) & (abs(YY - yc) < 3)
            img[cap] = hexc("#d8c088")
            img[cap & (YY < yc - 1)] = hexc("#f8ecc8")
    # gold throne dais
    m = (abs(XX - 120) < 30) & (YY > 62) & (YY < 86)
    img[m] = ramp([(0, "#a07a2a"), (1, "#e0b850")], 1 - (YY[m] - 62) / 24)[..., :] if False else img[m]
    for s in range(3):
        st = (abs(XX - 120) < 40 - s * 6) & (abs(YY - (96 - s * 5)) < 2.5)
        img[st] = hexc(["#c8a868", "#d8bc80", "#e8d098"][s])
    m = YY >= 98
    fl = ramp([(0, "#e8dcc0"), (1, "#b8a078")], (YY - 98) / 62)
    img[m] = fl[m]
    chk = m & (((((XX - 120) / (1 + (YY - 98) / 20)) // 8) + ((YY - 98) ** 0.75 // 3)) % 2 == 0)
    img[chk] = lerp(img[chk], hexc("#8a7050"), 0.25)
    carpet = m & (abs(XX - 120) < 12 + (YY - 98) * 0.5)
    img[carpet] = ramp([(0, "#7a1a2a"), (1, "#a82a3a")], N.fbm(4, 4, 2))[carpet]
    trim = m & (abs(abs(XX - 120) - (12 + (YY - 98) * 0.5)) < 1.2)
    img[trim] = hexc("#e0b850")
    return grounded(img, 98, lambda im: stand_spots(im, "#5a4020", 0.3, top="#e8dcc0", rim="#a88a60", side=False), 24)


def indoor():
    N = Noise(19)
    img = np.zeros((H, W, 3), np.float32)
    m = YY < 84
    plank = (XX // 16)
    grain = N.fbm(3, 30, 3)
    img[m] = ramp([(0, "#4a2e1c"), (0.5, "#6a4428"), (1, "#8a5a34")], grain * 0.8 + (plank % 3) * 0.08)[m]
    img[m & ((XX % 16) < 1)] = hexc("#2a1a10")
    # beam, window, shelf
    beam = (YY > 8) & (YY < 16)
    img[beam] = hexc("#3a2414")
    img[beam & (YY < 10)] = hexc("#5a3a22")
    win = (abs(XX - 160) < 18) & (YY > 24) & (YY < 58)
    img[win] = ramp([(0, "#c8e0f0"), (1, "#f0f4e0")], (YY - 24) / 34)[win]
    frame = win & ((abs(XX - 160) < 1) | (abs(YY - 41) < 1) | (abs(abs(XX - 160) - 17) < 1.5) |
                   (abs(YY - 25) < 1.5) | (abs(YY - 57) < 1.5))
    img[frame] = hexc("#3a2414")
    img[:] = lerp(img, hexc("#fff0c0"), np.clip(1 - np.hypot(XX - 150, (YY - 90) * 0.8) / 90, 0, 1) * 0.3)
    shelf = (abs(XX - 60) < 26) & (abs(YY - 44) < 1.5)
    img[shelf] = hexc("#3a2414")
    for k, col in enumerate(("#8a2a2a", "#2a5a8a", "#6a8a3a", "#c8a040", "#5a3a6a")):
        b = (abs(XX - 42 - k * 6) < 2.2) & (YY > 34 - (k % 2) * 2) & (YY < 43)
        img[b] = hexc(col)
    jar = ((XX - 76) ** 2 + ((YY - 39) * 1.2) ** 2) < 20
    img[jar] = hexc("#a88a6a")
    m = YY >= 84
    fl = ramp([(0, "#5a3a22"), (1, "#8a6038")], N.fbm(40, 2, 3) * 0.6 + (YY - 84) / 160)
    img[m] = fl[m]
    boards = m & ((((YY - 84) ** 0.8) % 6) < 0.8)
    img[boards] = lerp(img[boards], hexc("#2a1a10"), 0.5)
    rug = (((XX - 120) / 100) ** 2 + ((YY - 122) / 30) ** 2) < 1
    img[rug] = ramp([(0, "#6a2a24"), (1, "#8a3a2a")], N.fbm(3, 3, 2))[rug]
    border = rug & ((((XX - 120) / 100) ** 2 + ((YY - 122) / 30) ** 2) > 0.8)
    img[border] = hexc("#c89a40")
    return grounded(img, 84, lambda im: stand_spots(im, "#1a0e08", 0.35, top="#8a6038", rim="#4a2e1c", side=False), 22)


SCENES = {"forest": forest, "marsh": marsh, "cliffs": cliffs, "ruins": ruins, "road": road, "crypt": crypt,
          "sephirot": sephirot, "palace": palace, "indoor": indoor}


def build(preview=None):
    out = CANON / "bg"
    out.mkdir(exist_ok=True)
    ims = {}
    for n, fn in SCENES.items():
        ims[n] = fn()
        ims[n].save(assert_write(out / f"{n}.png"))
    if preview:
        sheet = Image.new("RGB", (W * 3 * 2, H * 3 * 2))
        for i, (n, im) in enumerate(ims.items()):
            sheet.paste(im.resize((W * 2, H * 2), Image.NEAREST), ((i % 3) * W * 2, (i // 3) * H * 2))
        sheet.save(preview)
    return list(ims)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview")
    a = ap.parse_args()
    print("bg:", " ".join(build(a.preview)))
