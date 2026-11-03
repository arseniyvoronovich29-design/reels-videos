"""Shot-based engine for the «что будет с телом, если…» simulation videos.

A video is described by a spec file (see ../../videos/*/spec.py and STYLE.md).
Usage:
    python engine.py check  <spec.py> [t1,t2,...]   -> contact sheet next to the spec (sheet.png)
    python engine.py render <spec.py>               -> <slug>.mp4 next to the spec (video + sound)
    python engine.py part   <spec.py> <t0> <t1> <out.mp4>   (internal)
"""
import os, sys, math, subprocess, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from base import *          # noqa: F401,F403
import base as B

YEL = (255, 206, 60)
TAGRED = (210, 40, 46)
S = {}            # the loaded spec
SHOTS = []
HRv = PHASE = None
N = 0
T_END = 60.0
SPEC_MOD = None


# ======================================================================
# spec loading / timeline
# ======================================================================
def load(path):
    global S, SHOTS, HRv, PHASE, N, T_END, SPEC_MOD
    spec = importlib.util.spec_from_file_location("spec", path)
    m = importlib.util.module_from_spec(spec)
    m.__dict__["E"] = sys.modules[__name__]
    for k in ("WHITE", "RED", "AMBER", "TEAL", "GREY", "YEL", "SKIN0", "math", "np", "Image", "ImageDraw", "ImageFilter", "F", "ease", "smooth", "lerp", "pw", "mixc", "SS", "W", "H", "A"):
        m.__dict__[k] = globals()[k]
    spec.loader.exec_module(m)
    SPEC_MOD = m
    S = m.SPEC
    S["_dir"] = os.path.dirname(os.path.abspath(path))
    SHOTS = []
    t = 0.0
    for sh in S["shots"]:
        d = dict(sh)
        d["t0"] = t
        d["t1"] = t + d.get("dur", 3.0)
        t = d["t1"]
        SHOTS.append(d)
    T_END = t
    S["T_END"] = T_END
    HRv = np.zeros(int(T_END * FPS) + 2)
    pts = S.get("hr", [(0, 80), (T_END, 80)])
    for i in range(len(HRv)):
        HRv[i] = pw(pts, i / FPS)
    PHASE = np.cumsum(HRv / 60 / FPS)
    N = len(HRv)
    return S


def shot_at(t):
    for i, s in enumerate(SHOTS):
        if s["t0"] <= t < s["t1"]:
            return i, s
    return len(SHOTS) - 1, SHOTS[-1]


def shot_named(name):
    for s in SHOTS:
        if s.get("name") == name:
            return s
    return None


def phase_at(t):
    x = t * FPS
    i = int(np.clip(x, 0, N - 2))
    return PHASE[i] + (PHASE[i + 1] - PHASE[i]) * (x - i)


def hr_at(t):
    return HRv[min(int(max(t, 0) * FPS), N - 1)]


def ecg_at(tt):
    if hr_at(tt) < 1:
        return 0.0
    p = phase_at(tt) % 1.0
    v = 0.12 * math.exp(-((p - 0.12) / 0.035) ** 2)
    v -= 0.15 * math.exp(-((p - 0.235) / 0.012) ** 2)
    v += 1.0 * math.exp(-((p - 0.26) / 0.012) ** 2)
    v -= 0.28 * math.exp(-((p - 0.285) / 0.014) ** 2)
    v += 0.26 * math.exp(-((p - 0.48) / 0.05) ** 2)
    if S.get("ecg_noise") and S["ecg_noise"][0] <= tt < S["ecg_noise"][1]:
        v += 0.22 * math.sin(tt * 90)
    return v


def beat_pulse(t):
    if hr_at(t) < 1:
        return 0.0
    return math.exp(-((((phase_at(t) % 1.0) - 0.26) * 6) ** 2))


def val(spec_val, u, t=None):
    """a number or a list of (u, value) keyframes over the shot"""
    if isinstance(spec_val, (list, tuple)) and spec_val and isinstance(spec_val[0], (list, tuple)):
        return pw(spec_val, u)
    return spec_val


# ======================================================================
# generic drawing helpers
# ======================================================================
def grad(c_top, c_bot, w=W, h=H):
    rows = np.arange(h, dtype=np.float32)[:, None] / h
    col = np.array(c_top, np.float32) * (1 - rows) + np.array(c_bot, np.float32) * rows
    return Image.fromarray(np.ascontiguousarray(np.broadcast_to(col.astype(np.uint8)[:, None, :], (h, w, 3))), "RGB").convert("RGBA")


def blur_layer(draw_fn, size=(W, H), r=20):
    lay = Image.new("RGBA", size, (0, 0, 0, 0))
    draw_fn(ImageDraw.Draw(lay))
    return lay.filter(ImageFilter.GaussianBlur(r))


def text_pop(d, txt, x, y, size, t_rel, col=(255, 220, 60)):
    if t_rel < 0:
        return
    pop = 1 + 0.4 * (1 - ease(t_rel / 0.2))
    f = F("Black", int(size * pop))
    w = f.getlength(txt)
    x = min(max(x - w / 2, 60), SAFE_RIGHT - w)
    d.text((x + 5, y + 6), txt, font=f, fill=(0, 0, 0, 220))
    d.text((x, y), txt, font=f, fill=col + (255,))


def stamp(img, word, x, y, al, rot=-12, col=(230, 40, 50), size=80):
    f = F("Black", size)
    w = int(f.getlength(word) + 60)
    st = Image.new("RGBA", (w, int(size * 1.7)), (0, 0, 0, 0))
    sd = ImageDraw.Draw(st)
    sd.rounded_rectangle((6, 6, w - 6, int(size * 1.7) - 6), radius=16, outline=col + (255,), width=8)
    sd.text((30, int(size * 0.2)), word, font=f, fill=col + (255,))
    st = st.rotate(rot, expand=True, resample=Image.BICUBIC)
    st.putalpha(st.getchannel("A").point(lambda a: int(a * al)))
    img.alpha_composite(st, (int(x), int(y)))


def droop_warp(k):
    """stroke: the right side of the face sags (screen-left)"""
    if k <= 0:
        return None

    def w(p):
        x, y = p
        if y < 0.15 and x < 0:
            m = min(1.0, -x / 0.04) * (1 if 0.06 < y < 0.14 else 0.4)
            return (x, y + 0.016 * k * m)
        return p
    return w


