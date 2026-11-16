#!/usr/bin/env python3
"""Prelúdio do culto · OPÇÃO B: documentário em película (1920x1080, mesma música).

Outra linguagem para as mesmas 8 frases: nada de brilho dourado nem partículas. Aqui o vídeo
parece filme: preto e branco quente, grão, poeira e riscos de película, leve tremor de projetor,
corte seco com queima de filme, tela de cinema (barras 2,39:1), serifa editorial alinhada à
esquerda, ênfases em itálico com um traço à mão e autores em máquina de escrever. Três frases
passam sobre imagens reais da igreja (roda de adoração) em câmera lenta, preto e branco.

Uso:
    python3 render_b.py                        # vídeo final -> preludio-culto-opcao-b.mp4
    python3 render_b.py --preview 4 20 80 127  # só quadros PNG em preview/
"""
from __future__ import annotations

import math
import os
import subprocess
import sys
from functools import lru_cache
from multiprocessing import Pool

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
A = lambda *p: os.path.join(HERE, "assets", *p)  # noqa: E731
CACHE = os.path.join(HERE, ".cache")
SRC = A("original.mp4")
OUT = os.path.join(HERE, "preludio-culto-opcao-b.mp4")

W, H, FPS = 1920, 1080, 30
DUR = 130.8
NFRAMES = int(round(DUR * FPS))
LB_T, LB_B = 138, 942   # tela de cinema 2,39:1
BH = LB_B - LB_T
X0 = 172                # margem esquerda do texto
T_END = 126.0
COUNTDOWN = True
USE_FOOTAGE = True      # False = todas as frases sobre preto de película (sem imagens da igreja)

F_SERIF = A("fonts", "DMSerifDisplay-Regular.ttf")
F_ITAL = A("fonts", "DMSerifDisplay-Italic.ttf")
F_MONO = A("fonts", "CourierPrime-Bold.ttf")

PAPER = (236, 229, 214)   # branco de papel (texto)
INK = (22, 20, 18)        # tinta (texto sobre papel)
RED = (212, 64, 32)       # vermelhão: único acento
BLACK = (9, 8, 7)

# ------------------------------------------------------------------ FRASES (corrigidas, caixa normal)
# linha: (atraso em s, [(texto, estilo[, atraso extra])]) · "r" romano · "i" itálico com traço à mão
QUOTES = [
    dict(t0=0.5, author="Leonard Ravenhill", author_t=9.1, plate=(0.6, 0.56), lines=[
        (0.25, [("“As únicas pessoas que querem", "r")]),
        (1.9, [("mudar o Evangelho", "i")]),
        (4.3, [("são aquelas que não são", "r")]),
        (6.2, [("mudadas por ele.”", "i")]),
    ]),
    dict(t0=15.8, author="John Piper", author_t=14.7, plate=None, lines=[
        (0.25, [("“Tire minhas pernas,", "r")]),
        (2.6, [("mas não minha ", "r"), ("Bíblia.", "i", 0.5)]),
        (6.5, [("Eu posso chegar ao céu sem andar,", "r")]),
        (10.7, [("mas não sem a ", "r"), ("Palavra de Deus.”", "i", 0.5)]),
    ]),
    dict(t0=34.7, author="John Piper", author_t=13.4, plate=None, lines=[
        (0.25, [("“Você quer ouvir a voz de Deus?", "r")]),
        (3.0, [("Leia a Bíblia.", "i")]),
        (7.0, [("Você quer ouvir a voz de Deus", "r")]),
        (8.1, [("audivelmente?", "r")]),
        (10.6, [("Leia a Bíblia em voz alta.”", "i")]),
    ]),
    dict(t0=54.4, author="Billy Graham", author_t=11.2, plate=None, lines=[
        (0.25, [("“Quando você se lembrar", "r")]),
        (2.2, [("de onde Deus te tirou,", "i")]),
        (5.6, [("vai parar de duvidar", "r")]),
        (8.0, [("de aonde Ele pode te levar.”", "i")]),
    ]),
    dict(t0=73.2, author="Leonard Ravenhill", author_t=8.0, plate=(5.0, 0.50), lines=[
        (0.25, [("“Se fracassarmos na ", "r"), ("oração,", "i", 0.45)]),
        (2.5, [("fracassaremos em toda", "r")]),
        (4.2, [("frente de batalha.”", "r")]),
    ]),
    dict(t0=86.8, author="David Wilkerson", author_t=8.6, plate=None, lines=[
        (0.25, [("“Estou cansado da música", "r")]),
        (2.2, [("que faz jovens pularem", "r")]),
        (4.6, [("em vez de ", "r"), ("dobrarem", "i", 0.4)]),
        (5.9, [("seus joelhos.”", "i")]),
    ]),
    dict(t0=100.1, author="David Wilkerson", author_t=9.9, plate=(9.0, 0.47), lines=[
        (0.25, [("“Não haverá renovação,", "r")]),
        (1.8, [("despertar, avivamento,", "r")]),
        (4.2, [("até que estejamos dispostos", "r")]),
        (5.6, [("a deixar que Ele mais uma vez", "r")]),
        (7.6, [("nos quebre.”", "i")]),
    ]),
    dict(t0=113.7, author="A. W. Tozer", author_t=9.6, plate=None, lines=[
        (0.25, [("“O verdadeiro ideal cristão", "r")]),
        (2.6, [("não é ser feliz,", "r")]),
        (5.6, [("mas ser ", "r"), ("santo.”", "i", 2.37)]),  # "santo" cai no ataque da música em 121,67 s
    ]),
]
for _i, _q in enumerate(QUOTES):  # cada frase vai até o corte para a próxima
    _q["t1"] = QUOTES[_i + 1]["t0"] if _i + 1 < len(QUOTES) else T_END
