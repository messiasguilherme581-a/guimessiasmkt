# Prelúdio do culto · frases com impacto

Nova versão do vídeo de abertura do culto (`assets/original.mp4`): as mesmas 8 frases e a mesma música, com os textos corrigidos e visual de cinema em Full HD.

| Arquivo | O que é |
|---|---|
| `preludio-culto.mp4` | Vídeo final: 1920x1080, 30 fps, 2 min 11 s, cerca de 36 MB, com o áudio original copiado sem recompressão |
| `preludio-culto-opcao-b.mp4` | **Opção B (escolhida)**: estilo documentário de película, nas cores e com a logo da Igreja Evangélica Atos |
| `render.py` | Gera a opção A; as frases ficam no bloco `QUOTES` |
| `render_b.py` | Gera a opção B |
| `assets/logo-atos.png` | Logo da Igreja Evangélica Atos (branca, fundo transparente) |
| `assets/original.mp4` | Vídeo original (fonte da música) |
| `assets/fonts/` | Anton (opção A), DM Serif Display e Courier Prime (opção B), todas com licença OFL |

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

## Opção B: documentário em película, nas cores da Igreja Evangélica Atos

A opção A (dourado com brilho, partículas e raios de luz) tem os sinais típicos de vídeo gerado por IA. A opção B troca essa linguagem pela de filme de verdade: imperfeição analógica (grão, riscos, corte seco), tipografia editorial e movimento contido. Esta é a versão escolhida.

| | Opção A | Opção B |
|---|---|---|
| Cor | Azul e dourado com brilho | Preto de película com luz azul; texto prateado e detalhes no azul da Atos |
| Fundo | Partículas, névoa e raios gerados | Preto de película com uma luz azul suave |
| Letra | Anton em caixa alta, centralizada | DM Serif Display em caixa normal, alinhada à esquerda |
| Ênfase | Palavras em dourado | Itálico com um traço azul feito à mão |
| Autor | Caixa alta espaçada | Datilografado letra por letra (Courier), em prata |
| Troca de frase | Risco de luz | Corte seco com vazamento de luz azul e prata |
| Acabamento | Brilho suave | Grão, poeira, riscos, tremor de projetor e tela de cinema (2,39:1) |
| Final | Dourado sobre azul | Inversão para cartela prata com tinta azul-marinho |
| Marca | Não tem | Logo da Atos pequena no canto inferior direito, o vídeo todo |

- **Cores da igreja:** azul `#233DFF` (o mesmo das artes da Atos no Canva) e prata. Sobre o preto, os traços usam esse azul um pouco mais claro para manter a leitura.
- **Logo:** `assets/logo-atos.png`, tirada do arquivo "ATOS - LOGO - PNG" do Canva na versão de 200 px de largura, que é a que o conector entrega. Serve para o canto do vídeo (178 px). Para usar a logo maior, é preciso o arquivo original.
- **Sem imagens do acampamento:** a primeira versão desta opção usava a roda de adoração em três frases; foi retirada a pedido.
- **Contagem regressiva:** fica na barra de cima, em máquina de escrever. Para tirar, `COUNTDOWN = False`.
- **Textos:** as mesmas correções da opção A; aqui em caixa normal ("Evangelho", "Bíblia", "Palavra de Deus" e "Ele" com maiúscula).

Para gerar: `python3 render_b.py` (aceita `--preview`).

## Ritmo de leitura da opção B (telão)

Pensado para quem está sentado longe da tela:

- **A frase entra como alguém lendo em voz alta:** 2,5 palavras por segundo, com um respiro depois de vírgula (0,3 s) e de ponto (0,6 s). Antes, as linhas entravam com pausas longas entre elas.
- **Depois fica inteira na tela** até o corte, por pelo menos 5 segundos.
- **Letra maior:** de 84–112 px para 106–124 px, com linhas mais curtas.
- **A frase mais longa (3) vai em duas telas**, com troca suave, para não diminuir a letra.

| Frase | Entra | Completa em | Fica inteira | Letra |
|---|---|---|---|---|
| 1 · Ravenhill | 0:00 | 6,6 s | 8,8 s | 124 px |
| 2 · Piper | 0:16 | 9,0 s | 9,9 s | 106 px |
| 3 · Piper (tela 1) | 0:35 | 4,6 s | 5,4 s | 124 px |
| 3 · Piper (tela 2) | 0:45 | 6,2 s | 5,4 s | 124 px |
| 4 · Graham | 0:56 | 6,8 s | 10,1 s | 110 px |
| 5 · Ravenhill | 1:13 | 4,2 s | 7,3 s | 120 px |
| 6 · Wilkerson | 1:25 | 6,2 s | 6,8 s | 124 px |
| 7 · Wilkerson | 1:38 | 8,2 s | 7,7 s | 106 px |
| 8 · Tozer | 1:54 | 5,1 s | 7,2 s | 124 px |
| Cartela final | 2:06 | | até 2:11 | |

Os tempos saem de um cálculo, não de números digitados: para deixar a leitura mais lenta ou mais rápida, mude `RATE` em `render_b.py`.

## Tempos da opção A

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
3. Para gerar o vídeo final: `python3 render.py` (cerca de 10 minutos em 4 núcleos, contando a compressão final).

Requisitos: Python 3.11+, Pillow, numpy, scipy, ffmpeg com libx264 e Inter Display em `/usr/share/fonts/opentype/inter`.
