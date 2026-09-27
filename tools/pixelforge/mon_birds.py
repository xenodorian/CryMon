"""Bird CryMon."""
from __future__ import annotations

import math

from .core import M, Mat, crop_frames, flame, sparkle
from .bird import build
from .registry import register
from .mon_quads import sparks, static_zaps


def bird(sid, **spec):
    def make():
        return crop_frames([build(spec, t).render() for t in range(4)])
    register("monsters", sid)(make)
    return make


def _smoke(c, a, t, n=6):
    smoke = Mat(["#2a2426", "#4a4244", "#6a6264", "#8a8284", "#aaa2a2"], soft=0.6)
    for i in range(n):
        x = a["bx"] + 26 + i * 7 + t * 2
        y = a["by"] - 6 + math.sin(i + t) * 4 - i * 2
        r = 3 + i * 0.8
        c.ell(x, y, r, r * 0.8, smoke, z=-30 - i)


def _hot_beak(c, a, t, m=None):
    x, y = a["beak"]

    def fx(cc):
        for i in range(3):
            cc.put(x - 2 - i - t % 2, y - 3 - i * 2, (255, 200, 80) if i % 2 else (255, 120, 40))
    c.fx(fx)


# ------------------------------------------------------------------ chicks
bird("dawnchick", seed=31, body=(17, 17), head=(13, 12), head_type="chick", beak=5, beak_w=3, tilt=0,
     body_col="#f2c83a", belly="#fbe690", beak_col="#f08a2a", leg_col="#f08a2a", eye="#2a1a10",
     tail=8, tail_n=3, feathers=3, wing=0.8, crest="spikes", leg=8,
     extras=[sparks((255, 236, 120), 4, seed=31), static_zaps(n=2, seed=31)])

bird("scorchbeak", seed=32, body=(17, 17), head=(13, 12), head_type="chick", beak=6, beak_w=3.2, tilt=0,
     body_col="#d8402a", belly="#f6a060", beak_col="#ffb030", leg_col="#e0802a", eye="#2a1a10", angry=0.5,
     tail=9, tail_n=3, feathers=3, wing=0.8, crest="flame", leg=8,
     extras=[_hot_beak, sparks((255, 170, 60), 3, seed=32)])

bird("pipwren", seed=33, body=(15, 13), head=(10, 9), beak=6, beak_w=2, tilt=-10,
     body_col="#8a603a", belly="#e6d0a8", wing_col="#7a5230", wing_tip="#5a3a22", beak_col="#3a2a20",
     leg_col="#c08a60", eye="#1a1010", tail=16, tail_n=4, tail_up=0.9, feathers=5, leg=10)

# ------------------------------------------------------------------ hawks
bird("kestrail", seed=34, pose="fly", body=(16, 12), head=(10, 9), beak=6, beak_w=3, hook=True, tilt=-10,
     body_col="#b0603a", belly="#f0dcc0", wing_col="#a05a36", wing_tip="#3a2a2a", beak_col="#e8c050",
     leg_col="#f0c040", eye="#1a1010", tail=18, tail_n=5, feathers=6, span=1.0, angry=0.6,
     flap=(2, 1, 0, 1))

bird("sunhawk", seed=35, pose="fly", body=(20, 14), head=(12, 10), beak=8, beak_w=3.4, hook=True,
     body_col="#e8a830", belly="#fff0b0", wing_col="#f2c040", wing_tip="#fff4a0", beak_col="#f07a20",
     leg_col="#f07a20", eye="#ff6020", tail=22, tail_n=6, feathers=7, span=1.25, angry=0.8, crest="crest",
     extras=[lambda c, a, t, m: _sunrays(c, a, t), sparks((255, 240, 150), 4, seed=35)])


def _sunrays(c, a, t):
    disk = Mat(["#f2a020", "#f8c030", "#ffe060", "#fff4a0", "#fffbe0"], emit=True)
    c.ell(22, 24, 12, 12, disk, z=-60)

    def fx(cc):
        for k in range(8):
            ang = k * math.pi / 4 + t * 0.2
            for r in range(15, 19):
                x, y = 22 + math.cos(ang) * r, 24 + math.sin(ang) * r
                if not cc.alpha[int(y), int(x)]:
                    cc.put(x, y, (255, 226, 110))
    c.fx(fx)


bird("ashwing", seed=36, pose="fly", body=(20, 14), head=(12, 10), beak=8, beak_w=3.4, hook=True,
     body_col="#a0302a", belly="#e87a4a", wing_col="#8a2a24", wing_tip="#3a2424", beak_col="#f0b040",
     leg_col="#e0a040", eye="#ffd040", tail=22, tail_n=6, feathers=7, span=1.25, angry=0.9, crest="flame",
     pre=[lambda c, a, t, m: _smoke(c, a, t)], extras=[sparks((255, 150, 60), 5, seed=36)])

bird("grandroc", seed=37, pose="fly", body=(26, 18), head=(13, 12), beak=11, beak_w=4.5, hook=True,
     body_col="#8a7a6a", belly="#e6dccb", wing_col="#6a5a4c", wing_tip="#f0ece2", head_col="#f4f0e6",
     beak_col="#e8c050", leg_col="#e8c050", eye="#f0b030", tail=24, tail_n=6, feathers=8, span=1.5, angry=0.8)

