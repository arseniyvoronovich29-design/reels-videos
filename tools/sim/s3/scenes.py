"""Cinematic backgrounds (drawn sharp, then softly blurred for depth of field). bg(name, t) -> RGBA W x H"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from gfx import W, H, vgrad, shade, glow, tube, catmull, mixc, lerp, stroke_path, radial_layer, paste_any

_cache = {}


def studio(top=(24, 34, 52), bot=(8, 10, 18), accent=(40, 120, 160), seed=1):
    img = vgrad((W, H), top, bot)
    rng = np.random.default_rng(seed)
    for k in range(5):
        glow(img, rng.uniform(0, W), rng.uniform(300, 1500), rng.uniform(300, 600), accent, a=0.18)
    return img


def room():
    img = vgrad((W, H), (34, 40, 60), (16, 18, 28))
    d = ImageDraw.Draw(img)
    for x in range(0, W, 120):
        d.line((x, 0, x, 1500), fill=(40, 46, 68, 255), width=4)
    # window with city
    shade(img, [(80, 380), (520, 380), (520, 1000), (80, 1000)], (20, 30, 56), light=(0, -1), hi=0.15, lo=0.3, inner=0.4, outline=(70, 66, 80, 255), ow=16)
    rng = np.random.default_rng(2)
    for k in range(10):
        x = 100 + k * 42
        h = rng.uniform(150, 420)
        d.rectangle((x, 1000 - h, x + 36, 990), fill=(14, 18, 34, 255))
        for j in range(int(h / 30)):
            if rng.random() < 0.45:
                d.rectangle((x + 8, 1000 - h + 12 + j * 30, x + 16, 1000 - h + 24 + j * 30), fill=(255, 210, 120, 255) if rng.random() < 0.7 else (150, 190, 255, 255))
    glow(img, 380, 520, 90, (220, 230, 255), a=0.5)
    d.line((300, 380, 300, 1000), fill=(70, 66, 80, 255), width=10)
    # garland
    pts = [(30 + k * 52, 300 + 34 * math.sin(k * 0.5)) for k in range(21)]
    stroke_path(img, pts, (20, 20, 20, 255), 3)
    for k, p in enumerate(pts):
        c = [(255, 80, 80), (255, 210, 80), (90, 230, 120), (90, 160, 255)][k % 4]
        glow(img, p[0], p[1] + 10, 40, c, a=0.6)
        d.ellipse((p[0] - 7, p[1] + 3, p[0] + 7, p[1] + 19), fill=c + (255,))
    # shelf and lamp
    d.rectangle((640, 640, 1040, 660), fill=(110, 80, 60, 255))
    for k, c in enumerate([(200, 80, 60), (80, 120, 180), (220, 190, 90), (120, 160, 110), (180, 180, 190)]):
        d.rectangle((660 + k * 66, 540 + (k % 2) * 30, 708 + k * 66, 640), fill=c + (255,))
    shade(img, [(820, 980), (960, 980), (930, 1130), (850, 1130)], (240, 200, 140), hi=0.3, lo=0.3, inner=0.3)
    glow(img, 890, 1080, 420, (255, 190, 110), a=0.45)
    # sofa
    shade(img, catmull([(-60, 1280), (1140, 1280), (1140, 1700), (-60, 1700)], n=4), (70, 50, 60), hi=0.2, lo=0.5, inner=0.5)
    d.rectangle((0, 1700, W, H), fill=(40, 30, 30, 255))
    return img


def kitchen():
    img = vgrad((W, H), (46, 52, 66), (22, 24, 32))
    d = ImageDraw.Draw(img)
    shade(img, [(0, 160), (1080, 160), (1080, 520), (0, 520)], (80, 62, 50), hi=0.2, lo=0.4, inner=0.4)
    for x in (10, 280, 550, 820):
        d.rectangle((x, 175, x + 250, 505), outline=(50, 40, 32, 255), width=5)
        d.rectangle((x + 110, 330, x + 140, 342), fill=(190, 180, 160, 255))
    for y in range(560, 1250, 56):
        d.line((0, y, W, y), fill=(56, 62, 76, 255), width=2)
    for x in range(0, W, 56):
        d.line((x, 560, x, 1250), fill=(56, 62, 76, 255), width=2)
    glow(img, 760, 260, 120, (255, 220, 160), a=0.6)
    glow(img, 540, 700, 700, (255, 200, 140), a=0.18)
    shade(img, [(-20, 1250), (1100, 1250), (1100, 1330), (-20, 1330)], (120, 86, 62), light=(0, -1), hi=0.3, lo=0.3, inner=0.3)
    d.rectangle((0, 1330, W, H), fill=(36, 30, 30, 255))
    return img


def plane():
    img = vgrad((W, H), (60, 66, 82), (24, 26, 34))
    d = ImageDraw.Draw(img)
    shade(img, [(0, 0), (1080, 0), (1080, 300), (0, 300)], (78, 82, 96), hi=0.2, lo=0.4, inner=0.4)
    for k in range(9):
        glow(img, 60 + k * 125, 250, 40, (255, 230, 170), a=0.6)
    for k in range(3):
        x = 70 + k * 360
        shade(img, catmull([(x, 430), (x + 170, 430), (x + 170, 700), (x, 700)], n=4), (96, 100, 116), hi=0.2, lo=0.3, inner=0.3)
        shade(img, catmull([(x + 20, 450), (x + 150, 450), (x + 150, 680), (x + 20, 680)], n=4), (10, 16, 36), hi=0.1, lo=0.2, inner=0.6)
        glow(img, x + 85, 560, 40, (120, 150, 220), a=0.4)
    for k in range(4):
        x = -80 + k * 330
        shade(img, catmull([(x, 820), (x + 250, 820), (x + 260, 1400), (x - 10, 1400)], n=4), (44, 64, 120), hi=0.25, lo=0.5, inner=0.5)
        shade(img, catmull([(x + 30, 780), (x + 220, 780), (x + 220, 880), (x + 30, 880)], n=4), (226, 226, 232), hi=0.2, lo=0.3, inner=0.3)
    d.rectangle((0, 1400, W, H), fill=(40, 42, 54, 255))
    return img


def ward():
    img = vgrad((W, H), (40, 52, 62), (18, 24, 30))
    d = ImageDraw.Draw(img)
    shade(img, [(600, 300), (1020, 300), (1020, 800), (600, 800)], (16, 24, 44), hi=0.1, lo=0.3, inner=0.5, outline=(100, 110, 120, 255), ow=12)
    for k in range(7):
        d.line((600, 330 + k * 66, 1020, 330 + k * 66), fill=(70, 80, 96, 255), width=5)
    # monitor
    shade(img, [(80, 360), (440, 360), (440, 640), (80, 640)], (24, 28, 34), hi=0.2, lo=0.3, inner=0.4, outline=(120, 126, 136, 255), ow=6)
    # iv pole + bag
    d.rectangle((520, 220, 530, 1300), fill=(170, 176, 186, 255))
    shade(img, catmull([(470, 240), (580, 240), (590, 420), (460, 420)], n=4), (210, 230, 240), hi=0.4, lo=0.2, inner=0.3, alpha=0.8)
    d.rectangle((0, 1050, W, 1075), fill=(70, 86, 96, 255))
    d.rectangle((0, 1075, W, H), fill=(52, 60, 68, 255))
    return img


def stairs():
    img = vgrad((W, H), (54, 58, 70), (26, 28, 36))
    d = ImageDraw.Draw(img)
    for k in range(11):
        y = 1500 - k * 90
        x = 380 + k * 64
        shade(img, [(x, y - 90), (1100, y - 90), (1100, y), (x, y)], (82, 84, 96), light=(0, -1), hi=0.3, lo=0.4, inner=0.3)
    stroke_path(img, [(380, 1300), (1080, 500)], (150, 120, 80, 255), 14)
    shade(img, [(60, 420), (320, 420), (320, 700), (60, 700)], (20, 26, 44), hi=0.1, lo=0.3, inner=0.4, outline=(90, 90, 100, 255), ow=10)
    glow(img, 600, 300, 260, (255, 240, 200), a=0.35)
    return img


def dacha():
    img = vgrad((W, H), (40, 50, 86), (140, 96, 96))
    d = ImageDraw.Draw(img)
    glow(img, 840, 420, 260, (255, 210, 160), a=0.5)
    d.ellipse((800, 380, 880, 460), fill=(255, 236, 200, 255))
    rng = np.random.default_rng(9)
    for k in range(10):
        x = rng.uniform(-80, 1160)
        r = rng.uniform(140, 260)
        d.ellipse((x - r, 1050 - r, x + r, 1050 + r * 0.8), fill=(26, 40, 38, 255))
    for x in range(0, W, 46):
        shade(img, [(x, 1060), (x + 30, 1060), (x + 30, 1300), (x, 1300)], (100, 76, 56), hi=0.2, lo=0.3, inner=0.3)
    d.rectangle((0, 1300, W, H), fill=(40, 56, 36, 255))
    return img


def car_inside(t=0.0):
    """inside a car at night, side window with passing street lights (dynamic parts drawn by car_inside_fx)"""
    img = vgrad((W, H), (20, 22, 30), (10, 10, 14))
    shade(img, catmull([(-40, 260), (1120, 220), (1120, 900), (-40, 940)], n=4), (14, 18, 34), hi=0.1, lo=0.2, inner=0.6)
    shade(img, [(-40, 900), (1120, 860), (1120, 1100), (-40, 1140)], (36, 36, 44), hi=0.2, lo=0.4, inner=0.4)
    shade(img, [(-40, 1100), (1120, 1060), (1120, H), (-40, H)], (30, 30, 36), hi=0.15, lo=0.5, inner=0.5)
    return img


def car_inside_fx(img, t, speed=1.0):
    for k in range(4):
        x = (k * 380 - t * 1400 * speed) % 1500 - 200
        glow(img, x, 520, 160, (255, 200, 120), a=0.5)
    for k in range(6):
        x = (k * 260 - t * 2600 * speed) % 1600 - 260
        stroke_path(img, [(x, 700), (x + 220, 700)], (255, 230, 200, 60), 6, blur=4)


BUILDERS = {"room": room, "kitchen": kitchen, "plane": plane, "ward": ward, "stairs": stairs, "dacha": dacha, "car_inside": car_inside}


def bg(name, blur=5):
    key = (name, blur)
    if key not in _cache:
        if name.startswith("studio"):
            parts = name.split(":")
            accent = {"teal": (40, 130, 170), "red": (170, 20, 40), "blue": (60, 80, 200), "green": (60, 160, 90)}.get(parts[1] if len(parts) > 1 else "teal")
            top = {"teal": (22, 36, 52), "red": (60, 10, 18), "blue": (22, 26, 56), "green": (18, 34, 30)}.get(parts[1] if len(parts) > 1 else "teal")
            im = studio(top, (8, 8, 14), accent)
        else:
            im = BUILDERS[name]()
        if blur:
            im = im.filter(ImageFilter.GaussianBlur(blur))
        _cache[key] = im
    return _cache[key].copy()
