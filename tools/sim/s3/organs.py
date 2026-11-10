"""Shaded anatomy illustrations. Every function draws into img (RGBA, 1080x1920) around (cx, cy) with scale s (px)."""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from gfx import shade, tube, catmull, ellipse_pts, glow, mixc, lerp, stroke_path, bokeh, clamp, paste_any

OUTL = (40, 12, 18, 255)
LUNG = (232, 140, 150)
HEART = (196, 40, 52)
AORTA = (220, 50, 60)
VEIN = (70, 90, 200)
LIVER = (150, 50, 50)
GUT = (232, 160, 150)
COLON = (214, 150, 120)
BONE = (236, 226, 206)


def P(cx, cy, s):
    return lambda x, y: (cx + x * s, cy + y * s)


# ---------------------------------------------------------------- lungs + heart
def lungs(img, cx, cy, s, breath=1.0, dark=0.0, block=0.0, spots=0.0, t=0.0, heart_beat=0.0, show_heart=True, col=None):
    """front view of trachea, lungs and heart. block: right-lower area grey (no blood). spots: dark patches (water / damage)"""
    S = P(cx, cy, s)
    b = breath
    col = col or mixc(LUNG, (120, 110, 130), dark)
    # trachea
    tube(img, [S(0, -1.55), S(0, -0.55)], (236, 200, 196), s * 0.22, outline=OUTL)
    for k in range(7):
        y = -1.48 + k * 0.13
        stroke_path(img, [S(-0.1, y), S(0.1, y)], (200, 150, 150, 220), max(2, s * 0.025))
    tube(img, [S(0, -0.6), S(-0.32, -0.3), S(-0.5, 0.05)], (236, 200, 196), s * 0.15, outline=OUTL)
    tube(img, [S(0, -0.6), S(0.32, -0.3), S(0.5, 0.05)], (236, 200, 196), s * 0.15, outline=OUTL)
    for side in (-1, 1):
        pts = [(0.12, -1.0), (0.42, -1.12), (0.78, -0.8), (0.98, -0.1), (1.04, 0.55), (0.95, 0.98), (0.55, 1.05), (0.24, 0.85), (0.16, 0.25)]
        pts = [S(side * (x * (1 + 0.04 * (b - 1))), y * (1 + 0.05 * (b - 1))) for x, y in pts]
        poly = catmull(pts, n=8)
        shade(img, poly, col, light=(-0.6, -0.6), hi=0.3, lo=0.45, inner=0.6, rim=0.3, rim_col=(255, 190, 200), outline=OUTL, ow=max(2, int(s * 0.02)),
              spec=0.15, spec_at=(0.45 if side < 0 else 0.55, 0.25), spec_r=0.25)
        # bronchial tree
        lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        rng = np.random.default_rng(7 + side)

        def br(x, y, a, L, w, depth):
            if depth == 0 or w < 1:
                return
            x2, y2 = x + L * math.cos(a), y + L * math.sin(a)
            ImageDraw.Draw(lay).line((x, y, x2, y2), fill=(180, 80, 96, 200), width=int(w))
            for da in (-0.45, 0.45):
                br(x2, y2, a + da + rng.uniform(-0.2, 0.2), L * 0.72, w * 0.7, depth - 1)
        x0, y0 = S(side * 0.5, 0.05)
        br(x0, y0, math.pi / 2 + side * -0.35, s * 0.32, s * 0.06, 5)
        img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(1)))
        if spots > 0:
            rng = np.random.default_rng(3 + side)
            d = ImageDraw.Draw(img)
            for k in range(int(26 * spots)):
                x, y = rng.uniform(0.3, 0.9), rng.uniform(-0.6, 0.9)
                r = s * rng.uniform(0.03, 0.07)
                c = S(side * x, y)
                d.ellipse((c[0] - r, c[1] - r * 0.8, c[0] + r, c[1] + r * 0.8), fill=(70, 20, 30, 190))
        if block > 0 and side > 0:
            m = Image.new("L", img.size, 0)
            ImageDraw.Draw(m).polygon(poly, fill=255)
            g = Image.new("RGBA", img.size, (120, 124, 140, 0))
            ga = Image.new("L", img.size, 0)
            ImageDraw.Draw(ga).ellipse((*S(0.15, -0.1), *S(1.2, 1.2)), fill=int(220 * block))
            ga = ga.filter(ImageFilter.GaussianBlur(s * 0.12))
            from PIL import ImageChops
            g.putalpha(ImageChops.multiply(ga, m))
            img.alpha_composite(g)
    if show_heart:
        heart(img, cx + 0.12 * s, cy + 0.45 * s, s * 0.55, beat=heart_beat)


