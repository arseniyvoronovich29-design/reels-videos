# Ужалила медуза-коробочка — 5 ноября 2026
# Источники: NT Government (Австралия) — Chironex: колокол 25–30 см, по 10–12 щупалец в каждом углу, 2 м и длиннее;
#            мгновенная сильная боль, белые полосы → красные «как от плети»; остановка сердца и смерть примерно за 5 минут;
#            первая помощь: из воды, 000, СЛР, уксус; пресной водой не промывать; сезон октябрь–май.
#            LITFL (Box jellyfish) — сердечный токсин, если остановка — обычно в первые 5 минут; долгая СЛР; противоядие CSL.
import math


def jelly(d, cx, cy, sc, t, al=120, n_tent=12):
    """translucent box jellyfish: square bell + long trailing tentacles (screen px, SS scale)"""
    bw = 0.13 * sc
    d.rounded_rectangle((cx - bw, cy - bw * 0.9, cx + bw, cy + bw * 0.5), radius=int(bw * 0.35), fill=(190, 220, 255, al), outline=(230, 245, 255, min(255, al + 80)), width=max(2, int(sc * 0.003)))
    for k in range(n_tent):
        x0 = cx - bw * 0.9 + k * (bw * 1.8 / (n_tent - 1))
        pts = []
        for j in range(16):
            q = j / 15
            pts.append((x0 + 0.04 * sc * math.sin(q * 6 + t * 2 + k), cy + bw * 0.5 + q * 0.9 * sc))
        d.line(pts, fill=(200, 230, 255, int(al * 0.9)), width=max(2, int(sc * 0.0025)), joint="curve")


def draw_swim(img, d, t, u, T0, s, T):
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ld = ImageDraw.Draw(lay)
    x, y = T0(0.32 - 0.08 * u, 0.55)
    jelly(ld, x, y, s, t, al=70)
    img.alpha_composite(lay)


def draw_contact(img, d, t, u, T0, s, T):
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ld = ImageDraw.Draw(lay)
    x, y = T0(0.16, 0.50)
    jelly(ld, x, y, s, t, al=110)
    # tentacles wrapped around the shin
    for k in range(6):
        yy = 0.70 + k * 0.035
        a, b = T(0.0, yy), T(0.12, yy + 0.02)
        ld.arc(A.box(T(-0.02, yy - 0.012), T(0.11, yy + 0.02)), 200, 360, fill=(255, 255, 255, 220), width=max(2, int(s * 0.003)))
    img.alpha_composite(lay)


def shot_nemato(t, u, sh):
    img = E.dark_bg(t, 0.5)
    d = ImageDraw.Draw(img)
    # skin layers
    d.rectangle((60, 980, 1020, 1030), fill=(236, 170, 150, 255))
    d.rectangle((60, 1030, 1020, 1170), fill=(220, 120, 120, 255))
    d.text((70, 990), "кожа", font=F("SemiBold", 22), fill=(60, 30, 30, 255))
    # tentacle with stinging capsules
    d.rounded_rectangle((60, 700, 1020, 760), radius=30, fill=(200, 230, 255, 200))
    for k in range(9):
        x = 120 + k * 105
        fire = smooth((u - 0.1 - k * 0.04) / 0.15)
        d.ellipse((x - 26, 740, x + 26, 820), fill=(170, 210, 250, 255), outline=(255, 255, 255, 255), width=3)
        if fire < 1:
            for j in range(4):
                d.arc((x - 16 + j * 3, 760 + j * 12, x + 16 - j * 3, 790 + j * 12), 0, 300, fill=(60, 90, 160, 255), width=3)
        if fire > 0:
            y1 = lerp(820, 1100, fire)
            d.line((x, 820, x + 6, y1), fill=(255, 240, 120, 255), width=5)
            d.polygon([(x + 6, y1 + 18), (x - 6, y1 - 4), (x + 18, y1 - 4)], fill=(255, 240, 120, 255))
            if fire > 0.9:
                d.ellipse((x - 30, y1 - 10, x + 40, y1 + 40), fill=(150, 255, 120, 180))
    d.text((540 - F("Bold", 30).getlength("стрекательные клетки стреляют ядом") / 2, 1200), "стрекательные клетки стреляют ядом", font=F("Bold", 30), fill=(255, 220, 90, 255))
    return img


