#!/usr/bin/env python3
"""PLACEHOLDER_ART: write simple stand-in battle frames for new CryMon.

    python3 tools/make_placeholder_monsters.py shrewbit jolthare ...

Writes public/sprites/monsters/<id>/1..4.png: a round blob in the species'
crystal color (stripes for multi-color crystals like Prism), eyes, and a
"PLACEHOLDER" tag with the name, bobbing across the 4 idle frames. It is
meant to be overwritten by real art (Grok) at the same paths; nothing else
needs to change when that happens. Refuses to overwrite an existing PNG
unless --force is given, so it can never clobber finished art.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sprite_root import CANON, assert_write  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SIZE = 128
BOB = [0, -2, -4, -2]  # idle bob per frame, px


def font(size: int):
    try:
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)
    except Exception:
        return ImageFont.load_default()


def hex_rgb(c: str) -> tuple[int, int, int]:
    return int(c[1:3], 16), int(c[3:5], 16), int(c[5:7], 16)


def frame(name: str, colors: list[str], bob: int) -> Image.Image:
    im = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    body = [18, 26 + bob, SIZE - 18, SIZE - 30 + bob]
    # Body fill: vertical stripes, one per crystal color, clipped to an ellipse.
    fill = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    fd = ImageDraw.Draw(fill)
    w = (body[2] - body[0]) / len(colors)
    for i, c in enumerate(colors):
        fd.rectangle([body[0] + i * w, 0, body[0] + (i + 1) * w, SIZE], fill=hex_rgb(c) + (255,))
    mask = Image.new("L", (SIZE, SIZE), 0)
    ImageDraw.Draw(mask).ellipse(body, fill=255)
    im.paste(fill, (0, 0), mask)
    d = ImageDraw.Draw(im)
    d.ellipse(body, outline=(24, 20, 16, 255), width=3)
    # Eyes.
    for ex in (48, 80):
        d.ellipse([ex - 8, 52 + bob, ex + 8, 68 + bob], fill=(245, 242, 232, 255), outline=(24, 20, 16, 255), width=2)
        d.ellipse([ex - 3, 57 + bob, ex + 3, 65 + bob], fill=(24, 20, 16, 255))
    # Tag so nobody mistakes this for finished art.
    d.rectangle([4, SIZE - 26, SIZE - 5, SIZE - 2], fill=(24, 20, 16, 230))
    f = font(9)
    for row, label in enumerate(("PLACEHOLDER", name.upper())):
        tw = d.textlength(label, font=f)
        d.text(((SIZE - tw) / 2, SIZE - 25 + row * 11), label, fill=(255, 0, 255, 255), font=f)
    return im


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("ids", nargs="+")
    ap.add_argument("--force", action="store_true", help="overwrite existing PNGs")
    args = ap.parse_args()
    species = json.loads((ROOT / "content/species.json").read_text())
    natures = {n["id"]: n for n in json.loads((ROOT / "content/logic.json").read_text())["natures"]}
    for sid in args.ids:
        s = species.get(sid)
        if not s:
            raise SystemExit(f"unknown species {sid!r}")
        colors = natures[s["nature"]].get("colors") or ["#888888"]
        out_dir = CANON / "monsters" / sid
        for i, bob in enumerate(BOB, start=1):
            out = assert_write(out_dir / f"{i}.png")
            if out.exists() and not args.force:
                print(f"skip {out.relative_to(ROOT)} (exists)")
                continue
            out_dir.mkdir(parents=True, exist_ok=True)
            frame(s["name"], colors, bob).save(out)
            print(f"wrote {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
