"""Dark trap / phonk score + sound design, synced to the style-3 timeline.
build(E, wav): E = loaded engine3 module (E.S spec, E.SHOTS).
SPEC['music'] = dict(bpm=120, drop='<shot name>', calm=[shot names], key=0 (semitones from F), seed)
Sections: intro hit -> groove A -> riser + silence -> DROP (heavy B with cowbell) -> facts (light C) -> loop hit.
"""
import math, os, sys, wave
import numpy as np
from scipy.signal import butter, lfilter, fftconvolve, sosfilt

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import _sfx_lib as X

SR = 44100
rng = np.random.default_rng(7)


def bp(x, lo, hi, order=2):
    sos = butter(order, [lo / (SR / 2), min(hi / (SR / 2), 0.999)], btype="band", output="sos")
    return sosfilt(sos, x)


def lp(x, f, order=2):
    sos = butter(order, min(f / (SR / 2), 0.999), btype="low", output="sos")
    return sosfilt(sos, x)


def hp(x, f, order=2):
    sos = butter(order, f / (SR / 2), btype="high", output="sos")
    return sosfilt(sos, x)


def note(n):
    """semitones from F1 (43.65 Hz)"""
    return 43.654 * 2 ** (n / 12)


def tt(d):
    return np.arange(int(d * SR)) / SR


# ------------------------------------------------------------------ instruments
def k808(f0, dur=1.4, glide_to=None, drive=2.2):
    t = tt(dur)
    f = f0 * (1 + 1.6 * np.exp(-t * 38))
    if glide_to:
        g = np.clip((t - dur * 0.45) / (dur * 0.35), 0, 1)
        f = f * (1 - g) + glide_to * g
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(ph) * np.exp(-t * 1.6)
    x = np.tanh(x * drive) / np.tanh(drive)
    x[: int(0.004 * SR)] *= np.linspace(0, 1, int(0.004 * SR))
    return x


def kick():
    t = tt(0.32)
    f = 48 + 150 * np.exp(-t * 45)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 11)
    x += 0.5 * hp(rng.normal(0, 1, len(t)), 2000) * np.exp(-t * 180)
    return np.tanh(x * 1.6)


def snare():
    t = tt(0.35)
    n = bp(rng.normal(0, 1, len(t)), 1200, 9000) * np.exp(-t * 18)
    body = np.sin(2 * np.pi * np.cumsum(200 + 60 * np.exp(-t * 30)) / SR) * np.exp(-t * 25)
    clap = np.zeros_like(t)
    for off in (0.0, 0.011, 0.023):
        i = int(off * SR)
        seg = bp(rng.normal(0, 1, len(t) - i), 900, 5000) * np.exp(-t[: len(t) - i] * 30)
        clap[i:] += seg
    return 0.6 * n + 0.5 * body + 0.5 * clap


def hat(open_=False):
    t = tt(0.25 if open_ else 0.06)
    x = hp(rng.normal(0, 1, len(t)), 7000) * np.exp(-t * (14 if open_ else 70))
    return x


def cowbell(f):
    t = tt(0.32)
    x = np.sign(np.sin(2 * np.pi * f * t)) + np.sign(np.sin(2 * np.pi * f * 1.48 * t))
    x = bp(x, 450, 2600) * (np.exp(-t * 10) * 0.8 + 0.2 * np.exp(-t * 40))
    return x


def bell(f, dur=1.6):
    t = tt(dur)
    idx = 3.5 * np.exp(-t * 3.5)
    m = np.sin(2 * np.pi * f * 3.5 * t) * idx
    x = np.sin(2 * np.pi * f * t + m) * np.exp(-t * 2.2)
    x += 0.3 * np.sin(2 * np.pi * f * 2.01 * t) * np.exp(-t * 4)
    return x


def pad(freqs, dur):
    t = tt(dur)
    x = np.zeros_like(t)
    for f in freqs:
        for det in (-0.12, 0.0, 0.13):
            ph = 2 * np.pi * f * 2 ** (det / 12) * t + rng.uniform(0, 6.28)
            x += ((ph / np.pi) % 2 - 1)
    x = lp(x, 900) / (len(freqs) * 3)
    env = np.minimum(1, t / 0.4) * np.minimum(1, (dur - t) / 0.4)
    return x * np.clip(env, 0, 1)


