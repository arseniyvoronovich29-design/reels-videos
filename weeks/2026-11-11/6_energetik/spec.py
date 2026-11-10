# Передоз энергетиками — стиль-3, публикация 15 ноября 2026 (воскресенье)
# Источники:
#  - FDA «Spilling the Beans: How Much Caffeine is Too Much?»: до 400 мг кофеина в сутки обычно безопасно для здоровых взрослых;
#    токсические эффекты, например судороги, наблюдались при быстром приёме около 1200 мг.
#  - StatPearls «Caffeine Toxicity» (NCBI): тахикардия, аритмии, рвота, тремор, возбуждение, гипокалиемия; смертельная доза
#    оценивается примерно в 10 г (150–200 мг/кг) — в ролике помечено «≈».
#  - Содержание кофеина в банке 0,5 л популярных энергетиков — порядка 150–200 мг (по этикеткам), в ролике «≈160 мг».
import ui
import props as PR

STUD = dict(outfit="hoodie", shirt=(40, 46, 70), hair=(34, 26, 22), skin=(234, 186, 154))


def H(**kw):
    return dict(STUD, **kw)


def can(img, cx, by, s, col=(30, 200, 120), t=0.0, open_=True):
    w, h = s * 0.42, s * 1.3
    body = [(cx - w, by - h), (cx + w, by - h), (cx + w, by), (cx - w, by)]
    shade(img, body, col, light=(-0.8, -0.2), hi=0.45, lo=0.55, inner=0.3, outline=(20, 20, 24, 255), ow=3, spec=0.35, spec_at=(0.3, 0.4), spec_r=0.15)
    shade(img, [(cx - w * 0.92, by - h - s * 0.1), (cx + w * 0.92, by - h - s * 0.1), (cx + w, by - h), (cx - w, by - h)], (190, 194, 204), hi=0.5, lo=0.3, inner=0.2)
    d = ImageDraw.Draw(img)
    d.rectangle((cx - w, by - h * 0.62, cx + w, by - h * 0.4), fill=(20, 20, 24, 255))
    f = font(TITLE, s * 0.16)
    d.text((cx - f.getlength("ENERGY") / 2, by - h * 0.6), "ENERGY", font=f, fill=(255, 255, 255, 255))
    for k in range(3):
        shade(img, None, (200, 230, 255), ellipse=(cx - w * 0.5 + k * w * 0.5, by - h * 0.25 - k * 9, 6, 9), hi=0.5, lo=0.1, inner=0.1, alpha=0.7)


def cans_table(img, t, u, sh):
    shade(img, [(-20, 1400), (1100, 1400), (1100, 1600), (-20, 1600)], (90, 66, 52), light=(0, -1), hi=0.3, lo=0.4, inner=0.3)
    cols = [(30, 200, 120), (230, 40, 50), (40, 120, 230), (240, 200, 40)]
    n = 2 + int(6 * smooth(u))
    for k in range(n):
        x = 90 + (k % 8) * 125
        can(img, x, 1440 - (k % 2) * 20, 110, cols[k % 4], t)


def can_big(img, t, u, sh):
    glow(img, 540, 1050, 500, (30, 200, 120), a=0.25)
    can(img, 540, 1480, 420, (30, 200, 120), t)


def syn(img, t, u, sh):
    O.synapse(img, t, block=0.3 + 0.6 * smooth(u), cx=540, cy=980, s=420)


def heart_fast(img, t, u, sh):
    beat = 0.5 + 0.5 * math.sin(t * 2 * math.pi * 2.2)
    O.heart(img, 540, 1080, 200, beat=beat)
    glow(img, 540, 1080, 420, (255, 40, 50), a=0.25 * beat)


