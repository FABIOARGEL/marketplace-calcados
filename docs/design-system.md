# Design System — Marketplace de Calçados
**Versão:** 1.0 | **Status:** Ativo | **Data:** Setembro/2026

---

## Objetivo deste documento

Este documento é a **referência oficial de design e padrões visuais** do Marketplace de Calçados, desenvolvido como projeto acadêmico de Engenharia/Sistemas de Informação. Ele funciona como um **Design System + Guia de Padrões do Projeto**, e deve ser consultado por todos os membros da equipe antes de criar qualquer tela, componente ou elemento visual.

**Qualquer decisão de design não documentada aqui deve ser discutida com a equipe e incorporada ao documento antes de ser implementada.**

---

## Contexto do projeto

O sistema é um **marketplace de calçados** no qual:

- **Compradores** podem visualizar, pesquisar, filtrar e comprar produtos.
- **Vendedores** podem cadastrar, editar e administrar seus próprios calçados.

**Stack tecnológica:**

| Camada | Tecnologia |
|---|---|
| Backend | Python + Django |
| Banco de dados | PostgreSQL |
| Frontend | HTML + CSS + JavaScript |
| Templates | Django Templates |
| Versionamento | Git / GitHub |

Como diferentes membros da equipe trabalharão em partes distintas do sistema, as regras deste documento devem ser seguidas rigorosamente para evitar inconsistências visuais e estruturais.

---

## Princípios de Design

Antes de implementar qualquer tela, internalize estes cinco princípios:

1. **Consistência acima de criatividade individual** — Sempre reutilize componentes existentes antes de criar novos.
2. **Clareza acima de decoração** — Cada elemento visual deve ter uma função. Nada é decorativo sem propósito.
3. **Contraste como hierarquia** — Use peso visual, tamanho e cor para guiar o olhar do usuário na ordem certa.
4. **Mobile como restrição real** — Toda tela deve funcionar em 375 px de largura sem quebrar.
5. **Feedback sempre presente** — O usuário nunca deve duvidar do que acabou de acontecer.

---

## 1. Direção Visual — Neo-Brutalism + Streetwear + E-commerce Moderno

### 1.1 Conceito

A estética do projeto une três referências:

- **Neo-Brutalismo:** Bordas marcadas, sombras sólidas, contraste alto, sem arredondamento excessivo.
- **Streetwear:** Tipografia marcante, personalidade visual forte, referência ao universo de moda urbana.
- **E-commerce Moderno:** Layout limpo, hierarquia clara, foco no produto, navegação fluida.

O resultado é uma interface que **chama atenção**, mas não compromete a experiência de compra. O neo-brutalismo aqui não significa caos visual — significa **força e personalidade controladas**.

> **Por que Neo-Brutalism?** Calçados, especialmente tênis e produtos streetwear, são associados a cultura urbana, atitude e identidade. Um design com bordas marcadas, sombras sólidas e contraste forte transmite essa personalidade sem parecer genérico como um e-commerce comum.

### 1.2 Características Visuais

| Elemento | Definição |
|---|---|
| **Bordas** | Sólidas, 2px, cor preta (`#0D0D0D`) em todos os componentes interativos |
| **Sombras** | Sólidas (sem blur), deslocadas 3–4px para baixo e para a direita |
| **Cantos** | Sem arredondamento (`border-radius: 0`) como regra padrão. Exceção: badges e tags com `border-radius: 2px` |
| **Espaçamento** | Generoso, com base em múltiplos de 4px. Nunca sufocado |
| **Fundo** | Creme/off-white, nunca branco puro |
| **Contraste** | Alto entre texto e fundo. Cor de destaque aplicada com economia |
| **Imagens** | Tratadas com fundo neutro, enquadramento padronizado |
| **Hover** | Sombra se desloca para baixo e aumenta, dando sensação de profundidade |

### 1.3 Comportamento dos Componentes

- Ao passar o mouse sobre um botão, a sombra se move: o componente "afunda" e depois "levanta".
- Cards têm sombra sólida que aumenta no hover, simulando elevação.
- Inputs ganham borda reforçada (3px) no estado focus.
- Transições são rápidas (150–200ms) para manter a sensação de responsividade.

### 1.4 O que NÃO fazer

- Nunca usar `border-radius` acima de 4px em cards e botões principais.
- Nunca usar sombras com blur excessivo (efeito "nuvem").
- Nunca usar gradientes em áreas de destaque sem aprovação do time.
- Nunca usar mais de 3 cores em uma mesma tela.
- Nunca usar fontes decorativas fora dos títulos principais.

---

## 2. Paleta de Cores

### 2.1 Cores Principais

| Token | Nome | HEX | Finalidade |
|---|---|---|---|
| `--color-bg` | Background | `#F5F0E8` | Fundo padrão de todas as páginas |
| `--color-primary` | Primary | `#0D0D0D` | Texto, bordas, elementos principais |
| `--color-accent` | Accent | `#FF3B00` | Cor de destaque, CTAs, preços em oferta, badges |
| `--color-secondary` | Secondary | `#1A1A1A` | Textos secundários, títulos de cards |
| `--color-border` | Border | `#0D0D0D` | Bordas de todos os componentes |
| `--color-surface` | Surface | `#FFFFFF` | Superfície de cards, modais, inputs |
| `--color-muted` | Muted | `#8C8C8C` | Textos de apoio, placeholders, metadados |

### 2.2 Cores de Estado

| Token | Nome | HEX | Uso |
|---|---|---|---|
| `--color-success` | Success | `#1A8C4E` | Confirmação, estoque disponível, pedido realizado |
| `--color-error` | Error | `#CC2200` | Erros de formulário, falta de estoque |
| `--color-warning` | Warning | `#E8A000` | Alertas, estoque baixo, atenção |
| `--color-info` | Info | `#1A5FA8` | Informações neutras, tooltips |

### 2.3 Descrição Detalhada de Cada Cor

#### `--color-bg` — Background `#F5F0E8`

- **Finalidade:** Fundo base de todas as páginas.
- **Exemplos de uso:** `<body>`, seções de listagem, área de conteúdo.
- **Não usar em:** Texto, bordas, ícones.
- **Motivo:** O creme/off-white dá personalidade sem o cansaço do branco puro e cria contraste natural com a cor primária preta.

#### `--color-primary` — Primary `#0D0D0D`

- **Finalidade:** Textos, bordas, botões primários, ícones.
- **Exemplos de uso:** Títulos H1–H3, bordas de cards, fundo do botão primário, navbar.
- **Não usar em:** Fundo de páginas inteiras, atrás de texto claro em quantidade grande.

#### `--color-accent` — Accent `#FF3B00`

- **Finalidade:** Destaque visual, chamadas para ação, preços promocionais, badges de oferta.
- **Exemplos de uso:** Botão "Comprar Agora", badge "NOVO", preço riscado, links hover.
- **Não usar em:** Textos longos, fundos de páginas, elementos decorativos sem função.
- **Motivo:** O laranja-vermelho vibrante sobre o creme cria o "choque" visual característico do neo-brutalismo, remetendo à energia do streetwear.

#### `--color-surface` — Surface `#FFFFFF`

- **Finalidade:** Superfícies elevadas como cards, modais, inputs.
- **Exemplos de uso:** Product Card, modal de confirmação, campos de formulário.
- **Não usar em:** Fundo principal da página.

#### `--color-muted` — Muted `#8C8C8C`

- **Finalidade:** Informações secundárias sem peso visual.
- **Exemplos de uso:** Placeholder de input, data do pedido, avaliações secundárias.
- **Não usar em:** Informações críticas, erros, preços.

---

## 3. Tipografia

### 3.1 Famílias de Fonte

| Função | Fonte | Justificativa |
|---|---|---|
| **Títulos** | `Space Grotesk` | Fonte geométrica com personalidade marcante, perfeita para o conceito streetwear/neo-brutal |
| **Textos e interface** | `Inter` | Altamente legível em telas, padrão em produtos digitais modernos |

