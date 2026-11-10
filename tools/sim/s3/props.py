"""Shaded props: mushroom jar, wounded hand, car (side view), seat belt, oxygen mask, plane seat leg."""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from gfx import shade, tube, glow, catmull, stroke_path, mixc, lerp, ease, smooth, W, H, paste_any

OUTL = (30, 16, 18, 255)


def jar(img, cx, by, s, bulge=0.6, t=0.0, open_=False):
    """glass jar of pickled mushrooms, bottom centre (cx, by), s = height/2"""
    w, h = s * 0.75, s * 1.6
    x0, x1, y0 = cx - w, cx + w, by - h
    body = catmull([(x0 + 10, by), (x0, by - 30), (x0, y0 + 60), (x0 + 30, y0 + 20), (x1 - 30, y0 + 20), (x1, y0 + 60), (x1, by - 30), (x1 - 10, by)], n=4)
    shade(img, body, (120, 98, 52), light=(-0.6, -0.4), hi=0.25, lo=0.55, inner=0.5)
    rng = np.random.default_rng(2)
    for k in range(14):
        mx, my = cx + rng.uniform(-0.75, 0.75) * w, by - rng.uniform(0.1, 0.85) * h
        r = s * rng.uniform(0.12, 0.2)
        shade(img, catmull([(mx - r, my), (mx - r * 0.7, my - r * 0.6), (mx, my - r * 0.75), (mx + r * 0.7, my - r * 0.6), (mx + r, my), (mx, my + r * 0.15)], n=5),
              (176, 120, 60), hi=0.35, lo=0.45, inner=0.4, spec=0.2)
        tube(img, [(mx, my), (mx + r * 0.1, my + r * 0.8)], (226, 206, 170), r * 0.35, hi=0.3, lo=0.3)
    # glass
    shade(img, body, (200, 225, 235), hi=0.6, lo=0.0, inner=0.0, alpha=0.18, outline=(230, 240, 245, 255), ow=4)
    stroke_path(img, [(x0 + 25, y0 + 90), (x0 + 25, by - 50)], (255, 255, 255, 120), 10, blur=2)
    for k in range(6):
        ph = (t * 0.5 + k * 0.17) % 1
        bx = cx + (k - 2.5) * w * 0.25
        byy = lerp(by - 30, y0 + 70, ph)
        ImageDraw.Draw(img).ellipse((bx - 6, byy - 6, bx + 6, byy + 6), outline=(255, 255, 255, 160), width=2)
    # lid
    lid = [(x0 - 8, y0 + 30), (x1 + 8, y0 + 30), (x1 + 8, y0 - 18), (x0 - 8, y0 - 18)]
    shade(img, lid, (210, 176, 60), hi=0.45, lo=0.4, inner=0.3, outline=OUTL, ow=3, spec=0.3)
    if bulge and not open_:
        b = s * 0.22 * bulge
        dome = [(x0 - 8, y0 - 16)] + [(cx + (w + 8) * math.cos(a), y0 - 16 - b * math.sin(a)) for a in np.linspace(math.pi, 0, 16)] + [(x1 + 8, y0 - 16)]
        shade(img, dome, (226, 190, 70), hi=0.5, lo=0.3, inner=0.3, outline=OUTL, ow=3, spec=0.4, spec_at=(0.4, 0.3))


def wounded_hand(img, cx, cy, s, red=0.3, streaks=0.0, t=0.0, skin=(232, 180, 150)):
    """big open palm seen from the front with a cut; red = inflammation 0..1; streaks = red lines up the wrist"""
    S = lambda x, y: (cx + x * s, cy + y * s)
    tube(img, [S(0, 2.2), S(0, 1.0)], skin, s * 0.95, hi=0.25, lo=0.45, outline=OUTL)
    palm = catmull([S(-0.62, 0.95), S(-0.7, 0.1), S(-0.55, -0.45), S(0.55, -0.45), S(0.72, 0.1), S(0.6, 0.95), S(0, 1.15)], n=6)
    shade(img, palm, skin, hi=0.25, lo=0.45, inner=0.5, outline=OUTL, ow=4, spec=0.12)
    for k, (x, L) in enumerate(((-0.45, 0.85), (-0.15, 1.05), (0.15, 1.0), (0.43, 0.8))):
        tube(img, [S(x, -0.35), S(x * 1.05, -0.35 - L)], skin, s * 0.26, hi=0.3, lo=0.45, outline=OUTL)
        stroke_path(img, [S(x * 1.03 - 0.06, -0.35 - L * 0.55), S(x * 1.03 + 0.06, -0.35 - L * 0.55)], mixc(skin, (120, 70, 60), 0.5) + (180,), 3)
    tube(img, [S(0.62, 0.55), S(0.95, 0.1), S(1.05, -0.3)], skin, s * 0.3, hi=0.3, lo=0.45, outline=OUTL)
    # inflammation halo + cut
    glow(img, *S(-0.05, 0.35), s * (0.45 + 0.4 * red), (240, 60, 60), a=0.25 + 0.5 * red)
    cut = [S(-0.35, 0.5), S(-0.05, 0.3), S(0.3, 0.18)]
    stroke_path(img, cut, (120, 10, 20, 255), max(4, s * 0.06))
    stroke_path(img, cut, (220, 40, 50, 255), max(2, s * 0.025))
    if red > 0.5:
        for k in range(5):
            p = cut[1]
            ImageDraw.Draw(img).ellipse((p[0] - 8 + k * 12 - 24, p[1] + 10, p[0] + k * 12 - 16, p[1] + 18), fill=(236, 220, 120, 200))
    if streaks > 0:
        for k in range(3):
            x = -0.2 + k * 0.2
            pts = [S(x, 0.9), S(x + 0.05 * math.sin(k), 1.4), S(x - 0.04, 1.9), S(x, 2.3)]
            n = max(2, int(len(pts) * streaks + 0.5))
            stroke_path(img, catmull(pts, closed=False, n=6)[: int(18 * streaks) + 2], (210, 40, 50, 200), max(3, s * 0.035), blur=2)


