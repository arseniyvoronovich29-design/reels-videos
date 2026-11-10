# ДТП без ремня на заднем сиденье — версия 3 (стиль референсов 10.11), 13 ноября 2026
# Источники:
#  - ВОЗ, бюллетень «Травмы в результате ДТП»: ремень снижает риск гибели водителя и пассажиров спереди до 50%, сзади — до 25%.
#  - Ichikawa M. et al., The Lancet 2002: риск гибели пристёгнутого водителя/переднего пассажира примерно в 5 раз выше,
#    если сзади сидит непристёгнутый пассажир.
#  - Физика: 60 км/ч = 16,7 м/с; h = v²/2g ≈ 14 м (≈ 5 этаж).
#  - NHTSA, материалы по механизму травм: машина останавливается за доли секунды, непристёгнутое тело продолжает двигаться;
#    мозг и внутренние органы ударяются по инерции.
import props as PR

DANYA = dict(outfit="hoodie", shirt=(220, 120, 40), hair=(66, 42, 28))
DRV = dict(outfit="jacket", shirt=(50, 90, 140), hair=(30, 22, 18), skin=(226, 176, 140))


def H(**kw):
    return dict(DANYA, **kw)


def car(crash=0.0, fly=0.0, speed=1.0, pole=None, lean=0.0, alarm=False):
    def f(img, t, u, sh):
        PR.car_side(img, t, crash=kv(crash, u), fly=kv(fly, u), speed=speed, pole=kv(pole, u) if pole is not None else None, drv_lean=kv(lean, u), alarm=alarm)
    return f


def belt_strap(img, t, u, sh):
    pass


def no_belt(img, t, u, sh):
    # hanging unused belt next to the hero
    stroke_path(img, [(150, 380), (120, 900), (140, 1380)], (40, 42, 50, 255), 46)
    for k in range(16):
        y = 420 + k * 60
        stroke_path(img, [(118 + 0, y), (165, y + 10)], (70, 74, 86, 200), 3)
    shade(img, [(95, 1380), (185, 1380), (185, 1500), (95, 1500)], (180, 186, 196), hi=0.4, lo=0.3, inner=0.3, spec=0.3)


def head_hit(img, t, u, sh):
    k = smooth((u - 0.15) / 0.3)
    O.head_section(img, 500, 980, 420, shift=k, bleed=smooth((u - 0.4) / 0.4))


def chest_hit(img, t, u, sh):
    O.lungs(img, 540 + 20 * smooth(u), 940, 280, heart_beat=0.5 + 0.5 * math.sin(t * 12))
    glow(img, 520, 900, 200 * smooth(u), (255, 20, 30), a=0.6)


def flatline(img, t, u, sh):
    import ui
    ui.monitor(img, 160, 1150, 920, 1420, t, hr=0)


def fall_cmp(img, t, u, sh):
    # building with 5 floors and a falling silhouette
    from gfx import shade
    shade(img, [(560, 520), (900, 520), (900, 1560), (560, 1560)], (44, 52, 70), hi=0.2, lo=0.4, inner=0.4, outline=(20, 24, 34, 255), ow=4)
    d = ImageDraw.Draw(img)
    for fl in range(5):
        y = 560 + fl * 200
        for k in range(3):
            d.rectangle((590 + k * 100, y, 650 + k * 100, y + 110), fill=(250, 210, 120, 255) if (fl + k) % 3 else (30, 36, 50, 255))
        label(img, 520, y + 40, f"{5 - fl}", col=(200, 210, 230), size=40, anchor="r", name=TITLE)
    yy = 560 + 960 * smooth(u * 1.1) ** 2
    shade(img, None, (230, 120, 40), ellipse=(420, yy, 36, 60), hi=0.3, lo=0.4, inner=0.3)
    shade(img, None, (236, 184, 150), ellipse=(420, yy - 80, 30, 30), hi=0.3, lo=0.4, inner=0.3)
    stroke_path(img, [(420, 560), (420, 1560)], (255, 255, 255, 60), 3)
    label(img, 300, 1000, "14 М", col=(255, 80, 90), size=70, anchor="c", name=TITLE, stroke=6)


