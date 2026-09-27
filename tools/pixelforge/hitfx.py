#!/usr/bin/env python3
"""Battle hit bursts, one per crystal nature, drawn in code.

    python3 tools/pixelforge/hitfx.py                  # write public/sprites/fx/<nature>-1..4.png
    python3 tools/pixelforge/hitfx.py --preview out.png  # sheet only, no writes

The natures come from content/logic.json (quartz, jasper, diamond, citrine,
obsidian, prism, emerald, ruby, sapphire). Colors come from
content/sprites.json battleFx, so the burst and the particles that fly out of
it (drawn live by both engines) share one palette. Each nature has its own
shape so a hit reads at a glance:

    quartz    white eight-point starburst and ring
    jasper    cracked rock chunks and dust
    diamond   four-point starlight glints
    citrine   forked lightning
    obsidian  dark swirling smoke with a violet rim
    prism     rainbow rings and rays
    emerald   a whirl of leaves
    ruby      a flame burst
    sapphire  radiating ice shards

Frames: 1 impact, 2 full burst, 3 breaking up, 4 last wisps. 48x48 RGBA,
hard pixels, a dark 1px outline so the burst reads on any backdrop.
"""
from __future__ import annotations

import argparse
import json
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "public" / "sprites" / "fx"
S = 48
C = S / 2


def hx(c):
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4)) + (255,)


def pol(r, a):
    return (C + math.cos(a) * r, C + math.sin(a) * r)


def star(d, n, r0, r1, col, rot=0.0):
    pts = []
    for i in range(n * 2):
        a = rot + math.pi * i / n
        pts.append(pol(r1 if i % 2 == 0 else r0, a))
    d.polygon(pts, fill=col)


def ring(d, r, w, col):
    d.ellipse((C - r, C - r, C + r, C + r), outline=col, width=w)


def disc(d, x, y, r, col):
    d.ellipse((x - r, y - r, x + r, y + r), fill=col)


def outline(im, col=(20, 16, 24, 255)):
    """Dark 1px rim around every opaque pixel (4-neighbour)."""
    src = im.load()
    out = Image.new("RGBA", im.size, (0, 0, 0, 0))
    o = out.load()
    for y in range(S):
        for x in range(S):
            if src[x, y][3]:
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < S and 0 <= ny < S and src[nx, ny][3]:
                    o[x, y] = col
                    break
    out.alpha_composite(im)
    return out


def harden(im):
    """No half-transparent pixels: the Dreamcast keys on one color."""
    px = im.load()
    for y in range(S):
        for x in range(S):
            r, g, b, a = px[x, y]
            px[x, y] = (r, g, b, 255) if a >= 128 else (0, 0, 0, 0)
    return im


# ------------------------------------------------------------ one per nature
def quartz(d, f, col, rng):
    w, l, g = col[0], col[1], col[2]
    if f == 0:
        star(d, 4, 3, 10, w, math.pi / 4)
        disc(d, C, C, 4, w)
    elif f == 1:
        star(d, 8, 6, 22, l)
        star(d, 8, 4, 16, w, math.pi / 8)
        disc(d, C, C, 6, w)
    elif f == 2:
        ring(d, 19, 2, l)
        star(d, 8, 3, 14, g)
        star(d, 4, 2, 9, w, math.pi / 4)
    else:
        ring(d, 22, 1, g)
        for i in range(8):
            x, y = pol(20, i * math.pi / 4)
            d.rectangle((x - 1, y - 1, x, y), fill=w)


def jasper(d, f, col, rng):
    dark, mid, light = col[2], col[0], col[1]
    def chunk(cx, cy, r, c):
        pts = [(cx + math.cos(a) * r * rng.uniform(.6, 1.1), cy + math.sin(a) * r * rng.uniform(.6, 1.1))
               for a in [i * math.pi / 3 + rng.uniform(-.3, .3) for i in range(6)]]
        d.polygon(pts, fill=c)
    if f == 0:
        chunk(C, C, 9, mid)
        chunk(C - 2, C - 2, 5, light)
    elif f == 1:
        star(d, 7, 8, 20, dark, .2)
        chunk(C, C, 11, mid)
        for i in range(6):
            x, y = pol(15, i * math.pi / 3 + .4)
            chunk(x, y, 4, light)
    elif f == 2:
        for i in range(7):
            x, y = pol(17 + (i % 2) * 3, i * 2 * math.pi / 7)
            chunk(x, y + 2, 4, mid if i % 2 else light)
        disc(d, C, C + 4, 7, dark)
    else:
        for i in range(9):
            x, y = pol(21, i * 2 * math.pi / 9 + .3)
            d.rectangle((x - 1, y + 4, x + 1, y + 6), fill=mid)
        for i in range(5):
            d.rectangle((C - 12 + i * 6, C + 12 - (i % 2) * 2, C - 11 + i * 6, C + 13 - (i % 2) * 2), fill=dark)