def car_side(img, t, crash=0.0, fly=0.0, speed=1.0, gy=1260, scale=1.25, drv_lean=0.0, passengers=True, pole=None, alarm=False):
    """side view of a car driving right on a night road. crash 0..1 crumples the front, fly 0..1 throws the back passenger forward"""
    d = ImageDraw.Draw(img)
    tt = t * speed
    for k in range(-1, 6):
        x = k * 330 - (tt * 900) % 330
        d.rectangle((x, gy - 520, x + 16, gy), fill=(56, 58, 70, 255))
        glow(img, x + 8, gy - 520, 90, (255, 200, 120), a=0.5)
    d.rectangle((0, gy, W, H), fill=(30, 30, 36, 255))
    for k in range(-1, 9):
        x = k * 170 - (tt * 1600) % 170
        d.rectangle((x, gy + 80, x + 90, gy + 92), fill=(220, 220, 210, 255))
    if pole is not None:
        shade(img, [(pole, gy - 700), (pole + 54, gy - 700), (pole + 54, gy + 20), (pole, gy + 20)], (130, 132, 140), hi=0.3, lo=0.5, inner=0.3, outline=OUTL, ow=3)
    sc = scale
    X = lambda x: 540 + (x - 545) * sc
    Y = lambda y: gy - 70 + (y - (gy - 70)) * sc
    x0, x1 = X(110), X(980 - 160 * crash)
    yb = gy - 70
    roof = Y(yb - 340)
    body = catmull([(x0, yb), (x0, Y(yb - 150)), (X(230), Y(yb - 175)), (X(330), roof), (x1 - 300 * sc, roof), (x1 - 180 * sc, Y(yb - 185)), (x1, Y(yb - 150)), (x1, yb)], n=4)
    shade(img, body, (176, 26, 36), light=(-0.4, -0.8), hi=0.35, lo=0.55, inner=0.4, outline=OUTL, ow=4, spec=0.25, spec_at=(0.4, 0.2))
    win = [(X(255), Y(yb - 185)), (X(345), Y(yb - 320)), (x1 - 310 * sc, Y(yb - 320)), (x1 - 205 * sc, Y(yb - 190))]
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(lay).polygon(win, fill=(26, 34, 54, 255))
    if passengers:
        import hero as HR
        drv = dict(outfit="jacket", shirt=(50, 90, 140), hair=(30, 22, 18), mouth="grit" if crash > 0 else "neutral", brows="pain" if crash > 0 else "neutral")
        pas = dict(outfit="hoodie", shirt=(220, 120, 40), hair=(66, 42, 28), mouth="scream" if crash > 0 else "smile", open=1.2 if crash > 0 else 1.0, brows="worried" if crash > 0 else "raised")
        hs = 50 * sc
        dx = x1 - 440 * sc
        HR.draw_body(lay, dx, Y(yb - 250), hs, drv, t)
        HR.draw_head(lay, dx + 40 * drv_lean * sc, Y(yb - 250), hs, dict(drv, tilt=0.35 * drv_lean), t)
        stroke_path(lay, [(dx - 60 * sc, Y(yb - 225)), (dx + 50 * sc, Y(yb - 140))], (230, 190, 60, 255), 10)
        px = X(380) + fly * 260 * sc
        HR.draw_body(lay, px, Y(yb - 250) - fly * 20, hs, pas, t)
        HR.draw_head(lay, px + 30 * fly, Y(yb - 250) - fly * 20, hs, dict(pas, tilt=0.5 * fly), t)
    m = Image.new("L", img.size, 0)
    ImageDraw.Draw(m).polygon(win, fill=255)
    from PIL import ImageChops
    lay.putalpha(ImageChops.multiply(lay.getchannel("A"), m))
    img.alpha_composite(lay)
    d = ImageDraw.Draw(img)
    d.line(win + [win[0]], fill=(210, 220, 236, 255), width=6)
    d.line((x1 - 480 * sc, Y(yb - 320), x1 - 480 * sc, yb - 10), fill=(110, 14, 24, 255), width=8)
    if crash > 0:
        rng = np.random.default_rng(3)
        for k in range(int(14 * crash)):
            a = (x1 - rng.uniform(0, 90 * sc), Y(yb - rng.uniform(0, 160)))
            d.line([a, (a[0] - rng.uniform(20, 60), a[1] + rng.uniform(-40, 40))], fill=(70, 6, 12, 255), width=5)
        cxw, cyw = x1 - 250 * sc, Y(yb - 260)
        for k in range(10):
            a = k * 0.63
            d.line([(cxw, cyw), (cxw + 90 * crash * math.cos(a), cyw + 90 * crash * math.sin(a))], fill=(230, 240, 255, 230), width=3)
        for k in range(int(40 * crash)):
            sx, sy = x1 + rng.uniform(-20, 200) * crash, Y(yb - rng.uniform(0, 320))
            d.polygon([(sx, sy), (sx + 12, sy + 5), (sx + 4, sy + 14)], fill=(220, 235, 255, 230))
    for wx in (X(250), x1 - 170 * sc):
        shade(img, None, (18, 18, 22), ellipse=(wx, yb, 78 * sc, 78 * sc), hi=0.2, lo=0.3, inner=0.4)
        shade(img, None, (150, 154, 166), ellipse=(wx, yb, 38 * sc, 38 * sc), hi=0.4, lo=0.4, inner=0.3, spec=0.3)
    if crash < 0.3:
        beam = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ImageDraw.Draw(beam).polygon([(x1, Y(yb - 120)), (1080, Y(yb - 240)), (1080, Y(yb + 50))], fill=(255, 240, 200, 80))
        img.alpha_composite(beam.filter(ImageFilter.GaussianBlur(24)))
    if alarm:
        on = (t * 2) % 1 < 0.5
        if on:
            glow(img, x1 - 10, Y(yb - 140), 120, (255, 170, 40), a=0.8)
            glow(img, x0 + 10, Y(yb - 130), 120, (255, 170, 40), a=0.8)