# ======================================================================
# scene presets (drawn at SS scale)
# ======================================================================
def P(x, y):
    return (x * SS, y * SS)


def bg_preset(img, d, name, t, sh):
    Wd, Hd = W * SS, H * SS
    gy = sh.get("ground", 1300) * SS
    if name == "forest":
        img.alpha_composite(grad((150, 180, 170), (226, 214, 170), Wd, Hd))
        d = ImageDraw.Draw(img)
        rr = np.random.default_rng(4)
        for k in range(14):
            x = rr.uniform(-50, 1130) * SS
            w = rr.uniform(30, 70) * SS
            c = int(rr.uniform(60, 100))
            d.rectangle((x - w / 2, 0, x + w / 2, gy), fill=(c, c - 14, c - 28, 255))
        for k in range(10):
            x = rr.uniform(0, 1080) * SS
            r = rr.uniform(120, 260) * SS
            d.ellipse((x - r, -r * 0.4, x + r, r * 0.9), fill=(190, 120, 40, 255) if k % 2 else (150, 150, 50, 255))
        d.rectangle((0, gy, Wd, Hd), fill=(120, 90, 50, 255))
        for k in range(160):
            x, y = rr.uniform(0, Wd), rr.uniform(gy, Hd)
            r = rr.uniform(4, 10) * SS
            d.ellipse((x - r, y - r * 0.5, x + r, y + r * 0.5), fill=(200, 110, 30, 255) if k % 3 else (170, 60, 30, 255))
    elif name == "kitchen":
        img.alpha_composite(grad((214, 206, 190), (190, 180, 162), Wd, Hd))
        d = ImageDraw.Draw(img)
        for y in range(0, int(gy), 60 * SS):
            d.line((0, y, Wd, y), fill=(200, 192, 176, 255), width=2 * SS)
        for x in range(0, Wd, 60 * SS):
            d.line((x, 0, x, gy), fill=(200, 192, 176, 255), width=2 * SS)
        d.rectangle((640 * SS, 560 * SS, 980 * SS, 900 * SS), fill=(40, 50, 80, 255), outline=(240, 240, 240, 255), width=10 * SS)
        d.line((810 * SS, 560 * SS, 810 * SS, 900 * SS), fill=(240, 240, 240, 255), width=8 * SS)
        d.rectangle((0, gy, Wd, Hd), fill=(150, 120, 90, 255))
    elif name == "beach":
        img.alpha_composite(grad((90, 170, 230), (200, 230, 250), Wd, Hd))
        d = ImageDraw.Draw(img)
        d.ellipse((800 * SS, 380 * SS, 920 * SS, 500 * SS), fill=(255, 240, 180, 255))
        hy = min(900 * SS, gy - 220 * SS)
        d.rectangle((0, hy, Wd, gy), fill=(30, 120, 170, 255))
        for k in range(10):
            yy = hy + k * 40 * SS
            d.line([(x, yy + 6 * SS * math.sin(x / (40 * SS) + t * 2 + k)) for x in range(0, Wd + 40, 40)], fill=(120, 200, 230, 255), width=3 * SS)
        d.rectangle((0, gy, Wd, Hd), fill=(232, 210, 160, 255))
    elif name == "sea":
        sy = sh.get("surface", 900) * SS
        img.alpha_composite(grad((90, 170, 230), (200, 230, 250), Wd, Hd))
        d = ImageDraw.Draw(img)
        under = grad((20, 110, 160), (6, 30, 60), Wd, Hd - int(sy))
        img.alpha_composite(under, (0, int(sy)))
        d = ImageDraw.Draw(img)
    elif name == "bedroom":
        img.alpha_composite(grad((40, 44, 64), (24, 26, 40), Wd, Hd))
        d = ImageDraw.Draw(img)
        d.rectangle((120 * SS, 560 * SS, 380 * SS, 860 * SS), fill=(20, 26, 50, 255), outline=(90, 90, 110, 255), width=8 * SS)
        d.rectangle((0, gy, Wd, Hd), fill=(70, 50, 40, 255))
        # door with fire glow underneath
        d.rectangle((760 * SS, 700 * SS, 1000 * SS, gy), fill=(90, 60, 40, 255))
    elif name == "street":
        img.alpha_composite(grad((160, 190, 220), (220, 226, 230), Wd, Hd))
        d = ImageDraw.Draw(img)
        rr = np.random.default_rng(7)
        x = 0
        while x < Wd:
            w = rr.uniform(140, 260) * SS
            h = rr.uniform(500, 900) * SS
            c = int(rr.uniform(120, 170))
            d.rectangle((x, gy - h, x + w, gy), fill=(c, c + 4, c + 12, 255))
            for wy in range(int(gy - h + 30 * SS), int(gy - 40 * SS), 70 * SS):
                for wx in range(int(x + 20 * SS), int(x + w - 30 * SS), 60 * SS):
                    d.rectangle((wx, wy, wx + 30 * SS, wy + 40 * SS), fill=(200, 220, 240, 255))
            x += w + 10 * SS
        d.rectangle((0, gy, Wd, Hd), fill=(150, 150, 156, 255))
    elif name == "office":
        img.alpha_composite(grad((200, 204, 210), (170, 174, 182), Wd, Hd))
        d = ImageDraw.Draw(img)
        d.rectangle((0, gy, Wd, Hd), fill=(110, 110, 120, 255))
    elif name == "hospital":
        img.alpha_composite(grad((26, 34, 40), (14, 18, 22), Wd, Hd))
        d = ImageDraw.Draw(img)
        d.rectangle((0, gy, Wd, Hd), fill=(40, 46, 52, 255))
    elif name == "night":
        img.alpha_composite(grad((8, 12, 30), (34, 30, 50), Wd, Hd))
        d = ImageDraw.Draw(img)
        d.rectangle((0, gy, Wd, Hd), fill=(40, 36, 34, 255))
    else:
        img.alpha_composite(grad((20, 20, 26), (8, 8, 10), Wd, Hd))
    return ImageDraw.Draw(img)


