#!/usr/bin/env python3
# Converts CryMon's sprite art into a C header of raw RGB565 pixel
# arrays for the bare-metal Dreamcast port's put_pixel-based
# framebuffer: the player (max, 4 walk frames per direction), the 4
# HOUSE furniture props, single standing-frame sprites for every
# world NPC (Wren, Mae, Ivo, Nell, Pike, Bram, Calder, Mason,
# soldiers, Shinigami, Cathleen), and single-frame battle art for
# every fightable species.
#
# Each sprite is downscaled with nearest-neighbor resampling to a
# fixed target size and color-keyed for transparency: any source
# pixel with alpha < 128 becomes the key color (0xF81F, magenta, one
# per sprite -- picked to not collide with that sprite's own opaque
# colors, checked below) and is skipped by the blitter at draw time.
# The source art has anti-aliased edges (alpha spans the full 0-255
# range, not just 0/255), so this hard cutoff is an approximation --
# edge pixels end up fully opaque or fully see-through, not blended.
# Good enough to verify sprites load and draw; true alpha blending
# isn't attempted here.
#
# Usage: gen_sprites.py <path-to-xenodorian/CryMon-checkout>
# Requires Pillow (pip install pillow).

import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', 'src', 'sprites.h')
KEY = 0xF81F  # magenta

# ----------------------------------------------------------------------
# Placeholder art: any entity tagged PLACEHOLDER_ART has no PNG in
# public/sprites yet. open_or_placeholder() synthesizes a checkerboard
# in memory (never writes a PNG). Dropping the real file in
# public/sprites/ at that relative path replaces it. Missing files are
# listed in ART_NEEDED.md at the end of the run.
# ----------------------------------------------------------------------

def _placeholder_font(size):
    try:
        return ImageFont.truetype(
            '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', size)
    except Exception:
        return ImageFont.load_default()


