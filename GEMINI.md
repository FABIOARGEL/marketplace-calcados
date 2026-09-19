# Regras do Projeto — Marketplace de Calcados

Voce esta trabalhando no **Marketplace de Calcados**, projeto academico Django.
Leia `docs/AI-STANDARDS.md` para referencia completa. Este arquivo e um resumo operacional.

## Stack (nao altere sem justificativa)

- Backend: Python 3.11+ / Django 4.2 LTS
- Banco: PostgreSQL 14+ (NUNCA SQLite)
- Frontend: HTML + CSS vanilla + JavaScript ES6+ nativo (sem jQuery, sem Tailwind, sem DRF)
- Templates: Django Templates — MVT puro, sem API REST separada
- Env vars: django-environ (.env nunca commitado)

## Estrutura de apps e dependencias

```
config/   → settings.py, urls.py
apps/
  users/    → CustomUser (CLIENT|SELLER), SellerProfile
  products/ → Product, Category, ProductImage, Stock
  cart/     → Cart (1:1 com User), CartItem
  orders/   → Order, OrderItem
```

Dependencias: `users <- products <- cart` e `products <- orders`
Apps superiores NUNCA importam de apps inferiores.

## Antes de implementar qualquer coisa

1. Leia a secao relevante de `docs/` (architecture.md, design-system.md, development.md)
2. Verifique se ja existe implementacao semelhante
3. Siga os padroes existentes — nao crie solucoes paralelas
4. Implemente apenas o escopo da Sprint atual
5. Quando algo nao estiver definido, diga explicitamente e proponha como sugestao

## Codigo Python / Django

- PEP 8: 4 espacos, max 88 chars
- Classes: PascalCase | Funcoes/variaveis: snake_case | Constantes: UPPER_SNAKE
- Docstrings em portugues (Google Style)
- Models: sempre `__str__`, `verbose_name`, `verbose_name_plural`, `ordering`
- `auto_now_add` para created_at, `auto_now` para updated_at
- NUNCA `FloatField` para precos — sempre `DecimalField`
- NUNCA expor excecoes do banco ao usuario
- `get_object_or_404()` ao buscar por PK
- `@login_required` em views protegidas
- Cada app tem seu proprio `urls.py`; nomes de URL com hifens: `name='product-detail'`
- FBV preferidas; CBVs quando ha padrao repetitivo

## CSS

- SEMPRE variáveis CSS — nunca valores hardcoded
- Classes seguem BEM: `.block__element--modifier`
- Escala de espacamento: `--space-1` (4px) a `--space-24` (96px) — sem valores arbitrarios
- `base.css` carregado primeiro em toda pagina

## Templates

- Sempre `{% extends 'base.html' %}`
- Componentes via `{% include 'partials/...' %}` — NUNCA duplicar HTML

## JavaScript

- `addEventListener` — NUNCA eventos inline (`onclick=`)
- Um arquivo `.js` por funcionalidade | `data-*` para integracao HTML/JS

## Banco de dados — decisoes imutaveis

| Decisao | Regra |
|---|---|
| CustomUser | AUTH_USER_MODEL ja definido antes da 1a migration. Nao mude. |
| Soft delete | `Product.is_active = False` — NUNCA excluir produto fisicamente |
| Snapshot de preco | `OrderItem.unit_price` = preco no momento da compra. Imutavel. |
| CartItem unico | `unique_together = ('cart', 'product', 'size')` — atualizar qty, nao inserir duplicata |
| Chave primaria | BigAutoField em todos os models |

## Design System — Neo-Brutalism + Streetwear

Conceito: bordas marcadas, sombras solidas (sem blur), fundo creme, alto contraste.

### Cores (tokens — nunca HEX direto no CSS)
```
--color-bg:      #F5F0E8   (fundo — nunca branco puro)
--color-primary: #0D0D0D   (texto, bordas, botao primario)
--color-accent:  #FF3B00   (destaque, CTA, ofertas)
--color-surface: #FFFFFF   (cards, inputs, modais)
--color-muted:   #8C8C8C   (textos de apoio)
--color-success: #1A8C4E | --color-error: #CC2200
--color-warning: #E8A000  | --color-info:  #1A5FA8
```

### Tipografia
- Titulos: **Space Grotesk** (`--font-heading`)
- Textos: **Inter** (`--font-body`)

