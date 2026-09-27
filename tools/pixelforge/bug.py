"""Bug CryMon: flying insects, moths, spiders, ticks and grubs. Facing left."""
from __future__ import annotations

import math

from .core import M, Mat, Canvas, peye, hx, mix


def wing_mat(col, light=False):
    base = hx(col)
    cols = [mix(base, (30, 30, 50), 0.5), mix(base, (60, 60, 90), 0.2), base,
            mix(base, (255, 255, 255), 0.3), mix(base, (255, 255, 255), 0.6)]
    return Mat(cols, soft=0.5, spec=0.5 if light else 0.0)


def veins(c, x0, y0, x1, y1, col, n=4):
    def ink(cc):
        for k in range(n):
            f = (k + 1) / (n + 1)
            ex = x0 + (x1 - x0) + (k - n / 2) * 4
            ey = y0 + (y1 - y0) * f * 1.4
            steps = 20
            for i in range(steps):
                u = i / steps
                x = x0 + (ex - x0) * u
                y = y0 + (ey - y0) * u
                xi, yi = int(x), int(y)
                if 0 <= xi < cc.w and 0 <= yi < cc.h and cc.alpha[yi, xi]:
                    cc.put(xi, yi, col)
    c.ink(ink)


def insect(c, t, *, cx=64, cy=64, head=6, thorax=(9, 8), abdomen=(14, 10), ab_angle=20,
           body="#e0b030", body2=None, stripe=None, leg_col="#3a3020", wing="#e8f4ff", wings=2,
           wing_len=26, antenna=10, stinger=0, glow=None, eye="#2a2020", eye_r=3.0, flap=True,
           z=0, legs=True, wing_shape=(1.0, 0.45)):
    """A generic flying insect. Returns anchor dict."""
    bm = M(body, spec=0.4)
    b2 = M(body2 or body, spec=0.4)
    lm = M(leg_col, n=5)
    wm = wing_mat(wing, light=True)
    fl = [0, 1, 2, 1][t] if flap else 0
    a = {}
    # abdomen angled down-back
    ang = math.radians(ab_angle)
    ax = cx + thorax[0] * 0.6 + math.cos(ang) * abdomen[0] * 0.9
    ay = cy + math.sin(ang) * abdomen[0] * 0.9
    a["abdomen"] = (ax, ay)
    # far wings (behind)
    wx, wy = cx + 2, cy - thorax[1] * 0.6
    for k in range(wings):
        wa = math.radians(-60 + k * 25 - fl * 18)
        L = wing_len * (1 - k * 0.2)
        ex, ey = wx + math.cos(wa) * L * 0.4 + L * 0.35, wy + math.sin(wa) * L
        c.ell((wx + ex) / 2, (wy + ey) / 2, L * wing_shape[0] * 0.5, L * wing_shape[1] * 0.5, wm, z=z - 10 - k,
              rot=math.degrees(wa) + 90 - 90 * 0, th=1)
    # legs
    if legs:
        for k in range(3):
            lx = cx - 3 + k * 4
            for side, zz in ((1, z - 6), (-1, z + 8)):
                kx, ky = lx - 4 + k * 3 + side, cy + thorax[1] * 0.7 + 5
                fx_, fy_ = lx - 8 + k * 7, cy + thorax[1] + 13
                c.chain([(lx, cy + thorax[1] * 0.4, 1.5), (kx, ky, 1.2), (fx_, fy_, 0.8)], lm, z=zz)
    g = c.group()
    c.ell(ax, ay, abdomen[0], abdomen[1], b2, z=z, rot=ab_angle, g=g)
    if stripe:
        sm = M(stripe)
        c.pattern(lambda x, y: (((x - ax) * math.cos(ang) + (y - ay) * math.sin(ang)) % 6 < 2.5), 0, only=g)
        for k in range(-2, 3):
            px = ax + math.cos(ang) * k * 5.5
            py = ay + math.sin(ang) * k * 5.5
            c.ell(px, py, 1.6, abdomen[1] * 1.1, sm, decal=True, only=g, rot=ab_angle)
    if glow:
        gm = Mat([mix(glow, (80, 60, 0), 0.4), glow, mix(glow, (255, 255, 220), 0.4),
                  mix(glow, (255, 255, 255), 0.7), (255, 255, 250)], emit=True)
        c.ell(ax + abdomen[0] * 0.35, ay + abdomen[1] * 0.1, abdomen[0] * 0.65, abdomen[1] * 0.85, gm, z=z + 1,
              rot=ab_angle)
    if stinger:
        tx_, ty_ = ax + math.cos(ang) * (abdomen[0] + stinger), ay + math.sin(ang) * (abdomen[0] + stinger)
        c.cap(ax + math.cos(ang) * abdomen[0] * 0.8, ay + math.sin(ang) * abdomen[0] * 0.8, 2.2, tx_, ty_, 0.4,
              M("#2a2420", spec=0.6), z=z)
        a["stinger"] = (tx_, ty_)
    c.ell(cx, cy, thorax[0], thorax[1], bm, z=z + 3)
    hxx, hyy = cx - thorax[0] - head * 0.6, cy - 2
    c.ell(hxx, hyy, head, head * 0.95, bm, z=z + 6)
    a["head"] = (hxx, hyy)
    # antennae
    if antenna:
        for side, zz in ((1, z), (-1, z + 8)):
            c.chain([(hxx + 1 + side, hyy - head * 0.7, 1.0), (hxx - 3 + side * 2, hyy - head - antenna * 0.6, 0.8),
                     (hxx - 8 + side * 3, hyy - head - antenna, 0.8)], lm, z=zz)
    # near wings (in front)
    for k in range(wings):
        wa = math.radians(-50 + k * 25 - fl * 18)
        L = wing_len * (1 - k * 0.2)
        ex, ey = wx + math.cos(wa) * L * 0.4 + L * 0.3, wy + math.sin(wa) * L
        c.ell((wx + ex) / 2 - 2, (wy + ey) / 2, L * wing_shape[0] * 0.5, L * wing_shape[1] * 0.5, wm,
              z=z + 20 + k, rot=math.degrees(wa) + 90, th=1)
    ec = hx(eye)

    def face(cc):
        peye(cc, hxx - head * 0.25, hyy - head * 0.1, eye_r, eye_r * 1.1, iris=ec, pw=0.7, ph=0.7)
    c.ink(face)
    return a


