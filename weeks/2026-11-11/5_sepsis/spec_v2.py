# Сепсис от пореза — 15 ноября 2026 (Стиль-2)
# Источники:
#  - ВОЗ, информационный бюллетень «Сепсис»; Rudd K.E. et al., The Lancet 2020 (GBD): в 2017 г. ≈ 48,9 млн случаев
#    и ≈ 11 млн смертей — около 1 из 5 смертей в мире. Сепсис — нарушенный ответ организма на инфекцию,
#    который повреждает собственные ткани и органы; может начаться с любой инфекции, в т.ч. кожной.
#  - Kumar A. et al., Crit Care Med 2006: при септическом шоке каждый час задержки эффективных антибиотиков
#    снижает выживаемость в среднем на 7,6%.
#  - UK Sepsis Trust / NHS «Sepsis»: признаки — спутанность, невнятная речь, пятнистая или бледная кожа, частое дыхание,
#    озноб и сильная мышечная боль, «никогда так плохо не было»; при подозрении — сразу 999/скорая.
import math

STAND = {"arm_a_r": 0.14, "arm_a_l": 0.14}
HAND_UP = {"arm_a_r": 0.45, "arm_b_r": 0.9, "arm_a_l": 0.14}
SHIVER = {"arm_a_r": 0.6, "arm_b_r": 2.7, "arm_s_r": 0.8, "arm_a_l": 0.6, "arm_b_l": 2.7, "arm_s_l": 0.8, "head": 0.05}
LYING = {"rot": -math.pi / 2, "cy": 0.5, "dy": 0.12, "arm_a_r": 0.05, "arm_a_l": 0.05}


def hand(d, cx, cy, sc, red=0.0, t=0.0):
    skin = (226, 176, 146)
    d.rounded_rectangle((cx - 150 * sc, cy - 40 * sc, cx + 150 * sc, cy + 260 * sc), radius=int(90 * sc), fill=skin + (255,))
    for k in range(4):
        x = cx - 120 * sc + k * 76 * sc
        d.rounded_rectangle((x, cy - 260 * sc + abs(k - 1.5) * 26 * sc, x + 64 * sc, cy + 20 * sc), radius=int(32 * sc), fill=skin + (255,))
    d.rounded_rectangle((cx + 150 * sc, cy + 30 * sc, cx + 260 * sc, cy + 110 * sc), radius=int(40 * sc), fill=skin + (255,))
    d.ellipse((cx - 110 * sc, cy + 40 * sc, cx + 110 * sc, cy + 180 * sc), fill=(230, 90, 80, int(140 * red)))
    d.line((cx - 70 * sc, cy + 120 * sc, cx + 60 * sc, cy + 90 * sc), fill=(160, 20, 30, 255), width=int(10 * sc))


def hook_draw(img, d, t, u, *_):
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(g).ellipse((330, 1050, 750, 1300), fill=(255, 40, 40, int(90 + 50 * math.sin(t * 6))))
    img.alpha_composite(g.filter(ImageFilter.GaussianBlur(50)))
    d = ImageDraw.Draw(img)
    hand(d, 540, 1060, 1.3, red=0.8, t=t)
    # red streaks spreading up the wrist
    for k in range(3):
        d.line([(500 + k * 40, 1340), (490 + k * 40 + 10 * math.sin(t + k), 1500), (480 + k * 40, 1700)], fill=(200, 40, 50, 160), width=8)


def draw_cut(img, d, t, u, T0, s, T):
    # garden: rake + wire fence near the hand
    k = s / 900
    a, b = T0(0.35, 0.25), T0(0.37, 1.0)
    d.rectangle(A.box(a, b), fill=(120, 90, 60, 255))
    for j in range(6):
        p = T0(0.30 + j * 0.02, 0.25)
        d.line([p, (p[0], p[1] - 0.05 * s)], fill=(150, 150, 150, 255), width=max(2, int(4 * k)))
    if u > 0.4:
        p = T(0.18, 0.585)
        for j in range(4):
            q = (p[0] + (j - 1.5) * 0.008 * s, p[1] + (0.01 + 0.03 * smooth((u - 0.4) / 0.6)) * s)
            d.ellipse((q[0] - 0.007 * s, q[1] - 0.01 * s, q[0] + 0.007 * s, q[1] + 0.01 * s), fill=(200, 20, 30, 255))


