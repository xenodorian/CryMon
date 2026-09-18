#!/usr/bin/env python3
"""Flood-from-edge magenta/hot-pink chroma key + 1px fringe.

Walkers, NPCs, CryMon, items, and props are always processed.
Portraits are only keyed when the image border is already magenta —
painted grey/studio portrait backgrounds stay intact.
"""
from __future__ import annotations

import math
import sys
from collections import deque
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SPRITES = ROOT / "public" / "sprites"

# Exact key plus the leftover rose/hot-pink used on some NPC sheets
# (Tessa/sentry ~ hue 317–327, (174,24,123) / (180,12,104)).
HUE_LO, HUE_HI = 300.0, 338.0
SAT_MIN = 0.42
VAL_MIN = 0.18
RGB_KEY = (255, 0, 255)
RGB_DIST = 92


def hsv(r: int, g: int, b: int) -> tuple[float, float, float]:
    rf, gf, bf = r / 255.0, g / 255.0, b / 255.0
    mx = max(rf, gf, bf)
    mn = min(rf, gf, bf)
    d = mx - mn
    if d == 0:
        h = 0.0
    elif mx == rf:
        h = (60 * ((gf - bf) / d) + 360) % 360
    elif mx == gf:
        h = (60 * ((bf - rf) / d) + 120) % 360
    else:
        h = (60 * ((rf - gf) / d) + 240) % 360
    s = 0.0 if mx == 0 else d / mx
    return h, s, mx


def is_key(r: int, g: int, b: int, a: int) -> bool:
    if a < 8:
        return True
    dr, dg, db = r - RGB_KEY[0], g - RGB_KEY[1], b - RGB_KEY[2]
    if dr * dr + dg * dg + db * db <= RGB_DIST * RGB_DIST:
        return True
    # JPEG-fringed magenta: high R+B, low G
    if r >= 140 and b >= 90 and g <= 90 and r + b - 2 * g >= 140:
        return True
    h, s, v = hsv(r, g, b)
    if HUE_LO <= h <= HUE_HI and s >= SAT_MIN and v >= VAL_MIN:
        return True
    return False


def fringe_key(r: int, g: int, b: int, a: int) -> bool:
    if a < 40:
        return True
    if is_key(r, g, b, a):
        return True
    h, s, v = hsv(r, g, b)
    # Softer edge: lower sat still counts if it touches transparency
    if 295 <= h <= 340 and s >= 0.22 and v >= 0.16:
        return True
    if r >= 120 and b >= 70 and g <= 110 and r + b - 2 * g >= 80:
        return True
    return False


def edge_key_ratio(im: Image.Image) -> float:
    px = im.convert("RGBA").load()
    w, h = im.size
    pts = []
    for x in range(w):
        pts.append((x, 0))
        pts.append((x, h - 1))
    for y in range(1, h - 1):
        pts.append((0, y))
        pts.append((w - 1, y))
    if not pts:
        return 0.0
    n = 0
    for x, y in pts:
        r, g, b, a = px[x, y]
        if is_key(r, g, b, a):
            n += 1
    return n / len(pts)


def strip_one(im: Image.Image) -> tuple[Image.Image, int]:
    im = im.convert("RGBA")
    w, h = im.size
    src = im.load()
    key = [[False] * w for _ in range(h)]
    q: deque[tuple[int, int]] = deque()
    for x in range(w):
        for y in (0, h - 1):
            r, g, b, a = src[x, y]
            if is_key(r, g, b, a):
                key[y][x] = True
                q.append((x, y))
    for y in range(1, h - 1):
        for x in (0, w - 1):
            r, g, b, a = src[x, y]
            if is_key(r, g, b, a):
                key[y][x] = True
                q.append((x, y))
    while q:
        x, y = q.popleft()
        for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if nx < 0 or ny < 0 or nx >= w or ny >= h or key[ny][nx]:
                continue
            r, g, b, a = src[nx, ny]
            if is_key(r, g, b, a):
                key[ny][nx] = True
                q.append((nx, ny))
    # 1px fringe on remaining opaque pixels that neighbor keyed/transparent
    fringe = [[False] * w for _ in range(h)]
    for y in range(h):
        for x in range(w):
            if key[y][x]:
                continue
            r, g, b, a = src[x, y]
            if a < 8:
                continue
            nkey = False
            for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                if nx < 0 or ny < 0 or nx >= w or ny >= h or key[ny][nx]:
                    nkey = True
                    break
                if src[nx, ny][3] < 8:
                    nkey = True
                    break
            if nkey and fringe_key(r, g, b, a):
                fringe[y][x] = True
    out = Image.new("RGBA", (w, h))
    dst = out.load()
    cleared = 0
    for y in range(h):
        for x in range(w):
            r, g, b, a = src[x, y]
            if key[y][x] or fringe[y][x] or a < 8:
                dst[x, y] = (0, 0, 0, 0)
                if a >= 8:
                    cleared += 1
            else:
                dst[x, y] = (r, g, b, a)
    return out, cleared


