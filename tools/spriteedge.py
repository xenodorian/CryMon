#!/usr/bin/env python3
"""spriteedge: find the drawn outline of a sprite in pixel-art images, exactly, with no guessing.

Give this file to any AI or person who needs to cut a character out of its background or recolour
its outline. It needs only Python 3.8+, Pillow and numpy (scipy is used if it is installed, never required).

WHAT IT DOES
  1. Decides what is OUTSIDE the character: the flat background and, if you name it, a flat drop shadow.
     Outside colours are matched exactly (or within --tolerance for softer art).
  2. The sprite is everything else. Its BOUNDARY is the sprite pixels that touch the outside.
  3. The BORDER is the boundary pixels that are ink (dark by default, or the ink colours you give).
     Boundary pixels that are not ink (a pale drool string, a tusk tip with no black edge) are reported as
     SKIPPED and are never recoloured. Dark lines INSIDE the sprite are never touched, because they do not
     touch the outside.
  4. It writes the original frame, the frame with the border recoloured, a transparent cutout, mask images
     and a JSON report with counts and warnings.

WHY IT WORKS (and when it does not)
  It works on images whose colours are exact: GIF, PNG, sprite sheets, anything drawn with a palette.
  It does NOT work by brightness thresholds on the whole picture, which cannot tell a shadow from a dark
  belly. It works on JPEG, blurred or anti-aliased art only in --tolerance mode, which is less reliable.
  A shadow that is a soft gradient cannot be named as one flat colour, so it cannot be separated.
  Measured on a real sprite frame (a 450 x 450 boar with 2,575 true border pixels) re-saved as JPEG and run with
  --tolerance 14 --flood --ink-lum 60: JPEG quality 95 finds 91% of the border with no extra pixels, quality 88 finds
  87% with 26 extra, quality 75 finds 71% with 141 extra. Treat JPEG results as approximate and look at them.

QUICK START
  python3 spriteedge.py boar.gif --suggest                 # list the colours that look like backdrop and shadow
  python3 spriteedge.py boar.gif --outside 99,99,99 49,49,49
        # frame 0, backdrop gray and shadow gray, border drawn red -> boar_edge/boar_f0_border.png ...
  python3 spriteedge.py boar.gif --outside 99,99,99 49,49,49 --frames all   # every frame of an animation
  python3 spriteedge.py sprite.png --outside 87,114,119 --ink-lum 60 --thickness 2
  python3 spriteedge.py --self-test                         # checks the tool on a built-in test picture

OPTIONS (all optional except the input)
  --outside C [C ...]   colours that are not the sprite, as R,G,B or #rrggbb. Without it the four corner
                        colours are used (backdrop only; a shadow must be named or it counts as sprite).
  --suggest             print likely backdrop and shadow colours and exit
  --tolerance N         match outside colours within N (RGB distance); also turns on --flood
  --flood               only outside regions that touch the image edge count (use with --tolerance)
  --ink-lum N           border pixels must have luminance below N (default 45, scale 0 to 255)
  --ink-color C [C ..]  instead of luminance, border pixels must be these exact colours
  --thickness N         border layers to take from the outside in (default 1)
  --connectivity 4|8    neighbours that count as touching the outside (default 4: a 1 px staircase)
  --border-color C      recolour colour (default 255,0,0)
  --show-skipped C      also paint skipped boundary pixels in this colour (default: not painted)
  --frame N | --frames all   which frame of an animation (default frame 0)
  --scale N             nearest-neighbour enlarge the written pictures (default 1)
  --outdir DIR          where to write (default <input name>_edge/ next to the input)
  --no-cutout           skip the transparent cutout

PYTHON USE
  import spriteedge as se
  frames = se.load_frames("boar.gif")                  # [(index, RGBA uint8 array), ...]
  r = se.find_border(frames[0][1], outside=[(99, 99, 99), (49, 49, 49)])
  r.border      # bool mask: the drawn outline        r.skipped   # boundary pixels that are not ink
  r.sprite      # bool mask: the character            r.outside   # bool mask: backdrop and shadow
  r.report      # dict: counts, enclosed pockets, warnings
  se.recolor(frames[0][1], r.border, (255, 0, 0))     # RGBA array with the border painted

READING THE REPORT
  border_px            pixels that were recoloured
  skipped_px           boundary pixels left alone because they are not ink (check them: a large number means
                       the art has no black edge there, or --ink-lum is too low)
  outside_regions      each outside region: size, whether it touches the image edge, colours; regions that do
                       not touch the edge are pockets (a tail curl, the gap between legs): real background
  warnings             things to look at, such as an outside colour found enclosed inside the sprite
"""
import argparse
import json
import os
import sys
from collections import Counter, deque

