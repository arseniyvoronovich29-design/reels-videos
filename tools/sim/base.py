"""Shared drawing helpers for the body-simulation videos (fonts, easing, HUD text, anatomy figure, faces, lighting)."""
import sys, math, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

import os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import anatomy as A
import pose as PZ

W, H, FPS, SS = 1080, 1920, 30, 2
T_END = 69.0
FD = os.path.join(HERE, "fonts") + "/"


def F(name, size):
    return ImageFont.truetype(FD + f"Inter-{name}.otf", size)


WHITE = (244, 244, 248)
GREY = (150, 156, 170)
TEAL = (90, 225, 200)
AMBER = (255, 186, 80)
RED = (255, 72, 72)
SAFE_TOP, SAFE_RIGHT, CX = 170, 940, 500


def ease(x):
    x = max(0.0, min(1.0, x))
    return 1 - (1 - x) ** 3


def smooth(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def lerp(a, b, k):
    return a + (b - a) * k


def pw(pts, x):
    if x <= pts[0][0]:
        return pts[0][1]
    for (a, va), (b, vb) in zip(pts, pts[1:]):
        if a <= x <= b:
            return lerp(va, vb, (x - a) / (b - a))
    return pts[-1][1]


def mixc(a, b, k):
    k = max(0.0, min(1.0, k))
    return tuple(int(a[i] * (1 - k) + b[i] * k) for i in range(3))


def plural(n, f1, f2, f5):
    if n % 10 == 1 and n % 100 != 11:
        return f1
    if 2 <= n % 10 <= 4 and not 12 <= n % 100 <= 14:
        return f2
    return f5



def vgrad(top_a, bottom_a, y0, y1, col=(0, 0, 0)):
    arr = np.zeros((H, W, 4), np.uint8)
    yy = np.arange(H)[:, None]
    a = np.clip((yy - y0) / max(y1 - y0, 1), 0, 1)
    arr[..., 0], arr[..., 1], arr[..., 2] = col
    arr[..., 3] = np.broadcast_to(top_a * (1 - a) + bottom_a * a, (H, W)).astype(np.uint8)
    return Image.fromarray(arr, "RGBA")


TOP_SH = vgrad(215, 0, 470, 580)
BOT_SH = vgrad(0, 215, 1330, 1460)
HDRF = F("Medium", 22)
TIMERF = F("Black", 66)
TITLE = F("ExtraBold", 40)
SUBF = F("Medium", 27)
NUMF = F("Bold", 24)
SMALL = F("Medium", 23)
LBLF = F("SemiBold", 24)
VALF = F("Bold", 25)
PULSEF = F("Black", 60)
BIG = F("Black", 150)
QF = F("SemiBold", 40)
HEADER = "СИМУЛЯЦИЯ · ОТКРЫТЫЙ КОСМОС"


def wrap_lines(text, font, maxw):
    out = []
    for para in text.split("\n"):
        cur = ""
        for w in para.split(" "):
            tt = (cur + " " + w).strip()
            if font.getlength(tt) <= maxw or not cur:
                cur = tt
            else:
                out.append(cur)
                cur = w
        out.append(cur)
    return out


def ctext(d, text, font, color, y, al, maxw=800, lh=1.2, shadow=True, cx=CX):
    for ln in wrap_lines(text, font, maxw):
        x = cx - font.getlength(ln) / 2
        if shadow:
            d.text((x + 2, y + 3), ln, font=font, fill=(0, 0, 0, int(160 * al)))
        d.text((x, y), ln, font=font, fill=color + (int(255 * al),))
        y += font.size * lh
    return y



# ---------------- background: dark + red veins ----------------
def make_veins():
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    rr = np.random.default_rng(42)

    def branch(x, y, ang, ln, w, depth):
        if depth == 0 or ln < 8:
            return
        x2, y2 = x + ln * math.cos(ang), y + ln * math.sin(ang)
        d.line((x, y, x2, y2), fill=(150, 20, 30, 150), width=max(1, int(w)))
        branch(x2, y2, ang + rr.uniform(-0.5, 0.5), ln * rr.uniform(0.7, 0.92), w * 0.8, depth - 1)
        if rr.random() < 0.5:
            branch(x2, y2, ang + rr.choice([-1, 1]) * rr.uniform(0.5, 1.1), ln * 0.6, w * 0.6, depth - 2)
    for k in range(14):
        side = k % 4
        if side == 0:
            x, y, a = 0, rr.uniform(0, H), rr.uniform(-0.5, 0.5)
        elif side == 1:
            x, y, a = W, rr.uniform(0, H), math.pi + rr.uniform(-0.5, 0.5)
        elif side == 2:
            x, y, a = rr.uniform(0, W), H, -math.pi / 2 + rr.uniform(-0.5, 0.5)
        else:
            x, y, a = rr.uniform(0, W), 0, math.pi / 2 + rr.uniform(-0.5, 0.5)
        branch(x, y, a, rr.uniform(60, 110), 6, 9)
    return img.filter(ImageFilter.GaussianBlur(1.2))


VEINS = make_veins()


def vig_layer(col, k):
    if "a" not in _vig:
        yy, xx = np.mgrid[0:H, 0:W]
        dx = (xx - W / 2) / (W / 2)
        dy = (yy - H / 2) / (H / 2)
        r = np.sqrt(dx ** 2 * 1.1 + dy ** 2 * 0.6)
        _vig["a"] = np.clip((r - 0.5) / 0.6, 0, 1) ** 1.3
    arr = np.zeros((H, W, 4), np.uint8)
    arr[..., 0], arr[..., 1], arr[..., 2] = col
    arr[..., 3] = (_vig["a"] * 255 * k).astype(np.uint8)
    return Image.fromarray(arr, "RGBA")


_vig = {}


def dark_bg(t, red=0.0):
    rows = np.arange(H, dtype=np.float32)[:, None] / H
    top = np.array(mixc((22, 22, 26), (40, 10, 14), red), np.float32)
    bot = np.array(mixc((10, 10, 12), (20, 4, 6), red), np.float32)
    col = top * (1 - rows) + bot * rows
    img = Image.fromarray(np.ascontiguousarray(np.broadcast_to(col.astype(np.uint8)[:, None, :], (H, W, 3))), "RGB").convert("RGBA")
    # faint grid like the references
    d = ImageDraw.Draw(img)
    for x in range(0, W, 60):
        d.line((x, 0, x, H), fill=(255, 255, 255, 6))
    for y in range(0, H, 60):
        d.line((0, y, W, y), fill=(255, 255, 255, 6))
    if red > 0.05:
        v = VEINS.copy()
        v.putalpha(v.getchannel("A").point(lambda a: int(a * min(1, red))))
        img.alpha_composite(v)
    return img


# ---------------- person drawing ----------------
SKIN0 = (232, 186, 156)
HAIR = (60, 44, 34)
BRAIN_F = A.scale_pts(A.BRAIN, 0.0, 0.008, 0.93, 0.66)


def head_fn(ang, pitch=0.0):
    c = (0.0, 0.125)

    def h(x, y):
        if (ang == 0 and pitch == 0) or y > 0.15:
            return (x, y)
        w = 1.0 if y < 0.12 else smooth((0.15 - y) / 0.03)
        a = ang * w
        ca, sa = math.cos(a), math.sin(a)
        dx, dy = x - c[0], y - c[1]
        dy *= (1 - 0.25 * pitch * w)
        return (c[0] + dx * ca - dy * sa, c[1] + dx * sa + dy * ca)
    return h


def draw_face(d, P, s, expr="normal", t=0.0, skin=SKIN0, sweat=0.0, tears=0.0, brain=False):
    lw = lambda f_: max(1, int(s * f_))
    d.polygon(P([(-0.026, 0.10), (0.026, 0.10), (0.03, 0.17), (-0.03, 0.17)]), fill=mixc(skin, (120, 70, 60), 0.12) + (255,))
    d.polygon(P(A.HEAD), fill=skin + (255,))
    for ex, ey, rx, ry in A.EARS:
        a, b = P([(ex - rx, ey - ry), (ex + rx, ey + ry)])
        d.ellipse(A.box(a, b), fill=skin + (255,))
        a, b = P([(ex - rx * 0.45, ey - ry * 0.6), (ex + rx * 0.45, ey + ry * 0.6)])
        d.ellipse(A.box(a, b), fill=mixc(skin, (150, 90, 80), 0.3) + (220,))
    if brain:
        d.polygon(P(BRAIN_F), fill=(236, 172, 176, 235), outline=(255, 220, 220, 200))
        for k in range(6):
            y = 0.017 + k * 0.0068
            wv = [(-0.032 + j * 0.0064, y + 0.0026 * math.sin(j * 2.1 + k * 1.3)) for j in range(11)]
            d.line(P(wv), fill=(190, 112, 122, 220), width=lw(0.0021), joint="curve")
    hair = [(-0.049, 0.058), (-0.050, 0.030), (-0.041, 0.008), (-0.02, -0.004), (0.0, -0.007), (0.02, -0.004), (0.041, 0.008),
            (0.050, 0.030), (0.049, 0.058), (0.044, 0.044), (0.036, 0.034), (0.02, 0.030), (0.006, 0.034), (-0.01, 0.028), (-0.028, 0.032), (-0.042, 0.042)]
    d.polygon(P(A.catmull(hair, closed=True, n=5)), fill=HAIR + (150 if brain else 255,))
    line = (50, 34, 30, 255)
    shade = mixc(skin, (120, 70, 60), 0.45)
    # expression parameters
    eye_op, brow_lift, brow_in, mouth = 1.0, 0.0, 0.0, "line"
    if expr == "pain":
        eye_op, brow_lift, brow_in, mouth = 0.45, -0.002, 0.004, "grit"
    elif expr == "lock":
        eye_op, brow_lift, brow_in, mouth = 1.15, 0.003, 0.003, "lock"
    elif expr == "grin":
        eye_op, brow_lift, brow_in, mouth = 1.0, 0.007, -0.002, "grin"
    elif expr == "scream":
        eye_op, brow_lift, brow_in, mouth = 0.5, 0.004, 0.004, "scream_lock"
    elif expr == "aware":
        eye_op, brow_lift, brow_in, mouth = 1.1, 0.004, 0.004, "grin_soft"
    elif expr == "happy":
        eye_op, brow_lift, brow_in, mouth = 1.0, 0.003, 0.0, "smile"
    elif expr == "ouch":
        eye_op, brow_lift, brow_in, mouth = 0.3, -0.002, 0.004, "open"
    elif expr == "terror":
        eye_op, brow_lift, brow_in, mouth = 1.45, 0.007, 0.004, "open"
    elif expr == "yell":
        eye_op, brow_lift, brow_in, mouth = 0.55, 0.003, 0.006, "yell"
    elif expr == "cry":
        eye_op, brow_lift, brow_in, mouth = 0.6, 0.005, 0.006, "sob"
    elif expr == "gasp":
        eye_op, brow_lift, brow_in, mouth = 0.85, 0.004, 0.005, "gasp"
    elif expr == "sleep":
        eye_op, brow_lift, brow_in, mouth = 0.2, -0.001, 0.0, "slack"
    for sx in (-1, 1):
        cx, cy = sx * 0.0165, 0.079
        if eye_op < 0.35:
            d.line(P([(cx - 0.009, cy - 0.002), (cx, cy + 0.002), (cx + 0.009, cy - 0.002)]), fill=line, width=lw(0.003), joint="curve")
        else:
            op = eye_op
            a, b = P([(cx - 0.0094, cy - 0.006 * op), (cx + 0.0094, cy + 0.006 * op)])
            d.ellipse(A.box(a, b), fill=(250, 248, 244, 255), outline=line, width=lw(0.0018))
            jit = 0.0012 * math.sin(t * 37 + sx) if expr in ("lock", "aware") else 0.0
            r = 0.0044 * min(1.0, op)
            a, b = P([(cx - r + jit, cy - r), (cx + r + jit, cy + r)])
            d.ellipse(A.box(a, b), fill=(70, 50, 34, 255))
            r2 = 0.0016 if expr in ("lock", "aware", "grin") else 0.0021
            a, b = P([(cx - r2 + jit, cy - r2), (cx + r2 + jit, cy + r2)])
            d.ellipse(A.box(a, b), fill=(10, 8, 8, 255))
            a, b = P([(cx + 0.0008 + jit, cy - 0.0028), (cx + 0.0024 + jit, cy - 0.0012)])
            d.ellipse(A.box(a, b), fill=(255, 255, 255, 240))
            d.arc(A.box(*P([(cx - 0.0096, cy - 0.0062 * op), (cx + 0.0096, cy + 0.0062 * op)])), 200, 340, fill=line, width=lw(0.003))
        d.line(P([(sx * 0.006, 0.0675 - brow_lift + brow_in), (sx * 0.017, 0.0652 - brow_lift), (sx * 0.028, 0.0670 - brow_lift * 0.4)]),
               fill=mixc(HAIR, (0, 0, 0), 0.2) + (255,), width=lw(0.004), joint="curve")
    if brow_lift > 0.004:
        for k in range(3):
            y = 0.050 - k * 0.005
            d.arc(A.box(*P([(-0.02, y - 0.003), (0.02, y + 0.003)])), 200, 340, fill=shade + (180,), width=lw(0.0015))
    d.line(P([(0.002, 0.082), (0.004, 0.094), (0.0, 0.0965)]), fill=shade + (230,), width=lw(0.0024), joint="curve")
    lip = (180, 96, 98)
    teeth = (246, 242, 230)
    if mouth == "line":
        d.line(P(A.catmull([(-0.012, 0.111), (0, 0.1105), (0.012, 0.111)], closed=False, n=6)), fill=lip + (255,), width=lw(0.0036), joint="curve")
    elif mouth == "smile":
        d.line(P(A.catmull([(-0.012, 0.108), (0, 0.112), (0.012, 0.108)], closed=False, n=6)), fill=lip + (255,), width=lw(0.0036), joint="curve")
    elif mouth == "yell":
        pts = [(-0.017, 0.104), (0, 0.101), (0.017, 0.104), (0.013, 0.123), (0, 0.128), (-0.013, 0.123)]
        d.polygon(P(A.catmull(pts, closed=True, n=6)), fill=(60, 18, 24, 255), outline=lip + (255,))
        d.polygon(P([(-0.013, 0.1045), (0.013, 0.1045), (0.011, 0.1085), (-0.011, 0.1085)]), fill=teeth + (255,))
        a, b = P([(-0.009, 0.117), (0.009, 0.127)])
        d.ellipse(A.box(a, b), fill=(190, 80, 90, 255))
    elif mouth == "gasp":
        a, b = P([(-0.008, 0.103), (0.008, 0.122)])
        d.ellipse(A.box(a, b), fill=(60, 18, 24, 255), outline=lip + (255,), width=lw(0.0025))
    elif mouth == "sob":
        pts = [(-0.012, 0.110), (0, 0.105), (0.012, 0.110), (0.008, 0.116), (-0.008, 0.116)]
        d.polygon(P(A.catmull(pts, closed=True, n=6)), fill=(70, 26, 32, 255), outline=lip + (255,))
    elif mouth == "slack":
        a, b = P([(-0.006, 0.108), (0.006, 0.114)])
        d.ellipse(A.box(a, b), fill=(80, 34, 40, 255), outline=lip + (255,), width=lw(0.002))
    elif mouth == "open":
        a, b = P([(-0.009, 0.104), (0.009, 0.118)])
        d.ellipse(A.box(a, b), fill=(70, 26, 32, 255), outline=lip + (255,), width=lw(0.0025))
    elif mouth in ("grit", "lock", "scream_lock"):
        wdt = 0.013 if mouth == "grit" else 0.016
        h = 0.006 if mouth != "scream_lock" else 0.009
        poly = [(-wdt, 0.110), (wdt, 0.110), (wdt * 0.9, 0.110 + h), (-wdt * 0.9, 0.110 + h)]
        d.polygon(P(poly), fill=teeth + (255,), outline=lip + (255,))
        d.line(P([(-wdt * 0.95, 0.110 + h / 2), (wdt * 0.95, 0.110 + h / 2)]), fill=(150, 140, 130, 255), width=lw(0.0012))
        for k in range(1, 8):
            x = -wdt + k * wdt * 2 / 8
            d.line(P([(x, 0.110), (x, 0.110 + h)]), fill=(170, 160, 150, 255), width=lw(0.0010))
        if mouth == "lock":
            # tense jaw muscles (masseters)
            for sx in (-1, 1):
                a, b = P([(sx * 0.031 - 0.006, 0.096), (sx * 0.031 + 0.006, 0.116)])
                d.ellipse(A.box(a, b), fill=(220, 90, 90, int(70 + 60 * abs(math.sin(t * 6)))))
    elif mouth in ("grin", "grin_soft"):
        k = 1.0 if mouth == "grin" else 0.7
        wdt = 0.020 * k + 0.004
        pts = [(-wdt, 0.104), (0, 0.1105), (wdt, 0.104), (wdt * 0.85, 0.1135), (0, 0.1175), (-wdt * 0.85, 0.1135)]
        d.polygon(P(A.catmull(pts, closed=True, n=6)), fill=teeth + (255,), outline=lip + (255,))
        d.line(P(A.catmull([(-wdt * 0.92, 0.108), (0, 0.113), (wdt * 0.92, 0.108)], closed=False, n=6)), fill=(150, 140, 130, 255), width=lw(0.0012))
        for k2 in range(1, 9):
            x = -wdt + k2 * wdt * 2 / 9
            d.line(P([(x, 0.106 + 0.004 * (1 - abs(x) / wdt)), (x, 0.113 + 0.003 * (1 - abs(x) / wdt))]), fill=(170, 160, 150, 255), width=lw(0.0010))
        for sx in (-1, 1):
            d.line(P([(sx * wdt, 0.104), (sx * (wdt + 0.006), 0.100)]), fill=shade + (230,), width=lw(0.0022))
            d.line(P([(sx * 0.028, 0.090), (sx * 0.034, 0.104)]), fill=shade + (200,), width=lw(0.0018))
    if sweat > 0.05:
        rr = np.random.default_rng(3)
        for j in range(int(9 * sweat)):
            ph = (t * 0.3 + j * 0.13) % 1.0
            x = rr.uniform(-0.038, 0.038)
            y = 0.03 + 0.09 * ph
            a, b = P([(x - 0.0024, y - 0.0034), (x + 0.0024, y + 0.0034)])
            d.ellipse(A.box(a, b), fill=(210, 235, 255, int(230 * sweat)), outline=(255, 255, 255, int(220 * sweat)))
    if tears > 0.05:
        for sx in (-1, 1):
            ph = (t * 0.5 + (sx > 0) * 0.4) % 1.0
            y0 = 0.086
            pts = [(sx * 0.019, y0), (sx * 0.021, y0 + 0.02 * ph)]
            d.line(P(pts), fill=(170, 210, 255, int(220 * tears)), width=lw(0.003))
            a, b = P([(sx * 0.021 - 0.002, y0 + 0.02 * ph - 0.002), (sx * 0.021 + 0.002, y0 + 0.02 * ph + 0.003)])
            d.ellipse(A.box(a, b), fill=(170, 210, 255, int(240 * tears)))


def person(img, T0, pose, s, mode="opaque", expr="normal", t=0.0, outfit="dacha", extras=None, warp=None, skin=SKIN0, sweat=0.0, tears=0.0):
    pf = PZ.make_pose(pose)
    hf = head_fn(pose.get("head", 0.0), pose.get("pitch", 0.0))
    W_ = warp if warp else (lambda p: p)

    def T(x, y):
        return T0(*W_(pf(*hf(x, y))))

    def Tg(x, y):
        return T0(*W_(pf.glob((x, y))))

    def Th(x, y):
        return T0(*W_(pf.glob(hf(x, y))))
    st = {"s": s, "core": 0, "limb": 0, "skin": skin, "no_brain": True, "body_alpha": 1.0 if mode == "opaque" else 0.45,
          "T_limb": Tg, "T_body": Th, "chains": pf.chains, "breath": 1.0 + 0.03 * math.sin(t * 3), "beat": 1.0 + 0.05 * abs(math.sin(t * 7))}
    if extras:
        st.update(extras)
    body, org = A.draw_figure(img.size, T, st)
    img.alpha_composite(body)
    cl = Image.new("RGBA", img.size, (0, 0, 0, 0))
    cd = ImageDraw.Draw(cl)
    if outfit:
        ca = 255 if mode == "opaque" else 120
        shirt_c = {"dacha": (70, 120, 90), "suit": (38, 40, 50), "caver": (196, 110, 40), "casual": (176, 52, 62), "swim": None}.get(outfit, (150, 190, 200))
        torso = A.scale_pts(A.TORSO, 0.0, 0.3, 1.05, 1.0)
        if shirt_c is None:
            cd.polygon([Th(-0.106, 0.42), Th(0.106, 0.42), Th(0.104, 0.53), Th(-0.104, 0.53)], fill=(30, 90, 170, ca))
            for side in ("r", "l"):
                poly, _ = A.limb_poly(pf.chains["leg_" + side][:2], [w * 1.12 for w in A.LEG_W[:2]], n=4)
                cd.polygon([Tg(*p) for p in poly], fill=(30, 90, 170, ca))
            outfit = None
        if outfit is not None:
            cd.polygon([Th(x_, min(y_, 0.462)) for x_, y_ in torso], fill=shirt_c + (ca,))
            cd.arc(A.box(Th(-0.035, 0.145), Th(0.035, 0.185)), 0, 180, fill=mixc(shirt_c, (20, 20, 20), 0.4) + (ca,), width=max(2, int(0.005 * s)))
            for side in ("r", "l"):
                poly, _ = A.limb_poly(pf.chains["arm_" + side][:3], [w * 1.3 for w in A.ARM_W[:3]], n=6)
                cd.polygon([Tg(*p) for p in poly], fill=shirt_c + (ca,))
                j0 = pf.chains["arm_" + side][0]
                a_, b_ = Tg(j0[0] - A.ARM_W[0] * 0.6, j0[1] - A.ARM_W[0] * 0.6), Tg(j0[0] + A.ARM_W[0] * 0.6, j0[1] + A.ARM_W[0] * 0.6)
                cd.ellipse(A.box(a_, b_), fill=shirt_c + (ca,))
            if outfit == "suit":
                cd.polygon([Th(-0.03, 0.16), Th(0.03, 0.16), Th(0.0, 0.27)], fill=(240, 240, 244, ca))
                cd.polygon([Th(-0.008, 0.175), Th(0.008, 0.175), Th(0.012, 0.25), Th(0.0, 0.265), Th(-0.012, 0.25)], fill=(120, 20, 30, ca))
            if outfit in ("dacha", "suit", "caver", "casual", "hosp"):
                pants = {"dacha": (60, 70, 110), "suit": (32, 34, 42), "caver": (176, 98, 36), "casual": (52, 66, 102), "hosp": (130, 172, 186)}[outfit]
                cd.polygon([Th(-0.112, 0.44), Th(0.112, 0.44), Th(0.10, 0.52), Th(-0.10, 0.52)], fill=pants + (ca,))
                for side in ("r", "l"):
                    poly, _ = A.limb_poly(pf.chains["leg_" + side][:5], [w * 1.12 for w in A.LEG_W[:5]], n=6)
                    cd.polygon([Tg(*p) for p in poly], fill=pants + (ca,))
    img.alpha_composite(cl)
    if mode == "xray":
        img.alpha_composite(org)
    face = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw_face(ImageDraw.Draw(face), lambda pts: [Th(x, y) for x, y in pts], s, expr=expr, t=t, skin=skin, sweat=sweat, tears=tears, brain=(mode == "xray"))
    img.alpha_composite(face)
    if outfit == "caver":
        hd = ImageDraw.Draw(img)
        dome = [(-0.058, 0.052), (-0.054, 0.024), (-0.040, 0.000), (-0.018, -0.014), (0.0, -0.017), (0.018, -0.014), (0.040, 0.000), (0.054, 0.024), (0.058, 0.052), (0.0, 0.046)]
        hd.polygon([Th(*p) for p in A.catmull(dome, closed=True, n=4)], fill=(232, 192, 44, 255), outline=(150, 120, 20, 255))
        hd.line([Th(-0.064, 0.054), Th(0.0, 0.048), Th(0.064, 0.054)], fill=(190, 150, 30, 255), width=max(2, int(0.006 * s)), joint="curve")
        la, lb = Th(-0.012, 0.004), Th(0.012, 0.026)
        hd.ellipse(A.box(la, lb), fill=(255, 250, 220, 255), outline=(90, 90, 90, 255), width=max(1, int(0.003 * s)))
        ga, gb = Th(-0.022, -0.006), Th(0.022, 0.036)
        hd.ellipse(A.box(ga, gb), outline=(255, 245, 200, 120), width=max(2, int(0.006 * s)))
        hd.ellipse(A.box(Th(-0.007, 0.009), Th(0.007, 0.021)), fill=(255, 255, 255, 255))
    return T, Tg, pf


def mkT0(cx, cy, z, FH=900.0, FX=540.0, FY=620.0):
    def T0(x, y):
        return (((FX + x * FH - cx) * z + W / 2) * SS, ((FY + y * FH - cy) * z + H / 2) * SS)
    return T0, FH * z * SS


def big(t_img):
    return t_img.convert("RGB").resize((W, H), Image.LANCZOS).convert("RGBA")


def xray_base(t, red):
    bg = dark_bg(t, red).resize((W * SS, H * SS))
    return bg


def labels_block(d, T, items, al=1.0):
    vf = F("ExtraBold", 26)
    for name, val, col, anchor, side, y in items:
        lx0, lx1 = (56, 300) if side < 0 else (720, SAFE_RIGHT - 6)
        an = lx1 if side < 0 else lx0
        d.rounded_rectangle((lx0 - 10, y - 64, lx1 + 10, y + 12), radius=12, fill=(8, 10, 18, int(190 * al)))
        d.text((lx0, y - 58), name, font=F("SemiBold", 23), fill=(215, 220, 230, int(255 * al)))
        d.text((lx1 - vf.getlength(val), y - 31), val, font=vf, fill=col + (int(255 * al),))
        d.line((lx0, y + 2, lx1, y + 2), fill=col + (int(220 * al),), width=4)
        if anchor:
            ox, oy = T(*anchor)
            ox, oy = ox / SS, oy / SS
            d.line((an, y + 2, ox, oy), fill=(255, 255, 255, int(110 * al)), width=2)
            d.ellipse((ox - 6, oy - 6, ox + 6, oy + 6), fill=col + (int(255 * al),))

def speech(d, x, y, text, al, tail="left"):
    if al <= 0:
        return
    f = F("Bold", 30)
    w = f.getlength(text) + 36
    if x + w > SAFE_RIGHT:
        x = SAFE_RIGHT - w
    d.rounded_rectangle((x, y, x + w, y + 54), radius=18, fill=(250, 250, 250, int(255 * al)))
    tx = x + 30 if tail == "left" else x + w - 30
    d.polygon([(tx - 10, y + 52), (tx + 10, y + 52), (tx - 4, y + 76)], fill=(250, 250, 250, int(255 * al)))
    d.text((x + 18, y + 10), text, font=f, fill=(20, 20, 24, int(255 * al)))


def ImageChops_offset(img, dx, dy):
    out = Image.new("RGBA", img.size, (0, 0, 0, 255))
    out.paste(img, (dx, dy))
    return out



# ---------------- lighting helpers ----------------
_rad = {}


def radial(size, cx, cy, r):
    key = (size, int(cx) // 4, int(cy) // 4, int(r) // 4)
    if key not in _rad:
        w, h = size
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / r
        _rad[key] = np.clip(1 - d, 0, 1) ** 1.6
        if len(_rad) > 60:
            _rad.pop(next(iter(_rad)))
    return _rad[key]


def light(img, cx, cy, r, k, amb=0.08, tint=(255, 214, 160)):
    """darken everything except a warm pool of light (phone torch)"""
    a = np.asarray(img).astype(np.float32)
    L = radial(img.size, cx, cy, r) * k
    m = amb + (1 - amb) * L
    tn = np.array(tint, np.float32) / 255.0
    rgb = a[..., :3] * m[..., None] * (tn * L[..., None] + (1 - L[..., None]))
    out = np.concatenate([np.clip(rgb, 0, 255), a[..., 3:]], axis=2).astype(np.uint8)
    return Image.fromarray(out, "RGBA")


def flicker(t, base=1.0):
    n = 0.5 + 0.5 * math.sin(t * 37) * math.sin(t * 23.3)
    return base * (0.88 + 0.12 * n)


