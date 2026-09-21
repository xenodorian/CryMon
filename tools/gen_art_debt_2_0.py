#!/usr/bin/env python3
"""Generate remaining Leg 2.0 art debt: bogwalker/reedguard/fenn frames+portraits, quartz-2.

Source sizes: world 48x64, portraits 160x200, transparent background.
"""
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
NPC = ROOT / "public" / "sprites" / "npc"
POR = ROOT / "public" / "sprites" / "portraits"
NPC.mkdir(parents=True, exist_ok=True)
POR.mkdir(parents=True, exist_ok=True)


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


def outline_rect(img, x0, y0, x1, y1, c):
    for x in range(x0, x1):
        px(img, x, y0, c)
        px(img, x, y1 - 1, c)
    for y in range(y0, y1):
        px(img, x0, y, c)
        px(img, x1 - 1, y, c)


def key_cleanup(img):
    pixels = img.load()
    w, h = img.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = pixels[x, y]
            if a > 0 and r > 200 and b > 200 and g < 80:
                pixels[x, y] = (0, 0, 0, 0)
    return img


def draw_walker_base(img, skin, hair, tunic, trim, boots, frame, accent=None):
    ellipse_fill(img, 24, 60, 10, 3, C(0, 0, 0, 50))
    leg_off = [0, 2, 0, -2][frame % 4]
    fill_rect(img, 16, 42, 22, 54 + leg_off, tunic)
    fill_rect(img, 16, 54 + leg_off, 22, 60 + max(0, leg_off), boots)
    fill_rect(img, 26, 42, 32, 54 - leg_off, tunic)
    fill_rect(img, 26, 54 - leg_off, 32, 60 - min(0, leg_off), boots)
    fill_rect(img, 14, 24, 34, 44, tunic)
    if trim:
        fill_rect(img, 14, 24, 34, 28, trim)
        fill_rect(img, 14, 40, 34, 44, trim)
    arm_swing = [1, 0, -1, 0][frame % 4]
    fill_rect(img, 10, 26 + arm_swing, 15, 40 + arm_swing, tunic)
    fill_rect(img, 10, 38 + arm_swing, 15, 42 + arm_swing, skin)
    fill_rect(img, 33, 26 - arm_swing, 38, 40 - arm_swing, tunic)
    fill_rect(img, 33, 38 - arm_swing, 38, 42 - arm_swing, skin)
    ellipse_fill(img, 24, 16, 9, 10, skin)
    if hair:
        ellipse_fill(img, 24, 10, 10, 6, hair)
        fill_rect(img, 14, 10, 34, 14, hair)
    px(img, 20, 16, C(20, 20, 30))
    px(img, 21, 16, C(20, 20, 30))
    px(img, 27, 16, C(20, 20, 30))
    px(img, 28, 16, C(20, 20, 30))
    if accent:
        fill_rect(img, 18, 34, 30, 37, accent)


def bogwalker_frame(frame):
    img = new_rgba(48, 64)
    draw_walker_base(
        img,
        C(196, 160, 120),
        C(40, 50, 40),
        C(60, 90, 55),
        C(40, 60, 35),
        C(70, 50, 35),
        frame,
        C(120, 90, 40),
    )
    fill_rect(img, 12, 8, 36, 12, C(50, 70, 45))
    for y in range(18, 58):
        px(img, 39, y, C(90, 70, 40))
    # mud flecks
    for x, y in ((17, 48), (29, 50), (20, 36), (30, 30)):
        px(img, x, y, C(80, 60, 35))
    return key_cleanup(img)


def reedguard_frame(frame):
    img = new_rgba(48, 64)
    draw_walker_base(
        img,
        C(180, 150, 115),
        C(90, 100, 70),
        C(100, 120, 70),
        C(70, 90, 50),
        C(55, 50, 40),
        frame,
        C(160, 150, 60),
    )
    fill_rect(img, 15, 6, 33, 12, C(90, 100, 60))
    fill_rect(img, 22, 4, 26, 8, C(120, 130, 80))
    for y in range(4, 58):
        px(img, 40, y, C(100, 90, 70))
    fill_rect(img, 38, 4, 43, 10, C(180, 180, 190))
    return key_cleanup(img)


def fenn_frame(frame):
    img = new_rgba(48, 64)
    draw_walker_base(
        img,
        C(210, 170, 130),
        C(50, 35, 30),
        C(140, 90, 55),
        C(180, 140, 70),
        C(60, 45, 35),
        frame,
        C(50, 90, 120),
    )
    fill_rect(img, 30, 32, 38, 42, C(100, 70, 45))
    outline_rect(img, 30, 32, 38, 42, C(60, 40, 25))
    fill_rect(img, 12, 8, 36, 12, C(90, 60, 40))
    fill_rect(img, 18, 4, 30, 10, C(90, 60, 40))
    return key_cleanup(img)