def braam(f, dur=2.5):
    t = tt(dur)
    x = np.zeros_like(t)
    for mult, det in ((1, 0), (1, 0.1), (2, -0.08), (1.5, 0.05)):
        ph = 2 * np.pi * f * mult * 2 ** (det / 12) * t
        x += ((ph / np.pi) % 2 - 1)
    cut = 200 + 1800 * np.exp(-t * 1.5)
    y = np.zeros_like(x)
    # time-varying lowpass via blocks
    B = 2048
    for i in range(0, len(x), B):
        y[i:i + B] = lp(x[i:i + B + 512], float(cut[i]))[: len(x[i:i + B])]
    y = np.tanh(y * 1.8) * np.exp(-t * 0.9)
    return y


def impact(dur=2.2):
    t = tt(dur)
    sub = np.sin(2 * np.pi * np.cumsum(30 + 70 * np.exp(-t * 6)) / SR) * np.exp(-t * 1.8)
    nz = lp(rng.normal(0, 1, len(t)), 3000) * np.exp(-t * 6)
    return np.tanh((sub * 1.2 + 0.4 * nz) * 1.5)


def riser(dur=1.6):
    t = tt(dur)
    k = t / dur
    nz = rng.normal(0, 1, len(t))
    out = np.zeros_like(t)
    B = 2048
    for i in range(0, len(t), B):
        f = 300 + 7000 * k[i] ** 2
        out[i:i + B] = bp(nz[i:i + B], f * 0.7, f * 1.3)[: len(out[i:i + B])]
    tone = np.sin(2 * np.pi * np.cumsum(200 + 900 * k ** 2) / SR) * 0.3
    return (out * 0.8 + tone) * k ** 1.5


def whoosh(dur=0.35):
    t = tt(dur)
    k = t / dur
    nz = rng.normal(0, 1, len(t))
    y = bp(nz, 400, 5000) * np.sin(np.pi * k) ** 2
    return y


def reverb(x, dur=2.0, mix=0.25):
    t = tt(dur)
    ir = rng.normal(0, 1, len(t)) * np.exp(-t * 3.2)
    ir = lp(ir, 5000)
    ir /= np.sqrt((ir ** 2).sum())
    wet = fftconvolve(x, ir)[: len(x)]
    return x * (1 - mix) + wet * mix * 2.2


