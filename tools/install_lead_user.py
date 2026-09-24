#!/usr/bin/env python3
"""Install Lieutenant Lead sprites cut from user image (bg removed)."""
import base64
from pathlib import Path
ROOT = Path('.')
DATA = ROOT / 'tools' / 'lead_data'
SPRITES = ROOT / 'public' / 'sprites'
def write(path, b64):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(base64.b64decode(b64.strip()))
    print('wrote', path, len(path.read_bytes()), 'bytes')
ow = (DATA / 'ow1.b64').read_text()
bat = (DATA / 'bat1.b64').read_text()
port = (DATA / 'port.b64').read_text()
for i in range(1,5):
    write(SPRITES / 'npc' / f'lead-{i}.png', ow)
    write(SPRITES / 'monsters' / 'lead' / f'{i}.png', bat)
write(SPRITES / 'portraits' / 'lead.png', port)
print('Lieutenant Lead user sprites installed')
