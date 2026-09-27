"""Overworld NPC walkers: 48x64, front-facing, 4-frame idle, feet on the bottom row."""
from __future__ import annotations

import math

from .core import M, Mat, Canvas, flame, hx, mix, darken, sparkle
from .people import PEOPLE, SKIN
from .registry import register

W, H = 48, 64
BREATH = [0, 0, 1, 1]


def mats_for(p):
    skin = M(SKIN[p["skin"]], n=6, shift=0.04, sat=0.62, light=0.9)
    return dict(
        skin=skin,
        hair=M(p.get("hair", "#4a3222"), tex="fur", tex_amp=0.3),
        main=M(p["main"], tex="fur", tex_amp=0.15, spec=0.5 if p["outfit"] == "armor" else 0.0),
        trim=M(p["trim"], spec=0.5),
        shirt=M(p.get("shirt", p["trim"])),
        pants=M(p["pants"]),
        boots=M(p["boots"], n=5, spec=0.3),
        hat=M(p.get("hat_col", p["main"]), spec=0.5 if p.get("hat") in ("helmet", "plume", "crown") else 0.1),
        beard=M(p.get("beard_col", p.get("hair", "#4a3222")), tex="fur", tex_amp=0.4),
        metal=M("#aab0bc", spec=0.8),
        wood=M("#7a5634", tex="grain", tex_amp=0.6),
        leather=M("#6a4426"),
        gold=M("#e0b840", spec=0.8),
    )


