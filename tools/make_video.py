"""Render a vertical 'body fact' video from a topic config.

Usage: python3 make_video.py topics.json OUT_DIR [only_slug ...]
"""
import json, math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS, DUR = 1080, 1920, 30, 15
BG = (10, 10, 22)
WHITE = (245, 245, 250)
FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
f_big = ImageFont.truetype(FONT_B, 92)
f_mid = ImageFont.truetype(FONT_B, 64)
f_num = ImageFont.truetype(FONT_B, 150)


def mix(fg, a):
    a = max(0.0, min(1.0, a))
    return tuple(int(BG[i] + (fg[i] - BG[i]) * a) for i in range(3))


def center_text(d, y, text, font, color):
    b = d.textbbox((0, 0), text, font=font)
    d.text(((W - (b[2] - b[0])) // 2 - b[0], y), text, font=font, fill=color)


def fade(t, t0, t1=None, fade_in=0.5, fade_out=0.4):
    a = min(1.0, (t - t0) / fade_in) if t >= t0 else 0.0
    if t1 is not None and t > t1 - fade_out:
        a = min(a, max(0.0, (t1 - t) / fade_out))
    return a


def ease(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def heart_points(cx, cy, scale):
    pts = []
    for i in range(240):
        a = 2 * math.pi * i / 240
        x = 16 * math.sin(a) ** 3
        y = 13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a)
        pts.append((cx + x * scale, cy - y * scale))
    return pts


def beat(t, bpm=75):
    period = 60.0 / bpm
    ph = (t % period) / period
    s = 0.11 * math.exp(-10 * ph)
    if ph > 0.25:
        s += 0.06 * math.exp(-10 * (ph - 0.25))
    return 1.0 + s


def fmt_num(n):
    return f"{int(n):,}".replace(",", " ")


def make_frame_fn(cfg):
    color = tuple(cfg["color"])
    shape = cfg.get("shape", "rings")
    n0, n1 = cfg["from"], cfg["to"]
    suffix = cfg.get("suffix", "")

    def frame(t):
        img = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(img)
        ha = fade(t, 2.5, None, fade_in=0.8)
        if ha > 0:
            glow = Image.new("RGB", (W, H), BG)
            gd = ImageDraw.Draw(glow)
            if shape == "heart":
                s = beat(t - 2.5)
                pts = heart_points(W // 2, 880, 24 * s)
                gd.polygon(pts, fill=mix(color, 0.9 * ha))
            else:
                for k in range(3):
                    ph = ((t - 2.5) * 0.45 + k / 3.0) % 1.0
                    r = 80 + 300 * ph
                    al = (1 - ph) * ha
                    gd.ellipse([W // 2 - r, 880 - r, W // 2 + r, 880 + r],
                               outline=mix(color, al), width=26)
                gd.ellipse([W // 2 - 70, 880 - 70, W // 2 + 70, 880 + 70], fill=mix(color, ha))
            glow = glow.filter(ImageFilter.GaussianBlur(40))
            img = Image.blend(img, glow, 0.8)
            d = ImageDraw.Draw(img)
            if shape == "heart":
                d.polygon(pts, fill=mix(color, ha))
            else:
                for k in range(3):
                    ph = ((t - 2.5) * 0.45 + k / 3.0) % 1.0
                    r = 80 + 300 * ph
                    d.ellipse([W // 2 - r, 880 - r, W // 2 + r, 880 + r],
                              outline=mix(color, (1 - ph) * ha), width=10)
                d.ellipse([W // 2 - 70, 880 - 70, W // 2 + 70, 880 + 70], fill=mix(color, ha))

        a = fade(t, 0.2, 3.2)
        if a > 0:
            center_text(d, 760, cfg["title"][0], f_big, mix(WHITE, a))
            center_text(d, 880, cfg["title"][1], f_big, mix(color, a))

        a = fade(t, 3.2, 10.5)
        if a > 0:
            v = n0 + (n1 - n0) * ease((t - 3.5) / 6.0)
            center_text(d, 1330, fmt_num(v) + suffix, f_num, mix(WHITE, a))
            center_text(d, 1520, cfg["unit"], f_mid, mix(color, a))

        a = fade(t, 10.8, None)
        if a > 0:
            center_text(d, 1290, cfg["outro"][0], f_mid, mix(WHITE, a))
            center_text(d, 1380, cfg["outro"][1], f_mid, mix(WHITE, a))
            center_text(d, 1520, cfg["tag"], f_big, mix(color, a))
        return np.asarray(img)

    return frame


def render(cfg, out):
    fn = make_frame_fn(cfg)
    cmd = ["ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
           "-shortest", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "96k", "-movflags", "+faststart", out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
    for i in range(FPS * DUR):
        p.stdin.write(fn(i / FPS).tobytes())
    p.stdin.close()
    p.wait()
    return p.returncode


if __name__ == "__main__":
    topics = json.load(open(sys.argv[1], encoding="utf-8"))
    out_dir = sys.argv[2]
    only = set(sys.argv[3:])
    os.makedirs(out_dir, exist_ok=True)
    for cfg in topics:
        if only and cfg["slug"] not in only:
            continue
        out = os.path.join(out_dir, cfg["slug"] + ".mp4")
        rc = render(cfg, out)
        print(cfg["slug"], rc, flush=True)
