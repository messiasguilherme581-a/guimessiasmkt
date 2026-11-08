#!/usr/bin/env python3
"""Reels 9:16 — "Inscrições abertas · Acampamento 2027".

Motion graphics a partir de uma única foto (assets/chacara.jpg):
fundo desfocado + foto em "card" com movimento de câmera (Ken Burns),
tipografia cinética e CTA final.

Uso:
    python3 render.py                 # render completo -> acampamento-2027-reels.mp4 + capa.jpg
    python3 render.py --preview 1.2 4.5 9 13.5   # só quadros PNG em preview/

Requisitos: Python 3.11+, Pillow, numpy, ffmpeg (libx264) e a fonte Inter Display.
Para mudar textos (data, valor, contato), edite o bloco TEXTOS abaixo.
"""
from __future__ import annotations

import math
import os
import subprocess
import sys
from multiprocessing import Pool

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "assets", "chacara.jpg")
OUT_MP4 = os.path.join(HERE, "acampamento-2027-reels.mp4")
OUT_COVER = os.path.join(HERE, "capa.jpg")

W, H, FPS, DUR = 1080, 1920, 30, 15.0
DY = 50  # desloca o layout p/ o centro da área segura (Reels/Stories)
NFRAMES = int(DUR * FPS)

FONT_DIR = "/usr/share/fonts/opentype/inter"
F_BLACK = os.path.join(FONT_DIR, "InterDisplay-Black.otf")
F_BOLD = os.path.join(FONT_DIR, "InterDisplay-Bold.otf")
F_SEMI = os.path.join(FONT_DIR, "InterDisplay-SemiBold.otf")

# Paleta tirada da própria foto: portão amarelo + muro azul, com navy de contraste.
YELLOW = (255, 194, 26)
NAVY = (12, 24, 58)
WHITE = (255, 255, 255)

# ---------------------------------------------------------------- TEXTOS
TXT = {
    "kicker1": "VEM AÍ",
    "acampamento": "ACAMPAMENTO",
    "ano": "2027",
    "inscricoes": "INSCRIÇÕES",
    "abertas": "ABERTAS",
    "sub2": [("A chácara já está", WHITE), ("te esperando.", YELLOW)],
    "dias_de": "DIAS DE",
    "palavras": ["COMUNHÃO", "LOUVOR", "PALAVRA"],
    "sub3": [("Um tempo separado", WHITE), ("para Deus.", YELLOW)],
    "kicker4": "ACAMPAMENTO 2027",
    "cta": "GARANTA SUA VAGA",
    "cta_sub": "Fale com a liderança da igreja",
}


# ---------------------------------------------------------------- easing
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease_out_cubic(x):
    x = clamp(x)
    return 1 - (1 - x) ** 3


def ease_in_cubic(x):
    x = clamp(x)
    return x ** 3


def ease_in_out_cubic(x):
    x = clamp(x)
    return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2


def ease_out_back(x, s=1.9):
    x = clamp(x)
    return 1 + (s + 1) * (x - 1) ** 3 + s * (x - 1) ** 2


def lerp(a, b, t):
    return a + (b - a) * t


def prog(t, start, dur):
    return clamp((t - start) / dur)


# ---------------------------------------------------------------- sprites
def font(path, size):
    return ImageFont.truetype(path, size)


def _shadowed(layer_alpha: Image.Image, color, pad, shadow=0.55, blur=16, dy=8):
    """Recebe a máscara do texto e devolve RGBA com sombra suave + texto."""
    w, h = layer_alpha.size
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    if shadow > 0:
        sh = Image.new("L", (w, h), 0)
        sh.paste(layer_alpha, (0, dy))
        sh = sh.filter(ImageFilter.GaussianBlur(blur)).point(lambda a: int(a * shadow))
        out.paste(Image.new("RGBA", (w, h), (4, 8, 24, 255)), (0, 0), sh)
    fill = Image.new("RGBA", (w, h), color + (255,))
    out.alpha_composite(Image.composite(fill, Image.new("RGBA", (w, h), (0, 0, 0, 0)), layer_alpha))
    return out


