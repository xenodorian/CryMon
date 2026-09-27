"""Four-legged CryMon built on quad.build."""
from __future__ import annotations

import math

from .core import M, Mat, crop_frames, flame, peye, sparkle, mix, hx
from .quad import build
from .registry import register


def quad(sid, **spec):
    def make():
        return crop_frames([build(spec, t).render() for t in range(4)])
    register("monsters", sid)(make)
    return make


def sparks(color=(255, 200, 70), n=4, spread=(10, 120, 20, 112), seed=1):
    """fx: little star sparks that jump around between frames."""
    def extra(c, a, t, mats):
        def fx(cc):
            x0, x1, y0, y1 = spread
            for i in range(n):
                h = (i * 7919 + t * 104729 + seed * 31) % 9973
                x = x0 + (h % (x1 - x0))
                y = y0 + ((h // 97) % (y1 - y0))
                if cc.alpha[min(int(y), cc.h - 1), min(int(x), cc.w - 1)]:
                    continue
                sparkle(cc, x, y, color, 1 if i % 2 == 0 else 0)
        c.fx(fx)
    return extra


def static_zaps(color=(255, 236, 120), n=3, seed=3):
    """fx: short zigzag bolts jumping off the top of the silhouette."""
    def extra(c, a, t, mats):
        def fx(cc):
            import numpy as np
            al = cc.alpha
            top = al.copy()
            top[1:, :] &= ~al[:-1, :]
            top[0, :] = False
            ys, xs = np.nonzero(top)
            if len(xs) == 0:
                return
            for i in range(n):
                k = (i * 2654435761 + t * 40503 + seed * 97) % len(xs)
                x, y = int(xs[k]), int(ys[k]) - 1
                dx = -1 if (i + t) % 2 else 1
                for j in range(7):
                    if j % 2 == 0:
                        x += dx
                    else:
                        dx = -dx
                    y -= 1
                    if 0 <= y < cc.h and 0 <= x < cc.w and not al[y, x]:
                        cc.put(x, y, (255, 255, 255) if j in (2, 3) else color)
        c.fx(fx)
    return extra


# ------------------------------------------------------------------ ruby cats
quad("sparkit", seed=4, body=(40, 24), leg=18, leg_r=4.6, head=(20, 17), neck=3,
     fur="#d4572e", belly="#f4d3a0", eye="#ffb020", slit=True, stripes=True,
     tail="cat", tail_tip="flame", tail_len=0.95, ear_size=1.1, pale_paws=True,
     extras=[sparks((255, 190, 60), 4)])

quad("blazelynx", seed=5, body=(50, 24), leg=26, leg_r=4.4, head=(16, 14), neck=7,
     fur="#c8452a", belly="#f0c690", eye="#ffcf40", slit=True, angry=0.6, stripes=True,
     ears="fox", ear_size=1.25, tail="short", tail_len=1.1, pale_paws=True,
     extras=[lambda c, a, t, m: [flame(c, a["hx"] - a["hrx"] * 0.35 + dx, a["hy"] - a["hry"] * 1.7 + dy,
                                       9, 2.4, t + i, z=24) for i, (dx, dy) in enumerate(((0, 0), (11, 2)))],
             lambda c, a, t, m: flame(c, a["tip"][0] + 2, a["tip"][1] + 2, 16, 4.5, t, z=-4),
             lambda c, a, t, m: [flame(c, a["bx"] + dx, a["by"] - a["ry"] * 0.8, 8, 2.6, t + i, z=-2)
                                 for i, dx in enumerate((-6, 4, 14))]])

quad("pyrelion", seed=6, body=(58, 30), leg=26, leg_r=6.2, head=(17, 16), neck=6,
     fur="#d88a3a", belly="#f2d09a", eye="#ffe070", angry=0.8, mane="flame",
     ears="round", ear_size=0.9, tail="long", tail_tip="flame", tail_len=1.0, feet="claw",
     tuft=True, extras=[sparks((255, 170, 50), 5, seed=6)])

# ------------------------------------------------------------------ canines / fox
quad("sleightfox", seed=7, body=(44, 20), leg=22, leg_r=3.8, head=(14, 12), neck=6,
     head_type="dog", snout=12, fur="#c75a2c", belly="#f6ead8", eye="#7fd35a", slit=True,
     ears="fox", ear_size=1.3, tail="bushy", tail_len=1.05, tail_col="#c75a2c", pale_paws=True,
     accent="#fbf4e8", tail_tip="tuft",
     extras=[lambda c, a, t, m: _cards(c, a, t)])


def _cards(c, a, t):
    """Three playing cards fanned in the fox's tail wind."""
    red = M("#d63a3a")
    paper = Mat(["#6c6a78", "#b8b4c0", "#e2dee6", "#f6f4f8", "#ffffff"], soft=0.4)
    for i, (dx, dy, rot) in enumerate(((10, -40, -20), (22, -48, 5), (34, -42, 28))):
        x = a["bx"] + dx
        y = a["by"] + dy + [0, -1, -2, -1][(t + i) % 4]
        ca, sa = math.cos(math.radians(rot)), math.sin(math.radians(rot))
        pts = [(x + (-4 * ca - -6 * sa), y + (-4 * sa + -6 * ca)), (x + (4 * ca - -6 * sa), y + (4 * sa + -6 * ca)),
               (x + (4 * ca - 6 * sa), y + (4 * sa + 6 * ca)), (x + (-4 * ca - 6 * sa), y + (-4 * sa + 6 * ca))]
        c.poly(pts, paper, z=30 + i, bevel=1)
        suit = [(0, 0), (-1, 0), (1, 0), (0, 1), (0, -1)]
        col = red.colors[3] if i != 1 else (40, 36, 48)

        def ink(cc, x=x, y=y, col=col):
            for sx, sy in suit:
                cc.put(x + sx, y + sy, col)
        c.ink(ink)


quad("tidewolf", seed=8, body=(56, 26), leg=26, leg_r=5.0, head=(16, 14), neck=8,
     head_type="dog", snout=14, fur="#3f6fb0", belly="#cfe2f2", eye="#bff0ff", angry=0.5,
     ears="fox", ear_size=1.05, tail="bushy", tail_len=1.1, feet="claw", mane="shag", shag_col="#5b8fcc",
     extras=[lambda c, a, t, m: _tide_breath(c, a, t), sparks((200, 236, 255), 4, seed=8)])


def _tide_breath(c, a, t):
    """A cold mist rolling off the wolf's muzzle."""
    mist = Mat(["#6a9ad0", "#9ac4ea", "#c8e6fa", "#eaf8ff", "#ffffff"], soft=0.4)
    x, y = a["nose"]
    for k in range(4):
        c.ell(x - 5 - k * 5, y + 3 + [0, 1, 0, -1][(t + k) % 4], 2.2 + k * 0.8, 1.6 + k * 0.5, mist, z=60 - k)


def _waves(c, a, t):
    foam = Mat(["#1f4f86", "#3a78c0", "#6fb0e6", "#b8e4fa", "#f2fcff"], spec=0.4)
    G = a["G"]
    for i in range(5):
        x = 22 + i * 18 + [0, 2, 4, 2][t]
        c.cap(x, G + 1, 3.5, x + 9, G - 3 - (i % 2) * 2, 1.2, foam, z=20)


# ------------------------------------------------------------------ hares / deer
quad("jolthare", seed=9, body=(38, 24), leg=14, leg_r=4.2, head=(15, 14), neck=2,
     head_type="rodent", snout=5, fur="#e4bf4a", belly="#fbf1d0", eye="#3a2a18",
     ears="long", ear_size=1.0, tail="puff", puff_col="#fff6d8", pale_paws=True,
     extras=[lambda c, a, t, m: _hare_face(c, a, t), static_zaps(n=4), sparks((255, 240, 120), 3, seed=9)])


def _hare_face(c, a, t):
    """Cheek fluff that crackles, and a lightning-bolt forelock."""
    fluff = M("#fbf1d0", tex="fur", tex_amp=0.5)
    hx_, hy_, hrx, hry = a["hx"], a["hy"], a["hrx"], a["hry"]
    c.ell(hx_ - hrx * 0.1, hy_ + hry * 0.55, hrx * 0.7, hry * 0.45, fluff, z=26, th=3, tuft=10, tuft_len=2.5,
          tuft_arc=(20, 200))
    bolt = Mat(["#b08010", "#e0b020", "#ffe050", "#fff4a0", "#ffffff"], emit=True)
    x, y = hx_ - 2, hy_ - hry * 0.75
    c.poly([(x, y - 7), (x + 5, y - 7), (x + 2, y - 2), (x + 5, y - 2), (x - 2, y + 6), (x, y), (x - 3, y)], bolt, z=34,
           bevel=1)
    # dark ear tips
    for ex, ey in a.get("ear_tips", []):
        c.ell(ex, ey + 2, 3, 3.5, M("#5a4020"), z=20)

quad("voltbuck", seed=10, body=(54, 26), leg=30, leg_r=4.0, head=(13, 12), neck=12,
     head_type="deer", snout=10, fur="#c8a038", belly="#f6e8c0", eye="#fff080", feet="hoof",
     ears="long", ear_size=0.45, tail="short", horns="bolt", horn_size=1.1, horn_col="#fff27a",
     tuft=False, extras=[static_zaps(n=4, seed=10), sparks((255, 250, 150), 4, seed=10)])

quad("reedfawn", seed=11, body=(40, 20), leg=26, leg_r=3.2, head=(12, 11), neck=9,
     head_type="deer", snout=8, fur="#9a7040", belly="#efe0c0", eye="#2a1c10", feet="hoof",
     ears="long", ear_size=0.5, tail="short", spots=1, tuft=False,
     extras=[lambda c, a, t, m: _reeds(c, a, t)])


def _reeds(c, a, t):
    reed = M("#6a9a3a")
    tip = M("#8a5a2a", tex="grain", tex_amp=0.6)
    for i, x in enumerate((14, 20, 104, 110, 116)):
        sway = [0, 1, 2, 1][(t + i) % 4]
        h = 34 + (i * 7) % 12
        c.cap(x, a["G"], 1.2, x + sway, a["G"] - h, 0.8, reed, z=40 if i < 2 else -30)
        c.ell(x + sway, a["G"] - h - 4, 1.8, 4.5, tip, z=40 if i < 2 else -30)


quad("bowstag", seed=12, body=(56, 28), leg=30, leg_r=4.6, head=(14, 13), neck=12,
     head_type="deer", snout=10, fur="#7a5a32", belly="#e2d0a8", eye="#2a1c10", feet="hoof",
     ears="long", ear_size=0.5, tail="short", horns="antler", horn_size=1.25, horn_col="#6a9040",
     tuft=False, mane="shag", shag_col="#58703a",
     extras=[lambda c, a, t, m: _bowstring(c, a, t)])


def _bowstring(c, a, t):
    tips = a.get("antler_tips", [])
    if len(tips) < 2:
        return
    (x0, y0), (x1, y1) = tips
    thorn = M("#a6c870")

    def ink(cc):
        n = 24
        for i in range(n + 1):
            f = i / n
            x = x0 + (x1 - x0) * f
            y = y0 + (y1 - y0) * f + 6 * math.sin(math.pi * f)
            cc.put(x, y, (232, 240, 200))
    c.ink(ink)
    for i, (x, y) in enumerate(((x0 - 10, y0 + 4), (x1 - 16, y1 + 6))):
        c.cap(x, y, 1.2, x - 7, y + 2, 0.4, thorn, z=40)


quad("bloomdoe", seed=13, body=(50, 26), leg=28, leg_r=4.0, head=(13, 12), neck=11,
     head_type="deer", snout=9, fur="#b08a5a", belly="#f2e4c8", eye="#2a1c10", feet="hoof",
     ears="long", ear_size=0.5, tail="short", tuft=False,
     extras=[lambda c, a, t, m: _flowers(c, a, t)])


def _flowers(c, a, t, n=14, where="back"):
    petals = [M("#f28ab0"), M("#fff2f6"), M("#f6d24a"), M("#b88af0")]
    leaf = M("#4f9a42")
    bx, by, rx, ry = a["bx"], a["by"], a["rx"], a["ry"]
    for i in range(n):
        ang = math.radians(200 + i * (140 / n))
        x = bx + math.cos(ang) * rx * (0.55 + (i % 3) * 0.15)
        y = by + math.sin(ang) * ry * (0.6 + (i % 2) * 0.25)
        c.ell(x + 2, y + 2, 3.2, 2, leaf, z=18, rot=30)
        p = petals[i % len(petals)]
        r = 2.6 + (i % 3) * 0.6
        for k in range(5):
            aa = math.radians(k * 72 + i * 20)
            c.ell(x + math.cos(aa) * r * 0.8, y + math.sin(aa) * r * 0.8, r * 0.6, r * 0.6, p, z=22)
        c.ell(x, y, 1.2, 1.2, M("#f6c030"), z=26)
    # a crown of blossoms between the ears
    hx_, hy_ = a["hx"], a["hy"]
    for k, (dx, dy) in enumerate(((-4, -12), (3, -14), (9, -11))):
        p = petals[k]
        for j in range(5):
            aa = math.radians(j * 72)
            c.ell(hx_ + dx + math.cos(aa) * 2, hy_ + dy + math.sin(aa) * 2, 1.8, 1.8, p, z=40)
        c.ell(hx_ + dx, hy_ + dy, 1, 1, M("#f6c030"), z=42)


# ------------------------------------------------------------------ cattle / sheep / goats
quad("mooncalf", seed=14, body=(44, 26), leg=18, leg_r=5.0, head=(15, 14), neck=3,
     head_type="bovine", fur="#d8dcf4", belly="#f4f6ff", eye="#6070c0", feet="hoof", hoof_col="#5a5c7a",
     ears="cow", tail="whip", tuft=False, nose_col="#8a8ab0",
     extras=[lambda c, a, t, m: _moonglow(c, a, t), sparks((220, 230, 255), 4, seed=14)])


def _moonglow(c, a, t):
    # crescent birthmark on the flank
    bx, by = a["bx"] + 6, a["by"] - 4
    mark = M("#9aa6f2")
    c.ell(bx, by, 7, 7, mark, decal=True, only=a["g_body"])
    c.ell(bx + 3, by - 2, 6, 6, M("#d8dcf4", tex="fur", tex_amp=0.4), decal=True, only=a["g_body"])


quad("moonbull", seed=15, body=(62, 34), leg=24, leg_r=6.4, head=(17, 15), neck=4,
     head_type="bovine", fur="#9aa4d8", belly="#dde2fa", eye="#fff7c0", feet="hoof", hoof_col="#3a3c5a",
     ears="cow", tail="whip", horns="crescent", horn_size=1.25, horn_col="#f4f0d0", angry=0.6,
     nose_col="#4a4c70", mane="shag", shag_col="#7a84c0",
     extras=[lambda c, a, t, m: _moonglow(c, a, t), sparks((230, 236, 255), 5, seed=15)])

quad("clovercalf", seed=16, body=(44, 26), leg=18, leg_r=5.0, head=(15, 14), neck=3,
     head_type="bovine", fur="#e8e0cc", belly="#fbf6ea", eye="#3a2c18", feet="hoof",
     ears="cow", tail="whip", tuft=False, spots=-2, nose_col="#c48a8a",
     extras=[lambda c, a, t, m: _clover(c, a, t)])


def _clover(c, a, t, n=10, big=False):
    leaf = M("#4aa048")
    dark = M("#2f7a3a")
    bx, by, rx, ry = a["bx"], a["by"], a["rx"], a["ry"]
    for i in range(n):
        ang = math.radians(205 + i * (130 / n))
        x = bx + math.cos(ang) * rx * 0.75 + (i % 2) * 3
        y = by + math.sin(ang) * ry * 0.95
        r = 3.0 if not big else 4.2
        for k in range(3):
            aa = math.radians(-90 + k * 120 + i * 17)
            c.ell(x + math.cos(aa) * r * 0.75, y + math.sin(aa) * r * 0.75, r * 0.62, r * 0.62,
                  leaf if (i + k) % 3 else dark, z=18 + (i % 3))


quad("gardenbull", seed=17, body=(64, 34), leg=24, leg_r=6.6, head=(17, 15), neck=4,
     head_type="bovine", fur="#8a6a48", belly="#d6c4a0", eye="#3a2c18", feet="hoof",
     ears="cow", tail="whip", horns="bull", horn_col="#e8dcb8", angry=0.3, tuft=False,
     extras=[lambda c, a, t, m: _clover(c, a, t, 14, True), lambda c, a, t, m: _flowers(c, a, t, 8),
             lambda c, a, t, m: _bees(c, a, t)])


def _bees(c, a, t):
    def fx(cc):
        for i, (x, y) in enumerate(((96, 30), (104, 44), (20, 34))):
            x += [0, 2, 3, 1][(t + i) % 4]
            y += [0, -1, 1, 0][(t + i) % 4]
            for dx, col in ((0, (240, 200, 40)), (1, (30, 24, 20)), (2, (240, 200, 40))):
                cc.put(x + dx, y, col)
            cc.put(x + 1, y - 1, (230, 240, 255))
            cc.put(x + 2, y - 1, (230, 240, 255))
    c.fx(fx)


quad("warbison", seed=18, body=(70, 38), leg=20, leg_r=7.0, head=(17, 16), neck=2, head_dy=8,
     head_type="bovine", fur="#6a5a4c", belly="#a89480", eye="#f0c040", feet="hoof", angry=0.9,
     ears="cow", ear_size=0.8, tail="whip", horns="broken", horn_col="#dcd2bc", mane="shag", shag_col="#4a3c30",
     nose_col="#2a2220")

quad("boltlamb", seed=19, body=(40, 26), leg=16, leg_r=3.6, head=(12, 12), neck=4,
     head_type="goat", snout=6, beard=False, fur="#3a3440", belly="#5a5060", eye="#ffe060", feet="hoof",
     ears="floppy", ear_size=0.9, tail="short", mane="wool", wool_col="#f4e690", tuft=False,
     extras=[static_zaps(n=4, seed=19), sparks((255, 246, 140), 3, seed=19)])

quad("thunderam", seed=20, body=(54, 32), leg=20, leg_r=5.0, head=(14, 13), neck=5,
     head_type="goat", snout=8, beard=False, fur="#3a3440", belly="#5a5060", eye="#ffe060", feet="hoof",
     ears="floppy", ear_size=0.8, tail="short", mane="wool", wool_col="#e6d470", horns="ram", horn_size=1.2,
     horn_col="#f6e070", angry=0.7, tuft=False,
     extras=[static_zaps(n=6, seed=20), sparks((255, 246, 140), 4, seed=20)])

quad("hornblaze", seed=21, body=(54, 30), leg=22, leg_r=5.0, head=(14, 13), neck=6,
     head_type="goat", snout=8, beard=False, fur="#b8382a", belly="#e89a70", eye="#ffd040", feet="hoof",
     ears="floppy", ear_size=0.8, tail="short", mane="wool", wool_col="#d85a3a", horns="trumpet",
     horn_size=0.95, horn_col="#f0c050", angry=0.6, tuft=False,
     extras=[sparks((255, 160, 60), 5, seed=21)])

quad("grimkid", seed=22, body=(36, 22), leg=18, leg_r=3.2, head=(13, 12), neck=4,
     head_type="goat", snout=6, fur="#2a2430", belly="#4a4050", eye="#ff3030", feet="hoof", hoof_col="#15101a",
     ears="floppy", ear_size=0.8, tail="short", horns="goat", horn_size=0.7, horn_col="#8a8090",
     angry=0.5, nose_col="#15101a")

# ------------------------------------------------------------------ rodents / moles / hog
quad("shrewbit", seed=23, body=(38, 22), leg=8, leg_r=3.2, head=(13, 12), neck=0, head_dy=6,
     head_type="rodent", snout=10, fur="#8a6a4c", belly="#d8c4a4", eye="#1a1210", ears="round",
     ear_size=0.9, tail="long", tail_len=0.8, tail_col="#d0a090", pale_paws=True)

quad("scavrat", seed=24, body=(44, 26), leg=9, leg_r=3.8, head=(14, 12), neck=0, head_dy=6,
     head_type="rodent", snout=11, fur="#6a6058", belly="#b0a494", eye="#e03030", ears="round",
     ear_size=1.1, tail="long", tail_len=1.1, tail_col="#c09080", pale_paws=True,
     extras=[lambda c, a, t, m: _ration(c, a, t)])


def _ration(c, a, t):
    bread = M("#c89050", tex="grain", tex_amp=0.5)
    x, y = a["nose"]
    c.ell(x - 1, y + 6, 6, 4, bread, z=60, rot=-15)


quad("plunderat", seed=25, body=(58, 32), leg=12, leg_r=5.0, head=(16, 14), neck=0, head_dy=4,
     head_type="rodent", snout=12, fur="#5a524c", belly="#a0968a", eye="#ff4030", ears="round",
     ear_size=0.9, tail="long", tail_len=1.3, tail_col="#b08878", feet="claw", angry=0.8,
     extras=[lambda c, a, t, m: _helmet(c, a, t)])


def _helmet(c, a, t):
    steel = M("#8a929c", spec=0.6)
    hx_, hy_, hrx, hry = a["hx"], a["hy"], a["hrx"], a["hry"]
    g = c.group()
    c.ell(hx_ + 1, hy_ - hry * 0.45, hrx * 0.95, hry * 0.7, steel, z=40, g=g)
    c.cap(hx_ - hrx * 1.0, hy_ - hry * 0.2, 1.5, hx_ + hrx * 1.0, hy_ - hry * 0.2, 1.5, steel, z=44, g=g)
    c.cap(hx_ + 1, hy_ - hry * 1.2, 1.4, hx_ + 1, hy_ - hry * 0.2, 1.2, M("#6a727c", spec=0.4), z=46)
    # a dent
    c.pattern(lambda x, y: ((x - hx_ - 4) ** 2 + (y - hy_ + hry * 0.7) ** 2) < 5, -2, only=g)


quad("dustmole", seed=26, body=(38, 30), leg=5, leg_r=4.4, head=(14, 13), neck=0, head_dy=8,
     head_type="mole", snout=7, fur="#6a5040", belly="#a88c70", eye="#000000", eye_kind="none",
     ears="none", tail="short", tail_len=0.6, feet="claw", horn_col="#f0e0d0", nose_col="#e89a9a",
     extras=[lambda c, a, t, m: _dust(c, a, t), lambda c, a, t, m: _shovels(c, a, t, 0.7),
             lambda c, a, t, m: _star_nose(c, a, t)])


def _star_nose(c, a, t):
    """A ring of pink feelers around the nose that flex in and out while it sniffs."""
    pink = M("#f0a0a8", spec=0.3)
    x0, y0 = a["nose"]
    flex = [0, 1, 2, 1][t]
    for k in range(9):
        ang = math.radians(100 + k * 20)
        L = 5 + flex * 0.6 + (k % 2)
        c.cap(x0, y0, 1.6, x0 + math.cos(ang) * L, y0 + math.sin(ang) * L * 0.9, 1.0, pink, z=70)
    c.ell(x0 - 1, y0, 2.4, 2.4, M("#d87080", spec=0.5), z=72)


def _dust(c, a, t, n=6):
    def fx(cc):
        x0, y0 = a["nose"]
        for i in range(n):
            x = x0 - 4 - i * 3 - t
            y = y0 + ((i * 5 + t * 3) % 7) - 3
            col = (196, 170, 130) if i % 2 else (160, 132, 100)
            if not cc.alpha[int(y) % cc.h, int(x) % cc.w]:
                cc.put(x, y, col)
    c.fx(fx)

    def mouth(cc):
        # closed eyes: a little dark slit
        hx_, hy_, hrx, hry = a["hx"], a["hy"], a["hrx"], a["hry"]
        for dx in range(3):
            cc.put(hx_ - hrx * 0.3 + dx, hy_ - hry * 0.1, (40, 28, 24))
    c.ink(mouth)


def _shovels(c, a, t, big=1.0):
    claw = M("#e8d8c0", spec=0.4)
    G = a["G"]
    for k, (x, z) in enumerate(((a["bx"] - a["rx"] * 0.55 - 4, 30), (a["bx"] - a["rx"] * 0.55 + 4, -6))):
        for j in range(3):
            c.cap(x - 3 + j * 3, G - 6, 2.0 * big, x - 8 + j * 3, G, 1.2 * big, claw, z=z)


quad("tunneler", seed=27, body=(56, 34), leg=8, leg_r=5.5, head=(15, 14), neck=0, head_dy=12,
     head_type="mole", snout=10, fur="#5a4034", belly="#98785c", eye="#000000", eye_kind="none",
     ears="none", tail="short", tail_len=0.6, feet="claw", nose_col="#e89a9a",
     extras=[lambda c, a, t, m: _dust(c, a, t), lambda c, a, t, m: _spades(c, a, t),
             lambda c, a, t, m: _back_rubble(c, a, t)])


def _spades(c, a, t):
    """Front paws grown into flat digging blades, raised and scraping in turn."""
    blade = M("#b8a488", spec=0.6)
    edge = M("#f4ecdc", spec=0.8)
    G = a["G"]
    for k, (x, z) in enumerate(((a["bx"] - a["rx"] * 0.62, 34), (a["bx"] - a["rx"] * 0.42, -8))):
        lift = [0, 2, 4, 2][(t + k * 2) % 4]
        y = G - 4 - lift
        c.poly([(x + 4, y - 12), (x - 10, y - 8), (x - 16, y + 2), (x - 6, y + 4), (x + 5, y - 2)], blade, z=z, bevel=2)
        c.cap(x - 16, y + 2, 1.0, x - 6, y + 4, 1.0, edge, z=z + 1)
        for j in range(3):
            c.cap(x - 4 - j * 4, y - 6 + j, 0.5, x - 8 - j * 4, y + 2 + j * 0.5, 0.5, M("#a89478"), z=z + 1, decal=True)


def _back_rubble(c, a, t):
    """Dirt and stones riding on its back from the last tunnel."""
    dirt = M("#7a5a3c", tex="grain", tex_amp=0.8)
    rock = M("#9a8a78", tex="grain", tex_amp=0.6, spec=0.2)
    bx, by, rx, ry = a["bx"], a["by"], a["rx"], a["ry"]
    for i, (dx, r) in enumerate(((-10, 5), (2, 7), (14, 4.5), (22, 3.5))):
        c.poly([(bx + dx - r, by - ry * 0.85), (bx + dx - r * 0.4, by - ry * 0.85 - r * 1.3), (bx + dx + r * 0.7, by - ry * 0.85 - r),
                (bx + dx + r, by - ry * 0.8)], rock, z=40, bevel=1.5)

quad("quakelord", seed=28, body=(76, 42), leg=10, leg_r=7.5, head=(18, 16), neck=0, head_dy=12,
     head_type="mole", snout=12, fur="#4a3a30", belly="#8a7058", eye="#000000", eye_kind="none",
     ears="none", tail="short", tail_len=0.6, feet="claw", nose_col="#e0908a",
     extras=[lambda c, a, t, m: _dust(c, a, t, 9), lambda c, a, t, m: _shovels(c, a, t, 1.5),
             lambda c, a, t, m: _cracks(c, a, t)])


def _cracks(c, a, t):
    rock = M("#8a7a68", tex="grain", tex_amp=0.6)
    G = a["G"]
    for i, (x, h) in enumerate(((10, 6), (18, 4), (112, 7), (120, 4))):
        jump = [0, 1, 2, 1][(t + i) % 4]
        c.poly([(x - 3, G), (x, G - h - jump), (x + 3, G)], rock, z=60, bevel=1)


quad("wheelhog", seed=29, body=(44, 32), leg=8, leg_r=3.6, head=(12, 11), neck=0, head_dy=10,
     head_type="rodent", snout=8, fur="#e0c070", belly="#f4e4b8", eye="#2a1c10", ears="round",
     ear_size=0.7, tail="none", pale_paws=True,
     extras=[lambda c, a, t, m: _spines(c, a, t)])


def _spines(c, a, t):
    sp = M("#c89a30", spec=0.3)
    tipm = M("#fff6a0")
    bx, by, rx, ry = a["bx"], a["by"], a["rx"], a["ry"]
    g = c.group()
    for i in range(16):
        ang = math.radians(170 + i * 12)
        x0 = bx + math.cos(ang) * rx * 0.6
        y0 = by + math.sin(ang) * ry * 0.6
        L = 12 + (i % 3) * 2
        x1 = x0 + math.cos(ang + 0.3) * (rx * 0.5 + L)
        y1 = y0 + math.sin(ang + 0.3) * (ry * 0.5 + L)
        c.cap(x0, y0, 3.2, x1, y1, 0.6, sp, z=4 + (i % 4), g=g)
    static_zaps(n=5, seed=29)(c, a, t, None)
