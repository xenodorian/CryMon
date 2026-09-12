#!/usr/bin/env python3
"""Build CryMon.sfc — LoROM Mode 1 SNES port."""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
from asm65816 import Asm, AsmError

ROOT = Path("/workspace")
OUT = ROOT / "public" / "rom" / "CryMon.sfc"
SPR = ROOT / "public" / "sprites"
FONT_H = ROOT / "native" / "font8.h"

# --- ZP ---
NMI_READY, MODE, MAP_ID = 0x00, 0x01, 0x02
JOY_L, JOY_H, JOY_PL, JOY_PH = 0x03, 0x04, 0x05, 0x06
JOY_NL, JOY_NH = 0x07, 0x08
P_DIR, P_FRAME, P_ANIM = 0x09, 0x0A, 0x0B
P_X, P_Y = 0x0C, 0x0E
CAM_X, CAM_Y = 0x10, 0x12
OAM_N = 0x14
FLAGS0, FLAGS1 = 0x15, 0x16
ANNE_PH, MASON_PH = 0x17, 0x18
A_X, A_Y, M_X, M_Y = 0x19, 0x1B, 0x1D, 0x1F
A_DIR, M_DIR = 0x21, 0x22
TALK_I = 0x23
SCR = 0x24  # 3-byte long pointer
B_PHASE, B_CUR = 0x27, 0x28
B_HP, B_MHP, F_HP, F_MHP = 0x29, 0x2A, 0x2B, 0x2C
B_WILD, B_FOE, B_SPP = 0x2D, 0x2E, 0x2F
BAG_SALVE, BAG_BAND, BAG_ROOT, BAG_GEM, MARKS = 0x30, 0x31, 0x32, 0x33, 0x34
P_HP, P_MHP, P_SPP = 0x35, 0x36, 0x37
ENC_LOCK, DOOR_LOCK = 0x38, 0x39
SEED = 0x3A
TMP0, TMP1, TMP2, TMP3 = 0x3C, 0x3D, 0x3E, 0x3F
TMP4, TMP5, TMPW = 0x40, 0x41, 0x42
MAP_W, MAP_H = 0x44, 0x45
NPARTY = 0x46
LAST_TX, LAST_TY = 0x47, 0x48
B_TRAINER = 0x49
A_FRAME, M_FRAME = 0x4A, 0x4B
BATTLES = 0x4C
FRAME = 0x4D  # word
MOVE_DX, MOVE_DY = 0x4F, 0x50
COL = 0x51
SP_X, SP_Y = 0x52, 0x54  # word, word
SP_TL, SP_AT, SP_SZ = 0x56, 0x57, 0x58
MENU_N = 0x59
TALK_WHO = 0x5A
TX, TY = 0x5B, 0x5C
PTR = 0x5D  # 3-byte
NUM = 0x60
STRPTR = 0x61  # 3-byte for print
DRAWX, DRAWY = 0x64, 0x65
EV_I = 0x66
NEED_UP = 0x6A  # 1=upload gfx, 2=upload map

OAM = 0x0200
OAMHI = 0x0400
BG3 = 0x0500
COLL = 0x0D00  # collision / metatile copy, up to 32*24

M_TITLE, M_WORLD, M_TALK, M_BATTLE, M_BAG, M_PARTY, M_SHOP, M_END = range(8)
DIR_D, DIR_L, DIR_R, DIR_U = 0, 1, 2, 3

OP_END, OP_SAY, OP_GIVE_PUP, OP_SALVE, OP_BAND, OP_ROOT, OP_GEM = 0, 1, 2, 3, 4, 5, 6
OP_FLAG, OP_BATTLE, OP_HEAL, OP_ANNE, OP_MASON, OP_SHOP, OP_MARKS = 7, 8, 9, 10, 11, 12, 13
OP_IFN, OP_IF, OP_MODE = 14, 15, 16

F_SHELF, F_MASON, F_ANNE, F_WREN, F_IVO, F_NELL, F_PIKE, F_PHELP = range(8)
F_NBONUS, F_CALDER, F_HERB, F_GEMF, F_STUMP, F_CART, F_SHIN, F_CATH = range(8, 16)

WHO = ["Max", "Anne", "Mason", "Wren", "Ivo", "Nell", "Pike", "Bram", "Calder", "Cathleen", "Shinigami", ""]

HOUSE = [
    "HHHHHHHHHHHHHH",
    "HFFFFFFFFFFFFH",
    "HFFFFFFFFFFFFH",
    "HFFFFFFFFFFFFH",
    "HFBFFFFSFFFCFH",
    "HFFFFFFFFFFFFH",
    "HUFFFFFFFFFFFH",
    "HFFFFPFFFFFFFH",
    "HFFFFFFFFFFFFH",
    "HFFFFFFFFFFFFH",
    "HHHHHHDHHHHHHH",
]
VELD = [
    "##############################",
    "####..........RRRR..........##",
    "##.Q.^^.......HHHH......WWW.##",
    "##............HDH......WWA..##",
    "##..K.........===.......W....#",
    "##...TTT.....=====.....TTT..G#",
    "##...TTT....===,===....TTT...#",
    "##....M......=====....**.....#",
    "##.V.TTT......===......TTT...#",
    "##............===............#",
    "###....X...J.=====...........#",
    "##...TTT......===............#",
    "##............===.......L....#",
    "##...TTT.....=====......TTT..#",
    "##............===......^^....#",
    "##....TTT....=====......TTT..#",
    "##....TTT.....===......TTT...#",
    "##............===............#",
    "##...........=====.....NNNN..#",
    "##............===.......NE...#",
    "###...........===...........##",
    "#############=Z=##############",
]
FOREST = [
    "##########################",
    "####.........Y.........###",
    "###.........===.........##",
    "##...TTT....===....TTT..##",
    "##...TTT...=====...TTT..##",
    "##.1........===.......2.##",
    "##...TTT....===....TTT..##",
    "##..........=====.......##",
    "##...TTT....===....TTT..##",
    "##...........===........##",
    "##...TTT....=====..TTT..##",
    "##...........===........##",
    "##...TTT.....===...TTT..##",
    "##...........=====......##",
    "##....TTT....===...TTT..##",
    "##............===.......##",
    "##...TTT......===..TTT..##",
    "##............===....3..##",
    "###...........===......###",
    "#############=O=##########",
]
GROVE = [
    "##########################",
    "####.........O.........###",
    "###.........===.........##",
    "##..........===.........##",
    "##.........=====........##",
    "##..........===.........##",
    "##.........=====........##",
    "##..........===.........##",
    "##.........=====........##",
    "##..........===.........##",
    "##........=======.......##",
    "##........===8===.......##",
    "##........=======.......##",
    "#############I############",
    "##.........=====........##",
    "##..........===.........##",
    "##.........=====........##",
    "##..........===.........##",
    "##...........9..........##",
    "###....................###",
    "##########################",
]
MAPS = [HOUSE, VELD, FOREST, GROVE]


def rgb5(r, g, b):
    return (r >> 3) | ((g >> 3) << 5) | ((b >> 3) << 10)


def pack_4bpp(pix, w, ox, oy):
    out = bytearray(32)
    for y in range(8):
        p0 = p1 = p2 = p3 = 0
        for x in range(8):
            c = pix[(oy + y) * w + (ox + x)] & 15
            bit = 7 - x
            if c & 1:
                p0 |= 1 << bit
            if c & 2:
                p1 |= 1 << bit
            if c & 4:
                p2 |= 1 << bit
            if c & 8:
                p3 |= 1 << bit
        out[y * 2] = p0
        out[y * 2 + 1] = p1
        out[16 + y * 2] = p2
        out[16 + y * 2 + 1] = p3
    return bytes(out)


def pack_2bpp(pix, w, ox, oy):
    out = bytearray(16)
    for y in range(8):
        p0 = p1 = 0
        for x in range(8):
            c = pix[(oy + y) * w + (ox + x)] & 3
            bit = 7 - x
            if c & 1:
                p0 |= 1 << bit
            if c & 2:
                p1 |= 1 << bit
        out[y * 2] = p0
        out[y * 2 + 1] = p1
    return bytes(out)


def load_font():
    text = FONT_H.read_text()
    font = []
    for m in re.finditer(r"\{(\s*\d+(?:\s*,\s*\d+){7}\s*)\}", text):
        nums = [int(x.strip()) for x in m.group(1).split(",")]
        font.append(nums)
    if len(font) < 96:
        raise RuntimeError(f"font parse got {len(font)} glyphs")
    while len(font) < 128:
        font.append([0] * 8)
    return font[:128]


def make_bg_tiles():
    """16-color 8x8 tiles. Tile 0 empty. ~40 terrain tiles."""
    pal = [
        (0, 0, 0),
        (197, 206, 198),
        (28, 36, 24),
        (232, 228, 216),
        (46, 78, 38),
        (74, 118, 52),
        (108, 148, 70),
        (90, 68, 40),
        (140, 108, 62),
        (168, 136, 84),
        (62, 40, 26),
        (118, 74, 44),
        (156, 52, 42),
        (48, 88, 128),
        (32, 70, 36),
        (210, 196, 160),
    ]
    tiles = []

    def solid(c):
        return [c] * 64

    def dither(a, b, phase=0):
        p = []
        for y in range(8):
            for x in range(8):
                p.append(a if (x + y + phase) & 1 else b)
        return p

    def noise(base, alts, seed=1):
        p = []
        s = seed
        for i in range(64):
            s = (s * 37 + 11) & 255
            p.append(base if s > 70 else alts[s % len(alts)])
        return p

    def brick():
        p = [10] * 64
        for y in range(8):
            for x in range(8):
                if y in (0, 4):
                    p[y * 8 + x] = 2
                elif (y < 4 and x == 0) or (y >= 4 and x == 4):
                    p[y * 8 + x] = 2
                elif (x + y) & 1:
                    p[y * 8 + x] = 11
        return p

    def wood():
        p = []
        for y in range(8):
            for x in range(8):
                c = 8 if y not in (0, 7) else 10
                if x == 3:
                    c = 10
                if (x + y) & 3 == 0:
                    c = 9
                p.append(c)
        return p

    def tree():
        # dense green canopy, tiny trunk — must not read as brick
        p = [14] * 64
        for y in range(8):
            for x in range(8):
                dx, dy = x - 3.5, y - 3.0
                if dx * dx + dy * dy < 16:
                    p[y * 8 + x] = 6 if ((x * 3 + y * 5) & 3) else 5
                elif y > 6 and abs(x - 4) <= 1:
                    p[y * 8 + x] = 10
                else:
                    p[y * 8 + x] = 14
        return p

    def water(ph=0):
        p = [13] * 64
        for y in range(8):
            for x in range(8):
                if y == (3 + ph) % 8:
                    p[y * 8 + x] = 1
        return p

    def tall():
        p = dither(5, 6)
        for x in range(8):
            p[x] = 6
            p[8 + x] = 5 if x & 1 else 14
        return p

    def bed(occ):
        p = [8] * 64
        for y in range(1, 7):
            for x in range(8):
                p[y * 8 + x] = 12 if occ and y < 4 else 3
        if occ:
            for x in range(2, 6):
                p[2 * 8 + x] = 7
        return p

    def door():
        p = [10] * 64
        for y in range(8):
            for x in range(1, 7):
                p[y * 8 + x] = 7
        p[4 * 8 + 5] = 9
        return p

    def shelf():
        p = wood()
        for x in range(1, 7):
            p[2 * 8 + x] = 15
            p[5 * 8 + x] = 1
        return p

    def crate():
        p = [7] * 64
        for i in range(8):
            p[i] = 10
            p[7 * 8 + i] = 10
            p[i * 8] = 10
            p[i * 8 + 7] = 10
        return p

    def flower():
        p = dither(5, 4)
        p[3 * 8 + 3] = 12
        p[3 * 8 + 4] = 3
        p[4 * 8 + 3] = 3
        p[4 * 8 + 4] = 12
        return p

    defs = [
        solid(0),  # 0 empty
        noise(5, [4, 6, 5], 11),  # 1 grass (no checkerboard)
        noise(5, [4, 14, 5], 29),  # 2 grass variation
        noise(7, [8, 10], 3),  # 3 dirt
        noise(8, [9, 7], 9),  # 4 path
        noise(8, [9, 15], 5),  # 5 path2
        water(0),  # 6 water
        water(3),  # 7 water2
        brick(),  # 8 wall
        brick(),  # 9 wall2 (same)
        wood(),  # 10 floor
        noise(8, [9, 10], 2),  # 11 floor2
        tree(),  # 12 tree
        tall(),  # 13 tall grass
        bed(1),  # 14 bed father
        bed(0),  # 15 empty bed
        door(),  # 16 door
        shelf(),  # 17 shelf
        crate(),  # 18 crate
        flower(),  # 19 flower
        noise(5, [4, 6], 2),  # 20 reed/grass
        solid(14),  # 21 dark green
        solid(12),  # 22 roof
        dither(6, 14),  # 23 canopy — green on green, not brown
        noise(4, [5, 14], 7),  # 24 dark grass
        solid(5),  # 25 mid green
    ]
    chr_ = b""
    for d in defs:
        chr_ += pack_4bpp(d, 8, 0, 0)
    # pad to 256 tiles
    while len(chr_) < 256 * 32:
        chr_ += bytes(32)
    pal_w = [rgb5(*c) for c in pal]
    return chr_[: 256 * 32], pal_w, len(defs)


# metatile: TL TR BL BR (tile ids), solid bit
# 16x16 = 4 tiles
MT_WALK, MT_SOLID, MT_TALL, MT_DOOR, MT_LOCK = 0, 1, 2, 3, 4


def metatile(tl, tr, bl, br, flags=MT_WALK):
    return (tl, tr, bl, br, flags)


MT = {
    ".": metatile(1, 1, 1, 1, MT_WALK),
    "F": metatile(10, 11, 11, 10, MT_WALK),
    "=": metatile(4, 4, 5, 5, MT_WALK),
    ",": metatile(5, 5, 4, 4, MT_WALK),
    "T": metatile(13, 13, 1, 1, MT_TALL),
    "^": metatile(12, 12, 12, 1, MT_SOLID),
    "H": metatile(8, 9, 8, 9, MT_SOLID),
    "#": metatile(12, 12, 12, 12, MT_SOLID),
    "W": metatile(6, 6, 7, 7, MT_SOLID),
    "N": metatile(8, 9, 8, 9, MT_SOLID),
    "R": metatile(22, 22, 8, 8, MT_WALK),
    "*": metatile(19, 1, 1, 19, MT_WALK),
    "D": metatile(16, 16, 4, 4, MT_DOOR),
    "B": metatile(14, 14, 10, 10, MT_SOLID),
    "U": metatile(15, 15, 10, 10, MT_WALK),
    "S": metatile(17, 17, 10, 10, MT_SOLID),
    "C": metatile(18, 18, 10, 10, MT_SOLID),
    "P": metatile(10, 11, 11, 10, MT_WALK),
    "Z": metatile(4, 5, 5, 4, MT_DOOR),
    "Y": metatile(4, 5, 5, 4, MT_DOOR),
    "O": metatile(4, 5, 5, 4, MT_DOOR),
    "I": metatile(16, 16, 4, 4, MT_LOCK),
}


def mt_of(ch):
    if ch in MT:
        return MT[ch]
    return MT["."]


def find_mark(rows, ch):
    for y, row in enumerate(rows):
        x = row.find(ch)
        if x >= 0:
            return x, y
    return None


def expand_map(rows):
    h, w = len(rows), len(rows[0])
    # 64x64 tilemap words, each metatile is 2x2 tiles
    tw, th = 64, 64
    words = [12] * (tw * th)  # forest fill outside the map, not empty
    coll = [MT_SOLID] * (w * h)
    for y in range(h):
        for x in range(w):
            tl, tr, bl, br, fl = mt_of(rows[y][x])
            coll[y * w + x] = fl
            tx, ty = x * 2, y * 2
            if tx + 1 < tw and ty + 1 < th:
                words[ty * tw + tx] = tl
                words[ty * tw + tx + 1] = tr
                words[(ty + 1) * tw + tx] = bl
                words[(ty + 1) * tw + tx + 1] = br
    raw = bytearray()
    for wd in words:
        raw.append(wd & 0xFF)
        raw.append((wd >> 8) & 0xFF)
    return bytes(raw), bytes(coll), w, h


def crop_opaque(im: Image.Image) -> Image.Image:
    im = im.convert("RGBA")
    a = im.split()[-1]
    bbox = a.getbbox()
    if not bbox:
        return im
    # ignore near-magenta
    px = im.load()
    w, h = im.size
    minx, miny, maxx, maxy = w, h, 0, 0
    found = False
    for y in range(h):
        for x in range(w):
            r, g, b, al = px[x, y]
            if al < 16:
                continue
            if r > 160 and b > 140 and g < 80:
                continue
            found = True
            if x < minx:
                minx = x
            if y < miny:
                miny = y
            if x > maxx:
                maxx = x
            if y > maxy:
                maxy = y
    if not found:
        return im
    return im.crop((minx, miny, maxx + 1, maxy + 1))