**Importação (no `<head>` do `base.html`):**
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700;800&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
```

### 3.2 Hierarquia Tipográfica

| Elemento | Fonte | Peso | Tamanho | Line-height | Letter-spacing | Caixa |
|---|---|---|---|---|---|---|
| **H1** | Space Grotesk | 800 | 48px | 1.1 | -0.02em | Maiúsculas opcionais |
| **H2** | Space Grotesk | 700 | 36px | 1.2 | -0.01em | Normal |
| **H3** | Space Grotesk | 600 | 28px | 1.3 | 0 | Normal |
| **H4 / Subtítulo** | Space Grotesk | 600 | 20px | 1.4 | 0 | Normal |
| **Texto normal** | Inter | 400 | 16px | 1.6 | 0 | Normal |
| **Texto pequeno** | Inter | 400 | 14px | 1.5 | 0 | Normal |
| **Texto de apoio** | Inter | 400 | 12px | 1.4 | 0.01em | Normal |
| **Preço principal** | Space Grotesk | 700 | 24px | 1 | -0.01em | Normal |
| **Preço promocional** | Space Grotesk | 800 | 28px | 1 | -0.02em | Normal |
| **Preço original** | Inter | 400 | 14px | 1 | 0 | Normal (riscado) |
| **Texto de botão** | Space Grotesk | 700 | 15px | 1 | 0.04em | MAIÚSCULAS |
| **Badge / Etiqueta** | Space Grotesk | 700 | 11px | 1 | 0.06em | MAIÚSCULAS |
| **Erro / Sucesso** | Inter | 500 | 14px | 1.4 | 0 | Normal |
| **Label de input** | Inter | 600 | 13px | 1 | 0.02em | Normal |

### 3.3 Variáveis CSS

```css
:root {
    --font-heading: 'Space Grotesk', sans-serif;
    --font-body: 'Inter', sans-serif;

    --text-xs:   12px;
    --text-sm:   14px;
    --text-base: 16px;
    --text-lg:   20px;
    --text-xl:   28px;
    --text-2xl:  36px;
    --text-3xl:  48px;

    --font-regular:    400;
    --font-medium:     500;
    --font-semibold:   600;
    --font-bold:       700;
    --font-extrabold:  800;
}
```

---

## 4. Sistema de Espaçamento

A escala de espaçamento é baseada em múltiplos de 4px. **Use apenas esses valores.** Nunca use valores arbitrários como `13px` ou `22px`.

| Token | Valor | Quando usar |
|---|---|---|
| `--space-1` | 4px | Espaço mínimo entre ícone e texto, separadores internos finos |
| `--space-2` | 8px | Padding interno de badges, gap entre ícones próximos |
| `--space-3` | 12px | Padding de inputs pequenos, gap entre elementos inline |
| `--space-4` | 16px | Padding padrão de inputs, gap entre itens de lista |
| `--space-5` | 20px | Espaço entre campo e label, gap em forms |
| `--space-6` | 24px | Padding de cards, gap entre cards em grid |
| `--space-8` | 32px | Margem entre seções de um componente |
| `--space-10` | 40px | Padding de seções internas, espaço antes de títulos |
| `--space-12` | 48px | Separação entre blocos maiores de conteúdo |
| `--space-16` | 64px | Separação entre seções da página |
| `--space-24` | 96px | Separação entre seções principais (hero, destaque, footer) |

**Variáveis CSS:**
```css
:root {
    --space-1:  4px;
    --space-2:  8px;
    --space-3:  12px;
    --space-4:  16px;
    --space-5:  20px;
    --space-6:  24px;
    --space-8:  32px;
    --space-10: 40px;
    --space-12: 48px;
    --space-16: 64px;
    --space-24: 96px;
}
```

---

## 5. Sistema de Bordas e Sombras

Este é o elemento mais característico do neo-brutalismo neste projeto.

### 5.1 Bordas

| Token | Valor | Uso |
|---|---|---|
| `--border-width` | 2px | Borda padrão de todos os componentes interativos |
| `--border-width-thick` | 3px | Borda de inputs em estado focus |
| `--border-color` | `#0D0D0D` | Cor única de bordas |
| `--border-radius` | 0px | Padrão de todos os cards e botões |
| `--border-radius-sm` | 2px | Badges, tags, pills |
| `--border-radius-input` | 0px | Inputs e selects |

### 5.2 Sombras

As sombras são **sólidas, sem blur**. Este é o elemento definidor do neo-brutalismo.

| Token | Valor | Uso |
|---|---|---|
| `--shadow-sm` | `2px 2px 0px #0D0D0D` | Badges, elementos pequenos |
| `--shadow-md` | `3px 3px 0px #0D0D0D` | Botões no estado padrão |
| `--shadow-lg` | `4px 4px 0px #0D0D0D` | Cards de produto |
| `--shadow-xl` | `6px 6px 0px #0D0D0D` | Modais, elementos destacados |
| `--shadow-hover` | `6px 6px 0px #0D0D0D` | Cards e botões no estado hover |
| `--shadow-active` | `1px 1px 0px #0D0D0D` | Botões no estado active (pressionado) |

**Variáveis CSS:**
```css
:root {
    --border-width:        2px;
    --border-width-thick:  3px;
    --border-color:        #0D0D0D;
    --border-radius:       0px;
    --border-radius-sm:    2px;

    --shadow-sm:      2px 2px 0px #0D0D0D;
    --shadow-md:      3px 3px 0px #0D0D0D;
    --shadow-lg:      4px 4px 0px #0D0D0D;
    --shadow-xl:      6px 6px 0px #0D0D0D;
    --shadow-hover:   6px 6px 0px #0D0D0D;
    --shadow-active:  1px 1px 0px #0D0D0D;
}
```

### 5.3 Comportamento de Hover — Botões

```css
.btn-primary {
    background-color: var(--color-primary);
    color: var(--color-surface);
    border: var(--border-width) solid var(--border-color);
    box-shadow: var(--shadow-md);
    transform: translate(0, 0);
    transition: box-shadow 150ms ease, transform 150ms ease;
}

.btn-primary:hover {
    box-shadow: var(--shadow-hover);
    transform: translate(-2px, -2px);
}

.btn-primary:active {
    box-shadow: var(--shadow-active);
    transform: translate(2px, 2px);
}
```

### 5.4 Comportamento de Hover — Cards

```css
.product-card {
    border: var(--border-width) solid var(--border-color);
    box-shadow: var(--shadow-lg);
    transform: translate(0, 0);
    transition: box-shadow 150ms ease, transform 150ms ease;
}

.product-card:hover {
    box-shadow: var(--shadow-hover);
    transform: translate(-2px, -2px);
}
```

---

## 6. Componentes

### 6.1 Navbar

**Finalidade:** Navegação principal do sistema, presente em todas as páginas.

**Aparência:**
- Fundo: `--color-primary` (`#0D0D0D`).
- Texto/ícones: `--color-surface` (branco).
- Logotipo à esquerda, links ao centro/direita.

**Estrutura:**
```
[ LOGO ] ——— [ Início ] [ Produtos ] [ Categorias ] ——— [ Busca ] [ Carrinho ] [ Conta ]
```

**Estados:**
- Link ativo: cor `--color-accent` com sublinhado sólido.
- Link hover: `--color-accent`.
- Carrinho com itens: badge numérico vermelho sobre o ícone.

**Responsividade:**
- Em tablet/mobile: links colapsam para menu hambúrguer.
- Menu hambúrguer abre painel lateral (drawer) com fundo `--color-primary`.

**Regras de uso:**
- Sempre usar o componente `{% include 'partials/navbar.html' %}`.
- Nunca duplicar a navbar manualmente em outra template.

