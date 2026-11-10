"""Style-3 engine (references of 10.11: whirlpool / bleeding).
python3 engine3.py check  <spec.py> [t1,t2..]  -> sheet.png
python3 engine3.py render <spec.py>            -> <slug>.mp4 (video + music + sfx)
python3 engine3.py frame  <spec.py> <t> <out.png>
"""
import os, sys, math, subprocess, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from gfx import *
import gfx as G
import hero as HR
import organs as O
import scenes as SC

S = {}
SHOTS = []
T_END = 0.0
_static = {}
_hero = {}


def load(path):
    global S, SHOTS, T_END
    spec = importlib.util.spec_from_file_location("spec", path)
    m = importlib.util.module_from_spec(spec)
    for k, v in list(G.__dict__.items()):
        if not k.startswith("__"):
            m.__dict__[k] = v
    m.__dict__.update(dict(O=O, SC=SC, HR=HR, G=G, E=sys.modules[__name__], math=math, np=np, Image=Image, ImageDraw=ImageDraw, ImageFilter=ImageFilter))
    spec.loader.exec_module(m)
    S = m.SPEC
    S["_dir"] = os.path.dirname(os.path.abspath(path))
    SHOTS = []
    t = 0.0
    for i, sh in enumerate(S["shots"]):
        d = dict(sh)
        d["t0"], d["t1"], d["i"] = t, t + d.get("dur", 2.6), i
        t = d["t1"]
        SHOTS.append(d)
    T_END = t
    S["T_END"] = T_END
    # running HUD values: carry forward
    cur = {}
    for d in SHOTS:
        if d.get("hud") is not None:
            cur = dict(cur, **d["hud"])
        d["_hud"] = dict(cur)
    return S


def shot_at(t):
    for s in SHOTS:
        if s["t0"] <= t < s["t1"]:
            return s
    return SHOTS[-1]


def shot_named(n):
    for s in SHOTS:
        if s.get("name") == n:
            return s
    raise KeyError(n)


# ------------------------------------------------------------------ scene layer
def static_layer(sh):
    k = sh["i"]
    if k not in _static:
        b = sh.get("bg", "studio:teal")
        img = SC.bg(b, sh.get("bg_blur", 5)) if isinstance(b, str) else b()
        for fn in sh.get("static", []):
            fn(img)
        _static.clear() if len(_static) > 3 else None
        _static[k] = img
    return _static[k].copy()


def hero_layer(p, cx, cy, s, t):
    key = (round(cx), round(cy), round(s), tuple(sorted((k, v if not isinstance(v, list) else tuple(v)) for k, v in p.items() if k not in ("sweat", "tears"))),
           _blink(t, p))
    if key not in _hero:
        if len(_hero) > 12:
            _hero.clear()
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        q = dict(p)
        q["no_blink"] = True
        b = _blink(t, p)
        if b:
            q["open"] = q.get("open", 1.0) * (0.12 if b == 2 else 0.5)
        q.pop("sweat", None)
        q.pop("tears", None)
        HR.draw_body(lay, cx, cy, s, q, 0.0)
        if q.get("arms") == "up":
            HR.draw_arms(lay, cx, cy, s, q, 0.0)
        HR.draw_head(lay, cx, cy, s, q, 0.0)
        if q.get("arms") not in (None, "up", "down"):
            HR.draw_arms(lay, cx, cy, s, q, 0.0)
        _hero[key] = lay
    return _hero[key]


def _blink(t, p):
    if p.get("closed") or p.get("no_blink"):
        return 0
    ph = (t + p.get("blink_off", 0.0)) % 3.7
    if ph < 0.05 or 0.13 <= ph < 0.18:
        return 1
    if ph < 0.13:
        return 2
    return 0


def draw_hero(img, hp, t, u):
    p = {k: kv(v, u) if not isinstance(v, tuple) else v for k, v in hp.items() if k not in ("x", "y", "s", "bob")}
    cx, cy, s = kv(hp.get("x", 540), u), kv(hp.get("y", 900), u), kv(hp.get("s", 210), u)
    lay = hero_layer(p, cx, cy, s, t)
    sh = p.get("shake", 0)
    dx = 6 * math.sin(t * 1.3) * hp.get("bob", 1) + 12 * sh * math.sin(t * 31)
    dy = 4 * math.sin(t * 2.1) * hp.get("bob", 1) + 8 * sh * math.cos(t * 27)
    img.alpha_composite(lay, (int(dx), int(dy))) if dx >= 0 and dy >= 0 else paste_any(img, lay, int(dx), int(dy))
    HR.draw_fx(img, cx + dx, cy + dy, s, p, t)