def shot_welts(t, u, sh):
    img = E.grad((40, 20, 20), (10, 6, 6))
    d = ImageDraw.Draw(img)
    # a leg close-up filling the frame
    d.rounded_rectangle((250, 420, 830, 1700), radius=260, fill=(232, 186, 156, 255))
    rr = np.random.default_rng(3)
    k = smooth(u / 0.7)
    for j in range(7):
        y0 = 620 + j * 110
        col = E.mixc((255, 245, 245), (210, 30, 45), smooth((u - 0.15) / 0.35))
        x0, x1 = 270, 810
        n = int(14 * k)
        pts = [(lerp(x0, x1, q / 13), y0 + 30 * math.sin(q * 0.8 + j) + 20 * j * 0.1) for q in range(n)]
        if len(pts) > 1:
            d.line(pts, fill=col + (255,), width=26, joint="curve")
            for q in range(1, n, 2):
                x, y = pts[q]
                d.line((x, y - 18, x + 6, y + 18), fill=col + (255,), width=6)
    return img


def draw_cpr(img, d, t, u, T0, s, T):
    # rescuer kneeling at the chest, pushing in rhythm (~110/min)
    push = abs(math.sin(t * math.pi * 110 / 60))
    cx, cy = T(0.0, 0.28)
    k = s / 900
    hy = cy - (110 + 18 * push) * k
    d.ellipse((cx - 40 * k, hy - 260 * k, cx + 40 * k, hy - 180 * k), fill=(70, 60, 56, 255))
    d.rounded_rectangle((cx - 60 * k, hy - 185 * k, cx + 60 * k, hy - 20 * k), radius=int(20 * k), fill=(220, 60, 40, 255))
    d.line((cx - 30 * k, hy - 150 * k, cx, cy - 6 * k), fill=(200, 160, 130, 255), width=int(22 * k))
    d.line((cx + 30 * k, hy - 150 * k, cx, cy - 6 * k), fill=(200, 160, 130, 255), width=int(22 * k))


def draw_vinegar(img, d, t, u, T0, s, T):
    k = s / 900
    bx, by = 650 * SS, (700 + 30 * math.sin(t * 2)) * SS
    d.rounded_rectangle((bx - 50 * k, by - 160 * k, bx + 50 * k, by + 40 * k), radius=int(18 * k), fill=(240, 240, 230, 255), outline=(150, 150, 150, 255), width=3)
    d.rectangle((bx - 50 * k, by - 90 * k, bx + 50 * k, by - 20 * k), fill=(200, 40, 40, 255))
    d.text((bx - 40 * k, by - 80 * k), "УКСУС", font=F("Black", int(26 * k)), fill=(255, 255, 255, 255))
    for j in range(20):
        ph = (t * 2 + j * 0.05) % 1.0
        d.ellipse((bx - 60 * k - j * 2 * k, by + 40 * k + ph * 420 * k, bx - 50 * k - j * 2 * k, by + 52 * k + ph * 420 * k), fill=(230, 220, 160, 220))


LEG_STING = {"arm_a_r": 0.9, "arm_b_r": 1.0, "arm_a_l": 0.9, "arm_b_l": 1.0, "leg_a_r": 0.25}
LYING = {"rot": -math.pi / 2, "cy": 0.5, "dy": 0.12, "arm_a_r": 0.05, "arm_a_l": 0.05}

