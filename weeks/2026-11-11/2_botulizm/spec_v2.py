# Ботулизм из домашних консервов — 12 ноября 2026 (Стиль-2)
# Источники:
#  - CDC «Botulism — Signs and Symptoms» / «Home-Canned Foods»: симптомы обычно через 18–36 ч (от 6 ч до 10 дней);
#    двоение в глазах, опущенные веки, смазанная речь, трудно глотать, сухость во рту, нисходящая слабость мышц,
#    паралич дыхательных мышц; токсин нельзя увидеть, почувствовать по запаху или вкусу; домашние консервы прокипятить 10 минут.
#  - ВОЗ, информационный бюллетень «Ботулизм»: инкубационный период обычно 12–36 ч; токсин разрушается кипячением;
#    лечение — антитоксин и ИВЛ; восстановление может занять недели и месяцы.
#  - Роспотребнадзор, памятка о профилактике ботулизма: основная причина в РФ — домашние консервы (особенно грибы),
#    вздутые крышки — признак опасности, но опасной может быть и банка без вздутия.
import math

STAND = {"arm_a_r": 0.14, "arm_a_l": 0.14}
EAT = {"arm_a_r": 0.6, "arm_b_r": 2.4, "arm_s_r": 0.6, "arm_a_l": 0.3, "arm_b_l": 0.6}
WEAK = {"arm_a_r": 0.04, "arm_a_l": 0.04, "head": -0.1}
LYING = {"rot": -math.pi / 2, "cy": 0.5, "dy": 0.12, "arm_a_r": 0.05, "arm_a_l": 0.05}


