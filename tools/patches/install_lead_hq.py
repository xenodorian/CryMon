#!/usr/bin/env python3
import base64
from pathlib import Path

root = Path(__file__).resolve().parents[2]
data = root / "tools/patches/lead_data"
npc = root / "public/sprites/npc"
mon = root / "public/sprites/monsters/lead"
mon.mkdir(parents=True, exist_ok=True)
port = root / "public/sprites/portraits"

def load(name):
    p = data / name
    if not p.exists():
        return None
    return base64.b64decode(p.read_text().strip())

ow1 = load("ow1.b64")
if not ow1:
    raise SystemExit("missing ow1.b64")
for i in range(1, 5):
    raw = load(f"ow{i}.b64") or ow1
    (npc / f"lead-{i}.png").write_bytes(raw)
    print("ow", i, len(raw))

bat = load("bat.b64")
if bat:
    for i in range(1, 5):
        (mon / f"{i}.png").write_bytes(bat)
    print("battle", len(bat))
else:
    print("WARN no bat.b64")

pr = load("port.b64")
if pr:
    (port / "lead.png").write_bytes(pr)
    print("portrait", len(pr))
else:
    print("WARN no port.b64")
