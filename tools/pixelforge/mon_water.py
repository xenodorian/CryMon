"""Fish, crabs, newts, wyrms and the hill tortoise."""
from __future__ import annotations

import math

from .core import M, Mat, Canvas, crop_frames, peye, mix, hx, sparkle
from .registry import register
from .mon_quads import sparks

ICE = Mat(["#3a5a8a", "#5a8ac0", "#8ab8e6", "#c0e2fa", "#eaf8ff", "#ffffff"], spec=0.9)
ICE_DARK = Mat(["#1e3456", "#2e5282", "#4a78b0", "#78a6d8", "#b0d4f2", "#e6f6ff"], spec=0.8)


def mon(sid):
    def deco(fn):
        def make():
            return crop_frames([fn(t).render() for t in range(4)])
        register("monsters", sid)(make)
        return fn
    return deco


# ------------------------------------------------------------------ fish
def fish(c, t, *, cx=64, cy=64, L=40, H=16, body="#5a8ac0", belly="#dcecf8", fin="#8ab8e6", eye="#1a1a2a",
         teeth=False, jaw=0.0, scale_pat=True, fins=True, z=0, emit=False, spikes=0, angry=0.0, spec=0.6):
    """Side-on fish swimming left. Returns anchors."""
    bm = M(body, spec=spec) if not emit else Mat([mix(body, (0, 0, 40), 0.5), body, mix(body, (255, 255, 255), 0.3),
                                                  mix(body, (255, 255, 255), 0.6), (255, 255, 255)], emit=True)
    be = M(belly, spec=0.3)
    fm = M(fin, soft=0.6, spec=0.3)
    sw = [0, 1, 2, 1][t]
    g = c.group()
    # tail fin
    tx = cx + L * 0.5
    c.poly([(tx - 4, cy), (tx + L * 0.35, cy - H * 0.8 - sw), (tx + L * 0.25, cy), (tx + L * 0.35, cy + H * 0.8 - sw)],
           fm, z=z - 4, bevel=2)
    # body: head ellipse + tapering rear
    c.ell(cx - L * 0.12, cy, L * 0.42, H * 0.55, bm, z=z, g=g)
    c.cap(cx + L * 0.05, cy, H * 0.5, tx, cy + sw * 0.3, H * 0.18, bm, z=z, g=g)
    c.ell(cx - L * 0.1, cy + H * 0.28, L * 0.38, H * 0.25, be, g=g, decal=True, only=g)
    if scale_pat:
        c.pattern(lambda x, y: ((x + (y % 6 < 3) * 3) % 6 < 1) & ((y % 3) < 1), -1, only=g)
    if fins:
        c.poly([(cx - L * 0.1, cy - H * 0.45), (cx + L * 0.12, cy - H * 1.05 - sw * 0.5), (cx + L * 0.25, cy - H * 0.4)],
               fm, z=z - 2, bevel=1)
        c.poly([(cx - L * 0.15, cy + H * 0.2), (cx, cy + H * 0.8 + sw * 0.5), (cx + L * 0.08, cy + H * 0.25)],
               fm, z=z + 8, bevel=1)
    for k in range(spikes):
        x0 = cx - L * 0.3 + k * (L * 0.6 / max(spikes - 1, 1))
        c.tri((x0 - 2.5, cy - H * 0.45), (x0 + 1, cy - H * 0.95 - (k % 2) * 3), (x0 + 3, cy - H * 0.4), ICE, z=z + 2,
              bevel=1)
    head_x = cx - L * 0.5
    a = dict(head=(head_x, cy), tail=(tx + L * 0.3, cy))
    ec = hx(eye)

    def ink(cc):
        peye(cc, head_x + L * 0.14, cy - H * 0.12, max(2.0, H * 0.13), max(2.2, H * 0.14), iris=ec, pw=0.7, ph=0.7,
             angry=angry)
        # gill line
        for k in range(int(H * 0.5)):
            cc.put(head_x + L * 0.3 + (k % 3 == 0), cy - H * 0.2 + k, mix(body, (0, 0, 20), 0.55))
        # mouth
        for k in range(int(L * 0.12 + jaw * 6)):
            cc.put(head_x + 2 + k, cy + H * 0.12 + jaw * k * 0.3, (30, 20, 30))
        if teeth:
            for k in range(0, int(L * 0.2), 2):
                cc.put(head_x + 3 + k, cy + H * 0.12 + jaw * k * 0.3 - 1, (250, 250, 255))
                cc.put(head_x + 3 + k, cy + H * 0.12 + jaw * k * 0.3 + 1, (250, 250, 255))
    c.ink(ink)
    return a


