"""Phone / chat / monitor props for style-3."""
import math
from PIL import Image, ImageDraw
from gfx import shade, glow, font, BODY, TITLE, COND, ease, catmull, stroke_path, mixc


def phone(img, cx, cy, s, t, screen=None, msgs=None, u=0.0, call_t=None):
    """phone of height ~ 2*s centred at (cx, cy), screen content: dict(top, big, sub) or chat msgs [(text, 'l'|'r')]"""
    w, h = s * 0.95, s * 1.95
    x0, y0, x1, y1 = cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2
    glow(img, cx, cy, s * 1.6, (110, 150, 230), a=0.35)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((x0, y0, x1, y1), radius=int(s * 0.16), fill=(26, 26, 32, 255), outline=(130, 134, 150, 255), width=5)
    m = s * 0.05
    d.rounded_rectangle((x0 + m, y0 + m, x1 - m, y1 - m), radius=int(s * 0.1), fill=(16, 20, 32, 255))
    d.rounded_rectangle((cx - s * 0.14, y0 + m * 1.6, cx + s * 0.14, y0 + m * 2.4), radius=int(s * 0.03), fill=(4, 4, 6, 255))
    if msgs:
        y = y0 + s * 0.28
        f = font(BODY, s * 0.088)
        for k, (txt, side) in enumerate(msgs):
            a = ease((u - k * 0.25) / 0.08)
            if a <= 0:
                continue
            words, lines, cur = txt.split(), [], ""
            for wd in words:
                if f.getlength(cur + " " + wd) > w * 0.66 and cur:
                    lines.append(cur)
                    cur = wd
                else:
                    cur = (cur + " " + wd).strip()
            lines.append(cur)
            bw = max(f.getlength(l) for l in lines) + s * 0.08
            bh = len(lines) * f.size * 1.25 + s * 0.06
            bx = x0 + m * 2 if side == "l" else x1 - m * 2 - bw
            col = (58, 64, 82) if side == "l" else (40, 120, 240)
            d.rounded_rectangle((bx, y, bx + bw, y + bh), radius=int(s * 0.05), fill=col + (int(255 * a),))
            yy = y + s * 0.03
            for l in lines:
                d.text((bx + s * 0.04, yy), l, font=f, fill=(255, 255, 255, int(255 * a)))
                yy += f.size * 1.25
            y += bh + s * 0.05
    elif screen:
        f1 = font(COND, s * 0.09)
        top = screen.get("top", "")
        d.text((cx - f1.getlength(top) / 2, y0 + s * 0.35), top, font=f1, fill=(180, 190, 210, 255))
        fb = font(TITLE, s * 0.36)
        big = screen.get("big", "")
        d.text((cx - fb.getlength(big) / 2, y0 + s * 0.48), big, font=fb, fill=(255, 255, 255, 255))
        sub = screen.get("sub", "")
        d.text((cx - f1.getlength(sub) / 2, y0 + s * 0.92), sub, font=f1, fill=(180, 190, 210, 255))
        if call_t is not None:
            tt = f"00:{int(call_t):02d}"
            d.text((cx - f1.getlength(tt) / 2, y0 + s * 1.05), tt, font=f1, fill=(110, 230, 140, 255))
        by = y1 - s * 0.38
        r = s * 0.13 * (1 + 0.06 * math.sin(t * 8))
        glow(img, cx, by, r * 2.4, (255, 50, 60), a=0.5)
        d.ellipse((cx - r, by - r, cx + r, by + r), fill=(230, 40, 50, 255))
        d.rounded_rectangle((cx - r * 0.5, by - r * 0.16, cx + r * 0.5, by + r * 0.16), radius=int(r * 0.15), fill=(255, 255, 255, 255))


def monitor(img, x0, y0, x1, y1, t, hr=90, spo2=None, col=(90, 240, 140)):
    import engine3 as E
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((x0, y0, x1, y1), radius=14, fill=(8, 12, 14, 255), outline=(120, 130, 140, 255), width=4)
    pts = []
    for xx in range(int(x0 + 16), int(x1 - 120), 3):
        tt = t - (x1 - 120 - xx) / 160.0
        v = E.ecg(tt * hr / 60) if hr >= 1 else 0
        pts.append((xx, (y0 + y1) / 2 - v * (y1 - y0) * 0.3))
    d.line(pts, fill=(col if hr >= 1 else (255, 60, 60)) + (255,), width=4)
    f = font(TITLE, (y1 - y0) * 0.3)
    d.text((x1 - 110, y0 + 14), str(int(hr)), font=f, fill=(col if hr >= 1 else (255, 60, 60)) + (255,))
    if spo2 is not None:
        d.text((x1 - 110, y0 + 20 + f.size), f"{spo2}%", font=font(TITLE, (y1 - y0) * 0.2), fill=(100, 200, 255, 255))
