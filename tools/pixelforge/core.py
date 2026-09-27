"""pixelforge core: a tiny 2.5D sculpt-and-shade pixel-art renderer.

Art is built from shaded primitives (ellipsoids, tapered capsules,
bevelled polygons) that write into a depth buffer, so overlapping parts
intersect naturally. The result is quantized onto hand-tuned color ramps
(hue-shifted shadows, warm highlights), then finished the way a pixel
artist would: cast shadows, dark lines where one part passes in front of
another, a selective outline, and pixel-level "ink" for eyes and small
details. Everything is drawn at native resolution, no resampling.

Coordinates are canvas pixels, y down. Depth grows toward the viewer.
Light comes from the upper left, in front.
"""
from __future__ import annotations

import colorsys
import math

import numpy as np
from PIL import Image, ImageDraw

LIGHT = np.array([-0.62, -0.68, 0.42])
LIGHT = LIGHT / np.linalg.norm(LIGHT)
BAYER = np.array([[0.0, 0.5], [0.75, 0.25]]) - 0.375


# ---------------------------------------------------------------- color
def hx(c):
    if isinstance(c, str):
        c = c.lstrip("#")
        return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))
    return tuple(int(v) for v in c[:3])


def _hue_toward(h, target, amt):
    d = ((target - h + 0.5) % 1.0) - 0.5
    return (h + d * amt) % 1.0


def ramp(base, n=6, dark=0.09, light=0.86, shift=0.10, sat=1.0):
    """Color ramp dark->light around `base`. Shadows lean cool (blue/purple),
    highlights lean warm (yellow), the classic pixel-art hue shift."""
    r, g, b = [v / 255 for v in hx(base)]
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    s = min(1.0, s * sat)
    out = []
    for i in range(n):
        t = i / (n - 1)
        # lightness: pass through the base value at ~60% of the ramp
        if t < 0.6:
            li = dark + (l - dark) * (t / 0.6)
        else:
            li = l + (light - l) * ((t - 0.6) / 0.4)
        k = abs(t - 0.6) / 0.6
        if t < 0.6:
            hi = _hue_toward(h, 0.72, shift * k)
            si = min(1.0, s * (1.0 + 0.15 * k))
        else:
            hi = _hue_toward(h, 0.14, shift * k * 1.2)
            si = s * (1.0 - 0.18 * k)
        rr, gg, bb = colorsys.hls_to_rgb(hi, max(0, min(1, li)), max(0, min(1, si)))
        out.append((round(rr * 255), round(gg * 255), round(bb * 255)))
    return out


def mix(a, b, t):
    a, b = hx(a), hx(b)
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def darken(c, k=0.6):
    c = hx(c)
    return tuple(round(v * k) for v in c)


class Mat:
    def __init__(self, colors, *, spec=0.0, emit=False, tex=None, tex_amp=0.0,
                 dither=0.0, amb=0.16, line=None, outline=None, soft=1.0):
        self.colors = [hx(c) for c in colors]
        self.spec = spec          # 0..1 specular highlight strength
        self.emit = emit          # ignore lighting (flames, glows)
        self.tex = tex            # 'fur' | 'noise' | 'scale' | callable
        self.tex_amp = tex_amp
        self.dither = dither
        self.amb = amb
        self.soft = soft          # <1 flattens the shading
        self.line = hx(line) if line else None
        self.outline = hx(outline) if outline else None

    @property
    def n(self):
        return len(self.colors)


def M(base, **kw):
    """Material from a base color, with a default hue-shifted ramp."""
    rk = {k: kw.pop(k) for k in ("n", "dark", "light", "shift", "sat") if k in kw}
    return Mat(ramp(base, **rk), **kw)


# ---------------------------------------------------------------- noise
def _hash2(x, y, seed=0):
    x = np.asarray(x, dtype=np.uint64)
    y = np.asarray(y, dtype=np.uint64)
    with np.errstate(over="ignore"):
        h = (x * np.uint64(374761393) + y * np.uint64(668265263) + np.uint64(seed * 144269504)) & np.uint64(0xFFFFFFFF)
        h = ((h ^ (h >> np.uint64(13))) * np.uint64(1274126177)) & np.uint64(0xFFFFFFFF)
        h = (h ^ (h >> np.uint64(16))) & np.uint64(0xFFFF)
    return h.astype(float) / 65535.0


