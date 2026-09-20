#!/usr/bin/env python3
from pathlib import Path
import re

p = Path("ports/dreamcast/src/main.c")
m = p.read_text()

# Remove existing static defs (may be too late in file)
m = m.replace("static int g_mercy_red_fade = 0;\nstatic unsigned int g_executed_mask = 0; /* Leg 2.9 permanent execute-delete */\n", "")
m = m.replace("static int g_mercy_red_fade = 0;\n", "")
m = m.replace("static unsigned int g_executed_mask = 0; /* Leg 2.9 permanent execute-delete */\n", "")

# Insert early, before apply_fade
marker = "static void apply_fade"
if marker not in m:
    # try alternate
    marker = "apply_fade"
    # find function definition
    idx = m.find("static void apply_fade(")
    if idx < 0:
        idx = m.find("static int apply_fade(")
    if idx < 0:
        # insert after first block of includes - look for SCREEN_W define area
        raise SystemExit("apply_fade not found")
else:
    idx = m.find("static void apply_fade(")
    if idx < 0:
        idx = m.find(marker)

block = (
    "/* Leg 2.9 mercy state — must be before apply_fade uses red tint */\n"
    "static int g_mercy_red_fade = 0;\n"
    "static unsigned int g_executed_mask = 0;\n\n"
)
if "Leg 2.9 mercy state — must be before" not in m:
    m = m[:idx] + block + m[idx:]

# Remove unused dismiss array block (optional cleanup)
m = re.sub(
    r"\s*static const char \*dismiss\[\] = \{[^}]+\};\s*int di;\s*",
    "\n                    ",
    m,
    count=1,
)
# remove leftover di usage if any
m = re.sub(r"\s*di = \(int\)\(frand\(0\.0f, 1\.0f\) \* 5\.0f\);\s*if\(di < 0\) di = 0;\s*if\(di > 4\) di = 4;\s*", "\n                    ", m)

p.write_text(m)
print("ok")
print("early static", m.find("g_mercy_red_fade = 0") < m.find("if(g_mercy_red_fade)"))
