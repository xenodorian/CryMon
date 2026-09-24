#!/usr/bin/env python3
"""Crop Lead reference sheet into OW / battle / portrait sprites."""
import base64
from pathlib import Path
from PIL import Image
import numpy as np
import io

root = Path(__file__).resolve().parents[2]
b64 = (root / "tools/patches/lead_ref_sheet.b64").read_text().strip()
img = Image.open(io.BytesIO(base64.b64decode(b64))).convert("RGBA")
a = np.array(img)
rgb = a[:, :, :3].astype(np.int16)
is_bg = (rgb[:, :, 0] < 22) & (rgb[:, :, 1] < 22) & (rgb[:, :, 2] < 22)
a[is_bg, 3] = 0
img = Image.fromarray(a)
w, h = img.size
col_w = w // 3
names = ["overworld", "battle", "portrait"]
crops = {}
for i, name in enumerate(names):
    x0, x1 = i * col_w, (i + 1) * col_w if i < 2 else w
    col = img.crop((x0, 0, x1, h))
    ca = np.array(col)
    ca2 = ca.copy()
    ca2[: max(1, h // 8), :, 3] = 0
    ys = np.where(ca2[:, :, 3].max(axis=1) > 0)[0]
    xs = np.where(ca2[:, :, 3].max(axis=0) > 0)[0]
    if len(ys) == 0:
        continue
    pad = 2
    trimmed = col.crop((max(0, xs[0] - pad), max(0, ys[0] - pad), min(col.width, xs[-1] + 1 + pad), min(col.height, ys[-1] + 1 + pad)))
    ta = np.array(trimmed)
    rgb = ta[:, :, :3].astype(np.int16)
    is_bg = (rgb[:, :, 0] < 22) & (rgb[:, :, 1] < 22) & (rgb[:, :, 2] < 22)
    ta[is_bg, 3] = 0
    crops[name] = Image.fromarray(ta)

def fit(im, tw, th, feet=True):
    scale = min(tw / im.width, th / im.height)
    nw, nh = max(1, int(im.width * scale)), max(1, int(im.height * scale))
    scaled = im.resize((nw, nh), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    x = (tw - nw) // 2
    y = th - nh if feet else (th - nh) // 2
    canvas.paste(scaled, (x, y), scaled)
    return canvas

npc = root / "public/sprites/npc"
mon = root / "public/sprites/monsters/lead"
mon.mkdir(parents=True, exist_ok=True)
ow = fit(crops["overworld"], 48, 64, True)
for i in range(4):
    ow.save(npc / f"lead-{i+1}.png")
bat = fit(crops["battle"], 96, 128, True)
for i in range(4):
    bat.save(mon / f"{i+1}.png")
port = fit(crops["portrait"], 160, 200, False)
port.save(root / "public/sprites/portraits/lead.png")
print("Lead HQ sprites written from sheet")
