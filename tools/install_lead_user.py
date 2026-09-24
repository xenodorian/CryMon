#!/usr/bin/env python3
import base64
from pathlib import Path
ROOT = Path('.')
DATA = ROOT / 'tools' / 'lead_data'
SPRITES = ROOT / 'public' / 'sprites'
def write(path, b64):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(base64.b64decode(b64))
    print('wrote', path)
ow = (DATA / 'ow1.b64').read_text().strip()
bat = (DATA / 'bat1.b64').read_text().strip()
port = (DATA / 'port.b64').read_text().strip()
for i in range(1,5):
    write(SPRITES / 'npc' / f'lead-{i}.png', ow)
    write(SPRITES / 'monsters' / 'lead' / f'{i}.png', bat)
write(SPRITES / 'portraits' / 'lead.png', port)
print('done')
