# Лопнул аппендицит — 11 ноября 2026 (Стиль-2)
# Источники:
#  - Addiss D.G. et al. «The epidemiology of appendicitis and appendectomy in the United States», Am J Epidemiol 1990:
#    риск аппендицита за жизнь ≈ 8,6% у мужчин и 6,7% у женщин.
#  - Bickell N.A. et al., J Am Coll Surg 2006 «How time affects the risk of rupture in appendicitis»: риск перфорации
#    низкий в первые 36 ч от начала симптомов и растёт после 36 ч.
#  - NHS / MSD Manual «Appendicitis»: боль начинается около пупка и смещается в правую нижнюю часть живота;
#    при разрыве боль может ненадолго стихнуть, затем развивается перитонит (живот напряжён «как доска»), нужна срочная операция.
#  - Клинические рекомендации МЗ РФ «Острый аппендицит» (2020+): до осмотра врача не греть живот и не принимать обезболивающие,
#    чтобы не смазать картину.
import math

PAIN = {"arm_a_r": 0.6, "arm_b_r": 2.95, "arm_s_r": 0.7, "arm_a_l": 0.6, "arm_b_l": 2.95, "arm_s_l": 0.7}
PAIN_BENT = dict(PAIN, rot=0.18, cx=0.0, cy=0.9, head=0.08)
STAND = {"arm_a_r": 0.14, "arm_a_l": 0.14}
PHONE = {"arm_a_r": 0.6, "arm_b_r": 2.4, "arm_s_r": 0.6, "arm_a_l": 0.14}
LYING = {"rot": -math.pi / 2, "cy": 0.5, "dy": 0.12, "arm_a_r": 0.05, "arm_a_l": 0.05}
APX = (-0.055, 0.425)          # appendix in body units (screen-left = right side of the body)


def gut(d, T, s, k_inf=0.0, burst=0.0, t=0.0):
    """intestines + appendix drawn through T (body units)"""
    lw = max(3, int(0.012 * s))
    # large intestine frame
    colon = [(-0.06, 0.44), (-0.075, 0.36), (-0.07, 0.31), (0.0, 0.30), (0.07, 0.31), (0.075, 0.36), (0.065, 0.45), (0.02, 0.47)]
    d.line([T(*p) for p in colon], fill=(190, 140, 120, 230), width=int(lw * 2.2), joint="curve")
    # small intestine loops
    for j in range(5):
        y = 0.335 + j * 0.022
        pts = [(-0.05 + i * 0.01, y + 0.008 * math.sin(i * 1.4 + j)) for i in range(11)]
        d.line([T(*p) for p in pts], fill=(220, 160, 150, 220), width=lw, joint="curve")
    # appendix
    col = (255, int(150 - 110 * k_inf), int(140 - 110 * k_inf))
    sw = 1 + 0.8 * k_inf
    a = T(APX[0], APX[1])
    b = T(APX[0] + 0.012, APX[1] + 0.035)
    d.line([a, b], fill=col + (255,), width=int(lw * 1.4 * sw))
    r = lw * 0.7 * sw
    d.ellipse((b[0] - r, b[1] - r, b[0] + r, b[1] + r), fill=col + (255,))
    if burst > 0:
        rng = np.random.default_rng(3)
        for j in range(int(60 * burst)):
            ang = rng.uniform(0, 2 * math.pi)
            rr = rng.uniform(0.0, 0.11) * burst
            p = T(APX[0] + rr * math.cos(ang), APX[1] + 0.02 + rr * math.sin(ang) * 0.8)
            q = 0.004 * s * rng.uniform(0.6, 1.4)
            d.ellipse((p[0] - q, p[1] - q, p[0] + q, p[1] + q), fill=(220, 200, 90, 220))


def hook_draw(img, d, t, u, *_):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(lay)
    cx, cy, sc = 540, 1180, 2600
    T = lambda x, y: (cx + x * sc, cy + (y - 0.38) * sc)
    sil = [(-0.30, 0.10), (-0.16, 0.20), (-0.13, 0.30), (-0.115, 0.38), (-0.13, 0.46), (-0.14, 0.62), (0.14, 0.62), (0.13, 0.46), (0.115, 0.38), (0.13, 0.30), (0.16, 0.20), (0.30, 0.10)]
    ld.polygon([T(*p) for p in sil], fill=(110, 130, 175, 46), outline=(150, 170, 215, 130))
    ld.line([T(*p) for p in sil], fill=(150, 170, 215, 150), width=4)
    img.alpha_composite(lay)
    d = ImageDraw.Draw(img)
    k = 0.6 + 0.4 * math.sin(t * 7)
    gut(d, T, sc, k_inf=0.9, t=t)
    p = T(APX[0] + 0.006, APX[1] + 0.02)
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(g).ellipse((p[0] - 90, p[1] - 90, p[0] + 90, p[1] + 90), fill=(255, 40, 40, int(150 * k)))
    img.alpha_composite(g.filter(ImageFilter.GaussianBlur(30)))


