# Инсульт в 35 — 8 ноября 2026
# Источники: Saver J.L. «Time is brain — quantified», Stroke 2006: без лечения при ишемическом инсульте в минуту гибнет
#            ~1,9 млн нейронов, 14 млрд синапсов; мозг «стареет» на ~3,6 года за каждый час.
#            Окно тромболизиса до 4,5 ч от начала симптомов — клинические рекомендации AHA/ASA и Минздрава РФ.
#            Признаки «УДАР» (улыбка, движение, артикуляция, решение) — памятка о симптомах инсульта, принятая в России.
import math


def neurons_caption(t, u):
    sh = E.shot_named("neurons")
    mins = 3 + u * 1.0
    return f"потеряно ≈ {mins * 1.9:.1f} млн нейронов"


def draw_desk(img, d, t, u, T0, s, T):
    k = s / 900
    a, b = T0(0.12, 0.47), T0(0.75, 0.50)
    d.rectangle(A.box(a, b), fill=(150, 110, 80, 255))
    a, b = T0(0.38, 0.30), T0(0.70, 0.46)
    d.rounded_rectangle(A.box(a, b), radius=int(8 * k), fill=(30, 34, 44, 255), outline=(90, 90, 100, 255), width=max(2, int(4 * k)))
    a2, b2 = T0(0.40, 0.32), T0(0.68, 0.44)
    d.rectangle(A.box(a2, b2), fill=(80, 140, 220, 255))
    for j in range(5):
        y = 0.34 + j * 0.02
        d.line([T0(0.42, y), T0(0.42 + 0.2 * ((j * 37) % 10) / 10 + 0.05, y)], fill=(230, 240, 255, 255), width=max(2, int(4 * k)))


def draw_cup_fall(img, d, t, u, T0, s, T):
    draw_desk(img, d, t, u, T0, s, T)
    k = smooth((u - 0.25) / 0.3)
    x = 0.25 + 0.04 * k
    y = 0.44 + 0.53 * k * k
    ang = k * 2.0
    cx, cy = T0(x, y)
    w = 0.03 * s
    pts = [(-1, -1.2), (1, -1.2), (0.8, 1), (-0.8, 1)]
    P = [(cx + (px * math.cos(ang) - py * math.sin(ang)) * w, cy + (px * math.sin(ang) + py * math.cos(ang)) * w) for px, py in pts]
    d.polygon(P, fill=(240, 240, 240, 255), outline=(150, 150, 150, 255))
    if u > 0.58:
        for j in range(8):
            a = j * 0.8
            d.line([T0(x, 0.99), T0(x + 0.05 * math.cos(a), 0.99 - 0.03 * abs(math.sin(a)))], fill=(240, 240, 240, 255), width=max(2, int(0.004 * s)))
        lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ImageDraw.Draw(lay).ellipse(A.box(T0(x - 0.1, 0.98), T0(x + 0.1, 1.0)), fill=(110, 70, 40, 180))
        img.alpha_composite(lay)


def draw_colleague(img, d, t, u, T0, s, T):
    draw_desk(img, d, t, u, T0, s, T)
    k = s / 900
    x, y = T0(-0.45, 0.0)
    d.ellipse((x - 45 * k, y - 10 * k, x + 45 * k, y + 80 * k), fill=(60, 50, 46, 255))
    d.rounded_rectangle((x - 80 * k, y + 80 * k, x + 80 * k, y + 420 * k), radius=int(30 * k), fill=(70, 90, 140, 255))


def draw_clot(img, d, t, u, T0, s, T):
    # artery in the brain: a bright vessel with a dark clot stuck in it
    pts = [T(0.035, 0.11), T(0.025, 0.07), T(0.015, 0.045), T(-0.005, 0.03), T(-0.02, 0.025)]
    d.line(pts, fill=(255, 80, 90, 255), width=max(3, int(0.006 * s)), joint="curve")
    k = smooth(u / 0.5)
    cx = lerp(pts[0][0], pts[2][0], k)
    cy = lerp(pts[0][1], pts[2][1], k)
    r = 0.008 * s
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(60, 10, 20, 255), outline=(255, 200, 200, 255), width=max(2, int(0.002 * s)))


