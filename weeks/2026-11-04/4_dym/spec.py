# Надышался дымом при пожаре — 7 ноября 2026
# Источники: Fireco «Why smoke is more deadly than fire» — большинство смертей при пожарах в помещениях от дыма, а не ожогов;
#            CO — самый частый токсичный газ, HCN — от горящего пластика; кислород 21 % норма, 17 % — нарушается мышление,
#            9 % — потеря сознания, 6 % — смерть; горячий воздух обжигает дыхательные пути.
#            NFPA (Fire Prevention Week) — после сигнала датчика на выход может остаться всего ~2 минуты.
import math

SOOT = (200, 180, 170)
BLUISH = (190, 182, 196)
LYING = {"rot": -math.pi / 2, "cy": 0.5, "dy": 0.12, "arm_a_r": 0.05, "arm_a_l": 0.05}
CRAWL = {"rot": math.pi / 2, "cy": 0.5, "dy": 0.30, "arm_a_r": 2.7, "arm_b_r": 0.5, "arm_a_l": 2.9, "arm_b_l": 0.2}


def draw_spark(img, d, t, u, T0, s, T):
    k = s / 900
    x, y = 860 * SS, 1180 * SS
    d.rectangle((x - 30 * k, y - 20 * k, x + 30 * k, y + 20 * k), fill=(240, 240, 240, 255))
    d.line((x, y + 20 * k, x - 200 * k, y + 60 * k), fill=(30, 30, 30, 255), width=int(6 * k))
    if (int(t * 12) % 3) != 0:
        for j in range(6):
            a = j * 1.05 + t * 7
            d.line((x, y, x + 50 * k * math.cos(a), y + 50 * k * math.sin(a)), fill=(255, 230, 120, 255), width=int(4 * k))
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(lay).ellipse((x - 160 * k, y - 160 * k, x + 160 * k, y + 160 * k), fill=(255, 150, 40, int(60 + 60 * u)))
    img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(30 * SS)))


def draw_mask(img, d, t, u, T0, s, T):
    a, b = T(-0.02, 0.095), T(0.02, 0.125)
    d.ellipse(A.box(a, b), fill=(200, 230, 240, 200), outline=(240, 250, 255, 255), width=max(2, int(0.003 * s)))
    d.line([T(0.0, 0.125), T0(-0.55, 0.3)], fill=(220, 235, 245, 255), width=max(2, int(0.006 * s)))
    k = s / 900
    x, y = T0(-0.55, 0.3)
    d.rounded_rectangle((x - 40 * k, y - 140 * k, x + 40 * k, y + 40 * k), radius=int(20 * k), fill=(60, 160, 90, 255))


def draw_firefighter(img, d, t, u, T0, s, T):
    k = s / 900
    x, y = T0(0.35, 0.40)
    d.ellipse((x - 50 * k, y - 300 * k, x + 50 * k, y - 200 * k), fill=(230, 190, 40, 255))
    d.rounded_rectangle((x - 80 * k, y - 210 * k, x + 80 * k, y + 60 * k), radius=int(30 * k), fill=(40, 40, 46, 255))
    for yy in (y - 120 * k, y - 20 * k):
        d.rectangle((x - 80 * k, yy, x + 80 * k, yy + 16 * k), fill=(230, 230, 120, 255))
    d.rectangle((x - 70 * k, y + 60 * k, x - 20 * k, y + 330 * k), fill=(40, 40, 46, 255))
    d.rectangle((x + 20 * k, y + 60 * k, x + 70 * k, y + 330 * k), fill=(40, 40, 46, 255))
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(lay).polygon([(x - 40 * k, y - 260 * k), (x - 700 * k, y + 200 * k), (x - 400 * k, y + 400 * k)], fill=(255, 250, 220, 70))
    img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(10 * SS)))


