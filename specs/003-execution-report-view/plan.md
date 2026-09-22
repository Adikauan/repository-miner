# Implementation Plan: Visualização de Relatório de Execução

**Branch**: 003-execution-report-view | **Date**: 2026-09-20 | **Spec**: [spec.md](./spec.md)

## Summary

Adicionar ao frontend uma visão de relatório acessível pelo execution_id, reutilizando as consultas e contratos persistidos já existentes. A implementação organizará o carregamento do resumo, repositories, commits, alertas e falhas em estados de interface independentes, preservará os sete contadores canônicos e encaminhará execuções ativas para o acompanhamento existente. Não haverá alteração no runner, scheduler, checkpoints, contratos de WebSocket ou regras de mineração.

## Technical Context

**Language/Version**: TypeScript e Python já utilizados pelo projeto; esta feature altera somente o frontend, com contratos consumidos do backend existente.

**Primary Dependencies**: React, Material UI, cliente HTTP existente e mecanismo de rotas existente no frontend.

**Storage**: Dados persistidos no backend existente; o frontend não adiciona armazenamento durável.

**Testing**: Vitest e Testing Library no frontend; testes de contrato e integração existentes permanecem a referência para os payloads do backend.

**Target Platform**: Navegador suportado pela aplicação web atual.

**Project Type**: Aplicação web monolítica com frontend e backend existentes.

**Performance Goals**: Uma consulta por seção do relatório, sem polling agressivo; navegação de páginas deve atualizar apenas a coleção selecionada.

**Constraints**: Não recalcular contadores, não reconstruir relatório a partir de eventos quando houver dados persistidos, não expor segredos e não introduzir novos endpoints ou estados de mineração sem necessidade comprovada.

**Scale/Scope**: Execuções existentes, listas potencialmente paginadas de repositories, commits, alertas e falhas; sem dashboards gráficos ou exportação.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **I. Simplicidade arquitetural**: PASS. A solução reutiliza a página, cliente, rotas e consultas existentes; não adiciona serviços, filas ou armazenamento.
- **II. Segurança de credenciais**: PASS. O relatório exibe apenas mensagens seguras; fixtures usam dados sintéticos e nenhum token é necessário.
- **III. Rastreabilidade**: PASS. A interface preserva execution_id, repository, branch, commit_hash, autor, e-mail e data quando fornecidos pelo contrato.
- **IV. Mineração incremental**: PASS. Nenhuma regra de mineração ou checkpoint é alterada.
- **V. Isolamento de integrações**: PASS. O frontend usa o cliente de consulta já existente; não acessa GitLab diretamente.
- **VII. Testabilidade**: PASS. Os testes utilizam respostas sintéticas e mocks do cliente HTTP.
- **VIII. Falhas isoladas**: PASS. Falha de uma lista não deve ocultar as demais se estas puderem ser carregadas; falhas do relatório são apresentadas com segurança.
- **X. Observabilidade**: PASS. O identificador da execução é mantido na navegação e nas consultas; eventos de acompanhamento continuam sob o fluxo existente.

No design desta feature, os princípios de IA e privacidade de código não são diretamente acionados porque o MVP não analisa código nem envia dados a provedores de IA.

## Project Structure

### Documentation (this feature)

    specs/003-execution-report-view/
    ├── plan.md
    ├── research.md
    ├── data-model.md
    ├── quickstart.md
    ├── contracts/
    │   └── report-view.md
    └── checklists/
        └── requirements.md

### Source Code (repository root)

    frontend/src/
    ├── app/
    │   ├── App.tsx
    │   └── routes.tsx
    ├── executions/
    │   ├── ExecutionHistoryPage.tsx
    │   ├── ExecutionDetailPage.tsx
    │   └── api.ts
    ├── reporting/
    │   ├── api.ts
    │   ├── ReportDetailPage.tsx
    │   └── ReportSummary.tsx
    └── shared/api/
        └── client.ts

    frontend/src/**/__tests__/
    └── report-view tests and fixtures

**Structure Decision**: Manter a organização atual do frontend. A tela de relatório permanece no módulo reporting; histórico, detalhes e rotas apenas passam a oferecer navegação para ela. O cliente de consultas será estendido somente para representar paginação e estados de erro necessários.

## Phase 0: Research

As decisões de pesquisa estão registradas em [research.md](./research.md). Não há decisões tecnológicas abertas: a feature deve reutilizar o frontend e os contratos atuais.

## Phase 1: Design & Contracts

- O modelo de dados de apresentação está em [data-model.md](./data-model.md).
- O contrato de consumo dos endpoints existentes está em [contracts/report-view.md](./contracts/report-view.md).
- O guia de validação executável está em [quickstart.md](./quickstart.md).
- Nenhuma migration ou alteração de schema é necessária.
- Nenhuma alteração ao contrato de WebSocket é necessária; para running, a UI reutiliza o acompanhamento já existente.

## Re-evaluation of Constitution Check

Todos os gates permanecem **PASS** após o design. O plano não introduz complexidade arquitetural, coleta adicional de dados, processamento de código ou exposição de credenciais.

## Complexity Tracking

Nenhuma violação constitucional ou complexidade adicional requer justificativa.
