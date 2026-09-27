"""Spirits, bells, cards, fae, plants, stonework and the odd beasts."""
from __future__ import annotations

import math

from .core import M, Mat, Canvas, crop_frames, flame, peye, mix, hx, sparkle
from .registry import register
from .mon_quads import sparks, static_zaps
from .mon_water import ICE, ICE_DARK
from . import quad as Q
from . import bird as B


def mon(sid):
    def deco(fn):
        def make():
            return crop_frames([fn(t).render() for t in range(4)])
        register("monsters", sid)(make)
        return fn
    return deco


GHOST_OUT = Mat(["#2a1a4a", "#4a2a7a", "#7a4ab8", "#a07ae0", "#c8b0f6", "#ece0ff"], emit=True)
GHOST_IN = Mat(["#7a4ab8", "#a07ae0", "#c8b0f6", "#ece6ff", "#ffffff"], emit=True)
IRON = M("#4a4650", spec=0.6)
PRISM = ["#d63a3a", "#f2c230", "#3fa34d", "#3a6fd6", "#8a4fd0"]


def ghost_face(c, x, y, s=1.0, mouth=True, col=(30, 14, 50)):
    def ink(cc):
        for dx in (-4 * s, 3 * s):
            for k in range(int(3 * s) + 1):
                cc.put(x + dx, y + k, col)
                cc.put(x + dx + 1, y + k, col)
        if mouth:
            for k in range(3):
                cc.put(x - 1 + k, y + 5 * s + (k == 1), col)
    c.ink(ink)


# ------------------------------------------------------------------ ghost lights
@mon("tallowisp")
def tallowisp(t):
    c = Canvas(128, 128, seed=81)
    bob = [0, -2, -3, -1][t]
    x, y = 64, 84 + bob
    # a teardrop of ghostfire: round glowing body, licking tongues above
    flame(c, x, y - 2, 56, 22, t, outer=GHOST_OUT, inner=GHOST_IN, tongues=5, z=-4)
    c.ell(x, y, 22, 20, GHOST_OUT, z=4)
    c.ell(x - 3, y + 2, 14, 13, GHOST_IN, z=16)
    ghost_face(c, x - 2, y - 4, s=1.2)
    # it gutters: a few flecks break off and drift down
    wax = M("#e8e0cc", spec=0.4)
    for k, dx in enumerate((-10, 8)):
        c.cap(x + dx, y + 20 + k * 3 + t, 1.8, x + dx, y + 23 + k * 3 + t, 1.2, wax, z=4)
    sparks((200, 170, 255), 5, seed=81)(c, {}, t, None)
    return c


@mon("cryptlamp")
def cryptlamp(t):
    c = Canvas(128, 128, seed=82)
    sw = [0, 1, 2, 1][t]
    x, y = 64 + sw * 0.5, 70
    glass = Mat(["#2a2438", "#4a4260", "#6a6288", "#9a92b8", "#cfc8e6"], spec=0.9, soft=0.6)
    # chain
    for k in range(5):
        c.ell(x - sw * (5 - k) * 0.1, 6 + k * 6, 2, 3, IRON, z=0)
    c.poly([(x - 16, y - 26), (x + 16, y - 26), (x + 10, y - 36), (x - 10, y - 36)], IRON, z=4, bevel=2)
    c.ell(x, y - 38, 5, 4, IRON, z=6)
    c.poly([(x - 14, y - 26), (x + 14, y - 26), (x + 14, y + 22), (x - 14, y + 22)], glass, z=0, bevel=3)
    flame(c, x, y + 16, 34, 9, t, z=6, outer=GHOST_OUT, inner=GHOST_IN, tongues=4)
    for bx_ in (x - 14, x, x + 14):
        c.cap(bx_, y - 26, 2, bx_, y + 22, 2, IRON, z=16)
    c.poly([(x - 18, y + 22), (x + 18, y + 22), (x + 12, y + 32), (x - 12, y + 32)], IRON, z=18, bevel=2)
    ghost_face(c, x - 1, y - 2, s=0.9)
    sparks((200, 170, 255), 3, seed=82)(c, {}, t, None)
    return c


def bell(c, x, y, w, h, mat, z=0, lip=True, g=None):
    g = g or c.group()
    pts = []
    for k in range(13):
        f = k / 12
        yy = y - h + f * h
        ww = w * (0.45 + 0.55 * f ** 1.8)
        pts.append((x - ww, yy))
    for k in range(13):
        f = 1 - k / 12
        yy = y - h + f * h
        ww = w * (0.45 + 0.55 * f ** 1.8)
        pts.append((x + ww, yy))
    c.ell(x, y - h, w * 0.45, h * 0.18, mat, z=z, g=g)
    c.poly(pts, mat, z=z, bevel=max(3, w * 0.5), th=w * 0.6, g=g)
    if lip:
        c.cap(x - w * 1.02, y, 2.4, x + w * 1.02, y, 2.4, mat, z=z + w * 0.6, g=g)
    return g


@mon("deathknell")
def deathknell(t):
    c = Canvas(128, 128, seed=83)
    swing = [-6, 0, 6, 0][t]
    black = M("#2a2430", spec=0.7)
    x, y = 64 + swing * 0.3, 92
    # yoke + chain
    c.cap(x - 26, 22, 3, x + 26, 22, 3, M("#4a3a30", tex="grain", tex_amp=0.6), z=-4)
    c.cap(x, 22, 2, x + swing * 0.2, 36, 2, IRON, z=0)
    g = bell(c, x + swing * 0.3, y, 30, 56, black, z=0)
    c.ell(x + swing * 0.6, y + 4, 5, 5, IRON, z=30)      # clapper
    # skull face etched
    # a bone skull set into the bronze, eye sockets burning red
    fx_, fy_ = x + swing * 0.3 - 1, y - 30
    bone = M("#d8d0bc", spec=0.3)
    c.ell(fx_, fy_, 11, 10, bone, decal=True, only=g)
    c.ell(fx_, fy_ + 9, 7, 4, bone, decal=True, only=g)
    sock = Mat(["#300808", "#601010", "#a01818", "#e03020", "#ff8060"], emit=True)
    glow = [2.4, 2.8, 3.2, 2.8][t]
    c.ell(fx_ - 4.5, fy_ + 1, glow, glow * 1.1, sock, decal=True, only=g)
    c.ell(fx_ + 4.5, fy_ + 1, glow, glow * 1.1, sock, decal=True, only=g)

    def teeth(cc):
        cc.put(fx_, fy_ + 5, (40, 20, 24))
        for k in range(-4, 5, 2):
            cc.put(fx_ + k, fy_ + 9, (60, 50, 50))
    c.ink(teeth)

    def rings(cc):
        n = [1, 2, 3, 2][t]
        for r in range(n):
            R = 40 + r * 8
            for k in range(60):
                ang = math.radians(-150 + k * 2)
                px, py = x + math.cos(ang) * R, y - 20 + math.sin(ang) * R * 0.8
                if 0 <= px < cc.w and 0 <= py < cc.h and not cc.alpha[int(py), int(px)] and k % 3:
                    cc.put(px, py, (160, 120, 200))
    c.fx(rings)
    return c


@mon("snowbell")
def snowbell(t):
    c = Canvas(128, 128, seed=84)
    swing = [-4, 0, 4, 0][t]
    x, y = 64, 96
    bx = x + swing * 0.4
    SNOW = M("#f4f8ff", spec=0.3)
    RIB = M("#c83a4a", spec=0.3)
    # hanging loop and a snow drift on the crown
    c.ell(bx, 44, 6, 6, ICE_DARK, z=-2, th=2)
    bell(c, bx, y, 24, 46, ICE, z=0)
    c.ell(bx - 3, 53, 12, 5, SNOW, z=14)
    c.ell(bx + 6, 52, 7, 4, SNOW, z=15)
    # ribbon bow round the shoulder
    c.cap(bx - 11, 60, 2.0, bx + 11, 60, 2.0, RIB, z=18)
    c.tri((bx + 8, 60), (bx + 15, 55), (bx + 15, 65), RIB, z=20, bevel=1)
    c.tri((bx + 8, 60), (bx + 1, 55), (bx + 1, 65), RIB, z=20, bevel=1)
    c.ell(bx + 8, 60, 2.2, 2.2, RIB, z=22)
    c.cap(bx + 9, 62, 1.2, bx + 12 + swing * 0.3, 70, 1.0, RIB, z=19)
    # icicles off the lip and a swinging clapper
    for k in range(6):
        ix = bx - 18 + k * 7.2
        L = 4 + (k * 5) % 4
        c.tri((ix - 1.6, y + 1), (ix, y + 1 + L), (ix + 1.6, y + 1), ICE_DARK if k % 2 else ICE, z=26, bevel=0.6)
    c.ell(x + swing * 1.2, y + 5, 4, 4, ICE_DARK, z=24)
    c.ink(lambda cc: [peye(cc, bx - 8, y - 24, 3.0, 3.4, iris=(60, 120, 200), pw=0.7, ph=0.7),
                      peye(cc, bx + 6, y - 24, 3.0, 3.4, iris=(60, 120, 200), pw=0.7, ph=0.7),
                      [cc.put(bx - 13 + k, y - 18, (240, 170, 190)) for k in range(3)],
                      [cc.put(bx + 10 + k, y - 18, (240, 170, 190)) for k in range(3)],
                      [cc.put(bx - 2 + k, y - 16 + (k in (0, 4)) * -1, (40, 70, 120)) for k in range(5)],
                      [cc.put(bx + dx, y - 6 + dy, (230, 244, 255)) for dx, dy in
                       ((-12, 0), (-14, 0), (-10, 0), (-12, -2), (-12, 2), (-13, -1), (-11, 1), (-13, 1), (-11, -1))]])

    def snow(cc):
        for i in range(10):
            px = 14 + (i * 37 + t * 5) % 100
            py = 10 + (i * 23 + t * 6) % 110
            if not cc.alpha[int(py), int(px)]:
                sparkle(cc, px, py, (220, 240, 255), 1 if i % 3 == 0 else 0)
    c.fx(snow)
    return c


