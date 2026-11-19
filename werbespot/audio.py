"""Soundtrack v2 – Deep-House-Groove, 120 BPM, synchron zu ad.html (v2).
python3 audio.py out.wav"""
import sys, wave
import numpy as np
from scipy import signal

SR = 48000
DUR = 30.0
N = int(SR * DUR)
BEAT = 0.5
S16 = BEAT / 4
SWING = 0.018
rng = np.random.default_rng(11)

BUS_NAMES = ("drums", "bass", "keys", "pad", "fx", "intro")
bus = {k: np.zeros((2, N)) for k in BUS_NAMES}
send = np.zeros((2, N))


def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def tt(d):
    return np.arange(int(d * SR)) / SR


def fade(s, a=0.003, r=0.01):
    s = s.copy()
    na, nr = max(1, int(a * SR)), max(1, int(r * SR))
    s[..., :na] *= np.linspace(0, 1, na)
    s[..., -nr:] *= np.linspace(1, 0, nr)
    return s


def bp(x, lo=None, hi=None, order=2):
    if lo and hi:
        sos = signal.butter(order, [lo, hi], 'bandpass', fs=SR, output='sos')
    elif hi:
        sos = signal.butter(order, hi, 'lowpass', fs=SR, output='sos')
    else:
        sos = signal.butter(order, lo, 'highpass', fs=SR, output='sos')
    return signal.sosfilt(sos, x, axis=-1)


def add(b, sig, start, gain=1.0, pan=0.0, rev=0.0):
    sig = np.atleast_2d(sig)
    if sig.shape[0] == 1:
        l, r = np.cos((pan + 1) * np.pi / 4) * 1.414, np.sin((pan + 1) * np.pi / 4) * 1.414
        sig = np.vstack([sig[0] * l, sig[0] * r])
    i = int(round(start * SR))
    if i < 0:
        sig, i = sig[:, -i:], 0
    n = min(sig.shape[1], N - i)
    if n <= 0:
        return
    bus[b][:, i:i + n] += sig[:, :n] * gain
    if rev:
        send[:, i:i + n] += sig[:, :n] * gain * rev


# ---------------- instruments ----------------
def kick(gain=1.0):
    t = tt(0.42)
    f = 48 + 140 * np.exp(-t * 38)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7.5)
    punch = np.sin(2 * np.pi * 120 * t) * np.exp(-t * 45) * 0.35
    click = bp(rng.standard_normal(len(t)) * np.exp(-t * 500), lo=3000) * 0.18
    return fade(np.tanh((body + punch + click) * 1.8) * gain, 0.001, 0.02)


def clap():
    t = tt(0.45)
    env = np.zeros_like(t)
    for off in (0, 0.009, 0.019, 0.028):
        m = t >= off
        env[m] += np.exp(-(t[m] - off) * 220)
    m = t >= 0.028
    env[m] += 0.45 * np.exp(-(t[m] - 0.028) * 14)
    n = bp(rng.standard_normal(len(t)), 1000, 7500) * env
    body = np.sin(2 * np.pi * 210 * t) * np.exp(-t * 40) * 0.25
    return fade(n + body)


def snare(d=0.22):
    t = tt(d)
    return fade(bp(rng.standard_normal(len(t)), 1800, 9000) * np.exp(-t * 24) + np.sin(2 * np.pi * 185 * t) * np.exp(-t * 32) * 0.5)


def hat(open_=False):
    t = tt(0.32 if open_ else 0.06)
    metal = sum(np.sign(np.sin(2 * np.pi * f * t)) for f in (3140, 4420, 5870, 7210, 8650))
    n = rng.standard_normal(len(t)) * 0.7 + metal * 0.15
    return fade(bp(n, lo=7000, order=3) * np.exp(-t * (11 if open_ else 75)))


def rim():
    t = tt(0.08)
    return fade(bp(rng.standard_normal(len(t)) * np.exp(-t * 120), 1500, 3500) + np.sin(2 * np.pi * 820 * t) * np.exp(-t * 90) * 0.4)


