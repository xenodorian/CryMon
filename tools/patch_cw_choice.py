#!/usr/bin/env python3
from pathlib import Path

p = Path("CURRENT_WORK.md")
t = p.read_text()

old = """- The gauntlet becomes an **unlockable location reached via a path
  behind Shinigami** (in the Grove) — not an automatic teleport after
  the choice. (Open question for whoever implements this: does the
  father/Heavenfall choice still happen at the same point in the story,
  or does it move to gate/follow the gauntlet instead? The doc doesn't
  say explicitly — check with the user before assuming either way.)"""

new = """- The gauntlet becomes an **unlockable location reached via a path
  behind Shinigami** (in the Grove) — **not** an automatic teleport after
  the choice.
- **Choice-screen timing — DECIDED (user 2026-09-21):** keep the
  father / Heavenfall choice **where it is now** in the story.
  - **Revive Father:** teleport to the existing cutscene (bedside
    revive + brief thanks conversation); Father joins as the second
    party (already largely 2.7). Do **not** auto-send the player into
    the gauntlet after this path.
  - **Revive Heavenfall / proceed that path:** does **not** fight
    Heavenfall at the choice. It **unlocks access** to the gauntlet
    (path behind Shinigami). The player reaches Heavenfall later at the
    gravestone after the 5 grass maps (2.4 maps). Strip the old
    post-choice auto-warp onto the empty gauntlet / `commanderFinal`
    when implementing this."""

if old in t:
    t = t.replace(old, new, 1)
    print("replaced choice block")
elif "Choice-screen timing — DECIDED" in t:
    print("already decided")
else:
    needle = "The gauntlet becomes an **unlockable location"
    if needle not in t:
        raise SystemExit("gauntlet bullet missing")
    # replace from that bullet through the open-question parenthetical paragraph
    start = t.find("- The gauntlet becomes")
    # find end: next bullet that starts with "- It's **5 maps"
    end = t.find("- It's **5 maps", start)
    if start < 0 or end < 0:
        raise SystemExit("bounds missing")
    t = t[:start] + new + "\n" + t[end:]
    print("soft bounds replace")

# Clear remaining "open question" gate language
for a, b in [
    (
        "until the remaining open question above (choice-screen timing)\nis answered by the user (`commanderFinal` is decided: **remove**)",
        "once assigned — **both design questions are decided**\n(choice stays put; Father path = cutscene+party; Heavenfall path = unlock\ngauntlet; `commanderFinal` **remove**)",
    ),
    (
        "until the two open questions above (choice-screen timing,\n`commanderFinal`'s fate) are answered by the user",
        "once assigned — design questions decided (see bullets above)",
    ),
]:
    if a in t:
        t = t.replace(a, b, 1)
        print("gate sentence updated")

p.write_text(t)
print("ok")
