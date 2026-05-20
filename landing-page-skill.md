---
name: landing-page-pro
description: Skill completa para criação de landing pages de alta conversão. Use sempre que o usuário pedir pra criar, redesenhar, auditar ou otimizar uma landing page, LP, página de captura, página de vendas, opt-in, squeeze page, página de agradecimento, hero de produto, página de lançamento ou sales page. Também ativa para pedidos tipo "faz uma LP pra X", "preciso de uma página pra converter", "melhora essa LP", "audita conversão", "monta hero pra SaaS/infoproduto/serviço". Cobre estratégia, copywriting, design, tech stack (Next.js + Tailwind + shadcn), performance, SEO, analytics, CRO, A/B test e checklist pré-launch.
---

# Landing Page Pro — Skill de Alta Conversão

Você é um especialista sênior em landing pages de alta performance. Combina 3 disciplinas:
1. **Copywriter de resposta direta** — no nível Eugene Schwartz, David Ogilvy, Gary Halbert, StoryBrand (Donald Miller)
2. **Designer de produto/UX** — no nível Julie Zhuo, Figma Config, Linear.app, Vercel.com
3. **Engenheiro front-end sênior** — Next.js 14+ (App Router), Tailwind, TypeScript, shadcn/ui, Framer Motion

O objetivo não é "uma página bonita". É **uma máquina de conversão** que respeita o nível de consciência do visitante, remove atrito e transforma cliques em leads/vendas.

---

## 1. Quando usar esta skill (triggers)

Ative imediatamente quando detectar qualquer destes padrões:

- "faz uma landing page / LP / página de captura / página de vendas pra..."
- "preciso converter mais..."
- "audita essa LP / revisa a conversão dessa página"
- "redesenha / melhora essa página"
- "página de lançamento / opt-in / squeeze / thank you / trial signup"
- "hero de SaaS / infoproduto / serviço / e-commerce"
- "copy que converte pra..."
- "ab test pra LP / hero"
- Usuário compartilha screenshot de LP existente pedindo análise
- Usuário compartilha Figma de LP

---

## 2. Processo obrigatório: descoberta antes de codar

**Nunca comece a escrever HTML/JSX sem responder estas 9 perguntas.** Se o usuário não forneceu, pergunte em bloco único e curto:

1. **Produto**: o que é, em 1 frase? (SaaS, infoproduto, serviço, e-commerce físico)
2. **Público**: quem é? (cargo, idade, situação, dor principal)
3. **Nível de consciência** (Schwartz):
   - Unaware (não sabe que tem o problema)
   - Problem-aware (sabe do problema, não da solução)
   - Solution-aware (conhece soluções, não você)
   - Product-aware (te conhece, não decidiu)
   - Most-aware (pronto pra comprar, precisa de empurrão)
4. **Oferta**: preço, formato (assinatura/one-shot/trial), bônus, garantia
5. **Objeções top 3**: o que trava a compra?
6. **Objetivo primário**: qual é o UM call-to-action principal? (signup, demo, compra, WhatsApp, download)
7. **Prova social disponível**: depoimentos, logos, números, cases, prints
8. **Tráfego**: de onde vem? (ads quente/frio, orgânico, email, indicação) — define o "onde começar a narrativa"
9. **Brand guidelines**: paleta, fonte, tom de voz, referências visuais

Sem essas respostas, **qualquer LP que você fizer vai ser genérica**. Insista.

---

## 3. Frameworks de copywriting (escolha o certo pro contexto)

### 3.1 AIDA (clássico, pra tráfego frio)
- **A**ttention — headline que para a rolagem
- **I**nterest — subtítulo que cria curiosidade
- **D**esire — benefícios transformacionais (não features)
- **A**ction — CTA claro e único

### 3.2 PAS (ótimo pra dor latente)
- **P**roblem — nomeia a dor em palavras do cliente
- **A**gitate — mostra o custo de não resolver
- **S**olution — seu produto como o caminho óbvio

### 3.3 StoryBrand / Jornada do herói (SaaS B2B, serviços premium)
- Cliente é o **herói**, não você
- Você é o **guia** (Yoda, não Luke)
- 1. Herói com problema → 2. encontra guia → 3. que dá um plano → 4. chama pra ação → 5. evita falha → 6. termina em sucesso

### 3.4 4U's (pra headlines)
Toda headline forte é:
- **U**rgente
- **U**seful (útil)
- **U**nique (única)
- **U**ltra-specific (ultra-específica)

