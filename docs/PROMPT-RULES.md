# PROMPT-RULES.md — Regras do Projeto para Colar no Chat da IA

> Copie e cole este arquivo **no início de qualquer conversa com uma IA** sobre este projeto.
> Versão compacta do `AI-STANDARDS.md` — otimizada para caber em um contexto de chat.

---

## CONTEXTO DO PROJETO

Você está trabalhando no **Marketplace de Calçados** — projeto acadêmico Django.

- Plataforma web para clientes comprarem calçados e vendedores gerenciarem produtos.
- Dois perfis: `CLIENT` (compra) e `SELLER` (vende).
- Documentação completa em `docs/`. Consulte SEMPRE antes de implementar qualquer coisa.

---

## STACK TECNOLÓGICA (não altere sem justificativa)

| Camada | Tecnologia |
|---|---|
| Backend | Python 3.11+ / Django 4.2 LTS |
| Banco | PostgreSQL 14+ (NUNCA SQLite) |
| Driver BD | psycopg2-binary |
| Frontend | HTML + CSS vanilla + JavaScript ES6+ nativo |
| Templates | Django Templates (MVT puro — sem DRF, sem API REST) |
| Env vars | django-environ (.env — nunca commitado) |

---

## ESTRUTURA DO PROJETO

```
config/          → settings.py, urls.py, wsgi.py, asgi.py
apps/
  users/         → CustomUser (CLIENT|SELLER), SellerProfile
  products/      → Product, Category, ProductImage, Stock
  cart/          → Cart (1:1 com User), CartItem
  orders/        → Order, OrderItem
docs/            → documentação oficial
tests/           → test_foundation.py + tests/<app>/
templates/       → base.html, partials/, home/, products/, cart/, orders/, users/, seller/
static/css/      → base.css, components/, pages/
```

**Dependências entre apps (não violar):**
`users ← products ← cart` e `products ← orders`
Apps de nível superior NUNCA importam de nível inferior.

---

## PADRÕES DE CÓDIGO

### Python
- PEP 8: 4 espaços, máx 88 chars por linha
- Classes: `PascalCase` | Funções/variáveis: `snake_case` | Constantes: `UPPER_SNAKE`
- Docstrings em **português** (Google Style: Args / Returns)
- Importações: stdlib → third-party → local

### Django
- **Models:** sempre `__str__`, `verbose_name`, `verbose_name_plural`, `ordering` na Meta
- `auto_now_add=True` para `created_at`, `auto_now=True` para `updated_at`
- **NUNCA** `FloatField` para preços — sempre `DecimalField`
- **NUNCA** expor exceções do banco ao usuário
- `get_object_or_404()` ao buscar por PK
- `@login_required` em views protegidas
- `ModelForm` quando formulário reflete um Model; validar em `clean()`
- FBV preferidas; CBVs quando há padrão repetitivo
- Cada app tem seu próprio `urls.py`; `config/urls.py` usa `include()`
- URLs com nome: use hifens — `name='product-detail'` (não underscore, não camelCase)

### CSS
- **SEMPRE** usar variáveis CSS — nunca hardcodar valores
- Classes seguem **BEM**: `.block__element--modifier`
- Espaçamento: apenas a escala `--space-1` (4px) a `--space-24` (96px)
- `base.css` carregado primeiro em toda página

### JavaScript
- `addEventListener` — NUNCA eventos inline (`onclick=`)
- Um arquivo `.js` por funcionalidade
- `data-*` attributes para integração HTML/JS

### Templates
- Sempre `{% extends 'base.html' %}`
- Componentes via `{% include 'partials/...' %}` — NUNCA duplicar HTML

---

## BANCO DE DADOS — DECISÕES JÁ TOMADAS (não altere)

| Decisão | Regra |
|---|---|
| CustomUser | `AUTH_USER_MODEL = 'users.CustomUser'` — definido antes da 1ª migration. Não mude. |
| Soft delete | `Product.is_active = False` — NUNCA excluir produto fisicamente. |
| Snapshot de preço | `OrderItem.unit_price` = preço no momento da compra. Imutável após criação. |
| CartItem único | `unique_together = ('cart', 'product', 'size')` — atualizar qty, não inserir duplicata. |
| Chave primária | `BigAutoField` em todos os models. |
| Timestamps | `created_at` (auto_now_add) + `updated_at` (auto_now) em todos os models. |

**Entidades:** CustomUser, SellerProfile, Category, Product, ProductImage, Stock, Cart, CartItem, Order, OrderItem

**Status de pedido:** `PENDING → CONFIRMED → SHIPPED → DELIVERED` | `CANCELLED`

---

## DESIGN SYSTEM — NEO-BRUTALISM + STREETWEAR

### Cores (tokens obrigatórios — nunca HEX direto no CSS)
```
--color-bg:        #F5F0E8   ← fundo de página (creme, nunca branco puro)
--color-primary:   #0D0D0D   ← texto, bordas, botão primário
--color-accent:    #FF3B00   ← destaque, CTAs, ofertas
--color-secondary: #1A1A1A   ← texto secundário
--color-surface:   #FFFFFF   ← cards, inputs, modais
--color-muted:     #8C8C8C   ← textos de apoio, placeholders
--color-success:   #1A8C4E
--color-error:     #CC2200
--color-warning:   #E8A000
--color-info:      #1A5FA8
```

### Tipografia
- Títulos (H1–H4): **Space Grotesk** (Google Fonts) → `--font-heading`
- Textos/interface: **Inter** (Google Fonts) → `--font-body`

