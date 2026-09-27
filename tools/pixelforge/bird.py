"""Parametric bird CryMon (chicks, songbirds, hawks, owls, crows), facing left."""
from __future__ import annotations

import math

from .core import M, Mat, Canvas, flame, peye, hx, mix

DEFAULT = dict(
    seed=1, ground=121,
    pose="perch",           # perch | fly
    bx=66, body=(20, 24), tilt=-18,
    head=(13, 12), head_type="bird",   # bird | chick | owl | crow
    beak=8, beak_w=3.5, hook=False,
    wing=1.0, feathers=6, span=1.0,
    tail=18, tail_n=5, tail_up=0.0,
    leg=10,
    crest=None,             # tuft | crest | flame | spikes | ears
    body_col="#9a6a40", belly="#e8d6b0", wing_col=None, wing_tip=None, head_col=None,
    beak_col="#e8b040", leg_col="#d0902a", eye="#1a1010", eye_big=1.0, angry=0.0,
    face_col=None,          # owl facial disc
    extras=(), pre=(),
    flap=(0, 1, 2, 1),
)


def feather_rows(c, g, cx, cy, step=4, amt=-1):
    """Scalloped feather rows on a group."""
    c.pattern(lambda x, y: (((y - cy) + 0.08 * (x - cx) ** 2 / step) % step < 1.0), amt, only=g)


