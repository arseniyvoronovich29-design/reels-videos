"""Style-3 graphics core: soft-shaded vector shapes, glows, particles, grain, typography.
Everything works on RGBA PIL images; shapes are drawn supersampled inside their own bbox to stay fast."""
import math, os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops

W, H, FPS = 1080, 1920, 30
HERE = os.path.dirname(os.path.abspath(__file__))
FD = os.path.join(HERE, "..", "fonts")
_fonts = {}


def font(name, size):
    key = (name, int(size))
    if key not in _fonts:
        p = os.path.join(FD, name + ".ttf")
        if not os.path.exists(p):
            p = os.path.join(FD, name + ".otf")
        _fonts[key] = ImageFont.truetype(p, int(size))
    return _fonts[key]


TITLE = "Montserrat-Black"
COND = "Oswald-Bold"
BODY = "Montserrat-ExtraBold"


# ------------------------------------------------------------------ math
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease(x):
    x = clamp(x)
    return 1 - (1 - x) ** 3


def smooth(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def lerp(a, b, k):
    return a + (b - a) * k


def mixc(a, b, k):
    k = clamp(k)
    return tuple(int(round(a[i] + (b[i] - a[i]) * k)) for i in range(3))


def pw(pts, x):
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return float(np.interp(x, xs, ys))


def kv(v, u):
    """value or keyframes [(u, v), ...]"""
    if isinstance(v, (list, tuple)) and v and isinstance(v[0], (list, tuple)):
        return pw(v, u)
    return v


def catmull(pts, closed=True, n=8):
    P = list(pts)
    if closed:
        P = [P[-1]] + P + [P[0], P[1]]
    else:
        P = [P[0]] + P + [P[-1]]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for j in range(n):
            t = j / n
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * p1[k]) + (-p0[k] + p2[k]) * t + (2 * p0[k] - 5 * p1[k] + 4 * p2[k] - p3[k]) * t2 +
                                    (-p0[k] + 3 * p1[k] - 3 * p2[k] + p3[k]) * t3) for k in range(2)))
    if not closed:
        out.append(P[-2])
    return out


def ellipse_pts(cx, cy, rx, ry, n=48, a0=0.0):
    return [(cx + rx * math.cos(a0 + 2 * math.pi * k / n), cy + ry * math.sin(a0 + 2 * math.pi * k / n)) for k in range(n)]


# ------------------------------------------------------------------ shaded shapes
SSF = 2  # supersampling inside bboxes


def _bbox(pts, pad):
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return int(math.floor(min(xs) - pad)), int(math.floor(min(ys) - pad)), int(math.ceil(max(xs) + pad)), int(math.ceil(max(ys) + pad))


def shape_mask(pts, box, ellipse=None):
    x0, y0, x1, y1 = box
    m = Image.new("L", ((x1 - x0) * SSF, (y1 - y0) * SSF), 0)
    d = ImageDraw.Draw(m)
    if ellipse:
        cx, cy, rx, ry = ellipse
        d.ellipse(((cx - rx - x0) * SSF, (cy - ry - y0) * SSF, (cx + rx - x0) * SSF, (cy + ry - y0) * SSF), fill=255)
    else:
        d.polygon([((x - x0) * SSF, (y - y0) * SSF) for x, y in pts], fill=255)
    return m.resize((x1 - x0, y1 - y0), Image.LANCZOS)


