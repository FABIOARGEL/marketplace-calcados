# Sprints — Marketplace de Calçados

> Versão: 1.0 | Data: Setembro/2026
> Documento de planejamento técnico e gerencial — 6 Sprints

---

## 1. Visão Geral

Este documento define o **planejamento completo de 6 Sprints** para o desenvolvimento do Marketplace de Calçados Online. Cada Sprint foi construída com base na análise de dependências técnicas, fatiamento vertical e ordem natural de construção de um marketplace.

**Premissas observadas:**
- A Sprint 1 (Fundação) **já está concluída**: todos os models estão implementados e migrados, o admin está configurado, o `EmailBackend` funciona e os testes de fundação passam.
- **Nenhuma view, form, URL de app, template, CSS ou JS existe** — todo o desenvolvimento funcional começa na Sprint 2.
- O projeto segue o padrão MVT (Model-View-Template) do Django, sem API REST.
- Pagamento é **simulado** — sem gateway real.
- Frete é **simulado** — distância informada pelo vendedor, sem API de mapas.

---

## 2. Objetivo do Projeto

Desenvolver um **marketplace de calçados funcional** como projeto acadêmico, permitindo:
- Compradores: navegar, buscar, filtrar, comprar calçados e acompanhar pedidos.
- Vendedores: cadastrar, editar, gerenciar produtos e acompanhar pedidos de seus produtos.
- Fluxo completo de e-commerce: catálogo → carrinho → checkout → pedido → acompanhamento.

---

## 3. Equipe

| Pessoa | Função | Atuação nas Sprints |
|--------|--------|---------------------|
| Fábio Argel | CTO | Arquitetura, revisão técnica, integração, validação, organização, apresentação ao CEO |
| Alessandro | CEO | Validação de entregas, aceite de negócio |
| Paula | DEV | Desenvolvimento de tarefas (backend + frontend) |
| Williams | DEV | Desenvolvimento de tarefas (backend + frontend) |

> **Regra**: Paula e Williams são os desenvolvedores responsáveis pelas tarefas. Fábio atua como CTO e não é alocado como desenvolvedor para equilibrar pontos.

---

## 4. Tecnologias

| Camada | Tecnologia |
|--------|-----------|
| Backend | Python 3.11+ / Django 4.2 LTS |
| Banco de dados | PostgreSQL 14+ (banco: `marketplace_calcados`) |
| Frontend | HTML + CSS vanilla + JavaScript ES6+ nativo |
| Templates | Django Templates (MVT puro) |
| Versionamento | Git / GitHub |
| Gestão | Linear |
| Variáveis de ambiente | django-environ (`.env`) |

---

## 5. Requisitos

### Requisitos Funcionais

| ID | Descrição | Status atual |
|----|-----------|-------------|
| RF01 | Criar conta (e-mail, senha, nome, tipo cliente/vendedor) | Planejado |
| RF02 | Login por e-mail e logout | Planejado |
| RF03 | Visualizar e editar dados cadastrais | Planejado |
| RF04 | Visualizar calçados disponíveis | Planejado |
| RF05 | Visualizar detalhes do calçado | Planejado |
| RF06 | Pesquisar calçados por nome ou descrição | Planejado |
| RF07 | Filtrar por categoria, tamanho, marca, faixa de preço | Planejado |
| RF08 | Vendedor cadastra novos calçados | Planejado |
| RF09 | Vendedor edita seus calçados | Planejado |
| RF10 | Vendedor desativa calçado (soft delete) | Planejado |
| RF11 | Adicionar calçados ao carrinho | Planejado |
| RF12 | Alterar quantidade no carrinho | Planejado |
| RF13 | Remover itens do carrinho | Planejado |
| RF14 | Calcular subtotal do carrinho | Planejado |
| RF15 | Finalizar compra via checkout | Planejado |
| RF16 | Registrar pedidos com snapshot de preço | Planejado |
| RF17 | Consultar histórico de pedidos (cliente) | Planejado |
| RF18 | Vendedor visualiza pedidos de seus produtos | Planejado |
| RF19 | Atualizar status do pedido | Planejado |
| RF20 | Controlar estoque por tamanho | Planejado |
| RF21 | Autenticação por e-mail (único) | Implementado (backend) |
| RF22 | CRUD de endereços de entrega | Planejado |
| RF23 | Selecionar endereço no checkout | Planejado |
| RF24 | Frete = distância_km × valor_por_km (vendedor) | Implementado (modelo) |
| RF25 | Pagamento simulado | Implementado (modelo) |

---

## 6. Análise de Dependências

### 6.1 Grafo de Dependências Técnicas

```
Sprint 1 (Fundação ✅)
  └─► Sprint 2 (Usuários + Autenticação)
        └─► Sprint 3 (Catálogo + Vendedor-Produto)
              └─► Sprint 4 (Busca/Filtros + Carrinho)
                    └─► Sprint 5 (Checkout + Pedidos)
                          └─► Sprint 6 (Dashboard Vendedor + Integração)
```

### 6.2 Dependências entre domínios

| Funcionalidade | Depende de | Justificativa |
|---------------|------------|---------------|
| Login/Cadastro | EmailBackend (pronto) | Views, forms e templates precisam ser criados |
| Perfil do usuário | Login funcional | Só edita perfil quem está autenticado |
| Endereços | Login funcional | Endereço pertence ao usuário |
| Cadastro de produto | Login + SellerProfile | Vendedor precisa estar autenticado e ter perfil |
| Catálogo público | Produtos existirem no banco | Listagem depende de haver dados |
| Busca e filtros | Catálogo funcional | Estende a listagem existente |
| Carrinho | Login + Produto existente | Usuário logado adiciona produto ao carrinho |
| Checkout | Carrinho + Endereço + SellerProfile (frete) | Tudo converge no checkout |
| Pedido | Checkout | Pedido é resultado do checkout |
| Dashboard vendedor | Pedidos existirem + SellerProfile | Vendedor precisa ver pedidos de seus produtos |

### 6.3 Decisões sobre a estrutura das Sprints

A referência sugerida (Fundação → Usuários → Produtos → Vendedor → Compra → Integração) foi **parcialmente ajustada**:

1. **Sprint 3 unifica Catálogo e Vendedor-Produto**: Separar "produtos" e "vendedor cadastra produtos" seria artificial — o vendedor cria o produto e o catálogo exibe. São faces da mesma funcionalidade.

2. **Sprint 4 unifica Busca/Filtros e Carrinho**: Busca e filtros sozinhos seriam uma Sprint subcarregada. O carrinho depende apenas do catálogo (S3) e do login (S2), ambos prontos.

3. **Dashboard do Vendedor ficou na Sprint 6**: RF18 e RF19 exigem que pedidos existam, o que só acontece após Sprint 5.

---

## 7. Estratégia de Fatiamento Vertical

Cada Sprint entrega funcionalidades **de ponta a ponta** — do model (já pronto) até a interface funcional no browser:

```
Model (✅ pronto) → Form → View → URL → Template → CSS → JS → Teste
```

| Sprint | Entrega demonstrável |
|--------|---------------------|
| Sprint 1 ✅ | Projeto Django funcionando, models migrados, admin operacional |
| Sprint 2 | Usuário cria conta, faz login por e-mail, vê perfil, gerencia endereços |
| Sprint 3 | Vendedor cadastra produto, cliente vê catálogo e detalhes do produto |
| Sprint 4 | Cliente busca/filtra produtos e gerencia carrinho de compras |
| Sprint 5 | Cliente finaliza compra com frete, pagamento simulado e vê histórico |
| Sprint 6 | Vendedor gerencia pedidos, sistema integrado e testado end-to-end |

---

## 8. As 6 Sprints

---

### Sprint 1 — Fundação e Arquitetura ✅ CONCLUÍDA

**Objetivo:** Estabelecer a base técnica do projeto — configuração Django, PostgreSQL, estrutura de apps, models, migrations, admin e testes de fundação.

**Status:** ✅ Concluída

**Entregáveis realizados:**
- [x] Projeto Django configurado com django-environ
- [x] PostgreSQL (`marketplace_calcados`) conectado
- [x] 4 apps criados: `users`, `products`, `cart`, `orders`
- [x] Todos os models implementados (CustomUser, SellerProfile, Address, Category, Product, ProductImage, Stock, Cart, CartItem, Order, OrderItem)
- [x] Todas as migrations aplicadas
- [x] EmailBackend para autenticação por e-mail
- [x] Admin configurado para todos os models
- [x] Health check endpoint (`/health/`)
- [x] 15 testes de fundação passando
- [x] Documentação: architecture.md, design-system.md, development.md, requirements.md, vertical-slicing.md

---

### Sprint 2 — Autenticação, Perfil e Endereços

**Objetivo:** Entregar o fluxo completo de identidade do usuário — cadastro, login por e-mail, logout, visualização/edição de perfil, e CRUD de endereços. Ao final, o sistema sabe quem é o usuário e permite acesso autenticado.

**Justificativa da posição:** Toda funcionalidade posterior depende de um usuário autenticado. Login é pré-requisito para: associar produtos ao vendedor, criar carrinho, fazer checkout, gerenciar pedidos. É a primeira camada funcional após a fundação.

**RFs cobertos:** RF01, RF02, RF03, RF21, RF22

**Dependências:** Sprint 1 (models e EmailBackend prontos)

---

#### Tarefa 1 — Estrutura base de templates e CSS

**Responsável:** Paula
**Story Points:** 5
**Tipo:** Frontend / Infraestrutura

##### Objetivo
Criar o `base.html` com layout responsivo, navegação, blocos de conteúdo e o `base.css` com todos os tokens do Design System (cores, tipografia, espaçamentos, bordas, sombras neo-brutalism). Esta base será herdada por todas as páginas do sistema.