def walker(p, t):
    c = Canvas(W, H, seed=hash(p["main"]) % 97)
    m = mats_for(p)
    b = BREATH[t]
    child = p.get("age") == "child"
    old = p.get("age") == "old"
    build = p.get("build", "avg")
    bw = {"slim": 0.88, "avg": 1.0, "broad": 1.15}[build]
    G = H - 1
    # vertical layout
    if child:
        head_y, head_r, sh_y, waist, hip_w = 27, 7.5, 34, 47, 6
    else:
        head_y, head_r, sh_y, waist, hip_w = 13, 7.0, 22, 41, 7
    if old:
        head_y += 1
        sh_y += 1
    hy = head_y + b
    cx = 24
    tw = 8.5 * bw * (0.8 if child else 1)
    outfit = p["outfit"]
    ex = p.get("extras", [])

    # ---- behind: cape, long hair, pony, hood back, weapons held behind
    if "cape" in ex:
        capem = m["trim"] if p["main"] in ("#46549a",) else M(darken(p["main"], 0.8))
        c.poly([(cx - tw - 1, sh_y + b), (cx + tw + 1, sh_y + b), (cx + tw + 5, G - 3), (cx - tw - 5, G - 3)], capem,
               z=-12, bevel=2)
    hs = p.get("hair_style", "short")
    if hs == "long":
        c.poly([(cx - 8, hy - 2), (cx + 8, hy - 2), (cx + 9, sh_y + 10 + b), (cx - 9, sh_y + 10 + b)], m["hair"], z=-10,
               bevel=2)
    if hs == "pony":
        c.cap(cx + 5, hy - 3, 3, cx + 9, sh_y + 6 + b, 2, m["hair"], z=-10)
    if hs == "braid":
        c.chain([(cx + 6, hy + 2, 2.4), (cx + 9, sh_y + 4 + b, 2.2), (cx + 9, sh_y + 14 + b, 1.8)], m["hair"], z=14)
    if p.get("hat") == "hood":
        c.ell(cx, hy + 1, head_r + 3, head_r + 4, m["hat"], z=-8)
    pole = None
    for k in ("spear", "halberd", "staff"):
        if k in ex:
            pole = k
    if pole:
        px = cx + tw + 5
        c.cap(px, 4 + b if pole != "staff" else hy - 4, 1.1, px, G - 1, 1.1, m["wood"], z=-2)
        if pole == "spear":
            c.tri((px - 2.5, 7 + b), (px, -1 + b), (px + 2.5, 7 + b), m["metal"], z=0, bevel=1)
        elif pole == "halberd":
            c.poly([(px - 1, 2 + b), (px + 6, 4 + b), (px + 6, 10 + b), (px - 1, 9 + b)], m["metal"], z=0, bevel=1)
            c.tri((px - 2, 3 + b), (px, -3 + b), (px + 2, 3 + b), m["metal"], z=0, bevel=1)
        else:
            c.ell(px, hy - 5, 2.6, 2.6, M("#8ac0ff", spec=0.9) if p["main"] != "#787878" else m["wood"], z=0)
    if "bow" in ex:
        c.chain([(cx + tw + 3, sh_y - 6 + b, 1.2), (cx + tw + 7, sh_y + 6 + b, 1.2), (cx + tw + 3, sh_y + 18 + b, 1.2)],
                m["wood"], z=-6)

    # ---- legs + boots
    if outfit not in ("robe", "ghost", "dress"):
        for k, lx in enumerate((cx - 3.5, cx + 3.5)):
            c.cap(lx, waist + b * 0.5, 3.0 * bw, lx, G - 4, 2.6, m["pants"], z=0)
            c.ell(lx + (-0.5 if k == 0 else 0.5), G - 2, 3.6, 2.4, m["boots"], z=4)
    elif outfit == "dress":
        for lx in (cx - 3, cx + 3):
            c.ell(lx, G - 2, 3.2, 2.2, m["boots"], z=4)
    elif outfit == "robe":
        for lx in (cx - 3.5, cx + 3.5):
            c.ell(lx, G - 1.5, 3.4, 2.0, m["boots"], z=-2)

    # ---- torso by outfit
    g = c.group()
    top = sh_y + b
    if outfit == "ghost":
        wag = [0, 1, 0, -1][t]
        c.poly([(cx - tw, top), (cx + tw, top), (cx + tw - 1, waist), (cx + 3 + wag, G - 6), (cx + wag, G - 2),
                (cx - 3 + wag, G - 8), (cx - tw + 1, waist)], m["main"], z=2, bevel=3, g=g)
    elif outfit == "robe":
        c.poly([(cx - tw, top), (cx + tw, top), (cx + tw + 3, G - 2), (cx - tw - 3, G - 2)], m["main"], z=2, bevel=3, g=g)
        c.cap(cx - tw - 3, G - 3, 1.2, cx + tw + 3, G - 3, 1.2, m["trim"], z=8)
        c.cap(cx, top + 2, 1.0, cx, G - 4, 1.0, m["trim"], z=8)
    elif outfit == "dress":
        c.poly([(cx - tw + 1, top), (cx + tw - 1, top), (cx + tw - 1, waist - 4 + b), (cx - tw + 1, waist - 4 + b)],
               m["main"], z=2, bevel=2, g=g)
        c.poly([(cx - tw + 1, waist - 5 + b), (cx + tw - 1, waist - 5 + b), (cx + tw + 4, G - 3), (cx - tw - 4, G - 3)],
               m["main"], z=2, bevel=3, g=g)
        c.cap(cx - tw - 4, G - 4, 1.0, cx + tw + 4, G - 4, 1.0, m["trim"], z=8)
    else:
        bottom = waist + 2 + b if outfit != "coat" else waist + 8 + b * 0.5
        flare = 2 if outfit == "coat" else 0
        body_m = m["shirt"] if outfit == "vest" else m["main"]
        c.poly([(cx - tw, top), (cx + tw, top), (cx + tw - 1 + flare, bottom), (cx - tw + 1 - flare, bottom)], body_m,
               z=2, bevel=3, g=g)
        if outfit == "vest":
            c.poly([(cx - tw, top), (cx - 2, top), (cx - 2, waist + b), (cx - tw + 1, waist + b)], m["main"], z=3, bevel=1)
            c.poly([(cx + 2, top), (cx + tw, top), (cx + tw - 1, waist + b), (cx + 2, waist + b)], m["main"], z=3, bevel=1)
        if outfit == "coat":
            c.cap(cx, top + 2, 0.8, cx, bottom - 1, 0.8, m["trim"], z=6)
            if not child:
                c.tri((cx - 3.5, top), (cx, top + 5), (cx + 3.5, top), m["trim"], z=6, bevel=1)
        if outfit == "armor":
            c.cap(cx - tw + 1, waist - 1 + b, 1.4, cx + tw - 1, waist - 1 + b, 1.4, m["leather"], z=6)
            c.ell(cx - 2, top + 6, 4, 4, m["main"], z=4)
            c.ell(cx + 2, top + 6, 4, 4, m["main"], z=4)
        if outfit == "tunic" or "belt" in ex:
            c.cap(cx - tw + 1, waist - 1 + b, 1.3, cx + tw - 1, waist - 1 + b, 1.3, m["leather"], z=7)
    if "tabard" in ex:
        c.poly([(cx - 4, top + 2), (cx + 4, top + 2), (cx + 4, waist + 6 + b), (cx - 4, waist + 6 + b)], m["main"], z=8,
               bevel=1)
        c.poly([(cx - 4, top + 2), (cx + 4, top + 2), (cx + 4, waist + 6 + b), (cx - 4, waist + 6 + b)], m["trim"], z=8,
               bevel=1, decal=True, only=None) if False else None
    if "apron" in ex:
        c.poly([(cx - 5, waist - 6 + b), (cx + 5, waist - 6 + b), (cx + 6, waist + 9 + b * 0.5), (cx - 6, waist + 9 + b * 0.5)],
               M("#ece4d0"), z=8, bevel=1)
    if "fur_collar" in ex:
        c.ell(cx, top + 1, tw + 2, 3.5, M("#ece8e0", tex="fur", tex_amp=0.6), z=10, tuft=10, tuft_len=1)
    if "epaulets" in ex:
        for d in (-1, 1):
            c.ell(cx + d * (tw - 1), top + 1, 3.2, 2.0, m["gold"], z=10)

    # ---- arms (skin hands)
    arm_m = m["main"] if outfit not in ("vest",) else m["shirt"]
    for d in (-1, 1):
        sx = cx + d * (tw + 0.5)
        hand_y = waist - 1 + b
        c.cap(sx, top + 2, 2.6 * bw, sx + d * 1.5, hand_y - 2, 2.2, arm_m, z=4)
        if "gloves" in ex:
            c.ell(sx + d * 1.5, hand_y, 2.4, 2.4, M("#2a2226"), z=6)
        elif outfit != "ghost":
            c.ell(sx + d * 1.5, hand_y, 2.2, 2.2, m["skin"], z=6)

    # ---- hand-held things
    if "sword" in ex:
        c.cap(cx - tw - 3, waist - 2 + b, 1.0, cx - tw - 5, G - 8, 1.0, m["metal"], z=8)
        c.cap(cx - tw - 5, waist - 3 + b, 0.9, cx - tw - 1, waist - 3 + b, 0.9, m["gold"], z=9)
    if "dagger" in ex:
        c.cap(cx + tw - 2, waist + b, 0.8, cx + tw - 1, waist + 5 + b, 0.8, m["metal"], z=9)
    if "torch" in ex:
        c.cap(cx - tw - 2, waist - 2 + b, 1.0, cx - tw - 4, waist - 12 + b, 1.0, m["wood"], z=9)
        flame(c, cx - tw - 4, waist - 12 + b, 8, 2.2, t, z=10)
    if "lantern" in ex:
        c.cap(cx - tw - 2, waist - 1 + b, 0.5, cx - tw - 2, waist + 3 + b, 0.5, M("#3a3a40"), z=9)
        c.ell(cx - tw - 2, waist + 6 + b, 2.6, 3.4, Mat(["#6a50a0", "#9a80e0", "#c8b0ff", "#f0e6ff", "#ffffff"],
                                                         emit=True), z=10)
    if "flask" in ex:
        c.ell(cx - tw - 2, waist + 1 + b, 2.2, 3.0, M("#6a8aa0", spec=0.8), z=9)
    if "keys" in ex:
        c.ell(cx + tw - 2, waist + 3 + b, 2.4, 2.4, m["gold"], z=9, th=1)
    if "sack" in ex:
        c.ell(cx + tw + 3, waist + 3 + b, 5, 6, M("#a08a5a", tex="grain", tex_amp=0.6), z=-3)
    if "satchel" in ex:
        c.ell(cx - tw + 1, waist + 1 + b, 3.5, 3.0, m["leather"], z=9)
    if "bird" in ex:
        bx_, by_ = cx + tw, top - 3
        c.ell(bx_, by_, 3.2, 2.6, M("#e6e6e6"), z=12)
        c.ell(bx_ - 2, by_ - 2, 2.0, 2.0, M("#e6e6e6"), z=13)

    # ---- head
    hg = c.group()
    c.ell(cx, hy, head_r, head_r + 0.5, m["skin"], z=10, g=hg)
    c.ell(cx - head_r, hy + 1, 1.4, 2, m["skin"], z=9)
    c.ell(cx + head_r, hy + 1, 1.4, 2, m["skin"], z=9)
    # hair
    if hs in ("short", "long", "bun", "braid", "pony", "wild"):
        c.ell(cx, hy - 3, head_r + 0.8, head_r * 0.62, m["hair"], z=12, tuft=10 if hs == "wild" else 0, tuft_len=1.5)
        c.ell(cx - head_r + 1.5, hy - 1, 2.2, 3.2, m["hair"], z=13)
        c.ell(cx + head_r - 1.5, hy - 1, 2.2, 3.2, m["hair"], z=13)
    if hs == "bald":
        c.ell(cx - head_r + 1, hy + 0.5, 1.8, 2.5, m["hair"], z=13)
        c.ell(cx + head_r - 1, hy + 0.5, 1.8, 2.5, m["hair"], z=13)
    if hs == "bun":
        c.ell(cx, hy - head_r - 1, 3.2, 3, m["hair"], z=11)
    if hs == "long":
        c.ell(cx - head_r, hy + 3, 2.4, 5, m["hair"], z=13)
        c.ell(cx + head_r, hy + 3, 2.4, 5, m["hair"], z=13)
    # beard
    bd = p.get("beard", "none")
    if bd == "full":
        c.ell(cx, hy + 4.5, head_r - 1, 4.5, m["beard"], z=14, tuft=8, tuft_len=1.2, tuft_arc=(20, 160))
    elif bd == "goatee":
        c.ell(cx, hy + 6, 2.2, 2.4, m["beard"], z=14)
    # hat
    hat = p.get("hat", "none")
    if hat == "cap":
        c.ell(cx, hy - 4, head_r + 1, 4, m["hat"], z=15)
        c.cap(cx - head_r - 1, hy - 2, 1.1, cx + head_r + 1, hy - 2, 1.1, m["hat"], z=16)
    elif hat == "peaked":
        c.poly([(cx - head_r - 1, hy - 3), (cx - head_r + 0, hy - 9), (cx + head_r - 0, hy - 9), (cx + head_r + 1, hy - 3)],
               m["hat"], z=15, bevel=2)
        c.cap(cx - head_r, hy - 2.5, 1.2, cx + head_r, hy - 2.5, 1.2, M("#1a1618", spec=0.6), z=16)
        c.cap(cx - head_r, hy - 4.2, 0.7, cx + head_r, hy - 4.2, 0.7, m["gold"], z=16)
        c.ell(cx, hy - 6.5, 1.4, 1.4, m["gold"], z=17)
    elif hat == "crown":
        for k in range(5):
            x0 = cx - 6 + k * 3
            c.tri((x0 - 1.5, hy - 5), (x0, hy - 11 - (k % 2) * 2), (x0 + 1.5, hy - 5), m["hat"], z=16, bevel=1)
        c.cap(cx - 7, hy - 5, 1.4, cx + 7, hy - 5, 1.4, m["hat"], z=17)
    elif hat == "hood":
        c.ell(cx, hy - 3, head_r + 2.5, head_r * 0.7, m["hat"], z=15)
        c.ell(cx - head_r - 0.5, hy + 1, 2.2, 5, m["hat"], z=15)
        c.ell(cx + head_r + 0.5, hy + 1, 2.2, 5, m["hat"], z=15)
    elif hat in ("helmet", "plume"):
        c.ell(cx, hy - 2.5, head_r + 1.2, head_r * 0.85, m["hat"], z=15)
        c.cap(cx - head_r - 1, hy - 0.5, 1.2, cx + head_r + 1, hy - 0.5, 1.2, m["hat"], z=16)
        if hat == "plume":
            c.chain([(cx, hy - 9, 2.2), (cx + 3, hy - 13, 2.4), (cx + 7, hy - 11, 1.6)], M(p.get("plume", "#c02a3a")),
                    z=14)

    # ---- face ink
    ec = hx(p.get("eyes", "#2a1a10"))
    expr = p.get("expr", "neutral")
    dark = (36, 22, 20)
    skin_d = darken(SKIN[p["skin"]], 0.6)

    def face(cc):
        ey = int(hy + 0.5)
        lx, rx = cx - 3, cx + 2
        if hat in ("helmet", "plume") and "tears" in ex and p["outfit"] != "ghost":
            pass
        for x in (lx, rx):
            if "eyepatch" in ex and x == rx:
                cc.put(x, ey, (20, 16, 18))
                cc.put(x + 1, ey, (20, 16, 18))
                for k in range(6):
                    cc.put(cx - 3 + k, ey - 2 - (k > 3), (20, 16, 18))
                continue
            cc.put(x, ey, dark)
            cc.put(x, ey + 1, ec if not old else dark)
            if expr in ("frown", "grim"):
                cc.put(x - (1 if x == lx else -1), ey - 1, dark)
                cc.put(x, ey - 1, dark)
            if expr == "sad":
                cc.put(x + (1 if x == lx else -1) * -1, ey - 1, skin_d)
        my = int(hy + 4)
        if bd not in ("full",):
            if expr in ("smile", "smirk"):
                cc.put(cx - 2, my, dark) if expr == "smile" else None
                cc.put(cx - 1, my + 1, dark)
                cc.put(cx, my + 1, dark)
                cc.put(cx + 1, my, dark)
            elif expr == "shock":
                cc.put(cx - 1, my, dark); cc.put(cx, my, dark); cc.put(cx - 1, my + 1, dark); cc.put(cx, my + 1, dark)
            elif expr in ("frown", "sad", "grim"):
                cc.put(cx - 2, my + 1, dark); cc.put(cx - 1, my, dark); cc.put(cx, my, dark); cc.put(cx + 1, my + 1, dark)
            else:
                cc.put(cx - 1, my, dark); cc.put(cx, my, dark)
        if bd == "mustache":
            bc = hx(p.get("beard_col", "#4a3222"))
            for k in range(-2, 3):
                cc.put(cx - 0.5 + k, my - 1, bc)
            cc.put(cx - 3, my, bc); cc.put(cx + 2, my, bc)
        if bd == "stubble":
            sc = mix(SKIN[p["skin"]], hx(p.get("beard_col", "#4a3222")), 0.45)
            for k in range(-3, 3):
                if (k + t) % 2:
                    cc.put(cx + k, my + 2, sc)
        if "tears" in ex:
            for x in (lx, rx):
                cc.put(x, ey + 2, (120, 190, 255))
                cc.put(x, ey + 3 + (t % 2), (160, 210, 255))
        if "scar" in ex:
            for k in range(3):
                cc.put(rx + 1 - k * 0 + (k == 2), ey - 1 + k, (180, 80, 80))
        if "sweat" in ex:
            cc.put(cx + 6, ey - 2 + (t % 2), (180, 220, 255))
        if "mask" in ex:
            for yy in range(my - 1, my + 3):
                for xx in range(cx - 5, cx + 5):
                    cc.put(xx, yy, (120, 36, 36) if yy > my - 1 else (90, 26, 26))
        if "veil" in ex:
            for yy in range(my - 1, my + 3):
                for xx in range(cx - 5, cx + 5):
                    if (xx + yy) % 2 == 0:
                        cc.put(xx, yy, (30, 26, 34))
        if "medals" in ex:
            mx0 = cx - 5
            for k, col in enumerate(((220, 190, 60), (200, 60, 60), (70, 120, 220))):
                cc.put(mx0 + k * 2, sh_y + 5 + b, col)
                cc.put(mx0 + k * 2, sh_y + 6 + b, darken(col, 0.7))
        if "cross" in ex:
            y0 = sh_y + 5 + b
            for d in range(-1, 2):
                cc.put(cx + 3 + d, y0 + 1, (60, 150, 90))
                cc.put(cx + 3, y0 + 1 + d, (60, 150, 90))
        if "patch" in ex:
            cc.put(cx - tw - 1, sh_y + 5 + b, (212, 176, 64)); cc.put(cx - tw - 1, sh_y + 6 + b, (212, 176, 64))
        if "rings" in ex:
            cc.put(cx - tw - 3, waist + b, (240, 200, 60)); cc.put(cx + tw + 2, waist + b, (240, 200, 60))
        if "bird" in ex:
            cc.put(cx + tw - 3, top - 5, (20, 20, 20))
            cc.put(cx + tw - 5, top - 4, (230, 150, 40))
    c.ink(face)
    return c