def draw_props(img, d, props, t, u, T0, s, sh, T=None):
    for pr in props or []:
        name = pr if isinstance(pr, str) else pr[0]
        opt = {} if isinstance(pr, str) else pr[1]
        if name == "bed":
            a, b = T0(-0.62, 0.70), T0(0.62, 0.78)
            d.rounded_rectangle(A.box(a, b), radius=12 * SS, fill=opt.get("col", (190, 196, 206)) + (255,))
            for xx in (-0.56, 0.56):
                a, b = T0(xx - 0.01, 0.78), T0(xx + 0.01, 1.0)
                d.rectangle(A.box(a, b), fill=(140, 146, 156, 255))
        elif name == "table":
            a, b = T0(opt.get("x0", 0.12), opt.get("y", 0.56)), T0(opt.get("x1", 0.62), opt.get("y", 0.56) + 0.03)
            d.rectangle(A.box(a, b), fill=(140, 96, 60, 255))
            for xx in (opt.get("x0", 0.12) + 0.03, opt.get("x1", 0.62) - 0.03):
                a, b = T0(xx - 0.01, opt.get("y", 0.56) + 0.03), T0(xx + 0.01, 1.0)
                d.rectangle(A.box(a, b), fill=(120, 80, 50, 255))
        elif name == "plate":
            x, y = opt.get("at", (0.3, 0.55))
            a, b = T0(x - 0.08, y - 0.015), T0(x + 0.08, y + 0.01)
            d.ellipse(A.box(a, b), fill=(245, 245, 245, 255), outline=(200, 200, 200, 255))
            for k in range(5):
                mx = x - 0.05 + k * 0.025
                a, b = T0(mx - 0.014, y - 0.03), T0(mx + 0.014, y - 0.012)
                d.chord(A.box(a, b), 180, 360, fill=opt.get("cap", (170, 180, 140)) + (255,))
                a, b = T0(mx - 0.004, y - 0.022), T0(mx + 0.004, y - 0.005)
                d.rectangle(A.box(a, b), fill=(240, 236, 220, 255))
        elif name == "jar":
            x, y = opt.get("at", (0.3, 0.55))
            a, b = T0(x - 0.035, y - 0.11), T0(x + 0.035, y)
            d.rounded_rectangle(A.box(a, b), radius=int(0.01 * s), fill=(200, 220, 230, 160), outline=(230, 240, 245, 255), width=max(2, int(0.003 * s)))
            a, b = T0(x - 0.03, y - 0.08), T0(x + 0.03, y - 0.004)
            d.rounded_rectangle(A.box(a, b), radius=int(0.008 * s), fill=opt.get("fill", (150, 120, 60)) + (230,))
            a, b = T0(x - 0.038, y - 0.125), T0(x + 0.038, y - 0.105)
            d.rectangle(A.box(a, b), fill=(200, 180, 60, 255))
            if opt.get("bulge"):
                a, b = T0(x - 0.04, y - 0.14), T0(x + 0.04, y - 0.11)
                d.chord(A.box(a, b), 180, 360, fill=(200, 180, 60, 255))
        elif name == "basket":
            x, y = opt.get("at", (0.2, 0.62))
            a, b = T0(x - 0.07, y - 0.06), T0(x + 0.07, y)
            d.chord(A.box(T0(x - 0.07, y - 0.12), T0(x + 0.07, y)), 0, 180, fill=(170, 120, 60, 255))
            d.arc(A.box(T0(x - 0.06, y - 0.16), T0(x + 0.06, y - 0.02)), 180, 360, fill=(140, 96, 50, 255), width=max(2, int(0.008 * s)))
            for k in range(4):
                mx = x - 0.045 + k * 0.03
                d.chord(A.box(T0(mx - 0.018, y - 0.085), T0(mx + 0.018, y - 0.045)), 180, 360, fill=opt.get("cap", (170, 180, 140)) + (255,))
        elif name == "mushroom":
            x, y = opt.get("at", (0.3, 1.0))
            sc = opt.get("size", 0.06)
            d.rectangle(A.box(T0(x - sc * 0.15, y - sc * 1.1), T0(x + sc * 0.15, y)), fill=(245, 242, 230, 255))
            d.ellipse(A.box(T0(x - sc * 0.3, y - sc * 0.25), T0(x + sc * 0.3, y + sc * 0.05)), fill=(240, 236, 224, 255))   # volva
            d.rectangle(A.box(T0(x - sc * 0.22, y - sc * 0.75), T0(x + sc * 0.22, y - sc * 0.68)), fill=(235, 232, 220, 255))   # ring
            d.chord(A.box(T0(x - sc * 0.6, y - sc * 1.55), T0(x + sc * 0.6, y - sc * 0.75)), 180, 360, fill=opt.get("cap", (170, 180, 140)) + (255,))
        elif name == "phone":
            x, y = opt.get("at", (0.3, 0.3))
            d.rounded_rectangle(A.box(T0(x - 0.02, y - 0.04), T0(x + 0.02, y + 0.04)), radius=int(0.006 * s), fill=(20, 20, 24, 255))
            d.rectangle(A.box(T0(x - 0.016, y - 0.034), T0(x + 0.016, y + 0.032)), fill=opt.get("screen", (120, 200, 255)) + (255,))
        elif name == "monitor":
            x, y = opt.get("at", (0.42, 0.25))
            a, b = T0(x - 0.09, y - 0.07), T0(x + 0.09, y + 0.07)
            d.rounded_rectangle(A.box(a, b), radius=int(0.01 * s), fill=(20, 24, 30, 255), outline=(120, 130, 140, 255), width=max(2, int(0.003 * s)))
            pts = []
            for k in range(60):
                xx = lerp(a[0] + 0.01 * s, b[0] - 0.01 * s, k / 59)
                tt = t - (59 - k) / 59 * 2.5
                pts.append((xx, (a[1] + b[1]) / 2 - ecg_at(tt) * 0.03 * s))
            d.line(pts, fill=(90, 255, 140, 255), width=max(2, int(0.003 * s)))
        elif name == "iv":
            x = opt.get("x", -0.5)
            d.rectangle(A.box(T0(x - 0.004, 0.0), T0(x + 0.004, 0.75)), fill=(170, 176, 186, 255))
            d.rounded_rectangle(A.box(T0(x - 0.04, 0.02), T0(x + 0.04, 0.14)), radius=int(0.01 * s), fill=(220, 235, 245, 200), outline=(240, 250, 255, 255))
        elif name == "lamp_or":
            lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
            ImageDraw.Draw(lay).polygon([T0(-0.1, -0.4), T0(0.1, -0.4), T0(0.6, 0.75), T0(-0.6, 0.75)], fill=(220, 240, 255, 50))
            img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(20 * SS)))
            d = ImageDraw.Draw(img)
        elif name == "fire":
            k = val(opt.get("k", 1.0), u)
            lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
            ld = ImageDraw.Draw(lay)
            x0, x1 = opt.get("x", (700, 1080))
            rr = np.random.default_rng(int(t * 12))
            gy = sh.get("ground", 1300)
            for j in range(40):
                x = rr.uniform(x0, x1)
                h = rr.uniform(80, 420) * k
                w = rr.uniform(30, 80)
                ld.polygon([P(x - w, gy), P(x, gy - h), P(x + w, gy)], fill=(255, int(rr.uniform(80, 200)), 20, 200))
            img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(6 * SS)))
            d = ImageDraw.Draw(img)
    return d