def value_noise(w, h, scale, seed=0):
    ys, xs = np.mgrid[0:h, 0:w].astype(float)
    fx, fy = xs / scale, ys / scale
    x0, y0 = np.floor(fx).astype(np.int64), np.floor(fy).astype(np.int64)
    tx, ty = fx - x0, fy - y0
    tx = tx * tx * (3 - 2 * tx)
    ty = ty * ty * (3 - 2 * ty)
    n00, n10 = _hash2(x0, y0, seed), _hash2(x0 + 1, y0, seed)
    n01, n11 = _hash2(x0, y0 + 1, seed), _hash2(x0 + 1, y0 + 1, seed)
    return (n00 * (1 - tx) + n10 * tx) * (1 - ty) + (n01 * (1 - tx) + n11 * tx) * ty


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, seed=1):
        self.w, self.h = w, h
        self.seed = seed
        self.depth = np.full((h, w), -1e9)
        self.mat = np.full((h, w), -1, dtype=np.int32)
        self.grp = np.full((h, w), -1, dtype=np.int32)
        self.nrm = np.zeros((h, w, 3))
        self.nrm[..., 2] = 1
        self.shift = np.zeros((h, w))       # per-pixel ramp offset (patterns)
        self.mats: list[Mat] = []
        self._mat_ids: dict[int, int] = {}
        self._gid = 0
        self.ink_ops = []                    # drawn after shading, before outline
        self.fx_ops = []                     # drawn last, never outlined
        self.ys, self.xs = np.mgrid[0:h, 0:w].astype(float)
        self.xs += 0.5
        self.ys += 0.5
        self._noise = {}

    # -- materials / groups
    def m(self, mat: Mat) -> int:
        k = id(mat)
        if k not in self._mat_ids:
            self._mat_ids[k] = len(self.mats)
            self.mats.append(mat)
        return self._mat_ids[k]

    def group(self):
        self._gid += 1
        return self._gid

    def noise(self, scale, seed=0):
        k = (scale, seed)
        if k not in self._noise:
            self._noise[k] = value_noise(self.w, self.h, scale, self.seed * 31 + seed)
        return self._noise[k]

    # -- core write
    def _write(self, mask, depth, nrm, mat, grp, decal=False, only=None):
        mi = self.m(mat)
        if decal:
            sel = mask & (self.mat >= 0)
            if only is not None:
                sel &= np.isin(self.grp, np.atleast_1d(only))
            self.mat[sel] = mi
            return
        sel = mask & (depth > self.depth)
        self.depth[sel] = depth[sel]
        self.mat[sel] = mi
        self.grp[sel] = grp
        self.nrm[sel] = nrm[sel]
        self.shift[sel] = 0

    def _g(self, g):
        return self.group() if g is None else g

    # -- primitives
    def ell(self, cx, cy, rx, ry, mat, z=0.0, rot=0.0, th=None, g=None, decal=False,
            only=None, flat=1.0, tuft=0, tuft_len=3.0, tuft_dir=0.0, tuft_arc=None, g_seed=1):
        """Ellipsoid. rot in degrees. th = how far it bulges toward the viewer."""
        th = min(rx, ry) if th is None else th
        a = math.radians(rot)
        ca, sa = math.cos(a), math.sin(a)
        dx, dy = self.xs - cx, self.ys - cy
        u = (dx * ca + dy * sa) / max(rx, 0.01)
        v = (-dx * sa + dy * ca) / max(ry, 0.01)
        r2 = u * u + v * v
        mask = r2 <= 1.0
        stroke = None
        if tuft:
            # fur: sawtooth tufts around the rim plus dark clump strokes
            ang = np.arctan2(v, u) - math.radians(tuft_dir)
            ph = (ang / (2 * math.pi) * tuft + 0.37 * g_seed) % 1.0
            rr = np.sqrt(r2)
            ext = tuft_len / max(min(rx, ry), 1)
            reach = 1 + ext * (1 - ph) ** 1.6
            if tuft_arc is not None:
                a0, a1 = [math.radians(a) for a in tuft_arc]
                aa = np.arctan2(dy, dx) % (2 * math.pi)
                a0, a1 = a0 % (2 * math.pi), a1 % (2 * math.pi)
                inarc = (aa >= a0) & (aa <= a1) if a0 <= a1 else (aa >= a0) | (aa <= a1)
                reach = np.where(inarc, reach, 1.0)
            mask = rr <= reach
            r2 = np.minimum(r2, 0.97)
            stroke = mask & (ph < 0.22) & (rr > 0.5)
        nz = np.sqrt(np.clip(1 - r2, 0, 1))
        nx = (u * ca - v * sa) * flat
        ny = (u * sa + v * ca) * flat
        nrm = np.stack([nx, ny, nz], -1)
        nrm /= np.linalg.norm(nrm, axis=-1, keepdims=True) + 1e-9
        before = self.depth.copy()
        self._write(mask, z + th * nz, nrm, mat, self._g(g), decal, only)
        if stroke is not None:
            self.shift[stroke & (self.depth != before)] -= 1
        return self

    def cap(self, x0, y0, r0, x1, y1, r1, mat, z=0.0, z1=None, g=None, decal=False,
            only=None, th=1.0):
        """Tapered capsule from (x0,y0,r0) to (x1,y1,r1)."""
        z1 = z if z1 is None else z1
        ax, ay = self.xs - x0, self.ys - y0
        bx, by = x1 - x0, y1 - y0
        L2 = bx * bx + by * by + 1e-9
        t = np.clip((ax * bx + ay * by) / L2, 0, 1)
        cx, cy = x0 + bx * t, y0 + by * t
        r = r0 + (r1 - r0) * t
        dx, dy = self.xs - cx, self.ys - cy
        d = np.sqrt(dx * dx + dy * dy)
        mask = d <= r
        rr = np.maximum(r, 0.01)
        lx, ly = dx / rr, dy / rr
        nz = np.sqrt(np.clip(1 - lx * lx - ly * ly, 0, 1))
        nrm = np.stack([lx, ly, nz], -1)
        depth = z + (z1 - z) * t + rr * nz * th
        self._write(mask, depth, nrm, mat, self._g(g), decal, only)
        return self

    def chain(self, pts, mat, z=0.0, z1=None, g=None, **kw):
        """Smooth limb/tail through [(x,y,r), ...] as joined capsules."""
        g = self._g(g)
        n = len(pts) - 1
        z1 = z if z1 is None else z1
        for i in range(n):
            (xa, ya, ra), (xb, yb, rb) = pts[i], pts[i + 1]
            za = z + (z1 - z) * i / max(n, 1)
            zb = z + (z1 - z) * (i + 1) / max(n, 1)
            self.cap(xa, ya, ra, xb, yb, rb, mat, za, zb, g=g, **kw)
        return self

    def poly(self, pts, mat, z=0.0, bevel=2, th=None, g=None, decal=False, only=None,
             tilt=(0.0, 0.0)):
        """Filled polygon with a rounded bevel around its edge. tilt=(tx,ty)
        leans the flat face so it catches more or less light."""
        im = Image.new("L", (self.w, self.h), 0)
        ImageDraw.Draw(im).polygon([(float(x), float(y)) for x, y in pts], fill=255)
        mask = np.array(im) > 0
        dist = mask.astype(float)
        cur = mask.copy()
        for i in range(1, int(bevel) + 1):
            e = cur.copy()
            e[1:, :] &= cur[:-1, :]
            e[:-1, :] &= cur[1:, :]
            e[:, 1:] &= cur[:, :-1]
            e[:, :-1] &= cur[:, 1:]
            cur = e
            dist += cur
        b = max(bevel, 1)
        gy, gx = np.gradient(dist)
        k = np.clip(1 - (dist - 1) / b, 0, 1)
        nx = -gx * k * 1.2 + tilt[0]
        ny = -gy * k * 1.2 + tilt[1]
        nz = np.ones_like(nx)
        nrm = np.stack([nx, ny, nz], -1)
        nrm /= np.linalg.norm(nrm, axis=-1, keepdims=True)
        th = b if th is None else th
        depth = z + th * np.clip(dist / b, 0, 1)
        self._write(mask, depth, nrm, mat, self._g(g), decal, only)
        return self

    def tri(self, a, b, c, mat, **kw):
        return self.poly([a, b, c], mat, **kw)

    def pattern(self, fn, amt, only=None, where=None):
        """Shift ramp index by amt where fn(xs, ys) is true (stripes, spots)."""
        sel = fn(self.xs, self.ys) & (self.mat >= 0)
        if only is not None:
            sel &= np.isin(self.grp, np.atleast_1d(only))
        if where is not None:
            sel &= np.isin(self.mat, [self.m(w) for w in np.atleast_1d(where)])
        self.shift[sel] += amt
        return self

    # -- ink (pixel detail) and fx
    def ink(self, fn):
        self.ink_ops.append(fn)
        return self

    def fx(self, fn):
        self.fx_ops.append(fn)
        return self

    # -- render
    def render(self, outline=True, shadow=True, lines=True, line_t=2.0):
        h, w = self.h, self.w
        rgb = np.zeros((h, w, 3), dtype=np.int32)
        alpha = self.mat >= 0
        idx = np.zeros((h, w), dtype=np.int32)
        n = self.nrm
        ndl = np.clip(n @ LIGHT, 0, 1)
        up = np.clip(-n[..., 1], 0, 1)
        bay = np.tile(BAYER, (h // 2 + 1, w // 2 + 1))[:h, :w]
        for mi, mat in enumerate(self.mats):
            sel = self.mat == mi
            if not sel.any():
                continue
            if mat.emit:
                inten = 0.55 + 0.45 * n[..., 2]
            else:
                inten = mat.amb + (1 - mat.amb) * ndl ** 1.15 + 0.10 * up
                inten = inten * mat.soft + (1 - mat.soft) * 0.6
            tex = 0
            if mat.tex == "fur":
                # directional strands: short strokes that fall down and back
                perp = self.xs * 0.94 - self.ys * 0.34 + self.noise(2.2, 11) * 2.6
                along = self.xs * 0.34 + self.ys * 0.94
                brk = self.noise(3.5, 13)
                band = perp % 3.2
                seg = ((along + self.noise(1.7, 17) * 6) % 7) < 5
                dark = (band < 0.9) & seg & (brk > 0.3)
                lite = (band > 1.7) & (band < 2.3) & seg & (brk > 0.45)
                tex = dark * -1.0 + lite * 0.8 + (self.noise(6.0, 5) - 0.5) * 0.3
            elif mat.tex == "noise":
                tex = (self.noise(2.5, 7) - 0.5) * 1.6
            elif mat.tex == "grain":
                tex = (self.noise(1.2, 9) - 0.5) * 1.6
            elif callable(mat.tex):
                tex = mat.tex(self.xs, self.ys)
            f = inten * (mat.n - 2) + 1 + tex * mat.tex_amp + self.shift + bay * mat.dither
            if mat.spec > 0 and not mat.emit:
                hv = LIGHT + np.array([0, 0, 1.0])
                hv /= np.linalg.norm(hv)
                sp = np.clip(n @ hv, 0, 1) ** 40
                f = f + sp * mat.spec * 4
            ii = np.clip(np.round(f), 1, mat.n - 1).astype(np.int32)
            idx[sel] = ii[sel]
        # bounce light: a thin rim on the shadow side (lower right) of each shape
        edge = np.zeros((h, w), bool)
        edge[:-1, :] |= ~alpha[1:, :]
        edge[:, :-1] |= ~alpha[:, 1:]
        edge[-1, :] = True
        edge &= alpha & (ndl < 0.35)
        for mi, mat in enumerate(self.mats):
            if mat.emit:
                edge &= self.mat != mi
        idx = np.where(edge, idx + 1, idx)
        # cast shadows: something in front and up-left of this pixel
        if shadow:
            sh = np.zeros((h, w), bool)
            for k in (1, 2, 3):
                q = np.full((h, w), -1e9)
                q[k:, k:] = self.depth[:-k, :-k]
                sh |= alpha & (q > self.depth + 1.5 + k * 0.8)
            idx = np.where(sh, np.maximum(idx - 1, 1), idx)
        # color lookup
        for mi, mat in enumerate(self.mats):
            sel = self.mat == mi
            if sel.any():
                pal = np.array(mat.colors)
                rgb[sel] = pal[np.clip(idx[sel], 0, mat.n - 1)]
        # interior lines where another group passes in front
        if lines:
            ln = np.zeros((h, w), bool)
            for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)):
                q = np.roll(np.roll(self.depth, dy, 0), dx, 1)
                qg = np.roll(np.roll(self.grp, dy, 0), dx, 1)
                ln |= alpha & (qg >= 0) & (qg != self.grp) & (q > self.depth + line_t)
            for mi, mat in enumerate(self.mats):
                sel = ln & (self.mat == mi)
                if sel.any():
                    rgb[sel] = mat.line or darken(mat.colors[0], 0.9)
        self.rgb, self.alpha, self.idx = rgb, alpha.copy(), idx
        for op in self.ink_ops:
            op(self)
        if outline:
            a = self.alpha
            nb = np.zeros_like(a)
            src_mat = np.full((h, w), -1)
            for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)):
                sa = np.roll(np.roll(a, dy, 0), dx, 1)
                sm = np.roll(np.roll(self.mat, dy, 0), dx, 1)
                if dy == 1:
                    sa[0, :] = False
                if dy == -1:
                    sa[-1, :] = False
                if dx == 1:
                    sa[:, 0] = False
                if dx == -1:
                    sa[:, -1] = False
                newly = sa & ~a
                src_mat = np.where(newly & (src_mat < 0), sm, src_mat)
                nb |= newly
            # lit side (outline pixel sits up-left of the shape) gets a softer outline
            lit = np.zeros((h, w), bool)
            lit[:-1, :-1] = a[1:, 1:]
            for mi, mat in enumerate(self.mats):
                sel = nb & (src_mat == mi)
                if not sel.any():
                    continue
                dark = mat.outline or darken(mat.colors[0], 0.55)
                soft = mix(dark, mat.colors[1], 0.55)
                rgb[sel & ~lit] = dark
                rgb[sel & lit] = soft
            self.alpha = a | nb
        for op in self.fx_ops:
            op(self)
        out = np.zeros((h, w, 4), dtype=np.uint8)
        out[..., :3] = np.clip(self.rgb, 0, 255)
        out[..., 3] = np.where(self.alpha, 255, 0)
        return Image.fromarray(out, "RGBA")

    # -- pixel helpers for ink/fx ops
    def put(self, x, y, c):
        x, y = int(round(x)), int(round(y))
        if 0 <= x < self.w and 0 <= y < self.h:
            self.rgb[y, x] = hx(c)
            self.alpha[y, x] = True

    def col(self, mat, i):
        return mat.colors[max(0, min(mat.n - 1, i))]

    def shade_at(self, x, y):
        x, y = int(x), int(y)
        return tuple(self.rgb[y, x])