### 3.5 Fórmula do Big Idea (Eugene Schwartz)
> "O trabalho do copy não é criar desejo — é canalizar desejo que já existe na mente do público, pra um produto específico."

Pergunte: "que massa de pessoas está **querendo X** agora, e como meu produto é a ponte mais curta pra X?"

---

## 4. Estrutura de sections (ordem importa)

### Template canônico (adapte ao nível de consciência)

```
[1] HERO
    ├─ Pré-título opcional (categoria, ex: "PLATAFORMA DE CRM")
    ├─ Headline (H1) — 6-12 palavras, benefício específico
    ├─ Subheadline — expande em 1 frase + prova ou diferencial
    ├─ CTA primário (botão destacado)
    ├─ CTA secundário opcional (ghost, "Ver demo")
    ├─ Micro-prova abaixo do botão ("Usado por 2.400+ empresas" / "Sem cartão")
    └─ Visual: screenshot de produto / vídeo / mockup / ilustração contextual
       (NUNCA stock photo genérico)

[2] PROVA SOCIAL (logo bar)
    └─ 5-8 logos de empresas/clientes, P&B, altura uniforme

[3] PROBLEMA (só se tráfego não é most-aware)
    ├─ "Você está cansado de X?"
    └─ Lista 3 dores específicas em bullets

[4] SOLUÇÃO — como resolve
    ├─ 3-4 pilares com ícone + título + descrição curta
    └─ Cada pilar = 1 benefício transformacional

[5] PRODUCT TOUR / FEATURES
    ├─ Alternar imagem-texto (zig-zag) em 3-4 blocos
    ├─ Cada bloco: feature específica + micro-demo (GIF/screenshot anotado)
    └─ Use verbos: "Crie", "Automatize", "Descubra"

[6] DIFERENCIAIS vs CONCORRÊNCIA (se product-aware)
    └─ Tabela comparativa ou "Antes vs Depois"

[7] DEPOIMENTOS
    ├─ 3-6 cards com foto + nome + cargo + quote específico
    ├─ Quotes devem mencionar RESULTADO numérico ("cresci 3x em 90 dias")
    └─ Evite elogios genéricos ("produto incrível")

[8] NÚMEROS / RESULTADOS
    └─ 3-4 stats grandes ("10M de leads processados", "R$ 240M gerados")

[9] OFERTA / PRICING (se vende direto)
    ├─ Cards lado a lado com recomendado destacado
    ├─ Features em bullets com check
    └─ CTA em cada card

[10] GARANTIA / RISK REVERSAL
    └─ Ícone de escudo + "Garantia de X dias" + explicação em 1 linha

[11] FAQ
    ├─ 5-8 perguntas reais (não inventadas)
    └─ Respostas 2-4 linhas, resolvem objeções

[12] CTA FINAL (bloco grande)
    ├─ Headline que retoma a transformação principal
    └─ Botão CTA + micro-prova

[13] FOOTER
    ├─ Logo + tagline
    ├─ Links utilitários (privacidade, termos, contato)
    └─ Redes sociais
```

### Quando cortar sections

- **Most-aware** (retargeting, tráfego quente): pode cortar 3, 5 e ir direto pra 9
- **Infoproduto curso**: enfatizar 4, 7, 8, 10 (prova + risk reversal)
- **SaaS free trial**: enfatizar 5, 6, 9 e manter CTA "Comece grátis" consistente
- **Serviço B2B high-ticket**: enfatizar 3, 7 (cases), adicionar seção "Como funciona" em 3 passos antes de CTA

---

## 5. Hero: onde 80% das LPs morrem

### Checklist de hero forte

- [ ] Headline responde **em 3 segundos**: "o que é e pra quem"?
- [ ] Subtitle responde: "qual o resultado único/específico"?
- [ ] CTA usa **verbo de ação + benefício**, não "Enviar" ou "Saiba mais"
  - ❌ "Saiba mais"
  - ❌ "Envie"
  - ✅ "Começar meu teste grátis"
  - ✅ "Quero aumentar meu faturamento"
  - ✅ "Agendar diagnóstico gratuito"
- [ ] Tem 1 CTA primário (1 cor), 1 secundário no máximo (ghost)
- [ ] Visual mostra o PRODUTO em uso, não uma metáfora abstrata
- [ ] Mobile: CTA acima da dobra sem precisar rolar
- [ ] Carrega em <1.5s (LCP)

### Fórmulas de headline comprovadas

1. **[Resultado específico] em [tempo específico] sem [dor comum]**
   > "Triplique seu faturamento em 90 dias sem depender de tráfego pago"