##### O que fazer
1. Criar diretório `templates/` na raiz do projeto (já configurado em `settings.py`)
2. Criar `templates/base.html` com:
   - doctype, meta viewport, meta charset
   - links para Google Fonts (Space Grotesk + Inter)
   - bloco `{% block title %}` para título da página
   - bloco `{% block extra_css %}` para CSS específico
   - header com logo/nome do marketplace e navegação principal
   - navegação responsiva (hamburger em mobile)
   - bloco `{% block content %}` para conteúdo da página
   - footer com informações básicas
   - bloco `{% block extra_js %}` para JS específico
   - exibição de `{% if messages %}` (Django messages framework)
3. Criar diretório `static/css/`
4. Criar `static/css/base.css` com todos os tokens do Design System:
   - variáveis CSS (cores, tipografia, espaçamentos, bordas, sombras)
   - reset/normalize básico
   - classes utilitárias de layout (container, grid, flex)
   - estilos globais (body, headings, links, paragraphs)
   - componentes base: botões (`.btn`, `.btn--primary`, `.btn--accent`), inputs, labels
   - responsividade mobile-first com breakpoints 640/768/1024/1280px
5. Criar `static/css/components.css` com estilos de componentes reutilizáveis:
   - cards (`.card`)
   - alertas/mensagens (`.alert`, `.alert--success`, `.alert--error`)
   - formulários (`.form-group`, `.form-field`)
   - badges
6. Criar `templates/partials/header.html` e `templates/partials/footer.html` para inclusão via `{% include %}`
7. Criar `templates/partials/messages.html` para exibição de mensagens Django

##### Dependências
- Nenhuma (primeira tarefa da Sprint)

##### Resultado esperado
Ao carregar qualquer página que estenda `base.html`, o layout completo neo-brutalism será exibido — header, navegação, conteúdo, footer — responsivo e com todos os tokens do Design System aplicados.

##### DoD
- [ ] `base.html` criado com herança de template funcional
- [ ] `base.css` contém todos os tokens do Design System documentados em `design-system.md`
- [ ] Nenhum valor hardcoded — apenas variáveis CSS
- [ ] Classes seguem convenção BEM
- [ ] Layout responsivo testado manualmente em 375px, 768px e 1280px
- [ ] Partials de header, footer e messages criados
- [ ] Fontes Google Fonts (Space Grotesk + Inter) carregando
- [ ] Git: branch `feature/base-templates`, commit, PR para `develop`

---

#### Tarefa 2 — Formulário e view de cadastro de usuário

**Responsável:** Williams
**Story Points:** 5
**Tipo:** Backend / Frontend

##### Objetivo
Permitir que um visitante crie uma conta como Cliente ou Vendedor, usando e-mail como identificador principal. Ao cadastrar como vendedor, o SellerProfile deve ser criado automaticamente.

##### O que fazer
1. Criar `apps/users/forms.py` com `UserRegistrationForm`:
   - campos: email, first_name, last_name, password1, password2, user_type
   - campo `username` **não exposto** (preenchido automaticamente pelo model)
   - validação de e-mail único
   - validação de senha (password validators do Django)
2. Criar `apps/users/views.py` com view `register`:
   - GET: exibir formulário de cadastro
   - POST: validar, criar usuário, criar SellerProfile se user_type=SELLER (via signal ou na view)
   - após cadastro: logar automaticamente e redirecionar para home
   - tratamento de erros com mensagens no formulário
3. Criar `apps/users/urls.py` com rota `cadastro/` → `name='user-register'`
4. Registrar `apps/users/urls.py` no `config/urls.py` com `include('apps.users.urls')` no prefixo `usuarios/`
5. Criar `templates/users/register.html`:
   - estende `base.html`
   - formulário estilizado com Design System
   - exibição de erros por campo
   - link para login
6. Implementar signal `post_save` para criação automática do SellerProfile (ou lógica na view)

##### Dependências
- Tarefa 1 (base.html e CSS precisam existir)

##### Resultado esperado
Visitante acessa `/usuarios/cadastro/`, preenche o formulário, cria uma conta como Cliente ou Vendedor, é logado automaticamente e redirecionado. Se vendedor, SellerProfile é criado.

##### DoD
- [ ] Formulário valida e-mail único, senhas, nome obrigatório
- [ ] Campo username não é exposto ao usuário
- [ ] Usuário CLIENT ou SELLER criado corretamente no PostgreSQL
- [ ] SellerProfile criado automaticamente para vendedores
- [ ] Login automático após cadastro
- [ ] Erros de validação exibidos no formulário
- [ ] Template estilizado com Design System
- [ ] Git: branch `feature/user-registration`, PR para `develop`

---

#### Tarefa 3 — Login por e-mail e logout

**Responsável:** Paula
**Story Points:** 3
**Tipo:** Backend / Frontend

##### Objetivo
Permitir que o usuário faça login usando e-mail e senha, e faça logout. O EmailBackend já existe — esta tarefa cria as views, formulários e templates.

##### O que fazer
1. Criar `LoginForm` em `apps/users/forms.py`:
   - campos: email, password
   - label do campo email como "E-mail" (não "Username")
2. Criar view `user_login` em `apps/users/views.py`:
   - GET: exibir formulário
   - POST: autenticar com `authenticate(request, username=email, password=password)`, logar com `login()`
   - redirecionar para `LOGIN_REDIRECT_URL` ou `next` parameter
   - mensagem de erro se credenciais inválidas
3. Criar view `user_logout` em `apps/users/views.py`:
   - `@login_required`
   - chamar `logout(request)` e redirecionar para home
4. Adicionar rotas em `apps/users/urls.py`:
   - `login/` → `name='user-login'`
   - `logout/` → `name='user-logout'`
5. Criar `templates/users/login.html`:
   - estende `base.html`
   - formulário estilizado
   - link para cadastro
6. Atualizar navegação no header para exibir:
   - visitante: links de Login e Cadastro
   - autenticado: nome do usuário, link de Logout

##### Dependências
- Tarefa 1 (templates base)
- Tarefa 2 (URLs de users registradas)

##### Resultado esperado
Usuário acessa `/usuarios/login/`, informa e-mail e senha, é autenticado e redirecionado. Header mostra estado de autenticação. Logout funciona.

##### DoD
- [ ] Login por e-mail funcional (não username)
- [ ] Mensagem de erro para credenciais inválidas
- [ ] Redirect para `next` ou home após login
- [ ] Logout funcional com redirect
- [ ] Header atualiza estado logado/deslogado
- [ ] Template estilizado
- [ ] Git: branch `feature/user-auth`, PR para `develop`

---

#### Tarefa 4 — Página de perfil e edição de dados cadastrais

**Responsável:** Williams
**Story Points:** 3
**Tipo:** Backend / Frontend

##### Objetivo
Permitir que o usuário autenticado visualize e edite seus dados cadastrais (nome, e-mail). Se vendedor, exibir e permitir edição dos dados do SellerProfile (nome da loja, CNPJ, descrição, configuração de frete).

##### O que fazer
1. Criar `UserProfileForm` em `apps/users/forms.py`:
   - campos editáveis: first_name, last_name, email
   - email com validação de unicidade (excluindo o próprio usuário)
2. Criar `SellerProfileForm` em `apps/users/forms.py`:
   - campos: store_name, cnpj, description, shipping_rate_per_km, shipping_distance_km
3. Criar view `profile` em `apps/users/views.py`:
   - `@login_required`
   - GET: exibir dados do usuário + SellerProfile se vendedor
   - POST: salvar alterações (dois forms se vendedor)
   - mensagem de sucesso/erro via Django messages
4. Adicionar rota `perfil/` → `name='user-profile'` em `apps/users/urls.py`
5. Criar `templates/users/profile.html`:
   - estende `base.html`
   - exibe dados do usuário
   - formulário de edição
   - seção de SellerProfile (condicional para vendedores)

##### Dependências
- Tarefa 3 (login funcional para acessar perfil)

##### Resultado esperado
Usuário logado acessa `/usuarios/perfil/`, vê seus dados, edita e salva. Vendedor também vê e edita dados da loja e configuração de frete.

##### DoD
- [ ] Perfil acessível apenas logado (`@login_required`)
- [ ] Edição de nome e e-mail funcional
- [ ] Vendedor edita SellerProfile (incluindo frete)
- [ ] Validação de e-mail único
- [ ] Mensagens de sucesso/erro
- [ ] Template estilizado
- [ ] Dados persistidos corretamente no PostgreSQL
- [ ] Git: branch `feature/user-profile`, PR para `develop`

---

#### Tarefa 5 — CRUD de endereços de entrega

**Responsável:** Paula
**Story Points:** 5
**Tipo:** Backend / Frontend

##### Objetivo
Permitir que o usuário gerencie múltiplos endereços de entrega — listar, adicionar, editar, excluir e definir endereço padrão.

##### O que fazer
1. Criar `AddressForm` em `apps/users/forms.py`:
   - campos: nickname, recipient_name, zip_code, street, number, complement, neighborhood, city, state, reference, is_default
   - validação de CEP (formato XXXXX-XXX)
   - validação de UF (2 caracteres)
2. Criar views em `apps/users/views.py`:
   - `address_list`: lista endereços do usuário logado
   - `address_create`: formulário + criação de novo endereço
   - `address_edit`: edição de endereço existente (somente do próprio usuário)
   - `address_delete`: exclusão de endereço (somente do próprio usuário)
   - Lógica para `is_default`: ao marcar um como padrão, desmarcar os outros
3. Adicionar rotas em `apps/users/urls.py`:
   - `enderecos/` → `name='address-list'`
   - `enderecos/novo/` → `name='address-create'`
   - `enderecos/<int:pk>/editar/` → `name='address-edit'`
   - `enderecos/<int:pk>/excluir/` → `name='address-delete'`
4. Criar templates:
   - `templates/users/address_list.html` — lista de endereços com ações
   - `templates/users/address_form.html` — formulário de criação/edição
   - `templates/users/address_confirm_delete.html` — confirmação de exclusão
5. Garantir que cada view valide propriedade do endereço (`address.user == request.user`)

##### Dependências
- Tarefa 3 (login funcional)

##### Resultado esperado
Usuário logado gerencia seus endereços — cria, lista, edita, exclui e define um como padrão. Não é possível acessar endereços de outro usuário.