# ------------------------------------------------------------------ camera
def cam_params(sh, u, t):
    c = sh.get("cam", {})
    z = kv(c.get("z", [(0, 1.0), (1, 1.07)]), u)
    x = kv(c.get("x", 0), u)
    y = kv(c.get("y", 0), u)
    r = kv(c.get("rot", 0), u)
    cx, cy = c.get("c", (540, 900))
    shk = kv(sh.get("fx", {}).get("shake", 0), u)
    for hit in sh.get("fx", {}).get("hits", []):
        tr = t - (sh["t0"] + hit[0])
        if 0 <= tr < 0.6:
            shk += hit[1] * (1 - tr / 0.6)
    x += 16 * shk * math.sin(t * 57)
    y += 16 * shk * math.cos(t * 49)
    # cut punch-in
    tr = t - sh["t0"]
    if sh["i"] > 0 and tr < 0.22 and not sh.get("no_punch"):
        z *= 1 + 0.07 * (1 - ease(tr / 0.22))
    return z, x, y, r, cx, cy


def apply_cam(img, z, x, y, r, cx, cy):
    if abs(z - 1) < 1e-3 and not x and not y and not r:
        return img
    a = math.radians(r)
    ca, sa = math.cos(a), math.sin(a)
    # inverse map: out(px) -> src = c + R^-1 (px - c - t) / z
    ia, ib = ca / z, sa / z
    id_, ie = -sa / z, ca / z
    ox, oy = cx + x, cy + y
    c0 = cx - (ia * ox + ib * oy)
    f0 = cy - (id_ * ox + ie * oy)
    return img.transform((W, H), Image.AFFINE, (ia, ib, c0, id_, ie, f0), resample=Image.BILINEAR)


def cam_point(p, z, x, y, r, cx, cy):
    a = math.radians(r)
    dx, dy = p[0] - cx, p[1] - cy
    return (cx + x + z * (dx * math.cos(a) - dy * math.sin(a)), cy + y + z * (dx * math.sin(a) + dy * math.cos(a)))


# ------------------------------------------------------------------ HUD (top bar like the references)
def ecg(ph):
    p = ph % 1.0
    v = 0.12 * math.exp(-((p - 0.12) / 0.035) ** 2) - 0.15 * math.exp(-((p - 0.235) / 0.012) ** 2) + math.exp(-((p - 0.26) / 0.014) ** 2)
    return v - 0.28 * math.exp(-((p - 0.285) / 0.014) ** 2) + 0.26 * math.exp(-((p - 0.48) / 0.05) ** 2)


def hud(img, sh, t, a=1.0):
    h = sh["_hud"]
    if not h or sh.get("no_hud"):
        return
    x0, y0, x1, y1 = 40, 176, 1040, 292
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.rounded_rectangle((x0, y0, x1, y1), radius=18, fill=(10, 14, 24, 200), outline=(90, 110, 140, 160), width=2)
    big, small = font(TITLE, 44), font(COND, 22)
    x = x0 + 28
    cols = [("time", (255, 255, 255)), ("hr", (255, 70, 80)), ("o2", (100, 200, 255)), ("v", (255, 255, 255))]
    for key, col in cols:
        if key not in h:
            continue
        val, lab = h[key] if isinstance(h[key], (list, tuple)) else (h[key], "")
        val = val if not callable(val) else val(t)
        if key == "hr":
            hv = float(str(val).split()[0]) if str(val)[0].isdigit() else 0
            col = (255, 70, 80) if hv > 110 or hv < 50 else (120, 230, 140)
            beat = 0.5 + 0.5 * math.cos(2 * math.pi * (t * max(hv, 1) / 60))
            _heart_icon(d, x + 14, y0 + 40, 13 * (1 + 0.15 * beat), col)
            x += 34
            lab = lab or "УД/МИН"
        if key == "o2":
            ov = float(str(val).rstrip("%")) if str(val)[0].isdigit() else 100
            col = (100, 200, 255) if ov >= 94 else ((255, 200, 60) if ov >= 85 else (255, 70, 80))
            lab = lab or "КИСЛОРОД"
        s_ = str(val)
        d.text((x, y0 + 16), s_, font=big, fill=col + (255,))
        d.text((x, y0 + 72), lab.upper(), font=small, fill=(170, 180, 200, 255))
        x += max(big.getlength(s_), small.getlength(lab.upper())) + 40
    # ecg trace
    hv = h.get("hr", (0,))
    hv = hv[0] if isinstance(hv, (list, tuple)) else hv
    try:
        hv = float(str(hv).split()[0])
    except Exception:
        hv = 0
    ex0, ex1 = max(x, 760), x1 - 24
    if ex1 - ex0 > 80:
        pts = []
        for xx in range(int(ex0), int(ex1), 3):
            tt = t - (ex1 - xx) / 180.0
            v = ecg(tt * hv / 60) if hv >= 1 else 0
            pts.append((xx, y0 + 66 - v * 30))
        d.line(pts, fill=(90, 230, 140, 255) if hv >= 1 else (255, 70, 80, 255), width=3)
    if a < 1:
        lay.putalpha(lay.getchannel("A").point(lambda v: int(v * a)))
    img.alpha_composite(lay)


