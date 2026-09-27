"""Parametric four-legged CryMon, facing left in a 3/4 view.

One builder covers cats, canines, hares, deer, cattle, sheep, goats,
rodents and moles. A species passes a spec dict; anything it leaves out
takes the default. Extras are callables run with the computed anchor
points so a species can bolt on its own details (wool, gardens, sparks).
"""
from __future__ import annotations

import math

from .core import M, Mat, Canvas, flame, peye, sparkle, hx, mix

BOB = [0, 1, 2, 1]

DEFAULT = dict(
    seed=1,
    ground=121,
    bx=70,                 # body center x
    body=(46, 28),         # body length, height
    leg=24, leg_r=5.0,     # leg length, thickness
    feet="paw",            # paw | hoof | claw
    neck=6, neck_r=None,
    head=(19, 16),         # head radii
    head_dx=0, head_dy=0,  # nudge head from its default spot
    head_type="cat",       # cat | dog | bovine | deer | rodent | goat | mole
    snout=0,               # snout length (dog/deer/rodent)
    ears="cat",            # cat | fox | long | round | floppy | cow | tiny | none
    ear_size=1.0,
    tail="cat",            # cat | bushy | short | long | puff | whip | none
    tail_len=1.0,
    tail_tip=None,         # flame | spark | tuft | None
    horns=None,            # ram | bull | crescent | antler | bolt | goat | broken | trumpet
    horn_size=1.0,
    mane=None,             # flame | fluff | wool | shag
    fur="#b0703a", belly="#ead2a6", accent=None, inner_ear="#e49a90",
    eye="#f0b030", eye_kind="round", eye_size=1.0, slit=False, angry=0.0,
    horn_col="#e8dcc0", hoof_col="#3a2c28", nose_col="#3a2226",
    tuft=True, stripes=False, spots=False,
    extras=(), pre=(),     # callables(c, a, t, mats)
    fur_tex=0.5,
    tail_col=None,
)