END_LINES = [(0.15, [("Nosso culto", "r")]), (0.55, [("se inicia agora!", "i")])]
CUTS = [q["t0"] for q in QUOTES[1:]] + [T_END]


# ------------------------------------------------------------------ util
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def lerp(a, b, t):
    return a + (b - a) * t


def prog(t, t0, d):
    return clamp((t - t0) / d)


def e_out_cubic(x):
    return 1 - (1 - clamp(x)) ** 3


def e_out_expo(x):
    x = clamp(x)
    return 1 if x >= 1 else 1 - 2 ** (-10 * x)


def e_in_cubic(x):
    return clamp(x) ** 3


@lru_cache(maxsize=None)
def font(path, size):
    return ImageFont.truetype(path, size)


# ------------------------------------------------------------------ imagens da igreja (P&B, câmera lenta)
PLATE_FPS = 24
PLATE_SLOW = 0.3


def extract_plates():
    """Quadros da roda de adoração: vídeo vertical -> recorte 16:9 em P&B (dois enquadramentos)."""
    for name, cy in (("p47", 0.47), ("p50", 0.50), ("p56", 0.56)):
        d = os.path.join(CACHE, name)
        if os.path.isdir(d) and len(os.listdir(d)) > 100:
            continue
        os.makedirs(d, exist_ok=True)
        y0 = int(1280 * cy - 405 / 2)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", A("adoracao.mp4"), "-vf",
                        f"fps={PLATE_FPS},crop=720:405:0:{y0},hqdn3d=2:2:5:5,scale={W}:{H}:flags=lanczos,format=gray",
                        "-q:v", "2", os.path.join(d, "%04d.jpg")], check=True)


@lru_cache(maxsize=8)
def _plate_frame(name, idx):
    d = os.path.join(CACHE, name)
    n = len(os.listdir(d))
    return np.asarray(Image.open(os.path.join(d, f"{int(clamp(idx, 0, n - 1)) + 1:04d}.jpg")).convert("L"), np.float32)


def _left_shade():
    xx = np.linspace(0, 1, W, dtype=np.float32)[None, :]
    yy = np.linspace(-1, 1, BH, dtype=np.float32)[:, None]
    g = 0.22 + 0.78 * np.clip((xx - 0.18) / 0.72, 0, 1) ** 1.3   # esquerda escura (texto), direita aberta
    return g * (1 - 0.35 * yy ** 2)