##### DoD
- [ ] CRUD completo de endereços funcional
- [ ] Validação de propriedade (usuário só vê/edita seus endereços)
- [ ] Lógica de endereço padrão funcional (apenas um por vez)
- [ ] Validação de CEP e UF
- [ ] `@login_required` em todas as views
- [ ] `get_object_or_404()` ao buscar endereço por PK
- [ ] Templates estilizados
- [ ] Dados persistidos no PostgreSQL
- [ ] Git: branch `feature/address-crud`, PR para `develop`

---

#### Tarefa 6 — Testes de autenticação e endereços

**Responsável:** Williams
**Story Points:** 3
**Tipo:** Teste

##### Objetivo
Criar testes automatizados para validar cadastro, login, logout, perfil e CRUD de endereços.

##### O que fazer
1. Criar `tests/users/test_views.py`:
   - `test_register_client_success` — cadastro de cliente com redirect
   - `test_register_seller_creates_profile` — cadastro de vendedor cria SellerProfile
   - `test_register_duplicate_email` — e-mail duplicado mostra erro
   - `test_login_by_email_success` — login com e-mail e senha corretos
   - `test_login_invalid_credentials` — credenciais inválidas mostram erro
   - `test_logout_redirects` — logout redireciona para home
   - `test_profile_requires_login` — perfil sem login redireciona para login
   - `test_profile_edit_success` — edição de perfil salva dados
2. Criar `tests/users/test_forms.py`:
   - testes de validação do `UserRegistrationForm`
   - testes de validação do `AddressForm` (CEP, UF)
3. Criar `tests/users/test_addresses.py`:
   - `test_address_create` — criar endereço
   - `test_address_edit_own` — editar próprio endereço
   - `test_address_cannot_edit_other_user` — não editar endereço alheio
   - `test_address_delete` — excluir endereço
   - `test_address_default_toggle` — alterar endereço padrão

##### Dependências
- Tarefas 2, 3, 4, 5 (funcionalidades implementadas)

##### Resultado esperado
Suite de testes para o app `users` cobre fluxos de cadastro, autenticação, perfil e endereços. Executável via `python manage.py test tests.users`.

##### DoD
- [ ] Pelo menos 12 testes cobrindo caminhos felizes e de erro
- [ ] Testes passando com `python manage.py test tests.users`
- [ ] Testes usam `setUp()` para dados reutilizáveis
- [ ] Git: branch `feature/user-tests`, PR para `develop`

---

#### Tarefa 7 — Página inicial (home)

**Responsável:** Williams
**Story Points:** 2
**Tipo:** Frontend

##### Objetivo
Criar a página inicial do marketplace com layout neo-brutalism, que servirá como landing page e ponto de entrada do sistema.

##### O que fazer
1. Criar view `home` em `config/views.py` (ou app separado):
   - renderiza template com contexto básico
2. Criar `templates/home.html`:
   - estende `base.html`
   - hero section com título e CTA
   - seção placeholder para "Produtos em destaque" (será populada na Sprint 3)
   - categorias destaque (placeholder)
3. Atualizar `config/urls.py` para rota raiz `/` → `name='home'`
4. Garantir que `LOGIN_REDIRECT_URL` e `LOGOUT_REDIRECT_URL` apontem para a home

##### Dependências
- Tarefa 1 (templates base)

##### Resultado esperado
Acessar `localhost:8000/` exibe a página inicial do marketplace com layout neo-brutalism completo, navegação funcional e estado de autenticação visível.

##### DoD
- [ ] Home acessível na raiz `/`
- [ ] Layout neo-brutalism aplicado
- [ ] Navegação exibe estado logado/deslogado
- [ ] Responsiva em mobile (375px)
- [ ] Git: branch `feature/home-page`, PR para `develop`

---

#### Resumo da Sprint 2

| Tarefa | Responsável | SP | Tipo |
|--------|------------|---:|------|
| T1 — Estrutura base de templates e CSS | Paula | 5 | Frontend/Infra |
| T2 — Cadastro de usuário | Williams | 5 | Backend/Frontend |
| T3 — Login e logout | Paula | 3 | Backend/Frontend |
| T4 — Perfil e edição cadastral | Williams | 3 | Backend/Frontend |
| T5 — CRUD de endereços | Paula | 5 | Backend/Frontend |
| T6 — Testes de autenticação e endereços | Williams | 3 | Teste |
| T7 — Página inicial | Williams | 2 | Frontend |
| **Total** | **Paula 13 / Williams 13** | **26** | |

**Entregáveis:**
- Sistema com layout neo-brutalism completo
- Cadastro de cliente e vendedor funcional
- Login por e-mail e logout
- Perfil com edição de dados (incluindo frete para vendedor)
- CRUD de endereços de entrega
- Página inicial
- Suite de testes para o app users

**DoD da Sprint:**
- [ ] Usuário pode criar conta, logar, ver/editar perfil e gerenciar endereços
- [ ] Vendedor tem SellerProfile criado automaticamente
- [ ] Layout Design System aplicado em todas as páginas
- [ ] Testes do app users passando
- [ ] Código revisado e mergeado em `develop`

---

### Sprint 3 — Catálogo de Produtos e Gestão do Vendedor

**Objetivo:** Entregar o domínio de produtos completo — vendedor cadastra, edita e desativa calçados; cliente visualiza o catálogo e os detalhes de cada produto. Ao final, existe um catálogo funcional alimentado por vendedores reais.

**Justificativa da posição:** Produtos são o núcleo do marketplace. Sem produtos, não há catálogo, busca, carrinho ou pedido. O vendedor é quem cria os produtos — portanto, a gestão do vendedor sobre seus produtos faz parte desta mesma fatia. Separar seria artificial.

**RFs cobertos:** RF04, RF05, RF08, RF09, RF10, RF20

**Dependências:** Sprint 2 (autenticação e SellerProfile funcionais)

---

#### Tarefa 8 — Formulários e views de cadastro de produto (vendedor)

**Responsável:** Williams
**Story Points:** 5
**Tipo:** Backend / Frontend

##### Objetivo
Permitir que o vendedor autenticado cadastre novos calçados com nome, descrição, marca, preço, categoria, imagens e estoque por tamanho.

##### O que fazer
1. Criar `apps/products/forms.py` com:
   - `ProductForm`: campos name, description, brand, price, category
   - `ProductImageFormSet` (inline formset): permite upload de múltiplas imagens
   - `StockForm` / `StockFormSet` (inline formset): permite definir tamanho + quantidade
2. Criar `apps/products/views.py` com view `product_create`:
   - `@login_required` + verificação de `user.is_seller`
   - GET: exibir formulário de produto com formsets de imagens e estoque
   - POST: validar, salvar produto associado ao vendedor logado, salvar imagens e estoque
   - redirecionar para lista de produtos do vendedor
   - tratar erros de validação
3. Criar `apps/products/urls.py`:
   - `novo/` → `name='product-create'`
4. Registrar `apps/products/urls.py` no `config/urls.py` com `include('apps.products.urls')` no prefixo `produtos/`
5. Criar `templates/products/product_form.html`:
   - estende `base.html`
   - formulário estilizado com Design System
   - seção de upload de imagens (múltiplas)
   - seção de estoque por tamanho (adicionar linhas dinamicamente)
   - preview de imagens (JavaScript)
6. Criar `static/js/product-form.js`:
   - adicionar/remover linhas de estoque dinamicamente
   - preview de imagens antes do upload
7. Popular categorias via fixture ou admin (dependência técnica, não RF)

##### Dependências
- Sprint 2 (autenticação + SellerProfile)

##### Resultado esperado
Vendedor logado acessa `/produtos/novo/`, preenche dados do calçado, adiciona imagens e define estoque por tamanho. Produto é salvo no PostgreSQL vinculado ao vendedor.

##### DoD
- [ ] Vendedor cadastra produto com todos os campos obrigatórios
- [ ] Imagens são salvas em `media/products/`
- [ ] Estoque por tamanho criado corretamente (unique_together respeitado)
- [ ] Apenas vendedores acessam a view (permissão verificada)
- [ ] Validação: preço > 0, nome obrigatório, pelo menos um tamanho
- [ ] `enctype="multipart/form-data"` no formulário
- [ ] Produto salvo com `seller = request.user`
- [ ] Template estilizado com Design System
- [ ] Git: branch `feature/product-create`, PR para `develop`

---

#### Tarefa 9 — Edição e desativação de produto (vendedor)

**Responsável:** Paula
**Story Points:** 3
**Tipo:** Backend / Frontend

##### Objetivo
Permitir que o vendedor edite os dados de seus calçados e desative produtos (soft delete com `is_active=False`).

##### O que fazer
1. Criar view `product_edit` em `apps/products/views.py`:
   - `@login_required` + verificação `product.seller == request.user`
   - GET: preencher formulário com dados atuais + formsets de imagens e estoque
   - POST: salvar alterações
   - `get_object_or_404(Product, pk=pk)`
2. Criar view `product_toggle_active`:
   - `@login_required` + verificação de propriedade
   - altera `is_active` (soft delete / reativação)
   - redirecionar com mensagem
3. Adicionar rotas em `apps/products/urls.py`:
   - `<int:pk>/editar/` → `name='product-edit'`
   - `<int:pk>/desativar/` → `name='product-toggle-active'`
4. Reutilizar `templates/products/product_form.html` para edição (mesmo template, contexto diferente)

##### Dependências
- Tarefa 8 (formulários e views de cadastro)

##### Resultado esperado
Vendedor edita seus produtos (nome, preço, imagens, estoque) e desativa/reativa produtos. Não pode editar produtos de outro vendedor.

##### DoD
- [ ] Edição salva todos os campos e formsets corretamente
- [ ] Desativação usa `is_active=False` (nunca delete físico)
- [ ] Verificação de propriedade (`product.seller == request.user`)
- [ ] `get_object_or_404()` ao buscar produto
- [ ] Mensagens de sucesso/erro
- [ ] Template estilizado
- [ ] Git: branch `feature/product-edit`, PR para `develop`

---

