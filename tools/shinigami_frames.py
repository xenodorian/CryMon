#!/usr/bin/env python3
"""Rebuild Shinigami's overworld walk frames from his hand-painted art.

Only these frames are real art (CURRENT_WORK.md, 2026-09-28): down-1, down-2,
up-1, up-2 and left-4 (right-4 is its mirror). Every other frame was a flat
leftover. This derives the missing frames from the real ones, so all four
directions have a consistent 4-frame cycle:

  down/up  1 neutral        (source)
           2 step           (source)
           3 neutral, 1px breathing dip above the waist, feet planted
           4 step on the other side (frame 2 mirrored)
  left     1 passing: feet drawn together under the body, body 1px up
           2 stride with a 1px dip above the waist
           3 passing (same as 1; the web alternates 3 and 4)
           4 stride         (source)
  right    the left frames mirrored (the source right-4 is left-4 mirrored)

Rerunnable: sources are never overwritten. Writes via sprite_root.assert_write.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image

from sprite_root import CANON, assert_write

DIR = CANON / "shinigami"
WAIST = 34          # rows above this dip 1px in the breathing frames
FOOT_TOP = 58       # side view: first row of the feet below the robe hem
FOOT_SPLIT = 22     # side view: column between the front and back foot
FOOT_SHIFT = 3      # px each foot slides toward the other in the passing pose


def load(name: str) -> np.ndarray:
    return np.array(Image.open(DIR / f"{name}.png").convert("RGBA"))


def save(a: np.ndarray, name: str) -> None:
    Image.fromarray(a, "RGBA").save(assert_write(DIR / f"{name}.png"))


def dip(a: np.ndarray, waist: int = WAIST) -> np.ndarray:
    """Upper body 1px lower; rows from the waist down (and the feet) unchanged."""
    out = a.copy()
    out[1:waist + 1] = a[0:waist]
    out[0] = 0
    return out


def mirror(a: np.ndarray) -> np.ndarray:
    return a[:, ::-1].copy()


def passing(a: np.ndarray) -> np.ndarray:
    """Side-view passing pose from a stride: feet slide together, body 1px up."""
    out = np.zeros_like(a)
    out[0:FOOT_TOP - 1] = a[1:FOOT_TOP]           # body up 1px
    out[FOOT_TOP - 1] = a[FOOT_TOP - 1]           # hem row repeated: robe hangs 1px longer
    feet = a[FOOT_TOP:]
    band = np.zeros_like(feet)
    back = feet.copy(); back[:, :FOOT_SPLIT] = 0   # rear foot: slide toward the front
    front = feet.copy(); front[:, FOOT_SPLIT:] = 0  # front foot: slide back under the body
    back = np.roll(back, -FOOT_SHIFT, axis=1); front = np.roll(front, FOOT_SHIFT, axis=1)
    for part in (back, front):                     # front foot drawn over the rear one
        m = part[..., 3] > 0
        band[m] = part[m]
    out[FOOT_TOP:] = band
    return out


def main() -> None:
    for d in ("down", "up"):
        one, two = load(f"{d}-1"), load(f"{d}-2")
        save(dip(one), f"{d}-3")
        save(mirror(two), f"{d}-4")
    stride = load("left-4")
    left = {1: passing(stride), 2: dip(stride), 3: passing(stride), 4: stride}
    for i, a in left.items():
        if i != 4:
            save(a, f"left-{i}")
        save(mirror(a), f"right-{i}")
    print("shinigami: rebuilt down-3/4, up-3/4, left-1..3, right-1..4 from the painted frames")


if __name__ == "__main__":
    main()