def bubbles(c, t, x0, y0, n=3):
    def fx(cc):
        for i in range(n):
            x = x0 - i * 5 + (i % 2)
            y = y0 - i * 8 - t * 2
            for dx, dy in ((0, -1), (1, 0), (0, 1), (-1, 0)):
                cc.put(x + dx, y + dy, (200, 236, 255))
            cc.put(x - 1, y - 1, (255, 255, 255)) if False else None
    c.fx(fx)


@mon("frostfry")
def frostfry(t):
    c = Canvas(128, 128, seed=61)
    bob = [0, -1, -2, -1][t]
    fish(c, t, cx=64, cy=64 + bob, L=46, H=22, body="#7ab0e0", belly="#e6f4ff", fin="#bfe4ff", eye="#1a2a4a")
    c.pattern(lambda x, y: ((x - y) % 7 < 1), 2, where=[])
    sparks((220, 246, 255), 3, seed=61)(c, {}, t, None)
    bubbles(c, t, 34, 52)
    return c


@mon("floepike")
def floepike(t):
    c = Canvas(128, 128, seed=62)
    bob = [0, -1, -2, -1][t]
    fish(c, t, cx=60, cy=62 + bob, L=84, H=22, body="#3a70b0", belly="#d8ecf8", fin="#8ab8e6", eye="#f0f8ff",
         teeth=True, jaw=0.4, spikes=4, angry=0.7)
    return c


@mon("glacierjaw")
def glacierjaw(t):
    c = Canvas(128, 128, seed=63)
    bob = [0, -1, -2, -1][t]
    jaw = [0.8, 1.2, 1.6, 1.2][t]
    a = fish(c, t, cx=66, cy=58 + bob, L=100, H=40, body="#2a5a96", belly="#cfe6f6", fin="#6a9ad0", eye="#b0f0ff",
             teeth=True, jaw=jaw, spikes=6, angry=0.9)
    # the glacier jaw: a huge ice-plated underbite that gapes and snaps,
    # with fangs of ice standing up out of it
    hx_, hy_ = a["head"]
    gape = [2, 4, 6, 4][t]
    c.poly([(hx_ - 8, hy_ + 6 + gape), (hx_ + 26, hy_ + 10), (hx_ + 30, hy_ + 22), (hx_ + 6, hy_ + 26 + gape * 0.5),
            (hx_ - 10, hy_ + 16 + gape)], ICE, z=60, bevel=3)
    for k in range(4):
        fx_ = hx_ - 5 + k * 7
        c.tri((fx_ - 2.2, hy_ + 8 + gape - k * 0.4), (fx_ + 0.5, hy_ - 1 + gape - k * 0.4), (fx_ + 3, hy_ + 9 + gape - k * 0.4),
              M("#f4fbff", spec=0.8), z=64, bevel=1)
    # a brow plate of ice over the eye
    c.poly([(hx_ + 4, hy_ - 14), (hx_ + 26, hy_ - 18), (hx_ + 30, hy_ - 10), (hx_ + 8, hy_ - 8)], ICE, z=60, bevel=2)
    # frozen breath
    sparks((220, 246, 255), 6, seed=63, spread=(4, 30, 50, 90))(c, {}, t, None)
    return c


