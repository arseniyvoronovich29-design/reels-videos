"""Soundtrack builder. build(E, wav_path) where E is the loaded engine module (E.S = spec, E.SHOTS).

Spec keys used:
  shots[i]["amb"]     ambience bed: forest kitchen sea beach bedroom fire street office hospital night underwater inside none
                      (default: from the shot preset; dark/xray/micro/face -> drone only)
  shots[i]["red"]     0..1, also drives the dread drone level
  shots[i]["riser"]   True -> Shepard riser over the shot
  shots[i]["hb"]      heartbeat gain (default 0.65)
  shots[i]["muffle"]  0..1 low-pass the whole mix during the shot (fading consciousness)
  S["sfx"]            list of (time, type, kwargs); time is seconds or ("shot name", seconds into that shot)
                      types: scream groan gasp breath thud crunch slam beeps alarm siren splash fire cough sob
                             whoosh boom drip zap bubble heartbeat_skip
"""
import math, wave
import numpy as np
from _sfx_lib import *          # noqa: F401,F403
import _sfx_lib as X


def build(E, path):
    S = E.S
    DUR = S["T_END"]
    N = int(SR * DUR)
    t = np.arange(N) / SR
    L = np.zeros(N)
    R = np.zeros(N)
    rng = np.random.default_rng(S.get("seed", 5))
    X.rng = rng

    def put(t0, sig, g=1.0, pan=0.0):
        i0 = int(t0 * SR)
        n = min(len(sig), N - i0)
        if n > 0 and i0 >= 0:
            L[i0:i0 + n] += sig[:n] * g * (1 - pan)
            R[i0:i0 + n] += sig[:n] * g * (1 + pan)

    def tt_of(spec_t):
        if isinstance(spec_t, (list, tuple)):
            sh = E.shot_named(spec_t[0])
            return sh["t0"] + spec_t[1]
        return float(spec_t)

    def seg_env(shots_mask, fade=0.08):
        pts = [(0, 0)]
        for sh in E.SHOTS:
            v = shots_mask(sh)
            pts += [(sh["t0"] + 1e-3, v), (sh["t1"] - 1e-3, v)]
        pts.append((DUR, pts[-1][1]))
        return np.interp(t, [p[0] for p in pts], [p[1] for p in pts])

    def noise(n):
        return rng.normal(0, 1, n)

    # ---------------- ambience beds ----------------
    def amb_of(sh):
        if "amb" in sh:
            return sh["amb"]
        if sh["kind"] in ("scene", "face"):
            return {"forest": "forest", "kitchen": "kitchen", "sea": "sea", "beach": "beach", "bedroom": "bedroom", "street": "street",
                    "office": "office", "hospital": "hospital", "night": "night"}.get(sh.get("preset", "dark"), "none")
        return "none"

    beds = {}

    def bed(name):
        if name in beds:
            return beds[name]
        if name == "forest":
            x = filt(noise(N), 150, 1200) * 0.3
            for k in np.arange(0.2, DUR, 0.7):
                n = int(0.12 * SR); tt = np.arange(n) / SR
                f0 = rng.uniform(3000, 4300)
                ch = np.sin(2 * np.pi * np.cumsum(f0 + 1200 * np.sin(2 * np.pi * 25 * tt)) / SR) * np.sin(np.pi * tt / 0.12) ** 2
                i = int((k + rng.uniform(0, 0.4)) * SR)
                if i + n < N:
                    x[i:i + n] += ch * 0.25
        elif name == "kitchen":
            x = 0.25 * np.sin(2 * np.pi * 100 * t) * 0.3 + filt(noise(N), 60, 400) * 0.25
            for k in np.arange(0, DUR, 1.0):
                n = int(0.015 * SR)
                i = int(k * SR)
                if i + n < N:
                    x[i:i + n] += filt(noise(n), 2000, 8000) * np.hanning(n) * 0.6
        elif name in ("sea", "beach"):
            sw = 0.6 + 0.4 * np.sin(2 * np.pi * 0.12 * t)
            x = filt(noise(N), 200, 3000) * sw * 0.6
        elif name == "underwater":
            x = filt(noise(N), 40, 300) * 0.8
        elif name == "bedroom":
            x = filt(noise(N), 40, 200) * 0.3
        elif name == "fire":
            x = filt(noise(N), 100, 1500) * 0.5
            for k in range(int(DUR * 14)):
                n = int(0.01 * SR)
                i = int(rng.uniform(0, DUR - 0.02) * SR)
                x[i:i + n] += filt(noise(n), 1500, 8000) * np.hanning(n) * rng.uniform(0.5, 2)
        elif name == "street":
            x = filt(noise(N), 60, 800) * 0.5 + 0.15 * np.sin(2 * np.pi * 80 * t) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.2 * t))
        elif name == "office":
            x = filt(noise(N), 80, 500) * 0.25
            for k in np.arange(0.1, DUR, 0.23):
                if rng.random() < 0.5:
                    n = int(0.02 * SR)
                    i = int(k * SR)
                    if i + n < N:
                        x[i:i + n] += filt(noise(n), 1500, 6000) * np.hanning(n) * 0.5
        elif name == "hospital":
            x = filt(noise(N), 40, 300) * 0.2
            for k in np.arange(0.3, DUR, 1.0):
                n = int(0.1 * SR)
                i = int(k * SR)
                if i + n < N:
                    x[i:i + n] += np.sin(2 * np.pi * 1000 * np.arange(n) / SR) * 0.15
        elif name == "night":
            x = filt(noise(N), 120, 900) * 0.4
            x += np.sin(2 * np.pi * 4300 * t) * (np.sin(2 * np.pi * 15 * t) > 0.5) * (np.sin(2 * np.pi * 0.8 * t) > 0) * 0.03
        elif name == "inside":
            x = filt(noise(N), 30, 180) * 0.5
        else:
            x = np.zeros(N)
        m = np.abs(x).max()
        beds[name] = x / m if m > 0 else x
        return beds[name]

    names = set(amb_of(sh) for sh in E.SHOTS)
    for nm in names:
        if nm == "none":
            continue
        e = seg_env(lambda sh: 1.0 if amb_of(sh) == nm else 0.0)
        b = bed(nm)
        g = {"forest": 0.09, "kitchen": 0.08, "sea": 0.12, "beach": 0.1, "underwater": 0.18, "bedroom": 0.08, "fire": 0.14, "street": 0.1,
             "office": 0.07, "hospital": 0.1, "night": 0.08, "inside": 0.12}.get(nm, 0.08)
        L += b * e * g
        R += np.roll(b, 3000) * e * g

    # ---------------- drone + dissonant cluster ----------------
    dr_e = seg_env(lambda sh: 0.0 if sh["kind"] in ("facts", "fact") else (0.25 + 0.7 * sh.get("red", 0.2)))
    drone = sum(a * np.sin(2 * np.pi * f * t + rng.uniform(0, 6)) for f, a in [(41.2, 1), (41.5, 0.8), (61.7, 0.5), (87.3, 0.3), (98.0, 0.2)])
    drone *= 0.7 + 0.3 * np.sin(2 * np.pi * 0.21 * t)
    L += drone * dr_e * 0.16
    R += drone * dr_e * 0.16
    cl_e = seg_env(lambda sh: max(0.0, sh.get("red", 0.0) - 0.3))
    cl = sum(np.sin(2 * np.pi * f * t + 0.4 * np.sin(2 * np.pi * 4.5 * t)) for f in (523.3, 554.4, 587.3, 622.3))
    cl = filt(cl, 300, 3000) * cl_e
    L += cl * 0.05
    R += cl * 0.05
    # calm pad on facts / black / myth
    pad_e = seg_env(lambda sh: 0.3 if sh["kind"] in ("facts", "black", "myth", "fact") else 0.0)
    pad = sum(np.sin(2 * np.pi * f * t + rng.uniform(0, 6)) for f in (110, 130.8, 164.8))
    pad = filt(pad, 60, 800) * pad_e
    L += pad * 0.05
    R += pad * 0.05

    # ---------------- risers and cuts ----------------
    for sh in E.SHOTS:
        if sh.get("riser"):
            a0, a1 = sh["t0"], sh["t1"]
            n = int((a1 - a0) * SR); tt = np.arange(n) / SR
            sig = np.zeros(n)
            for k in range(5):
                f = 110 * 2 ** ((k + tt / (a1 - a0)) % 5)
                sig += np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-((np.log2(f / 440)) ** 2))
            put(a0, sig * (tt / (a1 - a0)) ** 2, 0.09)
    for k, sh in enumerate(E.SHOTS[1:], 1):
        if sh["kind"] in ("black", "loop"):
            continue
        put(sh["t0"] - 0.25, whoosh(0.32), 0.16, (-1) ** k * 0.3)
        put(sh["t0"], boom(0.6, 46), 0.42)
        if sh["kind"] == "myth":
            u_ = sh["t0"] + 0.38 * (sh["t1"] - sh["t0"])
            put(u_, boom(0.5, 80), 0.7)
            put(u_, crunch(0.12), 0.4)
        if sh["kind"] == "facts":
            dd = sh["t1"] - sh["t0"]
            for j in range(len(S["facts"])):
                x = sh["t0"] + (0.08 + j * 0.11) * dd
                put(x, beep(880 + 110 * j, 0.07), 0.08)
                put(x, whoosh(0.15), 0.1)
            put(sh["t0"] + 0.72 * dd, boom(0.6, 75), 0.75)
            put(sh["t0"] + 0.72 * dd, crunch(0.12), 0.4)
        if sh["kind"] == "black":
            put(sh["t0"] + 0.3 * (sh["t1"] - sh["t0"]) + 0.3, boom(1.0, 38), 0.5)
        if sh["kind"] == "loop":
            put(sh["t0"], boom(1.0, 40), 0.6)
    put(0.0, boom(1.0, 40), 0.8)
    # hits inside shots: boom
    for sh in E.SHOTS:
        for hit in sh.get("hits", []):
            put(sh["t0"] + hit[0], boom(0.7, 50), 0.6 * min(1.5, hit[1]))
    # flatline shots
    for sh in E.SHOTS:
        if sh["kind"] == "flat":
            prev = E.phase_at(sh["t0"])
            flat_t = None
            for k in range(int(sh["t0"] * 200), int(sh["t1"] * 200)):
                x = k / 200
                ph = E.phase_at(x)
                if E.hr_at(x) < 1 and flat_t is None:
                    flat_t = x
                if E.hr_at(x) >= 1 and math.floor(ph - 0.26) > math.floor(prev - 0.26):
                    put(x, beep(1000, 0.12), 0.12)
                prev = ph
            if flat_t is not None:
                put(flat_t, beep(1000, sh["t1"] - flat_t), 0.13)

    # ---------------- spec events ----------------
    def breath_seq(t0, t1, rate, g, lo=400, hi=2600):
        per = 1.0 / rate
        x = t0
        k = 0
        while x < t1:
            n = int(per * 0.48 * SR); tt = np.arange(n) / SR
            e = np.sin(np.pi * tt / (per * 0.48)) ** 1.5
            sig = filt(noise(n), lo if k % 2 else lo * 1.4, hi if k % 2 else hi * 1.3) * e
            put(x, sig / (np.abs(sig).max() + 1e-9), g)
            x += per * 0.5
            k += 1

    for ev in S.get("sfx", []):
        at = tt_of(ev[0])
        typ = ev[1]
        kw = ev[2] if len(ev) > 2 else {}
        g = kw.get("g", 0.45)
        pan = kw.get("pan", 0.0)
        if typ == "scream":
            put(at, scream(kw.get("dur", 1.2), kw.get("f0", 300), kw.get("peak", 600), kw.get("end", 420), kw.get("vowel", "a"), kw.get("rough", 0.7)), g, pan)
        elif typ == "groan":
            put(at, groan(kw.get("dur", 1.0), kw.get("f0", 160)), kw.get("g", 0.2), pan)
        elif typ == "gasp":
            put(at, gasp(kw.get("dur", 0.6)), kw.get("g", 0.25), pan)
        elif typ == "breath":
            breath_seq(at, at + kw.get("dur", 2.0), kw.get("rate", 2.0), kw.get("g", 0.14))
        elif typ == "thud":
            n = int(0.35 * SR); tt = np.arange(n) / SR
            x = np.sin(2 * np.pi * np.cumsum(85 + 80 * np.exp(-tt * 40)) / SR) * np.exp(-tt * 14) + 0.4 * filt(noise(n), 200, 2500) * np.exp(-tt * 60)
            put(at, x / np.abs(x).max(), kw.get("g", 0.6), pan)
        elif typ == "crunch":
            put(at, crunch(kw.get("dur", 0.3)), kw.get("g", 0.7), pan)
        elif typ == "slam":
            put(at, slam(), kw.get("g", 0.8), pan)
        elif typ == "boom":
            put(at, boom(kw.get("dur", 0.8), kw.get("f", 45)), kw.get("g", 0.7), pan)
        elif typ == "whoosh":
            put(at, whoosh(kw.get("dur", 0.4)), kw.get("g", 0.2), pan)
        elif typ == "beeps":
            for j in range(kw.get("n", 6)):
                put(at + j * kw.get("every", 0.5), beep(kw.get("f", 960), 0.18), kw.get("g", 0.12), 0.4)
        elif typ == "alarm":
            for j in range(kw.get("n", 6)):
                put(at + j * 0.5, beep(960, 0.18), kw.get("g", 0.13), 0.4)
                put(at + j * 0.5 + 0.22, beep(760, 0.18), kw.get("g", 0.13), 0.4)
        elif typ == "siren":
            d_ = kw.get("dur", 2.5)
            n = int(d_ * SR); tt = np.arange(n) / SR
            s_ = np.sin(2 * np.pi * np.cumsum(700 + 250 * np.sin(2 * np.pi * 0.5 * tt)) / SR)
            put(at, filt(s_, 300, 3000) * np.sin(np.pi * tt / d_), kw.get("g", 0.08), pan)
        elif typ == "splash":
            n = int(1.0 * SR); tt = np.arange(n) / SR
            put(at, filt(noise(n), 400, 8000) * np.exp(-tt * 4), kw.get("g", 0.5), pan)
        elif typ == "bubble":
            for j in range(kw.get("n", 8)):
                n = int(0.06 * SR); tt = np.arange(n) / SR
                f0 = rng.uniform(300, 900)
                put(at + j * rng.uniform(0.05, 0.2), np.sin(2 * np.pi * np.cumsum(f0 + 1500 * tt / 0.06) / SR) * np.exp(-tt * 40), kw.get("g", 0.1), rng.uniform(-0.5, 0.5))
        elif typ == "fire":
            d_ = kw.get("dur", 3.0)
            n = int(d_ * SR)
            x = filt(noise(n), 100, 1500) * 0.5
            for k in range(int(d_ * 20)):
                m = int(0.01 * SR)
                i = int(rng.uniform(0, d_ - 0.02) * SR)
                x[i:i + m] += filt(noise(m), 1500, 8000) * np.hanning(m) * rng.uniform(0.5, 2)
            put(at, x / np.abs(x).max() * np.sin(np.pi * np.arange(n) / n) ** 0.3, kw.get("g", 0.3), pan)
        elif typ == "cough":
            for j in range(kw.get("n", 3)):
                n = int(0.22 * SR); tt = np.arange(n) / SR
                c = filt(noise(n), 200, 3000) * np.exp(-tt * 14) + 0.5 * reson(glottal(np.full(n, 140.0)), 500, 150) * np.exp(-tt * 18) * 0.05
                put(at + j * 0.35, c / np.abs(c).max(), kw.get("g", 0.3), pan)
        elif typ == "sob":
            for j in range(kw.get("n", 3)):
                n = int(0.45 * SR); tt = np.arange(n) / SR
                put(at + j * 0.6, filt(noise(n), 300, 1800) * np.sin(np.pi * tt / 0.45) ** 3, kw.get("g", 0.12), pan)
        elif typ == "drip":
            for j in range(kw.get("n", 5)):
                n = int(0.08 * SR); tt = np.arange(n) / SR
                f0 = rng.uniform(900, 1500)
                put(at + j * kw.get("every", 0.7), np.sin(2 * np.pi * np.cumsum(f0 + 900 * tt / 0.08) / SR) * np.exp(-tt * 60), kw.get("g", 0.08))
        elif typ == "zap":
            n = int(kw.get("dur", 0.6) * SR); tt = np.arange(n) / SR
            z = filt(noise(n), 1000, 9000) * (np.sin(2 * np.pi * 60 * tt) > 0) * np.exp(-tt * 4)
            put(at, z / (np.abs(z).max() + 1e-9), kw.get("g", 0.4), pan)
        elif typ == "tinnitus":
            d_ = kw.get("dur", 3.0)
            n = int(d_ * SR); tt = np.arange(n) / SR
            put(at, np.sin(2 * np.pi * 7600 * tt) * np.sin(np.pi * tt / d_), kw.get("g", 0.02))
        elif typ == "ring":
            for j in range(kw.get("n", 3)):
                put(at + j * 0.7, beep(440, 0.35) + beep(480, 0.35), kw.get("g", 0.06))

    # ---------------- heartbeat ----------------
    hb = np.zeros(N)
    bn = int(0.26 * SR); bt = np.arange(bn) / SR
    th = lambda g: np.sin(2 * np.pi * np.cumsum(72 * np.exp(-bt * 26) + 40) / SR) * np.exp(-bt * 13) * g
    prev = E.phase_at(0)
    for k in range(1, int(DUR * 200)):
        x = k / 200
        ph = E.phase_at(x)
        if E.hr_at(x) > 1 and math.floor(ph - 0.26) > math.floor(prev - 0.26):
            _, sh = E.shot_at(x)
            gg = sh.get("hb", 0.0 if sh["kind"] in ("facts", "myth", "black", "fact") else 0.65)
            i = int(x * SR)
            for off, g in ((0, 1.0), (0.16, 0.6)):
                j = i + int(off * SR)
                if j + bn < N:
                    hb[j:j + bn] += th(g * gg)
        prev = ph
    L += hb * 0.75
    R += hb * 0.75

    # ---------------- muffle ----------------
    mf = seg_env(lambda sh: sh.get("muffle", 0.0))
    if mf.max() > 0:
        Lm, Rm = filt(L, 20, 450), filt(R, 20, 450)
        L = L * (1 - mf) + Lm * mf
        R = R * (1 - mf) + Rm * mf
    mix = np.stack([L, R], 1)
    mix *= np.clip((DUR - t) / 0.2, 0, 1)[:, None]
    mix = np.tanh(mix * 1.3) / np.tanh(1.3)
    mix /= np.abs(mix).max() / 0.89
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((mix * 32767).astype(np.int16).tobytes())
    return path