def jar(d, x, y, sc, bulge=1.0, t=0.0):
    """mushroom jar centred at (x, y-bottom), 1080-space"""
    w, h = 170 * sc, 260 * sc
    d.rounded_rectangle((x - w / 2, y - h, x + w / 2, y), radius=int(28 * sc), fill=(150, 175, 185, 120), outline=(220, 235, 240, 255), width=int(5 * sc))
    d.rounded_rectangle((x - w / 2 + 12 * sc, y - h + 50 * sc, x + w / 2 - 12 * sc, y - 12 * sc), radius=int(18 * sc), fill=(120, 100, 50, 230))
    for k in range(9):
        mx = x - w / 2 + 34 * sc + (k % 3) * 50 * sc
        my = y - 50 * sc - (k // 3) * 60 * sc
        d.chord((mx - 26 * sc, my - 22 * sc, mx + 26 * sc, my + 18 * sc), 180, 360, fill=(170, 120, 60, 255))
        d.rectangle((mx - 7 * sc, my - 2 * sc, mx + 7 * sc, my + 22 * sc), fill=(220, 200, 160, 255))
    d.rectangle((x - w / 2 - 6 * sc, y - h - 26 * sc, x + w / 2 + 6 * sc, y - h + 6 * sc), fill=(200, 176, 60, 255))
    if bulge:
        b = 34 * sc * bulge
        d.chord((x - w / 2 - 6 * sc, y - h - 26 * sc - b, x + w / 2 + 6 * sc, y - h - 26 * sc + b), 180, 360, fill=(200, 176, 60, 255))
    for k in range(5):
        ph = (t * 0.6 + k * 0.2) % 1
        bx = x - w / 2 + 30 * sc + k * 26 * sc
        by = lerp(y - 20 * sc, y - h + 60 * sc, ph)
        d.ellipse((bx - 5 * sc, by - 5 * sc, bx + 5 * sc, by + 5 * sc), fill=(255, 255, 255, 110))


def hook_draw(img, d, t, u, *_):
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(g).ellipse((300, 760, 780, 1300), fill=(200, 160, 60, 40))
    img.alpha_composite(g.filter(ImageFilter.GaussianBlur(60)))
    d = ImageDraw.Draw(img)
    d.rectangle((0, 1260, W, 1300), fill=(70, 52, 40, 255))
    jar(d, 540, 1260, 1.6, bulge=0.8 + 0.2 * math.sin(t * 5), t=t)
    # spoon
    d.line((760, 1100, 980, 900), fill=(200, 205, 215, 255), width=16)
    d.ellipse((720, 1080, 800, 1140), fill=(200, 205, 215, 255))


def draw_table(img, d, t, u, T0, s, T):
    k = s / 900
    a, b = T0(0.10, 0.52), T0(0.75, 0.55)
    d.rectangle(A.box(a, b), fill=(110, 80, 60, 255))
    for xx in (0.14, 0.71):
        a, b = T0(xx - 0.01, 0.55), T0(xx + 0.01, 1.0)
        d.rectangle(A.box(a, b), fill=(90, 66, 50, 255))
    x, y = T0(0.52, 0.52)
    jar(d, x, y, k * 0.32, bulge=0.7, t=t)
    a, b = T0(0.22, 0.505), T0(0.38, 0.52)
    d.ellipse(A.box(a, b), fill=(240, 240, 240, 255))
    for j in range(4):
        a, b = T0(0.25 + j * 0.03, 0.49), T0(0.27 + j * 0.03, 0.51)
        d.chord(A.box(a, b), 180, 360, fill=(170, 120, 60, 255))


def draw_vent(img, d, t, u, T0, s, T):
    k = s / 900
    a, b = T0(0.45, 0.20), T0(0.70, 0.45)
    d.rounded_rectangle(A.box(a, b), radius=int(10 * k), fill=(70, 80, 92, 255), outline=(150, 160, 170, 255), width=max(2, int(4 * k)))
    a2, b2 = T0(0.47, 0.22), T0(0.68, 0.32)
    d.rectangle(A.box(a2, b2), fill=(12, 20, 26, 255))
    pts = []
    for j in range(40):
        xx = lerp(a2[0] + 6 * k, b2[0] - 6 * k, j / 39)
        ph = (t * 0.25 - j / 39 * 1.5) % 1
        pts.append((xx, (a2[1] + b2[1]) / 2 - 0.03 * s * math.sin(ph * 2 * math.pi) * (ph < 0.5)))
    d.line(pts, fill=(90, 200, 255, 255), width=max(2, int(3 * k)))
    # tube to the mouth
    d.line([T0(0.45, 0.40), T0(0.25, 0.42), T(0.0, 0.17)], fill=(200, 220, 230, 255), width=max(3, int(10 * k)), joint="curve")


def xr_resp(img, d, t, u, T0, s, T):
    pass


SPEC = dict(
    style=2,
    slug="botulizm",
    title="Ботулизм из домашней банки",
    caption="Банку грибов открыли «на закуску»… через сутки он всё понимал, но не мог даже позвать на помощь 😨 Кипятишь домашние консервы? 👇",
    hashtags="#ботулизм #консервы #чтобудетесли #симуляция #организм",
    over="ОЛЕГ, 45 · СУББОТА",
    card=dict(label="ПАРАЛИЧ МЫШЦ", right_label="ЧАС", notes=[(0, "норма"), (30, "слабость"), (70, "критично")],
              minis=[("ПУЛЬС", "hr"), ("ДЫХАНИЕ", "НОРМА"), ("СОЗНАНИЕ", "ЯСНОЕ")]),
    hr=[(0, 78), (12, 80), (24, 92), (32, 104), (38, 112), (44, 90), (60, 80)],
    shots=[
        dict(kind="hook", dur=2.3, phrase="ЛОЖКА ГРИБОВ —\nИ ТЫ НЕ ДЫШИШЬ", draw=hook_draw, over="ДОМАШНИЕ КОНСЕРВЫ"),
        dict(kind="eye", dur=1.2, card=False, lid=[(0, 0.0), (1, 0.3)], pupil=0.6, look=0.04, over="БОТУЛИЗМ"),
        dict(kind="scene", dur=2.9, preset="kitchen2", ground=1500, title="ДОМАШНЯЯ ЗАКАТКА", tag="крышку чуть вздуло — «да нормально»",
             cam=(0.3, 0.37, 1.2), outfit="casual", expr="happy", pose=EAT, draw=draw_table, clock="0", value=0,
             callouts=[(0.3, (790, 1000), (860, 820), "КРЫШКУ ВЗДУЛО")]),
        dict(kind="flasks", dur=3.0, over="В БАНКЕ", title="НИ ЗАПАХА, НИ ВКУСА", tag="без воздуха бактерия делает яд",
             items=[("споры в грибах", (170, 130, 70)), ("банка без воздуха", (140, 150, 120)), ("ботулотоксин", (150, 220, 90))], organ=None, splash=True, clock="0"),
        dict(kind="scene", dur=2.8, preset="kitchen2", ground=1500, over="ЧАС 18", title="ВСЁ НОРМАЛЬНО?", tag="ни боли, ни жара — только сухо во рту",
             cam=(0.1, 0.37, 1.2), outfit="casual", expr="normal", pose=STAND, value=5, clock="18"),
        dict(kind="scene", dur=2.8, preset="kitchen2", ground=1500, over="ЧАС 22", title="ДВОИТСЯ В ГЛАЗАХ", tag="яд глушит сигнал от нервов к мышцам",
             cam=(0.3, 0.37, 1.2), outfit="casual", expr="normal", pose=STAND, draw=draw_table, pov=dict(double=[(0, 0.3), (1, 1.0)], blur=0.25),
             value=(10, 20), clock="22", hud=True),
        dict(kind="eye", dur=2.6, over="ЧАС 24", title="ВЕКИ ПАДАЮТ", tag="сначала слабеют мышцы лица и глаз", lid=[(0, 0.3), (1, 0.6)], pupil=0.7,
             value=(20, 30), clock="24", minis=[("ПУЛЬС", "hr"), ("ДЫХАНИЕ", "НОРМА"), ("РЕЧЬ", "!СМАЗАНА")]),
        dict(kind="micro", dur=2.8, cells="neuron", over="ЧАС 26", title="ПРОВОДА ОТКЛЮЧЕНЫ", tag="нервы целы — но мышцы не слышат команд",
             kill=[(0, 0.2), (1, 0.7)], attackers=30, attack_col=(150, 220, 90), value=(30, 45), clock="26", red=0.3),
        dict(kind="face", dur=2.8, preset="kitchen2", over="ЧАС 28", title="НЕ ПРОГЛОТИТЬ", tag="трудно говорить и глотать", expr="pain", zoom=4.6,
             outfit="casual", value=(45, 55), clock="28", say="«мне… пло… хо»", say_y=1190,
             lighting=(540, 820, 1000, 1.0, 0.5, (255, 230, 200))),
        dict(kind="xray", dur=3.0, over="ЧАС 32", title="ПАРАЛИЧ ИДЁТ ВНИЗ", tag="шея, руки… дыхательные мышцы", cam=(0.0, 0.28, 1.8),
             expr="sleep", breath_amp=[(0, 0.05), (1, 0.008)], value=(55, 75), clock="32", red=0.5,
             minis=[("ПУЛЬС", "hr"), ("ДЫХАНИЕ", "!СЛАБОЕ"), ("СОЗНАНИЕ", "ЯСНОЕ")],
             glow=[dict(at=(0.0, 0.40), r=0.07, col=(255, 60, 60), k=[(0, 0.2), (1, 1.0)])],
             callouts=[(0.35, (540, 945), (800, 1040), "ДИАФРАГМА")], riser=True),
        dict(kind="face", dur=3.0, preset="kitchen2", over="ЧАС 34", title="ОН ВСЁ ПОНИМАЕТ", tag="сознание ясное — но не может позвать", expr="sleep",
             zoom=4.8, outfit="casual", tears=0.7, value=(75, 85), clock="34", red=0.6, pov=dict(tunnel=[(0, 0.2), (1, 0.6)]),
             minis=[("ПУЛЬС", "hr"), ("ДЫХАНИЕ", "!ЕЛЕ-ЕЛЕ"), ("СОЗНАНИЕ", "ЯСНОЕ")], name="aware",
             lighting=(540, 820, 900, 0.9, 0.35, (230, 210, 210))),
        dict(kind="phone", dur=2.6, over="ЧАС 34", title="ЖЕНА ЗВОНИТ 103", tag="«он не может говорить!»", clock="34",
             screen=dict(top="вызов…", big="103", sub="скорая помощь", timer=True)),
        dict(kind="scene", dur=3.0, preset="ward", ground=1500, over="РЕАНИМАЦИЯ", title="ДЫШИТ АППАРАТ", tag="антитоксин остановил яд — но паралич остался",
             cam=(0.0, 0.62, 1.05), outfit="hosp", expr="sleep", pose=LYING, props_back=[("bed", {})], draw=draw_vent, value=85, clock="36",
             minis=[("ПУЛЬС", "hr"), ("ДЫХАНИЕ", "!ИВЛ"), ("СОЗНАНИЕ", "ЯСНОЕ")]),
        dict(kind="scene", dur=2.8, preset="ward", ground=1500, over="НЕДЕЛИ СПУСТЯ", title="УЧИТСЯ ЗАНОВО", tag="нервные окончания отрастают неделями и месяцами",
             cam=(0.1, 0.42, 1.2), outfit="hosp", expr="normal", pose=WEAK, value=(60, 35), clock="+6 НЕД",
             minis=[("ПУЛЬС", "hr"), ("ДЫХАНИЕ", "САМ"), ("СИЛЫ", "!МАЛО")]),
        dict(kind="fact", dur=2.6, value="12–36 ЧАСОВ", size=120, line="обычно проходит от еды до первых симптомов", plaque="иногда — до 10 дней", pages=(5, 0)),
        dict(kind="fact", dur=2.6, value="0 ЗАПАХА", line="ботулотоксин не видно и не почувствовать на вкус", plaque="банка может выглядеть нормально", pages=(5, 1)),
        dict(kind="fact", dur=2.6, value="НЕДЕЛИ", line="может длиться жизнь на аппарате ИВЛ", plaque="пока восстанавливаются нервы", pages=(5, 2)),
        dict(kind="fact", dur=2.6, value="10 МИНУТ", col=(255, 210, 70), line="кипячения перед едой разрушают токсин", plaque="совет для домашних консервов", pages=(5, 3)),
        dict(kind="fact", dur=3.0, value="ДВОИТСЯ + ВЕКИ?", size=100, line="после домашних консервов —", plaque="сразу звони 103", pages=(5, 4)),
        dict(kind="loop", dur=1.6),
    ],
    sfx=[(0.3, "gasp", {"g": 0.15}), (("aware", 0.4), "breath", {"dur": 2.0, "g": 0.25}), (24.0, "groan", {"dur": 1.4, "f0": 110, "g": 0.18})],
)