@mon("starfry")
def starfry(t):
    c = Canvas(128, 128, seed=64)
    bob = [0, -1, -2, -1][t]
    fish(c, t, cx=62, cy=64 + bob, L=46, H=22, body="#b8c4ff", belly="#f0f2ff", fin="#e0e6ff", eye="#2a2a6a",
         scale_pat=False, emit=False, spec=0.9)
    star = Mat(["#e0c040", "#ffe070", "#fff4b0", "#fffbe6", "#ffffff"], emit=True)
    x0, y0 = 58, 58 + bob
    pts = []
    for k in range(10):
        r = 7 if k % 2 == 0 else 3
        ang = math.radians(-90 + k * 36)
        pts.append((x0 + math.cos(ang) * r, y0 + math.sin(ang) * r))
    c.poly(pts, star, z=30, bevel=1)
    sparks((240, 240, 255), 6, seed=64)(c, {}, t, None)
    return c


@mon("starwhale")
def starwhale(t):
    c = Canvas(128, 128, seed=65)
    bob = [0, -1, -2, -1][t]
    body = M("#3a3e8a", spec=0.3)
    belly = M("#c8ccf6", spec=0.3)
    fin = M("#2e3272", spec=0.3)
    sw = [0, 2, 4, 2][t]
    cx, cy = 60, 66 + bob
    g = c.group()
    # tail flukes
    c.poly([(104, cy - 6), (124, cy - 20 - sw), (118, cy - 4), (124, cy + 10 - sw)], fin, z=-4, bevel=2)
    c.ell(cx, cy, 50, 26, body, z=0, g=g)
    c.cap(cx + 30, cy - 2, 18, 108, cy - 4, 6, body, z=0, g=g)
    c.ell(cx - 6, cy + 14, 44, 12, belly, g=g, decal=True, only=g)
    c.pattern(lambda x, y: (y > cy + 8) & ((x % 5) < 1), -1, only=g)
    # flipper
    c.poly([(cx - 10, cy + 10), (cx + 10, cy + 34 - sw * 0.5), (cx + 16, cy + 12)], fin, z=30, bevel=2)
    # constellation on its back
    stars = [(cx - 20, cy - 14), (cx - 6, cy - 18), (cx + 8, cy - 14), (cx + 22, cy - 18), (cx + 34, cy - 10)]

    def ink(cc):
        for i, (x, y) in enumerate(stars):
            if i:
                x0, y0 = stars[i - 1]
                for k in range(12):
                    f = k / 12
                    cc.put(x0 + (x - x0) * f, y0 + (y - y0) * f, (120, 130, 220))
        for i, (x, y) in enumerate(stars):
            sparkle(cc, x, y, (200, 210, 255), 1)
        peye(cc, cx - 36, cy + 2, 2.4, 2.6, iris=(230, 230, 255), pw=0.7, ph=0.7)
        for k in range(16):
            cc.put(cx - 48 + k, cy + 8 + k * 0.12, (20, 20, 50))
    c.ink(ink)
    sparks((230, 236, 255), 7, seed=65, spread=(4, 124, 4, 40))(c, {}, t, None)
    return c