import numpy as np
from PIL import Image, ImageSequence

try:                                                     # optional: much faster region labelling on big images
    from scipy import ndimage as _ndi
except Exception:                                        # pragma: no cover
    _ndi = None

__all__ = ['load_frames', 'find_border', 'suggest_outside', 'recolor', 'cutout', 'EdgeResult', 'parse_color', 'self_test']


# ------------------------------------------------------------------ small helpers
def parse_color(s):
    """'R,G,B' or '#rrggbb' -> (r, g, b)."""
    if isinstance(s, (tuple, list)):
        return tuple(int(v) for v in s[:3])
    s = s.strip()
    if s.startswith('#') and len(s) == 7:
        return tuple(int(s[i:i + 2], 16) for i in (1, 3, 5))
    parts = [int(v) for v in s.replace(' ', '').split(',')]
    if len(parts) != 3 or any(not 0 <= v <= 255 for v in parts):
        raise ValueError(f'not a colour: {s!r} (use R,G,B or #rrggbb)')
    return tuple(parts)


def load_frames(path, frame=None):
    """[(index, RGBA uint8 HxWx4)] for every frame of an image or animation (or just `frame`)."""
    im = Image.open(path)
    out = []
    for i, f in enumerate(ImageSequence.Iterator(im)):
        if frame is None or i == frame:
            out.append((i, np.asarray(f.convert('RGBA')).copy()))
        if frame is not None and i >= frame:
            break
    if not out:
        raise ValueError(f'{path}: no frame {frame}')
    return out


def luminance(rgb):
    rgb = rgb.astype(np.float64)
    return 0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2]


def touches(mask, connectivity=4, edge=False):
    """Pixels that have a neighbour inside `mask`. `edge` is what lies beyond the image border."""
    p = np.pad(mask, 1, constant_values=edge)
    n = p[:-2, 1:-1] | p[2:, 1:-1] | p[1:-1, :-2] | p[1:-1, 2:]
    if connectivity == 8:
        n = n | p[:-2, :-2] | p[:-2, 2:] | p[2:, :-2] | p[2:, 2:]
    return n


def label(mask, connectivity=4):
    """(labels, count) of the connected regions of a boolean mask; labels start at 1."""
    if _ndi is not None:
        st = np.ones((3, 3), int) if connectivity == 8 else None
        return _ndi.label(mask, structure=st)
    h, w = mask.shape
    lab = np.zeros((h, w), np.int32)
    n = 0
    steps = [(-1, 0), (1, 0), (0, -1), (0, 1)] + ([(-1, -1), (-1, 1), (1, -1), (1, 1)] if connectivity == 8 else [])
    for y, x in zip(*np.nonzero(mask)):
        if lab[y, x]:
            continue
        n += 1
        lab[y, x] = n
        q = deque([(y, x)])
        while q:
            cy, cx = q.popleft()
            for dy, dx in steps:
                ny, nx = cy + dy, cx + dx
                if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and not lab[ny, nx]:
                    lab[ny, nx] = n
                    q.append((ny, nx))
    return lab, n


def _bbox(mask):
    ys, xs = np.nonzero(mask)
    return [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())]


