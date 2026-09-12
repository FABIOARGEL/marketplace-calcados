# Requisitos do Sistema — Marketplace de Calçados

## REQUISITOS FUNCIONAIS

| ID | Requisito |
|---|---|
| RF01 | O sistema deve permitir que o usuário crie uma conta. |
| RF02 | O sistema deve permitir que o usuário faça login e logout |
| RF03 | O sistema deve permitir que o usuário visualize e edite seus dados cadastrais |
| RF04 | O sistema deve permitir visualizar os calçados disponíveis para venda |
| RF05 | O sistema deve permitir visualizar os detalhes de um calçado, incluindo nome, descrição, preço, tamanho, marca e imagens. |
| RF06 | O sistema deve permitir pesquisar calçados por nome ou descrição |
| RF07 | O sistema deve permitir filtrar calçados por categoria, tamanho, marca e faixa de preço |
| RF08 | O sistema deve permitir que o vendedor cadastre novos calçados. |
| RF09 | O sistema deve permitir que o vendedor edite os dados de seus calçados |
| RF10 | O sistema deve permitir que o vendedor remova ou desative um calçado |
| RF11 | O sistema deve permitir que o usuário adicione calçados ao carrinho |
| RF12 | O sistema deve permitir que o usuário altere a quantidade de itens no carrinho. |
| RF13 | O sistema deve permitir que o usuário remova itens do carrinho. |
| RF14 | O sistema deve calcular o valor total da compra |
| RF15 | O sistema deve permitir que o usuário finalize uma compra |
| RF16 | O sistema deve registrar os pedidos realizados |
| RF17 | O sistema deve permitir que o usuário consulte seu histórico de pedidos. |
| RF18 | O sistema deve permitir que o vendedor visualize os pedidos relacionados aos seus produtos. |
| RF19 | O sistema deve permitir atualizar o status de um pedido |
| RF20 | O sistema deve controlar a quantidade disponível de cada calçado em estoque. |

---

## REQUISITOS NÃO FUNCIONAIS

| ID | Requisito |
|---|---|
| RNF01 | O sistema deve ser acessível através de navegadores web modernos. |
| RNF02 | O sistema deve possuir uma interface simples e intuitiva. |
| RNF03 | O sistema deve ser responsivo |
| RNF04 | O sistema deve utilizar PostgreSQL para armazenamento dos dados |
| RNF05 | O sistema deve ser desenvolvido utilizando Django (python) |
| RNF06 | As senhas dos usuários devem ser armazenadas de forma segura |
| RNF07 | O sistema deve restringir o acesso às funcionalidades de acordo com o tipo de usuário |
| RNF08 | O sistema deve validar os dados enviados pelos usuários antes de armazená-los no banco de dados |
| RNF09 | O sistema deve possuir código organizado e modular, facilitando sua manutenção |
| RNF10 | O sistema deve utilizar Git e GitHub para controle de versão |
| RNF11 | O sistema deve apresentar tempo de resposta adequado para operações comuns, como consulta de produtos e acesso ao carrinho |
| RNF12 | O sistema deve manter a integridade e consistência dos dados armazenados |
| RNF13 | O sistema deve tratar erros de forma adequada, evitando a exposição de informações internas da aplicação |
