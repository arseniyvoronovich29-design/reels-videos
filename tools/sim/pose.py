"""Pose (skinning) for the front-view anatomy figure. All drawing goes through a
transform T(x, y); wrap it with pose_fn(params) to bend limbs and move the body."""
import math
import numpy as np
import anatomy as A

S_R, E_R, W_R = (0.112, 0.196), (0.145, 0.362), (0.176, 0.484)
H_R, K_R, AN_R = (0.052, 0.49), (0.050, 0.72), (0.042, 0.955)
_tor = sorted([(y, x) for x, y in A.TORSO_R[:-1]])


def torso_hw(y):
    ys = [p[0] for p in _tor]
    xs = [p[1] for p in _tor]
    return float(np.interp(y, ys, xs))


def rot(p, c, a):
    ca, sa = math.cos(a), math.sin(a)
    dx, dy = p[0] - c[0], p[1] - c[1]
    return (c[0] + dx * ca - dy * sa, c[1] + dx * sa + dy * ca)


def smooth(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def proj(p, a, b):
    vx, vy = b[0] - a[0], b[1] - a[1]
    L2 = vx * vx + vy * vy
    return ((p[0] - a[0]) * vx + (p[1] - a[1]) * vy) / L2


def seg_dist(p, a, b):
    t = max(0.0, min(1.0, proj(p, a, b)))
    q = (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
    return math.hypot(p[0] - q[0], p[1] - q[1])


def make_pose(pp):
    """pp: dict with arm_a_r, arm_b_r, arm_a_l, arm_b_l, leg_a_r, leg_b_r, leg_a_l, leg_b_l (radians),
    rot (global, radians), cx, cy (rotation centre), dx, dy (translation, body units)."""
    g = pp.get

    def f(x, y):
        p = (x, y)
        s = 1 if x > 0 else -1
        ax = abs(x)
        out = p
        # arm region
        Sh = (s * S_R[0], S_R[1])
        El = (s * E_R[0], E_R[1])
        Wr = (s * W_R[0], W_R[1])
        Tip = (s * 0.19, 0.585)
        darm = min(seg_dist(p, Sh, El), seg_dist(p, El, Wr), seg_dist(p, Wr, Tip))
        if 0.16 < y < 0.64 and darm < 0.034 and ax > torso_hw(y) - 0.025 and not (y > 0.47 and ax < 0.12):
            a = -s * g(f"arm_a_{'r' if s > 0 else 'l'}", 0.0)
            b = s * g(f"arm_b_{'r' if s > 0 else 'l'}", 0.0)
            t = proj(p, Sh, El)
            sc = g(f"arm_s_{'r' if s > 0 else 'l'}", 1.0)
            Els = (Sh[0] + (El[0] - Sh[0]) * sc, Sh[1] + (El[1] - Sh[1]) * sc)
            pu = (Sh[0] + (p[0] - Sh[0]) * sc, Sh[1] + (p[1] - Sh[1]) * sc) if t < 1 else (p[0] + Els[0] - El[0], p[1] + Els[1] - El[1])
            pf_ = (p[0] + Els[0] - El[0], p[1] + Els[1] - El[1])
            up = rot(pu, Sh, a)
            El2 = rot(Els, Sh, a)
            fo = rot(rot(pf_, Sh, a), El2, b)
            wfo = smooth((t - 0.88) / 0.24)
            q = (up[0] * (1 - wfo) + fo[0] * wfo, up[1] * (1 - wfo) + fo[1] * wfo)
            dsh = math.hypot(x - Sh[0], y - Sh[1])
            wsh = smooth((dsh - 0.015) / 0.04) if t < 0.3 else 1.0
            out = (p[0] * (1 - wsh) + q[0] * wsh, p[1] * (1 - wsh) + q[1] * wsh)
        elif y > 0.47 and ax > 0.004:
            Hp = (s * H_R[0], H_R[1])
            Kn = (s * K_R[0], K_R[1])
            a = -s * g(f"leg_a_{'r' if s > 0 else 'l'}", 0.0)
            b = s * g(f"leg_b_{'r' if s > 0 else 'l'}", 0.0)
            th = rot(p, Hp, a)
            K2 = rot(Kn, Hp, a)
            sh = rot(th, K2, b)
            w = smooth((y - (K_R[1] - 0.03)) / 0.06)
            q = (th[0] * (1 - w) + sh[0] * w, th[1] * (1 - w) + sh[1] * w)
            wh = smooth((y - 0.47) / 0.06)
            out = (p[0] * (1 - wh) + q[0] * wh, p[1] * (1 - wh) + q[1] * wh)
        return glob(out)

    def glob(out):
        G = g("rot", 0.0)
        if G:
            out = rot(out, (g("cx", 0.0), g("cy", 0.5)), G)
        return (out[0] + g("dx", 0.0), out[1] + g("dy", 0.0))

    def chain(pts, root, mid, a, b, nmid, sc=1.0):
        out = []
        mids = (root[0] + (mid[0] - root[0]) * sc, root[1] + (mid[1] - root[1]) * sc)
        mid2 = rot(mids, root, a)
        for i, p in enumerate(pts):
            if i <= nmid:
                p = (root[0] + (p[0] - root[0]) * sc, root[1] + (p[1] - root[1]) * sc)
            else:
                p = (p[0] + mids[0] - mid[0], p[1] + mids[1] - mid[1])
            q = rot(p, root, a)
            if i > nmid:
                q = rot(q, mid2, b)
            out.append(q)
        return out

    chains = {}
    for s, sd in ((1, "r"), (-1, "l")):
        arm = [(s * x, y) for x, y in A.ARM_C]
        chains["arm_" + sd] = chain(arm, (s * S_R[0], S_R[1]), (s * E_R[0], E_R[1]), -s * g("arm_a_" + sd, 0.0), s * g("arm_b_" + sd, 0.0), 2, g("arm_s_" + sd, 1.0))
        leg = [(s * x, y) for x, y in A.LEG_C]
        chains["leg_" + sd] = chain(leg, (s * H_R[0], H_R[1]), (s * K_R[0], K_R[1]), -s * g("leg_a_" + sd, 0.0), s * g("leg_b_" + sd, 0.0), 2)
    f.glob = glob
    f.chains = chains
    return f
