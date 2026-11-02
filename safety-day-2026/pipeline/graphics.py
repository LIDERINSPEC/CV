"""Elementos gráficos do Reels Safety Day 2026 (legendas, títulos, cartões, tela final, QR).

Todos os textos, o logo e o QR code são aplicados na edição — nunca gerados pela IA de vídeo.
Paleta e tipografia conforme o briefing (Saira Semi Condensed nos títulos, Inter nos textos).
"""
from __future__ import annotations

import os
from functools import lru_cache

import numpy as np
import qrcode
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = os.path.join(ROOT, "assets", "fonts")
LOGO = os.path.join(ROOT, "assets", "logo-lider-original.jpg")

W, H = 1080, 1920

BLUE = (19, 57, 105)        # #133969 — azul principal
BLUE_DEEP = (12, 38, 72)
BLUE_SOFT = (29, 72, 126)
GOLD = (210, 157, 24)       # #d29d18 — só filetes e detalhes
OFF = (249, 250, 248)       # #f9faf8
GRAY = (133, 142, 154)      # #858e9a

# Zona segura do Reels: evita a UI do Instagram (topo, rodapé e coluna direita de ícones).
SAFE_TOP, SAFE_BOTTOM, SAFE_LEFT, SAFE_RIGHT = 220, 1540, 80, 960


@lru_cache(None)
def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    files = {
        "saira-bold": "SairaSemiCondensed-Bold.ttf",
        "saira-semibold": "SairaSemiCondensed-SemiBold.ttf",
        "saira-medium": "SairaSemiCondensed-Medium.ttf",
        "inter": "Inter-Regular.otf",
        "inter-medium": "Inter-Medium.otf",
        "inter-semibold": "Inter-SemiBold.otf",
        "inter-bold": "Inter-Bold.otf",
        "inter-italic": "Inter-Italic.otf",
    }
    return ImageFont.truetype(os.path.join(FONTS, files[name]), size)


def text_size(txt: str, f: ImageFont.FreeTypeFont, tracking: int = 0) -> tuple[int, int]:
    l, t, r, b = f.getbbox(txt)
    return r - l + tracking * max(len(txt) - 1, 0), b - t


def draw_text(d: ImageDraw.ImageDraw, xy, txt, f, fill, tracking=0, anchor="la"):
    """Texto com espaçamento entre letras (tracking) — Pillow não tem nativo."""
    if tracking == 0:
        d.text(xy, txt, font=f, fill=fill, anchor=anchor)
        return
    x, y = xy
    if anchor[0] == "m":
        x -= text_size(txt, f, tracking)[0] / 2
    for ch in txt:
        d.text((x, y), ch, font=f, fill=fill, anchor="l" + anchor[1])
        x += f.getlength(ch) + tracking


class Sprite:
    """Camada RGBA recortada ao tamanho útil + posição no quadro."""

    def __init__(self, img: Image.Image, x: int, y: int):
        bbox = img.getbbox() or (0, 0, 1, 1)
        img = img.crop(bbox)
        self.x, self.y = x + bbox[0], y + bbox[1]
        a = np.asarray(img, dtype=np.float32) / 255.0
        self.rgb = a[..., :3]
        self.alpha = a[..., 3:4]

    def composite(self, frame: np.ndarray, opacity: float = 1.0, dx: int = 0, dy: int = 0):
        if opacity <= 0.001:
            return
        x, y = self.x + dx, self.y + dy
        h, w = self.alpha.shape[:2]
        x0, y0, x1, y1 = max(x, 0), max(y, 0), min(x + w, W), min(y + h, H)
        if x1 <= x0 or y1 <= y0:
            return
        src = self.rgb[y0 - y:y1 - y, x0 - x:x1 - x]
        a = self.alpha[y0 - y:y1 - y, x0 - x:x1 - x] * opacity
        dst = frame[y0:y1, x0:x1]
        dst[:] = dst * (1 - a) + src * a


