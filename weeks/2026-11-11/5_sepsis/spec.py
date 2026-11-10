# Сепсис от пореза — версия 3 (стиль референсов 10.11), 15 ноября 2026
# Источники:
#  - ВОЗ, бюллетень «Сепсис»; Rudd K.E. et al., The Lancet 2020: в 2017 г. ≈ 48,9 млн случаев и ≈ 11 млн смертей (≈ 1 из 5 смертей в мире).
#    Сепсис — нарушенный ответ организма на инфекцию, повреждающий собственные органы; может начаться с любой инфекции, в т.ч. кожной.
#  - Kumar A. et al., Crit Care Med 2006: при септическом шоке каждый час задержки эффективных антибиотиков снижает выживаемость ≈ на 7,6%.
#  - UK Sepsis Trust / NHS «Sepsis»: спутанность, невнятная речь, пятнистая/бледная кожа, частое дыхание, озноб и сильная боль в мышцах,
#    «никогда так плохо не было»; при подозрении — сразу скорая.
import ui
import props as PR

VANYA = dict(outfit="tshirt", shirt=(70, 110, 80), hair=(90, 60, 34), skin=(234, 184, 152))


def H(**kw):
    return dict(VANYA, **kw)


def hand(red=0.3, streaks=0.0):
    def f(img, t, u, sh):
        PR.wounded_hand(img, 540, 960, 330, red=kv(red, u), streaks=kv(streaks, u), t=t)
    return f


def micro(bact=8, wbc=1, leak=0.0, flow=0.6):
    def f(img, t, u, sh):
        O.vessel(img, t, flow=flow, cells=30, bacteria=int(kv(bact, u)), wbc=wbc, leak=kv(leak, u), y0=620, y1=1300)
    return f


def spread(img, t, u, sh):
    O.silhouette(img, 540, 900, 300, alpha=0.4)
    rng = np.random.default_rng(3)
    k = smooth(u / 0.9)
    for i in range(int(90 * k)):
        x, y = rng.uniform(260, 820), rng.uniform(380, 1560)
        if abs(x - 540) > 250 and not (700 < y < 1200):
            continue
        tube(img, [(x - 8, y), (x + 8, y + 4)], (130, 220, 80), 10, hi=0.3, lo=0.3)
    glow(img, 640, 1180, 160, (255, 50, 50), a=0.6)


def organs_fail(img, t, u, sh):
    O.lungs(img, 540, 760, 220, dark=0.4 * u, spots=0.4 * u, heart_beat=0.5 + 0.5 * math.sin(t * 14))
    O.kidneys(img, 540, 1260, 200, fail=smooth(u / 0.6), t=t)


def chat(img, t, u, sh):
    ui.phone(img, 540, 1080, 400, t, msgs=[("температура 39, всё ломит", "r"), ("грипп ходит. выпей жаропонижающее и спи", "l"), ("ок 👍", "r")], u=u)


def call103(img, t, u, sh):
    ui.phone(img, 540, 1060, 360, t, screen=dict(top="ВЫЗОВ…", big="103", sub="СКОРАЯ ПОМОЩЬ"), call_t=u * 2.6)


def mottled(img, t, u, sh):
    pass


def ward_mon(img, t, u, sh):
    ui.monitor(img, 70, 1170, 420, 1420, t, hr=132, spo2=90)