def _heart_icon(d, x, y, r, col):
    d.ellipse((x - r, y - r, x, y), fill=col + (255,))
    d.ellipse((x, y - r, x + r, y), fill=col + (255,))
    d.polygon([(x - r, y - r * 0.4), (x + r, y - r * 0.4), (x, y + r * 1.1)], fill=col + (255,))


# ------------------------------------------------------------------ fact cards
def fact_bg(img, t, sh):
    glow(img, 540, 900, 900, (120, 14, 26), a=0.45)
    bokeh(img, t, n=26, col=(200, 30, 46), seed=sh["i"], speed=(0, -14), rmin=20, rmax=70, alpha=0.35, cells=True)
    img.alpha_composite(img.filter(ImageFilter.GaussianBlur(10)))


def draw_fact(img, sh, t):
    tr = t - sh["t0"]
    f = sh["fact"]
    y = 560
    label(img, 540, y, f.get("tag", "").upper(), col=(110, 200, 255), size=36, anchor="c", a=ease(tr / 0.2), name=COND)
    y = title_block(img, f["title"], y + 60, tr, size=92, maxw=960)
    big = f["big"]
    k = ease((tr - 0.25) / 0.3)
    if k > 0:
        fs = font(TITLE, f.get("size", 210) * (1 + 0.25 * (1 - k)))
        while fs.getlength(big) > 980:
            fs = font(TITLE, fs.size - 8)
        lay = Image.new("RGBA", (W, int(fs.size * 1.5)), (0, 0, 0, 0))
        dl = ImageDraw.Draw(lay)
        dl.text((540 - fs.getlength(big) / 2, 10), big, font=fs, fill=(234, 30, 44, int(255 * k)), stroke_width=10, stroke_fill=(255, 255, 255, int(255 * k)))
        img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(14)), (0, int(y + 30)))
        img.alpha_composite(lay, (0, int(y + 30)))
        y += fs.size * 1.15 + 30
    if f.get("unit"):
        label(img, 540, y, f["unit"].upper(), col=(255, 255, 255), size=54, anchor="c", a=ease((tr - 0.45) / 0.2), name=TITLE, stroke=6)
        y += 70
    if f.get("line"):
        sub_line(img, f["line"], y + 20, tr - 0.35, col=(230, 232, 240), size=40)