#### Tarefa 10 — Lista de produtos do vendedor (painel)

**Responsável:** Williams
**Story Points:** 3
**Tipo:** Backend / Frontend

##### Objetivo
Criar o painel do vendedor onde ele vê todos os seus produtos (ativos e inativos), com ações de editar e desativar.

##### O que fazer
1. Criar view `seller_product_list` em `apps/products/views.py`:
   - `@login_required` + verificação `user.is_seller`
   - listar produtos do vendedor logado (`Product.objects.filter(seller=request.user)`)
   - exibir status ativo/inativo
   - paginação (10 por página)
2. Adicionar rota: `meus-produtos/` → `name='seller-product-list'`
3. Criar `templates/products/seller_product_list.html`:
   - tabela/cards com nome, preço, categoria, status, ações
   - botões: editar, desativar/ativar
   - link para "Cadastrar novo produto"
4. Adicionar link no header/navegação para vendedores ("Meus Produtos")

##### Dependências
- Tarefa 8 (produtos existem)

##### Resultado esperado
Vendedor logado acessa `/produtos/meus-produtos/` e vê a lista completa de seus calçados com status e ações rápidas.

##### DoD
- [ ] Lista mostra apenas produtos do vendedor logado
- [ ] Paginação funcional
- [ ] Ações de editar e desativar acessíveis
- [ ] Status ativo/inativo visível
- [ ] Apenas vendedores acessam
- [ ] Template estilizado
- [ ] Git: branch `feature/seller-product-list`, PR para `develop`

---

#### Tarefa 11 — Catálogo público e página de detalhes do produto

**Responsável:** Paula
**Story Points:** 3
**Tipo:** Backend / Frontend

##### Objetivo
Criar a listagem pública de calçados (catálogo) acessível a qualquer visitante e a página de detalhes de um produto específico.

##### O que fazer
1. Criar view `product_list` em `apps/products/views.py`:
   - acessível sem login (público)
   - listar apenas `Product.objects.filter(is_active=True)`
   - paginação (12 por página)
   - template com grid de cards de produto
2. Criar view `product_detail` em `apps/products/views.py`:
   - `get_object_or_404(Product, pk=pk, is_active=True)`
   - exibir: nome, descrição, preço, marca, categoria, imagens, tamanhos disponíveis (Stock com quantity > 0)
   - informações do vendedor (nome da loja)
3. Adicionar rotas em `apps/products/urls.py`:
   - `` (raiz do app) → `name='product-list'`
   - `<int:pk>/` → `name='product-detail'`
4. Criar `templates/products/product_list.html`:
   - grid responsivo de cards
   - card: imagem principal, nome, marca, preço
   - link para detalhes
5. Criar `templates/products/product_detail.html`:
   - galeria de imagens
   - informações completas do produto
   - grade de tamanhos disponíveis
   - nome da loja do vendedor
   - botão "Adicionar ao carrinho" (placeholder, funcional na Sprint 4)
6. Criar `static/js/product-gallery.js` — navegação entre imagens
7. Atualizar home page para exibir produtos em destaque (últimos 8 adicionados)

##### Dependências
- Tarefa 8 (produtos precisam existir no banco)

##### Resultado esperado
Qualquer visitante acessa `/produtos/` e vê o catálogo de calçados em grid. Clica em um produto e vê todos os detalhes. Home exibe produtos em destaque.

##### DoD
- [ ] Catálogo mostra apenas produtos ativos
- [ ] Paginação funcional no catálogo
- [ ] Detalhes exibem: nome, descrição, preço, marca, imagens, tamanhos, vendedor
- [ ] Apenas tamanhos com estoque > 0 são mostrados
- [ ] `get_object_or_404()` para produto inexistente
- [ ] Grid responsivo (mobile-first)
- [ ] Home atualizada com produtos em destaque
- [ ] Templates estilizados com Design System
- [ ] Git: branch `feature/product-catalog`, PR para `develop`

---

#### Tarefa 12 — Configuração de media files e categorias seed

**Responsável:** Williams
**Story Points:** 2
**Tipo:** Infraestrutura / Backend

##### Objetivo
Configurar o serving de arquivos de mídia em desenvolvimento e criar categorias iniciais para o catálogo.

##### O que fazer
1. Atualizar `config/urls.py` para servir arquivos de mídia em `DEBUG=True`:
   ```python
   if settings.DEBUG:
       urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
   ```
2. Adicionar Pillow ao `requirements.txt` (necessário para `ImageField`)
3. Criar fixture ou management command para categorias seed:
   - Tênis, Sandália, Bota, Sapatênis, Chinelo, Social, Mule, Rasteirinha
4. Documentar como carregar categorias: `python manage.py loaddata categories`

##### Dependências
- Sprint 1 (settings e URLs base)

##### Resultado esperado
Imagens de produtos são servidas corretamente em desenvolvimento. Categorias iniciais estão disponíveis no banco.

##### DoD
- [ ] `media/` servido em desenvolvimento
- [ ] Pillow instalado e funcional
- [ ] Categorias seed carregáveis via fixture
- [ ] Git: branch `feature/media-categories`, PR para `develop`

---

#### Tarefa 13 — Testes de produtos

**Responsável:** Paula
**Story Points:** 3
**Tipo:** Teste

##### Objetivo
Criar testes para validar cadastro, edição, desativação de produtos e catálogo público.

##### O que fazer
1. Criar `tests/products/test_views.py`:
   - `test_product_create_as_seller` — vendedor cria produto com sucesso
   - `test_product_create_as_client_forbidden` — cliente não acessa cadastro
   - `test_product_edit_own` — vendedor edita próprio produto
   - `test_product_edit_other_seller_forbidden` — não edita produto de outro
   - `test_product_toggle_active` — desativação funciona
   - `test_catalog_shows_active_only` — catálogo mostra apenas ativos
   - `test_product_detail_shows_info` — detalhes exibem dados completos
   - `test_product_detail_inactive_404` — produto inativo retorna 404
2. Criar `tests/products/test_forms.py`:
   - testes de validação do `ProductForm` (preço, nome)

##### Dependências
- Tarefas 8, 9, 10, 11 (funcionalidades implementadas)

##### Resultado esperado
Suite de testes cobre fluxos de CRUD de produtos e catálogo. Executável via `python manage.py test tests.products`.

##### DoD
- [ ] Pelo menos 8 testes cobrindo caminhos felizes e de erro
- [ ] Testes passando
- [ ] Git: branch `feature/product-tests`, PR para `develop`

---

#### Resumo da Sprint 3

| Tarefa | Responsável | SP | Tipo |
|--------|------------|---:|------|
| T8 — Cadastro de produto (vendedor) | Williams | 5 | Backend/Frontend |
| T9 — Edição e desativação de produto | Paula | 3 | Backend/Frontend |
| T10 — Lista de produtos do vendedor | Williams | 3 | Backend/Frontend |
| T11 — Catálogo público e detalhes | Paula | 3 | Backend/Frontend |
| T12 — Media files e categorias seed | Williams | 2 | Infraestrutura |
| T13 — Testes de produtos | Paula | 3 | Teste |
| **Total** | **Paula 9 / Williams 10** | **19** | |

**Entregáveis:**
- Vendedor cadastra, edita e desativa calçados com imagens e estoque
- Catálogo público com grid de produtos
- Página de detalhes com galeria, tamanhos e informações completas
- Painel do vendedor com lista de seus produtos
- Home com produtos em destaque
- Suite de testes para o app products

**DoD da Sprint:**
- [ ] Vendedor pode cadastrar produto completo (modelo + imagens + estoque)
- [ ] Catálogo público exibe apenas produtos ativos
- [ ] Detalhes do produto exibem todas as informações (RF05)
- [ ] Soft delete funcional (RF10)
- [ ] Testes passando
- [ ] Código revisado e mergeado em `develop`

---

### Sprint 4 — Busca, Filtros e Carrinho de Compras

**Objetivo:** Permitir que o cliente pesquise e filtre calçados no catálogo, e gerencie um carrinho de compras — adicionar, alterar quantidade, remover itens e ver subtotal. Ao final, o cliente pode montar seu pedido.

**Justificativa da posição:** Busca e filtros estendem o catálogo (Sprint 3). O carrinho depende do catálogo e do login (ambos prontos). Unificar busca/filtros com carrinho evita uma Sprint subcarregada e entrega duas funcionalidades complementares — navegação e seleção de produtos.

**RFs cobertos:** RF06, RF07, RF11, RF12, RF13, RF14

**Dependências:** Sprint 3 (catálogo funcional) + Sprint 2 (autenticação)

---

#### Tarefa 14 — Busca por nome e descrição

**Responsável:** Paula
**Story Points:** 3
**Tipo:** Backend / Frontend

##### Objetivo
Permitir que o usuário pesquise calçados digitando termos que serão buscados no nome e descrição dos produtos.

##### O que fazer
1. Estender a view `product_list` em `apps/products/views.py`:
   - receber parâmetro `q` via query string
   - filtrar com `Q(name__icontains=q) | Q(description__icontains=q)`
   - manter paginação com parâmetros de busca
2. Atualizar `templates/products/product_list.html`:
   - campo de busca no topo do catálogo
   - exibir termo buscado e quantidade de resultados
   - mensagem quando não há resultados
3. Adicionar campo de busca no header (busca rápida em todas as páginas)
4. Criar `static/js/search.js` — submit do formulário de busca

##### Dependências
- Sprint 3 (catálogo funcional)

##### Resultado esperado
Usuário digita "tênis" no campo de busca, sistema exibe produtos cujo nome ou descrição contém o termo.

##### DoD
- [ ] Busca funcional por nome e descrição (`icontains`)
- [ ] URL preserva parâmetro de busca na paginação
- [ ] Campo de busca no catálogo e no header
- [ ] Mensagem "nenhum resultado" quando vazio
- [ ] Template estilizado
- [ ] Git: branch `feature/product-search`, PR para `develop`

---

#### Tarefa 15 — Filtros por categoria, tamanho, marca e faixa de preço

**Responsável:** Williams
**Story Points:** 5
**Tipo:** Backend / Frontend