def _hex(c):
    return '#%02x%02x%02x' % tuple(int(v) for v in c)


# ------------------------------------------------------------------ finding the outside candidates
def suggest_outside(rgba, min_pixels=200, top=12):
    """Colours that probably are not the sprite. Returns a list of dicts, best first:
    kind 'backdrop' (a flat colour whose largest region touches the image edge) or 'shadow-like' (a flat, neutral
    gray region, not touching the edge, that sits against a backdrop region). These are suggestions: check them."""
    rgb = rgba[..., :3]
    h, w, _ = rgb.shape
    flat = rgb.reshape(-1, 3)
    cols, counts = np.unique(flat, axis=0, return_counts=True)
    order = np.argsort(-counts)
    cand = []
    backdrops = []
    for i in order[:60]:
        if counts[i] < min_pixels:
            break
        c = tuple(int(v) for v in cols[i])
        m = (rgb == np.array(c)).all(2)
        lab, n = label(m, 4)
        if n == 0:
            continue
        sizes = np.bincount(lab.ravel())[1:]
        k = int(sizes.argmax()) + 1
        big = lab == k
        edge = bool(big[0].any() or big[-1].any() or big[:, 0].any() or big[:, -1].any())
        rec = dict(color=c, hex=_hex(c), pixels=int(counts[i]), largest_region=int(sizes.max()), regions=int(n),
                   touches_image_edge=edge, neutral_gray=(c[0] == c[1] == c[2]), bbox=_bbox(big))
        cand.append((rec, big))
        if edge and sizes.max() >= 0.05 * h * w:
            backdrops.append(big)
    out = []
    back_union = np.zeros((h, w), bool)
    for b in backdrops:
        back_union |= b
    near_back = touches(back_union, 4)
    for rec, big in cand:
        if rec['touches_image_edge'] and rec['largest_region'] >= 0.05 * h * w:
            rec['kind'] = 'backdrop'
        elif rec['neutral_gray'] and (big & near_back).any():
            rec['kind'] = 'shadow-like'
        else:
            continue
        out.append(rec)
    out.sort(key=lambda r: (r['kind'] != 'backdrop', -r['pixels']))
    return out[:top]


# ------------------------------------------------------------------ the core
class EdgeResult:
    """Boolean masks (HxW) and a report for one frame."""
    def __init__(self, **kw):
        self.__dict__.update(kw)


