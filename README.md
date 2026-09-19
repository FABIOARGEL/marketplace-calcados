# Marketplace de Calçados

Marketplace web para venda de calçados, desenvolvido como projeto acadêmico de desenvolvimento de software.

Permite que **clientes** descubram e comprem calçados e que **vendedores** gerenciem seus produtos, estoque e pedidos — tudo em uma única plataforma integrada.

---

## Índice

- [Objetivo](#objetivo)
- [Funcionalidades Previstas](#funcionalidades-previstas)
- [Stack Tecnológica](#stack-tecnologica)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Pré-requisitos](#pre-requisitos)
- [Instalação](#instalacao)
- [Configuração do Ambiente](#configuracao-do-ambiente)
- [Configuração do PostgreSQL](#configuracao-do-postgresql)
- [Execução Local](#execucao-local)
- [Migrations](#migrations)
- [Superusuário](#superusuario)
- [Testes Automatizados](#testes-automatizados)
- [Fluxo de Contribuição](#fluxo-de-contribuicao)
- [Estratégia de Branches](#estrategia-de-branches)
- [Documentação](#documentacao)
- [Design System](#design-system)
- [Licença](#licenca)

---

<a id="objetivo"></a>
## Objetivo

Construir um marketplace web de calçados com dois perfis de usuário:

- **Cliente**: cria conta, pesquisa produtos por filtros (marca, categoria, tamanho, preço), adiciona ao carrinho e realiza pedidos.
- **Vendedor**: cadastra produtos, gerencia estoque por tamanho e acompanha/atualiza pedidos dos seus produtos.

---

<a id="funcionalidades-previstas"></a>
## Funcionalidades Previstas

### Cliente
- Criar conta e realizar autenticação (login/logout)
- Visualizar catálogo de calçados ativos
- Pesquisar e filtrar por categoria, marca, tamanho e preço
- Adicionar produtos e tamanhos específicos ao carrinho
- Finalizar compras e acompanhar pedidos
- Consultar histórico detalhado de compras

### Vendedor
- Cadastrar, editar e desativar produtos (soft-delete)
- Controlar estoque individualizado por tamanho
- Visualizar pedidos contendo seus produtos
- Atualizar status de envio dos pedidos

---

<a id="stack-tecnologica"></a>
## Stack Tecnológica

| Camada | Tecnologia | Versão / Descrição |
|--------|-----------|--------------------|
| Linguagem | Python | 3.11+ (testado em 3.14) |
| Framework Web | Django | 4.2 LTS |
| Banco de Dados | PostgreSQL | 14+ |
| Driver BD | psycopg2-binary | 2.9+ |
| Variáveis de Ambiente | django-environ | 0.11+ |
| Versionamento | Git + GitHub | GitHub Flow / Gitflow simplificado |
| Gestão de Tarefas | Linear | Acompanhamento de Sprints |
| Comunicação | WhatsApp | Alinhamento do time |

---

<a id="estrutura-do-projeto"></a>
## Estrutura do Projeto

```
marketplace-calcados/
│
├── manage.py               ← Utilitário de linha de comando do Django
├── README.md               ← Documentação principal do repositório
├── .gitignore              ← Arquivos e diretórios ignorados pelo Git
├── .env.example            ← Modelo de variáveis de ambiente (sem credenciais reais)
├── requirements.txt        ← Dependências do projeto Python
│
├── config/                 ← Configuração central do projeto Django
│   ├── __init__.py
│   ├── settings.py         ← Configurações (banco, apps, middleware, auth)
│   ├── urls.py             ← Roteamento principal e health check
│   ├── wsgi.py             ← Ponto de entrada WSGI
│   └── asgi.py             ← Ponto de entrada ASGI
│
├── apps/                   ← Aplicações modulares do domínio
│   ├── __init__.py
│   ├── users/              ← Usuários customizados (Cliente/Vendedor) e perfis
│   ├── products/           ← Produtos, categorias, imagens e estoque por tamanho
│   ├── cart/               ← Carrinho de compras e itens do carrinho
│   └── orders/             ← Pedidos, itens do pedido e histórico
│
├── docs/                   ← Documentação técnica e de engenharia
│   ├── REQUISITOS.md       ← Especificação de requisitos (RF e RNF)
│   ├── requirements.md     ← Requisitos funcionais (RF), status e rastreabilidade
│   ├── architecture.md     ← Arquitetura do sistema e responsabilidades
│   ├── vertical-slicing.md ← Planejamento de fatias verticais por Sprint
│   ├── development.md      ← Padrões de código, Git e convenção de commits
│   └── design-system.md    ← Design System: paleta, tipografia, componentes e padrões visuais
│
└── tests/                  ← Testes automatizados
    ├── __init__.py
    └── test_foundation.py  ← Testes de fundação e integridade (Sprint 1)
```

---

<a id="pre-requisitos"></a>
## Pré-requisitos

Certifique-se de ter instalado em sua máquina:

- **Python 3.11+** (com `pip` configurado)
- **PostgreSQL 14+** em execução localmente
- **Git**

---

<a id="instalacao"></a>
## Instalação

### 1. Clonar o repositório

```bash
git clone https://github.com/FABIOARGEL/marketplace-calcados.git
cd marketplace-calcados
```

### 2. Criar e ativar o ambiente virtual

#### No Windows:
```bash
# Criar ambiente virtual
python -m venv venv

# Ativação via PowerShell:
venv\Scripts\Activate.ps1
# (Se houver restrição de execução no PowerShell: Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass)

# Ativação via Prompt de Comando (CMD):
venv\Scripts\activate.bat

# Ativação via Git Bash:
source venv/Scripts/activate
```

#### No Linux / macOS:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar as dependências

```bash
pip install -r requirements.txt
```

---

<a id="configuracao-do-ambiente"></a>
## Configuração do Ambiente

### 1. Criar o arquivo `.env` a partir do modelo

```bash
# Windows (PowerShell) / Linux / macOS:
cp .env.example .env

# Windows (CMD):
copy .env.example .env
```

### 2. Gerar uma `SECRET_KEY` segura

Execute no terminal:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 3. Configurar os valores no `.env`

Abra o arquivo `.env` gerado e defina suas credenciais:

```env
SECRET_KEY=cole_aqui_a_chave_gerada
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=marketplace_calcados
DB_USER=marketplace_user
DB_PASSWORD=sua_senha_aqui
DB_HOST=localhost
DB_PORT=5432
```

---

<a id="configuracao-do-postgresql"></a>
## Configuração do PostgreSQL

### 1. Acessar o terminal do PostgreSQL (psql)

```bash
psql -U postgres
```

### 2. Criar usuário e banco de dados

Recomenda-se criar o banco definindo o usuário como proprietário (`OWNER`), garantindo permissões totais no PostgreSQL 15+:

```sql
CREATE USER marketplace_user WITH PASSWORD 'sua_senha_aqui';
CREATE DATABASE marketplace_calcados OWNER marketplace_user;
GRANT ALL PRIVILEGES ON DATABASE marketplace_calcados TO marketplace_user;
\q
```

> **Dica:** Se preferir utilizar o usuário padrão `postgres`, basta manter `DB_USER=postgres` e a senha correspondente no arquivo `.env`.

---

<a id="execucao-local"></a>
## Execução Local

### 1. Iniciar o servidor de desenvolvimento

```bash
python manage.py runserver
```

### 2. Endpoints disponíveis

- **Health Check:** [http://localhost:8000/health/](http://localhost:8000/health/) *(Retorna JSON de validação operacional)*
- **Painel Administrativo:** [http://localhost:8000/admin/](http://localhost:8000/admin/)
- **Raiz do projeto (`/`):** [http://localhost:8000](http://localhost:8000) *(As rotas visuais de catálogo e vitrine serão integradas na Sprint 2)*

---

<a id="migrations"></a>
## Migrations

### Aplicar migrations ao banco de dados

```bash
python manage.py migrate
```

### Criar novas migrations (após alterar modelos em `apps/`)

```bash
python manage.py makemigrations
```

### Verificar o status das migrations

```bash
python manage.py showmigrations
```

---

<a id="superusuario"></a>
## Superusuário

Para acessar o painel Django Admin (`/admin/`), crie um usuário administrador:

```bash
python manage.py createsuperuser
```

Siga as instruções para definir username, e-mail e senha.

---

<a id="testes-automatizados"></a>
## Testes Automatizados

### Executar a suíte completa de testes

```bash
python manage.py test
```

### Executar os testes de fundação (Sprint 1)

```bash
python manage.py test tests
```

### Checagem de integridade do Django (sem rodar testes)

```bash
python manage.py check
```

---

<a id="fluxo-de-contribuicao"></a>
## Fluxo de Contribuição

1. **Atualize sua base local:**
   ```bash
   git checkout main
   git pull origin main
   ```
   *(Caso utilize branch `develop`, sincronize com `git checkout develop && git pull origin develop`)*

2. **Crie uma branch específica para a funcionalidade:**
   ```bash
   git checkout -b feature/nome-da-funcionalidade
   ```

3. **Desenvolva e realize commits seguindo o padrão Conventional Commits:**
   ```bash
   git add .
   git commit -m "feat: adicionar listagem de produtos com filtros"
   ```

4. **Envie a branch para o repositório remoto:**
   ```bash
   git push origin feature/nome-da-funcionalidade
   ```

5. **Abra um Pull Request (PR)** detalhando as alterações para revisão da equipe.

> Consulte o guia completo em [docs/development.md](docs/development.md) para convenções detalhadas de código e commits.

---

<a id="estrategia-de-branches"></a>
## Estratégia de Branches

| Branch | Finalidade |
|--------|------------|
| `main` | Código estável, homologado e pronto para apresentação |
| `develop` | Branch de integração de novas funcionalidades |
| `feature/<nome>` | Branches de trabalho para cada funcionalidade ou fatia |

**Exemplos de nomenclatura de branches:**
```
feature/user-authentication
feature/product-catalog
feature/shopping-cart
feature/order-checkout
feature/seller-dashboard
```

---

<a id="documentacao"></a>
## Documentação Técnica

| Documento | Descrição |
|-----------|-----------|
| [docs/REQUISITOS.md](docs/REQUISITOS.md) | Lista oficial de requisitos funcionais (RF) e não funcionais (RNF) |
| [docs/requirements.md](docs/requirements.md) | Requisitos funcionais (RF), status e rastreabilidade por Sprint |
| [docs/architecture.md](docs/architecture.md) | Arquitetura do sistema, diagrama DER (Mermaid) e responsabilidades |
| [docs/vertical-slicing.md](docs/vertical-slicing.md) | Planejamento de fatias verticais por Sprint |
| [docs/development.md](docs/development.md) | Padrões de código PEP 8, convenções de commits e Git |
| [docs/design-system.md](docs/design-system.md) | **Design System** — paleta de cores, tipografia, componentes, padrões visuais e checklist de telas |
| [docs/AI-STANDARDS.md](docs/AI-STANDARDS.md) | **Contrato da IA** — padrões, decisões, lacunas e checklist completo para desenvolvimento com IA |
| [docs/PROMPT-RULES.md](docs/PROMPT-RULES.md) | **Regras compactas para IA** — versão resumida para colar no chat do Antigravity |

---

<a id="design-system"></a>
## Design System

O projeto adota um **Design System** oficial que define a identidade visual e os padrões de implementação para toda a equipe.

**Conceito:** Neo-Brutalism + Streetwear + E-commerce moderno

**O documento cobre:**
- Paleta de cores com tokens CSS (`--color-bg`, `--color-primary`, `--color-accent` …)
- Hierarquia tipográfica (Space Grotesk + Inter)
- Sistema de espaçamento em escala de 4px
- Bordas 2px e sombras sólidas (sem blur) — estilo neo-brutalista
- Especificação completa de componentes: Navbar, Botões, Inputs, Cards, Badges, Alerts, Toasts, Modais
- Padrão do Product Card com HTML de exemplo
- Nomenclatura de produtos, imagens e campos de cadastro
- Estrutura de arquivos CSS e templates Django
- Regras de responsividade (mobile-first, 375 / 768 / 1280px)
- Requisitos de acessibilidade (WCAG AA)
- Design Tokens e checklist de 40+ itens para validação de novas telas

> **Consulte [docs/design-system.md](docs/design-system.md) antes de criar qualquer nova tela ou componente.**

---

<a id="ia"></a>
## Desenvolvimento com IA (Antigravity)

Este projeto utiliza o **Antigravity IDE** como assistente de desenvolvimento. Para garantir consistência entre sessões, o projeto inclui um sistema de regras automáticas.

### Como funciona

| Arquivo | Função | Quando usar |
|---|---|---|
| `GEMINI.md` | Regras carregadas **automaticamente** pelo Antigravity em toda nova conversa | Sempre ativo — não precisa fazer nada |
| `docs/AI-STANDARDS.md` | Referência completa com todos os padrões e decisões | Consulte para dúvidas detalhadas |

### Regras automáticas (GEMINI.md)

O arquivo `GEMINI.md` na raiz do projeto é carregado automaticamente pelo Antigravity em toda nova conversa. Ele instrui a IA a:

- Consultar `docs/` antes de implementar qualquer coisa
- Seguir a stack: Django 4.2 LTS + PostgreSQL + CSS vanilla
- Respeitar o Design System Neo-Brutalism (bordas 2px, sombras sólidas, tokens CSS)
- Não criar APIs REST, não usar SQLite, não usar jQuery
- Registrar lacunas explicitamente em vez de inventar padrões

> **Para o Antigravity:** as regras já estão ativas via `GEMINI.md`. Nenhuma configuração adicional é necessária.

---

<a id="licenca"></a>
## Licença

Projeto acadêmico desenvolvido para fins educacionais. Todos os direitos reservados aos autores.

