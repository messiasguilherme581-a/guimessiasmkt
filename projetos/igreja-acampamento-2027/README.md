# Acampamento 2027 · Inscrições abertas (Reels 9:16, versão 2)

Peça de divulgação para **jovens de 15 a 30 anos**, editada com os melhores trechos dos vídeos do último acampamento e a foto da chácara. Esta versão tem copy revisada, imagens restauradas e capa nova.

| Arquivo | O que é |
|---|---|
| `acampamento-2027-reels.mp4` | **Versão principal**: 1080x1920, 30 fps, 20 s, com trilha original + efeitos + som ambiente (cerca de 16 MB) |
| `acampamento-2027-reels-sem-musica.mp4` | Mesmo vídeo, só com efeitos e som ambiente, para colocar uma música da biblioteca do Instagram ou do TikTok |
| `capa.jpg` | Capa própria: O ACAMPA VOLTOU + INSCRIÇÕES ABERTAS sobre a roda de adoração |
| `render.py` | Gera o vídeo; os textos ficam no bloco `T` |
| `trilha.py` | Gera a trilha (120 BPM, sintetizada aqui mesmo, sem direitos de terceiros) |
| `assets/` | Material bruto: `gincana.mp4`, `adoracao.mp4`, `chacara.jpg` e as fontes (licença OFL) |

## Trechos aproveitados

| Vídeo | Trecho | Por quê |
|---|---|---|
| `gincana.mp4` | 0,6–2,9 s | Cabo de guerra com as barracas ao fundo: ação e cara de acampamento |
| `gincana.mp4` | 3,6–4,6 s | Rapaz rindo pra câmera, em câmera lenta: "alegria" |
| `adoracao.mp4` | 0,4–2,4 s | Mãos levantadas em primeiro plano |
| `adoracao.mp4` | 7,6–13,0 s | A roda inteira de adoração debaixo das árvores |
| `chacara.jpg` | foto | Revelação das inscrições |

## Roteiro (cortes no tempo da música, 120 BPM)

| Tempo | Imagem | Texto na tela |
|---|---|---|
| 0–2 s | Preto, depois **VOLTOU** com contorno fino e a adoração dentro das letras | *avisa a galera:* **O ACAMPA** / **VOLTOU** |
| 2–4 s | Faixa de cinema: cabo de guerra, com rampa de velocidade | *tem* **GINCANA** |
| 4–6 s | Câmera lenta do rapaz rindo | *tem* **ALEGRIA** |
| 6–8 s | A faixa abre para tela cheia: adoração | *tem* **ADORAÇÃO** |
| 8–10 s | Roda inteira, câmera aproximando | *e o principal:* **DEUS NO MEIO** |
| 10–12 s | Cortes rápidos; "VOCÊ" entra com o rapaz olhando pra câmera e depois fica laranja no preto | **SÓ · FALTA · VOCÊ** |
| 12–15 s | **Drop**: flash e a chácara na faixa | ACAMPAMENTO 2027 · **INSCRIÇÕES ABERTAS** |
| 15–20 s | Adoração em câmera lenta (bloco mais alto, fora da área da legenda do Reels) | **GARANTE SUA VAGA** · Inscrições com a liderança da igreja · *e marca quem vai com você ↓* |

### Por que essa copy

- **Gancho "avisa a galera: o acampa voltou":** fala como o jovem fala ("acampa"). Quem já foi se reconhece e quem nunca foi fica curioso, logo no primeiro segundo.
- **"tem gincana / tem alegria / tem adoração":** cada frase aparece junto com a imagem que comprova o que ela diz.
- **"e o principal: Deus no meio":** coloca o propósito do acampamento acima da diversão, sem soar como sermão.
- **"só falta você":** convite que acolhe, em vez de cobrar como no "vai ficar de fora?". A frase aparece com o rapaz olhando pra câmera.
- **"garante sua vaga" + "e marca quem vai com você":** dá um passo pra se inscrever e outro pra marcar amigos, e as marcações espalham o post.

### Tratamento das imagens

- **Restauração dos vídeos do WhatsApp:** tira a compressão (`hqdn3d` + `nlmeans`), amplia em 2x com Lanczos e devolve nitidez com CAS. A foto da chácara recebeu o mesmo tratamento.
- **Cor:** mais contraste, pretos levemente levantados, altas quentes e saturação ajustada por vídeo (o verde da adoração foi controlado). Granulação e halação por cima.
- **Capa nova (`capa.jpg`):** a roda de adoração em tela cheia, o gancho "O ACAMPA VOLTOU" e a faixa laranja "INSCRIÇÕES ABERTAS". Tudo cabe no recorte 3:4 da grade do perfil.

**Linguagem visual:** preto profundo, faixa widescreen 2:1 que abre para tela cheia no momento da adoração, Anton (condensada) com acentos em Instrument Serif itálica, laranja "fogueira" `#FF601C` sobre branco quente, flashes e tremor com aberração cromática nos impactos.

**Trilha:** gancho com dois impactos, groove na gincana e na alegria, pausa com pad e som ambiente da adoração, subida com caixa acelerando e um impacto em cada palavra de "só falta você", drop nas inscrições e batida final em 19 s. Entrega em -14 LUFS.

## Legenda sugerida para o post

> Avisa a galera: o acampa voltou. E esse ano só falta você.
>
> Tem gincana, tem alegria, tem adoração debaixo das árvores… e o principal: Deus no meio.
> As inscrições pro **Acampamento 2027** estão abertas.
>
> 📲 Inscrições com a liderança da igreja [ou: chama no WhatsApp (xx) xxxxx-xxxx]
> 📅 [data] · 📍 [local] · 💰 [valor]   ← preencher ou apagar
>
> Marca aqui quem vai com você 👇
>
> #acampamento2027 #acampamentocristao #juventudecrista

**Outras primeiras linhas pra testar em stories ou repost:**
- "Se você foi no último, já sabe. Se não foi… esse é o ano."
- "Gincana, alegria e Deus no meio. As inscrições abriram."

## Como mudar textos e gerar de novo

1. Edite o bloco `T` em `render.py`. Exemplo: troque `cta_sub` pelo WhatsApp ou pela data.
2. Para conferir quadros parados: `python3 render.py --preview 1.5 9 13.5 16.5 capa`, que salva PNGs em `preview/`.
3. Para gerar o vídeo final: `python3 render.py`. Na primeira vez a restauração leva cerca de 3 min a mais; depois, cerca de 1 min 20 s em 4 núcleos e também gera as duas trilhas.

Requisitos: Python 3.11+, Pillow, numpy, scipy, ffmpeg com libx264 e Inter Display em `/usr/share/fonts/opentype/inter`. Anton e Instrument Serif já estão em `assets/fonts`.
