"""Synthesised soundtrack for the NEXT GAME video (30 s, 120 BPM, D minor).
Every event time below matches the GSAP timeline in src/index.html.
Usage: python3 audio.py out/sound.wav
"""
import sys, wave
import numpy as np

SR = 48000
DUR = 30.0
N = int(SR * DUR)
rng = np.random.default_rng(7)
L = np.zeros(N); R = np.zeros(N)
BEAT = 0.5


def t_arr(d):
    return np.arange(int(d * SR)) / SR


def spec_filter(x, lo=None, hi=None, order=4):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR); g = np.ones_like(f)
    if hi: g *= 1 / (1 + (f / hi) ** order)
    if lo: g *= 1 / (1 + (lo / np.maximum(f, 1e-3)) ** order)
    return np.fft.irfft(X * g, len(x))


def sweep_noise(d, f0, f1, q=1.2, seed=0):
    """band-passed noise whose centre sweeps f0 -> f1 (overlap-add, 2048 window)."""
    n = int(d * SR); w = 2048; hop = 512; out = np.zeros(n + w)
    noise = np.random.default_rng(seed).standard_normal(n + w); win = np.hanning(w)
    f = np.fft.rfftfreq(w, 1 / SR)
    for i in range(0, n, hop):
        p = i / max(1, n); fc = f0 * (f1 / f0) ** p
        g = np.exp(-0.5 * (np.log2(np.maximum(f, 1) / fc) / q) ** 2)
        out[i:i + w] += np.fft.irfft(np.fft.rfft(noise[i:i + w] * win) * g, w) * win
    out = out[:n]; return out / (np.abs(out).max() + 1e-9)


def add(sig, t0, gain=1.0, pan=0.0):
    i = int(t0 * SR); j = min(N, i + len(sig))
    if j <= i: return
    s = sig[:j - i] * gain
    L[i:j] += s * np.sqrt(0.5 * (1 - pan)) * 1.414
    R[i:j] += s * np.sqrt(0.5 * (1 + pan)) * 1.414


def env(n, a, d):
    t = np.arange(n) / SR; e = np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / d); return e


# ---------------- sound design ----------------
def impact(size=1.0):
    d = 2.5 * size; t = t_arr(d)
    f = 30 + 110 * np.exp(-t * 9)
    boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / (0.55 * size))
    crack = spec_filter(rng.standard_normal(len(t)), lo=600, hi=7000) * np.exp(-t / 0.05)
    body = spec_filter(rng.standard_normal(len(t)), hi=900) * np.exp(-t / (0.35 * size))
    tail = spec_filter(rng.standard_normal(len(t)), lo=200, hi=3000) * np.exp(-t / (0.9 * size)) * 0.12
    s = boom * 1.0 + crack * 0.35 + body * 0.5 + tail
    return np.tanh(s * 1.3)


def whoosh(d=0.45, up=True, seed=1):
    n = sweep_noise(d, 300 if up else 3000, 3000 if up else 300, 0.9, seed)
    t = np.linspace(0, 1, len(n)); e = np.sin(np.pi * t ** (0.7 if up else 1.4)) ** 2
    return n * e


def riser(d):
    n = sweep_noise(d, 200, 6000, 1.0, 11); t = np.linspace(0, 1, len(n))
    tt = t_arr(d); tone = np.sin(2 * np.pi * np.cumsum(110 * 2 ** (t * 2.5)) / SR) * 0.25
    return (n * 0.8 + tone) * t ** 2.2


def reverse_cymbal(d):
    x = spec_filter(rng.standard_normal(int(d * SR)), lo=3000); t = np.linspace(0, 1, len(x)); return x * t ** 3


def tick():
    t = t_arr(0.05); return np.sin(2 * np.pi * 3200 * t) * np.exp(-t / 0.006)


