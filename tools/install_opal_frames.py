#!/usr/bin/env python3
import base64, pathlib
root = pathlib.Path("public/sprites/npc")
src = pathlib.Path("tools/opal_chunks")
for i in range(1, 5):
    parts = [(src / f"{i}_{c}.txt").read_text().strip() for c in range(4)]
    b64 = "".join(parts)
    p = root / f"opal-{i}.png"
    p.write_bytes(base64.b64decode(b64))
    print("wrote", p, p.stat().st_size)
