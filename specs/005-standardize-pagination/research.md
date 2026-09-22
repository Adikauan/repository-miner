# Research: Padronização da Paginação Cronológica

## Decision: Ordenação global no backend

**Decision**: Aplicar filtros, ordenar pelo campo temporal canônico em ordem decrescente, aplicar identificador estável como desempate e somente depois aplicar `offset`/`limit`.

**Rationale**: Evita que registros recentes sejam empurrados para páginas posteriores ou que empates mudem de página.

**Alternatives considered**: Ordenar cada página no frontend e carregar todo o histórico foram rejeitados por não garantirem ordem global nem paginação eficiente.

## Decision: MiningExecution e NULLs

**Decision**: Usar `started_at DESC NULLS LAST` quando preenchido. Execuções `pending` com `started_at IS NULL` permanecem no grupo NULL final e são ordenadas deterministicamente por `MiningExecution.id DESC`; nenhum `created_at` será criado.

**Rationale**: O modelo atual não possui outro campo temporal persistido aplicável para criação. Ordenação explícita de NULLs e ID mantém consultas estáveis sem alterar o schema.

**Alternatives considered**: Adicionar `created_at` ou usar horário da consulta foi rejeitado por ampliar o modelo e produzir instabilidade.

## Decision: Recursos e endpoints abrangidos

**Decision**: Alterar somente contratos paginados existentes: execução geral, repositories/commits/falhas de execução e UnauthorizedCommitAlerts. A lista de Planos de Verificação não é paginada e permanece inalterada. Não existe endpoint paginado independente de CommitVerification; nenhum será criado.

**Rationale**: O escopo revisado proíbe nova paginação ou endpoint apenas para esta feature.

**Alternatives considered**: Paginar a lista de planos ou criar listagem de CommitVerification foi rejeitado por ampliar o escopo funcional.

## Decision: Compatibilidade do frontend

**Decision**: Não inverter nem ordenar itens no frontend. Componentes apenas encaminham parâmetros e preservam a sequência recebida.

**Rationale**: O backend é a fonte oficial da ordem.

## Decision: Page size

**Decision**: Nenhuma tela atual oferece controle interativo de tamanho. `PlanExecutionsTab` usa 20 itens fixos e relatórios usam 50 itens fixos. A regra permanece condicional para telas futuras ou já existentes que venham a oferecer esse controle, sem criar um novo controle nesta feature.

**Rationale**: Evita ampliar o escopo com uma nova interação.
