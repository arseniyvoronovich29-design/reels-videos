# Тромб после долгого перелёта (ТЭЛА) — версия 3 (стиль референсов 10.11), 14 ноября 2026
# Источники:
#  - ВОЗ, проект WRIGHT, 2007: после поездок > 4 ч риск венозного тромбоза примерно удваивается; абсолютный риск ≈ 1 на 6000
#    для перелётов > 4 ч; риск выше при ожирении, росте > 1,9 м или < 1,6 м, приёме оральных контрацептивов; совет — двигать икрами.
#  - CDC Yellow Book «Deep Vein Thrombosis & Pulmonary Embolism»: отёк, боль, покраснение ноги; при ТЭЛА — внезапная одышка,
#    боль в груди, учащённое сердцебиение; может проявиться через дни после поездки.
#  - NHS «Pulmonary embolism»: нужна срочная помощь, лечат антикоагулянтами, при тяжёлой ТЭЛА растворяют тромб.
import ui

IGOR = dict(outfit="tshirt", shirt=(56, 80, 130), hair=(40, 30, 24), skin=(232, 182, 150))


def H(**kw):
    return dict(IGOR, **kw)


def legv(clot=0.0, swell=0.0, travel=None, flow=1.0):
    def f(img, t, u, sh):
        O.leg(img, 540, 1000, 420, clot=kv(clot, u), swell=kv(swell, u), t=t, flow=flow, travel=kv(travel, u) if travel is not None else None)
    return f


def path_clot(img, t, u, sh):
    O.silhouette(img, 540, 760, 260, alpha=0.35)
    # leg below the silhouette
    tube(img, [(470, 1420), (460, 1700)], (150, 180, 230), 120)
    pts = [(470, 1690), (480, 1420), (500, 1150), (520, 900), (560, 760)]
    stroke_path(img, catmull(pts, closed=False, n=8), (70, 90, 210, 230), 16)
    O.heart(img, 560, 760, 70, beat=0.5 + 0.5 * math.sin(t * 10), vessels=False)
    O.lungs(img, 540, 650, 160, show_heart=False)
    k = smooth(u / 0.85)
    P = catmull(pts + [(600, 640)], closed=False, n=8)
    p = P[min(len(P) - 1, int(k * (len(P) - 1)))]
    shade(img, None, (90, 10, 22), ellipse=(p[0], p[1], 20, 34), hi=0.3, lo=0.5, inner=0.4, outline=(30, 0, 6, 255), ow=3)
    glow(img, p[0], p[1], 90, (255, 30, 40), a=0.5)


def lung_block(img, t, u, sh):
    O.lungs(img, 540, 960, 320, breath=1 + 0.08 * math.sin(t * 7), block=smooth(u / 0.6), heart_beat=0.5 + 0.5 * math.sin(t * 14))


def plane_window(img, t, u, sh):
    pass


def call103(img, t, u, sh):
    ui.phone(img, 540, 1060, 360, t, screen=dict(top="ВЫЗОВ…", big="103", sub="СКОРАЯ ПОМОЩЬ"), call_t=u * 2.6)


def micro_clot(img, t, u, sh):
    O.vessel(img, t, flow=0.25, cells=34, clot=0.3 + 0.6 * smooth(u), col_bg=(70, 40, 90), y0=620, y1=1300)


def ward_mon(img, t, u, sh):
    ui.monitor(img, 70, 1170, 420, 1420, t, hr=110, spo2=92)