def process_file(path: Path, portraits: bool) -> tuple[bool, int]:
    im = Image.open(path)
    if portraits:
        if edge_key_ratio(im) < 0.12:
            return False, 0
    out, n = strip_one(im)
    if n == 0:
        return False, 0
    out.save(path)
    return True, n


def bbox_opaque(im: Image.Image, pad: int = 8) -> tuple[int, int, int, int]:
    px = im.load()
    w, h = im.size
    xs, ys = [], []
    for y in range(h):
        for x in range(w):
            if px[x, y][3] > 16:
                xs.append(x)
                ys.append(y)
    if not xs:
        return 0, 0, w, h
    x0, x1 = max(0, min(xs) - pad), min(w, max(xs) + pad + 1)
    y0, y1 = max(0, min(ys) - pad), min(h, max(ys) + pad + 1)
    return x0, y0, x1, y1


def make_key_icon(src: Path, dest: Path) -> None:
    im = Image.open(src)
    clean, n = strip_one(im)
    x0, y0, x1, y1 = bbox_opaque(clean, pad=24)
    crop = clean.crop((x0, y0, x1, y1))
    # Square canvas, then 128x128 like the other bag icons
    side = max(crop.size)
    canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    canvas.paste(crop, ((side - crop.size[0]) // 2, (side - crop.size[1]) // 2), crop)
    icon = canvas.resize((128, 128), Image.Resampling.LANCZOS)
    dest.parent.mkdir(parents=True, exist_ok=True)
    icon.save(dest)
    print(f"cageKey: keyed {n} px -> {dest} {icon.size}")


def walk_targets() -> list[tuple[Path, bool]]:
    out: list[tuple[Path, bool]] = []
    always = [
        SPRITES / "max",
        SPRITES / "mason",
        SPRITES / "anne",
        SPRITES / "shinigami",
        SPRITES / "npc",
        SPRITES / "monsters",
        SPRITES / "items",
        SPRITES / "props",
    ]
    for folder in always:
        if not folder.exists():
            continue
        for p in folder.rglob("*.png"):
            out.append((p, False))
    port = SPRITES / "portraits"
    if port.exists():
        for p in port.glob("*.png"):
            out.append((p, True))
    return out


def main() -> None:
    key_src = Path("/workspace/artifacts/imagine_images/72348c7a-a736-4418-8a4f-35a076cb46f5.jpg")
    if key_src.exists():
        make_key_icon(key_src, SPRITES / "items" / "cageKey.png")
    else:
        print("key source missing", file=sys.stderr)

    files = walk_targets()
    changed = 0
    pixels = 0
    skipped_port = 0
    for path, portraits in files:
        if path.name == "cageKey.png" and not portraits:
            # just written; still run strip in case LANCZOS reintroduced fringe
            pass
        ok, n = process_file(path, portraits)
        if portraits and not ok and n == 0:
            skipped_port += 1
        if ok:
            changed += 1
            pixels += n
            print(f"  {path.relative_to(SPRITES)}  -{n}")
    print(f"done: {changed} files, {pixels} pixels keyed, portraits skipped={skipped_port}")


if __name__ == "__main__":
    main()