def text_sprite(text, path, size, color, tracking=0, shadow=0.55, pad=48):
    """Sprite com caixa = métricas da fonte, então palavras da mesma linha alinham no baseline."""
    f = font(path, size)
    asc, desc = f.getmetrics()
    adv = [f.getlength(c) for c in text]
    tw = sum(adv) + tracking * (len(text) - 1) if tracking else f.getlength(text)
    w, h = int(math.ceil(tw)) + 2 * pad, asc + desc + 2 * pad
    mask = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(mask)
    if tracking:
        x = pad
        for c, a in zip(text, adv):
            d.text((x, pad + asc), c, font=f, fill=255, anchor="ls")
            x += a + tracking
    else:
        d.text((pad, pad + asc), text, font=f, fill=255, anchor="ls")
    return _shadowed(mask, color, pad, shadow=shadow)


def fit_size(text, path, maxw, start, tracking=0):
    s = start
    while s > 20:
        f = font(path, s)
        tw = sum(f.getlength(c) for c in text) + tracking * (len(text) - 1) if tracking else f.getlength(text)
        if tw <= maxw:
            return s
        s -= 2
    return s


def box_sprite(text, path, size, fg, bg, padx=44, pady=26, radius=22, tracking=0, shadow=0.5):
    """Texto dentro de caixa (selo/botão), centralizado pela altura real das maiúsculas."""
    f = font(path, size)
    tw = (sum(f.getlength(c) for c in text) + tracking * (len(text) - 1)) if tracking else f.getlength(text)
    l, t, r, b = f.getbbox("H")  # altura de maiúscula -> centragem óptica
    cap_h = b - t
    bw, bh = int(tw + 2 * padx), int(cap_h + 2 * pady)
    m = 40
    w, h = bw + 2 * m, bh + 2 * m
    box_mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(box_mask).rounded_rectangle((m, m, m + bw, m + bh), radius=radius, fill=255)
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    if shadow:
        sh = Image.new("L", (w, h), 0)
        sh.paste(box_mask, (0, 10))
        sh = sh.filter(ImageFilter.GaussianBlur(18)).point(lambda a: int(a * shadow))
        out.paste(Image.new("RGBA", (w, h), (4, 8, 24, 255)), (0, 0), sh)
    out.paste(Image.new("RGBA", (w, h), bg + (255,)), (0, 0), box_mask)
    d = ImageDraw.Draw(out)
    base_y = m + pady + cap_h + 0  # baseline: topo da caixa + pady + altura da maiúscula
    if tracking:
        x = m + padx
        for c in text:
            d.text((x, base_y), c, font=f, fill=fg + (255,), anchor="ls")
            x += f.getlength(c) + tracking
    else:
        d.text((m + padx, base_y), text, font=f, fill=fg + (255,), anchor="ls")
    return out


def words_layout(lines, path, size, cy0, line_gap):
    """Quebra cada linha em palavras (para revelar palavra a palavra, estilo legenda CapCut)."""
    f = font(path, size)
    space = f.getlength(" ")
    words = []
    for li, (line, color) in enumerate(lines):
        parts = line.split(" ")
        widths = [f.getlength(p) for p in parts]
        total = sum(widths) + space * (len(parts) - 1)
        x = W / 2 - total / 2
        cy = cy0 + li * line_gap
        for p, wd in zip(parts, widths):
            words.append((text_sprite(p, path, size, color, shadow=0.7), x + wd / 2, cy))
            x += wd + space
    return words


