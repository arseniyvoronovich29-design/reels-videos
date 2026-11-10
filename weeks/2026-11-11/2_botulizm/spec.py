# Ботулизм из домашних консервов — версия 3 (стиль референсов 10.11), 12 ноября 2026
# Источники:
#  - CDC «Botulism — Signs and Symptoms», «Home-Canned Foods»: симптомы обычно через 18–36 ч (от 6 ч до 10 дней):
#    двоение, опущенные веки, смазанная речь, трудно глотать, сухость во рту, нисходящая слабость, паралич дыхательных мышц;
#    токсин нельзя увидеть, почувствовать по запаху или вкусу; домашние консервы прокипятить 10 минут.
#  - ВОЗ, бюллетень «Ботулизм»: инкубация обычно 12–36 ч; токсин разрушается кипячением; лечение — антитоксин и ИВЛ;
#    восстановление — недели и месяцы.
#  - Роспотребнадзор, памятка о профилактике ботулизма: основная причина в РФ — домашние консервы (особенно грибы);
#    вздутая крышка — признак опасности, но опасной может быть и банка без вздутия.
import ui
import props as PR

OLEG = dict(outfit="tshirt", shirt=(60, 74, 60), hair=(48, 34, 26), skin=(230, 180, 146))


def H(**kw):
    return dict(OLEG, **kw)


def table_jar(img, t, u, sh):
    from gfx import shade
    shade(img, [(-20, 1380), (1100, 1380), (1100, 1560), (-20, 1560)], (110, 78, 56), light=(0, -1), hi=0.3, lo=0.4, inner=0.3)
    PR.jar(img, 820, 1420, 150, bulge=0.6, t=t)
    shade(img, None, (240, 240, 244), ellipse=(300, 1410, 170, 40), hi=0.3, lo=0.3, inner=0.3)


def jar_close(img, t, u, sh):
    PR.jar(img, 540, 1440, 330, bulge=0.8 + 0.1 * math.sin(t * 3), t=t)


def jar_inside(img, t, u, sh):
    O.vessel(img, t, flow=0.15, cells=0, bacteria=14, toxin=int(4 + 14 * u), col_bg=(60, 58, 26), y0=600, y1=1320)


def toxin_big(img, t, u, sh):
    glow(img, 540, 1000, 500, (120, 200, 80), a=0.25)
    for k in range(7):
        a = k * 0.9 + t * 0.2
        r = 220 + 60 * math.sin(k)
        O.molecule(img, 540 + r * math.cos(a), 1000 + r * 0.8 * math.sin(a), 34, (150, 230, 80), t + k)
    O.molecule(img, 540, 1000, 70, (160, 240, 90), t)


def syn(img, t, u, sh):
    O.synapse(img, t, block=smooth((u - 0.2) / 0.5), cx=540, cy=980, s=420)


def body_paralysis(img, t, u, sh):
    O.silhouette(img, 540, 900, 300, alpha=0.4)
    lungs_small(img, t, u, sh, show=False)
    k = 0.15 + 0.7 * smooth(u)
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    y = 280 + 1300 * k
    ImageDraw.Draw(lay).rectangle((0, 0, W, y), fill=(120, 140, 170, 130))
    m = Image.new("L", img.size, 0)
    lay = lay.filter(ImageFilter.GaussianBlur(40))
    img.alpha_composite(lay)
    stroke_path(img, [(160, y), (920, y)], (150, 230, 80, 220), 6, blur=3)


def lungs_small(img, t, u, sh, show=True):
    b = 1 + 0.06 * math.sin(t * 2.6) * (1 - 0.85 * smooth(u))
    O.lungs(img, 540, 900, 260, breath=b, dark=0.2 * u, heart_beat=0.5 + 0.5 * math.sin(t * 9))
    if show:
        tube(img, [(250, 1260), (540, 1180), (830, 1260)], (200, 90, 100), 30, outline=(40, 12, 18, 255))


def call103(img, t, u, sh):
    ui.phone(img, 540, 1060, 360, t, screen=dict(top="ВЫЗОВ…", big="103", sub="СКОРАЯ ПОМОЩЬ"), call_t=u * 2.6)


def vent(img, t, u, sh):
    PR.ventilator_tube(img, 600, 920, 210, t)
    ui.monitor(img, 70, 1170, 420, 1420, t, hr=96, spo2=97)


