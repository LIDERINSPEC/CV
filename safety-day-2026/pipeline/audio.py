"""Trilha instrumental, ambiente de usinagem e notificação — sintetizados localmente (sem créditos).

A trilha é discreta e acolhedora (piano + pad, ~72 BPM). O ambiente industrial é reduzido
automaticamente durante as falas (ducking guiado pelas legendas de cues.json).
"""
from __future__ import annotations

import numpy as np
from scipy.signal import butter, fftconvolve, sosfilt

SR = 48000


def _t(n):
    return np.arange(n) / SR


def _reverb(x, seconds=2.4, mix=0.28, seed=7):
    rng = np.random.default_rng(seed)
    n = int(SR * seconds)
    ir = rng.standard_normal(n) * np.exp(-_t(n) * 5.5 / seconds * 2.2)
    ir = sosfilt(butter(2, 5200, "low", fs=SR, output="sos"), ir)
    ir /= np.sqrt((ir ** 2).sum())
    wet = fftconvolve(x, ir)[: len(x)]
    return x * (1 - mix) + wet * mix * 2.2


def _note(freq, dur, vel=0.5):
    n = int(SR * dur)
    t = _t(n)
    partials = [(1, 1.0), (2, 0.42), (3, 0.18), (4, 0.09), (5, 0.04)]
    s = np.zeros(n)
    for k, a in partials:
        inh = 1 + 0.0004 * k * k
        s += a * np.sin(2 * np.pi * freq * k * inh * t) * np.exp(-t * (1.6 + 0.9 * k))
    att = np.minimum(t / 0.006, 1)
    return s * att * vel


def _pad(freqs, dur):
    n = int(SR * dur)
    t = _t(n)
    s = np.zeros(n)
    for f in freqs:
        for det in (-0.12, 0.0, 0.11):
            ph = 2 * np.pi * f * (1 + det / 100) * t
            s += np.sin(ph) + 0.25 * np.sin(2 * ph) + 0.1 * np.sin(3 * ph)
    env = np.minimum(t / 1.2, 1) * np.minimum((dur - t) / 1.2, 1)
    return s * np.clip(env, 0, 1) / (len(freqs) * 3)


def _add(out, start, x):
    """Soma x em out a partir de start, recortando o que passar do fim."""
    if start < 0:
        x, start = x[-start:], 0
    if start >= len(out):
        return
    x = x[: len(out) - start]
    out[start: start + len(x)] += x


