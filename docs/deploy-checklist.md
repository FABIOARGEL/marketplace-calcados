
# Checklist de Implantação — Marketplace de Calçados

Este documento apresenta as verificações necessárias para preparar o Marketplace de Calçados para implantação em um ambiente de produção.

## 1. Código e dependências

- [ ] Confirmar que a branch de implantação contém as alterações aprovadas.
- [ ] Verificar se o código está atualizado.
- [ ] Criar o ambiente virtual:

```bash
python -m venv venv
```

- [ ] Ativar o ambiente virtual no Windows PowerShell:

```powershell
venv\Scripts\Activate.ps1
```

- [ ] Instalar as dependências:

```bash
pip install -r requirements.txt
```

- [ ] Confirmar a compatibilidade da versão do Python com Django 4.2.
- [ ] Executar a verificação do Django:

```bash
python manage.py check
```

## 2. Variáveis de ambiente

- [ ] Criar o arquivo `.env` no ambiente de implantação.
- [ ] Definir uma `SECRET_KEY` exclusiva e segura.
- [ ] Configurar `DEBUG=False`.
- [ ] Configurar `ALLOWED_HOSTS` com os domínios autorizados.
- [ ] Configurar as credenciais do PostgreSQL.
- [ ] Não armazenar credenciais diretamente no código-fonte.
- [ ] Não versionar o arquivo `.env`.

Variáveis necessárias:

```env
SECRET_KEY=sua-chave-secreta
DEBUG=False
ALLOWED_HOSTS=seudominio.com

DB_NAME=marketplace_calcados
DB_USER=usuario_do_banco
DB_PASSWORD=senha_segura
DB_HOST=host_do_postgresql
DB_PORT=5432
```

## 3. Banco de dados

- [ ] Criar o banco de dados PostgreSQL.
- [ ] Criar ou configurar o usuário de acesso.
- [ ] Conceder as permissões necessárias.
- [ ] Confirmar a conexão entre Django e PostgreSQL.
- [ ] Aplicar as migrations:

```bash
python manage.py migrate
```

- [ ] Verificar o estado das migrations:

```bash
python manage.py showmigrations
```

- [ ] Realizar uma cópia de segurança do banco de dados antes de atualizações importantes.

## 4. Dados iniciais

- [ ] Verificar se as categorias iniciais estão cadastradas.
- [ ] Caso necessário, carregar a fixture de categorias:

```bash
python manage.py loaddata apps/products/fixtures/categories.json
```

A fixture disponibiliza oito categorias de calçados.

- [ ] Verificar se os registros foram carregados corretamente.

## 5. Arquivos estáticos e mídia

- [ ] Configurar o armazenamento dos arquivos estáticos.
- [ ] Executar a coleta dos arquivos estáticos:

```bash
python manage.py collectstatic
```

- [ ] Verificar a configuração de `STATIC_ROOT`.
- [ ] Verificar a configuração de `MEDIA_ROOT`.
- [ ] Definir uma estratégia de armazenamento e backup para imagens enviadas pelos usuários.

## 6. Segurança

- [ ] Confirmar que `DEBUG=False`.
- [ ] Utilizar uma `SECRET_KEY` segura e privada.
- [ ] Restringir `ALLOWED_HOSTS` aos domínios autorizados.
- [ ] Utilizar HTTPS no ambiente de produção.
- [ ] Garantir que as credenciais do banco não estejam expostas.
- [ ] Verificar as permissões de acesso de clientes e vendedores.
- [ ] Confirmar que as páginas e operações protegidas exigem autenticação.
- [ ] Revisar as configurações de segurança do Django e do servidor.
- [ ] Executar a verificação de configurações de produção:

```bash
python manage.py check --deploy
```

## 7. Testes e validação

- [ ] Executar a suíte de testes:

```bash
python manage.py test
```

- [ ] Verificar a integridade da aplicação:

```bash
python manage.py check
```

- [ ] Testar o cadastro e a autenticação.
- [ ] Testar a navegação pelo catálogo.
- [ ] Testar a pesquisa e os filtros.
- [ ] Testar o gerenciamento de produtos e estoque.
- [ ] Testar o carrinho de compras.
- [ ] Testar o checkout e a criação de pedidos.
- [ ] Testar o histórico de pedidos.
- [ ] Testar o painel do vendedor e a atualização de status.
- [ ] Verificar o endpoint `/health/`.

## 8. Disponibilização da aplicação

- [ ] Configurar o servidor de aplicação compatível com Django.
- [ ] Configurar o servidor web ou proxy reverso, quando aplicável.
- [ ] Configurar o processo de execução da aplicação.
- [ ] Configurar domínio e HTTPS.
- [ ] Confirmar a comunicação com o PostgreSQL.
- [ ] Verificar os arquivos estáticos e as imagens.
- [ ] Consultar os logs para identificar erros.
- [ ] Confirmar o acesso à aplicação após a implantação.

## 9. Observações importantes

- O projeto utiliza PostgreSQL como banco de dados.
- O pagamento é simulado e não realiza transações financeiras reais.
- O cálculo de frete é simulado com base na distância e na tarifa configuradas pelo vendedor.
- A configuração definitiva de servidor, domínio, HTTPS e armazenamento de mídia depende da plataforma de hospedagem escolhida.

## 10. Aprovação final

- [ ] Código revisado e aprovado.
- [ ] Testes executados com sucesso.
- [ ] Banco de dados configurado.
- [ ] Variáveis de ambiente verificadas.
- [ ] Configurações de segurança revisadas.
- [ ] Aplicação validada no ambiente de implantação.

**Status da implantação:** Pendente de validação.