SPEC = dict(
    slug="dym",
    title="Надышался дымом при пожаре",
    header="СИМУЛЯЦИЯ · ДЫМ ПРИ ПОЖАРЕ",
    caption="Огонь ещё даже не дошёл до него… а он уже не может встать 😨 У тебя дома есть датчик дыма? 👇",
    hashtags="#пожар #дым #чтобудетесли #симуляция #организм",
    hr=[(0, 150), (2.6, 64), (8.2, 66), (11.2, 72), (14.2, 80), (14.6, 150), (17.4, 160), (23.0, 168), (26.0, 150), (28.8, 120), (31.6, 90),
        (34.6, 110), (40, 100), (50, 90)],
    stat=dict(name="кислород в воздухе", pts=[(5.4, 21), (8.2, 20), (11.2, 19), (14.2, 18), (17.4, 17), (20.2, 15), (23.2, 13), (26.0, 11), (28.8, 9), (31.6, 21)],
              from_=0, fmt="{name} {v:.0f}%", good=(20, 22), warn=(17, 22)),
    shots=[
        dict(kind="face", dur=2.6, title="НАДЫШАЛСЯ ДЫМОМ", tag="что будет с телом?", expr="gasp", skin=SOOT, sweat=0.8, tears=1.0, zoom=4.6, preset="bedroom",
             smoke=0.3, red=0.6, shake_head=True, lighting=(700, 900, 1000, 1.0, 0.45, (255, 170, 90)), flicker=True),
        dict(kind="scene", dur=2.8, preset="bedroom", ground=1260, title="НОЧЬ. ОН СПИТ", tag="у дивана загорается зарядка", timer="0:00",
             cam=(0.0, 0.62, 1.05), outfit="casual", expr="sleep", pose=LYING, props_back=[("bed", {"col": (120, 110, 150)})], draw=draw_spark,
             lighting=(860, 1180, 700, 1.0, 0.35, (255, 190, 120)), flicker=True, name="spark"),
        dict(kind="scene", dur=3.0, preset="bedroom", ground=1260, title="ДЫМ ПОД ПОТОЛКОМ", tag="он опускается всё ниже, а он спит", timer="+1 мин",
             cam=(0.0, 0.62, 1.05), outfit="casual", expr="sleep", pose=LYING, props_back=[("bed", {"col": (120, 110, 150)})],
             props=[("fire", {"x": (720, 1080), "k": [(0, 0.3), (1, 0.7)]})], smoke=[(0, 0.15), (1, 0.4)], amb="fire",
             lighting=(900, 1150, 900, 1.0, 0.35, (255, 170, 90)), flicker=True, red=0.3),
        dict(kind="xray", dur=3.0, title="УГАРНЫЙ ГАЗ", tag="без цвета и запаха — во сне его не почувствуешь", timer="+2 мин", cam=(0.0, 0.22, 2.0), expr="sleep",
             flow=[dict(path=[(0.0, 0.11), (0.0, 0.16), (-0.03, 0.24), (-0.05, 0.28)], col=(150, 150, 160), n=30, speed=0.4, size=0.007),
                   dict(path=[(0.0, 0.11), (0.0, 0.16), (0.03, 0.24), (0.05, 0.28)], col=(150, 150, 160), n=30, speed=0.4, size=0.007)],
             glow=[dict(at=(0.0, 0.04), r=0.05, col=(150, 150, 200), pulse=False, k=[(0, 0.3), (1, 0.9)])],
             labels=[("лёгкие", "вдыхают дым", AMBER, (-0.05, 0.27), -1, 1180), ("мозг", "засыпает крепче", RED, (0.0, 0.04), 1, 700)], red=0.4),
        dict(kind="micro", dur=3.0, cells="blood", title="ГАЗ ВМЕСТО КИСЛОРОДА", tag="угарный газ цепляется к крови сильнее кислорода", timer="+3 мин",
             kill=[(0, 0.0), (1, 0.4)], attack_col=(160, 160, 170), attackers=60, caption="серые — угарный газ на красных клетках крови", red=0.5, name="co"),
        dict(kind="face", dur=2.8, title="ПРОСЫПАЕТСЯ В ДЫМУ", tag="глаза режет, горло горит, ничего не видно", timer="+3 мин", expr="terror", skin=SOOT, sweat=0.8,
             tears=1.0, zoom=4.5, preset="bedroom", smoke=0.3, red=0.6, lighting=(760, 900, 1000, 1.0, 0.45, (255, 170, 90)), flicker=True, say="«кха… кха…»", name="wake"),
        dict(kind="bignum", dur=2.6, value="17%", sub=[("кислорода в воздухе — и мысли уже путаются", WHITE), ("в обычном воздухе его 21%", (180, 220, 255))], red=0.6),
        dict(kind="scene", dur=3.0, preset="bedroom", ground=1260, title="ПОЛЗЁТ К ДВЕРИ", tag="у пола дыма меньше — но он почти ослеп", timer="+4 мин",
             cam=(0.15, 0.62, 1.0), outfit="casual", expr="gasp", pose=CRAWL, props=[("fire", {"x": (40, 300), "k": 0.9})], smoke=0.45, amb="fire",
             lighting=(540, 1050, 1000, 1.0, 0.4, (255, 160, 80)), flicker=True, red=0.6, riser=True),
        dict(kind="xray", dur=2.8, title="ДЫМ ЖЖЁТ ДЫХАТЕЛЬНЫЕ ПУТИ", tag="горячий воздух обжигает горло и бронхи", timer="+4 мин", cam=(0.0, 0.22, 2.0), expr="gasp",
             glow=[dict(at=(0.0, 0.15), r=0.035, col=(255, 90, 30)), dict(at=(-0.04, 0.25), r=0.05, col=(255, 60, 30)), dict(at=(0.04, 0.25), r=0.05, col=(255, 60, 30))],
             labels=[("горло", "отекает", RED, (0.0, 0.15), -1, 700), ("бронхи", "обожжены", RED, (0.04, 0.25), 1, 700), ("кашель", "без остановки", AMBER, None, 1, 820)],
             red=0.8, ecg=True),
        dict(kind="bignum", dur=2.6, value="9%", sub=[("кислорода — человек теряет сознание", WHITE), ("при 6% — смерть", (255, 120, 120))], red=0.8),
        dict(kind="face", dur=2.8, title="ОТКЛЮЧАЕТСЯ У ДВЕРИ", tag="в метре от выхода", timer="+5 мин", expr="sleep", skin=BLUISH, zoom=4.7, preset="bedroom",
             smoke=0.45, red=0.5, muffle=0.8, lighting=(700, 900, 700, 0.8, 0.2, (255, 160, 90)), flicker=True, dark=[(0, 0.1), (1, 0.5)], name="faint"),
        dict(kind="scene", dur=3.0, preset="bedroom", ground=1260, title="ПОЖАРНЫЕ НАХОДЯТ ЕГО", tag="его выносят — и сразу кислород", timer="+8 мин",
             cam=(0.1, 0.62, 1.0), outfit="casual", expr="sleep", pose=LYING, smoke=0.6, draw=draw_firefighter, lighting=(600, 900, 1000, 1.0, 0.3, (255, 240, 210)),
             name="fireman"),
        dict(kind="scene", dur=2.8, preset="hospital", title="КИСЛОРОДНАЯ МАСКА", tag="кровь очищают от угарного газа, лёгкие лечат неделями", timer="+30 мин",
             cam=(0.0, 0.62, 1.05), outfit="hosp", expr="sleep", pose=LYING, skin=SOOT, props_back=[("bed", {})], props=[("monitor", {"at": (0.45, 0.3)})],
             draw=draw_mask, lighting=(540, 900, 800, 1.0, 0.3, (200, 220, 255))),
        dict(kind="bignum", dur=2.6, value="2 МИНУТЫ", size=130, sub=[("иногда столько остаётся на выход", WHITE), ("после сигнала датчика дыма", (255, 120, 120))], red=0.5),
        dict(kind="myth", dur=3.4, word="ГЛАВНОЕ — ОГОНЬ?", truth="чаще убивает дым", text="большинство погибших при пожарах в домах отравились дымом, а не сгорели"),
        dict(kind="facts", dur=5.4),
        dict(kind="loop", dur=2.4),
    ],
    facts=[("дым, а не огонь", "главная причина смерти при пожарах в помещениях"),
           ("угарный газ", "без цвета и запаха — во сне его не почувствуешь"),
           ("17% → 9%", "кислорода в воздухе: сначала путаются мысли, потом обморок"),
           ("~2 минуты", "может остаться на выход после сигнала датчика"),
           ("датчик дыма", "стоит копейки и даёт эти минуты")],
    sfx=[(0.0, "cough", {"n": 4, "g": 0.35}), (0.3, "gasp", {"g": 0.25}),
         (("spark", 0.4), "zap", {"dur": 0.4, "g": 0.25}), (("spark", 1.6), "zap", {"dur": 0.5, "g": 0.25}),
         (14.6, "cough", {"n": 5, "g": 0.4}), (15.2, "scream", {"dur": 0.9, "f0": 280, "peak": 520, "end": 360, "vowel": "o", "g": 0.3}),
         (16.6, "gasp", {"g": 0.3}), (20.2, "cough", {"n": 3, "g": 0.3}), (21.2, "groan", {"dur": 1.0, "f0": 170, "g": 0.2}),
         (22.4, "breath", {"dur": 2.0, "rate": 3.0, "g": 0.12}), (23.4, "cough", {"n": 4, "g": 0.3}), (24.3, "gasp", {"g": 0.25}),
         (28.8, "thud", {"g": 0.5}), (29.3, "tinnitus", {"dur": 2.5, "g": 0.02}),
         (("fireman", 0.0), "slam", {"g": 0.6}), (("fireman", 0.4), "siren", {"dur": 2.6, "g": 0.06}),
         (34.8, "gasp", {"dur": 0.8, "g": 0.3}), (35.4, "cough", {"n": 3, "g": 0.25})],
)
SPEC["stat"]["from"] = 2.6