def find_border(rgba, outside=None, tolerance=0, flood=None, ink_lum=45, ink_colors=None, ink_tolerance=0,
                thickness=1, connectivity=4, alpha_cut=128):
    """Find the sprite's drawn outline in one RGBA (or RGB) uint8 array.

    outside     list of (r, g, b) that are not the sprite; default: the four corner colours
    tolerance   0 = exact match; >0 = within this RGB distance (turns flood on unless flood=False)
    flood       True: only outside regions that touch the image edge count
    ink_lum     border pixels must be darker than this luminance (ignored if ink_colors is given)
    ink_colors  list of (r, g, b): border pixels must be one of these colours (within ink_tolerance)
    thickness   number of layers to take from the outside in
    connectivity 4 or 8: which neighbours count as touching the outside
    Pixels with alpha below alpha_cut always count as outside.
    Returns an EdgeResult with masks outside, sprite, boundary, border, skipped, and report (a dict)."""
    a = np.asarray(rgba)
    if a.ndim != 3 or a.shape[2] not in (3, 4):
        raise ValueError('expected an HxWx3 or HxWx4 array')
    rgb = a[..., :3].astype(np.int32)
    h, w, _ = rgb.shape
    transparent = (a[..., 3] < alpha_cut) if a.shape[2] == 4 else np.zeros((h, w), bool)
    if not outside:
        outside = sorted({tuple(int(v) for v in rgb[y, x]) for y, x in ((0, 0), (0, w - 1), (h - 1, 0), (h - 1, w - 1))
                          if not transparent[y, x]})
    outside = [parse_color(c) for c in outside]
    if flood is None:
        flood = tolerance > 0
    om = np.zeros((h, w), bool)
    for c in outside:
        if tolerance > 0:
            om |= ((rgb - np.array(c)) ** 2).sum(2) <= tolerance ** 2
        else:
            om |= (rgb == np.array(c)).all(2)
    om |= transparent
    if flood:                                           # keep only outside regions that reach the image edge
        lab, n = label(om, 4)
        keep = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
        om = np.isin(lab, list(keep)) if keep else np.zeros((h, w), bool)
    sprite = ~om
    # boundary layers, taken from the outside in
    layers = []
    gone = om.copy()
    remaining = sprite.copy()
    for _ in range(max(1, int(thickness))):
        layer = remaining & touches(gone, connectivity)
        layers.append(layer)
        gone |= layer
        remaining &= ~layer
    boundary = np.zeros((h, w), bool)
    for l in layers:
        boundary |= l
    if ink_colors:
        ink = np.zeros((h, w), bool)
        for c in ink_colors:
            c = parse_color(c)
            ink |= (((rgb - np.array(c)) ** 2).sum(2) <= ink_tolerance ** 2)
    else:
        ink = luminance(rgb) < ink_lum
    border = boundary & ink
    skipped = boundary & ~ink
    report = _report(rgb, om, sprite, boundary, border, skipped, outside, tolerance, flood, connectivity)
    return EdgeResult(outside=om, sprite=sprite, boundary=boundary, border=border, skipped=skipped, report=report)


def _report(rgb, om, sprite, boundary, border, skipped, outside, tolerance, flood, connectivity):
    h, w, _ = rgb.shape
    warns = []
    lab, n = label(om, 4)
    regions = []
    for i in range(1, n + 1):
        m = lab == i
        edge = bool(m[0].any() or m[-1].any() or m[:, 0].any() or m[:, -1].any())
        cc = Counter(map(tuple, rgb[m].tolist()))
        regions.append(dict(pixels=int(m.sum()), touches_image_edge=edge, bbox=_bbox(m),
                            colors=[dict(color=_hex(c), pixels=int(k)) for c, k in cc.most_common(3)]))
    regions.sort(key=lambda r: -r['pixels'])
    backdrop = _hex(outside[0]) if outside else None
    ncol = len(np.unique(rgb.reshape(-1, 3), axis=0))
    if ncol > 3000 and tolerance == 0:
        warns.append(f'{ncol} distinct colours: this looks like a photo or JPEG. Exact matching is unreliable here: '
                     f'use --tolerance (try 10 to 20), --flood and a higher --ink-lum (try 60)')
    odd = [r for r in regions if not r['touches_image_edge'] and all(c['color'] != backdrop for c in r['colors'])]
    for r in odd[:3]:
        warns.append(f"enclosed outside region of {r['colors'][0]['color']} ({r['pixels']} px at {r['bbox']}) holds no "
                     f"backdrop colour: if it is part of the drawing, remove that colour from --outside")
    if len(odd) > 3:
        warns.append(f'... and {len(odd) - 3} more enclosed outside regions like that (the report lists the largest 12 regions)')
    nb = int(boundary.sum())
    if nb and skipped.sum() > 0.25 * nb:
        warns.append(f'{int(skipped.sum())} of {nb} boundary pixels are not ink: the art may have no dark edge there, or '
                     f'--ink-lum is too low; look at the skipped pixels (--show-skipped)')
    if not sprite.any():
        warns.append('no sprite pixels left: every pixel matched an outside colour')
    if nb == 0 and sprite.any():
        warns.append('the sprite touches no outside pixels (is --outside right?)')
    sl, sn = label(sprite, 8)
    sizes = sorted((int(s) for s in np.bincount(sl.ravel())[1:]), reverse=True) if sn else []
    bl, bn = label(border, 8)
    return dict(
        size=[w, h], outside_colors=[_hex(c) for c in outside], tolerance=tolerance, flood=bool(flood),
        connectivity=connectivity, outside_px=int(om.sum()), sprite_px=int(sprite.sum()), boundary_px=nb,
        border_px=int(border.sum()), skipped_px=int(skipped.sum()), border_regions=int(bn),
        sprite_regions=sizes[:8], outside_regions=regions[:12], warnings=warns)


