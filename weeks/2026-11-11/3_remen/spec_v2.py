# ДТП без ремня на заднем сиденье — 13 ноября 2026 (Стиль-2)
# Источники:
#  - ВОЗ, информационный бюллетень «Травмы в результате ДТП»: ремень безопасности снижает риск гибели водителя и пассажиров
#    переднего сиденья до 50%, пассажиров заднего сиденья — до 25%.
#  - Ichikawa M., Nakahara S., Wakai S. «Mortality of front-seat occupants attributable to unbelted rear-seat passengers
#    in car crashes», The Lancet, 2002: риск гибели пристёгнутого переднего пассажира/водителя примерно в 5 раз выше,
#    если сзади сидит непристёгнутый пассажир.
#  - Физика: скорость 60 км/ч = 16,7 м/с, эквивалентная высота падения h = v²/2g ≈ 14 м (≈ 5 этаж).
#  - NHTSA, «Occupant protection» / материалы по механизму травм: при ударе машина останавливается за доли секунды,
#    непристёгнутое тело продолжает двигаться с прежней скоростью; мозг и внутренние органы ударяются по инерции.
import math

LYING = {"rot": -math.pi / 2, "cy": 0.5, "dy": 0.12, "arm_a_r": 0.05, "arm_a_l": 0.05}


def buckle_hook(img, d, t, u, *_):
    # seat belt and an empty buckle
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(g).ellipse((260, 820, 820, 1320), fill=(200, 40, 50, 36))
    img.alpha_composite(g.filter(ImageFilter.GaussianBlur(60)))
    d = ImageDraw.Draw(img)
    sw = 6 * math.sin(t * 2)
    d.polygon([(150, 700), (230, 700), (560 + sw, 1040), (480 + sw, 1040)], fill=(40, 44, 54, 255))
    for k in range(10):
        y = 720 + k * 32
        x = 190 + (y - 700) * 1.0
        d.line((x - 30 + sw * k / 10, y, x + 30 + sw * k / 10, y), fill=(60, 66, 80, 255), width=3)
    d.rounded_rectangle((470 + sw, 1020, 590 + sw, 1160), radius=10, fill=(190, 196, 206, 255))
    d.rectangle((500 + sw, 1040, 560 + sw, 1100), fill=(120, 126, 136, 255))
    d.rounded_rectangle((640, 1130, 840, 1260), radius=22, fill=(30, 32, 40, 255))
    d.rounded_rectangle((675, 1150, 805, 1190), radius=8, fill=(220, 40, 50, 255))
    d.text((690, 1153), "PRESS", font=F("Black", 28), fill=(255, 255, 255, 255))


def person_side(d, x, y, sc, col, lean=0.0, belt=False, skin=(232, 186, 156)):
    """simple side-view seated figure, hip at (x, y), facing right"""
    hx, hy = x + lean * 80 * sc, y - 150 * sc
    d.line([(x, y), (hx, hy)], fill=col + (255,), width=int(60 * sc))
    d.line([(x, y), (x + 110 * sc, y + 6 * sc), (x + 120 * sc, y + 100 * sc)], fill=(50, 60, 90, 255), width=int(42 * sc), joint="curve")
    d.ellipse((hx - 6 * sc, hy - 98 * sc, hx + 76 * sc, hy - 16 * sc), fill=skin + (255,))
    d.chord((hx - 6 * sc, hy - 104 * sc, hx + 76 * sc, hy - 30 * sc), 180, 340, fill=(60, 44, 34, 255))
    d.line([(hx + 10 * sc, hy - 20 * sc), (hx + 70 * sc + lean * 30 * sc, hy + 50 * sc)], fill=col + (255,), width=int(26 * sc))
    if belt:
        d.line([(x - 20 * sc, hy - 10 * sc), (x + 40 * sc, y - 10 * sc)], fill=(230, 190, 60, 255), width=int(12 * sc))
    return hx, hy