def overlay_effects(out, sh, t, u):
    """post effects on the W×H frame"""
    sm = val(sh.get("smoke", 0), u)
    if sm:
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ld = ImageDraw.Draw(lay)
        top = int(lerp(400, 1700, sm))
        ld.rectangle((0, 0, W, top), fill=(70, 70, 76, int(180 * min(1, sm * 1.4))))
        for k in range(10):
            x = (k * 180 + t * 60 * (1 + k % 3)) % (W + 400) - 200
            ld.ellipse((x - 260, top - 120, x + 260, top + 80), fill=(80, 80, 86, 160))
        out.alpha_composite(lay.filter(ImageFilter.GaussianBlur(24)))
    if sh.get("water_tint"):
        out.alpha_composite(Image.new("RGBA", (W, H), (20, 80, 140, int(90 * sh["water_tint"]))))
    if sh.get("lighting"):
        lx, ly, r, k, amb, tint = sh["lighting"]
        out = light(out, lx, ly, r, flicker(t, k) if sh.get("flicker") else k, amb=amb, tint=tint)
    dist = val(sh.get("distort", 0), u)
    if dist:
        a = np.asarray(out).copy()
        shf = int((10 + 10 * math.sin(t * 3)) * dist)
        a[..., 0] = np.roll(a[..., 0], shf, axis=1)
        a[..., 2] = np.roll(a[..., 2], -shf, axis=1)
        rows = np.arange(H)
        off = (10 * dist * np.sin(rows / 40.0 + t * 6)).astype(int)
        for y in range(0, H, 4):
            a[y:y + 4] = np.roll(a[y:y + 4], off[y], axis=1)
        out = Image.fromarray(a, "RGBA").filter(ImageFilter.GaussianBlur(1.2 * dist))
    dk = val(sh.get("dark", 0), u)
    if dk:
        out.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, int(255 * min(1, dk)))))
    return out


# ======================================================================
# shot kinds
# ======================================================================
def cam_of(sh, u):
    c = sh.get("cam", (0.0, 0.5, 1.0))
    if isinstance(c[0], (list, tuple)):
        a, b = c
        k = ease(u)
        return tuple(lerp(a[i], b[i], k) for i in range(3))
    return c


def T0_for(cam):
    """cam = (body_x, body_y, zoom): that body point goes to screen (540, 900)"""
    bx, by, z = cam
    FH = 900.0

    def T0(x, y):
        return ((540 + (x - bx) * FH * z) * SS, (900 + (y - by) * FH * z) * SS)
    return T0, FH * z * SS


def shot_scene(t, u, sh):
    img = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 255))
    d = ImageDraw.Draw(img)
    d = bg_preset(img, d, sh.get("preset", "dark"), t, sh)
    cam = cam_of(sh, u)
    T0, s = T0_for(cam)
    d = draw_props(img, d, sh.get("props_back"), t, u, T0, s, sh)
    T = None
    if sh.get("person", True):
        pose = dict(val(sh.get("pose", {}), u)) if not callable(sh.get("pose")) else sh["pose"](t, u)
        warp = None
        if sh.get("droop"):
            warp = droop_warp(val(sh["droop"], u))
        if sh.get("pose_warp"):
            warp = sh["pose_warp"](t, u)
        T, Tg, pf = person(img, T0, pose, s, mode=sh.get("mode", "opaque"), expr=sh.get("expr", "normal") if not callable(sh.get("expr")) else sh["expr"](t, u),
                           t=t, outfit=sh.get("outfit", "casual") if sh.get("mode", "opaque") == "opaque" else None,
                           extras=sh.get("extras"), skin=sh.get("skin", SKIN0), sweat=sh.get("sweat", 0.0), tears=sh.get("tears", 0.0), warp=warp)
        d = ImageDraw.Draw(img)
    d = draw_props(img, d, sh.get("props"), t, u, T0, s, sh, T)
    if sh.get("sea_front"):
        sy = sh.get("surface", 900)
        lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ld = ImageDraw.Draw(lay)
        ld.rectangle((0, sy * SS, W * SS, H * SS), fill=(20, 90, 150, 120))
        ld.line([(x, sy * SS + 8 * SS * math.sin(x / (50 * SS) + t * 3)) for x in range(0, W * SS + 40, 40)], fill=(200, 240, 255, 230), width=4 * SS)
        img.alpha_composite(lay)
    if sh.get("draw"):
        sh["draw"](img, ImageDraw.Draw(img), t, u, T0, s, T)
    out = big(img)
    if sh.get("flip"):
        out = out.rotate(180)
    return overlay_effects(out, sh, t, u)


def shot_face(t, u, sh):
    sh2 = dict(sh)
    z = val(sh.get("zoom", 4.6), u)
    sh2["cam"] = (0.0, sh.get("face_y", 0.10), z)
    sh2["preset"] = sh.get("preset", "dark")
    if sh2["preset"] == "dark" and "bg" in sh:
        pass
    sh2.setdefault("pose", {"head": 0.025 * math.sin(t * (9 if sh.get("shake_head") else 1.7))})
    if sh.get("shake_head") and not callable(sh2["pose"]):
        sh2["pose"] = dict(sh2["pose"])
        sh2["pose"]["head"] = 0.03 * math.sin(t * 13)
    return shot_scene(t, u, sh2)