def shade(img, pts, base, light=(-0.5, -0.7), hi=0.35, lo=0.45, rim=0.0, rim_col=None, inner=0.5, outline=None, ow=3,
          spec=0.0, spec_at=(0.3, 0.25), spec_r=0.18, alpha=1.0, ellipse=None, tex=None, clip=None, grad_col=None):
    """Fill polygon (or ellipse=(cx,cy,rx,ry)) with a soft 3D-ish shading.
    light: direction the light comes FROM (unit-ish, screen coords). hi/lo: highlight / shadow strength.
    inner: soft dark inner edge (ambient occlusion). rim: bright rim on the shadow side. spec: specular blob."""
    if ellipse:
        cx, cy, rx, ry = ellipse
        pts = [(cx - rx, cy - ry), (cx + rx, cy + ry)]
    size = max(_bbox(pts, 0)[2] - _bbox(pts, 0)[0], _bbox(pts, 0)[3] - _bbox(pts, 0)[1], 2)
    pad = int(max(4, ow + 2))
    box = _bbox(pts, pad)
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    if w <= 2 or h <= 2:
        return
    m = shape_mask(pts, box, ellipse)
    ma = np.asarray(m).astype(np.float32) / 255.0
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    lx, ly = light
    ln = math.hypot(lx, ly) or 1
    lx, ly = lx / ln, ly / ln
    # normalised position across the shape
    cxm, cym = (w - 1) / 2, (h - 1) / 2
    nx, ny = (xx - cxm) / (w / 2), (yy - cym) / (h / 2)
    g = -(nx * lx + ny * ly)              # +1 lit side, -1 shadow side
    g = np.clip(g, -1.2, 1.2)
    col = np.empty((h, w, 3), np.float32)
    base_a = np.array(base, np.float32)
    if grad_col is not None:
        # vertical colour gradient (top -> bottom)
        bot = np.array(grad_col, np.float32)
        k = np.clip(yy / max(h - 1, 1), 0, 1)[..., None]
        base_a = base_a * (1 - k) + bot * k
        col[:] = base_a
    else:
        col[:] = base_a
    light_c = np.array((255, 248, 236), np.float32)
    dark_c = np.array((10, 12, 30), np.float32)
    kpos = np.clip(g, 0, None)[..., None] * hi
    kneg = np.clip(-g, 0, None)[..., None] * lo
    col = col * (1 - kpos) + light_c * kpos
    col = col * (1 - kneg) + dark_c * kneg
    if inner > 0:
        r = max(2.0, size * 0.06)
        bl = np.asarray(m.filter(ImageFilter.GaussianBlur(r))).astype(np.float32) / 255.0
        edge = np.clip((ma - bl) * 2.2, 0, 1)[..., None] * inner
        col = col * (1 - edge * 0.8)
    if rim > 0:
        r = max(2.0, size * 0.03)
        bl = np.asarray(m.filter(ImageFilter.GaussianBlur(r))).astype(np.float32) / 255.0
        edge = np.clip((ma - bl) * 3.0, 0, 1) * np.clip(-g, 0, None)
        rc = np.array(rim_col or (150, 200, 255), np.float32)
        col = col * (1 - edge[..., None] * rim) + rc * edge[..., None] * rim
    if spec > 0:
        sx, sy = spec_at
        d2 = ((xx / w - sx) ** 2 + (yy / h - sy) ** 2) / (spec_r ** 2)
        s = np.exp(-d2 * 2.2)[..., None] * spec
        col = col * (1 - s) + 255 * s
    if tex is not None:
        col = tex(col, xx, yy, w, h)
    a = ma * alpha
    if clip is not None:
        a = a * clip(x0, y0, w, h)
    lay = np.concatenate([np.clip(col, 0, 255), (a * 255)[..., None]], axis=2).astype(np.uint8)
    L = Image.fromarray(lay, "RGBA")
    img.alpha_composite(L, (x0, y0)) if x0 >= 0 and y0 >= 0 and x1 <= img.size[0] and y1 <= img.size[1] else paste_any(img, L, x0, y0)
    if outline:
        d = ImageDraw.Draw(img)
        if ellipse:
            cx, cy, rx, ry = ellipse
            d.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), outline=outline, width=ow)
        else:
            d.line(list(pts) + [pts[0]], fill=outline, width=ow, joint="curve")


def paste_any(img, L, x0, y0):
    """alpha_composite that tolerates partially off-canvas layers"""
    W_, H_ = img.size
    cx0, cy0 = max(0, -x0), max(0, -y0)
    cx1, cy1 = min(L.size[0], W_ - x0), min(L.size[1], H_ - y0)
    if cx1 <= cx0 or cy1 <= cy0:
        return
    img.alpha_composite(L.crop((cx0, cy0, cx1, cy1)), (x0 + cx0, y0 + cy0))


def stroke_path(img, pts, col, width, closed=False, blur=0.0):
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    P = list(pts) + ([pts[0]] if closed else [])
    d.line(P, fill=col, width=int(width), joint="curve")
    r = width / 2
    for p in (P[0], P[-1]):
        d.ellipse((p[0] - r, p[1] - r, p[0] + r, p[1] + r), fill=col)
    if blur:
        lay = lay.filter(ImageFilter.GaussianBlur(blur))
    img.alpha_composite(lay)


