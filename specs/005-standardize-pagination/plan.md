# Implementation Plan: Padronização da Paginação Cronológica

**Branch**: `[005-standardize-pagination]` | **Date**: 2026-09-21 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/005-standardize-pagination/spec.md`

## Summary

Alterar somente listagens que já possuem paginação ou contrato de paginação. O backend aplicará filtros, ordenação cronológica descendente e desempate determinístico antes de `offset`/`limit`; o frontend exibirá a ordem recebida sem reordenar páginas.

## Technical Context

**Language/Version**: Python >=3.13; TypeScript/React 19

**Primary Dependencies**: FastAPI, SQLAlchemy 2, pytest, Vite, Vitest, Material UI

**Storage**: SQLite ou banco configurado via SQLAlchemy; schema existente reutilizado

**Testing**: pytest para contratos/integração e Vitest + Testing Library para frontend

**Target Platform**: Serviço web Repository Miner e frontend em navegador

**Project Type**: Aplicação web com backend Python e frontend React

**Performance Goals**: Manter limites atuais de paginação (máximo 200 itens por solicitação) e ordenar no banco antes do recorte, sem carregar o histórico inteiro no frontend.

**Constraints**: Não adicionar campos temporais, endpoints, controles de page size ou regras de domínio. Preservar envelopes, filtros, relatórios, contadores, ownership, checkpoints, scheduling e semântica de execução.

**Scale/Scope**: Endpoints paginados existentes de execuções, repositories, commits, falhas e UnauthorizedCommitAlerts. `GET /configurations` e qualquer endpoint independente de CommitVerification ficam fora do escopo.

## Constitution Check

| Gate | Status | Evidence |
|---|---|---|
| Architectural simplicity | PASS | Reutiliza consultas e campos existentes; não adiciona infraestrutura. |
| Credential security | PASS | Nenhum dado de credencial é incluído ou alterado. |
| End-to-end traceability | PASS | IDs e relações de execução, repository, commit e alerta permanecem intactos. |
| Incremental mining | PASS | Nenhum estado de mineração é modificado. |
| Integration isolation | PASS | Nenhuma integração externa é alterada. |
| Testability without external services | PASS | Testes usam registros sintéticos e mocks controlados. |
| Failure isolation and observability | PASS | Ciclo de vida e falhas de execução permanecem inalterados. |

No constitution violation requires complexity tracking.

## Project Structure

### Documentation (this feature)

```text
specs/005-standardize-pagination/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
└── tasks.md
```

### Source Code (repository root)

```text
backend/
├── src/repository_miner/
│   ├── executions/application/queries.py
│   ├── executions/api/query_router.py
│   ├── reporting/api/router.py
│   ├── alerts/application/queries.py
│   └── persistence/models.py
└── tests/
    ├── contract/
    ├── integration/
    └── unit/

frontend/
├── src/executions/api.ts
├── src/plans/PlanExecutionsTab.tsx
├── src/reporting/api.ts
└── tests/
    ├── plans/
    └── reporting/
```

**Structure Decision**: Manter o monorepo web. A ordenação pertence às consultas do backend; o frontend apenas preserva a sequência recebida e refaz consultas ao trocar página ou filtro. Atualmente nenhuma tela oferece controle interativo de page size: `PlanExecutionsTab` usa 20 itens fixos e consumidores de relatório usam 50 itens fixos. Portanto, a regra de alteração de page size é condicional e não gera implementação nesta feature.

## Affected Existing Paginated Endpoints

| Endpoint | Current consumer | Ordering decision |
|---|---|---|
| `GET /api/v1/executions?configuration_id=&status=&offset=&limit=` | Histórico geral e aba Execuções do plano | `started_at DESC NULLS LAST`; NULLs formam o grupo final e usam `id DESC`; ID também desempata datas iguais. |
| `GET /api/v1/executions/{execution_id}/repositories?offset=&limit=` | Relatório de repositories | Preservar ordem de domínio existente, pois não é cronológica. |
| `GET /api/v1/executions/{execution_id}/commits?offset=&limit=` | Relatório de commits | Preservar ordem de hash/domínio; não criar listagem independente de CommitVerification. |
| `GET /api/v1/executions/{execution_id}/failures?offset=&limit=` | Lista de falhas | `occurred_at DESC`, depois `id DESC`. |
| `GET /api/v1/executions/{execution_id}/unauthorized-commits?offset=&limit=` | UnauthorizedCommitAlerts | `detected_at DESC`, depois `id DESC`. |
| `GET /api/v1/executions/{execution_id}/failures-detail?offset=&limit=` | Consumidor legado de detalhes | Mesma ordenação de falhas. |

`GET /api/v1/configurations` não é paginado e permanece inalterado. Não existe endpoint paginado independente de CommitVerification; nenhum será criado.

The ordering change is applied to execution history, UnauthorizedCommitAlerts, and failure histories. Repository and execution-commit endpoints are listed to make the current pagination surface explicit, but retain their established non-chronological order.

## MiningExecution NULL ordering

`started_at` é o campo principal. Registros com `started_at` preenchido vêm em ordem descendente e `NULLS LAST`. Registros com `started_at IS NULL` formam o grupo final e são ordenados por `MiningExecution.id DESC`. Nenhum `created_at` será adicionado.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|---|---|---|
| None | N/A | A alteração cabe nas consultas e consumidores existentes. |