def prop_grave(t):
    c = Canvas(W, H, seed=3)
    stone = M("#8a8680", tex="grain", tex_amp=0.9)
    dirt = M("#5c4630", tex="grain", tex_amp=0.8)
    moss = M("#5a7a3a", tex="fur", tex_amp=0.6)
    c.ell(24, 58, 19, 5, dirt, z=0)
    c.poly([(12, 56), (12, 22), (16, 15), (24, 12), (32, 15), (36, 22), (36, 56)], stone, z=4, bevel=3, th=6)
    c.ell(14, 50, 4, 6, moss, z=10, tuft=6, tuft_len=1)

    def ink(cc):
        # carved cross and a faint rune glow
        for y in range(22, 36):
            cc.put(24, y, (70, 66, 62))
        for x in range(20, 29):
            cc.put(x, 26, (70, 66, 62))
        for k, (x, y) in enumerate(((19, 42), (24, 44), (29, 42))):
            cc.put(x, y, (170, 150, 255) if (k + t) % 3 else (230, 220, 255))
    c.ink(ink)
    return c


def prop_shrine(t):
    c = Canvas(W, H, seed=5)
    stone = M("#9a8a72", tex="grain", tex_amp=0.9)
    roof = M("#b8402e", tex="grain", tex_amp=0.4)
    wood = M("#6a4a30", tex="grain", tex_amp=0.6)
    c.poly([(8, 62), (8, 56), (40, 56), (40, 62)], stone, z=0, bevel=2)
    c.poly([(12, 56), (12, 30), (36, 30), (36, 56)], stone, z=2, bevel=2)
    c.poly([(16, 50), (16, 36), (32, 36), (32, 50)], Mat(["#1a1410", "#2a2018", "#3a2c20", "#4a3828", "#5a4430"], soft=0.3),
           z=4, bevel=1)
    for x in (13, 35):
        c.cap(x, 30, 1.4, x, 56, 1.4, wood, z=6)
    c.poly([(4, 31), (24, 14), (44, 31), (40, 33), (8, 33)], roof, z=8, bevel=3)
    c.ell(24, 50, 5, 2.2, M("#c8b8a0", spec=0.4), z=10)   # offering bowl

    def ink(cc):
        cc.put(24, 42, (240, 200, 90) if t % 2 else (200, 150, 60))
        cc.put(24, 43, (200, 150, 60))
    c.ink(ink)
    return c