def heart_arr(img, t, u, sh):
    ph = (t * 3.1) % 1
    irregular = math.sin(t * 17) * math.sin(t * 5.3)
    beat = max(0, math.sin(ph * math.pi)) * (0.6 + 0.4 * irregular)
    O.heart(img, 540, 960, 180, beat=beat, pale=0.1)
    ui.monitor(img, 140, 1220, 940, 1440, t * (1 + 0.4 * math.sin(t * 7)), hr=168, col=(255, 90, 90))


def potassium(img, t, u, sh):
    O.vessel(img, t, flow=0.8, cells=26, y0=620, y1=1300)
    rng = np.random.default_rng(5)
    n = int(22 * (1 - 0.8 * smooth(u)))
    for k in range(n):
        x = (rng.uniform(0, 1080) + t * 140) % 1150 - 40
        y = rng.uniform(680, 1240)
        shade(img, None, (250, 214, 60), ellipse=(x, y, 22, 22), hi=0.5, lo=0.3, inner=0.2, outline=(80, 60, 0, 255), ow=2)
        label(img, x, y - 17, "K", col=(40, 30, 0), size=26, anchor="c", name=TITLE, stroke=0)


def brain_hot(img, t, u, sh):
    O.head_section(img, 500, 980, 420, shift=0.0)
    k = 0.5 + 0.5 * math.sin(t * 9)
    glow(img, 530, 760, 300, (255, 230, 90), a=0.35 + 0.25 * k)
    for j in range(10):
        a = j * 0.63 + t * 3
        stroke_path(img, [(530 + 120 * math.cos(a), 760 + 90 * math.sin(a)), (530 + 210 * math.cos(a + 0.3), 760 + 160 * math.sin(a + 0.3))], (255, 240, 120, 200), 4, blur=1)


def call103(img, t, u, sh):
    ui.phone(img, 540, 1060, 360, t, screen=dict(top="ВЫЗОВ…", big="103", sub="СКОРАЯ ПОМОЩЬ"), call_t=u * 2.6)


def ward_mon(img, t, u, sh):
    ui.monitor(img, 70, 1170, 420, 1420, t, hr=112, spo2=97)