##### Objetivo
Permitir que o usuário filtre calçados combinando critérios: categoria, tamanho, marca e faixa de preço.

##### O que fazer
1. Estender a view `product_list` em `apps/products/views.py`:
   - receber parâmetros via query string: `categoria`, `tamanho`, `marca`, `preco_min`, `preco_max`
   - filtrar por categoria (slug)
   - filtrar por tamanho (JOIN com Stock onde quantity > 0)
   - filtrar por marca (`brand__iexact`)
   - filtrar por faixa de preço (`price__gte`, `price__lte`)
   - combinar com busca por texto (se existir `q`)
   - passar opções de filtro ao template (categorias, marcas, tamanhos disponíveis)
2. Atualizar `templates/products/product_list.html`:
   - sidebar/accordion com filtros
   - checkboxes para categorias e marcas
   - select/checkboxes para tamanhos
   - inputs para faixa de preço (min/max)
   - botão "Filtrar" e "Limpar filtros"
   - manter filtros ativos visíveis na URL e na interface
3. Criar `static/js/filters.js`:
   - interação dos filtros (mobile: collapsible sidebar)
   - atualizar URL com filtros selecionados
4. Responsividade: filtros em sidebar no desktop, collapsible no mobile

##### Dependências
- Tarefa 14 (busca integrada)
- Sprint 3 (produtos e categorias existem)

##### Resultado esperado
Usuário acessa o catálogo e combina filtros (ex: Tênis + Nike + R$100–R$300 + Tamanho 42). A lista é atualizada mostrando apenas os produtos que atendem todos os critérios.

##### DoD
- [ ] Filtros por categoria, marca, tamanho e faixa de preço funcionais
- [ ] Filtros combinam entre si (AND)
- [ ] Filtros combinam com busca por texto
- [ ] Opções de filtro são dinâmicas (apenas valores que existem no banco)
- [ ] Paginação preserva filtros na URL
- [ ] Layout responsivo (sidebar/collapsible)
- [ ] Template estilizado com Design System
- [ ] Git: branch `feature/product-filters`, PR para `develop`

---

#### Tarefa 16 — Adicionar produto ao carrinho

**Responsável:** Paula
**Story Points:** 5
**Tipo:** Backend / Frontend

##### Objetivo
Permitir que o cliente autenticado adicione um calçado ao carrinho, selecionando tamanho e quantidade. Respeitar regra de `unique_together` (mesmo produto+tamanho = atualizar quantidade, não duplicar).

##### O que fazer
1. Criar `apps/cart/views.py` com view `cart_add`:
   - `@login_required`
   - receber `product_id`, `size`, `quantity` via POST
   - buscar ou criar Cart para o usuário
   - verificar estoque disponível (`Stock.quantity >= quantidade solicitada`)
   - se CartItem com mesmo product+size existe: atualizar quantidade
   - se não existe: criar CartItem
   - redirecionar para página do carrinho ou produto com mensagem de sucesso
2. Criar `apps/cart/urls.py`:
   - `adicionar/` → `name='cart-add'` (POST)
3. Registrar `apps/cart/urls.py` no `config/urls.py` com prefixo `carrinho/`
4. Atualizar `templates/products/product_detail.html`:
   - formulário de "Adicionar ao carrinho" com select de tamanho e input de quantidade
   - tamanhos sem estoque desabilitados
   - validação client-side (quantidade > 0)
5. Criar `static/js/cart-add.js`:
   - feedback visual ao adicionar (mensagem de sucesso)
   - atualizar indicador do carrinho no header (quantidade de itens)

##### Dependências
- Sprint 2 (autenticação)
- Sprint 3 (produtos com estoque)

##### Resultado esperado
Cliente logado vê página de detalhes, seleciona tamanho 42, quantidade 1, clica "Adicionar ao carrinho". CartItem é criado. Repetir com mesmo tamanho incrementa a quantidade.

##### DoD
- [ ] Carrinho criado automaticamente na primeira adição
- [ ] `unique_together` respeitado — atualiza qty em vez de duplicar
- [ ] Validação de estoque antes de adicionar
- [ ] Apenas usuários logados podem adicionar
- [ ] Mensagem de sucesso/erro
- [ ] Template funcional no product_detail
- [ ] Git: branch `feature/cart-add`, PR para `develop`

---

#### Tarefa 17 — Página do carrinho (visualizar, alterar, remover)

**Responsável:** Williams
**Story Points:** 5
**Tipo:** Backend / Frontend

##### Objetivo
Criar a página completa do carrinho onde o cliente vê seus itens, altera quantidades, remove itens e vê o subtotal total.

##### O que fazer
1. Criar views em `apps/cart/views.py`:
   - `cart_detail`: exibir carrinho do usuário com todos os itens
   - `cart_update`: alterar quantidade de um CartItem (POST)
   - `cart_remove`: remover CartItem (POST)
2. Adicionar rotas em `apps/cart/urls.py`:
   - `` (raiz) → `name='cart-detail'`
   - `atualizar/<int:item_pk>/` → `name='cart-update'` (POST)
   - `remover/<int:item_pk>/` → `name='cart-remove'` (POST)
3. Criar `templates/cart/cart_detail.html`:
   - lista de itens: imagem, nome, tamanho, preço unitário, quantidade (editável), subtotal do item
   - botão remover por item
   - subtotal total do carrinho
   - botão "Continuar comprando" (link para catálogo)
   - botão "Finalizar compra" (link para checkout — placeholder, Sprint 5)
   - mensagem quando carrinho vazio
4. Criar `static/js/cart.js`:
   - atualização de quantidade com feedback
   - confirmação antes de remover
   - recalcular subtotal visualmente
5. Validação: verificar estoque ao atualizar quantidade
6. Atualizar header: indicador de itens no carrinho (badge com contagem)

##### Dependências
- Tarefa 16 (adicionar ao carrinho)

##### Resultado esperado
Cliente acessa `/carrinho/`, vê todos os itens, altera quantidade (com validação de estoque), remove itens e vê o subtotal total atualizado.

##### DoD
- [ ] Lista de itens com imagem, nome, tamanho, preço, quantidade, subtotal
- [ ] Alteração de quantidade funcional com validação de estoque
- [ ] Remoção de item funcional
- [ ] Subtotal total calculado corretamente
- [ ] Carrinho vazio exibe mensagem
- [ ] Badge no header com contagem de itens
- [ ] `@login_required` em todas as views
- [ ] Template estilizado com Design System
- [ ] Git: branch `feature/cart-page`, PR para `develop`

---

#### Tarefa 18 — Testes de busca, filtros e carrinho

**Responsável:** Paula
**Story Points:** 3
**Tipo:** Teste

##### Objetivo
Criar testes para validar busca, filtros e operações do carrinho.

##### O que fazer
1. Criar `tests/products/test_search_filters.py`:
   - `test_search_by_name` — busca encontra produto pelo nome
   - `test_search_no_results` — busca sem resultados
   - `test_filter_by_category` — filtro por categoria
   - `test_filter_by_price_range` — filtro por faixa de preço
   - `test_filter_combined` — filtros combinados
2. Criar `tests/cart/test_views.py`:
   - `test_add_to_cart` — adicionar produto ao carrinho
   - `test_add_same_product_updates_qty` — mesma product+size incrementa
   - `test_add_exceeds_stock` — não permite além do estoque
   - `test_update_quantity` — alterar quantidade
   - `test_remove_item` — remover item
   - `test_cart_subtotal` — subtotal calculado corretamente
   - `test_cart_requires_login` — acesso sem login redireciona

##### Dependências
- Tarefas 14, 15, 16, 17 (funcionalidades implementadas)

##### Resultado esperado
Suite de testes cobre busca, filtros e carrinho. Executável via `python manage.py test tests.products tests.cart`.

##### DoD
- [ ] Pelo menos 12 testes entre busca/filtros e carrinho
- [ ] Testes passando
- [ ] Git: branch `feature/search-cart-tests`, PR para `develop`

---

#### Resumo da Sprint 4

| Tarefa | Responsável | SP | Tipo |
|--------|------------|---:|------|
| T14 — Busca por nome e descrição | Paula | 3 | Backend/Frontend |
| T15 — Filtros (categoria, tamanho, marca, preço) | Williams | 5 | Backend/Frontend |
| T16 — Adicionar ao carrinho | Paula | 5 | Backend/Frontend |
| T17 — Página do carrinho (ver, alterar, remover) | Williams | 5 | Backend/Frontend |
| T18 — Testes de busca, filtros e carrinho | Paula | 3 | Teste |
| **Total** | **Paula 11 / Williams 10** | **21** | |

**Entregáveis:**
- Busca por nome/descrição funcional
- Filtros combinados por categoria, tamanho, marca e faixa de preço
- Carrinho completo: adicionar, alterar, remover, subtotal
- Badge de carrinho no header
- Suite de testes para busca, filtros e carrinho

**DoD da Sprint:**
- [ ] Cliente pode buscar e filtrar calçados (RF06, RF07)
- [ ] Cliente pode gerenciar carrinho completo (RF11–RF14)
- [ ] Estoque validado ao adicionar/atualizar
- [ ] Testes passando
- [ ] Código revisado e mergeado em `develop`

---

### Sprint 5 — Checkout, Pedidos e Histórico

**Objetivo:** Entregar o fluxo completo de compra — seleção de endereço, cálculo de frete, pagamento simulado, criação do pedido com snapshot de preço, desconto de estoque e histórico de pedidos do cliente. Ao final, o marketplace tem um ciclo de compra funcional.

**Justificativa da posição:** O checkout é o ápice funcional do marketplace. Depende de todas as Sprints anteriores: autenticação (2), endereços (2), produtos (3), estoque (3) e carrinho (4). É a Sprint mais complexa e com mais integrações entre apps.

**RFs cobertos:** RF15, RF16, RF17, RF20, RF23, RF24, RF25

**Dependências:** Sprint 4 (carrinho funcional) + Sprint 2 (endereços)

---

