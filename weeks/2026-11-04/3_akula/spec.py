# Укусила акула — 6 ноября 2026
# Источники: Swellnet / Australian National University (Taylor et al., Emergency Medicine Australasia, 2021):
#   у выживших после первого укуса ниже туловища главная причина смерти — кровопотеря; при разрыве крупной артерии —
#   несколько минут до потери большей части крови; кулак прямой рукой всем весом в середину между бедром и пахом;
#   кровоток снижался в среднем на 89,7 % (жгут в опыте — 43,8 %), у 75 % участников останавливался полностью.
#   Объём крови взрослого ~5 л — общеизвестная физиология.
import math

PALE = (214, 196, 186)
BLUISH = (196, 186, 198)


def shark_shape(d, x, y, sc, ang=0.0, col=(90, 110, 130, 255)):
    pts = [(-1.0, 0.0), (-0.6, -0.22), (0.1, -0.28), (0.5, -0.2), (0.9, -0.05), (1.15, -0.35), (1.1, 0.0), (1.15, 0.35), (0.9, 0.08),
           (0.5, 0.22), (0.0, 0.26), (-0.6, 0.2)]
    ca, sa = math.cos(ang), math.sin(ang)
    P = [(x + (px * ca - py * sa) * sc, y + (px * sa + py * ca) * sc) for px, py in pts]
    d.polygon(P, fill=col)
    fin = [(0.0, -0.26), (0.25, -0.62), (0.35, -0.24)]
    d.polygon([(x + (px * ca - py * sa) * sc, y + (px * sa + py * ca) * sc) for px, py in fin], fill=col)
    ex, ey = -0.72, -0.06
    d.ellipse((x + (ex * ca - ey * sa) * sc - 0.03 * sc, y + (ex * sa + ey * ca) * sc - 0.03 * sc, x + (ex * ca - ey * sa) * sc + 0.03 * sc,
               y + (ex * sa + ey * ca) * sc + 0.03 * sc), fill=(10, 10, 10, 255))


def draw_fin(img, d, t, u, T0, s, T):
    x = lerp(1000, 640, ease(u)) * SS
    y = 880 * SS
    d.polygon([(x - 50 * SS, y), (x + 10 * SS, y - 120 * SS), (x + 40 * SS, y)], fill=(70, 80, 96, 255))
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    shark_shape(ImageDraw.Draw(lay), x, y + 120 * SS, 260 * SS, 0.0, (60, 80, 100, 110))
    img.alpha_composite(lay)


def shot_bite(t, u, sh):
    img = E.grad((20, 90, 140), (4, 20, 40))
    d = ImageDraw.Draw(img)
    for k in range(30):
        x = (k * 97 + t * 40) % 1080
        y = 560 + (k * 53) % 900
        d.ellipse((x - 3, y - 3, x + 3, y + 3), fill=(180, 220, 255, 120))
    # legs from above
    d.rounded_rectangle((330, 420, 450, 1200), radius=60, fill=(232, 186, 156, 255))
    d.rounded_rectangle((520, 420, 640, 1200), radius=60, fill=(232, 186, 156, 255))
    d.rectangle((310, 420, 660, 560), fill=(30, 90, 170, 255))
    k = smooth(u / 0.35)
    sx = lerp(1300, 760, k)
    sy = lerp(1500, 900, k)
    shark_shape(d, sx, sy, 380, -0.55)
    if u > 0.3:
        al = smooth((u - 0.3) / 0.4)
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ld = ImageDraw.Draw(lay)
        for j in range(14):
            r = 60 + 30 * j * al
            ld.ellipse((600 - r, 760 - r * 0.7 + j * 8, 600 + r, 760 + r * 0.7 + j * 8), fill=(170, 10, 20, int(60 * al)))
        img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(14)))
    return img


def draw_blood_sea(img, d, t, u, T0, s, T):
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ld = ImageDraw.Draw(lay)
    cx, cy = T0(0.05, 0.62)
    for j in range(12):
        r = (0.06 + 0.03 * j * (0.4 + u)) * s
        ld.ellipse((cx - r, cy - r * 0.45, cx + r, cy + r * 0.45), fill=(160, 10, 20, 50))
    img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(10 * SS)))


def draw_press(img, d, t, u, T0, s, T):
    k = s / 900
    gx, gy = T(0.05, 0.52)
    push = 0.5 + 0.5 * math.sin(t * 3)
    top = gy - (250 + 10 * push) * k
    d.ellipse((gx - 40 * k, top - 120 * k, gx + 40 * k, top - 40 * k), fill=(70, 60, 56, 255))
    d.rounded_rectangle((gx - 60 * k, top - 45 * k, gx + 60 * k, top + 120 * k), radius=int(20 * k), fill=(240, 200, 40, 255))
    d.line((gx, top + 40 * k, gx, gy - 20 * k), fill=(200, 160, 130, 255), width=int(26 * k))
    d.ellipse((gx - 30 * k, gy - 40 * k, gx + 30 * k, gy + 10 * k), fill=(200, 160, 130, 255))
    # wound + blood on sand
    wx, wy = T(0.06, 0.62)
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ld = ImageDraw.Draw(lay)
    ld.ellipse((wx - 0.07 * s, wy - 0.03 * s, wx + 0.12 * s, wy + 0.06 * s), fill=(150, 10, 20, 200))
    img.alpha_composite(lay)


