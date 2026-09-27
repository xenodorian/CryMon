"""Dialogue portraits: 160x200 busts of the same people as npcs.py."""
from __future__ import annotations

import math

import numpy as np

from .core import M, Mat, Canvas, flame, peye, hx, mix, darken, sparkle
from .people import PEOPLE, SKIN
from .registry import register

W, H = 160, 200


def pm(col, n=8, **kw):
    kw.setdefault("dither", 0.35)
    return M(col, n=n, **kw)


def bust(p):
    c = Canvas(W, H, seed=sum(map(ord, p["main"])))
    skin = pm(SKIN[p["skin"]], shift=0.04, sat=0.62, light=0.93, amb=0.34, soft=0.85)
    hair = pm(p.get("hair", "#4a3222"), tex="fur", tex_amp=0.35)
    main = pm(p["main"], tex="fur", tex_amp=0.12, spec=0.5 if p["outfit"] == "armor" else 0.0)
    trim = pm(p["trim"], spec=0.6)
    shirt = pm(p.get("shirt", p["trim"]))
    hatm = pm(p.get("hat_col", p["main"]), spec=0.5 if p.get("hat") in ("helmet", "plume", "crown") else 0.1)
    beard = pm(p.get("beard_col", p.get("hair", "#4a3222")), tex="fur", tex_amp=0.4)
    gold = pm("#e0b840", spec=0.8)
    metal = pm("#aab0bc", spec=0.8)
    ex = p.get("extras", [])
    child = p.get("age") == "child"
    old = p.get("age") == "old"
    build = p.get("build", "avg")
    bw = {"slim": 0.9, "avg": 1.0, "broad": 1.12}[build]
    outfit = p["outfit"]
    hs = p.get("hair_style", "short")
    hat = p.get("hat", "none")

    hx_, hy_ = 80, 90 if not child else 100
    hrx, hry = (35, 43) if not child else (36, 40)
    sh_y = 146 if not child else 156

    # ---- behind the head: long hair, hood back, cape, pony, weapon
    if "cape" in ex:
        c.ell(80, 196, 80, 40, pm(darken(p["main"], 0.75)), z=-20)
    if hs == "long":
        c.poly([(hx_ - hrx - 6, hy_ - 20), (hx_ + hrx + 6, hy_ - 20), (hx_ + hrx + 14, sh_y + 20),
                (hx_ - hrx - 14, sh_y + 20)], hair, z=-14, bevel=10)
    if hs == "pony":
        c.chain([(hx_ + hrx - 6, hy_ - 20, 11), (hx_ + hrx + 10, hy_ + 20, 8), (hx_ + hrx + 12, hy_ + 60, 4)], hair, z=-14)
    if hat == "hood":
        c.poly([(hx_ - hrx - 20, sh_y + 20), (hx_ - hrx - 14, hy_ - 20), (hx_ - 10, hy_ - hry - 22),
                (hx_ + 6, hy_ - hry - 26), (hx_ + hrx + 14, hy_ - 24), (hx_ + hrx + 20, sh_y + 20)], hatm, z=-12, bevel=12)
    for k in ("spear", "halberd", "staff"):
        if k in ex:
            wood = pm("#7a5634", tex="grain", tex_amp=0.6)
            c.cap(140, 10, 4, 146, 200, 4, wood, z=-16)
            if k == "spear":
                c.tri((132, 26), (140, 0), (148, 26), metal, z=-15, bevel=3)
            elif k == "halberd":
                c.poly([(140, 12), (158, 18), (158, 40), (140, 36)], metal, z=-15, bevel=3)
            else:
                c.ell(141, 16, 9, 9, pm("#8ac0ff", spec=0.9), z=-15)
    if "bow" in ex:
        c.chain([(128, 110, 3), (150, 150, 3), (140, 200, 3)], pm("#7a5634", tex="grain", tex_amp=0.6), z=-16)

    # ---- shoulders and torso
    g = c.group()
    sw = 64 * bw if not child else 52
    torso_m = shirt if outfit == "vest" else main
    c.poly([(80 - sw, 204), (80 - sw, sh_y + 34), (80 - sw * 0.82, sh_y + 8), (58, sh_y - 4), (102, sh_y - 4),
            (80 + sw * 0.82, sh_y + 8), (80 + sw, sh_y + 34), (80 + sw, 204)], torso_m, z=0, bevel=16, th=14, g=g)
    c.pattern(lambda x, y: ((x - 80) ** 2 < 30) & (y > sh_y + 40), 0, only=g)
    if outfit == "vest":
        c.poly([(80 - sw, sh_y + 50), (80 - sw * 0.8, sh_y - 2), (66, sh_y - 6), (70, 200), (80 - sw, 200)], main, z=14,
               bevel=6)
        c.poly([(80 + sw, sh_y + 50), (80 + sw * 0.8, sh_y - 2), (94, sh_y - 6), (90, 200), (80 + sw, 200)], main, z=14,
               bevel=6)
    if outfit in ("coat", "robe", "armor", "tunic", "dress", "ghost"):
        # collar V with trim
        c.tri((62, sh_y - 8), (80, sh_y + 22), (98, sh_y - 8), trim, z=16, bevel=3)
        c.tri((66, sh_y - 8), (80, sh_y + 14), (94, sh_y - 8), shirt if outfit != "ghost" else main, z=17, bevel=2)
        c.cap(80, sh_y + 24, 2, 80, 200, 2, trim, z=18) if outfit in ("coat", "robe") else None
    if outfit == "armor":
        # layered pauldrons: a domed cap and three overlapping lames below it
        for d in (-1, 1):
            px = 80 + d * sw * 0.7
            for k in range(3, 0, -1):
                c.ell(px + d * k * 2, sh_y + 8 + k * 9, 24 - k * 1.5, 7, main, z=20 + (3 - k) * 2, rot=d * (14 + k * 4))
                c.cap(px - 18 + d * k * 2, sh_y + 12 + k * 9, 1.0, px + 18 + d * k * 2, sh_y + 12 + k * 9, 1.0, trim,
                      z=21 + (3 - k) * 2, decal=True)
            c.ell(px, sh_y + 2, 24, 13, main, z=28, rot=d * 12)
            c.cap(px - 20, sh_y + 8, 1.8, px + 20, sh_y + 8, 1.8, trim, z=30)
            for rx in (-12, 0, 12):
                c.ell(px + rx, sh_y + 8, 1.6, 1.6, gold, z=33)
        c.pattern(lambda x, y: (abs(x - 80) < 1.2) & (y > sh_y + 20), -2, only=g)
    if "epaulets" in ex:
        for d in (-1, 1):
            c.ell(80 + d * sw * 0.72, sh_y + 2, 20, 9, gold, z=30)
            c.pattern(lambda x, y, d=d: ((x - (80 + d * sw * 0.72)) % 4 < 1.5) & (y > sh_y + 4) & (y < sh_y + 12), -2,
                      where=[gold])
    if "fur_collar" in ex:
        c.ell(80, sh_y + 2, sw * 0.9, 18, pm("#ece8e0", tex="fur", tex_amp=0.6), z=30, tuft=24, tuft_len=4)
    if "apron" in ex:
        c.poly([(56, 176), (104, 176), (110, 200), (50, 200)], pm("#ece4d0"), z=22, bevel=3)
    if "tabard" in ex:
        c.poly([(62, sh_y + 10), (98, sh_y + 10), (98, 200), (62, 200)], main, z=20, bevel=3)
        c.cap(62, sh_y + 10, 2.4, 62, 200, 2.4, trim, z=24)
        c.cap(98, sh_y + 10, 2.4, 98, 200, 2.4, trim, z=24)
    if "satchel" in ex:
        c.cap(40, sh_y, 3, 120, 200, 3, pm("#6a4426"), z=26)
    if "bird" in ex:
        c.ell(128, sh_y - 14, 14, 12, pm("#e6e6e6"), z=40)
        c.ell(120, sh_y - 28, 9, 9, pm("#e6e6e6"), z=42)
        c.tri((110, sh_y - 28), (104, sh_y - 25), (111, sh_y - 24), pm("#e8a030"), z=44, bevel=1)
    if "lantern" in ex:
        c.ell(30, 184, 12, 14, Mat(["#6a50a0", "#9a80e0", "#c8b0ff", "#f0e6ff", "#ffffff"], emit=True), z=40)
        c.cap(22, 170, 2, 38, 170, 2, pm("#3a3a40", spec=0.6), z=42)
    if "torch" in ex:
        c.cap(26, 200, 3, 30, 150, 3, pm("#7a5634", tex="grain", tex_amp=0.6), z=40)
        flame(c, 30, 150, 34, 9, 0, z=42)

    # ---- neck + head
    c.cap(80, hy_ + hry * 0.6, 17, 80, sh_y + 2, 20, skin, z=2, th=0.5)
    hg = c.group()
    c.ell(hx_ - hrx, hy_ + 4, 6, 10, skin, z=6)
    c.ell(hx_ + hrx, hy_ + 4, 6, 10, skin, z=6)
    c.ell(hx_, hy_, hrx, hry, skin, z=10, g=hg)
    # jaw, turned a little toward the left like the finished portraits
    c.ell(hx_ - 3, hy_ + hry * 0.45, hrx * 0.78, hry * 0.55, skin, z=12, g=hg)
    # nose: bridge plus a rounded tip that sticks out toward the left
    c.cap(hx_ - 5, hy_ - 2, 3.4, hx_ - 8, hy_ + 13, 4.6, skin, z=hrx + 12, z1=hrx + 18, g=hg, th=1.0)
    # shadow under the jaw onto the neck
    c.pattern(lambda x, y: (y > hy_ + hry * 0.85) & (y < hy_ + hry * 0.85 + 9) & (abs(x - 80) < 20), -2, where=[skin])
    # cloth folds pulling from the shoulders toward the chest
    c.pattern(lambda x, y: (y > sh_y + 12) & ((abs((x - 80) * 0.7 + (y - sh_y) * np.sign(x - 80) * -0.5) % 17) < 1.2)
              & (abs(x - 80) > 22), -1, only=g)

    # ---- hair
    if hs in ("short", "long", "bun", "braid", "pony", "wild"):
        c.ell(hx_, hy_ - hry * 0.45, hrx + 5, hry * 0.65, hair, z=22, tuft=18 if hs == "wild" else 10,
              tuft_len=4 if hs == "wild" else 2, tuft_arc=(160, 380))
        # fringe sweeping left
        c.ell(hx_ - 10, hy_ - hry * 0.52, hrx * 0.7, hry * 0.26, hair, z=34, rot=-10)
        c.ell(hx_ - hrx + 3, hy_ - 4, 6, 16, hair, z=26)
        c.ell(hx_ + hrx - 3, hy_ - 4, 6, 16, hair, z=26)
    if hs == "bald":
        c.ell(hx_ - hrx + 2, hy_ + 2, 5, 12, hair, z=26)
        c.ell(hx_ + hrx - 2, hy_ + 2, 5, 12, hair, z=26)
    if hs == "bun":
        c.ell(hx_ + 4, hy_ - hry - 6, 14, 12, hair, z=20)
    if hs == "braid":
        c.chain([(hx_ + hrx - 4, hy_ + 10, 7), (hx_ + hrx + 4, hy_ + 40, 6), (hx_ + hrx + 6, hy_ + 76, 4)], hair, z=40)
        c.pattern(lambda x, y: (((y + x * 0.6) % 6) < 1.5) & (x > hx_ + hrx - 12) & (y > hy_ + 6), -2, where=[hair])
    if hs == "long":
        c.ell(hx_ - hrx - 2, hy_ + 22, 8, 30, hair, z=26)
        c.ell(hx_ + hrx + 2, hy_ + 22, 8, 30, hair, z=26)
    # ---- beard
    bd = p.get("beard", "none")
    if bd == "full":
        # beard hangs from the cheeks to a rounded point below the chin, strands running down
        gb = c.group()
        c.poly([(hx_ - hrx * 0.86, hy_ + 6), (hx_ - hrx * 0.7, hy_ + hry * 0.9), (hx_ - 16, hy_ + hry + 12),
                (hx_ - 4, hy_ + hry + 18), (hx_ + 10, hy_ + hry + 10), (hx_ + hrx * 0.72, hy_ + hry * 0.8),
                (hx_ + hrx * 0.86, hy_ + 6), (hx_ + 10, hy_ + 24), (hx_ - 22, hy_ + 24)], beard, z=52, bevel=8, g=gb)
        c.pattern(lambda x, y: ((x * 1.0 + (y - hy_) * 0.18 * np.sign(x - hx_ + 4)) % 3.2 < 1.0), -2, only=gb)
        c.pattern(lambda x, y: ((x + 1.6 + (y - hy_) * 0.18 * np.sign(x - hx_ + 4)) % 6.4 < 0.8), 1, only=gb)
        # mustache sweeping out from under the nose
        c.chain([(hx_ + 12, hy_ + 30, 2.5), (hx_ + 2, hy_ + 21, 5), (hx_ - 8, hy_ + 19, 5.5), (hx_ - 18, hy_ + 21, 5),
                 (hx_ - 27, hy_ + 30, 2.5)], beard, z=58)
    elif bd == "goatee":
        c.ell(hx_ - 2, hy_ + hry * 0.8, 8, 9, beard, z=30)
        c.ell(hx_ - 3, hy_ + 18, 12, 3.5, beard, z=34)
    # ---- hats
    if hat == "cap":
        c.ell(hx_, hy_ - hry * 0.55, hrx + 6, hry * 0.5, hatm, z=40)
        c.ell(hx_ - 12, hy_ - hry * 0.3, hrx * 0.9, 7, hatm, z=44)
    elif hat == "peaked":
        c.poly([(hx_ - hrx - 6, hy_ - hry * 0.35), (hx_ - hrx + 2, hy_ - hry - 14), (hx_ + hrx - 2, hy_ - hry - 14),
                (hx_ + hrx + 6, hy_ - hry * 0.35)], hatm, z=40, bevel=8)
        c.ell(hx_, hy_ - hry * 0.33, hrx + 4, 7, pm("#1a1618", spec=0.7), z=46)
        c.cap(hx_ - hrx - 2, hy_ - hry * 0.55, 2.2, hx_ + hrx + 2, hy_ - hry * 0.55, 2.2, gold, z=48)
        c.ell(hx_, hy_ - hry * 0.8, 6, 6, gold, z=50)
    elif hat == "crown":
        by = hy_ - hry * 0.55
        velvet = pm("#5a1a3a", tex="fur", tex_amp=0.3)
        ruby, sapph = pm("#c02a4a", spec=0.9), pm("#3a5ad0", spec=0.9)
        # velvet cap inside, two arches over it meeting at an orb and cross
        c.ell(hx_, by - 14, 30, 16, velvet, z=38)
        for d in (-1, 1):
            c.chain([(hx_ + d * 30, by - 4, 3), (hx_ + d * 24, by - 26, 2.6), (hx_ + d * 8, by - 36, 2.4), (hx_, by - 37, 2.4)],
                    hatm, z=41)
            for k in range(1, 4):
                c.ell(hx_ + d * (30 - k * 7), by - 8 - k * 9, 1.4, 1.4, pm("#f4ecd8", spec=0.9), z=43)
        c.ell(hx_, by - 42, 5, 5, hatm, z=44)
        c.cap(hx_, by - 47, 1.6, hx_, by - 57, 1.6, hatm, z=45)
        c.cap(hx_ - 4, by - 53, 1.6, hx_ + 4, by - 53, 1.6, hatm, z=45)
        # points: tall fleurons and short spikes, each tipped with a pearl
        for k in range(7):
            x0 = hx_ - 33 + k * 11
            tall = k % 2 == 0
            h = 20 if tall else 11
            c.tri((x0 - 5, by), (x0, by - h), (x0 + 5, by), hatm, z=46 - abs(k - 3) * 0.5, bevel=2)
            if tall:
                c.ell(x0 - 4, by - h + 5, 2.4, 3, hatm, z=46)
                c.ell(x0 + 4, by - h + 5, 2.4, 3, hatm, z=46)
            c.ell(x0, by - h - 2, 2.2, 2.2, pm("#f4ecd8", spec=0.9), z=48)
        # thick band with alternating set stones
        c.poly([(hx_ - 36, by - 5), (hx_ + 36, by - 5), (hx_ + 37, by + 6), (hx_ - 37, by + 6)], hatm, z=50, bevel=3)
        for k in range(5):
            x0 = hx_ - 28 + k * 14
            c.ell(x0, by + 0.5, 3.4 if k % 2 == 0 else 2.6, 3.4 if k % 2 == 0 else 3.0, ruby if k % 2 == 0 else sapph, z=53)
    elif hat == "hood":
        # a cowl framing the face: brow edge over the forehead and two drapes
        c.poly([(hx_ - hrx - 8, hy_ - 4), (hx_ - hrx + 4, hy_ - hry - 6), (hx_, hy_ - hry - 16), (hx_ + hrx - 2, hy_ - hry - 8),
                (hx_ + hrx + 8, hy_ - 4), (hx_ + hrx - 6, hy_ - hry * 0.45), (hx_ - hrx + 6, hy_ - hry * 0.45)],
               hatm, z=40, bevel=8)
        c.poly([(hx_ - hrx - 10, hy_ - 10), (hx_ - hrx + 4, hy_ - 14), (hx_ - hrx + 8, sh_y + 4), (hx_ - hrx - 16, sh_y + 10)],
               hatm, z=40, bevel=6)
        c.poly([(hx_ + hrx + 10, hy_ - 10), (hx_ + hrx - 4, hy_ - 14), (hx_ + hrx - 8, sh_y + 4), (hx_ + hrx + 16, sh_y + 10)],
               hatm, z=40, bevel=6)
    elif hat in ("helmet", "plume"):
        c.ell(hx_, hy_ - hry * 0.35, hrx + 8, hry * 0.78, hatm, z=40)
        c.cap(hx_ - hrx - 8, hy_ - 4, 4, hx_ + hrx + 8, hy_ - 4, 4, hatm, z=46)
        c.cap(hx_, hy_ - hry - 6, 2.5, hx_, hy_ - 6, 2.5, hatm, z=48)
        for d in (-1, 1):
            c.poly([(hx_ + d * (hrx + 6), hy_ - 6), (hx_ + d * (hrx - 6), hy_ - 6), (hx_ + d * (hrx - 10), hy_ + 30),
                    (hx_ + d * (hrx + 2), hy_ + 26)], hatm, z=42, bevel=4)
        if hat == "plume":
            c.chain([(hx_, hy_ - hry - 8, 7), (hx_ + 18, hy_ - hry - 24, 9), (hx_ + 44, hy_ - hry - 16, 6),
                     (hx_ + 56, hy_ - hry + 6, 3)], pm(p.get("plume", "#c02a3a"), tex="fur", tex_amp=0.5), z=38)

    # ---- face
    ec = hx(p.get("eyes", "#3a2a1a"))
    expr = p.get("expr", "neutral")
    skin_c = hx(SKIN[p["skin"]])
    line = darken(skin_c, 0.45)
    lip = mix(skin_c, (170, 60, 60), 0.35)

    def face(cc):
        ey = int(hy_ - 2)
        eyes = [(hx_ - 18, 1.0), (hx_ + 10, 0.9)]
        lashes = hs in ("bun", "braid", "long", "pony") and bd == "none"
        helmet_shadow = hat in ("helmet", "plume")
        for i, (x, s) in enumerate(eyes):
            if "eyepatch" in ex and i == 1:
                for yy in range(ey - 6, ey + 6):
                    for xx in range(x - 7, x + 7):
                        cc.put(xx, yy, (22, 18, 20))
                for k in range(60):
                    cc.put(hx_ - 34 + k, ey - 18 + k * 0.28, (22, 18, 20))
                continue
            ang = {"frown": 0.9, "grim": 0.7, "sad": -0.6, "shock": -0.2, "smirk": 0.2}.get(expr, 0.0)
            # sclera + iris
            for yy in range(-3, 4):
                for xx in range(-7, 8):
                    if (xx / 7.2) ** 2 + (yy / 3.6) ** 2 <= 1:
                        cc.put(x + xx, ey + yy, (238, 232, 226) if p["skin"] != "dead" else (200, 206, 214))
            peye(cc, x - 1, ey + 0.5, 4.2 * s, 4.2 * s, iris=ec, pw=0.5, ph=0.5, look=-0.3, lid=(40, 24, 26))
            # upper lid line, crease above it, soft lower lid
            for xx in range(-8, 9):
                yy = -4 + (xx * xx) / 26
                cc.put(x + xx, ey + yy, (40, 24, 26))
                cc.put(x + xx, ey + yy - 1, (40, 24, 26)) if abs(xx) < 6 else None
                if abs(xx) < 7:
                    cc.put(x + xx, ey + yy - 4, mix(skin_c, line, 0.45))
                if abs(xx) < 6:
                    cc.put(x + xx, ey + 4 + (xx * xx) / 40, mix(skin_c, line, 0.35))
            if lashes:
                ox = -9 if i == 0 else 9
                cc.put(x + ox, ey - 4, (40, 24, 26)); cc.put(x + ox + (-1 if i == 0 else 1), ey - 5, (40, 24, 26))
            # brows
            bc = hx(p.get("hair", "#4a3222")) if hs != "none" else line
            if old:
                bc = mix(bc, (230, 230, 230), 0.5)
            sgn = 1 if i == 0 else -1
            for xx in range(-9, 10):
                tilt = ang * (xx * sgn) / 9 * 3
                yy = ey - 10 - 2 * (1 - (xx / 9) ** 2) + tilt
                for th in range(3 if p.get("build") == "broad" else 2):
                    cc.put(x + xx, yy + th, darken(bc, 0.8))
            if old:
                for k in range(4):
                    cc.put(x + 8 + k * sgn * 0, ey + 3 + k, line) if False else None
                for k in range(5):
                    cc.put(x - 7 - k if i == 0 else x + 7 + k, ey + 1 + k // 2, mix(skin_c, line, 0.6))
            if "tears" in ex:
                for k in range(14):
                    cc.put(x - 1 + (k > 8), ey + 5 + k, (130, 190, 250) if k % 4 else (200, 230, 255))
        # nose: shadow side, nostrils, a highlight on the tip
        for k in range(10):
            cc.put(hx_ - 2 + k * 0.1, hy_ + 3 + k, mix(skin_c, line, 0.4))
        for dx in (-11, -10, -5, -4):
            cc.put(hx_ + dx, hy_ + 16, mix(skin_c, line, 0.8))
        cc.put(hx_ - 9, hy_ + 11, mix(skin_c, (255, 255, 255), 0.45))
        cc.put(hx_ - 8, hy_ + 11, mix(skin_c, (255, 255, 255), 0.3))
        # mouth
        my = int(hy_ + 26)
        if bd != "full":
            if expr in ("smile", "smirk"):
                for k in range(-9, 10):
                    curve = ((k / 9) ** 2) * (4 if expr == "smile" else 3)
                    if expr == "smirk":
                        curve = ((k + 9) / 18) ** 2 * 5
                    cc.put(hx_ - 8 + k, my - curve + (2 if expr == "smile" else 0), line)
                if expr == "smile":
                    for k in range(-6, 7):
                        cc.put(hx_ - 8 + k, my + 3, lip)
            elif expr in ("frown", "grim", "sad"):
                for k in range(-8, 9):
                    curve = ((k / 8) ** 2) * 3
                    cc.put(hx_ - 8 + k, my + curve, line)
                for k in range(-5, 6):
                    cc.put(hx_ - 8 + k, my + 3, lip)
            elif expr == "shock":
                for yy in range(-3, 5):
                    for xx in range(-4, 5):
                        if (xx / 4.5) ** 2 + (yy / 4.5) ** 2 <= 1:
                            cc.put(hx_ - 6 + xx, my + yy, (70, 24, 30))
            else:
                for k in range(-7, 8):
                    cc.put(hx_ - 8 + k, my, line)
                for k in range(-5, 6):
                    cc.put(hx_ - 8 + k, my + 2, lip)
            # lower lip catches light, a dimple of shadow under it
            if expr != "shock":
                for k in range(-3, 3):
                    cc.put(hx_ - 9 + k, my + 4, mix(skin_c, (255, 236, 220), 0.35))
                for k in range(-4, 4):
                    cc.put(hx_ - 8 + k, my + 7, mix(skin_c, line, 0.3))
        if bd == "full":
            for k in range(-5, 5):
                cc.put(hx_ - 8 + k, my + 1 + abs(k) // 4, darken(hx(p.get("beard_col", "#4a3222")), 0.45))
        if bd == "mustache":
            bc = hx(p.get("beard_col", "#4a3222"))
            for k in range(-14, 15):
                for th in range(4 - abs(k) // 5):
                    cc.put(hx_ - 8 + k, my - 4 + th + abs(k) // 4, darken(bc, 0.9 if th else 0.7))
        if bd == "stubble":
            sc = mix(skin_c, hx(p.get("beard_col", "#4a3222")), 0.35)
            for yy in range(int(hy_ + 18), int(hy_ + hry + 2)):
                for xx in range(int(hx_ - hrx * 0.7), int(hx_ + hrx * 0.7)):
                    if (xx * 7 + yy * 13) % 5 == 0 and cc.alpha[yy, xx]:
                        cc.put(xx, yy, sc)
        if "scar" in ex:
            for k in range(22):
                cc.put(hx_ + 16 + k * 0.3, hy_ - 16 + k, (170, 80, 80))
        if "sweat" in ex:
            for k, (x, y) in enumerate(((hx_ + 30, hy_ - 20), (hx_ - 32, hy_ - 10))):
                for yy in range(4):
                    cc.put(x, y + yy, (180, 220, 255))
                cc.put(x - 1, y + 2, (180, 220, 255))
        if "mask" in ex or "veil" in ex:
            veil = "veil" in ex
            for yy in range(int(hy_ + 14), int(hy_ + hry + 8)):
                for xx in range(int(hx_ - hrx - 2), int(hx_ + hrx + 3)):
                    if cc.alpha[yy, xx] and (not veil or (xx + yy) % 2 == 0):
                        cc.put(xx, yy, (130, 36, 36) if not veil else (26, 22, 30))
        if "medals" in ex:
            for k, col in enumerate(((220, 190, 60), (200, 60, 60), (70, 120, 220))):
                x0, y0 = 44 + k * 10, sh_y + 26
                for yy in range(8):
                    for xx in range(4):
                        cc.put(x0 + xx, y0 + yy, col if yy < 5 else (230, 200, 90))
        if "cross" in ex:
            for d in range(-5, 6):
                for w_ in (-1, 0, 1):
                    cc.put(112 + d, sh_y + 30 + w_, (60, 150, 90))
                    cc.put(112 + w_, sh_y + 30 + d, (60, 150, 90))
        if "patch" in ex:
            for yy in range(10):
                for xx in range(10):
                    cc.put(28 + xx, sh_y + 26 + yy, (212, 176, 64) if (xx + yy) % 5 else (150, 120, 40))
        if "keys" in ex:
            for k in range(20):
                a = k / 20 * 2 * math.pi
                cc.put(118 + math.cos(a) * 7, 184 + math.sin(a) * 7, (220, 190, 70))
        if "rings" in ex:
            cc.put(40, 190, (240, 200, 60))
        if "bird" in ex:
            cc.put(116, sh_y - 30, (20, 20, 20)); cc.put(117, sh_y - 30, (20, 20, 20))
        # cheek blush for young/child
        if child or expr == "smile":
            for k in range(4):
                cc.put(hx_ - 24 + k, hy_ + 12, mix(skin_c, (230, 120, 120), 0.3))
                cc.put(hx_ + 18 + k, hy_ + 12, mix(skin_c, (230, 120, 120), 0.3))
    c.ink(face)
    return c


def ghost_bust(p):
    c = bust(dict(p, outfit="ghost"))
    return c


def _reg(sid):
    def make():
        return [bust(PEOPLE[sid]).render()]
    register("portraits", sid)(make)


for _sid in PEOPLE:
    _reg(_sid)
