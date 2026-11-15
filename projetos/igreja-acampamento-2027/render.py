#!/usr/bin/env python3
"""Reels 9:16 · "Acampamento 2027 · Inscrições abertas" (v2, público de 15 a 30 anos).

Edição com cara de cinema: faixa widescreen sobre preto, tipografia condensada (Anton)
com acentos em serifa itálica (Instrument Serif), cortes no tempo da música (120 BPM),
abertura da faixa para tela cheia no momento da adoração, granulação de filme, light leak e flashes.

Material: assets/gincana.mp4 · assets/adoracao.mp4 · assets/chacara.jpg
Trilha: trilha.py (original, sintetizada; sem direitos de terceiros)

Uso:
    python3 render.py                       # Reels 9:16: vídeos finais + capa
    python3 render.py --preview 1.5 3 7 13  # só quadros PNG em preview/
    python3 render.py --telao               # versão horizontal 16:9 (1920x1080) para telão
    python3 render.py --telao --preview 3 9 # quadros da versão telão
"""
from __future__ import annotations

import math
import os
import subprocess
import sys
from functools import lru_cache
from multiprocessing import Pool

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

import trilha

HERE = os.path.dirname(os.path.abspath(__file__))
A = lambda *p: os.path.join(HERE, "assets", *p)  # noqa: E731
CACHE = os.path.join(HERE, ".cache")
TELAO = "--telao" in sys.argv  # versão horizontal 16:9 para projeção
_NOME = "telao" if TELAO else "reels"
OUT_MAIN = os.path.join(HERE, f"acampamento-2027-{_NOME}.mp4")
OUT_NOMUSIC = os.path.join(HERE, f"acampamento-2027-{_NOME}-sem-musica.mp4")
OUT_COVER = os.path.join(HERE, "capa.jpg")

W, H = (1920, 1080) if TELAO else (1080, 1920)
FPS, DUR = 30, 20.0
NFRAMES = int(DUR * FPS)
# telão: janela "scope" 2,39:1 com barras de cinema, que abrem para 16:9 cheio na adoração
LB_H = 804
LB_B = (H + LB_H) // 2  # base da janela
BASE_T = 968            # baseline dos títulos do telão (a cedilha ainda cabe na tela)
MX = 96                 # margem lateral segura para projeção
BAND_H, BAND_Y = 540, 960  # faixa 2:1, centro vertical
BT, BB = BAND_Y - BAND_H // 2, BAND_Y + BAND_H // 2  # topo / base da faixa

F_ANTON = A("fonts", "Anton-Regular.ttf")
F_SERIF = A("fonts", "InstrumentSerif-Italic.ttf")
F_LABEL = "/usr/share/fonts/opentype/inter/InterDisplay-SemiBold.otf"
F_SMALL = "/usr/share/fonts/opentype/inter/InterDisplay-Medium.otf"

INK = (11, 10, 9)
WHITE = (246, 243, 236)
ORANGE = (255, 96, 28)  # "fogueira"

# ------------------------------------------------------------------ TEXTOS
T = {
    "hud_l": "ACAMPAMENTO 2027",
    "hud_r": "INSCRIÇÕES ABERTAS",
    "kicker": "avisa a galera:",
    "open1": "O ACAMPA",
    "open2": "VOLTOU",
    "tem": "tem",
    "gincana": "GINCANA",
    "alegria": "ALEGRIA",
    "adoracao": "ADORAÇÃO",
    "e_tem": "e o principal:",
    "deus": "DEUS",
    "no_meio": "NO MEIO",
    "build": ["SÓ", "FALTA", "VOCÊ", "VOCÊ"],
    "insc": "INSCRIÇÕES",
    "abertas": "ABERTAS",
    "label": "ACAMPAMENTO 2027",
    "garanta": "GARANTE",
    "sua_vaga": "SUA VAGA",
    "cta_sub": "Inscrições com a liderança da igreja",
    "cta_tag": "e marca quem vai com você",
    "cta_tag_telao": "e chama quem vai com você",  # no telão não existe "marcar nos comentários"
}


# ------------------------------------------------------------------ util
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def lerp(a, b, t):
    return a + (b - a) * t


def prog(t, t0, d):
    return clamp((t - t0) / d)


def e_out_expo(x):
    x = clamp(x)
    return 1 if x >= 1 else 1 - 2 ** (-10 * x)


def e_io_cubic(x):
    x = clamp(x)
    return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2


def e_out_cubic(x):
    return 1 - (1 - clamp(x)) ** 3


# ------------------------------------------------------------------ cor (grade de filme)
def _lut(lift, gamma, gain, contrast):
    x = np.linspace(0, 1, 256)
    y = 0.5 + (x - 0.5) * contrast
    y = np.clip(y, 0, 1)
    y = 1 - (1 - y) ** 1.06  # rolloff suave nas altas
    y = lift + (gain - lift) * y ** gamma
    return (np.clip(y, 0, 1) * 255).astype(np.uint8)


GRADES = {
    # (R, G, B) luts + saturação
    "gincana": ([_lut(0.035, 0.98, 1.0, 1.16), _lut(0.03, 1.0, 0.985, 1.14), _lut(0.045, 1.04, 0.95, 1.12)], 1.08),
    "adoracao": ([_lut(0.03, 0.97, 1.0, 1.10), _lut(0.03, 1.0, 0.975, 1.08), _lut(0.05, 1.05, 0.94, 1.08)], 0.92),
    "chacara": ([_lut(0.03, 0.97, 1.0, 1.12), _lut(0.03, 1.0, 0.98, 1.1), _lut(0.05, 1.04, 0.94, 1.08)], 1.0),
}


def grade(arr: np.ndarray, kind: str) -> np.ndarray:
    luts, sat = GRADES[kind]
    out = np.stack([luts[c][arr[..., c]] for c in range(3)], -1).astype(np.float32)
    if sat != 1:
        y = (out @ np.array([0.299, 0.587, 0.114], np.float32))[..., None]
        out = y + (out - y) * sat
    return np.clip(out, 0, 255).astype(np.uint8)