def midi(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def music(duration: float) -> np.ndarray:
    """Progressão Cmaj7 – G/B – Am7 – Fmaj7 (I–V–vi–IV), resolve em C no final."""
    bpm = 72
    beat = 60 / bpm
    bar = beat * 4
    n = int(SR * duration)
    out = np.zeros(n + SR * 4)
    chords = [
        ([48, 55, 59, 64], [60, 64, 67, 71]),   # Cmaj7
        ([47, 55, 62, 67], [59, 62, 67, 74]),   # G/B
        ([45, 52, 60, 64], [57, 60, 64, 69]),   # Am7
        ([41, 48, 57, 64], [57, 60, 65, 69]),   # Fmaj7
    ]
    rng = np.random.default_rng(3)
    t0, i = 0.0, 0
    end_music = duration - 0.4
    while t0 < end_music - bar * 0.5:
        bass, arp = chords[i % 4]
        last = t0 + bar >= end_music - 0.1
        if last:
            bass, arp = [36, 48, 55, 64], [60, 64, 67, 72]
        st = int(t0 * SR)
        p = _pad([midi(m) for m in bass[1:]], bar + 1.5) * 0.55
        _add(out, st, p)
        b = _note(midi(bass[0]), bar + 0.5, 0.42)
        _add(out, st, b)
        # Arpejo suave em colcheias, densidade cresce depois do convite (50 s).
        steps = 8 if t0 > 50 else 4
        for k in range(steps):
            if last and k > 0:
                break
            m = arp[(k * 2 + i) % 4] if steps == 8 else arp[k % 4]
            ts = t0 + k * (bar / steps) + rng.uniform(-0.008, 0.008)
            nt = _note(midi(m), 2.6 if not last else 6.0, 0.24 + 0.05 * rng.random())
            s = int(ts * SR)
            _add(out, s, nt)
        t0 += bar
        i += 1
    out = out[:n]
    out = _reverb(out, 2.8, 0.32)
    t = _t(n)
    # Entrada suave, leve crescimento no convite e no final, fade-out no último segundo.
    env = np.clip(t / 2.5, 0, 1) * (0.75 + 0.25 * np.clip((t - 48) / 4, 0, 1))
    env *= np.clip((duration - t) / 1.2, 0, 1)
    return out * env


def ambience(duration: float) -> np.ndarray:
    """Usinagem ao fundo: zumbido de spindle, ventilação e corte abafado."""
    n = int(SR * duration)
    t = _t(n)
    rng = np.random.default_rng(11)
    noise = rng.standard_normal(n)
    air = sosfilt(butter(2, [180, 1400], "band", fs=SR, output="sos"), noise) * 0.6
    rumble = sosfilt(butter(2, 120, "low", fs=SR, output="sos"), rng.standard_normal(n)) * 1.4
    spindle_f = 186 + 3 * np.sin(2 * np.pi * 0.07 * t)
    spindle = 0.10 * np.sin(2 * np.pi * np.cumsum(spindle_f) / SR) + 0.05 * np.sin(4 * np.pi * np.cumsum(spindle_f) / SR)
    cut = sosfilt(butter(2, [2500, 6000], "band", fs=SR, output="sos"), rng.standard_normal(n))
    cut *= 0.12 * (0.5 + 0.5 * np.sin(2 * np.pi * 0.21 * t) ** 2)
    x = air + rumble + spindle + cut
    return x / np.max(np.abs(x)) * 0.5


def notification(at: float, duration: float) -> np.ndarray:
    n = int(SR * duration)
    out = np.zeros(n)
    # Vibração (dois pulsos) + toque curto e discreto.
    for k in range(2):
        s = int((at + k * 0.32) * SR)
        m = int(0.22 * SR)
        tt = _t(m)
        buzz = np.sign(np.sin(2 * np.pi * 165 * tt)) * 0.5 + np.sin(2 * np.pi * 330 * tt) * 0.3
        buzz = sosfilt(butter(2, 900, "low", fs=SR, output="sos"), buzz)
        buzz *= np.minimum(tt / 0.01, 1) * np.minimum((0.22 - tt) / 0.02, 1)
        _add(out, s, buzz * 0.55)
    s = int((at + 0.05) * SR)
    for f, d, a in [(1318.5, 0.0, 0.22), (1975.5, 0.09, 0.18)]:
        nt = _note(f, 0.8, a)
        st = s + int(d * SR)
        _add(out, st, nt)
    return out


def speech_envelope(subs, duration: float, attack=0.25, release=0.45) -> np.ndarray:
    """1.0 durante falas, 0.0 fora; transições suaves para o ducking."""
    n = int(SR * duration)
    env = np.zeros(n)
    for s in subs:
        a, b = int((s["start"] - attack) * SR), int((s["end"] + release) * SR)
        env[max(a, 0): min(b, n)] = 1
    k = int(0.3 * SR)
    win = np.hanning(k)
    win /= win.sum()
    return np.clip(np.convolve(env, win, mode="same"), 0, 1)


def mix(cues: dict, dialogue: np.ndarray | None) -> np.ndarray:
    dur = cues["duration"]
    n = int(SR * dur)
    subs = cues["subtitles"]
    sp = speech_envelope(subs, dur)
    t = _t(n)
    end_t = cues["endcard"]["start"]

    amb = ambience(dur)
    amb_gain = 10 ** (-24 / 20) * (1 - 0.6 * sp)            # ambiente baixo, ~-8 dB nas falas
    amb_gain *= np.clip((end_t - 0.3 - t) / 1.0, 0, 1)        # some na tela final
    amb_gain *= np.clip(t / 0.8, 0, 1)

    mus = music(dur)
    mus_gain = 10 ** (-17 / 20) * (1 - 0.45 * sp)            # trilha recua sob as vozes
    mus_gain *= 1 + 0.6 * np.clip((t - end_t + 0.6) / 0.8, 0, 1)

    out = amb * amb_gain + mus * mus_gain + notification(cues["audio"]["notification_at"], dur) * 0.5
    if dialogue is not None:
        d = np.zeros(n)
        d[: min(len(dialogue), n)] = dialogue[:n]
        out += d
    out = np.tanh(out * 1.2) / 1.2
    return np.stack([out, out], axis=1).astype(np.float32)