def shutter():
    t = tt(0.14)
    a = bp(rng.standard_normal(len(t)), 1500, 9000) * (np.exp(-t * 300) + 0.7 * np.exp(-np.clip(t - 0.07, 0, None) * 260) * (t > 0.07))
    return fade(a)


def tick():
    t = tt(0.03)
    return fade(np.sin(2 * np.pi * 2400 * t) * np.exp(-t * 300))


def ep(note, d, vel=1.0):
    """FM-E-Piano."""
    t = tt(d + 0.5)
    f = midi(note)
    idx = 1.8 * vel * np.exp(-t * 3.5) + 0.25
    s = np.sin(2 * np.pi * f * t + idx * np.sin(2 * np.pi * f * t))
    s += 0.07 * vel * np.sin(2 * np.pi * f * 14 * t) * np.exp(-t * 50)
    env = np.minimum(1, t / 0.003) * (0.6 * np.exp(-t * 1.6) + 0.4 * np.exp(-t * 0.4))
    env *= np.where(t > d, np.exp(-(t - d) * 14), 1)
    s = s * env
    trem = 0.5 + 0.25 * np.sin(2 * np.pi * 4.2 * t)
    return np.vstack([s * trem, s * (1 - trem)]) * 1.4


def chord_ep(notes, d, vel=1.0):
    out = None
    for n in notes:
        e = ep(n, d, vel)
        out = e if out is None else out + e
    return out / len(notes) * 2.2


def bass_note(note, d):
    t = tt(d + 0.03)
    f = midi(note)
    ph = 2 * np.pi * f * t
    s = np.sin(ph) + 0.35 * np.sin(2 * ph) + 0.15 * np.sin(3 * ph)
    sub = np.sin(ph / 2) * 0.6
    env = np.minimum(1, t / 0.004) * np.where(t > d, np.exp(-(t - d) * 60), 1) * (0.7 + 0.3 * np.exp(-t * 6))
    return fade(np.tanh((s + sub) * env * 1.6) * 0.8, 0.002, 0.01)


def pad(notes, d, attack=0.8, release=1.5, cutoff=1800):
    t = tt(d + release)
    out = np.zeros((2, len(t)))
    for n in notes:
        for det, pan in ((-9, -0.7), (0, 0), (9, 0.7)):
            f = midi(n) * 2 ** (det / 1200)
            saw = 2 * ((f * t + rng.random()) % 1) - 1
            l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
            out[0] += saw * l
            out[1] += saw * r
    out = bp(out, hi=cutoff, order=2)
    env = np.minimum(1, t / attack) * np.where(t > d, np.exp(-(t - d) / (release / 4)), 1)
    return out * env / (len(notes) * 3) * 0.8


def impact(size=1.0):
    t = tt(2.2 * size)
    f = 28 + 80 * np.exp(-t * 7)
    sub = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / (0.5 * size))
    thump = bp(rng.standard_normal(len(t)), hi=300) * np.exp(-t * 12) * 2
    crash = bp(rng.standard_normal(len(t)), 600, 12000) * np.exp(-t / (0.3 * size)) * 0.4
    return fade(np.tanh((sub * 1.3 + thump + crash) * 1.3), 0.001, 0.2)


def riser(d, top=8000):
    t = tt(d)
    p = t / d
    n = rng.standard_normal(len(t))
    out = np.zeros_like(t)
    edges = np.geomspace(250, top, 9)
    for i in range(len(edges) - 1):
        band = bp(n, edges[i], edges[i + 1])
        c = i / (len(edges) - 2)
        out += band * np.exp(-((c - p) ** 2) / 0.05)
    out = out / (np.max(np.abs(out)) + 1e-9) * p ** 1.6
    sw = np.sin(2 * np.pi * np.cumsum(220 * 2 ** (p * 2.5)) / SR) * p ** 3 * 0.18
    return fade(out + sw, 0.05, 0.003)


def reverse_cym(d):
    t = tt(d)
    return fade(bp(rng.standard_normal(len(t)), lo=4000) * (t / d) ** 3.5, 0.01, 0.003)