def draw_lysis(img, d, t, u, T0, s, T):
    pts = [T(0.035, 0.11), T(0.025, 0.07), T(0.015, 0.045), T(-0.005, 0.03), T(-0.02, 0.025)]
    d.line(pts, fill=(255, 80, 90, 255), width=max(3, int(0.006 * s)), joint="curve")
    cx, cy = pts[2]
    r = 0.008 * s * (1 - smooth((u - 0.3) / 0.5))
    if r > 1:
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(60, 10, 20, 255))
    for j in range(16):
        ph = (t * 0.7 + j / 16) % 1.0
        x = lerp(pts[0][0], pts[2][0], ph)
        y = lerp(pts[0][1], pts[2][1], ph)
        d.ellipse((x - 0.003 * s, y - 0.003 * s, x + 0.003 * s, y + 0.003 * s), fill=(120, 255, 160, 255))


def shot_udar(t, u, sh):
    img = E.dark_bg(t, 0.4)
    d = ImageDraw.Draw(img)
    rows = [("У", "УЛЫБКА", "один угол рта опущен?"), ("Д", "ДВИЖЕНИЕ", "одна рука не поднимается?"),
            ("А", "АРТИКУЛЯЦИЯ", "речь смазана, не повторить фразу?"), ("Р", "РЕШЕНИЕ", "сразу звонить 103 или 112")]
    y = 600
    for k, (L_, w, sub) in enumerate(rows):
        al = ease((u - 0.05 - k * 0.18) / 0.12)
        if al <= 0:
            y += 165
            continue
        d.rounded_rectangle((80, y, 220, y + 140), radius=20, fill=(210, 40, 46, int(255 * al)))
        d.text((150 - F("Black", 100).getlength(L_) / 2, y + 6), L_, font=F("Black", 100), fill=(255, 255, 255, int(255 * al)))
        d.text((250, y + 14), w, font=F("Black", 54), fill=(255, 206, 60, int(255 * al)))
        d.text((252, y + 84), sub, font=F("SemiBold", 30), fill=(235, 235, 240, int(255 * al)))
        y += 165
    return img


DESK = {"arm_a_r": 0.55, "arm_b_r": 1.4, "arm_s_r": 0.8, "arm_a_l": 0.12}
LIMP = {"arm_a_r": 0.55, "arm_b_r": 1.4, "arm_s_r": 0.8, "arm_a_l": 0.02, "arm_b_l": 0.0, "head": -0.12}
LYING = {"rot": -math.pi / 2, "cy": 0.5, "dy": 0.12, "arm_a_r": 0.05, "arm_a_l": 0.05}