SPEC = dict(
    slug="sepsis",
    title="Сепсис от царапины",
    caption="Порезался на даче, «заживёт само»… через 3 дня он не мог назвать, какой сегодня день 😨 Знал, что так бывает от царапины? 👇",
    hashtags="#сепсис #инфекция #чтобудетесли #симуляция #организм",
    shots=[
        dict(dur=2.2, bg="room", hero=dict(x=540, y=880, s=250, **H(mouth="slack", brows="pain", open=0.6, sweat=1, pale=0.5, blue=0.2, bags=0.9, tilt=0.08, shake=0.3)),
             title=["ОДНА ЦАРАПИНА —", "{И ОТКАЗЫВАЮТ ОРГАНЫ}"], fx=dict(red=0.5), cam=dict(z=[(0, 1.12), (1, 1.0)]), name="hook"),
        dict(dur=1.6, bg="studio:red", draw=[hand(0.9, 1.0)], title=["ЧТО БУДЕТ", "С ТЕЛОМ?"], fx=dict(red=0.5), cam=dict(z=[(0, 1.0), (1, 1.1)])),
        dict(dur=2.8, bg="dacha", hero=dict(x=540, y=940, s=200, **H(mouth="worried", brows="pain", open=0.8)), title=["ДАЧА.", "{ПОРЕЗАЛСЯ О ГРАБЛИ}"],
             sub="«заживёт само»", hud=dict(time=("0 Ч", "ПОСЛЕ ПОРЕЗА"), hr=(78, ""), v=("36,7°", "ТЕМПЕРАТУРА")), cam=dict(z=[(0, 1.0), (1, 1.07)])),
        dict(dur=2.8, bg="studio:teal", draw=[hand(0.2)], title=["НЕ ПРОМЫЛ,", "[НЕ ОБРАБОТАЛ]"], sub="бактерии уже внутри",
             callouts=[(0.35, (520, 1060), (800, 1400), "ПОРЕЗ", (255, 90, 90))], cam=dict(z=[(0, 1.0), (1, 1.2)], c=(540, 1060))),
        dict(dur=2.8, bg="studio:red", draw=[micro(10, 1)], title=["БАКТЕРИИ", "[РАЗМНОЖАЮТСЯ]"], sub="рана краснеет, горячая, дёргает",
             hud=dict(time=("1 ДН", "ПОСЛЕ ПОРЕЗА"), hr=(84, ""), v=("37,4°", "ТЕМПЕРАТУРА")), cam=dict(z=[(0, 1.0), (1, 1.1)])),
        dict(dur=2.8, bg="room", hero=dict(x=540, y=900, s=235, **H(mouth="grit", brows="pain", open=0.7, sweat=0.9, flush=0.8, shake=0.6)),
             title=["ДЕНЬ 2.", "ЭТО [ГРИПП?]"], sub="жар, озноб, ломит всё тело", hud=dict(time=("2 ДН", "ПОСЛЕ ПОРЕЗА"), hr=(108, ""), v=("39,2°", "ТЕМПЕРАТУРА")),
             cam=dict(z=[(0, 1.0), (1, 1.08)])),
        dict(dur=3.0, bg="room", draw=[chat], title=["«ПРОСТО", "{ГРИПП}»"], sub="про порез никто даже не вспомнил", cam=dict(z=[(0, 1.0), (1, 1.04)]), name="calm"),
        dict(dur=3.0, bg="studio:blue", draw=[spread], title=["ЗАРАЗА", "{В КРОВИ}"], sub="бактерии разносятся по всему телу",
             hud=dict(time=("2 ДН", "ПОСЛЕ ПОРЕЗА"), hr=(114, ""), v=("39,4°", "ТЕМПЕРАТУРА")), cam=dict(z=[(0, 1.0), (1, 1.08)])),
        dict(dur=2.8, bg="studio:red", draw=[micro(20, 4, [(0, 0), (1, 1)])], title=["ЗАЩИТА БЬЁТ", "{ПО СВОИМ}"], sub="иммунитет повреждает сосуды",
             fx=dict(red=0.4, cells=0.5), cam=dict(z=[(0, 1.0), (1, 1.1)])),
        dict(dur=2.8, bg="studio:red", draw=[micro(24, 2, 1.0, 1.4)], title=["СОСУДЫ", "[ПРОТЕКАЮТ]"], sub="давление падает", fx=dict(red=0.5),
             hud=dict(time=("3 ДН", "ПОСЛЕ ПОРЕЗА"), hr=(126, ""), v=("90/55", "ДАВЛЕНИЕ")), cam=dict(z=[(0, 1.0), (1, 1.12)]), name="drop"),
        dict(dur=3.0, bg="room", hero=dict(x=540, y=880, s=250, **H(mouth="open", brows="worried", open=0.75, sweat=1, pale=0.6, blue=0.25, bags=1.0, tilt=-0.06)),
             title=["«А КАКОЙ", "[СЕГОДНЯ ДЕНЬ?]»"], sub="мозгу не хватает крови", fx=dict(blur=[(0, 0), (1, 0.2)], double=[(0, 0), (1, 0.4)]),
             hud=dict(time=("3 ДН", "ПОСЛЕ ПОРЕЗА"), hr=(130, ""), v=("80/50", "ДАВЛЕНИЕ")), cam=dict(z=[(0, 1.0), (1, 1.12)], rot=[(0, 0), (1, -3)]), name="confused"),
        dict(dur=3.0, bg="studio:red", draw=[organs_fail], title=["ОРГАНЫ", "{ОТКАЗЫВАЮТ}"], sub="почки, лёгкие…",
             callouts=[(0.3, (430, 1260), (160, 1420), "ПОЧКИ", (255, 90, 90)), (0.5, (680, 760), (820, 1420), "ЛЁГКИЕ", (255, 90, 90))],
             fx=dict(red=0.6, flash=[(0.5, 0.7)], hits=[(0.5, 1.0)]), hud=dict(time=("3 ДН", "ПОСЛЕ ПОРЕЗА"), hr=(134, ""), v=("70/40", "ДАВЛЕНИЕ")),
             cam=dict(z=[(0, 1.0), (1, 1.08)])),
        dict(dur=2.6, bg="room", draw=[call103], title=["ДРУГ ЗВОНИТ {103}"], sub="«он бредит, кожа в пятнах!»", cam=dict(z=[(0, 1.0), (1, 1.06)])),
        dict(dur=3.0, bg="ward", hero=dict(x=600, y=920, s=210, **H(outfit="gown", mouth="slack", closed=True, pale=0.5)), draw=[ward_mon],
             front=[lambda img, t, u, sh: PR.oxygen_mask(img, 600, 920, 210, t)], title=["СЧЁТ", "{НА ЧАСЫ}"], sub="антибиотики — как можно быстрее",
             hud=dict(time=("3 ДН", "ПОСЛЕ ПОРЕЗА"), hr=(132, ""), v=("75/45", "ДАВЛЕНИЕ")), cam=dict(z=[(0, 1.0), (1, 1.06)]), soft_cut=True),
        dict(dur=2.8, bg="ward", hero=dict(x=540, y=900, s=230, **H(outfit="gown", mouth="worried", brows="worried", pale=0.2, bags=0.5)), title=["ВЫЖИЛ"],
             sub="но слабость и последствия — месяцами", hud=dict(time=("2 НЕД", "СПУСТЯ"), hr=(84, ""), v=("115/75", "ДАВЛЕНИЕ")), cam=dict(z=[(0, 1.0), (1, 1.06)])),
        dict(dur=2.8, kind="fact", fact=dict(page=(1, 5), tag="в мире", title=["СМЕРТЕЙ ОТ СЕПСИСА"], big="11 МЛН", size=180, unit="за год", line="≈ каждая пятая смерть · 2017")),
        dict(dur=2.8, kind="fact", fact=dict(page=(2, 5), tag="септический шок", title=["КАЖДЫЙ ЧАС БЕЗ ЛЕЧЕНИЯ"], big="−7,6%", size=200, unit="выживаемости", line="Kumar, 2006")),
        dict(dur=2.8, kind="fact", fact=dict(page=(3, 5), tag="откуда", title=["ЛЮБАЯ ИНФЕКЦИЯ"], big="!", size=260, unit="даже ранка на коже", line="чаще — лёгкие, почки, живот")),
        dict(dur=2.8, kind="fact", fact=dict(page=(4, 5), tag="признаки", title=["ЭТО НЕ ГРИПП"], big="4", size=260, unit="тревожных знака", line="спутанность, частое дыхание, пятна, «так плохо не было»")),
        dict(dur=3.0, kind="fact", fact=dict(page=(5, 5), tag="что делать", title=["ЖАР + СПУТАННОСТЬ?"], big="103", unit="не жди утра", line="особенно после раны или инфекции")),
        dict(dur=1.6, bg="room", hero=dict(x=540, y=880, s=250, **H(mouth="slack", brows="pain", open=0.6, sweat=1, pale=0.5, blue=0.2, bags=0.9, tilt=0.08, shake=0.3)),
             title=["ОДНА ЦАРАПИНА —", "{И ОТКАЗЫВАЮТ ОРГАНЫ}"], fx=dict(red=0.5), cam=dict(z=[(0, 1.0), (1, 1.12)]), soft_cut=True, no_hud=True, name="loop"),
    ],
    music=dict(bpm=120, drop="drop", calm=["calm"], key=-1, prog=[0, 0, 5, 3]),
    sfx=[(("hook", 0.2), "groan", dict(dur=1.5, f0=130, g=0.25)), (("confused", 0.3), "tinnitus", dict(dur=2.6, g=0.12)),
         (("calm", 0.2), "phone", dict(g=0.08)), (("confused", 0.2), "heartbeat", dict(dur=2.7, bpm=130, g=0.45))],
)