# ------------------------------------------------------------------ crabs
def crab(c, t, *, cx=64, G=120, shell=(26, 16), shell_mat=None, body="#c86a4a", claw_big=1.0, claw_small=1.0,
         eye_col="#1a1a1a", legs=4, stone=None):
    bm = M(body, spec=0.4)
    sm = shell_mat or bm
    sw = [0, 1, 2, 1][t]
    cy = G - shell[1] - 8 + sw * 0.5
    # far legs
    def leg(k, z, far):
        # walking legs splay wide like a real crab seen from the side: the
        # tips spread from under the claws to well behind the shell, and
        # each leg arches up to a knee above the line from hip to tip
        n = max(1, legs - 1)
        f = k / n
        bx_ = cx + shell[0] * (-0.1 + 0.45 * f)
        by_ = cy + shell[1] * 0.3
        lift = (sw if (k + far) % 2 else 0)
        fx_ = cx + shell[0] * (-0.35 + 1.55 * f) + (5 if far else 0)
        fy = G - (3 if far else 0) - lift * 0.5
        kx = (bx_ + fx_) / 2 + shell[0] * 0.18 * (f - 0.3)
        ky = min(by_, fy) - shell[1] * 0.45 - lift - (1 - abs(f - 0.5)) * 3
        c.chain([(bx_, by_, 2.8), (kx, ky, 2.3), (fx_, fy, 0.7)], bm, z=z)
        c.ell(kx, ky, 2.1, 2.1, bm, z=z + 1)
    for k in range(legs):
        leg(k, -10, True)
    g = c.group()
    if stone:
        stone(c, cx, cy, g)
    else:
        c.ell(cx, cy, shell[0], shell[1], sm, z=0, g=g)
        c.pattern(lambda x, y: ((x - cx) ** 2 / shell[0] ** 2 + (y - cy) ** 2 / shell[1] ** 2) % 0.35 < 0.07, -1, only=g)
    # eyes on stalks
    for side, zz in ((1, -2), (-1, 20)):
        ex = cx - shell[0] * 0.55 + side * 4
        c.cap(ex, cy - shell[1] * 0.5, 1.4, ex - 1, cy - shell[1] * 0.5 - 9, 1.2, bm, z=zz)
        c.ell(ex - 1, cy - shell[1] * 0.5 - 10, 2.6, 2.6, M("#1a1a22", spec=0.8), z=zz + 2)
    # near legs
    for k in range(legs):
        leg(k, 24, False)
    # claws: small far, big near
    for k, (sc, zz, dy) in enumerate(((claw_small, -6, -6), (claw_big, 30, 6))):
        ax0, ay0 = cx - shell[0] * 0.7, cy + dy * 0.5
        wx, wy = ax0 - 12 * sc, ay0 + dy - 4
        c.chain([(ax0, ay0, 3.0 * sc), (wx, wy, 3.2 * sc)], bm, z=zz)
        op = [0, 1, 2, 1][t] * 0.6
        c.ell(wx - 7 * sc, wy - 2, 8 * sc, 5.5 * sc, sm if sm is not bm else bm, z=zz + 2, rot=-25)
        c.cap(wx - 10 * sc, wy - 4 - op, 3.2 * sc, wx - 18 * sc, wy - 9 - op * 2, 1.2 * sc, sm, z=zz + 3)
        c.cap(wx - 10 * sc, wy + 1, 2.8 * sc, wx - 17 * sc, wy + 2 + op, 1.1 * sc, sm, z=zz + 3)
    return dict(cy=cy)


@mon("rimecrab")
def rimecrab(t):
    c = Canvas(128, 128, seed=66)
    crab(c, t, cx=66, shell=(24, 15), shell_mat=ICE, body="#6a8ab0", claw_big=0.9, claw_small=0.8)
    sparks((220, 246, 255), 4, seed=66)(c, {}, t, None)
    return c


@mon("floeclaw")
def floeclaw(t):
    c = Canvas(128, 128, seed=67)
    crab(c, t, cx=74, shell=(30, 18), shell_mat=ICE, body="#4a6a98", claw_big=1.7, claw_small=0.8)
    for k, x in enumerate((60, 74, 88)):
        c.tri((x - 4, 88), (x + 1, 70 - (k % 2) * 6), (x + 5, 88), ICE, z=20, bevel=1)
    sparks((220, 246, 255), 5, seed=67)(c, {}, t, None)
    return c


def _stone(cx_off=0, big=False):
    rock = M("#8a7a6a", tex="grain", tex_amp=0.9)
    moss = M("#6a8a40", tex="fur", tex_amp=0.5)

    def draw(c, cx, cy, g):
        w = 34 if big else 26
        h = 26 if big else 19
        pts = [(cx - w, cy + h * 0.6), (cx - w * 0.8, cy - h * 0.5), (cx - w * 0.2, cy - h), (cx + w * 0.5, cy - h * 0.8),
               (cx + w, cy - h * 0.1), (cx + w * 0.9, cy + h * 0.6)]
        c.poly(pts, rock, z=0, bevel=6, th=12, g=g)
        c.pattern(lambda x, y: ((x * 0.7 + y * 1.3) % 11 < 1) & (y > cy - h), -1, only=g)
        if big:
            c.ell(cx, cy - h * 0.85, w * 0.7, h * 0.3, moss, z=14, tuft=12, tuft_len=2)
            # a sage's hermit beard of moss
            c.cap(cx - w * 0.85, cy - 2, 3, cx - w * 0.9, cy + h * 0.8, 1.5, moss, z=30)
    return draw