```html
<nav class="navbar" role="navigation" aria-label="Menu principal">
    <div class="navbar__container">
        <a href="/" class="navbar__logo" aria-label="Página inicial">
            <span class="navbar__logo-text">SOLESTEP</span>
        </a>

        <ul class="navbar__links" role="list">
            <li><a href="/" class="navbar__link">Início</a></li>
            <li><a href="/produtos/" class="navbar__link">Produtos</a></li>
            <li><a href="/categorias/" class="navbar__link">Categorias</a></li>
        </ul>

        <div class="navbar__actions">
            <a href="/busca/" class="navbar__icon-btn" aria-label="Buscar produtos">
                <!-- ícone lupa -->
            </a>
            <a href="/carrinho/" class="navbar__icon-btn" aria-label="Carrinho de compras">
                <!-- ícone carrinho -->
                {% if cart_count > 0 %}
                <span class="navbar__badge" aria-label="{{ cart_count }} itens no carrinho">{{ cart_count }}</span>
                {% endif %}
            </a>
            {% if user.is_authenticated %}
                <a href="/perfil/" class="navbar__icon-btn" aria-label="Meu perfil"><!-- ícone usuário --></a>
            {% else %}
                <a href="/login/" class="btn btn--sm btn--outline-light">Entrar</a>
            {% endif %}
        </div>

        <button class="navbar__hamburger" aria-label="Abrir menu" aria-expanded="false" aria-controls="mobile-menu">
            <span></span><span></span><span></span>
        </button>
    </div>
</nav>
```

---

### 6.2 Breadcrumb

**Finalidade:** Indicar ao usuário a localização atual dentro da hierarquia do site.

**Aparência:**
- Texto 14px, cor `--color-muted`.
- Separador: `›`.
- Item atual: cor `--color-primary`, sem link.

**Regra:** Obrigatório em páginas de produto, carrinho e área do vendedor.

```html
<nav aria-label="Breadcrumb" class="breadcrumb">
    <ol class="breadcrumb__list" role="list">
        <li class="breadcrumb__item"><a href="/" class="breadcrumb__link">Início</a></li>
        <li class="breadcrumb__item" aria-hidden="true">›</li>
        <li class="breadcrumb__item"><a href="/tenis/" class="breadcrumb__link">Tênis</a></li>
        <li class="breadcrumb__item" aria-hidden="true">›</li>
        <li class="breadcrumb__item breadcrumb__item--active" aria-current="page">Nike Air Max 270</li>
    </ol>
</nav>
```

---

### 6.3 Footer

**Finalidade:** Rodapé institucional com links secundários.

**Aparência:**
- Fundo: `--color-primary`.
- Texto: `--color-surface`.
- Divisão em colunas: Logo + Descrição | Links rápidos | Categorias | Contato.

**Regras:**
- Sempre usar `{% include 'partials/footer.html' %}`.
- Footer aparece em todas as páginas públicas.

---

### 6.4 Botão Primário

**Finalidade:** Ação principal da tela (ex.: "Comprar Agora", "Adicionar ao Carrinho").

**Aparência:**
- Fundo: `--color-primary`.
- Texto: branco, Space Grotesk 700, 15px, MAIÚSCULAS.
- Borda: 2px sólida `--color-border`.
- Sombra: `var(--shadow-md)`.
- Padding: 14px 24px.

**Estados:**
- `hover`: sombra aumenta, componente se move -2px, -2px.
- `active`: sombra diminui, componente se move +2px, +2px.
- `disabled`: opacidade 40%, sem sombra, cursor `not-allowed`.
- `loading`: texto substituído por spinner, `disabled` aplicado.

**Regra de uso:** Máximo um botão primário por seção de ação.

```css
.btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: var(--space-2);
    cursor: pointer;
    border: none;
    text-decoration: none;
}

.btn--primary {
    background: var(--color-primary);
    color: var(--color-surface);
    border: var(--border-width) solid var(--border-color);
    box-shadow: var(--shadow-md);
    padding: 14px 24px;
    font-family: var(--font-heading);
    font-weight: var(--font-bold);
    font-size: var(--text-sm);
    letter-spacing: 0.04em;
    text-transform: uppercase;
    transition: box-shadow 150ms ease, transform 150ms ease;
}
.btn--primary:hover {
    box-shadow: var(--shadow-hover);
    transform: translate(-2px, -2px);
}
.btn--primary:active {
    box-shadow: var(--shadow-active);
    transform: translate(2px, 2px);
}
.btn--primary:disabled {
    opacity: 0.4;
    box-shadow: none;
    cursor: not-allowed;
    transform: none;
}
```

---

### 6.5 Botão Secundário

**Finalidade:** Ação alternativa ou de suporte (ex.: "Ver detalhes", "Cancelar").

**Aparência:**
- Fundo: transparente.
- Texto: `--color-primary`.
- Borda: 2px sólida `--color-primary`.
- Sombra: `var(--shadow-sm)`.

```css
.btn--secondary {
    background: transparent;
    color: var(--color-primary);
    border: var(--border-width) solid var(--color-primary);
    box-shadow: var(--shadow-sm);
    padding: 14px 24px;
    font-family: var(--font-heading);
    font-weight: var(--font-bold);
    font-size: var(--text-sm);
    letter-spacing: 0.04em;
    text-transform: uppercase;
    transition: box-shadow 150ms ease, transform 150ms ease, background 150ms ease;
}
.btn--secondary:hover {
    background: var(--color-primary);
    color: var(--color-surface);
    box-shadow: var(--shadow-hover);
    transform: translate(-2px, -2px);
}
```

---

### 6.6 Botão de Perigo

**Finalidade:** Ações destrutivas (ex.: "Excluir produto", "Cancelar pedido").

**Aparência:**
- Fundo: `--color-error` (`#CC2200`).
- Texto: branco.
- Sempre precedido de confirmação (modal).

```css
.btn--danger {
    background: var(--color-error);
    color: var(--color-surface);
    border: var(--border-width) solid #990000;
    box-shadow: 3px 3px 0px #990000;
}
```

---

### 6.7 Botão de Acento (CTA Principal)

**Finalidade:** Chamada para ação de máximo impacto (ex.: "Comprar Agora" no hero).

**Aparência:**
- Fundo: `--color-accent` (`#FF3B00`).
- Texto: branco.
- Borda: 2px sólida `--color-primary`.

```css
.btn--accent {
    background: var(--color-accent);
    color: var(--color-surface);
    border: var(--border-width) solid var(--color-primary);
    box-shadow: var(--shadow-md);
}
```

---

### 6.8 Inputs e Formulários

**Finalidade:** Captura de dados do usuário.

**Aparência:**
- Fundo: `--color-surface` (branco).
- Borda: 2px sólida `--color-border`.
- Sem border-radius.
- Padding: 12px 16px.
- Font: Inter 400, 16px.
- Placeholder: cor `--color-muted`.

**Estados:**
- `focus`: borda 3px, sombra `var(--shadow-sm)`, outline visível para acessibilidade.
- `error`: borda cor `--color-error`, mensagem de erro abaixo.
- `success`: borda cor `--color-success`.
- `disabled`: fundo `#F0F0F0`, opacidade 60%.

```css
.input {
    width: 100%;
    background: var(--color-surface);
    border: var(--border-width) solid var(--color-border);
    border-radius: var(--border-radius);
    padding: 12px 16px;
    font-family: var(--font-body);
    font-size: var(--text-base);
    color: var(--color-primary);
    transition: border-width 100ms ease, box-shadow 100ms ease;
}
.input:focus {
    outline: none;
    border-width: var(--border-width-thick);
    box-shadow: var(--shadow-sm);
}
.input--error   { border-color: var(--color-error); }
.input--success { border-color: var(--color-success); }

.label {
    display: block;
    font-family: var(--font-body);
    font-weight: var(--font-semibold);
    font-size: 13px;
    letter-spacing: 0.02em;
    color: var(--color-primary);
    margin-bottom: var(--space-2);
}

.input-error-msg {
    display: block;
    font-size: var(--text-sm);
    color: var(--color-error);
    margin-top: var(--space-1);
}
```