# ------------------------------------------------------------------ pictures
def recolor(rgba, mask, color=(255, 0, 0)):
    """A copy of the picture with the masked pixels painted `color`."""
    out = np.asarray(rgba).copy()
    out[mask, 0], out[mask, 1], out[mask, 2] = color
    if out.shape[2] == 4:
        out[mask, 3] = 255
    return out


def cutout(rgba, sprite):
    """RGBA copy where everything outside the sprite is fully transparent."""
    a = np.asarray(rgba)
    out = np.dstack([a[..., :3], np.full(a.shape[:2], 255, np.uint8)]) if a.shape[2] == 3 else a.copy()
    out[~sprite, 3] = 0
    return out


def _save(arr, path, scale=1):
    im = Image.fromarray(arr)
    if scale > 1:
        im = im.resize((im.width * scale, im.height * scale), Image.NEAREST)
    im.save(path)


def _mask_img(mask):
    return (mask.astype(np.uint8) * 255)


# ------------------------------------------------------------------ self test
def self_test(verbose=True):
    """Draws a small test picture (backdrop, drop shadow, a sprite with a one pixel ink border, an inside ink line,
    a pocket, and a pale string with no border) and checks the tool finds exactly the border. Raises on failure."""
    BACK, SHAD, FUR, INK, PALE = (99, 99, 99), (49, 49, 49), (40, 44, 44), (8, 9, 9), (200, 200, 205)
    img = np.zeros((40, 60, 3), np.uint8)
    img[:] = BACK
    img[26:32, 4:56] = SHAD                                   # shadow: flat gray under the sprite, not touching the image edge
    img[5:25, 10:40] = INK                                    # sprite: ink rectangle ...
    img[6:24, 11:39] = FUR                                    # ... filled with fur
    img[14, 15:31] = INK                                      # an ink line INSIDE: must not be border
    img[16:22, 19:25] = INK                                   # a pocket: ink ring ...
    img[17:21, 20:24] = BACK                                  # ... around real backdrop
    img[25:29, 25:27] = PALE                                  # a pale string hanging below, no border
    r = find_border(img, outside=[BACK, SHAD])
    # outer ring: 2 * (30 + 20) - 4 = 96 pixels, minus the 2 bottom ones that sit on the pale string (not on the outside);
    # pocket ring: 20 pixels, minus its 4 corners, which touch the pocket only diagonally (4-neighbour rule) = 16
    ring = (96 - 2) + (20 - 4)
    checks = {
        'border pixels': (int(r.border.sum()), ring),
        'skipped (pale string) pixels': (int(r.skipped.sum()), 8),
        'inside ink line is not border': (int((r.border[14, 15:31]).sum()), 0),
        'shadow is not sprite': (int((r.sprite & (img == SHAD).all(2)).sum()), 0),
        'no border pixel is outside': (int((r.border & r.outside).sum()), 0),
    }
    bad = {k: v for k, v in checks.items() if v[0] != v[1]}
    if verbose:
        for k, (got, want) in checks.items():
            print(('PASS ' if got == want else 'FAIL ') + f'{k}: got {got}, want {want}')
    if bad:
        raise AssertionError(f'self test failed: {bad}')
    return True


# ------------------------------------------------------------------ command line
def _frame_name(stem, i, many):
    return f'{stem}_f{i}' if many else stem