@mon("rockhermit")
def rockhermit(t):
    c = Canvas(128, 128, seed=68)
    crab(c, t, cx=70, shell=(26, 19), body="#c8784a", claw_big=0.9, claw_small=0.8, stone=_stone())
    return c


@mon("cragsage")
def cragsage(t):
    c = Canvas(128, 128, seed=69)
    crab(c, t, cx=72, shell=(34, 26), body="#a8603a", claw_big=1.1, claw_small=0.9, stone=_stone(big=True))
    # a glowing rune on the boulder: it knows things
    rune = Mat(["#a06a20", "#e0a040", "#ffd070", "#fff0b0", "#ffffff"], emit=True)

    def ink(cc):
        x, y = 76, 72
        for dx, dy in ((0, 0), (0, 1), (0, 2), (0, 3), (-1, 1), (1, 1), (-2, 3), (2, 3), (0, -1)):
            cc.put(x + dx, y + dy, rune.colors[3 if (t % 2) else 2])
    c.ink(ink)
    return c


# ------------------------------------------------------------------ newt / wyrm
def lizard(c, t, *, cx=64, G=120, L=60, H=12, body="#4a7ab0", belly="#c8e0f0", back=None, leg=8, head=(12, 9),
           tail=40, eye="#f0e060", neck=0, z=0, frills=0, curl=0.0, horns=False):
    bm = M(body, spec=0.5)
    be = M(belly, spec=0.3)
    sw = [0, 1, 2, 1][t]
    by = G - leg - H * 0.6 + sw * 0.4
    # tail
    pts = []
    for k in range(7):
        f = k / 6
        x = cx + L * 0.4 + f * tail
        y = by + math.sin(f * 3.2 + t * 0.9) * 3 + f * 4 - curl * f * f * 20
        pts.append((x, y, H * 0.55 * (1 - f * 0.85)))
    c.chain(pts, bm, z=-6)
    # far legs
    for x0, z0 in ((cx - L * 0.28 + 4, -8), (cx + L * 0.3 + 4, -8)):
        c.chain([(x0, by + 2, 3.2), (x0 - 4, by + leg * 0.6, 2.4), (x0 - 2, G - 1, 1.8)], bm, z=z0)
    g = c.group()
    c.cap(cx - L * 0.35, by, H * 0.7, cx + L * 0.4, by + 1, H * 0.62, bm, z=0, g=g)
    c.cap(cx - L * 0.35, by + H * 0.4, H * 0.35, cx + L * 0.35, by + H * 0.45, H * 0.3, be, g=g, decal=True, only=g)
    if back:
        c.pattern(lambda x, y: ((x % 8) < 3) & (y < by - H * 0.2), 2, only=g)
    for k in range(frills):
        x0 = cx - L * 0.3 + k * (L * 0.75 / max(frills, 1))
        c.tri((x0 - 3, by - H * 0.5), (x0 + 1, by - H * 1.3 - (k % 2) * 3), (x0 + 3.5, by - H * 0.45), ICE, z=6, bevel=1)
    # near legs
    for x0 in (cx - L * 0.28, cx + L * 0.3):
        c.chain([(x0, by + 3, 3.6), (x0 - 5, by + leg * 0.6, 2.8), (x0 - 3, G, 2.0)], bm, z=18)
        c.ell(x0 - 5, G - 1, 4, 1.6, bm, z=20)
    # neck + head
    hx_, hy_ = cx - L * 0.35 - neck * 0.8 - head[0] * 0.6, by - neck - 2
    if neck:
        c.cap(cx - L * 0.3, by, H * 0.6, hx_ + 4, hy_, head[1] * 0.7, bm, z=6)
    hg = c.group()
    c.ell(hx_, hy_, head[0], head[1], bm, z=10, g=hg)
    c.ell(hx_ - head[0] * 0.4, hy_ + head[1] * 0.4, head[0] * 0.6, head[1] * 0.35, be, g=hg, decal=True, only=hg)
    if horns:
        c.cap(hx_ + head[0] * 0.3, hy_ - head[1] * 0.6, 2.4, hx_ + head[0] * 1.3, hy_ - head[1] * 1.6, 0.8, ICE, z=16)
        c.cap(hx_, hy_ - head[1] * 0.7, 2.4, hx_ + head[0] * 0.8, hy_ - head[1] * 1.9, 0.8, ICE, z=24)
    ec = hx(eye)

    def ink(cc):
        peye(cc, hx_ - head[0] * 0.2, hy_ - head[1] * 0.3, 2.6, 2.8, iris=ec, pw=0.5, ph=0.8, slit=True)
        for k in range(int(head[0] * 0.9)):
            cc.put(hx_ - head[0] + 2 + k, hy_ + head[1] * 0.3 + (k > head[0] * 0.6), (30, 30, 50))
    c.ink(ink)
    return dict(head=(hx_, hy_), by=by)


