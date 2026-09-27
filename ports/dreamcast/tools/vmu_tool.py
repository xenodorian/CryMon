#!/usr/bin/env python3
"""Put a CryMon save blob into a VMU flash image, or take one out.

Used by the emulator tests (tools/dc_emu.py) with Flycast's per-game VMU
file (~/.local/share/flycast/<game id>_vmu_save_A1.bin, 128 KiB raw flash).
Writes exactly what save.c save_store() writes: a VMS file named
CRYMON_DAT, header + 32x32 icon + payload, CRC-16/CCITT over all of it.

  vmu_tool.py inject IMAGE BLOB    # BLOB = raw 332-byte save (content/save.json size)
  vmu_tool.py extract IMAGE OUT    # writes the payload save.c would read
"""
import sys
from pathlib import Path

BLOCK = 512
ROOT = 255
FAT_FREE, FAT_LAST = 0xFFFC, 0xFFFA
FILE_DATA = 0x33
NAME = b"CRYMON_DAT  "
HDR = 0x80
DATA_OFF = HDR + 512


def u16(b, o):
    return b[o] | (b[o + 1] << 8)


def put16(b, o, v):
    b[o] = v & 0xFF
    b[o + 1] = (v >> 8) & 0xFF


def crc16(data):
    rv = 0
    for c in data:
        tmp = ((rv >> 8) ^ c) & 0xFFFF
        tmp ^= tmp >> 4
        rv = ((rv << 8) ^ (tmp << 12) ^ (tmp << 5) ^ tmp) & 0xFFFF
    return rv


def layout(img):
    root = img[ROOT * BLOCK:(ROOT + 1) * BLOCK]
    if root[:16] != b"\x55" * 16:
        raise SystemExit("VMU image is not formatted")
    return u16(root, 0x46), u16(root, 0x4A), u16(root, 0x4C), u16(root, 0x50)


def entries(img, dir_loc, dir_size):
    for d in range(dir_size):
        blk = dir_loc - d
        for ent in range(BLOCK // 32):
            yield blk * BLOCK + ent * 32


def chain(img, fat_off, first):
    out, b = [], first
    while b < 256 and len(out) < 8:
        out.append(b)
        b = u16(img, fat_off + b * 2)
        if b in (FAT_LAST, FAT_FREE):
            break
    return out


def find(img):
    fat, dloc, dsize, _ = layout(img)
    for off in entries(img, dloc, dsize):
        if img[off] == FILE_DATA and bytes(img[off + 4:off + 16]) == NAME:
            return off, chain(img, fat * BLOCK, u16(img, off + 2))
    return None, []


def inject(img, blob):
    fat, dloc, dsize, user = layout(img)
    fat_off = fat * BLOCK
    size = DATA_OFF + len(blob)
    nblk = (size + BLOCK - 1) // BLOCK
    f = bytearray(nblk * BLOCK)
    f[0x00:0x10] = b"CRYMON".ljust(16, b" ")
    f[0x10:0x30] = b"CryMon save".ljust(32, b" ")
    f[0x30:0x40] = b"CRYMON".ljust(16, b"\0")
    f[0x40] = 1
    put16(f, 0x48, len(blob))
    f[DATA_OFF:DATA_OFF + len(blob)] = blob
    put16(f, 0x46, crc16(f[:size]))
    ent, old = find(img)
    for b in old:
        put16(img, fat_off + b * 2, FAT_FREE)
    if ent is None:
        ent = next(o for o in entries(img, dloc, dsize) if img[o] == 0)
    blks = [b for b in range(user - 1, -1, -1) if u16(img, fat_off + b * 2) == FAT_FREE][:nblk]
    if len(blks) < nblk:
        raise SystemExit("VMU full")
    for i, b in enumerate(blks):
        put16(img, fat_off + b * 2, blks[i + 1] if i + 1 < nblk else FAT_LAST)
        img[b * BLOCK:(b + 1) * BLOCK] = f[i * BLOCK:(i + 1) * BLOCK]
    e = bytearray(32)
    e[0] = FILE_DATA
    put16(e, 2, blks[0])
    e[4:16] = NAME
    e[0x18] = nblk
    img[ent:ent + 32] = e


def extract(img):
    ent, blks = find(img)
    if ent is None:
        raise SystemExit("no CRYMON_DAT on this VMU")
    f = b"".join(bytes(img[b * BLOCK:(b + 1) * BLOCK]) for b in blks)
    n = u16(f, 0x48)
    chk = bytearray(f[:DATA_OFF + n])
    saved = u16(chk, 0x46)
    chk[0x46] = chk[0x47] = 0
    if crc16(chk) != saved:
        raise SystemExit("CRC mismatch")
    return f[DATA_OFF:DATA_OFF + n]


if __name__ == "__main__":
    if len(sys.argv) != 4 or sys.argv[1] not in ("inject", "extract"):
        raise SystemExit(__doc__)
    image = Path(sys.argv[2])
    img = bytearray(image.read_bytes())
    if sys.argv[1] == "inject":
        inject(img, Path(sys.argv[3]).read_bytes())
        image.write_bytes(img)
    else:
        Path(sys.argv[3]).write_bytes(extract(img))