**Regras de uso:**
- Toda `<input>` deve ter um `<label>` associado via `for` / `id`.
- Mensagens de erro são exibidas abaixo do campo, nunca dentro.
- O placeholder **não substitui** o label.

---

### 6.9 Busca

**Finalidade:** Campo de pesquisa de produtos.

```html
<div class="search-wrapper" role="search">
    <label for="search-input" class="sr-only">Buscar calçados</label>
    <input
        type="search"
        id="search-input"
        name="q"
        class="input search__input"
        placeholder="Buscar tênis, botas, sandálias..."
        aria-label="Buscar produtos"
    >
    <button type="submit" class="search__btn" aria-label="Buscar">
        <!-- ícone lupa -->
    </button>
</div>
```

---

### 6.10 Select, Checkbox e Radio

**Select:**
- Mesmas regras visuais do input.
- Seta indicadora visível.

**Checkbox e Radio:**
- Borda 2px `--color-primary`.
- Quando marcado: fundo `--color-primary`, check em branco.
- Tamanho mínimo: 20px × 20px (área de toque de 44px × 44px).

---

### 6.11 Badge

**Finalidade:** Etiquetas informativas em produtos (ex.: "NOVO", "OFERTA", "ESGOTADO").

| Badge | Fundo | Texto | Uso |
|---|---|---|---|
| `badge--new` | `--color-primary` | Branco | Produto novo |
| `badge--sale` | `--color-accent` | Branco | Produto em oferta |
| `badge--out` | `--color-muted` | Branco | Esgotado |
| `badge--exclusive` | `#1A1A1A` | Branco | Exclusivo |

```css
.badge {
    display: inline-block;
    padding: 3px 8px;
    font-family: var(--font-heading);
    font-weight: var(--font-bold);
    font-size: 11px;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    border-radius: var(--border-radius-sm);
    border: var(--border-width) solid var(--color-border);
    box-shadow: var(--shadow-sm);
}
.badge--new  { background: var(--color-primary); color: white; }
.badge--sale { background: var(--color-accent);  color: white; border-color: #CC2E00; }
.badge--out  { background: var(--color-muted);   color: white; }
```

---

### 6.12 Alert

**Finalidade:** Mensagens informativas persistentes na página.

**Tipos:** `success`, `error`, `warning`, `info`.

```css
.alert {
    padding: var(--space-4) var(--space-6);
    border: var(--border-width) solid var(--color-border);
    border-left: 4px solid;
    display: flex;
    align-items: flex-start;
    gap: var(--space-3);
}
.alert--success { border-left-color: var(--color-success); background: #F0FAF4; }
.alert--error   { border-left-color: var(--color-error);   background: #FFF0EE; }
.alert--warning { border-left-color: var(--color-warning); background: #FFF8E6; }
.alert--info    { border-left-color: var(--color-info);    background: #EEF4FF; }
```

---

### 6.13 Toast

**Finalidade:** Notificações temporárias (ex.: "Produto adicionado ao carrinho!").

**Comportamento:**
- Aparece no canto inferior direito.
- Duração: 3 segundos.
- Animação: slide-in da direita, fade-out ao desaparecer.
- Máximo 3 toasts simultâneos.

```css
.toast-container {
    position: fixed;
    bottom: var(--space-6);
    right: var(--space-6);
    z-index: 9999;
    display: flex;
    flex-direction: column;
    gap: var(--space-3);
}
.toast {
    background: var(--color-primary);
    color: white;
    padding: var(--space-4) var(--space-6);
    border: var(--border-width) solid var(--color-border);
    box-shadow: var(--shadow-lg);
    min-width: 280px;
    animation: toastSlideIn 200ms ease forwards;
}
@keyframes toastSlideIn {
    from { transform: translateX(110%); opacity: 0; }
    to   { transform: translateX(0);   opacity: 1; }
}
```

---

### 6.14 Modal

**Finalidade:** Confirmação de ações críticas ou exibição de conteúdo em sobreposição.

**Aparência:**
- Overlay: `rgba(0,0,0,0.6)`.
- Caixa modal: fundo `--color-surface`, borda 2px, sombra `--shadow-xl`.
- Sem border-radius.
- Largura: 480px (desktop), 100% em mobile.

**Comportamento:**
- Fecha ao pressionar `Esc`.
- Fecha ao clicar fora do modal.
- Foco retorna ao elemento acionador ao fechar.

**Regras:**
- Sempre incluir botão de fechar com `aria-label="Fechar modal"`.
- Nunca usar modal para formulários longos — usar página dedicada.

---

### 6.15 Loading

**Tipos:**
- **Spinner inline:** ícone girando dentro do botão.
- **Skeleton:** blocos animados simulando o conteúdo (preferencial para listagens).
- **Overlay de página:** apenas em operações críticas como checkout.

```css
.skeleton {
    background: linear-gradient(90deg, #E8E3DB 25%, #D0CBB8 50%, #E8E3DB 75%);
    background-size: 200% 100%;
    animation: skeleton-loading 1.5s infinite;
}
@keyframes skeleton-loading {
    0%   { background-position: 200% 0; }
    100% { background-position: -200% 0; }
}
```

---

### 6.16 Estado Vazio

**Aparência:**
- Ícone ilustrativo centralizado.
- Título descritivo em Space Grotesk.
- Subtexto em Inter.
- Botão de ação quando aplicável.

**Exemplos:**
- Carrinho vazio → "Seu carrinho está vazio" + botão "Ver produtos".
- Busca sem resultado → "Nenhum calçado encontrado para '...'" + sugestão de filtros.
- Histórico de pedidos vazio → "Você ainda não realizou pedidos".

---

## 7. Product Card — Especificação Detalhada

O Product Card é o componente mais importante do sistema. **Deve ser criado uma única vez e reutilizado em todas as telas.**

### 7.1 Anatomia do Card

```
┌──────────────────────────────┐  ← borda 2px #0D0D0D
│  [BADGE]                     │  ← área de badges
│                              │
│         IMAGEM 1:1           │  ← proporção quadrada obrigatória
│       (600 × 600px)          │
│                              │
├──────────────────────────────┤
│  MARCA (muted, 12px)         │
│  Nome do Produto (16px 700)  │
│                              │
│  Tamanhos: 38 39 40 41 42    │  ← chips de tamanho
│                              │
│  R$ 199,90   ~~R$ 259,90~~   │  ← preço promo + original riscado
│                              │
│  [ ADICIONAR AO CARRINHO ]   │  ← botão primário, width 100%
└──────────────────────────────┘
         sombra sólida 4px
```

### 7.2 Especificações

| Elemento | Especificação |
|---|---|
| **Largura** | Definida pela grid (min 200px, max 320px) |
| **Imagem** | Proporção 1:1, `object-fit: cover`, fundo `#F5F5F0` |
| **Borda** | 2px sólida `#0D0D0D` |
| **Sombra** | `4px 4px 0px #0D0D0D` |
| **Padding interno** | 16px |
| **Nome** | Space Grotesk 700, 16px, máx 2 linhas |
| **Marca** | Inter 400, 12px, `--color-muted`, MAIÚSCULAS |
| **Preço promo** | Space Grotesk 700, 22px, `--color-primary` |
| **Preço original** | Inter 400, 14px, `--color-muted`, `text-decoration: line-through` |
| **Badge** | Canto superior esquerdo, sobreposição na imagem |
| **Hover** | `transform: translate(-2px, -2px)`, sombra vira `6px 6px` |
| **Transição** | `150ms ease` |

### 7.3 Grid de Produtos

