#!/usr/bin/env python3
import base64, io
from pathlib import Path
from PIL import Image

root = Path(__file__).resolve().parents[2]
parts = [(root / f"tools/patches/lead_sheet_part{i}.b64").read_text().strip() for i in range(3)]
b64 = "".join(parts)
sheet = Image.open(io.BytesIO(base64.b64decode(b64))).convert("RGBA")
# Layout: OW 48x64 at (0,136), battle 96x128 at (56,72), portrait 160x200 at (160,0)
ow = sheet.crop((0, 136, 48, 200))
bat = sheet.crop((56, 72, 152, 200))
port = sheet.crop((160, 0, 320, 200))
npc = root / "public/sprites/npc"
mon = root / "public/sprites/monsters/lead"
mon.mkdir(parents=True, exist_ok=True)
for i in range(1, 5):
    ow.save(npc / f"lead-{i}.png")
    bat.save(mon / f"{i}.png")
port.save(root / "public/sprites/portraits/lead.png")
print("installed", (npc/"lead-1.png").stat().st_size, (mon/"1.png").stat().st_size, (root/"public/sprites/portraits/lead.png").stat().st_size)
