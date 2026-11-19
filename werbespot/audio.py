"""Synthetischer Soundtrack für den 30s Spot (120 BPM, synchron zu ad.html).
python3 audio.py out.wav"""
import sys, wave
import numpy as np

SR = 48000
DUR = 30.0
N = int(SR * DUR)
rng = np.random.default_rng(7)

buses = {k: np.zeros((2, N)) for k in ("music", "drums", "fx")}
send = np.zeros((2, N))  # reverb send


def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def filt(x, lp=None, hp=None, order=2):
    n = len(x)
    m = 1 << int(np.ceil(np.log2(n + SR // 4)))
    X = np.fft.rfft(x, m)
    f = np.fft.rfftfreq(m, 1 / SR)
    Hm = np.ones_like(f)
    if lp:
        Hm *= 1 / np.sqrt(1 + (f / lp) ** (2 * order))
    if hp:
        Hm *= 1 / np.sqrt(1 + (hp / np.maximum(f, 1e-3)) ** (2 * order))
    return np.fft.irfft(X * Hm, m)[:n]


def add(bus, sig, start, gain=1.0, pan=0.0, rev=0.0):
    sig = np.atleast_2d(sig)
    if sig.shape[0] == 1:
        l, r = np.cos((pan + 1) * np.pi / 4) * 1.414, np.sin((pan + 1) * np.pi / 4) * 1.414
        sig = np.vstack([sig[0] * l, sig[0] * r])
    i = int(round(start * SR))
    if i < 0:
        sig = sig[:, -i:]
        i = 0
    n = min(sig.shape[1], N - i)
    if n <= 0:
        return
    buses[bus][:, i:i + n] += sig[:, :n] * gain
    if rev:
        send[:, i:i + n] += sig[:, :n] * gain * rev


def tt(d):
    return np.arange(int(d * SR)) / SR


def fade(s, a=0.005, r=0.01):
    na, nr = max(1, int(a * SR)), max(1, int(r * SR))
    s = s.copy()
    s[:na] *= np.linspace(0, 1, na)
    s[-nr:] *= np.linspace(1, 0, nr)
    return s


# ---------------- instruments ----------------
def kick(f0=160, f1=44, decay=0.30, d=0.6):
    t = tt(d)
    f = f1 + (f0 - f1) * np.exp(-t * 30)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / decay)
    click = filt(rng.standard_normal(len(t)) * np.exp(-t * 400), hp=2500) * 0.25
    return fade(np.tanh((s + click) * 1.6))


def clap():
    t = tt(0.5)
    env = np.zeros_like(t)
    for k, off in enumerate((0, 0.011, 0.023)):
        m = t >= off
        env[m] += np.exp(-(t[m] - off) * 180) * (0.8 if k < 2 else 1)
    m = t >= 0.023
    env[m] += 0.35 * np.exp(-(t[m] - 0.023) * 16)
    s = filt(rng.standard_normal(len(t)), lp=6000, hp=900) * env
    return fade(s)


def snare(d=0.25):
    t = tt(d)
    n = filt(rng.standard_normal(len(t)), lp=7000, hp=1500) * np.exp(-t * 22)
    b = np.sin(2 * np.pi * 190 * t) * np.exp(-t * 35) * 0.6
    return fade(n + b)


def hat(open_=False):
    t = tt(0.25 if open_ else 0.07)
    s = filt(rng.standard_normal(len(t)), hp=7500) * np.exp(-t * (14 if open_ else 70))
    return fade(s)


def bass(note, d):
    t = tt(d)
    f = midi(note)
    ph = 2 * np.pi * f * t
    s = np.sin(ph) + 0.45 * np.sin(2 * ph) + 0.2 * np.sin(3 * ph) + 0.08 * np.sin(4 * ph)
    env = np.minimum(1, t / 0.004) * (0.55 + 0.45 * np.exp(-t * 9))
    return fade(np.tanh(s * env * 1.3), 0.002, 0.02)


def pad(notes, d, attack=1.2, release=1.4, bright=1.0):
    t = tt(d + release)
    out = np.zeros((2, len(t)))
    for j, n in enumerate(notes):
        for det, pan in ((-7, -0.6), (0, 0.0), (7, 0.6)):
            f = midi(n) * 2 ** (det / 1200)
            s = np.zeros_like(t)
            for h in range(1, 8):
                if f * h > 9000:
                    break
                s += np.sin(2 * np.pi * f * h * t + rng.uniform(0, 6.28)) / h ** (1.6 - 0.4 * bright)
            s *= 1 + 0.15 * np.sin(2 * np.pi * (0.2 + 0.07 * j) * t)
            l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
            out[0] += s * l
            out[1] += s * r
    env = np.minimum(1, t / attack) * np.where(t > d, np.exp(-(t - d) / (release / 4)), 1)
    return out * env / (len(notes) * 3)


def impact(size=1.0):
    d = 2.5 * size
    t = tt(d)
    f = 30 + 70 * np.exp(-t * 6)
    sub = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / (0.55 * size))
    body = filt(rng.standard_normal(len(t)), lp=400) * np.exp(-t * 9) * 1.5
    crash = filt(rng.standard_normal(len(t)), hp=500, lp=10000) * np.exp(-t / (0.35 * size)) * 0.5
    return fade(np.tanh((sub * 1.2 + body + crash) * 1.2), 0.001, 0.1)


def riser(d):
    t = tt(d)
    p = t / d
    noise = rng.standard_normal(len(t))
    centers = [300, 600, 1200, 2400, 4800, 9000]
    s = np.zeros_like(t)
    for i, c in enumerate(centers):
        band = filt(noise, lp=c * 1.4, hp=c / 1.4)
        w = np.exp(-((np.log2(c / 300) - p * 5) ** 2) / 1.2)
        s += band * w
    s = s / np.max(np.abs(s)) * p ** 2
    sweep = np.sin(2 * np.pi * np.cumsum(180 * 2 ** (p * 2.6)) / SR) * p ** 3 * 0.25
    return fade(s + sweep, 0.05, 0.004)


def reverse_cym(d):
    t = tt(d)
    p = t / d
    return fade(filt(rng.standard_normal(len(t)), hp=3500) * p ** 4, 0.01, 0.004)


def whoosh(d, pan_from=-0.8, pan_to=0.8, lo=350, hi=3500):
    t = tt(d)
    p = t / d
    s = filt(rng.standard_normal(len(t)), lp=hi, hp=lo) * np.sin(np.pi * p) ** 2
    pan = pan_from + (pan_to - pan_from) * p
    return np.vstack([s * np.cos((pan + 1) * np.pi / 4), s * np.sin((pan + 1) * np.pi / 4)]) * 1.4


def heartbeat():
    t = tt(0.6)
    def thump(f, a):
        return np.sin(2 * np.pi * f * t) * np.exp(-t * 16) * np.minimum(1, t / 0.008) * a
    lub = thump(52, 1.0)
    dub = np.zeros_like(t)
    o = int(0.2 * SR)
    dub[o:] = thump(60, 0.7)[:len(t) - o]
    return fade(filt(lub + dub, lp=180) * 2.2)


def ping(note, d=2.0):
    t = tt(d)
    f = midi(note)
    s = (np.sin(2 * np.pi * f * t) * np.exp(-t * 2.2) + 0.4 * np.sin(2 * np.pi * f * 2.0 * t) * np.exp(-t * 4)
         + 0.15 * np.sin(2 * np.pi * f * 3.01 * t) * np.exp(-t * 6))
    return fade(s * np.minimum(1, t / 0.003), 0.002, 0.2)


# ---------------- arrangement ----------------
# Pads (D-Moll -> F-Dur Auflösung am Ende)
chords = [
    (0.0, 8.0, [50, 57, 62, 64, 65], 3.0, 0.5),   # Dm(add9)
    (8.0, 5.0, [46, 53, 58, 62, 65], 0.4, 0.8),   # Bb
    (13.0, 3.0, [41, 53, 60, 65, 69], 0.5, 0.8),  # F
    (16.0, 2.0, [48, 55, 60, 64, 67], 0.5, 0.9),  # C
    (18.0, 2.0, [50, 57, 62, 65, 69], 0.05, 1.0),  # Dm
    (20.0, 2.0, [46, 58, 62, 65, 70], 0.05, 1.0),  # Bb
    (22.0, 2.0, [48, 60, 64, 67, 72], 0.05, 1.0),  # C
    (24.0, 5.5, [41, 48, 57, 64, 67, 72], 0.05, 0.9),  # Fmaj9
]
for st, d, notes, att, br in chords:
    g = 0.22 if st < 8 else 0.42
    add("music", pad(notes, d, attack=att, release=1.6, bright=br), st, gain=g, rev=0.35)
# Sub-Drone im Intro
t0 = tt(8.5)
add("music", fade(np.sin(2 * np.pi * midi(38) * t0) * np.minimum(1, t0 / 3) * 0.25, 0.01, 0.6), 0)

# Herzschlag
for k in range(5):
    add("fx", heartbeat(), 0.5 + k * 1.0, gain=0.38 + 0.03 * k)

# Impacts
for h, size, g in ((5.0, 0.8, 0.75), (8.0, 1.2, 0.9), (18.0, 1.1, 0.8), (20.0, 0.6, 0.35), (22.0, 0.6, 0.35), (24.0, 1.4, 1.0)):
    add("fx", impact(size), h, gain=g, rev=0.4)

# Riser / Reverse-Becken
add("fx", riser(2.0), 6.0, gain=0.45, rev=0.2)
add("fx", reverse_cym(1.0), 7.0, gain=0.35)
add("fx", riser(1.5), 16.5, gain=0.4, rev=0.2)
add("fx", reverse_cym(0.8), 17.2, gain=0.3)
add("fx", reverse_cym(0.5), 23.5, gain=0.35)

# Whooshes
add("fx", whoosh(0.9, -0.9, 0.3), 7.95, gain=0.6, rev=0.2)
add("fx", whoosh(1.1, 0.0, 0.0, 200, 1800), 13.0, gain=0.35, rev=0.3)
add("fx", whoosh(0.6, 0.6, -0.6, 500, 5000), 17.4, gain=0.3, rev=0.2)

# GEL-Pulse (Close-up)
for h in (14.5, 15.5, 16.5):
    add("drums", kick(110, 40, 0.22), h, gain=0.55)
    add("fx", ping(84, 1.6), h, gain=0.10, pan=0.3, rev=0.6)
    add("fx", ping(91, 1.2), h + 0.01, gain=0.05, pan=-0.3, rev=0.6)

# Bass-Pulse
def bass_line(start, end, root, octave_pump=False, gain=0.3):
    k = 0
    tb = start
    while tb < end - 1e-6:
        n = root + (12 if (octave_pump and k % 2) else 0)
        add("music", bass(n, 0.23), tb, gain=gain)
        tb += 0.25
        k += 1

bass_line(10.0, 13.0, 34, gain=0.16)
bass_line(13.0, 16.0, 41 - 12 + 12, gain=0.2)
bass_line(16.0, 17.0, 36, gain=0.2)
bass_line(18.0, 20.0, 38, True, 0.3)
bass_line(20.0, 22.0, 34, True, 0.3)
bass_line(22.0, 23.5, 36, True, 0.3)

# Drums
kicks = []
for tb in np.arange(13.0, 16.01, 1.0):
    kicks.append(tb)
    add("drums", kick(), tb, gain=0.45)
for tb in np.arange(18.0, 23.49, 0.5):
    kicks.append(tb)
    add("drums", kick(), tb, gain=1.0)
for tb in np.arange(18.5, 23.49, 1.0):
    add("drums", clap(), tb, gain=0.6, rev=0.25)
vel = [0.30, 0.15, 0.55, 0.15]
for i, tb in enumerate(np.arange(18.0, 23.49, 0.125)):
    add("drums", hat(), tb, gain=vel[i % 4] * 0.5, pan=0.25)
for tb in np.arange(18.25, 23.49, 0.5):
    add("drums", hat(True), tb, gain=0.12, pan=-0.2, rev=0.1)
for tb in np.arange(10.25, 16.49, 0.5):
    add("drums", hat(), tb, gain=0.12 if tb < 13 else 0.2, pan=0.3)
# Snare-Build vor dem Drop
for a, b, step in ((16.5, 17.0, 0.5), (17.0, 17.5, 0.25), (17.5, 18.0, 0.125)):
    for tb in np.arange(a, b - 1e-6, step):
        add("drums", snare(), tb, gain=0.15 + 0.45 * (tb - 16.5) / 1.5, rev=0.2)
for tb in np.arange(23.5, 24.0 - 1e-6, 0.0625):
    add("drums", snare(0.12), tb, gain=0.15 + 0.4 * (tb - 23.5) / 0.5, rev=0.2)

# Endcard: Glocken-Arpeggio
for i, (n, tb) in enumerate(((77, 24.6), (81, 25.0), (84, 25.4), (88, 25.8), (84, 26.6), (89, 27.4))):
    add("music", ping(n, 2.5), tb, gain=0.10, pan=(-0.4, 0.4)[i % 2], rev=0.7)

# ---------------- mix ----------------
t = np.arange(N) / SR
duck = np.ones(N)
for k in kicks:
    m = (t >= k) & (t < k + 0.4)
    duck[m] = np.minimum(duck[m], 1 - 0.55 * np.exp(-(t[m] - k) / 0.09))
buses["music"] *= duck

# reverb (synthetic stereo IR)
ird = 2.8
ti = tt(ird)
irs = []
for _ in range(2):
    ir = rng.standard_normal(len(ti)) * np.exp(-ti / 0.55)
    ir = filt(ir, lp=5500, hp=200)
    ir[: int(0.02 * SR)] = 0
    irs.append(ir / np.sqrt(np.sum(ir ** 2)))
m = 1 << int(np.ceil(np.log2(N + len(ti))))
wet = np.vstack([np.fft.irfft(np.fft.rfft(send[c], m) * np.fft.rfft(irs[c], m), m)[:N] for c in range(2)])

mix = buses["music"] + buses["drums"] + buses["fx"] + wet * 0.55
# master fade-out
fo = np.clip((DUR - 0.4 - t) / 1.6, 0, 1)
mix *= fo
mix = filt(mix[0], hp=25)[None, :], filt(mix[1], hp=25)[None, :]
mix = np.vstack(mix)
mix = np.tanh(mix * 1.1) / np.tanh(1.1)
mix /= np.max(np.abs(mix)) / 0.9

pcm = (np.clip(mix.T, -1, 1) * 32767).astype("<i2")
with wave.open(sys.argv[1] if len(sys.argv) > 1 else "soundtrack.wav", "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print("ok")