### Bordas e Sombras (definidores do neo-brutalism)
```
--border-width:  2px sólida #0D0D0D (todos os componentes interativos)
--border-radius: 0px (excecao: badges com 2px)
--shadow-md: 3px 3px 0px #0D0D0D   (botoes padrao)
--shadow-lg: 4px 4px 0px #0D0D0D   (cards)
--shadow-xl: 6px 6px 0px #0D0D0D   (modais)
```
Sombras SAO SOLIDAS (sem blur). Hover: transform: translate(-2px, -2px) + shadow aumenta.

### Responsividade
- Mobile-first obrigatorio | Breakpoints: 640 / 768 / 1024 / 1280px
- Minimo: 375px sem quebrar

### Acessibilidade (WCAG AA obrigatorio)
- Contraste 4.5:1 | labels em inputs | aria-label em icones | areas 44x44px min

## Git e Commits

```
Branches: feature/nome-da-funcionalidade
Commits:  feat: adicionar listagem de produtos   (imperativo, portugues)
          fix: corrigir calculo do carrinho
          docs: atualizar readme
          test: adicionar testes para pedidos
          refactor: extrair logica de desconto
          chore: atualizar requirements.txt
```

Nunca commitar: .env, senhas, credenciais, arquivos de IDE.

## Regras de negocio

1. Um usuario e CLIENT ou SELLER — sem perfil duplo
2. Vendedor so gerencia seus proprios produtos e pedidos
3. Soft delete: `is_active = False` (nunca delete fisico em produto)
4. Carrinho: 1 por usuario. Mesmo produto+tamanho → atualizar qty
5. Pedido: descontar estoque ao finalizar
6. Categorias: gerenciadas pelo admin, nao pelo vendedor
7. Nunca confiar em dados do cliente sem validacao Django Forms
8. Login SEMPRE por e-mail — nunca expor campo username ao usuario
9. Usuario pode ter MULTIPLOS enderecos de entrega (modelo Address)
10. Frete = shipping_distance_km × shipping_rate_per_km (ambos configurados pelo vendedor)
11. Pagamento e SIMULADO — NUNCA integrar gateway real nesta versao

## O que a IA NUNCA deve fazer

- Criar API REST (DRF)
- Usar SQLite
- Usar FloatField para precos
- Usar jQuery ou libs JS externas
- Usar TailwindCSS
- Hardcodar cores/espacamentos/sombras no CSS
- border-radius > 4px em cards/botoes
- Sombras com blur
- Duplicar HTML de componentes (usar {% include %})
- Logica de negocio em templates
- Commitar .env ou credenciais
- Excluir produtos fisicamente
- Usar onclick= inline
- Inventar padroes para lacunas — registrar explicitamente

## Decisoes de banco de dados — imutaveis

| Decisao | Regra |
|---|---|
| CustomUser | AUTH_USER_MODEL ja definido antes da 1a migration. Nao mude. |
| Login | Por EMAIL (USERNAME_FIELD = 'email'). Email unico. Username preenchido automaticamente. |
| Soft delete | `Product.is_active = False` — NUNCA excluir produto fisicamente |
| Snapshot de preco | `OrderItem.unit_price` = preco no momento da compra. Imutavel. |
| CartItem unico | `unique_together = ('cart', 'product', 'size')` — atualizar qty, nao inserir duplicata |
| Chave primaria | BigAutoField em todos os models |
| Enderecos | Modelo `Address` separado com FK para CustomUser. Nunca campo avulso. |
| Frete | `SellerProfile.shipping_distance_km × shipping_rate_per_km`. Distancia definida pelo vendedor. |
| Pagamento | SIMULADO. Sem gateway real. Campos `payment_method` e `payment_status` em Order apenas para registro academico. |

## Lacunas conhecidas (sinalizar ao encontrar)

- Valores possiveis de `Stock.size` (CharField sem enum definido)
- Numero de itens por pagina nas listagens
- Calculo de distancia real via API de mapas (fora do escopo desta versao)

## Lacunas RESOLVIDAS (nao reabrir)

| Lacuna | Decisao |
|---|---|
| Login por e-mail vs. username | Login por e-mail — EmailBackend, email unico, username automatico |
| Endereco de entrega no checkout | Modelo Address com FK para CustomUser, multiplos enderecos |
| Como funciona o pagamento | Pagamento SIMULADO — sem processamento financeiro real |
| Politica de frete | Frete = distancia_km x valor_por_km, ambos definidos pelo vendedor |

---
Referencia completa: `docs/architecture.md` | Design System: `docs/design-system.md`
