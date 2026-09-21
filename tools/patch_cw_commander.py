#!/usr/bin/env python3
from pathlib import Path

p = Path("CURRENT_WORK.md")
t = p.read_text()

old = """- `commanderFinal` (the old single gauntlet boss) isn't mentioned in
  this redesign at all — decide with the user whether it's kept as an
  earlier beat, folded into one of the 5 grass maps, or removed;
  don't unilaterally delete a working boss fight without asking."""

new = """- **`commanderFinal` — REMOVED (user decision 2026-09-21).** Do not
  keep as an earlier beat and do not fold into the grass maps. When
  2.4 is implemented, strip the old gauntlet Commander trainer/NPC/
  `beatCommander` endgame beat; the only climax is Heavenfall at the
  gravestone (Slayer/Tamer). Until 2.4 lands, leave the live
  `commanderFinal` fight in place so the current endgame still works."""

if old in t:
    t = t.replace(old, new, 1)
    print("replaced decision block")
elif "commanderFinal — REMOVED" in t:
    print("already recorded")
else:
    # softer: find the commanderFinal bullet
    needle = "`commanderFinal` (the old single gauntlet boss)"
    if needle in t:
        start = t.find(needle)
        # from -2 for leading "- " through end of paragraph
        line_start = t.rfind("\n", 0, start) + 1
        # end at next blank line or next "- " at line start after a few lines
        rest = t[line_start:]
        end_rel = rest.find("\n\n")
        if end_rel < 0:
            end_rel = 400
        t = t[:line_start] + new + "\n" + t[line_start + end_rel :]
        print("soft replace")
    else:
        raise SystemExit("anchor missing")

# Update the "two open questions" line if present
t2 = t.replace(
    "until the two open questions above (choice-screen timing,\n`commanderFinal`'s fate) are answered by the user",
    "until the remaining open question above (choice-screen timing)\nis answered by the user (`commanderFinal` is decided: **remove**)",
)
if t2 != t:
    t = t2
    print("updated gate sentence")

p.write_text(t)
print("ok")