def build(spec, t):
    s = dict(DEFAULT)
    s.update(spec)
    c = Canvas(128, 128, seed=s["seed"])
    body = M(s["body_col"], tex="fur", tex_amp=0.3)
    belly = M(s["belly"], tex="fur", tex_amp=0.3)
    wingm = M(s["wing_col"] or s["body_col"], tex="fur", tex_amp=0.2)
    tipm = M(s["wing_tip"]) if s["wing_tip"] else wingm
    headm = M(s["head_col"], tex="fur", tex_amp=0.3) if s["head_col"] else body
    beak = M(s["beak_col"], spec=0.4, n=5)
    legm = M(s["leg_col"], n=5)
    mats = dict(body=body, belly=belly, wing=wingm, tip=tipm, head=headm, beak=beak, leg=legm)
    G = s["ground"]
    fly = s["pose"] == "fly"
    ph = s["flap"][t]
    bob = [0, 1, 2, 1][t] if not fly else [0, -2, -3, -1][t]
    rx, ry = s["body"]
    bx = s["bx"]
    by = (G - s["leg"] - ry * 0.85 + bob) if not fly else (70 + bob)
    hrx, hry = s["head"]
    ht = s["head_type"]
    tilt = s["tilt"]
    # head position: up-left of body
    if ht in ("chick", "owl"):
        hx_, hy_ = bx - rx * 0.15, by - ry * 0.75 - hry * 0.45
    else:
        hx_, hy_ = bx - rx * 0.75, by - ry * 0.85 - hry * 0.2
    hx_ += s.get("head_dx", 0) + ([0, -1, -1, 0][t] if not fly else 0)
    hy_ += s.get("head_dy", 0) + ([0, 0, 1, 1][t] if not fly else 0)
    a = dict(bx=bx, by=by, rx=rx, ry=ry, hx=hx_, hy=hy_, hrx=hrx, hry=hry, G=G, t=t)
    for fn in s["pre"]:
        fn(c, a, t, mats)

    # ---- tail feathers (behind)
    tg = c.group()
    ta = math.radians(180 + 20 + tilt * 0.5 - s["tail_up"] * 40 + [0, 4, 7, 3][t])
    tbx, tby = bx + rx * 0.7, by + ry * 0.35
    for k in range(s["tail_n"]):
        spread = (k - (s["tail_n"] - 1) / 2) * 0.12
        ang = -ta + spread + math.pi
        L = s["tail"] * (1 - abs(spread) * 1.2)
        ex = tbx + math.cos(ang) * L
        ey = tby - math.sin(ang) * L
        c.cap(tbx, tby, 3.2, ex, ey, 1.6, tipm if k % 2 else wingm, z=-10 - k * 0.3, g=tg)

    # ---- far wing
    if fly:
        _spread_wing(c, s, mats, bx + rx * 0.2, by - ry * 0.4, ph, near=False)
    # ---- legs
    if not fly:
        for k, (lx, zz) in enumerate(((bx + 3, -4), (bx - 5, 8))):
            top = by + ry * 0.7
            c.cap(lx, top, 2.2, lx - 1, G - 2, 1.4, legm, z=zz)
            for j in range(3):
                c.cap(lx - 1, G - 1.5, 1.2, lx - 5 + j * 3, G - 0.5, 0.9, legm, z=zz + 1)
    else:
        for k, (lx, zz) in enumerate(((bx + 5, -4), (bx - 2, 8))):
            top = by + ry * 0.6
            c.cap(lx, top, 2.0, lx + 5, top + 10, 1.4, legm, z=zz)
            for j in range(3):
                c.cap(lx + 5, top + 10, 1.0, lx + 2 + j * 3, top + 14, 0.7, legm, z=zz + 1)

    # ---- body
    g = c.group()
    a["g_body"] = g
    c.ell(bx, by, rx, ry, body, z=0, g=g, rot=tilt)
    c.ell(bx - rx * 0.35, by + ry * 0.2, rx * 0.72, ry * 0.8, belly, g=g, decal=True, only=g, rot=tilt)
    # ---- folded near wing
    if not fly:
        wg = c.group()
        a["g_wing"] = wg
        wx, wy = bx + rx * 0.2, by - ry * 0.05
        W = s["wing"]
        c.ell(wx, wy, rx * 0.72 * W, ry * 0.72 * W, wingm, z=rx * 0.6, g=wg, rot=tilt - 20, th=4)
        # primaries sweeping back
        for k in range(s["feathers"]):
            fx0 = wx - rx * 0.1 + k * 2
            fy0 = wy - ry * 0.35 + k * ry * 0.13
            c.cap(fx0, fy0, 3.4 - k * 0.2, fx0 + rx * 0.9 * W + k * 1.2, fy0 + ry * 0.55 * W, 1.2, tipm,
                  z=rx * 0.6 + 2 - k * 0.2, g=wg)
        feather_rows(c, wg, wx, wy, 4)
    else:
        _spread_wing(c, s, mats, bx - rx * 0.1, by - ry * 0.3, ph, near=True)

    # ---- head
    hg = c.group()
    a["g_head"] = hg
    zH = rx * 0.9
    c.ell(hx_, hy_, hrx, hry, headm, z=zH, g=hg, tuft=9 if ht == "chick" else 0, tuft_len=1.5,
          tuft_arc=(200, 330))
    if ht == "owl":
        face = M(s["face_col"] or s["belly"])
        c.ell(hx_ - hrx * 0.28, hy_ + hry * 0.05, hrx * 0.52, hry * 0.62, face, g=hg, decal=True, only=hg)
        c.ell(hx_ + hrx * 0.38, hy_ + hry * 0.05, hrx * 0.46, hry * 0.6, face, g=hg, decal=True, only=hg)
    cr = s["crest"]
    if cr == "tuft":
        for k, (dx, d) in enumerate(((-0.55, -1), (0.45, 1))):
            x0 = hx_ + dx * hrx
            y0 = hy_ - hry * 0.7
            c.cap(x0, y0, 3.0, x0 + d * 3 - 2, y0 - hry * 0.9, 0.8, headm, z=zH + 2 - k * 4)
    elif cr == "crest":
        for k in range(3):
            x0 = hx_ + hrx * 0.2 + k * 2
            c.cap(x0, hy_ - hry * 0.8, 2.0, x0 + 8 + k * 3, hy_ - hry * 1.4 - k * 2, 0.7, headm, z=zH - 2)
    elif cr == "flame":
        flame(c, hx_ + 2, hy_ - hry * 0.6, hry * 1.3, hrx * 0.35, t, z=zH - 1, lean=0.3)
    elif cr == "spikes":
        for k in range(3):
            x0 = hx_ - hrx * 0.1 + k * 4
            c.cap(x0, hy_ - hry * 0.8, 1.8, x0 + 3, hy_ - hry * 1.35 - (k % 2) * 3, 0.6, headm, z=zH - 1)

    # ---- beak
    bL, bw = s["beak"], s["beak_w"]
    if ht == "owl":
        bxx, byy = hx_ - hrx * 0.1, hy_ + hry * 0.25
        c.cap(bxx, byy - 2, bw * 0.7, bxx - 1, byy + bL * 0.5, 0.6, beak, z=zH + hry + 2)
    else:
        bxx, byy = hx_ - hrx * 0.8, hy_ + hry * 0.15
        if s["hook"]:
            c.chain([(bxx + 2, byy - 1, bw), (bxx - bL * 0.7, byy, bw * 0.55),
                     (bxx - bL, byy + bw * 0.9, 0.7)], beak, z=zH + 6)
        else:
            c.cap(bxx + 2, byy, bw, bxx - bL, byy + 1, 0.6, beak, z=zH + 6)
    a["beak"] = (bxx - bL, byy + 1)

    for fn in s["extras"]:
        fn(c, a, t, mats)

    eye_col = hx(s["eye"])
    big = s["eye_big"]

    def face(cc):
        if ht == "owl":
            for k, (dx, r) in enumerate(((-0.35, 1.0), (0.42, 0.9))):
                peye(cc, hx_ + dx * hrx, hy_ - hry * 0.05, 3.6 * big * r, 3.8 * big * r, iris=eye_col,
                     pw=0.55, ph=0.55, look=-0.2, angry=s["angry"])
        elif ht == "chick":
            peye(cc, hx_ - hrx * 0.35, hy_ - hry * 0.15, 2.6 * big, 3.4 * big, iris=eye_col, angry=s["angry"])
            peye(cc, hx_ + hrx * 0.3, hy_ - hry * 0.15, 2.2 * big, 3.2 * big, iris=eye_col, angry=s["angry"])
        else:
            peye(cc, hx_ - hrx * 0.3, hy_ - hry * 0.15, 2.4 * big, 2.8 * big, iris=eye_col, angry=s["angry"],
                 pw=0.6, ph=0.6)
    c.ink(face)
    return c