@mon("chillnewt")
def chillnewt(t):
    c = Canvas(128, 128, seed=70)
    lizard(c, t, cx=56, L=48, H=13, body="#4a8ac8", belly="#d8ecf8", leg=6, head=(12, 9), tail=36, eye="#f0e060",
           frills=5)
    c.pattern(lambda x, y: (((x * 0.5 + y) % 9) < 1.2), 2, where=[])
    sparks((220, 246, 255), 4, seed=70)(c, {}, t, None)
    return c


@mon("rimewyrm")
def rimewyrm(t):
    c = Canvas(128, 128, seed=71)
    a = lizard(c, t, cx=66, L=64, H=18, body="#2a5a9a", belly="#c8e0f6", leg=10, head=(15, 11), tail=44,
               eye="#b0f0ff", neck=14, frills=7, horns=True, curl=0.6)
    # cold breath
    hx_, hy_ = a["head"]
    breath = Mat(["#8ab8e6", "#b0d4f2", "#d8ecfa", "#f0faff", "#ffffff"], soft=0.4)
    for k in range(4):
        c.ell(hx_ - 18 - k * 6, hy_ + 4 - k * 1.5 + [0, 1, 0, -1][(t + k) % 4], 3 + k, 2.2 + k * 0.6, breath, z=40 - k)
    return c


