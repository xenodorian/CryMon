#!/usr/bin/env python3
"""Rebuild Shinigami's overworld walk cycles from his hand-painted art.

Painted sources (never overwritten):
  front  public/sprites/shinigami/down-1.png   (ships unchanged as down-1)
  back   public/sprites/shinigami/up-1.png     (ships unchanged as up-1)
  side   the painted stride, read from git: ae0e102:public/sprites/shinigami/left-4.png
         (no side frame keeps it pixel for pixel: every side frame gets the new boots)

Cycle, in the `% 4 + 1` walker order: 1 passing (also the idle), 2 contact, 3 passing,
4 the other contact. The motion follows a plain 4-frame walk: at contact the feet are apart
and the body is low; at passing one foot is planted under the body, the other swings through
out of sight under the robe, and the body is 1 px up. Arms swing against the legs.

Rules that keep the painting crisp (earlier versions broke these and turned to mud):
  * parts move only by whole pixels; nothing is resampled, rotated or stretched
  * a part can be stepped row by row to angle it, but only as its own masked layer
  * what a moved part uncovers comes from the robe beside or under it, never from
    repeating the part's own edge
  * new pixels use colours that are already in the painting
  * the head and shoulders never change, they only ride the bob
Side view: the painted boots are the same navy as the hem band and vanish into it, so the
boots are redrawn in the painting's own boot colours with a light toe cap and a sole line.
Front/back: frame 1 and 3 are the painting; contact frames step one painted boot out.

Run: python3 tools/shinigami_frames.py   (checks run first; nothing is written on a failure)
"""
from __future__ import annotations

import io
import subprocess
import sys

import numpy as np
from PIL import Image

from sprite_root import CANON, ROOT, assert_write

DIR = CANON / "shinigami"
PAINTED = "ae0e102:public/sprites/shinigami/{}.png"    # the hand-painted originals, in git
SIDE_SRC = PAINTED.format("left-4")
W, H, GROUND = 48, 64, 62
NOISE_ALPHA = 8          # the paintings carry invisible alpha 1-7 specks off the body


# ---------------------------------------------------------------- layer helpers
def clean(a):
    a = a.copy()
    a[a[..., 3] < NOISE_ALPHA] = 0
    return a


def load_painting(name):
    src = PAINTED.format(name)
    try:
        raw = subprocess.run(["git", "show", src], cwd=ROOT, check=True,
                             capture_output=True).stdout
    except (OSError, subprocess.CalledProcessError) as e:
        raise SystemExit(f"cannot read the painting {src} from git history "
                         f"(shallow clone? run `git fetch --unshallow`): {e}")
    return clean(np.array(Image.open(io.BytesIO(raw)).convert("RGBA")))


def load_side_painting():
    return load_painting("left-4")


def blank():
    return np.zeros((H, W, 4), np.uint8)


def over(dst, src):
    """Source-over alpha compositing, in place: soft edge pixels blend, they never punch holes."""
    m = src[..., 3] > 0
    if not m.any():
        return dst
    sa = src[m, 3:4] / 255.0
    da = dst[m, 3:4] / 255.0
    oa = sa + da * (1 - sa)
    rgb = (src[m, :3] * sa + dst[m, :3] * da * (1 - sa)) / np.maximum(oa, 1e-6)
    dst[m, :3] = np.clip(np.round(rgb), 0, 255).astype(np.uint8)
    dst[m, 3] = np.clip(np.round(oa[:, 0] * 255), 0, 255).astype(np.uint8)
    return dst


def shift(layer, dx, dy):
    """Whole-pixel move with transparent fill."""
    out = blank()
    ys, xs = np.nonzero(layer[..., 3] > 0)
    y2, x2 = ys + dy, xs + dx
    ok = (y2 >= 0) & (y2 < H) & (x2 >= 0) & (x2 < W)
    out[y2[ok], x2[ok]] = layer[ys[ok], xs[ok]]
    return out


def row_shift(layer, shifts):
    """Step a masked layer row by row: shifts = {row: dx}."""
    out = layer.copy()
    for r, dx in shifts.items():
        if dx:
            row = layer[r].copy()
            out[r] = 0
            xs = np.nonzero(row[:, 3] > 0)[0]
            ok = (xs + dx >= 0) & (xs + dx < W)
            out[r, xs[ok] + dx] = row[xs[ok]]
    return out


def keep(a, m):
    out = a.copy()
    out[~m] = 0
    return out


def rect(y0, y1, x0, x1):
    m = np.zeros((H, W), bool)
    m[y0:y1, x0:x1] = True
    return m


