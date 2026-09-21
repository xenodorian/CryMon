#!/usr/bin/env python3
"""Generate Lieutenant Lead sprites: 48x64 walk frames, 160x200 portrait, battle 48x64."""
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
NPC = ROOT / "public" / "sprites" / "npc"
POR = ROOT / "public" / "sprites" / "portraits"
MON = ROOT / "public" / "sprites" / "monsters"
for d in (NPC, POR, MON):
    d.mkdir(parents=True, exist_ok=True)


def C(r, g, b, a=255):
    return (r, g, b, a)


def new_rgba(w, h):
    return Image.new("RGBA", (w, h), (0, 0, 0, 0))


def px(img, x, y, c):
    if 0 <= x < img.width and 0 <= y < img.height:
        img.putpixel((x, y), c)


def fill_rect(img, x0, y0, x1, y1, c):
    for y in range(y0, y1):
        for x in range(x0, x1):
            px(img, x, y, c)


def ellipse_fill(img, cx, cy, rx, ry, c):
    for y in range(cy - ry, cy + ry + 1):
        for x in range(cx - rx, cx + rx + 1):
            if rx and ry and ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1.0:
                px(img, x, y, c)


def key_cleanup(img):
    pixels = img.load()
    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = pixels[x, y]
            if a > 0 and r > 200 and b > 200 and g < 80:
                pixels[x, y] = (0, 0, 0, 0)
    return img


def lead_frame(frame: int):
    """Camo soldier with rifle silhouette."""
    img = new_rgba(48, 64)
    skin = C(180, 150, 120)
    camo1 = C(70, 90, 50)
    camo2 = C(50, 70, 40)
    camo3 = C(90, 100, 55)
    boot = C(40, 35, 30)
    gun = C(50, 50, 55)
    # shadow
    ellipse_fill(img, 24, 60, 10, 3, C(0, 0, 0, 50))
    leg = [0, 2, 0, -2][frame % 4]
    fill_rect(img, 16, 42, 22, 54 + leg, camo1)
    fill_rect(img, 16, 54 + leg, 22, 60 + max(0, leg), boot)
    fill_rect(img, 26, 42, 32, 54 - leg, camo2)
    fill_rect(img, 26, 54 - leg, 32, 60 - min(0, leg), boot)
    fill_rect(img, 14, 22, 34, 44, camo1)
    # camo blotches
    for x, y in ((16, 26), (22, 30), (28, 28), (18, 36), (30, 38)):
        px(img, x, y, camo3)
        px(img, x + 1, y, camo2)
    # arms
    swing = [1, 0, -1, 0][frame % 4]
    fill_rect(img, 10, 24 + swing, 15, 38 + swing, camo1)
    fill_rect(img, 10, 36 + swing, 15, 40 + swing, skin)
    fill_rect(img, 33, 24 - swing, 38, 36 - swing, camo1)
    # rifle held across body / right
    for x in range(30, 44):
        px(img, x, 28, gun)
        px(img, x, 29, gun)
    fill_rect(img, 42, 26, 45, 32, gun)  # muzzle
    fill_rect(img, 32, 30, 36, 36, C(60, 50, 40))  # grip
    # head + helmet
    ellipse_fill(img, 24, 14, 8, 9, skin)
    fill_rect(img, 15, 6, 33, 12, camo2)
    fill_rect(img, 14, 10, 34, 13, camo1)
    px(img, 20, 14, C(20, 20, 20))
    px(img, 27, 14, C(20, 20, 20))
    return key_cleanup(img)


def portrait():
    img = new_rgba(160, 200)
    camo1, camo2 = C(70, 90, 50), C(50, 70, 40)
    skin = C(180, 150, 120)
    fill_rect(img, 28, 120, 132, 200, camo1)
    for y in range(130, 195, 6):
        fill_rect(img, 40, y, 50, y + 3, camo2)
        fill_rect(img, 100, y + 2, 115, y + 5, camo2)
    fill_rect(img, 68, 100, 92, 128, skin)
    ellipse_fill(img, 80, 70, 36, 42, skin)
    fill_rect(img, 45, 28, 115, 55, camo2)
    fill_rect(img, 50, 35, 110, 48, camo1)
    fill_rect(img, 60, 68, 70, 74, C(20, 20, 20))
    fill_rect(img, 90, 68, 100, 74, C(20, 20, 20))
    fill_rect(img, 72, 92, 88, 96, C(120, 90, 80))
    # rifle slant
    for i in range(40):
        px(img, 120 + i // 3, 80 + i, C(50, 50, 55))
        px(img, 121 + i // 3, 80 + i, C(50, 50, 55))
    return key_cleanup(img)


def main():
    for i in range(4):
        lead_frame(i).save(NPC / f"lead-{i + 1}.png", "PNG")
    portrait().save(POR / "lead.png", "PNG")
    # battle: same 4-frame-directory convention every other species uses
    # (monsters/{id}/1.png..4.png), not a single flat monsters/{id}.png --
    # gen_sprites.py and check_sync both expect the directory form.
    mon_dir = MON / "lead"
    mon_dir.mkdir(parents=True, exist_ok=True)
    for i in range(4):
        lead_frame(i).save(mon_dir / f"{i + 1}.png", "PNG")
    print("wrote lead art")


if __name__ == "__main__":
    main()
