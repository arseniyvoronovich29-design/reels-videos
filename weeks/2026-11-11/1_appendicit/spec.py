# Лопнул аппендицит — версия 3 (стиль референсов 10.11), 11 ноября 2026
# Источники:
#  - Addiss D.G. et al., Am J Epidemiol 1990: риск аппендицита за жизнь ≈ 8,6% (муж.) и 6,7% (жен.).
#  - Bickell N.A. et al., J Am Coll Surg 2006: риск перфорации низкий в первые 36 ч от начала симптомов и растёт после.
#  - NHS / MSD Manual «Appendicitis»: боль начинается около пупка и смещается в правую нижнюю часть живота;
#    при разрыве боль может ненадолго стихнуть, затем развивается перитонит (живот напряжён «как доска»), нужна срочная операция.
#  - Клинические рекомендации МЗ РФ «Острый аппендицит»: до осмотра не греть живот и не принимать обезболивающие.
import ui

SKY = dict(outfit="hoodie", shirt=(150, 30, 42), hair=(66, 42, 28))


def H(**kw):
    return dict(SKY, **kw)


def belly(inflame=0.0, burst=0.0, pus=0.0, s=420, cy=980):
    def f(img, t, u, sh):
        O.abdomen(img, 540, cy, s, inflame=kv(inflame, u), burst=kv(burst, u), pus=kv(pus, u), t=t)
    return f


def chat(msgs):
    def f(img, t, u, sh):
        ui.phone(img, 540, 1080, 400, t, msgs=msgs, u=u)
    return f


def call103(img, t, u, sh):
    ui.phone(img, 540, 1050, 340, t, screen=dict(top="ВЫЗОВ…", big="103", sub="СКОРАЯ ПОМОЩЬ"), call_t=u * 2.6)


def gut_micro(img, t, u, sh):
    O.vessel(img, t, flow=0.4, cells=18, bacteria=int(6 + 20 * u), wbc=2, col_bg=(110, 30, 30), y0=620, y1=1300)


def blood_sepsis(img, t, u, sh):
    O.vessel(img, t, flow=1.0, cells=30, bacteria=22, wbc=3, leak=u, y0=620, y1=1300)


def ward_props(img, t, u, sh):
    ui.monitor(img, 70, 1180, 400, 1420, t, hr=104, spo2=95)


def cannula(img, t, u, sh):
    pass