SPEC = dict(
    slug="insult",
    title="Инсульт в 35",
    header="СИМУЛЯЦИЯ · ИНСУЛЬТ",
    caption="Коллеги решили, что он просто устал… а мозг каждую минуту терял почти 2 млн нейронов 😨 Знаешь признаки? 👇",
    hashtags="#инсульт #мозг #чтобудетесли #симуляция #организм",
    hr=[(0, 110), (2.6, 76), (5.4, 80), (8.4, 96), (14.0, 104), (22.4, 100), (31.0, 110), (40, 90), (50, 80)],
    shots=[
        dict(kind="face", dur=2.6, title="ИНСУЛЬТ В 35", tag="что будет с телом?", expr="terror", droop=1.0, zoom=4.8, preset="office", red=0.5,
             lighting=(540, 820, 1000, 1.0, 0.5, (255, 245, 230)), outfit="suit"),
        dict(kind="scene", dur=2.8, preset="office", ground=1500, title="ОБЫЧНЫЙ ДЕНЬ", tag="ему 35, он ничем не болеет", timer="14:02",
             cam=(0.2, 0.36, 1.2), outfit="suit", expr="normal", pose=DESK, draw=draw_desk),
        dict(kind="xray", dur=3.0, title="ТРОМБ В МОЗГЕ", tag="сгусток крови перекрывает сосуд", timer="14:03", cam=(0.0, 0.07, 4.2), expr="normal",
             draw=draw_clot, glow=[dict(at=(0.015, 0.045), r=0.02, col=(255, 40, 40), k=[(0, 0), (0.5, 0.2), (1, 1)])],
             labels=[("артерия мозга", "перекрыта", RED, (0.015, 0.045), 1, 1180)], red=0.5, riser=True),
        dict(kind="scene", dur=2.8, preset="office", ground=1500, title="РУКА НЕ СЛУШАЕТСЯ", tag="половина тела вдруг слабеет", timer="14:04",
             cam=(0.2, 0.36, 1.2), outfit="suit", expr="terror", pose=LIMP, draw=draw_cup_fall, droop=0.6, pops=[(1.7, "ДЗЫНЬ!", 760, 1080)], name="cup", red=0.3),
        dict(kind="face", dur=2.8, title="ЛИЦО ПЕРЕКОСИЛО", tag="угол рта опустился, слова не выговорить", timer="14:05", expr="terror", droop=1.0, zoom=4.6,
             preset="office", outfit="suit", lighting=(540, 820, 1000, 1.0, 0.5, (255, 245, 230)), say="«мне… пло… хо…»", red=0.5),
        dict(kind="micro", dur=3.0, cells="neuron", title="МОЗГ УМИРАЕТ", tag="без крови нейроны гибнут каждую минуту", timer="14:06", kill=[(0, 0.1), (1, 0.6)],
             attackers=0, caption=neurons_caption, red=0.6, name="neurons"),
        dict(kind="bignum", dur=2.8, value="1 900 000", size=130, sub=[("нейронов гибнет каждую минуту", WHITE), ("если инсульт не лечить", (255, 120, 120))], red=0.7),
        dict(kind="scene", dur=3.0, preset="office", ground=1500, title="ЕМУ НЕ ВЕРЯТ", tag="думают: устал или выпил", timer="14:15",
             cam=(0.0, 0.36, 1.0), outfit="suit", expr="terror", pose=LIMP, droop=1.0, draw=draw_colleague, say="«да ты просто устал, иди полежи»", say_size=40),
        dict(kind="face", dur=2.8, title="УХОДИТ ВРЕМЯ", tag="каждый час без лечения — минус 3,6 года мозгу", timer="15:00", expr="gasp", droop=1.0, zoom=4.5,
             preset="office", outfit="suit", distort=[(0, 0.2), (1, 0.8)], muffle=0.5, red=0.7, lighting=(540, 820, 900, 0.9, 0.3, (255, 200, 190))),
        dict(kind="custom", fn=shot_udar, dur=4.2, title="ПРИЗНАКИ: «УДАР»", tag="запомни — это спасает мозг", red=0.3, vitals=False),
        dict(kind="scene", dur=2.8, preset="street", ground=1000, props_back=[("bed", {"col": (230, 230, 236)})], title="НАКОНЕЦ СКОРАЯ", tag="звонок 103 — почти через час", timer="15:05",
             cam=(0.0, 0.62, 1.05), outfit="suit", expr="sleep", pose=LYING, droop=1.0, red=0.3, name="ambulance"),
        dict(kind="xray", dur=3.0, title="РАСТВОРЯЮТ ТРОМБ", tag="такая капельница работает только в первые часы — обычно до 4,5 часа", timer="15:40",
             cam=(0.0, 0.07, 4.2), expr="sleep", draw=draw_lysis, labels=[("артерия", "открывается", TEAL, (0.015, 0.045), 1, 1180)], red=0.2),
        dict(kind="scene", dur=3.0, preset="hospital", title="ОН ВЫЖИЛ", tag="но рука слабая, речь восстанавливают месяцами", timer="+3 дня",
             cam=(0.0, 0.62, 1.05), outfit="hosp", expr="normal", droop=0.6, pose=LYING, props_back=[("bed", {})], props=[("monitor", {"at": (0.45, 0.3)})],
             lighting=(540, 900, 800, 1.0, 0.35, (200, 220, 255))),
        dict(kind="myth", dur=3.4, word="ТОЛЬКО У\nСТАРИКОВ?", truth="инсульт бывает и в 30–40", text="поэтому признаки «УДАР» должен знать каждый — и не ждать, что пройдёт само"),
        dict(kind="facts", dur=5.4),
        dict(kind="loop", dur=2.4),
    ],
    facts=[("1,9 млн", "нейронов в минуту теряет мозг при инсульте без лечения"),
           ("3,6 года", "так «стареет» мозг за каждый час без лечения"),
           ("до 4,5 часа", "окно для капельницы, растворяющей тромб"),
           ("«УДАР»", "улыбка, движение рук, речь — и сразу решение звонить"),
           ("103 или 112", "не ждать, что «отпустит», и не везти домой")],
    sfx=[(0.0, "gasp", {"g": 0.25}), (0.4, "groan", {"dur": 1.4, "f0": 140, "g": 0.2}),
         (("cup", 1.7), "crunch", {"dur": 0.25, "g": 0.6}), (("cup", 1.8), "gasp", {"g": 0.25}),
         (13.6, "groan", {"dur": 1.6, "f0": 130, "g": 0.25}), (17.0, "tinnitus", {"dur": 3.0, "g": 0.02}),
         (25.0, "tinnitus", {"dur": 2.8, "g": 0.025}), (25.4, "groan", {"dur": 1.2, "f0": 120, "g": 0.2}),
         (("ambulance", 0.0), "siren", {"dur": 2.8, "g": 0.1})],
)
