#!/usr/bin/env python3
"""PLACEHOLDER_ART: stand-in overworld sprites for new NPCs.

    python3 tools/make_placeholder_npcs.py harrow nero weepingGuard ...

Writes public/sprites/npc/<id>-1..4.png (48x64, the size every other NPC
walker uses) and a 160x200 dialogue portrait at public/sprites/portraits/
<id>.png (a zoomed bust of the same figure): a plain standing figure in the colors given in STYLE below,
bobbing across the 4 idle frames, with a magenta "PH" tag so nobody takes
it for finished art. Real art (Grok) replaces the same paths later.
Refuses to overwrite an existing PNG unless --force is given.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sprite_root import CANON, assert_write  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
W, H = 48, 64
BOB = [0, -1, -2, -1]
SKIN = (222, 184, 150)
INK = (24, 20, 16)

# id -> (uniform, trim, hat): hat is "cap", "peaked" (officer), "crown",
# "hood" or "none".
STYLE = {
    "weepingGuard": ((70, 72, 78), (40, 40, 44), "cap"),
    "royalGuard": ((96, 30, 40), (200, 170, 70), "cap"),
    "harrow": ((110, 84, 52), (212, 176, 64), "peaked"),
    "ashgrove": ((104, 96, 44), (212, 176, 64), "peaked"),
    "stroud": ((84, 70, 110), (212, 176, 64), "peaked"),
    "vale": ((44, 40, 54), (212, 176, 64), "peaked"),
    "kessler": ((120, 44, 36), (212, 176, 64), "peaked"),
    "morrow": ((40, 70, 118), (212, 176, 64), "peaked"),
    "crane": ((150, 150, 144), (212, 176, 64), "peaked"),
    "blackwood": ((46, 86, 50), (212, 176, 64), "peaked"),
    "sorrel": ((70, 84, 150), (230, 230, 240), "peaked"),
    "nero": ((60, 20, 70), (230, 190, 60), "crown"),
    # Malkuth (narrative fix pass): healer, merchant, elder, and one shared
    # townsperson look for the freed citizen in each General's city.
    "ada": ((226, 226, 214), (60, 140, 90), "none"),
    "hale": ((140, 96, 50), (90, 60, 30), "cap"),
    "marn": ((96, 90, 110), (200, 200, 200), "hood"),
    "citizen": ((120, 110, 80), (160, 140, 100), "none"),
    # Ghost Guild arc: grave-warden Vesk, a bound ghost, and two props drawn
    # as objects rather than people ("grave" / "shrine" shapes).
    "vesk": ((34, 30, 36), (120, 110, 130), "hood"),
    "ghost": ((196, 206, 222), (150, 164, 190), "ghost"),
    "grave": ((128, 124, 118), (84, 80, 76), "grave"),
    "shrine": ((150, 120, 90), (190, 60, 50), "shrine"),
    # Heroes Guild (blue and silver), Thieves Guild (dark, red trim), outlaws.
    "ardent": ((40, 70, 150), (220, 220, 230), "peaked"),
    "pell": ((70, 100, 170), (220, 220, 230), "none"),
    "aldous": ((60, 90, 160), (200, 170, 70), "cap"),
    "brin": ((50, 80, 140), (200, 170, 70), "none"),
    "rook": ((30, 60, 120), (230, 230, 240), "peaked"),
    "mag": ((50, 30, 40), (170, 40, 40), "hood"),
    "fingers": ((70, 60, 50), (170, 40, 40), "cap"),
    "mallory": ((150, 40, 40), (60, 30, 20), "hood"),
    "silas": ((90, 80, 60), (150, 130, 60), "cap"),
    # Townsfolk archetypes (named townsfolk share these; sprites.json
    # portraitAlias maps each speaker to one) and a quest-item sparkle.
    "townsman": ((110, 96, 70), (80, 60, 40), "cap"),
    "townswoman": ((150, 90, 110), (110, 70, 50), "none"),
    "elder": ((120, 120, 120), (220, 220, 220), "none"),
    "child": ((90, 140, 90), (120, 80, 40), "none"),
    "bandit": ((60, 50, 40), (140, 40, 40), "hood"),
    "pickup": ((230, 200, 90), (255, 250, 200), "pickup"),
}


def font(size: int):
    try:
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)
    except Exception:
        return ImageFont.load_default()


def frame(uniform, trim, hat: str, bob: int) -> Image.Image:
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    y = 6 + bob
    if hat == "pickup":
        d.ellipse([16, 40 + bob, 32, 52 + bob], fill=(120, 90, 50), outline=INK)  # pouch
        d.rectangle([22, 36 + bob, 26, 41 + bob], fill=(90, 60, 30))
        for sx, sy in ((12, 30), (34, 28), (24, 22)):
            d.line([(sx - 3, sy + bob), (sx + 3, sy + bob)], fill=trim)
            d.line([(sx, sy - 3 + bob), (sx, sy + 3 + bob)], fill=trim)
        return tag(im, d)
    if hat in ("grave", "shrine"):
        return prop(im, d, uniform, trim, hat)
    if hat == "ghost":
        d.ellipse([12, y + 4, 36, y + 28], fill=uniform + (200,), outline=trim)
        d.polygon([(12, y + 16), (36, y + 16), (36, y + 50), (30, y + 44), (24, y + 52), (18, y + 44), (12, y + 50)],
                  fill=uniform + (200,), outline=trim)
        d.ellipse([18, y + 12, 22, y + 17], fill=INK)
        d.ellipse([26, y + 12, 30, y + 17], fill=INK)
        return tag(im, d)
    # legs, body, arms
    d.rectangle([17, y + 40, 22, y + 55], fill=INK)
    d.rectangle([26, y + 40, 31, y + 55], fill=INK)
    d.rectangle([14, y + 20, 34, y + 42], fill=uniform, outline=INK)
    d.rectangle([10, y + 21, 14, y + 38], fill=uniform, outline=INK)
    d.rectangle([34, y + 21, 38, y + 38], fill=uniform, outline=INK)
    d.rectangle([14, y + 20, 34, y + 23], fill=trim)
    # head
    d.ellipse([16, y + 4, 32, y + 20], fill=SKIN, outline=INK)
    d.point([(21, y + 12), (27, y + 12)], fill=INK)
    if hat == "crown":
        d.polygon([(16, y + 7), (18, y - 1), (21, y + 4), (24, y - 3), (27, y + 4), (30, y - 1), (32, y + 7)],
                  fill=trim, outline=INK)
    elif hat == "hood":
        d.pieslice([13, y + 1, 35, y + 23], 180, 360, fill=uniform, outline=INK)
    elif hat == "none":
        d.rectangle([16, y + 4, 32, y + 7], fill=trim)  # hair
    else:
        d.rectangle([15, y + 3, 33, y + 8], fill=uniform, outline=INK)
        if hat == "peaked":
            d.rectangle([13, y + 7, 35, y + 9], fill=INK)
            d.rectangle([22, y + 4, 26, y + 6], fill=trim)
    return tag(im, d)


def tag(im, d):
    d.rectangle([0, H - 9, W - 1, H - 1], fill=(24, 20, 16, 230))
    d.text((2, H - 10), "PH", fill=(255, 0, 255, 255), font=font(8))
    return im


def prop(im, d, body, trim, kind: str):
    """Still objects (no bob): a headstone, or a small roofed shrine."""
    if kind == "grave":
        d.rectangle([8, 48, 40, 54], fill=(92, 70, 48), outline=INK)  # dirt
        d.rounded_rectangle([14, 16, 34, 50], radius=8, fill=body, outline=INK)
        d.line([(24, 24), (24, 38)], fill=trim, width=2)
        d.line([(19, 29), (29, 29)], fill=trim, width=2)
    else:
        d.polygon([(8, 22), (24, 8), (40, 22)], fill=trim, outline=INK)  # roof
        d.rectangle([12, 22, 36, 50], fill=body, outline=INK)
        d.rectangle([19, 30, 29, 42], fill=INK)  # niche
        d.ellipse([21, 34, 27, 40], fill=(240, 200, 90))  # candle
    return tag(im, d)


def portrait(uniform, trim, hat: str) -> Image.Image:
    """160x200 bust: the idle frame's head and shoulders, scaled up 5x."""
    fig = frame(uniform, trim, hat, 0).crop((8, 0, 40, 40)).resize((160, 200), Image.NEAREST)
    im = Image.new("RGBA", (160, 200), (46, 40, 34, 255))
    im.alpha_composite(fig)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 182, 159, 199], fill=(24, 20, 16, 235))
    label = "PLACEHOLDER"
    f = font(11)
    d.text(((160 - d.textlength(label, font=f)) / 2, 185), label, fill=(255, 0, 255, 255), font=f)
    return im


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("ids", nargs="+")
    ap.add_argument("--force", action="store_true", help="overwrite existing PNGs")
    args = ap.parse_args()
    for nid in args.ids:
        if nid not in STYLE:
            raise SystemExit(f"no placeholder style for {nid!r}; add it to STYLE")
        uniform, trim, hat = STYLE[nid]
        for i, bob in enumerate(BOB, start=1):
            out = assert_write(CANON / "npc" / f"{nid}-{i}.png")
            if out.exists() and not args.force:
                print(f"skip {out.relative_to(ROOT)} (exists)")
                continue
            frame(uniform, trim, hat, bob).save(out)
            print(f"wrote {out.relative_to(ROOT)}")
        out = assert_write(CANON / "portraits" / f"{nid}.png")
        if out.exists() and not args.force:
            print(f"skip {out.relative_to(ROOT)} (exists)")
        else:
            portrait(uniform, trim, hat).save(out)
            print(f"wrote {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