SPEC = dict(
    slug="tromb",
    title="Тромб после перелёта",
    caption="9 часов в самолёте, ни разу не встал… а через 2 дня на лестнице ему не хватило воздуха 😨 Ты встаёшь в долгом перелёте? 👇",
    hashtags="#тромб #перелёт #чтобудетесли #симуляция #организм",
    shots=[
        dict(dur=2.2, bg="stairs", hero=dict(x=540, y=880, s=250, **H(mouth="gasp", brows="worried", open=1.2, pupil=0.25, sweat=1, blue=0.45, arms="chest", shake=0.5)),
             title=["ТЫ НЕ МОЖЕШЬ", "{ВДОХНУТЬ}"], fx=dict(red=0.5), cam=dict(z=[(0, 1.12), (1, 1.0)]), name="hook"),
        dict(dur=1.6, bg="stairs", hero=dict(x=540, y=880, s=250, **H(mouth="gasp", brows="worried", open=1.2, pupil=0.25, sweat=1, blue=0.55, arms="chest", shake=0.7)),
             title=["ЧТО БУДЕТ", "С ТЕЛОМ?"], fx=dict(red=0.6, tunnel=0.4), cam=dict(z=[(0, 1.0), (1, 1.1)])),
        dict(dur=2.8, bg="plane", hero=dict(x=540, y=960, s=200, **H(mouth="neutral", closed=True)), title=["ПЕРЕЛЁТ", "{9 ЧАСОВ}"], sub="спит, ни разу не встал",
             hud=dict(time=("0 Ч", "ПОСЛЕ ВЗЛЁТА"), hr=(68, ""), o2=("98%", "")), cam=dict(z=[(0, 1.0), (1, 1.07)])),
        dict(dur=2.8, bg="studio:blue", draw=[legv(flow=0.25)], title=["КРОВЬ", "{ЗАСТАИВАЕТСЯ}"], sub="без ходьбы икры не «качают» кровь вверх",
             callouts=[(0.3, (480, 1040), (180, 1320), "ВЕНА ГОЛЕНИ", (130, 170, 255))], hud=dict(time=("5 Ч", "ПОСЛЕ ВЗЛЁТА"), hr=(66, ""), o2=("98%", "")),
             cam=dict(z=[(0, 1.0), (1, 1.1)])),
        dict(dur=2.6, bg="studio:blue", draw=[micro_clot], title=["РАСТЁТ", "[СГУСТОК]"], sub="в глубокой вене образуется тромб", cam=dict(z=[(0, 1.0), (1, 1.12)])),
        dict(dur=2.8, bg="studio:blue", draw=[legv(clot=[(0, 0.3), (1, 1.0)], flow=0.2)], title=["ТРОМБ", "[В НОГЕ]"], sub="его пока никто не замечает",
             callouts=[(0.35, (477, 1105), (180, 1320), "ТРОМБ", (255, 90, 90))], hud=dict(time=("8 Ч", "ПОСЛЕ ВЗЛЁТА"), hr=(70, ""), o2=("98%", "")),
             cam=dict(z=[(0, 1.0), (1, 1.4)], c=(480, 1100))),
        dict(dur=2.8, bg="room", hero=dict(x=540, y=900, s=230, **H(mouth="grit", brows="pain", open=0.8)), title=["ИКРА", "[ОПУХЛА]"], sub="«просто отсидел ногу»",
             hud=dict(time=("14 Ч", "ПОСЛЕ ВЗЛЁТА"), hr=(74, ""), o2=("98%", "")), cam=dict(z=[(0, 1.0), (1, 1.08)])),
        dict(dur=2.8, bg="room", hero=dict(x=540, y=900, s=230, **H(mouth="smile", brows="raised")), title=["ДЕНЬ 2.", "НОГА [ПОЧТИ НЕ БОЛИТ]"], sub="он забыл про неё",
             hud=dict(time=("2 ДН", "ПОСЛЕ ВЗЛЁТА"), hr=(72, ""), o2=("98%", "")), cam=dict(z=[(0, 1.0), (1, 1.06)]), name="calm"),
        dict(dur=2.8, bg="stairs", hero=dict(x=540, y=920, s=220, **H(mouth="neutral", brows="neutral")), title=["ДЕНЬ 3.", "{ЛЕСТНИЦА}"], sub="пара пролётов вверх",
             hud=dict(time=("3 ДН", "ПОСЛЕ ВЗЛЁТА"), hr=(96, ""), o2=("97%", "")), cam=dict(z=[(0, 1.0), (1, 1.06)], y=[(0, 0), (1, -30)])),
        dict(dur=3.0, bg="studio:blue", draw=[path_clot], title=["ТРОМБ", "{ОТОРВАЛСЯ}"], sub="по вене — через сердце — в лёгкое",
             fx=dict(flash=[(2.5, 0.8)], hits=[(2.5, 1.3)]), cam=dict(z=[(0, 1.0), (1, 1.1)]), name="fly"),
        dict(dur=3.0, bg="studio:red", draw=[lung_block], title=["ЛЁГКОЕ", "{БЕЗ КРОВИ}"], sub="кровь не может взять кислород",
             callouts=[(0.35, (700, 1000), (800, 1420), "ЗАКУПОРКА", (255, 90, 90))], hud=dict(time=("3 ДН", "ПОСЛЕ ВЗЛЁТА"), hr=(132, ""), o2=("86%", "")),
             fx=dict(red=0.6), cam=dict(z=[(0, 1.0), (1, 1.12)]), name="drop"),
        dict(dur=3.0, bg="stairs", hero=dict(x=540, y=880, s=255, **H(mouth="gasp", brows="worried", open=1.2, pupil=0.25, sweat=1, blue=0.5, arms="chest", shake=0.5)),
             title=["НЕ ВДОХНУТЬ.", "[БОЛЬ В ГРУДИ]"], sub="сердце колотится на пределе", hud=dict(time=("3 ДН", "ПОСЛЕ ВЗЛЁТА"), hr=(138, ""), o2=("82%", "")),
             fx=dict(tunnel=[(0, 0.3), (1, 0.7)], red=0.4), cam=dict(z=[(0, 1.0), (1, 1.12)]), name="gasp"),
        dict(dur=2.6, bg="stairs", draw=[call103], title=["СОСЕД ЗВОНИТ {103}"], sub="«он задыхается!»", cam=dict(z=[(0, 1.0), (1, 1.06)])),
        dict(dur=3.0, bg="ward", hero=dict(x=600, y=920, s=210, **H(outfit="gown", mouth="slack", lid=0.5, pale=0.3)), draw=[ward_mon],
             front=[lambda img, t, u, sh: __import__("props").oxygen_mask(img, 600, 920, 210, t)],
             title=["{УСПЕЛИ}"], sub="лекарства не дают тромбу расти", hud=dict(time=("3 ДН", "ПОСЛЕ ВЗЛЁТА"), hr=(110, ""), o2=("92%", "")),
             cam=dict(z=[(0, 1.0), (1, 1.06)]), soft_cut=True),
        dict(dur=2.8, kind="fact", fact=dict(page=(1, 5), tag="исследование воз", title=["ПОСЛЕ 4 ЧАСОВ В ПУТИ"], big="×2", size=260, unit="риск тромбоза", line="длинный перелёт — фактор риска")),
        dict(dur=2.8, kind="fact", fact=dict(page=(2, 5), tag="как часто", title=["ТРОМБ ПОЛУЧАЕТ"], big="1/6000", size=190, unit="пассажиров", line="перелётов дольше 4 часов")),
        dict(dur=2.8, kind="fact", fact=dict(page=(3, 5), tag="ловушка", title=["МОЖЕТ «ВЫСТРЕЛИТЬ»"], big="ДНИ", size=230, unit="спустя", line="уже после посадки")),
        dict(dur=2.8, kind="fact", fact=dict(page=(4, 5), tag="риск выше", title=["ГОРМОНЫ · ВЕС · РОСТ"], big="!", size=260, unit="контрацептивы, лишний вес", line="рост выше 190 или ниже 160 см")),
        dict(dur=3.0, kind="fact", fact=dict(page=(5, 5), tag="что делать", title=["ОДЫШКА ПОСЛЕ ПОЛЁТА?"], big="103", unit="сразу", line="а в полёте вставай и двигай стопами")),
        dict(dur=1.6, bg="stairs", hero=dict(x=540, y=880, s=250, **H(mouth="gasp", brows="worried", open=1.2, pupil=0.25, sweat=1, blue=0.45, arms="chest", shake=0.5)),
             title=["ТЫ НЕ МОЖЕШЬ", "{ВДОХНУТЬ}"], fx=dict(red=0.5), cam=dict(z=[(0, 1.0), (1, 1.12)]), soft_cut=True, no_hud=True, name="loop"),
    ],
    music=dict(bpm=116, drop="drop", calm=["calm"], key=3, prog=[0, 0, 3, 2]),
    sfx=[(("hook", 0.1), "gasp", dict(g=0.3)), (("hook", 0.7), "gasp", dict(g=0.3)), (("gasp", 0.2), "breath", dict(dur=2.6, rate=2.6, g=0.32)),
         (("gasp", 0.2), "heartbeat", dict(dur=2.6, bpm=138, g=0.5)), (("fly", 2.5), "boom", dict(g=0.7))],
)