# ------------------------------------------------------------------ fontes de imagem
RESTORE = {  # remove a compressão do WhatsApp, amplia com Lanczos e devolve nitidez (CAS)
    "gincana": "fps=60,hqdn3d=1.5:1.5:3:3,nlmeans=s=3.5:p=7:r=13,scale=iw*2:ih*2:flags=lanczos,cas=strength=0.6",
    "adoracao": "fps=24,nlmeans=s=2.2:p=7:r=11,scale=1080:1920:flags=lanczos,cas=strength=0.5",
}


def extract_frames():
    for name, vf in RESTORE.items():
        d = os.path.join(CACHE, name + "_hd")
        if os.path.isdir(d) and len(os.listdir(d)) > 50:
            continue
        os.makedirs(d, exist_ok=True)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", A(f"{name}.mp4"), "-vf", vf,
                        "-q:v", "1", os.path.join(d, "%04d.jpg")], check=True)
    ph = os.path.join(CACHE, "chacara_hd.png")
    if not os.path.exists(ph):
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", A("chacara.jpg"), "-vf",
                        "nlmeans=s=3:p=7:r=13,scale=iw*2:ih*2:flags=lanczos,cas=strength=0.55", ph], check=True)


SRC_FPS = {"gincana": 60, "adoracao": 24}


@lru_cache(maxsize=64)
def frame_arr(name, idx):
    d = os.path.join(CACHE, name + "_hd")
    n = len(os.listdir(d))
    idx = int(clamp(idx, 0, n - 1))
    return grade(np.asarray(Image.open(os.path.join(d, f"{idx + 1:04d}.jpg")).convert("RGB")), name)


@lru_cache(maxsize=1)
def photo_arr():
    return grade(np.asarray(Image.open(os.path.join(CACHE, "chacara_hd.png")).convert("RGB")), "chacara")


def src_image(name, ts, blend=False):
    if name == "chacara":
        return Image.fromarray(photo_arr())
    f = ts * SRC_FPS[name]
    i0 = int(math.floor(f))
    if blend and f - i0 > 0.05:
        a, b = frame_arr(name, i0).astype(np.float32), frame_arr(name, i0 + 1).astype(np.float32)
        return Image.fromarray((a + (b - a) * (f - i0)).astype(np.uint8))
    return Image.fromarray(frame_arr(name, int(round(f))))


def view(img: Image.Image, ow, oh, z=1.0, fx=0.5, fy=0.5, sharpen=True):
    """Recorta a janela (proporção ow:oh) com zoom z centrada em (fx, fy) e escala para ow x oh."""
    sw, sh = img.size
    ar = ow / oh
    if sw / sh > ar:
        bw, bh = sh * ar, sh
    else:
        bw, bh = sw, sw / ar
    vw, vh = bw / z, bh / z
    cx = clamp(fx * sw, vw / 2, sw - vw / 2)
    cy = clamp(fy * sh, vh / 2, sh - vh / 2)
    s = vw / ow
    out = img.transform((ow, oh), Image.AFFINE, (s, 0, cx - vw / 2, 0, s, cy - vh / 2), resample=Image.BICUBIC)
    if sharpen:
        out = out.filter(ImageFilter.UnsharpMask(radius=1.4, percent=28, threshold=3))
    return out


# ------------------------------------------------------------------ tipografia
@lru_cache(maxsize=None)
def font(path, size):
    return ImageFont.truetype(path, size)


def glyph_sprite(text, path, size, color, shadow=0.0, tracking=0):
    """Sprite justo à tinta. Devolve (img, ox, oy): deslocamento do ponto (x0, baseline) até o canto do sprite."""
    f = font(path, size)
    pad = 60 if shadow else 8
    l, t, r, b = f.getbbox(text, anchor="ls")
    if tracking:
        r += tracking * (len(text) - 1)
    w, h = int(r - l) + 2 * pad, int(b - t) + 2 * pad
    mask = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(mask)
    x = pad - l
    if tracking:
        for c in text:
            d.text((x, pad - t), c, font=f, fill=255, anchor="ls")
            x += f.getlength(c) + tracking
    else:
        d.text((x, pad - t), text, font=f, fill=255, anchor="ls")
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    if shadow:
        sh = mask.filter(ImageFilter.GaussianBlur(22)).point(lambda a: int(a * shadow))
        out.paste(Image.new("RGBA", (w, h), (0, 0, 0, 255)), (0, 10), sh)
    out.paste(Image.new("RGBA", (w, h), color + (255,)), (0, 0), mask)
    return out, l - pad, t - pad  # canto sup-esq relativo a (x0, baseline)


def text_w(text, path, size, tracking=0):
    f = font(path, size)
    l, _, r, _ = f.getbbox(text, anchor="ls")
    return r - l + tracking * (len(text) - 1)


def fit(text, path, maxw, maxs, tracking=0):
    s = maxs
    while s > 10 and text_w(text, path, s, tracking) > maxw:
        s -= 2
    return s


def cap_h(path, size):
    l, t, r, b = font(path, size).getbbox("H", anchor="ls")
    return -t


@lru_cache(maxsize=None)
def spr(text, path, size, color, shadow=0.0, tracking=0):
    return glyph_sprite(text, path, size, color, shadow, tracking)


def put(frame: Image.Image, sp, x0, base, s=1.0, a=1.0, center=True):
    """Desenha o sprite com baseline em `base`. Se center, x0 é o centro horizontal da palavra."""
    img, ox, oy = sp
    if a <= 0.004:
        return
    iw, ih = img.size
    # sprite justo à tinta: centro do sprite = centro da palavra
    cx = x0 if center else x0 + ox + iw / 2
    cy = base + oy + ih / 2
    if abs(s - 1) > 1e-3:
        img = img.resize((max(1, round(iw * s)), max(1, round(ih * s))), Image.BICUBIC)
        # escala em torno do centro da palavra no baseline (fica mais natural)
        cy = base + (oy + ih / 2) * s
    if a < 0.996:
        img = img.copy()
        img.putalpha(img.getchannel("A").point(lambda v: int(v * a)))
    paste(frame, img, cx - img.width / 2, cy - img.height / 2)