@mon("icecantor")
def icecantor(t):
    c = Canvas(128, 128, seed=85)
    x, y = 64, 100
    bell(c, x, y, 28, 62, ICE, z=0)
    # an icicle fringe hanging off the lip, and a frost crown on top
    for k in range(9):
        ix = x - 26 + k * 6.5
        L = 5 + (k * 7) % 5
        c.tri((ix - 2, y + 1), (ix, y + 1 + L), (ix + 2, y + 1), ICE_DARK if k % 2 else ICE, z=40, bevel=0.8)
    for k in range(5):
        cx_ = x - 10 + k * 5
        c.tri((cx_ - 2, y - 62), (cx_, y - 70 - (k % 2) * 4), (cx_ + 2, y - 62), ICE, z=20, bevel=0.8)
    # singing mouth, open wider each frame
    op = [3, 5, 7, 5][t]
    mouth = Mat(["#10203a", "#1a2e50", "#28406a", "#3a5a8a", "#4a6aa0"], soft=0.4)
    c.ell(x - 2, y - 22, 6, op, mouth, z=30, th=1)
    c.ink(lambda cc: [peye(cc, x - 12, y - 42, 3.4, 3.0, iris=(80, 150, 230), pw=0.6, ph=0.6),
                      peye(cc, x + 8, y - 42, 3.4, 3.0, iris=(80, 150, 230), pw=0.6, ph=0.6)])

    def notes(cc):
        # the one high note, drawn as frost shards flying out and a crack
        for i in range(3):
            nx, ny = x - 30 - i * 10 - t * 2, y - 40 - i * 6
            for dy in range(5):
                cc.put(nx + 3, ny + dy, (230, 246, 255))
            cc.put(nx, ny + 4, (230, 246, 255)); cc.put(nx + 1, ny + 4, (230, 246, 255))
            cc.put(nx + 1, ny + 5, (230, 246, 255)); cc.put(nx + 2, ny + 5, (230, 246, 255))
            cc.put(nx + 4, ny, (230, 246, 255)); cc.put(nx + 5, ny + 1, (230, 246, 255))
        for k in range(14):
            cc.put(x + 14 + (k % 3), y - 50 + k * 2, (40, 80, 140))
    c.fx(notes)
    return c


@mon("frostchoir")
def frostchoir(t):
    """A crown of ice with a choir of bells hanging from it; the big one leads the song."""
    c = Canvas(128, 128, seed=86)
    cx = 64
    glow = Mat(["#6a9ad0", "#a0ccf2", "#d0ecff", "#f0faff", "#ffffff"], emit=True)
    bob = [0, -1, -2, -1][t]
    ry = 24 + bob
    # the crown: a ring of upward icicles, back half first
    ring = []
    for k in range(10):
        ang = math.radians(k * 36 + t * 9)
        ring.append((math.sin(ang), ang, k))
    for depth, ang, k in sorted(ring):
        x = cx + math.cos(ang) * 34
        y = ry + math.sin(ang) * 7
        hgt = 14 if k % 2 == 0 else 9
        c.tri((x - 3.5, y), (x, y - hgt), (x + 3.5, y), ICE if depth > -0.3 else ICE_DARK, z=depth * 40, bevel=1.5)
    c.ell(cx, ry + 1, 36, 7, ICE_DARK, z=-30, th=0.5)
    c.cap(cx - 36, ry + 1, 2.6, cx + 36, ry + 1, 2.6, ICE, z=41)
    # the hanging choir: four small bells on ice threads, swinging out of step
    for k, (dx, L, s_) in enumerate(((-28, 30, 0.8), (-14, 44, 0.9), (14, 44, 0.9), (28, 30, 0.8))):
        sw = [-3, 0, 3, 0][(t + k) % 4]
        x0, y0 = cx + dx, ry + 3
        x1, y1 = x0 + sw, y0 + L
        c.cap(x0, y0, 0.8, x1, y1 - 18 * s_, 0.8, ICE_DARK, z=20)
        bell(c, x1, y1, 9 * s_, 18 * s_, ICE, z=24 + k)
        c.ell(x1 + sw * 0.4, y1 + 2, 2.2, 2.2, glow, z=36)
        op = [1, 2, 3, 2][(t + k) % 4]
        c.ink(lambda cc, x=x1, y=y1 - 9 * s_, op=op: [cc.put(x - 3, y - 2, (30, 60, 110)), cc.put(x + 2, y - 2, (30, 60, 110)),
                                                       [cc.put(x - 1 + i, y + 2 + j, (30, 50, 90)) for i in range(2) for j in range(op)]])
    # the lead bell in the middle, singing
    sw = [-2, 0, 2, 0][t]
    x1, y1 = cx + sw, ry + 72
    c.cap(cx, ry + 3, 1.2, x1, y1 - 44, 1.2, ICE_DARK, z=30)
    bell(c, x1, y1, 18, 40, ICE, z=40)
    c.ell(x1 + sw, y1 + 4, 3.6, 3.6, glow, z=66)
    op = [3, 5, 7, 5][t]
    mouth = Mat(["#10203a", "#1a2e50", "#28406a", "#3a5a8a", "#4a6aa0"], soft=0.4)
    c.ell(x1 - 2, y1 - 12, 4, op * 0.8, mouth, z=62, th=1)
    c.ink(lambda cc: [peye(cc, x1 - 7, y1 - 24, 2.6, 3.0, iris=(60, 120, 200), pw=0.7, ph=0.7),
                      peye(cc, x1 + 4, y1 - 24, 2.6, 3.0, iris=(60, 120, 200), pw=0.7, ph=0.7)])

    def notes(cc):
        for i in range(3):
            px = 100 + i * 7 - ((t + i) % 4) * 2
            py = 70 - i * 12 - ((t + i) % 4) * 3
            for j in range(5):
                cc.put(px + 2, py - j, (200, 236, 255))
            cc.put(px, py, (200, 236, 255)); cc.put(px + 1, py, (200, 236, 255)); cc.put(px, py + 1, (200, 236, 255))
            cc.put(px + 3, py - 4, (200, 236, 255))
    c.fx(notes)
    sparks((220, 246, 255), 8, seed=86)(c, {}, t, None)
    return c


# ------------------------------------------------------------------ runes, lights, cards
def rune_glyph(cc, x, y, kind, col):
    shapes = {
        0: [(0, -4), (0, -3), (0, -2), (0, -1), (0, 0), (0, 1), (0, 2), (0, 3), (1, -3), (2, -2), (1, -1), (-1, 1), (-2, 2)],
        1: [(-2, -3), (-1, -2), (0, -1), (1, 0), (2, 1), (2, -3), (1, -2), (-1, 0), (-2, 1), (0, 2), (0, 3)],
        2: [(-2, -2), (-1, -2), (0, -2), (1, -2), (2, -2), (0, -1), (0, 0), (0, 1), (-1, 2), (1, 2), (-2, 3), (2, 3)],
        3: [(0, -3), (-1, -2), (1, -2), (-2, -1), (2, -1), (-1, 0), (1, 0), (0, 1), (0, 2), (0, 3)],
    }
    for dx, dy in shapes[kind % 4]:
        cc.put(x + dx, y + dy, col)


