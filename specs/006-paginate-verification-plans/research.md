# Research: Paginação de Planos de Verificação

## Decision: Reutilizar `offset` e `limit`

**Rationale**: O endpoint de execuções já usa esses parâmetros e o frontend já possui um cliente que os serializa. Reutilizar o contrato evita um segundo formato de paginação.

**Alternatives considered**: `page`/`page_size` exigiria uma conversão ou contrato paralelo; aceitar ambos aumentaria ambiguidades sem benefício para o escopo atual.

## Decision: Retornar `items`, `offset`, `limit`, `total` e `total_pages`

**Rationale**: Esses metadados permitem que o componente saiba exatamente quantas páginas existem, trate páginas inválidas e não dependa de inferência pelo tamanho da resposta.

**Alternatives considered**: Inferir a próxima página por `items.length == limit` não trata exclusões ou páginas vazias de forma confiável.

## Decision: Usar `MonitoringConfiguration.id DESC`

**Rationale**: A tabela atual não possui `created_at` nem outro timestamp de criação. O requisito proíbe criar automaticamente um campo apenas para esta feature. O identificador persistido fornece ordem determinística sem migração; a limitação de não representar cronologia real fica documentada.

**Alternatives considered**: Adicionar `created_at` exigiria migração e ampliaria o modelo; usar `CredentialReference.created_at` representaria ciclo de vida da credencial, não criação do plano; ordenar por nome não representa recência.

## Decision: Ordenar antes de contar/recortar

**Rationale**: O conjunto filtrado deve ter ordem global determinística antes do `offset`/`limit`, evitando duplicações e omissões entre páginas estáveis.

**Alternatives considered**: Ordenar itens depois do recorte produziria páginas apenas localmente ordenadas.

## Decision: Estado no `PlanListPage`

**Rationale**: O componente já carrega a listagem, abre o modal e atualiza após criação. Centralizar paginação, loading, erro e correção de página inválida evita paginação local em `PlanCard`.

**Alternatives considered**: Paginar no cliente exigiria carregar todos os planos.

## Decision: Não alterar page size

**Rationale**: A tela atual não oferece controle de tamanho. O valor padrão permanece fixo e a funcionalidade fica condicional para telas futuras.

**Alternatives considered**: Adicionar seletor agora ampliaria o escopo visual sem requisito funcional.