# ------------------------------------------------------------------ tortoise
@mon("atlashell")
def atlashell(t):
    c = Canvas(128, 128, seed=72)
    G = 121
    skin = M("#8a7a5a", tex="grain", tex_amp=0.5)
    shellm = M("#7a5a3a", tex="grain", tex_amp=0.7)
    grass = M("#5a9a3a", tex="fur", tex_amp=0.6)
    rock = M("#9a8a78", tex="grain", tex_amp=0.8)
    roof = M("#b04a30", tex="grain", tex_amp=0.5)
    wall = M("#e8dcc0", tex="grain", tex_amp=0.4)
    sw = [0, 1, 2, 1][t]
    cx, cy = 70, 84 + sw * 0.5
    def leg(x0, z, lift):
        # stubby elephant-like column: wide at the shoulder, a round pad and
        # three toenails, with scale rings down its length
        top, foot = cy + 10, G - 3 - lift
        c.cap(x0, top, 9, x0 - 1, foot, 7.5, skin, z=z)
        c.ell(x0 - 2, foot + 1, 9, 3.4, skin, z=z + 2)
        for k in range(3):
            c.ell(x0 - 8 + k * 5, foot + 2.5, 1.8, 1.4, M("#e8dcc0", spec=0.4), z=z + 4)
        c.pattern(lambda x, y, x0=x0: (abs(x - x0) < 8) & (y > top + 4) & (y < foot - 2) & ((y + (x // 4) * 2) % 5 < 1),
                  -1, where=[skin])
    step = [0, 2, 0, 0][t], [0, 0, 0, 2][t]
    leg(52, -10, step[1])
    leg(96, -10, step[0])
    # stubby tail
    c.cap(cx + 42, cy + 10, 4, cx + 52, cy + 16, 1.5, skin, z=-6)
    g = c.group()
    c.ell(cx, cy, 44, 26, shellm, z=0, g=g)
    # scutes: hexagon-ish plates in two rows, each with its own growth rings
    for row, (yy, n, w) in enumerate(((cy - 6, 5, 17), (cy + 8, 6, 15))):
        for k in range(n):
            px = cx - (n - 1) * w / 2 + k * w + (row * 3)
            c.pattern(lambda x, y, px=px, yy=yy, w=w: ((abs(x - px) / (w * 0.5) + abs(y - yy) / 8.0) > 0.92)
                      & ((abs(x - px) / (w * 0.5) + abs(y - yy) / 8.0) < 1.08), -2, only=g)
            c.pattern(lambda x, y, px=px, yy=yy, w=w: ((abs(x - px) / (w * 0.5) + abs(y - yy) / 8.0) > 0.52)
                      & ((abs(x - px) / (w * 0.5) + abs(y - yy) / 8.0) < 0.62), -1, only=g)
    # rim
    c.cap(cx - 44, cy + 12, 5, cx + 44, cy + 12, 5, shellm, z=14)
    c.pattern(lambda x, y: (abs(y - cy - 12) < 5) & ((x % 9) < 1), -2, where=[shellm])
    # the hill on top
    c.ell(cx + 2, cy - 18, 36, 14, grass, z=12, tuft=16, tuft_len=2, tuft_arc=(180, 360))
    c.poly([(cx + 10, cy - 24), (cx + 18, cy - 38), (cx + 28, cy - 26)], rock, z=24, bevel=3)
    # a tiny house people built on it
    hx0, hy0 = cx - 14, cy - 28
    c.poly([(hx0 - 7, hy0 + 8), (hx0 - 7, hy0), (hx0 + 7, hy0), (hx0 + 7, hy0 + 8)], wall, z=30, bevel=1)
    c.poly([(hx0 - 9, hy0 + 1), (hx0, hy0 - 8), (hx0 + 9, hy0 + 1)], roof, z=31, bevel=1)
    # little tree
    c.cap(cx + 30, cy - 22, 1.4, cx + 30, cy - 32, 1.2, M("#6a4a30"), z=26)
    c.ell(cx + 30, cy - 36, 6, 6, M("#3a8a3a", tex="fur", tex_amp=0.6), z=28, tuft=8, tuft_len=1.5)
    # near legs, head
    leg(44, 24, step[0])
    leg(88, 24, step[1])
    # neck with wrinkles and a beaked head that nods
    nod = [0, 1, 2, 1][t]
    c.cap(cx - 40, cy + 6, 8, cx - 54, cy - 2 + nod, 9, skin, z=20)
    c.pattern(lambda x, y: (x < cx - 40) & (x > cx - 56) & ((x + y * 0.3) % 4 < 1), -1, where=[skin])
    hx_, hy_ = cx - 58, cy - 4 + nod
    c.ell(hx_, hy_, 11, 9, skin, z=26)
    c.tri((hx_ - 10, hy_ - 1), (hx_ - 15, hy_ + 3), (hx_ - 8, hy_ + 6), M("#5a4a3a", spec=0.4), z=30, bevel=1)

    def ink(cc):
        peye(cc, hx_ - 4, hy_ - 3, 2.2, 2.4, iris=(40, 30, 20), pw=0.7, ph=0.7)
        for k in range(8):
            cc.put(hx_ - 10 + k, hy_ + 4, (40, 30, 24))
        # a lit window
        cc.put(hx0 - 2, hy0 + 3, (255, 220, 120))
        cc.put(hx0 - 1, hy0 + 3, (255, 220, 120))
        cc.put(hx0 - 2, hy0 + 4, (255, 200, 90))
        cc.put(hx0 - 1, hy0 + 4, (255, 200, 90))
    c.ink(ink)
    return c