def paste(frame, img, x, y):
    x, y = int(round(x)), int(round(y))
    sx, sy = max(0, -x), max(0, -y)
    ex, ey = min(img.width, frame.width - x), min(img.height, frame.height - y)
    if ex <= sx or ey <= sy:
        return
    if sx or sy or ex < img.width or ey < img.height:
        img = img.crop((sx, sy, ex, ey))
    frame.alpha_composite(img, (x + sx, y + sy))


def slam(frame, sp, cx, base, t, t0, big=1.16):
    """Entrada de impacto no tempo: escala grande -> 1 em ~0,2 s."""
    if t < t0:
        return
    p = prog(t, t0, 0.22)
    put(frame, sp, cx, base, lerp(big, 1.0, e_out_expo(p)), e_out_cubic(prog(t, t0, 0.05)))


def reveal(frame, text, path, size, color, cx, base, t, t0, stagger=0.035, shadow=0.0):
    """Letras sobem de trás de uma máscara (revelação por letra)."""
    if t < t0:
        return
    f = font(path, size)
    asc, desc = f.getmetrics()
    total = text_w(text, path, size)
    l0 = f.getbbox(text, anchor="ls")[0]
    pad = 60 if shadow else 0
    box_h = asc + desc + 2 * pad
    canvas = Image.new("RGBA", (int(total) + 2 * pad + 40, box_h), (0, 0, 0, 0))
    for i, c in enumerate(text):
        p = e_out_expo(prog(t, t0 + i * stagger, 0.5))
        if p <= 0:
            continue
        x = pad + 20 + f.getlength(text[:i]) - l0
        img, ox, oy = spr(c, path, size, color, shadow)
        dy = (1 - p) * (asc + desc)
        paste(canvas, img, x + ox, pad + asc + oy + dy)
    paste(frame, canvas, cx - canvas.width / 2, base - asc - pad)


