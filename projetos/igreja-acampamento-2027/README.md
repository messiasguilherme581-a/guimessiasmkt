# Acampamento 2027 · Inscrições abertas (Reels 9:16, versão 2)

Peça de divulgação para **jovens de 15 a 30 anos**, editada com os melhores trechos dos vídeos do último acampamento e a foto da chácara.

| Arquivo | O que é |
|---|---|
| `acampamento-2027-reels.mp4` | **Versão principal**: 1080x1920, 30 fps, 20 s, com trilha original + efeitos + som ambiente (cerca de 16 MB) |
| `acampamento-2027-reels-sem-musica.mp4` | Mesmo vídeo, só com efeitos e som ambiente, para colocar uma música da biblioteca do Instagram ou do TikTok |
| `capa.jpg` | Capa: INSCRIÇÕES ABERTAS sobre a chácara |
| `render.py` | Gera o vídeo; os textos ficam no bloco `T` |
| `trilha.py` | Gera a trilha (120 BPM, sintetizada aqui mesmo, sem direitos de terceiros) |
| `assets/` | Material bruto: `gincana.mp4`, `adoracao.mp4`, `chacara.jpg` e as fontes (licença OFL) |

## Trechos aproveitados

| Vídeo | Trecho | Por quê |
|---|---|---|
| `gincana.mp4` | 0,6–2,9 s | Cabo de guerra com as barracas ao fundo: ação e cara de acampamento |
| `gincana.mp4` | 3,6–4,6 s | Rapaz rindo pra câmera, em câmera lenta: "resenha" |
| `adoracao.mp4` | 0,4–2,4 s | Mãos levantadas em primeiro plano |
| `adoracao.mp4` | 7,6–13,0 s | A roda inteira de adoração debaixo das árvores |
| `chacara.jpg` | foto | Revelação das inscrições |

## Roteiro (cortes no tempo da música, 120 BPM)

| Tempo | Imagem | Texto |
|---|---|---|
| 0–2 s | Preto, depois **2027** vazado com a adoração dentro das letras | **ACAMPAMENTO** / **2027** (dois impactos) |
| 2–4 s | Faixa de cinema: cabo de guerra, com rampa de velocidade | *tem* **GINCANA** |
| 4–6 s | Câmera lenta do rapaz rindo | *tem* **RESENHA** |
| 6–8 s | A faixa abre para tela cheia: adoração | *tem* **ADORAÇÃO** |
| 8–10 s | Roda inteira, câmera aproximando | *e tem* **DEUS NO MEIO** |
| 10–12 s | Cortes rápidos com zoom de impacto e caixa acelerando | **VOCÊ · VAI · FICAR · DE · FORA?** |
| 12–15 s | **Drop**: flash e a chácara na faixa | ACAMPAMENTO 2027 · **INSCRIÇÕES ABERTAS** |
| 15–20 s | Adoração em câmera lenta | **GARANTA SUA VAGA** · Fale com a liderança da igreja → |

Faixa fixa no topo: `ACAMPAMENTO 2027 · ● INSCRIÇÕES ABERTAS` (o ponto pisca como um REC).

**Linguagem visual:** preto profundo, faixa widescreen 2:1 que abre para tela cheia no momento da adoração, Anton (condensada) com acentos em Instrument Serif itálica, laranja "fogueira" `#FF601C` sobre branco quente, granulação de filme, halação, light leak, flashes e tremor com aberração cromática nos impactos.

**Trilha:** abertura com dois impactos, groove na gincana e na resenha, pausa com pad e som ambiente da adoração, subida com caixa acelerando e riser, drop nas inscrições e batida final em 19 s. Entrega em -14 LUFS (padrão das redes).

## Legenda sugerida para o post

> SE VOCÊ NÃO FOI NO ÚLTIMO, ESSE NÃO DÁ PRA PERDER 🔥
>
> Tem gincana, tem resenha, tem adoração… e tem Deus no meio.
> As inscrições pro **Acampamento 2027** estão abertas!
>
> 📲 Fale com a liderança da igreja e garanta sua vaga.
> 📅 [data] · 💰 [valor] · 📞 [contato/WhatsApp]   ← preencher ou apagar
>
> Marca aqui quem vai com você 👇
>
> #acampamento2027 #acampamentocristao #juventudecrista #jovensdeDeus #igreja

## Como mudar textos e gerar de novo

1. Edite o bloco `T` em `render.py`. Exemplo: troque `cta_sub` pelo WhatsApp ou pela data.
2. Para conferir quadros parados: `python3 render.py --preview 1.5 9 13.5 16.5`, que salva PNGs em `preview/`.
3. Para gerar o vídeo final: `python3 render.py`. Leva cerca de 1 min 20 s em 4 núcleos e também gera as duas trilhas.

Requisitos: Python 3.11+, Pillow, numpy, scipy, ffmpeg com libx264 e Inter Display em `/usr/share/fonts/opentype/inter`. Anton e Instrument Serif já estão em `assets/fonts`.
