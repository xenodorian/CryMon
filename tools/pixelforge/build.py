#!/usr/bin/env python3
"""Draw CryMon art in code and write it into public/sprites/.

    python3 tools/pixelforge/build.py monsters sparkit blazelynx
    python3 tools/pixelforge/build.py monsters --all
    python3 tools/pixelforge/build.py npcs --all
    python3 tools/pixelforge/build.py portraits vesk
    python3 tools/pixelforge/build.py monsters --all --preview out.png   # sheet only, no writes

Replaces PLACEHOLDER_ART on purpose (it overwrites). It only ever writes the
ids registered in this package, and only through sprite_root.assert_write.
Needs Pillow and numpy.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

from PIL import Image  # noqa: E402

from sprite_root import CANON, assert_write  # noqa: E402
from pixelforge import registry  # noqa: E402


def sheet(items, scale=2, cols=6, bg=(150, 150, 156, 255)):
    """items: list of (name, [frames])."""
    cw = max(max(f.width for f in fr) for _, fr in items) * scale + 8
    ch = max(max(f.height for f in fr) for _, fr in items) * scale + 8
    rows = (len(items) + cols - 1) // cols
    out = Image.new("RGBA", (cw * cols, ch * rows), bg)
    for i, (_, fr) in enumerate(items):
        f = fr[0]
        big = f.resize((f.width * scale, f.height * scale), Image.NEAREST)
        x = (i % cols) * cw + (cw - big.width) // 2
        y = (i // cols) * ch + (ch - big.height)
        out.alpha_composite(big, (x, y - 4))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("kind", choices=["monsters", "npcs", "portraits"])
    ap.add_argument("ids", nargs="*")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--preview", help="write a contact sheet here and do not touch public/sprites")
    ap.add_argument("--anim", help="write a 4-frame strip of the first id here")
    ap.add_argument("--scale", type=int, default=2)
    args = ap.parse_args()
    reg = registry.load(args.kind)
    ids = sorted(reg) if args.all else args.ids
    missing = [i for i in ids if i not in reg]
    if missing:
        raise SystemExit(f"not drawn yet: {' '.join(missing)}")
    items = [(i, reg[i]()) for i in ids]
    if args.anim:
        fr = items[0][1]
        w, h = fr[0].width * 4, fr[0].height * 4
        strip = Image.new("RGBA", (w * 4, h), (150, 150, 156, 255))
        for k, f in enumerate(fr):
            strip.alpha_composite(f.resize((w, h), Image.NEAREST), (k * w, 0))
        strip.save(args.anim)
    if args.preview:
        sheet(items, args.scale).save(args.preview)
        return
    if args.anim:
        return
    for sid, frames in items:
        if args.kind == "monsters":
            d = CANON / "monsters" / sid
            d.mkdir(parents=True, exist_ok=True)
            for k, f in enumerate(frames, 1):
                f.save(assert_write(d / f"{k}.png"))
        elif args.kind == "npcs":
            for k, f in enumerate(frames, 1):
                f.save(assert_write(CANON / "npc" / f"{sid}-{k}.png"))
        else:
            frames[0].save(assert_write(CANON / "portraits" / f"{sid}.png"))
        print("wrote", args.kind, sid)


if __name__ == "__main__":
    main()