def build(spec, t):
    s = dict(DEFAULT)
    s.update(spec)
    b = BOB[t]
    c = Canvas(128, 128, seed=s["seed"])
    fur = M(s["fur"], tex="fur", tex_amp=s["fur_tex"])
    belly = M(s["belly"], tex="fur", tex_amp=0.3)
    acc = M(s["accent"]) if s["accent"] else fur
    tailm = M(s["tail_col"], tex="fur", tex_amp=0.4) if s["tail_col"] else fur
    horn = M(s["horn_col"], spec=0.3)
    hoof = M(s["hoof_col"], n=5)
    ear_in = M(s["inner_ear"])
    mats = dict(fur=fur, belly=belly, acc=acc, horn=horn, hoof=hoof, ear_in=ear_in, tail=tailm)

    G = s["ground"]
    bl, bh = s["body"]
    rx, ry = bl / 2, bh / 2
    L = s["leg"]
    bx = s["bx"]
    by = G - L - ry * 0.55 + b * 0.5
    hrx, hry = s["head"]
    neck = s["neck"]
    # head sits forward and up from the chest
    hx_ = bx - rx * 0.78 - neck * 0.55 - hrx * 0.45 + s["head_dx"]
    hy_ = by - ry * 0.7 - neck * 0.55 - hry * 0.25 + s["head_dy"] + b * 0.3
    a = dict(bx=bx, by=by, rx=rx, ry=ry, hx=hx_, hy=hy_, hrx=hrx, hry=hry, G=G, b=b, t=t)

    for fn in s["pre"]:
        fn(c, a, t, mats)

    # ---- tail (behind everything)
    tl = s["tail_len"]
    tx, ty = bx + rx * 0.85, by - ry * 0.25
    sw = [0, 1, 2, 1][t]
    tail = s["tail"]
    tg = c.group()
    tip = None
    if tail == "cat":
        pts = [(tx, ty, 4), (tx + 12 * tl, ty - 2, 3.6), (tx + 18 * tl, ty - 14 * tl, 3.2),
               (tx + 14 * tl + sw, ty - 26 * tl, 3.0)]
        c.chain(pts, tailm, z=-14, g=tg)
        tip = pts[-1]
    elif tail == "bushy":
        pts = [(tx - 2, ty, 5), (tx + 10 * tl, ty + 2, 7), (tx + 20 * tl, ty - 4 * tl + sw, 8),
               (tx + 26 * tl, ty - 14 * tl + sw, 5), (tx + 25 * tl, ty - 20 * tl + sw, 2)]
        for i in range(len(pts) - 1):
            (x0, y0, r0), (x1, y1, r1) = pts[i], pts[i + 1]
            c.cap(x0, y0, r0, x1, y1, r1, tailm, z=-14, g=tg)
        c.ell(tx + 21 * tl, ty - 8 * tl + sw, 8, 9, tailm, z=-10, g=tg, tuft=9, tuft_len=3)
        tip = pts[-2]
    elif tail == "long":
        pts = [(tx, ty, 3.6), (tx + 14 * tl, ty + 6, 3.0), (tx + 24 * tl, ty + 2 * tl + sw, 2.4),
               (tx + 30 * tl, ty - 6 * tl + sw, 2.0)]
        c.chain(pts, tailm, z=-14, g=tg)
        tip = pts[-1]
    elif tail == "whip":
        pts = [(tx, ty + 4, 2.6), (tx + 10 * tl, ty + 14, 2.0), (tx + 14 * tl, ty + 24 + sw, 1.5)]
        c.chain(pts, tailm, z=-14, g=tg)
        tip = pts[-1]
    elif tail == "short":
        c.ell(tx + 2, ty - 1, 5 * tl, 4 * tl, tailm, z=-2, g=tg, rot=-30)
        tip = (tx + 5, ty - 3, 3)
    elif tail == "puff":
        c.ell(tx + 1, ty, 6 * tl, 6 * tl, s.get("puff_col") and M(s["puff_col"], tex="fur", tex_amp=0.4) or belly,
              z=4, g=tg, tuft=8, tuft_len=2.5)
        tip = (tx + 3, ty - 3, 3)
    a["tip"] = tip
    if tip and s["tail_tip"] == "flame":
        flame(c, tip[0], tip[1] + 2, 20 * tl, 6, t, z=-10)
    elif tip and s["tail_tip"] == "tuft":
        c.ell(tip[0], tip[1], 4, 5, acc, z=-10, tuft=6, tuft_len=2)

    # ---- far legs
    far_dx, far_dy = 6, -3
    fl = [(bx - rx * 0.55, "front"), (bx + rx * 0.55, "back")]
    for lx, kind in fl:
        _leg(c, s, mats, lx + far_dx, by + far_dy + ry * 0.2, G - 1, L, kind, z=-8, far=True, t=t)

    # ---- body
    g = c.group()
    a["g_body"] = g
    tuft = 10 if s["tuft"] else 0
    c.ell(bx, by, rx, ry, fur, z=0, g=g, tuft=tuft, tuft_len=2.5, tuft_arc=(190, 350))
    c.ell(bx - rx * 0.55, by - ry * 0.05, rx * 0.5, ry * 1.05, fur, z=2, g=g)   # chest
    c.ell(bx + rx * 0.55, by - ry * 0.05, rx * 0.48, ry * 0.95, fur, z=1, g=g)  # hips
    c.ell(bx - rx * 0.2, by + ry * 0.55, rx * 0.7, ry * 0.45, belly, g=g, decal=True, only=g)
    if s["stripes"]:
        c.pattern(lambda x, y: ((x - y * 0.45) % 9 < 2.2) & (y < by + ry * 0.2) & (x > bx - rx * 0.4), -2, only=g)
    if s["spots"]:
        sc = s["spots"]
        c.pattern(lambda x, y: (((x * 0.37 + y * 0.11) % 5 < 1.6) & ((y * 0.41 - x * 0.07) % 4.6 < 1.7)), sc, only=g)

    # ---- mane / wool (on the body, before head)
    if s["mane"] == "wool":
        wm = M(s.get("wool_col", "#efe8dc"), tex="fur", tex_amp=0.4, spec=0.1)
        mats["wool"] = wm
        wg = c.group()
        for i, (ox, oy, rr) in enumerate([(-0.6, -0.4, 0.45), (-0.1, -0.6, 0.5), (0.45, -0.45, 0.48),
                                          (0.7, 0.05, 0.4), (-0.75, 0.1, 0.42), (0.1, 0.0, 0.55),
                                          (-0.35, 0.2, 0.45), (0.45, 0.3, 0.4)]):
            c.ell(bx + ox * rx * 0.95, by + oy * ry * 0.9, rr * ry * 1.5, rr * ry * 1.35, wm, z=ry * 0.3 + i % 3, g=wg,
                  tuft=7, tuft_len=1.5)
    if s["mane"] == "shag":
        sm = M(s.get("shag_col", s["fur"]), tex="fur", tex_amp=0.6)
        c.ell(bx - rx * 0.55, by - ry * 0.3, rx * 0.58, ry * 1.05, sm, z=6, tuft=12, tuft_len=4,
              tuft_arc=(60, 300))

    # ---- near legs
    for lx, kind in fl:
        _leg(c, s, mats, lx, by + ry * 0.3, G, L, kind, z=10, far=False, t=t)

    # ---- neck + head
    nr = s["neck_r"] or min(hry, ry) * 0.7
    hg = c.group()
    a["g_head"] = hg
    c.cap(bx - rx * 0.6, by - ry * 0.3, nr, hx_ + hrx * 0.25, hy_ + hry * 0.2, nr * 0.85, fur, z=6, z1=12)
    if s["mane"] == "flame":
        mg = c.group()
        mcx, mcy = hx_ + hrx * 0.35, hy_ + hry * 0.1
        for i in range(9):
            ang = math.radians(-200 + i * 32 + [0, 5, 9, 4][t])
            mx = mcx + math.cos(ang) * hrx * 1.3
            my = mcy + math.sin(ang) * hry * 1.35
            flame(c, mx, my + 5, hry * 0.9 + (i % 2) * 5, hrx * 0.3, (t + i) % 4, z=3,
                  lean=math.cos(ang) * 0.5)
        c.ell(mcx, mcy, hrx * 1.45, hry * 1.5, M("#c8401c", tex="fur", tex_amp=0.6),
              z=6, th=3, g=mg, tuft=16, tuft_len=4)
        c.ell(mcx, mcy, hrx * 1.1, hry * 1.15, M("#e8702a", tex="fur", tex_amp=0.5),
              z=8, th=3, g=mg, tuft=14, tuft_len=3)
    if s["mane"] == "fluff":
        fm = M(s.get("fluff_col", s["belly"]), tex="fur", tex_amp=0.4)
        c.ell(hx_ + hrx * 0.5, hy_ + hry * 0.8, hrx * 0.95, hry * 0.8, fm, z=10, tuft=12, tuft_len=3,
              tuft_arc=(20, 200))
    _head(c, s, mats, a, hg, t)

    for fn in s["extras"]:
        fn(c, a, t, mats)
    return c


