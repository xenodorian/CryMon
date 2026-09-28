#!/usr/bin/env python3
"""Rebuild Shinigami's overworld walk cycles from his hand-painted art.

Painted bases: down-1, up-1 and left-2 (the painted side stride, first shipped
as left-4). down-2/up-2 were a second, differently shaded painting (kept in git
history). Swapping between different
paintings makes the sprite flicker, so every frame of a direction is now the
SAME painted base moved by a small rig, the way the Biboo pipeline animates:
whole row/column bands shift by 1-2 px (no holes can open), feet step, the
robe hem sways from the waist, sleeves swing against the legs, the body bobs.

Cycle (the standard `% 4 + 1` walker order, 3 fps):
  1  neutral  - base; also the idle frame
  2  contact  - one foot forward, body 1px down, hem and sleeves swing
  3  passing  - feet under the body, body 1px up (idle breath on Dreamcast)
  4  contact  - the other foot forward, everything swings the other way
Front/back base: down-1 / up-1. Side base: left-2, unchanged, is the first
contact; the passing pose draws the feet together; right = left mirrored.

Rerunnable: the painted bases are never overwritten (down-2/up-2 stay as
painted reference but are regenerated from the base for a consistent cycle).
"""
from __future__ import annotations

import numpy as np
from PIL import Image

from sprite_root import CANON, assert_write

DIR = CANON / "shinigami"
SRC = {"down": "down-1", "up": "up-1", "side": "left-2"}   # left-2 is the painted stride

# front/back view geometry (48x64 frames)
FB_FEET = 58            # first row of the feet below the robe
FB_HEM = (46, 58)       # robe rows that sway: pinned at the top row, full sway at the bottom
FB_SLEEVE_L = (8, 16)   # column strips of the hanging sleeves (viewer left / right)
FB_SLEEVE_R = (31, 40)
FB_SLEEVE_ROWS = (34, 54)
# side view geometry
SD_FEET = 58            # first row below the hem
SD_SPLIT = 22           # column between the front (left) and rear foot
FEET_SLIDE = 3          # px each foot slides toward the other in the passing pose
SD_HEM = (48, 58)
SD_ARM = (18, 30)       # columns of the hanging arm and hand
SD_ARM_ROWS = (30, 44)


def load(name):
    return np.array(Image.open(DIR / f"{name}.png").convert("RGBA"))


def save(a, name):
    Image.fromarray(a, "RGBA").save(assert_write(DIR / f"{name}.png"))


def bob(a, dy, feet_top):
    """Everything above the feet moves dy px (down +). Vacated rows repeat the edge row."""
    out = a.copy()
    body = a[:feet_top]
    if dy > 0:
        out[dy:feet_top] = body[:feet_top - dy]
        out[:dy] = 0
    elif dy < 0:
        out[:feet_top + dy] = body[-dy:]
        out[feet_top + dy:feet_top] = body[-1]          # robe hangs a pixel longer
    return out


def shear(a, rows, cols, dx_top, dx_bottom):
    """Shift a band sideways by an amount that grows from the top row to the bottom row."""
    out = a.copy()
    r0, r1 = rows
    c0, c1 = cols
    for r in range(r0, r1):
        t = (r - r0) / max(r1 - 1 - r0, 1)
        dx = int(round(dx_top + (dx_bottom - dx_top) * t))
        if dx:
            src = a[r, c0:c1]
            dst = np.empty_like(src)
            if dx > 0: dst[dx:] = src[:-dx]; dst[:dx] = src[0]      # repeat the edge: no holes
            else: dst[:dx] = src[-dx:]; dst[dx:] = src[-1]
            out[r, c0:c1] = dst
    return out


def strip_shift(a, cols, rows, dy):
    """Move a column strip vertically by dy (sleeve swing); the vacated row repeats the edge."""
    out = a.copy()
    c0, c1 = cols
    r0, r1 = rows
    band = a[r0:r1, c0:c1]
    if dy > 0:
        out[r0 + dy:r1, c0:c1] = band[:-dy]; out[r0:r0 + dy, c0:c1] = band[0]
    elif dy < 0:
        out[r0:r1 + dy, c0:c1] = band[-dy:]; out[r1 + dy:r1, c0:c1] = band[-1]
    return out


def feet_shift(a, feet_top, dx, dy=0):
    out = a.copy()
    feet = a[feet_top:].copy()
    out[feet_top:] = 0
    feet = np.roll(feet, dx, axis=1)
    if dy < 0:                                        # lifted foot: keep it touching the hem
        out[feet_top + dy:feet.shape[0] + feet_top + dy] = np.where(
            feet[..., 3:4] > 0, feet, out[feet_top + dy:feet.shape[0] + feet_top + dy])
    else:
        out[feet_top:] = feet
    return out


def front_back(base):
    """4-frame cycle for the front or back view from one painted base."""
    def contact(side):                                # side +1: step to the viewer's right
        f = bob(base, 1, FB_FEET)
        f = shear(f, FB_HEM, (0, 48), 0, side * 2)
        f = feet_shift(f, FB_FEET, side)
        f = strip_shift(f, FB_SLEEVE_L, FB_SLEEVE_ROWS, -side)   # arms swing against the legs
        f = strip_shift(f, FB_SLEEVE_R, FB_SLEEVE_ROWS, side)
        return f
    return {1: base, 2: contact(+1), 3: bob(base, -1, FB_FEET), 4: contact(-1)}


def side(stride):
    """4-frame cycle for the side view (facing left) from the painted stride.

    The long robe hides the legs, so the step reads through the feet under the hem, the body
    bob, the arm and the hem. Both contacts keep the painted feet (redrawing the far foot in
    front tears the hem); the second contact swings the arm forward and the hem back."""
    feet = stride[SD_FEET:]
    front = feet.copy(); front[:, SD_SPLIT:] = 0      # leading foot (facing left)
    rear = feet.copy(); rear[:, :SD_SPLIT] = 0

    def together(a):
        out = a.copy(); band = np.zeros_like(feet)
        for part in (np.roll(rear, -FEET_SLIDE, axis=1), np.roll(front, FEET_SLIDE, axis=1)):
            m = part[..., 3] > 0
            band[m] = part[m]
        out[SD_FEET:] = band
        return out

    p = together(bob(stride, -1, SD_FEET))                    # passing: feet under the body, up 1px
    b = shear(stride, SD_ARM_ROWS, SD_ARM, 0, -1)             # arm swings forward
    b = shear(b, SD_HEM, (0, 48), 0, 1)                       # hem trails back
    return {1: p, 2: stride, 3: p, 4: b}


def main():
    bases = {k: load(v) for k, v in SRC.items()}      # read every base before writing
    for d in ("down", "up"):
        for i, f in front_back(bases[d]).items():
            if i != 1:
                save(f, f"{d}-{i}")
    for i, f in side(bases["side"]).items():
        if i != 2:
            save(f, f"left-{i}")
        save(f[:, ::-1].copy(), f"right-{i}")
    print("shinigami: walk cycles rebuilt from down-1, up-1 and left-2")


if __name__ == "__main__":
    main()