def whoosh(d, p0=-0.8, p1=0.8, lo=300, hi=4000):
    t = tt(d)
    p = t / d
    s = bp(rng.standard_normal(len(t)), lo, hi) * np.sin(np.pi * p) ** 2
    pan = p0 + (p1 - p0) * p
    return np.vstack([s * np.cos((pan + 1) * np.pi / 4), s * np.sin((pan + 1) * np.pi / 4)]) * 1.4


def chime(note, d=3.0):
    t = tt(d)
    f = midi(note)
    s = sum(a * np.sin(2 * np.pi * f * r * t) * np.exp(-t * k) for a, r, k in ((1, 1, 1.3), (0.5, 2.0, 2.5), (0.25, 3.01, 4), (0.12, 5.4, 7)))
    return fade(s * np.minimum(1, t / 0.002), 0.001, 0.3)


def crackle(d):
    t = tt(d)
    n = np.zeros_like(t)
    idx = rng.integers(0, len(t), int(d * 40))
    n[idx] = rng.standard_normal(len(idx)) * 0.9
    n = bp(n, 800, 9000) + bp(rng.standard_normal(len(t)) * 0.05, 3000, 12000)
    return n


# ---------------- song data ----------------
CHORDS = [[53, 57, 60, 64, 67], [52, 55, 59, 62, 66], [50, 53, 57, 60, 64], [48, 52, 55, 59, 62]]  # Fmaj9 Em9 Dm9 Cmaj9
ROOTS = [41, 40, 38, 36]
STABS = [(0, 3.0), (3, 1.0), (6, 2.0), (10, 1.0), (13, 1.6)]   # 16th-Position, Länge in 16teln
BASS = [(0, 2, 0), (3, 1, 0), (6, 1.5, 12), (8, 2, 0), (11, 1, 0), (14, 1, 12)]


def pos(bar_t, i16):
    return bar_t + i16 * S16 + (SWING if i16 % 2 else 0)


