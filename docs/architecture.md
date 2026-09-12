# Arquitetura do Sistema — Marketplace de Calçados

> Versão: 1.0 | Sprint 1

---

## Visão Geral

O marketplace de calçados segue uma arquitetura **monolítica web** com Django, adequada para
a escala e complexidade do projeto acadêmico. A arquitetura foi escolhida por:

- Simplicidade operacional (um único processo)
- Coesão entre camadas (models, views, templates no mesmo framework)
- Facilidade de manutenção pela equipe
- Suporte nativo do Django para autenticação, admin, ORM e migrations

---

## Diagrama de Arquitetura

```
┌─────────────────────────────────────────────────────────┐
│                    CLIENTE (Browser)                    │
│            Chrome / Firefox / Edge / Safari             │
└─────────────────────────┬───────────────────────────────┘
                          │ HTTP/HTTPS
                          ▼
┌─────────────────────────────────────────────────────────┐
│                   DJANGO (Backend)                      │
│                                                         │
│  ┌─────────┐   ┌──────────┐   ┌──────────────────────┐ │
│  │  URLs   │──▶│  Views   │──▶│  Templates (HTML)    │ │
│  └─────────┘   └────┬─────┘   └──────────────────────┘ │
│                     │                                   │
│  ┌──────────────────▼────────────────────────────────┐  │
│  │                   Models (ORM)                    │  │
│  │  users │ products │ cart │ orders                 │  │
│  └──────────────────┬────────────────────────────────┘  │
│                     │                                   │
└─────────────────────┼───────────────────────────────────┘
                      │ psycopg2
                      ▼
┌─────────────────────────────────────────────────────────┐
│                   PostgreSQL                            │
│           Banco de dados relacional principal           │
└─────────────────────────────────────────────────────────┘
```

---

## Responsabilidades do Django

| Responsabilidade | Mecanismo Django |
|------------------|-----------------|
| Autenticação e sessão | `django.contrib.auth` + `AbstractUser` |
| Autorização por tipo de usuário | `user_type` no `CustomUser` |
| Regras de negócio | Models e Views |
| Comunicação com banco | ORM + `psycopg2` |
| Proteção CSRF | `CsrfViewMiddleware` |
| Administração | `django.contrib.admin` |
| Migrations | `django.db.migrations` |
| Arquivos estáticos | `django.contrib.staticfiles` |

---

## Estrutura de Apps

```
apps/
├── users/      → Usuários, autenticação e perfil do vendedor
├── products/   → Catálogo, categorias, imagens e estoque
├── cart/       → Carrinho de compras e seus itens
└── orders/     → Pedidos e itens de pedido
```

### Dependências entre Apps

```
users  ←──── products  ←──── cart
                │
                └──────────── orders
```

> **Regra**: apps de nível superior não importam de apps de nível inferior.
> `products` referencia `users` (vendedor). `cart` e `orders` referenciam `products`.

---

## Modelo de Dados — Entidades Principais

```
CustomUser
├── user_type (CLIENT | SELLER)
└── SellerProfile (1:1, apenas vendedores)
    └── store_name, cnpj, description

Category
└── name, slug, description

Product
├── FK → CustomUser (vendedor)
├── FK → Category
├── name, brand, price, is_active
├── ProductImage (1:N)
│   └── image, alt_text, order
└── Stock (1:N, por tamanho)
    └── size, quantity

Cart (1:1 com usuário)
└── CartItem (1:N)
    ├── FK → Product
    ├── size, quantity
    └── subtotal (property)

Order
├── FK → CustomUser (cliente)
├── status (PENDING|CONFIRMED|SHIPPED|DELIVERED|CANCELLED)
├── total (snapshot)
└── OrderItem (1:N)
    ├── FK → Product (SET_NULL)
    ├── size, quantity
    └── unit_price (snapshot)
```

---

## Decisões de Design

### 1. CustomUser antes da primeira migration
O modelo `CustomUser` foi criado e configurado como `AUTH_USER_MODEL` antes de qualquer migration.
Mudar o modelo de usuário depois da primeira migration é extremamente complexo.

### 2. Snapshot de preço em OrderItem
`OrderItem.unit_price` armazena o preço no momento da compra.
Se o vendedor alterar o preço do produto, pedidos anteriores não são afetados.

### 3. Soft delete em produtos
`Product.is_active = False` desativa o produto sem excluí-lo.
Isso preserva a integridade referencial com pedidos e itens de carrinho existentes.

### 4. CartItem.unique_together
Evita que o mesmo produto no mesmo tamanho apareça duas vezes no carrinho.
A lógica de "atualizar quantidade" substituirá inserção duplicada.

### 5. Sem microsserviços
Arquitetura monolítica Django. Adequada ao escopo e à equipe do projeto acadêmico.

---

## Segurança

- `SECRET_KEY` carregada via variável de ambiente
- `DEBUG=False` em produção
- Senhas hasheadas via PBKDF2 (AbstractUser)
- Proteção CSRF ativa por padrão (`CsrfViewMiddleware`)
- Validação de dados via Django Forms
- `.env` não versionado no Git

---

## Configuração de Ambiente

```
Desenvolvimento: DEBUG=True, banco local PostgreSQL
Produção:        DEBUG=False, ALLOWED_HOSTS configurado, banco externo
```