| Breakpoint | Colunas |
|---|---|
| Mobile (< 640px) | 2 colunas |
| Tablet (640px–1024px) | 3 colunas |
| Desktop (> 1024px) | 4 colunas |

```css
.product-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
    gap: var(--space-6);
}
```

### 7.4 HTML do Product Card

```html
<article class="product-card" aria-label="{{ product.name }}">
    <div class="product-card__image-wrap">
        {% if product.is_on_sale %}
        <span class="badge badge--sale" aria-label="Produto em oferta">OFERTA</span>
        {% endif %}
        <img
            src="{{ product.image.url }}"
            alt="{{ product.name }} - {{ product.brand }}"
            class="product-card__image"
            width="600"
            height="600"
            loading="lazy"
        >
    </div>

    <div class="product-card__body">
        <p class="product-card__brand">{{ product.brand }}</p>
        <h3 class="product-card__name">{{ product.name }}</h3>

        <div class="product-card__sizes" aria-label="Tamanhos disponíveis">
            {% for size in product.available_sizes %}
            <span class="size-chip">{{ size }}</span>
            {% endfor %}
        </div>

        <div class="product-card__pricing">
            {% if product.promotional_price %}
            <span class="price price--promo">R$ {{ product.promotional_price }}</span>
            <span class="price price--original" aria-label="Preço original">R$ {{ product.price }}</span>
            {% else %}
            <span class="price price--promo">R$ {{ product.price }}</span>
            {% endif %}
        </div>

        <a href="{{ product.get_absolute_url }}" class="btn btn--primary" style="width: 100%;">
            Ver Produto
        </a>
    </div>
</article>
```

---

## 8. Padrão Visual dos Produtos

### 8.1 Nomenclatura de Produtos

**Padrão obrigatório:**

```
[Marca] + [Modelo] + [Público/Gênero]
```

| ✅ Correto | ❌ Incorreto |
|---|---|
| Nike Air Max 270 Masculino | Tênis Nike barato |
| Adidas Samba OG Feminino | Samba Adidas |
| Vans Old Skool Unissex | Vans Classico Off White |
| Puma RS-X Infantil | Lindo tênis colorido |

**Regras:**
- O campo `nome` no cadastro nunca deve conter descrições promocionais.
- Gênero/público: `Masculino`, `Feminino`, `Unissex`, `Infantil`.
- Modelo: nome oficial do produto conforme a marca.

### 8.2 Padrão de Imagens

| Atributo | Valor |
|---|---|
| **Proporção** | 1:1 (quadrada) |
| **Resolução mínima** | 800 × 800px |
| **Resolução recomendada** | 1200 × 1200px |
| **Fundo** | Neutro — branco (`#FFFFFF`) ou creme claro (`#F5F5F0`) |
| **Enquadramento** | Produto centralizado, ocupando 75%–85% da imagem |
| **Posição** | Lateral com angulação a 45° ou frontal |
| **Quantidade mínima** | 1 imagem (principal) |
| **Quantidade ideal** | 4–6 imagens (frente, lateral, detalhe, sola) |
| **Qualidade** | Sem marcas d'água, sem logotipos de terceiros |
| **Consistência** | Todas as imagens do mesmo produto devem ter o mesmo fundo e iluminação |

> **Essas regras podem ser ajustadas conforme necessidades do projeto**, mas toda alteração deve ser documentada aqui antes de implementada.

---

## 9. Padrão de Cadastro dos Calçados

### 9.1 Campos do Produto

#### Identificação

| Campo | Tipo | Obrigatório | Observações |
|---|---|---|---|
| `id` | Integer (auto) | — | Gerado automaticamente |
| `nome` | CharField(200) | ✅ | Seguir padrão: Marca + Modelo + Gênero |
| `marca` | CharField(100) | ✅ | Ex.: Nike, Adidas, Vans |
| `modelo` | CharField(150) | ✅ | Ex.: Air Max 270, Samba OG |
| `categoria` | ForeignKey | ✅ | Veja seção 10 |
| `subcategoria` | CharField(100) | ❌ | Opcional |
| `slug` | SlugField | Auto | Gerado a partir do nome |

#### Informações Comerciais

| Campo | Tipo | Obrigatório | Observações |
|---|---|---|---|
| `preco` | DecimalField(8,2) | ✅ | Preço de tabela |
| `preco_promocional` | DecimalField(8,2) | ❌ | Somente se houver oferta ativa |
| `estoque_total` | IntegerField | ✅ | Quantidade total disponível |
| `ativo` | BooleanField | ✅ | Default: True |

#### Características

| Campo | Tipo | Obrigatório | Observações |
|---|---|---|---|
| `cor` | CharField(50) | ✅ | Ex.: Preto/Branco, Vermelho |
| `material` | CharField(100) | ❌ | Ex.: Couro sintético, Lona |
| `genero` | CharField | ✅ | Masculino / Feminino / Unissex / Infantil |
| `estilo` | CharField(100) | ❌ | Ex.: Casual, Esportivo, Social |
| `descricao` | TextField | ✅ | Mínimo 50 caracteres |

#### Tamanhos

| Campo | Tipo | Obrigatório | Observações |
|---|---|---|---|
| `tamanhos` | ManyToMany → ProductSize | ✅ | Relação com tabela de tamanhos |
| `estoque_por_tamanho` | IntegerField por size | ❌ | Quando o controle for granular |

#### Imagens

| Campo | Tipo | Obrigatório | Observações |
|---|---|---|---|
| `imagem_principal` | ImageField | ✅ | Proporção 1:1, mín. 800×800px |
| `imagens_adicionais` | M2M → ProductImage | ❌ | Máx. 8 imagens adicionais |

---

## 10. Categorias de Produtos

### 10.1 Estrutura de Categorias

| Categoria | Subcategorias sugeridas |
|---|---|
| **Tênis** | Casual, Esportivo, Running, Basketball, Skate, Lifestyle |
| **Sapatos** | Social, Oxford, Derby, Mocassim, Sapatilha |
| **Botas** | Coturno, Cano Longo, Cano Curto, Chelsea, Motoqueiro |
| **Sandálias** | Rasteira, Plataforma, Tiras, Papete |
| **Chinelos** | Slide, Havaianas, Rider |
| **Chuteiras** | Campo, Society, Futsal, Indoor |
| **Outros** | Pantufas, Galochas, Tamancos |

### 10.2 Regras para Categorias

- Nunca criar subcategorias que existam como categoria principal.
- Se um produto não se encaixar em nenhuma categoria, usar "Outros" e sugerir nova categoria ao administrador.
- Categorias são gerenciadas pelo administrador, não pelo vendedor.
- Evite categorias excessivamente específicas: prefira "Botas" com subcategoria "Coturno" a criar uma categoria "Coturno".

---

## 11. Padrão das Páginas

### 11.1 Home

**Objetivo:** Apresentar o marketplace, destacar produtos e categorias, e direcionar o usuário para compra.

**Estrutura:**
```
[ NAVBAR ]
[ HERO ] — título impactante + CTA + imagem de destaque
[ CATEGORIAS ] — grid de ícones/cards das categorias principais
[ PRODUTOS EM DESTAQUE ] — carrossel ou grid 4 colunas
[ OFERTAS / PROMOÇÕES ] — faixa com destaque visual (fundo accent)
[ BANNER SECUNDÁRIO ] — chamada para cadastro de vendedor
[ FOOTER ]
```

**Componentes:** Navbar, Hero, ProductCard (destaque), Badge, Footer.

**Responsividade:**
- Hero: texto e imagem empilhados em mobile.
- Grid de categorias: 2 colunas em mobile, 4 em desktop.
- Seção de destaque: carrossel em mobile, grid em desktop.

---

### 11.2 Listagem de Produtos

**Objetivo:** Permitir ao usuário encontrar e filtrar calçados.

