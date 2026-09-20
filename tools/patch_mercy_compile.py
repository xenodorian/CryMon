#!/usr/bin/env python3
"""Fix main.c mercy compile errors: frand arity, talk(), foe.level."""
from pathlib import Path

p = Path("ports/dreamcast/src/main.c")
m = p.read_text()

# frand needs (lo, hi)
m = m.replace("frand() * 5.0f", "frand(0.0f, 1.0f) * 5.0f")
m = m.replace(
    "frand() * (ITEM_COUNT > 1 ? ITEM_COUNT - 1 : 1)",
    "frand(0.0f, 1.0f) * (ITEM_COUNT > 1 ? ITEM_COUNT - 1 : 1)",
)

# No talk() — keep HUD; remove broken talk() call if present
m = m.replace("                    talk(dismiss[di]);\n", "")

# foe.level -> foe.lv
m = m.replace("battle.foe.level", "battle.foe.lv")
m = m.replace("battle.bench[bi].level", "battle.bench[bi].lv")

p.write_text(m)
print("patched")
print("remaining frand()", m.count("frand()"))
print("talk(dismiss", "talk(dismiss" in m)
print("foe.level", m.count("foe.level"))