# ---------------------------------------------------------------- details
EYES = {
    # K lid/outline, I iris, i iris light, P pupil, W glint, w sclera
    "dot": ["KK", "KW"],
    "small": [".KK.", "KWIK", "KPiK", ".KK."],
    "round": [".KKK.", "KWIPK", "KIPPK", "KiPiK", ".KKK."],
    "big": [".KKKK.", "KWWIPK", "KWIPPK", "KIPPPK", "KiiPiK", ".KKKK."],
    "cat": ["KKKKK.", "KWIPIK", "KIIPiK", ".KiPiK", "..KKK."],
    "fierce": ["KKKKKK", ".KWPIK", "..KPiK", "...KK."],
    "sleepy": ["KKKK", "KiPK", ".KK."],
    "bead": [".K.", "KWK", ".K."],
    "glow": [".KKK.", "KWiiK", "KiIiK", ".KKK."],
    "kbig": [".KKKKK.", "KKWWIPK", "KWWIPPK", "KIIPPPK", "KIIPPPK", "KiiPPiK", ".KiiiK.", "..KKK.."],
    "kcat": ["KKKKKKK", "KWWIPIK", "KWIIPiK", "KIIIPiK", ".KiiPiK", "..KiiK.", "...KK.."],
    "almond": ["..KKKK.", ".KWIPIK", "KIIPPiK", ".KiiiK.", "..KKK.."],
}