def oxygen_mask(img, cx, cy, s, t=0.0):
    """transparent mask over nose/mouth of a hero whose head centre is (cx, cy), radius s"""
    pts = catmull([(cx - 0.32 * s, cy + 0.22 * s), (cx, cy + 0.1 * s), (cx + 0.32 * s, cy + 0.22 * s), (cx + 0.36 * s, cy + 0.7 * s), (cx, cy + 0.92 * s), (cx - 0.36 * s, cy + 0.7 * s)], n=6)
    fog = 0.25 + 0.2 * (0.5 + 0.5 * math.sin(t * 2.5))
    shade(img, pts, (210, 235, 245), hi=0.5, lo=0.1, inner=0.4, alpha=fog, outline=(230, 245, 255, 200), ow=3)
    stroke_path(img, [(cx - 0.36 * s, cy + 0.4 * s), (cx - 0.95 * s, cy + 0.25 * s)], (230, 240, 245, 200), 4)
    stroke_path(img, [(cx + 0.36 * s, cy + 0.4 * s), (cx + 0.95 * s, cy + 0.25 * s)], (230, 240, 245, 200), 4)
    tube(img, [(cx, cy + 0.92 * s), (cx + 0.2 * s, cy + 1.6 * s), (cx + 0.9 * s, cy + 2.4 * s)], (200, 225, 235), s * 0.12, hi=0.4, lo=0.2)


def ventilator_tube(img, cx, cy, s, t=0.0):
    tube(img, [(cx, cy + 0.66 * s), (cx + 0.15 * s, cy + 1.2 * s), (cx + 1.2 * s, cy + 1.9 * s), (cx + 2.4 * s, cy + 2.0 * s)], (200, 220, 230), s * 0.16, hi=0.45, lo=0.3)
    stroke_path(img, [(cx - 0.4 * s, cy + 0.62 * s), (cx + 0.4 * s, cy + 0.62 * s)], (240, 240, 245, 230), max(3, s * 0.05))