def car_shot(t, u, sh):
    img = E.dark_bg(t, 0.0)
    d = ImageDraw.Draw(img)
    gy = 1210
    spd = sh.get("speed", 1.0)
    tt = t * spd
    rng = np.random.default_rng(4)
    for k in range(40):
        x, y = rng.uniform(0, 1080), rng.uniform(450, 800)
        d.ellipse((x, y, x + 3, y + 3), fill=(200, 210, 255, 140))
    for k in range(-1, 6):
        x = k * 330 - (tt * 900) % 330
        d.rectangle((x, gy - 470, x + 14, gy), fill=(52, 54, 64, 255))
        d.ellipse((x - 26, gy - 488, x + 40, gy - 460), fill=(255, 210, 140, 200))
    d.rectangle((0, gy, W, H), fill=(34, 34, 40, 255))
    for k in range(-1, 9):
        x = k * 170 - (tt * 1600) % 170
        d.rectangle((x, gy + 70, x + 85, gy + 82), fill=(210, 210, 200, 255))
    crash = E.val(sh.get("crash", 0.0), u)
    fly = E.val(sh.get("fly", 0.0), u)
    if sh.get("pole") is not None:
        px = sh["pole"] if not isinstance(sh["pole"], (list, tuple)) else pw(sh["pole"], u)
        d.rectangle((px, gy - 640, px + 46, gy + 20), fill=(110, 112, 120, 255), outline=(60, 60, 66, 255), width=3)
    # car body
    x0, x1 = 120, 950 - 150 * crash
    yb = gy - 70
    body = [(x0, yb), (x0, yb - 150), (x0 + 120, yb - 170), (x0 + 220, yb - 330), (x1 - 290, yb - 330), (x1 - 170, yb - 180), (x1, yb - 150), (x1, yb)]
    d.polygon(body, fill=(170, 30, 40, 255), outline=(90, 10, 20, 255))
    win = [(x0 + 150, yb - 175), (x0 + 240, yb - 310), (x1 - 300, yb - 310), (x1 - 195, yb - 180)]
    d.polygon(win, fill=(30, 40, 60, 255))
    # people inside (drawn over window, clipped roughly)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(lay)
    seat_f = x1 - 380 + 150 * crash
    ld.rounded_rectangle((seat_f - 60, yb - 330 + 70, seat_f - 10, yb - 60), radius=16, fill=(40, 40, 46, 255))
    ld.rounded_rectangle((x0 + 170, yb - 330 + 80, x0 + 220, yb - 60), radius=16, fill=(40, 40, 46, 255))
    dl = min(0.35, crash * 0.35) + sh.get("drv_lean", 0.0)
    person_side(ld, seat_f + 10, yb - 80, 0.9, (60, 120, 180), lean=dl, belt=True)
    bx = x0 + 260 + fly * 300
    person_side(ld, bx, yb - 80 - fly * 30, 0.9, (220, 120, 40), lean=fly * 0.6)
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).polygon(win, fill=255)
    img.paste(lay, (0, 0), ImageChops_mask(mask, lay))
    d = ImageDraw.Draw(img)
    d.line(win + [win[0]], fill=(200, 210, 230, 255), width=5)
    d.line([(x1 - 470, yb - 330), (x1 - 470, yb - 10)], fill=(90, 10, 20, 255), width=6)
    if crash > 0:
        rng = np.random.default_rng(int(crash * 20))
        for k in range(int(10 * crash)):
            a = (x1 - rng.uniform(0, 80), yb - rng.uniform(0, 150))
            d.line([a, (a[0] - rng.uniform(20, 60), a[1] + rng.uniform(-40, 40))], fill=(70, 6, 12, 255), width=4)
        cx, cy = x1 - 230, yb - 250
        for k in range(8):
            a = k * 0.8
            d.line([(cx, cy), (cx + 70 * crash * math.cos(a), cy + 70 * crash * math.sin(a))], fill=(230, 240, 255, 220), width=3)
        for k in range(int(26 * crash)):
            ph = rng.uniform(0, 1)
            sx, sy = x1 + rng.uniform(-20, 120) * crash, yb - rng.uniform(0, 300)
            d.polygon([(sx, sy), (sx + 10, sy + 4), (sx + 3, sy + 12)], fill=(220, 235, 255, 220))
    for wx in (x0 + 140, x1 - 170):
        d.ellipse((wx - 70, yb - 70, wx + 70, yb + 70), fill=(20, 20, 24, 255))
        d.ellipse((wx - 34, yb - 34, wx + 34, yb + 34), fill=(130, 134, 144, 255))
        a = tt * 20
        d.line((wx, wx and yb, wx + 30 * math.cos(a), yb + 30 * math.sin(a)), fill=(60, 60, 66, 255), width=6)
    if crash < 0.3:
        beam = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(beam).polygon([(x1, yb - 120), (1080, yb - 220), (1080, yb + 40)], fill=(255, 240, 200, 70))
        img.alpha_composite(beam.filter(ImageFilter.GaussianBlur(20)))
    z, cx, cy = 1.15, 560, 1000
    w2, h2 = int(W * z), int(H * z)
    big = img.resize((w2, h2), Image.BILINEAR)
    ox, oy = int(cx * z - 540), int(cy * z - 950)
    return big.crop((ox, oy, ox + W, oy + H))