**Estrutura:**
```
[ NAVBAR ]
[ BREADCRUMB ]
[ TÍTULO DA LISTAGEM + CONTADOR ]
[ BARRA DE FILTROS + ORDENAÇÃO ]
[ GRID DE PRODUTOS ]
[ PAGINAÇÃO ]
[ FOOTER ]
```

**Filtros:** Categoria, Marca, Tamanho, Faixa de preço, Gênero.

**Ordenação:** Relevância, Menor preço, Maior preço, Mais recentes.

**Estado vazio:** Mensagem + sugestão de limpar filtros.

**Responsividade:**
- Desktop: sidebar de filtros à esquerda (240px), grid à direita.
- Mobile: filtros em drawer acionado por botão.

---

### 11.3 Detalhes do Produto

**Objetivo:** Apresentar todas as informações do produto e permitir a compra.

**Estrutura:**
```
[ NAVBAR ]
[ BREADCRUMB ]
[ GALERIA (esq.) | INFORMAÇÕES (dir.) ]
    Galeria: imagem principal + miniaturas
    Info: Marca | Nome | Avaliação
          Preço (+ promo se houver)
          Seleção de tamanho (chips obrigatórios)
          Quantidade
          [ ADICIONAR AO CARRINHO ] [ COMPRAR AGORA ]
          Descrição
          Características técnicas
[ PRODUTOS RELACIONADOS ]
[ FOOTER ]
```

**Regras:**
- Botão "Adicionar ao Carrinho" desabilitado até seleção de tamanho.
- Tamanhos sem estoque: riscados, não clicáveis.
- Galeria: clique em miniatura atualiza imagem principal.

---

### 11.4 Login

**Estrutura:**
```
[ NAVBAR SIMPLIFICADA ]
[ CARD CENTRALIZADO ]
    Título: "ENTRAR NA CONTA"
    Input: E-mail
    Input: Senha [mostrar/ocultar]
    [ ENTRAR ] (btn primário, width 100%)
    Link: "Esqueci minha senha"
    Link: "Criar uma conta"
```

**Regras:** Redirecionar via parâmetro `next` após login.

---

### 11.5 Cadastro

**Estrutura:**
```
[ NAVBAR SIMPLIFICADA ]
[ CARD CENTRALIZADO ]
    Título: "CRIAR CONTA"
    Seletor tipo: [ COMPRADOR ] [ VENDEDOR ]
    Input: Nome completo
    Input: E-mail
    Input: Senha
    Input: Confirmar senha
    [ CRIAR CONTA ]
    Link: "Já tenho conta"
```

---

### 11.6 Carrinho

**Estrutura:**
```
[ NAVBAR ]
[ BREADCRUMB ]
[ ITENS (esq. 65%) | RESUMO DO PEDIDO (dir. 35%) ]
    Itens: imagem + nome + tamanho + quantidade (- n +) + preço + [remover]
    Resumo: subtotal + frete + total + [ FINALIZAR COMPRA ]
[ FOOTER ]
```

**Estado vazio:** "Seu carrinho está vazio" + botão "Continuar comprando".

**Responsividade:** Itens acima do resumo em mobile.

---

### 11.7 Checkout

**Estrutura:**
```
[ NAVBAR SIMPLIFICADA ]
[ STEPPER: 1. Endereço → 2. Revisão → 3. Confirmação ]
[ FORMULÁRIO DO PASSO ATUAL ]
[ RESUMO COMPACTO À DIREITA ]
```

---

### 11.8 Área do Vendedor

**Estrutura:**
```
[ NAVBAR (com indicador "Modo Vendedor") ]
[ SIDEBAR INTERNA ]
    → Painel / Dashboard
    → Meus Produtos
    → Adicionar Produto
    → Pedidos Recebidos
    → Meu Perfil
[ CONTEÚDO PRINCIPAL ]
```

**Regra:** Acesso restrito a `user_type = 'seller'`.

---

### 11.9 Cadastro e Edição de Produto

**Estrutura:**
```
[ NAVBAR + SIDEBAR DO VENDEDOR ]
[ FORMULÁRIO EM SEÇÕES ]
    1. Identificação
    2. Informações comerciais
    3. Características
    4. Tamanhos
    5. Imagens
    6. Descrição
[ [ CANCELAR ] [ RASCUNHO ] [ PUBLICAR ] ]
```

---

### 11.10 Perfil do Usuário

**Estrutura:**
```
[ NAVBAR ]
[ SIDEBAR: Avatar + Nome + Links ]
    → Meus Dados
    → Histórico de Pedidos
    → Endereços
    → Segurança
[ CONTEÚDO ]
```

---

## 12. Responsividade

### 12.1 Breakpoints

| Token | Breakpoint | Descrição |
|---|---|---|
| `--bp-sm` | 640px | Mobile landscape / tablet pequeno |
| `--bp-md` | 768px | Tablet |
| `--bp-lg` | 1024px | Desktop pequeno |
| `--bp-xl` | 1280px | Desktop padrão |
| `--bp-2xl` | 1536px | Desktop grande |

### 12.2 Estratégia Mobile-First

```css
/* Base (mobile) */
.container { padding: 0 var(--space-4); }

@media (min-width: 768px) {
    .container { padding: 0 var(--space-8); }
}

@media (min-width: 1024px) {
    .container { max-width: 1200px; margin: 0 auto; padding: 0 var(--space-10); }
}
```

### 12.3 Comportamento por Elemento

| Elemento | Mobile | Tablet | Desktop |
|---|---|---|---|
| **Navbar** | Logo + Hambúrguer | Logo + Links principais | Logo + Todos os links + Ações |
| **Grid de produtos** | 2 colunas | 3 colunas | 4 colunas |
| **Filtros** | Drawer (bottom) | Drawer lateral | Sidebar fixa |
| **Botões CTA** | `width: 100%` | Tamanho natural | Tamanho natural |
| **Galeria de produto** | Carrossel | Grid pequeno | Imagem grande + miniaturas |
| **Formulários** | 1 coluna | 1–2 colunas | 2 colunas |
| **Tabelas** | Scroll horizontal | Scroll horizontal | Exibição completa |

**Regra principal:** A identidade visual não muda entre dispositivos. O que muda é o layout e agrupamento dos elementos.

---

## 13. Acessibilidade

### 13.1 Requisitos Mínimos Obrigatórios

| Requisito | Regra |
|---|---|
| **Contraste de texto** | Mínimo 4.5:1 para texto normal, 3:1 para texto grande (WCAG AA) |
| **Tamanho mínimo de fonte** | 14px para qualquer texto funcional |
| **Foco de teclado** | Todos os elementos interativos devem ter `:focus` visível |
| **Alt em imagens** | `alt="{{ product.name }} - {{ product.brand }}"` |
| **Labels de formulário** | Toda `<input>` deve ter `<label>` via `for`/`id` |
| **Mensagens de erro** | Identificar o campo e descrever a correção |
| **Áreas clicáveis** | Mínimo 44px × 44px |
| **Navegação por teclado** | Tab/Shift+Tab em ordem lógica |
| **Roles semânticos** | `<nav>`, `<main>`, `<header>`, `<footer>`, `<article>`, `<section>` |
| **ARIA labels** | `aria-label` em ícones sem texto, `aria-current="page"` no item ativo |

### 13.2 CSS de Foco Padrão

```css
*:focus-visible {
    outline: 3px solid var(--color-accent);
    outline-offset: 2px;
}
*:focus:not(:focus-visible) {
    outline: none;
}
```

---

## 14. Estados dos Componentes

| Estado | Descrição | CSS típico |
|---|---|---|
| `default` | Estado inicial | Estilos base |
| `hover` | Mouse sobre o elemento | `transform`, sombra aumentada |
| `focus` | Foco via teclado | `outline` visível, borda reforçada |
| `active` | Sendo clicado | `transform: translate(2px,2px)`, sombra reduzida |
| `disabled` | Não interativo | `opacity: 0.4`, `cursor: not-allowed` |
| `loading` | Processando | Spinner, texto substituído |
| `error` | Entrada inválida | Borda vermelha, mensagem de erro |
| `success` | Ação concluída | Borda verde, mensagem de sucesso |
| `empty` | Sem conteúdo | Ilustração + texto + ação sugerida |