def xray_bg():
    img = Image.new("RGBA", (W * SS, H * SS), (6, 10, 18, 255))
    d = ImageDraw.Draw(img)
    for x in range(0, W * SS, 60 * SS):
        d.line((x, 0, x, H * SS), fill=(20, 40, 70, 255))
    for y in range(0, H * SS, 60 * SS):
        d.line((0, y, W * SS, y), fill=(20, 40, 70, 255))
    return img


def shot_xray(t, u, sh):
    img = xray_bg()
    cam = cam_of(sh, u)
    T0, s = T0_for(cam)
    pose = sh.get("pose", {"arm_a_r": 0.14, "arm_a_l": 0.14}) if not callable(sh.get("pose")) else sh["pose"](t, u)
    ex = dict(sh.get("extras", {}))
    ex.setdefault("breath", 1.0 + val(sh.get("breath_amp", 0.04), u) * math.sin(t * 2 * math.pi * sh.get("breath_rate", 0.3)))
    ex.setdefault("beat", 1.0 + 0.1 * beat_pulse(t))
    T, Tg, pf = person(img, T0, pose, s, mode="xray", expr=sh.get("expr", "normal"), t=t, outfit=None, extras=ex,
                       skin=sh.get("skin", SKIN0), sweat=sh.get("sweat", 0.0), tears=sh.get("tears", 0.0))
    d = ImageDraw.Draw(img)
    for hl in sh.get("glow", []):
        k = val(hl.get("k", 1.0), u)
        if k <= 0:
            continue
        x, y = hl["at"]
        c = T(x, y)
        r = hl.get("r", 0.05) * s / cam[2] * cam[2]
        col = hl.get("col", (255, 50, 60))
        pul = 0.5 + 0.5 * math.sin(t * 6) if hl.get("pulse", True) else 1.0
        lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ImageDraw.Draw(lay).ellipse((c[0] - r, c[1] - r, c[0] + r, c[1] + r), fill=col + (int(150 * k * (0.6 + 0.4 * pul)),))
        img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(r * 0.35)))
        d = ImageDraw.Draw(img)
        for j in range(2):
            ph = (t * 1.2 + j * 0.5) % 1.0
            rr_ = r * (0.8 + 0.8 * ph)
            d.ellipse((c[0] - rr_, c[1] - rr_, c[0] + rr_, c[1] + rr_), outline=col + (int(200 * k * (1 - ph)),), width=max(2, int(0.003 * s)))
    for fl in sh.get("flow", []):
        path = fl["path"]
        k = val(fl.get("k", 1.0), u)
        n = fl.get("n", 30)
        col = fl.get("col", (255, 60, 70))
        for j in range(int(n * k)):
            ph = (j / n + t * fl.get("speed", 0.4)) % 1.0
            seg = ph * (len(path) - 1)
            i = min(int(seg), len(path) - 2)
            q = seg - i
            x = lerp(path[i][0], path[i + 1][0], q)
            y = lerp(path[i][1], path[i + 1][1], q)
            p = T(x, y)
            r = fl.get("size", 0.006) * s
            d.ellipse((p[0] - r, p[1] - r, p[0] + r, p[1] + r), fill=col + (230,))
    if sh.get("draw"):
        sh["draw"](img, d, t, u, T0, s, T)
    out = big(img)
    if sh.get("labels"):
        al = ease((u - 0.05) / 0.15)
        items = []
        for lb in sh["labels"]:
            name, v, col, anchor, side, y = lb
            v = v if not callable(v) else v(t, u)
            items.append((name, v, col, anchor, side, y))
        labels_block(ImageDraw.Draw(out), T, items, al)
    return overlay_effects(out, sh, t, u)