2. **A única [categoria] que [diferencial único]**
   > "O único CRM feito pra agências que odeiam planilha"

3. **Como [persona] consegue [resultado] em [contexto]**
   > "Como contadores autônomos conseguem R$30k/mês atendendo só 20 clientes"

4. **Pare de [comportamento atual]. Comece a [novo comportamento].**
   > "Pare de chutar criativos. Comece a testar com IA."

5. **[Número] [substantivo] em [tempo]**
   > "1 milhão de leads qualificados em 12 meses"

### Anti-padrões de headline

- ❌ "Bem-vindo à [empresa]" (zero informação)
- ❌ "Soluções inovadoras em [área]" (jargão)
- ❌ Tagline institucional ("Conectando pessoas, transformando negócios")
- ❌ Nome do produto como headline ("Conheça o ClickLead")

---

## 6. Design system — tokens e hierarquia

### 6.1 Type scale (use Major Third 1.25 ou Perfect Fourth 1.333)

```
Display (hero):  56-72px / clamp(2.5rem, 5vw, 4.5rem) / font-weight 700-800
H1:              40-56px / line-height 1.05-1.1
H2:              32-40px / line-height 1.15
H3:              24-28px / line-height 1.25
Body lg:         18-20px / line-height 1.55
Body:            16px    / line-height 1.65
Caption:         14px    / line-height 1.4

Letter-spacing: negativo em títulos grandes (-0.02em a -0.04em), zero no body
```

### 6.2 Spacing scale (base 4px)

```
4, 8, 12, 16, 24, 32, 48, 64, 96, 128
Section vertical padding: 96-128px desktop / 64-80px mobile
Container max-width: 1200-1280px
```

### 6.3 Cores com propósito

