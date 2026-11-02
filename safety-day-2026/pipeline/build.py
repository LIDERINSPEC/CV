"""Monta o Reels Safety Day 2026 (1080×1920, 30 fps, 90,0 s).

Uso:
    python3 pipeline/build.py            # vídeo final em output/
    python3 pipeline/build.py --stills   # só quadros-chave para conferência

Entradas opcionais (quando a animação 3D for gerada):
    scenes/<id>.mp4      cena animada de cada bloco (s01..s08). Sem o arquivo, usa o quadro de prévia.
    voices/dialogue.wav  trilha de diálogo já posicionada na linha do tempo (48 kHz).
                         Sem ela, usa o áudio das cenas (se houver) ou fica só trilha + ambiente.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import audio  # noqa: E402
import graphics as g  # noqa: E402

ROOT = g.ROOT
OUT = os.path.join(ROOT, "output")
CUES = json.load(open(os.path.join(ROOT, "roteiro", "cues.json"), encoding="utf-8"))
FPS = CUES["fps"]
DUR = CUES["duration"]
NFRAMES = int(round(DUR * FPS))


def ease(x):
    x = min(max(x, 0.0), 1.0)
    return 1 - (1 - x) ** 3


def window(t, start, end, fin=0.3, fout=0.3):
    if t < start or t > end:
        return 0.0
    return min(ease((t - start) / fin) if fin else 1, ease((end - t) / fout) if fout else 1)


# ------------------------------------------------------------------ base (cenas)
def scene_reader(scene):
    path = os.path.join(ROOT, "scenes", f"{scene['id']}.mp4")
    dur = scene["end"] - scene["start"]
    n = int(round(dur * FPS))
    if not os.path.exists(path):
        for k in range(n):
            yield g.placeholder(scene, k / FPS)
        return
    vf = (f"scale={g.W}:{g.H}:force_original_aspect_ratio=increase,crop={g.W}:{g.H},"
          f"fps={FPS},tpad=stop_mode=clone:stop_duration={dur}")
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", path, "-vf", vf, "-frames:v", str(n),
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    size = g.W * g.H * 3
    for _ in range(n):
        buf = p.stdout.read(size)
        if len(buf) < size:
            break
        yield np.frombuffer(buf, np.uint8).reshape(g.H, g.W, 3).astype(np.float32) / 255
    p.stdout.close()
    p.wait()


def base_frames():
    for sc in CUES["scenes"]:
        if sc["id"] == "end":
            continue
        yield from scene_reader(sc)


# ------------------------------------------------------------------ camadas
def build_layers():
    ov = CUES["overlays"]
    subs = [(s, g.subtitle(s["text"])) for s in CUES["subtitles"]]
    hook = g.hook(ov["hook"]["text"])
    lid = g.lower_id(ov["lower_id"]["name"], ov["lower_id"]["role"])
    infos = [(c, g.info_card(c["text"], i)) for i, c in enumerate(ov["info"])]
    end = np.asarray(g.endcard(CUES["endcard"]), np.float32) / 255
    return subs, hook, lid, infos, end


def wipe_mask(p):
    """Transição diagonal (trapézio azul com filete ouro) entrando da direita."""
    xs = np.arange(g.W, dtype=np.float32)[None, :]
    ys = np.arange(g.H, dtype=np.float32)[:, None]
    edge = (1 - ease(p)) * (g.W + 420) - 60 + (g.H - ys) * 0.19
    inside = (xs >= edge).astype(np.float32)
    line = ((xs >= edge - 10) & (xs < edge)).astype(np.float32)
    return inside[..., None], line[..., None]


def compose(t, base, layers):
    subs, hook, lid, infos, end = layers
    ov = CUES["overlays"]
    end_t = CUES["endcard"]["start"]
    if t >= end_t:
        return end  # tela final estática nos últimos 6 s
    f = base.copy()

    h = ov["hook"]
    a = window(t, h["start"], h["end"], 0.35, 0.3)
    hook.composite(f, a, dy=int(18 * (1 - ease((t - h["start"]) / 0.5))))

    li = ov["lower_id"]
    a = window(t, li["start"], li["end"], 0.45, 0.35)
    lid.composite(f, a, dx=-int(60 * (1 - ease((t - li["start"]) / 0.5))))

    for c, sp in infos:
        a = window(t, c["start"], ov["info_end"], 0.4, 0.4)
        sp.composite(f, a, dx=-int(50 * (1 - ease((t - c["start"]) / 0.5))))

    for s, sp in subs:
        sp.composite(f, window(t, s["start"], s["end"], 0.12, 0.12))

    bw = ov["brand_wipe"]
    if bw["start"] <= t < end_t:
        p = (t - bw["start"]) / (bw["end"] - bw["start"])
        inside, line = wipe_mask(p)
        f = f * (1 - inside) + end * inside
        gold = np.array(g.GOLD, np.float32) / 255
        f = f * (1 - line) + gold * line
    return f


# ------------------------------------------------------------------ áudio
def load_wav(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", str(audio.SR),
                          "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32)


def dialogue_track():
    p = os.path.join(ROOT, "voices", "dialogue.wav")
    if os.path.exists(p):
        return load_wav(p)
    n = int(audio.SR * DUR)
    out, found = np.zeros(n, np.float32), False
    for sc in CUES["scenes"]:
        sp = os.path.join(ROOT, "scenes", f"{sc['id']}.mp4")
        if not os.path.exists(sp):
            continue
        probe = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries",
                                "stream=index", "-of", "csv=p=0", sp], capture_output=True, text=True).stdout
        if not probe.strip():
            continue
        x = load_wav(sp)[: int((sc["end"] - sc["start"]) * audio.SR)]
        s = int(sc["start"] * audio.SR)
        out[s: s + len(x)] += x[: n - s]
        found = True
    return out if found else None


def write_audio(path):
    import wave
    st = audio.mix(CUES, dialogue_track())
    pcm = (np.clip(st, -1, 1) * 32767).astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(audio.SR)
        w.writeframes(pcm.tobytes())


# ------------------------------------------------------------------ SRT
def srt_time(x):
    ms = int(round(x * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def write_srt(path):
    with open(path, "w", encoding="utf-8") as fh:
        for i, s in enumerate(CUES["subtitles"], 1):
            fh.write(f"{i}\n{srt_time(s['start'])} --> {srt_time(s['end'])}\n{s['text']}\n\n")


# ------------------------------------------------------------------ main
def main():
    os.makedirs(OUT, exist_ok=True)
    layers = build_layers()
    write_srt(os.path.join(ROOT, "roteiro", "legendas.srt"))
    Image.fromarray((layers[4] * 255).astype(np.uint8)).save(os.path.join(OUT, "tela-final.png"))

    if "--stills" in sys.argv:
        keys = [1.0, 6.5, 12.0, 20.0, 37.0, 47.0, 60.5, 66.0, 72.0, 80.0, 83.7, 87.0]
        frames = base_frames()
        k = 0
        for i in range(NFRAMES):
            t = i / FPS
            b = next(frames) if t < CUES["endcard"]["start"] else None
            if k < len(keys) and abs(t - keys[k]) < 0.5 / FPS:
                fr = compose(t, b, layers)
                Image.fromarray((fr * 255).astype(np.uint8)).save(os.path.join(OUT, f"key_{t:05.1f}.png"))
                k += 1
        return

    wav = os.path.join(OUT, "_mix.wav")
    write_audio(wav)
    final = os.path.join(OUT, "safety-day-2026-reels-1080x1920.mp4")
    enc = subprocess.Popen([
        "ffmpeg", "-y", "-v", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{g.W}x{g.H}", "-r", str(FPS), "-i", "-",
        "-i", wav,
        "-map", "0:v", "-map", "1:a",
        "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-profile:v", "high", "-level", "4.2",
        "-pix_fmt", "yuv420p", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
        "-af", "loudnorm=I=-14:TP=-1.5:LRA=11",
        "-c:a", "aac", "-b:a", "256k", "-ar", "48000",
        "-t", f"{DUR:.3f}", "-movflags", "+faststart", final,
    ], stdin=subprocess.PIPE)
    frames = base_frames()
    for i in range(NFRAMES):
        t = i / FPS
        b = next(frames) if t < CUES["endcard"]["start"] else None
        fr = compose(t, b, layers)
        enc.stdin.write((np.clip(fr, 0, 1) * 255 + 0.5).astype(np.uint8).tobytes())
        if i % 300 == 0:
            print(f"  quadro {i}/{NFRAMES}", flush=True)
    enc.stdin.close()
    enc.wait()
    os.remove(wav)
    print(final)


if __name__ == "__main__":
    main()