def thud():
    t = t_arr(0.4); return np.sin(2 * np.pi * np.cumsum(60 + 90 * np.exp(-t * 30)) / SR) * np.exp(-t / 0.12)


def shimmer(d=1.0):
    t = t_arr(d); s = sum(np.sin(2 * np.pi * f * t + k) for k, f in enumerate([1760, 2217, 2637, 3520]))
    return s * 0.12 * np.exp(-t / 0.35) * np.minimum(1, t / 0.02)


def crack():
    t = t_arr(0.6); x = spec_filter(rng.standard_normal(len(t)), lo=1500) * np.exp(-t / 0.08)
    return x + impact(0.6)[:len(t)] * 0.4


# ---------------- music ----------------
def kick():
    t = t_arr(0.45); f = 45 + 120 * np.exp(-t * 35)
    return np.tanh(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.16) * 2.2)


def snare():
    t = t_arr(0.3); return (spec_filter(rng.standard_normal(len(t)), lo=1200, hi=9000) * np.exp(-t / 0.07) * 0.7
                            + np.sin(2 * np.pi * 190 * t) * np.exp(-t / 0.05) * 0.5)


def tom(f0=90):
    t = t_arr(0.6); f = f0 * (1 + 0.6 * np.exp(-t * 20))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.22)


def hat():
    t = t_arr(0.06); return spec_filter(rng.standard_normal(len(t)), lo=7000) * np.exp(-t / 0.015)


def saw(f, t):
    return 2 * ((f * t) % 1) - 1


def braam(freqs, d, bright=1.0):
    t = t_arr(d); s = np.zeros(len(t))
    for f in freqs:
        for det in (-0.12, 0, 0.13):
            s += saw(f * 2 ** (det / 12), t)
    s = spec_filter(s, hi=500 * bright, order=2)
    e = np.minimum(1, t / 0.08) * np.exp(-t / (d * 0.55))
    return np.tanh(s / len(freqs) * 0.9) * e


def pad(freqs, d):
    t = t_arr(d); s = sum(np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t) for f in freqs)
    e = np.minimum(1, t / 0.6) * np.minimum(1, (d - t) / 0.6)
    return s / len(freqs) * e


def bass(f, d):
    t = t_arr(d); s = spec_filter(saw(f, t) + 0.5 * np.sin(2 * np.pi * f / 2 * t), hi=220, order=2)
    return s * np.minimum(1, t / 0.01) * np.exp(-t / 0.35)


D2, F2, G2, A2, Bb1, C2 = 73.42, 87.31, 98.0, 110.0, 58.27, 65.41
CH = {'Dm': [D2, D2 * 1.5, D2 * 2 * 1.189], 'Bb': [Bb1 * 2, Bb1 * 3, Bb1 * 4 * 1.26],
      'Gm': [G2, G2 * 1.5, G2 * 2 * 1.189], 'A': [A2, A2 * 1.5, A2 * 2 * 1.26]}
PROG = ['Dm', 'Bb', 'Gm', 'A']
ROOT = {'Dm': D2, 'Bb': Bb1, 'Gm': G2 / 2 * 2, 'A': A2 / 2 * 2}

M = np.zeros(N)  # music bus (mono, widened later)
Ms = np.zeros(N)


def madd(sig, t0, g=1.0, bus=None):
    b = M if bus is None else bus; i = int(t0 * SR); j = min(N, i + len(sig))
    if j > i: b[i:j] += sig[:j - i] * g


# intro drone 0-4
t = t_arr(4.2)
drone = spec_filter(saw(D2 / 2, t) + saw(D2 / 2 * 1.003, t) + 0.6 * saw(D2, t), hi=180, order=2)
madd(drone * np.minimum(1, t / 2.5) * np.minimum(1, (4.2 - t) / 0.3), 0, 0.55)
madd(pad([D2 * 4, D2 * 6, D2 * 4 * 1.189], 4.0), 0, 0.12)
for tt in (1.2, 2.3):
    madd(tom(70), tt, 0.9); madd(braam(CH['Dm'], 1.6, 0.8), tt, 0.5)