@mon("runemote")
def runemote(t):
    c = Canvas(128, 128, seed=87)
    bob = [0, -2, -3, -1][t]
    x, y = 64, 60 + bob
    stone = M("#b0a490", tex="grain", tex_amp=0.9)
    moss = M("#6a8a40", tex="fur", tex_amp=0.6)
    glowc = [hx(p) for p in PRISM]
    hue = glowc[(t + 3) % 5]
    rune = Mat([mix(hue, (0, 0, 0), 0.5), hue, mix(hue, (255, 255, 255), 0.35), mix(hue, (255, 255, 255), 0.7),
                (255, 255, 255)], emit=True)
    # a chip of ruin wall, drifting and slowly turning
    tilt = [0, 2, 4, 2][t]
    pts = [(x - 20, y - 8 + tilt * 0.3), (x - 6, y - 22), (x + 16, y - 16), (x + 22, y + 4), (x + 6, y + 20),
           (x - 18, y + 14 - tilt * 0.3)]
    c.poly(pts, stone, z=0, bevel=5, th=9)
    c.ell(x + 10, y - 16, 9, 4, moss, z=10, tuft=8, tuft_len=1.5)
    # the carved word, glowing through the stone
    for (x0, y0, x1, y1) in ((x - 2, y - 12, x - 2, y + 10), (x - 2, y - 8, x + 8, y - 2), (x - 2, y + 1, x - 10, y + 7),
                             (x + 8, y - 2, x + 8, y + 8)):
        c.cap(x0, y0, 1.6, x1, y1, 1.6, rune, z=10)

    def ink(cc):
        peye(cc, x - 11, y - 8, 2.4, 2.8, iris=hue, pw=0.7, ph=0.7)
        peye(cc, x + 14, y - 8, 2.4, 2.8, iris=hue, pw=0.7, ph=0.7)
    c.ink(ink)

    def hum(cc):
        for k in range(48):
            ang = math.radians(k * 7.5 + t * 22)
            px, py = x + math.cos(ang) * 32, y + math.sin(ang) * 26
            if k % 4 < 2 and not cc.alpha[int(py), int(px)]:
                cc.put(px, py, glowc[(k // 4) % 5])
        for k in range(3):
            sparkle(cc, x - 30 + k * 30, y - 34 + (k + t) % 3 * 3, hue, 1 if k == t % 3 else 0)
    c.fx(hum)
    return c


def orb(c, x, y, r, col, z=0):
    cc = hx(col)
    m = Mat([mix(cc, (0, 0, 0), 0.4), cc, mix(cc, (255, 255, 255), 0.35), mix(cc, (255, 255, 255), 0.7), (255, 255, 255)],
            emit=True)
    c.ell(x, y, r, r, m, z=z)


def star(c, x, y, r, col, z=0, rot=0, pts=5, inner=0.45):
    cc = hx(col)
    m = Mat([mix(cc, (0, 0, 0), 0.35), cc, mix(cc, (255, 255, 255), 0.35), mix(cc, (255, 255, 255), 0.7), (255, 255, 255)],
            emit=True)
    P = []
    for k in range(pts * 2):
        ang = math.radians(rot - 90 + k * 180 / pts)
        rr = r if k % 2 == 0 else r * inner
        P.append((x + math.cos(ang) * rr, y + math.sin(ang) * rr))
    c.poly(P, m, z=z, bevel=r * 0.35)


@mon("twinklet")
def twinklet(t):
    c = Canvas(128, 128, seed=88)
    pos = []
    for k, (col, ph) in enumerate((("#f2c230", 0), ("#9a60e0", math.pi))):
        ang = t * math.pi / 4 + ph
        x = 64 + math.cos(ang) * 22
        y = 62 + math.sin(ang) * 9
        zz = 10 + math.sin(ang) * 8
        pos.append((x, y, col, zz))
        for j in range(1, 5):
            a2 = ang - j * 0.28
            orb(c, 64 + math.cos(a2) * 22, 62 + math.sin(a2) * 9, 4.5 - j, col, z=zz - j * 2)
        # a soft star with a round face in the middle; the two spin opposite ways
        star(c, x, y, 17, col, z=zz, rot=(t * 9 if k == 0 else -t * 9))
        orb(c, x, y, 8, col, z=zz + 6)
    # the thread of light that ties them together
    def thread(cc):
        (x0, y0, *_), (x1, y1, *_) = pos
        for j in range(1, 30):
            f = j / 30
            x = x0 + (x1 - x0) * f
            y = y0 + (y1 - y0) * f + math.sin(f * math.pi) * 6
            if not cc.alpha[int(y), int(x)] and (j + t) % 3:
                cc.put(x, y, (255, 246, 220))
    c.fx(thread)
    for x, y, col, zz in pos:
        c.ink(lambda cc, x=x, y=y: [peye(cc, x - 3, y - 1, 1.6, 2.2, iris=(40, 20, 50), pw=0.9, ph=0.9, glint=True),
                                    peye(cc, x + 3, y - 1, 1.6, 2.2, iris=(40, 20, 50), pw=0.9, ph=0.9, glint=True),
                                    cc.put(x, y + 3, (120, 60, 80))])
    sparks((255, 250, 220), 8, seed=88)(c, {}, t, None)
    return c


def wisp_body(c, x, y, h, col, z=0, lean=0, t=0):
    """A small humanoid spirit: head, tapering tail instead of legs, arms."""
    cc = hx(col)
    m = Mat([mix(cc, (20, 10, 40), 0.55), mix(cc, (20, 10, 40), 0.25), cc, mix(cc, (255, 255, 255), 0.35),
             mix(cc, (255, 255, 255), 0.7)], spec=0.2)
    wag = [0, 2, 3, 1][t]
    c.chain([(x, y, h * 0.2), (x + lean * 4 + wag, y + h * 0.35, h * 0.12), (x + lean * 8 - wag, y + h * 0.65, 1.0)], m,
            z=z)
    c.ell(x, y - h * 0.12, h * 0.2, h * 0.24, m, z=z + 4)
    c.ell(x, y - h * 0.42, h * 0.2, h * 0.2, m, z=z + 6)
    return m


@mon("geminal")
def geminal(t):
    c = Canvas(128, 128, seed=89)
    bob = [0, -2, -3, -1][t]
    # each spirit wears the star it grew from, spinning behind its head
    star(c, 40, 22 + bob, 13, "#f2c230", z=-20, rot=t * 9)
    star(c, 88, 22 - bob, 13, "#9a60e0", z=-20, rot=-t * 9)
    warm = wisp_body(c, 44, 70 + bob, 70, "#f2a040", z=0, lean=-1, t=t)
    cool = wisp_body(c, 84, 70 - bob, 70, "#6a9af0", z=0, lean=1, t=(t + 2) % 4)
    # joined hands
    c.cap(50, 64 + bob, 3.5, 64, 70, 3, warm, z=20)
    c.cap(78, 64 - bob, 3.5, 64, 70, 3, cool, z=20)
    orb(c, 64, 70, 5, "#ffffff", z=26)
    # free arms gesturing at each other (arguing)
    c.cap(38, 64 + bob, 3, 30, 52 + bob - t, 2.2, warm, z=12)
    c.cap(90, 64 - bob, 3, 100, 50 - bob + t, 2.2, cool, z=12)

    def faces(cc):
        for x, y, iris, ang in ((44, 40 + bob, (160, 60, 20), 0.9), (84, 40 - bob, (30, 50, 140), 0.9)):
            peye(cc, x - 5, y, 2.2, 2.8, iris=iris, pw=0.8, ph=0.8, angry=ang)
            peye(cc, x + 4, y, 2.2, 2.8, iris=iris, pw=0.8, ph=0.8, angry=ang)
            for k in range(4):
                cc.put(x - 2 + k, y + 8 - (k in (0, 3)), (60, 30, 40))
    c.ink(faces)
    sparks((255, 240, 220), 4, seed=89)(c, {}, t, None)
    return c


def star_poly(x, y, r1, r2, n=5, rot=-90):
    pts = []
    for k in range(n * 2):
        r = r1 if k % 2 == 0 else r2
        a = math.radians(rot + k * 180 / n)
        pts.append((x + math.cos(a) * r, y + math.sin(a) * r))
    return pts


@mon("stardrop")
def stardrop(t):
    c = Canvas(128, 128, seed=90)
    G = 120
    bob = [0, 1, 2, 1][t]
    rock = M("#4a4a6a", tex="grain", tex_amp=0.9, spec=0.3)
    glowm = Mat(["#8a90e0", "#b9c4ff", "#dfe4ff", "#f6f8ff", "#ffffff"], emit=True)
    x, y = 64, G - 34 + bob
    for side, zz in ((1, -6), (-1, 20)):
        for k, dx in enumerate((-10, 8)):
            c.chain([(x + dx + side * 2, y + 14, 3.4), (x + dx - 3 + side * 2, y + 24, 2.8), (x + dx - 2 + side * 2, G - 1, 2.6)],
                    rock, z=zz)
    c.poly(star_poly(x, y, 30, 15, rot=-100 + t * 2), rock, z=0, bevel=7, th=10)
    # glowing cracks
    c.pattern(lambda xx, yy: ((abs((xx - x) * 0.8 + (yy - y) * 0.3) < 1.2) | (abs((yy - y) - (xx - x) * 0.9 + 4) < 1.0))
              & (((xx - x) ** 2 + (yy - y) ** 2) < 300), 0, where=[rock])
    c.ell(x - 1, y + 6, 3 + (t % 2), 2, glowm, z=4, decal=True)
    c.ink(lambda cc: [peye(cc, x - 6, y - 4, 2.6, 3.0, iris=(40, 40, 120), pw=0.8, ph=0.8, angry=0.5),
                      peye(cc, x + 5, y - 4, 2.6, 3.0, iris=(40, 40, 120), pw=0.8, ph=0.8, angry=0.5)])
    sparks((230, 236, 255), 5, seed=90)(c, {}, t, None)
    return c


@mon("charmkin")
def charmkin(t):
    c = Canvas(96, 96, seed=91)
    bob = [0, -2, -3, -1][t]
    x, y = 48, 52 + bob
    skin = M("#f2c8a8")
    dress = M("#3fa34d", spec=0.2)
    hair = M("#f2c230", tex="fur", tex_amp=0.5)
    wingm = Mat(["#6a8ac0", "#9ac0f0", "#d0e8ff", "#f4faff", "#ffffff"], soft=0.4, spec=0.6)
    fl = [0, 1, 2, 1][t]
    for k, (ang, L) in enumerate(((-60, 26), (-20, 20))):
        a = math.radians(ang - fl * 12)
        c.ell(x + 10 + math.cos(a) * L * 0.5, y - 6 + math.sin(a) * L * 0.5, L * 0.5, L * 0.22, wingm, z=-10,
              rot=ang - fl * 12, th=1)
    c.poly([(x - 9, y + 16), (x - 4, y), (x + 4, y), (x + 9, y + 16)], dress, z=0, bevel=2)
    c.cap(x - 3, y + 16, 1.6, x - 4, y + 24, 1.2, skin, z=2)
    c.cap(x + 3, y + 16, 1.6, x + 4, y + 24, 1.2, skin, z=2)
    c.ell(x, y - 8, 10, 10, skin, z=6)
    c.ell(x + 2, y - 14, 11, 7, hair, z=8, tuft=8, tuft_len=2)
    c.cap(x + 8, y - 12, 4, x + 12, y + 2, 2, hair, z=4)
    # holding a shiny coin bigger than its head
    coin = M("#f2c230", spec=0.9)
    c.cap(x - 4, y + 2, 1.6, x - 12, y - 2, 1.4, skin, z=20)
    c.ell(x - 16, y - 4, 7, 7, coin, z=22, th=2)
    for k, (ang, L) in enumerate(((-150, 26), (170, 20))):
        a = math.radians(ang + fl * 12)
        c.ell(x - 6 + math.cos(a) * L * 0.5, y - 6 + math.sin(a) * L * 0.5, L * 0.5, L * 0.22, wingm, z=30,
              rot=ang + fl * 12, th=1)
    c.ink(lambda cc: [peye(cc, x - 4, y - 8, 1.8, 2.4, iris=(60, 140, 60), pw=0.8, ph=0.8),
                      peye(cc, x + 3, y - 8, 1.8, 2.4, iris=(60, 140, 60), pw=0.8, ph=0.8),
                      cc.put(x - 1, y - 3, (200, 90, 90)), cc.put(x, y - 3, (200, 90, 90)),
                      rune_glyph(cc, x - 16, y - 4, 3, (200, 150, 40))])
    sparks((255, 240, 180), 5, seed=91, spread=(4, 92, 4, 90))(c, {}, t, None)
    return c


PAPER = Mat(["#6c6a78", "#b8b4c0", "#e2dee6", "#f6f4f8", "#ffffff"], soft=0.5)


def card(c, x, y, w, h, rot, z, suit_col, suit=0, back=False, g=None):
    ca, sa = math.cos(math.radians(rot)), math.sin(math.radians(rot))

    def P(u, v):
        return (x + u * ca - v * sa, y + u * sa + v * ca)
    pts = [P(-w, -h), P(w, -h), P(w, h), P(-w, h)]
    m = PAPER if not back else Mat(["#3a1a4a", "#5a2a7a", "#8a4fd0", "#b08ae6", "#e0d0ff"], soft=0.5)
    c.poly(pts, m, z=z, bevel=1, g=g)
    col = hx(suit_col)

    def ink(cc):
        if back and w > 8:
            for u in range(-int(w) + 2, int(w) - 1):
                for v in range(-int(h) + 2, int(h) - 1):
                    if (u + v) % 6 == 0 or (u - v) % 6 == 0:
                        cc.put(*P(u, v), (200, 170, 240))
        if back:
            for k in range(-2, 3):
                cc.put(*P(k, k), (240, 220, 255))
                cc.put(*P(k, -k), (240, 220, 255))
            return
        shp = [[(0, -2), (-1, -1), (1, -1), (-2, 0), (2, 0), (-1, 1), (1, 1), (0, 2), (0, 0), (-1, 0), (1, 0), (0, -1), (0, 1)],
               [(-1, -1), (1, -1), (-2, 0), (0, 0), (2, 0), (-1, 1), (0, 1), (1, 1), (0, 2), (-1, 0), (1, 0)]][suit % 2]
        for dx, dy in shp:
            cc.put(*P(dx, dy), col)
        cc.put(*P(-w + 2, -h + 2), col)
        cc.put(*P(w - 2, h - 2), col)
    c.ink(ink)


@mon("cardkin")
def cardkin(t):
    """A playing card on cartoon legs that flips itself over as it idles."""
    c = Canvas(112, 112, seed=92)
    G = 108
    bob = [0, -1, -2, -1][t]
    sq = [1.0, 0.45, 1.0, 0.45][t]           # card width as it turns edge-on
    back = t == 2
    limb = M("#2a2430")
    glove = M("#f6f4f0", spec=0.3)
    shoe = M("#c02a3a", spec=0.6)
    x, y = 56, 56 + bob
    w, h = 20 * sq, 28
    # legs and shoes
    for d in (-1, 1):
        c.cap(x + d * 7, y + h - 2, 2.0, x + d * 9, G - 4, 1.6, limb, z=0)
        c.ell(x + d * 10 - 2, G - 2, 5, 2.6, shoe, z=2)
    # arms: one on the hip, one waving a tiny card
    wave = [0, -3, -5, -3][t]
    c.chain([(x - w + 1, y - 2, 1.8), (x - w - 10, y - 10 + wave, 1.6), (x - w - 14, y - 22 + wave, 1.4)], limb, z=-2)
    c.ell(x - w - 14, y - 24 + wave, 3.2, 3.2, glove, z=0)
    card(c, x - w - 16, y - 32 + wave, 4, 6, -20 + wave * 2, 1, "#d63a3a", 1)
    c.chain([(x + w - 1, y + 2, 1.8), (x + w + 8, y + 8, 1.6), (x + w + 3, y + 14, 1.4)], limb, z=-2)
    c.ell(x + w + 3, y + 15, 3.2, 3.2, glove, z=0)
    # the card: gold rim, big pip, corner marks
    gold = M("#e0b840", spec=0.8)
    c.poly([(x - w - 2, y - h - 2), (x + w + 2, y - h - 2), (x + w + 2, y + h + 2), (x - w - 2, y + h + 2)], gold, z=4,
           bevel=1.5)
    card(c, x, y, w, h, 0, 8, "#d63a3a", 0, back=back)
    red = M("#d63a3a", spec=0.5)
    if not back and sq > 0.9:
        # a large heart made of two lobes and a point
        c.ell(x - 4, y + 8, 5.5, 5.5, red, z=12)
        c.ell(x + 4, y + 8, 5.5, 5.5, red, z=12)
        c.tri((x - 9.5, y + 10), (x, y + 21), (x + 9.5, y + 10), red, z=12, bevel=2)

        def face(cc):
            peye(cc, x - 6, y - 12, 2.6, 3.4, iris=(40, 60, 160), pw=0.8, ph=0.8)
            peye(cc, x + 6, y - 12, 2.6, 3.4, iris=(40, 60, 160), pw=0.8, ph=0.8)
            for k in range(7):
                cc.put(x - 3 + k, y - 4 + (1 if 1 <= k <= 5 else 0), (60, 30, 40))
            for dx, dy in ((0, 0), (0, 1), (0, 2), (1, 0), (1, 2), (2, 0), (2, 1), (2, 2)):
                cc.put(x - w + 3 + dx, y - h + 3 + dy, (200, 40, 50))
                cc.put(x + w - 5 + dx, y + h - 5 + dy, (200, 40, 50))
        c.ink(face)
    sparks((255, 240, 200), 5, seed=92, spread=(4, 108, 4, 100))(c, {}, t, None)
    return c


@mon("fateweaver")
def fateweaver(t):
    c = Canvas(128, 128, seed=93)
    cx, cy = 64, 62
    eye_m = Mat(["#3a1a4a", "#5a2a7a", "#8a4fd0", "#c8a0f6", "#f0e6ff"], emit=True)
    rot = t * 11
    cards = []
    for k in range(10):
        a = math.radians(rot + k * 36)
        cards.append((math.sin(a), a, k))
    for depth, a, k in sorted(cards):
        x = cx + math.cos(a) * 40
        y = cy + math.sin(a) * 14
        card(c, x, y, 7, 10, math.degrees(a) * 0.3, depth * 20, PRISM[k % 5], k, back=depth < -0.2)
    c.ell(cx, cy, 16, 16, eye_m, z=0)
    c.ink(lambda cc: [peye(cc, cx, cy, 9, 7, iris=(240, 200, 60), pw=0.3, ph=0.9, slit=True),
                      [cc.put(cx - 18 + k, cy + 22 + (k % 5 == 0), (120, 80, 170)) for k in range(0)]])
    # threads of fate
    def threads(cc):
        for k in range(3):
            for j in range(40):
                f = j / 40
                px = cx - 30 + f * 60
                py = cy + 30 + math.sin(f * 6 + t + k * 2) * 4 + k * 3
                if not cc.alpha[int(py), int(px)]:
                    cc.put(px, py, hx(PRISM[(k * 2) % 5]))
    c.fx(threads)
    return c


@mon("arcanox")
def arcanox(t):
    def extras(c, a, t, m):
        # floating cards and symbols orbiting the beast
        rot = t * 12
        for k in range(6):
            ang = math.radians(rot + k * 60)
            x = a["bx"] + math.cos(ang) * 52
            y = a["by"] - 30 + math.sin(ang) * 14
            card(c, x, y, 5, 7, math.degrees(ang) * 0.2, 60 * math.sin(ang), PRISM[k % 5], k, back=(k % 2 == 1))
        glyphs = [hx(p) for p in PRISM]

        # a third eye on the brow that opens as it reads you
        op = [0.6, 1.2, 1.8, 1.2][t]

        def ink(cc):
            peye(cc, a["hx"] + 1, a["hy"] - a["hry"] * 0.55, 2.4, op, iris=glyphs[1], pw=0.5, ph=0.9, slit=True)
            # a single band of runes glowing along the flank
            for k in range(3):
                rune_glyph(cc, a["bx"] - 10 + k * 11, a["by"] - 4, k + t, glyphs[(k + t) % 5])
        c.ink(ink)
    spec = dict(seed=94, body=(56, 28), leg=26, leg_r=5.2, head=(16, 14), neck=6, fur="#5a3a8a", belly="#b09ae0",
                eye="#f2c230", slit=True, angry=0.7, ears="fox", ear_size=1.2, tail="long", tail_len=1.1,
                tail_tip="tuft", accent="#f2c230", feet="claw", mane="shag", shag_col="#3a2a6a", extras=[extras])
    return Q.build(spec, t)


@mon("glyphwing")
def glyphwing(t):
    glyphs = [hx(p) for p in PRISM]

    def extras(c, a, t, m):
        def ink(cc):
            import numpy as np
            ys, xs = np.nonzero(cc.alpha)
            for k in range(0, len(xs), 97):
                x, y = xs[k], ys[k]
                if (x + y + t) % 3 == 0:
                    cc.put(x, y, glyphs[(x + t) % 5])
        c.ink(ink)
    spec = dict(seed=95, pose="fly", body=(18, 13), head=(11, 10), beak=7, beak_w=3, hook=True, body_col="#6a4ab0",
                belly="#c8b0f0", wing_col="#8a5ad0", wing_tip="#f2c230", beak_col="#f2c230", leg_col="#f2c230",
                eye="#3fe0a0", tail=22, tail_n=5, feathers=7, span=1.2, crest="crest", extras=[extras])
    return B.build(spec, t)


@mon("motley")
def motley(t):
    c = Canvas(128, 128, seed=96)
    G = 121
    bob = [0, -3, -5, -2][t]
    x, y = 64, 78 + bob
    skin = M("#e8d8c8")
    cols = [M(p, spec=0.2) for p in PRISM]
    # legs, curly shoes
    for k, (dx, zz) in enumerate(((8, -4), (-6, 10))):
        c.cap(x + dx, y + 16, 3.4, x + dx - 2, G - 4, 2.8, cols[k * 2], z=zz)
        c.cap(x + dx - 2, G - 3, 3, x + dx - 12, G - 6, 1.5, cols[4 - k], z=zz + 2)
    g = c.group()
    c.ell(x, y + 4, 16, 18, cols[3], z=0, g=g)
    # harlequin diamonds
    c.pattern(lambda xx, yy: ((abs((xx - x) % 10 - 5) + abs((yy - y) % 10 - 5)) < 4), 0, only=g)
    for k in range(4):
        dx, dy = (-6, -4), (6, 6)
    c.ell(x - 6, y - 2, 6, 6, cols[0], decal=True, only=g)
    c.ell(x + 7, y + 10, 6, 6, cols[1], decal=True, only=g)
    c.ell(x - 5, y + 14, 5, 5, cols[2], decal=True, only=g)
    # ruff collar
    c.ell(x, y - 12, 15, 5, M("#f6f2ea"), z=10, tuft=14, tuft_len=2)
    # arms: one waving
    c.cap(x - 14, y - 6, 3.2, x - 26, y - 18 - bob, 2.4, cols[1], z=12)
    c.ell(x - 27, y - 20 - bob, 3.4, 3.4, skin, z=14)
    c.cap(x + 14, y - 4, 3.2, x + 22, y + 10, 2.4, cols[0], z=12)
    # head + jester hat
    c.ell(x, y - 24, 13, 12, skin, z=12)
    for k, (tx_, ty_, col) in enumerate(((x - 26, y - 34 - bob, 0), (x + 2, y - 52, 2), (x + 26, y - 38 + bob, 4))):
        c.chain([(x - 8 + k * 8, y - 30, 5), ((x - 8 + k * 8 + tx_) / 2, y - 44 + (k == 1) * -4, 3.5), (tx_, ty_, 2)],
                cols[col], z=14 + k)
        c.ell(tx_, ty_ + 2, 3, 3, M("#f2c230", spec=0.9), z=20)
    c.cap(x - 12, y - 32, 2, x + 12, y - 32, 2, M("#f6f2ea"), z=24)

    def face(cc):
        peye(cc, x - 5, y - 26, 2.2, 3.0, iris=(40, 160, 60), pw=0.8, ph=0.8, angry=-0.5)
        peye(cc, x + 5, y - 26, 2.2, 3.0, iris=(40, 160, 60), pw=0.8, ph=0.8, angry=-0.5)
        for k in range(11):
            yy = y - 18 + (0 if k in (0, 10) else 1 if k in (1, 9) else 2)
            cc.put(x - 5 + k, yy, (120, 30, 40))
        for k in range(2, 9):
            cc.put(x - 5 + k, y - 17 + (0 if k in (2, 8) else 1), (255, 255, 255))
        # diamond face paint
        for dx, dy in ((0, -1), (-1, 0), (1, 0), (0, 1), (0, 0)):
            cc.put(x - 8 + dx, y - 21 + dy, (214, 58, 58))
    c.ink(face)
    return c


@mon("baphorn")
def baphorn(t):
    c = Canvas(128, 128, seed=97)
    G = 122
    bob = [0, 1, 2, 1][t]
    fur = M("#2e2834", tex="fur", tex_amp=0.6)
    belly = M("#54485e", tex="fur", tex_amp=0.4)
    horn = M("#c8b8a8", spec=0.4)
    hoof = M("#15101a", n=5)
    wax = M("#e8dcc0", spec=0.3)
    x, y = 70, 70 + bob
    # tail + far arm
    c.cap(x + 16, y + 20, 3, x + 28, y + 12, 1.6, fur, z=-12)
    c.chain([(x + 14, y - 8, 6), (x + 22, y + 8, 5), (x + 24, y + 24, 4.2)], fur, z=-8)
    # digitigrade goat legs
    for k, (dx, zz) in enumerate(((8, -6), (-8, 10))):
        c.chain([(x + dx, y + 20, 9), (x + dx + 7, y + 34, 6.5), (x + dx - 1, y + 43, 4.4), (x + dx, G - 5, 3.8)],
                fur, z=zz)
        c.cap(x + dx, G - 6, 4, x + dx - 1, G - 1, 4.6, hoof, z=zz + 2)
    # torso: broad chest, shaggy
    g = c.group()
    # broad shaggy shoulders over a narrow waist, so it reads as upright
    c.ell(x, y + 18, 13, 12, fur, z=0, g=g)
    c.ell(x - 2, y - 2, 22, 15, fur, z=2, g=g)
    c.ell(x - 4, y - 10, 20, 9, fur, z=6, g=g, tuft=18, tuft_len=4, tuft_arc=(160, 380))
    c.ell(x - 7, y + 6, 10, 12, belly, decal=True, only=g)
    c.pattern(lambda xx, yy: (abs(xx - x + 7) < 8) & ((yy - y) % 6 < 1) & (yy > y), -1, only=g)   # rib ridges
    # a ragged loincloth
    c.poly([(x - 12, y + 22), (x + 12, y + 22), (x + 8, y + 36), (x + 2, y + 32), (x - 4, y + 38), (x - 10, y + 32)],
           M("#5a1a24", tex="grain", tex_amp=0.6), z=40, bevel=1.5)
    # near arm raised, holding a candle up
    c.chain([(x - 16, y - 6, 6.5), (x - 26, y + 6, 5), (x - 32, y - 8 - bob, 4.4)], fur, z=16)
    c.ell(x - 32, y - 10 - bob, 5, 4, fur, z=18)
    c.cap(x - 33, y - 12 - bob, 3, x - 33, y - 26 - bob, 3, wax, z=20)
    flame(c, x - 33, y - 26 - bob, 14, 3.4, t, z=22)
    # head: long goat skull turned left, beard, ram horns
    hx_, hy_ = x - 10, y - 26
    hg = c.group()
    c.ell(hx_, hy_, 12, 11, fur, z=12, g=hg, tuft=10, tuft_len=2, tuft_arc=(180, 360))
    c.cap(hx_ - 2, hy_ + 2, 8, hx_ - 16, hy_ + 10, 5, fur, z=16, g=hg)
    c.ell(hx_ - 16, hy_ + 10, 4.5, 4, belly, z=20, g=hg)
    c.chain([(hx_ - 10, hy_ + 12, 3), (hx_ - 11, hy_ + 18, 2), (hx_ - 12, hy_ + 22, 0.8)], belly, z=18)   # beard
    # ears
    c.ell(hx_ + 10, hy_ - 1, 7, 3, fur, z=8, rot=20)
    c.ell(hx_ - 8, hy_ - 4, 6, 2.6, fur, z=22, rot=-20)
    # ram horns curling back and around
    for k, (cx, cy, zz, sc) in enumerate(((hx_ + 8, hy_ - 10, 6, 0.85), (hx_ + 1, hy_ - 9, 24, 1.0))):
        R = 16 * sc
        pts = []
        for i in range(10):
            ang = math.radians(-150 + i * 40)
            rr = R * (1 - i * 0.07)
            pts.append((cx + math.cos(ang) * rr + R * 0.4, cy + math.sin(ang) * rr + R * 0.35, R * 0.36 * (1 - i * 0.07)))
        c.chain(pts, horn, z=zz)
        c.pattern(lambda xx, yy, cx=cx, cy=cy, R=R: ((((xx - cx - R * 0.4) ** 2 + (yy - cy - R * 0.35) ** 2) ** 0.5) % 3 < 1)
                  & ((xx - cx - R * 0.4) ** 2 + (yy - cy - R * 0.35) ** 2 < (R * 1.3) ** 2), -1, where=[horn])

    def face(cc):
        peye(cc, hx_ - 5, hy_ - 1, 2.8, 2.4, iris=(255, 50, 40), pw=0.25, ph=0.9, slit=True, angry=0.9)
        cc.put(hx_ - 20, hy_ + 9, (15, 10, 20))
        cc.put(hx_ - 19, hy_ + 9, (15, 10, 20))
        for k in range(7):
            cc.put(hx_ - 19 + k, hy_ + 13 + (k > 4), (20, 12, 20))
    c.ink(face)
    # candles lighting themselves around its hooves
    for k, cx_ in enumerate((24, 108)):
        c.cap(cx_, G, 2.8, cx_, G - 11 - k * 3, 2.8, wax, z=40)
        flame(c, cx_, G - 11 - k * 3, 10, 2.6, (t + k) % 4, z=42)
    return c


# ------------------------------------------------------------------ plants
LEAF = M("#4aa048", spec=0.2)
LEAF_D = M("#2f7a3a")
BARK = M("#7a5a3a", tex="grain", tex_amp=0.9)
VINE = M("#4a8a3a", tex="grain", tex_amp=0.5)


def leaf(c, x, y, L, ang, z=0, m=None):
    a = math.radians(ang)
    ex, ey = x + math.cos(a) * L, y + math.sin(a) * L
    c.ell((x + ex) / 2, (y + ey) / 2, L * 0.55, L * 0.26, m or LEAF, z=z, rot=ang, th=2)


@mon("pipsprout")
def pipsprout(t):
    c = Canvas(96, 96, seed=98)
    G = 92
    bob = [0, -2, -3, -1][t]
    seed_m = M("#b08a4a", spec=0.3)
    stem = M("#5aa040")
    x, y = 48, 62 + bob
    step = [(-3, 0), (0, -2), (3, 0), (0, -2)][t]
    for k, (dx, zz) in enumerate(((5, -4), (-5, 10))):
        lift = step[k] if True else 0
        c.chain([(x + dx, y + 14, 2.4), (x + dx - 1 + lift, G - 6 + (lift < 0) * -2, 2.0), (x + dx - 3 + lift, G - 1, 2.2)],
                stem, z=zz)
    g = c.group()
    c.ell(x, y, 16, 19, seed_m, z=0, g=g)
    c.pattern(lambda xx, yy: (abs(xx - x - (yy - y) * 0.2) < 1.0) & (yy < y - 4), -2, only=g)
    c.cap(x, y - 18, 2, x + 2 + bob * 0.3, y - 30, 1.6, stem, z=4)
    leaf(c, x + 2, y - 30, 14, -150 + t * 3, z=6)
    leaf(c, x + 2, y - 30, 12, -30 - t * 3, z=4, m=LEAF_D)
    c.ink(lambda cc: [peye(cc, x - 7, y - 2, 2.6, 3.2, iris=(40, 30, 20), pw=0.8, ph=0.8),
                      peye(cc, x + 5, y - 2, 2.6, 3.2, iris=(40, 30, 20), pw=0.8, ph=0.8),
                      cc.put(x - 1, y + 6, (70, 40, 30)), cc.put(x, y + 7, (70, 40, 30)), cc.put(x + 1, y + 6, (70, 40, 30))])
    return c


@mon("vinebrute")
def vinebrute(t):
    c = Canvas(128, 128, seed=99)
    G = 122
    bob = [0, 1, 2, 1][t]
    x, y = 64, 62 + bob
    THORN = M("#c8b87a", spec=0.3)
    BERRY = M("#c8283a", spec=0.7)
    # legs: thick braided trunks that splay into root toes
    for k, (dx, zz) in enumerate(((11, -6), (-11, 10))):
        for j in range(3):
            c.chain([(x + dx + j * 3 - 3, y + 18, 5), (x + dx + 4 - j * 3, y + 38, 4.6), (x + dx - 2 + j * 2, G - 4, 4.2)],
                    (VINE, LEAF_D, BARK)[j], z=zz + j)
        for j, fx in enumerate((-8, -2, 5)):
            c.cap(x + dx - 1, G - 4, 3.4, x + dx + fx, G - 1, 1.6, BARK, z=zz + 4)
    # torso: a knot of vines, broad at the shoulders
    g = c.group()
    for j in range(9):
        a_ = j * 40
        x0 = x + math.cos(math.radians(a_)) * 9
        y0 = y + math.sin(math.radians(a_)) * 10
        c.cap(x0 - 12, y0 - 10, 6.5, x0 + 12, y0 + 10, 5.5, VINE if j % 2 else LEAF_D, z=j % 3, g=g)
    c.poly([(x - 26, y - 14), (x - 10, y - 24), (x + 10, y - 24), (x + 26, y - 14), (x + 18, y + 14), (x - 18, y + 14)],
           VINE, z=2, bevel=6, th=8, g=g)
    c.pattern(lambda xx, yy: ((xx * 0.6 + yy) % 7 < 1.6), -2, only=g)
    c.pattern(lambda xx, yy: ((xx * 0.6 - yy) % 11 < 1.0) & (yy > y), -1, only=g)
    # face hollow with glowing eyes
    hol = Mat(["#0c1a0c", "#122412", "#182e18", "#1e381e", "#244224"], soft=0.4)
    c.ell(x - 1, y - 7, 11, 6, hol, z=12)
    glow = Mat(["#806010", "#c09020", "#f0c840", "#ffe890", "#fffbe0"], emit=True)
    c.ell(x - 6, y - 8, 2.6, 2.0, glow, z=40)
    c.ell(x + 4, y - 8, 2.6, 2.0, glow, z=40)
    # arms: vines coiling down to thorned club fists
    for k, (d, zz) in enumerate(((1, -4), (-1, 22))):
        sx, sy = x + d * 22, y - 12
        c.ell(sx, sy, 9, 8, LEAF_D, z=zz + 2, tuft=10, tuft_len=1.6)
        c.chain([(sx, sy + 2, 6.5), (sx + d * 10, sy + 16, 5.5), (sx + d * 9, sy + 30 + bob, 5)], VINE, z=zz)
        fx_, fy_ = sx + d * 9, sy + 36 + bob
        c.ell(fx_, fy_, 9, 8, VINE, z=zz + 4)
        c.pattern(lambda xx, yy, fx_=fx_, fy_=fy_: ((xx - fx_) ** 2 + (yy - fy_) ** 2 < 80) & (((xx + yy * 2) % 6) < 1.2), -2)
        for j in range(5):
            ang = math.radians(-60 + j * 55)
            c.tri((fx_ + math.cos(ang) * 7 - 1.4, fy_ + math.sin(ang) * 6), (fx_ + math.cos(ang) * 12, fy_ + math.sin(ang) * 10),
                  (fx_ + math.cos(ang) * 7 + 1.4, fy_ + math.sin(ang) * 6), THORN, z=zz + 6, bevel=0.6)
    # thorns and berries on the chest, leafy crest
    for j, (px, py) in enumerate(((-14, 2), (12, -2), (-4, 10), (16, 8))):
        c.tri((x + px - 1.5, y + py), (x + px + (1 if px > 0 else -1) * 3, y + py - 3), (x + px + 1.5, y + py), THORN,
              z=30, bevel=0.4)
    for px, py in ((-16, -16), (-12, -18), (14, -18), (8, 6), (11, 4)):
        c.ell(x + px, y + py, 1.8, 1.8, BERRY, z=32)
    for k in range(6):
        leaf(c, x - 9 + k * 3.6, y - 24, 10 + (k % 2) * 4, -155 + k * 26, z=8)

    def mouth(cc):
        for k in range(8):
            cc.put(x - 5 + k, y + 1 + (k % 2), (14, 30, 14))
    c.ink(mouth)
    return c


@mon("rootking")
def rootking(t):
    c = Canvas(128, 128, seed=100)
    G = 124
    bob = [0, 1, 2, 1][t]
    x, y = 64, 72 + bob
    canopy = M("#3a8a3a", tex="fur", tex_amp=0.8)
    canopy2 = M("#5aa84a", tex="fur", tex_amp=0.8)
    # root legs
    for k, (dx, zz) in enumerate(((-16, 10), (-4, -6), (10, 12), (22, -6))):
        sw = ([0, 2, 0, -2][(t + k) % 4])
        c.chain([(x + dx * 0.5, y + 22, 6), (x + dx + sw, y + 38, 4.5), (x + dx * 1.3 + sw, G - 2, 2.5)], BARK, z=zz)
    # trunk
    g = c.group()
    c.poly([(x - 14, y + 26), (x - 12, y - 16), (x + 12, y - 16), (x + 14, y + 26)], BARK, z=0, bevel=6, th=12, g=g)
    c.pattern(lambda xx, yy: ((xx - x + (yy % 9 < 4) * 2) % 5 < 1), -2, only=g)
    # branches + canopy crown
    for d in (-1, 1):
        c.chain([(x + d * 8, y - 12, 4), (x + d * 22, y - 26, 3), (x + d * 30, y - 40, 2)], BARK, z=-2)
    for k, (dx, dy, r) in enumerate(((-28, -38, 14), (0, -48, 18), (26, -40, 15), (-14, -26, 12), (16, -26, 12))):
        c.ell(x + dx, y + dy, r, r * 0.85, canopy if k % 2 else canopy2, z=-4 + k, tuft=12, tuft_len=2.5)
    # a crown grown from branches
    gold = M("#c8a040", spec=0.6)
    for k in range(5):
        px = x - 10 + k * 5
        c.tri((px - 2, y - 58), (px + 0.5, y - 66 - (k % 2) * 4), (px + 3, y - 58), gold, z=30, bevel=1)
    c.cap(x - 12, y - 58, 1.8, x + 12, y - 58, 1.8, gold, z=31)

    def face(cc):
        peye(cc, x - 6, y - 4, 2.4, 2.0, iris=(250, 220, 90), pw=0.6, ph=0.6, angry=0.3)
        peye(cc, x + 5, y - 4, 2.4, 2.0, iris=(250, 220, 90), pw=0.6, ph=0.6, angry=0.3)
        for k in range(7):
            cc.put(x - 3 + k, y + 8, (40, 24, 16))
        # birds following it
        for i, (bx_, by_) in enumerate(((104, 20), (112, 30), (20, 28))):
            bx_ += [0, 1, 2, 1][(t + i) % 4]
            wing = (t + i) % 2
            cc.put(bx_, by_, (60, 50, 50))
            cc.put(bx_ - 1, by_ - wing, (60, 50, 50))
            cc.put(bx_ + 1, by_ - wing, (60, 50, 50))
            cc.put(bx_ - 2, by_ - 1 + wing, (60, 50, 50))
            cc.put(bx_ + 2, by_ - 1 + wing, (60, 50, 50))
    c.ink(face)
    return c


# ------------------------------------------------------------------ stonework
BRICK = M("#b0603a", tex="grain", tex_amp=0.7)
MORTAR = M("#d8c8a8")
STONE = M("#9a9288", tex="grain", tex_amp=0.8)


def brick_pat(c, g, h=6, w=12):
    c.pattern(lambda x, y: ((y % h) < 1) | (((x + (((y // h) % 2) * w / 2)) % w) < 1), -2, only=g)


def stone_legs(c, x, y, G, dxs, r=4, mat=STONE, t=0):
    for k, dx in enumerate(dxs):
        lift = [0, -2, 0, 0][(t + k * 2) % 4]
        c.chain([(x + dx, y, r * 1.2), (x + dx - 2, (y + G) / 2 + lift, r), (x + dx - 1, G - 2 + lift, r)], mat,
                z=-6 if k % 2 else 10)
        c.ell(x + dx - 3, G - 2 + lift, r * 1.3, r * 0.6, mat, z=12)


MOSS = M("#5a8a3a", tex="grain", tex_amp=0.9)


def stone_arm(c, sx, sy, ex, ey, hx_, hy_, r, mat, z):
    """Shoulder boulder, blocky forearm, knuckled fist."""
    c.ell(sx, sy, r * 1.5, r * 1.3, mat, z=z + 2)
    c.chain([(sx, sy, r * 1.1), (ex, ey, r), (hx_, hy_, r * 0.95)], mat, z=z)
    c.ell(hx_, hy_ + r * 0.4, r * 1.35, r * 1.15, mat, z=z + 3)


@mon("rubblet")
def rubblet(t):
    c = Canvas(96, 96, seed=101)
    G = 92
    bob = [0, -1, -2, -1][t]
    sw = [0, 2, 0, -2][t]
    x, y = 48, 60 + bob
    stone_legs(c, x, y + 10, G, (-8, 8), r=3.6, mat=BRICK, t=t)
    # far arm behind the block
    stone_arm(c, x + 18, y - 2, x + 24, y + 6 - sw, x + 26, y + 13 - sw, 2.6, BRICK, z=-8)
    g = c.group()
    c.poly([(x - 20, y + 12), (x - 18, y - 16), (x + 18, y - 14), (x + 20, y + 13)], BRICK, z=0, bevel=4, th=8, g=g)
    brick_pat(c, g, 8, 14)
    # a chipped corner and a mossy cap
    c.pattern(lambda xx, yy: (xx > x + 11) & (yy < y - 8) & (xx - x - 11 > y - 8 - yy), -1, only=g)
    c.ell(x - 8, y - 16, 9, 3, MOSS, z=10)
    c.ell(x + 3, y - 15, 6, 2.4, MOSS, z=11)
    # loose pebbles orbiting overhead
    for k in range(3):
        px = x - 12 + k * 12
        py = y - 24 + [0, -1, -2, -1][(t + k) % 4] - (k == 1) * 3
        c.ell(px, py, 2.4, 2, STONE, z=12)
    stone_arm(c, x - 19, y - 2, x - 25, y + 4 + sw, x - 26, y + 11 + sw, 2.8, BRICK, z=16)
    c.ink(lambda cc: [peye(cc, x - 7, y - 4, 2.8, 3.0, iris=(40, 30, 20), pw=0.9, ph=0.9, angry=0.35),
                      peye(cc, x + 5, y - 4, 2.8, 3.0, iris=(40, 30, 20), pw=0.9, ph=0.9, angry=0.35),
                      [cc.put(x - 3 + k, y + 5 + (k in (0, 5)) * -1, (50, 24, 16)) for k in range(6)]])
    return c


@mon("ramparth")
def ramparth(t):
    c = Canvas(128, 128, seed=102)
    G = 122
    bob = [0, 1, 2, 1][t]
    sw = [0, 3, 0, -3][t]
    x, y = 64, 72 + bob
    stone_legs(c, x, y + 24, G, (-24, -9, 9, 24), r=6.4, t=t)
    stone_arm(c, x + 44, y - 8, x + 52, y + 6 - sw, x + 54, y + 20 - sw, 6, STONE, z=-8)
    g = c.group()
    pts = [(x - 46, y + 28), (x - 48, y - 18)]
    for k in range(5):
        x0 = x - 48 + k * 19.2
        pts += [(x0, y - 30), (x0 + 10, y - 30), (x0 + 10, y - 18), (x0 + 19.2, y - 18)]
    pts = pts[:-1] + [(x + 48, y - 30), (x + 48, y - 18), (x + 46, y + 28)]
    c.poly(pts, STONE, z=0, bevel=4, th=10, g=g)
    brick_pat(c, g, 9, 18)
    # gate mouth: dark arch with a raised portcullis
    gate = lambda xx, yy: ((xx - x) ** 2 / 110 + (yy - y - 12) ** 2 / 150 < 1) & (yy > y + 2) | \
        ((abs(xx - x) < 10.5) & (yy >= y + 12) & (yy < y + 28))
    c.pattern(gate, -4, only=g)
    teeth = [0, 2, 4, 2][t]
    c.ink(lambda cc: [[cc.put(x + dx, yy, (70, 64, 60)) for dx in (-7, -3, 1, 5) for yy in range(int(y + 2), int(y + 8 + teeth))],
                      [cc.put(x + dx, int(y + 8 + teeth), (120, 112, 100)) for dx in range(-8, 8)]])
    # moss and ivy on the wall
    c.ell(x - 30, y + 22, 10, 4, MOSS, z=8)
    c.ell(x + 34, y - 16, 8, 3, MOSS, z=8)
    c.chain([(x - 40, y - 18, 1.4), (x - 36, y - 4, 1.4), (x - 40, y + 8, 1.4)], MOSS, z=9)
    # banner pole on the rightmost merlon
    c.cap(x + 38, y - 30, 1.2, x + 38, y - 52, 1.1, IRON, z=10)
    flap = [0, 2, 1, -1][t]
    c.poly([(x + 38, y - 52), (x + 54, y - 48 + flap), (x + 38, y - 42)], M("#b03a3a"), z=11, bevel=1)
    stone_arm(c, x - 44, y - 8, x - 52, y + 4 + sw, x - 54, y + 18 + sw, 6.4, STONE, z=20)
    win = Mat(["#6a3a10", "#b06a20", "#f0a030", "#ffd070", "#fff0c0"], emit=True)
    for dx in (-16, 14):
        c.poly([(x + dx - 4, y - 2), (x + dx - 4, y - 10), (x + dx, y - 13), (x + dx + 4, y - 10), (x + dx + 4, y - 2)],
               Mat(["#141010", "#201a16", "#2a2420", "#342c26", "#3e342c"]), z=22, bevel=1)
        c.ell(x + dx, y - 6, 2.4, 2.6, win, z=24)
    c.ink(lambda cc: [cc.put(x + dx + (1 if dx < 0 else -1), int(y - 11), (40, 36, 34)) for dx in (-17, -15, 13, 15)])
    return c


@mon("towerfall")
def towerfall(t):
    c = Canvas(128, 128, seed=103)
    G = 124
    bob = [0, 1, 2, 1][t]
    lean = [0, 1, 2, 1][t]
    x, y = 64, 60 + bob
    stone_legs(c, x, y + 44, G, (-14, 14), r=6, t=t)
    g = c.group()
    c.poly([(x - 20, y + 48), (x - 18 + lean, y - 28), (x + 18 + lean, y - 28), (x + 20, y + 48)], STONE, z=0, bevel=7,
           th=16, g=g)
    brick_pat(c, g, 8, 16)
    # battlement top
    for k in range(4):
        x0 = x - 21 + lean + k * 12
        c.poly([(x0, y - 28), (x0, y - 38), (x0 + 7, y - 38), (x0 + 7, y - 28)], STONE, z=6, bevel=2)
    # conical roof, banner
    c.poly([(x - 24 + lean, y - 38), (x + lean, y - 70), (x + 24 + lean, y - 38)], M("#5a4a8a", tex="grain", tex_amp=0.4),
           z=8, bevel=4)
    c.cap(x + lean, y - 70, 1, x + lean, y - 84, 1, IRON, z=10)
    c.poly([(x + lean, y - 84), (x + lean + 14 + lean, y - 80), (x + lean, y - 76)], M("#c8b050"), z=12, bevel=1)
    # window-eyes
    win = Mat(["#6a3a10", "#b06a20", "#f0a030", "#ffd070", "#fff0c0"], emit=True)
    for dx in (-8, 8):
        c.poly([(x + dx - 3 + lean * 0.5, y - 8), (x + dx - 3 + lean * 0.5, y - 16), (x + dx + 3 + lean * 0.5, y - 16),
                (x + dx + 3 + lean * 0.5, y - 8)], win, z=20, bevel=1)
    c.ink(lambda cc: [cc.put(x + dx + lean * 0.5, y - 12, (30, 16, 10)) for dx in (-9, 7)])
    c.poly([(x - 6, y + 26), (x - 6, y + 12), (x, y + 8), (x + 6, y + 12), (x + 6, y + 26)],
           Mat(["#1a1410", "#2a2018", "#3a2c20", "#4a3828", "#5a4430"], soft=0.3), z=20, bevel=1)
    return c


@mon("eclipsaur")
def eclipsaur(t):
    def extras(c, a, t, m):
        # replace the face with a black disc ringed by corona
        hx_, hy_, r = a["hx"] - 2, a["hy"], a["hry"] * 1.25
        corona = Mat(["#6a70c0", "#9aa4f0", "#c8d0ff", "#eef0ff", "#ffffff"], emit=True)
        disc = Mat(["#050508", "#0a0a12", "#12121e", "#1a1a2a", "#24243a"], spec=0.2)
        c.ell(hx_, hy_, r + 3, r + 3, corona, z=40)
        c.ell(hx_, hy_, r, r, disc, z=46)
        # two pinprick eyes of starlight, and a thin crescent of light on the rim
        glint = [1, 1, 0, 1][t]
        c.ink(lambda cc: [cc.put(hx_ - r * 0.4, hy_ - 2, (230, 236, 255)), cc.put(hx_ + r * 0.25, hy_ - 2, (230, 236, 255)),
                          cc.put(hx_ - r * 0.4, hy_ - 1, (150, 160, 230)) if glint else None,
                          cc.put(hx_ + r * 0.25, hy_ - 1, (150, 160, 230)) if glint else None,
                          [cc.put(hx_ + math.cos(math.radians(a)) * (r - 1), hy_ + math.sin(math.radians(a)) * (r - 1),
                                  (120, 130, 200)) for a in range(120, 240, 6)]])

        def fx(cc):
            for k in range(16):
                ang = k * math.pi / 8 + t * 0.2
                L = r + 6 + (k % 2) * 4
                for d in range(int(r + 4), int(L)):
                    px, py = hx_ + math.cos(ang) * d, hy_ + math.sin(ang) * d
                    if 0 <= px < cc.w and 0 <= py < cc.h and not cc.alpha[int(py), int(px)]:
                        cc.put(px, py, (200, 210, 255))
            # stars going out: hollow dots fading
            for i, (sx, sy) in enumerate(((16, 12), (40, 6), (110, 14), (120, 40))):
                if (i + t) % 3:
                    sparkle(cc, sx, sy, (180, 190, 240), 0)
        c.fx(fx)
    spec = dict(seed=104, body=(72, 40), leg=24, leg_r=8, head=(15, 14), neck=16, fur="#2a2e4a", belly="#6a70a0",
                eye="#000000", eye_kind="none", head_type="bovine", ears="none", tail="long", tail_len=1.4, feet="claw",
                mane="shag", shag_col="#3a3e62", horns=None, tuft=True, extras=[extras],
                spots=2)
    return Q.build(spec, t)