def _leg(c, s, mats, x, y, G, L, kind, z, far, t):
    fur, hoof, belly = mats["fur"], mats["hoof"], mats["belly"]
    r = s["leg_r"] * (0.9 if far else 1.0)
    g = c.group()
    feet = s["feet"]
    if kind == "front":
        pts = [(x, y, r * 1.35), (x - 1, y + L * 0.55, r), (x - 2, G - r * 0.6, r * 0.8)]
    else:
        pts = [(x, y - 2, r * 1.6), (x + 4, y + L * 0.45, r * 1.05), (x + 1, y + L * 0.7, r * 0.8),
               (x, G - r * 0.6, r * 0.8)]
    c.chain(pts, fur, z=z, g=g)
    fx_, fy_ = pts[-1][0], G - 1
    if feet == "hoof":
        c.cap(fx_ + 0.5, fy_ - r * 1.4, r * 0.85, fx_ - 0.5, fy_ - r * 0.3, r * 0.95, hoof, z=z + 2)
    elif feet == "claw":
        c.ell(fx_ - 1.5, fy_ - r * 0.5, r * 1.25, r * 0.7, belly if s.get("pale_paws") else fur, z=z + 3)
        cm = mats["horn"]

        def claws(cc, fx_=fx_, fy_=fy_, r=r):
            for k in range(3):
                cc.put(fx_ - r - 1 + k * 2, fy_, cm.colors[-2])
                cc.put(fx_ - r - 2 + k * 2, fy_, cm.colors[2])
        c.ink(claws)
    else:
        c.ell(fx_ - 1.5, fy_ - r * 0.45, r * 1.2, r * 0.62, belly if s.get("pale_paws") else fur, z=z + 3)


