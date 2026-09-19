# Fatiamento Vertical — Marketplace de Calçados

> Estratégia de desenvolvimento incremental por fatias funcionais completas.
> Cada fatia entrega valor ao usuário de ponta a ponta (modelo → view → template).
> Versão: 1.1 | Atualizado na Sprint 2 (decisões de negócio)

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

### Fatia 1 — Usuários e Endereços
**Sprint sugerida:** Sprint 2

**Objetivo:** Usuário pode criar conta, fazer login por e-mail, logout, ver seu perfil e gerenciar endereços.

**Requisitos cobertos:** RF01, RF02, RF03, RF21, RF22, RNF06, RNF07

**Entregáveis:**
- [ ] Formulário de cadastro (Cliente ou Vendedor) com **e-mail como identificador**
- [ ] View de login por **e-mail** (usando `EmailBackend`) e logout
- [ ] Página de perfil do usuário
- [ ] Criação automática do `SellerProfile` para vendedores (com campos de frete)
- [ ] CRUD de endereços de entrega (`Address`)
- [ ] Restrição de acesso via `@login_required`
- [ ] Testes: cadastro, login por e-mail, logout, acesso negado sem login, CRUD de endereços

**Componentes Django envolvidos:**
- `apps/users/views.py`
- `apps/users/forms.py`
- `apps/users/urls.py`
- `apps/users/backends.py` (já implementado)
- `templates/users/`

**Nota:** O `username` é preenchido automaticamente — não deve ser exposto no formulário público.

---

### Fatia 2 — Catálogo de Produtos
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
- [ ] Configuração de frete no painel do vendedor (`shipping_rate_per_km`, `shipping_distance_km`)
- [ ] Testes: CRUD de produto, acesso restrito ao vendedor, configuração de frete

**Componentes Django envolvidos:**
- `apps/products/views.py`
- `apps/products/forms.py`
- `apps/products/urls.py`
- `templates/products/`

---

### Fatia 3 — Busca e Filtros
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

### Fatia 4 — Carrinho
**Sprint sugerida:** Sprint 4

**Objetivo:** Cliente adiciona, altera e remove itens do carrinho e vê o subtotal.

**Requisitos cobertos:** RF11, RF12, RF13, RF14

**Entregáveis:**
- [ ] Adicionar produto ao carrinho (cria Cart se não existir)
- [ ] Alterar quantidade de um item
- [ ] Remover item do carrinho
- [ ] Página do carrinho com subtotais e subtotal total (sem frete)
- [ ] Validação de estoque antes de adicionar
- [ ] Testes: adicionar, atualizar, remover, calcular subtotal

**Componentes Django envolvidos:**
- `apps/cart/views.py`
- `apps/cart/urls.py`
- `templates/cart/`

---

### Fatia 5 — Checkout e Pedidos
**Sprint sugerida:** Sprint 4 ou Sprint 5

**Objetivo:** Cliente finaliza compra com seleção de endereço, cálculo de frete e pagamento simulado. Pedido é registrado, estoque é descontado.

**Requisitos cobertos:** RF15, RF16, RF17, RF20, RF23, RF24, RF25

**Fluxo do checkout:**
```
Usuário autenticado
  → Visualiza carrinho
  → Seleciona endereço de entrega (Address cadastrado)
  → Sistema calcula frete: SellerProfile.shipping_distance_km × shipping_rate_per_km
  → Sistema exibe: subtotal + frete + total
  → Usuário seleciona método de pagamento (simulado: cartão, PIX, boleto)
  → Usuário confirma pedido
  → Sistema cria Order com payment_status = APPROVED (simulado)
  → Sistema desconta estoque
  → Usuário vê confirmação do pedido
```

**Entregáveis:**
- [ ] Seleção de endereço de entrega no checkout (lista de endereços do usuário)
- [ ] Exibição do frete calculado (distância do vendedor × taxa/km)
- [ ] Seleção de método de pagamento simulado (cartão, PIX, boleto)
- [ ] Confirmação visual de "pagamento aprovado" (simulado — sem cobrança real)
- [ ] Criação do pedido com snapshot de preços, frete, endereço e pagamento
- [ ] Desconto automático do estoque ao finalizar compra
- [ ] Histórico de pedidos do cliente
- [ ] Página de confirmação de pedido
- [ ] Testes: checkout completo, desconto de estoque, histórico, frete calculado, pagamento simulado

**Nota obrigatória em templates:** Exibir aviso de que o pagamento é simulado e não há cobrança real.

**Componentes Django envolvidos:**
- `apps/orders/views.py`
- `apps/orders/urls.py`
- `templates/orders/`

---

### Fatia 6 — Área do Vendedor
**Sprint sugerida:** Sprint 5 ou Sprint 6

**Objetivo:** Vendedor visualiza e atualiza status dos pedidos relacionados aos seus produtos.

**Requisitos cobertos:** RF18, RF19

**Entregáveis:**
- [ ] Dashboard do vendedor com pedidos dos seus produtos
- [ ] Atualização de status do pedido (Confirmado → Em trânsito → Entregue)
- [ ] Histórico de pedidos por produto
- [ ] Visualização do endereço de entrega do comprador
- [ ] Testes: acesso restrito ao vendedor, atualização de status

**Componentes Django envolvidos:**
- `apps/orders/views.py` (extensão para vendedor)
- `templates/sellers/`

---

## Resumo por Sprint

> **Documento operacional oficial: [`sprints.md`](sprints.md)**
> Este arquivo documenta a estratégia de fatiamento. O planejamento detalhado de tarefas, responsabilidades e DoD estão em `sprints.md`.

| Sprint | Fatia(s) | RFs cobertos |
|--------|----------|--------------|
| Sprint 1 | Fundação (concluída) | — |
| Sprint 2 | Fatia 1 (Usuários + Autenticação + Endereços) | RF01, RF02, RF03, RF21, RF22 |
| Sprint 3 | Fatia 2 (Catálogo + Vendedor-Produto) | RF04, RF05, RF08, RF09, RF10, RF20 |
| Sprint 4 | Fatia 3 (Busca/Filtros) + Fatia 4 (Carrinho) | RF06, RF07, RF11, RF12, RF13, RF14 |
| Sprint 5 | Fatia 5 (Checkout + Pedidos) | RF15, RF16, RF17, RF20, RF23, RF24, RF25 |
| Sprint 6 | Fatia 6 (Área do Vendedor) + Refinamentos | RF18, RF19 |