---

## 15. Regras de UX

1. **Uma ação principal por tela** — Nunca dois botões primários competindo pelo mesmo espaço.
2. **Mensagens de erro descrevem a solução** — Nunca apenas "Campo inválido". Use "O e-mail deve conter @".
3. **Texto de botão descreve a ação** — Não use "Clique aqui". Use "Adicionar ao Carrinho".
4. **Feedback imediato** — Toda ação do usuário deve ter resposta visual em até 100ms.
5. **Consistência entre páginas** — O mesmo componente tem o mesmo aspecto em qualquer página.
6. **Nunca use cor como único diferenciador** — Combine cor com ícone ou texto para estados.
7. **Hierarquia clara** — O elemento mais importante da tela tem maior peso visual.
8. **Sem mudanças bruscas de layout** — Não inserir/remover elementos que empurrem conteúdo.
9. **Loading sempre visível** — O usuário nunca aguarda sem feedback visual.
10. **Formulários nunca perdem dados sem aviso** — Confirmar antes de descartar.

---

## 16. Convenções para Desenvolvimento

### 16.1 Arquivo Base de Variáveis CSS

Crie `static/css/base.css`:

```css
/* ================================================
   MARKETPLACE DE CALÇADOS — BASE CSS
   Design System v1.0
   ================================================ */

:root {
    /* Cores */
    --color-bg:        #F5F0E8;
    --color-primary:   #0D0D0D;
    --color-accent:    #FF3B00;
    --color-secondary: #1A1A1A;
    --color-border:    #0D0D0D;
    --color-surface:   #FFFFFF;
    --color-muted:     #8C8C8C;

    --color-success:   #1A8C4E;
    --color-error:     #CC2200;
    --color-warning:   #E8A000;
    --color-info:      #1A5FA8;

    /* Tipografia */
    --font-heading: 'Space Grotesk', sans-serif;
    --font-body:    'Inter', sans-serif;

    --text-xs:   12px;
    --text-sm:   14px;
    --text-base: 16px;
    --text-lg:   20px;
    --text-xl:   28px;
    --text-2xl:  36px;
    --text-3xl:  48px;

    --font-regular:   400;
    --font-medium:    500;
    --font-semibold:  600;
    --font-bold:      700;
    --font-extrabold: 800;

    /* Espaçamento */
    --space-1:  4px;   --space-8:  32px;
    --space-2:  8px;   --space-10: 40px;
    --space-3:  12px;  --space-12: 48px;
    --space-4:  16px;  --space-16: 64px;
    --space-5:  20px;  --space-24: 96px;
    --space-6:  24px;

    /* Bordas */
    --border-width:       2px;
    --border-width-thick: 3px;
    --border-color:       #0D0D0D;
    --border-radius:      0px;
    --border-radius-sm:   2px;

    /* Sombras */
    --shadow-sm:     2px 2px 0px #0D0D0D;
    --shadow-md:     3px 3px 0px #0D0D0D;
    --shadow-lg:     4px 4px 0px #0D0D0D;
    --shadow-xl:     6px 6px 0px #0D0D0D;
    --shadow-hover:  6px 6px 0px #0D0D0D;
    --shadow-active: 1px 1px 0px #0D0D0D;

    /* Breakpoints (referência) */
    --bp-sm:  640px;
    --bp-md:  768px;
    --bp-lg:  1024px;
    --bp-xl:  1280px;
    --bp-2xl: 1536px;
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

body {
    font-family: var(--font-body);
    font-size: var(--text-base);
    background-color: var(--color-bg);
    color: var(--color-primary);
    line-height: 1.6;
    -webkit-font-smoothing: antialiased;
}

h1, h2, h3, h4, h5, h6 {
    font-family: var(--font-heading);
    font-weight: var(--font-bold);
    line-height: 1.2;
    color: var(--color-primary);
}

a { color: inherit; text-decoration: none; }
a:hover { color: var(--color-accent); }

img { display: block; max-width: 100%; }

.sr-only {
    position: absolute;
    width: 1px; height: 1px;
    padding: 0; margin: -1px;
    overflow: hidden;
    clip: rect(0,0,0,0);
    white-space: nowrap;
    border: 0;
}
```

### 16.2 Nomenclatura de Classes CSS (BEM)

```
.block {}
.block__element {}
.block--modifier {}
```

**Exemplos:**

```
.product-card {}
.product-card__image {}
.product-card__body {}
.product-card__name {}
.product-card__pricing {}
.product-card__pricing--promo {}

.btn {}
.btn--primary {}
.btn--secondary {}
.btn--danger {}
.btn--sm {}

.navbar {}
.navbar__logo {}
.navbar__links {}
.navbar__link {}
.navbar__link--active {}
.navbar__hamburger {}

.input {}
.input--error {}
.input--success {}
.label {}
.input-error-msg {}

.badge {}
.badge--new {}
.badge--sale {}
.badge--out {}
```

### 16.3 Estrutura de Arquivos CSS

```
static/
└── css/
    ├── base.css              # Variáveis, reset, tipografia base
    ├── components/
    │   ├── navbar.css
    │   ├── footer.css
    │   ├── buttons.css
    │   ├── inputs.css
    │   ├── cards.css
    │   ├── badges.css
    │   ├── alerts.css
    │   ├── modals.css
    │   └── breadcrumb.css
    └── pages/
        ├── home.css
        ├── products.css
        ├── product-detail.css
        ├── cart.css
        ├── checkout.css
        ├── auth.css
        └── seller.css
```

**Regra:** `base.css` é carregado primeiro. Cada página carrega apenas seus próprios arquivos.

### 16.4 Estrutura de Templates Django

```
templates/
├── base.html                   # Template base
├── partials/
│   ├── navbar.html
│   ├── footer.html
│   ├── breadcrumb.html
│   ├── product_card.html       # Componente reutilizável
│   ├── alert.html
│   └── toast.html
├── home/
│   └── index.html
├── products/
│   ├── list.html
│   └── detail.html
├── cart/
│   └── cart.html
├── orders/
│   ├── checkout.html
│   └── confirmation.html
├── users/
│   ├── login.html
│   ├── register.html
│   └── profile.html
└── seller/
    ├── dashboard.html
    ├── product_form.html
    └── orders.html
```

### 16.5 Reutilização de Componentes

```html
<!-- Errado: copiar HTML do card em cada listagem -->
<article class="product-card">...</article>

<!-- Correto: usar partial -->
{% for product in products %}
    {% include 'partials/product_card.html' with product=product %}
{% endfor %}
```

### 16.6 JavaScript — Convenções

- Um arquivo `.js` por funcionalidade principal.
- Usar `data-*` attributes para integração HTML/JS.
- JavaScript nativo (ES6+), sem jQuery.
- `addEventListener`, nunca `onclick` inline.

```javascript
// Correto
document.getElementById('add-to-cart-btn')
    .addEventListener('click', handleAddToCart);

// Errado
// <button onclick="addToCart()">
```

---

## 17. Design Tokens — Tabela de Referência Completa

### Cores

| Token | Valor | Uso |
|---|---|---|
| `--color-bg` | `#F5F0E8` | Fundo de página |
| `--color-primary` | `#0D0D0D` | Texto, bordas, BTN primário |
| `--color-accent` | `#FF3B00` | Destaque, CTA, oferta |
| `--color-secondary` | `#1A1A1A` | Texto secundário |
| `--color-border` | `#0D0D0D` | Bordas |
| `--color-surface` | `#FFFFFF` | Cards, inputs, modais |
| `--color-muted` | `#8C8C8C` | Textos de apoio |
| `--color-success` | `#1A8C4E` | Confirmação |
| `--color-error` | `#CC2200` | Erro |
| `--color-warning` | `#E8A000` | Alerta |
| `--color-info` | `#1A5FA8` | Informação |