# ------------------------------------------------------------------ score
def build(E, path):
    S = E.S
    M = S.get("music", {})
    DUR = S["T_END"]
    N = int(DUR * SR) + SR
    bpm = M.get("bpm", 120)
    beat = 60 / bpm
    bar = beat * 4
    key = M.get("key", 0)
    drums = np.zeros(N); bass = np.zeros(N); mel = np.zeros(N); pads = np.zeros(N); fx = np.zeros(N); sfxL = np.zeros(N); sfxR = np.zeros(N)
    side = np.ones(N)

    def put(buf, t0, sig, g=1.0):
        i0 = int(t0 * SR)
        if i0 < 0:
            sig = sig[-i0:]
            i0 = 0
        n = min(len(sig), N - i0)
        if n > 0:
            buf[i0:i0 + n] += sig[:n] * g

    shots = E.SHOTS
    first_fact = next((s["t0"] for s in shots if s.get("kind") == "fact"), DUR)
    drop_t = None
    if M.get("drop"):
        try:
            drop_t = E.shot_named(M["drop"])["t0"]
        except KeyError:
            drop_t = None
    hook_end = shots[1]["t1"] if len(shots) > 1 else bar
    calm = [(E.shot_named(n)["t0"], E.shot_named(n)["t1"]) for n in M.get("calm", []) if any(s.get("name") == n for s in shots)]
    loop_t = shots[-1]["t0"] if shots[-1].get("name") == "loop" else None
    # grid start right after the hook so the groove lands on the third shot
    g0 = hook_end
    prog = M.get("prog", [0, 0, 3, 2])           # bass notes per bar (semitones from F)
    chords = {0: [0, 3, 7], 3: [3, 7, 10], 2: [2, 5, 9], -4: [-4, 0, 3], 5: [5, 8, 12], -2: [-2, 2, 5]}
    mel_seq = M.get("mel", [12, 15, 19, 15, 24, 22, 19, 15])

    def section(t):
        if t < g0:
            return "intro"
        if t >= first_fact:
            return "outro" if not loop_t or t < loop_t else "end"
        if drop_t and drop_t - 0.45 <= t < drop_t:
            return "silence"
        if drop_t and t >= drop_t:
            return "heavy"
        return "groove"

    # intro: impact + braam + 808 slide
    put(fx, 0.0, impact(2.4), 1.0)
    put(fx, 0.0, braam(note(key) * 2, 2.6), 0.55)
    put(bass, 0.05, k808(note(key + 12), 1.6, glide_to=note(key)), 0.9)
    put(fx, max(0, g0 - 0.9), riser(0.9), 0.35)
    # grid
    step = beat / 4
    nsteps = int((DUR - g0) / step) + 1
    kick_pat = [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0]
    kick_pat2 = [1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0]
    sn = snare(); kk = kick()
    hats_c = hat(); hat_o = hat(True)
    for j in range(nsteps):
        t = g0 + j * step
        sec = section(t)
        if sec in ("silence", "end"):
            continue
        b = j // 16
        s16 = j % 16
        heavy = sec == "heavy"
        light = sec == "outro"
        if any(a <= t < b_ for a, b_ in calm):
            light = True
        kp = kick_pat2 if heavy else kick_pat
        if kp[s16] and not (light and s16 not in (0,)):
            put(drums, t, kk, 0.9)
            side[int(t * SR):int((t + 0.18) * SR)] = np.minimum(side[int(t * SR):int((t + 0.18) * SR)], np.linspace(0.35, 1, len(side[int(t * SR):int((t + 0.18) * SR)])))
        if s16 in (4, 12) and not (light and b % 2):
            put(drums, t, sn, 0.6 if not light else 0.35)
        # hats: 8ths, 16ths in heavy, rolls on last beat of every 2nd bar
        hv = 0.0
        if s16 % 2 == 0:
            hv = 0.22 if s16 % 4 == 0 else 0.15
        elif heavy:
            hv = 0.1
        if not light or s16 % 4 == 0:
            if hv:
                put(drums, t, hats_c, hv * (0.6 if light else 1))
        if (b % 2 == 1) and s16 >= 12 and not light:
            for r in range(3 if s16 % 2 == 0 else 2):
                put(drums, t + r * step / 3, hats_c, 0.09)
        if heavy and s16 == 14:
            put(drums, t, hat_o, 0.12)
        # 808 on bar start (+ on step 10)
        if s16 in (0, 10):
            n = prog[b % len(prog)]
            gl = note(key + prog[(b + 1) % len(prog)]) if (s16 == 10 and b % 4 == 3) else None
            put(bass, t, k808(note(key + n), 1.2 if s16 == 0 else 0.7, glide_to=gl, drive=3.2 if heavy else 2.2), 0.85 if not light else 0.55)
        # pad per bar
        if s16 == 0:
            ch = chords.get(prog[b % len(prog)], [0, 3, 7])
            put(pads, t, pad([note(key + 24 + c) for c in ch], bar + 0.3), 0.5 if not heavy else 0.4)
        # bell melody: 8ths pattern, sparse
        if s16 % 4 == 0 and (b % 2 == 0 or s16 < 8) and sec != "intro":
            m = mel_seq[(b * 4 + s16 // 4) % len(mel_seq)]
            put(mel, t, bell(note(key + 36 + m), 1.4), 0.16 if not heavy else 0.12)
        # cowbell phonk riff in heavy
        if heavy and s16 in (0, 3, 6, 8, 10, 13):
            riff = [24, 27, 24, 31, 29, 27]
            put(mel, t, cowbell(note(key + riff[[0, 3, 6, 8, 10, 13].index(s16)] + 24)), 0.13)
    # drop hit
    if drop_t:
        put(fx, drop_t - 1.9, riser(1.45), 0.45)
        put(fx, drop_t, impact(2.6), 1.0)
        put(fx, drop_t, braam(note(key) * 2, 3.0), 0.6)
        put(bass, drop_t, k808(note(key + 12), 1.8, glide_to=note(key)), 1.0)
    if loop_t:
        put(fx, loop_t, impact(1.6), 0.9)
        put(fx, loop_t, braam(note(key) * 2, 1.8), 0.5)
    # whooshes on cuts, sub hits on fact cards
    for s in shots[1:]:
        put(fx, s["t0"] - 0.22, whoosh(0.3), 0.18)
        if s.get("kind") == "fact":
            put(fx, s["t0"], impact(0.9), 0.45)
        for hit in s.get("fx", {}).get("hits", []):
            put(fx, s["t0"] + hit[0], impact(1.4), 0.7 * min(1.3, hit[1]))
    # calm sections: low-pass the music
    music = drums * 1.0 + bass * 0.95 + mel + pads * 0.7
    music = reverb(music, 1.6, 0.18) * 0.0 + music
    mel_r = reverb(mel + pads * 0.6, 2.4, 0.5)
    music = drums * 0.9 + lp(bass, 400) * 0.55 + hp(bass, 120) * 0.5 + mel_r * 1.6 + lp(pads, 1200) * 0.0
    music = music * (side * 0.35 + 0.65)
    calm_env = np.zeros(N)
    for a, b_ in calm:
        i0, i1 = int(a * SR), int(b_ * SR)
        calm_env[i0:i1] = 1
    if calm_env.any():
        sm = np.convolve(calm_env, np.ones(2000) / 2000, mode="same")
        music = music * (1 - sm) + lp(music, 500) * sm
    # ---------------- sound design (screams, breaths, heart) ----------------
    X.rng = rng

    def tt_of(spec_t):
        if isinstance(spec_t, (list, tuple)):
            return E.shot_named(spec_t[0])["t0"] + spec_t[1]
        return float(spec_t)

    for ev in S.get("sfx", []):
        at = tt_of(ev[0])
        typ = ev[1]
        kw = ev[2] if len(ev) > 2 else {}
        g = kw.get("g", 0.4)
        sig = None
        if typ == "scream":
            sig = X.scream(kw.get("dur", 1.2), kw.get("f0", 300), kw.get("peak", 600), kw.get("end", 420), kw.get("vowel", "a"), kw.get("rough", 0.7))
        elif typ == "groan":
            sig = X.groan(kw.get("dur", 1.0), kw.get("f0", 150))
        elif typ == "gasp":
            sig = X.gasp(kw.get("dur", 0.6))
        elif typ == "breath":
            d_ = kw.get("dur", 1.5)
            sig = np.zeros(int(d_ * SR))
            per = 1 / kw.get("rate", 2.0)
            for k in range(int(d_ / per * 2)):
                n = int(per * 0.45 * SR)
                e = np.sin(np.pi * np.arange(n) / n) ** 1.5
                seg = bp(rng.normal(0, 1, n), 400 if k % 2 else 600, 2600) * e
                i = int(k * per / 2 * SR)
                sig[i:i + n] += seg[: len(sig[i:i + n])]
        elif typ == "crunch":
            sig = X.crunch(kw.get("dur", 0.3))
        elif typ == "boom":
            sig = impact(kw.get("dur", 1.5))
        elif typ == "slam":
            sig = X.slam()
        elif typ == "glass":
            n = int(0.8 * SR)
            t_ = np.arange(n) / SR
            sig = np.zeros(n)
            for k in range(30):
                f = rng.uniform(2500, 8000)
                i = int(rng.uniform(0, 0.4) * SR)
                m = n - i
                sig[i:] += np.sin(2 * np.pi * f * t_[:m]) * np.exp(-t_[:m] * rng.uniform(15, 40)) * rng.uniform(0.2, 1)
            sig += hp(rng.normal(0, 1, n), 3000) * np.exp(-t_ * 12)
        elif typ == "beeps":
            sig = np.zeros(int(kw.get("n", 4) * kw.get("every", 0.5) * SR))
            for j in range(kw.get("n", 4)):
                b_ = X.beep(kw.get("f", 1000), 0.12)
                i = int(j * kw.get("every", 0.5) * SR)
                sig[i:i + len(b_)] += b_[: len(sig[i:i + len(b_)])]
        elif typ == "flatline":
            d_ = kw.get("dur", 2.0)
            sig = np.sin(2 * np.pi * 1000 * tt(d_)) * 0.4
        elif typ == "siren":
            d_ = kw.get("dur", 2.5)
            t_ = tt(d_)
            sig = bp(np.sin(2 * np.pi * np.cumsum(700 + 250 * np.sin(2 * np.pi * 0.5 * t_)) / SR), 300, 3000) * np.sin(np.pi * t_ / d_)
        elif typ == "tinnitus":
            d_ = kw.get("dur", 2.5)
            t_ = tt(d_)
            sig = np.sin(2 * np.pi * 7400 * t_) * np.sin(np.pi * t_ / d_) * 0.3
        elif typ == "cough":
            sig = np.zeros(int(1.0 * SR))
            for j in range(3):
                n = int(0.22 * SR)
                seg = bp(rng.normal(0, 1, n), 200, 3000) * np.exp(-np.arange(n) / SR * 14)
                sig[int(j * 0.32 * SR):int(j * 0.32 * SR) + n] += seg
        elif typ == "phone":
            sig = np.zeros(int(2.4 * SR))
            for j in range(3):
                b_ = X.beep(440, 0.4) + X.beep(480, 0.4)
                sig[int(j * 0.8 * SR):int(j * 0.8 * SR) + len(b_)] += b_ * 0.5
        elif typ == "whoosh":
            sig = whoosh(kw.get("dur", 0.5))
        elif typ == "heartbeat":
            sig = np.zeros(int(kw.get("dur", 3) * SR))
            per = 60 / kw.get("bpm", 120)
            for j in range(int(kw.get("dur", 3) / per)):
                for off, gg in ((0, 1), (0.14, 0.6)):
                    tb = tt(0.22)
                    th = np.sin(2 * np.pi * np.cumsum(55 + 50 * np.exp(-tb * 30)) / SR) * np.exp(-tb * 14) * gg
                    i = int((j * per + off) * SR)
                    sig[i:i + len(th)] += th[: len(sig[i:i + len(th)])]
        if sig is not None:
            sig = sig / (np.abs(sig).max() + 1e-9)
            pan = kw.get("pan", 0.0)
            i0 = int(at * SR)
            n = min(len(sig), N - i0)
            if n > 0:
                sfxL[i0:i0 + n] += sig[:n] * g * (1 - pan)
                sfxR[i0:i0 + n] += sig[:n] * g * (1 + pan)
    # duck music under loud sfx
    env_s = np.convolve(np.abs(sfxL) + np.abs(sfxR), np.ones(4410) / 4410, mode="same")
    duck = 1 - 0.45 * np.clip(env_s / 0.15, 0, 1)
    fxs = reverb(fx, 2.2, 0.3)
    L = music * 0.75 * duck + fxs * 0.6 + sfxL
    R = music * 0.75 * duck + fxs * 0.6 + sfxR
    # stereo width on melody/pads
    w = np.roll(mel_r, int(0.012 * SR)) * 0.15
    L += w
    R -= w
    n = int(DUR * SR)
    mix = np.stack([L[:n], R[:n]], 1)
    fade = np.clip((DUR - np.arange(n) / SR) / 0.25, 0, 1)
    mix *= fade[:, None]
    rms = np.sqrt((mix ** 2).mean()) + 1e-9
    mix *= 10 ** (-15.5 / 20) / rms
    mix = np.tanh(mix / 0.92) * 0.92                 # soft limiter
    with wave.open(path, "wb") as wv:
        wv.setnchannels(2)
        wv.setsampwidth(2)
        wv.setframerate(SR)
        wv.writeframes((mix * 32767).astype(np.int16).tobytes())
    return path