SPEC = dict(
    slug="botulizm",
    title="Ботулизм из домашней банки",
    caption="Банку грибов открыли «на закуску»… через сутки он всё понимал, но не мог даже позвать на помощь 😨 Кипятишь домашние консервы? 👇",
    hashtags="#ботулизм #консервы #чтобудетесли #симуляция #организм",
    shots=[
        dict(dur=2.2, bg="kitchen", hero=dict(x=540, y=880, s=250, **H(mouth="slack", brows="worried", lid=0.55, tears=0.9, pupil=0.7, tilt=0.06)),
             title=["ЛОЖКА ГРИБОВ —", "{И ТЫ НЕ ДЫШИШЬ}"], fx=dict(red=0.5), cam=dict(z=[(0, 1.12), (1, 1.0)]), name="hook"),
        dict(dur=1.6, bg="studio:green", draw=[jar_close], title=["ЧТО БУДЕТ", "С ТЕЛОМ?"], fx=dict(red=0.3), cam=dict(z=[(0, 1.0), (1, 1.1)])),
        dict(dur=2.8, bg="kitchen", hero=dict(x=540, y=960, s=180, **H(mouth="smile", brows="raised")), front=[table_jar],
             title=["СУББОТА, УЖИН"], sub="домашние грибы, закатанные летом", hud=dict(time=("0 Ч", "ПОСЛЕ ЕДЫ"), hr=(76, ""), o2=("99%", "")),
             cam=dict(z=[(0, 1.0), (1, 1.07)])),
        dict(dur=2.8, bg="studio:green", draw=[jar_close], title=["КРЫШКУ", "{ЧУТЬ ВЗДУЛО}"], sub="«да нормально, съедим»",
             callouts=[(0.3, (540, 860), (820, 720), "ВЗДУТИЕ", (255, 210, 80))], cam=dict(z=[(0, 1.0), (1, 1.15)], c=(540, 900))),
        dict(dur=2.8, bg="studio:green", draw=[jar_inside], title=["В БАНКЕ", "{БЕЗ ВОЗДУХА}"], sub="бактерия выделяет яд", cam=dict(z=[(0, 1.0), (1, 1.1)]),
             callouts=[(0.4, (560, 960), (820, 1400), "БОТУЛОТОКСИН", (170, 240, 90))]),
        dict(dur=2.6, bg="studio:green", draw=[toxin_big], title=["НИ ВКУСА,", "[НИ ЗАПАХА]"], sub="один из сильнейших ядов в природе", cam=dict(z=[(0, 1.0), (1, 1.15)], rot=[(0, 0), (1, 4)])),
        dict(dur=2.8, bg="kitchen", hero=dict(x=540, y=900, s=230, **H(mouth="neutral", brows="neutral")),
             title=["ЧАС 18.", "ВСЁ [НОРМАЛЬНО?]"], sub="только сухо во рту", hud=dict(time=("18 Ч", "ПОСЛЕ ЕДЫ"), hr=(80, ""), o2=("98%", "")),
             cam=dict(z=[(0, 1.0), (1, 1.06)]), name="calm"),
        dict(dur=2.8, bg="kitchen", hero=dict(x=540, y=900, s=230, **H(mouth="worried", brows="worried", lid=0.2)), front=[table_jar],
             title=["ВСЁ", "[ДВОИТСЯ]"], sub="яд добрался до нервов", fx=dict(double=[(0, 0.3), (1, 1.0)], blur=[(0, 0.0), (1, 0.15)]),
             hud=dict(time=("22 Ч", "ПОСЛЕ ЕДЫ"), hr=(84, ""), o2=("98%", ""))),
        dict(dur=3.0, bg="studio:teal", draw=[syn], title=["НЕРВ ШЛЁТ СИГНАЛ —", "{МЫШЦА НЕ СЛЫШИТ}"], sub="токсин блокирует передачу",
             callouts=[(0.5, (540, 1030), (180, 1290), "ТОКСИН", (170, 240, 90))], cam=dict(z=[(0, 1.0), (1, 1.1)])),
        dict(dur=2.8, bg="kitchen", hero=dict(x=540, y=880, s=255, **H(mouth="worried", brows="worried", lid=[(0, 0.45), (1, 0.72)], sweat=0.4)),
             title=["ВЕКИ", "[ПАДАЮТ]"], sub="первыми слабеют мышцы лица", hud=dict(time=("24 Ч", "ПОСЛЕ ЕДЫ"), hr=(88, ""), o2=("97%", "")),
             cam=dict(z=[(0, 1.0), (1, 1.12)])),
        dict(dur=2.8, bg="kitchen", hero=dict(x=540, y=880, s=240, **H(mouth="slack", brows="pain", lid=0.65, sweat=0.6, arms="throat")),
             title=["НЕ МОЖЕТ", "{ГЛОТАТЬ}"], sub="речь смазана: «мнэ… пло… хо»", hud=dict(time=("28 Ч", "ПОСЛЕ ЕДЫ"), hr=(94, ""), o2=("96%", "")),
             cam=dict(z=[(0, 1.0), (1, 1.08)])),
        dict(dur=2.8, bg="studio:blue", draw=[body_paralysis], title=["ПАРАЛИЧ", "[ИДЁТ ВНИЗ]"], sub="шея, руки… грудь", cam=dict(z=[(0, 1.0), (1, 1.06)]),
             hud=dict(time=("32 Ч", "ПОСЛЕ ЕДЫ"), hr=(102, ""), o2=("93%", ""))),
        dict(dur=3.0, bg="studio:red", draw=[lungs_small], title=["ДИАФРАГМА", "{СДАЁТСЯ}"], sub="каждый вдох всё слабее",
             callouts=[(0.35, (540, 1200), (800, 1400), "ДИАФРАГМА", (255, 120, 120))], fx=dict(red=0.5, flash=[(0.05, 0.7)]),
             hud=dict(time=("34 Ч", "ПОСЛЕ ЕДЫ"), hr=(112, ""), o2=("88%", "")), cam=dict(z=[(0, 1.0), (1, 1.12)]), name="drop"),
        dict(dur=3.2, bg="kitchen", hero=dict(x=540, y=880, s=260, **H(mouth="slack", brows="worried", lid=0.62, tears=1.0, pale=0.4, blue=0.3, pupil=0.8)),
             title=["ОН ВСЁ СЛЫШИТ", "{И ВСЁ ПОНИМАЕТ}"], sub="но не может даже позвать на помощь", fx=dict(tunnel=[(0, 0.3), (1, 0.7)], red=0.3),
             hud=dict(time=("34 Ч", "ПОСЛЕ ЕДЫ"), hr=(118, ""), o2=("84%", "")), cam=dict(z=[(0, 1.0), (1, 1.15)]), name="aware"),
        dict(dur=2.6, bg="kitchen", draw=[call103], title=["ЖЕНА ЗВОНИТ {103}"], sub="«он не может говорить!»", cam=dict(z=[(0, 1.0), (1, 1.06)])),
        dict(dur=3.0, bg="ward", hero=dict(x=600, y=920, s=210, **H(outfit="gown", mouth="slack", lid=0.7, pale=0.3)), front=[vent],
             title=["ДЫШИТ", "{АППАРАТ}"], sub="антитоксин остановил яд — но не вернул силу", hud=dict(time=("36 Ч", "ПОСЛЕ ЕДЫ"), hr=(96, ""), o2=("97%", "")),
             cam=dict(z=[(0, 1.0), (1, 1.06)]), soft_cut=True),
        dict(dur=2.8, bg="ward", hero=dict(x=540, y=900, s=230, **H(outfit="gown", mouth="worried", brows="worried", lid=0.3, pale=0.2)),
             title=["НЕДЕЛИ", "[ВОССТАНОВЛЕНИЯ]"], sub="нервные окончания отрастают заново", hud=dict(time=("6 НЕД", "СПУСТЯ"), hr=(80, ""), o2=("98%", "")),
             cam=dict(z=[(0, 1.0), (1, 1.06)])),
        dict(dur=2.8, kind="fact", fact=dict(page=(1, 5), tag="когда", title=["СИМПТОМЫ ЧЕРЕЗ"], big="12–36 Ч", unit="после еды", line="иногда — до 10 дней")),
        dict(dur=2.8, kind="fact", fact=dict(page=(2, 5), tag="ловушка", title=["ЗАПАХ ЯДА"], big="0", size=260, unit="и вкуса тоже", line="банка может выглядеть нормально")),
        dict(dur=2.8, kind="fact", fact=dict(page=(3, 5), tag="лечение", title=["НА АППАРАТЕ ИВЛ"], big="НЕДЕЛИ", size=170, unit="а иногда месяцы", line="пока не отрастут нервные окончания")),
        dict(dur=2.8, kind="fact", fact=dict(page=(4, 5), tag="защита", title=["ПРОКИПЯТИ"], big="10 МИН", size=190, unit="домашние консервы", line="кипячение разрушает токсин")),
        dict(dur=3.0, kind="fact", fact=dict(page=(5, 5), tag="что делать", title=["ДВОИТСЯ + ВЕКИ?"], big="103", unit="сразу, не жди утра", line="особенно после домашних заготовок")),
        dict(dur=1.6, bg="kitchen", hero=dict(x=540, y=880, s=250, **H(mouth="slack", brows="worried", lid=0.55, tears=0.9, pupil=0.7, tilt=0.06)),
             title=["ЛОЖКА ГРИБОВ —", "{И ТЫ НЕ ДЫШИШЬ}"], fx=dict(red=0.5), cam=dict(z=[(0, 1.0), (1, 1.12)]), soft_cut=True, no_hud=True, name="loop"),
    ],
    music=dict(bpm=118, drop="drop", calm=["calm"], key=-2, prog=[0, 0, -4, -2], mel=[12, 15, 19, 17, 15, 12, 10, 12]),
    sfx=[(("hook", 0.2), "breath", dict(dur=1.8, rate=1.4, g=0.25)), (("aware", 0.2), "breath", dict(dur=2.6, rate=1.0, g=0.3)),
         (("drop", 0.05), "boom", dict(g=0.7)), (("aware", 0.4), "heartbeat", dict(dur=2.6, bpm=118, g=0.5))],
)
