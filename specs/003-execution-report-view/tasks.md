# Tasks: Visualização de Relatório de Execução

**Input**: Design documents from `/specs/003-execution-report-view/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/report-view.md, quickstart.md

**Tests**: Incluídos porque a specification exige cobertura frontend para carregamento, estados, paginação, segurança e navegação.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Preparar os pontos de extensão existentes sem alterar o backend.

- [X] T001 Confirmar os contratos e caminhos existentes de relatório em specs/003-execution-report-view/contracts/report-view.md
- [X] T002 [P] Catalogar os tipos canônicos de execução e contadores em frontend/src/reporting/api.ts
- [X] T003 [P] Definir fixtures sintéticas sem tokens ou credenciais em frontend/src/reporting/__tests__/fixtures.ts
- [X] T004 [P] Registrar a matriz de estados de loading, erro, vazio e sucesso em frontend/src/reporting/__tests__/report-state-cases.ts

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Criar os tipos e utilitários compartilhados que bloqueiam as histórias.

- [X] T005 [P] Criar tipos de relatório, coleções paginadas e erros seguros conforme data-model.md em frontend/src/reporting/api.ts
- [X] T006 [P] Criar helpers de estado e mensagem segura para consultas de relatório em frontend/src/reporting/reportViewState.ts
- [X] T007 [P] Criar camada de consulta independente para resumo, repositories, commits, UnauthorizedCommitAlerts e falhas em frontend/src/reporting/api.ts
- [X] T008 [P] Adicionar tratamento de 404, relatório indisponível e falhas parciais sem expor segredos em frontend/src/shared/api/client.ts
- [X] T009 [P] Criar harness de mocks do cliente HTTP para testes frontend em frontend/src/reporting/__tests__/apiMocks.ts

**Checkpoint**: Tipos, consultas, paginação, erros seguros e fixtures estão disponíveis para as histórias.

---

## Phase 3: User Story 1 - Consultar relatório de uma execução (Priority: P1) 🎯 MVP

**Goal**: Permitir abrir uma execução pelo execution_id e visualizar seu relatório persistido com estados de loading, sucesso, erro e indisponibilidade.

**Independent Test**: Com uma resposta sintética persistida, abrir o relatório pelo execution_id e validar o resumo, os sete contadores e os estados de consulta.

### Tests for User Story 1

- [X] T010 [P] [US1] Testar carregamento, sucesso, 404 e relatório indisponível em frontend/src/reporting/ReportDetailPage.test.tsx
- [X] T011 [P] [US1] Testar renderização dos sete contadores canônicos sem recálculo em frontend/src/reporting/ReportSummary.test.tsx
- [X] T012 [P] [US1] Testar estados pending, running, completed, partially_completed e failed e, para cada estado terminal, garantir em frontend/src/reporting/ReportDetailPage.test.tsx que snapshot/relatório persistido prevalece sobre eventos WebSocket ou estado transitório, que estes não sobrescrevem o relatório final e que os sete contadores canônicos exibidos correspondem ao estado persistido
- [X] T013 [P] [US1] Testar mensagens de erro sem tokens, credenciais ou secrets em frontend/src/reporting/ReportDetailPage.test.tsx

### Implementation for User Story 1

- [X] T014 [US1] Implementar carregamento independente do resumo e estados de tela em frontend/src/reporting/ReportDetailPage.tsx
- [X] T015 [US1] Implementar resumo com execution_id, configuração, origem, horários, estado e contadores em frontend/src/reporting/ReportSummary.tsx
- [X] T016 [US1] Implementar estados de loading, vazio, erro, inexistente e indisponível em frontend/src/reporting/ReportDetailPage.tsx
- [X] T017 [US1] Integrar a ação de abrir relatório às rotas e ao estado de navegação em frontend/src/app/routes.tsx
- [X] T018 [US1] Preservar o retorno à listagem ou à tela anterior no fluxo de relatório em frontend/src/app/App.tsx

**Checkpoint**: US1 permite abrir e ler o resumo persistido de forma independente.

---

## Phase 4: User Story 2 - Interpretar o resultado consolidado (Priority: P1)

**Goal**: Apresentar repositories, commits verificados, alertas de autoria não permitida e falhas com paginação e rastreabilidade.

**Independent Test**: Carregar coleções sintéticas paginadas contendo itens concluídos, falhos, alertas e author_email nulo.

### Tests for User Story 2

- [X] T019 [P] [US2] Testar listagem de repositories concluídos e falhos em frontend/src/reporting/RepositoryReportList.test.tsx
- [X] T020 [P] [US2] Testar commits verificados, commit_hash e author_email nulo em frontend/src/reporting/CommitVerificationList.test.tsx
- [X] T021 [P] [US2] Testar UnauthorizedCommitAlerts vinculados à execução original em frontend/src/reporting/UnauthorizedCommitList.test.tsx
- [X] T022 [P] [US2] Testar falhas com código, mensagem segura e data em frontend/src/reporting/RepositoryFailureList.test.tsx
- [X] T023 [P] [US2] Testar paginação sem recarregar o relatório inteiro em frontend/src/reporting/PaginatedReportCollection.test.tsx
- [X] T024 [P] [US2] Testar listas vazias como resultado válido em frontend/src/reporting/ReportCollections.test.tsx

### Implementation for User Story 2

- [X] T025 [P] [US2] Criar componente paginado de repositories com distinção visual de status em frontend/src/reporting/RepositoryReportList.tsx
- [X] T026 [P] [US2] Criar componente paginado de commits verificados com author_email explicitamente anulável em frontend/src/reporting/CommitVerificationList.tsx
- [X] T027 [P] [US2] Criar componente de UnauthorizedCommitAlerts preservando detection_execution_id em frontend/src/reporting/UnauthorizedCommitList.tsx
- [X] T028 [P] [US2] Criar componente paginado de falhas com mensagens seguras em frontend/src/reporting/RepositoryFailureList.tsx
- [X] T029 [US2] Integrar as coleções paginadas na tela de relatório sem recalcular contadores em frontend/src/reporting/ReportDetailPage.tsx
- [X] T030 [US2] Adicionar filtros locais somente para campos já presentes nas coleções em frontend/src/reporting/reportFilters.ts
- [X] T031 [US2] Ajustar estilos e feedback de lista vazia, falha e item selecionado em frontend/src/reporting/ReportDetailPage.tsx

**Checkpoint**: US2 permite consultar todo o resultado consolidado sem alterar dados de mineração.

---

## Phase 5: User Story 3 - Acompanhar execução ativa e navegar pelo histórico (Priority: P2)

**Goal**: Oferecer navegação a partir do histórico e encaminhamento para o acompanhamento existente quando a execução ainda estiver ativa.

**Independent Test**: Abrir uma execução running pelo histórico, navegar ao relatório, acessar o acompanhamento existente e retornar ao histórico.

### Tests for User Story 3

- [X] T032 [P] [US3] Testar abertura do relatório a partir do histórico em frontend/src/executions/ExecutionHistoryPage.test.tsx
- [X] T033 [P] [US3] Testar acesso ao relatório e ao acompanhamento para execução running em frontend/src/executions/ExecutionDetailPage.test.tsx
- [X] T034 [P] [US3] Testar retorno à listagem preservando execution_id em frontend/src/app/App.test.tsx
- [X] T035 [P] [US3] Testar que a tela não cria um segundo fluxo WebSocket em frontend/src/reporting/ReportDetailPage.test.tsx

### Implementation for User Story 3

- [X] T036 [US3] Adicionar ação de relatório em cada execução do histórico em frontend/src/executions/ExecutionHistoryPage.tsx
- [X] T037 [US3] Adicionar links entre detalhes, relatório e acompanhamento conforme status em frontend/src/executions/ExecutionDetailPage.tsx
- [X] T038 [US3] Reutilizar o fluxo de acompanhamento existente para execuções pending/running em frontend/src/reporting/ReportDetailPage.tsx
- [X] T039 [US3] Preservar navegação e recuperação por execution_id nas rotas em frontend/src/app/routes.tsx

**Checkpoint**: US3 completa o fluxo de navegação sem duplicar WebSocket ou alterar o estado oficial.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Validar qualidade, segurança e compatibilidade da entrega.

- [X] T040 [P] Adicionar testes de contrato dos tipos e contadores canônicos em frontend/src/reporting/api.contract.test.ts
- [X] T041 [P] Adicionar teste de segurança para ausência de segredos em respostas, erros e snapshots em frontend/src/reporting/security.test.ts
- [X] T042 [P] Adicionar acessibilidade básica para tabelas, estados vazios e mensagens de erro em frontend/src/reporting/ReportDetailPage.tsx
- [X] T043 [P] Validar que nenhum estado novo ou contador alternativo foi introduzido em frontend/src/reporting/api.test.ts
- [X] T044 Executar npm test -- --run e corrigir falhas da feature usando frontend/package.json
- [X] T045 Executar npm run build e validar o guia specs/003-execution-report-view/quickstart.md

---

## Dependencies & Execution Order

### Phase Dependencies

- Setup (Phase 1) não depende de outras fases.
- Foundational (Phase 2) depende de Setup e bloqueia todas as histórias.
- US1 depende da Phase 2 e é o MVP mínimo.
- US2 depende da Phase 2 e pode iniciar em paralelo com US1 após os tipos compartilhados.
- US3 depende da Phase 2 e integra rotas existentes; recomenda-se iniciar após US1.
- Polish depende das histórias escolhidas para entrega.

### User Story Dependencies

- **US1 (P1)**: depende da Phase 2; nenhuma outra história é necessária.
- **US2 (P1)**: depende da Phase 2; reutiliza o resumo de US1 na tela final.
- **US3 (P2)**: depende da Phase 2 e integra a tela de US1 ao histórico e acompanhamento.

### Within Each User Story

- Testes devem ser criados antes da implementação correspondente e inicialmente falhar.
- Tipos e consultas devem existir antes dos componentes.
- Componentes devem existir antes da integração de rotas.
- Cada checkpoint deve ser validado antes de avançar.

## Parallel Opportunities

- T002-T004 podem ser executadas em paralelo.
- T005-T009 podem ser executadas em paralelo após T001.
- Os testes T010-T013 podem ser executados em paralelo.
- Os componentes T025-T028 podem ser executados em paralelo.
- Os testes T019-T024 podem ser executados em paralelo.
- Os testes T032-T035 podem ser executados em paralelo.
- T040-T043 podem ser executadas em paralelo após as histórias.

## Parallel Example: User Story 1

    Task: T010 teste de estados da tela
    Task: T011 teste dos contadores
    Task: T012 teste dos estados canônicos
    Task: T013 teste de mensagens seguras

Após os testes, T014-T016 podem ser implementadas com dependências explícitas; T017-T018 integram a navegação.

## Implementation Strategy

### MVP First

1. Concluir Setup e Foundational.
2. Implementar US1.
3. Executar os testes e o build frontend.
4. Demonstrar abertura do relatório e leitura dos contadores.

### Incremental Delivery

1. Adicionar US2 para detalhes, paginação e rastreabilidade.
2. Adicionar US3 para histórico e acompanhamento de execuções ativas.
3. Executar Polish e validação do quickstart.

## Notes

- Todas as tarefas seguem o formato checklist com ID sequencial e caminho de arquivo.
- Nenhuma tarefa altera mineração, scheduler, baseline, checkpoints, credenciais ou contratos WebSocket.
- Fixtures e snapshots devem usar exclusivamente dados sintéticos e não sensíveis.

