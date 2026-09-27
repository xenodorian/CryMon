"""Bug CryMon."""
from __future__ import annotations

import math

from .core import M, Mat, Canvas, crop_frames, peye, mix, hx, sparkle
from .bug import insect, spider, wing_mat, veins
from .registry import register
from .mon_quads import sparks, static_zaps


def mon(sid):
    def deco(fn):
        def make():
            return crop_frames([fn(t).render() for t in range(4)])
        register("monsters", sid)(make)
        return fn
    return deco


def _zaps(c, t, n=3, seed=1):
    static_zaps(n=n, seed=seed)(c, {}, t, None)


@mon("sparkfly")
def sparkfly(t):
    c = Canvas(128, 128, seed=51)
    bob = [0, -2, -3, -1][t]
    insect(c, t, cx=60, cy=60 + bob, head=7, thorax=(9, 8), abdomen=(15, 11), ab_angle=25, body="#4a4030",
           body2="#5a4c34", glow="#ffe040", wing="#e8f0ff", wing_len=28, eye="#ffe060", eye_r=3.4, legs=True)
    sparks((255, 240, 120), 5, seed=51)(c, {}, t, None)
    return c


@mon("arcwasp")
def arcwasp(t):
    c = Canvas(128, 128, seed=52)
    bob = [0, -2, -3, -1][t]
    insect(c, t, cx=56, cy=58 + bob, head=7, thorax=(10, 8), abdomen=(18, 10), ab_angle=30, body="#e8b820",
           body2="#f2c830", stripe="#2a2420", wing="#f0f8ff", wing_len=30, stinger=10, eye="#303030",
           eye_r=3.6)
    _zaps(c, t, 5, 52)
    return c


@mon("thunderqueen")
def thunderqueen(t):
    c = Canvas(128, 128, seed=53)
    bob = [0, -2, -3, -1][t]
    a = insect(c, t, cx=52, cy=56 + bob, head=9, thorax=(13, 11), abdomen=(26, 15), ab_angle=32,
               body="#e0a818", body2="#f0c028", stripe="#2a2018", wing="#fff6c8", wings=2, wing_len=42,
               stinger=12, eye="#ff5030", eye_r=4.2)
    # crown
    gold = M("#ffd850", spec=0.7)
    hx_, hy_ = a["head"]
    for k in range(4):
        x = hx_ - 7 + k * 4.5
        c.tri((x - 2, hy_ - 7), (x + 0.5, hy_ - 14 - (k % 2) * 3), (x + 3, hy_ - 7), gold, z=40, bevel=1)
    c.cap(hx_ - 8, hy_ - 7, 1.6, hx_ + 8, hy_ - 7, 1.6, gold, z=41)
    _zaps(c, t, 6, 53)
    sparks((255, 240, 150), 4, seed=53)(c, {}, t, None)
    return c


def _moth(c, t, *, cx, cy, wing, wing2, body, eye, span=1.0, pattern=None, glow=False, veil=False):
    fl = [0, 1, 2, 1][t]
    wm = wing_mat(wing, light=veil)
    w2 = wing_mat(wing2, light=veil)
    bm = M(body, tex="fur", tex_amp=0.6)
    # far wings
    for k, (L, W, ang, m) in enumerate(((44, 20, -58, wm), (30, 16, 10, w2))):
        a = math.radians(ang - fl * 10 * (1 if k == 0 else 0.5))
        L *= span
        ex, ey = cx + 4 + math.cos(a) * L, cy + math.sin(a) * L
        c.ell((cx + ex) / 2 + 8, (cy + ey) / 2, L * 0.55, W * 0.6, m, z=-12 - k, rot=math.degrees(a), th=1)
    # body
    g = c.group()
    c.ell(cx + 10, cy + 6, 13, 7, bm, z=0, rot=25, g=g)
    c.pattern(lambda x, y: ((x + y * 0.5) % 5 < 1.5), -1, only=g)
    c.ell(cx - 3, cy - 1, 8, 7, bm, z=4, tuft=12, tuft_len=2)
    c.ell(cx - 11, cy - 3, 6, 6, bm, z=6)
    # feathery antennae
    am = M(body, n=5)
    for side, zz in ((1, -2), (-1, 12)):
        c.chain([(cx - 12, cy - 8, 1.0), (cx - 16 + side * 3, cy - 18, 0.9), (cx - 22 + side * 4, cy - 22, 0.8)], am, z=zz)
    # near wings
    ga = c.group()
    for k, (L, W, ang, m) in enumerate(((46, 22, -40, wm), (32, 17, 25, w2))):
        a = math.radians(ang - fl * 12 * (1 if k == 0 else 0.5))
        L *= span
        ex, ey = cx + math.cos(a) * L, cy + math.sin(a) * L
        mx, my = (cx + ex) / 2 + 6, (cy + ey) / 2
        c.ell(mx, my, L * 0.55, W * 0.6, m, z=18 - k, rot=math.degrees(a), th=1, g=ga)
        if pattern:
            pattern(c, mx, my, L, W, ga, k)
    veins(c, cx + 4, cy - 2, cx + 30, cy - 40, mix(wing, (20, 20, 30), 0.5), n=4)

    def face(cc):
        peye(cc, cx - 13, cy - 4, 2.6, 2.8, iris=hx(eye), pw=0.8, ph=0.8)
    c.ink(face)


