"""Style-2 («эталон Арсения 06.11»): pill super-title, red tilted ribbon title with glitch, one HUD card,
dark blue-graphite grading, callouts, single fact cards, hook / eye / phone / flasks shot kinds, glitch cuts.

Activated by SPEC["style"] = 2.  Extra spec keys:
  S["card"] = dict(label="ОТРАВЛЕНИЕ", pts=[(t, 0..100)], fmt="{v:.0f}%", notes=[(0,"норма"),(40,"опасно"),(75,"критично")],
                   right_label="ЧАС", minis=[("ПУЛЬС","hr"), ("ДЫХАНИЕ","НОРМА"), ...])        # bottom card defaults
  shot keys: over="ЧАС 12" (pill), title (ribbon), tag (sub-ribbon), clock="12" (card right big), clock_label, badge="×1000 замедлено",
             minis=[...] (override), card=False, callouts=[(at_u, (x,y), (lx,ly), "ТЕКСТ"[, col])], flash=[(at_s, k)], red_tint=k,
             pov=dict(blur=, veil=, double=, tunnel=, snow=), drift=0.04
  kinds: hook, eye, phone, flasks, fact
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from base import F, W, H, SS, ease, smooth, lerp, pw, mixc, wrap_lines, A

RIB = (214, 36, 46)
RIB2 = (168, 18, 30)
BG0, BG1 = (30, 36, 51), (18, 22, 34)
CALL = (240, 205, 100)
GREEN, YELLOW, REDC = (70, 200, 110), (240, 196, 60), (236, 52, 58)
GREYT = (150, 158, 176)

_cache = {}


# ---------------------------------------------------------------- background / grading
def vig_mask():
    if "vig" not in _cache:
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        dx = (xx - W / 2) / (W / 2)
        dy = (yy - H * 0.45) / (H / 2)
        r = np.sqrt(dx ** 2 * 0.9 + dy ** 2 * 0.75)
        _cache["vig"] = (1 - 0.55 * np.clip((r - 0.45) / 0.75, 0, 1) ** 1.4)[..., None]
    return _cache["vig"]


def dark_bg2(t=0.0, red=0.0):
    key = ("bg", round(red, 2))
    if key not in _cache:
        rows = np.arange(H, dtype=np.float32)[:, None] / H
        top = np.array(mixc(BG0, (52, 18, 24), red * 0.7), np.float32)
        bot = np.array(mixc(BG1, (26, 8, 12), red * 0.7), np.float32)
        col = top * (1 - rows) + bot * rows
        arr = np.broadcast_to(col[:, None, :], (H, W, 3)) * vig_mask()
        img = Image.fromarray(arr.astype(np.uint8), "RGB").convert("RGBA")
        # subtle noise texture
        rng = np.random.default_rng(3)
        nz = (rng.normal(0, 3, (H // 4, W // 4))).astype(np.int16)
        nz = np.kron(nz, np.ones((4, 4), np.int16))
        a = np.asarray(img).astype(np.int16)
        a[..., :3] = np.clip(a[..., :3] + nz[..., None], 0, 255)
        _cache[key] = Image.fromarray(a.astype(np.uint8), "RGBA")
        if len(_cache) > 40:
            pass
    return _cache[key].copy()


def grade(img, k=1.0, red_tint=0.0):
    """pull any frame into the dark blue-graphite palette"""
    a = np.asarray(img.convert("RGB")).astype(np.float32)
    lum = a @ np.array([0.299, 0.587, 0.114], np.float32)
    a = a * (1 - 0.28 * k) + lum[..., None] * 0.28 * k
    a = a * (1 - 0.2 * k) + np.array((14, 18, 32), np.float32) * 0.2 * k
    a = a * (0.92 - 0.0 * k)
    a *= vig_mask() if k > 0 else 1
    if red_tint > 0:
        r = np.array((200, 20, 30), np.float32)
        a = a * (1 - 0.45 * red_tint) + (lum[..., None] / 255.0 * 0.6 + 0.4) * r * 0.45 * red_tint
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGB").convert("RGBA")


# ---------------------------------------------------------------- titles
def pill(d, text, y=172, al=1.0, cx=540):
    if not text or al <= 0:
        return
    f = F("Bold", 25)
    txt = text.upper()
    w = f.getlength(txt) + 66
    x0 = cx - w / 2
    d.rounded_rectangle((x0, y, x0 + w, y + 44), radius=22, fill=(12, 14, 22, int(215 * al)), outline=(70, 76, 92, int(200 * al)), width=2)
    d.ellipse((x0 + 20, y + 16, x0 + 32, y + 28), fill=(236, 50, 56, int(255 * al)))
    d.text((x0 + 44, y + 8), txt, font=f, fill=(206, 210, 222, int(255 * al)))


def _ribbon_layer(text, font, fill, pad_x, pad_y, glitch=0.0, seed=0):
    lines = [ln for ln in text.split("\n")]
    lh = font.size * 1.08
    tw = max(font.getlength(ln) for ln in lines)
    w, h = int(tw + 2 * pad_x), int(lh * len(lines) + 2 * pad_y)
    lay = Image.new("RGBA", (w + 24, h + 24), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.rectangle((14, 16, w + 14, h + 16), fill=(70, 6, 12, 200))
    d.rectangle((6, 6, w + 6, h + 6), fill=fill + (255,))
    y = 6 + pad_y - font.size * 0.06
    for ln in lines:
        x = 6 + (w - font.getlength(ln)) / 2
        if glitch > 0.02:
            dx = int(16 * glitch * (1 if seed % 2 else -1))
            d.text((x - dx, y), ln, font=font, fill=(0, 230, 255, int(200 * glitch)))
            d.text((x + dx, y + 2), ln, font=font, fill=(255, 230, 0, int(160 * glitch)))
        d.text((x, y), ln, font=font, fill=(255, 255, 255, 255))
        y += lh
    return lay


def fit_title(text, maxw=900, size=82, minsize=56):
    txt = text.upper()
    f = F("Black", size)
    if "\n" in txt:
        while max(f.getlength(l) for l in txt.split("\n")) > maxw and f.size > minsize:
            f = F("Black", f.size - 4)
        return txt, f
    while f.getlength(txt) > maxw and f.size > minsize:
        f = F("Black", f.size - 4)
    if f.getlength(txt) > maxw:
        lines = wrap_lines(txt, F("Black", size - 6), maxw)
        f = F("Black", size - 6)
        while max(f.getlength(l) for l in lines) > maxw:
            f = F("Black", f.size - 4)
            lines = wrap_lines(txt, f, maxw)
        txt = "\n".join(l for l in lines if l)
    return txt, f


def ribbon(img, title, tag, t_rel, y=226, first=False):
    if not title:
        return y
    k = 1.0 if first else ease(t_rel / 0.22)
    gl = 0.0 if first else max(0.0, 1 - t_rel / 0.35)
    gl *= (0.6 + 0.4 * math.sin(t_rel * 70))
    txt, f = fit_title(title)
    lay = _ribbon_layer(txt, f, RIB, 30, 14, gl, int(t_rel * 40))
    lw = lay.size[0]
    if k < 1:
        cut = int(lw * k)
        if cut < 4:
            return y
        lay = lay.crop((0, 0, cut, lay.size[1])).crop((0, 0, lw, lay.size[1]))
    rl = lay.rotate(2.2, expand=True, resample=Image.BICUBIC)
    x = int(540 - rl.size[0] / 2)
    img.alpha_composite(rl, (x, int(y)))
    y2 = y + rl.size[1] - 6
    if tag:
        ka = ease((t_rel - 0.15) / 0.2) if not first else 1.0
        if ka > 0:
            tf = F("ExtraBold", 29)
            tt = tag.upper()
            while tf.getlength(tt) > 860 and tf.size > 20:
                tf = F("ExtraBold", tf.size - 1)
            if tf.getlength(tt) > 860:
                tt = "\n".join(wrap_lines(tt, tf, 860))
            sl = _ribbon_layer(tt, tf, RIB2, 18, 6)
            sw = sl.size[0]
            cut = int(sw * ka)
            if cut > 4:
                sl = sl.crop((0, 0, cut, sl.size[1])).crop((0, 0, sw, sl.size[1]))
                sl = sl.rotate(2.2, expand=True, resample=Image.BICUBIC)
                img.alpha_composite(sl, (int(540 - sl.size[0] / 2), int(y2 + 2)))
                y2 += sl.size[1]
    return y2


# ---------------------------------------------------------------- HUD card
def _glow_card(box):
    key = ("glow", box)
    if key not in _cache:
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(lay).rounded_rectangle(box, radius=26, outline=(236, 40, 50, 150), width=14)
        _cache[key] = lay.filter(ImageFilter.GaussianBlur(14))
    return _cache[key]


def seg_col(i, n=10):
    if i < n * 0.4:
        return GREEN
    if i < n * 0.7:
        return YELLOW
    return REDC


def card(img, E, t, sh, al=1.0):
    S = E.S
    c = S.get("card")
    if not c or sh.get("card") is False or al <= 0:
        return
    box = (80, 1336, 940, 1546)
    x0, y0, x1, y1 = box
    img.alpha_composite(_glow_card(box))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle(box, radius=24, fill=(14, 16, 24, 236), outline=(226, 44, 52, 255), width=3)
    lf = F("Bold", 21)
    d.text((x0 + 30, y0 + 20), c.get("label", "").upper(), font=lf, fill=GREYT + (255,))
    u = (t - sh["t0"]) / (sh["t1"] - sh["t0"])
    v = None
    for s_ in E.SHOTS:
        if s_["t0"] > sh["t0"]:
            break
        if s_.get("value") is not None:
            v = s_["value"]
            if s_ is not sh and isinstance(v, (list, tuple)):
                v = v[1]
            if s_ is not sh:
                for k_ in ("clock",):
                    pass
    if v is None:
        v = pw(c["pts"], t) if c.get("pts") else 0.0
    if isinstance(v, (list, tuple)):
        v = lerp(v[0], v[1], smooth(u / 0.8))
    if callable(v):
        v = v(t)
    n = 10
    filled = v / 100 * n
    for i in range(n):
        bx = x0 + 30 + i * 41
        d.rounded_rectangle((bx, y0 + 52, bx + 33, y0 + 80), radius=5, fill=(46, 52, 66, 255))
        part = max(0.0, min(1.0, filled - i))
        if part > 0:
            d.rounded_rectangle((bx, y0 + 52, bx + 33 * part, y0 + 80), radius=5, fill=seg_col(i, n) + (255,))
    vc = seg_col(min(n - 1, int(filled)), n) if v > 0.5 else GREEN
    vt = c.get("fmt", "{v:.0f}%").format(v=v) if not sh.get("value_txt") else sh["value_txt"]
    vf = F("Black", 40)
    d.text((x0 + 30, y0 + 88), vt, font=vf, fill=vc + (255,))
    note = ""
    for th, nt in c.get("notes", []):
        if v >= th:
            note = nt
    if sh.get("note"):
        note = sh["note"]
    if note:
        d.text((x0 + 42 + vf.getlength(vt), y0 + 104), note.upper(), font=F("Bold", 21), fill=(vc if v >= 70 else (200, 204, 214)) + (255,))
    # right: big clock
    rl = (sh.get("clock_label") or c.get("right_label", "")).upper()
    d.text((x1 - 30 - lf.getlength(rl), y0 + 20), rl, font=lf, fill=GREYT + (255,))
    clk = sh.get("clock")
    if clk is None:
        for s_ in E.SHOTS:
            if s_["t0"] > sh["t0"]:
                break
            if s_.get("clock") is not None:
                clk = s_["clock"]
        clk = clk or ""
    if callable(clk):
        clk = clk(t, (t - sh["t0"]) / (sh["t1"] - sh["t0"]))
    cf = F("Black", 60)
    while cf.getlength(clk) > 330:
        cf = F("Black", cf.size - 4)
    d.text((x1 - 30 - cf.getlength(clk), y0 + 44), clk, font=cf, fill=(250, 250, 252, 255))
    if sh.get("badge"):
        bf = F("ExtraBold", 19)
        bt = sh["badge"].upper()
        bw = bf.getlength(bt) + 24
        d.rounded_rectangle((x1 - 30 - bw, y0 + 112, x1 - 30, y0 + 140), radius=14, fill=(214, 36, 46, 255))
        d.text((x1 - 18 - bw, y0 + 115), bt, font=bf, fill=(255, 255, 255, 255))
    d.line((x0 + 30, y0 + 148, x1 - 30, y0 + 148), fill=(52, 58, 74, 255), width=2)
    minis = c.get("minis", [])
    for s_ in E.SHOTS:
        if s_["t0"] > sh["t0"]:
            break
        if s_.get("minis") is not None:
            minis = s_["minis"]
    if minis:
        colw = (x1 - x0 - 60) / len(minis)
        for j, (lab, val) in enumerate(minis):
            if val == "hr":
                hr = E.hr_at(t)
                val = f"{int(round(hr))}" if hr >= 1 else "0"
                if hr > 125 or hr < 45:
                    val = "!" + val
            elif isinstance(val, (list, tuple)):
                cur = val[0][1]
                for tt, vv in val:
                    if t >= tt:
                        cur = vv
                val = cur
            elif callable(val):
                val = val(t)
            bad = val.startswith("!")
            val = val.lstrip("!")
            mf = F("Black", 28)
            if j == 0:
                xx = x0 + 30
            elif j == len(minis) - 1:
                xx = x1 - 30 - max(mf.getlength(val.upper()), F("Bold", 18).getlength(lab.upper()))
            else:
                xx = x0 + 30 + colw * j + colw / 2 - mf.getlength(val.upper()) / 2
            d.text((xx, y0 + 158), lab.upper(), font=F("Bold", 18), fill=GREYT + (255,))
            d.text((xx, y0 + 178), val.upper(), font=mf, fill=((236, 56, 60) if bad else (244, 244, 248)) + (255,))


# ---------------------------------------------------------------- callouts
def callouts(img, sh, u, dur):
    d = ImageDraw.Draw(img)
    for co in sh.get("callouts", []):
        at, p, l, txt = co[:4]
        col = co[4] if len(co) > 4 else CALL
        k = ease((u - at) * dur / 0.35)
        if k <= 0:
            continue
        x, y = p
        lx, ly = l
        ex, ey = lerp(x, lx, k), lerp(y, ly, k)
        d.line((x, y, ex, ey), fill=col + (230,), width=3)
        d.ellipse((x - 9, y - 9, x + 9, y + 9), fill=col + (255,))
        d.ellipse((x - 17, y - 17, x + 17, y + 17), outline=col + (int(140 * k),), width=2)
        if k > 0.8:
            f = F("ExtraBold", 27)
            tx = txt.upper()
            a = int(255 * ease((k - 0.8) / 0.2))
            w = f.getlength(tx)
            if lx >= x:
                tx0 = min(lx + 10, 935 - w)
            else:
                tx0 = max(lx - 10 - w, 40)
            d.text((tx0 + 2, ly - 17), tx, font=f, fill=(0, 0, 0, a // 2))
            d.text((tx0, ly - 19), tx, font=f, fill=col + (a,))


# ---------------------------------------------------------------- effects
def glitch_cut(img, k, seed):
    """k 1 -> 0 at the start of a shot"""
    a = np.asarray(img.convert("RGB")).copy()
    dx = int(26 * k)
    a[..., 0] = np.roll(a[..., 0], dx, axis=1)
    a[..., 2] = np.roll(a[..., 2], -dx, axis=1)
    rng = np.random.default_rng(seed)
    for _ in range(int(7 * k) + 1):
        y = int(rng.uniform(0, H - 60))
        h = int(rng.uniform(10, 80))
        a[y:y + h] = np.roll(a[y:y + h], int(rng.uniform(-80, 80) * k), axis=1)
    out = Image.fromarray(a, "RGB").convert("RGBA")
    if k > 0.5:
        out.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, int(120 * (k - 0.5)))))
    return out


def pov(img, p, t):
    out = img
    if p.get("double"):
        sh = int(40 * p["double"] * (0.8 + 0.2 * math.sin(t * 2)))
        b = out.copy()
        b2 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        b2.paste(b, (sh, -sh // 4))
        out = Image.blend(out, Image.alpha_composite(out, b2), 0.5)
    if p.get("blur"):
        out = out.filter(ImageFilter.GaussianBlur(14 * p["blur"]))
    if p.get("snow"):
        rng = np.random.default_rng(int(t * 30))
        a = np.asarray(out).copy()
        m = rng.random((H // 3, W // 3)) < 0.08 * p["snow"]
        m = np.kron(m, np.ones((3, 3), bool))
        v = rng.integers(150, 255, m.shape)
        for c in range(3):
            ch = a[..., c]
            ch[m] = v[m]
        out = Image.fromarray(a, "RGBA")
    if p.get("veil"):
        out.alpha_composite(Image.new("RGBA", (W, H), (230, 232, 238, int(220 * p["veil"]))))
    if p.get("tunnel"):
        key = "tun"
        if key not in _cache:
            yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
            r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H * 0.47) / (H / 2)) ** 2)
            _cache[key] = r
        r = _cache[key]
        k = p["tunnel"]
        al = np.clip((r - (1.0 - 0.75 * k)) / 0.35, 0, 1) * 255
        lay = np.zeros((H, W, 4), np.uint8)
        lay[..., 3] = al.astype(np.uint8)
        out.alpha_composite(Image.fromarray(lay, "RGBA"))
    return out


# ---------------------------------------------------------------- kinds
def shot_hook(E, t, u, sh):
    img = dark_bg2(t, sh.get("red", 0.0))
    if sh.get("draw"):
        sh["draw"](img, ImageDraw.Draw(img), t, u, None, None, None)
    d = ImageDraw.Draw(img)
    txt = sh["phrase"].upper()
    f = F("Black", sh.get("size", 108))
    lines = txt.split("\n")
    while max(f.getlength(l) for l in lines) > 960:
        f = F("Black", f.size - 4)
    y = sh.get("y", 240)
    for i, ln in enumerate(lines):
        w = f.getlength(ln)
        d.text((540 - w / 2 + 5, y + 7), ln, font=f, fill=(0, 0, 0, 200))
        d.text((540 - w / 2, y), ln, font=f, fill=(255, 255, 255, 255))
        y += f.size * 1.02
        if i == len(lines) - 1:
            uw = w * min(1.0, ease(u * (sh["t1"] - sh["t0"]) / 0.5) + (1 if sh.get("_first_full") else 0))
            if sh.get("strike"):
                d.rectangle((540 - w / 2 - 10, y - f.size * 0.62, 540 - w / 2 - 10 + (w + 20) * min(1, uw / w), y - f.size * 0.62 + 16), fill=(236, 40, 50, 255))
            else:
                d.rectangle((540 - w / 2, y + 6, 540 - w / 2 + uw, y + 22), fill=(236, 40, 50, 255))
    return img


def shot_eye(E, t, u, sh):
    """macro eye. keys: lid 0..1 (drooping upper lid), red 0..1 (veins), haze 0..1, pupil 0..1, look (dx), tear"""
    S2 = 2
    w, h = W * S2, H * S2
    skin = sh.get("skin", (176, 128, 104))
    img = Image.new("RGBA", (w, h), skin + (255,))
    d = ImageDraw.Draw(img)
    cx, cy = w / 2, h * 0.47
    ew, eh = 470 * S2, 210 * S2
    # soft shading
    sh_l = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(sh_l).ellipse((cx - ew * 1.35, cy - eh * 2.2, cx + ew * 1.35, cy + eh * 2.0), fill=(60, 30, 30, 120))
    img.alpha_composite(sh_l.filter(ImageFilter.GaussianBlur(120)))
    d = ImageDraw.Draw(img)
    # brow
    by = cy - eh * 2.0
    d.line([(cx - ew * 1.1, by + 40 * S2), (cx - ew * 0.3, by - 40 * S2), (cx + ew * 0.6, by - 20 * S2), (cx + ew * 1.1, by + 50 * S2)],
           fill=(70, 46, 36, 255), width=70 * S2, joint="curve")
    top = [(cx + ew * math.cos(a), cy - eh * math.sin(a) * 1.05) for a in np.linspace(0, math.pi, 40)]
    bot = [(cx + ew * math.cos(a), cy - eh * 0.8 * math.sin(a)) for a in np.linspace(math.pi, 2 * math.pi, 40)]
    eye = top + bot
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).polygon(eye, fill=255)
    ey = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ed = ImageDraw.Draw(ey)
    red = val(sh.get("red", 0.0), u)
    ed.polygon(eye, fill=mixc((246, 242, 236), (240, 170, 160), red * 0.6) + (255,))
    rng = np.random.default_rng(5)
    for k in range(int(26 * red)):
        side = -1 if k % 2 else 1
        x = cx + side * ew * rng.uniform(0.95, 1.0)
        y = cy + rng.uniform(-eh * 0.5, eh * 0.5)
        pts = [(x, y)]
        for j in range(6):
            x -= side * rng.uniform(20, 45) * S2
            y += rng.uniform(-14, 14) * S2
            pts.append((x, y))
        ed.line(pts, fill=(200, 40, 50, 220), width=int(rng.uniform(2, 5) * S2))
    look = val(sh.get("look", 0.0), u) + 0.03 * math.sin(t * 1.3)
    ix, iy = cx + look * ew, cy - eh * 0.05
    ir = eh * 0.92
    ed.ellipse((ix - ir, iy - ir, ix + ir, iy + ir), fill=sh.get("iris", (70, 110, 150)) + (255,))
    for k in range(36):
        a = k / 36 * 2 * math.pi
        ed.line((ix + ir * 0.35 * math.cos(a), iy + ir * 0.35 * math.sin(a), ix + ir * 0.95 * math.cos(a), iy + ir * 0.95 * math.sin(a)),
                fill=(40, 70, 100, 160), width=3 * S2)
    pr = ir * lerp(0.28, 0.7, val(sh.get("pupil", 0.4), u))
    ed.ellipse((ix - pr, iy - pr, ix + pr, iy + pr), fill=(10, 10, 14, 255))
    ed.ellipse((ix - ir * 0.45, iy - ir * 0.5, ix - ir * 0.2, iy - ir * 0.25), fill=(255, 255, 255, 230))
    hz = val(sh.get("haze", 0.0), u)
    if hz:
        ed.ellipse((ix - ir, iy - ir, ix + ir, iy + ir), fill=(230, 232, 236, int(200 * hz)))
    img.paste(ey, (0, 0), ImageChops_mul(mask, ey.getchannel("A")))
    d = ImageDraw.Draw(img)
    lid = val(sh.get("lid", 0.0), u)
    blink = sh.get("blink")
    if blink is not None:
        bt = (u * (sh["t1"] - sh["t0"])) - blink
        if 0 <= bt < 0.25:
            lid = max(lid, 1 - abs(bt - 0.125) / 0.125)
    if lid > 0:
        ly = cy - eh * 1.1 + lid * eh * 1.95
        poly = [(cx - ew * 1.2, cy - eh * 2.5), (cx + ew * 1.2, cy - eh * 2.5), (cx + ew * 1.2, ly - eh * 0.2)] + \
               [(cx + ew * math.cos(a) * 1.05, ly + eh * 0.25 * math.sin(a)) for a in np.linspace(0, math.pi, 20)][::-1][::-1] + [(cx - ew * 1.2, ly - eh * 0.2)]
        lidc = mixc(skin, (90, 60, 50), 0.15)
        d.polygon(poly, fill=lidc + (255,))
        d.line([(cx + ew * math.cos(a) * 1.0, ly + eh * 0.25 * math.sin(a)) for a in np.linspace(0, math.pi, 20)], fill=(40, 24, 20, 255), width=14 * S2)
    else:
        d.line(top, fill=(40, 24, 20, 255), width=16 * S2)
        crease = [(cx + ew * 1.05 * math.cos(a), cy - eh * 1.45 * math.sin(a)) for a in np.linspace(0.15, math.pi - 0.15, 30)]
        d.line(crease, fill=mixc(skin, (60, 30, 30), 0.4) + (255,), width=6 * S2)
    d.line(bot, fill=mixc(skin, (60, 30, 30), 0.5) + (255,), width=6 * S2)
    if sh.get("tear"):
        tk = (u * 1.3) % 1
        tx, ty = cx - ew * 0.75, cy + eh * 0.7 + tk * 500 * S2
        d.ellipse((tx - 16 * S2, ty - 22 * S2, tx + 16 * S2, ty + 22 * S2), fill=(200, 225, 255, 200))
    out = img.resize((W, H), Image.LANCZOS)
    z = val(sh.get("zoom", [(0, 1.0), (1, 1.12)]), u)
    if z != 1.0:
        w2, h2 = int(W * z), int(H * z)
        out = out.resize((w2, h2), Image.BILINEAR).crop(((w2 - W) // 2, int((h2 - H) * 0.47), (w2 - W) // 2 + W, int((h2 - H) * 0.47) + H))
    return out


def ImageChops_mul(a, b):
    from PIL import ImageChops
    return ImageChops.multiply(a, b)


def val(v, u):
    if isinstance(v, (list, tuple)) and v and isinstance(v[0], (list, tuple)):
        return pw(v, u)
    return v


def shot_phone(E, t, u, sh):
    """phone held up. sh['screen'] = dict(top="ВЫЗОВ…", big="103", sub="СКОРАЯ ПОМОЩЬ", timer=True) or msgs=[(text, side)]"""
    img = dark_bg2(t, sh.get("red", 0.1))
    if sh.get("bg_draw"):
        sh["bg_draw"](img, ImageDraw.Draw(img), t, u)
    d = ImageDraw.Draw(img)
    sc = sh.get("screen", {})
    x0, y0, x1, y1 = 330, 520, 750, 1290
    bob = 6 * math.sin(t * 2.2)
    y0 += bob
    y1 += bob
    # hand
    skin = (214, 160, 130)
    d.rounded_rectangle((x0 - 40, y1 - 260, x0 + 60, y1 + 120), radius=50, fill=skin + (255,))
    d.rounded_rectangle((x0 + 20, y1 - 30, x1 + 30, y1 + 300), radius=90, fill=skin + (255,))
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).rounded_rectangle((x0 - 30, y0 - 30, x1 + 30, y1 + 30), radius=80, fill=sc.get("glow", (120, 150, 220)) + (60,))
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(40)))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((x0, y0, x1, y1), radius=56, fill=(20, 20, 26, 255), outline=(90, 94, 110, 255), width=4)
    d.rounded_rectangle((x0 + 16, y0 + 16, x1 - 16, y1 - 16), radius=44, fill=sc.get("bg", (24, 30, 44)) + (255,))
    d.rounded_rectangle((540 - 50, y0 + 30, 540 + 50, y0 + 52), radius=11, fill=(8, 8, 10, 255))
    if sc.get("msgs"):
        y = y0 + 110
        f = F("SemiBold", 26)
        for k, (txt, side) in enumerate(sc["msgs"]):
            al = ease((u - k * sc.get("step", 0.22)) / 0.08)
            if al <= 0:
                continue
            lines = wrap_lines(txt, f, 270)
            bh = len(lines) * 34 + 24
            bw = max(f.getlength(l) for l in lines) + 36
            bx = x0 + 34 if side == "l" else x1 - 34 - bw
            col = (52, 58, 74) if side == "l" else (46, 120, 230)
            d.rounded_rectangle((bx, y, bx + bw, y + bh), radius=20, fill=col + (int(255 * al),))
            yy = y + 12
            for l in lines:
                d.text((bx + 18, yy), l, font=f, fill=(255, 255, 255, int(255 * al)))
                yy += 34
            y += bh + 18
    else:
        f1 = F("SemiBold", 28)
        top = sc.get("top", "ВЫЗОВ…").upper()
        d.text((540 - f1.getlength(top) / 2, y0 + 150), top, font=f1, fill=(190, 196, 210, 255))
        big = sc.get("big", "103")
        fb = F("Black", 130)
        while fb.getlength(big) > 380:
            fb = F("Black", fb.size - 6)
        d.text((540 - fb.getlength(big) / 2, y0 + 200), big, font=fb, fill=(255, 255, 255, 255))
        sub = sc.get("sub", "").upper()
        fs = F("Bold", 26)
        d.text((540 - fs.getlength(sub) / 2, y0 + 360), sub, font=fs, fill=(190, 196, 210, 255))
        if sc.get("timer"):
            secs = int(u * (sh["t1"] - sh["t0"]) + sc.get("t0", 0))
            tt = f"00:{secs:02d}"
            d.text((540 - fs.getlength(tt) / 2, y0 + 410), tt, font=fs, fill=(120, 220, 140, 255))
        by = y1 - 170
        pul = 1 + 0.08 * math.sin(t * 8)
        r = 52 * pul
        d.ellipse((540 - r, by - r, 540 + r, by + r), fill=sc.get("btn", (226, 48, 56)) + (255,))
        d.rounded_rectangle((540 - 26, by - 9, 540 + 26, by + 9), radius=8, fill=(255, 255, 255, 255))
    return img


def shot_flasks(E, t, u, sh):
    """chemistry chain inside an organ: items=[(label, col)], organ=(col) blob, fill keyframes per item sequentially"""
    img = dark_bg2(t, sh.get("red", 0.2))
    d = ImageDraw.Draw(img)
    oc = sh.get("organ")
    if oc:
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ld = ImageDraw.Draw(lay)
        pts = sh.get("organ_pts") or [(90, 820), (300, 660), (700, 640), (1000, 720), (1010, 900), (820, 1140), (420, 1180), (140, 1080)]
        ld.polygon(A.catmull(pts, closed=True, n=8), fill=oc + (255,))
        img.alpha_composite(lay)
        hl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(hl).ellipse((250, 690, 700, 860), fill=(255, 255, 255, 30))
        img.alpha_composite(hl.filter(ImageFilter.GaussianBlur(30)))
        d = ImageDraw.Draw(img)
    items = sh["items"]
    n = len(items)
    xs = [lerp(230, 850, i / max(1, n - 1)) for i in range(n)]
    base = 1010
    d.rounded_rectangle((150, base + 4, 930, base + 20), radius=8, fill=(30, 34, 46, 255))
    for i, (lab, col) in enumerate(items):
        x = xs[i]
        k = smooth((u - 0.1 - i * 0.22) / 0.2)
        neck = [(x - 22, base - 230), (x + 22, base - 230), (x + 22, base - 150), (x + 95, base), (x - 95, base), (x - 22, base - 150)]
        if k > 0:
            lvl = lerp(base, base - 130 * k, 1)
            liq = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            ImageDraw.Draw(liq).polygon([(x - 95, base), (x + 95, base), (x + 95 - 73 * (base - lvl) / 150, lvl), (x - 95 + 73 * (base - lvl) / 150, lvl)], fill=col + (235,))
            img.alpha_composite(liq)
            d = ImageDraw.Draw(img)
            for b in range(5):
                ph = (t * 0.8 + b * 0.21 + i * 0.13) % 1
                by = lerp(base - 10, lvl + 10, ph)
                d.ellipse((x - 40 + b * 18 - 5, by - 5, x - 40 + b * 18 + 5, by + 5), fill=(255, 255, 255, 120))
        d.line(neck + [neck[0]], fill=(235, 238, 245, 255), width=6)
        f = F("ExtraBold", 24)
        tl = lab.upper()
        while f.getlength(tl) > 230:
            f = F("ExtraBold", f.size - 1)
        d.text((x - f.getlength(tl) / 2, base + 34), tl, font=f, fill=(255, 255, 255, 255))
        if i < n - 1:
            ka = smooth((u - 0.2 - i * 0.22) / 0.12)
            if ka > 0:
                ax0, ax1 = x + 105, lerp(x + 105, xs[i + 1] - 105, ka)
                for xx in np.arange(ax0, ax1, 26):
                    d.line((xx, base - 60, xx + 12, base - 60), fill=CALL + (255,), width=5)
                if ka > 0.95:
                    d.polygon([(ax1, base - 72), (ax1 + 18, base - 60), (ax1, base - 48)], fill=CALL + (255,))
    if sh.get("splash") and u > 0.75:
        x = xs[-1]
        rng = np.random.default_rng(int(t * 10))
        for j in range(14):
            a = rng.uniform(-math.pi, 0)
            r = rng.uniform(40, 130) * smooth((u - 0.75) / 0.2)
            d.ellipse((x + r * math.cos(a) - 8, base - 140 + r * math.sin(a) - 8, x + r * math.cos(a) + 8, base - 140 + r * math.sin(a) + 8), fill=items[-1][1] + (255,))
    return img


def shot_fact(E, t, u, sh):
    img = dark_bg2(t, 0.0)
    if sh.get("bg_draw"):
        sh["bg_draw"](img, ImageDraw.Draw(img), t, u)
    d = ImageDraw.Draw(img)
    dur = sh["t1"] - sh["t0"]
    tr = u * dur
    al = ease(tr / 0.25)
    v = sh["value"].upper()
    f = F("Black", sh.get("size", 150))
    while f.getlength(v) > 960:
        f = F("Black", f.size - 6)
    pop = 1 + 0.25 * (1 - ease(tr / 0.25))
    fv = F("Black", int(f.size * pop))
    y = 640
    col = sh.get("col", (255, 255, 255))
    d.text((540 - fv.getlength(v) / 2 + 6, y + 8 - (fv.size - f.size) / 2), v, font=fv, fill=(0, 0, 0, int(180 * al)))
    d.text((540 - fv.getlength(v) / 2, y - (fv.size - f.size) / 2), v, font=fv, fill=col + (int(255 * al),))
    y += f.size * 1.12
    lf = F("Bold", 36)
    a2 = ease((tr - 0.25) / 0.25)
    for ln in wrap_lines(sh["line"].upper(), lf, 900):
        if not ln:
            continue
        d.text((540 - lf.getlength(ln) / 2, y), ln, font=lf, fill=(236, 238, 244, int(255 * a2)))
        y += 46
    if sh.get("plaque"):
        a3 = ease((tr - 0.45) / 0.2)
        pf = F("ExtraBold", 30)
        pt = sh["plaque"].upper()
        while pf.getlength(pt) > 860:
            pf = F("ExtraBold", pf.size - 1)
        w = pf.getlength(pt) + 36
        lay = Image.new("RGBA", (int(w) + 10, 60), (0, 0, 0, 0))
        ImageDraw.Draw(lay).rectangle((0, 0, w, 52), fill=RIB + (255,))
        ImageDraw.Draw(lay).text((18, 9), pt, font=pf, fill=(255, 255, 255, 255))
        lay = lay.rotate(1.6, expand=True, resample=Image.BICUBIC)
        lay.putalpha(lay.getchannel("A").point(lambda a: int(a * a3)))
        img.alpha_composite(lay, (int(540 - lay.size[0] / 2), int(y + 14)))
        y += 80
    n, p = sh.get("pages", (0, 0))
    if n:
        y += 40
        tw = n * 48 - 12
        for i in range(n):
            x = 540 - tw / 2 + i * 48
            d.rounded_rectangle((x, y, x + 36, y + 7), radius=3, fill=((236, 50, 56) if i == p else (80, 86, 100)) + (255,))
    return img