bar = 4 * BEAT
# section A 4-11 (build), B 11-18 (full), C 18-24.6 (info, lighter), D 25-30 (final)
def section(t0, t1, level):
    k = 0; t = t0
    while t < t1 - 1e-6:
        beat_in_bar = k % 4; chord = PROG[(k // 4) % 4]
        madd(kick(), t, 0.95)
        if beat_in_bar in (1, 3) and level >= 1: madd(snare(), t, 0.5 * level)
        if level >= 1:
            madd(tom(95), t + BEAT / 2, 0.45); madd(tom(70), t + BEAT * 0.75, 0.35)
        if level >= 2:
            for h in range(4): madd(hat(), t + h * BEAT / 4, 0.18 if h % 2 else 0.26, Ms)
            madd(tom(60), t, 0.5)
        if level < 2 and level > 0:
            for h in range(2): madd(hat(), t + h * BEAT / 2, 0.16, Ms)
        madd(bass(ROOT[chord], BEAT), t, 0.7)
        madd(bass(ROOT[chord], BEAT / 2), t + BEAT / 2, 0.45)
        if beat_in_bar == 0:
            madd(braam(CH[chord], bar, 1.0 + 0.4 * level), t, 0.32 + 0.08 * level)
            madd(pad([f * 4 for f in CH[chord]], bar), t, 0.10)
        t += BEAT; k += 1

section(4.0, 11.0, 1)
section(11.0, 18.0, 2)
section(18.0, 24.5, 0.6)
section(25.0, 28.5, 2)
# final hold
madd(braam(CH['Dm'] + [D2 * 4], 1.6 + 0.0, 1.6), 28.5, 0.6)
madd(pad([D2 * 2, D2 * 3, D2 * 4 * 1.189, D2 * 6], 1.5), 28.5, 0.25)
madd(kick(), 28.5, 1.0)

# ---------------- SFX placement ----------------
for tt, pan in ((0.30, -0.6), (0.55, 0.6), (0.80, -0.4), (1.00, 0.5)):
    add(whoosh(0.4, True, int(tt * 100)), tt - 0.05, 0.25, pan)
add(whoosh(1.1, True, 3), 0.85, 0.35, 0.3)
add(riser(1.2), 0.0, 0.25)
add(impact(0.9), 1.2, 0.7)
add(whoosh(0.35, True, 5), 1.85, 0.4)
add(impact(1.1), 2.3, 0.85)
add(whoosh(0.35, False, 6), 2.45, 0.3)
add(shimmer(1.0), 2.78, 0.6)
add(riser(1.0), 3.0, 0.45)
add(reverse_cymbal(0.7), 3.3, 0.35)
add(whoosh(0.35, True, 8), 3.6, 0.45)
add(impact(1.4), 4.0, 1.0)
for i, tt in enumerate((4.2, 5.2, 6.2)):
    add(impact(0.7), tt, 0.55, (-0.4, 0.4, 0.2)[i])
    if i: add(whoosh(0.32, True, 20 + i), tt - 0.34, 0.5, 0.0)
add(whoosh(0.32, True, 30), 6.86, 0.5)
add(impact(1.3), 7.2, 0.95); add(shimmer(1.2), 7.25, 0.5)
add(whoosh(0.6, False, 31), 7.95, 0.45)
add(impact(0.8), 8.3, 0.6, -0.3); add(impact(0.8), 8.45, 0.6, 0.3)
add(shimmer(0.9), 9.0, 0.4)
add(riser(0.9), 10.1, 0.45)
add(whoosh(0.3, True, 33), 10.65, 0.45)
add(crack(), 10.98, 0.7)
add(impact(1.0), 11.12, 0.8)
add(whoosh(0.5, True, 34), 11.3, 0.45, -0.6); add(whoosh(0.5, True, 35), 11.3, 0.45, 0.6)
add(impact(1.6), 12.0, 1.1)
add(whoosh(0.45, True, 36), 12.4, 0.4, -0.6); add(whoosh(0.45, True, 37), 12.65, 0.4, 0.6)
add(tick(), 13.4, 0.4)
add(riser(1.4), 16.2, 0.45); add(reverse_cymbal(0.9), 16.7, 0.4)
add(whoosh(0.35, True, 38), 17.55, 0.55)
add(impact(1.2), 18.0, 0.9)
for i, tt in enumerate((18.45, 19.95, 21.45)):
    add(whoosh(0.4, True, 40 + i), tt - 0.05, 0.4, (-0.5, 0.5, -0.5)[i]); add(thud(), tt + 0.2, 0.5)
for k in range(10):
    add(tick(), 20.1 + 1.3 * (1 - (1 - k / 10) ** 2), 0.35)
add(thud(), 21.85, 0.7)
add(shimmer(0.8), 22.5, 0.3); add(shimmer(0.8), 23.1, 0.3)
add(riser(1.4), 23.2, 0.5); add(reverse_cymbal(1.0), 23.6, 0.45)
add(whoosh(0.35, True, 50), 24.55, 0.55)
add(impact(1.8), 25.0, 1.15)
add(whoosh(0.4, True, 51), 25.25, 0.45, -0.6); add(whoosh(0.4, True, 52), 25.25, 0.45, 0.6)
add(whoosh(0.4, True, 53), 25.7, 0.4); add(thud(), 25.95, 0.5)
add(whoosh(0.35, True, 54), 26.25, 0.35); add(whoosh(0.35, True, 55), 26.85, 0.4)
add(shimmer(1.0), 27.6, 0.45)
add(reverse_cymbal(1.0), 27.45, 0.4)
add(impact(2.0), 28.5, 1.2)

# ---------------- crowd ambience ----------------
cr = np.zeros(N)
base = spec_filter(rng.standard_normal(N), lo=250, hi=2200, order=2)
for k in range(6):  # many voices: modulated bands
    fc = 400 + k * 260
    band = spec_filter(rng.standard_normal(N), lo=fc * 0.8, hi=fc * 1.25, order=4)
    mod = 0.6 + 0.4 * np.sin(2 * np.pi * (0.13 + 0.07 * k) * np.arange(N) / SR + k)
    cr += band * mod
cr = base * 0.6 + cr * 0.5
tt = np.arange(N) / SR
lvl = np.interp(tt, [0, 3.5, 4, 11, 12, 18, 24.5, 25, 28.5, 29, 30], [0.05, 0.12, 0.35, 0.35, 0.5, 0.45, 0.35, 0.6, 0.7, 1.0, 0.5])
cr = cr / np.abs(cr).max() * lvl * 0.35

# ---------------- mix ----------------
# music ducks briefly before the big drops (0.3 s silence before 4.0 / 12.0 / 25.0)
duck = np.ones(N)
for t0 in (3.72, 24.62):
    i = int(t0 * SR); j = int((t0 + 0.36) * SR); duck[i:j] = np.linspace(1, 0.15, j - i)
fade = np.interp(tt, [0, 29.0, 30.0], [1, 1, 0.0])
music_l = (M + Ms * 0.9) * duck; music_r = (M + Ms * 1.1) * duck
mixL = (music_l * 0.55 + L * 0.8 + cr) * fade
mixR = (music_r * 0.55 + R * 0.8 + np.roll(cr, 977)) * fade
peak = max(np.abs(mixL).max(), np.abs(mixR).max())
mixL /= peak; mixR /= peak
out = np.stack([mixL, mixR], 1) * 0.89
pcm = (np.clip(out, -1, 1) * 32767).astype('<i2')
with wave.open(sys.argv[1] if len(sys.argv) > 1 else 'out/sound.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print('ok')