def _spread_wing(c, s, mats, sx, sy, ph, near):
    """Wing raised in a flap. ph 0..2: up .. level."""
    W = s["wing"] * s["span"]
    wingm, tipm = mats["wing"], mats["tip"]
    base_ang = [-70, -45, -20][int(ph)] if near else [-80, -58, -35][int(ph)]
    d = -1 if near else 1
    z = 20 if near else -14
    g = c.group()
    arm = 26 * W
    ang = math.radians(base_ang)
    wx = sx + d * math.cos(ang) * arm * (0.55 if not near else 0.8)
    wy = sy + math.sin(ang) * arm
    c.cap(sx, sy, 6 * W, wx, wy, 3.5 * W, wingm, z=z, g=g)
    n = s["feathers"] + 2
    for k in range(n):
        f = k / (n - 1)
        fa = ang + (0.2 + f * 1.3) * (1 if d < 0 else -1) * -1
        L = (30 - f * 12) * W
        bxk = wx + (sx - wx) * f * 0.9
        byk = wy + (sy - wy) * f * 0.9
        ex = bxk + d * math.cos(fa) * L * 0.55
        ey = byk + math.sin(fa) * L
        c.cap(bxk, byk, 3.4 * W, ex, ey, 1.4, tipm if k < 3 else wingm, z=z - k * 0.2, g=g)
    c.ell((sx + wx) / 2, (sy + wy) / 2 + 3, 9 * W, 6 * W, wingm, z=z + 3, g=g,
          rot=math.degrees(ang) * (1 if d < 0 else -1))
    feather_rows(c, g, sx, sy, 4)
