"""Synthesized soundtrack for the simulation videos: beds, drones, heartbeat, cuts, screams and effects.
Called by engine.py render; driven by the spec (shots, hr, sfx)."""
import math
import numpy as np
from scipy.signal import lfilter

SR = 44100
rng = np.random.default_rng(17)


def env(points, tt):
    return np.interp(tt, [p[0] for p in points], [p[1] for p in points])


def filt(x, lo, hi):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= (1 / (1 + (lo / np.maximum(f, 1e-3)) ** 4)) * (1 / (1 + (f / hi) ** 4))
    return np.fft.irfft(X, len(x))


def reson(x, f, bw):
    r = math.exp(-math.pi * bw / SR)
    a = [1, -2 * r * math.cos(2 * math.pi * f / SR), r * r]
    return lfilter([1 - r], a, x)




def glottal(f0):
    ph = np.cumsum(f0) / SR
    x = (ph % 1.0)
    src = 2 * x - 1                                     # sawtooth
    src -= 0.5 * np.sign(np.sin(2 * np.pi * ph))        # harsher
    return src


def scream(dur, f_start=300, f_peak=560, f_end=420, vowel="a", rough=0.6):
    n = int(dur * SR); tt = np.arange(n) / SR
    f0 = env([(0, f_start), (0.12 * dur, f_peak), (0.7 * dur, f_peak * 0.92), (dur, f_end)], tt)
    jit = filt(rng.normal(0, 1, n), 2, 40)
    jit /= np.abs(jit).max() + 1e-9
    f0 = f0 * (1 + 0.04 * jit + 0.015 * np.sin(2 * np.pi * 6.5 * tt))
    src = glottal(f0)
    src += rough * filt(rng.normal(0, 1, n), 100, 6000) * (0.6 + 0.4 * np.sin(2 * np.pi * f0 / 2 * tt))
    fm = {"a": [(850, 120, 1.0), (1250, 150, 0.6), (2700, 250, 0.35), (3500, 300, 0.2)],
          "y": [(400, 100, 1.0), (1100, 120, 0.5), (2500, 220, 0.3)],
          "o": [(550, 100, 1.0), (900, 120, 0.6), (2600, 250, 0.2)]}[vowel]
    v = sum(g * reson(src, f, bw) for f, bw, g in fm)
    v = np.tanh(v / (np.abs(v).max() + 1e-9) * 3.5)
    e = env([(0, 0), (0.05, 1), (0.8 * dur, 0.85), (dur, 0)], tt)
    return filt(v * e, 120, 9000)


def groan(dur, f=150):
    """muffled 'm-m-m' through clenched teeth"""
    n = int(dur * SR); tt = np.arange(n) / SR
    f0 = f * (1 + 0.08 * np.sin(2 * np.pi * 0.9 * tt) + 0.03 * filt(rng.normal(0, 1, n), 2, 20) / 0.02)
    src = glottal(np.clip(f0, 80, 400))
    v = reson(src, 260, 60) + 0.2 * reson(src, 1100, 200) + 0.05 * reson(src, 2300, 300)
    v += 0.25 * filt(rng.normal(0, 1, n), 1500, 6000) * (np.sin(2 * np.pi * 3 * tt) > 0.3)  # air through teeth
    v /= np.abs(v).max() + 1e-9
    pul = 0.6 + 0.4 * np.abs(np.sin(2 * np.pi * 1.6 * tt))
    return filt(v, 80, 2500) * env([(0, 0), (0.1, 1), (dur - 0.2, 1), (dur, 0)], tt) * pul


def gasp(dur):
    """stridor — whistling inhale through a closing larynx"""
    n = int(dur * SR); tt = np.arange(n) / SR
    no = rng.normal(0, 1, n)
    f = 900 + 500 * tt / dur
    w = reson(no, 1000, 90) * 0.6 + np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.3
    return w / (np.abs(w).max() + 1e-9) * np.sin(np.pi * tt / dur) ** 1.5


def whoosh(dur=0.35):
    n = int(dur * SR); tt = np.arange(n) / SR
    no = rng.normal(0, 1, n)
    out = np.zeros(n)
    for k in range(0, n, 512):
        fc = 300 + 5000 * (k / n)
        seg = no[k:k + 512]
        out[k:k + 512] = seg
    out = filt(out, 400, 7000)
    return out / (np.abs(out).max() + 1e-9) * np.sin(np.pi * tt / dur) ** 2


def boom(dur=0.7, f=55):
    n = int(dur * SR); tt = np.arange(n) / SR
    return np.sin(2 * np.pi * np.cumsum(f + 60 * np.exp(-tt * 18)) / SR) * np.exp(-tt * 5)


def crunch(dur=0.35):
    n = int(dur * SR); tt = np.arange(n) / SR
    x = np.zeros(n)
    for k in range(60):
        m = int(0.004 * SR)
        i = int(rng.uniform(0, 0.7) * (n - m))
        x[i:i + m] += rng.normal(0, 1, m) * rng.uniform(0.4, 1)
    x = filt(x, 600, 9000) + 0.6 * filt(rng.normal(0, 1, n), 80, 600) * np.exp(-tt * 25)
    return x / (np.abs(x).max() + 1e-9)


def slam():
    n = int(0.9 * SR); tt = np.arange(n) / SR
    x = filt(rng.normal(0, 1, n), 60, 3000) * np.exp(-tt * 22)
    x += 1.2 * np.sin(2 * np.pi * np.cumsum(70 + 80 * np.exp(-tt * 30)) / SR) * np.exp(-tt * 8)
    x += 0.3 * filt(rng.normal(0, 1, n), 300, 1200) * np.exp(-tt * 4)   # room tail
    return x / np.abs(x).max()


def beep(f, dur):
    n = int(dur * SR); tt = np.arange(n) / SR
    return np.sin(2 * np.pi * f * tt) * np.clip(tt / 0.005, 0, 1) * np.clip((dur - tt) / 0.01, 0, 1)