def quartz_frame(frame):
    img = new_rgba(48, 64)
    draw_walker_base(
        img,
        C(230, 225, 220),
        C(200, 210, 220),
        C(210, 215, 225),
        C(160, 180, 200),
        C(140, 150, 165),
        frame,
        C(120, 200, 220),
    )
    ellipse_fill(img, 24, 32, 4, 5, C(140, 220, 240, 220))
    fill_rect(img, 13, 6, 35, 14, C(220, 225, 235))
    # subtle crystal shards on shoulders
    px(img, 15, 26, C(160, 220, 240))
    px(img, 32, 26, C(160, 220, 240))
    return key_cleanup(img)


def portrait(name):
    img = new_rgba(160, 200)
    if name == "bogwalker":
        cloth, trim, skin, hair = C(60, 90, 55), C(40, 60, 35), C(196, 160, 120), C(40, 50, 40)
        fill_rect(img, 30, 120, 130, 200, cloth)
        fill_rect(img, 30, 120, 130, 135, trim)
        fill_rect(img, 70, 95, 90, 125, skin)
        ellipse_fill(img, 80, 70, 38, 45, skin)
        ellipse_fill(img, 80, 40, 40, 28, hair)
        fill_rect(img, 42, 35, 118, 55, hair)
        fill_rect(img, 40, 25, 120, 45, C(50, 70, 45))
        fill_rect(img, 62, 70, 72, 76, C(25, 30, 25))
        fill_rect(img, 88, 70, 98, 76, C(25, 30, 25))
        fill_rect(img, 72, 92, 88, 95, C(140, 100, 90))
        fill_rect(img, 20, 40, 26, 200, C(90, 70, 40))
        # cloak fold lines
        for y in range(140, 195, 8):
            fill_rect(img, 40, y, 42, y + 4, C(45, 65, 40))
    elif name == "reedguard":
        cloth, skin = C(100, 120, 70), C(180, 150, 115)
        fill_rect(img, 28, 125, 132, 200, cloth)
        fill_rect(img, 28, 125, 132, 140, C(70, 90, 50))
        fill_rect(img, 68, 100, 92, 130, skin)
        ellipse_fill(img, 80, 72, 36, 42, skin)
        fill_rect(img, 45, 28, 115, 55, C(90, 100, 60))
        fill_rect(img, 70, 18, 90, 35, C(120, 130, 80))
        fill_rect(img, 60, 70, 70, 76, C(20, 20, 20))
        fill_rect(img, 90, 70, 100, 76, C(20, 20, 20))
        fill_rect(img, 70, 95, 90, 98, C(120, 90, 80))
        fill_rect(img, 138, 10, 144, 200, C(100, 90, 70))
        fill_rect(img, 134, 8, 148, 22, C(180, 180, 190))
        # brass chest plate
        fill_rect(img, 70, 145, 90, 165, C(160, 150, 60))
    else:  # fenn
        cloth, skin, hair = C(140, 90, 55), C(210, 170, 130), C(50, 35, 30)
        fill_rect(img, 30, 125, 130, 200, cloth)
        fill_rect(img, 30, 125, 130, 140, C(180, 140, 70))
        fill_rect(img, 55, 130, 105, 145, C(50, 90, 120))
        fill_rect(img, 70, 100, 90, 128, skin)
        ellipse_fill(img, 80, 72, 36, 42, skin)
        ellipse_fill(img, 80, 42, 38, 24, hair)
        fill_rect(img, 40, 30, 120, 48, C(90, 60, 40))
        fill_rect(img, 55, 18, 105, 40, C(90, 60, 40))
        fill_rect(img, 62, 70, 72, 76, C(30, 25, 20))
        fill_rect(img, 88, 70, 98, 76, C(30, 25, 20))
        fill_rect(img, 72, 94, 88, 97, C(160, 110, 100))
        fill_rect(img, 100, 125, 110, 180, C(100, 70, 45))
        # smile crease
        fill_rect(img, 74, 98, 86, 100, C(180, 130, 110))
    return key_cleanup(img)


def main():
    written = []
    for i in range(4):
        for name, fn in (
            ("bogwalker", bogwalker_frame),
            ("reedguard", reedguard_frame),
            ("fenn", fenn_frame),
        ):
            path = NPC / f"{name}-{i + 1}.png"
            fn(i).save(path, "PNG")
            written.append(str(path.relative_to(ROOT)))
    q = NPC / "quartz-2.png"
    quartz_frame(1).save(q, "PNG")
    written.append(str(q.relative_to(ROOT)))
    for name in ("bogwalker", "reedguard", "fenn"):
        path = POR / f"{name}.png"
        portrait(name).save(path, "PNG")
        written.append(str(path.relative_to(ROOT)))
    print("wrote", len(written), "files")
    for w in written:
        print(" ", w)


if __name__ == "__main__":
    main()