# ---------------------------------------------------------------- composição
def place(canvas: Image.Image, spr: Image.Image, cx, cy, s=1.0, r=0.0, a=1.0):
    if a <= 0.004 or s <= 0.02:
        return
    im = spr
    if abs(s - 1) > 1e-3:
        im = im.resize((max(1, round(im.width * s)), max(1, round(im.height * s))), Image.BICUBIC)
    if abs(r) > 0.01:
        im = im.rotate(r, resample=Image.BICUBIC, expand=True)
    if a < 0.996:
        im = im.copy()
        im.putalpha(im.getchannel("A").point(lambda v: int(v * a)))
    x, y = round(cx - im.width / 2), round(cy - im.height / 2)
    # recorte para não sair do quadro
    sx, sy = max(0, -x), max(0, -y)
    ex, ey = min(im.width, W - x), min(im.height, H - y)
    if ex <= sx or ey <= sy:
        return
    if sx or sy or ex < im.width or ey < im.height:
        im = im.crop((sx, sy, ex, ey))
    canvas.alpha_composite(im, (x + sx, y + sy))


class El:
    """Elemento de texto com animação de entrada/saída."""

    def __init__(self, spr, cx, cy, t_in, t_out, kind="rise", rot=0.0, din=0.45, dout=0.28):
        self.spr, self.cx, self.cy = spr, cx, cy
        self.t_in, self.t_out, self.kind, self.rot = t_in, t_out, kind, rot
        self.din, self.dout = din, dout

    def draw(self, canvas, t, ox=0.0, oy=0.0):
        if t < self.t_in or t > self.t_out + self.dout:
            return
        pin = prog(t, self.t_in, self.din)
        pout = prog(t, self.t_out, self.dout)
        dy, s, a, r = 0.0, 1.0, 1.0, self.rot
        if self.kind == "rise":
            dy = lerp(70, 0, ease_out_cubic(pin))
            a = ease_out_cubic(prog(t, self.t_in, self.din * 0.7))
        elif self.kind == "pop":
            s = lerp(0.35, 1.0, ease_out_back(pin, 2.2))
            a = ease_out_cubic(prog(t, self.t_in, 0.14))
        elif self.kind == "stamp":
            s = lerp(2.1, 1.0, ease_out_cubic(pin))
            a = ease_out_cubic(prog(t, self.t_in, 0.1))
            r = lerp(self.rot - 9, self.rot, ease_out_cubic(pin))
        if pout > 0:
            e = ease_in_cubic(pout)
            dy += lerp(0, -50, e)
            a *= 1 - e
            s *= lerp(1, 0.94, e)
        place(canvas, self.spr, self.cx + ox, self.cy + dy + oy, s, r, a)


# ---------------------------------------------------------------- assets (pré-computados)
def grade(img: Image.Image) -> Image.Image:
    img = ImageEnhance.Contrast(img).enhance(1.10)
    img = ImageEnhance.Color(img).enhance(1.18)
    arr = np.asarray(img).astype(np.float32)
    arr[..., 0] *= 1.03  # leve aquecida
    arr[..., 2] *= 0.97
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))


SRC_IMG = grade(Image.open(SRC).convert("RGB"))
SW, SH = SRC_IMG.size
UP = 2  # fonte em 2x para Ken Burns sub-pixel suave
SRC_UP = SRC_IMG.resize((SW * UP, SH * UP), Image.LANCZOS).filter(
    ImageFilter.UnsharpMask(radius=2, percent=60, threshold=2)
)

