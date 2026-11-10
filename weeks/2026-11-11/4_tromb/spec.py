# Тромб после долгого перелёта (тромбоэмболия лёгочной артерии) — 14 ноября 2026 (Стиль-2)
# Источники:
#  - ВОЗ, проект WRIGHT (WHO Research Into Global Hazards of Travel), 2007: после поездок дольше 4 часов риск венозного
#    тромбоза примерно удваивается; абсолютный риск ≈ 1 на 6000 для перелётов > 4 ч; риск выше при ожирении,
#    росте выше 1,9 м или ниже 1,6 м, приёме оральных контрацептивов; совет — двигать икрами, ходить.
#  - CDC Yellow Book «Deep Vein Thrombosis & Pulmonary Embolism» (travel): признаки ТГВ — отёк, боль, покраснение ноги;
#    признаки ТЭЛА — внезапная одышка, боль в груди, учащённое сердцебиение; тромб может проявиться спустя дни после поездки.
#  - NHS «Pulmonary embolism»: требуется срочная помощь, лечат антикоагулянтами, при тяжёлой ТЭЛА — растворяют тромб.
import math

STAND = {"arm_a_r": 0.14, "arm_a_l": 0.14}
LEG_PAIN = {"arm_a_r": 0.9, "arm_b_r": 1.0, "arm_a_l": 0.14, "leg_a_r": 0.25, "head": 0.06}
CHEST = {"arm_a_r": 0.6, "arm_b_r": 2.7, "arm_s_r": 0.8, "arm_a_l": 0.6, "arm_b_l": 2.7, "arm_s_l": 0.8}
LYING = {"rot": -math.pi / 2, "cy": 0.5, "dy": 0.12, "arm_a_r": 0.05, "arm_a_l": 0.05}
CALF = (-0.05, 0.80)
VEIN = [(-0.05, 0.90), (-0.05, 0.80), (-0.055, 0.70), (-0.05, 0.58), (-0.03, 0.47), (-0.01, 0.38), (0.0, 0.30), (0.0, 0.25)]


def hook_draw(img, d, t, u, *_):
    # aircraft seat seen from the side, with a leg and a glowing clot in the calf
    d.rounded_rectangle((300, 760, 470, 1230), radius=40, fill=(62, 66, 84, 255))
    d.rounded_rectangle((300, 1120, 720, 1230), radius=30, fill=(62, 66, 84, 255))
    d.rounded_rectangle((320, 700, 470, 790), radius=24, fill=(220, 220, 228, 255))
    d.line([(560, 1150), (760, 1160), (780, 1400)], fill=(70, 96, 160, 255), width=90, joint="curve")
    d.ellipse((740, 1380, 860, 1440), fill=(30, 30, 34, 255))
    k = 0.6 + 0.4 * math.sin(t * 6)
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(g).ellipse((720, 1220, 840, 1340), fill=(255, 40, 40, int(170 * k)))
    img.alpha_composite(g.filter(ImageFilter.GaussianBlur(26)))
    d = ImageDraw.Draw(img)
    d.ellipse((765, 1262, 795, 1300), fill=(90, 10, 20, 255))
    # window with clouds
    d.rounded_rectangle((640, 640, 820, 900), radius=80, fill=(80, 86, 100, 255))
    d.rounded_rectangle((660, 660, 800, 880), radius=66, fill=(40, 60, 100, 255))
    for j in range(3):
        x = 660 + ((t * 60 + j * 60) % 160)
        d.ellipse((x - 30, 740 + j * 40, x + 30, 770 + j * 40), fill=(200, 210, 230, 200))


def xr_legflow(img, d, t, u, T0, s, T):
    pass


def xr_clot(img, d, t, u, T0, s, T):
    k = smooth(u / 0.7)
    c = T(*CALF)
    r = (0.006 + 0.01 * k) * s
    d.ellipse((c[0] - r * 0.7, c[1] - r * 1.6, c[0] + r * 0.7, c[1] + r * 1.6), fill=(90, 10, 20, 255), outline=(255, 160, 160, 255), width=max(2, int(0.002 * s)))