def draw_wound(img, d, t, u, T0, s, T):
    wx, wy = T(0.06, 0.62)
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ld = ImageDraw.Draw(lay)
    ld.ellipse((wx - 0.07 * s, wy - 0.03 * s, wx + 0.12 * s, wy + 0.06 * s), fill=(150, 10, 20, 210))
    img.alpha_composite(lay)
    d2 = ImageDraw.Draw(img)
    bx, by = T0(-0.5, 0.05)
    d2.rounded_rectangle((bx - 0.04 * s, by, bx + 0.04 * s, by + 0.12 * s), radius=int(0.01 * s), fill=(170, 20, 30, 230), outline=(240, 240, 250, 255), width=3)
    d2.line([(bx, by + 0.12 * s), T(-0.06, 0.25)], fill=(170, 20, 30, 255), width=max(2, int(0.004 * s)))


LYING = {"rot": -math.pi / 2, "cy": 0.5, "dy": 0.12, "arm_a_r": 0.05, "arm_a_l": 0.05}

SPEC = dict(
    slug="akula",
    title="Укусила акула",
    header="СИМУЛЯЦИЯ · УКУС АКУЛЫ",
    caption="Убивают не зубы… а то, что происходит в следующие минуты 😨 Знал, куда давить? 👇",
    hashtags="#акула #море #чтобудетесли #симуляция #организм",
    hr=[(0, 160), (2.6, 88), (5.4, 165), (10.8, 150), (14.0, 140), (16.8, 150), (20.0, 158), (23.0, 150), (28.6, 128), (31.4, 110), (34.4, 100), (50, 90)],
    stat=dict(name="кровь", pts=[(8.0, 100), (10.8, 92), (16.8, 80), (19.8, 70), (22.8, 64), (28.6, 60), (31.4, 62), (34.4, 85)], from=8.0, to=37.4,
              fmt="{name} ≈{v:.0f}%", good=(90, 100), warn=(75, 100)),
    shots=[
        dict(kind="face", dur=2.6, title="УКУСИЛА АКУЛА", tag="что будет с телом?", expr="yell", zoom=4.6, preset="sea", surface=1150, outfit="swim",
             water_tint=0.5, red=0.7, shake=0.5),
        dict(kind="scene", dur=2.8, preset="sea", surface=880, title="ПЛАВНИК", tag="он отдыхает на волнах и ничего не видит", timer="0 с",
             cam=(0.0, 0.40, 1.0), outfit="swim", expr="happy", pose={"arm_a_r": 0.6, "arm_a_l": 0.6}, sea_front=True, draw=draw_fin, riser=True),
        dict(kind="custom", fn=shot_bite, dur=2.6, title="УКУС", tag="акула хватает за бедро", timer="+1 с", hits=[(0.9, 1.6, True)], red=0.6,
             pops=[(0.9, "ХРЯСЬ!", 700, 700)], amb="underwater", name="bite"),
        dict(kind="xray", dur=3.0, title="РАЗОРВАНА АРТЕРИЯ", tag="кровь бьёт струёй с каждым ударом сердца", timer="+5 с", cam=(0.0, 0.58, 1.6),
             expr="yell", pose={"arm_a_r": 0.3, "arm_a_l": 0.3},
             glow=[dict(at=(0.06, 0.6), r=0.05, col=(255, 30, 40))],
             flow=[dict(path=[(0.03, 0.40), (0.05, 0.50), (0.06, 0.60), (0.16, 0.66), (0.26, 0.74)], col=(230, 20, 30), n=40, speed=1.2, size=0.008)],
             labels=[("бедренная артерия", "разорвана", RED, (0.06, 0.6), 1, 700), ("кровь", "уходит струёй", RED, None, 1, 820), ("сердце", "качает быстрее", AMBER, (0.02, 0.29), -1, 700)],
             red=0.8),
        dict(kind="bignum", dur=2.8, value="~5 ЛИТРОВ", sub=[("вся кровь в теле взрослого", WHITE), ("из большой артерии её можно потерять за минуты", (255, 120, 120))], red=0.8),
        dict(kind="scene", dur=2.8, preset="sea", surface=880, title="ВОДА КРАСНЕЕТ", tag="он плывёт к берегу и теряет кровь", timer="+30 с",
             cam=(0.0, 0.42, 1.05), outfit="swim", expr="yell", pose={"arm_a_r": 2.2, "arm_b_r": 0.6, "arm_a_l": 1.2}, sea_front=True, draw=draw_blood_sea,
             shake=0.3, red=0.6),
        dict(kind="face", dur=2.8, title="ОН БЛЕДНЕЕТ", tag="давление падает, сердце колотится, кожа холодеет", timer="+1 мин", expr="gasp", skin=PALE, sweat=1.0,
             zoom=4.5, preset="beach", ground=1300, red=0.6, lighting=(540, 820, 900, 1.0, 0.45, (220, 230, 255))),
        dict(kind="micro", dur=3.0, cells="blood", title="КРОВИ ВСЁ МЕНЬШЕ", tag="органы задыхаются без кислорода", timer="+2 мин",
             kill=[(0, 0.2), (1, 0.8)], attackers=0, caption="меньше крови — меньше кислорода мозгу и сердцу", red=0.7),
        dict(kind="scene", dur=3.0, preset="beach", ground=760, title="КУЛАК В ПАХ!", tag="давят прямой рукой всем весом — между бедром и пахом",
             timer="+2 мин", cam=(0.15, 0.6, 1.2), outfit="swim", expr="pain", pose=LYING, draw=draw_press, name="press", red=0.3),
        dict(kind="bignum", dur=2.8, value="≈ 90%", sub=[("на столько в среднем падал кровоток в ноге", WHITE), ("в эксперименте австралийских врачей", (180, 220, 255))], red=0.3),
        dict(kind="face", dur=2.8, title="ТЕРЯЕТ СОЗНАНИЕ", tag="мозгу не хватает крови", timer="+5 мин", expr="sleep", skin=BLUISH, sweat=0.5, zoom=4.7,
             preset="beach", ground=1300, muffle=0.8, red=0.5, lighting=(540, 820, 800, 0.8, 0.25, (200, 210, 255)), dark=[(0, 0.0), (1, 0.35)]),
        dict(kind="scene", dur=3.0, preset="hospital", title="ПЕРЕЛИВАНИЕ КРОВИ", tag="кровь, операция на сосуде — и он выживает", timer="+40 мин",
             cam=(0.0, 0.62, 1.05), outfit="swim", expr="sleep", pose=LYING, props_back=[("bed", {})], props=[("monitor", {"at": (0.45, 0.3)})],
             draw=draw_wound, lighting=(540, 900, 800, 1.0, 0.3, (200, 220, 255))),
        dict(kind="myth", dur=3.4, word="УБИВАЮТ ЗУБЫ?", truth="чаще убивает кровопотеря", text="у выживших после укуса в ногу главная причина смерти — потеря крови"),
        dict(kind="facts", dur=5.4),
        dict(kind="loop", dur=2.4),
    ],
    facts=[("кровопотеря", "главная причина смерти после укуса в ногу"),
           ("минуты", "при разрыве крупной артерии кровь уходит очень быстро"),
           ("кулак в пах", "прямой рукой, всем весом — между бедром и пахом"),
           ("≈ 90%", "так в среднем снижался кровоток в опыте (жгут — ≈ 44%)"),
           ("сразу 112", "звать спасателей и скорую, не терять ни минуты")],
    sfx=[(0.0, "scream", {"dur": 1.6, "f0": 320, "peak": 680, "end": 420, "vowel": "a", "g": 0.42}), (0.0, "splash", {"g": 0.4}),
         (("bite", 0.9), "crunch", {"dur": 0.35, "g": 0.9}), (("bite", 0.95), "scream", {"dur": 1.6, "f0": 340, "peak": 720, "end": 430, "vowel": "a", "rough": 0.9, "g": 0.5}),
         (("bite", 0.9), "bubble", {"n": 14, "g": 0.12}),
         (10.9, "groan", {"dur": 1.2, "f0": 190, "g": 0.25}), (12.2, "scream", {"dur": 1.0, "f0": 300, "peak": 560, "end": 380, "vowel": "o", "g": 0.35}),
         (16.8, "splash", {"g": 0.3}), (17.6, "splash", {"g": 0.3}), (18.0, "scream", {"dur": 1.2, "f0": 300, "peak": 600, "end": 400, "vowel": "a", "g": 0.35}),
         (19.8, "gasp", {"g": 0.25}), (20.8, "gasp", {"g": 0.22}), (21.6, "breath", {"dur": 1.2, "rate": 3.0, "g": 0.12}),
         (("press", 0.2), "scream", {"dur": 1.3, "f0": 280, "peak": 520, "end": 360, "vowel": "o", "g": 0.35}), (("press", 0.0), "siren", {"dur": 3.0, "g": 0.06}),
         (31.4, "tinnitus", {"dur": 2.8, "g": 0.02})],
)