#### Tarefa 19 — Página de checkout (seleção de endereço e cálculo de frete)

**Responsável:** Williams
**Story Points:** 5
**Tipo:** Backend / Frontend / Integração

##### Objetivo
Criar a primeira etapa do checkout: exibir resumo do carrinho, permitir seleção de endereço, calcular frete com base na configuração do vendedor, e exibir total (subtotal + frete).

##### O que fazer
1. Criar `apps/orders/views.py` com view `checkout`:
   - `@login_required`
   - verificar se carrinho não está vazio (redirecionar se vazio)
   - listar endereços do usuário (`request.user.addresses.all()`)
   - pré-selecionar endereço padrão (`is_default=True`)
   - calcular frete para cada item:
     - para cada CartItem, obter `SellerProfile` do vendedor do produto
     - aplicar fórmula: `frete = shipping_distance_km × shipping_rate_per_km`
     - somar frete de todos os vendedores (se carrinho tem itens de vendedores diferentes)
   - calcular subtotal (soma dos CartItem.subtotal)
   - calcular total (subtotal + frete)
   - passar dados ao template
2. Criar `apps/orders/urls.py`:
   - `checkout/` → `name='checkout'`
3. Registrar `apps/orders/urls.py` no `config/urls.py` com prefixo `pedidos/`
4. Criar `templates/orders/checkout.html`:
   - resumo dos itens do carrinho
   - seleção de endereço (radio buttons ou select)
   - link para "Adicionar novo endereço" (abre modal ou nova página)
   - exibição discriminada: subtotal, frete (por vendedor se necessário), total
   - formulário de seleção de método de pagamento simulado (radio: Cartão Crédito, Débito, PIX, Boleto)
   - aviso explícito: "PAGAMENTO SIMULADO — nenhuma cobrança real será realizada"
   - botão "Confirmar Pedido"
5. Criar `static/js/checkout.js`:
   - recalcular frete ao trocar endereço (se aplicável, ou exibir informação fixa do vendedor)
   - validação: endereço selecionado, método de pagamento escolhido

##### Dependências
- Sprint 4 (carrinho com itens)
- Sprint 2 (endereços do usuário)

##### Resultado esperado
Cliente acessa `/pedidos/checkout/`, vê resumo do carrinho, seleciona endereço, vê frete calculado, seleciona método de pagamento simulado e clica "Confirmar Pedido".

##### DoD
- [ ] Checkout acessível apenas com carrinho não-vazio
- [ ] Endereços do usuário listados com pré-seleção do padrão
- [ ] Frete calculado corretamente por vendedor
- [ ] Subtotal, frete e total exibidos
- [ ] Métodos de pagamento simulados disponíveis
- [ ] Aviso de pagamento simulado visível
- [ ] Validação de endereço e método de pagamento
- [ ] `@login_required`
- [ ] Template estilizado
- [ ] Git: branch `feature/checkout`, PR para `develop`

---

#### Tarefa 20 — Processamento do pedido (criar Order, descontar estoque, limpar carrinho)

**Responsável:** Paula
**Story Points:** 5
**Tipo:** Backend / Integração

##### Objetivo
Processar a confirmação do pedido — criar Order e OrderItems com snapshot de preço, descontar estoque, limpar carrinho e redirecionar para página de confirmação.

##### O que fazer
1. Criar view `order_confirm` em `apps/orders/views.py`:
   - `@login_required`
   - receber POST com: `address_id`, `payment_method`
   - validar dentro de `transaction.atomic()`:
     - verificar estoque de cada item novamente (evitar race condition)
     - calcular subtotal a partir do carrinho
     - calcular frete a partir do(s) SellerProfile(s)
     - criar `Order` com:
       - `user = request.user`
       - `shipping_address_id = address_id`
       - `subtotal`, `shipping_cost`, `total`
       - `payment_method = payment_method`
       - `payment_status = APPROVED` (simulado)
       - `status = CONFIRMED`
     - para cada CartItem, criar `OrderItem`:
       - `product`, `size`, `quantity`
       - `unit_price = product.price` (snapshot)
     - para cada CartItem, descontar estoque (`Stock.quantity -= CartItem.quantity`)
     - limpar carrinho (deletar todos os CartItems)
   - redirecionar para página de confirmação com o Order criado
2. Criar view `order_success`:
   - exibir confirmação do pedido com número, itens, total e pagamento
3. Adicionar rotas:
   - `confirmar/` → `name='order-confirm'` (POST)
   - `sucesso/<int:pk>/` → `name='order-success'`
4. Criar `templates/orders/order_success.html`:
   - número do pedido
   - lista de itens com preço snapshot
   - subtotal, frete, total
   - endereço de entrega
   - método e status de pagamento (SIMULADO)
   - aviso: "Pagamento aprovado (simulação acadêmica)"
   - link para "Ver meus pedidos"

##### Dependências
- Tarefa 19 (checkout funcional)

##### Resultado esperado
Ao confirmar pedido: Order e OrderItems são criados no banco, estoque é descontado, carrinho é limpo, cliente vê página de confirmação.

##### DoD
- [ ] Order criado com todos os campos corretos (incluindo snapshot de valores)
- [ ] OrderItems com `unit_price` = preço no momento da compra
- [ ] Estoque descontado corretamente (`Stock.quantity -= qty`)
- [ ] Carrinho limpo após confirmação
- [ ] Operação em `transaction.atomic()` (rollback se falhar)
- [ ] Verificação de estoque antes de processar (evitar venda sem estoque)
- [ ] `payment_status = APPROVED` (simulado)
- [ ] Página de sucesso exibe detalhes do pedido
- [ ] Dados persistidos no PostgreSQL
- [ ] Git: branch `feature/order-process`, PR para `develop`

---

#### Tarefa 21 — Histórico de pedidos do cliente

**Responsável:** Williams
**Story Points:** 3
**Tipo:** Backend / Frontend

##### Objetivo
Permitir que o cliente veja o histórico de seus pedidos com status, data, total e detalhes.

##### O que fazer
1. Criar view `order_list` em `apps/orders/views.py`:
   - `@login_required`
   - listar `Order.objects.filter(user=request.user).order_by('-created_at')`
   - paginação (10 por página)
2. Criar view `order_detail` em `apps/orders/views.py`:
   - `@login_required`
   - `get_object_or_404(Order, pk=pk, user=request.user)` — apenas pedidos do próprio usuário
   - exibir itens, subtotal, frete, total, endereço, pagamento, status
3. Adicionar rotas:
   - `meus-pedidos/` → `name='order-list'`
   - `meus-pedidos/<int:pk>/` → `name='order-detail'`
4. Criar `templates/orders/order_list.html`:
   - lista de pedidos: número, data, status (badge colorido), total
   - link para detalhes
5. Criar `templates/orders/order_detail.html`:
   - detalhes completos do pedido
   - timeline visual de status

##### Dependências
- Tarefa 20 (pedidos existem)

##### Resultado esperado
Cliente acessa `/pedidos/meus-pedidos/`, vê lista de pedidos ordenada por data. Clica em um pedido para ver detalhes completos.

##### DoD
- [ ] Lista de pedidos do cliente funcional com paginação
- [ ] Detalhes mostram itens, valores, endereço, pagamento e status
- [ ] Apenas pedidos do próprio usuário visíveis
- [ ] `get_object_or_404()` com filtro de propriedade
- [ ] `@login_required`
- [ ] Templates estilizados
- [ ] Git: branch `feature/order-history`, PR para `develop`

---

#### Tarefa 22 — Testes do checkout e pedidos

**Responsável:** Paula
**Story Points:** 5
**Tipo:** Teste

##### Objetivo
Criar testes de integração para o fluxo completo de compra.

##### O que fazer
1. Criar `tests/orders/test_views.py`:
   - `test_checkout_with_empty_cart_redirects` — carrinho vazio redireciona
   - `test_checkout_shows_addresses` — checkout lista endereços
   - `test_checkout_calculates_shipping` — frete calculado corretamente
   - `test_order_confirm_creates_order` — pedido criado com dados corretos
   - `test_order_confirm_creates_items_with_snapshot` — `unit_price` snapshot
   - `test_order_confirm_decrements_stock` — estoque descontado
   - `test_order_confirm_clears_cart` — carrinho limpo
   - `test_order_confirm_insufficient_stock` — rejeita se sem estoque
   - `test_order_list_shows_own_orders` — lista apenas pedidos do usuário
   - `test_order_detail_other_user_404` — não vê pedido de outro
   - `test_payment_status_approved` — pagamento sempre APPROVED (simulado)

##### Dependências
- Tarefas 19, 20, 21 (funcionalidades implementadas)

##### Resultado esperado
Suite de testes cobre o fluxo completo de checkout e pedidos. Executável via `python manage.py test tests.orders`.

##### DoD
- [ ] Pelo menos 10 testes de integração
- [ ] Testes passando
- [ ] Cobertura de cenários felizes e de erro
- [ ] Git: branch `feature/order-tests`, PR para `develop`

---

#### Resumo da Sprint 5

| Tarefa | Responsável | SP | Tipo |
|--------|------------|---:|------|
| T19 — Checkout (endereço, frete, pagamento) | Williams | 5 | Backend/Frontend/Integração |
| T20 — Processamento do pedido | Paula | 5 | Backend/Integração |
| T21 — Histórico de pedidos do cliente | Williams | 3 | Backend/Frontend |
| T22 — Testes de checkout e pedidos | Paula | 5 | Teste |
| **Total** | **Paula 10 / Williams 8** | **18** | |

**Fluxo do checkout:**
```
Usuário autenticado
  → Visualiza carrinho
  → Seleciona endereço de entrega (Address cadastrado)
  → Sistema calcula frete: SellerProfile.shipping_distance_km × shipping_rate_per_km
  → Sistema exibe: subtotal + frete + total
  → Usuário seleciona método de pagamento (SIMULADO: cartão, PIX, boleto)
  → Usuário confirma pedido
  → Sistema cria Order com payment_status = APPROVED (simulado)
  → Sistema desconta estoque
  → Usuário vê confirmação do pedido
```

