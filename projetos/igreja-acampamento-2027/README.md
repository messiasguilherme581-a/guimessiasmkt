# Acampamento 2027 · Inscrições abertas (Reels 9:16)

Peça de divulgação feita a partir de **uma foto** da chácara (`assets/chacara.jpg`):
motion graphics com fundo desfocado, foto em card com movimento de câmera,
tipografia animada e chamada pra ação no final.

| Arquivo | O que é |
|---|---|
| `acampamento-2027-reels.mp4` | Vídeo final · 1080x1920 · 30 fps · 15 s · H.264 · cerca de 8,5 MB |
| `capa.jpg` | Capa do Reels (o miolo cabe no recorte do feed) |
| `render.py` | Script que gera o vídeo; os textos ficam no bloco `TXT` |
| `assets/chacara.jpg` | Foto original |

## Roteiro

| Tempo | Câmera na foto | Texto |
|---|---|---|
| 0–3 s | Plano geral, push-in lento | selo **VEM AÍ** · **ACAMPAMENTO** · **2027** (carimbo com tremor) |
| 3–7 s | Zoom na placa da chácara | **INSCRIÇÕES** + selo **ABERTAS** · "A chácara já está *te esperando.*" (palavra a palavra) |
| 7–11 s | Passeio pela área coberta | "DIAS DE" **COMUNHÃO → LOUVOR → PALAVRA** · "Um tempo separado *para Deus.*" |
| 11–15 s | Volta ao plano geral, o card diminui | ACAMPAMENTO 2027 · **INSCRIÇÕES ABERTAS** · botão **GARANTA SUA VAGA** (pulsando) · "Fale com a liderança da igreja" |

Paleta tirada da própria foto: amarelo do portão `#FFC21A`, navy `#0C183A` e branco. Fonte: Inter Display (Black, Bold e SemiBold).

## Áudio

O vídeo sai com uma faixa de áudio **muda**. Escolha a música dentro do Instagram ou do TikTok:
o áudio da biblioteca do app já vem licenciado e também ajuda no alcance. Dá certo com louvor animado ou com trilha em alta.

## Legenda sugerida para o post

> ⛺ INSCRIÇÕES ABERTAS — ACAMPAMENTO 2027!
>
> Dias de comunhão, louvor e Palavra, um tempo separado para Deus. A chácara já está te esperando. 🙌
>
> 📲 Fale com a liderança da igreja e garanta sua vaga.
>
> 📅 [data] · 💰 [valor] · 📞 [contato/WhatsApp]   ← preencher ou apagar
>
> #acampamento2027 #acampamentocristao #igreja #juventudecrista #retiro

## Como mudar textos e gerar de novo

1. Edite o bloco `TXT` em `render.py`. Exemplo: troque `cta_sub` pelo WhatsApp ou pela data.
2. Para conferir quadros parados: `python3 render.py --preview 1.5 5 9 13.5`, que salva PNGs em `preview/`.
3. Para gerar o vídeo final: `python3 render.py`. Leva cerca de 1 minuto em 4 núcleos.

Requisitos: Python 3.11+, Pillow, numpy, ffmpeg com libx264 e a fonte Inter Display em `/usr/share/fonts/opentype/inter`.
