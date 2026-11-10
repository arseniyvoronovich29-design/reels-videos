"""Big expressive cartoon hero (bust + optional arms) with soft 3D-ish shading.
draw_hero(img, cx, cy, s, p, t): (cx, cy) = head centre, s = head radius in px.
p keys (all optional):
  skin (rgb), pale 0..1, blue 0..1 (hypoxia), flush 0..1, bags 0..1, sweat 0..1, tears 0..1
  hair (rgb), outfit 'tshirt'|'hoodie'|'gown'|'jacket', shirt (rgb)
  eyes: open 0..1.3, pupil 0..1, look (dx, dy), red 0..1, closed bool, lid (droop 0..1), squint
  brows 'neutral'|'worried'|'angry'|'raised'|'pain', mouth 'neutral'|'worried'|'scream'|'gasp'|'grit'|'smile'|'slack'|'open'
  mopen 0..1, tilt (radians), arms None|'belly'|'up'|'chest'|'throat'|'head'|'down', shake 0..1
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from gfx import shade, catmull, ellipse_pts, glow, mixc, lerp, tube, stroke_path, clamp

SKIN = (236, 184, 150)
HAIR = (70, 44, 30)
OUT = (34, 20, 22)

HEAD = [(0, -1.06), (0.5, -0.98), (0.84, -0.7), (0.96, -0.25), (0.95, 0.12), (0.86, 0.45), (0.66, 0.78), (0.36, 0.99), (0, 1.07),
        (-0.36, 0.99), (-0.66, 0.78), (-0.86, 0.45), (-0.95, 0.12), (-0.96, -0.25), (-0.84, -0.7), (-0.5, -0.98)]
HAIR_PTS = [(-0.98, -0.05), (-1.05, -0.55), (-0.88, -1.0), (-0.45, -1.3), (0.1, -1.36), (0.6, -1.22), (0.95, -0.86), (1.04, -0.35), (0.97, 0.0),
            (0.86, -0.45), (0.55, -0.56), (0.28, -0.47), (0.0, -0.55), (-0.3, -0.45), (-0.6, -0.56), (-0.84, -0.44)]


def _skin(p):
    s = p.get("skin", SKIN)
    s = mixc(s, (214, 212, 216), p.get("pale", 0) * 0.7)
    s = mixc(s, (150, 168, 196), p.get("blue", 0) * 0.6)
    s = mixc(s, (240, 130, 110), p.get("flush", 0) * 0.35)
    return s


def _rot(pts, cx, cy, a):
    if not a:
        return pts
    ca, sa = math.cos(a), math.sin(a)
    return [(cx + (x - cx) * ca - (y - cy) * sa, cy + (x - cx) * sa + (y - cy) * ca) for x, y in pts]


def draw_body(img, cx, cy, s, p, t):
    shirt = p.get("shirt", (40, 52, 78))
    outfit = p.get("outfit", "tshirt")
    br = 1 + 0.012 * math.sin(t * 2.4) * (1 + 2 * p.get("pant", 0))
    S = lambda x, y: (cx + x * s, cy + y * s * (br if y > 1.2 else 1))
    skin = _skin(p)
    # neck
    shade(img, [S(-0.36, 0.6), S(0.36, 0.6), S(0.4, 1.45), S(-0.4, 1.45)], mixc(skin, (150, 80, 70), 0.18), hi=0.15, lo=0.5, inner=0.6)
    # torso
    torso = catmull([S(-1.95, 5.6), S(-1.95, 4.4), S(-1.93, 3.4), S(-1.9, 2.6), S(-1.78, 1.75), S(-1.45, 1.38), S(-0.8, 1.2), S(0, 1.16), S(0.8, 1.2), S(1.45, 1.38), S(1.78, 1.75), S(1.9, 2.6), S(1.93, 3.4), S(1.95, 4.4), S(1.95, 5.6), S(0, 5.7)], closed=True, n=6)
    if outfit == "gown":
        shirt = (150, 186, 206)
    shade(img, torso, shirt, light=(-0.7, -0.35), hi=0.16, lo=0.5, inner=0.7, rim=0.35, rim_col=(120, 170, 255), outline=OUT + (255,), ow=max(2, int(s * 0.02)))
    d = ImageDraw.Draw(img)
    dark = mixc(shirt, (0, 0, 10), 0.4)
    # folds
    for a, b in (((-1.25, 1.9), (-1.05, 2.9)), ((1.25, 1.9), (1.0, 3.0)), ((-0.35, 2.6), (-0.15, 3.6)), ((0.5, 2.2), (0.35, 3.0))):
        stroke_path(img, [S(*a), S(*b)], dark + (120,), max(2, s * 0.03), blur=2)
    if outfit == "hoodie":
        hood = catmull([S(-1.15, 1.2), S(-0.8, 0.95), S(0, 0.92), S(0.8, 0.95), S(1.15, 1.2), S(0.6, 1.5), S(0, 1.55), S(-0.6, 1.5)], n=6)
        shade(img, hood, mixc(shirt, (255, 255, 255), 0.08), hi=0.25, lo=0.5, inner=0.6, outline=OUT + (255,), ow=max(2, int(s * 0.02)))
        for side in (-1, 1):
            stroke_path(img, [S(0.22 * side, 1.5), S(0.26 * side, 2.2)], (230, 230, 235, 255), max(2, s * 0.035))
            d.ellipse(_box(S(0.26 * side, 2.24), s * 0.04), fill=(200, 200, 205, 255))
    elif outfit == "gown":
        for k in range(14):
            x, y = -1.6 + (k % 7) * 0.5, 1.8 + (k // 7) * 0.7
            d.ellipse(_box(S(x, y), s * 0.04), fill=(110, 150, 180, 160))
        shade(img, catmull([S(-0.62, 1.16), S(0, 1.5), S(0.62, 1.16), S(0, 1.3)], n=6), mixc(shirt, (255, 255, 255), 0.15), hi=0.2, lo=0.3, inner=0.3)
    elif outfit == "jacket":
        stroke_path(img, [S(0, 1.3), S(0, 4.4)], (20, 20, 24, 255), max(2, s * 0.04))
        for side in (-1, 1):
            shade(img, [S(0.05 * side, 1.25), S(0.62 * side, 1.18), S(0.5 * side, 2.0)], mixc(shirt, (255, 255, 255), 0.1), hi=0.2, lo=0.4, inner=0.4)
    else:
        neck = catmull([S(-0.55, 1.16), S(0, 1.42), S(0.55, 1.16), S(0, 1.32)], n=6)
        shade(img, neck, mixc(shirt, (0, 0, 0), 0.25), hi=0.1, lo=0.2, inner=0.3)


def _box(c, r):
    return (c[0] - r, c[1] - r, c[0] + r, c[1] + r)


def hand(img, cx, cy, s, ang, skin, spread=0.0, fist=False):
    """mitten-ish cartoon hand at (cx, cy), pointing along ang (radians)"""
    ca, sa = math.cos(ang), math.sin(ang)
    R = lambda x, y: (cx + (x * ca - y * sa) * s, cy + (x * sa + y * ca) * s)
    palm = catmull([R(-0.05, -0.22), R(0.28, -0.24), R(0.36, 0.0), R(0.28, 0.24), R(-0.05, 0.22), R(-0.12, 0.0)], n=6)
    shade(img, palm, skin, hi=0.25, lo=0.45, inner=0.5, outline=OUT + (255,), ow=max(2, int(s * 0.03)))
    if not fist:
        for k in range(4):
            off = (k - 1.5) * 0.12
            a2 = off * (1.2 + 2.2 * spread)
            L = 0.34 if k in (1, 2) else 0.28
            x0, y0 = 0.3, off * 0.9
            x1, y1 = x0 + L * math.cos(a2), y0 + L * math.sin(a2) + off * spread * 0.4
            tube(img, [R(x0, y0), R(x1, y1)], skin, s * 0.13, hi=0.3, lo=0.4, outline=OUT + (255,))
    tube(img, [R(0.05, 0.2), R(0.25, 0.42)], skin, s * 0.14, hi=0.3, lo=0.4, outline=OUT + (255,))


def draw_arms(img, cx, cy, s, p, t):
    arms = p.get("arms")
    if not arms:
        return
    shirt = p.get("shirt", (40, 52, 78))
    if p.get("outfit") == "gown":
        shirt = (150, 186, 206)
    skin = _skin(p)
    S = lambda x, y: (cx + x * s, cy + y * s)
    sh = 0.03 * math.sin(t * 20) * p.get("shake", 0)
    if arms == "up":
        for side in (-1, 1):
            w = 0.06 * math.sin(t * 9 + side)
            tube(img, [S(1.5 * side, 1.55), S(1.95 * side, 0.55 + w), S(1.95 * side, -0.35 + w)], shirt, s * 0.62, outline=OUT + (255,))
            tube(img, [S(1.95 * side, -0.3 + w), S(1.98 * side, -0.7 + w)], skin, s * 0.36, outline=OUT + (255,))
            hand(img, *S(2.0 * side, -0.82 + w), s * 1.0, -math.pi / 2 - 0.3 * side, skin, spread=0.9)
    elif arms == "belly":
        for side in (-1, 1):
            tube(img, [S(1.62 * side, 1.7), S(1.75 * side, 2.9), S(0.75 * side, 3.05 + sh)], shirt, s * 0.6, outline=OUT + (255,))
            hand(img, *S(0.55 * side, 3.0 + sh), s * 0.95, (math.pi if side > 0 else 0.0) - 0.25 * side, skin, fist=False)
    elif arms == "chest":
        tube(img, [S(1.62, 1.7), S(1.72, 2.9), S(0.65, 2.3 + sh)], shirt, s * 0.6, outline=OUT + (255,))
        hand(img, *S(0.4, 2.25 + sh), s * 0.9, math.pi + 0.5, skin)
    elif arms == "throat":
        for side in (-1, 1):
            tube(img, [S(1.62 * side, 1.7), S(1.5 * side, 2.6), S(0.55 * side, 1.65 + sh)], shirt, s * 0.58, outline=OUT + (255,))
            hand(img, *S(0.38 * side, 1.4 + sh), s * 0.85, (math.pi if side > 0 else 0.0) - 0.9 * side, skin)
    elif arms == "head":
        for side in (-1, 1):
            tube(img, [S(1.62 * side, 1.7), S(1.9 * side, 0.8), S(1.15 * side, 0.1 + sh)], shirt, s * 0.58, outline=OUT + (255,))
            hand(img, *S(1.0 * side, -0.05 + sh), s * 0.85, -math.pi / 2 + 0.6 * side * -1 + (math.pi if side < 0 else 0) * 0, skin)
    elif arms == "phone":
        tube(img, [S(1.62, 1.7), S(1.7, 1.0), S(1.05, 0.45)], shirt, s * 0.58, outline=OUT + (255,))
        d = ImageDraw.Draw(img)
        shade(img, [S(0.78, -0.25), S(1.08, -0.3), S(1.18, 0.6), S(0.88, 0.65)], (30, 30, 36), hi=0.2, lo=0.3, inner=0.2, outline=OUT + (255,), ow=2)
        hand(img, *S(1.0, 0.45), s * 0.8, -math.pi / 2 - 0.3, skin, fist=True)


def draw_head(img, cx, cy, s, p, t):
    skin = _skin(p)
    a = p.get("tilt", 0.0) + 0.04 * math.sin(t * 23) * p.get("shake", 0)
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    S = lambda x, y: (cx + x * s, cy + y * s)
    ow = max(2, int(s * 0.022))
    # ears
    for side in (-1, 1):
        shade(lay, None, skin, ellipse=(cx + 0.92 * side * s, cy + 0.08 * s, 0.15 * s, 0.24 * s), hi=0.2, lo=0.45, inner=0.5, outline=OUT + (255,), ow=ow)
        shade(lay, None, mixc(skin, (170, 90, 80), 0.35), ellipse=(cx + 0.93 * side * s, cy + 0.09 * s, 0.07 * s, 0.13 * s), hi=0.0, lo=0.2, inner=0.3)
    head = catmull([S(x, y) for x, y in HEAD], n=8)
    shade(lay, head, skin, light=(-0.55, -0.6), hi=0.22, lo=0.42, inner=0.45, rim=0.25, rim_col=(140, 190, 255), outline=OUT + (255,), ow=ow,
          spec=0.12, spec_at=(0.32, 0.22), spec_r=0.22)
    # under-eye bags / cheeks
    for side in (-1, 1):
        lay.alpha_composite(_soft_ellipse(lay.size, cx + 0.5 * side * s, cy + 0.42 * s, 0.2 * s, 0.13 * s, (230, 110, 100), 0.35 + 0.4 * p.get("flush", 0)))
        if p.get("bags", 0):
            lay.alpha_composite(_soft_ellipse(lay.size, cx + 0.36 * side * s, cy + 0.17 * s, 0.2 * s, 0.07 * s, (90, 60, 110), 0.5 * p["bags"]))
    _eyes(lay, cx, cy, s, p, t, skin)
    _brows(lay, cx, cy, s, p)
    # nose
    nose = catmull([S(0.02, 0.12), S(0.12, 0.34), S(0.1, 0.42), S(-0.02, 0.44), S(-0.1, 0.4)], closed=False, n=6)
    stroke_path(lay, nose, mixc(skin, (120, 60, 50), 0.45) + (200,), max(2, s * 0.03), blur=1)
    lay.alpha_composite(_soft_ellipse(lay.size, cx - 0.03 * s, cy + 0.33 * s, 0.07 * s, 0.05 * s, (255, 240, 230), 0.5))
    _mouth(lay, cx, cy, s, p, t, skin)
    _hair(lay, cx, cy, s, p)
    if a:
        lay = lay.rotate(-math.degrees(a), center=(cx, cy + 0.9 * s), resample=Image.BICUBIC)
    img.alpha_composite(lay)
    return a


def _soft_ellipse(size, cx, cy, rx, ry, col, a):
    lay = Image.new("RGBA", size, (0, 0, 0, 0))
    r = max(rx, ry)
    x0, y0 = int(cx - rx * 1.6), int(cy - ry * 1.6)
    w, h = int(rx * 3.2) + 2, int(ry * 3.2) + 2
    sub = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(sub).ellipse((rx * 0.6, ry * 0.6, rx * 2.6, ry * 2.6), fill=col + (int(255 * min(1, a)),))
    sub = sub.filter(ImageFilter.GaussianBlur(max(1, r * 0.35)))
    from gfx import paste_any
    paste_any(lay, sub, x0, y0)
    return lay


def _hair(img, cx, cy, s, p):
    hc = p.get("hair", HAIR)
    pts = catmull([(cx + x * s, cy + y * s) for x, y in HAIR_PTS], n=6)
    shade(img, pts, hc, light=(-0.4, -0.9), hi=0.3, lo=0.5, inner=0.4, outline=OUT + (255,), ow=max(2, int(s * 0.022)), spec=0.18, spec_at=(0.35, 0.25), spec_r=0.2)
    for k in range(6):
        x = -0.6 + k * 0.24
        stroke_path(img, [(cx + x * s, cy - 1.1 * s), (cx + (x + 0.12) * s, cy - 0.75 * s)], mixc(hc, (255, 230, 200), 0.25) + (110,), max(2, s * 0.025), blur=1.5)


def _eyes(img, cx, cy, s, p, t, skin):
    op = p.get("open", 1.0)
    # blink every ~3.5 s
    bph = (t + p.get("blink_off", 0.0)) % 3.7
    if bph < 0.12 and not p.get("closed") and not p.get("no_blink"):
        op *= abs(bph - 0.06) / 0.06
    look = p.get("look", (0.0, 0.0))
    pup = p.get("pupil", 0.5)
    red = p.get("red", 0.0)
    terror = op > 1.05
    d = ImageDraw.Draw(img)
    for side in (-1, 1):
        ex, ey = cx + 0.36 * side * s, cy + 0.02 * s
        rx, ry = 0.235 * s, 0.165 * s * max(0.02, op)
        if p.get("closed") or op < 0.08:
            arc = [(ex + rx * math.cos(a_), ey + ry * 0.2 + 0.05 * s * math.sin(a_)) for a_ in np.linspace(0, math.pi, 16)]
            stroke_path(img, arc, OUT + (255,), max(2, s * 0.035))
            for k in range(3):
                a_ = 0.6 + k * 0.9
                x0, y0 = ex + rx * math.cos(a_), ey + 0.05 * s * math.sin(a_) + ry * 0.2
                stroke_path(img, [(x0, y0), (x0 + 0.03 * s * math.cos(a_), y0 + 0.06 * s)], OUT + (255,), max(1, s * 0.015))
            continue
        top = [(ex + rx * math.cos(a_), ey - ry * 1.15 * math.sin(a_) ** 0.8) for a_ in np.linspace(0, math.pi, 20)]
        bot = [(ex + rx * math.cos(a_), ey + ry * 0.9 * math.sin(a_) ** 0.9) for a_ in np.linspace(math.pi, 0, 20)]
        eye = top + bot[1:-1]
        shade(img, eye, mixc((250, 248, 244), (240, 160, 160), red * 0.7), light=(0, -1), hi=0.0, lo=0.35, inner=0.6)
        # veins
        if red > 0.2:
            for k in range(4):
                x0 = ex + side * rx * (0.95 - 0.05 * k)
                stroke_path(img, [(x0, ey + (k - 1.5) * 0.04 * s), (x0 - side * 0.1 * s, ey + (k - 1.5) * 0.02 * s)], (210, 40, 50, int(200 * red)), max(1, s * 0.012))
        ir = (0.125 if not terror else 0.09) * s
        ix, iy = ex + look[0] * 0.08 * s, ey + look[1] * 0.06 * s + (0.01 * s if terror else 0)
        if p.get("eyes_roll"):
            iy -= 0.12 * s
        clip_m = Image.new("L", img.size, 0)
        ImageDraw.Draw(clip_m).polygon(eye, fill=255)
        il = Image.new("RGBA", img.size, (0, 0, 0, 0))
        iris_c = p.get("iris", (96, 62, 40))
        shade(il, None, iris_c, ellipse=(ix, iy, ir, ir), light=(0.3, 0.8), hi=0.35, lo=0.45, inner=0.5, outline=(20, 12, 10, 255), ow=max(1, int(s * 0.012)))
        pr = ir * lerp(0.35, 0.78, pup)
        ImageDraw.Draw(il).ellipse(_box((ix, iy), pr), fill=(8, 6, 8, 255))
        ImageDraw.Draw(il).ellipse(_box((ix - ir * 0.38, iy - ir * 0.4), ir * 0.26), fill=(255, 255, 255, 240))
        ImageDraw.Draw(il).ellipse(_box((ix + ir * 0.35, iy + ir * 0.3), ir * 0.11), fill=(255, 255, 255, 200))
        il.putalpha(Image.fromarray(np.minimum(np.asarray(il.getchannel("A")), np.asarray(clip_m)), "L"))
        img.alpha_composite(il)
        # lids
        lid = p.get("lid", 0.0)
        if lid > 0:
            ly = ey - ry * 1.15 + lid * ry * 2.0
            lpoly = [(ex - rx * 1.1, ey - ry * 1.6)] + [(ex + rx * math.cos(a_) * 1.05, ly + 0.03 * s * math.sin(a_)) for a_ in np.linspace(math.pi, 0, 14)] + [(ex + rx * 1.1, ey - ry * 1.6)]
            shade(img, lpoly, mixc(skin, (150, 90, 80), 0.15), hi=0.1, lo=0.3, inner=0.2)
            stroke_path(img, [(ex + rx * math.cos(a_) * 1.05, ly + 0.03 * s * math.sin(a_)) for a_ in np.linspace(math.pi, 0, 14)], OUT + (255,), max(2, s * 0.035))
        else:
            stroke_path(img, top, OUT + (255,), max(2, s * (0.038 if not terror else 0.03)))
        stroke_path(img, bot[3:-3], mixc(skin, (110, 50, 50), 0.5) + (180,), max(1, s * 0.015))


def _brows(img, cx, cy, s, p):
    kind = p.get("brows", "neutral")
    hc = mixc(p.get("hair", HAIR), (0, 0, 0), 0.25)
    for side in (-1, 1):
        inner, outer = 0.0, 0.0
        if kind == "worried":
            inner, outer = -0.12, 0.03
        elif kind == "angry":
            inner, outer = 0.08, -0.06
        elif kind == "raised":
            inner, outer = -0.12, -0.1
        elif kind == "pain":
            inner, outer = -0.06, 0.06
        y = -0.26 + 0.02 * math.sin(0)
        a = (cx + side * 0.14 * s, cy + (y + inner) * s)
        m = (cx + side * 0.36 * s, cy + (y - 0.05 + (inner + outer) / 2) * s)
        b = (cx + side * 0.58 * s, cy + (y + 0.02 + outer) * s)
        tube(img, [a, m, b], hc, s * 0.075, hi=0.15, lo=0.2)


def _mouth(img, cx, cy, s, p, t, skin):
    kind = p.get("mouth", "neutral")
    mo = p.get("mopen", 1.0)
    mx, my = cx, cy + 0.62 * s
    lipc = mixc(skin, (170, 70, 70), 0.45)
    if kind in ("scream", "open", "gasp", "slack"):
        if kind == "scream":
            rx, ry = 0.3 * s, 0.26 * s * mo * (1 + 0.06 * math.sin(t * 30))
            my += 0.06 * s
        elif kind == "gasp":
            rx, ry = 0.13 * s, 0.17 * s * mo
            my += 0.04 * s
        elif kind == "slack":
            rx, ry = 0.17 * s, 0.07 * s * mo
        else:
            rx, ry = 0.22 * s, 0.14 * s * mo
        pts = catmull([(mx - rx, my - ry * 0.2), (mx - rx * 0.6, my - ry), (mx, my - ry * 1.05), (mx + rx * 0.6, my - ry), (mx + rx, my - ry * 0.2),
                       (mx + rx * 0.7, my + ry * 0.8), (mx, my + ry * 1.05), (mx - rx * 0.7, my + ry * 0.8)], n=6)
        shade(img, pts, (70, 14, 24), light=(0, -1), hi=0.0, lo=0.4, inner=0.6, outline=mixc(lipc, (60, 20, 20), 0.4) + (255,), ow=max(2, int(s * 0.03)))
        clip = Image.new("L", img.size, 0)
        ImageDraw.Draw(clip).polygon(pts, fill=255)
        inner = Image.new("RGBA", img.size, (0, 0, 0, 0))
        di = ImageDraw.Draw(inner)
        if ry > 0.06 * s:
            di.ellipse((mx - rx * 0.7, my + ry * 0.2, mx + rx * 0.7, my + ry * 1.4), fill=(214, 86, 96, 255))
            di.rectangle((mx - rx, my - ry * 1.2, mx + rx, my - ry * (0.62 if kind != "gasp" else 0.8)), fill=(248, 246, 240, 255))
            if kind == "scream":
                di.rectangle((mx - rx * 0.6, my + ry * 0.82, mx + rx * 0.6, my + ry * 1.2), fill=(240, 238, 232, 255))
        inner.putalpha(Image.fromarray(np.minimum(np.asarray(inner.getchannel("A")), np.asarray(clip)), "L"))
        img.alpha_composite(inner)
    elif kind == "grit":
        rx, ry = 0.28 * s, 0.1 * s
        pts = [(mx - rx, my - ry), (mx + rx, my - ry), (mx + rx * 0.9, my + ry), (mx - rx * 0.9, my + ry)]
        shade(img, pts, (246, 244, 236), hi=0.0, lo=0.2, inner=0.3, outline=mixc(lipc, (60, 20, 20), 0.4) + (255,), ow=max(2, int(s * 0.03)))
        d = ImageDraw.Draw(img)
        d.line((mx - rx, my, mx + rx, my), fill=(120, 110, 110, 255), width=max(1, int(s * 0.012)))
        for k in range(-3, 4):
            d.line((mx + k * rx / 4, my - ry, mx + k * rx / 4, my + ry), fill=(150, 140, 140, 255), width=max(1, int(s * 0.01)))
    elif kind == "smile":
        arc = [(mx + 0.24 * s * math.cos(a_), my - 0.04 * s + 0.12 * s * math.sin(a_)) for a_ in np.linspace(0.2, math.pi - 0.2, 16)]
        stroke_path(img, arc, OUT + (255,), max(2, s * 0.035))
    else:
        down = 0.06 if kind == "worried" else 0.0
        arc = [(mx + 0.18 * s * math.cos(a_), my + 0.02 * s - down * s * math.sin(a_) + 0.01 * s) for a_ in np.linspace(0.15, math.pi - 0.15, 14)]
        stroke_path(img, arc, mixc(lipc, (60, 20, 20), 0.5) + (255,), max(2, s * 0.03))


def draw_fx(img, cx, cy, s, p, t, a=0.0):
    """dynamic sweat / tears drawn per frame on top of cached hero"""
    d = ImageDraw.Draw(img)
    sw = p.get("sweat", 0)
    if sw:
        rng = np.random.default_rng(4)
        for k in range(int(7 * sw)):
            x = cx + rng.uniform(-0.75, 0.75) * s
            y0 = cy + rng.uniform(-0.75, -0.3) * s
            y = y0 + ((t * 0.12 + k * 0.17) % 1.0) * 0.5 * s
            r = s * rng.uniform(0.035, 0.055)
            shade(img, [(x, y - r * 1.8), (x + r, y), (x + r * 0.7, y + r * 0.8), (x - r * 0.7, y + r * 0.8), (x - r, y)], (200, 225, 245), hi=0.5, lo=0.2, inner=0.2, alpha=0.85)
            d.ellipse(_box((x - r * 0.3, y - r * 0.1), r * 0.25), fill=(255, 255, 255, 230))
    te = p.get("tears", 0)
    if te:
        for side in (-1, 1):
            x = cx + 0.3 * side * s
            y0 = cy + 0.13 * s
            L = (0.25 + 0.5 * te) * s
            stroke_path(img, [(x, y0), (x + 0.03 * side * s, y0 + L * 0.5), (x + 0.02 * side * s, y0 + L)], (190, 220, 250, int(170 * te)), max(2, s * 0.05), blur=1)
            stroke_path(img, [(x - 0.01 * s, y0), (x + 0.02 * side * s, y0 + L)], (255, 255, 255, int(150 * te)), max(1, s * 0.015))
            ph = (t * 0.6 + (0.5 if side > 0 else 0)) % 1
            yy = y0 + L + ph * 0.3 * s
            r = 0.04 * s
            d.ellipse(_box((x + 0.02 * side * s, yy), r), fill=(200, 230, 255, int(220 * (1 - ph))))


def draw_hero(img, cx, cy, s, p, t):
    draw_body(img, cx, cy, s, p, t)
    if p.get("arms") in ("up",):
        draw_arms(img, cx, cy, s, p, t)
    a = draw_head(img, cx + 0.02 * s * math.sin(t * 1.3), cy, s, p, t)
    if p.get("arms") not in (None, "up", "down"):
        draw_arms(img, cx, cy, s, p, t)
    draw_fx(img, cx, cy, s, p, t, a)