**Entregáveis:**
- Checkout completo: endereço, frete calculado, pagamento simulado
- Pedido criado com snapshot de preços, estoque descontado, carrinho limpo
- Histórico de pedidos do cliente com detalhes
- Suite de testes de integração do fluxo de compra

**DoD da Sprint:**
- [ ] Fluxo completo: carrinho → checkout → pedido → confirmação (RF15, RF16)
- [ ] Frete calculado corretamente (RF24)
- [ ] Pagamento simulado registrado com aviso explícito (RF25)
- [ ] Estoque descontado em `transaction.atomic()` (RF20)
- [ ] Histórico de pedidos funcional (RF17)
- [ ] Testes passando
- [ ] Código revisado e mergeado em `develop`

---

### Sprint 6 — Dashboard do Vendedor, Integração e Finalização

**Objetivo:** Completar o ciclo do marketplace com o dashboard do vendedor (visualizar e gerenciar pedidos), realizar testes de integração end-to-end, ajustes finais de UX, segurança básica, documentação e preparação para apresentação.

**Justificativa da posição:** O dashboard do vendedor depende de pedidos existirem (Sprint 5). Esta Sprint também é o momento de integrar todos os módulos, testar cenários cruzados, polir a interface e preparar a apresentação ao CEO.

**RFs cobertos:** RF18, RF19

**Dependências:** Sprint 5 (pedidos existem)

---

#### Tarefa 23 — Dashboard do vendedor (pedidos de seus produtos)

**Responsável:** Williams
**Story Points:** 5
**Tipo:** Backend / Frontend

##### Objetivo
Criar o dashboard onde o vendedor visualiza os pedidos que contêm seus produtos, com informações do comprador, endereço de entrega e itens vendidos.

##### O que fazer
1. Criar view `seller_order_list` em `apps/orders/views.py`:
   - `@login_required` + verificação `user.is_seller`
   - buscar OrderItems onde `product__seller == request.user`
   - agrupar por Order (cada Order pode ter itens de vários vendedores)
   - exibir apenas itens pertencentes ao vendedor logado
   - paginação
2. Criar view `seller_order_detail`:
   - detalhes do pedido com foco nos itens do vendedor
   - exibir endereço de entrega do comprador
   - exibir status atual do pedido
3. Adicionar rotas:
   - `vendedor/pedidos/` → `name='seller-order-list'`
   - `vendedor/pedidos/<int:pk>/` → `name='seller-order-detail'`
4. Criar `templates/sellers/order_list.html`:
   - lista de pedidos com: número, data, comprador, status, valor dos itens do vendedor
   - filtro por status (Pendente, Confirmado, Em trânsito, etc.)
5. Criar `templates/sellers/order_detail.html`:
   - itens vendidos naquele pedido
   - dados do comprador (nome)
   - endereço de entrega
   - status com opção de atualizar

##### Dependências
- Sprint 5 (pedidos existem no banco)

##### Resultado esperado
Vendedor logado acessa `/pedidos/vendedor/pedidos/`, vê lista de pedidos que contêm seus produtos. Clica para ver detalhes e endereço de entrega.

##### DoD
- [ ] Dashboard mostra apenas pedidos com itens do vendedor logado
- [ ] Detalhes exibem itens vendidos, comprador e endereço
- [ ] Filtro por status funcional
- [ ] Paginação funcional
- [ ] Apenas vendedores acessam
- [ ] Templates estilizados
- [ ] Git: branch `feature/seller-dashboard`, PR para `develop`

---

#### Tarefa 24 — Atualização de status do pedido (vendedor)

**Responsável:** Paula
**Story Points:** 3
**Tipo:** Backend / Frontend

##### Objetivo
Permitir que o vendedor atualize o status dos pedidos que contêm seus produtos, seguindo o ciclo: PENDING → CONFIRMED → SHIPPED → DELIVERED.

##### O que fazer
1. Criar view `seller_order_update_status` em `apps/orders/views.py`:
   - `@login_required` + verificação `user.is_seller`
   - verificar que o pedido contém itens do vendedor
   - aceitar novo status via POST
   - validar transição de status (não pular etapas, não voltar)
   - atualizar `Order.status`
   - mensagem de sucesso
2. Adicionar rota:
   - `vendedor/pedidos/<int:pk>/status/` → `name='seller-order-update-status'` (POST)
3. Atualizar `templates/sellers/order_detail.html`:
   - botões/dropdown para próximo status válido
   - exibir histórico de alterações (se implementado)
4. Criar regra de validação de transição:
   - PENDING → CONFIRMED ✅
   - CONFIRMED → SHIPPED ✅
   - SHIPPED → DELIVERED ✅
   - QUALQUER → CANCELLED ✅
   - Voltar status ❌

##### Dependências
- Tarefa 23 (dashboard do vendedor)

##### Resultado esperado
Vendedor visualiza pedido e clica para avançar o status (ex: Confirmado → Em trânsito). Status é atualizado no banco.

##### DoD
- [ ] Atualização de status funcional
- [ ] Validação de transição (sem pular etapas ou voltar)
- [ ] Apenas vendedor com itens naquele pedido pode alterar
- [ ] Mensagem de sucesso após alteração
- [ ] Template exibe apenas próximos status válidos
- [ ] Git: branch `feature/order-status-update`, PR para `develop`

---

#### Tarefa 25 — Testes de integração end-to-end

**Responsável:** Williams
**Story Points:** 5
**Tipo:** Teste / Integração

##### Objetivo
Criar testes de integração que validam o fluxo completo do marketplace de ponta a ponta.

##### O que fazer
1. Criar `tests/test_integration.py`:
   - `test_full_purchase_flow`:
     1. Criar vendedor e produto com estoque
     2. Criar cliente e endereço
     3. Logar como cliente
     4. Adicionar produto ao carrinho
     5. Acessar checkout
     6. Confirmar pedido
     7. Verificar Order e OrderItem criados
     8. Verificar estoque descontado
     9. Verificar carrinho vazio
   - `test_seller_sees_order_after_purchase`:
     1. Fluxo de compra completo
     2. Logar como vendedor
     3. Acessar dashboard
     4. Verificar pedido aparece
   - `test_seller_updates_status`:
     1. Pedido existente
     2. Vendedor atualiza status para CONFIRMED → SHIPPED → DELIVERED
   - `test_client_cannot_access_seller_dashboard`
   - `test_seller_cannot_see_other_seller_orders`
   - `test_insufficient_stock_blocks_checkout`
2. Criar `tests/orders/test_seller_views.py`:
   - `test_seller_order_list_shows_own` — lista apenas pedidos com seus produtos
   - `test_seller_order_update_status` — atualização de status
   - `test_seller_order_update_invalid_transition` — transição inválida rejeitada
   - `test_client_forbidden_on_seller_views` — cliente não acessa dashboard

##### Dependências
- Todas as funcionalidades das Sprints 2–5 e tarefas 23, 24

##### Resultado esperado
Suite de testes e2e cobre o ciclo completo do marketplace. Executável via `python manage.py test`.

##### DoD
- [ ] Pelo menos 8 testes de integração e2e
- [ ] Todos os testes do projeto passando (`python manage.py test`)
- [ ] Git: branch `feature/integration-tests`, PR para `develop`

---

#### Tarefa 26 — Ajustes de UX, segurança e responsividade

**Responsável:** Paula
**Story Points:** 5
**Tipo:** Frontend / Segurança

##### Objetivo
Revisar toda a interface do sistema, corrigir inconsistências visuais, melhorar responsividade e aplicar boas práticas de segurança.

##### O que fazer
1. **Revisão de UX:**
   - Verificar navegação em todas as páginas (links corretos, breadcrumbs)
   - Garantir mensagens de feedback em todas as ações (sucesso, erro, aviso)
   - Verificar estados vazios (carrinho vazio, sem pedidos, sem endereços)
   - Verificar acessibilidade: labels em inputs, contraste 4.5:1, áreas 44x44px
2. **Responsividade:**
   - Testar todas as páginas em 375px, 768px e 1280px
   - Corrigir quebras de layout
   - Verificar navegação mobile (hamburger menu)
3. **Segurança básica:**
   - Verificar CSRF em todos os formulários POST
   - Verificar `@login_required` em todas as views protegidas
   - Verificar filtros de propriedade (usuário só acessa seus dados)
   - Verificar que `DEBUG=False` funciona (ALLOWED_HOSTS, static files)
   - Revisar que `.env` não está no Git
4. **Consistência visual:**
   - Verificar uso de tokens CSS (sem valores hardcoded)
   - Verificar convenção BEM nas classes
   - Verificar sombras sólidas (sem blur)
   - Verificar border-radius: 0 (exceto badges)

##### Dependências
- Todas as Sprints anteriores

##### Resultado esperado
Interface polida, responsiva, acessível e segura. Todas as páginas seguem o Design System documentado.

##### DoD
- [ ] Todas as páginas responsivas em 375px, 768px, 1280px
- [ ] Acessibilidade WCAG AA verificada (contraste, labels, áreas de toque)
- [ ] CSRF presente em todos os forms POST
- [ ] `@login_required` e filtros de propriedade verificados
- [ ] Nenhum valor CSS hardcoded
- [ ] Git: branch `feature/ux-security-review`, PR para `develop`

---

#### Tarefa 27 — Documentação final e preparação para apresentação

**Responsável:** Williams
**Story Points:** 3
**Tipo:** Documentação

##### Objetivo
Atualizar toda a documentação do projeto, atualizar status dos requisitos e preparar material para apresentação ao CEO.

##### O que fazer
1. Atualizar `docs/requirements.md`:
   - marcar todos os RFs como "Implementado"
   - incluir Sprint em que foi implementado
2. Atualizar `README.md`:
   - instruções de instalação atualizadas
   - como rodar o projeto (`python manage.py runserver`)
   - como rodar testes (`python manage.py test`)
   - como carregar dados iniciais (categorias, fixture)
   - screenshots das principais telas
3. Atualizar `docs/architecture.md`:
   - incluir rotas implementadas
   - atualizar diagrama se necessário
