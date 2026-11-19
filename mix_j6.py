"""Soundtrack of the J6 video (30 s) from the client's TikTok track.
- Music 0.25-14.95 s, 136 BPM, first beat at 0.42 s. The TikTok outro (15.1-16 s) is never used.
- Loop of 32 beats (8 bars): segment A = 0.25-14.68 s, then segment B = 0.42-14.90 s, so the seam falls
  on the same bar of the music. Video beat grid: K(k) = 0.60 + 0.4456 k (see src/j6.html).
- Clean SFX only (deep short impacts, soft dark whooshes) on the scene changes, no noise tails.
Usage: python3 mix_j6.py audio_src/j6-son-tiktok.mp3 out/j6/sound_mix.wav
"""
import sys, subprocess, wave, numpy as np
SR = 48000; N = 30 * SR
BEAT, T0 = 0.4456, 0.60
K = lambda k: T0 + k * BEAT
raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', sys.argv[1], '-f', 's16le', '-ac', '2', '-ar', str(SR), '-'],
                     capture_output=True, check=True).stdout
src = np.frombuffer(raw, '<i2').astype(np.float32).reshape(-1, 2) / 32768
out = np.zeros((N, 2), np.float32)
t = np.arange(N) / SR
rng = np.random.default_rng(3)

def place(seg_a, seg_b, v0, fade_in=0.01, fade_out=0.01, gain=1.0):
    s = src[int(seg_a * SR):int(seg_b * SR)].copy(); n = len(s)
    e = np.ones(n, np.float32); fi = int(fade_in * SR); fo = int(fade_out * SR)
    if fi: e[:fi] = np.linspace(0, 1, fi)
    if fo: e[-fo:] = np.minimum(e[-fo:], np.linspace(1, 0, fo))
    i0 = int(v0 * SR); n = min(n, N - i0); out[i0:i0 + n] += s[:n] * e[:n, None] * gain

# A then B, seam on the 32nd beat (video K(32)), 25 ms crossfade
place(0.25, 14.68 + 0.025, K(0) - 0.17, fade_in=0.03, fade_out=0.025)
place(0.42 - 0.0, 14.90, K(32), fade_in=0.025, fade_out=0.06)
# short dropout before the poster comes back (beat 55.5 -> 56)
duck = 1 - 0.85 * np.clip((t - (K(55.5))) / 0.05, 0, 1) * (t < K(56) - 0.01)
out *= duck[:, None]
# after the final hit the music rings out
out *= np.where(t > K(64), np.clip(1 - (t - K(64)) / 0.5, 0, 1), 1)[:, None]

def spec_lp(x, hi):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR); return np.fft.irfft(X / (1 + (f / hi) ** 4), len(x))
def impact(size=1.0):
    d = 1.6 * size; tt = np.arange(int(d * SR)) / SR
    f = 30 + 110 * np.exp(-tt * 9)
    boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt / (0.45 * size))
    body = spec_lp(rng.standard_normal(len(tt)), 500) * np.exp(-tt / 0.08)
    return (boom * 0.8 + body * 0.35) * np.exp(-tt / (0.6 * size))
def whoosh(d=0.32):
    n = int(d * SR); x = spec_lp(rng.standard_normal(n), 1400)
    e = np.sin(np.pi * np.linspace(0, 1, n) ** 0.8) ** 2; x = x * e; return x / (np.abs(x).max() + 1e-9)
def add(sig, at, g):
    i = int(at * SR); j = min(N, i + len(sig)); out[i:j] += (sig[:j - i] * g)[:, None]

for k, g in [(2, .45), (4, .5), (8, .7), (12, .8), (16, .5), (24, .7), (25, .9), (40, .6), (56, .9)]:
    add(impact(0.8 if g < .8 else 1.0), K(k), g * 0.45)
add(impact(1.4), K(64), 0.6)
for k in [7.5, 11.5, 15.5, 23.5, 39.5, 55.6]:
    add(whoosh(), K(k) - 0.05, 0.22)

out /= max(1e-6, np.abs(out).max()) / 0.95
with wave.open(sys.argv[2], 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((out * 32767).astype('<i2').tobytes())
print('ok')