# ------------------------------------------------------------------ owls
bird("tuftowl", seed=38, body=(18, 18), head=(15, 13), head_type="owl", beak=4, beak_w=2.4, tilt=0,
     body_col="#8a7050", belly="#e6d8bc", face_col="#f2ead8", beak_col="#6a5a40", leg_col="#c0a070",
     eye="#f0b020", tail=8, tail_n=3, feathers=4, crest="tuft", leg=6, eye_big=1.0,
     extras=[lambda c, a, t, m: _wig(c, a, t)])


def _wig(c, a, t):
    wig = M("#f4f0ea", tex="fur", tex_amp=0.4)
    for k, dx in enumerate((-1, 1)):
        for j in range(3):
            c.ell(a["hx"] + dx * (a["hrx"] + 1), a["hy"] + j * 4 - 2, 3, 2.6, wig, z=24 + j)


bird("magistowl", seed=39, body=(26, 26), head=(18, 15), head_type="owl", beak=5, beak_w=3, tilt=0,
     body_col="#5a4a3a", belly="#c8b89c", face_col="#e8dcc4", beak_col="#4a3a2a", leg_col="#a08060",
     eye="#f09020", tail=10, tail_n=3, feathers=5, crest="tuft", leg=6, eye_big=1.15, angry=0.7,
     extras=[lambda c, a, t, m: _scales(c, a, t)])


def _scales(c, a, t):
    brass = M("#d8b050", spec=0.6)
    x0, y0 = a["bx"] + a["rx"] * 0.9, a["by"] + a["ry"] * 0.6
    c.cap(x0 - 14, y0 - 16, 1.2, x0 + 14, y0 - 16, 1.2, brass, z=60)
    c.cap(x0, y0 - 16, 1.2, x0, y0, 1.6, brass, z=60)
    for k, dx in enumerate((-14, 14)):
        dy = [0, 1, 2, 1][t] * (1 if k else -1)
        c.ell(x0 + dx, y0 - 8 + dy, 5, 2, brass, z=60)
        c.ink(lambda cc, x=x0 + dx, y=y0 - 16: [cc.put(x - 4 + i, y + 1 + i * 0.0, (160, 130, 60)) for i in ()])


bird("rimeowl", seed=40, body=(20, 20), head=(16, 13), head_type="owl", beak=4, beak_w=2.6, tilt=0,
     body_col="#dfe8f2", belly="#f6fbff", face_col="#ffffff", wing_col="#c4d4e6", wing_tip="#8aa6c8",
     beak_col="#3a4a60", leg_col="#8aa0c0", eye="#60c8ff", tail=9, tail_n=3, feathers=5, crest="tuft", leg=6,
     extras=[lambda c, a, t, m: _frost(c, a, t), sparks((200, 240, 255), 5, seed=40)])


def _frost(c, a, t):
    ice = Mat(["#6a9ac8", "#9ac4ea", "#c8e6fa", "#eaf8ff", "#ffffff"], spec=0.8)
    G = a["G"]
    c.poly([(30, G + 1), (40, G - 6), (52, G - 4), (70, G - 7), (86, G - 5), (98, G + 1)], ice, z=-2, bevel=2)
    for i, x in enumerate((34, 46, 90)):
        c.tri((x - 2, G - 4), (x + 1, G - 12 - (i % 2) * 4), (x + 3, G - 4), ice, z=4, bevel=1)


# ------------------------------------------------------------------ crow
bird("gallowcrow", seed=41, body=(18, 16), head=(11, 10), beak=10, beak_w=3, hook=False, tilt=-15,
     body_col="#262230", belly="#3a3446", wing_col="#1e1a28", wing_tip="#2c2a3e", beak_col="#3a3844",
     leg_col="#3a3440", eye="#e02a2a", tail=18, tail_n=5, feathers=6, leg=4, angry=0.6, ground=108,
     pre=[lambda c, a, t, m: _gallows(c, a, t)], extras=[lambda c, a, t, m: _laugh(c, a, t)])


def _gallows(c, a, t):
    wood = M("#6a4a32", tex="grain", tex_amp=0.8)
    rope = M("#b89a60", tex="grain", tex_amp=0.5)
    c.poly([(20, 108), (118, 108), (118, 114), (20, 114)], wood, z=-6, bevel=2)   # crossbeam the crow sits on
    c.poly([(106, 108), (114, 108), (114, 127), (106, 127)], wood, z=-8, bevel=2)
    c.cap(30, 114, 1.2, 30 + [0, 1, 2, 1][t], 126, 1.0, rope, z=-4)
    c.ell(30 + [0, 1, 2, 1][t], 126, 3, 2, rope, z=-3)


def _laugh(c, a, t):
    x, y = a["beak"]

    def fx(cc):
        if t in (1, 2):
            for i, (dx, dy) in enumerate(((-4, -8), (-8, -12), (-3, -14))):
                cc.put(x + dx, y + dy, (200, 190, 220))
                cc.put(x + dx + 1, y + dy, (200, 190, 220))
                cc.put(x + dx, y + dy + 1, (200, 190, 220))
    c.fx(fx)