def tube(img, pts, col, width, light=(-0.5, -0.7), hi=0.4, lo=0.5, outline=None, taper=None):
    """shaded tube along a path (vessels, intestines, limbs): built from dark->light offset strokes"""
    P = catmull(pts, closed=False, n=10) if len(pts) > 2 else pts
    base = np.array(col, np.float32)
    dark = tuple(int(c) for c in base * (1 - lo) + np.array((10, 12, 30)) * lo)
    light_c = tuple(int(c) for c in base * (1 - hi) + 255 * hi)
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    if outline:
        d.line(P, fill=outline, width=int(width + 6), joint="curve")
        for p in (P[0], P[-1]):
            r = (width + 6) / 2
            d.ellipse((p[0] - r, p[1] - r, p[0] + r, p[1] + r), fill=outline)
    for k, (c, wk, off) in enumerate(((dark, 1.0, 0.0), (tuple(int(x) for x in base), 0.72, -0.1), (light_c, 0.28, -0.24))):
        ox, oy = light[0] * width * -off * -1, light[1] * width * -off * -1
        Q = [(x + ox, y + oy) for x, y in P]
        d.line(Q, fill=c + (255,), width=max(1, int(width * wk)), joint="curve")
        r = width * wk / 2
        for p in (Q[0], Q[-1]):
            d.ellipse((p[0] - r, p[1] - r, p[0] + r, p[1] + r), fill=c + (255,))
    img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(max(0.6, width * 0.06))))


# ------------------------------------------------------------------ glows, gradients
def radial_layer(size, cx, cy, r, col, a=1.0, power=1.6):
    w, h = size
    x0, y0 = int(max(0, cx - r)), int(max(0, cy - r))
    x1, y1 = int(min(w, cx + r)), int(min(h, cy + r))
    lay = Image.new("RGBA", size, (0, 0, 0, 0))
    if x1 <= x0 or y1 <= y0:
        return lay
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
    d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / r
    al = (np.clip(1 - d, 0, 1) ** power) * 255 * a
    arr = np.zeros((y1 - y0, x1 - x0, 4), np.uint8)
    arr[..., 0], arr[..., 1], arr[..., 2] = col
    arr[..., 3] = al.astype(np.uint8)
    lay.paste(Image.fromarray(arr, "RGBA"), (x0, y0))
    return lay


def glow(img, cx, cy, r, col, a=1.0, power=1.6):
    img.alpha_composite(radial_layer(img.size, cx, cy, r, col, a, power))


def vgrad(size, top, bot):
    w, h = size
    rows = np.linspace(0, 1, h, dtype=np.float32)[:, None]
    col = np.array(top, np.float32) * (1 - rows) + np.array(bot, np.float32) * rows
    arr = np.broadcast_to(col[:, None, :], (h, w, 3)).astype(np.uint8)
    return Image.fromarray(np.ascontiguousarray(arr), "RGB").convert("RGBA")


_cache = {}


def vignette(k=0.6, cy=0.45):
    key = ("vig", round(k, 2), cy)
    if key not in _cache:
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 * 0.95 + ((yy - H * cy) / (H / 2)) ** 2 * 0.8)
        a = np.clip((r - 0.55) / 0.7, 0, 1) ** 1.5 * 255 * k
        arr = np.zeros((H, W, 4), np.uint8)
        arr[..., 3] = a.astype(np.uint8)
        _cache[key] = Image.fromarray(arr, "RGBA")
    return _cache[key]