def fit_rgba(im, size, feet=True):
    im = crop_opaque(im)
    im.thumbnail((size, size), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    x = (size - im.size[0]) // 2
    y = size - im.size[1] if feet else (size - im.size[1]) // 2
    canvas.paste(im, (x, max(0, y)), im)
    return canvas


def quantize_sprite(im, n=15):
    w, h = im.size
    px = list(im.getdata())
    opaque = [(r, g, b) for r, g, b, a in px if a >= 40 and not (r > 160 and b > 140 and g < 80)]
    pal = [(0, 0, 0)]
    if opaque:
        tmp = Image.new("RGB", (len(opaque), 1))
        tmp.putdata(opaque)
        q = tmp.quantize(colors=min(n, max(1, len(set(opaque)))), method=Image.Quantize.MEDIANCUT)
        pal_img = q.getpalette() or []
        cols = []
        nused = min(n, max(1, len(set(opaque))))
        for i in range(nused):
            cols.append((pal_img[i * 3], pal_img[i * 3 + 1], pal_img[i * 3 + 2]))
        # unique keep order
        seen = set()
        for c in cols:
            if c not in seen:
                seen.add(c)
                pal.append(c)
        while len(pal) < 16:
            pal.append((0, 0, 0))
        pal = pal[:16]
    else:
        pal += [(0, 0, 0)] * 15

    def near(r, g, b):
        best, bd = 1, 1e9
        for i, (pr, pg, pb) in enumerate(pal[1:], 1):
            d = (r - pr) ** 2 + (g - pg) ** 2 + (b - pb) ** 2
            if d < bd:
                bd, best = d, i
        return best

    idx = []
    for r, g, b, a in px:
        if a < 40 or (r > 160 and b > 140 and g < 80):
            idx.append(0)
        else:
            idx.append(near(r, g, b))
    return pal, idx, w, h


def blit_tiles(chr_list, tile, idx, w, tw, th):
    """Place tw x th 8x8 tiles starting at `tile` in a 16-wide sheet."""
    rows = th
    cols = tw
    for ty in range(rows):
        for tx in range(cols):
            dest = tile + tx + ty * 16
            while dest >= len(chr_list):
                chr_list.append(bytes(32))
            chr_list[dest] = pack_4bpp(idx, w, tx * 8, ty * 8)


def load_png(path):
    return Image.open(path).convert("RGBA")


class Gfx:
    def __init__(self):
        self.bg_chr, self.bg_pal, _ = make_bg_tiles()
        font = load_font()
        # 2bpp font 0-127 + 2x letters 128+
        fchr = bytearray()
        for ci in range(128):
            bits = font[ci]
            pix = []
            for row in bits:
                for bit in range(8):
                    on = 1 if (row & (0x80 >> bit)) else 0
                    pix.append(1 if on else 0)
            if ci == 1:
                pix = [1] * 64  # window fill (light)
            if ci == 2:
                pix = [2] * 64  # dark fill
            if ci == 3:
                pix = [3] * 64  # white fill
            fchr += pack_2bpp(pix, 8, 0, 0)
        # 2x A-Z at 128
        self.big = {}
        t = 128
        for i, ch in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
            bits = font[ord(ch)]
            bigpix = [0] * (16 * 16)
            for y in range(8):
                for x in range(8):
                    on = 1 if (bits[y] & (0x80 >> x)) else 0
                    v = 3 if on else 0
                    bigpix[(y * 2) * 16 + x * 2] = v
                    bigpix[(y * 2) * 16 + x * 2 + 1] = v
                    bigpix[(y * 2 + 1) * 16 + x * 2] = v
                    bigpix[(y * 2 + 1) * 16 + x * 2 + 1] = v
            for ty in range(2):
                for tx in range(2):
                    fchr += pack_2bpp(bigpix, 16, tx * 8, ty * 8)
            self.big[ch] = t
            t += 4
        while len(fchr) < 256 * 16:
            fchr += bytes(16)
        self.font_chr = bytes(fchr[: 256 * 16])
        self.font_pal = [rgb5(0, 0, 0), rgb5(232, 228, 216), rgb5(28, 22, 18), rgb5(255, 252, 240)]

        # sprites — SNES-native 16x32 (two 16x16) and 32x32 monsters
        self.spr_tiles = [bytes(32) for _ in range(256)]
        self.spr_pal = [[rgb5(0, 0, 0)] * 16 for _ in range(8)]
        self.names = {}
        SN = SPR / "snes"

        def add16x32(kind, path, tile, pal_i, d=0, fr=0, set_pal=True):
            if not path.exists():
                print(" missing", path)
                return
            im = load_png(path)
            pal, idx, w, h = quantize_sprite(im, 15)
            if set_pal:
                self.spr_pal[pal_i] = [rgb5(*c) for c in pal]
            blit_tiles(self.spr_tiles, tile, idx, w, 2, 4)
            self.names[(kind, d, fr)] = (tile, pal_i, 0)

        def add32(kind, path, tile, pal_i):
            if not path.exists():
                print(" missing", path)
                return
            im = load_png(path)
            pal, idx, w, h = quantize_sprite(im, 15)
            self.spr_pal[pal_i] = [rgb5(*c) for c in pal]
            blit_tiles(self.spr_tiles, tile, idx, w, 4, 4)
            self.names[(kind, 0, 0)] = (tile, pal_i, 1)

        # Band 0 rows 0-3: Max 8 walk poses, tile = (dir*2+frame)*2
        dirs = [("down", 0), ("left", 1), ("right", 2), ("up", 3)]
        t = 0
        first = True
        for name, d in dirs:
            for fi in (1, 2):
                add16x32("max", SN / f"max-{name}-{fi}.png", t, 0, d, fi - 1, set_pal=first)
                first = False
                t += 2
        # Band 1 rows 4-7: Anne D,L,R,U at 64,66,68,70 then Mason at 72,74,76,78
        t = 64
        first = True
        for name, d in dirs:
            add16x32("anne", SN / f"anne-{name}-1.png", t, 1, d, 0, set_pal=first)
            first = False
            t += 2
        t = 72
        first = True
        for name, d in dirs:
            add16x32("mason", SN / f"mason-{name}-1.png", t, 2, d, 0, set_pal=first)
            first = False
            t += 2
        # Band 2 rows 8-11: 8 NPCs
        npcs = [
            ("wren", "wren.png", 128),
            ("ivo", "ivo.png", 130),
            ("nell", "nell.png", 132),
            ("pike", "pike.png", 134),
            ("bram", "bram.png", 136),
            ("calder", "calder.png", 138),
            ("cathleen", "cathleen.png", 140),
            ("shinigami", "shinigami.png", 142),
        ]
        first = True
        for kind, fn, tile in npcs:
            add16x32(kind, SN / fn, tile, 3, 0, 0, set_pal=first)
            first = False
        add16x32("soldier", SN / "soldier.png", 134, 3, 0, 0, set_pal=False)  # forest guards share pike slot unless soldier packed — overwrite 134 with soldier? Keep pike; soldier uses same tile 134
        # actually restore pike then alias soldier
        add16x32("pike", SN / "pike.png", 134, 3, 0, 0, set_pal=False)

        # Band 3 rows 12-15: 32x32 monsters at 192,196,200,204
        add32("quillpup", SN / "quillpup.png", 192, 4)
        add32("glimmoth", SN / "glimmoth.png", 196, 5)
        add32("fenwisp", SN / "fenwisp.png", 200, 6)
        add32("crymare", SN / "crymare.png", 204, 7)

        self.spr_chr = b"".join(self.spr_tiles[:256])

        self.maps = []
        self.coll = []
        self.mw = []
        self.mh = []
        self.spawns = []
        for rows in MAPS:
            tm, col, w, h = expand_map(rows)
            self.maps.append(tm)
            self.coll.append(col)
            self.mw.append(w)
            self.mh.append(h)
            sp = {}
            for y, row in enumerate(rows):
                for x, ch in enumerate(row):
                    if ch not in "TFH#.=,W^* " and ch not in sp:
                        sp[ch] = (x, y)
            self.spawns.append(sp)

    def tile_of(self, kind, d=0, fr=0):
        return self.names.get((kind, d, fr), self.names.get((kind, 0, 0), (0, 0, 0)))


def pal_bytes(colors):
    b = bytearray()
    for c in colors:
        b.append(c & 0xFF)
        b.append((c >> 8) & 0xFF)
    return bytes(b)


def build_game(a: Asm, g: Gfx):
    # ---------- reset / nmi / irq at bank 0 ----------
    a.org(0, 0x8000)
    a.label("zero")
    a.db(0)

    a.label("reset")
    a.sei()
    a.clc()
    a.xce()
    a.rep(0x30)  # A16 XY16
    a.ldx_imm(0x1FFF)
    a.txs()
    a.lda_imm(0x0000)
    a.tcd()
    a.phk()
    a.plb()
    a.sep(0x20)  # A8
    a.a8xy16()

    a.lda_imm(0x8F)
    a.sta_abs(0x2100)
    a.stz_abs(0x4200)
    a.stz_abs(0x420B)
    a.stz_abs(0x420C)
    a.stz_abs(0x212C)
    a.stz_abs(0x212D)

    # clear WRAM $0000-$1FFF quickly
    a.rep(0x30)
    a.lda_imm(0x0000)
    a.ldx_imm(0x1FFE)
    a.label("clr_wram")
    a.sta_absx(0x0000)
    a.dex()
    a.dex()
    a.bpl("clr_wram")
    a.sep(0x20)

    a.jsr("init_ppu")
    a.lda_imm(1)
    a.sta_zp(NEED_UP)
    a.lda_imm(M_TITLE)
    a.sta_zp(MODE)
    a.lda_imm(1)
    a.sta_zp(MAP_ID)
    a.rep(0x20)
    a.lda_imm(16 * 8)
    a.sta_zp(P_X)
    a.lda_imm(16 * 7)
    a.sta_zp(P_Y)
    a.sep(0x20)
    # First upload under force-blank with NMI off. Snes9x EX+ drops VRAM
    # writes if display is already on, so do not enable NMI until CHR/map
    # are in VRAM.
    a.jsr("do_upload")

    a.label("main_loop")
    a.jsr("wait_nmi")
    a.jsr("do_upload")
    a.jsr("read_joy")
    a.jsr("update")
    a.jsr("draw")
    a.jmp("main_loop")

    a.label("nmi")
    a.php()
    a.rep(0x30)
    a.pha()
    a.phx()
    a.phy()
    a.phb()
    a.sep(0x20)
    a.lda_imm(0x00)
    a.pha()
    a.plb()
    a.lda_abs(0x4210)
    a.lda_imm(1)
    a.sta_zp(NMI_READY)
    a.jsr("dma_oam")
    a.jsr("dma_bg3")
    a.jsr("write_scroll")
    a.lda_imm(0x0F)
    a.sta_abs(0x2100)
    a.rep(0x20)
    a.inc_zp(FRAME)
    a.sep(0x20)
    a.rep(0x30)
    a.plb()
    a.ply()
    a.plx()
    a.pla()
    a.plp()
    a.rti()

    a.label("irq")
    a.rti()

    a.label("wait_nmi")
    a.a8xy16()
    a.stz_zp(NMI_READY)
    a.label("wait_nmi_l")
    a.lda_zp(NMI_READY)
    a.beq("wait_nmi_l")
    a.rts()

    a.label("read_joy")
    a.a8xy16()
    a.lda_zp(JOY_L)
    a.sta_zp(JOY_PL)
    a.lda_zp(JOY_H)
    a.sta_zp(JOY_PH)
    # Serial read — auto-joy ($4218) is empty in this libretro host.
    a.lda_imm(1)
    a.sta_abs(0x4016)
    a.nop()
    a.nop()
    a.stz_abs(0x4016)
    a.nop()
    a.nop()
    a.stz_zp(JOY_H)
    a.stz_zp(JOY_L)
    a.ldx_imm(8)
    a.label("rj_hi")
    a.lda_abs(0x4016)
    a.lsr_a()
    a.rol_zp(JOY_H)
    a.dex()
    a.bne("rj_hi")
    a.ldx_imm(8)
    a.label("rj_lo")
    a.lda_abs(0x4016)
    a.lsr_a()
    a.rol_zp(JOY_L)
    a.dex()
    a.bne("rj_lo")
    a.lda_zp(JOY_H)
    a.eor_zp(JOY_PH)
    a.and_zp(JOY_H)
    a.sta_zp(JOY_NH)
    a.lda_zp(JOY_L)
    a.eor_zp(JOY_PL)
    a.and_zp(JOY_L)
    a.sta_zp(JOY_NL)
    # also merge auto-joy in case serial missed the strobe
    a.lda_abs(0x4218)
    a.ora_zp(JOY_L)
    a.sta_zp(JOY_L)
    a.lda_abs(0x4219)
    a.ora_zp(JOY_H)
    a.sta_zp(JOY_H)
    a.lda_zp(JOY_H)
    a.eor_zp(JOY_PH)
    a.and_zp(JOY_H)
    a.ora_zp(JOY_NH)
    a.sta_zp(JOY_NH)
    a.lda_zp(JOY_L)
    a.eor_zp(JOY_PL)
    a.and_zp(JOY_L)
    a.ora_zp(JOY_NL)
    a.sta_zp(JOY_NL)
    a.rts()

    # ---------- PPU init / DMA ----------
    a.label("init_ppu")
    a.a8xy16()
    a.lda_imm(0x80)
    a.sta_abs(0x2115)
    # DMA fill VRAM 64KB with 0
    a.lda_imm(0x09)
    a.sta_abs(0x4300)
    a.lda_imm(0x18)
    a.sta_abs(0x4301)
    a.split16(0x4302, "zero")
    a.lda_imm(0x00)
    a.sta_abs(0x4304)
    a.split16(0x2116, 0x0000)
    a.split16(0x4305, 0x0000)
    a.lda_imm(0x01)
    a.sta_abs(0x420B)
    # CGRAM fill
    a.stz_abs(0x2121)
    a.lda_imm(0x08)
    a.sta_abs(0x4300)
    a.lda_imm(0x22)
    a.sta_abs(0x4301)
    a.split16(0x4302, "zero")
    a.lda_imm(0x00)
    a.sta_abs(0x4304)
    a.split16(0x4305, 0x0200)
    a.lda_imm(0x01)
    a.sta_abs(0x420B)

    a.lda_imm(0x61)  # 16x16 / 32x32, name $4000
    a.sta_abs(0x2101)
    a.lda_imm(0x09)  # mode 1, BG3 prio
    a.sta_abs(0x2105)
    a.lda_imm(0x43)  # BG1 map $8000 64x64
    a.sta_abs(0x2107)
    a.stz_abs(0x2108)
    a.lda_imm(0x38)  # BG3 map $7000 32x32
    a.sta_abs(0x2109)
    a.stz_abs(0x210A)
    a.lda_imm(0x00)  # BG1 chr $0000
    a.sta_abs(0x210B)
    a.lda_imm(0x03)  # BG3 chr $6000
    a.sta_abs(0x210C)
    a.lda_imm(0x15)  # BG1 + BG3 + OBJ
    a.sta_abs(0x212C)
    a.stz_abs(0x212D)
    a.stz_abs(0x2130)
    a.stz_abs(0x2131)
    a.lda_imm(0xE0)
    a.sta_abs(0x2132)
    a.stz_abs(0x210D)
    a.stz_abs(0x210D)
    a.stz_abs(0x210E)
    a.stz_abs(0x210E)
    a.stz_abs(0x2111)
    a.stz_abs(0x2111)
    a.stz_abs(0x2112)
    a.stz_abs(0x2112)
    a.rts()

    a.label("do_upload")
    a.a8xy16()
    a.lda_zp(NEED_UP)
    a.bne("du_go")
    a.rts()
    a.label("du_go")
    a.stz_abs(0x4200)  # disable NMI so long DMA cannot nest
    a.lda_imm(0x8F)
    a.sta_abs(0x2100)
    a.lda_zp(NEED_UP)
    a.cmp_imm(1)
    a.bne("du_map")
    a.jsr("load_gfx")
    a.label("du_map")
    a.lda_zp(MAP_ID)
    a.jsr("load_map")
    a.stz_zp(NEED_UP)
    a.lda_imm(0x0F)
    a.sta_abs(0x2100)
    a.lda_imm(0x81)
    a.sta_abs(0x4200)
    a.rts()

    a.label("load_gfx")
    a.a8xy16()
    # BG tiles -> VRAM $0000 (256 tiles * 32 = 8KB, we have 256*32)
    a.lda_imm(0x80)
    a.sta_abs(0x2115)
    a.split16(0x2116, 0x0000)
    a.lda_imm(0x01)
    a.sta_abs(0x4300)
    a.lda_imm(0x18)
    a.sta_abs(0x4301)
    a.split16(0x4302, "chr_bg")
    a.lda_imm(2)  # bank 2
    a.sta_abs(0x4304)
    a.split16(0x4305, 256 * 32)
    a.lda_imm(0x01)
    a.sta_abs(0x420B)
    # font 2bpp -> VRAM $6000 = word $3000
    a.split16(0x2116, 0x3000)
    a.split16(0x4302, "chr_font")
    a.lda_imm(2)
    a.sta_abs(0x4304)
    a.split16(0x4305, 256 * 16)
    a.lda_imm(0x01)
    a.sta_abs(0x420B)
    # sprites -> VRAM $4000 = word $2000
    a.split16(0x2116, 0x2000)
    a.split16(0x4302, "chr_spr")
    a.lda_imm(3)
    a.sta_abs(0x4304)
    a.split16(0x4305, 256 * 32)
    a.lda_imm(0x01)
    a.sta_abs(0x420B)
    # palettes CGRAM
    a.stz_abs(0x2121)
    a.lda_imm(0x00)
    a.sta_abs(0x4300)  # 1 reg
    a.lda_imm(0x22)
    a.sta_abs(0x4301)
    a.split16(0x4302, "pal_all")
    a.lda_imm(2)
    a.sta_abs(0x4304)
    a.split16(0x4305, 512)
    a.lda_imm(0x01)
    a.sta_abs(0x420B)
    a.rts()

    a.label("dma_oam")
    a.a8xy16()
    a.stz_abs(0x2102)
    a.stz_abs(0x2103)
    a.lda_imm(0x00)
    a.sta_abs(0x4300)
    a.lda_imm(0x04)
    a.sta_abs(0x4301)
    a.split16(0x4302, OAM)
    a.stz_abs(0x4304)
    a.split16(0x4305, 544)
    a.lda_imm(0x01)
    a.sta_abs(0x420B)
    a.rts()

    a.label("dma_bg3")
    a.a8xy16()
    a.lda_imm(0x80)
    a.sta_abs(0x2115)
    a.split16(0x2116, 0x3800)  # VRAM word $3800 = $7000
    a.lda_imm(0x01)
    a.sta_abs(0x4300)
    a.lda_imm(0x18)
    a.sta_abs(0x4301)
    a.split16(0x4302, BG3)
    a.stz_abs(0x4304)
    a.split16(0x4305, 32 * 32 * 2)
    a.lda_imm(0x01)
    a.sta_abs(0x420B)
    a.rts()

    a.label("write_scroll")
    a.a8xy16()
    a.lda_zp(CAM_X)
    a.sta_abs(0x210D)
    a.lda_zp(CAM_X + 1)
    a.sta_abs(0x210D)
    a.lda_zp(CAM_Y)
    a.sta_abs(0x210E)
    a.lda_zp(CAM_Y + 1)
    a.sta_abs(0x210E)
    a.rts()

    a.label("oam_clear")
    a.a8xy16()
    a.ldx_imm(0)
    a.lda_imm(0xE0)
    a.label("oam_cl")
    a.sta_absx(OAM + 1)
    a.stz_absx(OAM)
    a.stz_absx(OAM + 2)
    a.stz_absx(OAM + 3)
    a.inx()
    a.inx()
    a.inx()
    a.inx()
    a.cpx_imm(0x200)
    a.bne("oam_cl")
    a.ldx_imm(0)
    a.label("oam_hi")
    a.stz_absx(OAMHI)
    a.inx()
    a.cpx_imm(0x20)
    a.bne("oam_hi")
    a.stz_zp(OAM_N)
    a.rts()

    # add sprite: SP_X.w, SP_Y.w, SP_TL, SP_AT, SP_SZ (0=16 1=32)
    a.label("oam_add")
    a.a8xy16()
    a.rep(0x20)
    a.lda_zp(SP_X)
    a.bmi("oad_off")
    a.cmp_imm(256)
    a.bcs("oad_off")
    a.lda_zp(SP_Y)
    a.bmi("oad_off")
    a.cmp_imm(224)
    a.bcs("oad_off")
    a.sep(0x20)
    a.lda_zp(OAM_N)
    a.cmp_imm(128)
    a.bcs("oad_rts")
    # X = oam_n * 4
    a.rep(0x20)
    a.and_imm(0x00FF)
    a.asl_a()
    a.asl_a()
    a.tax()
    a.sep(0x20)
    a.lda_zp(SP_X)
    a.sta_absx(OAM)
    a.lda_zp(SP_Y)
    a.deca()
    a.sta_absx(OAM + 1)
    a.lda_zp(SP_TL)
    a.sta_absx(OAM + 2)
    a.lda_zp(SP_AT)
    a.sta_absx(OAM + 3)
    # high table
    a.lda_zp(OAM_N)
    a.lsr_a()
    a.lsr_a()
    a.rep(0x20)
    a.and_imm(0x00FF)
    a.tax()
    a.sep(0x20)
    a.lda_zp(OAM_N)
    a.and_imm(3)
    a.asl_a()  # shift 0,2,4,6
    a.sta_zp(TMP0)
    a.lda_zp(SP_SZ)
    a.asl_a()  # size in bit1
    a.ora_zp(SP_X + 1)  # x msb (0/1)
    a.sta_zp(TMP1)
    # shift TMP1 left by TMP0 (must be 8-bit Y)
    a.sep(0x10)
    a.ldy_zp(TMP0)
    a.beq("oad_nosh")
    a.label("oad_sh")
    a.asl_zp(TMP1)
    a.dey()
    a.bne("oad_sh")
    a.label("oad_nosh")
    a.rep(0x10)
    a.lda_absx(OAMHI)
    a.ora_zp(TMP1)
    a.sta_absx(OAMHI)
    a.inc_zp(OAM_N)
    a.bra("oad_rts")
    a.label("oad_off")
    a.sep(0x20)
    a.label("oad_rts")
    a.rts()

    # ---------- BG3 text ----------
    a.label("bg3_clear")
    a.a8xy16()
    a.rep(0x20)
    a.lda_imm(0x0000)
    a.jsr("bg3_fill")
    a.rts()

    a.label("bg3_fill")  # A.w = tilemap word, fill 32x32. Caller must be A16.
    a.rep(0x30)
    a.ldx_imm(0)
    a.label("b3f")
    a.sta_absx(BG3)
    a.inx()
    a.inx()
    a.cpx_imm(32 * 32 * 2)
    a.bne("b3f")
    a.sep(0x20)
    a.rts()

    # DRAWX, DRAWY, A = tile, TMP0 = pal (0-7)
    a.label("bg3_put")
    a.a8xy16()
    a.sta_zp(TMP1)
    a.lda_zp(DRAWY)
    a.rep(0x20)
    a.and_imm(0x00FF)
    a.asl_a()
    a.asl_a()
    a.asl_a()
    a.asl_a()
    a.asl_a()  # *32
    a.sep(0x20)
    a.clc()
    a.adc_zp(DRAWX)
    a.rep(0x20)
    a.and_imm(0x03FF)
    a.asl_a()
    a.tax()
    a.sep(0x20)
    a.lda_zp(TMP1)
    a.sta_absx(BG3)
    a.lda_zp(TMP0)
    a.asl_a()
    a.asl_a()  # pal << 2 in high byte's ppp... high byte = prio<<5 | pal<<2
    # word: tile lo, (vhopppNN) actually high = vhopppcc (top 2 of tile)
    # pal in bits 2-4 of high byte, prio bit 5
    a.ora_imm(0x20)  # priority
    a.sta_absx(BG3 + 1)
    a.rts()

    a.label("bg3_str")  # STRPTR 3-byte, DRAWX DRAWY, TMP0 pal
    a.a8xy16()
    a.label("b3s_l")
    a.lda_longind(STRPTR)
    a.beq("b3s_d")
    a.jsr("bg3_put")
    a.inc_zp(DRAWX)
    a.inc_zp(STRPTR)
    a.bne("b3s_l")
    a.inc_zp(STRPTR + 1)
    a.bne("b3s_l")
    a.inc_zp(STRPTR + 2)
    a.bra("b3s_l")
    a.label("b3s_d")
    a.rts()

    a.label("bg3_box")  # DRAWX DRAWY TMP2=w TMP3=h
    a.a8xy16()
    a.lda_zp(DRAWY)
    a.sta_zp(TY)
    a.lda_zp(TMP3)
    a.sta_zp(TMP5)
    a.label("bb_row")
    a.lda_zp(DRAWX)
    a.sta_zp(TX)
    a.lda_zp(TMP2)
    a.sta_zp(TMP4)
    a.label("bb_col")
    a.lda_zp(TX)
    a.sta_zp(DRAWX)
    a.lda_zp(TY)
    a.sta_zp(DRAWY)
    a.lda_imm(1)  # window tile
    a.jsr("bg3_put")
    a.inc_zp(TX)
    a.dec_zp(TMP4)
    a.bne("bb_col")
    a.inc_zp(TY)
    a.dec_zp(TMP5)
    a.bne("bb_row")
    a.rts()

    a.label("print_num")  # A = number, DRAWX DRAWY TMP0 pal → 3 digits
    a.a8xy16()
    a.sta_zp(NUM)
    a.ldy_imm(0)  # hundreds
    a.label("pn_h")
    a.lda_zp(NUM)
    a.cmp_imm(100)
    a.bcc("pn_h2")
    a.sbc_imm(100)
    a.sta_zp(NUM)
    a.iny()
    a.bra("pn_h")
    a.label("pn_h2")
    a.tya()
    a.clc()
    a.adc_imm(ord("0"))
    a.jsr("bg3_put")
    a.inc_zp(DRAWX)
    a.ldy_imm(0)
    a.label("pn_t")
    a.lda_zp(NUM)
    a.cmp_imm(10)
    a.bcc("pn_t2")
    a.sbc_imm(10)
    a.sta_zp(NUM)
    a.iny()
    a.bra("pn_t")
    a.label("pn_t2")
    a.tya()
    a.clc()
    a.adc_imm(ord("0"))
    a.jsr("bg3_put")
    a.inc_zp(DRAWX)
    a.lda_zp(NUM)
    a.clc()
    a.adc_imm(ord("0"))
    a.jsr("bg3_put")
    a.inc_zp(DRAWX)
    a.rts()

    a.label("big_str")  # STRPTR, DRAWX DRAWY  (A-Z 16x16 on BG3 pal TMP0)
    a.a8xy16()
    a.label("bs_l")
    a.lda_longind(STRPTR)
    a.beq("bs_d")
    a.cmp_imm(ord("A"))
    a.bcc("bs_sp")
    a.sec()
    a.sbc_imm(ord("A"))
    a.asl_a()
    a.asl_a()
    a.clc()
    a.adc_imm(128)
    a.sta_zp(TMP2)  # base tile; TMP1 is clobbered by bg3_put
    a.jsr("bg3_put")  # TL = base
    a.inc_zp(DRAWX)
    a.lda_zp(TMP2)
    a.clc()
    a.adc_imm(1)
    a.jsr("bg3_put")  # TR
    a.dec_zp(DRAWX)
    a.inc_zp(DRAWY)
    a.lda_zp(TMP2)
    a.clc()
    a.adc_imm(2)
    a.jsr("bg3_put")  # BL
    a.inc_zp(DRAWX)
    a.lda_zp(TMP2)
    a.clc()
    a.adc_imm(3)
    a.jsr("bg3_put")  # BR
    a.dec_zp(DRAWY)
    a.inc_zp(DRAWX)
    a.bra("bs_n")
    a.label("bs_sp")
    a.inc_zp(DRAWX)
    a.inc_zp(DRAWX)
    a.label("bs_n")
    a.inc_zp(STRPTR)
    a.bne("bs_l")
    a.inc_zp(STRPTR + 1)
    a.bne("bs_l")
    a.inc_zp(STRPTR + 2)
    a.bra("bs_l")
    a.label("bs_d")
    a.rts()

    # ---------- RNG ----------
    a.label("rng")
    a.a8xy16()
    a.lda_zp(SEED)
    a.asl_a()
    a.asl_a()
    a.clc()
    a.adc_zp(SEED)
    a.inca()
    a.sta_zp(SEED)
    a.rts()

    # ---------- map load ----------
    a.label("load_map")  # A = map id
    a.a8xy16()
    a.sta_zp(MAP_ID)
    a.rep(0x20)
    a.and_imm(0x00FF)
    a.asl_a()
    a.asl_a()
    a.asl_a()  # *8
    a.tax()
    a.sep(0x20)
    a.lda_absx("map_hdr")  # w
    a.sta_zp(MAP_W)
    a.lda_absx(("map_hdr", 1))
    a.sta_zp(MAP_H)
    # DMA tilemap from hdr+2 long to VRAM $4000 words ($8000)
    a.lda_imm(0x80)
    a.sta_abs(0x2115)
    a.lda_imm(0x00)
    a.sta_abs(0x2116)
    a.lda_imm(0x40)
    a.sta_abs(0x2117)
    a.lda_imm(0x01)
    a.sta_abs(0x4300)
    a.lda_imm(0x18)
    a.sta_abs(0x4301)
    a.lda_absx(("map_hdr", 2))
    a.sta_abs(0x4302)
    a.sta_zp(0xF0)
    a.lda_absx(("map_hdr", 3))
    a.sta_abs(0x4303)
    a.sta_zp(0xF1)
    a.lda_absx(("map_hdr", 4))
    a.sta_abs(0x4304)
    a.sta_zp(0xF2)
    a.rep(0x20)
    a.txa()
    a.sta_zp(0xF4)
    a.sep(0x20)
    a.lda_imm(0x00)
    a.sta_abs(0x4305)
    a.lda_imm(0x20)
    a.sta_abs(0x4306)
    a.lda_imm(0x01)
    a.sta_abs(0x420B)
    # copy collision
    a.lda_absx(("map_hdr", 5))
    a.sta_zp(PTR)
    a.lda_absx(("map_hdr", 6))
    a.sta_zp(PTR + 1)
    a.lda_absx(("map_hdr", 7))
    a.sta_zp(PTR + 2)
    a.lda_zp(MAP_W)
    a.sta_zp(TMP0)
    a.lda_zp(MAP_H)
    a.sta_zp(TMP1)
    a.rep(0x20)
    a.lda_zp(TMP0)
    a.and_imm(0x00FF)
    a.sta_zp(TMPW)
    # Y = w*h
    a.sep(0x20)
    a.lda_imm(0)
    a.xba()
    a.lda_zp(MAP_H)
    a.rep(0x20)
    a.and_imm(0x00FF)
    # multiply A * MAP_W
    a.sta_zp(TMP2)
    a.lda_imm(0)
    a.ldy_zp(MAP_W)
    a.sep(0x20)
    # simple: copy up to 1024
    a.ldx_imm(0)
    a.label("colcpy")
    a.lda_longind(PTR)
    a.sta_absx(COLL)
    a.inc_zp(PTR)
    a.bne("cc1")
    a.inc_zp(PTR + 1)
    a.bne("cc1")
    a.inc_zp(PTR + 2)
    a.label("cc1")
    a.inx()
    a.cpx_imm(1024)
    a.bne("colcpy")
    a.sep(0x20)
    a.rts()

    a.label("camera")
    a.a8xy16()
    a.rep(0x20)
    a.lda_zp(P_X)
    a.clc()
    a.adc_imm(8)
    a.sec()
    a.sbc_imm(128)
    a.bcs("cam_xok")
    a.lda_imm(0)
    a.label("cam_xok")
    # max = map_w*16 - 256
    a.sta_zp(CAM_X)
    a.lda_zp(P_Y)
    a.clc()
    a.adc_imm(8)
    a.sec()
    a.sbc_imm(112)
    a.bcs("cam_yok")
    a.lda_imm(0)
    a.label("cam_yok")
    a.sta_zp(CAM_Y)
    # clamp X to mw*16-256
    a.sep(0x20)
    a.lda_zp(MAP_W)
    a.rep(0x20)
    a.and_imm(0x00FF)
    a.asl_a()
    a.asl_a()
    a.asl_a()
    a.asl_a()
    a.sec()
    a.sbc_imm(256)
    a.bcs("cxm")
    a.lda_imm(0)
    a.label("cxm")
    a.cmp_zp(CAM_X)
    a.bcs("cxd")
    a.sta_zp(CAM_X)
    a.label("cxd")
    a.sep(0x20)
    a.lda_zp(MAP_H)
    a.rep(0x20)
    a.and_imm(0x00FF)
    a.asl_a()
    a.asl_a()
    a.asl_a()
    a.asl_a()
    a.sec()
    a.sbc_imm(224)
    a.bcs("cym")
    a.lda_imm(0)
    a.label("cym")
    a.cmp_zp(CAM_Y)
    a.bcs("cyd")
    a.sta_zp(CAM_Y)
    a.label("cyd")
    a.sep(0x20)
    a.rts()

    # collision at pixel X=TMPW, Y=TMP2 (words). result COL=flags
    a.label("collat")
    a.a8xy16()
    a.rep(0x20)
    a.lda_zp(TMPW)
    a.lsr_a()
    a.lsr_a()
    a.lsr_a()
    a.lsr_a()
    a.sep(0x20)
    a.cmp_zp(MAP_W)
    a.bcc("ca_x")
    a.lda_imm(MT_SOLID)
    a.sta_zp(COL)
    a.rts()
    a.label("ca_x")
    a.sta_zp(TX)
    a.rep(0x20)
    a.lda_zp(TMP2)
    a.lsr_a()
    a.lsr_a()
    a.lsr_a()
    a.lsr_a()
    a.sep(0x20)
    a.cmp_zp(MAP_H)
    a.bcc("ca_y")
    a.lda_imm(MT_SOLID)
    a.sta_zp(COL)
    a.rts()
    a.label("ca_y")
    a.sta_zp(TY)
    # idx = ty*mw+tx (16-bit)
    a.rep(0x20)
    a.lda_zp(TY)
    a.and_imm(0x00FF)
    a.sta_zp(TMP4)
    a.lda_zp(MAP_W)
    a.and_imm(0x00FF)
    a.tay()
    a.lda_imm(0)
    a.cpy_imm(0)
    a.beq("ca_m")
    a.label("ca_mul")
    a.clc()
    a.adc_zp(TMP4)
    a.dey()
    a.bne("ca_mul")
    a.label("ca_m")
    a.sta_zp(TMPW)
    a.lda_zp(TX)
    a.and_imm(0x00FF)
    a.clc()
    a.adc_zp(TMPW)
    a.tax()
    a.sep(0x20)
    a.lda_absx(COLL)
    a.sta_zp(COL)
    a.rts()

    a.label("blocked")  # TMPW,TMP2 pixels. A=1 if solid
    a.jsr("collat")
    a.lda_zp(COL)
    a.cmp_imm(MT_SOLID)
    a.beq("bl_yes")
    a.cmp_imm(MT_LOCK)
    a.bne("bl_no")
    a.lda_zp(FLAGS1)
    a.and_imm(1 << (F_CATH - 8))
    a.bne("bl_no")
    a.bra("bl_yes")
    a.label("bl_no")
    a.lda_imm(0)
    a.rts()
    a.label("bl_yes")
    a.lda_imm(1)
    a.rts()

    # ---------- modes ----------
    a.label("request_map")  # A = map id
    a.sta_zp(MAP_ID)
    a.lda_imm(2)
    a.sta_zp(NEED_UP)
    a.rts()

    a.label("show_title")
    a.a8xy16()
    a.lda_imm(M_TITLE)
    a.sta_zp(MODE)
    a.lda_imm(1)
    a.jsr("request_map")
    a.rep(0x20)
    a.lda_imm(16 * 8)
    a.sta_zp(P_X)
    a.lda_imm(16 * 7)
    a.sta_zp(P_Y)
    a.stz_zp(CAM_X)
    a.stz_zp(CAM_Y)
    a.sep(0x20)
    a.stz_zp(P_DIR)
    a.jsr("camera")
    a.rts()

    a.label("start_game")
    a.a8xy16()
    a.stz_zp(FLAGS0)
    a.stz_zp(FLAGS1)
    a.stz_zp(ANNE_PH)
    a.stz_zp(MASON_PH)
    a.lda_imm(1)
    a.sta_zp(NPARTY)
    a.stz_zp(BATTLES)
    a.lda_imm(16)
    a.sta_zp(MARKS)
    a.stz_zp(BAG_SALVE)
    a.stz_zp(BAG_BAND)
    a.stz_zp(BAG_ROOT)
    a.stz_zp(BAG_GEM)
    a.lda_imm(34)
    a.sta_zp(P_MHP)
    a.sta_zp(P_HP)
    a.lda_imm(3)
    a.sta_zp(P_SPP)
    a.lda_imm(M_WORLD)
    a.sta_zp(MODE)
    a.lda_imm(0)
    a.jsr("request_map")
    # spawn P
    a.rep(0x20)
    a.lda_imm(5 * 16)
    a.sta_zp(P_X)
    a.lda_imm(7 * 16)
    a.sta_zp(P_Y)
    a.sep(0x20)
    a.stz_zp(P_DIR)
    a.lda_imm(20)
    a.sta_zp(DOOR_LOCK)
    a.jsr("camera")
    a.rts()

    a.label("update")
    a.a8xy16()
    a.lda_zp(MODE)
    a.cmp_imm(M_TITLE)
    a.bne("up1")
    a.jmp("upd_title")
    a.label("up1")
    a.cmp_imm(M_WORLD)
    a.bne("up2")
    a.jmp("upd_world")
    a.label("up2")
    a.cmp_imm(M_TALK)
    a.bne("up3")
    a.jmp("upd_talk")
    a.label("up3")
    a.cmp_imm(M_BATTLE)
    a.bne("up4")
    a.jmp("upd_battle")
    a.label("up4")
    a.cmp_imm(M_BAG)
    a.bne("up5")
    a.jmp("upd_bag")
    a.label("up5")
    a.cmp_imm(M_PARTY)
    a.bne("up6")
    a.jmp("upd_party")
    a.label("up6")
    a.cmp_imm(M_SHOP)
    a.bne("up7")
    a.jmp("upd_shop")
    a.label("up7")
    a.jmp("upd_end")

    a.label("upd_title")
    a.lda_zp(JOY_NH)
    a.and_imm(0x10)  # start
    a.bne("ut_go")
    a.lda_zp(JOY_NL)
    a.and_imm(0x80)  # A
    a.beq("ut_r")
    a.label("ut_go")
    a.jsr("start_game")
    a.label("ut_r")
    a.rts()

    a.label("pressed_a")
    a.lda_zp(JOY_NL)
    a.and_imm(0x80)
    a.rts()

    a.label("pressed_b")
    a.lda_zp(JOY_NH)
    a.and_imm(0x80)
    a.rts()

    a.label("pressed_st")
    a.lda_zp(JOY_NH)
    a.and_imm(0x10)
    a.rts()

    a.label("pressed_sel")
    a.lda_zp(JOY_NH)
    a.and_imm(0x20)
    a.rts()

    a.label("upd_world")
    a.a8xy16()
    a.lda_zp(DOOR_LOCK)
    a.beq("uw_dl")
    a.dec_zp(DOOR_LOCK)
    a.label("uw_dl")
    a.jsr("upd_mason")
    a.jsr("upd_anne")
    a.jsr("try_move")
    a.jsr("try_doors")
    a.jsr("try_enc")
    a.jsr("pressed_a")
    a.beq("uw_na")
    a.jsr("try_talk")
    a.label("uw_na")
    a.jsr("pressed_st")
    a.beq("uw_ns")
    a.lda_imm(M_PARTY)
    a.sta_zp(MODE)
    a.label("uw_ns")
    a.jsr("pressed_sel")
    a.beq("uw_r")
    a.lda_imm(M_BAG)
    a.sta_zp(MODE)
    a.label("uw_r")
    a.jsr("camera")
    a.rts()

    a.label("try_move")
    a.a8xy16()
    a.stz_zp(MOVE_DX)
    a.stz_zp(MOVE_DY)
    a.lda_zp(JOY_H)
    a.and_imm(0x08)
    a.beq("tm_d")
    a.lda_imm(0xFF)
    a.sta_zp(MOVE_DY)
    a.lda_imm(DIR_U)
    a.sta_zp(P_DIR)
    a.label("tm_d")
    a.lda_zp(JOY_H)
    a.and_imm(0x04)
    a.beq("tm_l")
    a.lda_imm(1)
    a.sta_zp(MOVE_DY)
    a.lda_imm(DIR_D)
    a.sta_zp(P_DIR)
    a.label("tm_l")
    a.lda_zp(JOY_H)
    a.and_imm(0x02)
    a.beq("tm_r")
    a.lda_imm(0xFF)
    a.sta_zp(MOVE_DX)
    a.lda_imm(DIR_L)
    a.sta_zp(P_DIR)
    a.label("tm_r")
    a.lda_zp(JOY_H)
    a.and_imm(0x01)
    a.beq("tm_go")
    a.lda_imm(1)
    a.sta_zp(MOVE_DX)
    a.lda_imm(DIR_R)
    a.sta_zp(P_DIR)
    a.label("tm_go")
    a.lda_zp(MOVE_DX)
    a.ora_zp(MOVE_DY)
    a.bne("tm_mv")
    a.stz_zp(P_FRAME)
    a.rts()
    a.label("tm_mv")
    a.inc_zp(P_ANIM)
    a.lda_zp(P_ANIM)
    a.lsr_a()
    a.lsr_a()
    a.lsr_a()
    a.and_imm(1)
    a.sta_zp(P_FRAME)
    # try x — the candidate X must be held in TMP2, not TMPW: collat()'s
    # tile-index multiply clobbers TMPW internally, so a candidate stashed
    # there is corrupted by the time blocked() returns and gets copied back
    # into P_X, permanently freezing horizontal movement after one step.
    a.sep(0x20)
    a.lda_zp(MOVE_DX)
    a.beq("tm_xskip")
    a.rep(0x20)
    a.lda_zp(MOVE_DX)
    a.and_imm(0x00FF)
    a.cmp_imm(0x80)
    a.bcc("tm_xpos")
    a.ora_imm(0xFF00)
    a.label("tm_xpos")
    a.clc()
    a.adc_zp(P_X)
    a.sta_zp(TMP2)
    a.lda_zp(P_Y)
    a.clc()
    a.adc_imm(12)
    a.sta_zp(TMPW)
    a.sep(0x20)
    a.jsr("blocked")
    a.bne("tm_xskip")
    a.rep(0x20)
    a.lda_zp(TMP2)
    a.sta_zp(P_X)
    a.sep(0x20)
    a.label("tm_xskip")
    a.sep(0x20)
    a.lda_zp(MOVE_DY)
    a.beq("tm_ys")
    a.rep(0x20)
    a.lda_zp(MOVE_DY)
    a.and_imm(0x00FF)
    a.cmp_imm(0x80)
    a.bcc("tm_ypos")
    a.ora_imm(0xFF00)
    a.label("tm_ypos")
    a.clc()
    a.adc_zp(P_Y)
    a.sta_zp(TMP2)
    a.lda_zp(P_X)
    a.clc()
    a.adc_imm(8)
    a.sta_zp(TMPW)
    a.sep(0x20)
    a.jsr("blocked")
    a.bne("tm_ys")
    a.rep(0x20)
    a.lda_zp(TMP2)
    a.sta_zp(P_Y)
    a.sep(0x20)
    a.label("tm_ys")
    a.sep(0x20)
    a.rts()

    a.label("try_doors")
    a.a8xy16()
    a.lda_zp(DOOR_LOCK)
    a.beq("td_ok")
    a.rts()
    a.label("td_ok")
    a.rep(0x20)
    a.lda_zp(P_X)
    a.clc()
    a.adc_imm(8)
    a.sta_zp(TMPW)
    a.lda_zp(P_Y)
    a.clc()
    a.adc_imm(12)
    a.sta_zp(TMP2)
    a.sep(0x20)
    a.jsr("collat")
    a.lda_zp(COL)
    a.cmp_imm(MT_DOOR)
    a.beq("td_hit")
    a.rts()
    a.label("td_hit")
    a.lda_zp(MAP_ID)
    a.cmp_imm(0)
    a.bne("td_v")
    a.lda_zp(FLAGS0)
    a.and_imm(1 << F_SHELF)
    a.bne("td_out")
    a.jsr("script_doorlock")
    a.rts()
    a.label("td_out")
    a.lda_imm(1)
    a.jsr("request_map")
    a.rep(0x20)
    a.lda_imm(13 * 16)
    a.sta_zp(P_X)
    a.lda_imm(4 * 16)
    a.sta_zp(P_Y)
    a.sep(0x20)
    a.lda_imm(DIR_D)
    a.sta_zp(P_DIR)
    a.lda_imm(20)
    a.sta_zp(DOOR_LOCK)
    a.lda_zp(MASON_PH)
    a.bne("td_ms")
    a.lda_imm(1)
    a.sta_zp(MASON_PH)
    a.rep(0x20)
    a.lda_zp(P_X)
    a.sta_zp(M_X)
    a.lda_zp(P_Y)
    a.clc()
    a.adc_imm(96)
    a.sta_zp(M_Y)
    a.sep(0x20)
    a.lda_imm(DIR_U)
    a.sta_zp(M_DIR)
    a.jsr("script_footsteps")
    a.label("td_ms")
    a.rts()
    a.label("td_v")
    a.lda_zp(MAP_ID)
    a.cmp_imm(1)
    a.bne("td_f")
    # veld doors: house vs forest. If player y < 6*16 -> house else forest if bottom
    a.rep(0x20)
    a.lda_zp(P_Y)
    a.cmp_imm(10 * 16)
    a.sep(0x20)
    a.bcs("td_for")
    a.lda_imm(0)
    a.jsr("request_map")
    a.rep(0x20)
    a.lda_imm(6 * 16)
    a.sta_zp(P_X)
    a.lda_imm(9 * 16)
    a.sta_zp(P_Y)
    a.sep(0x20)
    a.lda_imm(DIR_U)
    a.sta_zp(P_DIR)
    a.lda_imm(20)
    a.sta_zp(DOOR_LOCK)
    a.rts()
    a.label("td_for")
    a.lda_imm(2)
    a.jsr("request_map")
    a.rep(0x20)
    a.lda_imm(13 * 16)
    a.sta_zp(P_X)
    a.lda_imm(2 * 16)
    a.sta_zp(P_Y)
    a.sep(0x20)
    a.lda_imm(DIR_D)
    a.sta_zp(P_DIR)
    a.lda_imm(20)
    a.sta_zp(DOOR_LOCK)
    a.jsr("script_trees")
    a.rts()
    a.label("td_f")
    a.lda_zp(MAP_ID)
    a.cmp_imm(2)
    a.bne("td_g")
    a.rep(0x20)
    a.lda_zp(P_Y)
    a.cmp_imm(10 * 16)
    a.sep(0x20)
    a.bcs("td_gr")
    a.lda_imm(1)
    a.jsr("request_map")
    a.rep(0x20)
    a.lda_imm(14 * 16)
    a.sta_zp(P_X)
    a.lda_imm(20 * 16)
    a.sta_zp(P_Y)
    a.sep(0x20)
    a.lda_imm(20)
    a.sta_zp(DOOR_LOCK)
    a.rts()
    a.label("td_gr")
    a.lda_imm(3)
    a.jsr("request_map")
    a.rep(0x20)
    a.lda_imm(13 * 16)
    a.sta_zp(P_X)
    a.lda_imm(2 * 16)
    a.sta_zp(P_Y)
    a.sep(0x20)
    a.lda_imm(20)
    a.sta_zp(DOOR_LOCK)
    a.jsr("script_grove")
    a.rts()
    a.label("td_g")
    a.lda_imm(2)
    a.jsr("request_map")
    a.rep(0x20)
    a.lda_imm(13 * 16)
    a.sta_zp(P_X)
    a.lda_imm(18 * 16)
    a.sta_zp(P_Y)
    a.sep(0x20)
    a.lda_imm(20)
    a.sta_zp(DOOR_LOCK)
    a.rts()

    a.label("try_enc")
    a.a8xy16()
    a.lda_zp(NPARTY)
    a.bne("te_ok")
    a.rts()
    a.label("te_ok")
    a.rep(0x20)
    a.lda_zp(P_X)
    a.clc()
    a.adc_imm(8)
    a.sta_zp(TMPW)
    a.lda_zp(P_Y)
    a.clc()
    a.adc_imm(12)
    a.sta_zp(TMP2)
    a.sep(0x20)
    a.jsr("collat")
    a.lda_zp(COL)
    a.cmp_imm(MT_TALL)
    a.beq("te_t")
    a.rts()
    a.label("te_t")
    a.lda_zp(P_X)
    a.lsr_a()
    a.lsr_a()
    a.lsr_a()
    a.lsr_a()
    a.cmp_zp(LAST_TX)
    a.bne("te_new")
    a.lda_zp(P_Y)
    a.lsr_a()
    a.lsr_a()
    a.lsr_a()
    a.lsr_a()
    a.cmp_zp(LAST_TY)
    a.bne("te_new")
    a.rts()
    a.label("te_new")
    a.lda_zp(P_X)
    a.lsr_a()
    a.lsr_a()
    a.lsr_a()
    a.lsr_a()
    a.sta_zp(LAST_TX)
    a.lda_zp(P_Y)
    a.lsr_a()
    a.lsr_a()
    a.lsr_a()
    a.lsr_a()
    a.sta_zp(LAST_TY)
    a.lda_zp(ENC_LOCK)
    a.beq("te_go")
    a.dec_zp(ENC_LOCK)
    a.rts()
    a.label("te_go")
    a.jsr("rng")
    a.cmp_imm(40)
    a.bcc("te_hit")
    a.rts()
    a.label("te_hit")
    a.lda_imm(8)
    a.sta_zp(ENC_LOCK)
    a.lda_imm(1)  # glimmoth
    a.sta_zp(B_FOE)
    a.lda_zp(MAP_ID)
    a.cmp_imm(2)
    a.bne("te_v")
    a.jsr("rng")
    a.and_imm(3)
    a.inca()
    a.inca()  # 2-5 fenwisp duskhorn needleroot
    a.cmp_imm(5)
    a.bcc("te_fok")
    a.lda_imm(2)
    a.label("te_fok")
    a.sta_zp(B_FOE)
    a.label("te_v")
    a.lda_imm(1)
    a.sta_zp(B_WILD)
    a.stz_zp(B_TRAINER)
    a.jsr("start_battle")
    a.rts()

    a.label("upd_mason")
    a.a8xy16()
    a.lda_zp(MASON_PH)
    a.cmp_imm(1)
    a.beq("um_ap")
    a.cmp_imm(3)
    a.beq("um_lv")
    a.rts()
    a.label("um_lv")
    a.lda_imm(DIR_D)
    a.sta_zp(M_DIR)
    a.rep(0x20)
    a.inc_zp(M_Y)
    a.inc_zp(M_Y)
    a.lda_zp(M_Y)
    a.cmp_zp(P_Y)
    a.sep(0x20)
    a.bcc("um_r2")
    a.rep(0x20)
    a.lda_zp(M_Y)
    a.sec()
    a.sbc_zp(P_Y)
    a.cmp_imm(160)
    a.sep(0x20)
    a.bcc("um_r2")
    a.stz_zp(MASON_PH)
    a.label("um_r2")
    a.rts()
    a.label("um_ap")
    a.lda_zp(MAP_ID)
    a.cmp_imm(1)
    a.beq("um_ok")
    a.rts()
    a.label("um_ok")
    # step toward player
    a.rep(0x20)
    a.lda_zp(P_X)
    a.cmp_zp(M_X)
    a.sep(0x20)
    a.beq("um_x")
    a.bcs("um_xr")
    a.rep(0x20)
    a.dec_zp(M_X)
    a.sep(0x20)
    a.lda_imm(DIR_L)
    a.sta_zp(M_DIR)
    a.bra("um_x")
    a.label("um_xr")
    a.rep(0x20)
    a.inc_zp(M_X)
    a.sep(0x20)
    a.lda_imm(DIR_R)
    a.sta_zp(M_DIR)
    a.label("um_x")
    a.rep(0x20)
    a.lda_zp(P_Y)
    a.cmp_zp(M_Y)
    a.sep(0x20)
    a.beq("um_y")
    a.bcs("um_yd")
    a.rep(0x20)
    a.dec_zp(M_Y)
    a.sep(0x20)
    a.lda_imm(DIR_U)
    a.sta_zp(M_DIR)
    a.bra("um_y")
    a.label("um_yd")
    a.rep(0x20)
    a.inc_zp(M_Y)
    a.sep(0x20)
    a.lda_imm(DIR_D)
    a.sta_zp(M_DIR)
    a.label("um_y")
    a.inc_zp(M_FRAME)
    # dist
    a.rep(0x20)
    a.lda_zp(P_X)
    a.sec()
    a.sbc_zp(M_X)
    a.bpl("um_ax")
    a.eor_imm(0xFFFF)
    a.inca()
    a.label("um_ax")
    a.sta_zp(TMPW)
    a.lda_zp(P_Y)
    a.sec()
    a.sbc_zp(M_Y)
    a.bpl("um_ay")
    a.eor_imm(0xFFFF)
    a.inca()
    a.label("um_ay")
    a.clc()
    a.adc_zp(TMPW)
    a.cmp_imm(16)
    a.sep(0x20)
    a.bcs("um_r")
    a.lda_imm(2)
    a.sta_zp(MASON_PH)
    a.jsr("script_mason")
    a.label("um_r")
    a.rts()

    a.label("upd_anne")
    a.a8xy16()
    a.lda_zp(ANNE_PH)
    a.cmp_imm(1)
    a.beq("ua_ap")
    a.cmp_imm(3)
    a.beq("ua_lv")
    a.rts()
    a.label("ua_ap")
    a.lda_zp(MAP_ID)
    a.cmp_imm(1)
    a.beq("ua_ok")
    a.rts()
    a.label("ua_ok")
    a.rep(0x20)
    a.lda_zp(P_X)
    a.cmp_zp(A_X)
    a.sep(0x20)
    a.beq("ua_x")
    a.bcs("ua_xr")
    a.rep(0x20)
    a.dec_zp(A_X)
    a.sep(0x20)
    a.bra("ua_x")
    a.label("ua_xr")
    a.rep(0x20)
    a.inc_zp(A_X)
    a.sep(0x20)
    a.label("ua_x")
    a.rep(0x20)
    a.lda_zp(P_Y)
    a.cmp_zp(A_Y)
    a.sep(0x20)
    a.beq("ua_y")
    a.bcs("ua_yd")
    a.rep(0x20)
    a.dec_zp(A_Y)
    a.sep(0x20)
    a.bra("ua_y")
    a.label("ua_yd")
    a.rep(0x20)
    a.inc_zp(A_Y)
    a.sep(0x20)
    a.label("ua_y")
    a.rep(0x20)
    a.lda_zp(P_X)
    a.sec()
    a.sbc_zp(A_X)
    a.bpl("ua_ax")
    a.eor_imm(0xFFFF)
    a.inca()
    a.label("ua_ax")
    a.sta_zp(TMPW)
    a.lda_zp(P_Y)
    a.sec()
    a.sbc_zp(A_Y)
    a.bpl("ua_ay")
    a.eor_imm(0xFFFF)
    a.inca()
    a.label("ua_ay")
    a.clc()
    a.adc_zp(TMPW)
    a.cmp_imm(16)
    a.sep(0x20)
    a.bcs("ua_r")
    a.lda_imm(2)
    a.sta_zp(ANNE_PH)
    a.jsr("script_anne")
    a.label("ua_r")
    a.rts()
    a.label("ua_lv")
    a.rep(0x20)
    a.inc_zp(A_Y)
    a.inc_zp(A_Y)
    a.lda_zp(A_Y)
    a.cmp_zp(P_Y)
    a.sep(0x20)
    a.bcc("ua_r2")
    a.rep(0x20)
    a.lda_zp(A_Y)
    a.sec()
    a.sbc_zp(P_Y)
    a.cmp_imm(160)
    a.sep(0x20)
    a.bcc("ua_r2")
    a.stz_zp(ANNE_PH)
    a.label("ua_r2")
    a.rts()

    a.label("try_talk")
    a.a8xy16()
    a.lda_zp(MAP_ID)
    a.cmp_imm(0)
    a.bne("tt_v")
    a.jmp("talk_house")
    a.label("tt_v")
    a.cmp_imm(1)
    a.bne("tt_f")
    a.jmp("talk_veld")
    a.label("tt_f")
    a.cmp_imm(2)
    a.bne("tt_g")
    a.jmp("talk_forest")
    a.label("tt_g")
    a.jmp("talk_grove")

    def near_mark(a, mx, my, lab_hit, lab_miss):
        # if player near metatile mx,my -> hit
        a.rep(0x20)
        a.lda_zp(P_X)
        a.clc()
        a.adc_imm(8)
        a.sec()
        a.sbc_imm(mx * 16 + 8)
        a.bpl(lab_hit + "_ax")
        a.eor_imm(0xFFFF)
        a.inca()
        a.label(lab_hit + "_ax")
        a.cmp_imm(24)
        a.bcs(lab_miss)
        a.lda_zp(P_Y)
        a.clc()
        a.adc_imm(8)
        a.sec()
        a.sbc_imm(my * 16 + 8)
        a.bpl(lab_hit + "_ay")
        a.eor_imm(0xFFFF)
        a.inca()
        a.label(lab_hit + "_ay")
        a.cmp_imm(24)
        a.bcs(lab_miss)
        a.sep(0x20)
        a.bra(lab_hit)
        # miss falls through as 16-bit? fix
        # actually bcs miss still 16-bit. miss should sep
        pass

    # house marks: B(2,4) U(2,6) S(7,4) C(11,4)
    a.label("talk_house")
    a.a8xy16()
    # father B 2,4
    a.rep(0x20)
    a.lda_zp(P_X)
    a.clc()
    a.adc_imm(8)
    a.sec()
    a.sbc_imm(2 * 16 + 8)
    a.bpl("th_bax")
    a.eor_imm(0xFFFF)
    a.inca()
    a.label("th_bax")
    a.cmp_imm(28)
    a.bcs("th_u")
    a.lda_zp(P_Y)
    a.clc()
    a.adc_imm(8)
    a.sec()
    a.sbc_imm(4 * 16 + 8)
    a.bpl("th_bay")
    a.eor_imm(0xFFFF)
    a.inca()
    a.label("th_bay")
    a.cmp_imm(28)
    a.bcs("th_u")
    a.sep(0x20)
    a.jmp("script_father")
    a.label("th_u")
    a.rep(0x20)
    a.lda_zp(P_X)
    a.clc()
    a.adc_imm(8)
    a.sec()
    a.sbc_imm(2 * 16 + 8)
    a.bpl("th_uax")
    a.eor_imm(0xFFFF)
    a.inca()
    a.label("th_uax")
    a.cmp_imm(24)
    a.bcs("th_s")
    a.lda_zp(P_Y)
    a.clc()
    a.adc_imm(8)
    a.sec()
    a.sbc_imm(6 * 16 + 8)
    a.bpl("th_uay")
    a.eor_imm(0xFFFF)
    a.inca()
    a.label("th_uay")
    a.cmp_imm(24)
    a.bcs("th_s")
    a.sep(0x20)
    a.jmp("script_bed")
    a.label("th_s")
    a.rep(0x20)
    a.lda_zp(P_X)
    a.clc()
    a.adc_imm(8)
    a.sec()
    a.sbc_imm(7 * 16 + 8)
    a.bpl("th_sax")
    a.eor_imm(0xFFFF)
    a.inca()
    a.label("th_sax")
    a.cmp_imm(24)
    a.bcs("th_c")
    a.lda_zp(P_Y)
    a.clc()
    a.adc_imm(8)
    a.sec()
    a.sbc_imm(4 * 16 + 8)
    a.bpl("th_say")
    a.eor_imm(0xFFFF)
    a.inca()
    a.label("th_say")
    a.cmp_imm(24)
    a.bcs("th_c")
    a.sep(0x20)
    a.jmp("script_shelf")
    a.label("th_c")
    a.rep(0x20)
    a.lda_zp(P_X)
    a.clc()
    a.adc_imm(8)
    a.sec()
    a.sbc_imm(11 * 16 + 8)
    a.bpl("th_cax")
    a.eor_imm(0xFFFF)
    a.inca()
    a.label("th_cax")
    a.cmp_imm(24)
    a.sep(0x20)
    a.bcs("th_r")
    a.rep(0x20)
    a.lda_zp(P_Y)
    a.clc()
    a.adc_imm(8)
    a.sec()
    a.sbc_imm(4 * 16 + 8)
    a.bpl("th_cay")
    a.eor_imm(0xFFFF)
    a.inca()
    a.label("th_cay")
    a.cmp_imm(24)
    a.sep(0x20)
    a.bcs("th_r")
    a.jmp("script_crate")
    a.label("th_r")
    a.sep(0x20)
    a.rts()

    a.label("talk_veld")
    a.a8xy16()
    # mason if ph>=2
    a.lda_zp(MASON_PH)
    a.cmp_imm(2)
    a.bcc("tv_a")
    a.rep(0x20)
    a.lda_zp(P_X)
    a.sec()
    a.sbc_zp(M_X)
    a.bpl("tv_max")
    a.eor_imm(0xFFFF)
    a.inca()
    a.label("tv_max")
    a.cmp_imm(24)
    a.bcs("tv_a")
    a.lda_zp(P_Y)
    a.sec()
    a.sbc_zp(M_Y)
    a.bpl("tv_may")
    a.eor_imm(0xFFFF)
    a.inca()
    a.label("tv_may")
    a.cmp_imm(24)
    a.bcs("tv_a")
    a.sep(0x20)
    a.lda_zp(FLAGS0)
    a.and_imm(1 << F_MASON)
    a.bne("tv_mdone")
    a.jmp("script_mason")
    a.label("tv_mdone")
    a.jmp("script_mason2")
    a.label("tv_a")
    a.sep(0x20)
    a.lda_zp(ANNE_PH)
    a.cmp_imm(2)
    a.bne("tv_k")
    a.jmp("script_anne")
    a.label("tv_k")
    # Wren K (3,4)
    a.jmp("talk_veld_npcs")

    a.label("talk_veld_npcs")
    a.a8xy16()
    a.jsr("near_wren")
    a.bcc("tvn1")
    a.jmp("script_wren")
    a.label("tvn1")
    a.jsr("near_ivo")
    a.bcc("tvn2")
    a.jmp("script_ivo")
    a.label("tvn2")
    a.jsr("near_nell")
    a.bcc("tvn3")
    a.jmp("script_nell")
    a.label("tvn3")
    a.jsr("near_pike")
    a.bcc("tvn4")
    a.jmp("script_pike")
    a.label("tvn4")
    a.jsr("near_bram")
    a.bcc("tvn5")
    a.lda_imm(M_SHOP)
    a.sta_zp(MODE)
    a.rts()
    a.label("tvn5")
    a.jsr("near_calder")
    a.bcc("tvn6")
    a.jmp("script_calder")
    a.label("tvn6")
    a.jsr("near_herb")
    a.bcc("tvn7")
    a.jmp("script_herb")
    a.label("tvn7")
    a.jsr("near_gem")
    a.bcc("tvn8")
    a.jmp("script_gem")
    a.label("tvn8")
    a.jsr("near_stump")
    a.bcc("tvn9")
    a.jmp("script_stump")
    a.label("tvn9")
    a.jsr("near_cart")
    a.bcc("tvn0")
    a.jmp("script_cart")
    a.label("tvn0")
    a.rts()

    def make_near(label, mx, my):
        a.label(label)
        a.a8xy16()
        a.rep(0x20)
        a.lda_zp(P_X)
        a.clc()
        a.adc_imm(8)
        a.sec()
        a.sbc_imm(mx * 16 + 8)
        a.bpl(label + "x")
        a.eor_imm(0xFFFF)
        a.inca()
        a.label(label + "x")
        a.cmp_imm(24)
        a.bcs(label + "n")
        a.lda_zp(P_Y)
        a.clc()
        a.adc_imm(8)
        a.sec()
        a.sbc_imm(my * 16 + 8)
        a.bpl(label + "y")
        a.eor_imm(0xFFFF)
        a.inca()
        a.label(label + "y")
        a.cmp_imm(24)
        a.bcs(label + "n")
        a.sep(0x20)
        a.sec()
        a.rts()
        a.label(label + "n")
        a.sep(0x20)
        a.clc()
        a.rts()

    # veld marks from map
    # K wren (3,4), V ivo (3,8), A nell (24,3), Q pike (3,2),
    # J bram (11,10), E calder (24,19), M herb (5,7), G gem (28,5), L stump (23,12), X cart (7,10)
    make_near("near_wren", 3, 4)
    make_near("near_ivo", 3, 8)
    make_near("near_nell", 24, 3)
    make_near("near_pike", 3, 2)
    make_near("near_bram", 11, 10)
    make_near("near_calder", 24, 19)
    make_near("near_herb", 5, 7)
    make_near("near_gem", 28, 5)
    make_near("near_stump", 23, 12)
    make_near("near_cart", 7, 10)
    make_near("near_s1", 3, 5)
    make_near("near_s2", 22, 5)
    make_near("near_s3", 21, 17)
    make_near("near_cath", 13, 11)
    make_near("near_shin", 12, 17)

    a.label("talk_forest")
    a.a8xy16()
    a.jsr("near_s1")
    a.bcc("tf1")
    a.jmp("script_sol")
    a.label("tf1")
    a.jsr("near_s2")
    a.bcc("tf2")
    a.jmp("script_sol")
    a.label("tf2")
    a.jsr("near_s3")
    a.bcc("tf3")
    a.jmp("script_sol")
    a.label("tf3")
    a.rts()

    a.label("talk_grove")
    a.a8xy16()
    a.jsr("near_cath")
    a.bcc("tg1")
    a.lda_zp(FLAGS1)
    a.and_imm(1 << (F_CATH - 8))
    a.bne("tg_cgone")
    a.jmp("script_cath")
    a.label("tg_cgone")
    a.jmp("script_cath_gone")
    a.label("tg1")
    a.jsr("near_shin")
    a.bcc("tg2")
    a.jmp("script_shin")
    a.label("tg2")
    a.rts()

    # ---------- VM / scripts ----------
    a.label("run_script")  # SCR already set
    a.a8xy16()
    a.lda_imm(M_TALK)
    a.sta_zp(MODE)
    a.stz_zp(TALK_I)
    a.jsr("vm_step")
    a.rts()

    a.label("vm_step")
    a.a8xy16()
    a.label("vm_l")
    a.lda_longind(SCR)
    a.bne_far("vm1")
    a.jmp("vm_end")
    a.label("vm1")
    a.cmp_imm(OP_SAY)
    a.bne("vm2s")
    a.jmp("vm_say")
    a.label("vm2s")
    a.cmp_imm(OP_GIVE_PUP)
    a.bne("vm2")
    a.jmp("vm_pup")
    a.label("vm2")
    a.cmp_imm(OP_SALVE)
    a.bne("vm3")
    a.inc_zp(BAG_SALVE)
    a.jmp("vm_skip1")
    a.label("vm3")
    a.cmp_imm(OP_BAND)
    a.bne("vm4")
    a.inc_zp(BAG_BAND)
    a.jmp("vm_skip1")
    a.label("vm4")
    a.cmp_imm(OP_ROOT)
    a.bne("vm5")
    a.inc_zp(BAG_ROOT)
    a.jmp("vm_skip1")
    a.label("vm5")
    a.cmp_imm(OP_GEM)
    a.bne("vm6")
    a.inc_zp(BAG_GEM)
    a.jmp("vm_skip1")
    a.label("vm6")
    a.cmp_imm(OP_FLAG)
    a.bne("vm7")
    a.jmp("vm_flag")
    a.label("vm7")
    a.cmp_imm(OP_BATTLE)
    a.bne("vm8")
    a.jmp("vm_bat")
    a.label("vm8")
    a.cmp_imm(OP_HEAL)
    a.bne("vm9")
    a.lda_zp(P_MHP)
    a.sta_zp(P_HP)
    a.lda_imm(3)
    a.sta_zp(P_SPP)
    a.jmp("vm_skip1")
    a.label("vm9")
    a.cmp_imm(OP_ANNE)
    a.bne("vm10")
    a.jsr("scr_inc")
    a.lda_longind(SCR)
    a.sta_zp(ANNE_PH)
    a.jsr("scr_inc")
    a.jmp("vm_l")
    a.label("vm10")
    a.cmp_imm(OP_MASON)
    a.bne("vm11")
    a.jsr("scr_inc")
    a.lda_longind(SCR)
    a.sta_zp(MASON_PH)
    a.jsr("scr_inc")
    a.jmp("vm_l")
    a.label("vm11")
    a.cmp_imm(OP_SHOP)
    a.bne("vm12")
    a.lda_imm(M_SHOP)
    a.sta_zp(MODE)
    a.rts()
    a.label("vm12")
    a.cmp_imm(OP_IFN)
    a.bne("vm13")
    a.jmp("vm_ifn")
    a.label("vm13")
    a.cmp_imm(OP_IF)
    a.bne("vm14")
    a.jmp("vm_if")
    a.label("vm14")
    a.cmp_imm(OP_MODE)
    a.bne("vm15")
    a.jsr("scr_inc")
    a.lda_longind(SCR)
    a.sta_zp(MODE)
    a.rts()
    a.label("vm15")
    a.jsr("scr_inc")
    a.jmp("vm_l")

    a.label("vm_end")
    a.lda_imm(M_WORLD)
    a.sta_zp(MODE)
    a.rts()

    a.label("scr_inc")
    a.inc_zp(SCR)
    a.bne("si1")
    a.inc_zp(SCR + 1)
    a.bne("si1")
    a.inc_zp(SCR + 2)
    a.label("si1")
    a.rts()

    a.label("vm_skip1")
    a.jsr("scr_inc")
    a.jmp("vm_l")

    a.label("vm_say")
    a.jsr("scr_inc")
    a.lda_longind(SCR)
    a.sta_zp(TALK_WHO)
    a.jsr("scr_inc")
    # leave SCR pointing at string; talk mode waits
    a.lda_imm(M_TALK)
    a.sta_zp(MODE)
    a.rts()

    a.label("vm_pup")
    a.lda_imm(1)
    a.sta_zp(NPARTY)
    a.lda_imm(34)
    a.sta_zp(P_HP)
    a.sta_zp(P_MHP)
    a.lda_imm(3)
    a.sta_zp(P_SPP)
    a.jmp("vm_skip1")

    a.label("vm_flag")
    a.jsr("scr_inc")
    a.lda_longind(SCR)
    a.sta_zp(TMP0)
    a.cmp_imm(8)
    a.bcc("vf0")
    a.sec()
    a.sbc_imm(8)
    a.sta_zp(TMP0)
    a.lda_imm(1)
    # X is 16-bit here (vm_step's calling convention); ldx_zp(TMP0) would
    # otherwise pull in TMP1 as a garbage high byte — and TMP1 still holds
    # a preceding OP_IFN's skip-count — turning a small shift count into a
    # huge one that shifts the flag bit out to zero before it's OR'd in.
    a.sep(0x10)
    a.ldx_zp(TMP0)
    a.beq("vf1s")
    a.label("vf1l")
    a.asl_a()
    a.dex()
    a.bne("vf1l")
    a.label("vf1s")
    a.rep(0x10)
    a.ora_zp(FLAGS1)
    a.sta_zp(FLAGS1)
    a.jsr("scr_inc")
    a.jmp("vm_l")
    a.label("vf0")
    a.lda_imm(1)
    a.sep(0x10)
    a.ldx_zp(TMP0)
    a.beq("vf0s")
    a.label("vf0l")
    a.asl_a()
    a.dex()
    a.bne("vf0l")
    a.label("vf0s")
    a.rep(0x10)
    a.ora_zp(FLAGS0)
    a.sta_zp(FLAGS0)
    a.jsr("scr_inc")
    a.jmp("vm_l")

    a.label("vm_bat")
    a.jsr("scr_inc")
    a.lda_longind(SCR)
    a.sta_zp(B_FOE)
    a.jsr("scr_inc")
    a.lda_longind(SCR)
    a.sta_zp(B_TRAINER)
    a.jsr("scr_inc")
    a.lda_longind(SCR)
    a.sta_zp(B_WILD)
    a.jsr("scr_inc")
    a.jsr("start_battle")
    a.rts()

    a.label("vm_ifn")
    a.jsr("scr_inc")
    a.lda_longind(SCR)
    a.sta_zp(TMP0)
    a.jsr("scr_inc")
    a.lda_longind(SCR)
    a.sta_zp(TMP1)  # skip
    a.jsr("test_flag")
    a.beq("vifn_ok")  # flag clear -> don't skip
    a.lda_zp(TMP1)
    a.sta_zp(TMP2)
    a.label("vifn_s")
    a.jsr("scr_inc")
    a.dec_zp(TMP2)
    a.bne("vifn_s")
    a.jsr("scr_inc")  # skip the skip-byte itself already consumed; TMP1 bytes of following
    a.jmp("vm_l")
    a.label("vifn_ok")
    a.jsr("scr_inc")
    a.jmp("vm_l")

    a.label("vm_if")
    a.jsr("scr_inc")
    a.lda_longind(SCR)
    a.sta_zp(TMP0)
    a.jsr("scr_inc")
    a.lda_longind(SCR)
    a.sta_zp(TMP1)
    a.jsr("test_flag")
    a.bne("vif_ok")
    a.lda_zp(TMP1)
    a.sta_zp(TMP2)
    a.label("vif_s")
    a.jsr("scr_inc")
    a.dec_zp(TMP2)
    a.bne("vif_s")
    a.jsr("scr_inc")
    a.jmp("vm_l")
    a.label("vif_ok")
    a.jsr("scr_inc")
    a.jmp("vm_l")

    a.label("test_flag")  # TMP0 = bit 0-15, Z=1 if clear
    a.lda_zp(TMP0)
    a.cmp_imm(8)
    a.bcc("tf_0")
    a.sec()
    a.sbc_imm(8)
    a.tax()
    a.lda_zp(FLAGS1)
    a.bra("tf_t")
    a.label("tf_0")
    a.tax()
    a.lda_zp(FLAGS0)
    a.label("tf_t")
    a.cpx_imm(0)
    a.beq("tf_d")
    a.label("tf_sh")
    a.lsr_a()
    a.dex()
    a.bne("tf_sh")
    a.label("tf_d")
    a.and_imm(1)
    a.rts()

    a.label("upd_talk")
    a.jsr("pressed_a")
    a.beq("utk_r")
    # skip rest of string
    a.label("utk_sk")
    a.lda_longind(SCR)
    a.beq("utk_n")
    a.jsr("scr_inc")
    a.bra("utk_sk")
    a.label("utk_n")
    a.jsr("scr_inc")  # skip NUL
    a.jsr("vm_step")
    a.label("utk_r")
    a.rts()

    # ---------- battle ----------
    a.label("start_battle")
    a.a8xy16()
    a.lda_imm(M_BATTLE)
    a.sta_zp(MODE)
    a.stz_zp(B_PHASE)  # msg
    a.stz_zp(B_CUR)
    a.lda_zp(P_HP)
    a.bne("sb_hp")
    a.lda_zp(P_MHP)
    a.sta_zp(P_HP)
    a.label("sb_hp")
    a.lda_zp(P_HP)
    a.sta_zp(B_HP)
    a.lda_zp(P_MHP)
    a.sta_zp(B_MHP)
    a.lda_zp(P_SPP)
    a.sta_zp(B_SPP)
    a.lda_zp(B_FOE)
    a.rep(0x20)
    a.and_imm(0x00FF)
    a.asl_a()
    a.tax()
    a.sep(0x20)
    a.lda_absx("foe_hp")
    a.sta_zp(F_MHP)
    a.sta_zp(F_HP)
    a.rts()

    a.label("upd_battle")
    a.a8xy16()
    a.lda_zp(B_PHASE)
    a.beq("ub_msg")
    a.cmp_imm(1)
    a.beq("ub_menu")
    a.cmp_imm(2)
    a.beq("ub_atk")
    a.cmp_imm(3)
    a.beq("ub_foe")
    a.cmp_imm(4)
    a.beq("ub_win")
    a.cmp_imm(5)
    a.beq("ub_lose")
    a.rts()
    a.label("ub_msg")
    a.jsr("pressed_a")
    a.beq("ub_r")
    a.lda_imm(1)
    a.sta_zp(B_PHASE)
    a.stz_zp(B_CUR)
    a.rts()
    a.label("ub_menu")
    a.lda_zp(JOY_NH)
    a.and_imm(0x04)
    a.beq("ub_mu")
    a.lda_zp(B_CUR)
    a.inca()
    a.cmp_imm(3)
    a.bcc("ub_ms")
    a.lda_imm(0)
    a.label("ub_ms")
    a.sta_zp(B_CUR)
    a.label("ub_mu")
    a.lda_zp(JOY_NH)
    a.and_imm(0x08)
    a.beq("ub_ma")
    a.lda_zp(B_CUR)
    a.bne("ub_md")
    a.lda_imm(3)
    a.label("ub_md")
    a.deca()
    a.sta_zp(B_CUR)
    a.label("ub_ma")
    a.jsr("pressed_a")
    a.beq("ub_r")
    a.lda_zp(B_CUR)
    a.cmp_imm(2)
    a.bne("ub_do")
    # run
    a.lda_zp(B_WILD)
    a.beq("ub_norun")
    a.lda_imm(M_WORLD)
    a.sta_zp(MODE)
    a.rts()
    a.label("ub_norun")
    a.rts()
    a.label("ub_do")
    a.lda_imm(2)
    a.sta_zp(B_PHASE)
    a.rts()
    a.label("ub_atk")
    # apply damage
    a.jsr("rng")
    a.and_imm(7)
    a.clc()
    a.adc_imm(8)
    a.sta_zp(TMP0)
    a.lda_zp(B_CUR)
    a.beq("ub_nip")
    a.lda_zp(B_SPP)
    a.beq("ub_nip")
    a.dec_zp(B_SPP)
    a.lda_zp(TMP0)
    a.clc()
    a.adc_imm(8)
    a.sta_zp(TMP0)
    a.label("ub_nip")
    a.lda_zp(F_HP)
    a.sec()
    a.sbc_zp(TMP0)
    a.bcs("ub_fa")
    a.lda_imm(0)
    a.label("ub_fa")
    a.sta_zp(F_HP)
    a.beq("ub_kd")
    a.lda_imm(3)
    a.sta_zp(B_PHASE)
    a.rts()
    a.label("ub_kd")
    a.lda_imm(4)
    a.sta_zp(B_PHASE)
    a.rts()
    a.label("ub_foe")
    a.jsr("pressed_a")
    a.beq("ub_r")
    a.jsr("rng")
    a.and_imm(7)
    a.clc()
    a.adc_imm(4)
    a.sta_zp(TMP0)
    a.lda_zp(B_HP)
    a.sec()
    a.sbc_zp(TMP0)
    a.bcs("ub_ph")
    a.lda_imm(0)
    a.label("ub_ph")
    a.sta_zp(B_HP)
    a.beq("ub_dead")
    a.lda_imm(1)
    a.sta_zp(B_PHASE)
    a.rts()
    a.label("ub_dead")
    a.lda_imm(5)
    a.sta_zp(B_PHASE)
    a.rts()
    a.label("ub_win")
    a.jsr("pressed_a")
    a.beq("ub_r")
    a.lda_zp(B_HP)
    a.sta_zp(P_HP)
    a.lda_zp(B_SPP)
    a.sta_zp(P_SPP)
    a.inc_zp(BATTLES)
    a.lda_zp(B_TRAINER)
    a.cmp_imm(1)  # mason
    a.bne("ub_w2")
    a.lda_zp(FLAGS0)
    a.ora_imm(1 << F_MASON)
    a.sta_zp(FLAGS0)
    a.lda_imm(3)
    a.sta_zp(MASON_PH)
    # A is now 3 (just written to MASON_PH), not B_TRAINER — falling
    # through into the checks below would spuriously match "shin" (3)
    # and fire the demo ending. Skip straight to the shared world-return.
    a.jmp("ub_w4")
    a.label("ub_w2")
    a.cmp_imm(2)  # calder
    a.bne("ub_w3")
    a.lda_zp(FLAGS1)
    a.ora_imm(1 << (F_CALDER - 8))
    a.sta_zp(FLAGS1)
    a.lda_imm(M_END)
    a.sta_zp(MODE)
    a.rts()
    a.label("ub_w3")
    a.cmp_imm(3)  # shin
    a.bne("ub_w3c")
    a.lda_zp(FLAGS1)
    a.ora_imm(1 << (F_SHIN - 8))
    a.sta_zp(FLAGS1)
    a.lda_imm(M_END)
    a.sta_zp(MODE)
    a.rts()
    a.label("ub_w3c")
    a.cmp_imm(4)  # cathleen
    a.bne("ub_w4")
    a.lda_zp(FLAGS1)
    a.ora_imm(1 << (F_CATH - 8))
    a.sta_zp(FLAGS1)
    a.label("ub_w4")
    a.lda_imm(M_WORLD)
    a.sta_zp(MODE)
    a.lda_zp(ANNE_PH)
    a.bne("ub_r")
    a.lda_zp(FLAGS0)
    a.and_imm(1 << F_ANNE)
    a.bne("ub_r")
    a.lda_zp(BATTLES)
    a.beq("ub_r")
    a.lda_zp(MAP_ID)
    a.cmp_imm(1)
    a.bne("ub_r")
    a.lda_imm(1)
    a.sta_zp(ANNE_PH)
    a.rep(0x20)
    a.lda_zp(P_X)
    a.sta_zp(A_X)
    a.lda_zp(P_Y)
    a.clc()
    a.adc_imm(64)
    a.sta_zp(A_Y)
    a.sep(0x20)
    a.rts()
    a.label("ub_lose")
    a.jsr("pressed_a")
    a.beq("ub_r")
    a.lda_zp(P_MHP)
    a.sta_zp(P_HP)
    a.lda_imm(3)
    a.sta_zp(P_SPP)
    a.lda_imm(0)
    a.jsr("request_map")
    a.rep(0x20)
    a.lda_imm(2 * 16)
    a.sta_zp(P_X)
    a.lda_imm(6 * 16)
    a.sta_zp(P_Y)
    a.sep(0x20)
    a.lda_imm(M_WORLD)
    a.sta_zp(MODE)
    a.label("ub_r")
    a.rts()

    a.label("upd_bag")
    a.jsr("pressed_a")
    a.bne("ubg_c")
    a.jsr("pressed_b")
    a.bne("ubg_c")
    a.jsr("pressed_sel")
    a.beq("ubg_r")
    a.label("ubg_c")
    a.lda_imm(M_WORLD)
    a.sta_zp(MODE)
    a.label("ubg_r")
    a.rts()

    a.label("upd_party")
    a.jsr("pressed_a")
    a.bne("upy_c")
    a.jsr("pressed_b")
    a.bne("upy_c")
    a.jsr("pressed_st")
    a.beq("upy_r")
    a.label("upy_c")
    a.lda_imm(M_WORLD)
    a.sta_zp(MODE)
    a.label("upy_r")
    a.rts()

    a.label("upd_shop")
    a.jsr("pressed_a")
    a.beq("ush_b")
    a.lda_zp(MARKS)
    a.cmp_imm(8)
    a.bcc("ush_b")
    a.sec()
    a.sbc_imm(8)
    a.sta_zp(MARKS)
    a.inc_zp(BAG_SALVE)
    a.label("ush_b")
    a.jsr("pressed_b")
    a.beq("ush_r")
    a.lda_imm(M_WORLD)
    a.sta_zp(MODE)
    a.label("ush_r")
    a.rts()

    a.label("upd_end")
    a.jsr("pressed_a")
    a.beq("ue_r")
    a.jsr("show_title")
    a.label("ue_r")
    a.rts()

    # ---------- draw ----------
    a.label("draw")
    a.jsr("oam_clear")
    a.jsr("bg3_clear")
    a.lda_imm(0x15)  # BG1 + BG3 + OBJ
    a.sta_abs(0x212C)
    a.lda_zp(MODE)
    a.cmp_imm(M_TITLE)
    a.bne("dr1")
    a.jmp("draw_title")
    a.label("dr1")
    a.cmp_imm(M_BATTLE)
    a.bne("dr2")
    a.jmp("draw_battle")
    a.label("dr2")
    a.cmp_imm(M_BAG)
    a.bne("dr3")
    a.jmp("draw_bag")
    a.label("dr3")
    a.cmp_imm(M_PARTY)
    a.bne("dr4")
    a.jmp("draw_party")
    a.label("dr4")
    a.cmp_imm(M_SHOP)
    a.bne("dr5")
    a.jmp("draw_shop")
    a.label("dr5")
    a.cmp_imm(M_END)
    a.bne("dr6")
    a.jmp("draw_end")
    a.label("dr6")
    a.jmp("draw_world")

    a.label("spr_world")  # SP_X/Y world -> screen using cam (16x16)
    a.rep(0x20)
    a.lda_zp(SP_X)
    a.sec()
    a.sbc_zp(CAM_X)
    a.sta_zp(SP_X)
    a.lda_zp(SP_Y)
    a.sec()
    a.sbc_zp(CAM_Y)
    a.sta_zp(SP_Y)
    a.sep(0x20)
    a.jsr("oam_add")
    a.rts()

    a.label("spr_tall")  # 16x32: two 16x16, feet stay at world SP_Y+16
    a.a8xy16()
    a.rep(0x20)
    a.lda_zp(SP_X)
    a.sta_zp(TMPW)
    a.sec()
    a.sbc_zp(CAM_X)
    a.sta_zp(SP_X)
    a.lda_zp(SP_Y)
    a.sec()
    a.sbc_zp(CAM_Y)
    a.sec()
    a.sbc_imm(16)
    a.sta_zp(SP_Y)
    a.sep(0x20)
    a.stz_zp(SP_SZ)
    a.jsr("oam_add")
    a.lda_zp(SP_Y)
    a.clc()
    a.adc_imm(16)
    a.sta_zp(SP_Y)
    a.lda_zp(SP_TL)
    a.clc()
    a.adc_imm(32)
    a.sta_zp(SP_TL)
    a.jsr("oam_add")
    a.rts()

    a.label("draw_title")
    a.a8xy16()
    # Hide the veld — title is a plate, not the overworld.
    a.lda_imm(0x14)  # BG3 + OBJ
    a.sta_abs(0x212C)
    # Full-screen dark (tile 2, pal 4, prio) then cream card
    a.rep(0x20)
    a.lda_imm(0x3002)
    a.jsr("bg3_fill")
    a.sep(0x20)
    a.lda_imm(4)
    a.sta_zp(TMP0)
    a.lda_imm(3)
    a.sta_zp(DRAWX)
    a.lda_imm(3)
    a.sta_zp(DRAWY)
    a.lda_imm(26)
    a.sta_zp(TMP2)
    a.lda_imm(16)
    a.sta_zp(TMP3)
    a.jsr("bg3_box")
    a.lda_imm(10)
    a.sta_zp(DRAWX)
    a.lda_imm(5)
    a.sta_zp(DRAWY)
    a.lda_imm(4)
    a.sta_zp(TMP0)
    a.ldx_imm("str_crymon")
    a.stx_zp(STRPTR)
    a.lda_imm(1)
    a.sta_zp(STRPTR + 2)
    a.jsr("big_str")
    a.lda_imm(11)
    a.sta_zp(DRAWX)
    a.lda_imm(9)
    a.sta_zp(DRAWY)
    a.ldx_imm("str_run")
    a.stx_zp(STRPTR)
    a.lda_imm(1)
    a.sta_zp(STRPTR + 2)
    a.jsr("bg3_str")
    a.lda_imm(8)
    a.sta_zp(DRAWX)
    a.lda_imm(15)
    a.sta_zp(DRAWY)
    a.ldx_imm("str_begin")
    a.stx_zp(STRPTR)
    a.jsr("bg3_str")
    a.a8xy16()
    a.rep(0x20)
    a.lda_imm(32)
    a.sta_zp(SP_X)
    a.lda_imm(152)
    a.sta_zp(SP_Y)
    a.sep(0x20)
    a.lda_imm(0)  # 16x32 Max down
    a.sta_zp(SP_TL)
    a.lda_imm(0x20)
    a.sta_zp(SP_AT)
    a.stz_zp(SP_SZ)
    a.jsr("oam_add")
    a.lda_imm(168)  # y+16
    a.sta_zp(SP_Y)
    a.lda_imm(32)
    a.sta_zp(SP_TL)
    a.jsr("oam_add")
    a.rep(0x20)
    a.lda_imm(184)
    a.sta_zp(SP_X)
    a.lda_imm(152)
    a.sta_zp(SP_Y)
    a.sep(0x20)
    a.lda_imm(192)
    a.sta_zp(SP_TL)
    a.lda_imm(0x20 | (4 << 1))
    a.sta_zp(SP_AT)
    a.lda_imm(1)
    a.sta_zp(SP_SZ)
    a.jsr("oam_add")
    a.rts()

    a.label("draw_world")
    a.a8xy16()
    # HUD
    a.lda_imm(4)
    a.sta_zp(TMP0)
    a.lda_imm(1)
    a.sta_zp(DRAWX)
    a.stz_zp(DRAWY)
    a.ldx_imm("str_hud")
    a.stx_zp(STRPTR)
    a.lda_imm(1)
    a.sta_zp(STRPTR + 2)
    a.lda_zp(NPARTY)
    a.beq("dw_np")
    a.jsr("bg3_str")
    a.lda_imm(10)
    a.sta_zp(DRAWX)
    a.stz_zp(DRAWY)
    a.lda_zp(P_HP)
    a.jsr("print_num")
    a.lda_imm(ord("/"))
    a.jsr("bg3_put")
    a.inc_zp(DRAWX)
    a.lda_zp(P_MHP)
    a.jsr("print_num")
    a.label("dw_np")
    a.lda_imm(24)
    a.sta_zp(DRAWX)
    a.stz_zp(DRAWY)
    a.lda_imm(ord("M"))
    a.jsr("bg3_put")
    a.inc_zp(DRAWX)
    a.lda_zp(MARKS)
    a.jsr("print_num")
    # player
    a.lda_zp(P_DIR)
    a.asl_a()
    a.clc()
    a.adc_zp(P_FRAME)
    a.asl_a()  # tile = (dir*2+frame)*2
    a.sta_zp(SP_TL)
    a.lda_imm(0x20)
    a.sta_zp(SP_AT)
    a.stz_zp(SP_SZ)
    a.rep(0x20)
    a.lda_zp(P_X)
    a.sta_zp(SP_X)
    a.lda_zp(P_Y)
    a.sta_zp(SP_Y)
    a.sep(0x20)
    a.jsr("spr_tall")
    # mason
    a.lda_zp(MASON_PH)
    a.beq("dw_nm")
    a.lda_zp(MAP_ID)
    a.cmp_imm(1)
    a.bne("dw_nm")
    a.lda_zp(M_DIR)
    a.asl_a()
    a.clc()
    a.adc_imm(72)
    a.sta_zp(SP_TL)
    a.lda_imm(0x20 | (2 << 1))
    a.sta_zp(SP_AT)
    a.stz_zp(SP_SZ)
    a.rep(0x20)
    a.lda_zp(M_X)
    a.sta_zp(SP_X)
    a.lda_zp(M_Y)
    a.sta_zp(SP_Y)
    a.sep(0x20)
    a.jsr("spr_tall")
    a.label("dw_nm")
    a.lda_zp(ANNE_PH)
    a.beq("dw_na2")
    a.lda_zp(MAP_ID)
    a.cmp_imm(1)
    a.bne("dw_na2")
    a.lda_imm(64)  # anne down 16x32
    a.sta_zp(SP_TL)
    a.lda_imm(0x20 | (1 << 1))
    a.sta_zp(SP_AT)
    a.stz_zp(SP_SZ)
    a.rep(0x20)
    a.lda_zp(A_X)
    a.sta_zp(SP_X)
    a.lda_zp(A_Y)
    a.sta_zp(SP_Y)
    a.sep(0x20)
    a.jsr("spr_tall")
    a.label("dw_na2")
    a.jsr("draw_npcs")
    a.lda_zp(MODE)
    a.cmp_imm(M_TALK)
    a.bne("dw_r")
    a.jsr("draw_talk")
    a.label("dw_r")
    a.rts()

    a.label("draw_npcs")
    a.a8xy16()
    a.lda_zp(MAP_ID)
    a.cmp_imm(1)
    a.beq("dn_v")
    a.cmp_imm(2)
    a.beq("dn_f")
    a.cmp_imm(3)
    a.beq("dn_g")
    a.rts()
    a.label("dn_v")
    # wren 128 pal3
    a.lda_imm(128)
    a.sta_zp(SP_TL)
    a.lda_imm(0x20 | (3 << 1))
    a.sta_zp(SP_AT)
    a.stz_zp(SP_SZ)
    a.rep(0x20)
    a.lda_imm(3 * 16)
    a.sta_zp(SP_X)
    a.lda_imm(4 * 16)
    a.sta_zp(SP_Y)
    a.sep(0x20)
    a.jsr("spr_tall")
    a.lda_imm(130)
    a.sta_zp(SP_TL)
    a.lda_imm(0x20 | (3 << 1))
    a.sta_zp(SP_AT)
    a.rep(0x20)
    a.lda_imm(3 * 16)
    a.sta_zp(SP_X)
    a.lda_imm(8 * 16)
    a.sta_zp(SP_Y)
    a.sep(0x20)
    a.jsr("spr_tall")
    a.lda_imm(132)
    a.sta_zp(SP_TL)
    a.rep(0x20)
    a.lda_imm(24 * 16)
    a.sta_zp(SP_X)
    a.lda_imm(3 * 16)
    a.sta_zp(SP_Y)
    a.sep(0x20)
    a.jsr("spr_tall")
    a.lda_imm(134)
    a.sta_zp(SP_TL)
    a.rep(0x20)
    a.lda_imm(3 * 16)
    a.sta_zp(SP_X)
    a.lda_imm(2 * 16)
    a.sta_zp(SP_Y)
    a.sep(0x20)
    a.jsr("spr_tall")
    a.lda_imm(136)
    a.sta_zp(SP_TL)
    a.rep(0x20)
    a.lda_imm(11 * 16)
    a.sta_zp(SP_X)
    a.lda_imm(10 * 16)
    a.sta_zp(SP_Y)
    a.sep(0x20)
    a.jsr("spr_tall")
    a.lda_imm(138)
    a.sta_zp(SP_TL)
    a.rep(0x20)
    a.lda_imm(24 * 16)
    a.sta_zp(SP_X)
    a.lda_imm(19 * 16)
    a.sta_zp(SP_Y)
    a.sep(0x20)
    a.jsr("spr_tall")
    a.rts()
    a.label("dn_f")
    a.lda_imm(134)
    a.sta_zp(SP_TL)
    a.lda_imm(0x20 | (3 << 1))
    a.sta_zp(SP_AT)
    a.stz_zp(SP_SZ)
    a.rep(0x20)
    a.lda_imm(3 * 16)
    a.sta_zp(SP_X)
    a.lda_imm(5 * 16)
    a.sta_zp(SP_Y)
    a.sep(0x20)
    a.jsr("spr_tall")
    a.rep(0x20)
    a.lda_imm(22 * 16)
    a.sta_zp(SP_X)
    a.lda_imm(5 * 16)
    a.sta_zp(SP_Y)
    a.sep(0x20)
    a.jsr("spr_tall")
    a.rep(0x20)
    a.lda_imm(21 * 16)
    a.sta_zp(SP_X)
    a.lda_imm(17 * 16)
    a.sta_zp(SP_Y)
    a.sep(0x20)
    a.jsr("spr_tall")
    a.rts()
    a.label("dn_g")
    a.lda_zp(FLAGS1)
    a.and_imm(1 << (F_CATH - 8))
    a.bne("dn_gc")
    a.lda_imm(140)
    a.sta_zp(SP_TL)
    a.lda_imm(0x20 | (3 << 1))
    a.sta_zp(SP_AT)
    a.stz_zp(SP_SZ)
    a.rep(0x20)
    a.lda_imm(13 * 16)
    a.sta_zp(SP_X)
    a.lda_imm(11 * 16)
    a.sta_zp(SP_Y)
    a.sep(0x20)
    a.jsr("spr_tall")
    a.label("dn_gc")
    a.lda_imm(142)
    a.sta_zp(SP_TL)
    a.rep(0x20)
    a.lda_imm(12 * 16)
    a.sta_zp(SP_X)
    a.lda_imm(17 * 16)
    a.sta_zp(SP_Y)
    a.sep(0x20)
    a.jsr("spr_tall")
    a.rts()

    a.label("draw_talk")
    a.a8xy16()
    a.lda_imm(4)
    a.sta_zp(TMP0)
    a.lda_imm(1)
    a.sta_zp(DRAWX)
    a.lda_imm(19)
    a.sta_zp(DRAWY)
    a.lda_imm(30)
    a.sta_zp(TMP2)
    a.lda_imm(8)
    a.sta_zp(TMP3)
    a.jsr("bg3_box")
    a.lda_imm(2)
    a.sta_zp(DRAWX)
    a.lda_imm(20)
    a.sta_zp(DRAWY)
    # speaker name from table
    a.lda_zp(TALK_WHO)
    a.rep(0x20)
    a.and_imm(0x00FF)
    a.asl_a()
    a.tax()
    a.sep(0x20)
    a.lda_absx("who_lo")
    a.sta_zp(STRPTR)
    a.lda_absx(("who_lo", 1))
    a.sta_zp(STRPTR + 1)
    a.lda_imm(1)
    a.sta_zp(STRPTR + 2)
    a.jsr("bg3_str")
    a.lda_imm(2)
    a.sta_zp(DRAWX)
    a.lda_imm(22)
    a.sta_zp(DRAWY)
    a.lda_zp(SCR)
    a.sta_zp(STRPTR)
    a.lda_zp(SCR + 1)
    a.sta_zp(STRPTR + 1)
    a.lda_zp(SCR + 2)
    a.sta_zp(STRPTR + 2)
    a.jsr("bg3_str")
    a.rts()

    a.label("draw_battle")
    a.a8xy16()
    a.lda_imm(4)
    a.sta_zp(TMP0)
    a.stz_zp(DRAWX)
    a.lda_imm(16)
    a.sta_zp(DRAWY)
    a.lda_imm(32)
    a.sta_zp(TMP2)
    a.lda_imm(12)
    a.sta_zp(TMP3)
    a.jsr("bg3_box")
    # foe name
    a.lda_imm(2)
    a.sta_zp(DRAWX)
    a.lda_imm(1)
    a.sta_zp(DRAWY)
    a.lda_zp(B_FOE)
    a.rep(0x20)
    a.and_imm(0x00FF)
    a.asl_a()
    a.tax()
    a.sep(0x20)
    a.lda_absx("foe_lo")
    a.sta_zp(STRPTR)
    a.lda_absx(("foe_lo", 1))
    a.sta_zp(STRPTR + 1)
    a.lda_imm(1)
    a.sta_zp(STRPTR + 2)
    a.jsr("bg3_str")
    a.lda_imm(2)
    a.sta_zp(DRAWX)
    a.lda_imm(2)
    a.sta_zp(DRAWY)
    a.lda_zp(F_HP)
    a.jsr("print_num")
    a.lda_imm(ord("/"))
    a.jsr("bg3_put")
    a.inc_zp(DRAWX)
    a.lda_zp(F_MHP)
    a.jsr("print_num")
    a.lda_imm(2)
    a.sta_zp(DRAWX)
    a.lda_imm(14)
    a.sta_zp(DRAWY)
    a.ldx_imm("str_pup")
    a.stx_zp(STRPTR)
    a.jsr("bg3_str")
    a.lda_imm(2)
    a.sta_zp(DRAWX)
    a.lda_imm(15)
    a.sta_zp(DRAWY)
    a.lda_zp(B_HP)
    a.jsr("print_num")
    a.lda_imm(ord("/"))
    a.jsr("bg3_put")
    a.inc_zp(DRAWX)
    a.lda_zp(B_MHP)
    a.jsr("print_num")
    a.lda_zp(B_PHASE)
    a.cmp_imm(1)
    a.bne("db_nm")
    a.lda_imm(2)
    a.sta_zp(DRAWX)
    a.lda_imm(18)
    a.sta_zp(DRAWY)
    a.ldx_imm("str_nip")
    a.stx_zp(STRPTR)
    a.jsr("bg3_str")
    a.lda_imm(2)
    a.sta_zp(DRAWX)
    a.lda_imm(20)
    a.sta_zp(DRAWY)
    a.ldx_imm("str_quill")
    a.stx_zp(STRPTR)
    a.jsr("bg3_str")
    a.lda_imm(2)
    a.sta_zp(DRAWX)
    a.lda_imm(22)
    a.sta_zp(DRAWY)
    a.ldx_imm("str_run")
    a.stx_zp(STRPTR)
    a.jsr("bg3_str")
    # cursor
    a.lda_imm(1)
    a.sta_zp(DRAWX)
    a.lda_zp(B_CUR)
    a.asl_a()
    a.clc()
    a.adc_imm(18)
    a.sta_zp(DRAWY)
    a.lda_imm(ord(">"))
    a.jsr("bg3_put")
    a.label("db_nm")
    a.lda_zp(B_PHASE)
    a.bne("db_p")
    a.lda_imm(2)
    a.sta_zp(DRAWX)
    a.lda_imm(18)
    a.sta_zp(DRAWY)
    a.ldx_imm("str_appear")
    a.stx_zp(STRPTR)
    a.jsr("bg3_str")
    a.label("db_p")
    a.cmp_imm(4)
    a.bne("db_l")
    a.lda_imm(2)
    a.sta_zp(DRAWX)
    a.lda_imm(18)
    a.sta_zp(DRAWY)
    a.ldx_imm("str_win")
    a.stx_zp(STRPTR)
    a.jsr("bg3_str")
    a.label("db_l")
    a.lda_zp(B_PHASE)
    a.cmp_imm(5)
    a.bne("db_s")
    a.lda_imm(2)
    a.sta_zp(DRAWX)
    a.lda_imm(18)
    a.sta_zp(DRAWY)
    a.ldx_imm("str_lose")
    a.stx_zp(STRPTR)
    a.jsr("bg3_str")
    a.label("db_s")
    # sprites
    a.rep(0x20)
    a.lda_imm(40)
    a.sta_zp(SP_X)
    a.lda_imm(120)
    a.sta_zp(SP_Y)
    a.sep(0x20)
    a.stz_zp(SP_TL)
    a.lda_imm(0x20)
    a.sta_zp(SP_AT)
    a.stz_zp(SP_SZ)
    a.jsr("oam_add")
    a.lda_imm(136)
    a.sta_zp(SP_Y)
    a.lda_imm(32)
    a.sta_zp(SP_TL)
    a.jsr("oam_add")
    a.rep(0x20)
    a.lda_imm(160)
    a.sta_zp(SP_X)
    a.lda_imm(40)
    a.sta_zp(SP_Y)
    a.sep(0x20)
    a.lda_zp(B_FOE)
    a.rep(0x20)
    a.and_imm(0x00FF)
    a.tax()
    a.sep(0x20)
    a.lda_absx("foe_tile")
    a.sta_zp(SP_TL)
    a.lda_absx("foe_attr")
    a.sta_zp(SP_AT)
    a.lda_imm(1)
    a.sta_zp(SP_SZ)
    a.jsr("oam_add")
    a.rts()

    a.label("draw_bag")
    a.lda_imm(4)
    a.sta_zp(TMP0)
    a.lda_imm(4)
    a.sta_zp(DRAWX)
    a.lda_imm(6)
    a.sta_zp(DRAWY)
    a.lda_imm(24)
    a.sta_zp(TMP2)
    a.lda_imm(14)
    a.sta_zp(TMP3)
    a.jsr("bg3_box")
    a.lda_imm(6)
    a.sta_zp(DRAWX)
    a.lda_imm(8)
    a.sta_zp(DRAWY)
    a.ldx_imm("str_bag")
    a.stx_zp(STRPTR)
    a.lda_imm(1)
    a.sta_zp(STRPTR + 2)
    a.jsr("bg3_str")
    a.lda_imm(6)
    a.sta_zp(DRAWX)
    a.lda_imm(10)
    a.sta_zp(DRAWY)
    a.ldx_imm("str_salve")
    a.stx_zp(STRPTR)
    a.jsr("bg3_str")
    a.lda_imm(20)
    a.sta_zp(DRAWX)
    a.lda_zp(BAG_SALVE)
    a.jsr("print_num")
    a.lda_imm(6)
    a.sta_zp(DRAWX)
    a.lda_imm(12)
    a.sta_zp(DRAWY)
    a.ldx_imm("str_xtal")
    a.stx_zp(STRPTR)
    a.jsr("bg3_str")
    a.lda_imm(20)
    a.sta_zp(DRAWX)
    a.lda_zp(BAG_GEM)
    a.jsr("print_num")
    a.rts()

    a.label("draw_party")
    a.lda_imm(4)
    a.sta_zp(TMP0)
    a.lda_imm(4)
    a.sta_zp(DRAWX)
    a.lda_imm(6)
    a.sta_zp(DRAWY)
    a.lda_imm(24)
    a.sta_zp(TMP2)
    a.lda_imm(12)
    a.sta_zp(TMP3)
    a.jsr("bg3_box")
    a.lda_imm(6)
    a.sta_zp(DRAWX)
    a.lda_imm(8)
    a.sta_zp(DRAWY)
    a.ldx_imm("str_party")
    a.stx_zp(STRPTR)
    a.lda_imm(1)
    a.sta_zp(STRPTR + 2)
    a.jsr("bg3_str")
    a.lda_imm(6)
    a.sta_zp(DRAWX)
    a.lda_imm(10)
    a.sta_zp(DRAWY)
    a.ldx_imm("str_pup")
    a.stx_zp(STRPTR)
    a.jsr("bg3_str")
    a.lda_imm(6)
    a.sta_zp(DRAWX)
    a.lda_imm(12)
    a.sta_zp(DRAWY)
    a.lda_zp(P_HP)
    a.jsr("print_num")
    a.rts()

    a.label("draw_shop")
    a.lda_imm(4)
    a.sta_zp(TMP0)
    a.lda_imm(4)
    a.sta_zp(DRAWX)
    a.lda_imm(8)
    a.sta_zp(DRAWY)
    a.lda_imm(24)
    a.sta_zp(TMP2)
    a.lda_imm(10)
    a.sta_zp(TMP3)
    a.jsr("bg3_box")
    a.lda_imm(6)
    a.sta_zp(DRAWX)
    a.lda_imm(10)
    a.sta_zp(DRAWY)
    a.ldx_imm("str_shop")
    a.stx_zp(STRPTR)
    a.lda_imm(1)
    a.sta_zp(STRPTR + 2)
    a.jsr("bg3_str")
    a.rts()

    a.label("draw_end")
    a.lda_imm(4)
    a.sta_zp(TMP0)
    a.lda_zp(FLAGS1)
    a.and_imm(1 << (F_SHIN - 8))
    a.beq("de_calder")
    a.lda_imm(3)
    a.sta_zp(DRAWX)
    a.lda_imm(9)
    a.sta_zp(DRAWY)
    a.ldx_imm("str_shin_end1")
    a.stx_zp(STRPTR)
    a.lda_imm(1)
    a.sta_zp(STRPTR + 2)
    a.jsr("bg3_str")
    a.lda_imm(3)
    a.sta_zp(DRAWX)
    a.lda_imm(11)
    a.sta_zp(DRAWY)
    a.ldx_imm("str_shin_end2")
    a.stx_zp(STRPTR)
    a.lda_imm(1)
    a.sta_zp(STRPTR + 2)
    a.jsr("bg3_str")
    a.rts()
    a.label("de_calder")
    a.lda_imm(6)
    a.sta_zp(DRAWX)
    a.lda_imm(10)
    a.sta_zp(DRAWY)
    a.ldx_imm("str_end")
    a.stx_zp(STRPTR)
    a.lda_imm(1)
    a.sta_zp(STRPTR + 2)
    a.jsr("bg3_str")
    a.rts()

    # script launchers: set SCR long and run_script
    def launch(name, lab):
        a.label(name)
        a.a8xy16()
        a.ldx_imm(lab)
        a.stx_zp(SCR)
        a.lda_imm(1)  # bank 1
        a.sta_zp(SCR + 2)
        a.jmp("run_script")

    launch("script_father", "sc_father")
    launch("script_father2", "sc_father2")
    launch("script_shelf", "sc_shelf")
    launch("script_bed", "sc_bed")
    launch("script_crate", "sc_crate")
    launch("script_doorlock", "sc_door")
    launch("script_footsteps", "sc_foot")
    launch("script_mason", "sc_mason")
    launch("script_mason2", "sc_mason2")
    launch("script_anne", "sc_anne")
    launch("script_wren", "sc_wren")
    launch("script_ivo", "sc_ivo")
    launch("script_nell", "sc_nell")
    launch("script_pike", "sc_pike")
    launch("script_calder", "sc_calder")
    launch("script_herb", "sc_herb")
    launch("script_gem", "sc_gem")
    launch("script_stump", "sc_stump")
    launch("script_cart", "sc_cart")
    launch("script_trees", "sc_trees")
    launch("script_grove", "sc_groveent")
    launch("script_sol", "sc_sol")
    launch("script_cath", "sc_cath")
    launch("script_cath_gone", "sc_cath_gone")
    launch("script_shin", "sc_shin")

    # tables in bank 0
    a.label("foe_hp")
    # 0 quillpup 34, 1 glimmoth 26, 2 fenwisp 24, 3 duskhorn 36, 4 needleroot 32, 5 crymare 30, 6 tortcask 42, 7 cathleen 38, 8 razorbat 30
    a.dw(34, 26, 24, 36, 32, 30, 42, 38, 30)
    a.label("foe_tile")
    a.db(192, 196, 200, 196, 200, 204, 196, 192, 196)
    a.db(0)
    a.label("foe_attr")
    prio = 0x20
    a.db(prio | (4 << 1), prio | (5 << 1), prio | (6 << 1), prio | (5 << 1), prio | (6 << 1), prio | (7 << 1), prio | (5 << 1), prio | (4 << 1), prio | (5 << 1))
    a.db(0)

    # map headers 8 bytes: w, h, tilemap lo,hi,bank, coll lo,hi,bank
    a.label("map_hdr")
    # filled after labels in bank 4+ exist — use known banks
    # map 0 house bank 4 $8000 tilemap, coll after 8192
    a.db(g.mw[0], g.mh[0])
    a.dw(0x8000)
    a.db(4)
    a.dw(0x8000 + 8192)
    a.db(4)
    a.db(g.mw[1], g.mh[1])
    a.dw(0x8000)
    a.db(5)
    a.dw(0x8000 + 8192)
    a.db(5)
    a.db(g.mw[2], g.mh[2])
    a.dw(0x8000)
    a.db(6)
    a.dw(0x8000 + 8192)
    a.db(6)
    a.db(g.mw[3], g.mh[3])
    a.dw(0x8000)
    a.db(7)
    a.dw(0x8000 + 8192)
    a.db(7)

    # who name pointer tables (bank 1)
    a.label("who_lo")
    # filled below after we know addresses - use placeholder and patch in pass2 via labels
    for i, name in enumerate(["nm_max", "nm_anne", "nm_mason", "nm_wren", "nm_ivo", "nm_nell", "nm_pike", "nm_bram", "nm_calder", "nm_cath", "nm_shin", "nm_none"]):
        a.dw(name)
    a.label("who_hi")
    # who_lo already 16-bit addresses; who_hi unused that way. draw_talk uses who_lo as pairs.
    # I used asl tax lda absx who_lo / who_hi as two tables of bytes. Fix draw_talk: I used two tables of 16-bit via asl.
    # who_lo is dw so asl tax is correct for 16-bit entries. who_hi is extra. draw_talk:
    # lda absx who_lo / lda absx who_hi  with asl tax means who_lo[x] is low byte of dw and who_lo[x+1] is high if we lda absx who_lo and lda absx who_lo+1
    # Let me fix: I already lda absx who_lo and who_hi as separate byte tables. I'll make byte tables.

    # Actually who_lo is dw so each entry 2 bytes, asl tax indexes words. Then lda absx who_lo is low, lda absx who_hi would be wrong.
    # draw_talk does:
    #   lda absx who_lo
    #   lda absx who_hi
    # with X = id*2. If who_lo is dw table, lda absx who_lo is LOW byte, we need HIGH from who_lo+1.
    # I'll add a note: change to lda_absx("who_lo"); sta STRPTR; lda_absx("who_lo"+1) — can't +1 as label easily.
    # I'll emit who_lo as interleaved already. Use:
    # Keep who_lo as dw. In draw_talk I used who_hi as second table of high bytes.
    pass

    # Pointer tables for foe names similarly
    a.label("foe_lo")
    for nm in ["fn_quill", "fn_glim", "fn_fen", "fn_dusk", "fn_need", "fn_cry", "fn_tort", "fn_cath", "fn_razor"]:
        a.dw(nm)

    # ---- BANK 1 strings + scripts ----
    a.org(1, 0x8000)
    a.label("str_crymon")
    a.asciiz("CRYMON")
    a.label("str_run")
    a.asciiz("MAX'S RUN")
    a.label("str_begin")
    a.asciiz("A / START  BEGIN")
    a.label("str_hud")
    a.asciiz("QUILLPUP")
    a.label("str_pup")
    a.asciiz("QUILLPUP")
    a.label("str_nip")
    a.asciiz("NIP")
    a.label("str_quill")
    a.asciiz("QUILLBURST")
    a.label("str_appear")
    a.asciiz("A CryMon appears!")
    a.label("str_win")
    a.asciiz("The CryMon is down.")
    a.label("str_lose")
    a.asciiz("Max blacked out.")
    a.label("str_bag")
    a.asciiz("BAG")
    a.label("str_salve")
    a.asciiz("MOSS SALVE")
    a.label("str_xtal")
    a.asciiz("CRYSTAL")
    a.label("str_party")
    a.asciiz("CRYMON")
    a.label("str_shop")
    a.asciiz("SALVE 8 MARKS  A BUY")
    a.label("str_end")
    a.asciiz("CRYTOWN HOLDS.")
    a.label("str_shin_end1")
    a.asciiz("Thank you for playing the")
    a.label("str_shin_end2")
    a.asciiz("demo of CryMon.")
    a.label("nm_max")
    a.asciiz("Max")
    a.label("nm_anne")
    a.asciiz("Anne")
    a.label("nm_mason")
    a.asciiz("Mason")
    a.label("nm_wren")
    a.asciiz("Wren")
    a.label("nm_ivo")
    a.asciiz("Ivo")
    a.label("nm_nell")
    a.asciiz("Nell")
    a.label("nm_pike")
    a.asciiz("Pike")
    a.label("nm_bram")
    a.asciiz("Bram")
    a.label("nm_calder")
    a.asciiz("Calder")
    a.label("nm_cath")
    a.asciiz("Cathleen")
    a.label("nm_shin")
    a.asciiz("Shinigami")
    a.label("nm_none")
    a.asciiz("")
    a.label("fn_quill")
    a.asciiz("Quillpup")
    a.label("fn_glim")
    a.asciiz("Glimmoth")
    a.label("fn_fen")
    a.asciiz("Fenwisp")
    a.label("fn_dusk")
    a.asciiz("Duskhorn")
    a.label("fn_need")
    a.asciiz("Needleroot")
    a.label("fn_cry")
    a.asciiz("CryMare")
    a.label("fn_tort")
    a.asciiz("Tortcask")
    a.label("fn_cath")
    a.asciiz("Cathleen")
    a.label("fn_razor")
    a.asciiz("Razorbat")

    def say(who, text):
        a.db(OP_SAY, who)
        a.asciiz(text)

    a.label("sc_father")
    say(0, "There's a war. CryTown is already bleeding.")
    say(0, "You're too sick to defend it from the soldiers.")
    say(0, "So I'm stealing your CryMon.")
    say(11, "Father does not wake.")
    a.db(OP_END)

    a.label("sc_father2")
    say(0, "I already took Quillpup. Sleep.")
    a.db(OP_END)

    a.label("sc_shelf")
    a.db(OP_IFN, F_SHELF, 12)
    say(0, "Quillpup. You're coming with me.")
    a.db(OP_GIVE_PUP)
    a.db(OP_FLAG, F_SHELF)
    a.db(OP_END)
    # if already: the IFN skip is approximate; also provide:
    a.label("sc_shelf2")
    say(0, "The shelf is empty.")
    a.db(OP_END)

    a.label("sc_bed")
    a.db(OP_HEAL)
    say(0, "Cuts close. Specials return.")
    a.db(OP_END)

    a.label("sc_crate")
    say(0, "Dust and a cracked bowl.")
    a.db(OP_END)

    a.label("sc_door")
    say(0, "Not yet. Father's CryMon is still on the shelf.")
    a.db(OP_END)

    a.label("sc_foot")
    say(11, "Footsteps on the path. Someone followed you out.")
    a.db(OP_END)

    a.label("sc_mason")
    say(2, "You walked out with that hound.")
    say(0, "He's mine.")
    say(2, "I already caught a CryMon. Fight me.")
    a.db(OP_MASON, 2)
    a.db(OP_BATTLE, 1, 1, 0)  # glimmoth, mason, not wild
    a.db(OP_END)

    a.label("sc_mason2")
    say(2, "Fine. Calder is still south.")
    a.db(OP_END)

    a.label("sc_anne")
    say(1, "Max. You actually fought.")
    say(1, "Take these. Five crystals.")
    say(0, "I won't waste them.")
    a.db(OP_GEM)
    a.db(OP_GEM)
    a.db(OP_GEM)
    a.db(OP_GEM)
    a.db(OP_GEM)
    a.db(OP_FLAG, F_ANNE)
    a.db(OP_ANNE, 3)
    a.db(OP_END)

    a.label("sc_wren")
    a.db(OP_IFN, F_WREN, 8)
    say(3, "Too young. Take the salve. Calder camps south.")
    a.db(OP_SALVE)
    a.db(OP_FLAG, F_WREN)
    a.db(OP_END)
    a.label("sc_wren2")
    a.db(OP_HEAL)
    say(3, "Cuts bound. Specials return.")
    a.db(OP_END)

    a.label("sc_ivo")
    say(4, "Camp took my CryMon. Chew this. Calder sits south.")
    a.db(OP_ROOT)
    a.db(OP_FLAG, F_IVO)
    a.db(OP_END)

    a.label("sc_nell")
    say(5, "Too young. Drink this anyway. Reeds hide a stone.")
    a.db(OP_SALVE)
    a.db(OP_FLAG, F_NELL)
    a.db(OP_END)

    a.label("sc_pike")
    say(6, "I dropped a stone in the east reeds. I'm not going back.")
    a.db(OP_FLAG, F_PIKE)
    a.db(OP_END)

    a.label("sc_calder")
    say(8, "The camp takes strays.")
    say(0, "I'm not stray.")
    a.db(OP_BATTLE, 8, 2, 0)  # razorbat, calder
    a.db(OP_END)

    a.label("sc_herb")
    say(0, "Bitterroot. It bites back.")
    a.db(OP_ROOT)
    a.db(OP_FLAG, F_HERB)
    a.db(OP_END)

    a.label("sc_gem")
    say(0, "A Capture Crystal.")
    a.db(OP_GEM)
    a.db(OP_FLAG, F_GEMF)
    a.db(OP_END)

    a.label("sc_stump")
    say(0, "A wrap stuffed in the stump.")
    a.db(OP_BAND)
    a.db(OP_FLAG, F_STUMP)
    a.db(OP_END)

    a.label("sc_cart")
    say(0, "A letter. They already knew her name.")
    a.db(OP_FLAG, F_CART)
    a.db(OP_END)

    a.label("sc_trees")
    say(0, "The trees close over the path.")
    a.db(OP_END)

    a.label("sc_groveent")
    say(0, "The grass dies out. Stone and hush.")
    a.db(OP_END)

    a.label("sc_sol")
    say(11, "A soldier sends a CryMon.")
    a.db(OP_BATTLE, 8, 5, 0)
    a.db(OP_END)

    a.label("sc_cath")
    say(9, "You walked the path. I am the path's answer.")
    say(0, "You're a CryMon.")
    say(9, "I am Cathleen. I fight as myself.")
    a.db(OP_BATTLE, 7, 4, 1)
    a.db(OP_END)

    a.label("sc_cath_gone")
    say(0, "She's gone. The gate stands open now.")
    a.db(OP_END)

    a.label("sc_shin")
    say(10, "Three names. Three graves. I keep them.")
    say(0, "You're in the way.")
    say(10, "CryMare. Come.")
    a.db(OP_BATTLE, 5, 3, 0)
    a.db(OP_END)

    # ---- BANK 2 graphics ----
    a.org(2, 0x8000)
    a.label("chr_bg")
    a.db(g.bg_chr)
    a.label("chr_font")
    a.db(g.font_chr)
    # palettes: 256 colors * 2 = 512 bytes
    a.label("pal_all")
    pals = [0] * 256
    # BG pal 0
    for i, c in enumerate(g.bg_pal):
        pals[i] = c
    # BG3 pal 4 -> CGRAM 16-19
    for i, c in enumerate(g.font_pal):
        pals[16 + i] = c
    # sprite pals 0-7 at CGRAM 128
    for pi in range(8):
        for ci, c in enumerate(g.spr_pal[pi]):
            pals[128 + pi * 16 + ci] = c
    pb = bytearray()
    for c in pals:
        pb.append(c & 0xFF)
        pb.append((c >> 8) & 0xFF)
    a.db(bytes(pb))

    a.org(3, 0x8000)
    a.label("chr_spr")
    a.db(g.spr_chr)

    for i, tm in enumerate(g.maps):
        a.org(4 + i, 0x8000)
        a.label(f"map{i}")
        a.db(tm)
        a.label(f"col{i}")
        a.db(g.coll[i])

    # header + vectors in bank 0
    a.org(0, 0xFFC0)
    title = "CRYMON               "[:21]
    a.ascii(title)
    a.db(0x20)  # LoROM
    a.db(0x00)  # ROM only
    a.db(0x08)  # 256KB
    a.db(0x00)  # SRAM
    a.db(0x01)  # USA
    a.db(0x33)  # extended header
    a.db(0x00)
    a.dw(0x0000)  # complement placeholder
    a.dw(0x0000)  # checksum placeholder

    # native vectors $FFE4
    a.org(0, 0xFFE4)
    a.dw("irq")  # COP
    a.dw("irq")  # BRK
    a.dw("irq")  # ABORT
    a.dw("nmi")  # NMI
    a.dw(0)  # unused
    a.dw("irq")  # IRQ
    # emu $FFF4
    a.org(0, 0xFFF4)
    a.dw("irq")
    a.dw("irq")
    a.dw("irq")
    a.dw("nmi")
    a.dw("reset")
    a.dw("irq")


def checksum(rom: bytearray):
    rom[0x7FDC] = 0
    rom[0x7FDD] = 0
    rom[0x7FDE] = 0
    rom[0x7FDF] = 0
    s = sum(rom) & 0xFFFF
    comp = s ^ 0xFFFF
    rom[0x7FDC] = comp & 0xFF
    rom[0x7FDD] = (comp >> 8) & 0xFF
    rom[0x7FDE] = s & 0xFF
    rom[0x7FDF] = (s >> 8) & 0xFF


def main():
    print("packing graphics...")
    g = Gfx()
    print(" sprites", len(g.names), "maps", g.mw, g.mh)
    a = Asm()
    print("assembling...")
    try:
        rom = a.assemble(lambda asm: build_game(asm, g))
    except AsmError as e:
        print("ASM ERROR", e)
        # dump labels
        for n, (b, p) in sorted(a.labels.items(), key=lambda kv: (kv[1][0], kv[1][1])):
            print(f"  {n:24s} {b:02X}:{p:04X}")
        raise
    checksum(rom)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_bytes(rom)
    print("wrote", OUT, "bytes", len(rom))
    print("reset", a.labels.get("reset"), "nmi", a.labels.get("nmi"))
    used0 = a.labels
    # show bank 0 last code-ish
    print("labels", len(a.labels))


if __name__ == "__main__":
    main()