### Tipografia

| Token | Valor |
|---|---|
| `--font-heading` | `'Space Grotesk', sans-serif` |
| `--font-body` | `'Inter', sans-serif` |
| `--text-xs` | `12px` |
| `--text-sm` | `14px` |
| `--text-base` | `16px` |
| `--text-lg` | `20px` |
| `--text-xl` | `28px` |
| `--text-2xl` | `36px` |
| `--text-3xl` | `48px` |
| `--font-regular` | `400` |
| `--font-medium` | `500` |
| `--font-semibold` | `600` |
| `--font-bold` | `700` |
| `--font-extrabold` | `800` |

### Espaçamento

| Token | Valor | Token | Valor |
|---|---|---|---|
| `--space-1` | `4px` | `--space-8` | `32px` |
| `--space-2` | `8px` | `--space-10` | `40px` |
| `--space-3` | `12px` | `--space-12` | `48px` |
| `--space-4` | `16px` | `--space-16` | `64px` |
| `--space-5` | `20px` | `--space-24` | `96px` |
| `--space-6` | `24px` | | |

### Bordas e Sombras

| Token | Valor |
|---|---|
| `--border-width` | `2px` |
| `--border-width-thick` | `3px` |
| `--border-color` | `#0D0D0D` |
| `--border-radius` | `0px` |
| `--border-radius-sm` | `2px` |
| `--shadow-sm` | `2px 2px 0px #0D0D0D` |
| `--shadow-md` | `3px 3px 0px #0D0D0D` |
| `--shadow-lg` | `4px 4px 0px #0D0D0D` |
| `--shadow-xl` | `6px 6px 0px #0D0D0D` |
| `--shadow-hover` | `6px 6px 0px #0D0D0D` |
| `--shadow-active` | `1px 1px 0px #0D0D0D` |

### Breakpoints

| Token | Valor |
|---|---|
| `--bp-sm` | `640px` |
| `--bp-md` | `768px` |
| `--bp-lg` | `1024px` |
| `--bp-xl` | `1280px` |
| `--bp-2xl` | `1536px` |

---

## 18. Página Style Guide (`/style-guide`)

### 18.1 Proposta

Criar uma página interna acessível em `/style-guide` que funcione como **"fonte oficial da verdade"** do design do projeto. Exibe visualmente todos os tokens, componentes e padrões.

### 18.2 Seções da Página

1. Paleta de Cores — Swatches com nome, HEX e token CSS.
2. Tipografia — Exemplos de H1–H4, texto, preços.
3. Botões — Primário, Secundário, Perigo, Acento, Disabled, Loading.
4. Inputs — Default, Focus, Error, Success, Disabled, Select, Checkbox, Textarea.
5. Cards — Product Card com dados mockados.
6. Badges — Todos os tipos.
7. Alerts — Success, Error, Warning, Info.
8. Toasts — Botão para acionar cada tipo.
9. Modais — Botão para abrir modal de exemplo.
10. Estados — Loading skeleton, Estado vazio.
11. Espaçamentos — Régua visual de cada `--space-*`.
12. Sombras e Bordas — Exemplos visuais de cada token.

### 18.3 Implementação no Django

```python
# urls.py
from django.conf import settings
from django.http import Http404

def style_guide(request):
    """Disponível apenas em ambiente de desenvolvimento."""
    if not settings.DEBUG:
        raise Http404
    return render(request, 'style_guide/index.html')

# Adicionar ao urls.py principal:
path('style-guide/', style_guide, name='style_guide'),
```

> **A rota `/style-guide` deve existir apenas com `DEBUG=True`. Em produção, retorna 404.**

### 18.4 Por que ter uma Style Guide?

- Elimina discussões sobre "qual é a cor certa" ou "qual é o tamanho do botão".
- Referência visual imediata para novos membros da equipe.
- Detecta inconsistências antes que cheguem ao usuário final.
- Funciona como teste: se um componente quebra na style guide, há um problema no CSS.

---

## 19. Checklist para Criação de Novas Telas

Antes de considerar uma tela como **concluída**, responda todas as perguntas. Qualquer "Não" indica uma pendência.

### Design Visual

- [ ] A tela utiliza **somente** as cores da paleta definida (`--color-*`)?
- [ ] A tipografia segue o padrão (Space Grotesk para títulos, Inter para textos)?
- [ ] Os pesos, tamanhos e line-heights estão dentro da escala tipográfica?
- [ ] Os espaçamentos utilizam a escala `--space-*` (sem valores arbitrários)?
- [ ] As bordas têm 2px sólida `--color-border`?
- [ ] As sombras são sólidas (sem blur) e seguem os tokens `--shadow-*`?
- [ ] O conceito Neo-Brutalism + Streetwear está preservado?

### Componentes e Reutilização

- [ ] Os componentes existentes foram reutilizados (navbar, footer, cards, botões)?
- [ ] Nenhum componente foi duplicado manualmente sem uso de `{% include %}`?
- [ ] Classes CSS seguem a nomenclatura BEM?
- [ ] Nenhuma cor, espaçamento ou sombra foi definida fora das variáveis CSS?

### Responsividade

- [ ] O layout foi testado em 375px (mobile)?
- [ ] O layout foi testado em 768px (tablet)?
- [ ] O layout foi testado em 1280px (desktop)?
- [ ] Os breakpoints utilizam a abordagem mobile-first?
- [ ] Nenhum elemento ultrapassa os limites da tela em mobile?

### Estados e Interatividade

- [ ] O estado `hover` de todos os elementos interativos foi definido?
- [ ] O estado `focus` é visível (outline 3px `--color-accent`)?
- [ ] O estado `disabled` está implementado onde aplicável?
- [ ] O estado `loading` foi considerado para operações assíncronas?
- [ ] O estado `empty` foi definido para listas e resultados de busca?
- [ ] O estado `error` foi definido para formulários?
- [ ] O estado `success` foi definido para ações concluídas?

### Acessibilidade

- [ ] Todas as imagens têm `alt` descritivo?
- [ ] Todos os inputs têm `<label>` associado via `for`/`id`?
- [ ] O contraste de texto atinge mínimo 4.5:1 (WCAG AA)?
- [ ] A navegação por teclado funciona em ordem lógica?
- [ ] Elementos interativos têm área mínima de 44px × 44px?
- [ ] Ícones sem texto têm `aria-label`?
- [ ] Mensagens de erro descrevem claramente o problema e a solução?

### UX e Comportamento

- [ ] Há no máximo um botão primário por seção de ação?
- [ ] O texto dos botões descreve claramente a ação realizada?
- [ ] O usuário recebe feedback visual imediato para toda ação?
- [ ] Formulários não perdem dados sem aviso de confirmação?
- [ ] O breadcrumb está presente em páginas internas?
- [ ] A hierarquia visual guia o olhar para a ação principal?

### Código

- [ ] O CSS utiliza variáveis definidas em `base.css` (sem hardcode)?
- [ ] O JavaScript usa `addEventListener` (sem eventos inline no HTML)?
- [ ] O template usa `{% include %}` para componentes reutilizáveis?
- [ ] O arquivo CSS da tela está na pasta `static/css/pages/`?

---

## Histórico de Versões

| Versão | Data | Descrição | Autor |
|---|---|---|---|
| 1.0 | Set/2026 | Versão inicial do documento | Equipe |

---

> **Este documento é vivo.** Qualquer decisão de design tomada durante o desenvolvimento que não esteja aqui documentada deve ser incorporada ao documento antes de ser implementada. Dúvidas sobre decisões visuais devem ser resolvidas com referência a este documento primeiro.
