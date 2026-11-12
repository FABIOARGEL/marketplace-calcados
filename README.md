
# Marketplace de Calçados

Marketplace web para venda de calçados, desenvolvido como projeto acadêmico de desenvolvimento de software.

A plataforma permite que clientes encontrem e comprem calçados e que vendedores gerenciem produtos, estoque e pedidos.

## Índice

- [Objetivo](#objetivo)
- [Funcionalidades](#funcionalidades)
- [Stack Tecnológica](#stack-tecnológica)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Pré-requisitos](#pré-requisitos)
- [Instalação](#instalação)
- [Configuração do Ambiente](#configuração-do-ambiente)
- [Configuração do PostgreSQL](#configuração-do-postgresql)
- [Migrations e Dados Iniciais](#migrations-e-dados-iniciais)
- [Execução Local](#execução-local)
- [Superusuário](#superusuário)
- [Testes Automatizados](#testes-automatizados)
- [Fluxo de Contribuição](#fluxo-de-contribuição)
- [Documentação Técnica](#documentação-técnica)
- [Licença](#licença)

---

## Objetivo

Construir um marketplace web de calçados com dois perfis principais:

- **Cliente:** realiza cadastro, pesquisa produtos, adiciona itens ao carrinho, finaliza compras e acompanha pedidos.
- **Vendedor:** cadastra produtos, administra estoque por tamanho, acompanha pedidos e atualiza seus status.

## Funcionalidades

### Cliente

- Cadastro e autenticação por e-mail e senha.
- Visualização do catálogo de produtos ativos.
- Pesquisa e filtros por categoria, marca, tamanho e faixa de preço.
- Visualização dos detalhes dos produtos.
- Gerenciamento de endereços de entrega.
- Adição, atualização e remoção de itens do carrinho.
- Finalização de pedidos.
- Consulta ao histórico e aos detalhes dos pedidos.

### Vendedor

- Cadastro e gerenciamento de produtos.
- Edição e desativação de produtos.
- Controle de estoque por tamanho.
- Visualização de pedidos relacionados aos seus produtos.
- Atualização do status dos pedidos.
- Painel de gerenciamento da loja e acompanhamento de vendas.

### Observações sobre simulações

- **Frete:** calculado com base na distância e na tarifa por quilômetro configuradas pelo vendedor. Não utiliza integração com serviços de mapas.
- **Pagamento:** os métodos disponíveis são simulados. O projeto não realiza transações financeiras reais nem utiliza gateway de pagamento.

## Stack Tecnológica

| Camada | Tecnologia | Descrição |
|---|---|---|
| Linguagem | Python | 3.11 ou superior |
| Framework Web | Django | 4.2 |
| Banco de Dados | PostgreSQL | 14 ou superior |
| Driver do banco | psycopg2-binary | Conexão com PostgreSQL |
| Ambiente | django-environ | Leitura de variáveis do `.env` |
| Imagens | Pillow | Processamento de imagens |
| Versionamento | Git e GitHub | Controle de versão |
| Front-end | HTML, CSS e JavaScript | Interface web com templates Django |

## Estrutura do Projeto

```text
marketplace-calcados/
│
├── manage.py
├── README.md
├── .env.example
├── .gitignore
├── requirements.txt
│
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── apps/
│   ├── users/       # Usuários, autenticação, perfis e endereços
│   ├── products/    # Produtos, categorias, imagens e estoque
│   │   └── fixtures/
│   │       └── categories.json
│   ├── cart/        # Carrinho e itens
│   ├── orders/      # Pedidos, itens e histórico
│   └── sellers/     # Painel e gerenciamento do vendedor
│
├── templates/       # Templates HTML do Django
├── static/          # Arquivos estáticos
├── tests/           # Testes de fundação
│
└── docs/
    ├── apresentacao.html
    ├── architecture.md
    ├── design-system.md
    ├── development.md
    ├── requirements.md
    ├── REQUISITOS.md
    ├── sprints.md
    └── vertical-slicing.md
```

## Pré-requisitos

Antes de iniciar, instale:

- Python 3.11 ou superior.
- PostgreSQL 14 ou superior.
- Git.
- pip, gerenciador de pacotes do Python.

## Instalação

### 1. Clonar o repositório

```bash
git clone https://github.com/FABIOARGEL/marketplace-calcados.git
cd marketplace-calcados
```

### 2. Criar o ambiente virtual

**Windows — PowerShell:**

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

Se houver restrição de execução:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
venv\Scripts\Activate.ps1
```

**Windows — CMD:**

```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**Linux ou macOS:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar as dependências

Com o ambiente virtual ativado:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Configuração do Ambiente

### 1. Criar o arquivo `.env`

Copie o arquivo de exemplo:

**PowerShell:**

```powershell
Copy-Item .env.example .env
```

**CMD:**

```cmd
copy .env.example .env
```

**Linux ou macOS:**

```bash
cp .env.example .env
```

### 2. Gerar uma SECRET_KEY

Execute:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copie a chave gerada e utilize-a no arquivo `.env`.

### 3. Configurar as variáveis

Edite o arquivo `.env`:

```env
SECRET_KEY=sua-chave-secreta-gerada
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=marketplace_calcados
DB_USER=postgres
DB_PASSWORD=sua-senha-do-postgresql
DB_HOST=localhost
DB_PORT=5432
```

As variáveis correspondem às configurações utilizadas em `config/settings.py`.

**Importante:** o arquivo `.env` contém configurações locais e credenciais. Não o envie para o Git. Utilize apenas o `.env.example` como modelo compartilhado.

## Configuração do PostgreSQL

### 1. Acessar o PostgreSQL

No terminal:

```bash
psql -U postgres
```

Informe a senha do usuário administrador quando solicitada.

### 2. Criar o banco de dados

Execute no terminal `psql`:

```sql
CREATE DATABASE marketplace_calcados;
```

O exemplo utiliza o usuário `postgres`. Caso utilize outro usuário, configure os valores correspondentes em `.env` e conceda as permissões necessárias no PostgreSQL.

Para sair:

```sql
\q
```

## Migrations e Dados Iniciais

### 1. Aplicar as migrations

Na raiz do projeto:

```bash
python manage.py migrate
```

Esse comando cria ou atualiza as tabelas do banco de dados conforme as migrations das aplicações.

### 2. Carregar as categorias iniciais

O projeto disponibiliza uma fixture com oito categorias de calçados:

- Tênis
- Sandália
- Bota
- Sapatilha
- Sapato Social
- Chinelo
- Chuteira
- Mocassim

Para carregá-las:

```bash
python manage.py loaddata apps/products/fixtures/categories.json
```

Execute a carga após aplicar as migrations. Se a fixture já tiver sido carregada, evite executá-la novamente sem verificar os registros existentes.

### 3. Verificar as migrations

```bash
python manage.py showmigrations
```

### 4. Criar novas migrations

Após alterações nos modelos:

```bash
python manage.py makemigrations
python manage.py migrate
```

## Execução Local

Com o ambiente virtual ativado, PostgreSQL configurado e migrations aplicadas:

```bash
python manage.py runserver
```

O servidor de desenvolvimento ficará disponível em:

http://127.0.0.1:8000/

### Principais rotas

| Rota | Descrição |
|---|---|
| `/` | Página inicial |
| `/admin/` | Painel administrativo Django |
| `/health/` | Verificação de funcionamento |
| `/usuarios/` | Cadastro, autenticação, perfil e endereços |
| `/produtos/` | Catálogo e gerenciamento de produtos |
| `/carrinho/` | Carrinho de compras |
| `/pedidos/` | Checkout e pedidos |
| `/painel/` | Painel do vendedor |

As rotas internas de cada aplicação estão organizadas em seus respectivos arquivos `urls.py`.

## Superusuário

Para criar uma conta administrativa:

```bash
python manage.py createsuperuser
```

Siga as instruções do terminal para informar os dados solicitados.

Depois, acesse:

http://127.0.0.1:8000/admin/

## Testes Automatizados

### Executar todos os testes

```bash
python manage.py test
```

### Executar os testes de uma aplicação específica

Exemplo:

```bash
python manage.py test apps.products
```

Outras aplicações podem ser verificadas utilizando seus respectivos caminhos:

```bash
python manage.py test apps.users
python manage.py test apps.cart
python manage.py test apps.orders
python manage.py test apps.sellers
```

### Verificar a integridade do projeto

```bash
python manage.py check
```

## Fluxo de Contribuição

1. Atualize sua branch de trabalho com as alterações mais recentes da equipe.
2. Crie uma branch específica para a tarefa.
3. Implemente as alterações seguindo os padrões do projeto.
4. Execute os testes relacionados.
5. Faça commits com mensagens descritivas.
6. Envie a branch para o repositório remoto.
7. Abra um Pull Request para revisão.

Exemplo de criação de branch:

```bash
git checkout -b feature/nome-da-funcionalidade
```

Exemplo de commit:

```bash
git add .
git commit -m "feat: adicionar gerenciamento de produtos"
```

Consulte `docs/development.md` para conhecer os padrões de desenvolvimento e versionamento.

## Documentação Técnica

| Documento | Descrição |
|---|---|
| [REQUISITOS.md](docs/REQUISITOS.md) | Especificação dos requisitos funcionais e não funcionais |
| [requirements.md](docs/requirements.md) | Status dos requisitos funcionais e rastreabilidade por Sprint |
| [architecture.md](docs/architecture.md) | Arquitetura, componentes, rotas e modelo de dados |
| [sprints.md](docs/sprints.md) | Planejamento e organização das Sprints |
| [vertical-slicing.md](docs/vertical-slicing.md) | Planejamento das fatias verticais |
| [development.md](docs/development.md) | Padrões de código, Git e commits |
| [design-system.md](docs/design-system.md) | Identidade visual e padrões de interface |
| [apresentacao.html](docs/apresentacao.html) | Material de apresentação do projeto |

## Licença

Projeto acadêmico desenvolvido para fins educacionais. Todos os direitos reservados aos autores.