def diamond(d, f, col, rng):
    w, blue, vio = col[0], col[1], col[2]
    def glint(x, y, r, c):
        d.polygon([(x, y - r), (x + r / 4, y - r / 4), (x + r, y), (x + r / 4, y + r / 4),
                   (x, y + r), (x - r / 4, y + r / 4), (x - r, y), (x - r / 4, y - r / 4)], fill=c)
    if f == 0:
        glint(C, C, 10, blue)
        glint(C, C, 5, w)
    elif f == 1:
        glint(C, C, 21, vio)
        glint(C, C, 15, blue)
        glint(C, C, 7, w)
        for a in (0.6, 2.2, 3.8, 5.3):
            x, y = pol(17, a)
            glint(x, y, 5, w)
    elif f == 2:
        ring(d, 16, 1, vio)
        for a in (0.2, 1.4, 2.6, 3.7, 4.9):
            x, y = pol(15, a)
            glint(x, y, 6, blue)
            glint(x, y, 3, w)
    else:
        for a in (0.9, 2.9, 4.4):
            x, y = pol(20, a)
            glint(x, y, 4, w)
        glint(C, C, 3, vio)


def citrine(d, f, col, rng):
    y1, w, o = col[0], col[1], col[2]
    def bolt(a, r, width, c):
        pts = [(C, C)]
        for k in range(1, 5):
            rr = r * k / 4
            jitter = (-1) ** k * 0.28
            pts.append(pol(rr, a + jitter))
        d.line(pts, fill=c, width=width, joint="curve")
    if f == 0:
        disc(d, C, C, 6, w)
        for i in range(4):
            bolt(i * math.pi / 2 + .3, 11, 2, y1)
    elif f == 1:
        disc(d, C, C, 8, y1)
        for i in range(6):
            bolt(i * math.pi / 3 + .2, 22, 3, o)
            bolt(i * math.pi / 3 + .2, 22, 1, w)
        disc(d, C, C, 4, w)
    elif f == 2:
        for i in range(5):
            bolt(i * 2 * math.pi / 5 + 1, 20, 2, y1)
        disc(d, C, C, 3, w)
    else:
        for i in range(3):
            x, y = pol(18, i * 2.1 + .5)
            d.line([(x - 2, y - 3), (x + 1, y), (x - 1, y + 1), (x + 2, y + 4)], fill=y1, width=1)


def obsidian(d, f, col, rng):
    blk, vio, lil = col[0], col[1], col[2]
    def swirl(r, width, c, turns=1.4, off=0.0):
        pts = [pol(r * (0.25 + 0.75 * t), off + t * turns * 2 * math.pi) for t in [i / 24 for i in range(25)]]
        d.line(pts, fill=c, width=width)
    if f == 0:
        disc(d, C, C, 8, vio)
        disc(d, C, C, 5, blk)
    elif f == 1:
        disc(d, C, C, 17, vio)
        disc(d, C, C, 14, blk)
        swirl(20, 3, lil, 1.2, 0)
        swirl(20, 3, lil, 1.2, math.pi)
        disc(d, C, C, 3, lil)
    elif f == 2:
        for i in range(6):
            x, y = pol(14, i * math.pi / 3)
            disc(d, x, y - 2, 6, vio)
            disc(d, x, y - 2, 4, blk)
        swirl(16, 2, lil, 0.9, .5)
    else:
        for i in range(4):
            x, y = pol(17, i * math.pi / 2 + .7)
            disc(d, x, y - 5, 3, vio)
            d.point((x, y - 6), fill=lil)


def prism(d, f, col, rng):
    cols = col
    if f == 0:
        for i, c in enumerate(cols):
            ring(d, 3 + i * 2, 2, c)
    elif f == 1:
        for i in range(12):
            a = i * math.pi / 6
            d.line([pol(8, a), pol(23, a)], fill=cols[i % len(cols)], width=2)
        for i, c in enumerate(cols):
            ring(d, 5 + i * 2, 2, c)
        disc(d, C, C, 3, (255, 255, 255, 255))
    elif f == 2:
        for i, c in enumerate(cols):
            ring(d, 11 + i * 2, 1, c)
        for i in range(6):
            x, y = pol(8, i * math.pi / 3)
            d.rectangle((x - 1, y - 1, x + 1, y + 1), fill=cols[i % len(cols)])
    else:
        for i in range(10):
            x, y = pol(21, i * math.pi / 5 + .3)
            d.rectangle((x, y, x + 1, y + 1), fill=cols[i % len(cols)])


def emerald(d, f, col, rng):
    g, lg, dg = col[0], col[1], col[2]
    def leaf(x, y, a, r, c):
        tip = (x + math.cos(a) * r, y + math.sin(a) * r)
        back = (x - math.cos(a) * r, y - math.sin(a) * r)
        side1 = (x + math.cos(a + math.pi / 2) * r * .45, y + math.sin(a + math.pi / 2) * r * .45)
        side2 = (x + math.cos(a - math.pi / 2) * r * .45, y + math.sin(a - math.pi / 2) * r * .45)
        d.polygon([tip, side1, back, side2], fill=c)
        d.line([back, tip], fill=dg, width=1)
    if f == 0:
        leaf(C, C, .8, 8, g)
        leaf(C, C, 2.4, 6, lg)
    elif f == 1:
        for i in range(8):
            a = i * math.pi / 4
            x, y = pol(13, a)
            leaf(x, y, a + 1.1, 7, g if i % 2 else lg)
        disc(d, C, C, 4, lg)
    elif f == 2:
        for i in range(7):
            a = i * 2 * math.pi / 7 + .5
            x, y = pol(18, a)
            leaf(x, y + 2, a + 1.5, 5, g if i % 2 else lg)
    else:
        for i in range(4):
            a = i * math.pi / 2 + 1
            x, y = pol(20, a)
            leaf(x, y + 5, a + 2, 4, lg)


