#!/usr/bin/env python3
"""Prelúdio do culto · OPÇÃO B: documentário em película, nas cores da Igreja Evangélica Atos.

Mesmas 8 frases e mesma música, com cara de filme: preto de película com grão, poeira, riscos e leve
tremor de projetor; corte seco com vazamento de luz; tela de cinema (barras 2,39:1); serifa editorial
alinhada à esquerda; ênfases em itálico com um traço à mão; autores em máquina de escrever.
Identidade da igreja: detalhes em azul (#233DFF) e prata, e a logo pequena no canto inferior direito.

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

F_SERIF = A("fonts", "DMSerifDisplay-Regular.ttf")
F_ITAL = A("fonts", "DMSerifDisplay-Italic.ttf")
F_MONO = A("fonts", "CourierPrime-Bold.ttf")

# Cores da Igreja Evangélica Atos: azul e prata
TEXT = (236, 239, 245)    # branco prateado (frases)
SILVER = (186, 194, 206)  # prata (autor, fios, contagem)
BLUE = (35, 61, 255)      # azul da marca (#233DFF)
BLUE_L = (96, 124, 255)   # o mesmo azul, mais claro, para os traços sobre o preto
INK = (12, 18, 44)        # azul-marinho quase preto (texto sobre a cartela clara)
CARD = (212, 218, 227)    # prata claro (cartela final)
BLACK = (6, 7, 11)
LOGO_W = 178              # largura da logo no canto (px)

# ------------------------------------------------------------------ FRASES (corrigidas, caixa normal)
# linha: (atraso em s, [(texto, estilo[, atraso extra])]) · "r" romano · "i" itálico com traço à mão
QUOTES = [
    dict(t0=0.5, author="Leonard Ravenhill", author_t=9.1, lines=[
        (0.25, [("“As únicas pessoas que querem", "r")]),
        (1.9, [("mudar o Evangelho", "i")]),
        (4.3, [("são aquelas que não são", "r")]),
        (6.2, [("mudadas por ele.”", "i")]),
    ]),
    dict(t0=15.8, author="John Piper", author_t=14.7, lines=[
        (0.25, [("“Tire minhas pernas,", "r")]),
        (2.6, [("mas não minha ", "r"), ("Bíblia.", "i", 0.5)]),
        (6.5, [("Eu posso chegar ao céu sem andar,", "r")]),
        (10.7, [("mas não sem a ", "r"), ("Palavra de Deus.”", "i", 0.5)]),
    ]),
    dict(t0=34.7, author="John Piper", author_t=13.4, lines=[
        (0.25, [("“Você quer ouvir a voz de Deus?", "r")]),
        (3.0, [("Leia a Bíblia.", "i")]),
        (7.0, [("Você quer ouvir a voz de Deus", "r")]),
        (8.1, [("audivelmente?", "r")]),
        (10.6, [("Leia a Bíblia em voz alta.”", "i")]),
    ]),
    dict(t0=54.4, author="Billy Graham", author_t=11.2, lines=[
        (0.25, [("“Quando você se lembrar", "r")]),
        (2.2, [("de onde Deus te tirou,", "i")]),
        (5.6, [("vai parar de duvidar", "r")]),
        (8.0, [("de aonde Ele pode te levar.”", "i")]),
    ]),
    dict(t0=73.2, author="Leonard Ravenhill", author_t=8.0, lines=[
        (0.25, [("“Se fracassarmos na ", "r"), ("oração,", "i", 0.45)]),
        (2.5, [("fracassaremos em toda", "r")]),
        (4.2, [("frente de batalha.”", "r")]),
    ]),
    dict(t0=86.8, author="David Wilkerson", author_t=8.6, lines=[
        (0.25, [("“Estou cansado da música", "r")]),
        (2.2, [("que faz jovens pularem", "r")]),
        (4.6, [("em vez de ", "r"), ("dobrarem", "i", 0.4)]),
        (5.9, [("seus joelhos.”", "i")]),
    ]),
    dict(t0=100.1, author="David Wilkerson", author_t=9.9, lines=[
        (0.25, [("“Não haverá renovação,", "r")]),
        (1.8, [("despertar, avivamento,", "r")]),
        (4.2, [("até que estejamos dispostos", "r")]),
        (5.6, [("a deixar que Ele mais uma vez", "r")]),
        (7.6, [("nos quebre.”", "i")]),
    ]),
    dict(t0=113.7, author="A. W. Tozer", author_t=9.6, lines=[
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
    """Vazamento de luz nos cortes: manchas azuis e prateadas desfocadas (aplicadas em 'screen')."""
    # textura com o dobro da largura: a janela desliza sobre ela, sem emenda
    img = Image.new("RGB", (W // 2, BH // 4), (0, 0, 0))
    d = ImageDraw.Draw(img)
    for (x, y, r, c) in [(60, 40, 120, (40, 70, 255)), (250, 150, 150, (120, 150, 255)), (420, 60, 130, (30, 50, 230)),
                         (150, 190, 90, (190, 205, 255)), (350, 20, 70, (225, 232, 255)), (560, 120, 140, (50, 84, 255)),
                         (700, 40, 110, (150, 175, 255)), (860, 170, 130, (34, 58, 240)), (640, 200, 80, (215, 225, 255))]:
        d.ellipse((x - r, y - r, x + r, y + r), fill=c)
    img = img.filter(ImageFilter.GaussianBlur(34)).resize((W * 2, BH), Image.BICUBIC)
    return np.asarray(img).astype(np.float32) / 255


BURN = _burn()


def _logo(color, opacity):
    """Logo da igreja (PNG branco com fundo transparente) recolorida e reduzida para o canto."""
    src = Image.open(A("logo-atos.png")).convert("RGBA")
    h = round(src.height * LOGO_W / src.width)
    alpha = src.getchannel("A").resize((LOGO_W, h), Image.LANCZOS).point(lambda v: int(v * opacity))
    img = Image.new("RGBA", (LOGO_W, h), color + (0,))
    img.putalpha(alpha)
    return img


LOGO_LIGHT = _logo(TEXT, 0.9)   # sobre o preto
LOGO_INK = _logo(INK, 0.95)     # sobre a cartela prata


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
def stroke_sprite(width, size, seed, color):
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
    img = Image.new("RGBA", (w, h), color + (0,))
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
MAXW, MAXH = 1300, 560  # a largura deixa o canto direito livre para a logo
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


def draw_lines(layer, lines, t, t_base, color, s, height, seed0, stroke_color):
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
                        st = stroke_sprite(int(ir - il), s, seed0 * 100 + li * 10 + si, stroke_color)
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
        d.rectangle((x + 2, y - 29, x + 18, y + 2), fill=BLUE_L + (235,))


# ------------------------------------------------------------------ película
def film(arr, t, i):
    """Aplica o 'filme' ao conteúdo da tela (H=BH): halação, tremor, cintilação, grão, poeira e riscos."""
    r = np.random.default_rng(900 + i)
    # halação: altas luzes vazam um brilho avermelhado
    small = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).resize((W // 8, BH // 8), Image.BILINEAR)
    small = small.filter(ImageFilter.GaussianBlur(5)).resize((W, BH), Image.BILINEAR)
    hl = np.clip(np.asarray(small).astype(np.float32) - 105, 0, None)
    dark = 1 - clamp(float(arr.mean()) / 150)  # cena clara (papel) quase não recebe halação
    arr = arr + hl * np.array([0.16, 0.26, 0.58], np.float32) * dark  # brilho frio, azulado
    # tremor de projetor (gate weave) + suavização leve da imagem digital
    dx = 1.3 * math.sin(t * 1.9) + 0.7 * math.sin(t * 4.7 + 1) + r.normal(0, 0.25)
    dy = 1.0 * math.sin(t * 2.6 + 2) + 0.6 * math.sin(t * 6.1) + r.normal(0, 0.25)
    img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    img = img.transform((W, BH), Image.AFFINE, (1, 0, dx, 0, 1, dy), resample=Image.BILINEAR)
    arr = np.asarray(img.filter(ImageFilter.GaussianBlur(0.55))).astype(np.float32)
    # cintilação de exposição
    arr *= 1 + r.normal(0, 0.012)
    # pretos levantados, puxados para o azul
    arr = np.array([6, 7, 12], np.float32) + arr * 0.955
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
        c = (226, 232, 244, int(r.uniform(90, 200))) if r.random() < 0.6 else (0, 0, 0, int(r.uniform(120, 220)))
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
                d.line((x, 0, x + rs.normal(0, 2), BH), fill=(226, 232, 244, int(rs.uniform(28, 70))), width=1)
    return out


# ------------------------------------------------------------------ barras: contagem e índice (limpos, fora do filme)
def hud(frame, t, qi):
    d = ImageDraw.Draw(frame, "RGBA")
    f = font(F_MONO, 31)
    a = e_out_cubic(prog(t, 0.6, 0.8)) * (1 - e_in_cubic(prog(t, 129.2, 1.2)))
    if a <= 0:
        return
    col = SILVER + (int(215 * a),)
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
            d.ellipse((cx - 7, y - 16, cx + 7, y - 2), fill=BLUE_L + (int(255 * a),))
        # fio de progresso na barra de baixo
        yb = H - 70
        d.rectangle((X0, yb, W - X0, yb), fill=SILVER + (int(70 * a),))
        d.rectangle((X0, yb - 1, X0 + (W - 2 * X0) * clamp(t / T_END), yb + 1), fill=BLUE_L + (int(245 * a),))


# ------------------------------------------------------------------ quadro
def compose(t: float) -> Image.Image:
    i = int(round(t * FPS))
    qi = next((k for k, q in enumerate(QUOTES) if q["t0"] <= t < q["t1"]), None)
    end = t >= T_END

    # ---- fundo da tela: preto de película com uma luz azul suave (ou a cartela prata no final)
    if end:
        arr = (PAPER_TEX * 0.96)[..., None] * np.array(CARD, np.float32)
    else:
        breathe = 0.85 + 0.15 * math.sin(t * 0.5)
        arr = np.array([3, 4, 7], np.float32) + (LAMP * breathe)[..., None] * np.array([14, 24, 86], np.float32)

    # ---- texto (camada própria, dentro da tela)
    layer = Image.new("RGBA", (W, BH), (0, 0, 0, 0))
    if end:
        s, hgt = fit_lines(END_LINES, 170)
        draw_lines(layer, END_LINES, t, T_END, INK, s, hgt, 99, BLUE)
    elif qi is not None:
        q = QUOTES[qi]
        s, hgt = fit_lines(q["lines"])
        seen, last = draw_lines(layer, q["lines"], t, q["t0"], TEXT, s, hgt, qi, BLUE_L)
        # fio vertical de citação, cresce com as linhas
        if seen is not None:
            top = CYB - hgt / 2 - 6
            d = ImageDraw.Draw(layer)
            d.rectangle((X0 - 44, top, X0 - 41, seen + 8), fill=SILVER + (95,))
        draw_author(layer, q["author"], t, q["t0"] + q["author_t"], last + s * 0.34 + 74, SILVER)
    # leve aproximação de câmera no texto
    if qi is not None and not end:
        q = QUOTES[qi]
        z = lerp(1.0, 1.03, prog(t, q["t0"], q["t1"] - q["t0"]))
        layer = layer.transform((W, BH), Image.AFFINE, (1 / z, 0, X0 * (1 - 1 / z), 0, 1 / z, CYB * (1 - 1 / z)),
                                resample=Image.BICUBIC)
    base = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).convert("RGBA")
    base.alpha_composite(layer)
    # logo da igreja, pequena, no canto inferior direito (entra junto com o filme: ganha grão e tremor)
    la = e_out_cubic(prog(t, 0.8, 1.2))
    if la > 0:
        lg = LOGO_INK if end else LOGO_LIGHT
        if la < 0.999:
            lg = lg.copy()
            lg.putalpha(lg.getchannel("A").point(lambda v: int(v * la)))
        base.alpha_composite(lg, (W - X0 - lg.width, BH - 40 - lg.height))
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
