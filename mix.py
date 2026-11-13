"""Mix of the two client tracks for the 30 s video (timings match src/index.html).
son2 : intro 0-11 s (beat-aligned, +0.47 s) and final impact (45.07 s in the file) on the 28.5 s hit.
son1 : stretched to 120 BPM, enters on the 11.12 s flash, phrase downbeat (46.0 s in the file) on the VS at 12.0 s.
sfx  : light whooshes / impacts from audio.py (SFX_ONLY=1) to sharpen the transitions.
Usage: python3 mix.py work/son1_120.wav work/son2.wav work/sfx.wav out/sound_mix.wav
"""
import sys, wave, numpy as np
SR = 48000; N = 30 * SR
def load(p):
    with wave.open(p) as w:
        a = np.frombuffer(w.readframes(w.getnframes()), '<i2').astype(np.float32) / 32768
        return a.reshape(-1, w.getnchannels())
s1, s2, fx = (load(p) for p in sys.argv[1:4])
out = np.zeros((N, 2), np.float32)
t = np.arange(N) / SR

def place(src, src_offset, v0, v1, gain, env):
    """copy src[src_offset + (v - v0)] for video time v in [v0, v1)"""
    i0, i1 = int(v0 * SR), int(v1 * SR); j0 = int(src_offset * SR)
    seg = src[j0:j0 + (i1 - i0)]
    n = len(seg); out[i0:i0 + n] += seg * gain * env(t[i0:i0 + n])[:, None]

db = lambda x: 10 ** (x / 20)
ramp = lambda a, b: (lambda tt: np.clip((tt - a) / (b - a), 0, 1))
# A: son2 intro (son2 time = v - 0.47)
place(s2, 0.0, 0.47, 11.30, db(5.0), lambda tt: np.clip((tt - .47) / .25, 0, 1) * (1 - ramp(10.85, 11.25)(tt)) ** 1.5)
# B: son1 at 120 BPM (son1' time = 45.0411 + (v - 12.0)), duck before the final section
S1_AT_12 = 46.0 / 1.0212766
def envB(tt):
    e = ramp(11.10, 11.15)(tt) * (1 - ramp(28.42, 28.58)(tt))
    duck = 1 - 0.8 * ramp(24.55, 24.70)(tt) * (1 - ramp(24.98, 25.0)(tt)) * (tt < 25.0)
    return e * duck
place(s1, S1_AT_12 - 0.9, 11.10, 28.60, db(-2.0), envB)
# C: son2 final impact (45.07 s) on the 28.5 s hit, tail to the end
place(s2, 45.07 - 0.75, 27.75, 30.0, db(-1.5), lambda tt: (0.25 + 0.75 * ramp(28.30, 28.48)(tt)) * ramp(27.75, 28.1)(tt) * (1 - ramp(29.6, 30.0)(tt)))
# SFX stem, discreet
out += fx[:N] * db(-9.0)
out /= max(1e-6, np.abs(out).max()) / 0.95
with wave.open(sys.argv[4], 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(out, -1, 1) * 32767).astype('<i2').tobytes())
print('ok')