def heart(img, cx, cy, s, beat=0.0, vessels=True, pale=0.0):
    S = P(cx, cy, s)
    k = 1 + 0.06 * beat
    if vessels:
        tube(img, [S(0.15, -0.55), S(0.2, -1.25), S(-0.25, -1.45), S(-0.5, -1.2), S(-0.55, -0.6)], AORTA, s * 0.26, outline=OUTL)
        for x in (-0.15, 0.05, 0.25):
            tube(img, [S(x * 0.9 - 0.05, -1.35), S(x - 0.05, -1.9)], AORTA, s * 0.1, outline=OUTL)
        tube(img, [S(-0.2, -0.45), S(-0.15, -1.05), S(0.45, -1.15), S(0.85, -0.95)], VEIN, s * 0.22, outline=OUTL)
        tube(img, [S(-0.62, -0.1), S(-0.7, -1.5)], (80, 100, 210), s * 0.2, outline=OUTL)
    pts = [(0.0, -0.62), (0.45, -0.72), (0.8, -0.45), (0.85, 0.05), (0.55, 0.6), (0.05, 1.05), (-0.25, 0.75), (-0.62, 0.25), (-0.7, -0.25), (-0.45, -0.62)]
    poly = catmull([S(x * k, y * k) for x, y in pts], n=8)
    shade(img, poly, mixc(HEART, (150, 140, 150), pale), light=(-0.6, -0.6), hi=0.35, lo=0.55, inner=0.5, rim=0.25, rim_col=(255, 120, 120), outline=OUTL,
          ow=max(2, int(s * 0.03)), spec=0.35, spec_at=(0.35, 0.3), spec_r=0.18)
    stroke_path(img, catmull([S(0.05, -0.55), S(0.1, -0.1), S(-0.05, 0.4), S(0.05, 0.9)], closed=False, n=6), (250, 220, 120, 230), max(2, s * 0.04))
    stroke_path(img, catmull([S(0.5, -0.5), S(0.65, 0.0), S(0.45, 0.5)], closed=False, n=6), (240, 90, 90, 230), max(2, s * 0.03))