SPEC = dict(
    slug="remen",
    title="Не пристегнулся на заднем",
    caption="«Да тут ехать 5 минут» — сказал он и не пристегнулся сзади… А пострадал не только он 😨 Ты пристёгиваешься на заднем? 👇",
    hashtags="#ремень #дтп #чтобудетесли #симуляция #организм",
    shots=[
        dict(dur=2.2, bg="car_inside", hero=dict(x=500, y=880, s=250, **H(mouth="scream", brows="worried", open=1.25, pupil=0.2, sweat=0.8, arms="up", shake=0.8)),
             draw=[lambda img, t, u, sh: SC.car_inside_fx(img, t, 0.3)], title=["ТЫ НЕ ПРИСТЕГНУЛСЯ", "{НА ЗАДНЕМ}"], fx=dict(red=0.5), cam=dict(z=[(0, 1.12), (1, 1.0)], rot=[(0, -3), (1, 2)]),
             name="hook"),
        dict(dur=1.6, bg="car_inside", hero=dict(x=500, y=880, s=250, **H(mouth="scream", brows="worried", open=1.25, pupil=0.2, sweat=1, arms="up", shake=1.0)),
             draw=[lambda img, t, u, sh: SC.car_inside_fx(img, t, 0.3)], title=["ЧТО БУДЕТ", "С ТЕЛОМ?"], fx=dict(red=0.6), cam=dict(z=[(0, 1.0), (1, 1.1)])),
        dict(dur=2.8, bg="car_inside", hero=dict(x=500, y=940, s=200, **H(mouth="smile", brows="raised", look=(0.4, 0))), draw=[lambda img, t, u, sh: SC.car_inside_fx(img, t, 1.0)], front=[no_belt],
             title=["«ДА ТУТ ЕХАТЬ", "{5 МИНУТ}»"], sub="Даня, 19, заднее сиденье", hud=dict(time=("60", "КМ/Ч"), hr=(78, ""), v=("НЕТ", "РЕМЕНЬ")),
             callouts=[(0.4, (140, 1430), (380, 1450), "РЕМЕНЬ НЕ ПРИСТЁГНУТ", (255, 90, 90))], cam=dict(z=[(0, 1.0), (1, 1.06)])),
        dict(dur=2.8, bg="studio:blue", draw=[car(speed=1.0)], title=["ДРУГ ЗА РУЛЁМ", "[ПРИСТЕГНУТ]"], sub="а Даня — нет",
             callouts=[(0.3, (560, 990), (800, 680), "РЕМЕНЬ", (255, 210, 80)), (0.5, (334, 960), (160, 680), "БЕЗ РЕМНЯ", (255, 90, 90))], cam=dict(z=[(0, 1.0), (1, 1.05)])),
        dict(dur=2.6, bg="studio:blue", draw=[car(speed=0.4, pole=[(0, 1300), (1, 1010)])], title=["ЗАНОС.", "{ВПЕРЕДИ СТОЛБ}"], sub="время замедлено ×1000",
             hud=dict(time=("0,000 С", "ДО УДАРА"), hr=(120, ""), v=("НЕТ", "РЕМЕНЬ")), fx=dict(shake=0.15), cam=dict(z=[(0, 1.0), (1, 1.12)])),
        dict(dur=2.8, bg="studio:blue", draw=[car(crash=[(0, 0), (0.3, 1.0)], speed=0.0, pole=1000)], title=["0,02 СЕКУНДЫ:", "{МАШИНА ВСТАЛА}"], sub="а тело всё ещё летит 60 км/ч",
             hud=dict(time=("0,02 С", "ПОСЛЕ УДАРА"), hr=(124, "")), fx=dict(flash=[(0.1, 0.9, (255, 255, 255))], hits=[(0.1, 1.6)]), cam=dict(z=[(0, 1.15), (1, 1.05)]), name="crash"),
        dict(dur=2.8, bg="studio:blue", draw=[car(crash=1.0, fly=[(0, 0), (1, 0.55)], speed=0.0, pole=1000)], title=["ВОДИТЕЛЯ", "[ДЕРЖИТ РЕМЕНЬ]"], sub="Даню не держит ничего",
             hud=dict(time=("0,05 С", "ПОСЛЕ УДАРА")), callouts=[(0.3, (560, 990), (800, 680), "ПОЯС УДЕРЖАЛ", (255, 210, 80))], cam=dict(z=[(0, 1.05), (1, 1.25)], c=(600, 1000))),
        dict(dur=2.6, bg="studio:blue", draw=[fall_cmp], title=["КАК УПАСТЬ", "{С 5 ЭТАЖА}"], sub="удар на 60 км/ч ≈ падение с 14 метров", cam=dict(z=[(0, 1.0), (1, 1.06)])),
        dict(dur=2.8, bg="studio:red", draw=[car(crash=1.0, fly=[(0, 0.55), (0.3, 0.95), (1, 1.0)], speed=0.0, pole=1000, lean=[(0, 0), (0.3, 1.0)])],
             title=["ОН ВРЕЗАЕТСЯ", "{В СПИНУ ВОДИТЕЛЯ}"], sub="с силой в десятки раз больше своего веса", hud=dict(time=("0,07 С", "ПОСЛЕ УДАРА"), hr=(130, "")),
             fx=dict(flash=[(0.3, 0.9)], hits=[(0.3, 1.8)], red=0.4), cam=dict(z=[(0, 1.25), (1, 1.35)], c=(600, 1000)), name="back"),
        dict(dur=2.8, bg="studio:teal", draw=[head_hit], title=["МОЗГ БЬЁТСЯ", "{О ЧЕРЕП}"], sub="голова встала — а мозг ещё летит", hud=dict(time=("0,1 С", "ПОСЛЕ УДАРА")),
             callouts=[(0.5, (780, 800), (800, 1420), "УШИБ МОЗГА", (255, 90, 90))], fx=dict(hits=[(0.45, 1.0)]), cam=dict(z=[(0, 1.0), (1, 1.1)])),
        dict(dur=2.8, bg="studio:red", draw=[chest_hit], title=["ОРГАНЫ", "[ЛЕТЯТ ДАЛЬШЕ]"], sub="внутри груди рвутся сосуды", hud=dict(time=("0,12 С", "ПОСЛЕ УДАРА")),
             fx=dict(red=0.5, tint=0.2), cam=dict(z=[(0, 1.0), (1, 1.12)])),
        dict(dur=2.8, bg="studio:blue", draw=[car(crash=1.0, fly=1.0, speed=0.0, pole=1000, lean=1.0, alarm=True)], title=["ТИШИНА"], sub="мигает аварийка… из салона ни звука",
             hud=dict(time=("1 С", "ПОСЛЕ УДАРА"), hr=(60, "")), fx=dict(tint=0.25, dark=0.2), cam=dict(z=[(0, 1.0), (1, 1.08)]), soft_cut=True, name="silence"),
        dict(dur=3.0, bg="ward", hero=dict(x=560, y=900, s=220, **H(outfit="gown", mouth="slack", closed=True, pale=0.3, bags=0.6)),
             front=[lambda img, t, u, sh: PR.oxygen_mask(img, 560, 900, 220, t)], title=["ДАНЯ", "{ВЫЖИЛ}"], sub="переломы и ушиб мозга",
             hud=dict(time=("+1 ДЕНЬ", "СПУСТЯ"), hr=(96, ""), v=("КОМА", "СОЗНАНИЕ")), cam=dict(z=[(0, 1.0), (1, 1.06)])),
        dict(dur=3.2, bg="ward", hero=dict(x=540, y=860, s=230, **DRV, mouth="slack", closed=True, pale=0.9, blue=0.4), draw=[flatline],
             title=["А ВОДИТЕЛЬ —", "{НЕТ}"], sub="его убил удар сзади, а не столб", hud=dict(time=("+1 ДЕНЬ", "СПУСТЯ"), hr=(0, ""), v=("—", "")),
             fx=dict(gray=0.6, tint=0.15), cam=dict(z=[(0, 1.0), (1, 1.1)]), name="twist"),
        dict(dur=2.8, kind="fact", fact=dict(page=(1, 5), tag="исследование", title=["РИСК ДЛЯ ВОДИТЕЛЯ"], big="×5", size=260, unit="если сзади не пристёгнуты", line="The Lancet, 2002")),
        dict(dur=2.8, kind="fact", fact=dict(page=(2, 5), tag="впереди", title=["РЕМЕНЬ СНИЖАЕТ РИСК"], big="ДО 50%", size=190, unit="гибели", line="данные ВОЗ")),
        dict(dur=2.8, kind="fact", fact=dict(page=(3, 5), tag="сзади", title=["И НА ЗАДНЕМ ТОЖЕ"], big="ДО 25%", size=190, unit="меньше смертей", line="данные ВОЗ")),
        dict(dur=2.8, kind="fact", fact=dict(page=(4, 5), tag="физика", title=["60 КМ/Ч БЕЗ РЕМНЯ"], big="14 М", size=230, unit="высота падения", line="≈ пятый этаж")),
        dict(dur=3.0, kind="fact", fact=dict(page=(5, 5), tag="что делать", title=["СЕЛ НАЗАД?"], big="ЩЁЛК", size=200, unit="пристегнись", line="даже если ехать 5 минут")),
        dict(dur=1.6, bg="car_inside", hero=dict(x=500, y=880, s=250, **H(mouth="scream", brows="worried", open=1.25, pupil=0.2, sweat=0.8, arms="up", shake=0.8)),
             draw=[lambda img, t, u, sh: SC.car_inside_fx(img, t, 0.3)], title=["ТЫ НЕ ПРИСТЕГНУЛСЯ", "{НА ЗАДНЕМ}"], fx=dict(red=0.5), cam=dict(z=[(0, 1.0), (1, 1.12)]),
             soft_cut=True, no_hud=True, name="loop"),
    ],
    music=dict(bpm=124, drop="crash", calm=["silence", "twist"], key=1, prog=[0, 0, 3, -2]),
    sfx=[(("hook", 0.1), "scream", dict(dur=1.4, g=0.32)), (("crash", 0.1), "crunch", dict(dur=0.6, g=0.8)), (("crash", 0.12), "glass", dict(g=0.6)),
         (("back", 0.3), "slam", dict(g=0.7)), (("back", 0.32), "crunch", dict(dur=0.3, g=0.5)), (("twist", 0.2), "flatline", dict(dur=2.8, g=0.12)),
         (("silence", 0.3), "beeps", dict(n=5, every=0.5, f=880, g=0.12))],
)