def shot_micro(t, u, sh):
    """cell-level diagram: cells get attacked/killed by particles"""
    img = dark_bg(t, sh.get("red", 0.4))
    d = ImageDraw.Draw(img)
    typ = sh.get("cells", "liver")
    kill = val(sh.get("kill", [(0, 0), (1, 0.8)]), u)
    col_ok = {"liver": (200, 130, 90), "neuron": (255, 200, 120), "lung": (240, 150, 160), "muscle": (210, 70, 80), "blood": (210, 40, 50), "nerve": (255, 210, 90)}[typ]
    col_dead = sh.get("dead_col", (70, 64, 60))
    rr = np.random.default_rng(11)
    y0, y1 = 620, 1180
    cells = []
    if typ in ("liver", "lung"):
        r = 52 if typ == "liver" else 48
        for row in range(6):
            for colm in range(9):
                x = 100 + colm * r * 1.75 + (row % 2) * r * 0.87
                y = y0 + 40 + row * r * 1.5
                if x < 960:
                    cells.append((x, y))
        for i, (x, y) in enumerate(cells):
            dead = rr.random() < kill
            c = mixc(col_ok, col_dead, 1.0 if dead else 0.0)
            if typ == "liver":
                pts = [(x + r * 0.95 * math.cos(a), y + r * 0.95 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 7)[:-1] + math.pi / 6]
                d.polygon(pts, fill=c + (255,), outline=(60, 30, 20, 255))
                d.ellipse((x - 10, y - 10, x + 10, y + 10), fill=mixc((90, 40, 40), (30, 30, 30), dead) + (255,))
            else:
                rr_ = r * (0.85 + 0.12 * math.sin(t * 2 + i)) * (0.6 if dead else 1.0)
                d.ellipse((x - rr_, y - rr_, x + rr_, y + rr_), fill=c + (255,), outline=(120, 40, 50, 255), width=3)
    elif typ in ("neuron", "nerve"):
        for i in range(16):
            x, y = rr.uniform(120, 920), rr.uniform(y0 + 40, y1 - 40)
            cells.append((x, y))
        for i, (x, y) in enumerate(cells):
            for j in range(i + 1, len(cells)):
                x2, y2 = cells[j]
                if (x - x2) ** 2 + (y - y2) ** 2 < 230 ** 2:
                    dead = (i * 7 + j) % 10 < kill * 10
                    d.line((x, y, x2, y2), fill=(mixc(col_ok, col_dead, 1 if dead else 0)) + (200,), width=4)
                    if not dead:
                        ph = (t * 1.5 + i * 0.1 + j * 0.07) % 1.0
                        d.ellipse((lerp(x, x2, ph) - 6, lerp(y, y2, ph) - 6, lerp(x, x2, ph) + 6, lerp(y, y2, ph) + 6), fill=(255, 255, 200, 255))
        for i, (x, y) in enumerate(cells):
            dead = (i % 10) < kill * 10
            d.ellipse((x - 26, y - 26, x + 26, y + 26), fill=mixc(col_ok, col_dead, 1 if dead else 0) + (255,), outline=(255, 255, 255, 120), width=3)
    elif typ == "muscle":
        for k in range(8):
            y = y0 + 40 + k * 60
            c = 1 - 0.3 * kill * (0.7 + 0.3 * math.sin(t * 20 + k))
            w = 760 * c
            d.rounded_rectangle((540 - w / 2, y, 540 + w / 2, y + 44), radius=22, fill=mixc(col_ok, col_dead, kill * (k % 3 == 0)) + (255,))
    elif typ == "blood":
        d.rounded_rectangle((60, y0 + 120, 1020, y1 - 120), radius=160, fill=(120, 20, 30, 255))
        n = int(40 * (1 - 0.8 * kill))
        for i in range(n):
            ph = (i / max(n, 1) + t * 0.3) % 1.0
            x = lerp(100, 980, ph)
            y = (y0 + y1) / 2 + 110 * math.sin(i * 1.7)
            d.ellipse((x - 26, y - 14, x + 26, y + 14), fill=(230, 50, 60, 255), outline=(150, 20, 30, 255), width=3)
    # attackers
    ac = sh.get("attack_col", (120, 255, 120))
    na = int(sh.get("attackers", 40) * val(sh.get("attack_k", [(0, 0.2), (1, 1.0)]), u))
    for i in range(na):
        x = (rr.uniform(60, 1020) + t * 40 * (1 + i % 3)) % 1000 + 40
        y = rr.uniform(y0, y1)
        shape = sh.get("attack_shape", "dot")
        if shape == "rod":
            a = rr.uniform(0, 3.14) + t
            d.line((x - 12 * math.cos(a), y - 12 * math.sin(a), x + 12 * math.cos(a), y + 12 * math.sin(a)), fill=ac + (255,), width=8)
        else:
            d.ellipse((x - 7, y - 7, x + 7, y + 7), fill=ac + (255,), outline=(255, 255, 255, 180))
    if sh.get("caption"):
        cf = F("Bold", 30)
        txt = sh["caption"] if not callable(sh["caption"]) else sh["caption"](t, u)
        d.text((540 - cf.getlength(txt) / 2, y1 + 20), txt, font=cf, fill=sh.get("caption_col", (255, 200, 90)) + (255,))
    if sh.get("legend"):
        lf = F("SemiBold", 24)
        y = y0 - 50
        x = 80
        for txt, c in sh["legend"]:
            d.ellipse((x, y + 4, x + 20, y + 24), fill=c + (255,))
            d.text((x + 30, y), txt, font=lf, fill=(230, 230, 236, 255))
            x += lf.getlength(txt) + 80
    return overlay_effects(img, sh, t, u)


def shot_bignum(t, u, sh):
    img = dark_bg(t, sh.get("red", 0.6))
    d = ImageDraw.Draw(img)
    v = sh["value"]
    if callable(v):
        v = v(t, u)
    elif isinstance(v, (list, tuple)):
        a, b, fmt = v
        v = fmt.format(lerp(a, b, ease(u / 0.7)))
    f = F("Black", sh.get("size", 150))
    while f.getlength(v) > 960 and f.size > 60:
        f = F("Black", f.size - 10)
    al = ease(u / 0.15)
    y = sh.get("y", 680)
    d.text((540 - f.getlength(v) / 2 + 6, y + 8), v, font=f, fill=(0, 0, 0, int(200 * al)))
    d.text((540 - f.getlength(v) / 2, y), v, font=f, fill=sh.get("col", YEL) + (int(255 * al),))
    yy = y + f.size * 1.15
    for k, line in enumerate(sh.get("sub", [])):
        txt, col = line if isinstance(line, tuple) else (line, WHITE)
        yy = ctext(d, txt, F("ExtraBold", 40), col, yy, ease((u - 0.15 - 0.12 * k) / 0.15), maxw=940, cx=540) + 10
    if sh.get("draw"):
        sh["draw"](img, d, t, u, None, None, None)
    return overlay_effects(img, sh, t, u)


def shot_flat(t, u, sh):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    d = ImageDraw.Draw(img)
    for x in range(0, W, 60):
        d.line((x, 520, x, 1240), fill=(20, 60, 40, 255))
    for y in range(520, 1240, 60):
        d.line((0, y, W, y), fill=(20, 60, 40, 255))
    pts = [(x, 880 - ecg_at(t - (W - x) / 260.0) * 200) for x in range(0, W, 3)]
    col = (90, 255, 140) if hr_at(t) > 0 else (255, 70, 70)
    d.line(pts, fill=col + (255,), width=6)
    f = F("Black", 120)
    txt = f"{int(hr_at(t))}"
    d.text((540 - f.getlength(txt) / 2, 1000), txt, font=f, fill=col + (255,))
    return img


def shot_black(t, u, sh):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    d = ImageDraw.Draw(img)
    y = sh.get("y", 700)
    for k, line in enumerate(sh["lines"]):
        txt, col = line if isinstance(line, tuple) else (line, WHITE)
        y = ctext(d, txt, F("Black" if k else "ExtraBold", 60 if k else 54), col, y, ease((u - 0.05 - 0.3 * k) / 0.2), maxw=960, cx=540) + 30
    return img


def shot_myth(t, u, sh):
    img = dark_bg(t, 0.3)
    d = ImageDraw.Draw(img)
    word = sh["word"]
    f = F("Black", 92)
    while f.getlength(word) > 900:
        f = F("Black", f.size - 6)
    ctext(d, word, f, WHITE, 620, ease(u / 0.15), shadow=False, maxw=980, cx=540)
    wdt = f.getlength(word.split("\n")[0])
    if u > 0.25:
        k = smooth((u - 0.25) / 0.12)
        d.line((540 - wdt / 2 - 10, 620 + f.size * 0.6, 540 - wdt / 2 - 10 + (wdt + 20) * k, 620 + f.size * 0.6), fill=(230, 40, 50, 255), width=12)
    if u > 0.38:
        stamp(img, sh.get("verdict", "МИФ"), 600, 540, ease((u - 0.38) / 0.1))
    ctext(d, sh["truth"], F("ExtraBold", 40), YEL, 820, ease((u - 0.5) / 0.15), maxw=900, cx=540)
    ctext(d, sh["text"], F("SemiBold", 30), (230, 230, 236), 900, ease((u - 0.6) / 0.15), maxw=880, cx=540)
    return img