@mon("gravemoth")
def gravemoth(t):
    c = Canvas(128, 128, seed=54)
    bob = [0, -2, -3, -1][t]

    def pat(c, mx, my, L, W, g, k):
        dark = M("#2a2830")
        pale = M("#d8d4cc")
        if k == 0:
            # a skull-like eyespot
            c.ell(mx + 2, my + 2, 5, 5, pale, decal=True, only=g)
            c.ell(mx, my + 1, 1.5, 1.8, dark, decal=True, only=g)
            c.ell(mx + 4, my + 1, 1.5, 1.8, dark, decal=True, only=g)
        else:
            c.ell(mx + 2, my, 4, 3, dark, decal=True, only=g)
    _moth(c, t, cx=58, cy=66 + bob, wing="#8a8272", wing2="#4a4450", body="#5a5460", eye="#c02a2a", pattern=pat)
    # a dusting of pale scales drifting over the wings

    def dust(cc):
        for i in range(10):
            px = 64 + (i * 13 + t * 3) % 50
            py = 20 + (i * 7 + t * 5) % 70
            if cc.alpha[int(py), int(px)]:
                cc.put(px, py, (200, 192, 176))
    c.ink(dust)
    return c


@mon("moonveil")
def moonveil(t):
    c = Canvas(128, 128, seed=55)
    bob = [0, -2, -3, -1][t]

    def pat(c, mx, my, L, W, g, k):
        c.ell(mx + 3, my, 3.5, 3.5, Mat(["#8a90d0", "#c8ccf6", "#f0f2ff", "#ffffff", "#ffffff"], emit=True),
              z=30, th=1)
    _moth(c, t, cx=58, cy=66 + bob, wing="#c8d0f0", wing2="#aab4e6", body="#e8ecff", eye="#4a5ab0",
          span=1.1, pattern=pat, veil=True)
    sparks((230, 236, 255), 6, seed=55)(c, {}, t, None)
    return c


@mon("soottick")
def soottick(t):
    c = Canvas(128, 128, seed=56)
    G = 118
    bob = [0, 1, 2, 1][t]
    bm = M("#2a2630", tex="fur", tex_amp=0.4, spec=0.5)
    lm = M("#3a3440", n=5)
    cx, cy = 66, G - 22 + bob
    for side, zz in ((1, -8), (-1, 14)):
        for k in range(4):
            bx0 = cx - 10 + k * 7
            spread = (k - 1.5) * 9
            kx = bx0 + spread * 0.8 + side * 2
            ky = cy - 10 - (1 if (k + t) % 2 else 0)
            fx_ = bx0 + spread * 1.7 + side * 3
            c.chain([(bx0, cy + 2, 2.2), (kx, ky, 1.8), (fx_, G - (0 if side < 0 else 3), 0.9)], lm, z=zz)
    g = c.group()
    c.ell(cx + 4, cy, 22, 17, bm, z=0, g=g)
    c.pattern(lambda x, y: ((x - cx) ** 2 / 400 + (y - cy) ** 2 / 200) % 1 < 0.12, -1, only=g)
    c.ell(cx - 18, cy + 4, 8, 6, bm, z=6)
    # mouthparts
    c.cap(cx - 24, cy + 6, 2.0, cx - 30, cy + 10, 0.8, M("#8a3030"), z=12)

    def face(cc):
        peye(cc, cx - 20, cy + 1, 1.8, 2.0, iris=(255, 60, 40), pw=0.6, ph=0.6)
        # soot falling
        for i in range(4):
            cc.put(cx + 10 + i * 6 - t, cy + 22 + (i * 3 + t * 2) % 6, (60, 56, 64))
    c.ink(face)
    return c