def eye(c: "Canvas", x, y, kind="round", iris=(230, 190, 60), pupil=(22, 14, 20),
        lid=(26, 16, 24), white=(250, 246, 236), flip=False):
    """Stamp a pixel eye with its top-left at (x, y). flip mirrors it."""
    tpl = EYES[kind]
    iris = hx(iris)
    light = mix(iris, (255, 250, 220), 0.45)
    cmap = {"K": hx(lid), "I": iris, "i": light, "P": hx(pupil), "W": (255, 253, 244), "w": hx(white)}
    for j, row in enumerate(tpl):
        if flip:
            row = row[::-1]
        for i, ch in enumerate(row):
            if ch in cmap:
                c.put(x + i, y + j, cmap[ch])


def peye(c: "Canvas", cx, cy, rx, ry, iris=(230, 190, 60), pupil=(22, 14, 20),
         lid=(28, 16, 24), pw=0.45, ph=0.8, slit=False, white=None, look=-0.25,
         glint=True, lash=0, angry=0.0):
    """Parametric pixel eye: dark rim, graded iris, pupil, glint, heavy upper lid.
    rx/ry in pixels. look shifts the pupil (-1 left .. 1 right). angry>0 slants
    the lid down toward the nose (left)."""
    iris = hx(iris)
    top = mix(iris, (20, 10, 20), 0.45)
    bot = mix(iris, (255, 250, 210), 0.45)
    x0, x1 = int(math.floor(cx - rx - 1)), int(math.ceil(cx + rx + 1))
    y0, y1 = int(math.floor(cy - ry - 1)), int(math.ceil(cy + ry + 1))
    inside = {}
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            u = (x + 0.5 - cx) / rx
            v = (y + 0.5 - cy) / ry
            lidcut = v < -0.95 + angry * (-(u) * 0.9 - 0.2)
            inside[(x, y)] = (u * u + v * v <= 1.0) and not lidcut
    pcx = cx + look * rx * 0.35
    for (x, y), ins in inside.items():
        if not ins:
            continue
        u = (x + 0.5 - cx) / rx
        v = (y + 0.5 - cy) / ry
        edge = any(not inside.get((x + dx, y + dy), False) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
        if edge:
            c.put(x, y, lid)
            continue
        if white is not None and abs(x + 0.5 - pcx) > rx * 0.62:
            c.put(x, y, white)
            continue
        t = (v + 1) / 2
        col = mix(top, bot, t ** 1.2)
        pu = (x + 0.5 - pcx) / max(rx * pw * (0.35 if slit else 1), 0.6)
        pv = (y + 0.5 - cy - ry * 0.1) / max(ry * ph, 0.6)
        if pu * pu + pv * pv <= 1.0:
            col = hx(pupil)
        c.put(x, y, col)
    # heavy upper lid: thicken the top rim
    for (x, y), ins in inside.items():
        if ins and not inside.get((x, y - 1), False):
            c.put(x, y - 1, lid)
            if lash and x < cx:
                c.put(x - 1, y - 1, lid)
    if glint:
        gx, gy = int(cx - rx * 0.35), int(cy - ry * 0.45)
        c.put(gx, gy, (255, 253, 244))
        if rx >= 3 and ry >= 3:
            c.put(gx + 1, gy, (255, 253, 244))
            c.put(gx, gy + 1, (255, 253, 244))
            c.put(gx + 1, gy + 1, (255, 253, 244))
        if ry >= 4:
            c.put(int(cx + rx * 0.3), int(cy + ry * 0.45), mix(bot, (255, 255, 255), 0.6))


def sparkle(c: Canvas, x, y, col, size=1):
    c.put(x, y, (255, 255, 240))
    for i in range(1, size + 1):
        for dx, dy in ((i, 0), (-i, 0), (0, i), (0, -i)):
            c.put(x + dx, y + dy, col)


def crop_frames(frames, pad=1):
    box = None
    for f in frames:
        b = f.getbbox()
        if b is None:
            continue
        box = b if box is None else (min(box[0], b[0]), min(box[1], b[1]),
                                     max(box[2], b[2]), max(box[3], b[3]))
    if box is None:
        return frames
    box = (max(0, box[0] - pad), max(0, box[1] - pad),
           min(frames[0].width, box[2] + pad), min(frames[0].height, box[3] + pad))
    return [f.crop(box) for f in frames]


FLAME_OUT = Mat(["#5a1206", "#9e2410", "#d8421a", "#f47a22", "#ffb13c", "#ffd66a"], emit=True, dither=0.6)
FLAME_IN = Mat(["#f47a22", "#ffb13c", "#ffd66a", "#fff0a8", "#fffbe6"], emit=True, dither=0.6)


def flame(c: "Canvas", x, y, h, w, t=0, z=0.0, outer=None, inner=None, lean=0.0, tongues=3):
    """Licking flame rising from (x, y). Flickers with frame t."""
    outer = outer or FLAME_OUT
    inner = inner or FLAME_IN
    g = c.group()
    wob = [0.0, 1.0, 0.3, -0.8][t % 4]
    offs = [(-0.55, 0.62), (0.0, 1.0), (0.5, 0.72), (-0.25, 0.45), (0.3, 0.5)][:tongues]
    for k, (ox, oh) in enumerate(offs):
        sx = x + ox * w * 0.8
        hh = h * oh * (1 + 0.08 * math.sin(t * 1.7 + k * 2.1))
        tip_x = sx + lean * hh + (wob if k % 2 == 0 else -wob) * w * 0.25
        c.cap(sx, y, w * (0.75 if k == 1 else 0.5), tip_x, y - hh, 0.6, outer, z=z, g=g)
    c.cap(x, y + w * 0.1, w * 0.45, x + lean * h * 0.5 + wob * w * 0.15, y - h * 0.55, 0.6,
          inner, z=z + w, g=g)
    return g