def prop_pickup(t):
    c = Canvas(W, H, seed=7)
    bob = [0, -1, -2, -1][t]
    pouch = M("#9a6a3a", tex="grain", tex_amp=0.5)
    c.ell(24, 50 + bob, 8, 7, pouch, z=0)
    c.cap(20, 43 + bob, 1.6, 28, 43 + bob, 1.6, M("#6a4020"), z=4)
    c.ell(24, 41 + bob, 4, 2.5, pouch, z=2)
    c.ell(24, 60, 7, 1.5, Mat(["#403830", "#504840", "#605850", "#706860", "#807870"], soft=0.2), z=-10)

    def fx(cc):
        pts = [((12, 32), (36, 28), (24, 22)), ((14, 26), (34, 34), (26, 20)), ((10, 30), (38, 26), (22, 24)),
               ((13, 28), (35, 32), (25, 18))][t]
        for i, (x, y) in enumerate(pts):
            sparkle(cc, x, y, (255, 230, 120), 1 if i == t % 3 else 0)
    c.fx(fx)
    return c


PROPS = {"grave": prop_grave, "shrine": prop_shrine, "pickup": prop_pickup}


def _reg(sid):
    def make():
        if sid in PROPS:
            return [PROPS[sid](t).render() for t in range(4)]
        return [walker(PEOPLE[sid], t).render() for t in range(4)]
    register("npcs", sid)(make)


for _sid in list(PEOPLE) + list(PROPS):
    _reg(_sid)
