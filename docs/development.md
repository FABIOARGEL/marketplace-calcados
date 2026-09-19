# Padrões de Desenvolvimento — Marketplace de Calçados

> Guia de referência para o time de desenvolvimento.
> Versão: 1.1 | Sprint 2 (atualizado com decisões de negócio: login por e-mail, endereços, frete, pagamento simulado)

---

## 1. Princípios Gerais

- **Simplicidade primeiro**: prefira a solução mais simples que funcione.
- **Baixo acoplamento, alta coesão**: cada module/app faz uma coisa bem.
- **Responsabilidade única**: funções e classes com uma única razão para mudar.
- **Nomes claros**: prefira `calculate_order_total()` a `calc()`.
- **Funções pequenas**: se uma função tem mais de 30 linhas, considere extrair.
- **Evite duplicação**: extraia lógica comum para funções reutilizáveis.
- **Não antecipe funcionalidades**: implemente apenas o que está no escopo da Sprint atual.

---

## 2. Convenções de Código Python

### Estilo
Seguir a [PEP 8](https://peps.python.org/pep-0008/):
- Indentação: **4 espaços** (não tabs)
- Comprimento máximo de linha: **88 caracteres**
- Importações: stdlib → third-party → local (separados por linha em branco)

### Nomenclatura
| Elemento | Convenção | Exemplo |
|----------|-----------|---------|
| Classes | PascalCase | `CustomUser`, `SellerProfile` |
| Funções e variáveis | snake_case | `get_user_cart()`, `order_total` |
| Constantes | UPPER_SNAKE | `MAX_CART_ITEMS = 50` |
| Apps Django | snake_case | `apps.users`, `apps.products` |
| Arquivos | snake_case | `models.py`, `test_foundation.py` |

### Docstrings
Use docstrings em português para classes e funções públicas:
```python
def calcular_total(carrinho):
    """
    Calcula o valor total do carrinho somando os subtotais dos itens.

    Args:
        carrinho: instância de Cart

    Returns:
        Decimal: valor total do carrinho
    """
```

---

## 3. Padrões Django

### Models
- Sempre defina `__str__` retornando algo descritivo.
- Defina `verbose_name` e `verbose_name_plural` na classe `Meta`.
- Use `ordering` na classe `Meta` quando relevante.
- Use `auto_now_add` para `created_at` e `auto_now` para `updated_at`.
- Use `DecimalField` para valores monetários (nunca `FloatField`).
- Use `TextChoices` para campos com opções fixas.

### Views
- Prefira views baseadas em funções (FBV) na Sprint 2. CBVs quando houver padrão repetitivo.
- Proteja views com `@login_required` quando necessário.
- Use `get_object_or_404()` ao buscar um objeto por PK.
- Nunca exponha exceções do banco ao usuário final.

### URLs
- Cada app deve ter seu próprio `urls.py`.
- Nomes de URLs devem ser descritivos: `name='product-detail'`.
- Use `include()` no `config/urls.py` para incluir rotas dos apps.

### Templates
- Estrutura sugerida: `templates/<app>/<funcionalidade>.html`
- Use o sistema de herança do Django com `{% extends 'base.html' %}`.
- Evite lógica de negócio em templates.

### Formulários
- Use `ModelForm` quando o formulário reflete um Model diretamente.
- Valide dados no método `clean()` do formulário.
- Nunca confie em dados do cliente sem validação.

---

## 4. Git — Fluxo de Trabalho

### Branches principais
| Branch | Descrição |
|--------|-----------|
| `main` | Código estável, revisado e testado |
| `develop` | Branch de integração das features |

### Branches de funcionalidade
```
feature/<nome-da-funcionalidade>
```

**Exemplos:**
```
feature/user-authentication
feature/product-catalog
feature/shopping-cart
feature/order-checkout
feature/seller-dashboard
```

### Fluxo padrão
```bash
# 1. Atualizar develop antes de iniciar
git checkout develop
git pull origin develop

# 2. Criar branch da feature
git checkout -b feature/nome-da-funcionalidade

# 3. Desenvolver, commitar aos poucos
git add .
git commit -m "feat: descrição objetiva da mudança"

# 4. Abrir Pull Request para develop
# 5. Code review por outro membro
# 6. Merge aprovado → deletar branch da feature
```

---

## 5. Convenção de Commits

Use o padrão **Conventional Commits** (simplificado):

```
<tipo>: <descrição curta em português>
```

| Tipo | Quando usar |
|------|-------------|
| `feat` | Nova funcionalidade |
| `fix` | Correção de bug |
| `docs` | Documentação |
| `test` | Adição ou correção de testes |
| `refactor` | Refatoração sem mudar comportamento |
| `chore` | Configuração, dependências, gitignore |
| `style` | Formatação, espaços, ponto e vírgula |

**Exemplos:**
```
feat: adicionar formulário de cadastro de usuário
fix: corrigir cálculo de total no carrinho
docs: atualizar README com instruções de instalação
test: adicionar testes para o modelo de pedido
chore: adicionar django-environ ao requirements.txt
```

### Regras de commit
- Um commit = uma mudança relacionada
- Mensagem no **imperativo**: "adicionar", não "adicionado"
- **Nunca commitar:** `.env`, senhas, credenciais, arquivos de IDE

---

## 6. Testes

### Estrutura
```
tests/
├── __init__.py
├── test_foundation.py      ← Sprint 1
└── <app>/
    ├── test_models.py
    ├── test_views.py
    └── test_forms.py
```

### Executar testes
```bash
# Todos os testes
python manage.py test

# Apenas os testes de fundação
python manage.py test tests

# Testes de um app específico
python manage.py test tests.users
```

### Boas práticas de teste
- Um teste por comportamento esperado
- Nomes descritivos: `test_usuario_nao_autenticado_nao_acessa_carrinho`
- Use `setUp()` para dados reutilizáveis
- Teste caminhos felizes e de erro
- Crie pelo menos um teste para cada model criado

---

## 7. Variáveis de Ambiente

**Nunca** coloque valores sensíveis diretamente no código.

Use o arquivo `.env` (nunca commitado) com base no `.env.example`:

```bash
# Copiar template
cp .env.example .env

# Editar com seus valores reais
# Gerar SECRET_KEY:
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## 8. Revisão de Código (Code Review)

Antes de aprovar um PR, verifique:
- [ ] O código segue os padrões deste documento?
- [ ] Existem testes para a funcionalidade?
- [ ] Os testes passam?
- [ ] O código não duplica lógica existente?
- [ ] Credenciais ou arquivos sensíveis foram inadvertidamente incluídos?
- [ ] A descrição do PR está clara?
