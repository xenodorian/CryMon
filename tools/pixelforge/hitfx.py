"""Battle hit effects. The shipped PNGs are AI pixel art, not this drawer.

The seven real crystals are quartz, hematite, diamond, opal, spinel, lapis,
amethyst. Do not redraw them from this file. An older pass invented ruby,
citrine, sapphire, emerald, jasper, obsidian and prism, which are not natures.
"""
from __future__ import annotations

REAL = ("quartz", "hematite", "diamond", "opal", "spinel", "lapis", "amethyst")


def build():
    raise SystemExit(
        "hitfx.py is retired. Shipped bursts are AI art for: " + " ".join(REAL)
    )


if __name__ == "__main__":
    build()