def xr_inflame(img, d, t, u, T0, s, T):
    gut(d, T, s, k_inf=0.2 + 0.7 * smooth(u), t=t)


def xr_burst(img, d, t, u, T0, s, T):
    gut(d, T, s, k_inf=1.0, burst=smooth((u - 0.25) / 0.5), t=t)


def xr_perit(img, d, t, u, T0, s, T):
    gut(d, T, s, k_inf=1.0, burst=1.0, t=t)
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    c = T(0.0, 0.39)
    r = (0.05 + 0.08 * smooth(u)) * s
    ImageDraw.Draw(lay).ellipse((c[0] - r, c[1] - r * 0.8, c[0] + r, c[1] + r * 0.8), fill=(255, 40, 40, int(110 + 40 * math.sin(t * 6))))
    img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(r * 0.25)))


SPEC = dict(
    style=2,
    slug="appendicit",
    title="Лопнул аппендицит",
    caption="Боль вдруг прошла — и он обрадовался… а это был самый опасный момент 😨 Знал этот признак? 👇",
    hashtags="#аппендицит #здоровье #чтобудетесли #симуляция #организм",
    over="МАКС, 24 · ПЯТНИЦА",
    card=dict(label="ВОСПАЛЕНИЕ", right_label="ЧАС", notes=[(0, "норма"), (30, "опасно"), (70, "критично")],
              minis=[("ПУЛЬС", "hr"), ("ТЕМПЕРАТУРА", "36,6"), ("БОЛЬ", "СЛАБАЯ")]),
    hr=[(0, 84), (8, 82), (14, 92), (20, 100), (25, 86), (29, 118), (36, 130), (41, 112), (45, 90), (60, 85)],
    shots=[
        dict(kind="hook", dur=2.3, phrase="БОЛЬ ПРОШЛА —\nЗНАЧИТ, ЛОПНУЛ", draw=hook_draw, over="АППЕНДИЦИТ"),
        dict(kind="eye", dur=1.2, card=False, pupil=[(0, 0.3), (1, 0.75)], red=0.3, over="АППЕНДИЦИТ", look=-0.05, blink=0.7),
        dict(kind="scene", dur=2.9, preset="room", ground=1500, title="ПРОСТО ЖИВОТ", tag="ноет вокруг пупка — «съел что-то не то»",
             cam=(0.1, 0.42, 1.25), outfit="casual", expr="normal", pose=PAIN, clock="0", value=8,
             callouts=[(0.3, (540, 1000), (780, 900), "НОЕТ У ПУПКА")]),
        dict(kind="xray", dur=2.9, over="ЧАС 4", title="ОТРОСТОК ЗАКУПОРЕН", tag="аппендикс воспаляется и раздувается", cam=(0.0, 0.40, 3.0),
             draw=xr_inflame, value=(10, 25), clock="4", minis=[("ПУЛЬС", "hr"), ("ТЕМПЕРАТУРА", "37,2"), ("БОЛЬ", "СРЕДНЯЯ")],
             callouts=[(0.35, (390, 1130), (180, 1240), "АППЕНДИКС")], riser=True, red=0.2),
        dict(kind="scene", dur=2.9, preset="room", ground=1500, over="ЧАС 10", title="БОЛЬ ПОЛЗЁТ ВПРАВО", tag="в правую нижнюю часть живота",
             cam=(0.05, 0.42, 1.3), outfit="casual", expr="pain", pose=PAIN_BENT, value=(25, 35), clock="10", sweat=0.3,
             callouts=[(0.3, (470, 1060), (170, 1200), "ПРАВЫЙ НИЗ")]),
        dict(kind="phone", dur=3.0, over="ЧАС 12", title="СОВЕТ ИЗ ЧАТА", tag="таблетка лишь приглушает сигнал", clock="12",
             screen=dict(msgs=[("живот болит уже полдня 😣", "r"), ("выпей обезболивающее и полежи с грелкой", "l"), ("ок, так и сделаю", "r")])),
        dict(kind="face", dur=2.8, preset="room", over="ЧАС 20", title="ЖАР И ТОШНОТА", tag="больно даже сделать шаг", expr="pain", zoom=4.6,
             outfit="casual", sweat=0.8, value=(40, 55), clock="20", minis=[("ПУЛЬС", "hr"), ("ТЕМПЕРАТУРА", "!38,0"), ("БОЛЬ", "!СИЛЬНАЯ")],
             lighting=(540, 820, 1000, 1.0, 0.5, (255, 220, 190))),
        dict(kind="micro", dur=2.8, cells="blood", over="ЧАС 30", title="ВНУТРИ — ГНОЙ", tag="бактерии размножаются в закрытом отростке",
             attack_col=(150, 230, 90), attack_shape="rod", attackers=60, kill=[(0, 0.2), (1, 0.7)], value=(55, 72), clock="30", red=0.4),
        dict(kind="scene", dur=3.0, preset="room", ground=1500, over="ЧАС 36", title="ВДРУГ ОТПУСТИЛО", tag="боль стихла… он рад: «прошло!»",
             cam=(0.1, 0.40, 1.2), outfit="casual", expr="happy", pose=STAND, value=72, clock="36",
             minis=[("ПУЛЬС", "hr"), ("ТЕМПЕРАТУРА", "!38,2"), ("БОЛЬ", "СЛАБЕЕТ")], say="«фух, само прошло»", say_y=1180, name="relief"),
        dict(kind="xray", dur=3.0, over="ЧАС 36", title="ОН ЛОПНУЛ", tag="давление упало — поэтому стало легче", cam=(0.0, 0.40, 3.0),
             draw=xr_burst, value=(72, 88), clock="36", red=0.6, flash=[(0.8, 0.9)], hits=[(0.8, 1.2, False)], name="burst",
             callouts=[(0.45, (390, 1150), (170, 1250), "РАЗРЫВ", (255, 90, 90))]),
        dict(kind="xray", dur=2.8, over="ЧАС 38", title="ПЕРИТОНИТ", tag="гной разлился по всему животу", cam=(0.0, 0.40, 2.4),
             draw=xr_perit, value=(88, 94), clock="38", red=0.7, red_tint=0.3,
             minis=[("ПУЛЬС", "hr"), ("ТЕМПЕРАТУРА", "!39,1"), ("БОЛЬ", "!АДСКАЯ")]),
        dict(kind="face", dur=2.8, preset="room", over="ЧАС 40", title="ЖИВОТ КАК ДОСКА", tag="любое движение — адская боль", expr="terror",
             zoom=4.6, outfit="casual", sweat=1.0, tears=0.6, skin=(214, 190, 170), value=95, clock="40", say="«не могу… встать»", say_y=1190,
             lighting=(540, 820, 900, 0.9, 0.35, (230, 210, 210)), red=0.5),
        dict(kind="phone", dur=2.6, over="ЧАС 40", title="ЗВОНОК 103", tag="наконец-то", clock="40",
             screen=dict(top="вызов…", big="103", sub="скорая помощь", timer=True)),
        dict(kind="scene", dur=3.0, preset="ward", ground=1500, over="ОПЕРАЦИЯ", title="УСПЕЛИ", tag="но лечение теперь намного дольше и тяжелее",
             cam=(0.0, 0.62, 1.05), outfit="hosp", expr="sleep", pose=LYING, props_back=[("bed", {})], props=[("monitor", {"at": (0.45, 0.3)}), ("iv", {"x": -0.5})],
             value=(95, 40), clock="+1 ДЕНЬ", minis=[("ПУЛЬС", "hr"), ("ТЕМПЕРАТУРА", "37,8"), ("СОЗНАНИЕ", "НАРКОЗ")]),
        dict(kind="fact", dur=2.6, value="≈ 7–9%", line="людей хоть раз в жизни сталкиваются с аппендицитом", plaque="это не редкость", pages=(5, 0)),
        dict(kind="fact", dur=2.6, value="36 ЧАСОВ", line="после этого риск разрыва заметно растёт", plaque="не тяни до утра", pages=(5, 1)),
        dict(kind="fact", dur=2.6, value="ПУПОК → ВПРАВО", size=110, line="типичный путь боли при аппендиците", plaque="правый низ живота", pages=(5, 2)),
        dict(kind="fact", dur=2.6, value="СТИХЛО ≠ ПРОШЛО", size=100, col=(255, 210, 70), line="резкое облегчение может означать разрыв", plaque="и это самое опасное", pages=(5, 3)),
        dict(kind="fact", dur=3.0, value="БОЛИТ ПРАВЫЙ НИЗ?", size=96, line="без грелки и таблеток до осмотра —", plaque="сразу к врачу или 103", pages=(5, 4)),
        dict(kind="loop", dur=1.6),
    ],
    sfx=[(0.2, "gasp", {"g": 0.2}), (8.8, "groan", {"dur": 1.2, "f0": 140, "g": 0.18}), (15.4, "groan", {"dur": 1.5, "f0": 130, "g": 0.2}),
         (("relief", 0.8), "breath", {"dur": 1.2, "g": 0.2}), (("burst", 0.8), "crunch", {"dur": 0.3, "g": 0.5}),
         (32.0, "scream", {"dur": 1.2, "g": 0.25}), (33.6, "groan", {"dur": 1.6, "f0": 120, "g": 0.25})],
)