def lum(a):
    return 0.3 * a[..., 0] + 0.59 * a[..., 1] + 0.11 * a[..., 2]


def rgba(hexstr):
    return [int(hexstr[k:k + 2], 16) for k in (0, 2, 4, 6)]


# ---------------------------------------------------------------- side view (built facing left)
SKIRT_TOP, HEM_LAST = 45, 58        # robe rows; 58 is the last solid hem row

# Boot in the painting's own boot colours, toe at the left, 9 x 4, sole on the ground row.
BOOT_PAL = {
    "K": "101825ff", "D": "192b41ff", "M": "2b415eff", "N": "384c63ff", "O": "445c79ff",
    "L": "7c92b0ff", "H": "a0afc2ff", "S": "1e2938ff", "T": "262f3cff",
    "s": "25292d8c", "o": "15181e6e",
}
BOOT_FAR = {"H": "L", "L": "O", "O": "N"}           # far boot: one step darker, same shape
BOOT_ART = [
    ".oo.KONDK",
    "oKHLONMDK",
    "KLONMMMDK",
    "sSTSSSTSs",
]
BOOT_LIFT = {"flat": [0] * 9,
             "strike": [2, 2, 1, 1, 1, 0, 0, 0, 0],     # toe up, heel on the ground
             "push": [0, 0, 0, 0, 1, 1, 1, 2, 2]}       # heel up, toe on the ground

# The painted front boot overlapped the hem's front corner; repainted as plain hem band.
FRONT_HEM = {
    56: [None, None, "232c37c8", "1e344eff", "192b42ff", "1e344eff", "192d45ff", "1f334bff", "1e344eff"],
    57: [None, None, "2a3442a0", "162437ff", "121b29ff", "162437ff", "121e30ff", "162639ff", "14263cff"],
    58: [None, None, None, "393b4174", "2c3a4bb0", "263d5ad0", "20324ad0", "1c293ad0", "141c28f0"],
}
FRONT_HEM_X = 11

# Sleeve cuff (moves 1 px) and hand (moves the full swing): {row: (first col, last col)}.
ARM_ROWS = {38: (22, 29), 39: (22, 29), 40: (23, 30),
            41: (23, 28), 42: (23, 28), 43: (24, 28), 44: (24, 28)}

# Passing: the robe hangs narrow. Front piece (x < 21) steps back, back piece (x > 30) steps in.
PASS_FRONT = [(49, 1), (52, 2), (55, 3)]            # (from row, shift)
PASS_BACK = [(50, -1), (53, -2), (56, -3)]
# The painting's front edge has a notch where the flap met the old front boot; once the robe
# closes it reads as a 2 px bite. These even it into one slope (frame rows, after the bob).
PASS_TOUCH = {
    (51, 13): "322d2d38", (51, 14): "171f2be4",
    (52, 14): "35323551", (52, 15): "0e1927fe",
    (53, 14): "3532353c", (53, 15): "0e1215e6",
}

CENTER_TOE, FRONT_TOE, BACK_TOE = 19, 11, 26
SIDE_SPEC = {
    # bob (px up), hand (px, + = back), robe, boots back to front: (pose, toe column, far)
    1: dict(bob=1, hand=0, robe="pass", boots=[("flat", CENTER_TOE, True)]),
    2: dict(bob=0, hand=2, robe="contact", boots=[("push", BACK_TOE, True), ("strike", FRONT_TOE, False)]),
    3: dict(bob=1, hand=0, robe="pass", boots=[("flat", CENTER_TOE, False)]),
    4: dict(bob=0, hand=-2, robe="contact", boots=[("push", BACK_TOE, False), ("strike", FRONT_TOE, True)]),
}


def steps(table, r):
    s = 0
    for row, v in table:
        if r >= row:
            s = v
    return s


