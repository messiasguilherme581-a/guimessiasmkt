#!/usr/bin/env python3
"""Prelúdio do culto · frases com impacto (1920x1080, mesma música do vídeo original).

Refaz o vídeo `assets/original.mp4` (texto parado sobre partículas) em versão cinematográfica:
fundo novo em Full HD (névoa, raios de luz e poeira dourada que reagem à música), frases entrando
palavra por palavra com as palavras-chave em dourado, autores com a grafia corrigida, contagem
regressiva discreta e cartela final. O áudio é copiado do original sem recompressão.

Uso:
    python3 render.py                       # vídeo final -> preludio-culto.mp4
    python3 render.py --preview 3 20 46 127 # só quadros PNG em preview/
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
from scipy.ndimage import gaussian_filter

HERE = os.path.dirname(os.path.abspath(__file__))
A = lambda *p: os.path.join(HERE, "assets", *p)  # noqa: E731
CACHE = os.path.join(HERE, ".cache")
SRC = A("original.mp4")
OUT = os.path.join(HERE, "preludio-culto.mp4")

W, H, FPS = 1920, 1080, 30
DUR = 130.8
NFRAMES = int(round(DUR * FPS))
T_END = 126.0          # cartela final entra no ataque da música em 126,0 s
COUNTDOWN = True       # contagem regressiva discreta até a cartela final

F_ANTON = A("fonts", "Anton-Regular.ttf")
F_LABEL = "/usr/share/fonts/opentype/inter/InterDisplay-SemiBold.otf"

WHITE = (247, 244, 236)
GOLD_TOP, GOLD_BOT = (255, 233, 176), (224, 156, 58)
GOLD = (240, 190, 105)

# ------------------------------------------------------------------ FRASES (já corrigidas)
# Cada linha: (atraso em s desde o início da frase, escala, [(texto, estilo)]) · estilo: "w" branco, "g" dourado
QUOTES = [
    dict(t0=0.5, t1=15.4, author="LEONARD RAVENHILL", author_t=8.9, lines=[
        (0.0, 1.00, [("“AS ÚNICAS PESSOAS QUE QUEREM", "w")]),
        (1.9, 1.30, [("MUDAR O EVANGELHO", "g")]),
        (4.3, 1.00, [("SÃO AQUELAS QUE NÃO SÃO", "w")]),
        (6.2, 1.30, [("MUDADAS POR ELE.”", "g")]),
    ]),
    dict(t0=15.8, t1=34.3, author="JOHN PIPER", author_t=14.7, lines=[
        (0.0, 1.00, [("“TIRE MINHAS PERNAS,", "w")]),
        (2.6, 1.25, [("MAS NÃO MINHA", "w"), ("BÍBLIA.", "g")]),
        (6.5, 1.00, [("EU POSSO CHEGAR AO CÉU SEM ANDAR,", "w")]),
        (11.2, 1.25, [("MAS NÃO SEM A", "w"), ("PALAVRA DE DEUS.”", "g")]),
    ]),
    dict(t0=34.7, t1=54.0, author="JOHN PIPER", author_t=13.2, lines=[
        (0.0, 1.00, [("“VOCÊ QUER OUVIR A VOZ DE DEUS?", "w")]),
        (3.0, 1.35, [("LEIA A BÍBLIA.", "g")]),
        (7.0, 1.00, [("VOCÊ QUER OUVIR A VOZ DE DEUS AUDIVELMENTE?", "w")]),
        (10.6, 1.35, [("LEIA A BÍBLIA EM VOZ ALTA.”", "g")]),
    ]),
    dict(t0=54.4, t1=72.9, author="BILLY GRAHAM", author_t=11.0, lines=[
        (0.0, 1.00, [("“QUANDO VOCÊ SE LEMBRAR", "w")]),
        (2.2, 1.25, [("DE ONDE DEUS TE TIROU,", "g")]),
        (5.6, 1.00, [("VAI PARAR DE DUVIDAR", "w")]),
        (8.0, 1.25, [("DE AONDE ELE PODE TE LEVAR.”", "g")]),
    ]),
    dict(t0=73.2, t1=86.4, author="LEONARD RAVENHILL", author_t=8.0, lines=[
        (0.0, 1.20, [("“SE FRACASSARMOS NA", "w"), ("ORAÇÃO,", "g")]),
        (2.5, 1.00, [("FRACASSAREMOS EM TODA", "w")]),
        (4.2, 1.20, [("FRENTE DE BATALHA.”", "w")]),
    ]),
    dict(t0=86.8, t1=99.7, author="DAVID WILKERSON", author_t=8.4, lines=[
        (0.0, 1.00, [("“ESTOU CANSADO DA MÚSICA", "w")]),
        (2.2, 1.00, [("QUE FAZ JOVENS PULAREM", "w")]),
        (4.6, 1.00, [("EM VEZ DE", "w"), ("DOBRAREM", "g")]),
        (5.8, 1.35, [("SEUS JOELHOS.”", "g")]),
    ]),
    dict(t0=100.1, t1=113.3, author="DAVID WILKERSON", author_t=9.8, lines=[
        (0.0, 1.00, [("“NÃO HAVERÁ RENOVAÇÃO,", "w")]),
        (1.8, 1.00, [("DESPERTAR, AVIVAMENTO,", "w")]),
        (4.2, 1.00, [("ATÉ QUE ESTEJAMOS DISPOSTOS", "w")]),
        (5.6, 1.00, [("A DEIXAR QUE ELE MAIS UMA VEZ", "w")]),
        (7.6, 1.55, [("NOS QUEBRE.”", "g")]),
    ]),
    dict(t0=113.7, t1=125.7, author="A. W. TOZER", author_t=9.4, lines=[
        (0.0, 1.00, [("“O VERDADEIRO IDEAL CRISTÃO", "w")]),
        (2.6, 1.00, [("NÃO É SER FELIZ,", "w")]),
        (5.6, 1.00, [("MAS SER", "w")]),
        (7.97, 1.90, [("SANTO.”", "g")]),  # cai no ataque da música em 121,67 s
    ]),
]
END_LINES = [("NOSSO CULTO", "w", 1.0), ("SE INICIA AGORA!", "g", 1.45)]
COUNT_LABEL = "O CULTO COMEÇA EM"

# ataques fortes da música (s): viram pulsos de luz
ONSETS = [2.37, 9.43, 11.26, 30.49, 34.69, 73.21, 75.7, 81.18, 121.67, 126.01, 127.27]


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


# ------------------------------------------------------------------ música -> envelope de energia
def audio_env() -> np.ndarray:
    """Energia da música por quadro (0..1), suavizada. Dirige raios, partículas e brilho."""
    os.makedirs(CACHE, exist_ok=True)
    p = os.path.join(CACHE, "env.npy")
    if os.path.exists(p):
        return np.load(p)
    sr = 22050
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", SRC, "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.float32)
    win = int(0.25 * sr)
    env = np.zeros(NFRAMES, np.float32)
    for i in range(NFRAMES):
        c = int(i / FPS * sr)
        seg = x[max(0, c - win // 2): c + win // 2]
        db = 20 * math.log10(float(np.sqrt(np.mean(seg ** 2))) + 1e-9) if len(seg) else -90
        env[i] = clamp((db + 34) / 24)  # -34 dB -> 0 · -10 dB -> 1
    out = np.zeros_like(env)
    v = 0.0
    for i, e in enumerate(env):  # ataque rápido, soltura lenta
        v += (e - v) * (0.25 if e > v else 0.04)
        out[i] = v
    np.save(p, out)
    return out


ENV = audio_env()


def energy(t):
    return float(ENV[int(clamp(t * FPS, 0, NFRAMES - 1))])


def pulse(t):
    k = 0.0
    for t0 in ONSETS:
        if 0 <= t - t0 < 2.0:
            k = max(k, math.exp(-(t - t0) * 2.6))
    return k


# ------------------------------------------------------------------ fundo (pré-cálculo)
rng = np.random.default_rng(7)
HW, HH = W // 2, H // 2  # campos suaves em meia resolução


def _noise(w, h, octaves=4, base=6):
    out = np.zeros((h, w), np.float32)
    amp, tot = 1.0, 0.0
    for o in range(octaves):
        n = base * 2 ** o
        small = rng.random((max(2, n * h // w + 2), n + 2)).astype(np.float32)
        img = Image.fromarray(small, "F").resize((w, h), Image.BICUBIC)
        out += np.asarray(img) * amp
        tot += amp
        amp *= 0.5
    out /= tot
    return (out - out.min()) / (out.max() - out.min())


FOG_A = _noise(HW + 520, HH + 120)
FOG_B = _noise(HW + 520, HH + 120, base=4)


def _rays(seed):
    r = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:HH, 0:HW].astype(np.float32)
    cx, cy = HW / 2, -HH * 0.55  # fonte de luz acima do quadro
    ang = np.arctan2(xx - cx, yy - cy)
    dist = np.hypot(xx - cx, yy - cy)
    ctrl = r.random(90).astype(np.float32) ** 2.2
    a = (ang - ang.min()) / (ang.max() - ang.min()) * (len(ctrl) - 1)
    i0 = np.clip(a.astype(int), 0, len(ctrl) - 2)
    f = a - i0
    f = f * f * (3 - 2 * f)
    beam = ctrl[i0] * (1 - f) + ctrl[i0 + 1] * f
    fall = np.exp(-dist / (HH * 1.25)) * np.clip(1 - np.abs(ang) / 1.05, 0, 1) ** 1.5
    return gaussian_filter((beam * fall).astype(np.float32), 5)


RAY_1, RAY_2 = _rays(11), _rays(23)


def _base():
    yy = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
    top, bot = np.array([8, 18, 33], np.float32), np.array([2, 4, 9], np.float32)
    return np.broadcast_to(top + (bot - top) * yy ** 0.8, (H, W, 3)).copy()


BASE = _base()


def _vignette():
    yy = np.linspace(-1, 1, H, dtype=np.float32)[:, None]
    xx = np.linspace(-1, 1, W, dtype=np.float32)[None, :]
    return (1 - np.clip(xx ** 2 * 0.5 + yy ** 2 * 0.6 - 0.22, 0, 1) * 0.78)[..., None]


VIG = _vignette()


def _streak():
    """Risco de luz anamórfico horizontal (transições)."""
    yy = np.arange(H, dtype=np.float32)[:, None] - H * 0.47
    xx = np.arange(W, dtype=np.float32)[None, :] - W / 2
    core = np.exp(-(yy / 5) ** 2) * np.exp(-(xx / 620) ** 2)
    halo = np.exp(-(yy / 60) ** 2) * np.exp(-(xx / 780) ** 2) * 0.35
    return (core + halo).astype(np.float32)


STREAK = _streak()
GRAIN = [rng.normal(0, 2.4, (HH, HW, 1)).astype(np.float32) for _ in range(8)]

# partículas: poeira dourada subindo, com profundidade
NP = 300
P_X0 = rng.random(NP) * (W + 200) - 100
P_Y0 = rng.random(NP) * (H + 80)
P_Z = rng.random(NP) ** 1.6 * 0.8 + 0.2
P_VY = -(7 + 38 * P_Z)
P_AMP = 12 + 30 * rng.random(NP)
P_FRQ = 0.05 + 0.16 * rng.random(NP)
P_PH = rng.random(NP) * 6.283
P_TW = 0.25 + 0.9 * rng.random(NP)
P_GOLD = rng.random(NP) < 0.78
P_RAD = 1.3 + 5.2 * P_Z ** 2.2


@lru_cache(maxsize=None)
def _blob(rq):
    r = rq / 2  # raio em px (quantizado em 0,5)
    n = int(r * 3.2) + 2
    yy, xx = np.mgrid[-n:n + 1, -n:n + 1].astype(np.float32)
    return np.exp(-(xx ** 2 + yy ** 2) / (2 * (r / 1.5) ** 2)).astype(np.float32)


# bokeh: discos grandes desfocados, bem sutis
NB = 14
B_X0 = rng.random(NB) * HW
B_Y0 = rng.random(NB) * HH
B_R = 16 + 34 * rng.random(NB)
B_A = 0.03 + 0.05 * rng.random(NB)
B_VX = (rng.random(NB) - 0.5) * 5
B_VY = -(1 + 3 * rng.random(NB))


@lru_cache(maxsize=None)
def _disc(r):
    n = r + 3
    yy, xx = np.mgrid[-n:n + 1, -n:n + 1].astype(np.float32)
    d = np.hypot(xx, yy)
    return (np.clip(r - d, 0, 1) * (0.75 + 0.25 * np.clip(d / r, 0, 1) ** 4)).astype(np.float32)


def _stamp(buf, spr, x, y, a):
    """Soma o sprite em buf com posição sub-pixel (bilinear)."""
    h, w = buf.shape
    n = spr.shape[0] // 2
    x0, y0 = int(math.floor(x)), int(math.floor(y))
    fx, fy = x - x0, y - y0
    for dx, dy, wt in ((0, 0, (1 - fx) * (1 - fy)), (1, 0, fx * (1 - fy)), (0, 1, (1 - fx) * fy), (1, 1, fx * fy)):
        if wt < 0.02:
            continue
        xs, ys = x0 + dx - n, y0 + dy - n
        sx0, sy0 = max(0, -xs), max(0, -ys)
        sx1, sy1 = min(spr.shape[1], w - xs), min(spr.shape[0], h - ys)
        if sx1 <= sx0 or sy1 <= sy0:
            continue
        buf[ys + sy0: ys + sy1, xs + sx0: xs + sx1] += spr[sy0:sy1, sx0:sx1] * (a * wt)


def _up(field):
    return np.asarray(Image.fromarray(field, "F").resize((W, H), Image.BILINEAR))


def background(t: float) -> np.ndarray:
    en, pu = energy(t), pulse(t)
    # névoa: duas camadas de ruído deslizando em sentidos opostos
    def layer(tex, speed, oy):
        x = 260 + speed * t
        x0 = int(math.floor(x))
        f = x - x0
        a = tex[oy: oy + HH, x0: x0 + HW]
        b = tex[oy: oy + HH, x0 + 1: x0 + 1 + HW]
        return a + (b - a) * f
    fog = layer(FOG_A, 1.7, 40) * 0.6 + layer(FOG_B, -1.2, 70) * 0.4
    fog = np.clip(fog - 0.28, 0, 1) ** 1.4 * (0.75 + 0.5 * en)
    rays = RAY_1 * (0.55 + 0.45 * math.sin(t * 0.23)) + RAY_2 * (0.55 + 0.45 * math.cos(t * 0.17 + 1.0))
    rays = rays * (0.16 + 0.55 * en + 0.5 * pu)

    # bokeh (meia resolução)
    bk = np.zeros((HH, HW), np.float32)
    for i in range(NB):
        x = (B_X0[i] + B_VX[i] * t) % (HW + 160) - 80
        y = (B_Y0[i] + B_VY[i] * t) % (HH + 160) - 80
        _stamp(bk, _disc(int(B_R[i])), x, y, B_A[i] * (0.7 + 0.6 * en))

    # combina os campos suaves em meia resolução e amplia uma vez por canal
    warm = rays * 1.0 + bk * 0.99
    arr = BASE.copy()
    for c, (kf, kw) in enumerate(((22, 255), (88, 207), (112, 138))):
        arr[..., c] += _up(fog * kf + warm * kw)

    # partículas (resolução cheia)
    gold = np.zeros((H, W), np.float32)
    cool = np.zeros((H, W), np.float32)
    boost = 0.55 + 0.75 * en + 0.6 * pu
    for i in range(NP):
        y = (P_Y0[i] + P_VY[i] * t) % (H + 80) - 40
        x = P_X0[i] + P_AMP[i] * math.sin(6.283 * P_FRQ[i] * t + P_PH[i])
        tw = 0.55 + 0.45 * math.sin(6.283 * P_TW[i] * t + P_PH[i] * 3)
        a = (0.35 + 0.65 * P_Z[i]) * tw * boost
        _stamp(gold if P_GOLD[i] else cool, _blob(int(round(P_RAD[i] * 2))), x, y, a)
    arr += gold[..., None] * np.array([255, 196, 104], np.float32)
    arr += cool[..., None] * np.array([170, 226, 255], np.float32)
    return arr


# ------------------------------------------------------------------ tipografia
@lru_cache(maxsize=None)
def font(path, size):
    return ImageFont.truetype(path, size)


def text_w(text, path, size, tracking=0):
    f = font(path, size)
    l, _, r, _ = f.getbbox(text, anchor="ls")
    return r - l + tracking * (len(text) - 1)


def cap_h(path, size):
    return -font(path, size).getbbox("H", anchor="ls")[1]


@lru_cache(maxsize=None)
def word_sprite(text, size, style, path=F_ANTON, tracking=0):
    """Palavra com brilho suave. Devolve (img RGBA, ox, oy) relativos a (x0, baseline)."""
    f = font(path, size)
    pad = 46
    l, t, r, b = f.getbbox(text, anchor="ls")
    if tracking:
        r += tracking * (len(text) - 1)
    w, h = int(r - l) + 2 * pad, int(b - t) + 2 * pad
    mask = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(mask)
    if tracking:
        x = pad - l
        for c in text:
            d.text((x, pad - t), c, font=f, fill=255, anchor="ls")
            x += f.getlength(c) + tracking
    else:
        d.text((pad - l, pad - t), text, font=f, fill=255, anchor="ls")
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    # sombra escura (legibilidade sobre partículas) + halo na cor do texto
    sh = mask.filter(ImageFilter.GaussianBlur(14)).point(lambda a: int(a * 0.8))
    out.paste(Image.new("RGBA", (w, h), (0, 3, 8, 255)), (0, 6), sh)
    glow_c = GOLD if style == "g" else (200, 225, 255)
    gl = mask.filter(ImageFilter.GaussianBlur(18)).point(lambda a: int(a * (0.5 if style == "g" else 0.16)))
    out.alpha_composite(Image.merge("RGBA", [Image.new("L", (w, h), c) for c in glow_c] + [gl]))
    # preenchimento: gradiente vertical (dourado metálico ou branco quente)
    top, bot = (GOLD_TOP, GOLD_BOT) if style == "g" else (WHITE, (214, 216, 220))
    y0, y1 = pad, h - pad
    ramp = np.clip((np.arange(h, dtype=np.float32) - y0) / max(1, y1 - y0), 0, 1)[:, None, None]
    fill = (np.array(top, np.float32) + (np.array(bot, np.float32) - np.array(top, np.float32)) * ramp)
    fill = np.broadcast_to(fill, (h, w, 3)).astype(np.uint8)
    out.paste(Image.fromarray(fill, "RGB"), (0, 0), mask)
    return out, l - pad, t - pad


def paste(frame, img, x, y):
    x, y = int(round(x)), int(round(y))
    sx, sy = max(0, -x), max(0, -y)
    ex, ey = min(img.width, frame.width - x), min(img.height, frame.height - y)
    if ex <= sx or ey <= sy:
        return
    if sx or sy or ex < img.width or ey < img.height:
        img = img.crop((sx, sy, ex, ey))
    frame.alpha_composite(img, (x + sx, y + sy))


def put(frame, sp, x0, base, a=1.0, s=1.0, cam=None):
    """Desenha o sprite com origem do texto em x0 e baseline em `base` (escala em torno do centro).
    cam=(z, px, py): aproximação de câmera z em torno do ponto (px, py)."""
    img, ox, oy = sp
    if a <= 0.004:
        return
    cx, cy = x0 + ox + img.width / 2, base + oy + img.height / 2
    if cam:
        z, px, py = cam
        cx, cy, s = px + (cx - px) * z, py + (cy - py) * z, s * z
    if abs(s - 1) > 1e-3:
        img = img.resize((max(1, round(img.width * s)), max(1, round(img.height * s))), Image.BICUBIC)
    if a < 0.996:
        img = img.copy()
        img.putalpha(img.getchannel("A").point(lambda v: int(v * a)))
    paste(frame, img, cx - img.width / 2, cy - img.height / 2)


# ------------------------------------------------------------------ layout das frases
LEAD = 1.2      # entrelinha (x tamanho): acentos e cedilhas não se tocam
MAXW, MAXH = 1640, 600
CY = 478        # centro vertical do bloco de texto
WORD_GAP = 0.11  # s entre palavras


@lru_cache(maxsize=None)
def layout(qi):
    q = QUOTES[qi]
    base = 150
    while base > 40:
        sizes = [int(base * sc) for _, sc, _ in q["lines"]]
        widths = []
        for (_, _, segs), s in zip(q["lines"], sizes):
            words = [w for txt, _ in segs for w in txt.split(" ")]
            sp = font(F_ANTON, s).getlength(" ") * 0.95
            widths.append(sum(text_w(w, F_ANTON, s) for w in words) + sp * (len(words) - 1))
        height = cap_h(F_ANTON, sizes[0]) + sum(s * LEAD for s in sizes[1:])
        if max(widths) <= MAXW and height <= MAXH:
            break
        base -= 2
    items = []  # (texto, tamanho, estilo, x, baseline, t_aparece)
    y = CY - height / 2 + cap_h(F_ANTON, sizes[0])
    for li, ((off, _, segs), s, wd) in enumerate(zip(q["lines"], sizes, widths)):
        if li:
            y += s * LEAD
        x = (W - wd) / 2
        sp = font(F_ANTON, s).getlength(" ") * 0.95
        k = 0
        for txt, st in segs:
            for w in txt.split(" "):
                l = font(F_ANTON, s).getbbox(w, anchor="ls")[0]
                items.append((w, s, st, x - l, y, q["t0"] + off + k * WORD_GAP))
                x += text_w(w, F_ANTON, s) + sp
                k += 1
    return items, y  # y = baseline da última linha


def draw_quote(frame, qi, t):
    q = QUOTES[qi]
    items, last_base = layout(qi)
    # leve aproximação de câmera no texto ao longo da frase
    cam = (lerp(1.0, 1.035, prog(t, q["t0"], q["t1"] - q["t0"])), W / 2, CY + 40)
    t_out = q["t1"] - 0.55
    out = e_in_cubic(prog(t, t_out, 0.55))
    for (w, s, st, x, base, tw) in items:
        if t < tw:
            continue
        p = e_out_cubic(prog(t, tw, 0.55))
        a = p * (1 - out)
        dy = (1 - p) * 30 - out * 22
        sc = 1.0
        if st == "g":  # palavras-chave: entram maiores e assentam
            sc = lerp(1.14, 1.0, e_out_expo(prog(t, tw, 0.5)))
        put(frame, word_sprite(w, s, st), x, base + dy, a, sc, cam)
    # autor: fio dourado + nome
    ta = q["t0"] + q["author_t"]
    if t >= ta:
        p = e_out_cubic(prog(t, ta, 0.7))
        a = p * (1 - out)
        ya = last_base + 92
        lw = 46 * p
        d = ImageDraw.Draw(frame)
        yl = cam[2] + (ya - 44 - cam[2]) * cam[0]
        d.line((W / 2 - lw, yl, W / 2 + lw, yl), fill=GOLD + (int(255 * a),), width=3)
        sp = word_sprite(q["author"], 40, "w", F_LABEL, 9)
        put(frame, sp, W / 2 - text_w(q["author"], F_LABEL, 40, 9) / 2, ya + 6 + (1 - p) * 12, a * 0.92, 1.0, cam)


def draw_end(frame, t):
    if t < T_END:
        return
    base = 150
    sizes = [int(base * sc) for _, _, sc in END_LINES]
    height = cap_h(F_ANTON, sizes[0]) + sizes[1] * LEAD
    y = H / 2 - height / 2 + cap_h(F_ANTON, sizes[0]) - 10
    for i, ((txt, st, _), s) in enumerate(zip(END_LINES, sizes)):
        if i:
            y += s * LEAD
        t0 = T_END + i * 0.28
        if t < t0:
            continue
        p = e_out_expo(prog(t, t0, 0.5))
        l = font(F_ANTON, s).getbbox(txt, anchor="ls")[0]
        put(frame, word_sprite(txt, s, st), (W - text_w(txt, F_ANTON, s)) / 2 - l, y, e_out_cubic(prog(t, t0, 0.12)),
            lerp(1.22, 1.0, p))


def draw_countdown(frame, t):
    if not COUNTDOWN or t >= T_END:
        return
    a = e_out_cubic(prog(t, 0.8, 0.8)) * (1 - e_in_cubic(prog(t, T_END - 0.5, 0.5)))
    if a <= 0:
        return
    left = max(0, int(math.ceil(T_END - t)))
    digits = f"{left // 60:02d}:{left % 60:02d}"
    size, tr = 30, 7
    y = 1004
    f = font(F_LABEL, size)
    slot = max(f.getlength(c) for c in "0123456789") + 5
    dw = slot * 4 + f.getlength(":") + 10
    lab_w = text_w(COUNT_LABEL, F_LABEL, size, tr)
    x = (W - (lab_w + 26 + dw)) / 2
    put(frame, word_sprite(COUNT_LABEL, size, "w", F_LABEL, tr), x, y, a * 0.62)
    x += lab_w + 26
    for c in digits:
        cw = f.getlength(":") + 10 if c == ":" else slot
        put(frame, word_sprite(c, size, "g", F_LABEL), x + (cw - f.getlength(c)) / 2, y, a * 0.95)
        x += cw
    # barra de progresso
    d = ImageDraw.Draw(frame)
    bw = 520
    x0, yb = (W - bw) / 2, y + 26
    d.rectangle((x0, yb, x0 + bw, yb + 2), fill=(255, 255, 255, int(40 * a)))
    d.rectangle((x0, yb, x0 + bw * clamp(t / T_END), yb + 2), fill=GOLD + (int(230 * a),))


# ------------------------------------------------------------------ quadro
BOUNDS = [q["t1"] + 0.2 for q in QUOTES[:-1]]  # troca de frase: risco de luz


def compose(t: float) -> Image.Image:
    arr = background(t)

    # risco de luz nas trocas de frase e clarão na cartela final
    for tb in BOUNDS:
        if abs(t - tb) < 0.6:
            k = math.cos((t - tb) / 0.6 * math.pi / 2) ** 2
            arr += STREAK[..., None] * np.array([255, 214, 160], np.float32) * (0.85 * k)
    if T_END <= t < T_END + 1.4:
        k = math.exp(-(t - T_END) * 3.2)
        arr += STREAK[..., None] * np.array([255, 220, 170], np.float32) * (1.6 * k)
        arr += 150 * k * (t - T_END < 0.5) * (1 - (t - T_END) / 0.5) ** 2

    arr *= VIG
    frame = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).convert("RGBA")

    for qi, q in enumerate(QUOTES):
        if q["t0"] <= t < q["t1"] + 0.05:
            draw_quote(frame, qi, t)
    draw_end(frame, t)
    draw_countdown(frame, t)

    out = np.asarray(frame.convert("RGB")).astype(np.float32)
    # halação: o que é claro (texto, partículas) ganha um brilho suave
    small = Image.fromarray(out.astype(np.uint8)).resize((W // 8, H // 8), Image.BILINEAR)
    small = small.filter(ImageFilter.GaussianBlur(7)).resize((W, H), Image.BILINEAR)
    bl = np.clip(np.asarray(small).astype(np.float32) - 120, 0, None) * np.array([1.0, 0.86, 0.66], np.float32)
    out += bl * 0.42
    g = GRAIN[int(t * FPS) % len(GRAIN)]
    out += np.repeat(np.repeat(g, 2, axis=0), 2, axis=1)
    # entrada e saída em preto
    fade = e_out_cubic(prog(t, 0.0, 1.2)) * (1 - e_in_cubic(prog(t, 129.2, 1.4)))
    if fade < 0.999:
        out *= fade
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))


# ------------------------------------------------------------------ main
def _frame(i):
    return compose(i / FPS).tobytes()


def main():
    args = sys.argv[1:]
    if args and args[0] == "--preview":
        os.makedirs(os.path.join(HERE, "preview"), exist_ok=True)
        for ts in args[1:]:
            p = os.path.join(HERE, "preview", f"t{float(ts):06.2f}.png")
            compose(float(ts)).save(p)
            print(p)
        return

    os.makedirs(CACHE, exist_ok=True)
    master = os.path.join(CACHE, "master.mp4")  # intermediário de alta qualidade (permite recodificar sem re-renderizar)
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


def encode(master, crf="23", maxrate="2800k"):
    """Vídeo final: H.264 (cerca de 36 MB) + o áudio ORIGINAL copiado sem recompressão."""
    subprocess.run([
        "ffmpeg", "-v", "error", "-y", "-i", master, "-i", SRC, "-map", "0:v", "-map", "1:a",
        "-c:v", "libx264", "-preset", "slow", "-crf", crf, "-maxrate", maxrate, "-bufsize", "8M",
        "-x264-params", "aq-mode=3", "-pix_fmt", "yuv420p", "-profile:v", "high", "-level", "4.2",
        "-c:a", "copy", "-movflags", "+faststart", OUT,
    ], check=True)


if __name__ == "__main__":
    main()
