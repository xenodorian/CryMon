"""UI box frame, a 16x16 nine-slice drawn pixel by pixel.

Writes public/sprites/ui/frame.png through sprite_root.assert_write. Corners
are 6x6; row/column 6..9 are the stretchable edges and the middle is the fill.
The web Engine.box() and the Dreamcast draw_ui_frame() both slice it the
same way. Run:  python3 tools/pixelforge/uiframe.py [--preview out.png]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sprite_root import CANON, assert_write  # noqa: E402

N, C = 16, 6
FILL = (18, 17, 14, 255)
OUT = (8, 7, 6, 255)
BR_D = (92, 68, 36, 255)     # brass shadow
BR = (150, 118, 64, 255)     # brass
BR_L = (214, 184, 118, 255)  # brass highlight
IN = (46, 42, 36, 255)       # inner groove
GEM = [(40, 90, 70, 255), (80, 160, 120, 255), (190, 240, 210, 255)]


def ring(d):
    """Colour for a pixel d steps in from the outer edge (straight edges)."""
    return [OUT, BR_L, BR_D, IN, FILL][min(d, 4)]


def build(preview=None):
    im = Image.new("RGBA", (N, N), FILL)
    px = im.load()
    for y in range(N):
        for x in range(N):
            d = min(x, y, N - 1 - x, N - 1 - y)
            col = ring(d)
            # light from the top left: the bottom and right brass run darker
            if d == 1 and (x > N - 1 - y or y >= N - 3 and x >= 2):
                col = BR
            px[x, y] = col
    # rounded outer corners
    for cx, cy in ((0, 0), (N - 1, 0), (0, N - 1), (N - 1, N - 1)):
        px[cx, cy] = (0, 0, 0, 0)
    for (x, y), (sx, sy) in (((1, 1), (1, 1)), ((N - 2, 1), (-1, 1)), ((1, N - 2), (1, -1)), ((N - 2, N - 2), (-1, -1))):
        px[x, y] = OUT
    for gx, gy in ((2, 2), (N - 4, 2), (2, N - 4), (N - 4, N - 4)):
        px[gx, gy], px[gx + 1, gy], px[gx, gy + 1], px[gx + 1, gy + 1] = GEM[2], GEM[1], GEM[1], GEM[0]
    out = CANON / "ui"
    out.mkdir(exist_ok=True)
    im.save(assert_write(out / "frame.png"))
    if preview:
        demo = Image.new("RGBA", (120, 60), (70, 100, 60, 255))
        W, H = 110, 50
        box = Image.new("RGBA", (W, H))
        for (sx, sw, dx, dw) in ((0, C, 0, C), (C, N - 2 * C, C, W - 2 * C), (N - C, C, W - C, C)):
            for (sy, sh, dy, dh) in ((0, C, 0, C), (C, N - 2 * C, C, H - 2 * C), (N - C, C, H - C, C)):
                box.paste(im.crop((sx, sy, sx + sw, sy + sh)).resize((dw, dh), Image.NEAREST), (dx, dy))
        demo.alpha_composite(box, (5, 5))
        demo.resize((480, 240), Image.NEAREST).save(preview)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview")
    build(ap.parse_args().preview)
    print("ui: frame")