4. Criar `docs/deploy-checklist.md`:
   - checklist para deploy (DEBUG=False, ALLOWED_HOSTS, static files, etc.)
5. Atualizar docstrings nas views e forms (se necessário)
6. Garantir que `.env.example` reflete todas as variáveis necessárias

##### Dependências
- Todas as funcionalidades implementadas

##### Resultado esperado
Documentação completa e atualizada. Qualquer membro da equipe pode clonar o repo, seguir o README e ter o projeto rodando.

##### DoD
- [ ] `requirements.md` — todos os RFs com status "Implementado"
- [ ] `README.md` — instruções completas e funcionais
- [ ] `architecture.md` — atualizado
- [ ] `.env.example` — completo
- [ ] Git: branch `feature/documentation`, PR para `develop`, depois `develop` → `main`

---

#### Resumo da Sprint 6

| Tarefa | Responsável | SP | Tipo |
|--------|------------|---:|------|
| T23 — Dashboard do vendedor (pedidos) | Williams | 5 | Backend/Frontend |
| T24 — Atualização de status do pedido | Paula | 3 | Backend/Frontend |
| T25 — Testes de integração e2e | Williams | 5 | Teste/Integração |
| T26 — Ajustes UX, segurança e responsividade | Paula | 5 | Frontend/Segurança |
| T27 — Documentação final e apresentação | Williams | 3 | Documentação |
| **Total** | **Paula 8 / Williams 13** | **21** | |

**Entregáveis:**
- Dashboard do vendedor com pedidos de seus produtos
- Atualização de status do pedido pelo vendedor
- Suite de testes e2e cobrindo o ciclo completo
- Interface polida, responsiva e segura
- Documentação completa e atualizada
- Projeto pronto para apresentação

**DoD da Sprint:**
- [ ] Vendedor pode ver e gerenciar pedidos (RF18, RF19)
- [ ] Todos os testes passando (`python manage.py test`)
- [ ] Interface responsiva e acessível
- [ ] Documentação atualizada
- [ ] Código final mergeado em `main`

---

## 9. Matriz de Rastreabilidade

| Requisito | Sprint | Tarefa(s) | Responsável | Status esperado |
|-----------|--------|-----------|-------------|-----------------|
| RF01 | Sprint 2 | T2 — Cadastro de usuário | Williams | Implementado |
| RF02 | Sprint 2 | T3 — Login e logout | Paula | Implementado |
| RF03 | Sprint 2 | T4 — Perfil e edição | Williams | Implementado |
| RF04 | Sprint 3 | T11 — Catálogo público | Paula | Implementado |
| RF05 | Sprint 3 | T11 — Detalhes do produto | Paula | Implementado |
| RF06 | Sprint 4 | T14 — Busca | Paula | Implementado |
| RF07 | Sprint 4 | T15 — Filtros | Williams | Implementado |
| RF08 | Sprint 3 | T8 — Cadastro de produto | Williams | Implementado |
| RF09 | Sprint 3 | T9 — Edição de produto | Paula | Implementado |
| RF10 | Sprint 3 | T9 — Desativação (soft delete) | Paula | Implementado |
| RF11 | Sprint 4 | T16 — Adicionar ao carrinho | Paula | Implementado |
| RF12 | Sprint 4 | T17 — Alterar quantidade | Williams | Implementado |
| RF13 | Sprint 4 | T17 — Remover do carrinho | Williams | Implementado |
| RF14 | Sprint 4 | T17 — Subtotal do carrinho | Williams | Implementado |
| RF15 | Sprint 5 | T19, T20 — Checkout e processamento | Williams, Paula | Implementado |
| RF16 | Sprint 5 | T20 — Snapshot de preço em OrderItem | Paula | Implementado |
| RF17 | Sprint 5 | T21 — Histórico de pedidos | Williams | Implementado |
| RF18 | Sprint 6 | T23 — Dashboard vendedor | Williams | Implementado |
| RF19 | Sprint 6 | T24 — Atualizar status | Paula | Implementado |
| RF20 | Sprint 3, 5 | T8 (estoque), T20 (desconto) | Williams, Paula | Implementado |
| RF21 | Sprint 1 ✅ | EmailBackend implementado | — | Implementado |
| RF22 | Sprint 2 | T5 — CRUD de endereços | Paula | Implementado |
| RF23 | Sprint 5 | T19 — Seleção de endereço no checkout | Williams | Implementado |
| RF24 | Sprint 5 | T19 — Cálculo de frete simulado | Williams | Implementado |
| RF25 | Sprint 5 | T20 — Pagamento simulado | Paula | Implementado |

> ✅ **Nenhum RF ficou sem tarefa vinculada.**

---

## 10. Distribuição de Story Points

| Sprint | Paula | Williams | Total |
|--------|------:|---------:|------:|
| Sprint 1 ✅ | — | — | — |
| Sprint 2 | 15 | 11 | 26 |
| Sprint 3 | 13 | 13 | 26 |
| Sprint 4 | 11 | 10 | 21 |
| Sprint 5 | 13 | 11 | 24 |
| Sprint 6 | 8 | 13 | 21 |
| **Total** | **60** | **58** | **118** |

### Análise de equilíbrio

| Critério | Resultado |
|----------|-----------|
| Diferença total Paula vs Williams | 2 pontos (excelente equilíbrio) |
| Sprint com maior carga | Sprint 2 e 3 (26 pts cada) — justificado pela fundação funcional |
| Sprint com menor carga | Sprint 4 e 6 (21 pts cada) — adequado ao escopo |
| Tarefa mais complexa | T8, T19 e T20 (8 pts) — cadastro de produto e checkout/processamento |
| Distribuição de tipos | Ambos fazem Backend + Frontend + Testes |

---

## 11. Mapa de Dependências

```
Sprint 1 — Fundação ✅
    │
    │  Models, migrations, admin, EmailBackend, PostgreSQL
    │
    ▼
Sprint 2 — Autenticação, Perfil e Endereços
    │
    │  Dependência: models prontos (Sprint 1)
    │  Entrega: login, cadastro, perfil, endereços, base.html, CSS
    │
    ▼
Sprint 3 — Catálogo de Produtos e Gestão do Vendedor
    │
    │  Dependência: autenticação + SellerProfile (Sprint 2)
    │  Entrega: CRUD produto, catálogo público, detalhes, painel vendedor
    │
    ▼
Sprint 4 — Busca, Filtros e Carrinho
    │
    │  Dependência: catálogo (Sprint 3) + login (Sprint 2)
    │  Entrega: busca, filtros, carrinho completo
    │
    ▼
Sprint 5 — Checkout, Pedidos e Histórico
    │
    │  Dependência: carrinho (Sprint 4) + endereços (Sprint 2) + SellerProfile (Sprint 2)
    │  Entrega: checkout, pedido, estoque, frete, pagamento simulado, histórico
    │
    ▼
Sprint 6 — Dashboard do Vendedor, Integração e Finalização
    │
    │  Dependência: pedidos (Sprint 5) + tudo anterior
    │  Entrega: dashboard vendedor, status pedido, testes e2e, UX, docs
    │
    ▼
    🏁 Marketplace completo e pronto para apresentação
```

### Dependências entre funcionalidades (cross-Sprint)

```
CustomUser (S1) ──────► login/cadastro (S2)
                 ──────► SellerProfile (S1/S2)
                 ──────► Address (S2)

SellerProfile (S1/S2) ─► Product.seller (S3)
                       ─► frete no checkout (S5)

Product (S1/S3) ──────► catálogo público (S3)
                ──────► busca/filtros (S4)
                ──────► CartItem (S4)
                ──────► OrderItem (S5)

Stock (S1/S3) ────────► adicionar ao carrinho (S4)
               ────────► descontar no checkout (S5)

Cart (S1/S4) ─────────► checkout (S5)

Address (S1/S2) ──────► checkout (S5)

Order (S1/S5) ────────► histórico cliente (S5)
               ────────► dashboard vendedor (S6)
```

---

## 12. Definition of Done Geral

Para qualquer tarefa ser considerada **concluída**, deve atender (quando aplicável):

| Critério | Descrição |
|----------|-----------|
| Implementação | Código funcional, sem erros de sintaxe ou runtime |
| Integração | Funcionalidade integrada com o restante do sistema |
| Validação | Django Forms valida dados antes de persistir |
| Tratamento de erros | Erros tratados com mensagens ao usuário (nunca exceções do banco expostas) |
| Persistência | Dados corretamente salvos/recuperados do PostgreSQL |
| Permissões | `@login_required` + verificação de propriedade onde necessário |
| Testes | Testes automatizados passando para a funcionalidade |
| Revisão | Code review por outro membro (PR para `develop`) |
| Git | Branch nomeada corretamente, commits seguindo convenção |
| Design System | Templates seguem tokens CSS, BEM, sombras sólidas, neo-brutalism |
| Responsividade | Funciona em 375px, 768px, 1280px |
| Ambiente local | Funciona em `localhost:8000` com PostgreSQL local |

---

## 13. Checklist Final do Projeto

- [x] Existem exatamente 6 Sprints
- [x] As Sprints estão em ordem lógica
- [x] As dependências foram consideradas
- [x] Existe fatiamento vertical
- [x] Os RFs estão distribuídos
- [x] Nenhum RF ficou sem tarefa
- [x] Cada tarefa possui responsável
- [x] Cada tarefa possui Story Points
- [x] Cada tarefa possui detalhamento (objetivo, o que fazer, dependências, resultado, DoD)
- [x] Paula e Williams possuem distribuição equilibrada
- [x] O CTO não foi utilizado artificialmente para aumentar a capacidade
- [x] A área do vendedor não foi colocada em uma Sprint apenas por conveniência
- [x] O fluxo de compra possui dependências corretas
- [x] Pagamento está corretamente tratado como simulado
- [x] Frete considera a regra definida pelo vendedor/km
- [x] Não foram inventadas integrações externas desnecessárias
- [x] As Sprints possuem entregas demonstráveis
- [x] O planejamento pode ser convertido em Issues do Linear
