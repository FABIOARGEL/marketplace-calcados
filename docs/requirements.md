# Requisitos do Sistema — Marketplace de Calçados

> Documento vivo. Atualizado a cada Sprint.
> Versão: 1.0 | Sprint 1

---

## Requisitos Funcionais

| ID    | Descrição | Status |
|-------|-----------|--------|
| RF01  | O sistema deve permitir que o usuário crie uma conta. | 📋 Planejado |
| RF02  | O sistema deve permitir que o usuário faça login e logout. | 📋 Planejado |
| RF03  | O sistema deve permitir que o usuário visualize e edite seus dados cadastrais. | 📋 Planejado |
| RF04  | O sistema deve permitir visualizar os calçados disponíveis para venda. | 📋 Planejado |
| RF05  | O sistema deve permitir visualizar os detalhes de um calçado, incluindo nome, descrição, preço, tamanho, marca e imagens. | 📋 Planejado |
| RF06  | O sistema deve permitir pesquisar calçados por nome ou descrição. | 📋 Planejado |
| RF07  | O sistema deve permitir filtrar calçados por categoria, tamanho, marca e faixa de preço. | 📋 Planejado |
| RF08  | O sistema deve permitir que o vendedor cadastre novos calçados. | 📋 Planejado |
| RF09  | O sistema deve permitir que o vendedor edite os dados de seus calçados. | 📋 Planejado |
| RF10  | O sistema deve permitir que o vendedor remova ou desative um calçado. | 📋 Planejado |
| RF11  | O sistema deve permitir que o usuário adicione calçados ao carrinho. | 📋 Planejado |
| RF12  | O sistema deve permitir que o usuário altere a quantidade de itens no carrinho. | 📋 Planejado |
| RF13  | O sistema deve permitir que o usuário remova itens do carrinho. | 📋 Planejado |
| RF14  | O sistema deve calcular o valor total da compra. | 📋 Planejado |
| RF15  | O sistema deve permitir que o usuário finalize uma compra. | 📋 Planejado |
| RF16  | O sistema deve registrar os pedidos realizados. | 📋 Planejado |
| RF17  | O sistema deve permitir que o usuário consulte seu histórico de pedidos. | 📋 Planejado |
| RF18  | O sistema deve permitir que o vendedor visualize os pedidos relacionados aos seus produtos. | 📋 Planejado |
| RF19  | O sistema deve permitir atualizar o status de um pedido. | 📋 Planejado |
| RF20  | O sistema deve controlar a quantidade disponível de cada calçado em estoque. | 📋 Planejado |

### Legenda de Status
- ✅ Implementado
- 🔄 Em progresso
- 📋 Planejado

---

## Requisitos Não Funcionais

| ID    | Descrição | Observações |
|-------|-----------|-------------|
| RNF01 | O sistema deve ser acessível através de navegadores web modernos. | Chrome, Firefox, Edge, Safari |
| RNF02 | O sistema deve possuir uma interface simples e intuitiva. | — |
| RNF03 | O sistema deve ser responsivo. | Mobile-first considerado |
| RNF04 | O sistema deve utilizar PostgreSQL para armazenamento dos dados. | Configurado na Sprint 1 |
| RNF05 | O sistema deve ser desenvolvido utilizando Django (python). | Python 3.14 / Django 4.2 LTS |
| RNF06 | As senhas dos usuários devem ser armazenadas de forma segura. | AbstractUser + PBKDF2 |
| RNF07 | O sistema deve restringir o acesso às funcionalidades de acordo com o tipo de usuário. | Campo `user_type` no modelo |
| RNF08 | O sistema deve validar os dados enviados pelos usuários antes de armazená-los no banco de dados. | Forms e serializers do Django |
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
- Sistemas complexos de logística
- Integrações externas não previstas nos requisitos