def grain(img, t, k=10):
    key = ("grain", int(t * FPS) % 6)
    if key not in _cache:
        rng = np.random.default_rng(int(t * FPS) % 6 + 3)
        n = rng.normal(0, 1, (H // 2, W // 2)).astype(np.float32)
        n = np.kron(n, np.ones((2, 2), np.float32))
        _cache[key] = n
    n = _cache[key]
    a = np.asarray(img.convert("RGB")).astype(np.float32)
    a += n[..., None] * k
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGB").convert("RGBA")


# ------------------------------------------------------------------ particles
def bokeh(img, t, n=24, col=(200, 40, 50), seed=1, speed=(0, -20), rmin=6, rmax=40, alpha=0.5, blur=True, area=(0, 0, W, H), cells=False):
    """drifting out-of-focus discs (blood cells, dust). cells=True draws red blood cell discs with a dimple"""
    rng = np.random.default_rng(seed)
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    x0, y0, x1, y1 = area
    for i in range(n):
        r = rng.uniform(rmin, rmax)
        depth = (r - rmin) / max(rmax - rmin, 1)
        x = (rng.uniform(x0, x1) + speed[0] * t * (0.4 + depth)) % (x1 - x0 + 2 * rmax) + x0 - rmax
        y = (rng.uniform(y0, y1) + speed[1] * t * (0.4 + depth)) % (y1 - y0 + 2 * rmax) + y0 - rmax
        x += 8 * math.sin(t * 0.7 + i)
        a = int(255 * alpha * (0.35 + 0.65 * (1 - abs(depth - 0.5) * 1.6)))
        if cells:
            ang = rng.uniform(0, math.pi) + t * rng.uniform(-0.6, 0.6)
            sx = abs(math.cos(ang)) * 0.75 + 0.25
            d.ellipse((x - r * sx, y - r, x + r * sx, y + r), fill=mixc(col, (90, 0, 10), 0.2) + (a,))
            d.ellipse((x - r * sx * 0.55, y - r * 0.55, x + r * sx * 0.55, y + r * 0.55), fill=mixc(col, (60, 0, 8), 0.45) + (a,))
            d.ellipse((x - r * sx * 0.8, y - r * 0.85, x - r * sx * 0.1, y - r * 0.3), fill=mixc(col, (255, 200, 200), 0.35) + (a // 2,))
        else:
            d.ellipse((x - r, y - r, x + r, y + r), fill=col + (a,))
    if blur:
        lay = lay.filter(ImageFilter.GaussianBlur(3))
    img.alpha_composite(lay)


def rain(img, t, n=70, col=(190, 210, 230), seed=3, ang=0.25, alpha=0.35, length=60):
    rng = np.random.default_rng(seed)
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for i in range(n):
        sp = rng.uniform(1400, 2400)
        x = (rng.uniform(0, W) + t * sp * ang) % W
        y = (rng.uniform(0, H) + t * sp) % (H + 200) - 100
        L = length * rng.uniform(0.6, 1.4)
        d.line((x, y, x - L * ang, y - L), fill=col + (int(255 * alpha * rng.uniform(0.4, 1)),), width=2)
    img.alpha_composite(lay)


def dust(img, t, n=40, seed=5, alpha=0.4, col=(220, 230, 255)):
    rng = np.random.default_rng(seed)
    d = ImageDraw.Draw(img)
    for i in range(n):
        x = (rng.uniform(0, W) + 12 * t * rng.uniform(-1, 1)) % W
        y = (rng.uniform(0, H) - 18 * t * rng.uniform(0.3, 1)) % H
        r = rng.uniform(1, 3)
        a = int(255 * alpha * (0.5 + 0.5 * math.sin(t * rng.uniform(1, 3) + i)))
        d.ellipse((x - r, y - r, x + r, y + r), fill=col + (a,))


# ------------------------------------------------------------------ typography
RED = (226, 30, 44)
YEL = (255, 204, 40)
WHITE = (255, 255, 255)


def text_w(f, s):
    return f.getlength(s)


def fit_font(name, size, lines, maxw, minsize=40):
    f = font(name, size)
    while max(f.getlength(l) for l in lines) > maxw and f.size > minsize:
        f = font(name, f.size - 4)
    return f


def rich_line(d, x, y, parts, f, stroke=8, shadow=True, alpha=255):
    """parts: [(text, style)] style in {'w','r','box','y'}: white, red text, white on red box, yellow"""
    for txt, st in parts:
        w = f.getlength(txt)
        if st == "box":
            pad = f.size * 0.16
            d.rectangle((x - pad, y + f.size * 0.04, x + w + pad, y + f.size * 1.12), fill=RED + (alpha,))
            d.text((x, y), txt, font=f, fill=WHITE + (alpha,), stroke_width=max(2, stroke // 2), stroke_fill=(0, 0, 0, alpha))
        else:
            col = {"w": WHITE, "r": (240, 34, 48), "y": YEL, "c": (110, 210, 255)}.get(st, WHITE)
            d.text((x, y), txt, font=f, fill=col + (alpha,), stroke_width=stroke, stroke_fill=(0, 0, 0, alpha))
        x += w


def parse_rich(s):
    """'ПУЛЬС [170]' -> red word; '{ВОДОВОРОТ}' -> red box; '<КИСЛОРОД>' -> yellow"""
    parts = []
    cur, st = "", "w"
    for ch in s:
        if ch in "[{<":
            if cur:
                parts.append((cur, st))
            cur, st = "", {"[": "r", "{": "box", "<": "y"}[ch]
        elif ch in "]}>":
            if cur:
                parts.append((cur, st))
            cur, st = "", "w"
        else:
            cur += ch
    if cur:
        parts.append((cur, st))
    return parts


def title_block(img, lines, y, t_rel, size=92, maxw=940, first=False, name=TITLE, stroke=9, anim="pop"):
    """lines: list of rich strings. Animated pop-in (scale + fade) per line."""
    if not lines:
        return y
    plain = [''.join(p[0] for p in parse_rich(l)) for l in lines]
    f = fit_font(name, size, plain, maxw)
    for i, (l, pl) in enumerate(zip(lines, plain)):
        tr = t_rel - i * 0.08
        k = 1.0 if first else ease(tr / 0.22)
        if k <= 0:
            y += f.size * 1.08
            continue
        sc = 1.0 if first else (1.0 + 0.35 * (1 - ease(tr / 0.18)))
        ff = font(name, f.size * sc) if sc != 1.0 else f
        w = ff.getlength(pl)
        lay = Image.new("RGBA", (int(w + 80), int(ff.size * 1.5)), (0, 0, 0, 0))
        dl = ImageDraw.Draw(lay)
        rich_line(dl, 40, 8, parse_rich(l), ff, stroke=stroke)
        if k < 1:
            lay.putalpha(lay.getchannel("A").point(lambda a: int(a * k)))
        sh = lay.copy()
        sha = np.asarray(sh.getchannel("A")).astype(np.float32) * 0.55
        sh = Image.fromarray(np.dstack([np.zeros_like(sha)] * 3 + [sha]).astype(np.uint8), "RGBA").filter(ImageFilter.GaussianBlur(6))
        x = int(540 - lay.size[0] / 2)
        yy = int(y - (ff.size - f.size) / 2)
        img.alpha_composite(sh, (x + 4, yy + 8)) if x >= 0 else paste_any(img, sh, x + 4, yy + 8)
        img.alpha_composite(lay, (x, yy)) if x >= 0 else paste_any(img, lay, x, yy)
        y += f.size * 1.08
    return y


def sub_line(img, txt, y, t_rel, col=(120, 205, 255), size=44, first=False):
    if not txt:
        return y
    a = 1.0 if first else ease((t_rel - 0.25) / 0.25)
    if a <= 0:
        return y + size * 1.3
    f = fit_font(BODY, size, [txt], 940, 24)
    d = ImageDraw.Draw(img)
    w = f.getlength(txt)
    d.text((540 - w / 2, y), txt, font=f, fill=col + (int(255 * a),), stroke_width=5, stroke_fill=(0, 0, 0, int(230 * a)))
    return y + f.size * 1.3


def label(img, x, y, txt, col=(255, 70, 80), size=30, anchor="l", a=1.0, name=BODY, stroke=4):
    f = font(name, size)
    d = ImageDraw.Draw(img)
    w = f.getlength(txt)
    if anchor == "c":
        x -= w / 2
    elif anchor == "r":
        x -= w
    d.text((x, y), txt, font=f, fill=col + (int(255 * a),), stroke_width=stroke, stroke_fill=(0, 0, 0, int(220 * a)))
    return w


def callout(img, p, l, txt, k, col=(255, 255, 255), size=30):
    """thin leader line from point p to label point l with a dot; k = 0..1 reveal"""
    if k <= 0:
        return
    d = ImageDraw.Draw(img)
    ex, ey = lerp(p[0], l[0], ease(k)), lerp(p[1], l[1], ease(k))
    d.line((p[0], p[1], ex, ey), fill=col + (230,), width=3)
    d.ellipse((p[0] - 8, p[1] - 8, p[0] + 8, p[1] + 8), fill=col + (255,), outline=(0, 0, 0, 200), width=2)
    if k > 0.7:
        a = ease((k - 0.7) / 0.3)
        f = font(BODY, size)
        w = f.getlength(txt)
        x = l[0] + 10 if l[0] >= p[0] else l[0] - 10 - w
        x = min(max(x, 30), 950 - w)
        label(img, x, l[1] - size * 0.65, txt, col=col, size=size, a=a)