# ------------------------------------------------------------------ frame
def render_frame(i):
    t = i / FPS
    sh = shot_at(t)
    u = (t - sh["t0"]) / (sh["t1"] - sh["t0"])
    tr = t - sh["t0"]
    fx = sh.get("fx", {})
    if sh.get("kind") == "fact":
        img = SC.bg("studio:red", 0)
        fact_bg(img, t, sh)
    else:
        img = static_layer(sh)
        for fn in sh.get("draw", []):
            fn(img, t, u, sh)
        if sh.get("hero"):
            draw_hero(img, sh["hero"], t, u)
        for fn in sh.get("front", []):
            fn(img, t, u, sh)
    z, x, y, r, cx, cy = cam_params(sh, u, t)
    img = apply_cam(img, z, x, y, r, cx, cy)
    # particles in front (not camera-bound)
    if fx.get("rain"):
        rain(img, t, n=int(80 * fx["rain"]), alpha=0.3)
    if fx.get("cells"):
        bokeh(img, t, n=int(18 * fx["cells"]), col=(210, 30, 46), seed=sh["i"] + 3, speed=(-30, -10), rmin=14, rmax=60, alpha=0.6, cells=True)
    if fx.get("dust", 1):
        dust(img, t, n=30, seed=sh["i"])
    # grading
    if fx.get("blur"):
        img = img.filter(ImageFilter.GaussianBlur(kv(fx["blur"], u) * 12))
    if fx.get("double"):
        k = kv(fx["double"], u)
        sh2 = img.copy()
        img = Image.blend(img, ImageChops_offset(sh2, int(40 * k * (0.8 + 0.2 * math.sin(t * 2))), 0), 0.45 * min(1, k * 2))
    tint = kv(fx.get("tint", 0), u)
    if tint:
        img = _tint(img, tint, fx.get("tint_col", (190, 20, 34)))
    red = kv(fx.get("red", 0), u)
    if red:
        beat = 0.5 + 0.5 * math.cos(2 * math.pi * t * 1.6)
        img.alpha_composite(vignette_col((160, 0, 16), min(1, red * (0.6 + 0.4 * beat))))
    gray = kv(fx.get("gray", 0), u)
    if gray:
        a = np.asarray(img.convert("RGB")).astype(np.float32)
        l = a.mean(2, keepdims=True)
        img = Image.fromarray((a * (1 - gray) + l * gray).astype(np.uint8), "RGB").convert("RGBA")
    img.alpha_composite(vignette(0.75))
    tun = kv(fx.get("tunnel", 0), u)
    if tun:
        img.alpha_composite(tunnel(tun))
    dark = kv(fx.get("dark", 0), u)
    if dark:
        img.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, int(255 * min(1, dark)))))
    for fl in fx.get("flash", []):
        ft = t - (sh["t0"] + fl[0])
        if 0 <= ft < 0.5:
            c = fl[2] if len(fl) > 2 else (255, 30, 40)
            img.alpha_composite(Image.new("RGBA", (W, H), c + (int(230 * fl[1] * (1 - ft / 0.5)),)))
    img = grain(img, t, 7)
    # overlays
    ov_a = 1.0
    if sh.get("kind") == "fact":
        draw_fact(img, sh, t)
        pg = sh["fact"].get("page")
        if pg:
            label(img, 540, 480, f"ФАКТ {pg[0]}/{pg[1]}", col=(170, 180, 200), size=32, anchor="c", name=COND)
    else:
        hud(img, sh, t)
        first = sh["i"] == 0
        ty = sh.get("title_y", 330 if sh["_hud"] and not sh.get("no_hud") else 300)
        y2 = title_block(img, sh.get("title", []), ty, tr, size=sh.get("title_size", 104), first=first)
        sub_line(img, sh.get("sub", ""), y2 + 6, tr, first=first)
        for co in sh.get("callouts", []):
            at, p, l, txt = co[:4]
            col = co[4] if len(co) > 4 else (255, 255, 255)
            k = (u - at) * (sh["t1"] - sh["t0"]) / 0.4
            callout(img, cam_point(p, z, x, y, r, cx, cy), l, txt, k, col=col)
        for pop in sh.get("pops", []):
            at, txt, px, py = pop[:4]
            pt = tr - at
            if 0 <= pt < (pop[4] if len(pop) > 4 else 9):
                k = ease(pt / 0.15)
                ff = font(TITLE, 80 * (1 + 0.4 * (1 - k)))
                ImageDraw.Draw(img).text((px - ff.getlength(txt) / 2, py), txt, font=ff, fill=(255, 255, 255, int(255 * k)), stroke_width=8, stroke_fill=(0, 0, 0, 255))
    # cut transition: quick white flash + rgb split
    if sh["i"] > 0 and tr < 0.1 and not sh.get("soft_cut"):
        k = 1 - tr / 0.1
        a = np.asarray(img.convert("RGB")).copy()
        dx = int(18 * k)
        a[..., 0] = np.roll(a[..., 0], dx, 1)
        a[..., 2] = np.roll(a[..., 2], -dx, 1)
        img = Image.fromarray(a, "RGB").convert("RGBA")
        img.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(70 * k))))
    if sh.get("soft_cut") and sh["i"] > 0 and tr < 0.35:
        prev = SHOTS[sh["i"] - 1]
        # dissolve from black
        img.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, int(255 * (1 - tr / 0.35)))))
    if sh.get("kind") == "loop":
        pass
    return img.convert("RGB")


def ImageChops_offset(img, dx, dy):
    out = Image.new("RGBA", img.size, (0, 0, 0, 0))
    out.paste(img, (dx, dy))
    return out