def spider(c, t, *, cx=64, cy=86, body=(12, 10), abdomen=(20, 16), col="#2a2430", mark=None,
           leg_len=34, leg_r=2.2, eyes_col="#ff3030", hair=True, z=0, G=121):
    bm = M(col, tex="fur", tex_amp=0.4, spec=0.2)
    lm = M(col, spec=0.3)
    sw = [0, 1, 2, 1][t]
    ax, ay = cx + body[0] + abdomen[0] * 0.6, cy - abdomen[1] * 0.35
    # legs: 4 far (behind), 4 near
    for side, zz in ((1, z - 10), (-1, z + 14)):
        for k in range(4):
            bx0 = cx - body[0] * 0.3 + k * 4
            by0 = cy
            outx = (-1 if k < 2 else 1) * (leg_len * (0.55 + 0.1 * (k % 2)))
            kx = bx0 + outx * 0.55 + side * 3
            ky = cy - leg_len * 0.45 - (sw if (k + side) % 2 else 0)
            fx_ = bx0 + outx + side * 4
            fy_ = G - (1 if side < 0 else 4)
            c.chain([(bx0, by0, leg_r * 1.3), (kx, ky, leg_r), (fx_, fy_, leg_r * 0.6)], lm, z=zz + k * 0.3)
    g = c.group()
    c.ell(ax, ay, abdomen[0], abdomen[1], bm, z=z, g=g, rot=-12, tuft=14 if hair else 0, tuft_len=2)
    if mark:
        mm = M(mark, spec=0.3)
        c.ell(ax + 2, ay - abdomen[1] * 0.35, abdomen[0] * 0.3, abdomen[1] * 0.3, mm, decal=True, only=g)
        c.ell(ax + 2, ay + abdomen[1] * 0.1, abdomen[0] * 0.2, abdomen[1] * 0.25, mm, decal=True, only=g)
    c.ell(cx, cy - 2, body[0], body[1], bm, z=z + 4)
    # fangs
    fm = M("#d8d0c8", spec=0.5)
    c.cap(cx - body[0] * 0.8, cy + 2, 1.8, cx - body[0] * 0.9 - 2, cy + 8, 0.6, fm, z=z + 16)
    c.cap(cx - body[0] * 0.5, cy + 3, 1.8, cx - body[0] * 0.5 - 1, cy + 9, 0.6, fm, z=z + 16)
    ec = hx(eyes_col)

    def face(cc):
        ex, ey = cx - body[0] * 0.55, cy - body[1] * 0.45
        for dx, dy, big in ((0, 0, 1), (4, -1, 1), (-2, 3, 0), (2, 3, 0), (6, 2, 0), (8, -2, 0)):
            cc.put(ex + dx, ey + dy, ec)
            if big:
                cc.put(ex + dx + 1, ey + dy, ec)
                cc.put(ex + dx, ey + dy + 1, mix(ec, (0, 0, 0), 0.4))
                cc.put(ex + dx + 1, ey + dy + 1, mix(ec, (0, 0, 0), 0.4))
                cc.put(ex + dx, ey + dy, (255, 240, 230))
    c.ink(face)
    return dict(abdomen=(ax, ay))