def groove(t0, t1, b_drums="drums", b_keys="keys", b_bass="bass", kick_on=True, bass_on=True, keys_on=True,
           hats=True, clap_on=True, perc=True, kick_gain=1.0):
    kicks = []
    bt = t0
    while bt < t1 - 1e-6:
        ci = int(bt // 2.0) % 4
        for i16 in range(16):
            tt_ = pos(bt, i16)
            if tt_ >= t1 - 1e-6:
                continue
            if kick_on and i16 % 4 == 0:
                add(b_drums, kick(kick_gain), tt_)
                kicks.append(tt_)
            if clap_on and i16 in (4, 12):
                add(b_drums, clap(), tt_, gain=0.55, rev=0.18)
            if hats:
                if i16 % 4 == 2:
                    add(b_drums, hat(True), tt_, gain=0.16, pan=-0.15, rev=0.05)
                elif i16 % 2 == 1:
                    add(b_drums, hat(), tt_, gain=0.20 if i16 % 4 == 3 else 0.12, pan=0.25)
            if perc and i16 in (7, 15):
                add(b_drums, rim(), tt_, gain=0.12, pan=-0.35, rev=0.15)
        if keys_on:
            for i16, ln in STABS:
                tt_ = pos(bt, i16)
                if tt_ < t1 - 1e-6:
                    add(b_keys, chord_ep(CHORDS[ci], ln * S16, 0.9), tt_, gain=0.34, rev=0.25)
        if bass_on:
            for i16, ln, oc in BASS:
                tt_ = pos(bt, i16)
                if tt_ < t1 - 1e-6:
                    add(b_bass, bass_note(ROOTS[ci] - 12 + oc, ln * S16 * 0.9), tt_, gain=0.42)
        bt += 2.0
    return kicks


all_kicks = []

# ----- 0–6 Intro -----
add("fx", crackle(6.0), 0, gain=0.25)
add("pad", pad(CHORDS[0], 2.0, attack=1.5, cutoff=900), 0, gain=0.6, rev=0.3)
for s in (1.0, 1.5, 2.0, 2.5):
    add("fx", shutter(), s, gain=0.55, pan=0.2)
# gedämpfter Groove ("aus dem Club nebenan"), wird später gefiltert
intro_kicks = groove(1.0, 5.0, b_drums="intro", b_keys="intro", b_bass="intro", clap_on=True, perc=False)
add("fx", riser(1.0, 6000), 4.9, gain=0.3)
# "Du" "hast" "deinen." – offene Akkord-Hits
for k, s in enumerate((5.0, 5.25, 5.5)):
    add("keys", chord_ep(CHORDS[[0, 1, 2][k]], 0.2, 1.0), s, gain=0.5, rev=0.4)
    add("drums", kick(0.8), s)
for i, s in enumerate(np.arange(5.0, 5.875, 0.0625)):
    add("drums", snare(0.1), s, gain=0.08 + 0.35 * i / 14, rev=0.15)
add("fx", reverse_cym(0.9), 4.975, gain=0.4)

# ----- 6–15 Drop / Hero / Triptychon -----
add("fx", impact(1.2), 6.0, gain=0.95, rev=0.35)
add("drums", hat(True), 6.0, gain=0.4, rev=0.3)
all_kicks += groove(6.0, 15.0)
add("pad", pad(CHORDS[0], 8.0, attack=0.3, cutoff=2500), 6.0, gain=0.22, rev=0.3)
for s in (8.0, 10.0):
    add("fx", whoosh(0.35, -0.6, 0.6, 600, 8000), s - 0.15, gain=0.35)
add("fx", whoosh(0.7, 0.8, -0.8, 300, 5000), 11.85, gain=0.5, rev=0.2)
add("fx", whoosh(0.6, -0.5, 0.5, 400, 6000), 14.5, gain=0.45, rev=0.2)

# ----- 15–18 Datenblatt (Breakdown) -----
groove(15.0, 17.5, kick_on=False, bass_on=False, clap_on=False, perc=False)
add("pad", pad(CHORDS[2] + [69], 3.0, attack=0.4, cutoff=3000), 15.0, gain=0.35, rev=0.4)
add("bass", bass_note(26 + 12, 2.5), 15.0, gain=0.35)
for c in (15.5, 16.0, 16.5):
    for k in range(10):
        add("fx", tick(), c + 0.15 + k * 0.045, gain=0.10, pan=0.4 if c == 15.5 else -0.4)
    add("fx", chime(84 if c != 16.0 else 81, 1.2), c, gain=0.06, rev=0.6)
add("fx", riser(1.5), 16.5, gain=0.45, rev=0.2)
for i, s in enumerate(np.arange(17.0, 18.0, 0.125)):
    add("drums", snare(), s, gain=0.12 + 0.4 * i / 8, rev=0.2)
for i, s in enumerate(np.arange(17.5, 18.0, 0.0625)):
    add("drums", snare(0.1), s, gain=0.3 + 0.2 * i / 8, rev=0.2)

# ----- 18–24 Energie -----
add("fx", impact(1.0), 18.0, gain=0.85, rev=0.35)
all_kicks += groove(18.0, 23.5)
add("fx", impact(0.5), 19.0, gain=0.45, rev=0.3)
add("drums", snare(0.3), 19.0, gain=0.5, rev=0.4)
for s in np.arange(20.0, 21.99, 0.5):
    add("fx", whoosh(0.18, -0.4, 0.4, 1500, 9000), s - 0.06, gain=0.25)
for s in np.arange(22.0, 23.5, 0.25):
    add("fx", shutter(), s, gain=0.3, pan=0.3)
# Stutter
for s in np.arange(23.5, 23.75, 0.03125):
    add("drums", kick(0.6), s)
    add("drums", snare(0.05), s, gain=0.25)
add("fx", reverse_cym(0.75), 23.0, gain=0.35)

# ----- 24–30 Endcard -----
add("fx", impact(1.4), 24.0, gain=1.0, rev=0.45)
add("keys", chord_ep(CHORDS[0], 2.5, 1.0), 24.0, gain=0.45, rev=0.5)
add("pad", pad(CHORDS[0] + [72], 5.4, attack=0.05, release=2.0, cutoff=2600), 24.0, gain=1.6, rev=0.5)
add("bass", bass_note(29 + 12, 3.0), 24.0, gain=0.5)
for i, (n, s) in enumerate(((77, 24.8), (81, 25.0), (84, 25.2), (88, 25.4), (86, 25.6))):
    add("fx", chime(n, 2.5), s, gain=0.09, pan=(-0.4, 0.4)[i % 2], rev=0.7)
add("fx", impact(0.5), 24.8, gain=0.3, rev=0.4)
add("keys", chord_ep([60, 64, 65, 69, 72], 2.0, 0.6), 26.0, gain=0.3, rev=0.6)
add("keys", chord_ep(CHORDS[0], 2.0, 0.5), 28.0, gain=0.3, rev=0.7)

# ---------------- mix ----------------
t = np.arange(N) / SR

# Intro-Bus: Tiefpass öffnet sich von 280 Hz bis 1.6 kHz (Blockverarbeitung)
x = bus["intro"]
y = np.zeros_like(x)
blk = 512
zi = None
for s0 in range(0, N, blk):
    tc = s0 / SR
    fc = 280 * (1.6e3 / 280) ** np.clip((tc - 1.0) / 4.0, 0, 1) ** 2
    sos = signal.butter(2, fc, 'lowpass', fs=SR, output='sos')
    if zi is None:
        zi = np.zeros((sos.shape[0], 2, 2))
    y[:, s0:s0 + blk], zi = signal.sosfilt(sos, x[:, s0:s0 + blk], axis=-1, zi=zi)
bus["intro"] = y * 0.55

# Sidechain
duck = np.ones(N)
for k in all_kicks + intro_kicks:
    i0 = int(k * SR)
    seg_ = np.arange(min(int(0.35 * SR), N - i0)) / SR
    duck[i0:i0 + len(seg_)] = np.minimum(duck[i0:i0 + len(seg_)], 1 - 0.6 * np.exp(-seg_ / 0.08))
for b in ("keys", "pad", "bass"):
    bus[b] *= duck

# Pre-Drop-Pause & Stutter-Pause
for a, b in ((5.875, 6.0), (23.75, 24.0)):
    m = (t >= a) & (t < b)
    for k in BUS_NAMES:
        if k != "fx" or a > 23:
            bus[k][:, m] *= 0
    send[:, m] *= 0.2

# Reverb
ti = tt(2.4)
irs = []
for c in range(2):
    ir = rng.standard_normal(len(ti)) * np.exp(-ti / 0.42)
    for d_, g_ in ((0.011, 0.6), (0.017, 0.45), (0.023 + 0.004 * c, 0.4), (0.031, 0.3)):
        ir[int(d_ * SR)] += g_ * 6
    ir = bp(ir, 250, 6500)
    ir[: int(0.008 * SR)] = 0
    irs.append(ir / np.sqrt(np.sum(ir ** 2)))
m = 1 << int(np.ceil(np.log2(N + len(ti))))
wet = np.vstack([np.fft.irfft(np.fft.rfft(send[c], m) * np.fft.rfft(irs[c], m), m)[:N] for c in range(2)])

mix = (bus["drums"] * 1.0 + bus["bass"] * 0.95 + bus["keys"] * 0.9 + bus["pad"] * 0.8
       + bus["fx"] * 1.0 + bus["intro"] + wet * 0.5)
mix = bp(mix, lo=28)
# leichte "Glue"-Kompression (RMS-Folger) + Sättigung
env = np.sqrt(signal.sosfilt(signal.butter(1, 8, 'lowpass', fs=SR, output='sos'), np.mean(mix ** 2, axis=0)) + 1e-9)
gr = np.minimum(1, (0.35 / env) ** 0.35)
mix *= gr
fo = np.clip((DUR - 0.3 - t) / 1.8, 0, 1)
mix *= fo
mix = np.tanh(mix * 1.25) / np.tanh(1.25)
mix /= np.max(np.abs(mix)) / 0.92

pcm = (np.clip(mix.T, -1, 1) * 32767).astype("<i2")
with wave.open(sys.argv[1] if len(sys.argv) > 1 else "soundtrack.wav", "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print("ok")