def xr_spread(img, d, t, u, T0, s, T):
    rng = np.random.default_rng(7)
    k = smooth(u / 0.9)
    for j in range(int(140 * k)):
        x = rng.uniform(-0.18, 0.18)
        y = rng.uniform(0.05, 0.95)
        if abs(x) > 0.13 and not (0.17 < y < 0.6):
            continue
        p = T(x, y)
        r = 0.004 * s
        d.ellipse((p[0] - r, p[1] - r, p[0] + r, p[1] + r), fill=(150, 230, 90, 230))


SPEC = dict(
    style=2,
    slug="sepsis",
    title="Сепсис от царапины",
    caption="Порезался на даче, «заживёт само»… через 3 дня он не мог назвать, какой сегодня день 😨 Знал, что так бывает от царапины? 👇",
    hashtags="#сепсис #инфекция #чтобудетесли #симуляция #организм",
    over="ВАНЯ, 27 · ДАЧА",
    card=dict(label="ИНФЕКЦИЯ", right_label="ДЕНЬ", notes=[(0, "местно"), (35, "в крови"), (70, "критично")],
              minis=[("ПУЛЬС", "hr"), ("ТЕМПЕРАТУРА", "36,7"), ("ДАВЛЕНИЕ", "120/80")]),
    hr=[(0, 78), (8, 80), (13, 104), (20, 112), (26, 125), (32, 135), (40, 110), (50, 90), (60, 85)],
    shots=[
        dict(kind="hook", dur=2.3, phrase="ЦАРАПИНА —\nИ ОТКАЗЫВАЮТ ОРГАНЫ", draw=hook_draw, over="СЕПСИС"),
        dict(kind="eye", dur=1.0, card=False, red=0.6, pupil=0.5, look=0.06, over="СЕПСИС", blink=0.8),
        dict(kind="scene", dur=2.9, preset="dacha", ground=1500, title="ПОРЕЗАЛСЯ", tag="о грабли — «заживёт само»",
             cam=(0.12, 0.40, 1.0), outfit="dacha", expr="ouch", pose=HAND_UP, draw=draw_cut, value=5, clock="0", amb="forest",
             callouts=[(0.35, (585, 1040), (820, 920), "ПОРЕЗ")]),
        dict(kind="micro", dur=2.8, cells="blood", over="ДЕНЬ 1", title="БАКТЕРИИ ВНУТРИ", tag="рана краснеет, горячая и дёргает",
             attack_col=(150, 230, 90), attack_shape="rod", attackers=40, kill=[(0, 0.0), (1, 0.3)], value=(10, 25), clock="1", red=0.2),
        dict(kind="scene", dur=2.9, preset="room", ground=1500, over="ДЕНЬ 2", title="ЭТО ГРИПП?", tag="жар, озноб, ломит всё тело",
             cam=(0.1, 0.40, 1.2), outfit="dacha", expr="pain", pose=SHIVER, sweat=0.7, shake=0.25, value=(30, 40), clock="2",
             minis=[("ПУЛЬС", "hr"), ("ТЕМПЕРАТУРА", "!39,2"), ("ДАВЛЕНИЕ", "110/70")]),
        dict(kind="phone", dur=3.0, over="ДЕНЬ 2", title="«ПРОСТО ГРИПП»", tag="про царапину никто даже не вспомнил", clock="2",
             screen=dict(msgs=[("температура 39, всё ломит", "r"), ("грипп ходит, выпей жаропонижающее и спи", "l"), ("ок 👍", "r")])),
        dict(kind="xray", dur=3.0, over="ДЕНЬ 2", title="ЗАРАЗА В КРОВИ", tag="бактерии разносятся по всему телу", cam=(0.0, 0.45, 1.05),
             draw=xr_spread, value=(40, 55), clock="2", red=0.3, riser=True),
        dict(kind="micro", dur=2.8, cells="blood", over="ДЕНЬ 3", title="ЗАЩИТА БЬЁТ ПО СВОИМ", tag="иммунитет повреждает сосуды и органы",
             attack_col=(255, 240, 200), attackers=70, kill=[(0, 0.3), (1, 0.8)], value=(55, 68), clock="3", red=0.5,
             minis=[("ПУЛЬС", "hr"), ("ТЕМПЕРАТУРА", "!39,6"), ("ДАВЛЕНИЕ", "!90/55")]),
        dict(kind="face", dur=3.0, preset="room", over="ДЕНЬ 3", title="ПУТАЕТСЯ В СЛОВАХ", tag="мозгу уже не хватает крови", expr="gasp", zoom=4.6,
             outfit="dacha", sweat=0.9, skin=(206, 186, 176), value=(68, 75), clock="3", say="«а… какой сегодня день?»", say_y=1190,
             pov=dict(blur=[(0, 0.0), (1, 0.15)]), lighting=(540, 820, 900, 0.9, 0.4, (220, 220, 240)), name="confused"),
        dict(kind="xray", dur=3.0, over="ДЕНЬ 3", title="ОРГАНЫ ОТКАЗЫВАЮТ", tag="давление падает: почки, лёгкие…", cam=(0.0, 0.33, 1.7),
             value=(75, 90), clock="3", red=0.7, red_tint=0.3, flash=[(0.6, 0.7)], hits=[(0.6, 1.0, False)],
             glow=[dict(at=(-0.05, 0.36), r=0.035, col=(255, 40, 40)), dict(at=(0.05, 0.36), r=0.035, col=(255, 40, 40)),
                   dict(at=(0.04, 0.25), r=0.05, col=(255, 60, 60), k=[(0, 0), (0.5, 1)])],
             minis=[("ПУЛЬС", "hr"), ("ТЕМПЕРАТУРА", "!35,9"), ("ДАВЛЕНИЕ", "!70/40")],
             callouts=[(0.3, (460, 1000), (170, 1160), "ПОЧКИ", (255, 110, 110)), (0.5, (620, 820), (800, 700), "ЛЁГКИЕ", (255, 110, 110))]),
        dict(kind="phone", dur=2.6, over="ДЕНЬ 3", title="ДРУГ ЗВОНИТ 103", tag="«у него пятна на коже и он бредит!»", clock="3",
             screen=dict(top="вызов…", big="103", sub="скорая помощь", timer=True)),
        dict(kind="scene", dur=3.0, preset="ward", ground=1500, over="РЕАНИМАЦИЯ", title="СЧЁТ НА ЧАСЫ", tag="антибиотики и капельницы — немедленно",
             cam=(0.0, 0.62, 1.05), outfit="hosp", expr="sleep", pose=LYING, props_back=[("bed", {})], props=[("monitor", {"at": (0.45, 0.3)}), ("iv", {"x": -0.5})],
             value=(90, 70), clock="3", minis=[("ПУЛЬС", "hr"), ("ТЕМПЕРАТУРА", "!38,8"), ("ДАВЛЕНИЕ", "!80/50")]),
        dict(kind="scene", dur=2.8, preset="ward", ground=1500, over="ДВЕ НЕДЕЛИ СПУСТЯ", title="ВЫЖИЛ", tag="но слабость и последствия — месяцами",
             cam=(0.1, 0.42, 1.2), outfit="hosp", expr="normal", pose={"arm_a_r": 0.04, "arm_a_l": 0.04, "head": -0.08}, value=(40, 10), clock="14",
             minis=[("ПУЛЬС", "hr"), ("ТЕМПЕРАТУРА", "36,8"), ("ДАВЛЕНИЕ", "115/75")]),
        dict(kind="fact", dur=2.6, value="11 МЛН", size=170, line="смертей от сепсиса в мире за год", plaque="≈ каждая 5-я смерть · 2017", pages=(5, 0)),
        dict(kind="fact", dur=2.6, value="−7,6%", size=170, line="выживаемости за каждый час без антибиотиков при септическом шоке", plaque="Kumar, 2006", pages=(5, 1)),
        dict(kind="fact", dur=2.6, value="ЛЮБАЯ ИНФЕКЦИЯ", size=100, line="может запустить сепсис — даже ранка на коже", plaque="чаще — лёгкие, почки, живот", pages=(5, 2)),
        dict(kind="fact", dur=2.6, value="ПРИЗНАКИ", col=(255, 210, 70), line="спутанность, частое дыхание, пятнистая кожа, «так плохо ещё не было»", plaque="это не грипп", pages=(5, 3)),
        dict(kind="fact", dur=3.0, value="ЖАР + СПУТАННОСТЬ?", size=90, line="особенно после раны или инфекции —", plaque="сразу звони 103", pages=(5, 4)),
        dict(kind="loop", dur=1.6),
    ],
    sfx=[(2.6, "groan", {"dur": 0.5, "f0": 170, "g": 0.2}), (11.0, "cough", {"g": 0.25}), (12.5, "groan", {"dur": 1.2, "f0": 140, "g": 0.18}),
         (("confused", 0.3), "tinnitus", {"dur": 2.6, "g": 0.02})],
)