# ------------------------------------------------------------------ overlays pré-calculados
rng = np.random.default_rng(27)
GRAIN = [rng.normal(0, 3.8, (H // 2, W // 2, 1)).astype(np.float32) for _ in range(8)]


def _vignette():
    yy = np.linspace(-1, 1, H)[:, None]
    xx = np.linspace(-1, 1, W)[None, :]
    v = 1 - np.clip((xx ** 2 * 0.55 + yy ** 2 * 0.45) - 0.25, 0, 1) * 0.55
    return v[..., None].astype(np.float32)


VIG = _vignette()


def _top_shade():
    yy = np.linspace(0, 1, H)[:, None]
    if TELAO:  # títulos ficam embaixo: escurece mais a base
        a = np.clip((yy - 0.46) / 0.54, 0, 1) ** 1.3 * 0.76 + np.clip(1 - yy / 0.2, 0, 1) ** 1.5 * 0.4
        return (1 - a)[..., None].astype(np.float32)
    a = np.clip(1 - yy / 0.5, 0, 1) ** 1.3 * 0.62 + np.clip((yy - 0.72) / 0.28, 0, 1) ** 1.5 * 0.5
    return (1 - a)[..., None].astype(np.float32)


TOP_SHADE = _top_shade()


def _leak():
    """Light leak quente (gradientes desfocados), aplicado em 'screen'."""
    qw, qh = W // 4, H // 4
    img = Image.new("RGB", (qw, qh), (0, 0, 0))
    d = ImageDraw.Draw(img)
    m = min(qw, qh)
    for (a, b, rr, c) in [(0.148, 0.125, 0.63, (255, 90, 20)), (0.852, 0.25, 0.444, (255, 170, 60)),
                          (0.333, 0.6875, 0.556, (255, 60, 30)), (0.963, 0.875, 0.407, (255, 140, 40))]:
        # (a, b) = fração no eixo curto / longo: no telão os eixos trocam
        x, y, r = (b * qw, a * qh, rr * m) if TELAO else (a * qw, b * qh, rr * m)
        d.ellipse((x - r, y - r, x + r, y + r), fill=c)
    img = img.filter(ImageFilter.GaussianBlur(55)).resize((W, H), Image.BICUBIC)
    return np.asarray(img).astype(np.float32) / 255


LEAK = _leak()
LEAKS = [(5.9, 0.9), (11.95, 1.0)]  # (início, duração)
FLASHES = [(0.0, 0.8), (1.0, 0.9), (2.0, 0.35), (4.0, 0.3), (8.0, 0.3), (12.0, 1.0), (15.0, 0.35), (19.0, 0.45)]
HITS = [(1.0, 1.0), (11.5, 0.8), (12.0, 1.3), (19.0, 0.7)]  # tremor + aberração cromática


def hit_k(t):
    k = 0.0
    for t0, s in HITS:
        if 0 <= t - t0 < 0.4:
            k = max(k, s * math.exp(-(t - t0) * 11))
    return k


# ------------------------------------------------------------------ cenas
def band(frame, img, h=BAND_H, cy=BAND_Y):
    """Cola a imagem de faixa (1080 x BAND_H) com centro em cy e altura visível h (abre do centro)."""
    h = int(round(h))
    if h <= 0:
        return
    top = (img.height - h) // 2
    frame.paste(img.crop((0, top, W, top + h)), (0, int(cy) - h // 2))


def shot_gincana(ts, z=1.0, fx=0.5, fy=0.52):
    return view(src_image("gincana", ts), W, BAND_H, z, fx, fy)


def shot_adoracao_full(ts, z=1.0, fy=0.5, blend=True, shade=1.0):
    img = view(src_image("adoracao", ts, blend), W, H, z, 0.5, fy)
    if shade > 0:  # escurece topo/base p/ legibilidade do texto
        a = np.asarray(img).astype(np.float32) * (1 + (TOP_SHADE - 1) * shade)
        img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    return img


def punch(t, t0, amt=0.12, d=0.3):
    """Zoom de impacto no corte."""
    return 1 + amt * (1 - e_out_expo(prog(t, t0, d)))


def headline_above(frame, t, t0, small, big, size=250, shadow=0.0, bt=BT):
    """'tem' (serifa laranja) + PALAVRA (Anton) com a base 34 px dentro da faixa."""
    s = fit(big, F_ANTON, 1000, size)
    base = bt + 34
    reveal(frame, big, F_ANTON, s, WHITE, W / 2, base, t, t0, shadow=shadow)
    if small:
        bw = text_w(big, F_ANTON, s)
        sp = spr(small, F_SERIF, 118, ORANGE, 0.6)
        p = e_out_cubic(prog(t, t0 + 0.12, 0.3))
        put(frame, sp, W / 2 - bw / 2 + 4, base - cap_h(F_ANTON, s) - 14 + (1 - p) * 20, 1, p, center=False)


def headline_below(frame, t, t0, small, big, size=250, color=WHITE, bb=BB):
    s = fit(big, F_ANTON, 1000, size)
    base = bb - 34 + cap_h(F_ANTON, s)
    reveal(frame, big, F_ANTON, s, color, W / 2, base, t, t0)
    if small:
        bw = text_w(big, F_ANTON, s)
        sp = spr(small, F_SERIF, 118, ORANGE, 0.6)
        p = e_out_cubic(prog(t, t0 + 0.12, 0.3))
        put(frame, sp, W / 2 - bw / 2 + 4, base - cap_h(F_ANTON, s) - 14 + (1 - p) * 20, 1, p, center=False)


def hud(frame, t):
    a = e_out_cubic(prog(t, 0.45, 0.4))
    if a <= 0:
        return
    y, fs, tr, mx, rad = (88, 34, 5, MX, 10) if TELAO else (236, 27, 4, 64, 8)
    l = spr(T["hud_l"], F_LABEL, fs, WHITE, 0.0, tr)
    r = spr(T["hud_r"], F_LABEL, fs, WHITE, 0.0, tr)
    put(frame, l, mx, y, 1, a * 0.9, center=False)
    rw = text_w(T["hud_r"], F_LABEL, fs, tr)
    put(frame, r, W - mx - rw, y, 1, a * 0.9, center=False)
    # ponto "REC" piscando
    if (t % 1.0) < 0.62:
        d = ImageDraw.Draw(frame)
        cx, cy = W - mx - rw - 3 * rad, y - round(fs * 0.4)
        d.ellipse((cx - rad, cy - rad, cx + rad, cy + rad), fill=ORANGE + (int(255 * a),))


def compose(t: float) -> Image.Image:
    frame = Image.new("RGBA", (W, H), INK + (255,))

    # ---------------- 0–2 s · gancho: avisa a galera: O ACAMPA / VOLTOU (vazado com a adoração)
    if t < 2.0:
        s1 = fit(T["open1"], F_ANTON, 1000, 330)
        s2 = fit(T["open2"], F_ANTON, 1010, 700)
        c1, c2 = cap_h(F_ANTON, s1), cap_h(F_ANTON, s2)
        base1 = 960 - (c1 + 40 + c2) / 2 + c1 + 50
        slam(frame, spr(T["open1"], F_ANTON, s1, WHITE), W / 2, base1, t, 0.0, 1.22)
        w1 = text_w(T["open1"], F_ANTON, s1)
        pk = e_out_cubic(prog(t, 0.14, 0.3))
        put(frame, spr(T["kicker"], F_SERIF, 112, ORANGE), W / 2 - w1 / 2 + 4,
            base1 - c1 - 18 + (1 - pk) * 20, 1, pk, center=False)
        if t >= 1.0:
            img, ox, oy = spr(T["open2"], F_ANTON, s2, WHITE)
            base = base1 + 40 + c2
            p = e_out_expo(prog(t, 1.0, 0.25))
            sc = lerp(1.25, 1.0, p)
            mask = img.getchannel("A")
            fill = view(src_image("adoracao", 1.0 + (t - 1.0) * 0.8, True), img.width, img.height, 1.15, 0.5, 0.42, False)
            fill = Image.fromarray(np.clip(np.asarray(fill).astype(np.float32) * 1.18 + 10, 0, 255).astype(np.uint8))
            fill = fill.convert("RGBA")
            fill.putalpha(mask)
            # contorno fino branco: mantém a palavra legível mesmo com a imagem por dentro
            ring = ImageChops.subtract(mask.filter(ImageFilter.MaxFilter(7)), mask)
            fill.paste(Image.new("RGBA", fill.size, WHITE + (255,)), (0, 0), ring)
            fill.putalpha(ImageChops.lighter(mask, ring))
            put(frame, (fill, ox, oy), W / 2, base, sc, e_out_cubic(prog(t, 1.0, 0.05)))

    # ---------------- 2–4 s · tem GINCANA (cabo de guerra)
    elif t < 4.0:
        bh = BAND_H * e_out_expo(prog(t, 2.0, 0.28))
        if t < 3.0:
            p = (t - 2.0)
            ts = 0.62 + 1.0 * (1 - (1 - p) ** 1.7)  # rampa: rápido -> lento
            img = shot_gincana(ts, punch(t, 2.0, 0.1), 0.42)
        else:
            img = shot_gincana(1.92 + (t - 3.0), punch(t, 3.0, 0.08), 0.5)
        band(frame, img, bh, cy=1050)
        headline_above(frame, t, 2.08, T["tem"], T["gincana"], bt=1050 - BAND_H // 2)

    # ---------------- 4–6 s · tem ALEGRIA (câmera lenta)
    elif t < 6.0:
        img = shot_gincana(3.58 + (t - 4.0) * 0.5, punch(t, 4.0, 0.1) * lerp(1.0, 1.06, prog(t, 4, 2)), 0.3, 0.5)
        band(frame, img, cy=870)
        headline_below(frame, t, 4.04, T["tem"], T["alegria"], bb=870 + BAND_H // 2)

    # ---------------- 6–8 s · a faixa abre: tem ADORAÇÃO
    elif t < 8.0:
        ex = e_io_cubic(prog(t, 6.0, 0.55))
        full = shot_adoracao_full(0.4 + (t - 6.0), z=lerp(1.0, 1.05, prog(t, 6, 2)), fy=0.5, shade=ex)
        h = lerp(BAND_H, H, ex)
        band_full(frame, full, h)
        if t >= 6.3:
            s = fit(T["adoracao"], F_ANTON, 980, 250)
            base = 690
            reveal(frame, T["adoracao"], F_ANTON, s, WHITE, W / 2, base, t, 6.3, shadow=0.5)
            bw = text_w(T["adoracao"], F_ANTON, s)
            p = e_out_cubic(prog(t, 6.42, 0.3))
            put(frame, spr(T["tem"], F_SERIF, 118, ORANGE, 0.6), W / 2 - bw / 2 + 4,
                base - cap_h(F_ANTON, s) - 14 + (1 - p) * 20, 1, p, center=False)

    # ---------------- 8–10 s · e tem DEUS NO MEIO
    elif t < 10.0:
        full = shot_adoracao_full(7.6 + (t - 8.0), z=punch(t, 8.0, 0.08) * lerp(1.06, 1.16, prog(t, 8, 2)), fy=0.47)
        frame.paste(full, (0, 0))
        s1 = fit(T["deus"], F_ANTON, 900, 400)
        b1 = 850
        slam(frame, spr(T["deus"], F_ANTON, s1, WHITE, 0.5), W / 2, b1, t, 8.04, 1.12)
        s2 = fit(T["no_meio"], F_ANTON, 640, 150)
        if t >= 8.5:
            reveal(frame, T["no_meio"], F_ANTON, s2, WHITE, W / 2, b1 + 26 + cap_h(F_ANTON, s2), t, 8.5, shadow=0.5)
        dw = text_w(T["deus"], F_ANTON, s1)
        p = e_out_cubic(prog(t, 8.16, 0.3))
        put(frame, spr(T["e_tem"], F_SERIF, 118, ORANGE, 0.6), W / 2 - dw / 2 + 4,
            b1 - cap_h(F_ANTON, s1) - 16 + (1 - p) * 20, 1, p, center=False)

    # ---------------- 10–12 s · subida: SÓ FALTA VOCÊ
    elif t < 12.0:
        words = T["build"]
        starts = [10.0, 10.5, 11.0, 11.5]
        i = max(k for k, s0 in enumerate(starts) if t >= s0)
        t0 = starts[i]
        z = punch(t, t0, 0.14, 0.35)
        if i == 0:
            frame.paste(shot_adoracao_full(4.0 + (t - t0), z * 1.1, 0.5, shade=0.6), (0, 0))
        elif i == 1:
            band(frame, shot_gincana(2.3 + (t - t0), z * 1.15, 0.45))
        elif i == 2:  # "VOCÊ" sobre o rapaz olhando pra câmera
            band(frame, shot_gincana(4.02 + (t - t0) * 0.5, z * 1.25, 0.28, 0.42))
        color = ORANGE if i == 3 else WHITE
        s = fit(words[i], F_ANTON, 980, 380)
        base = BAND_Y + cap_h(F_ANTON, s) / 2
        if i == 2:  # texto abaixo da faixa: o rosto dele fica livre
            s = 300
            base = BB - 30 + cap_h(F_ANTON, s)
        slam(frame, spr(words[i], F_ANTON, s, color, 0.55), W / 2, base, t, t0, 1.3)

    # ---------------- 12–15 s · DROP: INSCRIÇÕES ABERTAS (chácara)
    elif t < 15.0:
        bh = BAND_H * e_out_expo(prog(t, 12.0, 0.3))
        band(frame, view(src_image("chacara", 0), W, BAND_H, punch(t, 12.0, 0.15) * lerp(1.0, 1.1, prog(t, 12, 3)), 0.55, 0.45), bh)
        s = fit(T["insc"], F_ANTON, 1000, 260)
        lab = spr(T["label"], F_LABEL, 30, ORANGE, 0.0, 9)
        la = e_out_cubic(prog(t, 12.3, 0.35))
        put(frame, lab, W / 2, BT + 34 - cap_h(F_ANTON, s) - 0.21 * s - 30 + (1 - la) * 14, 1, la)
        reveal(frame, T["insc"], F_ANTON, s, WHITE, W / 2, BT + 34, t, 12.02, 0.03)
        base2 = BB - 34 + cap_h(F_ANTON, s)
        slam(frame, spr(T["abertas"], F_ANTON, s, ORANGE), W / 2, base2, t, 12.5, 1.2)

    # ---------------- 15–20 s · CTA: GARANTE SUA VAGA
    else:
        img = view(src_image("adoracao", 9.0 + (t - 15.0) * 0.75, True), W, BAND_H,
                   punch(t, 15.0, 0.08) * lerp(1.0, 1.08, prog(t, 15, 5)), 0.5, 0.47)
        cy = 860  # bloco mais alto: fora da área da legenda do Reels
        band(frame, img, cy=cy)
        s = fit(T["insc"], F_ANTON, 1000, 260)
        reveal(frame, T["garanta"], F_ANTON, s, WHITE, W / 2, cy - BAND_H // 2 + 34, t, 15.02, 0.04)
        base2 = cy + BAND_H // 2 - 34 + cap_h(F_ANTON, s)
        slam(frame, spr(T["sua_vaga"], F_ANTON, s, ORANGE), W / 2, base2, t, 15.5, 1.2)
        if t >= 16.0:
            p = e_out_cubic(prog(t, 16.0, 0.4))
            sub = spr(T["cta_sub"], F_SMALL, 48, WHITE)
            put(frame, sub, W / 2, base2 + 108 + (1 - p) * 16, 1, p * 0.92)
        if t >= 17.0:
            p = e_out_cubic(prog(t, 17.0, 0.4))
            tag = spr(T["cta_tag"], F_SERIF, 76, ORANGE)
            yb = base2 + 200 + (1 - p) * 16
            put(frame, tag, W / 2 - 24, yb, 1, p)
            x = W / 2 + text_w(T["cta_tag"], F_SERIF, 76) / 2 - 4
            put(frame, spr("↓", F_SMALL, 56, ORANGE), x, yb - 4 + math.sin((t - 17) * 7) * 7, 1, p, center=False)

    if not (11.5 <= t < 15.0):  # na revelação o selo "ACAMPAMENTO 2027" já está na tela
        hud(frame, t)
    return finish(frame, t)


def band_full(frame, full, h):
    h = int(round(h))
    top = max(0, (H - h) // 2)
    frame.paste(full.crop((0, top, W, top + h)), (0, top))


# ------------------------------------------------------------------ acabamento
def finish(frame: Image.Image, t: float) -> Image.Image:
    arr = np.asarray(frame.convert("RGB")).astype(np.float32)

    # bloom suave (halação)
    small = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).resize((W // 8, H // 8), Image.BILINEAR)
    small = small.filter(ImageFilter.GaussianBlur(6)).resize((W, H), Image.BILINEAR)
    bl = np.asarray(small).astype(np.float32)
    bl = np.clip(bl - 150, 0, None) * np.array([1.0, 0.75, 0.55], np.float32)
    arr = arr + bl * 0.35

    # light leaks
    for t0, d in LEAKS:
        if t0 <= t < t0 + d:
            p = (t - t0) / d
            a = math.sin(math.pi * p) * (0.3 if TELAO else 0.45)
            shift = int(lerp(-500, 500, p)) if TELAO else int(lerp(-300, 300, p))
            lk = np.roll(LEAK, shift, axis=1 if TELAO else 0) * a * 255
            arr = 255 - (255 - arr) * (255 - lk) / 255

    # flashes
    for t0, s in FLASHES:
        if t0 <= t < t0 + 0.2:
            a = s * (1 - (t - t0) / 0.2) ** 2 * 0.85
            arr = arr + (255 - arr) * a

    arr *= VIG

    # granulação (meia resolução, ampliada)
    g = GRAIN[int(t * FPS) % len(GRAIN)]
    g = np.repeat(np.repeat(g, 2, axis=0), 2, axis=1)
    arr = arr + g

    # tremor + aberração cromática nos impactos
    k = hit_k(t)
    out = np.clip(arr, 0, 255).astype(np.uint8)
    if k > 0.02:
        sh = int(round(8 * k))
        out[..., 0] = np.roll(out[..., 0], sh, axis=1)
        out[..., 2] = np.roll(out[..., 2], -sh, axis=1)
        img = Image.fromarray(out)
        dx, dy = math.sin(t * 90) * 14 * k, math.cos(t * 77) * 10 * k
        z = 1 + 0.03 * k
        img = img.transform((W, H), Image.AFFINE, (1 / z, 0, (W - W / z) / 2 - dx, 0, 1 / z, (H - H / z) / 2 - dy),
                            resample=Image.BILINEAR)
        return img
    return Image.fromarray(out)


# ------------------------------------------------------------------ capa (peça própria, não um quadro do vídeo)
def make_cover() -> Image.Image:
    """Capa 9:16 pensada para o recorte 3:4 da grade do perfil (miolo y 240–1680)."""
    frame = Image.new("RGBA", (W, H), INK + (255,))
    frame.paste(shot_adoracao_full(8.7, z=1.06, fy=0.5, blend=False, shade=1.0), (0, 0))
    s1 = fit(T["open1"], F_ANTON, 960, 300)
    s2 = fit(T["open2"], F_ANTON, 980, 520)
    c1, c2 = cap_h(F_ANTON, s1), cap_h(F_ANTON, s2)
    b1 = 760
    b2 = b1 + 34 + c2
    w1 = text_w(T["open1"], F_ANTON, s1)
    put(frame, spr(T["kicker"], F_SERIF, 108, ORANGE, 0.7), W / 2 - w1 / 2 + 4, b1 - c1 - 18, center=False)
    put(frame, spr(T["open1"], F_ANTON, s1, WHITE, 0.6), W / 2, b1)
    put(frame, spr(T["open2"], F_ANTON, s2, ORANGE, 0.6), W / 2, b2)
    # faixa de chamada
    lab = T["hud_r"]
    ls = 84
    lw = text_w(lab, F_ANTON, ls, 3)
    bw, bh = int(lw + 90), int(cap_h(F_ANTON, ls) + 64)
    y0 = 1430
    d = ImageDraw.Draw(frame)
    d.rounded_rectangle((W / 2 - bw / 2, y0, W / 2 + bw / 2, y0 + bh), radius=14, fill=ORANGE + (255,))
    put(frame, spr(lab, F_ANTON, ls, INK, 0.0, 3), W / 2, y0 + 32 + cap_h(F_ANTON, ls))
    put(frame, spr(T["label"], F_LABEL, 34, WHITE, 0.5, 10), W / 2, y0 - 36)
    return finish(frame, 99.0)


# ------------------------------------------------------------------ versão telão (16:9)
def lbox(frame, img, h=LB_H):
    """Cola a imagem 16:9 deixando visível só a altura h (barras de cinema em cima e embaixo)."""
    h = int(round(min(h, H)))
    if h <= 0:
        return
    top = (H - h) // 2
    frame.paste(img.crop((0, top, W, top + h)), (0, top))


def shot_t(name, ts, z=1.0, fx=0.5, fy=0.5, blend=False, shade=0.0):
    """Plano em 16:9 cheio. A adoração (vertical) entra recortada na faixa da roda de pessoas."""
    img = view(src_image(name, ts, blend), W, H, z, fx, fy)
    if shade > 0:
        a = np.asarray(img).astype(np.float32) * (1 + (TOP_SHADE - 1) * shade)
        img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    return img


def inline_title(frame, t, t0, small, big, side="left", size=270):
    """Serifa laranja + PALAVRA em Anton na mesma linha, no canto inferior, encostando na barra."""
    s = fit(big, F_ANTON, 1200, size)
    bw = text_w(big, F_ANTON, s)
    ss, gap = 140, 30
    sw = text_w(small, F_SERIF, ss)
    x0 = MX if side == "left" else W - MX - (sw + gap + bw)
    p = e_out_cubic(prog(t, t0, 0.3))
    put(frame, spr(small, F_SERIF, ss, ORANGE, 0.9), x0, BASE_T + (1 - p) * 20, 1, p, center=False)
    reveal(frame, big, F_ANTON, s, WHITE, x0 + sw + gap + bw / 2, BASE_T, t, t0 + 0.06, shadow=0.5)


def two_tone(frame, t, a_txt, b_txt, base, maxw, maxs, t_a, t_b, stagger=0.03):
    """Uma linha em duas cores: primeira palavra branca (revelada), segunda laranja (impacto)."""
    s = fit(a_txt + " " + b_txt, F_ANTON, maxw, maxs)
    w1, w2, gap = text_w(a_txt, F_ANTON, s), text_w(b_txt, F_ANTON, s), 0.24 * s
    x0 = (W - (w1 + gap + w2)) / 2
    reveal(frame, a_txt, F_ANTON, s, WHITE, x0 + w1 / 2, base, t, t_a, stagger, shadow=0.5)
    slam(frame, spr(b_txt, F_ANTON, s, ORANGE, 0.5), x0 + w1 + gap + w2 / 2, base, t, t_b, 1.2)
    return s


def compose_telao(t: float) -> Image.Image:
    frame = Image.new("RGBA", (W, H), INK + (255,))

    # ---------------- 0–2 s · gancho: avisa a galera: O ACAMPA / VOLTOU (vazado com a adoração)
    if t < 2.0:
        s1 = fit(T["open1"], F_ANTON, 1150, 300)
        s2 = fit(T["open2"], F_ANTON, 1150, 470)
        c1, c2 = cap_h(F_ANTON, s1), cap_h(F_ANTON, s2)
        base1 = H / 2 - (c1 + 36 + c2) / 2 + c1 + 48
        slam(frame, spr(T["open1"], F_ANTON, s1, WHITE), W / 2, base1, t, 0.0, 1.22)
        w1 = text_w(T["open1"], F_ANTON, s1)
        pk = e_out_cubic(prog(t, 0.14, 0.3))
        put(frame, spr(T["kicker"], F_SERIF, 112, ORANGE), W / 2 - w1 / 2 + 4,
            base1 - c1 - 18 + (1 - pk) * 20, 1, pk, center=False)
        if t >= 1.0:
            img, ox, oy = spr(T["open2"], F_ANTON, s2, WHITE)
            mask = img.getchannel("A")
            fill = view(src_image("adoracao", 1.0 + (t - 1.0) * 0.8, True), img.width, img.height, 1.0, 0.5, 0.47, False)
            fill = Image.fromarray(np.clip(np.asarray(fill).astype(np.float32) * 1.18 + 10, 0, 255).astype(np.uint8))
            fill = fill.convert("RGBA")
            ring = ImageChops.subtract(mask.filter(ImageFilter.MaxFilter(7)), mask)
            fill.paste(Image.new("RGBA", fill.size, WHITE + (255,)), (0, 0), ring)
            fill.putalpha(ImageChops.lighter(mask, ring))
            sc = lerp(1.25, 1.0, e_out_expo(prog(t, 1.0, 0.25)))
            put(frame, (fill, ox, oy), W / 2, base1 + 36 + c2, sc, e_out_cubic(prog(t, 1.0, 0.05)))

    # ---------------- 2–4 s · tem GINCANA (cabo de guerra, tela de cinema)
    elif t < 4.0:
        h = LB_H * e_out_expo(prog(t, 2.0, 0.28))
        if t < 3.0:
            p = t - 2.0
            ts = 0.62 + 1.0 * (1 - (1 - p) ** 1.7)  # rampa: rápido -> lento
            img = shot_t("gincana", ts, punch(t, 2.0, 0.1), 0.42, 0.5, shade=0.85)
        else:
            img = shot_t("gincana", 1.92 + (t - 3.0), punch(t, 3.0, 0.08), 0.5, 0.5, shade=0.85)
        lbox(frame, img, h)
        inline_title(frame, t, 2.08, T["tem"], T["gincana"], "left")

    # ---------------- 4–6 s · tem ALEGRIA (câmera lenta)
    elif t < 6.0:
        img = shot_t("gincana", 3.58 + (t - 4.0) * 0.5, punch(t, 4.0, 0.1) * lerp(1.0, 1.06, prog(t, 4, 2)), 0.3, 0.5, shade=0.85)
        lbox(frame, img)
        inline_title(frame, t, 4.04, T["tem"], T["alegria"], "right")

    # ---------------- 6–8 s · as barras abrem: tem ADORAÇÃO
    elif t < 8.0:
        ex = e_io_cubic(prog(t, 6.0, 0.55))
        img = shot_t("adoracao", 0.4 + (t - 6.0), lerp(1.0, 1.05, prog(t, 6, 2)), 0.5, 0.56, True, lerp(0.85, 1.0, ex))
        lbox(frame, img, lerp(LB_H, H, ex))
        if t >= 6.3:
            inline_title(frame, t, 6.3, T["tem"], T["adoracao"], "left")

    # ---------------- 8–10 s · e o principal: DEUS NO MEIO
    elif t < 10.0:
        img = shot_t("adoracao", 7.6 + (t - 8.0), punch(t, 8.0, 0.08) * lerp(1.04, 1.14, prog(t, 8, 2)), 0.5, 0.5, True, 1.0)
        frame.paste(img, (0, 0))
        line = T["deus"] + " " + T["no_meio"]
        s = fit(line, F_ANTON, 1500, 300)
        slam(frame, spr(line, F_ANTON, s, WHITE, 0.55), W / 2, BASE_T, t, 8.04, 1.12)
        dw = text_w(line, F_ANTON, s)
        p = e_out_cubic(prog(t, 8.16, 0.3))
        put(frame, spr(T["e_tem"], F_SERIF, 124, ORANGE, 0.6), W / 2 - dw / 2 + 4,
            BASE_T - cap_h(F_ANTON, s) - 18 + (1 - p) * 20, 1, p, center=False)

    # ---------------- 10–12 s · subida: SÓ FALTA VOCÊ
    elif t < 12.0:
        words = T["build"]
        starts = [10.0, 10.5, 11.0, 11.5]
        i = max(k for k, s0 in enumerate(starts) if t >= s0)
        t0 = starts[i]
        z = punch(t, t0, 0.14, 0.35)
        cx, smax = W / 2, 440
        if i == 0:
            frame.paste(shot_t("adoracao", 4.0 + (t - t0), z * 1.08, 0.5, 0.52, True, 0.5), (0, 0))
        elif i == 1:
            frame.paste(shot_t("gincana", 2.3 + (t - t0), z * 1.12, 0.45, 0.5), (0, 0))
        elif i == 2:  # "VOCÊ" ao lado do rapaz olhando pra câmera
            frame.paste(shot_t("gincana", 4.02 + (t - t0) * 0.5, z * 1.18, 0.3, 0.45), (0, 0))
            cx, smax = 1340, 360
        color = ORANGE if i == 3 else WHITE
        s = fit(words[i], F_ANTON, 1500, smax)
        slam(frame, spr(words[i], F_ANTON, s, color, 0.55), cx, H / 2 + cap_h(F_ANTON, s) / 2, t, t0, 1.3)

    # ---------------- 12–15 s · DROP: INSCRIÇÕES ABERTAS (chácara)
    elif t < 15.0:
        h = LB_H * e_out_expo(prog(t, 12.0, 0.3))
        img = shot_t("chacara", 0, punch(t, 12.0, 0.15) * lerp(1.0, 1.08, prog(t, 12, 3)), 0.55, 0.45)
        lbox(frame, img, h)
        two_tone(frame, t, T["insc"], T["abertas"], BASE_T, 1720, 260, 12.02, 12.5)
        la = e_out_cubic(prog(t, 12.3, 0.35))
        put(frame, spr(T["label"], F_LABEL, 34, ORANGE, 0.0, 10), W / 2, 88 + (1 - la) * 10, 1, la)

    # ---------------- 15–20 s · cartela final: GARANTE SUA VAGA
    else:
        img = shot_t("adoracao", 9.0 + (t - 15.0) * 0.75, punch(t, 15.0, 0.08) * lerp(1.0, 1.08, prog(t, 15, 5)), 0.5, 0.5, True)
        img = Image.eval(img, lambda v: int(v * 0.42))  # escurece a imagem: cartela legível de longe
        lbox(frame, img)
        b1 = 505
        two_tone(frame, t, T["garanta"], T["sua_vaga"], b1, 1480, 250, 15.02, 15.5, 0.04)
        if t >= 16.0:
            p = e_out_cubic(prog(t, 16.0, 0.4))
            put(frame, spr(T["cta_sub"], F_SMALL, 56, WHITE, 0.5), W / 2, b1 + 116 + (1 - p) * 16, 1, p * 0.95)
        if t >= 17.0:
            p = e_out_cubic(prog(t, 17.0, 0.4))
            put(frame, spr(T["cta_tag_telao"], F_SERIF, 98, ORANGE, 0.5), W / 2, b1 + 246 + (1 - p) * 16, 1, p)

    if not (11.5 <= t < 15.0):  # na revelação o selo "ACAMPAMENTO 2027" ocupa a barra de cima
        hud(frame, t)
    return finish(frame, t)


COMPOSE = compose_telao if TELAO else compose


# ------------------------------------------------------------------ main
def _frame(i):
    return COMPOSE(i / FPS).tobytes()


def encode(audio_path, out_path, video_tmp):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", video_tmp, "-i", audio_path,
                    "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    "-shortest", "-movflags", "+faststart", out_path], check=True)


def main():
    extract_frames()
    args = [a for a in sys.argv[1:] if a != "--telao"]
    if args and args[0] == "--preview":
        os.makedirs(os.path.join(HERE, "preview"), exist_ok=True)
        for ts in args[1:]:
            if ts == "capa":
                p = os.path.join(HERE, "preview", "capa.png")
                make_cover().save(p)
            else:
                p = os.path.join(HERE, "preview", f"{_NOME}_t{float(ts):05.2f}.png")
                COMPOSE(float(ts)).save(p)
            print(p)
        return

    audio_full, audio_nomusic = trilha.main(CACHE)
    video_tmp = os.path.join(CACHE, f"video_{_NOME}.mp4")
    # telão: mais bitrate (qualidade de projeção); Reels: leve o bastante para WhatsApp
    crf, maxrate, bufsize, level = ("19", "12M", "24M", "4.2") if TELAO else ("21", "6M", "12M", "4.1")
    ff = subprocess.Popen([
        "ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
        "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "slow", "-crf", crf,
        "-maxrate", maxrate, "-bufsize", bufsize, "-pix_fmt", "yuv420p", "-profile:v", "high",
        "-level", level, "-movflags", "+faststart", video_tmp,
    ], stdin=subprocess.PIPE)
    with Pool(os.cpu_count() or 2) as pool:
        for n, buf in enumerate(pool.imap(_frame, range(NFRAMES), chunksize=3)):
            ff.stdin.write(buf)
            if n % 90 == 0:
                print(f"quadro {n}/{NFRAMES}", flush=True)
    ff.stdin.close()
    if ff.wait():
        sys.exit("ffmpeg falhou")
    encode(audio_full, OUT_MAIN, video_tmp)
    encode(audio_nomusic, OUT_NOMUSIC, video_tmp)
    if TELAO:
        print(OUT_MAIN, OUT_NOMUSIC, sep="\n")
        return
    make_cover().convert("RGB").save(OUT_COVER, quality=93)
    print(OUT_MAIN, OUT_NOMUSIC, OUT_COVER, sep="\n")


if __name__ == "__main__":
    main()
