#!/usr/bin/env python3
"""Extract Mason's overworld walk frames from backups/assets-sprites/mason/walk-sheet.jpg.

The sheet is 12 columns x 4 rows (down, left, right, up) with a baked
white/gray checkerboard. Background is flood-keyed from the edges, then four
evenly spaced frames per row become <dir>-1..4 on a 48x64 canvas with one
shared scale so the figure matches Max's ~60px opaque height.
"""
from __future__ import annotations

from collections import deque
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "backups" / "assets-sprites" / "mason" / "walk-sheet.jpg"
OUT = ROOT / "public" / "sprites" / "mason"
DIRS = ["down", "left", "right", "up"]
PICK = [0, 3, 6, 9]
CANVAS_W, CANVAS_H = 48, 64
TARGET_H = 60
FOOT_Y = 61


def runs(v):
    out, s = [], None
    for i, b in enumerate(v):
        if b and s is None:
            s = i
        if not b and s is not None:
            out.append((s, i - 1))
            s = None
    if s is not None:
        out.append((s, len(v) - 1))
    return out


def key_background(a):
    h, w, _ = a.shape
    cand = ((a.max(2) - a.min(2)) <= 10) & (a.min(2) >= 205)
    bg = np.zeros((h, w), bool)
    dq = deque()
    for x in range(w):
        for y in (0, h - 1):
            if cand[y, x] and not bg[y, x]:
                bg[y, x] = True
                dq.append((y, x))
    for y in range(h):
        for x in (0, w - 1):
            if cand[y, x] and not bg[y, x]:
                bg[y, x] = True
                dq.append((y, x))
    while dq:
        y, x = dq.popleft()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w and cand[ny, nx] and not bg[ny, nx]:
                bg[ny, nx] = True
                dq.append((ny, nx))
    fg = ~bg
    lab = np.zeros((h, w), int)
    sizes = {}
    n = 0
    for y in range(h):
        for x in range(w):
            if fg[y, x] and not lab[y, x]:
                n += 1
                lab[y, x] = n
                q = deque([(y, x)])
                c = 0
                while q:
                    cy, cx = q.popleft()
                    c += 1
                    for dy in (-1, 0, 1):
                        for dx in (-1, 0, 1):
                            ny, nx = cy + dy, cx + dx
                            if 0 <= ny < h and 0 <= nx < w and fg[ny, nx] and not lab[ny, nx]:
                                lab[ny, nx] = n
                                q.append((ny, nx))
                sizes[n] = c
    keep = np.zeros(n + 1, bool)
    for k, v in sizes.items():
        keep[k] = v >= 60
    return fg & keep[lab]


def main():
    a = np.array(Image.open(SRC).convert("RGB")).astype(int)
    fg = key_background(a)
    rgba = np.zeros(a.shape[:2] + (4,), np.uint8)
    rgba[..., :3] = a
    rgba[..., 3] = np.where(fg, 255, 0)
    sheet = Image.fromarray(rgba)
    rows = runs(fg.any(1))
    cols = runs(fg.any(0))
    assert len(rows) == 4 and len(cols) == 12, (rows, cols)
    scale = TARGET_H / max(r1 - r0 + 1 for r0, r1 in rows)
    OUT.mkdir(parents=True, exist_ok=True)
    for d, (r0, r1) in zip(DIRS, rows):
        for n, ci in enumerate(PICK, 1):
            c0, c1 = cols[ci]
            c0 = max(0, c0 - 2)
            c1 = min(sheet.width - 1, c1 + 2)
            cell = sheet.crop((c0, r0, c1 + 1, r1 + 1))
            m = np.array(cell)[..., 3] > 0
            ys, xs = np.where(m)
            cell = cell.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
            m = m[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
            nw = max(1, round(cell.width * scale))
            nh = max(1, round(cell.height * scale))
            small = cell.convert("RGBa").resize((nw, nh), Image.LANCZOS).convert("RGBA")
            sa = np.array(small)
            sa[..., 3] = np.where(sa[..., 3] >= 128, 255, 0)
            small = Image.fromarray(sa)
            # horizontal anchor: centroid of the upper body so the walk does not jitter
            top = m[: max(1, int(m.shape[0] * 0.55))]
            cx = np.where(top)[1].mean() * scale
            canvas = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
            px = int(round(CANVAS_W / 2 - cx))
            py = FOOT_Y + 1 - nh
            canvas.alpha_composite(small, (px, py)) if 0 <= px and px + nw <= CANVAS_W else canvas.paste(small, (px, py), small)
            canvas.save(OUT / f"{d}-{n}.png")
            print(d, n, "size", (nw, nh), "x", px)


if __name__ == "__main__":
    main()