def shadowed(layer: Image.Image, radius=14, strength=150, offset=(0, 6)) -> Image.Image:
    """Sombra suave por baixo da camada — garante leitura sobre o vídeo."""
    alpha = layer.split()[3]
    sh = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    sh.putalpha(alpha.point(lambda v: v * strength // 255))
    sh = sh.filter(ImageFilter.GaussianBlur(radius))
    out = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    out.alpha_composite(sh, offset)
    out.alpha_composite(layer)
    return out


def trapezoid(d: ImageDraw.ImageDraw, x0, y0, x1, y1, fill, slant=0.185, left=False, right=True):
    """Painel com recorte diagonal (≈10,5°) — grafismo da marca."""
    s = (y1 - y0) * slant
    pts = [
        (x0 + (s if left else 0), y0),
        (x1, y0),
        (x1 - (s if right else 0), y1),
        (x0, y1),
    ]
    d.polygon(pts, fill=fill)


# ---------------------------------------------------------------- legendas
def subtitle(text: str) -> Sprite:
    """Legenda de no máximo 2 linhas, quebra equilibrada; reduz o corpo só se precisar."""
    maxw = SAFE_RIGHT - SAFE_LEFT - 56
    words = " ".join(text.split()).split(" ")
    for size in (46, 44, 42, 40):
        f = font("inter-semibold", size)
        full = " ".join(words)
        if text_size(full, f)[0] <= maxw:
            lines = [full]
            break
        best = min(range(1, len(words)), key=lambda k: max(
            text_size(" ".join(words[:k]), f)[0], text_size(" ".join(words[k:]), f)[0]))
        lines = [" ".join(words[:best]), " ".join(words[best:])]
        if max(text_size(l, f)[0] for l in lines) <= maxw:
            break
    lh = 60
    widths = [text_size(l, f)[0] for l in lines]
    bw = max(widths) + 56
    bh = lh * len(lines) + 30
    assert bw <= SAFE_RIGHT - SAFE_LEFT, f"legenda larga demais: {text!r}"
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = (SAFE_LEFT + SAFE_RIGHT) // 2
    y1 = 1505
    y0 = y1 - bh
    d.rounded_rectangle((cx - bw // 2, y0, cx + bw // 2, y1), radius=14, fill=BLUE_DEEP + (222,))
    for i, l in enumerate(lines):
        d.text((cx, y0 + 15 + lh * i + lh // 2), l, font=f, fill=OFF + (255,), anchor="mm")
    return Sprite(img, 0, 0)


# ---------------------------------------------------------------- textos de cena
def hook(text: str) -> Sprite:
    f = font("saira-bold", 104)
    img = Image.new("RGBA", (W, 420), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = (SAFE_LEFT + SAFE_RIGHT) // 2
    draw_text(d, (cx, 150), text, f, OFF + (255,), tracking=1, anchor="mm")
    d.rectangle((cx - 70, 232, cx + 70, 239), fill=GOLD + (255,))
    return Sprite(shadowed(img, radius=18, strength=190), 0, 170)


def lower_id(name: str, role: str) -> Sprite:
    fn = font("saira-bold", 60)
    fr = font("inter-medium", 38)
    sep = "  |  "
    wn = fn.getlength(name)
    ws = fr.getlength(sep)
    wr = fr.getlength(role)
    pad = 34
    pw = int(wn + ws + wr + pad * 2 + 40)
    ph = 104
    img = Image.new("RGBA", (pw + 40, ph + 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    trapezoid(d, 0, 0, pw, ph, BLUE + (238,))
    d.rectangle((0, 0, 7, ph), fill=GOLD + (255,))
    y = ph // 2
    d.text((pad, y), name, font=fn, fill=OFF + (255,), anchor="lm")
    d.text((pad + wn, y + 2), sep, font=fr, fill=GOLD + (255,), anchor="lm")
    d.text((pad + wn + ws, y + 2), role, font=fr, fill=OFF + (255,), anchor="lm")
    return Sprite(shadowed(img, radius=12, strength=120), SAFE_LEFT, 1190)


def info_card(text: str, index: int) -> Sprite:
    """Cartões do convite, empilhados no terço superior (rostos ficam abaixo de y≈760)."""
    big = index == 0
    f = font("saira-bold", 84) if big else font("saira-semibold", 58)
    ph = 124 if big else 90
    tw = text_size(text, f, 2)[0]
    pw = tw + 96
    img = Image.new("RGBA", (pw + 40, ph + 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    trapezoid(d, 0, 0, pw, ph, (BLUE if big else OFF) + (240,))
    d.rectangle((0, 0, 7, ph), fill=GOLD + (255,))
    draw_text(d, (40, ph // 2 + 2), text, f, (OFF if big else BLUE) + (255,), tracking=2, anchor="lm")
    y = 250 + (0 if big else 124 + 16 + (index - 1) * (90 + 16))
    return Sprite(shadowed(img, radius=12, strength=110), SAFE_LEFT, y)


# ---------------------------------------------------------------- logo / QR
def logo_on(bg_rgb, width: int) -> Image.Image:
    """Logo original sem redesenho: recorte das margens + multiplicação sobre o fundo claro."""
    im = Image.open(LOGO).convert("RGB")
    gray = np.asarray(im.convert("L"))
    ys, xs = np.where(gray < 235)
    im = im.crop((xs.min() - 6, ys.min() - 6, xs.max() + 7, ys.max() + 7))
    h = round(im.height * width / im.width)
    im = im.resize((width, h), Image.LANCZOS)
    base = Image.new("RGB", im.size, bg_rgb)
    return ImageChops.multiply(base, im)


def qr_image(url: str, size: int) -> Image.Image:
    q = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_Q, border=0, box_size=1)
    q.add_data(url)
    q.make(fit=True)
    m = q.get_matrix()
    n = len(m)
    mod = size // n
    img = Image.new("RGB", (n * mod, n * mod), "white")
    d = ImageDraw.Draw(img)
    for r, row in enumerate(m):
        for c, v in enumerate(row):
            if v:
                d.rectangle((c * mod, r * mod, c * mod + mod - 1, r * mod + mod - 1), fill=BLUE_DEEP)
    return img


# ---------------------------------------------------------------- tela final
def endcard(cfg: dict) -> Image.Image:
    img = Image.new("RGB", (W, H), BLUE)
    d = ImageDraw.Draw(img, "RGBA")

    # Grafismos discretos: trapézios diagonais em tom de azul + filetes ouro finos.
    d.polygon([(640, 0), (W, 0), (W, 520), (930, 520)], fill=BLUE_SOFT + (110,))
    d.polygon([(0, 1380), (300, 1380), (180, H), (0, H)], fill=BLUE_SOFT + (110,))
    d.polygon([(0, 1640), (520, 1640), (470, H), (0, H)], fill=BLUE_DEEP + (140,))
    d.line([(1012, 430), (1080, 70)], fill=GOLD + (200,), width=4)
    d.line([(150, 1590), (100, 1860)], fill=GOLD + (170,), width=4)

    cx = W // 2
    # Logo original em placa clara com recorte diagonal.
    logo = logo_on(OFF, 430)
    lw, lh = logo.size
    px0, py0 = cx - lw // 2 - 50, 205
    px1, py1 = cx + lw // 2 + 50, 205 + lh + 56
    trapezoid(d, px0, py0, px1, py1, OFF + (255,), slant=0.18, left=True, right=True)
    img.paste(logo, (cx - lw // 2, py0 + 28))

    y = py1 + 46
    f_title = font("saira-bold", 122)
    draw_text(d, (cx, y), cfg["title"], f_title, OFF, tracking=2, anchor="mt")
    y += 132
    d.rectangle((cx - 80, y, cx + 80, y + 6), fill=GOLD)
    y += 34
    d.text((cx, y), cfg["date"], font=font("inter-semibold", 42), fill=OFF, anchor="mt")
    y += 66
    draw_text(d, (cx, y), cfg["place"], font("saira-semibold", 60), OFF, tracking=3, anchor="mt")
    y += 84
    # Tags com marcadores ouro.
    f_tag = font("inter-medium", 33)
    parts = [p.strip() for p in cfg["tags"].split("•")]
    dot = "  •  "
    total = sum(f_tag.getlength(p) for p in parts) + f_tag.getlength(dot) * (len(parts) - 1)
    x = cx - total / 2
    for i, p in enumerate(parts):
        d.text((x, y), p, font=f_tag, fill=OFF + (235,), anchor="lt")
        x += f_tag.getlength(p)
        if i < len(parts) - 1:
            d.text((x, y), dot, font=f_tag, fill=GOLD, anchor="lt")
            x += f_tag.getlength(dot)
    y += 74

    # CTA com contorno ouro (detalhe discreto, sem preenchimento dourado).
    f_cta = font("saira-bold", 54)
    cw = text_size(cfg["cta"], f_cta, 3)[0] + 110
    ch = 92
    d.rounded_rectangle((cx - cw // 2, y, cx + cw // 2, y + ch), radius=10, outline=GOLD, width=4)
    draw_text(d, (cx, y + ch // 2 + 2), cfg["cta"], f_cta, OFF, tracking=3, anchor="mm")
    y += ch + 36

    # QR code com zona de silêncio branca.
    qr = qr_image(cfg["url_qr"], 330)
    q = qr.size[0]
    pad = 34
    d.rounded_rectangle((cx - q // 2 - pad, y, cx + q // 2 + pad, y + q + pad * 2), radius=18, fill=(255, 255, 255))
    img.paste(qr, (cx - q // 2, y + pad))
    y += q + pad * 2 + 26
    d.text((cx, y), cfg["url_display"], font=font("inter-semibold", 37), fill=OFF, anchor="mt")
    y += 64
    d.text((cx, y), cfg["signature"], font=font("inter-italic", 33), fill=OFF + (220,), anchor="mt")
    assert y + 40 <= SAFE_BOTTOM, f"tela final ultrapassa a zona segura: {y}"
    return img


# ---------------------------------------------------------------- prévia (animatic)
@lru_cache(None)
def _placeholder_bg() -> Image.Image:
    yy = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
    top = np.array([38, 58, 86], np.float32)
    bot = np.array([14, 30, 52], np.float32)
    return Image.fromarray(np.broadcast_to(top * (1 - yy) + bot * yy, (H, W, 3)).astype(np.uint8))


def placeholder(scene: dict, t_local: float) -> np.ndarray:
    """Quadro de animatic para cenas ainda não geradas. Mostra o que a cena animada deve conter."""
    img = _placeholder_bg().copy()
    d = ImageDraw.Draw(img, "RGBA")
    shift = int(t_local * 14) % 120
    for gx in range(-120 + shift, W + 120, 120):
        d.line([(gx, 0), (gx - 340, H)], fill=(255, 255, 255, 10), width=2)
    cx = W // 2
    d.rectangle((SAFE_LEFT, 780, SAFE_RIGHT, 1130), outline=GRAY + (120,), width=2)
    d.text((cx, 810), f"PRÉVIA · {scene['id'].upper()} · {scene['start']:.0f}–{scene['end']:.0f} s",
           font=font("inter-semibold", 30), fill=GOLD, anchor="mt")
    d.text((cx, 862), scene["title"].upper(), font=font("saira-bold", 66), fill=OFF, anchor="mt")
    f = font("inter", 31)
    words, lines, cur = scene["shot"].split(), [], ""
    for w_ in words:
        test = (cur + " " + w_).strip()
        if f.getlength(test) > 800:
            lines.append(cur)
            cur = w_
        else:
            cur = test
    lines.append(cur)
    for i, l in enumerate(lines[:5]):
        d.text((cx, 958 + i * 40), l, font=f, fill=OFF + (200,), anchor="mt")
    dur = scene["end"] - scene["start"]
    d.rectangle((SAFE_LEFT, 1128, SAFE_LEFT + int((SAFE_RIGHT - SAFE_LEFT) * t_local / dur), 1132), fill=GOLD)
    return np.asarray(img, dtype=np.float32) / 255