def shot_facts(t, u, sh=None):
    facts = S["facts"]
    img = Image.new("RGBA", (W, H), (238, 234, 226, 255))
    d = ImageDraw.Draw(img)
    for y in range(0, H, 6):
        d.line((0, y, W, y), fill=(225, 220, 210, 120))
    ctext(d, "ФАКТЫ — ПРОВЕРЕНО", F("Black", 56), (30, 30, 34), 470, ease(u / 0.1), shadow=False, cx=540)
    y = 590
    for k, (a_, b_) in enumerate(facts):
        al = ease((u - 0.08 - k * 0.11) / 0.08)
        if al <= 0:
            continue
        bf = F("Medium", 25)
        while bf.getlength(b_) > 680 and bf.size > 18:
            bf = F("Medium", bf.size - 1)
        card = Image.new("RGBA", (800, 120), (0, 0, 0, 0))
        cd = ImageDraw.Draw(card)
        cd.rounded_rectangle((4, 4, 796, 116), radius=10, fill=(255, 255, 255, 255), outline=(200, 195, 185, 255), width=2)
        cd.ellipse((22, 34, 72, 84), fill=(220, 50, 50, 255))
        cd.text((47 - F("Black", 30).getlength(str(k + 1)) / 2, 38), str(k + 1), font=F("Black", 30), fill=(255, 255, 255, 255))
        cd.text((96, 18), a_, font=F("ExtraBold", 34), fill=(25, 25, 30, 255))
        cd.text((96, 66), b_, font=bf, fill=(80, 80, 88, 255))
        card = card.rotate((-1) ** k * 0.6, expand=True, resample=Image.BICUBIC)
        card.putalpha(card.getchannel("A").point(lambda v: int(v * al)))
        img.alpha_composite(card, (110, y))
        y += 136
    if u > 0.72:
        stamp(img, "ПРОВЕРЕНО", 470, 1260, ease((u - 0.72) / 0.08), rot=14, col=(210, 40, 46), size=70)
    return img


KINDS = {"scene": shot_scene, "face": shot_face, "xray": shot_xray, "micro": shot_micro, "bignum": shot_bignum,
         "flat": shot_flat, "black": shot_black, "myth": shot_myth, "facts": shot_facts}
NO_HUD = ("black", "facts", "myth", "loop")


# ======================================================================
# HUD
# ======================================================================
def stat_now(t):
    st = S.get("stat")
    if not st or t < st.get("from", 0) or t >= st.get("to", 1e9):
        return None
    v = pw(st["pts"], t)
    return st, v


def hud(img, t, i, sh):
    kind = sh["kind"]
    u = (t - sh["t0"]) / (sh["t1"] - sh["t0"])
    d = ImageDraw.Draw(img)
    if kind in NO_HUD or sh.get("hud") is False:
        return img
    first = i == 0
    la = 1.0 if first else ease((t - sh["t0"]) / 0.18)
    d.text((70, SAFE_TOP), S.get("header", "СИМУЛЯЦИЯ"), font=HDRF, fill=(220, 224, 232, int(220 * la)))
    pop = 1.0 if first else 1 + 0.12 * (1 - ease((t - sh["t0"]) / 0.22))
    f = F("Black", int((64 if first else 54) * pop))
    y = 230
    for ln in wrap_lines(sh.get("title", ""), f, 940):
        if not ln:
            continue
        x = 540 - f.getlength(ln) / 2
        d.text((x + 4, y + 5), ln, font=f, fill=(0, 0, 0, int(220 * la)))
        d.text((x, y), ln, font=f, fill=YEL + (int(255 * la),))
        y += f.size * 1.05
    if sh.get("tag"):
        tf = F("ExtraBold", 26)
        for ln in wrap_lines(sh["tag"].upper(), tf, 820):
            w = tf.getlength(ln) + 28
            d.rounded_rectangle((540 - w / 2, y + 8, 540 + w / 2, y + 48), radius=6, fill=TAGRED + (int(235 * la),))
            d.text((540 - tf.getlength(ln) / 2, y + 13), ln, font=tf, fill=(255, 255, 255, int(255 * la)))
            y += 46
    if sh.get("timer"):
        tf = F("Black", 96)
        tw = tf.getlength(sh["timer"])
        tx, ty = 540 - tw / 2, 1270
        d.text((tx + 5, ty + 6), sh["timer"], font=tf, fill=(0, 0, 0, 220))
        d.text((tx, ty), sh["timer"], font=tf, fill=YEL + (255,))
    if sh.get("vitals", True) and kind != "flat":
        sv = stat_now(t)
        if sv:
            st, v = sv
            good = st.get("good", (94, 100))
            warn = st.get("warn", (88, 100))
            cc = TEAL if good[0] <= v <= good[1] else (AMBER if warn[0] <= v <= warn[1] else RED)
            txt = st.get("fmt", "{name} {v:.0f}%").format(name=st["name"], v=v)
            cf = F("ExtraBold", 30)
            w = cf.getlength(txt) + 30
            d.rounded_rectangle((80, 1394, 80 + w, 1440), radius=10, fill=(8, 10, 18, 200), outline=cc + (255,), width=3)
            d.text((95, 1400), txt, font=cf, fill=cc + (255,))
        hr = hr_at(t)
        col = RED if hr > 125 else (AMBER if hr > 95 else TEAL)
        if hr < 1:
            col = RED
        pts = [(x, 1488 - ecg_at(t - (640 - x) / 230.0) * 24) for x in range(80, 640, 3)]
        d.line(pts, fill=col + (220,), width=3)
        pv = f"{int(round(hr))}"
        d.text((700, 1458), pv, font=F("Black", 44), fill=col + (255,))
        d.text((700 + F("Black", 44).getlength(pv) + 10, 1478), "уд/мин", font=F("Medium", 22), fill=GREY + (230,))
    if sh.get("say"):
        sa = ease((u - sh.get("say_at", 0.2)) / 0.12)
        sf = F("Black", sh.get("say_size", 48))
        txt = sh["say"]
        while sf.getlength(txt) > 900:
            sf = F("Black", sf.size - 4)
        yy = sh.get("say_y", 1150)
        d.text((540 - sf.getlength(txt) / 2 + 4, yy + 5), txt, font=sf, fill=(0, 0, 0, int(230 * sa)))
        d.text((540 - sf.getlength(txt) / 2, yy), txt, font=sf, fill=(255, 255, 255, int(255 * sa)))
    for pop_ in sh.get("pops", []):
        at, txt, x, y_ = pop_[:4]
        tr = t - (sh["t0"] + at)
        if 0 <= tr < pop_[4] if len(pop_) > 4 else 0 <= tr:
            text_pop(d, txt, x, y_, 110, tr)
    return img