SPEC = dict(
    slug="meduza",
    title="Ужалила медуза-коробочка",
    header="СИМУЛЯЦИЯ · МЕДУЗА-КОРОБОЧКА",
    caption="Её почти не видно в воде… а сердце может остановиться за 5 минут 😨 Ты бы полез в это море? 👇",
    hashtags="#медуза #австралия #чтобудетесли #симуляция #организм",
    hr=[(0, 150), (2.6, 82), (5.4, 150), (8.2, 165), (16.6, 168), (19.6, 140), (22.4, 60), (23.6, 30), (24.0, 0), (26.8, 0), (27.2, 70),
        (28.2, 120), (31.0, 115), (34.0, 100), (48, 90)],
    ecg_noise=(16.6, 22.4),
    shots=[
        dict(kind="face", dur=2.6, title="УЖАЛИЛА МЕДУЗА-КОРОБОЧКА", tag="что будет с телом?", expr="yell", zoom=4.6, preset="sea", surface=1150,
             outfit="swim", water_tint=0.6, red=0.5, shake=0.3, sweat=0.0),
        dict(kind="scene", dur=2.8, preset="sea", surface=880, title="АВСТРАЛИЯ. ТЁПЛОЕ МОРЕ", tag="медуза прозрачная — в воде её почти не видно",
             timer="0 с", cam=(0.0, 0.45, 1.0), outfit="swim", expr="happy", pose={"arm_a_r": 0.5, "arm_a_l": 0.5}, sea_front=True, draw=draw_swim),
        dict(kind="scene", dur=2.8, preset="sea", surface=880, title="ЩУПАЛЬЦА НА НОГЕ", tag="по 10–12 щупалец в каждом углу, длиной 2 метра и больше",
             timer="+1 с", cam=(0.05, 0.55, 1.25), outfit="swim", expr="yell", pose=LEG_STING, sea_front=True, draw=draw_contact,
             hits=[(0.3, 1.4, True)], pops=[(0.3, "ЖЖЁТ!", 760, 760)], shake=0.4, red=0.6, name="contact"),
        dict(kind="custom", fn=shot_nemato, dur=2.8, title="ГАРПУНЫ С ЯДОМ", tag="тысячи клеток выстреливают в кожу за секунду", timer="+2 с", red=0.4),
        dict(kind="face", dur=2.8, title="БОЛЬ МГНОВЕННАЯ", tag="сразу — очень сильная жгучая боль", timer="+10 с", expr="yell", zoom=4.4, preset="sea", surface=1180,
             outfit="swim", shake_head=True, shake=0.6, red=0.8, say="«А-А-А-А!»", say_size=72),
        dict(kind="custom", fn=shot_welts, dur=2.8, title="СЛЕДЫ КАК ОТ ПЛЕТИ", tag="белые полосы за минуты становятся красными", timer="+1 мин", red=0.5),
        dict(kind="xray", dur=3.0, title="ЯД БЬЁТ ПО СЕРДЦУ", tag="у коробочки сердечный токсин", timer="+2 мин", cam=(0.0, 0.40, 1.35), expr="gasp",
             flow=[dict(path=[(0.05, 0.85), (0.05, 0.6), (0.03, 0.45), (0.02, 0.29)], col=(150, 255, 120), n=30, speed=0.7)],
             glow=[dict(at=(0.02, 0.29), r=0.05, col=(255, 40, 40))],
             labels=[("сердце", "сбивается ритм", RED, (0.02, 0.29), 1, 700), ("давление", "скачет", AMBER, None, 1, 820),
                     ("нога", "яд заходит", AMBER, (0.05, 0.8), -1, 1180)], red=0.8, riser=True),
        dict(kind="scene", dur=2.8, preset="beach", ground=760, title="ПАДАЕТ НА БЕРЕГУ", tag="без сознания. сердце может остановиться за 5 минут",
             timer="+3 мин", cam=(0.0, 0.6, 1.0), outfit="swim", expr="sleep", pose=LYING, red=0.6, hits=[(0.4, 1.0, False)]),
        dict(kind="flat", dur=2.8, title="СЕРДЦЕ ОСТАНОВИЛОСЬ", tag="через несколько минут после ожога", timer="+4 мин", red=0.5),
        dict(kind="scene", dur=3.0, preset="beach", ground=760, title="СЛР БЕЗ ОСТАНОВКИ", tag="качают долго — и сердце снова запускается", timer="+5 мин",
             cam=(0.0, 0.62, 1.15), outfit="swim", expr="sleep", pose=LYING, draw=draw_cpr, red=0.4, name="cpr"),
        dict(kind="scene", dur=2.8, preset="beach", ground=760, title="УКСУС НА ОЖОГ", tag="так оставшиеся клетки не выстрелят ядом", timer="+6 мин",
             cam=(0.25, 0.62, 1.15), outfit="swim", expr="pain", pose=LYING, draw=draw_vinegar, red=0.2),
        dict(kind="scene", dur=3.0, preset="hospital", title="ПРОТИВОЯДИЕ", tag="в больнице вводят сыворотку против яда коробочки", timer="+1 ч",
             cam=(0.0, 0.62, 1.05), outfit="hosp", expr="pain", pose=LYING, props_back=[("bed", {})], props=[("monitor", {"at": (0.45, 0.3)}), ("iv", {"x": -0.5})],
             lighting=(540, 900, 800, 1.0, 0.3, (200, 220, 255))),
        dict(kind="bignum", dur=2.6, value="5 МИНУТ", sub=[("за это время может", WHITE), ("остановиться сердце", (255, 120, 120))], red=0.7),
        dict(kind="myth", dur=3.4, word="ПРОМЫТЬ\nПРЕСНОЙ ВОДОЙ?", truth="пресной водой нельзя", text="по австралийским правилам первой помощи: уксус, а если его нет — морская вода"),
        dict(kind="facts", dur=5.4),
        dict(kind="loop", dur=2.4),
    ],
    facts=[("2+ метра", "длина щупалец, их по 10–12 в каждом углу"),
           ("~5 минут", "за это время могут наступить остановка сердца и смерть"),
           ("боль сразу", "белые полосы на коже краснеют, как от плети"),
           ("уксус и СЛР", "первая помощь: из воды, скорая, уксус на ожог"),
           ("сезон", "в северной Австралии — с октября по май")],
    sfx=[(0.05, "scream", {"dur": 1.6, "f0": 320, "peak": 650, "end": 420, "vowel": "a", "g": 0.4}), (0.0, "splash", {"g": 0.4}),
         (("contact", 0.3), "zap", {"g": 0.35}), (("contact", 0.32), "scream", {"dur": 1.5, "f0": 340, "peak": 700, "end": 450, "vowel": "a", "g": 0.48}),
         (("contact", 0.4), "splash", {"g": 0.5}), (("contact", 1.8), "scream", {"dur": 1.0, "f0": 300, "peak": 620, "end": 420, "vowel": "o", "g": 0.4}),
         (8.4, "zap", {"dur": 1.6, "g": 0.18}),
         (11.2, "scream", {"dur": 2.0, "f0": 330, "peak": 720, "end": 400, "vowel": "a", "rough": 0.9, "g": 0.5}),
         (14.0, "groan", {"dur": 1.4, "f0": 170, "g": 0.2}), (16.8, "gasp", {"g": 0.25}), (17.8, "gasp", {"g": 0.2}),
         (19.9, "thud", {"g": 0.6}), (20.4, "sob", {"n": 2, "g": 0.08}),
         (("cpr", 0.0), "beeps", {"n": 6, "every": 0.5, "f": 700, "g": 0.0}),
         (27.3, "gasp", {"dur": 0.8, "g": 0.35}), (27.9, "cough", {"n": 3, "g": 0.25}),
         (31.0, "groan", {"dur": 1.0, "f0": 150, "g": 0.15})],
)

for _k in range(5):
    SPEC["sfx"].append((("cpr", 0.1 + _k * 0.545), "thud", {"g": 0.18}))