def side(P):
    pal = np.unique(P[P[..., 3] >= 200][:, :3].astype(int), axis=0)

    def snap(c):
        return pal[np.abs(pal - np.array(c)).sum(1).argmin()]

    def boot(pose, x, far):
        out = blank()
        for cx, lift in enumerate(BOOT_LIFT[pose]):
            for cy, row in enumerate(BOOT_ART):
                ch = BOOT_FAR.get(row[cx], row[cx]) if far else row[cx]
                if ch != ".":
                    out[GROUND - (len(BOOT_ART) - 1) + cy - lift, x + cx] = rgba(BOOT_PAL[ch])
        return out

    upper = P.copy(); upper[SKIRT_TOP:] = 0
    robe = P.copy(); robe[:SKIRT_TOP] = 0; robe[HEM_LAST + 1:] = 0
    for r, cols in FRONT_HEM.items():
        for i, c in enumerate(cols):
            robe[r, FRONT_HEM_X + i] = 0 if c is None else rgba(c)

    arm_mask = np.zeros((H, W), bool)
    for r, (x0, x1) in ARM_ROWS.items():
        arm_mask[r, x0:x1 + 1] = True
    arm, torso = keep(upper, arm_mask), keep(upper, ~arm_mask)

    # what is behind the hand: each row blends from the robe left of it to the robe right of
    # it, snapped to the painting's colours; where the arm meets the outline, the outline stays
    plate = blank()
    for r, (x0, x1) in ARM_ROWS.items():
        def beside(x, step):
            start = x
            while 0 <= x < W and torso[r, x, 3] < 200:
                x += step
                if abs(x - start) > 3:
                    return None
            return torso[r, x] if 0 <= x < W else None
        L, R = beside(x0 - 1, -1), beside(x1 + 1, 1)
        for x in range(x0, x1 + 1):
            if L is None and R is None:
                continue
            if L is None or R is None:
                c = (L if R is None else R)[:3]
            else:
                t = (x - x0 + 1) / (x1 - x0 + 2)
                c = (1 - t) * L[:3].astype(float) + t * R[:3].astype(float)
            plate[r, x] = [*snap(c), 255]
        if R is None:
            plate[r, x1] = upper[r, x1]

    def swung(s):
        sh = {r: (int(np.sign(s)) * (abs(s) // 2) if r < 41 else s) for r in ARM_ROWS}
        moved = row_shift(arm, sh)
        body = over(torso.copy(), keep(plate, arm_mask & (moved[..., 3] == 0)))   # where it left
        for r in (38, 39, 40):                 # the cuff is a band: the same band continues
            d, (x0, x1) = sh[r], ARM_ROWS[r]
            if d > 0:
                body[r, x0:x0 + d] = torso[r, x0 - 1]
            elif d < 0:
                body[r, x1 + d + 1:x1 + 1] = torso[r, x1 + 1]
        return over(body, moved)

    band = [P[r, x].copy() for r in (56, 57) for x in range(21, 30) if lum(P[r, x].astype(float)) < 60]

    def passing_robe(bob):
        front = robe.copy(); front[:, 21:] = 0
        back = robe.copy(); back[:, :31] = 0
        mid = robe.copy(); mid[:, :21] = 0; mid[:, 31:] = 0
        rows = range(SKIRT_TOP, HEM_LAST + 1)
        out = over(mid, row_shift(back, {r: steps(PASS_BACK, r) for r in rows}))
        out = over(out, row_shift(front, {r: steps(PASS_FRONT, r) for r in rows}))
        out = shift(out, 0, -bob)
        # hanging straight, the hem comes back down to row 58: a clean dark band, soft ends
        xs = np.nonzero(out[HEM_LAST - 2, :, 3] >= 128)[0]
        x0, x1 = int(xs.min()), int(xs.max())
        for r in (HEM_LAST - 1, HEM_LAST):
            a0, a1 = x0 + (r == HEM_LAST), x1 - (r == HEM_LAST)
            out[r] = 0
            for x in range(a0, a1 + 1):
                out[r, x] = band[(x * 3 + r * 5) % len(band)]
            out[r, a0 - 1] = out[r, a1 + 1] = (0x1d, 0x21, 0x28, 150)
        for (r, x), c in PASS_TOUCH.items():
            out[r, x] = rgba(c)
        return out

    frames = {}
    for i, s in SIDE_SPEC.items():
        f = blank()
        for pose, x, far in s["boots"]:
            over(f, boot(pose, x, far))
        over(f, passing_robe(s["bob"]) if s["robe"] == "pass" else shift(robe, 0, -s["bob"]))
        over(f, shift(swung(s["hand"]), 0, -s["bob"]))
        frames[i] = f
    return frames


# ---------------------------------------------------------------- front and back views
FB = {
    # the painting's single boot (rows, cols), last hem row, sleeve cuff+hand boxes (rows, cols)
    "down": dict(boot=((59, 63), (20, 25)), hem_last=58,
                 sleeves={"L": ((36, 43), (10, 16)), "R": ((36, 43), (30, 37))}),
    "up": dict(boot=((57, 63), (19, 26)), hem_last=56,
               sleeves={"L": ((37, 42), (9, 17)), "R": ((37, 42), (29, 38))}),
}
FB_STEP = 3          # the stepping boot comes this far out to its side
FB_TUCK = (2, 2)     # the other boot: this far to its side and this far up, under the robe


def front_back(P, V):
    (b0, b1), (c0, c1) = V["boot"]
    shoe = blank(); shoe[b0:b1, c0:c1] = P[b0:b1, c0:c1]
    body = P.copy(); body[V["hem_last"] + 1:] = 0
    dark_shoe = shoe.copy()
    lit = (lum(dark_shoe.astype(float)) > 90) & (dark_shoe[..., 3] > 0)
    dark_shoe[lit, :3] = (dark_shoe[lit, :3] * 0.55).astype(np.uint8)

    def sleeve(b, side, dy):
        (r0, r1), (x0, x1) = V["sleeves"][side]
        m = rect(r0, r1, x0, x1)
        part, out = keep(b, m), keep(b, ~m)
        for x in range(x0, x1):
            if dy < 0 and part[r1 - 1, x, 3] and b[r1, x, 3] >= 128:
                out[r1 - 1, x] = b[r1, x]              # the robe under the cuff shows
            if dy > 0 and part[r0, x, 3]:
                out[r0, x] = b[r0 - 1, x] if b[r0 - 1, x, 3] else b[r0, x]   # sleeve hangs lower
        return over(out, shift(part, 0, dy))

    frames = {1: P.copy(), 3: P.copy()}
    for k, side in ((2, -1), (4, 1)):                  # side -1: the viewer-left foot steps
        b = sleeve(body, "L" if side < 0 else "R", -1)  # that side's hand swings back (up)
        b = sleeve(b, "R" if side < 0 else "L", 1)      # the other hand comes forward (down)
        last = V["hem_last"]
        b = row_shift(b, {r: side for r in range(last - 2, last + 1)})   # hem leans to the step
        b = shift(b, 0, 1)                              # weight down on the step
        f = over(blank(), shift(dark_shoe, -side * FB_TUCK[0], -FB_TUCK[1]))
        over(f, b)
        over(f, shift(shoe, side * FB_STEP, 0))         # the stepping boot, in front of the hem
        frames[k] = f
    return frames


# ---------------------------------------------------------------- checks
def check(name, frames, base, bobs):
    pal = np.unique(base[base[..., 3] >= 64][:, :3].astype(int), axis=0)
    boot_pal = np.array([rgba(c)[:3] for c in BOOT_PAL.values()])
    pal = np.vstack([pal, boot_pal])
    bad = []
    for k, a in frames.items():
        rows = np.nonzero(a[..., 3].max(1) >= 64)[0]
        if rows.max() != GROUND:
            bad.append(f"{name}-{k}: lowest row {rows.max()}, ground is {GROUND}")
        dy = bobs[k]                                   # frame[y + dy] == base[y] for the head
        r0, r1 = max(0, -dy), 30
        if np.any(a[r0 + dy:r1 + dy] != base[r0:r1]):
            bad.append(f"{name}-{k}: head or shoulders changed")
        px = np.unique(a[a[..., 3] >= 128][:, :3].astype(int), axis=0)
        off = [c for c in px if np.abs(pal - c).max(1).min() > 24]
        if off:
            bad.append(f"{name}-{k}: {len(off)} colours not in the painting")
    return bad


def main():
    down, up, side_p = load_painting("down-1"), load_painting("up-1"), load_side_painting()
    left = side(side_p)
    # Front and back play as a 2-frame walk (user call, 2026-09-29): the two step frames
    # alternate, 1 = 3 = one step and 2 = 4 = the other, so no shoe slides to the centre.
    sets = {}
    for d, base in (("down", down), ("up", up)):
        f = front_back(base, FB[d])
        sets[d] = {1: f[2], 2: f[4], 3: f[2], 4: f[4]}
    bad = (check("down", sets["down"], down, {k: 1 for k in (1, 2, 3, 4)})
           + check("up", sets["up"], up, {k: 1 for k in (1, 2, 3, 4)})
           + check("left", left, side_p, {k: -s["bob"] for k, s in SIDE_SPEC.items()}))
    if bad:
        print("shinigami: checks failed, nothing written:\n  " + "\n  ".join(bad))
        return 1
    for d in ("down", "up"):
        for i in (1, 2, 3, 4):
            Image.fromarray(sets[d][i], "RGBA").save(assert_write(DIR / f"{d}-{i}.png"))
    for i, a in left.items():
        Image.fromarray(a, "RGBA").save(assert_write(DIR / f"left-{i}.png"))
        Image.fromarray(a[:, ::-1].copy(), "RGBA").save(assert_write(DIR / f"right-{i}.png"))
    print("shinigami: 16 frames rebuilt from the painted down, up and side art; checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
