#!/usr/bin/env python3
from pathlib import Path
import re

p = Path("CURRENT_WORK.md")
t = p.read_text()

# Sub-steps 5-6 (flexible match)
t2, n = re.subn(
    r"5\.\s*Screen fade-to-red \+ scream SFX on both engines\.\s*\n6\.\s*Integration pass\.",
    "5. **DONE (Grok C), pushed.** Screen fade-to-red + scream SFX on both engines "
    "(web: audio.scream + red execute fade; DC: g_mercy_red_fade + faint stand-in).\n"
    "6. **DONE (Grok C), pushed.** Integration: executed NPCs hidden web+DC (draw/interact); "
    "g_executed_mask persisted; let-go dismiss lines on both engines.",
    t,
    count=1,
)
print("substeps replaced", n)
t = t2

# Current position fragment about remaining 2.9
t2, n = re.subn(
    r"Remaining 2\.9\.5.?6 \([^)]*\)\.?",
    "**2.9 fully DONE (Grok C)** (UI, effects, execute-delete, red fade/scream, integration).",
    t,
    count=1,
)
print("position replaced", n)
t = t2

if "2.9 fully DONE" not in t and "Remaining 2.9" in t:
    t = t.replace(
        "Remaining 2.9.5–6 (red fade/scream, integration).",
        "**2.9 fully DONE (Grok C)** (UI, effects, execute-delete, red fade/scream, integration).",
    )
    t = t.replace(
        "Remaining 2.9.5-6 (red fade/scream, integration).",
        "**2.9 fully DONE (Grok C)** (UI, effects, execute-delete, red fade/scream, integration).",
    )

p.write_text(t)
print("ok", "2.9 fully DONE" in t)