def _head(c, s, mats, a, hg, t):
    fur, belly, ear_in, horn = mats["fur"], mats["belly"], mats["ear_in"], mats["horn"]
    hx_, hy_, hrx, hry = a["hx"], a["hy"], a["hrx"], a["hry"]
    ht = s["head_type"]
    es = s["ear_size"]
    z = 14

    # ears behind/around head (far ear first)
    ears = s["ears"]
    if ears in ("cat", "fox"):
        tall = 1.25 if ears == "fox" else 1.0
        for k, (ex, lean, zz) in enumerate(((hx_ + hrx * 0.45, 0.35, z - 3), (hx_ - hrx * 0.35, -0.3, z + 2))):
            h = hry * 1.25 * es * tall
            w = hrx * 0.42 * es
            base_y = hy_ - hry * 0.55
            tipx = ex + lean * h * 0.4
            c.poly([(ex - w, base_y + 4), (tipx, base_y - h), (ex + w, base_y + 2)], fur, z=zz, bevel=2)
            c.poly([(ex - w * 0.55, base_y + 2), (tipx + (0.5 if lean > 0 else -0.5), base_y - h * 0.7),
                    (ex + w * 0.55, base_y + 1)], ear_in, z=zz + 2, bevel=1)
    elif ears == "long":
        for k, (ex, ang, zz) in enumerate(((hx_ + hrx * 0.35, 18, z - 3), (hx_ - hrx * 0.1, 6, z + 2))):
            h = hry * 2.3 * es
            sw = [0, 1, 2, 1][t] * (1 if k else -1)
            ang_r = math.radians(ang + sw)
            tx_, ty_ = ex + math.sin(ang_r) * h, hy_ - hry * 0.4 - math.cos(ang_r) * h
            c.cap(ex, hy_ - hry * 0.4, hrx * 0.32 * es, tx_, ty_, hrx * 0.22 * es, fur, z=zz)
            c.cap(ex, hy_ - hry * 0.4 - 3, hrx * 0.14 * es, tx_ - 0.5, ty_ + 3, hrx * 0.1 * es, ear_in, z=zz + 3)
            a.setdefault("ear_tips", []).append((tx_, ty_))
    elif ears == "round":
        for ex, zz in ((hx_ + hrx * 0.5, z - 3), (hx_ - hrx * 0.3, z + 2)):
            c.ell(ex, hy_ - hry * 0.75, hrx * 0.38 * es, hry * 0.4 * es, fur, z=zz)
            c.ell(ex, hy_ - hry * 0.72, hrx * 0.22 * es, hry * 0.24 * es, ear_in, z=zz + 3)
    elif ears == "floppy":
        for ex, zz in ((hx_ + hrx * 0.55, z - 3), (hx_ - hrx * 0.2, z + 6)):
            c.cap(ex, hy_ - hry * 0.5, hrx * 0.28 * es, ex + 3, hy_ + hry * 0.5 * es, hrx * 0.32 * es, fur, z=zz)
    elif ears == "cow":
        for ex, d, zz in ((hx_ + hrx * 0.75, 1, z - 3), (hx_ - hrx * 0.55, -1, z + 3)):
            c.ell(ex + d * hrx * 0.35, hy_ - hry * 0.35, hrx * 0.42 * es, hry * 0.2 * es, fur, z=zz,
                  rot=-d * 15)
            c.ell(ex + d * hrx * 0.35, hy_ - hry * 0.35, hrx * 0.25 * es, hry * 0.1 * es, ear_in, z=zz + 2,
                  rot=-d * 15)
    elif ears == "tiny":
        for ex, zz in ((hx_ + hrx * 0.4, z - 3), (hx_ - hrx * 0.25, z + 2)):
            c.ell(ex, hy_ - hry * 0.85, hrx * 0.2 * es, hry * 0.2 * es, fur, z=zz)

    # skull
    c.ell(hx_, hy_, hrx, hry, fur, z=z, g=hg, tuft=11 if s["tuft"] else 0, tuft_len=3,
          tuft_arc=(95, 250))
    sn = s["snout"]
    nose_x, nose_y = hx_ - hrx * 0.62, hy_ + hry * 0.35
    if ht == "cat":
        c.ell(hx_ - hrx * 0.45, hy_ + hry * 0.5, hrx * 0.55, hry * 0.38, belly, g=hg, decal=True, only=hg)
        c.ell(hx_ - hrx * 0.5, hy_ + hry * 0.45, hrx * 0.38, hry * 0.28, belly, z=z + hry * 0.9, th=3, g=hg)
        nose_x, nose_y = hx_ - hrx * 0.55, hy_ + hry * 0.28
    elif ht in ("dog", "rodent", "mole"):
        L = sn or hrx * 0.9
        tipr = hry * (0.28 if ht == "dog" else 0.18)
        c.cap(hx_ - hrx * 0.3, hy_ + hry * 0.25, hry * 0.5, hx_ - hrx * 0.4 - L, hy_ + hry * 0.4, tipr, fur,
              z=z + 4, z1=z + 6, g=hg)
        c.cap(hx_ - hrx * 0.3, hy_ + hry * 0.55, hry * 0.3, hx_ - hrx * 0.4 - L * 0.9, hy_ + hry * 0.55,
              tipr * 0.8, belly, g=hg, decal=True, only=hg)
        nose_x, nose_y = hx_ - hrx * 0.4 - L - tipr * 0.3, hy_ + hry * 0.3
    elif ht == "deer":
        L = sn or hrx * 0.9
        c.cap(hx_ - hrx * 0.2, hy_ + hry * 0.1, hry * 0.62, hx_ - hrx * 0.4 - L, hy_ + hry * 0.5, hry * 0.32,
              fur, z=z + 3, z1=z + 5, g=hg)
        c.ell(hx_ - hrx * 0.4 - L * 0.9, hy_ + hry * 0.55, hry * 0.36, hry * 0.3, belly, g=hg, decal=True, only=hg)
        nose_x, nose_y = hx_ - hrx * 0.4 - L - hry * 0.2, hy_ + hry * 0.38
    elif ht == "goat":
        L = sn or hrx * 0.8
        c.cap(hx_ - hrx * 0.2, hy_ + hry * 0.1, hry * 0.6, hx_ - hrx * 0.3 - L, hy_ + hry * 0.6, hry * 0.34,
              fur, z=z + 3, z1=z + 5, g=hg)
        nose_x, nose_y = hx_ - hrx * 0.3 - L - hry * 0.2, hy_ + hry * 0.5
        if s.get("beard", True):
            c.cap(hx_ - hrx * 0.2 - L * 0.7, hy_ + hry * 0.8, 2.5, hx_ - hrx * 0.15 - L * 0.7, hy_ + hry * 1.5, 1.0,
                  belly, z=z + 6)
    elif ht == "bovine":
        c.ell(hx_ - hrx * 0.55, hy_ + hry * 0.45, hrx * 0.62, hry * 0.5, belly, z=z + hry * 0.7, th=4, g=hg)
        nose_x, nose_y = hx_ - hrx * 0.95, hy_ + hry * 0.4
    a["nose"] = (nose_x, nose_y)

    # horns
    hs = s["horn_size"]
    hn = s["horns"]
    if hn:
        _horns(c, s, mats, a, hn, hs, z, t)

    ek = s["eye_kind"]
    es_ = s["eye_size"]
    eye_iris = hx(s["eye"])
    nose_col = hx(s["nose_col"])

    def face(cc):
        if ht == "cat":
            ex1, ey = hx_ - hrx * 0.52, hy_ - hry * 0.08
            ex2 = hx_ + hrx * 0.28
            peye(cc, ex1, ey, 3.6 * es_, 4.6 * es_, iris=eye_iris, slit=s["slit"], angry=s["angry"])
            peye(cc, ex2, ey, 3.2 * es_, 4.4 * es_, iris=eye_iris, slit=s["slit"], angry=s["angry"])
            nx, ny = int(nose_x), int(nose_y)
            for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1)):
                cc.put(nx + dx, ny + dy, nose_col)
            cc.put(nx, ny + 2, nose_col)
            cc.put(nx - 1, ny + 3, nose_col)
            cc.put(nx + 1, ny + 3, nose_col)
            if s.get("whiskers", True):
                wc = mix(s["belly"], (255, 255, 255), 0.5)
                for i in range(5):
                    cc.put(nx - 6 - i, ny + 1 + i // 3, wc)
                    cc.put(nx - 6 - i, ny + 4 + i // 2, wc)
        elif ht == "bovine":
            ex1, ey = hx_ - hrx * 0.25, hy_ - hry * 0.25
            peye(cc, ex1, ey, 2.6 * es_, 3.2 * es_, iris=eye_iris, angry=s["angry"])
            peye(cc, hx_ + hrx * 0.45, ey, 2.2 * es_, 3.0 * es_, iris=eye_iris, angry=s["angry"])
            for dy in (0, 1):
                cc.put(int(nose_x) + 2, int(nose_y) + dy, nose_col)
                cc.put(int(nose_x) + 6, int(nose_y) + dy + 1, nose_col)
        elif ht == "mole":
            nx, ny = int(round(nose_x)), int(round(nose_y))
            pk = (240, 150, 160)
            for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (-1, -1), (-1, 1), (-2, 0)):
                cc.put(nx + dx, ny + dy, pk)
            cc.put(nx, ny, (255, 210, 215))
            for dx in range(3):
                cc.put(hx_ - hrx * 0.35 + dx, hy_ - hry * 0.2, (30, 20, 18))
        else:
            ex1, ey = hx_ - hrx * 0.35, hy_ - hry * 0.15
            peye(cc, ex1, ey, 3.0 * es_, 3.8 * es_, iris=eye_iris, slit=s["slit"], angry=s["angry"])
            if ht in ("rodent", "mole", "dog", "cat"):
                peye(cc, hx_ + hrx * 0.35, ey, 2.4 * es_, 3.4 * es_, iris=eye_iris, slit=s["slit"],
                     angry=s["angry"])
            nx, ny = int(round(nose_x)), int(round(nose_y))
            for dx, dy in ((0, 0), (1, 0), (0, 1), (1, 1), (-1, 0)):
                cc.put(nx + dx, ny + dy, nose_col)
            cc.put(nx, ny - 1, mix(nose_col, (255, 255, 255), 0.5))
            if ht in ("dog", "deer", "goat"):
                for i in range(4):
                    cc.put(nx + 2 + i, ny + 3 + (i > 1), mix(nose_col, (0, 0, 0), 0.2))
    if s["eye_kind"] != "none" or ht == "mole":
        c.ink(face)


def _horns(c, s, mats, a, hn, hs, z, t):
    horn = mats["horn"]
    hx_, hy_, hrx, hry = a["hx"], a["hy"], a["hrx"], a["hry"]
    if hn in ("ram", "trumpet"):
        for k, (cx, cy, zz, sc) in enumerate(((hx_ + hrx * 0.45, hy_ - hry * 0.35, z - 2, 0.85),
                                              (hx_ + hrx * 0.05, hy_ - hry * 0.25, z + 8, 1.0))):
            R = hry * 0.95 * hs * sc
            pts = []
            for i in range(9):
                ang = math.radians(-120 + i * 42)
                rr = R * (1 - i * 0.075)
                pts.append((cx + math.cos(ang) * rr + R * 0.3, cy + math.sin(ang) * rr + R * 0.25,
                            R * 0.34 * (1 - i * 0.07)))
            c.chain(pts, horn, z=zz, g=c.group())
            c.pattern(lambda x, y, cx=cx, cy=cy, R=R: ((((x - cx) ** 2 + (y - cy) ** 2) ** 0.5) % 3 < 1)
                      & ((x - cx - R * 0.3) ** 2 + (y - cy - R * 0.25) ** 2 < (R * 1.4) ** 2), -1, where=[horn])
            if hn == "trumpet":
                ex, ey = pts[-1][0], pts[-1][1]
                c.ell(ex - 2, ey + 1, R * 0.35, R * 0.45, horn, z=zz + 4, rot=20)
    elif hn in ("bull", "crescent"):
        for k, (d, zz) in enumerate(((1, z - 2), (-1, z + 8))):
            bx0 = hx_ + d * hrx * 0.45
            by0 = hy_ - hry * 0.55
            L = hrx * 1.3 * hs
            if hn == "bull":
                pts = [(bx0, by0, hry * 0.2 * hs), (bx0 + d * L * 0.6, by0 - L * 0.15, hry * 0.16 * hs),
                       (bx0 + d * L * 0.85, by0 - L * 0.6, hry * 0.08 * hs)]
            else:
                pts = [(bx0, by0, hry * 0.18 * hs), (bx0 + d * L * 0.5, by0 - L * 0.1, hry * 0.2 * hs),
                       (bx0 + d * L * 0.75, by0 - L * 0.5, hry * 0.15 * hs),
                       (bx0 + d * L * 0.5, by0 - L * 0.95, hry * 0.05 * hs)]
            c.chain(pts, horn, z=zz, g=c.group())
    elif hn in ("antler", "bolt"):
        for k, (d, zz, sc) in enumerate(((1, z - 3, 0.85), (-1, z + 6, 1.0))):
            bx0 = hx_ + (0.35 if d > 0 else -0.1) * hrx
            by0 = hy_ - hry * 0.7
            H = hry * 2.2 * hs * sc
            g = c.group()
            lean = 0.35 if d > 0 else 0.15
            if hn == "antler":
                main = [(bx0, by0, 2.2), (bx0 + H * lean * 0.5, by0 - H * 0.5, 1.8),
                        (bx0 + H * lean, by0 - H, 1.2)]
                c.chain(main, horn, z=zz, g=g)
                for f in (0.35, 0.65, 0.9):
                    px_ = bx0 + H * lean * f
                    py_ = by0 - H * f
                    c.cap(px_, py_, 1.5, px_ - H * 0.22, py_ - H * 0.2, 0.8, horn, z=zz, g=g)
                a.setdefault("antler_tips", []).append((bx0 + H * lean, by0 - H))
            else:
                zig = [(bx0, by0, 2.0), (bx0 - 3, by0 - H * 0.3, 1.8), (bx0 + 4, by0 - H * 0.5, 1.6),
                       (bx0 - 2, by0 - H * 0.8, 1.3), (bx0 + 3, by0 - H, 0.8)]
                c.chain(zig, horn, z=zz, g=g)
                c.cap(bx0 + 4, by0 - H * 0.5, 1.4, bx0 + 11, by0 - H * 0.7, 0.7, horn, z=zz, g=g)
                c.cap(bx0 - 3, by0 - H * 0.3, 1.4, bx0 - 10, by0 - H * 0.5, 0.7, horn, z=zz, g=g)
                a.setdefault("antler_tips", []).append((bx0 + 3, by0 - H))
    elif hn == "goat":
        for d, zz in ((1, z - 2), (-1, z + 8)):
            bx0 = hx_ + (0.4 if d > 0 else 0.0) * hrx
            by0 = hy_ - hry * 0.7
            H = hry * 1.4 * hs
            c.chain([(bx0, by0, 2.6 * hs), (bx0 + H * 0.3, by0 - H * 0.6, 2.0 * hs), (bx0 + H * 0.75, by0 - H * 0.85, 0.8)],
                    horn, z=zz, g=c.group())
    elif hn == "broken":
        for d, zz, L in ((1, z - 2, 0.8), (-1, z + 8, 0.55)):
            bx0 = hx_ + d * hrx * 0.45
            by0 = hy_ - hry * 0.55
            Ln = hrx * 1.4 * hs * L
            c.chain([(bx0, by0, hry * 0.22 * hs), (bx0 + d * Ln * 0.6, by0 - Ln * 0.2, hry * 0.18 * hs),
                     (bx0 + d * Ln * 0.8, by0 - Ln * 0.55, hry * 0.15 * hs)], horn, z=zz, g=c.group())
        # crown of shards
        for i in range(5):
            px_ = hx_ - hrx * 0.4 + i * hrx * 0.25
            c.tri((px_ - 2, hy_ - hry * 0.8), (px_ + 0.5, hy_ - hry * 1.3 - (i % 2) * 3), (px_ + 3, hy_ - hry * 0.8),
                  horn, z=z + 6, bevel=1)