def ImageChops_mask(mask, lay):
    from PIL import ImageChops
    return ImageChops.multiply(mask, lay.getchannel("A"))


def tilt_head(t, u):
    return {"arm_a_r": 0.14, "arm_a_l": 0.14, "head": 0.18 * math.sin(min(1, u * 3) * math.pi) * (1 - u)}


SPEC = dict(
    style=2,
    slug="remen",
    title="Не пристегнулся на заднем",
    caption="«Да тут ехать 5 минут» — сказал он и не пристегнулся сзади… А пострадал не только он 😨 Ты пристёгиваешься на заднем? 👇",
    hashtags="#ремень #дтп #чтобудетесли #симуляция #организм",
    over="ДАНЯ, 19 · ЗАДНЕЕ СИДЕНЬЕ",
    card=dict(label="СКОРОСТЬ ТЕЛА", right_label="ПОСЛЕ УДАРА", fmt="{v:.0f}%", notes=[],
              minis=[("ПУЛЬС", "hr"), ("РЕМЕНЬ", "!НЕТ"), ("СОЗНАНИЕ", "ЯСНОЕ")]),
    hr=[(0, 80), (8, 82), (11, 120), (30, 130), (34, 60), (40, 96), (60, 90)],
    shots=[
        dict(kind="hook", dur=2.3, phrase="«ДА ТУТ ЕХАТЬ\n5 МИНУТ»", draw=buckle_hook, over="РЕМЕНЬ СЗАДИ"),
        dict(kind="eye", dur=1.0, card=False, pupil=0.35, look=0.12, over="ЗАДНЕЕ СИДЕНЬЕ", blink=0.5),
        dict(kind="custom", fn=car_shot, dur=3.0, title="РЕМЕНЬ? ЗАЧЕМ", tag="друг за рулём пристёгнут, Даня — нет", value=100, value_txt="60 КМ/Ч",
             clock="—", amb="street", callouts=[(0.25, (569, 938), (740, 640), "РЕМЕНЬ"), (0.45, (379, 950), (200, 640), "НЕ ПРИСТЕГНУТ", (255, 110, 110))]),
        dict(kind="custom", fn=car_shot, dur=2.6, over="ВРЕМЯ ЗАМЕДЛЕНО ×1000", title="ЗАНОС", tag="мокрая дорога — впереди столб", pole=[(0, 1300), (1, 960)],
             speed=0.35, value=100, value_txt="60 КМ/Ч", clock="0,000 С", badge="×1000 замедлено", riser=True, amb="street"),
        dict(kind="custom", fn=car_shot, dur=2.8, over="0,02 СЕКУНДЫ", title="МАШИНА ВСТАЛА", tag="а тело всё ещё летит 60 км/ч", pole=900, speed=0.0,
             crash=[(0, 0), (0.3, 1.0)], value=100, value_txt="60 КМ/Ч", clock="0,020 С", badge="×1000 замедлено", flash=[(0.1, 0.6)],
             hits=[(0.1, 1.5, True)], name="hit"),
        dict(kind="custom", fn=car_shot, dur=2.8, over="0,05 СЕКУНДЫ", title="ВОДИТЕЛЯ ДЕРЖИТ РЕМЕНЬ", tag="Даню не держит ничего", pole=900, speed=0.0,
             crash=1.0, fly=[(0, 0), (1, 0.55)], value=100, value_txt="60 КМ/Ч", clock="0,050 С", badge="×1000 замедлено",
             callouts=[(0.3, (632, 904), (760, 640), "ПОЯС УДЕРЖАЛ")]),
        dict(kind="bignum", dur=2.6, over="0,05 СЕКУНДЫ", value="≈ 14 М", size=180, sub=[("60 км/ч без ремня — как упасть", WHITE), ("с 5-го этажа", (255, 120, 120))],
             card=False, red=0.4),
        dict(kind="custom", fn=car_shot, dur=2.8, over="0,07 СЕКУНДЫ", title="УДАР В СПИНУ ВОДИТЕЛЯ", tag="удар в десятки раз сильнее веса Дани", pole=900,
             speed=0.0, crash=1.0, fly=[(0, 0.55), (0.3, 0.95), (1, 1.0)], drv_lean=0.25, value=(100, 30), value_txt=None, clock="0,070 С",
             badge="×1000 замедлено", flash=[(0.3, 0.8)], hits=[(0.3, 1.6, False)], minis=[("ПУЛЬС", "hr"), ("ВОДИТЕЛЬ", "!УДАР"), ("СОЗНАНИЕ", "!НЕТ")],
             name="back"),
        dict(kind="xray", dur=2.8, over="0,1 СЕКУНДЫ", title="МОЗГ БЬЁТСЯ О ЧЕРЕП", tag="голова встала — а мозг ещё летит", cam=(0.0, 0.07, 4.2),
             expr="sleep", pose=tilt_head, value=20, clock="0,100 С", badge="×1000 замедлено", red=0.5,
             glow=[dict(at=(0.03, 0.04), r=0.025, col=(255, 40, 40), k=[(0, 0), (0.3, 1.0)])], hits=[(0.4, 1.0, False)],
             minis=[("ПУЛЬС", "hr"), ("ДЫХАНИЕ", "!СБИТО"), ("СОЗНАНИЕ", "!НЕТ")],
             callouts=[(0.4, (620, 900), (780, 1180), "УШИБ МОЗГА", (255, 110, 110))]),
        dict(kind="xray", dur=2.8, over="0,12 СЕКУНДЫ", title="ОРГАНЫ ЛЕТЯТ ДАЛЬШЕ", tag="внутри груди рвутся сосуды", cam=(0.0, 0.28, 2.2),
             expr="sleep", value=10, clock="0,120 С", badge="×1000 замедлено", red=0.6, red_tint=0.25,
             glow=[dict(at=(0.01, 0.25), r=0.05, col=(255, 40, 40), k=[(0, 0.3), (1, 1.0)])],
             callouts=[(0.3, (560, 830), (800, 700), "СОСУДЫ ГРУДИ", (255, 110, 110))]),
        dict(kind="custom", fn=car_shot, dur=2.8, over="1 СЕКУНДА СПУСТЯ", title="ТИШИНА", tag="мигает аварийка… из салона ни звука", pole=900, speed=0.0,
             crash=1.0, fly=1.0, drv_lean=0.3, value=0, value_txt="0 КМ/Ч", clock="1 С", red_tint=0.35, red=0.3),
        dict(kind="scene", dur=2.8, preset="ward", ground=1500, over="РЕАНИМАЦИЯ", title="ДАНЯ ВЫЖИЛ", tag="переломы и ушиб мозга",
             cam=(0.0, 0.62, 1.05), outfit="hosp", expr="sleep", pose=LYING, props_back=[("bed", {})], props=[("monitor", {"at": (0.45, 0.3)}), ("iv", {"x": -0.5})],
             value=0, value_txt="0 КМ/Ч", clock="+1 ДЕНЬ", minis=[("ПУЛЬС", "hr"), ("ДЫХАНИЕ", "ИВЛ"), ("СОЗНАНИЕ", "!КОМА")]),
        dict(kind="hook", dur=2.8, phrase="А ВОДИТЕЛЬ —\nНЕТ", over="СТРАШНЕЕ ВСЕГО", y=700, size=120, name="twist"),
        dict(kind="fact", dur=2.6, value="×5", size=200, line="выше риск гибели пристёгнутого водителя, если сзади не пристегнулись", plaque="The Lancet, 2002", pages=(5, 0)),
        dict(kind="fact", dur=2.6, value="ДО 50%", line="на столько ремень снижает риск гибели впереди", plaque="данные ВОЗ", pages=(5, 1)),
        dict(kind="fact", dur=2.6, value="ДО 25%", line="на столько ремень снижает риск гибели сзади", plaque="данные ВОЗ", pages=(5, 2)),
        dict(kind="fact", dur=2.6, value="≈ 14 М", col=(255, 210, 70), line="падение, равное удару на 60 км/ч без ремня", plaque="≈ 5-й этаж", pages=(5, 3)),
        dict(kind="fact", dur=3.0, value="СЕЛ НАЗАД?", line="даже если ехать 5 минут —", plaque="пристегнись", pages=(5, 4)),
        dict(kind="loop", dur=1.6),
    ],
    sfx=[(("hit", 0.1), "crunch", {"dur": 0.5, "g": 0.8}), (("hit", 0.15), "slam", {"g": 0.7}), (("back", 0.3), "thud", {"g": 0.8}),
         (("back", 0.35), "crunch", {"dur": 0.3, "g": 0.4}), (7.0, "whoosh", {"g": 0.3})],
)