def main(argv=None):
    ap = argparse.ArgumentParser(description='Find the drawn outline of a sprite in pixel-art images (see the top of this file).')
    ap.add_argument('input', nargs='?', help='image or animation (GIF, PNG, WebP, ...)')
    ap.add_argument('--outside', nargs='+', metavar='COLOR', help='colours that are not the sprite: R,G,B or #rrggbb')
    ap.add_argument('--suggest', action='store_true', help='print likely backdrop and shadow colours, then exit')
    ap.add_argument('--tolerance', type=float, default=0.0)
    ap.add_argument('--flood', action='store_true')
    ap.add_argument('--ink-lum', type=float, default=45.0)
    ap.add_argument('--ink-color', nargs='+', metavar='COLOR')
    ap.add_argument('--thickness', type=int, default=1)
    ap.add_argument('--connectivity', type=int, choices=(4, 8), default=4)
    ap.add_argument('--border-color', default='255,0,0')
    ap.add_argument('--show-skipped', metavar='COLOR')
    ap.add_argument('--frame', type=int)
    ap.add_argument('--frames', choices=('all',))
    ap.add_argument('--scale', type=int, default=1)
    ap.add_argument('--outdir')
    ap.add_argument('--no-cutout', action='store_true')
    ap.add_argument('--self-test', action='store_true', help='check the tool on a built-in picture and exit')
    a = ap.parse_args(argv)
    if a.self_test:
        self_test()
        print('self test passed')
        return 0
    if not a.input:
        ap.error('give an input image (or --self-test)')
    frames = load_frames(a.input, None if a.frames == 'all' else (a.frame or 0))
    if a.suggest:
        for rec in suggest_outside(frames[0][1]):
            print(f"{rec['kind']:12s} {rec['color'][0]},{rec['color'][1]},{rec['color'][2]}  {rec['hex']}  "
                  f"{rec['pixels']} px, largest region {rec['largest_region']}, bbox {rec['bbox']}"
                  f"{'  (touches the image edge)' if rec['touches_image_edge'] else ''}")
        print('These are suggestions. Pass the ones that are not the character with --outside.')
        return 0
    stem = os.path.splitext(os.path.basename(a.input))[0]
    outdir = a.outdir or os.path.join(os.path.dirname(os.path.abspath(a.input)), stem + '_edge')
    os.makedirs(outdir, exist_ok=True)
    many = len(frames) > 1
    border_color = parse_color(a.border_color)
    reports = {}
    for i, rgba in frames:
        r = find_border(rgba, outside=a.outside, tolerance=a.tolerance, flood=True if a.flood else None, ink_lum=a.ink_lum,
                        ink_colors=a.ink_color, thickness=a.thickness, connectivity=a.connectivity)
        name = _frame_name(stem, i, many)
        pic = recolor(rgba, r.border, border_color)
        if a.show_skipped:
            pic = recolor(pic, r.skipped, parse_color(a.show_skipped))
        _save(rgba, os.path.join(outdir, name + '_original.png'), a.scale)
        _save(pic, os.path.join(outdir, name + '_border.png'), a.scale)
        _save(_mask_img(r.border), os.path.join(outdir, name + '_mask_border.png'), a.scale)
        _save(_mask_img(r.sprite), os.path.join(outdir, name + '_mask_sprite.png'), a.scale)
        if not a.no_cutout:
            _save(cutout(rgba, r.sprite), os.path.join(outdir, name + '_cutout.png'), a.scale)
        reports[str(i)] = r.report
        rp = r.report
        print(f"frame {i}: border {rp['border_px']} px, skipped {rp['skipped_px']} px, "
              f"{len(rp['outside_regions'])} outside regions, {len(rp['warnings'])} warnings")
        for wmsg in rp['warnings']:
            print('  WARNING:', wmsg)
    with open(os.path.join(outdir, stem + '_report.json'), 'w') as f:
        json.dump(reports, f, indent=1)
    print('wrote', outdir)
    return 0


if __name__ == '__main__':
    sys.exit(main())