def xr_travel(img, d, t, u, T0, s, T):
    k = smooth(u / 0.85)
    seg = k * (len(VEIN) - 1)
    i = min(int(seg), len(VEIN) - 2)
    q = seg - i
    x = lerp(VEIN[i][0], VEIN[i + 1][0], q)
    y = lerp(VEIN[i][1], VEIN[i + 1][1], q)
    d.line([T(*p) for p in VEIN], fill=(80, 120, 255, 200), width=max(3, int(0.006 * s)), joint="curve")
    c = T(x, y)
    r = 0.012 * s
    d.ellipse((c[0] - r, c[1] - r * 1.4, c[0] + r, c[1] + r * 1.4), fill=(90, 10, 20, 255), outline=(255, 160, 160, 255), width=max(2, int(0.003 * s)))


SPEC = dict(
    style=2,
    slug="tromb",
    title="Тромб после перелёта",
    caption="9 часов в самолёте, ни разу не встал… а через 2 дня на лестнице ему не хватило воздуха 😨 Ты встаёшь в долгом перелёте? 👇",
    hashtags="#тромб #перелёт #чтобудетесли #симуляция #организм",
    over="ИГОРЬ, 38 · ПЕРЕЛЁТ 9 ЧАСОВ",
    card=dict(label="ТРОМБ В ВЕНЕ", right_label="ЧАС", notes=[(0, "нет"), (20, "растёт"), (70, "критично")],
              minis=[("ПУЛЬС", "hr"), ("КИСЛОРОД", "98%"), ("ДЫХАНИЕ", "НОРМА")]),
    hr=[(0, 70), (14, 74), (22, 82), (26, 90), (30, 130), (38, 135), (42, 100), (60, 88)],
    shots=[
        dict(kind="hook", dur=2.3, phrase="9 ЧАСОВ В КРЕСЛЕ —\nИ ТРОМБ В ЛЁГКОМ", draw=hook_draw, over="ДОЛГИЙ ПЕРЕЛЁТ"),
        dict(kind="eye", dur=1.0, card=False, pupil=0.4, look=-0.08, iris=(110, 80, 50), over="ДОЛГИЙ ПЕРЕЛЁТ", blink=0.8),
        dict(kind="face", dur=2.9, preset="plane", title="СПИТ ВЕСЬ ПОЛЁТ", tag="ни разу не встал, ноги согнуты", expr="sleep", zoom=3.4,
             outfit="dacha", value=0, clock="0", lighting=(540, 820, 1000, 1.0, 0.55, (230, 230, 255)), amb="inside"),
        dict(kind="xray", dur=2.9, over="ЧАС 5", title="КРОВЬ ЗАСТАИВАЕТСЯ", tag="без ходьбы икры не «качают» кровь вверх", cam=(-0.02, 0.76, 2.2),
             value=(5, 15), clock="5", flow=[dict(path=VEIN[:5], col=(120, 150, 255), n=24, speed=0.05, size=0.006)],
             callouts=[(0.3, (430, 1000), (170, 1150), "ВЕНА ГОЛЕНИ")], riser=True),
        dict(kind="xray", dur=2.9, over="ЧАС 8", title="РАСТЁТ СГУСТОК", tag="в глубокой вене образуется тромб", cam=(-0.02, 0.78, 3.0),
             draw=xr_clot, value=(15, 35), clock="8", red=0.3, callouts=[(0.4, (420, 960), (160, 1160), "ТРОМБ", (255, 110, 110))]),
        dict(kind="scene", dur=2.9, preset="room", ground=1500, over="ЧАС 14", title="НОГА ОПУХЛА", tag="икра ноет — «просто отсидела»",
             cam=(0.0, 0.50, 1.15), outfit="dacha", expr="pain", pose=LEG_PAIN, value=40, clock="14",
             callouts=[(0.3, (480, 1180), (180, 1240), "ОТЁК")]),
        dict(kind="scene", dur=2.8, preset="room", ground=1500, over="ДЕНЬ 2", title="ЗАБЫЛ ПРО НОГУ", tag="гуляет, работает, всё как обычно",
             cam=(0.1, 0.40, 1.2), outfit="dacha", expr="happy", pose=STAND, value=45, clock="48"),
        dict(kind="scene", dur=2.8, preset="stairs", ground=1500, over="ДЕНЬ 3", title="ЛЕСТНИЦА", tag="тромб отрывается от стенки вены",
             cam=(0.1, 0.40, 1.2), outfit="dacha", expr="normal", pose={"arm_a_r": 0.3, "arm_a_l": 0.1, "leg_a_l": 0.4, "leg_b_l": -0.6},
             value=50, clock="62", name="stairs"),
        dict(kind="xray", dur=3.0, over="ДЕНЬ 3", title="ТРОМБ ЛЕТИТ", tag="по вене — через сердце — в лёгкое", cam=(0.0, 0.55, 1.15),
             draw=xr_travel, value=(50, 80), clock="62", red=0.4, hits=[(2.6, 1.2, False)], flash=[(2.6, 0.6)], name="fly"),
        dict(kind="xray", dur=3.0, over="ДЕНЬ 3", title="ЛЁГКОЕ БЕЗ КРОВИ", tag="кровь не может забрать кислород", cam=(0.0, 0.26, 2.4),
             value=90, clock="62", red=0.7, red_tint=0.3,
             glow=[dict(at=(0.045, 0.26), r=0.05, col=(255, 40, 40))], breath_amp=0.09, breath_rate=1.2,
             minis=[("ПУЛЬС", "!135"), ("КИСЛОРОД", "!86%"), ("ДЫХАНИЕ", "!ЧАСТОЕ")],
             callouts=[(0.3, (500, 900), (180, 1180), "ЛЁГОЧНАЯ АРТЕРИЯ", (255, 110, 110))]),
        dict(kind="face", dur=2.8, preset="stairs", over="ДЕНЬ 3", title="НЕ ВДОХНУТЬ", tag="резкая одышка и боль в груди", expr="gasp", zoom=4.6,
             outfit="dacha", sweat=0.8, value=92, clock="62", pov=dict(tunnel=[(0, 0.3), (1, 0.8)]), red=0.6, say="«воздуха… нет»", say_y=1190,
             minis=[("ПУЛЬС", "!138"), ("КИСЛОРОД", "!84%"), ("ДЫХАНИЕ", "!ЧАСТОЕ")], lighting=(540, 820, 900, 0.9, 0.35, (230, 210, 210))),
        dict(kind="phone", dur=2.6, over="ДЕНЬ 3", title="СОСЕД ЗВОНИТ 103", tag="«он задыхается на лестнице!»", clock="62",
             screen=dict(top="вызов…", big="103", sub="скорая помощь", timer=True)),
        dict(kind="scene", dur=3.0, preset="ward", ground=1500, over="РЕАНИМАЦИЯ", title="УСПЕЛИ", tag="лекарства растворяют и не дают расти тромбу",
             cam=(0.0, 0.62, 1.05), outfit="hosp", expr="sleep", pose=LYING, props_back=[("bed", {})], props=[("monitor", {"at": (0.45, 0.3)}), ("iv", {"x": -0.5})],
             value=(92, 40), clock="64", minis=[("ПУЛЬС", "hr"), ("КИСЛОРОД", "95%"), ("ДЫХАНИЕ", "МАСКА")]),
        dict(kind="fact", dur=2.6, value="×2", size=200, line="растёт риск тромбоза после поездки дольше 4 часов", plaque="исследование ВОЗ", pages=(5, 0)),
        dict(kind="fact", dur=2.6, value="1 НА 6000", size=140, line="пассажиров таких перелётов получает тромбоз", plaque="редко — но не ноль", pages=(5, 1)),
        dict(kind="fact", dur=2.6, value="ДНИ СПУСТЯ", size=120, line="тромб может «выстрелить» уже после посадки", plaque="следи за ногой и дыханием", pages=(5, 2)),
        dict(kind="fact", dur=2.6, value="ГОРМОНЫ · ВЕС", size=110, col=(255, 210, 70), line="таблетки-контрацептивы, лишний вес, рост выше 190 или ниже 160", plaque="повышают риск", pages=(5, 3)),
        dict(kind="fact", dur=3.0, value="ОДЫШКА ПОСЛЕ ПОЛЁТА?", size=82, line="в полёте — вставай и двигай стопами;", plaque="одышка + боль в груди — сразу 103", pages=(5, 4)),
        dict(kind="loop", dur=1.6),
    ],
    sfx=[(("stairs", 1.0), "thud", {"g": 0.3}), (("fly", 2.6), "boom", {"g": 0.5}), (29.0, "gasp", {"g": 0.3}), (30.0, "gasp", {"g": 0.3}), (31.2, "gasp", {"g": 0.3})],
)