# Fundo: recorte vertical da foto, desfocado e escurecido com navy
_bgw = int(SH * 9 / 16)
_bg = SRC_IMG.crop((620 - _bgw // 2, 0, 620 + _bgw // 2, SH)).filter(ImageFilter.GaussianBlur(10))
_bg = _bg.resize((int(W * 1.25), int(H * 1.25)), Image.BICUBIC).filter(ImageFilter.GaussianBlur(18))
BG = Image.blend(_bg, Image.new("RGB", _bg.size, NAVY), 0.58)


def _overlay():
    yy = np.linspace(0, 1, H)[:, None]
    xx = np.linspace(-1, 1, W)[None, :]
    top = np.clip(1 - yy / 0.32, 0, 1) ** 1.6 * 0.55
    bot = np.clip((yy - 0.62) / 0.38, 0, 1) ** 1.4 * 0.75
    vig = np.clip((xx ** 2 * 0.6 + ((yy - 0.5) * 2) ** 2 * 0.4) - 0.35, 0, 1) * 0.45
    a = np.clip(top + bot + vig, 0, 0.9)
    rgba = np.zeros((H, W, 4), np.uint8)
    rgba[..., 0], rgba[..., 1], rgba[..., 2] = 4, 8, 24
    rgba[..., 3] = (a * 255).astype(np.uint8)
    return Image.fromarray(rgba, "RGBA")


OVERLAY = _overlay()

# Card (foto com borda branca arredondada + sombra)
PW, PH, BORDER, CR = 960, 540, 14, 30
CW, CH = PW + 2 * BORDER, PH + 2 * BORDER
CM = 70  # margem para a sombra
_card_mask = Image.new("L", (CW + 2 * CM, CH + 2 * CM), 0)
ImageDraw.Draw(_card_mask).rounded_rectangle((CM, CM, CM + CW, CM + CH), radius=CR, fill=255)
_sh = Image.new("L", _card_mask.size, 0)
_sh.paste(_card_mask, (0, 26))
_sh = _sh.filter(ImageFilter.GaussianBlur(28)).point(lambda a: int(a * 0.6))
CARD_BASE = Image.new("RGBA", _card_mask.size, (0, 0, 0, 0))
CARD_BASE.paste(Image.new("RGBA", _card_mask.size, (2, 6, 20, 255)), (0, 0), _sh)
CARD_BASE.paste(Image.new("RGBA", _card_mask.size, (250, 248, 242, 255)), (0, 0), _card_mask)
PHOTO_MASK = Image.new("L", (PW, PH), 0)
ImageDraw.Draw(PHOTO_MASK).rounded_rectangle((0, 0, PW - 1, PH - 1), radius=CR - BORDER + 4, fill=255)

rng = np.random.default_rng(7)
GRAIN = [rng.normal(0, 2.6, (H, W, 1)).astype(np.float32) for _ in range(6)]


# ---------------------------------------------------------------- câmera do card (Ken Burns)
# (tempo, centro_x, centro_y, zoom) em coordenadas da foto original; easing do trecho que CHEGA no ponto
CAM = [
    (0.0, 512, 288, 1.00, None),
    (3.0, 512, 288, 1.10, "lin"),
    (3.9, 640, 196, 1.78, "io"),   # placa da chácara
    (7.2, 662, 200, 1.95, "lin"),
    (8.1, 245, 268, 1.55, "io"),   # área coberta / lazer
    (11.0, 330, 270, 1.45, "lin"),
    (11.9, 520, 300, 1.03, "io"),  # volta ao plano geral
    (15.0, 520, 300, 1.09, "lin"),
]


def cam_at(t):
    for (t0, x0, y0, z0, _), (t1, x1, y1, z1, e) in zip(CAM, CAM[1:]):
        if t <= t1:
            p = clamp((t - t0) / (t1 - t0))
            p = ease_in_out_cubic(p) if e == "io" else p
            z = math.exp(lerp(math.log(z0), math.log(z1), p))
            return lerp(x0, x1, p), lerp(y0, y1, p), z
    return CAM[-1][1:4]


def photo_at(t):
    cx, cy, z = cam_at(t)
    vw, vh = SW / z, SH / z  # janela visível na foto original
    cx = clamp(cx, vw / 2, SW - vw / 2)
    cy = clamp(cy, vh / 2, SH - vh / 2)
    s = (vw * UP) / PW
    x0, y0 = (cx - vw / 2) * UP, (cy - vh / 2) * UP
    return SRC_UP.transform((PW, PH), Image.AFFINE, (s, 0, x0, 0, s, y0), resample=Image.BICUBIC)


# (tempo, centro_y, escala, rotação) do card no quadro
CARD_KF = [
    (0.0, 1080, 0.70, -10.0, None),
    (0.9, 950, 1.00, -2.5, "back"),
    (3.15, 950, 1.00, -2.5, "lin"),
    (3.8, 950, 1.00, 2.0, "io"),
    (7.25, 950, 1.00, 2.0, "lin"),
    (7.9, 955, 1.00, -2.0, "io"),
    (11.15, 955, 1.00, -2.0, "lin"),
    (11.95, 902, 0.78, 0.0, "io"),
    (15.0, 902, 0.78, 0.0, "lin"),
]


def card_at(t):
    for (t0, y0, s0, r0, _), (t1, y1, s1, r1, e) in zip(CARD_KF, CARD_KF[1:]):
        if t <= t1:
            p = clamp((t - t0) / (t1 - t0))
            p = ease_out_back(p, 1.4) if e == "back" else ease_in_out_cubic(p) if e == "io" else p
            return lerp(y0, y1, p), lerp(s0, s1, p), lerp(r0, r1, p)
    return CARD_KF[-1][1:4]


# ---------------------------------------------------------------- roteiro (elementos de texto)
def build_elements():
    els = []
    # CENA 1 · 0–3.2s · gancho
    els.append(El(box_sprite(TXT["kicker1"], F_BLACK, 40, NAVY, YELLOW, padx=30, pady=18, radius=40, tracking=6),
                  540, 318, 0.30, 3.0, "pop"))
    s = fit_size(TXT["acampamento"], F_BLACK, 950, 150)
    els.append(El(text_sprite(TXT["acampamento"], F_BLACK, s, WHITE), 540, 462, 0.48, 3.0, "rise"))
    els.append(El(text_sprite(TXT["ano"], F_BLACK, 270, YELLOW, shadow=0.7), 540, 1395, 0.95, 3.05, "stamp", din=0.3))

    # CENA 2 · 3.2–7.3s · inscrições abertas
    s = fit_size(TXT["inscricoes"], F_BLACK, 930, 150)
    els.append(El(text_sprite(TXT["inscricoes"], F_BLACK, s, WHITE), 540, 372, 3.30, 7.1, "rise"))
    els.append(El(box_sprite(TXT["abertas"], F_BLACK, 122, NAVY, YELLOW, padx=46, pady=28, radius=24),
                  540, 548, 3.62, 7.1, "stamp", rot=3.0, din=0.28))
    for i, (spr, cx, cy) in enumerate(words_layout(TXT["sub2"], F_BOLD, 64, 1330, 82)):
        els.append(El(spr, cx, cy, 4.25 + i * 0.13, 7.1, "rise", din=0.35))

    # CENA 3 · 7.3–11.2s · o que é o acampamento
    els.append(El(text_sprite(TXT["dias_de"], F_SEMI, 58, WHITE, tracking=10), 540, 322, 7.42, 11.0, "rise"))
    ws = TXT["palavras"]
    s = min(fit_size(w, F_BLACK, 920, 156) for w in ws)
    slots = [(7.62, 8.86), (8.98, 10.0), (10.12, 11.0)]
    for w, (a, b) in zip(ws, slots):
        els.append(El(text_sprite(w, F_BLACK, s, YELLOW, shadow=0.65), 540, 452, a, b, "rise", din=0.32, dout=0.14))
    for i, (spr, cx, cy) in enumerate(words_layout(TXT["sub3"], F_BOLD, 64, 1335, 82)):
        els.append(El(spr, cx, cy, 7.95 + i * 0.13, 11.0, "rise", din=0.35))

    # CENA 4 · 11.2–15s · CTA
    END = 99.0  # fica até o fim
    els.append(El(text_sprite(TXT["kicker4"], F_BLACK, 44, YELLOW, tracking=8), 540, 292, 11.35, END, "rise"))
    s = fit_size(TXT["inscricoes"], F_BLACK, 900, 140)
    els.append(El(text_sprite(TXT["inscricoes"], F_BLACK, s, WHITE), 540, 408, 11.45, END, "rise"))
    els.append(El(box_sprite(TXT["abertas"], F_BLACK, 112, NAVY, YELLOW, padx=44, pady=26, radius=22),
                  540, 568, 11.72, END, "stamp", rot=3.0, din=0.28))
    els.append(El(text_sprite(TXT["cta_sub"], F_SEMI, 46, (232, 236, 245)), 540, 1345, 12.45, END, "rise"))
    return els


ELEMENTS = build_elements()
CTA = box_sprite(TXT["cta"], F_BLACK, 58, NAVY, YELLOW, padx=56, pady=36, radius=60, tracking=2)
SHAKES = [1.25, 3.90, 12.0]  # impactos dos "carimbos"


def shake(t):
    ox = oy = 0.0
    for t0 in SHAKES:
        d = t - t0
        if 0 <= d < 0.32:
            k = math.exp(-d * 14)
            ox += math.sin(d * 95) * 9 * k
            oy += math.cos(d * 80) * 7 * k
    return ox, oy


# ---------------------------------------------------------------- render de um quadro
def render(t: float, grain=True) -> Image.Image:
    # fundo com zoom lento
    z = lerp(1.0, 1.12, t / DUR)
    bw, bh = BG.size  # 1.25x o quadro: em z=1 mostra o miolo 1080x1920
    vw, vh = W / z, H / z
    cx, cy = bw / 2 + math.sin(t * 0.35) * 30, bh / 2
    frame = BG.transform((W, H), Image.AFFINE, (1 / z, 0, cx - vw / 2, 0, 1 / z, cy - vh / 2), resample=Image.BILINEAR)
    frame = frame.convert("RGBA")
    frame.alpha_composite(OVERLAY)

    ox, oy = shake(t)
    oy += DY

    # card
    ccy, cs, cr = card_at(t)
    card = CARD_BASE.copy()
    card.paste(photo_at(t), (CM + BORDER, CM + BORDER), PHOTO_MASK)
    ca = ease_out_cubic(prog(t, 0.1, 0.35))
    place(frame, card, 540 + ox * 0.5, ccy + DY + (oy - DY) * 0.5, cs, cr, ca)

    for el in ELEMENTS:
        el.draw(frame, t, ox, oy)

    # botão CTA: entra com "pop" e pulsa
    if t >= 12.1:
        p = prog(t, 12.1, 0.42)
        s = lerp(0.3, 1.0, ease_out_back(p, 2.0))
        if t > 12.7:
            s *= 1 + 0.035 * (0.5 - 0.5 * math.cos((t - 12.7) * 2 * math.pi / 1.1))
        place(frame, CTA, 540 + ox, 1222 + oy, s, 0, ease_out_cubic(prog(t, 12.1, 0.15)))

    rgb = frame.convert("RGB")
    fade = ease_out_cubic(prog(t, 0.0, 0.35))
    if grain or fade < 1:
        arr = np.asarray(rgb).astype(np.float32)
        if grain:
            arr += GRAIN[int(t * FPS) % len(GRAIN)]
        arr *= fade
        rgb = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    return rgb


def _frame_bytes(i):
    return render(i / FPS).tobytes()


def main():
    args = sys.argv[1:]
    if args and args[0] == "--preview":
        os.makedirs(os.path.join(HERE, "preview"), exist_ok=True)
        for ts in args[1:]:
            p = os.path.join(HERE, "preview", f"t{float(ts):05.2f}.png")
            render(float(ts)).save(p)
            print(p)
        return

    cmd = [
        "ffmpeg", "-y", "-loglevel", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
        "-map", "0:v", "-map", "1:a", "-shortest",
        "-c:v", "libx264", "-preset", "slow", "-crf", "20", "-maxrate", "9M", "-bufsize", "18M",
        "-pix_fmt", "yuv420p", "-profile:v", "high", "-level", "4.1",
        "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart",
        OUT_MP4,
    ]
    ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    with Pool(os.cpu_count() or 2) as pool:
        for n, buf in enumerate(pool.imap(_frame_bytes, range(NFRAMES), chunksize=4)):
            ff.stdin.write(buf)
            if n % 60 == 0:
                print(f"frame {n}/{NFRAMES}", flush=True)
    ff.stdin.close()
    if ff.wait() != 0:
        sys.exit("ffmpeg falhou")
    render(14.2, grain=False).save(OUT_COVER, quality=93)
    print(OUT_MP4)
    print(OUT_COVER)


if __name__ == "__main__":
    main()