def make_placeholder(w, h, tag):
    im = Image.new('RGBA', (w, h), (0, 0, 0, 255))
    d = ImageDraw.Draw(im)
    cell = max(4, min(w, h) // 8)
    for y in range(0, h, cell):
        for x in range(0, w, cell):
            if ((x // cell) + (y // cell)) % 2 == 0:
                d.rectangle([x, y, x + cell - 1, y + cell - 1], fill=(255, 0, 255, 255))
    d.rectangle([0, 0, w - 1, h - 1], outline=(255, 255, 0, 255), width=2)
    font = _placeholder_font(max(8, min(w, h) // 6))
    text = tag.upper()
    try:
        bbox = d.textbbox((0, 0), text, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    except Exception:
        tw, th = d.textsize(text, font=font)
    tx, ty = max(0, (w - tw) // 2), max(0, (h - th) // 2)
    d.rectangle([tx - 2, ty - 2, tx + tw + 2, ty + th + 2], fill=(0, 0, 0, 255))
    d.text((tx, ty), text, fill=(255, 255, 0, 255), font=font)
    return im


def open_or_placeholder(root, relpath, w, h, tag, manifest, note=''):
    # Shared web pack only (public/sprites). No local art/ override.
    shared = os.path.join(root, relpath)
    if os.path.exists(shared):
        return Image.open(shared)
    # In-memory only. Do not write PNG caches outside public/sprites/.
    manifest.append((relpath, w, h, tag, note))
    return make_placeholder(w, h, tag)

PLAYER_DIRS = ['down', 'up', 'left', 'right']
PLAYER_FRAMES = [1, 2, 3, 4]
ACTOR_SRC_W, ACTOR_SRC_H = 48, 64
ACTOR_DST_W, ACTOR_DST_H = 24, 32

# Target sizes are Dreamcast presentation (20px tiles). Names come from
# content/sprites.json; only house furniture is blitted by main.c today.
PROP_SIZES = {
    'bed-father': (42, 40),
    'bed-empty':  (42, 40),
    'shelf':      (34, 31),
    'crate':      (24, 25),
}
PROP_C_NAME = {
    'bed-father': 'bed_father',
    'bed-empty':  'bed_empty',
}

NPC_FRAMES = [1, 2, 3, 4]

# Cathleen overworld: json extra key cathleen-ow. Fallback to battle frame.
CATHLEEN_WORLD_W, CATHLEEN_WORLD_H = ACTOR_DST_W, ACTOR_DST_H

MONSTER_FRAMES = [1, 2, 3, 4]
MONSTER_W, MONSTER_H = 92, 92

BATTLE_BG_SRC = 'battle-bg.png'
TILE_NAMES = (['grass-%d' % i for i in range(1, 5)] + ['dirt-%d' % i for i in range(1, 5)] +
              ['water-%d' % i for i in range(1, 5)] + ['dirt2-1', 'dirt2-2'] +
              ['%s-%d' % (k, i) for k in ('tallgrass', 'tree', 'tree-s', 'cliff') for i in (1, 2)] +
              ['%s-%s' % (k, d) for k in ('dirtedge', 'shore') for d in 'nesw'])
# Building and room tiles (tools/pixelforge/tiles_town.py), per theme.
TOWN_TILE_NAMES = (['%s-%s-%d' % (k, t, i) for t in ('wood', 'keep', 'crypt', 'palace') for k in ('floor',) for i in (1, 2)] +
                   ['%s-%s' % (k, t) for t in ('wood', 'keep', 'crypt', 'palace') for k in ('wall', 'wallf', 'door')] +
                   ['%s-%s-%d' % (k, t, i) for t in ('town', 'seph') for k in ('wallf', 'roof') for i in (1, 2)] +
                   ['%s-%s' % (k, t) for t in ('town', 'seph') for k in ('ridge', 'door')] +
                   ['bars', 'gate', 'flowers-1', 'flowers-2', 'crate', 'bed'])
# The Hollow's regraded ground (tools/pixelforge/tiles_hollow.py).
HOLLOW_TILE_NAMES = (['h-grass-%d' % i for i in range(1, 5)] + ['h-water-%d' % i for i in range(1, 5)] +
                     ['h-%s-%d' % (k, i) for k in ('tallgrass', 'tree', 'tree-s') for i in (1, 2)])
LIGHT_NAMES = ['%s-%d' % (k, i) for k in ('torch', 'lantern') for i in range(1, 5)]
BATTLE_BG_W, BATTLE_BG_H = 320, 240

ITEM_ICON_W, ITEM_ICON_H = 14, 14
PORTRAIT_BOX_W, PORTRAIT_BOX_H = 312, 176


def find_sprites_json(sprite_root):
    here = os.path.dirname(os.path.abspath(__file__))
    cands = [
        os.path.normpath(os.path.join(os.path.dirname(os.path.dirname(sprite_root)), 'content', 'sprites.json')),
        os.path.normpath(os.path.join(here, '..', '..', '..', 'content', 'sprites.json')),
        os.path.normpath(os.path.join(here, '..', '..', 'content', 'sprites.json')),
    ]
    for c in cands:
        if os.path.isfile(c):
            return c
    return None


def load_catalog(sprite_root):
    path = find_sprites_json(sprite_root)
    if not path:
        raise SystemExit('content/sprites.json not found (sprite catalog)')
    with open(path) as f:
        cat = json.load(f)
    walkers = dict(cat['walkers'])
    player_dir = walkers.pop('max', 'max')
    # Shinigami stands still in the grove: idle down frames, not a walker.
    shinigami_dir = walkers.pop('shinigami', 'shinigami')
    npcs = {n: 'npc/%s-%%d.png' % n for n in cat['npcs']}
    npcs['shinigami'] = '%s/down-%%d.png' % shinigami_dir
    props = []
    for key, rel in cat.get('props', {}).items():
        if key in PROP_SIZES:
            cname = PROP_C_NAME.get(key, key.replace('-', '_'))
            props.append((cname, rel, PROP_SIZES[key]))
    extra = {k: v for k, v in cat.get('extra', [])}
    cathleen_rel = extra.get('cathleen-ow', '/sprites/monsters/cathleen/1.png')
    if cathleen_rel.startswith('/sprites/'):
        cathleen_rel = cathleen_rel[len('/sprites/'):]
    bg = extra.get('bg', '/sprites/' + BATTLE_BG_SRC)
    if bg.startswith('/sprites/'):
        bg = bg[len('/sprites/'):]
    return {
        'player': player_dir,
        'walkers': walkers,
        'npcs': npcs,
        'monsters': list(cat['monsters']),
        'portraits': list(cat['portraits']),
        'items': list(cat['items']),
        'props': props,
        'cathleen': cathleen_rel,
        'bg': bg,
        'area_bgs': [(k, extra[k][len('/sprites/'):]) for k in sorted(set(cat.get('battleBgMap', {}).values()))
                     if extra.get(k, '').startswith('/sprites/')],
        'json': path,
    }

def rgb565(r, g, b):
    return ((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3)

# Battle frames are normalised here, in memory; the PNGs stay as drawn.
# Generated art carries loose, uneven padding, and a wide canvas stretched
# to 92x92 squashes the creature. Each species is padded to a square it
# fills (by area) by its evolution stage (three-stage lines 0.66/0.83/1.0, two-stage
# 0.76/1.0, others 0.92), standing on the bottom edge, so evolved forms
# read as upgrades. Species whose four frames are identical get a breath:
# frames 2-4 stretch the body up a row or two with the feet fixed. The web
# engine does the same in monsterFrames.ts; keep the two in step.
STAGE_FILL = {3: (0.66, 0.83, 1.0), 2: (0.76, 1.0), 1: (0.92,)}

def stage_fills(sprites_json):
    path = os.path.join(os.path.dirname(sprites_json), 'species.json')
    sp = json.load(open(path))
    sp = sp.get('species', sp)
    pre = {v['evolvesTo']: k for k, v in sp.items() if v.get('evolvesTo')}
    out = {}
    for k in sp:
        head = k
        while head in pre:
            head = pre[head]
        chain = [head]
        while sp[chain[-1]].get('evolvesTo'):
            chain.append(sp[chain[-1]]['evolvesTo'])
        out[k] = STAGE_FILL[min(3, len(chain))][min(chain.index(k), 2)]
    return out

def breathe(im, rows):
    w, h = im.size
    x0, top, x1, bot = im.getbbox()
    bh = bot - top
    out = Image.new('RGBA', (w, h))
    src, dst = im.load(), out.load()
    for y in range(bh + rows):
        sy = top + min(bh - 1, y * bh // (bh + rows))
        for x in range(x0, x1):
            dst[x, top - rows + y] = src[x, sy]
    return out

def battle_frames(frames, fill):
    frames = [f.convert('RGBA') for f in frames]
    still = all(f.tobytes() == frames[0].tobytes() for f in frames[1:])
    boxes = [f.getbbox() or (0, 0, f.width, f.height) for f in frames]
    x0 = min(b[0] for b in boxes); y0 = min(b[1] for b in boxes)
    x1 = max(b[2] for b in boxes); y1 = max(b[3] for b in boxes)
    w, h = x1 - x0, y1 - y0
    # by area, so a long low creature is not shrunk to a sliver by its width
    side = max(max(w, h) + 2, int((w * h) ** 0.5 / (fill * 0.85) + 0.999))
    foot = max(1, round(side * 0.02))
    side = max(side, h + foot + 6)
    ox, oy = (side - w) // 2, side - foot - h
    out = []
    for f in frames:
        c = Image.new('RGBA', (side, side))
        c.paste(f.crop((x0, y0, x1, y1)), (ox, oy))
        out.append(c)
    if still:
        r = max(1, round(h / 48))
        out = [out[0], breathe(out[0], r), breathe(out[0], 2 * r), breathe(out[0], r)]
    return out

def encode(im, dst_w, dst_h, resample=Image.NEAREST):
    im = im.convert('RGBA').resize((dst_w, dst_h), resample)
    px = im.load()
    out = []
    for y in range(dst_h):
        for x in range(dst_w):
            r, g, b, a = px[x, y]
            if a < 128:
                out.append(KEY)
            else:
                v = rgb565(r, g, b)
                if v == KEY:
                    v ^= 0x0001  # nudge off the key color, imperceptible
                out.append(v)
    return out

def emit_array(lines, name, pixels, w, h):
    lines.append('static const unsigned short %s[%d * %d] = {' % (name, w, h))
    for row in range(h):
        vals = pixels[row * w:(row + 1) * w]
        lines.append('    ' + ', '.join('0x%04X' % v for v in vals) + ',')
    lines.append('};')
    lines.append('')

def default_sprite_root():
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.normpath(os.path.join(here, '..', '..', '..', 'public', 'sprites'))



VMU_ICON_OUT = os.path.join(HERE, '..', 'src', 'vmu_icon.h')
# Icon on the memory-card save (BIOS file manager / VMU screen). 32x32,
# 16-colour ARGB4444, index 0 = transparent. public/sprites/ui/vmu-icon.png
# wins if someone draws one; otherwise the starter's battle art is used.
VMU_ICON_SOURCES = ['ui/vmu-icon.png', 'monsters/quillpup/1.png']


def write_vmu_icon(root):
    src = next((os.path.join(root, r) for r in VMU_ICON_SOURCES
                if os.path.exists(os.path.join(root, r))), None)
    im = Image.open(src).convert('RGBA')
    bbox = im.getbbox() or (0, 0, im.width, im.height)
    im = im.crop(bbox)
    side = max(im.width, im.height)
    sq = Image.new('RGBA', (side, side), (0, 0, 0, 0))
    sq.paste(im, ((side - im.width) // 2, (side - im.height) // 2))
    small = sq.resize((32, 32), Image.LANCZOS)
    alpha = [a >= 128 for (_, _, _, a) in small.getdata()]
    rgb = Image.new('RGB', (32, 32), (0, 0, 0))
    rgb.paste(small.convert('RGB'), (0, 0), small)
    q = rgb.quantize(colors=15, method=Image.MEDIANCUT)
    pal = q.getpalette()[:15 * 3]
    idx = list(q.getdata())
    argb = [0x0000]  # index 0: fully transparent
    for i in range(15):
        r, g, b = pal[i * 3:i * 3 + 3] if i * 3 + 2 < len(pal) else (0, 0, 0)
        argb.append(0xF000 | ((r >> 4) << 8) | ((g >> 4) << 4) | (b >> 4))
    pix = [(idx[i] + 1) if alpha[i] else 0 for i in range(32 * 32)]
    data = [(pix[i] << 4) | pix[i + 1] for i in range(0, 32 * 32, 2)]  # left pixel = high nibble
    out = ['/* Generated by ports/dreamcast/tools/gen_sprites.py from',
           ' * public/sprites/%s. Do not hand-edit. */' % os.path.relpath(src, root),
           '#ifndef CRYMON_VMU_ICON_H', '#define CRYMON_VMU_ICON_H',
           'static const unsigned short VMU_ICON_PAL[16] = { ' +
           ', '.join('0x%04X' % v for v in argb) + ' };',
           'static const unsigned char VMU_ICON[512] = {']
    for r in range(0, 512, 16):
        out.append('    ' + ', '.join('0x%02X' % v for v in data[r:r + 16]) + ',')
    out += ['};', '#endif', '']
    with open(VMU_ICON_OUT, 'w') as f:
        f.write('\n'.join(out))
    print('wrote', os.path.normpath(VMU_ICON_OUT))


def main():
    if len(sys.argv) == 2:
        arg = sys.argv[1]
        root = os.path.join(arg, 'public', 'sprites') if os.path.isdir(os.path.join(arg, 'public', 'sprites')) else arg
    elif len(sys.argv) == 1:
        root = default_sprite_root()
    else:
        sys.exit('usage: gen_sprites.py [path-to-public/sprites]')
    if not os.path.isdir(root):
        sys.exit('sprite root not found: %s (expected public/sprites in this repo)' % root)
    cat = load_catalog(root)
    manifest = []  # (relpath, w, h, tag, note) for every placeholder actually used this run

    lines = []
    lines.append('/* Generated by ports/dreamcast/tools/gen_sprites.py from')
    lines.append(' * content/sprites.json + public/sprites. Do not hand-edit. */')
    lines.append('#if defined(__GNUC__)')
    lines.append('#pragma GCC diagnostic ignored "-Wunused-const-variable"')
    lines.append('#endif')
    lines.append('')
    lines.append('#define SPRITE_KEY 0x%04X' % KEY)
    lines.append('')

    lines.append('#define MAX_SPRITE_W %d' % ACTOR_DST_W)
    lines.append('#define MAX_SPRITE_H %d' % ACTOR_DST_H)
    lines.append('')
    for d in PLAYER_DIRS:
        for f in PLAYER_FRAMES:
            im = Image.open(os.path.join(root, cat['player'], '%s-%d.png' % (d, f)))
            assert im.size == (ACTOR_SRC_W, ACTOR_SRC_H), (d, f, im.size)
            pixels = encode(im, ACTOR_DST_W, ACTOR_DST_H)
            emit_array(lines, 'max_%s_%d' % (d, f), pixels, ACTOR_DST_W, ACTOR_DST_H)

    for name, relpath, (w, h) in cat['props']:
        im = Image.open(os.path.join(root, relpath))
        pixels = encode(im, w, h)
        lines.append('#define PROP_%s_W %d' % (name.upper(), w))
        lines.append('#define PROP_%s_H %d' % (name.upper(), h))
        emit_array(lines, 'prop_%s' % name, pixels, w, h)

    lines.append('#define NPC_SPRITE_W %d' % ACTOR_DST_W)
    lines.append('#define NPC_SPRITE_H %d' % ACTOR_DST_H)
    lines.append('')
    for name, pattern in cat['npcs'].items():
        first = None
        for f in NPC_FRAMES:
            # Still sprites (sprites.json stillFrames) ship only frame 1, and
            # a frame identical to frame 1 is not stored twice: frames 2-4
            # alias frame 1's array so main.c's 4-frame tables still work.
            if f > 1 and not os.path.exists(os.path.join(root, pattern % f)):
                lines.append('#define npc_%s_%d npc_%s_1' % (name, f, name))
                continue
            im = open_or_placeholder(root, pattern % f, ACTOR_DST_W, ACTOR_DST_H,
                                      name, manifest, 'world sprite, idle frame %d/4' % f)
            pixels = encode(im, ACTOR_DST_W, ACTOR_DST_H)
            if f == 1:
                first = pixels
            elif pixels == first:
                lines.append('#define npc_%s_%d npc_%s_1' % (name, f, name))
                continue
            emit_array(lines, 'npc_%s_%d' % (name, f), pixels, ACTOR_DST_W, ACTOR_DST_H)

    for name, reldir in cat['walkers'].items():
        for d in PLAYER_DIRS:
            for f in PLAYER_FRAMES:
                im = Image.open(os.path.join(root, reldir, '%s-%d.png' % (d, f)))
                assert im.size == (ACTOR_SRC_W, ACTOR_SRC_H), (name, d, f, im.size)
                pixels = encode(im, ACTOR_DST_W, ACTOR_DST_H)
                emit_array(lines, 'npc_%s_%s_%d' % (name, d, f), pixels, ACTOR_DST_W, ACTOR_DST_H)

    lines.append('#define CATHLEEN_WORLD_W %d' % CATHLEEN_WORLD_W)
    lines.append('#define CATHLEEN_WORLD_H %d' % CATHLEEN_WORLD_H)
    im = Image.open(os.path.join(root, cat['cathleen']))
    pixels = encode(im, CATHLEEN_WORLD_W, CATHLEEN_WORLD_H)
    emit_array(lines, 'npc_cathleen', pixels, CATHLEEN_WORLD_W, CATHLEEN_WORLD_H)

    # Monster battle frames. STREAM=1 (default): written to
    # ports/dreamcast/disc/MONSTERS.BIN, one record per species in
    # sprites.json order (= species order), 4 frames of little-endian RGB565
    # (1 frame for a species whose frames are all identical, e.g. listed in
    # sprites.json stillFrames with only 1.png), padded to whole 2048-byte
    # sectors so main.c reads a species with a single disc command.
    # MONSTER_REC_OFF / MONSTER_REC_SECS / MONSTER_NFRAMES locate each record. STREAM=0: embedded as C arrays like before, for a
    # build that never touches the disc. Either way a 16x16 icon per species
    # stays resident (party menu, and the battle fallback if a read fails);
    # it is sampled exactly like blit_sprite_fit(frame1, 92, 92, .., 16, 16).
    stream = os.environ.get('CRYMON_STREAM', '1') != '0'
    fills = stage_fills(cat['json'])
    frame_px = MONSTER_W * MONSTER_H
    rec_bytes = len(MONSTER_FRAMES) * frame_px * 2
    rec_sectors = (rec_bytes + 2047) // 2048
    lines.append('#define MONSTER_SPRITE_W %d' % MONSTER_W)
    lines.append('#define MONSTER_SPRITE_H %d' % MONSTER_H)
    lines.append('#define MONSTER_ICON_W 16')
    lines.append('#define MONSTER_ICON_H 16')
    lines.append('#define MONSTER_STREAM %d' % (1 if stream else 0))
    lines.append('#define MONSTER_REC_SECTORS %d' % rec_sectors)
    lines.append('#define MONSTER_FILE "MONSTERS.BIN"')
    lines.append('')
    blob = bytearray()
    rec_off, rec_secs, nframes = [], [], []
    for name in cat['monsters']:
        ims = []
        for f in MONSTER_FRAMES:
            rel = 'monsters/%s/%d.png' % (name, f)
            if f > 1 and not os.path.exists(os.path.join(root, rel)):
                ims.append(ims[0])  # still sprite: frame 1 stands in
                continue
            ims.append(open_or_placeholder(root, rel, MONSTER_W, MONSTER_H,
                                           name, manifest, 'battle sprite, frame %d/4' % f))
        if name in fills:
            ims = battle_frames(ims, fills[name])  # still sprites come back breathing
        frames = [encode(im, MONSTER_W, MONSTER_H) for im in ims]
        if all(px == frames[0] for px in frames[1:]):
            frames = frames[:1]
        nframes.append(len(frames))
        icon = [frames[0][(y * MONSTER_H // 16) * MONSTER_W + (x * MONSTER_W // 16)]
                for y in range(16) for x in range(16)]
        emit_array(lines, 'monster_icon_%s' % name, icon, 16, 16)
        if stream:
            rec = bytearray()
            for px in frames:
                for v in px:
                    rec += bytes((v & 0xFF, v >> 8))
            secs = (len(rec) + 2047) // 2048
            rec += bytes(secs * 2048 - len(rec))
            rec_off.append(len(blob) // 2048)
            rec_secs.append(secs)
            blob += rec
        else:
            for f, px in zip(MONSTER_FRAMES, frames):
                emit_array(lines, 'monster_%s_%d' % (name, f), px, MONSTER_W, MONSTER_H)
            for f in MONSTER_FRAMES[len(frames):]:
                lines.append('#define monster_%s_%d monster_%s_1' % (name, f, name))
    lines.append('/* Index = species index (sprites.json monsters order). */')
    lines.append('static const unsigned short *const MONSTER_ICONS[] = {')
    for name in cat['monsters']:
        lines.append('    monster_icon_%s,' % name)
    lines.append('};')
    lines.append('/* Frames stored per species: 1 = still (every frame is frame 1). */')
    lines.append('static const unsigned char MONSTER_NFRAMES[] = { ' + ', '.join(map(str, nframes)) + ' };')
    if stream:
        lines.append('/* MONSTERS.BIN record start sector and length per species. */')
        lines.append('static const unsigned short MONSTER_REC_OFF[] = { ' + ', '.join(map(str, rec_off)) + ' };')
        lines.append('static const unsigned char MONSTER_REC_SECS[] = { ' + ', '.join(map(str, rec_secs)) + ' };')
    if stream:
        disc_dir = os.path.join(HERE, '..', 'disc')
        os.makedirs(disc_dir, exist_ok=True)
        with open(os.path.join(disc_dir, 'MONSTERS.BIN'), 'wb') as f:
            f.write(blob)
        print('wrote', os.path.normpath(os.path.join(disc_dir, 'MONSTERS.BIN')), len(blob), 'bytes')
    else:
        lines.append('static const unsigned short *const MONSTER_SPRITES[][4] = {')
        for name in cat['monsters']:
            lines.append('    { ' + ', '.join('monster_%s_%d' % (name, f) for f in MONSTER_FRAMES) + ' },')
        lines.append('};')
    lines.append('')

    lines.append('#define BATTLE_BG_W %d' % BATTLE_BG_W)
    lines.append('#define BATTLE_BG_H %d' % BATTLE_BG_H)
    im = Image.open(os.path.join(root, cat['bg']))
    pixels = encode(im, BATTLE_BG_W, BATTLE_BG_H)
    emit_array(lines, 'battle_bg', pixels, BATTLE_BG_W, BATTLE_BG_H)

    # Brass nine-slice UI frame (tools/pixelforge/uiframe.py): 16x16, 6px
    # corners. main.c's draw_ui_frame() uses it when HAVE_UI_FRAME is set.
    frame_path = os.path.join(root, 'ui', 'frame.png')
    if os.path.isfile(frame_path):
        lines.append('#define HAVE_UI_FRAME 1')
        emit_array(lines, 'ui_frame', encode(Image.open(frame_path), 16, 16), 16, 16)

    # Title and ending backdrops (tools/pixelforge/screens.py), half size,
    # blitted 2x by draw_press_start() / draw_ending().
    scr = [(n, os.path.join(root, 'screens', n + '.png')) for n in ('title', 'ending')]
    if all(os.path.isfile(pth) for _, pth in scr):
        lines.append('#define HAVE_SCREEN_ART 1')
        for n, pth in scr:
            emit_array(lines, 'screen_' + n, encode(Image.open(pth), BATTLE_BG_W // 2, BATTLE_BG_H // 2, Image.BOX),
                       BATTLE_BG_W // 2, BATTLE_BG_H // 2)

    # Per-area battle backdrops (tools/pixelforge/battlebg.py), stored at half
    # size and blitted 2x so nine of them cost what two full ones would.
    # Index k+1 matches MAP_BATTLE_BG in content_maps.inc (sorted names from
    # sprites.json battleBgMap); 0 means battle_bg above.
    if cat['area_bgs']:
        lines.append('#define HAVE_AREA_BG 1')
        lines.append('#define AREA_BG_W %d' % (BATTLE_BG_W // 2))
        lines.append('#define AREA_BG_H %d' % (BATTLE_BG_H // 2))
        names = []
        for key, rel in cat['area_bgs']:
            cname = 'area_' + key.replace('-', '_')
            im = Image.open(os.path.join(root, rel))
            emit_array(lines, cname, encode(im, BATTLE_BG_W // 2, BATTLE_BG_H // 2, Image.BOX), BATTLE_BG_W // 2,
                       BATTLE_BG_H // 2)
            names.append(cname)
        lines.append('static const unsigned short *const AREA_BG[%d] = { %s };' % (len(names), ', '.join(names)))
        lines.append('')

    # Painted overworld ground tiles (tools/pixelforge/tiles.py), scaled from
    # 32px to the port's 20px TILE. main.c's draw_tile_art() uses them when
    # HAVE_TILE_ART is defined and keeps its flat tiles otherwise.
    tile_dir = os.path.join(root, 'tiles')
    if all(os.path.exists(os.path.join(tile_dir, n + '.png')) for n in TILE_NAMES):
        lines.append('#define HAVE_TILE_ART 1')
        lines.append('#define TILE_ART_PX 20')
        for n in TILE_NAMES:
            im = Image.open(os.path.join(tile_dir, n + '.png'))
            edge = 'edge' in n or 'shore' in n
            pixels = encode(im, 20, 20, Image.BOX if edge else Image.LANCZOS)
            emit_array(lines, 'tile_' + n.replace('-', '_'), pixels, 20, 20)
    # Building and room tiles plus the wall torch and lantern frames (fx/,
    # 16px -> 10px). main.c's draw_building_art() uses them per map theme.
    fx_dir = os.path.join(root, 'fx')
    if (all(os.path.exists(os.path.join(tile_dir, n + '.png')) for n in TOWN_TILE_NAMES) and
            all(os.path.exists(os.path.join(fx_dir, n + '.png')) for n in LIGHT_NAMES)):
        lines.append('#define HAVE_TOWN_TILES 1')
        lines.append('#define LIGHT_PX 10')
        for n in TOWN_TILE_NAMES:
            im = Image.open(os.path.join(tile_dir, n + '.png'))
            over = n in ('crate', 'bed')
            emit_array(lines, 'tile_' + n.replace('-', '_'), encode(im, 20, 20, Image.BOX if over else Image.LANCZOS), 20, 20)
        for n in LIGHT_NAMES:
            im = Image.open(os.path.join(fx_dir, n + '.png'))
            emit_array(lines, 'fx_' + n.replace('-', '_'), encode(im, 10, 10, Image.BOX), 10, 10)
    if all(os.path.exists(os.path.join(tile_dir, n + '.png')) for n in HOLLOW_TILE_NAMES):
        lines.append('#define HAVE_HOLLOW_TILES 1')
        for n in HOLLOW_TILE_NAMES:
            im = Image.open(os.path.join(tile_dir, n + '.png'))
            emit_array(lines, 'tile_' + n.replace('-', '_'), encode(im, 20, 20, Image.LANCZOS), 20, 20)

    lines.append('#define ITEM_ICON_W %d' % ITEM_ICON_W)
    lines.append('#define ITEM_ICON_H %d' % ITEM_ICON_H)
    lines.append('')
    for name in cat['items']:
        im = open_or_placeholder(root, 'items/%s.png' % name, ITEM_ICON_W, ITEM_ICON_H,
                                  name, manifest, 'bag/shop/battle item icon')
        pixels = encode(im, ITEM_ICON_W, ITEM_ICON_H)
        emit_array(lines, 'icon_%s' % name, pixels, ITEM_ICON_W, ITEM_ICON_H)

    lines.append('#define PORTRAIT_BOX_W %d' % PORTRAIT_BOX_W)
    lines.append('#define PORTRAIT_BOX_H %d' % PORTRAIT_BOX_H)
    lines.append('')
    for name in cat['portraits']:
        im = open_or_placeholder(root, 'portraits/%s.png' % name, PORTRAIT_BOX_W, PORTRAIT_BOX_H,
                                  name, manifest, 'dialogue-box portrait')
        sw, sh = im.size
        scale = min(PORTRAIT_BOX_W / sw, PORTRAIT_BOX_H / sh)
        dw, dh = max(1, round(sw * scale)), max(1, round(sh * scale))
        pixels = encode(im, dw, dh, resample=Image.LANCZOS)
        lines.append('#define PORT_%s_W %d' % (name.upper(), dw))
        lines.append('#define PORT_%s_H %d' % (name.upper(), dh))
        emit_array(lines, 'port_%s' % name, pixels, dw, dh)

    with open(OUT, 'w') as f:
        f.write('\n'.join(lines) + '\n')
    print('wrote', OUT)

    write_vmu_icon(root)

    manifest_path = os.path.join(HERE, '..', 'ART_NEEDED.md')
    if manifest:
        md = []
        md.append('# Art needed\n')
        md.append(
            'Auto-generated by `tools/gen_sprites.py` -- every row below is a real\n'
            'gap: no source art exists for it in `xenodorian/CryMon`, so the game is\n'
            'currently running a synthesized placeholder (a magenta/black checker\n'
            'tile with the entity\'s tag stamped on it, cached under\n'
            '`tools/placeholder_sprites/<path>` at the exact path below). Regenerate\n'
            'this file any time by re-running `gen_sprites.py` -- it reflects\n'
            'whatever is actually still missing, never hand-edited.\n'
        )
        md.append(
            '## Instructions for generating replacement art\n\n'
            '1. Draw/generate a PNG matching the **pixel size** given for each row\n'
            '   below (or any larger size with the same aspect ratio -- everything\n'
            '   is downscaled at build time, never upscaled).\n'
            '2. Style: match the existing CryMon art in `public/sprites/` -- simple,\n'
            '   readable silhouettes, flat-ish shading, small enough to read at 24-92px\n'
            '   on screen. Battle sprites (`monsters/<name>/`) are the most detailed;\n'
            '   world sprites (`npc/<name>-N.png`) and item icons are simpler.\n'
            '3. Background: fully transparent (alpha channel), not a solid color --\n'
            '   anything under alpha 128 is treated as see-through at build time.\n'
            '4. Save the PNG at **exactly** the "expected path" column below, rooted\n'
            '   at `public/sprites/` inside a checkout of `xenodorian/CryMon` (the\n'
            '   same repo this port\'s art already comes from). That\'s the only path\n'
            '   `tools/gen_sprites.py <path-to-CryMon-checkout>` ever looks at --\n'
            '   dropping a real file there automatically replaces the placeholder\n'
            '   next time sprites are regenerated, no code changes needed.\n'
            '5. Monsters and NPCs need one file per frame (1-4); it\'s fine for all 4\n'
            '   to be pixel-identical at first (no animation) -- a real idle cycle can\n'
            '   follow later.\n'
        )
        md.append('## Missing (%d files)\n' % len(manifest))
        md.append('| Expected path (under `public/sprites/`) | Size | Entity | Note |')
        md.append('|---|---|---|---|')
        for relpath, w, h, tag, note in manifest:
            md.append('| `%s` | %dx%d | %s | %s |' % (relpath, w, h, tag, note))
        md.append('')
        with open(manifest_path, 'w') as f:
            f.write('\n'.join(md) + '\n')
        print('wrote %s (%d missing files)' % (manifest_path, len(manifest)))
    elif os.path.exists(manifest_path):
        os.remove(manifest_path)
        print('removed %s (nothing missing)' % manifest_path)

if __name__ == '__main__':
    main()
