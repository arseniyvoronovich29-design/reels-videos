"""Anatomical front-view figure. Body units: height = 1, x from midline
(+x = viewer's right = patient's LEFT), y from top of head down."""
import math
import numpy as np
from PIL import Image, ImageDraw


def catmull(pts, closed=True, n=10):
    P = list(pts)
    m = len(P)
    out = []
    rng = range(m) if closed else range(m - 1)
    for i in rng:
        p0 = P[(i - 1) % m] if closed else P[max(i - 1, 0)]
        p1 = P[i]
        p2 = P[(i + 1) % m] if closed else P[min(i + 1, m - 1)]
        p3 = P[(i + 2) % m] if closed else P[min(i + 2, m - 1)]
        for k in range(n):
            t = k / n
            t2, t3 = t * t, t * t * t
            x = 0.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * t + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2 + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3)
            y = 0.5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * t + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2 + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)
            out.append((x, y))
    if not closed:
        out.append(P[-1])
    return out


def box(a, b):
    return (min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1]))


def mirror(pts):
    return [(-x, y) for x, y in pts]


def limb_poly(center, widths, n=8):
    c = catmull(center, closed=False, n=n)
    wc = []
    seg = len(center) - 1
    for i in range(len(c)):
        f = i / (len(c) - 1) * seg
        k = min(int(f), seg - 1)
        r = f - k
        wc.append(widths[k] * (1 - r) + widths[k + 1] * r)
    left, right = [], []
    for i, (x, y) in enumerate(c):
        a = c[max(i - 1, 0)]
        b = c[min(i + 1, len(c) - 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        h = wc[i] / 2
        left.append((x + nx * h, y + ny * h))
        right.append((x - nx * h, y - ny * h))
    tip = c[-1]
    return left + [tip] + right[::-1], c


# ---------------- silhouette ----------------
HEAD_R = [(0.0, 0.0), (0.026, 0.006), (0.042, 0.022), (0.047, 0.05), (0.045, 0.08), (0.039, 0.10),
          (0.030, 0.118), (0.016, 0.130), (0.0, 0.134)]
HEAD = catmull(HEAD_R[:-1] + [(0.0, 0.134)] + mirror(HEAD_R[1:-1])[::-1], n=8)
EARS = [(-0.049, 0.072, 0.007, 0.016), (0.049, 0.072, 0.007, 0.016)]
NECK = [(-0.026, 0.115), (0.026, 0.115), (0.029, 0.17), (-0.029, 0.17)]

TORSO_R = [(0.029, 0.162), (0.066, 0.173), (0.100, 0.182), (0.118, 0.198), (0.112, 0.232),
           (0.098, 0.248), (0.097, 0.28), (0.089, 0.33), (0.082, 0.37), (0.086, 0.41),
           (0.097, 0.455), (0.099, 0.497), (0.03, 0.512)]
TORSO = catmull(TORSO_R + [(0.0, 0.516)] + mirror(TORSO_R)[::-1], n=6)

ARM_C = [(0.112, 0.196), (0.128, 0.262), (0.145, 0.362), (0.160, 0.42), (0.176, 0.484), (0.183, 0.53), (0.188, 0.578)]
ARM_W = [0.050, 0.044, 0.034, 0.036, 0.025, 0.034, 0.024]
LEG_C = [(0.052, 0.49), (0.055, 0.60), (0.050, 0.72), (0.047, 0.80), (0.042, 0.955), (0.050, 0.995)]
LEG_W = [0.090, 0.070, 0.046, 0.052, 0.028, 0.034]
ARM_R, ARM_RC = limb_poly(ARM_C, ARM_W)
LEG_R, LEG_RC = limb_poly(LEG_C, LEG_W)
ARM_L, LEG_L = mirror(ARM_R), mirror(LEG_R)

# ---------------- skeleton hints ----------------
CLAV_R = [(0.010, 0.190), (0.050, 0.186), (0.085, 0.180), (0.108, 0.184)]
RIBS = []
for i in range(10):
    y0 = 0.200 + i * 0.0105
    sx = 0.013 if i < 7 else 0.013 + (i - 6) * 0.012
    sy = y0 if i < 7 else 0.305 + (i - 7) * 0.012
    RIBS.append([(sx, sy), (0.05, y0 + 0.006 + i * 0.0012), (0.080, y0 + 0.02 + i * 0.002), (0.089, y0 + 0.045 + i * 0.002)])
STERNUM = [(-0.008, 0.192), (0.008, 0.192), (0.007, 0.300), (0.0, 0.308), (-0.007, 0.300)]
PELVIS_R = [(0.012, 0.495), (0.035, 0.47), (0.065, 0.435), (0.085, 0.425), (0.090, 0.45), (0.072, 0.48), (0.055, 0.50), (0.030, 0.505)]

# ---------------- organs ----------------
BRAIN = catmull([(0.0, 0.010), (0.025, 0.014), (0.039, 0.030), (0.042, 0.055), (0.036, 0.080), (0.020, 0.088),
                 (0.0, 0.085), (-0.020, 0.088), (-0.036, 0.080), (-0.042, 0.055), (-0.039, 0.030), (-0.025, 0.014)], n=8)
LUNG_R = catmull([(-0.030, 0.170), (-0.018, 0.178), (-0.012, 0.20), (-0.010, 0.24), (-0.013, 0.28), (-0.021, 0.305),
                  (-0.042, 0.312), (-0.062, 0.322), (-0.079, 0.337), (-0.087, 0.343), (-0.089, 0.31), (-0.088, 0.27),
                  (-0.083, 0.23), (-0.071, 0.198), (-0.052, 0.178)], n=6)
LUNG_L = catmull([(0.030, 0.172), (0.018, 0.180), (0.013, 0.20), (0.012, 0.235), (0.022, 0.255), (0.038, 0.272),
                  (0.046, 0.292), (0.041, 0.306), (0.052, 0.320), (0.069, 0.333), (0.085, 0.350), (0.089, 0.31),
                  (0.088, 0.27), (0.083, 0.23), (0.071, 0.198), (0.052, 0.18)], n=6)
FISSURES = [[(-0.013, 0.255), (-0.05, 0.257), (-0.087, 0.262)],
            [(-0.040, 0.312), (-0.065, 0.29), (-0.088, 0.268)],
            [(0.045, 0.316), (0.068, 0.29), (0.088, 0.262)]]
HEART = catmull([(-0.016, 0.244), (-0.021, 0.265), (-0.019, 0.290), (-0.008, 0.301), (0.015, 0.306),
                 (0.036, 0.311), (0.053, 0.313), (0.051, 0.294), (0.043, 0.270), (0.031, 0.250),
                 (0.017, 0.240), (0.002, 0.237)], n=6)
HEART_C = (0.016, 0.276)
LIVER = catmull([(-0.088, 0.332), (-0.071, 0.317), (-0.041, 0.311), (-0.010, 0.308), (0.020, 0.309), (0.045, 0.316),
                 (0.050, 0.325), (0.022, 0.336), (-0.010, 0.347), (-0.040, 0.358), (-0.070, 0.370), (-0.087, 0.366)], n=6)
GALL = (-0.042, 0.353, 0.008, 0.012)
STOMACH = catmull([(0.030, 0.320), (0.055, 0.316), (0.073, 0.327), (0.076, 0.346), (0.069, 0.369), (0.051, 0.386),
                   (0.026, 0.391), (0.006, 0.384), (-0.009, 0.372), (0.002, 0.364), (0.020, 0.372),
                   (0.040, 0.369), (0.050, 0.355), (0.048, 0.338), (0.036, 0.330)], n=6)
SPLEEN = (0.080, 0.338, 0.010, 0.020)
KIDNEYS = [(-0.036, 0.398, 0.012, 0.019), (0.036, 0.388, 0.012, 0.019)]
COLON = [(-0.048, 0.468), (-0.060, 0.445), (-0.063, 0.405), (-0.055, 0.388), (-0.030, 0.392), (0.0, 0.402),
         (0.030, 0.394), (0.062, 0.374), (0.068, 0.40), (0.066, 0.455), (0.045, 0.476), (0.015, 0.484), (0.002, 0.497)]
SMALL_INT = catmull([(-0.045, 0.405), (0.0, 0.410), (0.052, 0.402), (0.055, 0.445), (0.040, 0.468),
                     (0.0, 0.474), (-0.040, 0.462), (-0.050, 0.435)], n=6)
BLADDER = (0.0, 0.492, 0.016, 0.011)
SI_PATH = []
_rows = 6
for _i in range(_rows):
    _y = 0.414 + _i * 0.0105
    _xs = [-0.040, -0.020, 0.0, 0.020, 0.042]
    if _i % 2:
        _xs = _xs[::-1]
    for _j, _x in enumerate(_xs):
        SI_PATH.append((_x + 0.003 * math.sin(_i * 2 + _j), _y + 0.003 * math.sin(_j * 1.9 + _i)))


def tube(od, P, center, w, col, edge, s, haustra=False):
    poly, c = limb_poly(center, [w] * len(center), n=8)
    ew = max(1, int(s * 0.0022))
    od.polygon(P(poly), fill=col + (245,), outline=edge + (255,))
    if haustra:
        for i in range(4, len(c) - 2, 5):
            a = c[i - 1]; b = c[i + 1]
            dx, dy = b[0] - a[0], b[1] - a[1]
            L = math.hypot(dx, dy) or 1
            nx, ny = -dy / L * w / 2, dx / L * w / 2
            od.line(P([(c[i][0] + nx, c[i][1] + ny), (c[i][0] - nx, c[i][1] - ny)]), fill=edge + (200,), width=ew)

TRACHEA = [(0.0, 0.142), (0.0, 0.228)]
BRONCHI = [[(0.0, 0.228), (-0.028, 0.247)], [(0.0, 0.228), (0.030, 0.244)]]

# vessels (arteries red, veins blue); limb flags for vasoconstriction
AORTA = [(0.000, 0.242), (-0.002, 0.224), (0.003, 0.212), (0.013, 0.209), (0.019, 0.218), (0.018, 0.240), (0.015, 0.30), (0.011, 0.37), (0.007, 0.432)]
BRACHIO = [(0.004, 0.212), (-0.008, 0.196), (-0.014, 0.185)]
VCAVA = [(-0.013, 0.200), (-0.014, 0.244)]
CAROTIDS = [[(0.010, 0.212), (0.016, 0.17), (0.020, 0.12)], [(0.006, 0.212), (-0.016, 0.17), (-0.020, 0.12)]]
ILIAC_R = [(0.006, 0.432), (0.035, 0.47), (0.052, 0.51), (0.050, 0.62), (0.042, 0.72), (0.044, 0.80), (0.040, 0.95)]
ILIAC_L = mirror(ILIAC_R)
ARM_ART_R = [(0.014, 0.208), (0.06, 0.196), (0.110, 0.205), (0.128, 0.27), (0.143, 0.362), (0.158, 0.42), (0.172, 0.484), (0.180, 0.53)]
ARM_ART_L = mirror(ARM_ART_R)
ARM_ART_L[0] = (0.006, 0.212)
ARM_VEIN_R = [(0.115, 0.215), (0.134, 0.28), (0.152, 0.362), (0.168, 0.42), (0.182, 0.484)]
ARM_VEIN_L = mirror(ARM_VEIN_R)
LEG_VEIN_R = [(0.060, 0.52), (0.062, 0.62), (0.054, 0.72), (0.052, 0.80), (0.046, 0.95)]
LEG_VEIN_L = mirror(LEG_VEIN_R)

WARM = np.array([238, 104, 76], np.float32)
MID = np.array([196, 140, 196], np.float32)
COLD = np.array([70, 150, 240], np.float32)


def thermal(c):
    c = max(0.0, min(1.0, c))
    if c < 0.5:
        v = WARM * (1 - c * 2) + MID * (c * 2)
    else:
        v = MID * (1 - (c - 0.5) * 2) + COLD * ((c - 0.5) * 2)
    return tuple(int(x) for x in v)


def mixc(a, b, k):
    return tuple(int(a[i] * (1 - k) + b[i] * k) for i in range(3))


def scale_pts(pts, cx, cy, sx, sy):
    return [(cx + (x - cx) * sx, cy + (y - cy) * sy) for x, y in pts]


def draw_figure(size, T, state):
    """T: function (bx,by)->(px,py) in canvas pixels; s: pixels per body unit.
    state keys: core (0..1 coldness), limb (0..1), breath (lung scale), beat (heart scale),
    vessel (limb vessel alpha 0..1), brain (0..1 dim), arm_focus (0..1 muscle highlight),
    body_alpha"""
    s = state["s"]
    W, H = size
    body = Image.new("RGBA", size, (0, 0, 0, 0))
    bd = ImageDraw.Draw(body)
    P = lambda pts: [T(x, y) for x, y in pts]
    core_c = state["skin"] if "skin" in state else thermal(state["core"])
    # limbs with gradient (colder toward tips): draw segments root->tip
    for poly_pts, cen, w in [(ARM_C, None, ARM_W), (LEG_C, None, LEG_W)]:
        pass
    TL = state.get("T_limb", T)
    TB = state.get("T_body", T)
    PL = lambda pts: [TL(x, y) for x, y in pts]
    PB = lambda pts: [TB(x, y) for x, y in pts]
    chains = state.get("chains", {})

    def limb_grad(center, widths, mirror_side, key):
        cpts = chains.get(key) or (center if mirror_side > 0 else mirror(center))
        poly, c = limb_poly(cpts, widths, n=10)
        nseg = len(c) - 1
        left = poly[:nseg + 1]
        right = poly[nseg + 2:][::-1]
        col = core_c
        for i in range(nseg):
            frac = i / nseg
            k = state["limb"] * 1.5 - (1 - frac) * 0.55
            col = core_c if "skin" in state else mixc(core_c, thermal(max(state["core"], state["limb"])), max(0, min(1, k + 0.3 * state["limb"])))
            quad = [left[i], left[i + 1], right[i + 1], right[i]]
            bd.polygon(PL(quad), fill=col + (255,))
        tip = poly[nseg + 1]
        bd.polygon(PL([left[-1], tip, right[-1]]), fill=col + (255,))
        tx, ty = c[-1]
        rr_ = widths[-1] * 0.55
        a_, b_ = TL(tx - rr_, ty - rr_ * 1.2), TL(tx + rr_, ty + rr_ * 0.6)
        bd.ellipse(box(a_, b_), fill=col + (255,))
        # rounded joints (shoulder/hip, elbow/knee) so bends never show gaps or webs
        for j, rj in ((0, widths[0] * 0.5), (2, widths[2] * 0.52)):
            jx, jy = cpts[j]
            p0 = TL(jx, jy)
            p1 = TL(jx + rj, jy)
            r = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
            bd.ellipse((p0[0] - r, p0[1] - r, p0[0] + r, p0[1] + r), fill=core_c + (255,))
    for side in (1, -1):
        sd = "r" if side > 0 else "l"
        limb_grad(LEG_C, LEG_W, side, "leg_" + sd)
        limb_grad(ARM_C, state.get("arm_w_r", ARM_W) if side > 0 else ARM_W, side, "arm_" + sd)
    bd.polygon(PB(TORSO), fill=core_c + (255,))
    if state.get("chest_swell", 0) > 0:
        cs = state["chest_swell"]
        bd.polygon(PB(catmull([(0.06, 0.20), (0.10 + 0.03 * cs, 0.205), (0.112 + 0.035 * cs, 0.25), (0.10 + 0.02 * cs, 0.30), (0.07, 0.28)], closed=True, n=6)), fill=core_c + (255,))
    bd.polygon(PB(NECK), fill=core_c + (255,))
    bd.polygon(PB(HEAD), fill=core_c + (255,))
    for ex, ey, rx, ry in EARS:
        a, b = T(ex - rx, ey - ry), T(ex + rx, ey + ry)
        bd.ellipse(box(a, b), fill=core_c + (255,))
    # translucency + outline
    arr = np.asarray(body).copy()
    mask = arr[..., 3] > 0
    er = mask.copy()
    k = max(2, int(s * 0.0022))
    for dx, dy in [(k, 0), (-k, 0), (0, k), (0, -k)]:
        er &= np.roll(np.roll(mask, dy, 0), dx, 1)
    edge = mask & ~er
    arr[..., 3] = np.where(mask, int(255 * state.get("body_alpha", 0.42)), 0)
    arr[edge] = (220, 240, 255, 235)
    body = Image.fromarray(arr, "RGBA")

    org = Image.new("RGBA", size, (0, 0, 0, 0))
    od = ImageDraw.Draw(org)
    lw = lambda f: max(1, int(s * f))
    # skeleton hints
    bone = (235, 240, 250, 70)
    for side in (1, -1):
        cl = CLAV_R if side > 0 else mirror(CLAV_R)
        od.line(P(catmull(cl, closed=False)), fill=(235, 240, 250, 120), width=lw(0.006), joint="curve")
        for r in RIBS:
            rr = r if side > 0 else mirror(r)
            od.line(P(catmull(rr, closed=False)), fill=bone, width=lw(0.0035), joint="curve")
        pv = PELVIS_R if side > 0 else mirror(PELVIS_R)
        od.line(P(catmull(pv, closed=True)), fill=bone, width=lw(0.004), joint="curve")
    od.polygon(P(STERNUM), fill=(235, 240, 250, 60))
    # vessels
    va = state.get("vessel", 1.0)
    art, vein = (225, 50, 55), (80, 110, 220)
    def vline(pts, col, w, a):
        if a > 0.02:
            od.line(P(catmull(pts, closed=False)), fill=col + (int(255 * a),), width=lw(w), joint="curve")
    vline(AORTA, art, 0.009, 1)
    vline(BRACHIO, art, 0.006, 1)
    vline(VCAVA, vein, 0.009, 1)
    for c_ in CAROTIDS:
        vline(c_, art, 0.004, 1)
    for pts in (ILIAC_R, ILIAC_L, ARM_ART_R, ARM_ART_L):
        vline(pts[:3], art, 0.005, 1)
        vline(pts[2:], art, 0.004, va)
    for pts in (ARM_VEIN_R, ARM_VEIN_L, LEG_VEIN_R, LEG_VEIN_L):
        vline(pts, vein, 0.0035, va * 0.9)
    # arm muscle highlight
    af = state.get("arm_focus", 0)
    if af > 0.01:
        mc = mixc((205, 70, 80), (90, 150, 230), state["limb"])
        for side in (1, -1):
            fore = [(0.150, 0.385), (0.170, 0.44), (0.177, 0.478)]
            fore = fore if side > 0 else mirror(fore)
            od.line(P(fore), fill=mc + (int(200 * af),), width=lw(0.026), joint="curve")
            up = [(0.120, 0.215), (0.133, 0.28), (0.142, 0.345)]
            up = up if side > 0 else mirror(up)
            od.line(P(up), fill=mc + (int(200 * af),), width=lw(0.032), joint="curve")
    # abdominal organs (back to front)
    for kx, ky, rx, ry in KIDNEYS:
        a, b = T(kx - rx, ky - ry), T(kx + rx, ky + ry)
        od.ellipse(box(a, b), fill=(150, 55, 60, 150))
    a, b = T(SPLEEN[0] - SPLEEN[2], SPLEEN[1] - SPLEEN[3]), T(SPLEEN[0] + SPLEEN[2], SPLEEN[1] + SPLEEN[3])
    od.ellipse(box(a, b), fill=(128, 48, 74, 230))
    tube(od, P, SI_PATH, 0.0115, (224, 164, 150), (176, 108, 100), s)
    tube(od, P, COLON, 0.017, (208, 148, 114), (160, 104, 80), s, haustra=True)
    a, b = T(BLADDER[0] - BLADDER[2], BLADDER[1] - BLADDER[3]), T(BLADDER[0] + BLADDER[2], BLADDER[1] + BLADDER[3])
    od.ellipse(box(a, b), fill=(226, 196, 120, 235))
    od.polygon(P(STOMACH), fill=(226, 158, 140, 245), outline=(250, 200, 185, 255))
    od.polygon(P(LIVER), fill=(146, 52, 44, 245), outline=(190, 90, 80, 255))
    a, b = T(GALL[0] - GALL[2], GALL[1] - GALL[3]), T(GALL[0] + GALL[2], GALL[1] + GALL[3])
    od.ellipse(box(a, b), fill=(96, 140, 64, 250))
    # thorax
    br = state.get("breath", 1.0)
    lr = scale_pts(LUNG_R, -0.05, 0.17, 1 + (br - 1) * 0.35, br)
    ll = scale_pts(LUNG_L, 0.05, 0.17, 1 + (br - 1) * 0.35, br)
    lcol = state.get("lung_col", (232, 142, 152))
    od.polygon(P(lr), fill=lcol + (230,), outline=(255, 190, 200, 255))
    od.polygon(P(ll), fill=lcol + (230,), outline=(255, 190, 200, 255))
    for f in FISSURES:
        ff = scale_pts(f, -0.05 if f[0][0] < 0 else 0.05, 0.17, 1 + (br - 1) * 0.35, br)
        od.line(P(catmull(ff, closed=False)), fill=(170, 80, 95, 220), width=lw(0.0025), joint="curve")
    od.line(P(TRACHEA), fill=(232, 222, 212, 240), width=lw(0.011))
    for bz in BRONCHI:
        od.line(P(bz), fill=(232, 222, 212, 240), width=lw(0.007))
    bt = state.get("beat", 1.0)
    hp = scale_pts(HEART, HEART_C[0], HEART_C[1], bt, bt)
    hcol = state.get("heart_col", (200, 36, 48))
    od.polygon(P(hp), fill=hcol + (250,), outline=(255, 120, 120, 255))
    if state.get("no_brain"):
        for side in (1, -1):
            for r in RIBS[:7]:
                rr = r if side > 0 else mirror(r)
                od.line(P(catmull(rr, closed=False)), fill=(240, 244, 252, 34), width=lw(0.0026), joint="curve")
        return body, org
    # brain
    dim = state.get("brain", 0.0)
    bcol = mixc((236, 176, 178), (120, 130, 160), dim)
    od.polygon(P(BRAIN), fill=bcol + (240,), outline=(255, 215, 215, 255))
    for i in range(7):
        y = 0.022 + i * 0.0095
        wv = [(-0.034 + j * 0.0068, y + 0.0035 * math.sin(j * 2.1 + i * 1.3)) for j in range(11)]
        od.line(P(wv), fill=mixc((196, 120, 128), (90, 100, 130), dim) + (220,), width=lw(0.0022), joint="curve")
    od.line(P([(0, 0.012), (0, 0.084)]), fill=mixc((196, 120, 128), (90, 100, 130), dim) + (230,), width=lw(0.0028))
    for side in (1, -1):
        for r in RIBS[:7]:
            rr = r if side > 0 else mirror(r)
            od.line(P(catmull(rr, closed=False)), fill=(240, 244, 252, 34), width=lw(0.0026), joint="curve")
    return body, org