@mon("gloomspider")
def gloomspider(t):
    c = Canvas(128, 128, seed=57)
    spider(c, t, cx=52, cy=92, body=(11, 9), abdomen=(19, 15), col="#2a2634", mark="#c8c0e0",
           leg_len=40, leg_r=2.0, eyes_col="#b0a0ff")

    def web(cc):
        col = (200, 200, 220)
        ox, oy = 100, 14
        for k in range(5):
            ang = math.radians(100 + k * 20)
            for r in range(2, 26):
                x, y = ox + math.cos(ang) * r, oy + math.sin(ang) * r
                if not cc.alpha[int(y), int(x)]:
                    cc.put(x, y, col)
        for r in (8, 14, 20):
            for k in range(40):
                ang = math.radians(100 + k * 2)
                x, y = ox + math.cos(ang) * r, oy + math.sin(ang) * r
                if not cc.alpha[int(y), int(x)]:
                    cc.put(x, y, (160, 160, 190) if (k + t) % 7 else (255, 255, 255))
    c.fx(web)
    return c


@mon("widowshade")
def widowshade(t):
    c = Canvas(128, 128, seed=58)
    spider(c, t, cx=46, cy=86, body=(14, 12), abdomen=(26, 21), col="#1e1a24", mark="#d02a3a",
           leg_len=48, leg_r=2.8, eyes_col="#ff3040")
    # silk-wrapped bundle hanging behind
    silk = M("#e6e2ea", tex="grain", tex_amp=0.8)
    sw = [0, 1, 2, 1][t]
    c.cap(110, 0, 0.6, 110 + sw * 0.5, 40, 0.6, silk, z=-40)
    c.ell(110 + sw, 50, 7, 12, silk, z=-38)
    c.pattern(lambda x, y: ((y + x * 0.4) % 4 < 1) & (x > 100), -1, where=[silk])
    return c


@mon("voltgrub")
def voltgrub(t):
    c = Canvas(128, 128, seed=59)
    G = 120
    bm = M("#d8c060", spec=0.3)
    seg_dark = M("#b09030", spec=0.3)
    wave = [0, 1, 2, 1][t]
    n = 7
    for k in range(n):
        x = 36 + k * 11
        y = G - 12 - math.sin(k * 0.9 + t * 0.8) * 2 - (4 if k == 0 else 0)
        r = 12 - abs(k - 2) * 0.9
        c.ell(x, y, r * 0.9, r, bm if k % 2 == 0 else seg_dark, z=20 - k * 2)
        if k > 0:
            for side, zz in ((1, -4), (-1, 30)):
                c.cap(x, y + r * 0.6, 1.6, x - 2, G, 1.0, M("#8a6a30", n=5), z=zz - k)
    # copper-ore chunks on its back
    cu = M("#c87a3a", spec=0.8)
    for k, (x, y) in enumerate(((58, G - 26), (80, G - 24), (100, G - 20))):
        c.poly([(x - 4, y + 3), (x - 1, y - 4), (x + 4, y - 2), (x + 3, y + 4)], cu, z=40, bevel=1)
    # mandibles
    mm = M("#6a4a2a", spec=0.5)
    c.cap(28, G - 12, 2.0, 22, G - 6, 0.8, mm, z=40)
    c.cap(30, G - 8, 2.0, 25, G - 2, 0.8, mm, z=40)

    def face(cc):
        peye(cc, 32, G - 20, 2.4, 2.6, iris=(40, 30, 20), pw=0.7, ph=0.7)
    c.ink(face)
    _zaps(c, t, 4, 59)
    return c
