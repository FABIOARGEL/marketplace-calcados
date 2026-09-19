# Requisitos do Sistema — Marketplace de Calçados

> **Documento vivo (fonte da verdade para status de implementação).** Atualizado a cada Sprint.
> Versão: 1.1 | Sprint 2
>
> Para especificação detalhada dos requisitos e lacunas, consulte também [`REQUISITOS.md`](REQUISITOS.md).

---

## Requisitos Funcionais

| ID    | Descrição | Status |
|-------|-----------|--------|
| RF01  | O sistema deve permitir que o usuário crie uma conta com e-mail, senha, nome e tipo (cliente ou vendedor). | Planejado |
| RF02  | O sistema deve permitir que o usuário faça login usando **e-mail e senha** e realize logout. | Planejado |
| RF03  | O sistema deve permitir que o usuário visualize e edite seus dados cadastrais. | Planejado |
| RF04  | O sistema deve permitir visualizar os calçados disponíveis para venda. | Planejado |
| RF05  | O sistema deve permitir visualizar os detalhes de um calçado, incluindo nome, descrição, preço, tamanho, marca e imagens. | Planejado |
| RF06  | O sistema deve permitir pesquisar calçados por nome ou descrição. | Planejado |
| RF07  | O sistema deve permitir filtrar calçados por categoria, tamanho, marca e faixa de preço. | Planejado |
| RF08  | O sistema deve permitir que o vendedor cadastre novos calçados. | Planejado |
| RF09  | O sistema deve permitir que o vendedor edite os dados de seus calçados. | Planejado |
| RF10  | O sistema deve permitir que o vendedor remova ou desative um calçado. | Planejado |
| RF11  | O sistema deve permitir que o usuário adicione calçados ao carrinho. | Planejado |
| RF12  | O sistema deve permitir que o usuário altere a quantidade de itens no carrinho. | Planejado |
| RF13  | O sistema deve permitir que o usuário remova itens do carrinho. | Planejado |
| RF14  | O sistema deve calcular o valor subtotal do carrinho (soma dos itens sem frete). | Planejado |
| RF15  | O sistema deve permitir que o usuário finalize uma compra através do checkout. | Planejado |
| RF16  | O sistema deve registrar os pedidos realizados com snapshot de preço unitário. | Planejado |
| RF17  | O sistema deve permitir que o usuário consulte seu histórico de pedidos. | Planejado |
| RF18  | O sistema deve permitir que o vendedor visualize os pedidos relacionados aos seus produtos. | Planejado |
| RF19  | O sistema deve permitir atualizar o status de um pedido. | Planejado |
| RF20  | O sistema deve controlar a quantidade disponível de cada calçado em estoque. | Planejado |
| RF21  | O sistema deve autenticar usuários por **e-mail** (não username). O e-mail deve ser único. | Implementado |
| RF22  | O usuário deve poder cadastrar, editar, excluir e visualizar múltiplos endereços de entrega. | Planejado |
| RF23  | O checkout deve permitir que o usuário selecione um dos seus endereços cadastrados para entrega. | Planejado |
| RF24  | O frete deve ser calculado com base na distância (km) e taxa por km configuradas pelo vendedor. Fórmula: `frete = distância_km × valor_por_km`. Cálculo simulado sem API de mapas nesta versão. | Implementado (modelo) |
| RF25  | O sistema deve registrar um **pagamento simulado** (sem processamento financeiro real). O usuário seleciona o método e o sistema registra aprovação fictícia. | Implementado (modelo) |

### Legenda de Status
- **Implementado** — Código e migration aplicados, testes passando
- **Em progresso** — Parcialmente implementado
- **Planejado** — Previsto para sprint futura

---

## Requisitos Não Funcionais

| ID    | Descrição | Observações |
|-------|-----------|-------------|
| RNF01 | O sistema deve ser acessível através de navegadores web modernos. | Chrome, Firefox, Edge, Safari |
| RNF02 | O sistema deve possuir uma interface simples e intuitiva. | — |
| RNF03 | O sistema deve ser responsivo. | Mobile-first, breakpoints: 640/768/1024/1280px |
| RNF04 | O sistema deve utilizar PostgreSQL para armazenamento dos dados. | Configurado na Sprint 1 |
| RNF05 | O sistema deve ser desenvolvido utilizando Django (python). | Python 3.11+ / Django 4.2 LTS |
| RNF06 | As senhas dos usuários devem ser armazenadas de forma segura. | AbstractUser + PBKDF2 |
| RNF07 | O sistema deve restringir o acesso às funcionalidades de acordo com o tipo de usuário. | Campo `user_type` no modelo |
| RNF08 | O sistema deve validar os dados enviados pelos usuários antes de armazená-los no banco de dados. | Forms e validações do Django |
| RNF09 | O sistema deve possuir código organizado e modular, facilitando sua manutenção. | Estrutura `apps/` modular |
| RNF10 | O sistema deve utilizar Git e GitHub para controle de versão. | Configurado na Sprint 1 |
| RNF11 | O sistema deve apresentar tempo de resposta adequado para operações comuns, como consulta de produtos e acesso ao carrinho. | Índices e queries otimizadas |
| RNF12 | O sistema deve manter a integridade e consistência dos dados armazenados. | FK, unique_together, migrations |
| RNF13 | O sistema deve tratar erros de forma adequada, evitando a exposição de informações internas da aplicação. | DEBUG=False em produção |

---

## Fora do Escopo

- Aplicativo mobile nativo
- Inteligência artificial para recomendação
- Sistema avançado de análise de vendas
- Integração com gateway de pagamento real (Mercado Pago, Stripe, PIX real, etc.)
- Integração com API de cálculo de distância / mapas (frete usa distância informada pelo vendedor)
- Sistemas complexos de logística
