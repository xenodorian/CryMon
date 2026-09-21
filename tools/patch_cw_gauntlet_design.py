#!/usr/bin/env python3
from pathlib import Path

p = Path("CURRENT_WORK.md")
t = p.read_text()

block = """
- **Map shape (user 2026-09-21):** each of the 5 grass maps (and the
  approach through them) should be **long and thin**, with **lines of
  trees** forming a **maze-like** layout and **multiple dead ends**.
  Navigation is part of the pressure: a full party wipe already sends
  the player home, so the gauntlet is a **one-shot run** — clear all
  maps without blacking out, or start over from home.
- **First gauntlet wipe dialogue (user 2026-09-21):** the first time the
  player blacks out / is sent home **from the gauntlet** after having
  chosen the Heavenfall path (not Father), play a short series of
  dialogue boxes as **Max**: she regrets choosing power over the life
  of her father and wishes he were still here. Gate with a new save
  flag (e.g. `gauntletWipeRegret`) so it only fires **once**. Later
  wipes are silent (or use generic blackout only).
"""

# Insert after the 5 maps bullet if not already present
if "long and thin" in t and "gauntletWipeRegret" in t:
    print("already present")
elif "long and thin" in t:
    print("partial — check manually")
else:
    anchor = "- It's **5 maps of tall grass**, back to back, each with\n  increasingly higher-level wild CryMon than the last."
    if anchor not in t:
        anchor = "increasingly higher-level wild CryMon than the last."
        if anchor not in t:
            raise SystemExit("5 maps anchor missing")
        # insert after that line's paragraph end
        idx = t.find(anchor) + len(anchor)
        t = t[:idx] + "\n" + block + t[idx:]
    else:
        t = t.replace(anchor, anchor + "\n" + block.rstrip("\n"), 1)
    print("inserted design bullets")

# Sub-step hint for implementers
if "gauntletWipeRegret" not in t[t.find("Proposed sub-steps") : t.find("Proposed sub-steps") + 2000] if "Proposed sub-steps" in t else True:
    pass
if "First gauntlet wipe" not in t.split("Proposed sub-steps")[-1][:2500] if "Proposed sub-steps" in t else True:
    marker = "8. Integration pass + playtest."
    extra = (
        "8. Integration pass + playtest.\n"
        "9. Maze layouts (long/thin + tree corridors + dead ends) for all 5 grass maps.\n"
        "10. First-wipe Max regret dialogue + `gauntletWipeRegret` flag (Heavenfall path only)."
    )
    if marker in t and "gauntletWipeRegret" not in t[t.find(marker) : t.find(marker) + 400]:
        t = t.replace(marker, extra, 1)
        print("sub-steps 9-10 added")

p.write_text(t)
print("ok")
