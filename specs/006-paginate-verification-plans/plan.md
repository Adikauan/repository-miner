# Implementation Plan: Paginação de Planos de Verificação

**Branch**: `006-paginate-verification-plans` | **Date**: 2026-09-21 | **Spec**: [spec.md](spec.md)

## Summary

Estender a listagem de `MonitoringConfiguration` para aceitar `offset` e `limit`, contar o conjunto filtrado, ordenar globalmente antes do recorte e retornar `items`, `offset`, `limit`, `total` e `total_pages`. O modelo atual não possui `created_at`; portanto, a ordenação usará o identificador estável `id DESC`, documentado como fallback determinístico sem migração. O frontend consumirá somente a página solicitada, exibirá navegação Material UI e reiniciará a página após criação ou quando uma página deixar de existir.

## Technical Context

**Language/Version**: Python 3.13+ no backend; TypeScript/React no frontend

**Primary Dependencies**: FastAPI, SQLAlchemy, Pydantic, pytest; React, Material UI, Vitest e Testing Library

**Storage**: SQLite ou banco relacional configurado por `DATABASE_URL`; tabela `monitoring_configurations` e relações existentes de schedule, credencial e execução

**Testing**: pytest para contratos/integração backend; Vitest + Testing Library para frontend; build Vite

**Target Platform**: Aplicação web responsiva com API HTTP local ou hospedada

**Project Type**: Web application com backend REST e frontend React

**Performance Goals**: Retornar somente a página solicitada e manter o objetivo de carregamento já adotado pelo frontend, sem carregar todos os planos em memória no cliente

**Constraints**: Ordenação no backend antes da paginação; não criar `created_at` apenas para esta feature; preservar os dados atuais dos cards; não expor credenciais; não alterar execução, scheduler ou mineração

**Scale/Scope**: Listagem existente de `MonitoringConfiguration`, com múltiplas páginas de planos; sem novos filtros, endpoints de domínio ou controles de alteração de `page_size`

## Constitution Check

*GATE: PASS — reavaliado após o desenho.*

- **I. Architectural Simplicity**: PASS. A solução estende o endpoint e componentes existentes; não adiciona serviços ou infraestrutura.
- **II. Credential Security**: PASS. A resposta preserva apenas o resumo existente e não inclui token, ciphertext ou referências internas.
- **III. End-to-End Traceability**: PASS. Nenhum resultado de mineração ou dado de proveniência é alterado.
- **IV. Incremental Mining**: PASS. Nenhuma regra de processamento incremental ou checkpoint é tocada.
- **V. Integration Isolation**: PASS. A listagem apenas consulta persistência; nenhuma integração GitLab é modificada.
- **VII. Testability Without External Services**: PASS. Testes usam banco e mocks locais, sem GitLab real.
- **VIII. Failure Isolation**: PASS. Erros de consulta ficam restritos à listagem e são apresentados com retry.
- **X. Execution Observability**: PASS. O resumo da última execução permanece em cada item do plano.

Não há violação constitucional que exija complexity tracking.

## Project Structure

### Documentation (this feature)

```text
specs/006-paginate-verification-plans/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── configuration-pagination.md
└── checklists/
    └── requirements.md
```

### Source Code (repository root)

```text
backend/
├── src/repository_miner/configuration/api/router.py
├── src/repository_miner/persistence/models.py
└── tests/
    ├── contract/test_configuration_list_contract.py
    └── integration/configuration/

frontend/
├── src/configurations/api.ts
├── src/plans/api.ts
├── src/plans/types.ts
├── src/plans/PlanListPage.tsx
├── src/plans/PlanCard.tsx
└── tests/plans/
```

**Structure Decision**: Manter a separação web existente. O backend será alterado apenas na rota/consulta de listagem de configurações e seus testes; o frontend concentrará o estado de paginação em `PlanListPage`, mantendo `PlanCard`, criação e navegação de detalhes reutilizáveis. Não há migração de banco.

## Phase 0: Research

Decisões de contrato, campo temporal, consulta e comportamento de página estão consolidadas em [research.md](research.md).

## Phase 1: Design & Contracts

- Modelo e invariantes: [data-model.md](data-model.md)
- Contrato HTTP: [contracts/configuration-pagination.md](contracts/configuration-pagination.md)
- Validação executável: [quickstart.md](quickstart.md)

## Implementation Notes

1. Validar `offset >= 0` e `1 <= limit <= 200`, alinhado ao endpoint de execuções.
2. Aplicar filtros existentes antes de `ORDER BY`, calcular `total`, e só então aplicar `offset`/`limit`.
3. Ordenar `MonitoringConfiguration.id DESC` porque o modelo atual não possui campo temporal persistido; não adicionar coluna/migração.
4. Retornar `total_pages = ceil(total / limit)` e `0` quando `total == 0`.
5. Atualizar o frontend para usar `total_pages` em `Pagination`, preservar os itens durante loading quando apropriado e recarregar a primeira página após criação.
6. Se uma resposta de página posterior vier vazia com `total > 0`, corrigir para a última página válida e refazer a consulta uma vez.
