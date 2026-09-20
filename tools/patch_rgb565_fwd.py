#!/usr/bin/env python3
from pathlib import Path

p = Path("ports/dreamcast/src/main.c")
m = p.read_text()

# Replace rgb565 call in apply_fade with literal to avoid order issue
# R=80,G=8,B=8 -> RGB565
lit = "((u16)(((80 >> 3) << 11) | ((8 >> 2) << 5) | (8 >> 3)))"
m2 = m.replace(
    "draw_fb[j] = rgb565(80, 8, 8);",
    f"draw_fb[j] = {lit};",
)
if m2 == m:
    # already fixed?
    if "80 >> 3" in m:
        print("already literal")
    else:
        raise SystemExit("anchor missing")
else:
    m = m2
    print("literal rgb")

p.write_text(m)
print("done")