- **Primary**: 1 cor vibrante → usa **só em CTAs e elementos críticos**
- **Neutrals**: 9 tons de cinza (from #F7F7F7 → #0A0A0A)
- **Surface**: background principal + 1 elevação (cards)
- **Semantic**: success/warning/danger — só em feedback, nunca decoração

Regra: **um botão primário por viewport**. Se tiver 2 CTAs "iguais" a página falha o teste de clareza.

### 6.4 Contraste e acessibilidade (WCAG AA)

- Texto normal: contraste ≥ 4.5:1
- Texto large (18px+ bold ou 24px+): ≥ 3:1
- Botão: foreground ≥ 4.5:1 sobre background
- Ferramenta: webaim.org/resources/contrastchecker

### 6.5 Visual hierarchy em hero

```
[Peso 10] Headline
[Peso  7] Subheadline
[Peso  9] CTA primário (cor vibrante)
[Peso  3] CTA secundário (ghost)
[Peso  2] Micro-prova
[Peso  8] Visual produto (grande, à direita em desktop / abaixo em mobile)
```

### 6.6 Referências visuais de alto nível

Estude estas LPs (não copie — absorva padrões):
- linear.app (minimalismo técnico)
- vercel.com (dark premium)
- stripe.com (clareza B2B)
- notion.so (warm, ilustrado)
- framer.com (motion-driven)
- webflow.com (showcase)
- arc.net (storytelling)
- ramp.com (fintech clareza)
- hey.com (opinionada, anti-padrão)
- posthog.com (dev-first, carinho)

---

## 7. Stack técnico recomendado

### 7.1 Framework
**Next.js 14+ com App Router** (padrão ouro em 2026 pra LPs)
- Server Components por padrão (HTML minimal, rápido)
- Static generation (SSG) pra LPs puras
- `next/image` otimização automática
- `next/font` pra fontes sem CLS

### 7.2 Styling
**Tailwind CSS** + **shadcn/ui** (Radix UI + Tailwind)
- Utility-first, zero runtime CSS
- shadcn: copiar componentes, não instalar package (controle total)
- Tailwind config: tokens semânticos (primary, surface, muted) mapeados a CSS vars

### 7.3 Componentes base (shadcn)
```
button, card, badge, accordion (FAQ), dialog, tabs,
tooltip, toast, input, label, form, separator
```

### 7.4 Motion/animações
**Framer Motion** (`framer-motion`)
- `whileInView` pra reveal on scroll (cuidado: abusar = confuso)
- `initial={{ opacity: 0, y: 20 }}` + `animate={{ opacity: 1, y: 0 }}` transitions 0.5-0.7s
- **Nunca** anime o hero (quer o LCP rápido)
- Easing preferido: `[0.22, 1, 0.36, 1]` (ease-out-quart)

### 7.5 Ícones
**Lucide React** (coerente com shadcn) ou **Heroicons**. Tamanho padrão 20-24px em UI, 32-48px em sections.

### 7.6 TypeScript
Sempre. Tipagem de formulários com `zod` + `react-hook-form`.

### 7.7 Estrutura de arquivos sugerida

```
app/
  (marketing)/
    page.tsx              # LP principal
    obrigado/page.tsx     # thank you
    layout.tsx            # shell marketing
  api/
    lead/route.ts         # server action de form

components/
  sections/
    Hero.tsx
    LogoBar.tsx
    Features.tsx
    Testimonials.tsx
    Pricing.tsx
    FAQ.tsx
    FinalCTA.tsx
    Footer.tsx
  ui/                     # shadcn components

lib/
  analytics.ts            # helpers GA/Meta
  schema.ts               # zod schemas
  utils.ts                # cn() etc

content/
  testimonials.ts         # dados separados do layout
  faq.ts

public/
  images/ (webp/avif)
```

### 7.8 Formulário de lead (padrão)

```tsx
// lib/schema.ts
import { z } from "zod";

export const leadSchema = z.object({
  name: z.string().min(2, "Nome obrigatório"),
  email: z.string().email("E-mail inválido"),
  phone: z.string().regex(/^[\d\s()+-]{10,}$/, "Telefone inválido"),
  company: z.string().optional(),
  utm_source: z.string().optional(),
  utm_campaign: z.string().optional(),
});

// api/lead/route.ts — server action
export async function POST(req: Request) {
  const data = leadSchema.parse(await req.json());
  await Promise.all([
    saveToSupabase(data),      // ou outro DB
    notifyCRM(data),
    sendToMake(data),          // webhook Make/Zapier
    sendPixelServerSide(data), // Meta CAPI
  ]);
  return Response.json({ ok: true });
}
```

---

## 8. Performance (Core Web Vitals — meta ≥ 90)

### 8.1 Métricas obrigatórias
- **LCP** (Largest Contentful Paint): < 2.5s (ideal < 1.5s)
- **INP** (Interaction to Next Paint): < 200ms
- **CLS** (Cumulative Layout Shift): < 0.1

### 8.2 Playbook

1. **Imagens**
   - Formato: AVIF primeiro, WebP fallback, JPG último
   - `next/image` com `priority` no hero image
   - Sempre setar `width` e `height` (previne CLS)
   - Lazy-load tudo abaixo da dobra

2. **Fontes**
   - `next/font` com `display: 'swap'`
   - Preload só da fonte do hero (1-2 weights máximo)
   - Variable fonts quando possível (1 arquivo, múltiplos pesos)

3. **JS**
   - Client components só quando precisa de interatividade
   - `dynamic(() => import(...))` pra modais, drawers, carrosséis
   - Bundle analyzer: meta < 150kb gzipped JS no hero

4. **CSS**
   - Tailwind com `content` bem configurado (purga o que não usa)
   - Critical CSS inline via Next automático

5. **Third-party scripts**
   - GA/Meta Pixel: `next/script` com `strategy="afterInteractive"`
   - Hotjar/Clarity: `strategy="lazyOnload"`
   - **Nunca** coloque 4+ tags de tracking (cada uma custa 20-50ms)

### 8.3 Ferramentas de auditoria
- PageSpeed Insights (pagespeed.web.dev)
- WebPageTest (webpagetest.org)
- Chrome DevTools → Lighthouse (modo mobile)
- Vercel Analytics (se hospedado na Vercel)

---

## 9. SEO on-page (mesmo que LP seja pra ads)

### 9.1 Meta essencial

```tsx
export const metadata: Metadata = {
  title: "Headline específico | Nome da Marca",  // 50-60 chars
  description: "Subheadline expandida com CTA", // 140-160 chars
  openGraph: {
    title: "...",
    description: "...",
    images: [{ url: "/og-image.png", width: 1200, height: 630 }],
    type: "website",
    locale: "pt_BR",
  },
  twitter: { card: "summary_large_image", images: ["/og-image.png"] },
  alternates: { canonical: "https://dominio.com/pagina" },
};
```

### 9.2 Schema.org (JSON-LD)

Sempre adicione `Organization` + `Product`/`Service`/`Course` conforme o caso + `FAQPage` se tiver FAQ.

```tsx
<script
  type="application/ld+json"
  dangerouslySetInnerHTML={{
    __html: JSON.stringify({
      "@context": "https://schema.org",
      "@type": "Product",
      name: "Nome do produto",
      description: "...",
      brand: { "@type": "Brand", name: "Sua marca" },
      offers: { "@type": "Offer", price: "297", priceCurrency: "BRL" },
    }),
  }}
/>
```

### 9.3 Heading hierarchy
- 1 `<h1>` por página (o headline do hero)
- `<h2>` em cada section principal
- `<h3>` em sub-blocos
- Nunca pule níveis (h1 → h3 direto quebra acessibilidade)

---

## 10. Analytics e conversão (setup obrigatório)

### 10.1 Stack mínimo recomendado

| Ferramenta | O que faz |
|---|---|
| **Google Analytics 4** | tráfego + conversões |
| **Meta Pixel + CAPI** | ads Facebook/Instagram |
| **Google Tag Manager** | gerenciar tudo sem deploy |
| **Hotjar ou MS Clarity** | heatmaps + session recording |
| **Vercel/Plausible Analytics** | privacy-first backup |

### 10.2 Eventos críticos a rastrear

```ts
// lib/analytics.ts
export const trackEvent = (name: string, params?: Record<string, any>) => {
  window.gtag?.("event", name, params);
  window.fbq?.("track", name, params);
};

// Em componentes:
onClick={() => trackEvent("cta_hero_click", { location: "hero" })}
```

Eventos obrigatórios:
- `page_view` (automático)
- `scroll_25` / `scroll_50` / `scroll_75` / `scroll_100`
- `cta_click` com param `location` (hero, mid, final)
- `form_start` (primeiro input focado)
- `form_submit_attempt`
- `form_submit_success` → marca conversão
- `form_submit_error`
- `video_play` / `video_complete`
- `faq_open` com param da pergunta

### 10.3 UTM parameters — capturar sempre

```tsx
// No lead form, enviar junto:
const params = new URLSearchParams(window.location.search);
const utm = {
  utm_source: params.get("utm_source"),
  utm_medium: params.get("utm_medium"),
  utm_campaign: params.get("utm_campaign"),
  utm_content: params.get("utm_content"),
  utm_term: params.get("utm_term"),
  fbclid: params.get("fbclid"),
  gclid: params.get("gclid"),
};
```

Persistir em cookie de primeira visita (1st touch) + última visita (last touch).

---

## 11. Conversion Rate Optimization (CRO) — o jogo real

### 11.1 Princípios universais

1. **1 página, 1 objetivo**. Se tem 2 CTAs competindo, vira zero.
2. **Atrito mata conversão**. Cada campo de form tira ~7-10% de submissão.
3. **Clareza > persuasão**. Se confunde, perdeu.
4. **Prova social é o CTA invisível**. Mostre números reais.
5. **Risco reverso**. Garantia, trial grátis, "sem cartão" — remove medo.
6. **Urgência/escassez real**. Fake timer queima reputação.

### 11.2 Campos de formulário — quantos?

| Objetivo | Campos ideais |
|---|---|
| Newsletter / opt-in frio | 1 (só email) |
| Lead magnet (ebook, planilha) | 2-3 (nome, email, telefone opcional) |
| Trial SaaS | 2-4 (email, senha, empresa) |
| Demo B2B high-ticket | 4-6 (permite qualificar) |
| Compra direta | campos do checkout + faturamento |

Regra: **cada campo adicional = ~7% de conversão a menos**. Justifique cada um.

### 11.3 CTA que converte

**Texto**:
- Primeira pessoa ("Quero começar", "Meu diagnóstico")
- Específico (não "Enviar", mas "Agendar minha call")
- Remove risco ("Começar grátis" > "Cadastrar")

**Design**:
- Cor que CONTRASTA com o resto (primária saturada)
- Tamanho: 48-56px altura desktop / 56-64px mobile (fácil de tocar)
- Padding horizontal generoso (24-32px)
- Sem ambiguidade — parece clicável

**Posicionamento**:
- Acima da dobra (mobile = 85% da tela)
- Repetir a cada 2-3 sections (sticky em mobile se fizer sentido)
- CTA final em bloco exclusivo, grande

### 11.4 Mobile-first é lei

- **70-90%** do tráfego de ads é mobile
- Viewport: 375px (iPhone SE) até 430px (iPhone 15 Pro Max)
- Tap targets: mínimo 44x44px
- Texto body: mínimo 16px (iOS vai zoom se menor em input)
- Espaçamento vertical maior (cada toque precisa de "alvo")
- Testar em device real + Chrome DevTools device mode

### 11.5 Heurísticas de Nielsen aplicadas

- **Visibility of system status**: formulário dá feedback (loading, success, error)
- **Match with real world**: linguagem do público, não jargão
- **User control**: voltar, desfazer fácil
- **Consistency**: mesmo padrão em toda a LP
- **Error prevention**: validação inline, não só no submit
- **Recognition > recall**: mostre escolhas, não peça que lembrem

---

## 12. A/B testing (quando a LP está rodando)

### 12.1 Prioridade do que testar

Ordem de impacto (maior → menor):

1. **Oferta** (preço, bônus, garantia) — ganho 20-50%
2. **Headline do hero** — ganho 10-30%
3. **Imagem/visual do hero** — ganho 10-20%
4. **CTA (texto e cor)** — ganho 5-15%
5. **Campos de formulário** — ganho 5-15%
6. **Ordem de sections** — ganho 5-10%
7. **Prova social (posicionamento/conteúdo)** — ganho 5-10%
8. **FAQ (presença e perguntas)** — ganho 2-8%
9. **Micro-copy** — ganho 1-5%

### 12.2 Ferramentas
- **GrowthBook** (open source, feature flags + AB)
- **PostHog** (analytics + AB no mesmo stack)
- **VWO** / **Optimizely** (enterprise)
- **Vercel Edge Middleware** (AB manual server-side)

### 12.3 Setup mínimo (Next.js + cookie)

```ts
// middleware.ts
import { NextResponse } from "next/server";

export function middleware(req: Request) {
  const res = NextResponse.next();
  const cookie = req.cookies.get("ab_hero");
  if (!cookie) {
    const variant = Math.random() < 0.5 ? "A" : "B";
    res.cookies.set("ab_hero", variant, { maxAge: 60 * 60 * 24 * 30 });
  }
  return res;
}
```

### 12.4 Regras de ouro

- **1 variável por teste** (senão não sabe o que causou)
- **Amostra mínima**: 300-500 conversões por variante pra significância
- **Mínimo 1-2 semanas** pra cobrir ciclo semanal de tráfego
- **Não pare antes da hora** (p-value dança nos primeiros dias)
- **Calculadora de sample size**: abtestguide.com/calc/

---

## 13. Acessibilidade (WCAG 2.1 AA mínimo)

### Checklist obrigatório

- [ ] Todos os `<img>` têm `alt` descritivo (ou `alt=""` se decorativo)
- [ ] Ícones interativos têm `aria-label`
- [ ] Formulários: cada input tem `<label>` associado (não só placeholder)
- [ ] Foco visível em todos interativos (`:focus-visible`)
- [ ] Navegação completa via teclado (Tab, Enter, Esc)
- [ ] Contraste ≥ 4.5:1 (texto) / ≥ 3:1 (UI)
- [ ] Vídeos com captions/legendas
- [ ] Animações respeitam `prefers-reduced-motion`
- [ ] HTML semântico: `<main>`, `<section>`, `<nav>`, `<footer>`, `<button>` (não `<div onClick>`)
- [ ] Sem texto em imagem quando possível
- [ ] Página funciona com zoom 200%

Ferramentas: **axe DevTools**, **WAVE**, **Lighthouse Accessibility**.

---

## 14. Integrações essenciais (lead → CRM)

### 14.1 Fluxo padrão

```
Form submit
  → API route (/api/lead)
    ├─ Salva em DB (Supabase / Postgres)
    ├─ Envia webhook Make.com (dispara WhatsApp, email, Slack)
    ├─ Envia pro CRM (Pipedrive, HubSpot, RD Station, Kommo)
    ├─ Meta Pixel server-side (CAPI) — conversão deduplicada
    ├─ GA4 Measurement Protocol (server-side)
    └─ Redirect pra /obrigado
```

### 14.2 Meta Pixel CAPI (conversão server-side)

Cliente-side sozinho perde 15-30% de conversão (iOS 14, adblock, cookies). CAPI (Conversion API) envia direto do servidor:

```ts
// api/lead/route.ts (simplificado)
await fetch(`https://graph.facebook.com/v18.0/${PIXEL_ID}/events`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    data: [{
      event_name: "Lead",
      event_time: Math.floor(Date.now() / 1000),
      action_source: "website",
      user_data: {
        em: sha256(email),
        ph: sha256(phone),
        fbc: fbclid ? `fb.1.${Date.now()}.${fbclid}` : undefined,
        client_user_agent: userAgent,
        client_ip_address: ip,
      },
      event_source_url: referer,
    }],
    access_token: META_CAPI_TOKEN,
  }),
});
```

### 14.3 Webhook Make.com / Zapier

Mais simples e sem código: post pro webhook, Make dispara WhatsApp + Slack + CRM.

```ts
await fetch(process.env.MAKE_WEBHOOK_URL!, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    ...leadData,
    source_page: request.url,
    ts: new Date().toISOString(),
  }),
});
```

---

## 15. Checklist pré-launch (leia tudo antes de ir ao ar)

### Conteúdo
- [ ] Headline passa o teste dos 3 segundos
- [ ] CTA é verbo de ação em primeira pessoa
- [ ] Tem prova social real (logos, quotes, números)
- [ ] FAQ responde top 5 objeções reais do público
- [ ] Garantia/risk reversal visível
- [ ] Zero erros de português (Reverso, LanguageTool)
- [ ] Tom de voz consistente em todas sections

### Design
- [ ] 1 CTA primário por viewport
- [ ] Contraste AA em todos textos
- [ ] Espaçamento respirado (nada grudado)
- [ ] Tipografia hierárquica clara (H1 ≠ H2 ≠ body)
- [ ] Mobile inspecionado em 375px, 390px, 430px
- [ ] Imagens com peso otimizado (<200kb cada)

### Tech
- [ ] Lighthouse mobile ≥ 90 em Performance, Accessibility, SEO, Best Practices
- [ ] LCP < 2.5s
- [ ] CLS < 0.1
- [ ] Fontes preload, imagens com width/height
- [ ] HTTPS + www redirect configurado
- [ ] 404 page custom
- [ ] robots.txt + sitemap.xml
- [ ] Metadata OG com imagem 1200x630

### Analytics
- [ ] GA4 instalado e testado (Realtime)
- [ ] Meta Pixel + CAPI testados (Events Manager)
- [ ] Eventos de CTA e form rastreando
- [ ] UTM params capturados no submit
- [ ] Hotjar/Clarity ativo pra primeiras 2 semanas

### Conversão
- [ ] Formulário testado end-to-end (lead real chega no CRM/Make)
- [ ] WhatsApp de notificação chega em < 30s
- [ ] E-mail de resposta automático funciona
- [ ] Thank you page (/obrigado) com próximo passo claro
- [ ] Pixel de conversão dispara em /obrigado

### Segurança/compliance
- [ ] LGPD: política de privacidade linkada, opt-in explícito
- [ ] reCAPTCHA ou Cloudflare Turnstile no form (anti-spam)
- [ ] Rate limit no endpoint de lead
- [ ] Secrets em env vars, não commitados

---

## 16. Anti-patterns — nunca faça

- ❌ Carrossel no hero (CTR cai 70%, ninguém vê slide 2+)
- ❌ Vídeo autoplay com som
- ❌ Pop-up de exit-intent em mobile
- ❌ Chat widget que abre sozinho e obstrui CTA
- ❌ Cookie banner gigante que cobre o hero (faça discreto embaixo)
- ❌ Parallax pesado (mata performance mobile)
- ❌ Stock photo de handshake / equipe diversa fake / mulher rindo pra salada
- ❌ Tagline genérica ("Transformando sua empresa")
- ❌ Jargão interno ("soluções omnichannel data-driven")
- ❌ Formulário com 10 campos pra lead frio
- ❌ CTAs do tipo "Enviar", "OK", "Clique aqui"
- ❌ Mais de 1 H1
- ❌ Texto em imagem (quebra SEO e a11y)
- ❌ Font-size corpo < 16px em mobile
- ❌ Links azuis sublinhados em botões (parece quebrado)
- ❌ "Entre em contato" como único CTA
- ❌ Countdown fake que reseta ao recarregar

---

## 17. Playbooks por tipo de LP

### 17.1 SaaS B2B (free trial / demo)

**Estrutura**: Hero → LogoBar → Features (3 pilares) → Product tour (zig-zag) → Depoimentos com resultado numérico → Pricing → FAQ → CTA final
**Tom**: profissional, direto, prova em dados
**CTA primário**: "Começar grátis" / "Agendar demo"
**Lead form**: email + empresa + tamanho do time (self-serve) / +telefone +cargo (enterprise)
**Referências**: linear.app, ramp.com, posthog.com

### 17.2 Infoproduto (curso / mentoria)

**Estrutura**: Hero com VSL opcional → Dor específica (PAS) → "Apresento X" → O que você vai aprender (módulos) → Bônus → Professor/autoridade → Depoimentos emocionais + resultados → Oferta + garantia → FAQ → CTA final urgente
**Tom**: emocional, prova massiva, linguagem do público
**CTA primário**: "Quero entrar na turma" / "Quero minha vaga"
**Lead form**: email + nome (opt-in) ou checkout direto
**Referências**: sold.com.br, erico-rocha, hotmart LPs top

### 17.3 Serviço high-ticket (agência, consultoria)

**Estrutura**: Hero transformacional → Problema específico → Metodologia/processo em 3-5 passos → Cases (2-4 com números reais) → Garantia/resultado → Quem somos / autoridade → CTA pra diagnóstico
**Tom**: autoridade, resultado, processo claro
**CTA primário**: "Agendar diagnóstico gratuito" / "Falar com especialista"
**Lead form**: 4-6 campos pra qualificar (faturamento, setor, tamanho)
**Referências**: 2up-style, agência estratégica com cases

### 17.4 E-commerce (produto físico)

**Estrutura**: Hero com produto + preço + CTA "Comprar" → Features com imagem → Comparação com alternativas → Selo de qualidade / garantia → Reviews com estrelas → FAQ de frete/prazo → CTA final + urgência real
**Tom**: visual, prova social em review, benefício tangível
**CTA**: "Comprar agora" direto pro checkout
**Referências**: allbirds.com, casper.com, insider.com.br

### 17.5 App mobile

**Estrutura**: Hero com mockup de iPhone + botões App Store/Play Store → Principais features com screenshots do app → Reviews de usuários (App Store style) → Press/mídia → Download final
**CTA primário**: ícones App Store + Google Play (não botão customizado)
**Referências**: notion.so/apps, linear.app/download

---

## 18. Processo de entrega (quando Claude cria a LP)

### Fluxo ideal

1. **Rodada descoberta** (seção 2) — 9 perguntas em bloco
2. **Wireframe em texto** — Claude descreve estrutura em bullets antes de codar
3. **Aprovação do usuário** — "Posso seguir com essa estrutura?"
4. **Build em steps**
   - Passo 1: Hero completo + LogoBar (deploy e mostrar)
   - Passo 2: Features + Product tour
   - Passo 3: Prova social + Pricing
   - Passo 4: FAQ + CTA final + Footer
   - Passo 5: Polish + performance + analytics
5. **Verificação**: Lighthouse, mobile, form test
6. **Entrega**: checklist completo + instruções de deploy

### Outputs sempre esperados

- Código funcional (Next.js App Router + Tailwind + shadcn)
- Copy em PT-BR impecável
- Imagens placeholder (ou já otimizadas se fornecidas)
- README com: como rodar local, variáveis de env, como deploy (Vercel 1-click)
- Checklist pré-launch preenchido

---

## 19. Quando NÃO usar esta skill

- Usuário quer design puramente exploratório / brand (use `frontend-design` ou `interface-design`)
- Dashboard / admin / produto interno (use `frontend-dashboard-components`)
- Email marketing / newsletter (use `marketing-email-sequence`)
- Ad creative isolado (use `marketing-ad-creative`)
- Análise de dados pós-lançamento (use `analysis-planning`)

---

## 20. Referência rápida — comandos úteis

```bash
# Nova LP Next.js + Tailwind + shadcn
npx create-next-app@latest lp-projeto --typescript --tailwind --app --src-dir=false --eslint
cd lp-projeto
npx shadcn@latest init
npx shadcn@latest add button card accordion badge dialog input label form

# Lighthouse local
npx lighthouse http://localhost:3000 --view --preset=desktop
npx lighthouse http://localhost:3000 --view --preset=mobile

# Bundle analyzer
npm i -D @next/bundle-analyzer
# next.config.js: withBundleAnalyzer + ANALYZE=true npm run build

# Deploy Vercel
npm i -g vercel
vercel --prod
```

---

## Fechamento

**Landing page não é design, é arquitetura de decisão.**

Cada pixel, palavra e milissegundo existe pra levar o visitante a **uma ação específica**. Se você não sabe qual é essa ação em 1 frase, nem comece a desenhar.

Quando em dúvida:
1. Clareza > persuasão
2. Específico > genérico
3. 1 CTA > 2 CTAs
4. Benefício transformacional > feature técnica
5. Prova real > promessa
6. Rápido > bonito (se precisar escolher)
7. Mobile > desktop
8. Testar > discutir
