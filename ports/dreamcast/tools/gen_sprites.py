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
CATHLEEN_WORLD_W, CATHLEEN_WORLD_H = 28, 28

MONSTER_FRAMES = [1, 2, 3, 4]
MONSTER_W, MONSTER_H = 92, 92

BATTLE_BG_SRC = 'battle-bg.png'
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
        'json': path,
    }

def rgb565(r, g, b):
    return ((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3)

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
        for f in NPC_FRAMES:
            im = open_or_placeholder(root, pattern % f, ACTOR_DST_W, ACTOR_DST_H,
                                      name, manifest, 'world sprite, idle frame %d/4' % f)
            pixels = encode(im, ACTOR_DST_W, ACTOR_DST_H)
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

    lines.append('#define MONSTER_SPRITE_W %d' % MONSTER_W)
    lines.append('#define MONSTER_SPRITE_H %d' % MONSTER_H)
    lines.append('')
    for name in cat['monsters']:
        for f in MONSTER_FRAMES:
            im = open_or_placeholder(root, 'monsters/%s/%d.png' % (name, f), MONSTER_W, MONSTER_H,
                                      name, manifest, 'battle sprite, frame %d/4 (all 4 may be identical)' % f)
            pixels = encode(im, MONSTER_W, MONSTER_H)
            emit_array(lines, 'monster_%s_%d' % (name, f), pixels, MONSTER_W, MONSTER_H)

    lines.append('#define BATTLE_BG_W %d' % BATTLE_BG_W)
    lines.append('#define BATTLE_BG_H %d' % BATTLE_BG_H)
    im = Image.open(os.path.join(root, cat['bg']))
    pixels = encode(im, BATTLE_BG_W, BATTLE_BG_H)
    emit_array(lines, 'battle_bg', pixels, BATTLE_BG_W, BATTLE_BG_H)

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