SPEC = dict(
    slug="energetik",
    title="8 энергетиков за ночь",
    caption="Он просто хотел не уснуть перед экзаменом… к утру сердце сбилось с ритма 😨 Сколько энергетиков ты пил за раз? 👇",
    hashtags="#энергетики #кофеин #чтобудетесли #симуляция #организм",
    shots=[
        dict(dur=2.2, bg="room", hero=dict(x=540, y=880, s=250, **H(mouth="gasp", brows="worried", open=1.25, pupil=0.95, sweat=1, arms="chest", shake=0.9)),
             title=["ТЫ ВЫПИЛ", "{8 ЭНЕРГЕТИКОВ}"], fx=dict(red=0.5), cam=dict(z=[(0, 1.12), (1, 1.0)]), name="hook"),
        dict(dur=1.6, bg="room", hero=dict(x=540, y=880, s=250, **H(mouth="gasp", brows="worried", open=1.25, pupil=0.95, sweat=1, arms="chest", shake=1.0)),
             title=["ЧТО БУДЕТ", "С ТЕЛОМ?"], fx=dict(red=0.6), cam=dict(z=[(0, 1.0), (1, 1.1)])),
        dict(dur=2.8, bg="room", hero=dict(x=540, y=930, s=190, **H(mouth="smile", brows="raised")), front=[cans_table],
             title=["НОЧЬ ПЕРЕД", "{ЭКЗАМЕНОМ}"], sub="банка за банкой, чтобы не уснуть", hud=dict(time=("23:00", "НОЧЬ"), hr=(78, ""), v=("160 МГ", "КОФЕИН")),
             cam=dict(z=[(0, 1.0), (1, 1.07)])),
        dict(dur=2.8, bg="studio:green", draw=[can_big], title=["В ОДНОЙ БАНКЕ", "{≈160 МГ КОФЕИНА}"], sub="безопасно для взрослого — до 400 мг в сутки",
             cam=dict(z=[(0, 1.0), (1, 1.12)], rot=[(0, -2), (1, 2)])),
        dict(dur=2.8, bg="studio:teal", draw=[syn], title=["КОФЕИН ГЛУШИТ", "{СИГНАЛ УСТАЛОСТИ}"], sub="мозгу кажется, что всё отлично",
             callouts=[(0.45, (540, 1030), (180, 1290), "КОФЕИН", (170, 240, 90))], cam=dict(z=[(0, 1.0), (1, 1.1)])),
        dict(dur=2.8, bg="room", hero=dict(x=540, y=900, s=235, **H(mouth="grit", brows="raised", open=1.15, pupil=0.85, sweat=0.4)),
             title=["02:00.", "СЕРДЦЕ [ЧАСТИТ]"], sub="5 банок — уже 800 мг", hud=dict(time=("02:00", "НОЧЬ"), hr=(118, ""), v=("800 МГ", "КОФЕИН")),
             cam=dict(z=[(0, 1.0), (1, 1.08)])),
        dict(dur=2.6, bg="studio:red", draw=[heart_fast], title=["ПУЛЬС", "{130}"], sub="сердце работает на износ", fx=dict(red=0.3),
             hud=dict(time=("03:00", "НОЧЬ"), hr=(130, ""), v=("960 МГ", "КОФЕИН")), cam=dict(z=[(0, 1.0), (1, 1.1)])),
        dict(dur=2.8, bg="room", hero=dict(x=540, y=900, s=235, **H(mouth="worried", brows="worried", open=1.1, pupil=0.9, sweat=0.9, arms="head", shake=1.0)),
             title=["РУКИ", "[ТРЯСУТСЯ]"], sub="тошнит, мысли скачут", cam=dict(z=[(0, 1.0), (1, 1.08)])),
        dict(dur=3.0, bg="room", hero=dict(x=540, y=930, s=190, **H(mouth="smile", brows="raised", open=1.1, pupil=0.9, sweat=0.6)), front=[cans_table],
             title=["«ЕЩЁ ОДНУ —", "{ЧТОБЫ НЕ УСНУТЬ}»"], sub="он не понимает, что это уже передоз", hud=dict(time=("04:00", "НОЧЬ"), hr=(142, ""), v=("1280 МГ", "КОФЕИН")),
             cam=dict(z=[(0, 1.0), (1, 1.06)]), name="calm"),
        dict(dur=2.8, bg="studio:red", draw=[potassium], title=["КАЛИЙ В КРОВИ", "[ПАДАЕТ]"], sub="без него сердце сбивается с ритма",
             callouts=[(0.3, (300, 960), (160, 1400), "КАЛИЙ", (255, 214, 60))], cam=dict(z=[(0, 1.0), (1, 1.1)])),
        dict(dur=3.0, bg="studio:red", draw=[heart_arr], title=["СЕРДЦЕ", "{СБИВАЕТСЯ С РИТМА}"], sub="удары то частят, то пропадают",
             fx=dict(red=0.6, flash=[(0.05, 0.8)], hits=[(0.05, 1.3), (1.4, 0.8)]), hud=dict(time=("05:00", "УТРО"), hr=(168, ""), v=("1280 МГ", "КОФЕИН")),
             cam=dict(z=[(0, 1.0), (1, 1.1)]), name="drop"),
        dict(dur=3.0, bg="room", hero=dict(x=540, y=880, s=255, **H(mouth="gasp", brows="worried", open=1.2, pupil=0.95, sweat=1, pale=0.5, arms="chest", shake=0.6)),
             title=["БОЛЬ В ГРУДИ.", "[ТЕМНЕЕТ]"], sub="голова кружится, не хватает воздуха", fx=dict(tunnel=[(0, 0.3), (1, 0.75)], red=0.4),
             hud=dict(time=("05:10", "УТРО"), hr=(176, ""), v=("1280 МГ", "КОФЕИН")), cam=dict(z=[(0, 1.0), (1, 1.12)]), name="pain"),
        dict(dur=2.8, bg="studio:teal", draw=[brain_hot], title=["МОЗГ", "{ПЕРЕВОЗБУЖДЁН}"], sub="при таких дозах возможны судороги", cam=dict(z=[(0, 1.0), (1, 1.1)])),
        dict(dur=2.6, bg="room", draw=[call103], title=["СОСЕД ЗВОНИТ {103}"], sub="«у него сердце выскакивает!»", cam=dict(z=[(0, 1.0), (1, 1.06)])),
        dict(dur=3.0, bg="ward", hero=dict(x=600, y=920, s=210, **H(outfit="gown", mouth="slack", lid=0.5, pale=0.3)), draw=[ward_mon],
             title=["КАПЕЛЬНИЦА", "И [КАЛИЙ]"], sub="сердце возвращают в ритм", hud=dict(time=("07:00", "УТРО"), hr=(112, ""), v=("↓", "КОФЕИН")),
             cam=dict(z=[(0, 1.0), (1, 1.06)]), soft_cut=True),
        dict(dur=2.8, bg="ward", hero=dict(x=540, y=900, s=230, **H(outfit="gown", mouth="worried", brows="worried", bags=0.7, pale=0.2)),
             title=["ЭКЗАМЕН", "{ПРОПУЩЕН}"], sub="зато живой", hud=dict(time=("12:00", "ДЕНЬ"), hr=(88, "")), cam=dict(z=[(0, 1.0), (1, 1.06)])),
        dict(dur=2.8, kind="fact", fact=dict(page=(1, 5), tag="норма fda", title=["БЕЗОПАСНО В СУТКИ"], big="400 МГ", size=190, unit="кофеина", line="для здорового взрослого")),
        dict(dur=2.8, kind="fact", fact=dict(page=(2, 5), tag="опасно", title=["ВЫПИТЫ БЫСТРО"], big="1200 МГ", size=170, unit="риск судорог", line="это всего 7–8 банок")),
        dict(dur=2.8, kind="fact", fact=dict(page=(3, 5), tag="в банке 0,5 л", title=["ОБЫЧНО"], big="≈160 МГ", size=170, unit="кофеина", line="смотри состав на этикетке")),
        dict(dur=2.8, kind="fact", fact=dict(page=(4, 5), tag="сердце", title=["ГЛАВНАЯ ОПАСНОСТЬ"], big="!", size=260, unit="сбой ритма", line="особенно вместе с бессонной ночью")),
        dict(dur=3.0, kind="fact", fact=dict(page=(5, 5), tag="что делать", title=["СЕРДЦЕ КОЛОТИТСЯ?"], big="103", unit="после энергетиков", line="рвота, дрожь, боль в груди — не жди")),
        dict(dur=1.6, bg="room", hero=dict(x=540, y=880, s=250, **H(mouth="gasp", brows="worried", open=1.25, pupil=0.95, sweat=1, arms="chest", shake=0.9)),
             title=["ТЫ ВЫПИЛ", "{8 ЭНЕРГЕТИКОВ}"], fx=dict(red=0.5), cam=dict(z=[(0, 1.0), (1, 1.12)]), soft_cut=True, no_hud=True, name="loop"),
    ],
    music=dict(bpm=128, drop="drop", calm=["calm"], key=2, prog=[0, 0, 3, -2]),
    sfx=[(("hook", 0.1), "gasp", dict(g=0.3)), (("hook", 0.8), "heartbeat", dict(dur=3.0, bpm=150, g=0.5)), (("drop", 0.2), "heartbeat", dict(dur=2.8, bpm=170, g=0.6)),
         (("pain", 0.2), "breath", dict(dur=2.6, rate=2.8, g=0.3)), (("calm", 0.4), "whoosh", dict(g=0.15))],
)
