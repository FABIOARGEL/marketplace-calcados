# Requisitos do Sistema — Marketplace de Calçados

> **Documento vivo:** fonte de referência para o acompanhamento da implementação dos requisitos.
> Versão: 2.0 | Atualizado após a Sprint 6.
>
> Para consultar a especificação original e as lacunas identificadas, consulte também [REQUISITOS.md](REQUISITOS.md).

---

## Requisitos Funcionais

| ID | Descrição | Status | Sprint |
|---|---|---|---|
| RF01 | O sistema deve permitir que o usuário crie uma conta com e-mail, senha, nome e tipo (cliente ou vendedor). | Implementado | Sprint 2 |
| RF02 | O sistema deve permitir que o usuário faça login usando e-mail e senha e realize logout. | Implementado | Sprint 2 |
| RF03 | O sistema deve permitir que o usuário visualize e edite seus dados cadastrais. | Implementado | Sprint 2 |
| RF04 | O sistema deve permitir visualizar os calçados disponíveis para venda. | Implementado | Sprint 3 |
| RF05 | O sistema deve permitir visualizar os detalhes de um calçado, incluindo nome, descrição, preço, tamanho, marca e imagens. | Implementado | Sprint 3 |
| RF06 | O sistema deve permitir pesquisar calçados por nome ou descrição. | Implementado | Sprint 4 |
| RF07 | O sistema deve permitir filtrar calçados por categoria, tamanho, marca e faixa de preço. | Implementado | Sprint 4 |
| RF08 | O sistema deve permitir que o vendedor cadastre novos calçados. | Implementado | Sprint 3 |
| RF09 | O sistema deve permitir que o vendedor edite os dados de seus calçados. | Implementado | Sprint 3 |
| RF10 | O sistema deve permitir que o vendedor remova ou desative um calçado. | Implementado | Sprint 3 |
| RF11 | O sistema deve permitir que o usuário adicione calçados ao carrinho. | Implementado | Sprint 4 |
| RF12 | O sistema deve permitir que o usuário altere a quantidade de itens no carrinho. | Implementado | Sprint 4 |
| RF13 | O sistema deve permitir que o usuário remova itens do carrinho. | Implementado | Sprint 4 |
| RF14 | O sistema deve calcular o valor subtotal do carrinho (soma dos itens sem frete). | Implementado | Sprint 4 |
| RF15 | O sistema deve permitir que o usuário finalize uma compra através do checkout. | Implementado | Sprint 5 |
| RF16 | O sistema deve registrar os pedidos realizados com snapshot de preço unitário. | Implementado | Sprint 5 |
| RF17 | O sistema deve permitir que o usuário consulte seu histórico de pedidos. | Implementado | Sprint 5 |
| RF18 | O sistema deve permitir que o vendedor visualize os pedidos relacionados aos seus produtos. | Implementado | Sprint 6 |
| RF19 | O sistema deve permitir atualizar o status de um pedido. | Implementado | Sprint 6 |
| RF20 | O sistema deve controlar a quantidade disponível de cada calçado em estoque. | Implementado | Sprints 3 e 5 |
| RF21 | O sistema deve autenticar usuários por e-mail (não username). O e-mail deve ser único. | Implementado | Sprints 1 e 2 |
| RF22 | O usuário deve poder cadastrar, editar, excluir e visualizar múltiplos endereços de entrega. | Implementado | Sprint 2 |
| RF23 | O checkout deve permitir que o usuário selecione um dos seus endereços cadastrados para entrega. | Implementado | Sprint 5 |
| RF24 | O frete deve ser calculado com base na distância (km) e taxa por km configuradas pelo vendedor. Fórmula: `frete = distância_km × valor_por_km`. Cálculo simulado sem API de mapas nesta versão. | Implementado (simulado) | Sprint 5 |
| RF25 | O sistema deve registrar um pagamento simulado (sem processamento financeiro real). O usuário seleciona o método e o sistema registra aprovação fictícia. | Implementado (simulado) | Sprint 5 |

### Legenda de Status

- **Implementado:** funcionalidade desenvolvida e integrada ao sistema.
- **Implementado (simulado):** funcionalidade implementada sem integração com serviço financeiro ou externo real.
- **Em progresso:** funcionalidade parcialmente implementada.
- **Planejado:** funcionalidade prevista para desenvolvimento futuro.

---

## Requisitos Não Funcionais

| ID | Descrição | Observações |
|---|---|---|
| RNF01 | O sistema deve ser acessível através de navegadores web modernos. | Chrome, Firefox, Edge e Safari |
| RNF02 | O sistema deve possuir uma interface simples e intuitiva. | Interface voltada à facilidade de uso |
| RNF03 | O sistema deve ser responsivo. | Breakpoints: 640, 768, 1024 e 1280px |
| RNF04 | O sistema deve utilizar PostgreSQL para armazenamento dos dados. | Configurado na Sprint 1 |
| RNF05 | O sistema deve ser desenvolvido utilizando Django (Python). | Python 3.11+ / Django 4.2 |
| RNF06 | As senhas dos usuários devem ser armazenadas de forma segura. | AbstractUser e PBKDF2 |
| RNF07 | O sistema deve restringir o acesso às funcionalidades de acordo com o tipo de usuário. | Campo `user_type` no modelo |
| RNF08 | O sistema deve validar os dados enviados pelos usuários antes de armazená-los no banco de dados. | Forms e validações do Django |
| RNF09 | O sistema deve possuir código organizado e modular, facilitando sua manutenção. | Estrutura modular em `apps/` |
| RNF10 | O sistema deve utilizar Git e GitHub para controle de versão. | Configurado na Sprint 1 |
| RNF11 | O sistema deve apresentar tempo de resposta adequado para operações comuns, como consulta de produtos e acesso ao carrinho. | Consultas e operações do banco de dados |
| RNF12 | O sistema deve manter a integridade e consistência dos dados armazenados. | Chaves estrangeiras, restrições e migrations |
| RNF13 | O sistema deve tratar erros de forma adequada, evitando a exposição de informações internas da aplicação. | `DEBUG=False` em produção |

---

## Rastreabilidade por Sprint

| Sprint | Requisitos funcionais |
|---|---|
| Sprint 1 | RF21 (configuração inicial de autenticação por e-mail) |
| Sprint 2 | RF01, RF02, RF03, RF21 e RF22 |
| Sprint 3 | RF04, RF05, RF08, RF09, RF10 e RF20 |
| Sprint 4 | RF06, RF07, RF11, RF12, RF13 e RF14 |
| Sprint 5 | RF15, RF16, RF17, RF20, RF23, RF24 e RF25 |
| Sprint 6 | RF18 e RF19 |

---

## Fora do Escopo

- Aplicativo mobile nativo.
- Inteligência artificial para recomendação.
- Sistema avançado de análise de vendas.
- Integração com gateway de pagamento real (Mercado Pago, Stripe, PIX real etc.).
- Integração com API de cálculo de distância ou mapas.
- Sistemas complexos de logística.