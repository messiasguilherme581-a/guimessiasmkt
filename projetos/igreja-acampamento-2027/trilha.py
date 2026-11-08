#!/usr/bin/env python3
"""Trilha original + desenho de som do Reels "Acampamento 2027".

120 BPM (1 tempo = 0,5 s), sincronizada com os cortes do render.py.
Gera dois WAVs (48 kHz, estéreo):
  - trilha_completa.wav : beat + baixo + pad + pluck + efeitos + som ambiente dos vídeos
  - trilha_sem_musica.wav: só efeitos + som ambiente (pra usar música do próprio Instagram/TikTok)

Tudo sintetizado aqui (sem samples de terceiros) → livre de direitos autorais.
"""
from __future__ import annotations

import os
import subprocess

import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve

SR = 48000
DUR = 20.0
N = int(SR * DUR)
BEAT = 0.5
STEP = BEAT / 4  # semicolcheia
rng = np.random.default_rng(2027)

HERE = os.path.dirname(os.path.abspath(__file__))


def midi(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def t_arr(dur):
    return np.arange(int(dur * SR)) / SR


def filt(x, kind, f, order=2):
    sos = butter(order, f, btype=kind, fs=SR, output="sos")
    return sosfilt(sos, x)


def place(buf, sig, t0, gain=1.0, pan=0.0):
    """Mixa sinal mono/estéreo no buffer estéreo a partir de t0 (s)."""
    i = int(round(t0 * SR))
    if i >= buf.shape[1]:
        return
    if sig.ndim == 1:
        l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
        sig = np.stack([sig * l * 1.414, sig * r * 1.414])
    n = min(sig.shape[1], buf.shape[1] - i)
    if i < 0:
        sig, n = sig[:, -i:], min(sig.shape[1] + i, buf.shape[1])
        i = 0
    buf[:, i:i + n] += sig[:, :n] * gain


# ------------------------------------------------------------------ instrumentos
def kick(dur=0.5):
    t = t_arr(dur)
    f = 46 + 120 * np.exp(-t * 32)
    ph = 2 * np.pi * np.cumsum(f) / SR
    body = np.sin(ph) * np.exp(-t * 6.5)
    click = filt(rng.standard_normal(len(t)), "highpass", 2500) * np.exp(-t * 400) * 0.35
    return np.tanh((body + click) * 1.8) * 0.9


def clap(dur=0.6):
    t = t_arr(dur)
    n = rng.standard_normal(len(t))
    env = np.zeros_like(t)
    for k, d in enumerate([0, 0.011, 0.022]):
        env += np.where(t >= d, np.exp(-(t - d) * 320), 0) * (0.8 + 0.1 * k)
    env += np.where(t >= 0.03, np.exp(-(t - 0.03) * 16), 0) * 0.55
    return filt(n * env, "bandpass", [900, 5200]) * 1.6


def snare(dur=0.35, tone=190):
    t = t_arr(dur)
    nz = filt(rng.standard_normal(len(t)), "bandpass", [1500, 9000]) * np.exp(-t * 26)
    tn = np.sin(2 * np.pi * tone * t) * np.exp(-t * 34)
    return nz * 0.9 + tn * 0.6


def hat(dur=0.06, open_=False):
    if open_:
        dur = 0.4
    t = t_arr(dur)
    n = filt(rng.standard_normal(len(t)), "highpass", 7500)
    return n * np.exp(-t * (11 if open_ else 85))


def crash(dur=2.2):
    t = t_arr(dur)
    n = filt(rng.standard_normal(len(t)), "highpass", 4200) * np.exp(-t * 2.2)
    metal = sum(np.sin(2 * np.pi * f * t + rng.uniform(0, 6)) for f in (3127, 4211, 5333, 6719)) * 0.05
    return (n + metal * np.exp(-t * 3)) * 0.8


def bass808(freq, dur):
    t = t_arr(dur)
    f = freq * (1 + 0.5 * np.exp(-t * 40))
    ph = 2 * np.pi * np.cumsum(f) / SR
    env = np.minimum(1, t / 0.004) * np.exp(-t * 1.1)
    rel = np.clip((dur - t) / 0.03, 0, 1)
    x = np.sin(ph) * env * rel
    # saturação = harmônicos audíveis no alto-falante do celular
    return np.tanh(x * 2.4) * 0.7 + np.sin(2 * ph) * env * rel * 0.12


def saw(freq, t, detune_cents=0.0, nh_max=60):
    f = freq * 2 ** (detune_cents / 1200)
    nh = int(min(nh_max, 7000 // f))
    ph0 = rng.uniform(0, 2 * np.pi)
    return sum(np.sin(2 * np.pi * k * f * t + ph0 * k) / k for k in range(1, nh + 1)) * 0.6


def pad_chord(notes, dur, att=0.35, rel=0.6):
    t = t_arr(dur + rel)
    L = np.zeros_like(t)
    R = np.zeros_like(t)
    for m in notes:
        f = midi(m)
        L += saw(f, t, -9) + saw(f, t, 4) * 0.7
        R += saw(f, t, 9) + saw(f, t, -4) * 0.7
    env = np.minimum(1, t / att) * np.clip((dur + rel - t) / rel, 0, 1)
    L, R = filt(L, "lowpass", 1700) * env, filt(R, "lowpass", 1700) * env
    return np.stack([L, R]) / (len(notes) * 1.6)


def pluck(freq, dur=0.5):
    t = t_arr(dur)
    x = sum(np.sin(2 * np.pi * k * freq * t) / k * np.exp(-t * (4 + k * 2.2)) for k in range(1, 12))
    return x * np.minimum(1, t / 0.002) * 0.7


def impact(dur=2.4, size=1.0):
    t = t_arr(dur)
    f = 30 + 52 * np.exp(-t * 5)
    sub = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 1.9)
    crack = filt(rng.standard_normal(len(t)), "lowpass", 3200) * np.exp(-t * 9) * 0.7
    body = filt(rng.standard_normal(len(t)), "bandpass", [80, 400]) * np.exp(-t * 5) * 0.6
    return np.tanh((sub * 1.4 + crack + body) * 1.3) * size


def whoosh(dur=0.7, rev=False):
    t = t_arr(dur)
    n = rng.standard_normal(len(t))
    lo = filt(n, "bandpass", [250, 1200])
    hi = filt(n, "bandpass", [1800, 7000])
    p = t / dur
    env = np.sin(np.pi * p) ** 2
    x = (lo * (1 - p) + hi * p) * env
    return x[::-1] if rev else x


def riser(dur=2.0):
    t = t_arr(dur)
    p = t / dur
    n = filt(rng.standard_normal(len(t)), "highpass", 900) * p ** 2.2
    f = 180 * 2 ** (p * 2.6)
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * p ** 2 * 0.25
    return (n * 0.6 + tone) * np.clip((dur - t) / 0.02, 0, 1)


def reverb(x, secs=1.8, wet=0.25, tone=5000):
    ir_t = t_arr(secs)
    ir = np.stack([
        filt(rng.standard_normal(len(ir_t)), "lowpass", tone) * np.exp(-ir_t * 6.9 / secs),
        filt(rng.standard_normal(len(ir_t)), "lowpass", tone) * np.exp(-ir_t * 6.9 / secs),
    ])
    ir /= np.sqrt((ir ** 2).sum(axis=1, keepdims=True))
    out = np.stack([fftconvolve(x[c], ir[c])[: x.shape[1]] for c in range(2)])
    return x + out * wet


# ------------------------------------------------------------------ arranjo
CHORDS = [  # (início, fim, baixo, notas do pad)
    (2.0, 4.0, 38, [50, 54, 57, 62]),    # D
    (4.0, 6.0, 35, [47, 50, 54, 59]),    # Bm
    (6.0, 8.0, 43, [47, 50, 55, 59]),    # G
    (8.0, 10.0, 40, [52, 55, 59, 64]),   # Em
    (10.0, 12.0, 45, [49, 52, 57, 61]),  # A
    (12.0, 14.0, 38, [50, 54, 57, 62]),  # D
    (14.0, 16.0, 45, [49, 52, 57, 61]),  # A
    (16.0, 18.0, 43, [47, 50, 55, 59]),  # G
    (18.0, 20.0, 38, [50, 54, 57, 62]),  # D
]

IMPACTS = [(0.0, 0.8), (1.0, 1.0), (12.0, 1.15), (19.0, 0.9)]
WHOOSHES = [(1.62, False), (5.62, False), (7.7, False), (14.7, False)]
WORD_HITS = [10.0, 10.5, 11.0, 11.5]


def extract_audio(path, start, dur):
    cmd = ["ffmpeg", "-v", "error", "-ss", str(start), "-t", str(dur), "-i", path,
           "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).T.copy()


def fade(x, fin=0.08, fout=0.3):
    n = x.shape[1]
    env = np.ones(n)
    a, b = int(fin * SR), int(fout * SR)
    env[:a] = np.linspace(0, 1, a)
    env[n - b:] = np.linspace(1, 0, b)
    return x * env


def build(music=True):
    sfx = np.zeros((2, N))
    mus = np.zeros((2, N))
    nat = np.zeros((2, N))

    # ---- som ambiente dos vídeos (torcida da gincana / palmas da adoração)
    g = extract_audio(os.path.join(HERE, "assets", "gincana.mp4"), 0.4, 4.0)
    nat_g = fade(filt(g, "highpass", 120), 0.05, 0.35)
    place(nat, nat_g, 2.0, 0.55)
    a = extract_audio(os.path.join(HERE, "assets", "adoracao.mp4"), 0.4, 4.0)
    a = filt(a, "highpass", 150)
    a = a / (np.abs(a).max() + 1e-9)
    place(nat, fade(a, 0.4, 0.6), 6.0, 0.6)

    # ---- efeitos
    for t0, s in IMPACTS:
        place(sfx, impact(size=s), t0, 0.95)
    for t0, rev in WHOOSHES:
        w = whoosh(0.75, rev)
        place(sfx, w, t0, 0.32, pan=-0.5)
        place(sfx, w, t0 + 0.03, 0.32, pan=0.5)
    place(sfx, riser(2.0), 10.0, 0.33)
    for t0 in WORD_HITS:
        place(sfx, impact(0.6, 0.45), t0, 0.6)
    place(sfx, whoosh(0.5, True), 11.5, 0.3)
    sfx = reverb(sfx, 1.6, 0.22)

    if music:
        drums = np.zeros((2, N))
        # crashes nas viradas
        for t0 in (2.0, 12.0, 19.0):
            place(drums, crash(), t0, 0.28, pan=0.15)
        # grooves
        def groove(t_start, t_end, full):
            kicks = [0, 6, 8, 11] if full else [0, 6, 8]
            bar = 0
            tb = t_start
            def place_(buf, sig, t0, g, pan=0.0):
                if t0 < t_end - 1e-6:
                    place(buf, sig, t0, g, pan)
            while tb < t_end - 1e-6:
                for s in kicks:
                    place_(drums, kick(), tb + s * STEP, 0.95)
                for s in (4, 12):
                    place_(drums, clap(), tb + s * STEP, 0.55)
                    if full:
                        place_(drums, snare(), tb + s * STEP, 0.25)
                for s in range(16):
                    if full or s % 2 == 0:
                        v = [1.0, 0.45, 0.75, 0.45][s % 4]
                        place_(drums, hat(), tb + s * STEP + (0.006 if s % 2 else 0), 0.2 * v, pan=0.35)
                    if bar % 2 == 1 and s in (13, 15):
                        place_(drums, hat(), tb + s * STEP + STEP / 2, 0.12, pan=0.35)
                place_(drums, hat(open_=True), tb + 10 * STEP, 0.09, pan=-0.3)
                tb += 2.0
                bar += 1
        groove(2.0, 6.0, False)
        groove(12.0, 19.0, True)
        # pulso suave ("coração") no fim da adoração
        for k in range(4):
            place(drums, kick(), 8.0 + k * 0.5, 0.35 if k % 2 == 0 else 0.2)
        # tempo forte final
        place(drums, kick(), 19.0, 1.0)
        # caixa acelerando na subida (10–12 s)
        tt = 10.0
        while tt < 11.875:
            step = 0.25 if tt < 11.0 else (0.125 if tt < 11.5 else 0.0625)
            vel = 0.25 + 0.75 * (tt - 10.0) / 2.0
            place(drums, snare(0.2, 200 + (tt - 10) * 60), tt, 0.42 * vel)
            tt += step
        drums = reverb(drums, 1.1, 0.12)

        # baixo 808 nos kicks; pad + pluck por acorde
        bass = np.zeros((2, N))
        pads = np.zeros((2, N))
        plk = np.zeros((2, N))
        for (c0, c1, root, notes) in CHORDS:
            if 2.0 <= c0 < 6.0 or 12.0 <= c0 < 19.0:
                hits = [0, 6, 8, 11] if c0 >= 12 else [0, 6, 8]
                for i, s in enumerate(hits):
                    t0 = c0 + s * STEP
                    if t0 >= 19.0:
                        continue
                    nxt = c0 + (hits[i + 1] * STEP if i + 1 < len(hits) else 2.0)
                    place(bass, bass808(midi(root), max(0.1, min(nxt, 19.0) - t0)), t0, 0.62)
            if c0 == 18.0:
                place(bass, bass808(midi(root), 1.0), 19.0, 0.7)
            gain = 0.5 if 6.0 <= c0 < 12.0 else 0.2
            place(pads, pad_chord(notes, c1 - c0), c0, gain)
            if c0 >= 12.0 or 6.0 <= c0 < 10.0:
                arp = [notes[0] + 12, notes[1] + 12, notes[2] + 12, notes[3] + 12, notes[2] + 12, notes[1] + 12, notes[3], notes[2] + 12]
                step = 0.25 if c0 >= 12 else 0.5
                k = 0
                t0 = c0
                while t0 < c1 - 1e-6 and t0 < 19.0:
                    p = pluck(midi(arp[k % len(arp)]), 0.6)
                    g = 0.17 if c0 >= 12 else 0.26
                    place(plk, p, t0, g, pan=-0.25)
                    place(plk, p, t0 + 0.014, g * 0.7, pan=0.45)  # Haas: abre o estéreo
                    t0 += step
                    k += 1
        pads = reverb(pads, 2.4, 0.35)
        plk = reverb(plk, 1.8, 0.3)

        # sidechain: pad e pluck "respiram" com o kick no drop
        sc = np.ones(N)
        tt = 12.0
        while tt < 19.0:
            for s in (0, 6, 8, 11):
                i = int((tt + s * STEP) * SR)
                d = np.arange(int(0.25 * SR)) / SR
                seg = 1 - 0.6 * np.exp(-d * 14)
                j = min(N, i + len(seg))
                sc[i:j] = np.minimum(sc[i:j], seg[: j - i])
            tt += 2.0
        mus = drums + bass + (pads + plk) * sc

    mix = mus + sfx + nat
    mix = filt(mix, "highpass", 28)
    mix = np.tanh(mix * 1.15) / np.tanh(1.15)
    # fim: cauda curta
    mix[:, int(19.85 * SR):] *= np.linspace(1, 0, N - int(19.85 * SR))
    return (mix / (np.abs(mix).max() + 1e-9) * 0.89).astype(np.float32)


def write_wav(path, x, lufs):
    raw = path + ".raw.f32"
    x.T.astype(np.float32).tofile(raw)
    subprocess.run([
        "ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", raw,
        "-af", f"loudnorm=I={lufs}:TP=-1.2:LRA=11", "-ar", str(SR), path,
    ], check=True)
    os.remove(raw)


def main(outdir):
    os.makedirs(outdir, exist_ok=True)
    a = os.path.join(outdir, "trilha_completa.wav")
    b = os.path.join(outdir, "trilha_sem_musica.wav")
    write_wav(a, build(True), -14)
    write_wav(b, build(False), -16)
    return a, b


if __name__ == "__main__":
    print(main(os.path.join(HERE, ".cache")))