### Bordas e Sombras (Neo-Brutalism — não altere o conceito)
```
--border-width:   2px   (padrão de todos os componentes interativos)
--border-color:   #0D0D0D
--border-radius:  0px   (regra geral — exceção: badges com 2px)
--shadow-sm:  2px 2px 0px #0D0D0D
--shadow-md:  3px 3px 0px #0D0D0D  ← botões padrão
--shadow-lg:  4px 4px 0px #0D0D0D  ← cards
--shadow-xl:  6px 6px 0px #0D0D0D  ← modais
```
**Sombras são SÓLIDAS (sem blur).** Este é o elemento definidor do projeto.

### Hover de botões e cards
```css
/* Hover: componente levanta -2px, sombra aumenta */
transform: translate(-2px, -2px);
box-shadow: var(--shadow-hover);  /* 6px 6px 0px */
/* Active: componente afunda +2px */
transform: translate(2px, 2px);
box-shadow: var(--shadow-active); /* 1px 1px 0px */
transition: 150ms ease;
```

### Responsividade (Mobile-First obrigatório)
- Breakpoints: 640px / 768px / 1024px / 1280px / 1536px
- Tela deve funcionar em **375px mínimo**

### Acessibilidade (WCAG AA — obrigatório)
- Contraste texto: mínimo 4.5:1
- Todo `<input>` com `<label>` via `for`/`id`
- Áreas clicáveis: mínimo 44×44px
- `alt` em todas as imagens, `aria-label` em ícones sem texto
- `:focus-visible { outline: 3px solid var(--color-accent); outline-offset: 2px; }`

---

## NOMENCLATURA

### Git
```
Branches:  feature/nome-da-funcionalidade
Commits:   feat: adicionar listagem de produtos    ← imperativo, português
           fix: corrigir calculo do carrinho
           docs: atualizar readme
           test: adicionar testes para pedidos
           refactor: extrair logica de desconto
           chore: atualizar requirements.txt
```

### Nomenclatura de produtos
`[Marca] + [Modelo] + [Genero]` → Ex: `Nike Air Max 270 Masculino`
Gêneros válidos: `Masculino`, `Feminino`, `Unissex`, `Infantil`

---

## REGRAS DE NEGÓCIO

1. Um usuário é CLIENT **ou** SELLER — não existe perfil duplo.
2. Vendedor só gerencia **seus próprios** produtos e pedidos.
3. Produto desativado: `is_active = False` (nunca delete físico).
4. Carrinho: 1 por usuário (1:1). Mesmo produto+tamanho → atualizar qty.
5. Pedido: ao finalizar, descontar estoque automaticamente.
6. Categorias: gerenciadas pelo administrador, não pelo vendedor.
7. Nunca confiar em dados do cliente sem validação via Django Forms.

---

## COMPONENTES — NÃO DUPLICAR

| Componente | Template partial | Obrigatório em |
|---|---|---|
| Navbar | `partials/navbar.html` | Todas as páginas |
| Footer | `partials/footer.html` | Todas as páginas públicas |
| Breadcrumb | `partials/breadcrumb.html` | Produtos, carrinho, área do vendedor |
| Product Card | `partials/product_card.html` | TODAS as listagens de produtos |
| Alert | `partials/alert.html` | Mensagens persistentes |
| Toast | `partials/toast.html` | Notificações temporárias (3s) |

---

## FORA DO ESCOPO (não implementar)

- App mobile nativo
- API REST (DRF)
- Inteligência artificial para recomendação
- Analytics avançado de vendas
- Logística complexa
- Integrações de pagamento externas (apenas checkout simples)

---

## O QUE A IA NUNCA DEVE FAZER

- Criar API REST com DRF
- Usar SQLite no lugar de PostgreSQL
- Usar `FloatField` para preços
- Usar jQuery ou libs JS externas
- Usar TailwindCSS
- Hardcodar cores/espaçamentos/sombras no CSS
- `border-radius` > 4px em cards ou botões
- Sombras com blur (box-shadow com valor de blur)
- Duplicar HTML de componentes em vez de usar `{% include %}`
- Colocar lógica de negócio em templates
- Commitar `.env` ou credenciais
- Alterar `AUTH_USER_MODEL` após migrations existirem
- Excluir produtos fisicamente (usar soft delete)
- Usar eventos JS inline (`onclick=`)
- Inventar padrões para preencher lacunas — registrar a lacuna explicitamente

---

## ANTES DE IMPLEMENTAR QUALQUER COISA

1. Leia a seção relevante de `docs/` (architecture.md, design-system.md, development.md)
2. Verifique se já existe implementação semelhante no projeto
3. Siga os padrões existentes — não crie soluções paralelas
4. Quando algo não estiver definido, diga explicitamente e proponha uma solução como sugestão
5. Implemente apenas o que está no escopo da Sprint atual

---

## LACUNAS RESOLVIDAS (não reabrir)

| Lacuna | Decisão |
|--------|---------|
| Sistema de login: e-mail vs. username | Login por e-mail — `EmailBackend`, `USERNAME_FIELD = 'email'`, email único. |
| Endereço de entrega no checkout | Modelo `Address` com FK para `CustomUser`. Múltiplos endereços, campo `is_default`. |
| Como funciona o pagamento | Pagamento **simulado** — campos `payment_method` e `payment_status` em `Order`. Sem gateway real. |
| Política de frete | `frete = shipping_distance_km × shipping_rate_per_km` — ambos definidos pelo vendedor em `SellerProfile`. |

---

## LACUNAS CONHECIDAS (não definidas — sinalizar ao encontrar)

- Valores possíveis de `Stock.size` (CharField sem enum definido — atualmente texto livre: 38, 39, M, G, etc.)
- Número de itens por página nas listagens

---

*Referência completa: `docs/architecture.md` | Design System: `docs/design-system.md`*
