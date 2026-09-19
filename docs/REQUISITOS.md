# Requisitos do Sistema — Marketplace de Calçados

> **Documento de especificação original** — contém lacunas resolvidas e remanescentes.
> Versão: 1.1 | Atualizado na Sprint 2 (decisões de negócio)
>
> Para o status de implementação atualizado a cada Sprint, consulte [`requirements.md`](requirements.md).

## REQUISITOS FUNCIONAIS

| ID | Requisito |
|---|---|
| RF01 | O sistema deve permitir que o usuário crie uma conta com e-mail, senha, nome e tipo (cliente ou vendedor). |
| RF02 | O sistema deve permitir que o usuário faça login usando **e-mail e senha** e realize logout. |
| RF03 | O sistema deve permitir que o usuário visualize e edite seus dados cadastrais. |
| RF04 | O sistema deve permitir visualizar os calçados disponíveis para venda. |
| RF05 | O sistema deve permitir visualizar os detalhes de um calçado, incluindo nome, descrição, preço, tamanho, marca e imagens. |
| RF06 | O sistema deve permitir pesquisar calçados por nome ou descrição. |
| RF07 | O sistema deve permitir filtrar calçados por categoria, tamanho, marca e faixa de preço. |
| RF08 | O sistema deve permitir que o vendedor cadastre novos calçados. |
| RF09 | O sistema deve permitir que o vendedor edite os dados de seus calçados. |
| RF10 | O sistema deve permitir que o vendedor remova ou desative um calçado (soft delete). |
| RF11 | O sistema deve permitir que o usuário adicione calçados ao carrinho. |
| RF12 | O sistema deve permitir que o usuário altere a quantidade de itens no carrinho. |
| RF13 | O sistema deve permitir que o usuário remova itens do carrinho. |
| RF14 | O sistema deve calcular o valor subtotal do carrinho (soma dos itens sem frete). |
| RF15 | O sistema deve permitir que o usuário finalize uma compra através do checkout. |
| RF16 | O sistema deve registrar os pedidos realizados com snapshot de preço. |
| RF17 | O sistema deve permitir que o usuário consulte seu histórico de pedidos. |
| RF18 | O sistema deve permitir que o vendedor visualize os pedidos relacionados aos seus produtos. |
| RF19 | O sistema deve permitir atualizar o status de um pedido. |
| RF20 | O sistema deve controlar a quantidade disponível de cada calçado em estoque. |
| RF21 | O sistema deve autenticar usuários por **e-mail** (não username). O e-mail deve ser único por usuário. |
| RF22 | O usuário deve poder cadastrar, editar, excluir e visualizar múltiplos endereços de entrega. |
| RF23 | O checkout deve permitir que o usuário selecione um dos seus endereços cadastrados para entrega. |
| RF24 | O frete deve ser calculado com base na distância (km) e taxa por km configuradas pelo vendedor no perfil da loja. Fórmula: `frete = distância_km × valor_por_km`. A distância é informada pelo vendedor (sem integração com API de mapas nesta versão). |
| RF25 | O sistema deve registrar um **pagamento simulado** (sem processamento financeiro real). O usuário seleciona o método (cartão, PIX, boleto — todos simulados) e o sistema registra a aprovação fictícia do pagamento para fins acadêmicos. |

---

## REQUISITOS NÃO FUNCIONAIS

| ID | Requisito |
|---|---|
| RNF01 | O sistema deve ser acessível através de navegadores web modernos. |
| RNF02 | O sistema deve possuir uma interface simples e intuitiva. |
| RNF03 | O sistema deve ser responsivo (mobile-first). |
| RNF04 | O sistema deve utilizar PostgreSQL para armazenamento dos dados. |
| RNF05 | O sistema deve ser desenvolvido utilizando Django (Python 3.11+). |
| RNF06 | As senhas dos usuários devem ser armazenadas de forma segura (PBKDF2). |
| RNF07 | O sistema deve restringir o acesso às funcionalidades de acordo com o tipo de usuário. |
| RNF08 | O sistema deve validar os dados enviados pelos usuários antes de armazená-los no banco de dados. |
| RNF09 | O sistema deve possuir código organizado e modular, facilitando sua manutenção. |
| RNF10 | O sistema deve utilizar Git e GitHub para controle de versão. |
| RNF11 | O sistema deve apresentar tempo de resposta adequado para operações comuns. |
| RNF12 | O sistema deve manter a integridade e consistência dos dados armazenados. |
| RNF13 | O sistema deve tratar erros de forma adequada, evitando a exposição de informações internas. |

---

## Lacunas Resolvidas

| Lacuna | Decisão implementada |
|--------|----------------------|
| Login por e-mail vs. username | **Login por e-mail** — `USERNAME_FIELD = 'email'`, `unique=True`, `EmailBackend` customizado. |
| Endereço de entrega | **Múltiplos endereços** — modelo `Address` com FK para `CustomUser`. |
| Política de frete | **Frete configurado pelo vendedor** — `shipping_rate_per_km` e `shipping_distance_km` em `SellerProfile`. Cálculo simulado sem API de mapas. |
| Pagamento | **Pagamento simulado** — campos `payment_method` e `payment_status` em `Order`. Sem processamento financeiro real. |

---

## Lacunas Remanescentes

| ID | Lacuna | Observação |
|----|--------|------------|
| L01 | Valores possíveis de `Stock.size` | `CharField` sem enum definido. Valores livres (ex: 38, 39, M, G). |
| L02 | Número de itens por página nas listagens | Paginação não definida. |
| L03 | Cálculo de distância real via API | A distância é informada pelo vendedor. Integração com API de mapas está fora do escopo desta versão. |