def _tint(img, k, col):
    a = np.asarray(img.convert("RGB")).astype(np.float32)
    l = a.mean(2, keepdims=True) / 255.0
    c = np.array(col, np.float32)
    out = a * (1 - k) + (l * 1.3 * c) * k
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGB").convert("RGBA")


_vc = {}


def vignette_col(col, k):
    key = (col, round(k, 2))
    if key not in _vc:
        if len(_vc) > 50:
            _vc.clear()
        base = vignette(1.0, 0.45)
        a = np.asarray(base.getchannel("A")).astype(np.float32) * k
        arr = np.zeros((H, W, 4), np.uint8)
        arr[..., 0], arr[..., 1], arr[..., 2] = col
        arr[..., 3] = np.clip(a * 1.2, 0, 255).astype(np.uint8)
        _vc[key] = Image.fromarray(arr, "RGBA")
    return _vc[key]


def tunnel(k):
    key = ("tun", round(k, 2))
    if key not in _vc:
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H * 0.47) / (H / 2)) ** 2)
        al = np.clip((r - (1.05 - 0.8 * k)) / 0.35, 0, 1) * 255
        arr = np.zeros((H, W, 4), np.uint8)
        arr[..., 3] = al.astype(np.uint8)
        _vc[key] = Image.fromarray(arr, "RGBA")
    return _vc[key]


# ------------------------------------------------------------------ CLI
def render_part(n0, n1, out):
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(n0, n1):
        p.stdin.write(render_frame(i).tobytes())
    p.stdin.close()
    p.wait()


def sheet(ts, out):
    ims = [render_frame(int(round(t * FPS))) for t in ts]
    cols = 6
    rows = (len(ims) + cols - 1) // cols
    sh = Image.new("RGB", (cols * 226 + 10, rows * 394 + 10), (60, 60, 60))
    for k, im in enumerate(ims):
        im = im.copy()
        dd = ImageDraw.Draw(im, "RGBA")
        dd.rectangle((0, 0, 1080, 150), fill=(255, 0, 255, 50))
        dd.rectangle((940, 880, 1080, 1600), fill=(255, 0, 255, 50))
        dd.rectangle((0, 1560, 1080, 1920), fill=(255, 0, 255, 50))
        sh.paste(im.resize((216, 384)), (10 + (k % cols) * 226, 10 + (k // cols) * 394))
    sh.save(out)


if __name__ == "__main__":
    cmd, path = sys.argv[1], sys.argv[2]
    load(path)
    d = S["_dir"]
    if cmd == "check":
        ts = [float(x) for x in sys.argv[3].split(",")] if len(sys.argv) > 3 else [round(s["t0"] + 0.6 * (s["t1"] - s["t0"]), 2) for s in SHOTS]
        sheet(ts, os.path.join(d, "sheet.png"))
        print("sheet", os.path.join(d, "sheet.png"), "T_END", round(T_END, 2), "shots", len(SHOTS))
    elif cmd == "frame":
        render_frame(int(round(float(sys.argv[3]) * FPS))).save(sys.argv[4])
    elif cmd == "part":
        render_part(int(sys.argv[3]), int(sys.argv[4]), sys.argv[5])
    elif cmd == "audio":
        import music
        music.build(sys.modules[__name__], os.path.join(d, "_score.wav"))
    elif cmd == "render":
        N = int(round(T_END * FPS))
        mid = N // 2
        p1, p2 = os.path.join(d, "_p1.mp4"), os.path.join(d, "_p2.mp4")
        procs = [subprocess.Popen([sys.executable, __file__, "part", path, "0", str(mid), p1]),
                 subprocess.Popen([sys.executable, __file__, "part", path, str(mid), str(N), p2])]
        import music
        wav = os.path.join(d, "_score.wav")
        music.build(sys.modules[__name__], wav)
        for p in procs:
            p.wait()
        lst = os.path.join(d, "_list.txt")
        open(lst, "w").write(f"file '{p1}'\nfile '{p2}'\n")
        out = os.path.join(d, S["slug"] + ".mp4")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-i", wav, "-map", "0:v", "-map", "1:a",
                        "-c:v", "libx264", "-preset", "medium", "-crf", "22", "-maxrate", "6M", "-bufsize", "12M", "-pix_fmt", "yuv420p",
                        "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out], check=True)
        for f in (p1, p2, lst):
            os.remove(f)
        print("video", out)