LEFT_SHADE = _left_shade()


def plate(q, t):
    """Fundo com imagem real: P&B contrastado, escurecido à esquerda, com aproximação lenta."""
    s0, cy = q["plate"]
    name = {0.47: "p47", 0.50: "p50", 0.56: "p56"}[cy]
    f = (s0 + (t - q["t0"]) * PLATE_SLOW) * PLATE_FPS
    i0 = int(math.floor(f))
    a, b = _plate_frame(name, i0), _plate_frame(name, i0 + 1)
    g = a + (b - a) * (f - i0)
    z = lerp(1.02, 1.09, prog(t, q["t0"], q["t1"] - q["t0"]))
    img = Image.fromarray(g, "F").transform((W, BH), Image.AFFINE,
                                            (1 / z, 0, (W - W / z) / 2, 0, 1 / z, (H - BH / z) / 2), resample=Image.BILINEAR)
    g = np.asarray(img) / 255.0
    g = np.clip((g - 0.06) * 1.18, 0, 1) ** 1.25      # contraste de película
    return g * LEFT_SHADE * 0.78


# ------------------------------------------------------------------ texturas analógicas (pré-cálculo)
rng = np.random.default_rng(1957)


def _smooth_noise(w, h, n):
    small = rng.random((max(2, n * h // w + 2), n + 2)).astype(np.float32)
    return np.asarray(Image.fromarray(small, "F").resize((w, h), Image.BICUBIC))


# luz de projetor: mancha suave e irregular (cenas sem imagem)
def _lamp():
    yy, xx = np.mgrid[0:BH, 0:W].astype(np.float32)
    r = np.hypot((xx - W * 0.66) / (W * 0.62), (yy - BH * 0.46) / (BH * 0.85))
    return (np.clip(1 - r, 0, 1) ** 1.8 * (0.75 + 0.5 * _smooth_noise(W, BH, 5))).astype(np.float32)


LAMP = _lamp()
# papel (cartela final)
PAPER_TEX = (0.90 + 0.10 * _smooth_noise(W, BH, 9) + rng.normal(0, 0.012, (BH, W))).astype(np.float32)
GRAIN = [rng.normal(0, 1, (BH // 2, W // 2)).astype(np.float32) for _ in range(10)]


def _vig():
    yy = np.linspace(-1, 1, BH, dtype=np.float32)[:, None]
    xx = np.linspace(-1, 1, W, dtype=np.float32)[None, :]
    return (1 - np.clip(xx ** 2 * 0.55 + yy ** 2 * 0.45 - 0.28, 0, 1) * 0.6).astype(np.float32)


VIG = _vig()


def _burn():
    """Queima de filme: manchas quentes desfocadas (aplicadas em 'screen' nos cortes)."""
    # textura com o dobro da largura: a janela desliza sobre ela, sem emenda
    img = Image.new("RGB", (W // 2, BH // 4), (0, 0, 0))
    d = ImageDraw.Draw(img)
    for (x, y, r, c) in [(60, 40, 120, (255, 96, 24)), (250, 150, 150, (255, 170, 60)), (420, 60, 130, (255, 60, 20)),
                         (150, 190, 90, (255, 210, 150)), (350, 20, 70, (255, 230, 190)), (560, 120, 140, (255, 110, 30)),
                         (700, 40, 110, (255, 190, 90)), (860, 170, 130, (255, 70, 24)), (640, 200, 80, (255, 225, 170))]:
        d.ellipse((x - r, y - r, x + r, y + r), fill=c)
    img = img.filter(ImageFilter.GaussianBlur(34)).resize((W * 2, BH), Image.BICUBIC)
    return np.asarray(img).astype(np.float32) / 255


BURN = _burn()


# ------------------------------------------------------------------ tipografia
def seg_sprite(text, size, style, color):
    """Trecho de texto numa caixa com a altura da linha. Devolve (img RGBA, avanço, x0 da tinta, x1 da tinta)."""
    return _seg_sprite(text, size, style, color)


@lru_cache(maxsize=None)
def _seg_sprite(text, size, style, color):
    f = font(F_ITAL if style == "i" else F_SERIF, size)
    asc, desc = font(F_SERIF, size).getmetrics()
    pad = int(size * 0.22)
    adv = f.getlength(text)
    img = Image.new("RGBA", (int(adv) + 2 * pad, asc + desc), (0, 0, 0, 0))
    ImageDraw.Draw(img).text((pad, asc), text, font=f, fill=color + (255,), anchor="ls")
    l, _, r, _ = f.getbbox(text.rstrip(), anchor="ls")
    return img, adv, l, r, pad


@lru_cache(maxsize=None)
def stroke_sprite(width, size, seed):
    """Traço à mão (sublinhado): contorno irregular, espessura variável, falhas de pincel seco."""
    r = np.random.default_rng(seed)
    th = max(5.0, size * 0.062)
    w, h = int(width + 34), int(th * 4)
    S = 3  # superamostragem
    n = max(4, w // 26)
    xs = np.linspace(0, w * S, n)
    mid = h * S / 2 + np.cumsum(r.normal(0, th * 0.16 * S, n)) * 0.5 + np.linspace(0, r.normal(0, th * 0.5) * S, n)
    half = th * S / 2 * (0.75 + 0.5 * r.random(n))
    half[0], half[-1] = half[0] * 0.35, half[-1] * 0.25
    X = np.arange(w * S)
    top = np.interp(X, xs, mid - half)
    bot = np.interp(X, xs, mid + half)
    Y = np.arange(h * S)[:, None]
    m = ((Y >= top[None, :]) & (Y <= bot[None, :])).astype(np.float32)
    # pincel seco: falhas mais fortes no fim do traço
    tex = np.asarray(Image.fromarray(r.random((h * S // 3 + 2, w * S // 10 + 2)).astype(np.float32), "F")
                     .resize((w * S, h * S), Image.BICUBIC))
    fade = np.clip((X / (w * S) - 0.55) / 0.45, 0, 1)[None, :]
    m *= np.clip((tex - 0.42 * fade) * 6 + 0.5, 0, 1)
    a = Image.fromarray((m * 255).astype(np.uint8)).resize((w, h), Image.LANCZOS)
    img = Image.new("RGBA", (w, h), RED + (0,))
    img.putalpha(a)
    return img


def paste(frame, img, x, y):
    x, y = int(round(x)), int(round(y))
    sx, sy = max(0, -x), max(0, -y)
    ex, ey = min(img.width, frame.width - x), min(img.height, frame.height - y)
    if ex <= sx or ey <= sy:
        return
    if sx or sy or ex < img.width or ey < img.height:
        img = img.crop((sx, sy, ex, ey))
    frame.alpha_composite(img, (x + sx, y + sy))


LEAD = 1.17
MAXW, MAXH = 1400, 560
CYB = 392  # centro vertical do bloco, medido dentro da tela de cinema


def fit_lines(lines, smax=132):
    s = smax
    while s > 40:
        ws = [sum(font(F_ITAL if sg[1] == "i" else F_SERIF, s).getlength(sg[0]) for sg in segs) for _, segs in lines]
        cap = s * 0.67
        height = cap + (len(lines) - 1) * s * LEAD
        if max(ws) <= MAXW and height <= MAXH:
            return s, height
        s -= 2
    return s, height


def draw_lines(layer, lines, t, t_base, color, s, height, seed0):
    """Linhas alinhadas à esquerda; cada trecho sobe de trás da linha de base (máscara)."""
    asc, desc = font(F_SERIF, s).getmetrics()
    base = CYB - height / 2 + s * 0.67
    last_seen = None
    for li, (off, segs) in enumerate(lines):
        x = X0
        for si, sg in enumerate(segs):
            text, style = sg[0], sg[1]
            tr = t_base + off + (sg[2] if len(sg) > 2 else 0.0)
            img, adv, il, ir, pad = seg_sprite(text, s, style, color)
            if t >= tr:
                p = e_out_expo(prog(t, tr, 0.75))
                dy = int(round((1 - p) * (asc + desc)))
                vis = img.crop((0, 0, img.width, img.height - dy)) if dy else img
                paste(layer, vis, x - pad, base - asc + dy)
                last_seen = base
                if style == "i":  # traço à mão sob a ênfase
                    ps = e_out_cubic(prog(t, tr + 0.5, 0.6))
                    if ps > 0:
                        st = stroke_sprite(int(ir - il), s, seed0 * 100 + li * 10 + si)
                        cut = st.crop((0, 0, max(1, int(st.width * ps)), st.height))
                        paste(layer, cut, x + il - 12, base + s * 0.17 - st.height / 2)
            x += adv
        base += s * LEAD
    return last_seen, base - s * LEAD


def draw_author(layer, name, t, ta, y, color):
    """Autor datilografado, letra por letra."""
    if t < ta:
        return
    txt = "— " + name.upper()
    n = int(clamp((t - ta) * 22, 0, len(txt)))
    f = font(F_MONO, 38)
    d = ImageDraw.Draw(layer)
    x = X0 + 4
    for c in txt[:n]:
        d.text((x, y), c, font=f, fill=color + (235,), anchor="ls")
        x += f.getlength(c) + 3
    if n < len(txt) or (t - ta) % 1.0 < 0.5 and t - ta < 3.0:  # cursor
        d.rectangle((x + 2, y - 29, x + 18, y + 2), fill=RED + (230,))


# ------------------------------------------------------------------ película
def film(arr, t, i):
    """Aplica o 'filme' ao conteúdo da tela (H=BH): halação, tremor, cintilação, grão, poeira e riscos."""
    r = np.random.default_rng(900 + i)
    # halação: altas luzes vazam um brilho avermelhado
    small = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).resize((W // 8, BH // 8), Image.BILINEAR)
    small = small.filter(ImageFilter.GaussianBlur(5)).resize((W, BH), Image.BILINEAR)
    hl = np.clip(np.asarray(small).astype(np.float32) - 105, 0, None)
    dark = 1 - clamp(float(arr.mean()) / 150)  # cena clara (papel) quase não recebe halação
    arr = arr + hl * np.array([0.55, 0.22, 0.10], np.float32) * dark
    # tremor de projetor (gate weave) + suavização leve da imagem digital
    dx = 1.3 * math.sin(t * 1.9) + 0.7 * math.sin(t * 4.7 + 1) + r.normal(0, 0.25)
    dy = 1.0 * math.sin(t * 2.6 + 2) + 0.6 * math.sin(t * 6.1) + r.normal(0, 0.25)
    img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    img = img.transform((W, BH), Image.AFFINE, (1, 0, dx, 0, 1, dy), resample=Image.BILINEAR)
    arr = np.asarray(img.filter(ImageFilter.GaussianBlur(0.55))).astype(np.float32)
    # cintilação de exposição
    arr *= 1 + r.normal(0, 0.012)
    # pretos levantados e tom quente
    arr = 9 + arr * 0.955
    arr *= 1 + (VIG[..., None] - 1) * (0.35 + 0.65 * dark)  # vinheta mais leve no papel
    # grão (mais forte nos meios-tons)
    g = GRAIN[i % len(GRAIN)]
    g = np.repeat(np.repeat(g, 2, axis=0), 2, axis=1)
    lum = arr.mean(axis=2)
    arr += (g * (3.2 + 5.5 * np.clip(lum / 255, 0, 1) * (1 - np.clip(lum / 255, 0, 1)) * 4))[..., None]
    out = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(out, "RGBA")
    # poeira: pontos que duram um quadro
    for _ in range(r.poisson(1.6)):
        x, y, rad = r.integers(0, W), r.integers(0, BH), r.uniform(0.8, 2.6)
        c = (235, 228, 214, int(r.uniform(90, 200))) if r.random() < 0.6 else (0, 0, 0, int(r.uniform(120, 220)))
        d.ellipse((x - rad, y - rad, x + rad, y + rad), fill=c)
    if r.random() < 0.035:  # fio de cabelo
        x, y = r.integers(100, W - 100), r.integers(60, BH - 60)
        pts = [(x + k * 9 + r.normal(0, 3), y + 14 * math.sin(k * 0.7 + r.random() * 6)) for k in range(7)]
        d.line(pts, fill=(0, 0, 0, 150), width=1)
    # riscos verticais: duram de 0,4 a 1,2 s
    for k in range(int(t // 0.4) - 3, int(t // 0.4) + 1):
        rs = np.random.default_rng(5000 + k)
        if rs.random() < 0.16:
            life = rs.uniform(0.4, 1.2)
            if k * 0.4 <= t < k * 0.4 + life:
                x = rs.integers(40, W - 40) + r.normal(0, 0.6)
                d.line((x, 0, x + rs.normal(0, 2), BH), fill=(240, 232, 218, int(rs.uniform(28, 70))), width=1)
    return out


# ------------------------------------------------------------------ barras: contagem e índice (limpos, fora do filme)
def hud(frame, t, qi):
    d = ImageDraw.Draw(frame, "RGBA")
    f = font(F_MONO, 31)
    a = e_out_cubic(prog(t, 0.6, 0.8)) * (1 - e_in_cubic(prog(t, 129.2, 1.2)))
    if a <= 0:
        return
    col = PAPER + (int(185 * a),)
    y = 86

    def mono(x, text, fill, right=False):
        adv = f.getlength("0") + 3
        if right:
            x -= adv * len(text)
        for c in text:
            d.text((x + (adv - f.getlength(c)) / 2, y), c, font=f, fill=fill, anchor="ls")
            x += adv
    if qi is not None:
        mono(X0, f"{qi + 1:02d}/{len(QUOTES):02d}", col)
    if COUNTDOWN:
        left = max(0, int(math.ceil(T_END - t)))
        txt = f"COMEÇA EM {left // 60:02d}:{left % 60:02d}" if t < T_END else "AGORA"
        mono(W - X0, txt, col, right=True)
        adv = f.getlength("0") + 3
        if (t % 1.0) < 0.6:
            cx = W - X0 - adv * len(txt) - 22
            d.ellipse((cx - 7, y - 16, cx + 7, y - 2), fill=RED + (int(255 * a),))
        # fio de progresso na barra de baixo
        yb = H - 70
        d.rectangle((X0, yb, W - X0, yb), fill=PAPER + (int(60 * a),))
        d.rectangle((X0, yb - 1, X0 + (W - 2 * X0) * clamp(t / T_END), yb + 1), fill=RED + (int(235 * a),))


# ------------------------------------------------------------------ quadro
def compose(t: float) -> Image.Image:
    i = int(round(t * FPS))
    qi = next((k for k, q in enumerate(QUOTES) if q["t0"] <= t < q["t1"]), None)
    end = t >= T_END

    # ---- fundo da tela (tons de cinza 0..1)
    if end:
        bg = PAPER_TEX * 0.94
    elif qi is not None and QUOTES[qi]["plate"] and USE_FOOTAGE:
        bg = plate(QUOTES[qi], t)
    else:
        breathe = 0.85 + 0.15 * math.sin(t * 0.5)
        bg = 0.016 + LAMP * 0.085 * breathe
    tone = np.array(PAPER, np.float32) if end else np.array([255, 247, 232], np.float32)  # P&B levemente quente
    arr = bg[..., None] * tone

    # ---- texto (camada própria, dentro da tela)
    layer = Image.new("RGBA", (W, BH), (0, 0, 0, 0))
    if end:
        s, hgt = fit_lines(END_LINES, 170)
        draw_lines(layer, END_LINES, t, T_END, INK, s, hgt, 99)
    elif qi is not None:
        q = QUOTES[qi]
        s, hgt = fit_lines(q["lines"])
        seen, last = draw_lines(layer, q["lines"], t, q["t0"], PAPER, s, hgt, qi)
        # fio vertical de citação, cresce com as linhas
        if seen is not None:
            top = CYB - hgt / 2 - 6
            d = ImageDraw.Draw(layer)
            d.rectangle((X0 - 44, top, X0 - 41, seen + 8), fill=PAPER + (70,))
        draw_author(layer, q["author"], t, q["t0"] + q["author_t"], last + s * 0.34 + 74, PAPER)
    # leve aproximação de câmera no texto
    if qi is not None and not end:
        q = QUOTES[qi]
        z = lerp(1.0, 1.03, prog(t, q["t0"], q["t1"] - q["t0"]))
        layer = layer.transform((W, BH), Image.AFFINE, (1 / z, 0, X0 * (1 - 1 / z), 0, 1 / z, CYB * (1 - 1 / z)),
                                resample=Image.BICUBIC)
    base = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).convert("RGBA")
    base.alpha_composite(layer)
    arr = np.asarray(base.convert("RGB")).astype(np.float32)

    # ---- queima de filme nos cortes
    for tc in CUTS:
        dt = t - tc
        if -0.2 <= dt < 0.4:
            k = (1 + dt / 0.2) if dt < 0 else (1 - dt / 0.4) ** 1.6
            big = 1.5 if tc == T_END else 1.0
            x0 = int(clamp((tc * 977) % (W * 0.6) + (dt + 0.2) * 700, 0, W))
            lk = BURN[:, x0: x0 + W] * (255 * 0.78 * k * big)
            arr = 255 - (255 - arr) * (255 - np.clip(lk, 0, 255)) / 255
            if 0 <= dt < 0.07:
                arr = arr + (255 - arr) * 0.55 * big / 1.5
    band = film(arr, t, i)

    frame = Image.new("RGB", (W, H), BLACK)
    frame.paste(band, (0, LB_T))
    frame = frame.convert("RGBA")
    hud(frame, t, None if end else qi)
    out = frame.convert("RGB")
    fade = e_out_cubic(prog(t, 0.0, 1.0)) * (1 - e_in_cubic(prog(t, 129.3, 1.3)))
    if fade < 0.999:
        out = Image.eval(out, lambda v: int(v * fade))
    return out


# ------------------------------------------------------------------ main
def _frame(i):
    return compose(i / FPS).tobytes()


def encode(master, crf="24", maxrate="2900k"):
    """Vídeo final: H.264 + o áudio ORIGINAL copiado sem recompressão."""
    subprocess.run([
        "ffmpeg", "-v", "error", "-y", "-i", master, "-i", SRC, "-map", "0:v", "-map", "1:a",
        "-c:v", "libx264", "-preset", "slow", "-crf", crf, "-maxrate", maxrate, "-bufsize", "9M",
        "-x264-params", "aq-mode=3", "-pix_fmt", "yuv420p", "-profile:v", "high", "-level", "4.2",
        "-c:a", "copy", "-movflags", "+faststart", OUT,
    ], check=True)


def main():
    os.makedirs(CACHE, exist_ok=True)
    if USE_FOOTAGE:
        extract_plates()
    args = sys.argv[1:]
    if args and args[0] == "--preview":
        os.makedirs(os.path.join(HERE, "preview"), exist_ok=True)
        for ts in args[1:]:
            p = os.path.join(HERE, "preview", f"b_t{float(ts):06.2f}.png")
            compose(float(ts)).save(p)
            print(p)
        return
    master = os.path.join(CACHE, "master_b.mp4")
    ff = subprocess.Popen([
        "ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
        "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "12",
        "-pix_fmt", "yuv420p", master,
    ], stdin=subprocess.PIPE)
    with Pool(os.cpu_count() or 2) as pool:
        for n, buf in enumerate(pool.imap(_frame, range(NFRAMES), chunksize=4)):
            ff.stdin.write(buf)
            if n % 300 == 0:
                print(f"quadro {n}/{NFRAMES}", flush=True)
    ff.stdin.close()
    if ff.wait():
        sys.exit("ffmpeg falhou")
    encode(master)
    print(OUT)


if __name__ == "__main__":
    main()