SPEC = dict(
    slug="appendicit",
    title="Лопнул аппендицит",
    caption="Боль вдруг прошла — и он обрадовался… а это был самый опасный момент 😨 Знал этот признак? 👇",
    hashtags="#аппендицит #здоровье #чтобудетесли #симуляция #организм",
    shots=[
        dict(dur=2.2, bg="room", hero=dict(x=540, y=880, s=250, **H(mouth="scream", brows="worried", open=1.25, pupil=0.2, sweat=1, tears=0.7, arms="belly", shake=0.6)),
             title=["ВНУТРИ ТЕБЯ", "{ЛОПНУЛ АППЕНДИКС}"], fx=dict(red=0.5), cam=dict(z=[(0, 1.12), (1, 1.0)]), name="hook"),
        dict(dur=1.6, bg="room", hero=dict(x=540, y=880, s=250, **H(mouth="scream", brows="worried", open=1.25, pupil=0.2, sweat=1, tears=0.9, arms="belly", shake=0.8)),
             title=["ЧТО БУДЕТ", "С ТЕЛОМ?"], fx=dict(red=0.6, dark=0.15), cam=dict(z=[(0, 1.0), (1, 1.1)])),
        dict(dur=2.8, bg="room", hero=dict(x=540, y=980, s=170, **H(mouth="worried", brows="worried", arms="belly")),
             title=["ПЯТНИЦА, 23:00"], sub="просто ноет живот", hud=dict(time=("0 Ч", "С НАЧАЛА БОЛИ"), hr=(82, ""), v=("36,6°", "ТЕМПЕРАТУРА")),
             cam=dict(z=[(0, 1.0), (1, 1.08)])),
        dict(dur=2.8, bg="studio:teal", draw=[belly(0.1)], title=["БОЛИТ", "{У ПУПКА}"], sub="так начинается почти всегда",
             callouts=[(0.3, (540, 1060), (800, 1320), "ПУПОК")], cam=dict(z=[(0, 1.0), (1, 1.06)])),
        dict(dur=2.8, bg="studio:teal", draw=[belly([(0, 0.2), (1, 0.8)])], title=["ОТРОСТОК", "{ЗАКУПОРИЛСЯ}"], sub="аппендикс раздувается изнутри",
             hud=dict(time=("4 Ч", "С НАЧАЛА БОЛИ"), hr=(86, ""), v=("37,1°", "ТЕМПЕРАТУРА")),
             callouts=[(0.3, (330, 1490), (160, 1300), "АППЕНДИКС", (255, 90, 90))], cam=dict(z=[(0, 1.05), (1, 1.6)], c=(330, 1450))),
        dict(dur=2.6, bg="studio:red", draw=[gut_micro], title=["БАКТЕРИИ", "[РАЗМНОЖАЮТСЯ]"], sub="внутри — гной и давление", fx=dict(red=0.2),
             cam=dict(z=[(0, 1.0), (1, 1.1)])),
        dict(dur=2.8, bg="room", hero=dict(x=540, y=900, s=230, **H(mouth="grit", brows="pain", open=0.7, sweat=0.6, arms="belly")),
             title=["ЧАС 10.", "БОЛЬ [ПОЛЗЁТ ВПРАВО]"], sub="в правую нижнюю часть живота",
             hud=dict(time=("10 Ч", "С НАЧАЛА БОЛИ"), hr=(94, ""), v=("37,4°", "ТЕМПЕРАТУРА")), cam=dict(z=[(0, 1.0), (1, 1.08)])),
        dict(dur=3.0, bg="room", hero=dict(x=540, y=760, s=150, **H(mouth="worried", brows="worried", arms="phone")), front=[chat([("живот болит уже полдня 😣", "r"), ("выпей обезболивающее и полежи с грелкой", "l"), ("ок, так и сделаю", "r")])],
             title=["СОВЕТ {ИЗ ЧАТА}"], sub="таблетка лишь приглушает сигнал", cam=dict(z=[(0, 1.0), (1, 1.04)])),
        dict(dur=2.8, bg="room", hero=dict(x=540, y=880, s=250, **H(mouth="grit", brows="pain", open=0.55, sweat=1.0, flush=0.8, bags=0.4)),
             title=["ЖАР", "И [ТОШНОТА]"], sub="больно даже сделать шаг", hud=dict(time=("20 Ч", "С НАЧАЛА БОЛИ"), hr=(104, ""), v=("38,0°", "ТЕМПЕРАТУРА")),
             fx=dict(red=0.25), cam=dict(z=[(0, 1.0), (1, 1.1)])),
        dict(dur=2.6, bg="studio:red", draw=[belly(1.0)], title=["ДАВЛЕНИЕ", "{НА ПРЕДЕЛЕ}"], sub="стенка отростка истончается",
             hud=dict(time=("30 Ч", "С НАЧАЛА БОЛИ"), hr=(110, ""), v=("38,4°", "ТЕМПЕРАТУРА")), fx=dict(red=0.4, shake=0.15), cam=dict(z=[(0, 1.4), (1, 1.7)], c=(330, 1450))),
        dict(dur=3.0, bg="room", hero=dict(x=540, y=900, s=230, **H(mouth="smile", brows="raised", open=1.0)),
             title=["ЧАС 36.", "ВДРУГ [ОТПУСТИЛО]"], sub="он рад: «само прошло!»", hud=dict(time=("36 Ч", "С НАЧАЛА БОЛИ"), hr=(90, ""), v=("38,2°", "ТЕМПЕРАТУРА")),
             cam=dict(z=[(0, 1.0), (1, 1.06)]), name="relief"),
        dict(dur=3.0, bg="studio:red", draw=[belly(1.0, [(0, 0), (0.25, 0.0), (0.6, 1.0)])], title=["ОН {ЛОПНУЛ}"], sub="поэтому боль и стихла",
             fx=dict(red=0.6, flash=[(0.7, 0.9)], hits=[(0.7, 1.4)]), cam=dict(z=[(0, 1.5), (1, 1.2)], c=(330, 1450)), name="burst"),
        dict(dur=2.8, bg="studio:red", draw=[belly(1.0, 1.0, [(0, 0.2), (1, 1.0)])], title=["ГНОЙ ПО ВСЕМУ", "{ЖИВОТУ}"], sub="это перитонит",
             fx=dict(red=0.7, tint=0.25), hud=dict(time=("38 Ч", "С НАЧАЛА БОЛИ"), hr=(122, ""), v=("39,1°", "ТЕМПЕРАТУРА")), cam=dict(z=[(0, 1.0), (1, 1.12)])),
        dict(dur=2.8, bg="room", hero=dict(x=540, y=880, s=255, **H(mouth="scream", brows="worried", open=1.2, pupil=0.25, sweat=1, tears=1, pale=0.35, bags=0.6, arms="belly", shake=0.7)),
             title=["ЖИВОТ", "[КАК ДОСКА]"], sub="больно даже дышать", hud=dict(time=("40 Ч", "С НАЧАЛА БОЛИ"), hr=(128, ""), v=("39,4°", "ТЕМПЕРАТУРА")),
             fx=dict(red=0.5), cam=dict(z=[(0, 1.0), (1, 1.12)]), name="board"),
        dict(dur=2.8, bg="studio:red", draw=[blood_sepsis], title=["ЗАРАЗА", "{В КРОВИ}"], sub="может начаться сепсис", fx=dict(red=0.4, cells=0.6),
             cam=dict(z=[(0, 1.0), (1, 1.1)])),
        dict(dur=2.6, bg="room", hero=dict(x=540, y=880, s=250, **H(mouth="slack", brows="pain", open=0.45, sweat=1, pale=0.6, bags=0.9, tilt=0.12)),
             title=["ТЕМНЕЕТ", "[В ГЛАЗАХ]"], sub="давление падает", fx=dict(tunnel=[(0, 0.2), (1, 0.75)], blur=[(0, 0), (1, 0.25)]),
             hud=dict(time=("40 Ч", "С НАЧАЛА БОЛИ"), hr=(134, ""), v=("39,4°", "ТЕМПЕРАТУРА"))),
        dict(dur=2.6, bg="room", draw=[call103], title=["ЗВОНОК {103}"], sub="наконец-то", cam=dict(z=[(0, 1.0), (1, 1.06)])),
        dict(dur=3.2, bg="ward", hero=dict(x=600, y=940, s=210, **H(outfit="gown", mouth="slack", closed=True, pale=0.4)), draw=[ward_props],
             title=["СРОЧНАЯ", "{ОПЕРАЦИЯ}"], sub="успели — но лечение теперь долгое", hud=dict(time=("41 Ч", "С НАЧАЛА БОЛИ"), hr=(104, ""), v=("38,6°", "ТЕМПЕРАТУРА")),
             cam=dict(z=[(0, 1.0), (1, 1.06)]), soft_cut=True),
        dict(dur=2.8, kind="fact", fact=dict(page=(1, 5), tag="как часто", title=["ЭТО НЕ РЕДКОСТЬ"], big="≈7–9%", unit="людей", line="хоть раз в жизни сталкиваются с аппендицитом")),
        dict(dur=2.8, kind="fact", fact=dict(page=(2, 5), tag="время", title=["РИСК РАЗРЫВА РАСТЁТ"], big="36 Ч", unit="после начала боли", line="не жди утра и «само пройдёт»")),
        dict(dur=2.8, kind="fact", fact=dict(page=(3, 5), tag="главный признак", title=["БОЛЬ ПЕРЕХОДИТ"], big="ПУПОК→", size=170, unit="вправо вниз", line="типичный путь боли при аппендиците")),
        dict(dur=2.8, kind="fact", fact=dict(page=(4, 5), tag="ловушка", title=["РЕЗКО СТИХЛО?"], big="!", size=260, unit="это может быть разрыв", line="облегчение — не всегда хороший знак")),
        dict(dur=3.0, kind="fact", fact=dict(page=(5, 5), tag="что делать", title=["БОЛИТ ПРАВЫЙ НИЗ?"], big="103", unit="без грелки и таблеток", line="до осмотра врача — ничего не глуши")),
        dict(dur=1.6, bg="room", hero=dict(x=540, y=880, s=250, **H(mouth="scream", brows="worried", open=1.25, pupil=0.2, sweat=1, tears=0.7, arms="belly", shake=0.6)),
             title=["ВНУТРИ ТЕБЯ", "{ЛОПНУЛ АППЕНДИКС}"], fx=dict(red=0.5), cam=dict(z=[(0, 1.0), (1, 1.12)]), soft_cut=True, no_hud=True, name="loop"),
    ],
    music=dict(bpm=120, drop="burst", calm=["relief"], key=0),
    sfx=[(("hook", 0.05), "scream", dict(dur=1.4, g=0.35)), (("board", 0.2), "scream", dict(dur=1.3, g=0.3, f0=280)),
         (("relief", 0.5), "breath", dict(dur=1.2, g=0.18)), (("burst", 0.7), "crunch", dict(dur=0.4, g=0.6)), (("burst", 0.7), "boom", dict(g=0.8))],
)