# ---------------------------------------------------------------- abdomen with appendix
def abdomen(img, cx, cy, s, inflame=0.0, burst=0.0, pus=0.0, t=0.0, skin=True):
    """front cutaway of the belly: ribs, liver, stomach, colon frame, small bowel, appendix (bottom-left = body's right)"""
    S = P(cx, cy, s)
    if skin:
        body = catmull([S(-1.25, -1.4), S(1.25, -1.4), S(1.22, -0.4), S(1.1, 0.5), S(1.2, 1.25), S(0.6, 1.55), S(0, 1.6), S(-0.6, 1.55), S(-1.2, 1.25), S(-1.1, 0.5), S(-1.22, -0.4)], n=6)
        shade(img, body, (120, 60, 66), light=(-0.5, -0.6), hi=0.15, lo=0.6, inner=0.8, outline=OUTL, ow=max(2, int(s * 0.02)))
    # ribs
    for k in range(4):
        y = -1.3 + k * 0.17
        for side in (-1, 1):
            tube(img, [S(0.08 * side, y), S(0.6 * side, y + 0.05), S(1.05 * side, y + 0.3 + k * 0.05)], BONE, s * 0.07, outline=OUTL)
    tube(img, [S(0, -1.4), S(0, -0.75)], BONE, s * 0.12, outline=OUTL)
    # liver (screen-left = body right) and stomach
    liver = catmull([S(-1.05, -0.85), S(-0.2, -0.95), S(0.25, -0.8), S(0.05, -0.55), S(-0.55, -0.35), S(-1.0, -0.45)], n=8)
    shade(img, liver, LIVER, hi=0.3, lo=0.5, inner=0.5, outline=OUTL, ow=max(2, int(s * 0.02)), spec=0.2, spec_at=(0.3, 0.3))
    stom = catmull([S(0.15, -0.85), S(0.75, -0.95), S(1.0, -0.6), S(0.8, -0.3), S(0.35, -0.3), S(0.25, -0.5)], n=8)
    shade(img, stom, (226, 150, 140), hi=0.3, lo=0.45, inner=0.5, outline=OUTL, ow=max(2, int(s * 0.02)), spec=0.2, spec_at=(0.4, 0.3))
    # colon frame (ascending on screen-left)
    colon = [S(-0.62, 0.95), S(-0.75, 0.3), S(-0.72, -0.2), S(-0.3, -0.25), S(0.3, -0.24), S(0.72, -0.2), S(0.78, 0.3), S(0.65, 0.9), S(0.25, 1.05)]
    tube(img, colon, COLON, s * 0.26, outline=OUTL)
    for k in range(12):
        p = colon[min(len(colon) - 1, k * len(colon) // 12)]
        ImageDraw.Draw(img).ellipse((p[0] - 3, p[1] - 3, p[0] + 3, p[1] + 3), fill=(170, 100, 80, 120))
    # small bowel coils
    for j in range(4):
        y = 0.05 + j * 0.2
        pts = [S(-0.45 + i * 0.1, y + 0.06 * math.sin(i * 1.9 + j * 1.3)) for i in range(10)]
        tube(img, pts, GUT, s * 0.13, hi=0.35, lo=0.45, outline=OUTL)
    # appendix
    ac = mixc((236, 170, 150), (230, 40, 40), inflame)
    sw = 1 + 0.9 * inflame
    a0 = S(-0.6, 0.98)
    a1 = S(-0.5, 1.28)
    if burst <= 0:
        tube(img, [a0, S(-0.62, 1.12), a1], ac, s * 0.085 * sw, outline=OUTL)
        if inflame > 0.3:
            glow(img, a1[0], a1[1], s * 0.35 * inflame, (255, 40, 40), a=0.55 * inflame * (0.7 + 0.3 * math.sin(t * 6)))
    else:
        tube(img, [a0, S(-0.62, 1.12), S(-0.56, 1.22)], ac, s * 0.085 * sw, outline=OUTL)
        rng = np.random.default_rng(5)
        d = ImageDraw.Draw(img)
        for k in range(int(70 * burst)):
            ang = rng.uniform(0, 2 * math.pi)
            r = rng.uniform(0, 0.9) * burst * s
            x, y = a1[0] + r * math.cos(ang), a1[1] + r * math.sin(ang) * 0.7
            q = s * rng.uniform(0.012, 0.03)
            d.ellipse((x - q, y - q, x + q, y + q), fill=(226, 206, 90, 220))
    if pus > 0:
        g = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ImageDraw.Draw(g).ellipse((*S(-1.05, -0.2), *S(1.05, 1.5)), fill=(255, 40, 40, int(130 * pus)))
        img.alpha_composite(g.filter(ImageFilter.GaussianBlur(s * 0.2)))


# ---------------------------------------------------------------- head cross-section (side view, facing right)
def head_section(img, cx, cy, s, shift=0.0, bleed=0.0, t=0.0):
    """sagittal section: skull, brain (can slide forward by `shift`), spinal column. bleed: red spot at front"""
    S = P(cx, cy, s)
    outer = catmull([S(-0.95, -0.2), S(-0.75, -0.85), S(-0.1, -1.15), S(0.6, -0.95), S(0.95, -0.4), S(1.0, 0.15), S(1.1, 0.35), S(0.95, 0.55), S(1.0, 0.75),
                     S(0.8, 0.95), S(0.55, 1.05), S(0.3, 1.5), S(-0.3, 1.6), S(-0.45, 0.9), S(-0.9, 0.5)], n=8)
    shade(img, outer, (226, 170, 140), hi=0.25, lo=0.5, inner=0.5, outline=OUTL, ow=max(2, int(s * 0.02)))
    skull = catmull([S(-0.85, -0.15), S(-0.68, -0.78), S(-0.1, -1.04), S(0.55, -0.86), S(0.86, -0.35), S(0.82, 0.1), S(0.2, 0.15), S(-0.5, 0.45)], n=8)
    shade(img, skull, BONE, hi=0.3, lo=0.4, inner=0.5, outline=OUTL, ow=max(2, int(s * 0.02)))
    csf = catmull([S(-0.76, -0.15), S(-0.6, -0.7), S(-0.1, -0.94), S(0.5, -0.78), S(0.76, -0.33), S(0.72, 0.03), S(0.15, 0.08), S(-0.45, 0.36)], n=8)
    shade(img, csf, (90, 150, 220), hi=0.2, lo=0.3, inner=0.4)
    sh = shift * 0.12
    brain = catmull([S(-0.7 + sh, -0.15), S(-0.55 + sh, -0.66), S(-0.1 + sh, -0.88), S(0.45 + sh, -0.74), S(0.7 + sh, -0.32), S(0.62 + sh, 0.0),
                     S(0.15 + sh, 0.02), S(-0.15 + sh, 0.2), S(-0.45 + sh, 0.28)], n=8)

    def gyri(col, xx, yy, w, h):
        v = np.sin(xx / max(w, 1) * 38 + np.sin(yy / max(h, 1) * 9) * 2.5) * np.sin(yy / max(h, 1) * 30 + np.sin(xx / max(w, 1) * 7) * 2)
        k = (v > 0.55)[..., None] * 0.28
        return col * (1 - k) + np.array((120, 50, 70), np.float32) * k
    shade(img, brain, (236, 170, 178), hi=0.3, lo=0.45, inner=0.5, outline=OUTL, ow=max(2, int(s * 0.02)), tex=gyri, spec=0.15, spec_at=(0.35, 0.25))
    cereb = catmull([S(-0.62 + sh, 0.05), S(-0.2 + sh, 0.12), S(-0.25 + sh, 0.36), S(-0.55 + sh, 0.34)], n=6)
    shade(img, cereb, (220, 150, 160), hi=0.2, lo=0.4, inner=0.4, outline=OUTL, ow=2)
    tube(img, [S(-0.2 + sh, 0.2), S(-0.15, 0.6), S(-0.12, 1.5)], (236, 200, 180), s * 0.16, outline=OUTL)
    for k in range(6):
        c = S(-0.32, 0.55 + k * 0.17)
        shade(img, [(c[0] - s * 0.1, c[1] - s * 0.06), (c[0] + s * 0.02, c[1] - s * 0.06), (c[0] + s * 0.02, c[1] + s * 0.06), (c[0] - s * 0.1, c[1] + s * 0.06)], BONE, hi=0.2, lo=0.3, inner=0.3, outline=OUTL, ow=2)
    if bleed > 0:
        c = S(0.6 + sh, -0.4)
        glow(img, c[0], c[1], s * 0.4 * bleed, (220, 0, 20), a=0.8)
        glow(img, c[0], c[1], s * 0.18 * bleed, (120, 0, 10), a=0.9)


# ---------------------------------------------------------------- vessel interior (micro)
def vessel(img, t, flow=1.0, cells=26, bacteria=0, wbc=0, clot=0.0, leak=0.0, col_bg=(120, 14, 26), y0=640, y1=1260, toxin=0, seed=2):
    """horizontal blood vessel cutaway filling the frame width"""
    d = ImageDraw.Draw(img)
    wall = (186, 70, 80)
    shade(img, [(-20, y0 - 70), (1100, y0 - 70), (1100, y0 + 10), (-20, y0 + 10)], wall, light=(0, -1), hi=0.3, lo=0.4, inner=0.3)
    shade(img, [(-20, y1 - 10), (1100, y1 - 10), (1100, y1 + 70), (-20, y1 + 70)], wall, light=(0, -1), hi=0.3, lo=0.4, inner=0.3)
    inner = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(inner).rectangle((0, y0 + 10, 1080, y1 - 10), fill=col_bg + (255,))
    img.alpha_composite(inner)
    glow(img, 540, (y0 + y1) / 2, 700, (200, 40, 50), a=0.35)
    rng = np.random.default_rng(seed)
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    dl = ImageDraw.Draw(lay)
    for i in range(cells):
        r = rng.uniform(22, 46)
        x = (rng.uniform(0, 1200) + t * flow * rng.uniform(120, 220)) % 1300 - 110
        if clot > 0 and x > 640:
            x = 640 - (x - 640) * 0.05
        y = rng.uniform(y0 + 40, y1 - 40)
        ang = t * rng.uniform(-1, 1) + i
        sx = abs(math.cos(ang)) * 0.7 + 0.3
        dl.ellipse((x - r * sx, y - r, x + r * sx, y + r), fill=(220, 40, 52, 255), outline=(130, 10, 24, 255), width=3)
        dl.ellipse((x - r * sx * 0.5, y - r * 0.5, x + r * sx * 0.5, y + r * 0.5), fill=(170, 20, 34, 255))
        dl.ellipse((x - r * sx * 0.75, y - r * 0.8, x - r * sx * 0.15, y - r * 0.35), fill=(255, 140, 140, 140))
    img.alpha_composite(lay)
    for i in range(wbc):
        x = (rng.uniform(0, 1080) + t * flow * 60) % 1200 - 60
        y = rng.uniform(y0 + 80, y1 - 80)
        shade(img, None, (230, 228, 240), ellipse=(x, y, 62, 56), hi=0.3, lo=0.3, inner=0.5, alpha=0.95)
        for k in range(3):
            shade(img, None, (110, 70, 170), ellipse=(x - 20 + k * 18, y + 6 * math.sin(k * 2), 16, 13), hi=0.3, lo=0.3, inner=0.3)
    for i in range(bacteria):
        x = (rng.uniform(0, 1080) + t * flow * rng.uniform(40, 120)) % 1200 - 60
        y = rng.uniform(y0 + 30, y1 - 30) + 12 * math.sin(t * 2 + i)
        a = rng.uniform(0, math.pi) + 0.4 * math.sin(t + i)
        L = rng.uniform(24, 36)
        tube(img, [(x - L * math.cos(a), y - L * math.sin(a)), (x + L * math.cos(a), y + L * math.sin(a))], (120, 210, 80), 22, hi=0.35, lo=0.4, outline=(20, 50, 10, 255))
    for i in range(toxin):
        x = (rng.uniform(0, 1080) + t * 70) % 1150 - 40
        y = rng.uniform(y0 + 30, y1 - 30) + 20 * math.sin(t * 1.5 + i)
        molecule(img, x, y, 16, (160, 230, 90), t + i)
    if clot > 0:
        c = (680, (y0 + y1) / 2)
        r = (y1 - y0) * 0.48 * clot
        rr = np.random.default_rng(9)
        pts = [(c[0] + r * 0.8 * math.cos(a) * rr.uniform(0.75, 1.1), c[1] + r * math.sin(a) * rr.uniform(0.75, 1.05)) for a in np.linspace(0, 2 * math.pi, 18, endpoint=False)]
        shade(img, catmull(pts, n=5), (110, 14, 26), hi=0.25, lo=0.5, inner=0.6, outline=(40, 0, 6, 255), ow=3, spec=0.15)
        for k in range(14):
            a = rr.uniform(0, 2 * math.pi)
            ImageDraw.Draw(img).line((c[0], c[1], c[0] + r * 0.9 * math.cos(a), c[1] + r * 0.9 * math.sin(a)), fill=(240, 210, 160, 160), width=2)
    if leak > 0:
        rr = np.random.default_rng(11)
        for k in range(int(20 * leak)):
            x = rr.uniform(60, 1020)
            ph = (t * 0.6 + k * 0.13) % 1
            y = y1 + 20 + ph * 220
            ImageDraw.Draw(img).ellipse((x - 10, y - 10, x + 10, y + 10), fill=(220, 50, 60, int(220 * (1 - ph))))


def molecule(img, x, y, r, col, t):
    d = ImageDraw.Draw(img)
    pts = [(x + r * 1.6 * math.cos(t + k * 2.1), y + r * 1.6 * math.sin(t * 0.7 + k * 2.1)) for k in range(3)]
    for p in pts:
        d.line((x, y, p[0], p[1]), fill=(230, 230, 230, 220), width=3)
    for p in pts:
        shade(img, None, (240, 240, 240), ellipse=(p[0], p[1], r * 0.55, r * 0.55), hi=0.4, lo=0.3, inner=0.2)
    shade(img, None, col, ellipse=(x, y, r, r), hi=0.45, lo=0.4, inner=0.3, outline=(20, 40, 10, 255), ow=2)


# ---------------------------------------------------------------- nerve -> muscle junction
def synapse(img, t, block=0.0, signal=1.0, cx=540, cy=900, s=420):
    S = P(cx, cy, s)
    # muscle fibre (bottom)
    for k in range(3):
        y = 0.55 + k * 0.28
        tube(img, [S(-1.4, y), S(1.4, y + 0.02)], (200, 70, 80), s * 0.26, hi=0.3, lo=0.5, outline=OUTL)
        for j in range(16):
            x = -1.3 + j * 0.17
            stroke_path(img, [S(x, y - 0.1), S(x, y + 0.1)], (150, 40, 50, 160), max(2, s * 0.01))
    # nerve axon coming from top
    tube(img, [S(-0.2, -1.6), S(-0.1, -0.9), S(0.0, -0.35)], (250, 214, 120), s * 0.22, hi=0.35, lo=0.45, outline=OUTL)
    term = catmull([S(-0.5, -0.4), S(0.0, -0.52), S(0.5, -0.4), S(0.58, 0.05), S(0.0, 0.22), S(-0.58, 0.05)], n=8)
    shade(img, term, (250, 214, 120), hi=0.35, lo=0.45, inner=0.5, outline=OUTL, ow=max(2, int(s * 0.015)), spec=0.2)
    rng = np.random.default_rng(4)
    for k in range(9):
        x, y = rng.uniform(-0.38, 0.38), rng.uniform(-0.32, 0.05)
        shade(img, None, (255, 255, 230), ellipse=(*S(x, y), s * 0.055, s * 0.055), hi=0.4, lo=0.3, inner=0.3, outline=(150, 120, 60, 255), ow=2)
    # signal pulses travelling down the axon
    if signal > 0:
        ph = (t * 1.2) % 1
        p = S(-0.2 + 0.2 * ph, -1.6 + 1.2 * ph)
        glow(img, p[0], p[1], s * 0.2, (255, 240, 150), a=0.9 * signal)
    # transmitter released into cleft (blocked by toxin)
    rel = 1 - block
    d = ImageDraw.Draw(img)
    for k in range(int(18 * rel)):
        ph = (t * 0.9 + k / 18) % 1
        x = -0.4 + 0.8 * ((k * 37) % 18) / 18
        y = 0.18 + ph * 0.3
        c = S(x, y)
        d.ellipse((c[0] - 7, c[1] - 7, c[0] + 7, c[1] + 7), fill=(255, 245, 150, int(255 * (1 - ph))))
    if block > 0:
        for k in range(int(10 * block)):
            x = -0.5 + k * 0.11
            molecule(img, *S(x, 0.12 + 0.03 * math.sin(t * 2 + k)), s * 0.035, (150, 230, 80), t + k)
    if rel > 0.5:
        glow(img, *S(0, 0.9), s * 0.9, (255, 120, 120), a=0.25 * rel * (0.5 + 0.5 * math.sin(t * 6)))


# ---------------------------------------------------------------- leg with deep vein
def leg(img, cx, cy, s, clot=0.0, flow=1.0, swell=0.0, t=0.0, travel=None):
    """calf seen from the front, cutaway deep vein with valves. travel: 0..1 clot breaking off and moving up"""
    S = P(cx, cy, s)
    sw = 1 + 0.12 * swell
    skin = catmull([S(-0.42 * sw, -1.6), S(0.42 * sw, -1.6), S(0.5 * sw, -0.6), S(0.42 * sw, 0.4), S(0.24, 1.3), S(0.26, 1.6), S(-0.26, 1.6), S(-0.24, 1.3), S(-0.44 * sw, 0.4), S(-0.52 * sw, -0.6)], n=8)
    shade(img, skin, mixc((226, 170, 140), (210, 120, 120), swell), hi=0.25, lo=0.5, inner=0.6, outline=OUTL, ow=3, spec=0.15, spec_at=(0.35, 0.3))
    tube(img, [S(0.12, -1.6), S(0.14, 0.0), S(0.08, 1.5)], BONE, s * 0.14, outline=OUTL)
    vein = [S(-0.12, 1.5), S(-0.15, 0.6), S(-0.16, -0.3), S(-0.12, -1.6)]
    tube(img, vein, (60, 80, 190), s * 0.17, outline=OUTL)
    d = ImageDraw.Draw(img)
    VP = catmull(vein, closed=False, n=12)
    for k in range(4):
        p = VP[6 + k * 9] if 6 + k * 9 < len(VP) else VP[-1]
        d.polygon([(p[0] - s * 0.06, p[1] + s * 0.05), (p[0], p[1] - s * 0.03), (p[0] + s * 0.06, p[1] + s * 0.05)], outline=(220, 230, 255, 220), width=3)
    n = 10
    for k in range(n):
        ph = (k / n + t * 0.25 * flow) % 1
        i = int((1 - ph) * (len(VP) - 1))
        p = VP[i]
        r = s * 0.035
        d.ellipse((p[0] - r, p[1] - r, p[0] + r, p[1] + r), fill=(200, 60, 80, 230))
    if clot > 0:
        c = S(-0.15, 0.25) if travel is None else VP[int((1 - travel) * (len(VP) - 1) * 0.55)]
        r = s * (0.05 + 0.08 * clot)
        shade(img, None, (90, 10, 22), ellipse=(c[0], c[1], r * 0.8, r * 1.7), hi=0.2, lo=0.5, inner=0.5, outline=(30, 0, 6, 255), ow=3)
        glow(img, c[0], c[1], r * 3, (255, 30, 30), a=0.35 * clot * (0.6 + 0.4 * math.sin(t * 5)))


# ---------------------------------------------------------------- kidneys
def kidneys(img, cx, cy, s, fail=0.0, t=0.0):
    S = P(cx, cy, s)
    for side in (-1, 1):
        pts = [(0.25, -0.55), (0.6, -0.6), (0.8, -0.2), (0.75, 0.35), (0.5, 0.6), (0.3, 0.45), (0.38, 0.1), (0.3, -0.2)]
        poly = catmull([S(side * x, y) for x, y in pts], n=8)
        shade(img, poly, mixc((150, 50, 60), (90, 80, 90), fail), hi=0.35, lo=0.5, inner=0.5, outline=OUTL, ow=3, spec=0.25, spec_at=(0.4, 0.3))
        tube(img, [S(side * 0.33, 0.1), S(side * 0.15, 0.4), S(side * 0.12, 1.2)], (240, 220, 140), s * 0.05, outline=OUTL)
    tube(img, [S(0.05, -1.0), S(0.05, 1.2)], AORTA, s * 0.12, outline=OUTL)
    tube(img, [S(-0.1, -1.0), S(-0.1, 1.2)], VEIN, s * 0.12, outline=OUTL)
    if fail > 0:
        for side in (-1, 1):
            glow(img, *S(side * 0.55, 0.0), s * 0.5, (255, 30, 30), a=0.45 * fail * (0.6 + 0.4 * math.sin(t * 6)))


# ---------------------------------------------------------------- translucent body silhouette
def silhouette(img, cx, cy, s, alpha=0.32, col=(150, 180, 230)):
    """glass body (head to hips), s = half shoulder width"""
    S = P(cx, cy, s)
    pts = [S(0, -2.05), S(0.36, -1.95), S(0.44, -1.55), S(0.3, -1.2), S(0.32, -1.02), S(0.95, -0.85), S(1.12, -0.45), S(1.18, 0.6), S(1.3, 1.6), S(1.1, 1.6),
           S(0.98, 0.4), S(0.85, 0.7), S(0.82, 1.6), S(0.95, 2.6), S(-0.95, 2.6), S(-0.82, 1.6), S(-0.85, 0.7), S(-0.98, 0.4), S(-1.1, 1.6), S(-1.3, 1.6),
           S(-1.18, 0.6), S(-1.12, -0.45), S(-0.95, -0.85), S(-0.32, -1.02), S(-0.3, -1.2), S(-0.44, -1.55), S(-0.36, -1.95)]
    poly = catmull(pts, n=6)
    shade(img, poly, col, hi=0.2, lo=0.4, inner=0.9, rim=0.6, rim_col=(200, 230, 255), alpha=alpha, outline=col + (150,), ow=3)
