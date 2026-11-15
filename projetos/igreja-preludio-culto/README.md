# Prelúdio do culto · frases com impacto

Nova versão do vídeo de abertura do culto (`assets/original.mp4`): as mesmas 8 frases e a mesma música, com os textos corrigidos e visual de cinema em Full HD.

| Arquivo | O que é |
|---|---|
| `preludio-culto.mp4` | Vídeo final: 1920x1080, 30 fps, 2 min 10 s, com o áudio original |
| `render.py` | Gera o vídeo; as frases ficam no bloco `QUOTES` |
| `assets/original.mp4` | Vídeo original (fonte da música) |
| `assets/fonts/` | Anton (licença OFL) |

## Correções de texto

| # | Como estava | Como ficou | O que foi corrigido |
|---|---|---|---|
| 1 | AS ÚNICAS PESSOAS QUE QUEREM MUDAR O EVANGELHO, SÃO AQUELES QUE NÃO SÃO MUDADOS POR ELE | As únicas pessoas que querem mudar o Evangelho são **aquelas** que não são **mudadas** por ele. | Vírgula entre sujeito e verbo; concordância com "pessoas"; ponto final |
| 2 | …EU POSSO CHEGAR AO **SEU** SEM ANDAR… | …Eu posso chegar ao **céu** sem andar, mas não sem a Palavra de Deus.” | "seu" → "céu"; faltava fechar as aspas |
| 3 | …LEIA A BÍBLIA**,** VOCÊ QUER OUVIR… EM VOZ ALTA | …Leia a Bíblia**.** Você quer ouvir a voz de Deus audivelmente? Leia a Bíblia em voz alta. | Ponto no lugar da vírgula; ponto final |
| 4 | QUANDO VOCÊ LEMBRAR DE ONDE… DUVIDAR AONDE ELE PODE TE LEVAR · BILLY **GRANHAM** | Quando você **se** lembrar de onde Deus te tirou, vai parar de duvidar **de** aonde Ele pode te levar. · BILLY **GRAHAM** | "lembrar-se de"; "duvidar de"; espaço antes das aspas; nome do autor |
| 5 | SE FRACASSARMOS NA ORAÇÃO, FRACASSAREMOS EM TODA FRENTE DE BATALHA | (igual) + ponto final | Só o ponto final |
| 6 | …PULAREM **AO INVÉS DE** DOBRAREM SEUS JOELHOS. · DAVID **WHIKERSON** | …pularem **em vez de** dobrarem seus joelhos. · DAVID **WILKERSON** | "ao invés de" (= ao contrário de) → "em vez de" (= no lugar de); nome do autor |
| 7 | NÃO HAVERÁ RENOVAÇÃO… NOS QUEBRE · DAVID **WHIKERSON** | (igual) + ponto final · DAVID **WILKERSON** | Ponto final; nome do autor |
| 8 | O VERDADEIRO IDEAL CRISTÃO NÃO É SER FELIZ, MAS SER SANTO · **AW** TOZER | (igual) + ponto final · **A. W.** TOZER | Ponto final; iniciais do autor |
| fim | NOSSO CULTO INICIA AGORA! | Nosso culto **se** inicia agora! | "iniciar-se" pede o pronome |

Decisões que ficaram como no original:

- **"Deus te tirou / te levar" com "você":** a gramática rígida pediria "o tirou / levá-lo", mas isso mudaria a frase. Mantive a forma falada, que é a conhecida.
- **Autores:** só corrigi a grafia dos nomes. Não consegui confirmar em fonte confiável a autoria das frases 2 e 3 (John Piper); vale conferir antes de exibir.

## O que mudou no visual

- **Fundo novo em Full HD:** névoa azul, raios de luz vindos do alto e poeira dourada subindo. O original tinha 1024x576 e bem pouca qualidade.
- **Reage à música:** a luz e as partículas ficam mais fortes quando a música cresce, e dão um pulso nos ataques.
- **Frases palavra por palavra:** o texto entra no ritmo da leitura, com pausas antes das frases de impacto. Antes ficava até 26 s parado.
- **Palavras-chave em dourado:** "Leia a Bíblia.", "Palavra de Deus.", "nos quebre.", "Santo." (esta cai no ataque da música em 2:01).
- **Autor:** fio dourado e nome em caixa alta espaçada.
- **Contagem regressiva discreta:** "O culto começa em 02:05", zerando quando entra a cartela final. Para tirar, `COUNTDOWN = False` no `render.py`.
- **Cartela final:** "Nosso culto se inicia agora!" entra com clarão no ataque da música em 2:06.

## Tempos

| Frase | Entra | Sai |
|---|---|---|
| 1 · Ravenhill | 0:00 | 0:15 |
| 2 · Piper | 0:16 | 0:34 |
| 3 · Piper | 0:35 | 0:54 |
| 4 · Graham | 0:54 | 1:13 |
| 5 · Ravenhill | 1:13 | 1:26 |
| 6 · Wilkerson | 1:27 | 1:40 |
| 7 · Wilkerson | 1:40 | 1:53 |
| 8 · Tozer | 1:54 | 2:06 |
| Cartela final | 2:06 | 2:11 |

## Como mudar textos e gerar de novo

1. Edite o bloco `QUOTES` em `render.py` (texto, estilo `"w"` branco ou `"g"` dourado, e o atraso de cada linha).
2. Para conferir quadros parados: `python3 render.py --preview 9.5 47 124 126.6`.
3. Para gerar o vídeo final: `python3 render.py` (cerca de 8 minutos em 4 núcleos).

Requisitos: Python 3.11+, Pillow, numpy, scipy, ffmpeg com libx264 e Inter Display em `/usr/share/fonts/opentype/inter`.