def ruby(d, f, col, rng):
    red, orange, yel = col[0], col[1], col[2]
    def flame(x, y, h, w, c):
        d.polygon([(x - w, y), (x - w * .6, y - h * .5), (x, y - h), (x + w * .6, y - h * .5), (x + w, y),
                   (x, y + w * .7)], fill=c)
    if f == 0:
        flame(C, C + 5, 16, 7, red)
        flame(C, C + 5, 10, 4, yel)
    elif f == 1:
        for i, dx in enumerate((-12, 12, -6, 6)):
            flame(C + dx, C + 10, 20 - abs(dx) // 2, 6, red)
        flame(C, C + 10, 30, 11, red)
        flame(C, C + 10, 22, 8, orange)
        flame(C, C + 10, 12, 4, yel)
    elif f == 2:
        for dx in (-13, 0, 13):
            flame(C + dx, C + 8, 16, 5, red)
            flame(C + dx, C + 8, 9, 3, orange)
        for i in range(5):
            x = C - 14 + i * 7
            d.rectangle((x, C - 16 + (i % 2) * 4, x + 1, C - 15 + (i % 2) * 4), fill=yel)
    else:
        for i in range(6):
            x = C - 15 + i * 6
            y = C - 8 - (i % 3) * 5
            d.rectangle((x, y, x + 1, y + 1), fill=orange if i % 2 else yel)
        for i in range(4):
            d.rectangle((C - 9 + i * 6, C + 6 - (i % 2) * 3, C - 8 + i * 6, C + 7 - (i % 2) * 3), fill=red)


def sapphire(d, f, col, rng):
    blue, pale, w = col[0], col[1], col[2]
    def shard(a, r0, r1, wd, c):
        d.polygon([pol(r0, a), pol((r0 + r1) / 2, a + wd), pol(r1, a), pol((r0 + r1) / 2, a - wd)], fill=c)
    if f == 0:
        for i in range(4):
            shard(i * math.pi / 2 + .4, 0, 11, .5, pale)
        disc(d, C, C, 3, w)
    elif f == 1:
        for i in range(8):
            a = i * math.pi / 4 + .2
            shard(a, 2, 23 if i % 2 else 17, .22, blue)
            shard(a, 4, 15 if i % 2 else 11, .16, pale)
        disc(d, C, C, 5, w)
    elif f == 2:
        ring(d, 17, 1, pale)
        for i in range(8):
            a = i * math.pi / 4 + .6
            shard(a, 12, 22, .12, blue)
            shard(a, 14, 19, .08, w)
    else:
        for i in range(6):
            x, y = pol(20, i * math.pi / 3 + .1)
            d.polygon([(x, y - 2), (x + 1, y), (x, y + 2), (x - 1, y)], fill=pale)


DRAW = {"quartz": quartz, "jasper": jasper, "diamond": diamond, "citrine": citrine,
        "obsidian": obsidian, "prism": prism, "emerald": emerald, "ruby": ruby, "sapphire": sapphire}


def natures():
    return [n["id"] for n in json.loads((ROOT / "content" / "logic.json").read_text())["natures"]]


def palette(nat):
    fx = json.loads((ROOT / "content" / "sprites.json").read_text())["battleFx"]["natures"][nat]
    return [hx(c) for c in fx["colors"]]


def frames(nat):
    col = palette(nat)
    out = []
    for f in range(4):
        im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        DRAW[nat](ImageDraw.Draw(im), f, col, random.Random(f * 97 + len(nat)))
        out.append(outline(harden(im)))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview")
    a = ap.parse_args()
    nats = natures()
    missing = [n for n in nats if n not in DRAW]
    if missing:
        raise SystemExit("no burst drawer for nature(s): " + ", ".join(missing))
    all_frames = {n: frames(n) for n in nats}
    if a.preview:
        sc = 3
        sheet = Image.new("RGBA", (4 * S * sc + 20, len(nats) * S * sc + 20), (70, 74, 86, 255))
        for r, n in enumerate(nats):
            for c, im in enumerate(all_frames[n]):
                sheet.alpha_composite(im.resize((S * sc, S * sc), Image.NEAREST), (10 + c * S * sc, 10 + r * S * sc))
        sheet.save(a.preview)
        print("preview", a.preview)
        return
    OUT.mkdir(parents=True, exist_ok=True)
    for n, fr in all_frames.items():
        for i, im in enumerate(fr):
            im.save(OUT / f"{n}-{i + 1}.png")
    print("wrote", len(nats) * 4, "bursts to", OUT)


if __name__ == "__main__":
    main()
