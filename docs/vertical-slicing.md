# Fatiamento Vertical — Marketplace de Calçados

> Estratégia de desenvolvimento incremental por fatias funcionais completas.
> Cada fatia entrega valor ao usuário de ponta a ponta (modelo → view → template).

---

## O que é Fatiamento Vertical?

Em vez de desenvolver todas as camadas de uma vez (todos os modelos, depois todas as views, etc.),
o fatiamento vertical entrega **uma funcionalidade completa** por vez — da base de dados à interface.

Isso permite:
- Entregar valor a cada Sprint
- Testar de ponta a ponta antes de avançar
- Detectar problemas de integração cedo
- Demonstrar progresso concreto

---

## Fatias Planejadas

---

### 🍕 Fatia 1 — Usuários
**Sprint sugerida:** Sprint 2

**Objetivo:** Usuário pode criar conta, fazer login, logout e ver seu perfil.

**Requisitos cobertos:** RF01, RF02, RF03, RNF06, RNF07

**Entregáveis:**
- [ ] Formulário de cadastro (Cliente ou Vendedor)
- [ ] View de login/logout usando `django.contrib.auth`
- [ ] Página de perfil do usuário
- [ ] Criação automática do `SellerProfile` para vendedores
- [ ] Restrição de acesso via `@login_required`
- [ ] Testes: cadastro, login, logout, acesso negado sem login

**Componentes Django envolvidos:**
- `apps/users/views.py`
- `apps/users/forms.py`
- `apps/users/urls.py`
- `templates/users/`

---

### 🍕 Fatia 2 — Catálogo de Produtos
**Sprint sugerida:** Sprint 2 ou Sprint 3

**Objetivo:** Vendedor cadastra produtos; cliente visualiza o catálogo e detalhes.

**Requisitos cobertos:** RF04, RF05, RF08, RF09, RF10, RF20

**Entregáveis:**
- [ ] Listagem de produtos ativos no catálogo
- [ ] Página de detalhes do produto (nome, preço, marca, imagens, tamanhos)
- [ ] Formulário para vendedor cadastrar produto
- [ ] Formulário para vendedor editar produto
- [ ] Botão de desativar produto (soft delete com `is_active=False`)
- [ ] Controle de estoque por tamanho
- [ ] Testes: CRUD de produto, acesso restrito ao vendedor

**Componentes Django envolvidos:**
- `apps/products/views.py`
- `apps/products/forms.py`
- `apps/products/urls.py`
- `templates/products/`

---

### 🍕 Fatia 3 — Busca e Filtros
**Sprint sugerida:** Sprint 3

**Objetivo:** Cliente pesquisa e filtra produtos no catálogo.

**Requisitos cobertos:** RF06, RF07

**Entregáveis:**
- [ ] Campo de busca por nome/descrição (ORM `icontains`)
- [ ] Filtros por categoria, marca, tamanho e faixa de preço
- [ ] URL com parâmetros de query string (`?q=tênis&categoria=esporte`)
- [ ] Paginação dos resultados
- [ ] Testes: busca com resultados, sem resultados, combinação de filtros

**Componentes Django envolvidos:**
- `apps/products/views.py` (extensão)
- `templates/products/list.html` (extensão)

---

### 🍕 Fatia 4 — Carrinho
**Sprint sugerida:** Sprint 4

**Objetivo:** Cliente adiciona, altera e remove itens do carrinho e vê o total.

**Requisitos cobertos:** RF11, RF12, RF13, RF14

**Entregáveis:**
- [ ] Adicionar produto ao carrinho (cria Cart se não existir)
- [ ] Alterar quantidade de um item
- [ ] Remover item do carrinho
- [ ] Página do carrinho com subtotais e total
- [ ] Validação de estoque antes de adicionar
- [ ] Testes: adicionar, atualizar, remover, calcular total

**Componentes Django envolvidos:**
- `apps/cart/views.py`
- `apps/cart/urls.py`
- `templates/cart/`

---

### 🍕 Fatia 5 — Pedidos
**Sprint sugerida:** Sprint 4 ou Sprint 5

**Objetivo:** Cliente finaliza compra, pedido é registrado, estoque é descontado.

**Requisitos cobertos:** RF15, RF16, RF17, RF20

**Entregáveis:**
- [ ] Finalização do carrinho → criação do pedido
- [ ] Desconto automático do estoque ao finalizar compra
- [ ] Histórico de pedidos do cliente
- [ ] Página de confirmação de pedido
- [ ] Testes: finalizar compra, desconto de estoque, histórico

**Componentes Django envolvidos:**
- `apps/orders/views.py`
- `apps/orders/urls.py`
- `templates/orders/`

---

### 🍕 Fatia 6 — Área do Vendedor
**Sprint sugerida:** Sprint 5 ou Sprint 6

**Objetivo:** Vendedor visualiza e atualiza status dos pedidos relacionados aos seus produtos.

**Requisitos cobertos:** RF18, RF19

**Entregáveis:**
- [ ] Dashboard do vendedor com pedidos dos seus produtos
- [ ] Atualização de status do pedido (Confirmado → Em trânsito → Entregue)
- [ ] Histórico de pedidos por produto
- [ ] Testes: acesso restrito ao vendedor, atualização de status

**Componentes Django envolvidos:**
- `apps/orders/views.py` (extensão para vendedor)
- `templates/sellers/`

---

## Resumo por Sprint

| Sprint | Fatia(s) | RFs cobertos |
|--------|----------|--------------|
| Sprint 1 | Fundação (esta sprint) | — |
| Sprint 2 | Fatia 1 (Usuários) + Fatia 2 (Catálogo) | RF01–RF05, RF08–RF10 |
| Sprint 3 | Fatia 3 (Busca e Filtros) | RF06, RF07 |
| Sprint 4 | Fatia 4 (Carrinho) + Fatia 5 (Pedidos) | RF11–RF17, RF20 |
| Sprint 5 | Fatia 6 (Área do Vendedor) | RF18, RF19 |
| Sprint 6 | Refinamentos, testes, melhorias de UX | — |