# ======================================================================
# frame
# ======================================================================
def render_shot(t, sh):
    u = (t - sh["t0"]) / (sh["t1"] - sh["t0"])
    if sh["kind"] == "custom":
        out = sh["fn"](t, u, sh)
        return overlay_effects(out, sh, t, u)
    return KINDS[sh["kind"]](t, u, sh)


def render(i):
    t = i / FPS
    si, sh = shot_at(t)
    t0, t1, kind = sh["t0"], sh["t1"], sh["kind"]
    if kind == "loop":
        k = smooth((t - t0) / (t1 - t0 - 0.2))
        a = shot_facts(t, 1.0).convert("RGB")
        s0 = SHOTS[0]
        tt = t - t0
        img = render_shot(tt, s0)
        img.alpha_composite(TOP_SH)
        b = hud(img, tt, 0, s0).convert("RGB")
        return Image.blend(a, b, k)
    img = render_shot(t, sh)
    if img.size != (W, H):
        img = img.resize((W, H))
    k = 1 - ease((t - t0) / 0.28)
    if k > 0.01 and si > 0:
        z = 1 + 0.08 * k
        w2, h2 = int(W * z), int(H * z)
        img = img.resize((w2, h2), Image.BILINEAR).crop(((w2 - W) // 2, (h2 - H) // 2, (w2 - W) // 2 + W, (h2 - H) // 2 + H))
    u = (t - t0) / (t1 - t0)
    shk = val(sh.get("shake", 0), u)
    for hit in sh.get("hits", []):          # (time in shot, strength)
        tr = t - (t0 + hit[0])
        if 0 <= tr < 1.0:
            shk += hit[1] * (1 - smooth(tr / 1.0))
    if shk > 0.05:
        dx, dy = int(14 * shk * math.sin(t * 61)), int(14 * shk * math.cos(t * 53))
        img = ImageChops_offset(img, dx, dy)
    rl = sh.get("red", 0.0)
    if rl > 0:
        img.alpha_composite(vig_layer((170, 10, 20), min(1.0, rl * (0.45 + 0.35 * beat_pulse(t)))))
    if kind not in ("facts",):
        img.alpha_composite(TOP_SH)
    img = hud(img, t, si, sh)
    if t - t0 < 0.07 and si > 0 and kind not in ("facts", "black"):
        img.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(170 * (1 - (t - t0) / 0.07)))))
    for hit in sh.get("hits", []):
        tr = t - (t0 + hit[0])
        if 0 <= tr < 0.1 and len(hit) > 2 and hit[2]:
            img.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(220 * (1 - tr / 0.1)))))
    return img.convert("RGB")


# ======================================================================
# CLI
# ======================================================================
def render_part(t0, t1, out):
    n0, n1 = int(round(t0 * FPS)), int(round(t1 * FPS))
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(n0, n1):
        p.stdin.write(render(i).tobytes())
    p.stdin.close()
    p.wait()


def contact_sheet(ts, out):
    ims = [render(int(round(t * FPS))) for t in ts]
    cols = 6
    rows = (len(ims) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * 226 + 10, rows * 394 + 10), (60, 60, 60))
    for k, im in enumerate(ims):
        im = im.copy()
        dd = ImageDraw.Draw(im, "RGBA")
        dd.rectangle((0, 0, 1080, 150), fill=(255, 0, 255, 60))
        dd.rectangle((960, 880, 1080, 1600), fill=(255, 0, 255, 60))
        dd.rectangle((0, 1560, 1080, 1920), fill=(255, 0, 255, 60))
        sheet.paste(im.resize((216, 384)), (10 + (k % cols) * 226, 10 + (k // cols) * 394))
    sheet.save(out)
    return ims


if __name__ == "__main__":
    cmd, path = sys.argv[1], sys.argv[2]
    load(path)
    d = S["_dir"]
    if cmd == "check":
        if len(sys.argv) > 3:
            ts = [float(x) for x in sys.argv[3].split(",")]
        else:
            ts = [round((s["t0"] + s["t1"]) / 2, 2) for s in SHOTS]
        ims = contact_sheet(ts, os.path.join(d, "sheet.png"))
        if os.environ.get("SAVE_FRAMES"):
            for t, im in zip(ts, ims):
                im.save(os.path.join(d, f"f_{t}.png"))
        print("sheet", os.path.join(d, "sheet.png"), "T_END", T_END)
    elif cmd == "part":
        render_part(float(sys.argv[3]), float(sys.argv[4]), sys.argv[5])
    elif cmd == "render":
        mid = round(T_END / 2 * FPS) / FPS
        p1 = os.path.join(d, "_p1.mp4")
        p2 = os.path.join(d, "_p2.mp4")
        procs = [subprocess.Popen([sys.executable, __file__, "part", path, "0", str(mid), p1]),
                 subprocess.Popen([sys.executable, __file__, "part", path, str(mid), str(T_END), p2])]
        import sound
        wav = os.path.join(d, "_score.wav")
        sound.build(sys.modules[__name__], wav)
        for p in procs:
            p.wait()
        lst = os.path.join(d, "_list.txt")
        open(lst, "w").write(f"file '{p1}'\nfile '{p2}'\n")
        out = os.path.join(d, S["slug"] + ".mp4")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-i", wav, "-map", "0:v", "-map", "1:a",
                        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", out], check=True)
        for f in (p1, p2, lst):
            os.remove(f)
        print("video", out)
