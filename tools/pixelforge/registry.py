"""Registry of drawn art. Species/NPC modules register a function that
returns the finished frames (list of PIL images)."""
from __future__ import annotations

import importlib

_REG = {"monsters": {}, "npcs": {}, "portraits": {}}

MODULES = {
    "monsters": ["mon_quads", "mon_birds", "mon_bugs", "mon_water", "mon_misc"],
    "npcs": ["npcs"],
    "portraits": ["portraits"],
}


def register(kind, sid):
    def deco(fn):
        _REG[kind][sid] = fn
        return fn
    return deco


def load(kind):
    for m in MODULES[kind]:
        try:
            importlib.import_module(f"pixelforge.{m}")
        except ModuleNotFoundError as e:
            if e.name != f"pixelforge.{m}":
                raise
    return _REG[kind]
