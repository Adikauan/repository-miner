# Tasks: Paginação de Planos de Verificação

**Input**: Design documents from `/specs/006-paginate-verification-plans/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/configuration-pagination.md`, `quickstart.md`

## Phase 1: Setup (Shared Infrastructure)

- [X] T001 [P] Atualizar fixtures sintéticas de listagem em `backend/tests/fixtures/pagination.py` para criar múltiplas `MonitoringConfiguration` sem segredos reais
- [X] T002 [P] Atualizar fixtures e tipos de planos paginados em `frontend/tests/plans/fixtures.ts` e `frontend/src/plans/types.ts`, preservando todos os campos atuais do card

## Phase 2: Foundational (Blocking Prerequisites)

- [X] T003 Documentar e alinhar o envelope `items`, `offset`, `limit`, `total` e `total_pages` em `specs/006-paginate-verification-plans/contracts/configuration-pagination.md` e nos tipos TypeScript correspondentes
- [X] T004 [P] Adicionar validação de limites `offset >= 0` e `1 <= limit <= 200` aos testes de contrato em `backend/tests/contract/test_configuration_list_contract.py`

## Phase 3: User Story 1 - Consultar planos recentes (Priority: P1) 🎯 MVP

**Goal**: Exibir a primeira página de planos e permitir navegar por páginas ordenadas globalmente.

**Independent Test**: Criar mais planos que o limite, consultar duas páginas e confirmar metadados, ordem determinística, ausência de duplicação/omissão e cards completos.

- [X] T005 [P] [US1] Expandir o contrato em `backend/tests/contract/test_configuration_list_contract.py` para validar primeira página, páginas seguintes, `total`, `total_pages`, limite e resposta vazia
- [X] T006 [P] [US1] Adicionar teste de integração em `backend/tests/integration/configuration/test_configuration_pagination.py` para ordenar antes do recorte, evitar duplicação/omissão e manter estabilidade
- [X] T007 [P] [US1] Adicionar teste frontend em `frontend/tests/plans/plan-list-pagination.test.tsx` para abertura em offset zero, controles de página e nova consulta ao avançar/voltar
- [X] T008 [US1] Alterar `backend/src/repository_miner/configuration/api/router.py` para aceitar `offset`/`limit`, ordenar `MonitoringConfiguration.id DESC` antes do recorte, calcular `total`/`total_pages` e preservar campos seguros; `id DESC` é somente fallback determinístico, não cronologia real
- [X] T009 [US1] Atualizar `frontend/src/configurations/api.ts` e `frontend/src/plans/api.ts` para enviar `offset`/`limit` e consumir o envelope paginado
- [X] T010 [US1] Atualizar `frontend/src/plans/PlanListPage.tsx` para manter página atual, carregar somente a página solicitada e renderizar `Pagination` Material UI quando necessário
- [X] T011 [US1] Atualizar `frontend/src/plans/types.ts` para representar `PaginatedPlanPage` com `items`, `offset`, `limit`, `total` e `total_pages`

## Phase 4: User Story 2 - Navegar e lidar com estados (Priority: P1)

**Goal**: Tratar loading, erro, lista vazia e páginas inválidas.

- [X] T012 [P] [US2] Adicionar testes de loading, erro/retry e estado vazio em `frontend/tests/plans/plan-list-pagination.test.tsx`, sem paginação desnecessária
- [X] T013 [P] [US2] Adicionar teste de página fora do intervalo e total reduzido em `frontend/tests/plans/plan-list-pagination.test.tsx`, confirmando retorno a página válida
- [X] T014 [US2] Adicionar teste backend de parâmetros inválidos e página sem itens em `backend/tests/contract/test_configuration_list_contract.py`, sem expor detalhes internos
- [X] T015 [US2] Ajustar `frontend/src/plans/PlanListPage.tsx` para loading durante troca, retry seguro, estado vazio e correção de página inválida usando `total_pages`
- [X] T016 [US2] Ajustar `backend/src/repository_miner/configuration/api/router.py` para validação consistente de parâmetros e metadados reais em offsets além do fim

## Phase 5: User Story 3 - Criar plano e retornar à primeira página (Priority: P2)

**Goal**: Atualizar a listagem pela fonte oficial após criação.

- [X] T017 [P] [US3] Adicionar teste frontend em `frontend/tests/plans/plan-list-pagination.test.tsx` para criação em página posterior, reset para primeira página e ausência de inserção manual
- [X] T018 [P] [US3] Adicionar teste backend em `backend/tests/integration/configuration/test_configuration_pagination.py` para nova configuração aparecer em nova consulta e atualizar total
- [X] T019 [US3] Atualizar callback `onCreated` em `frontend/src/plans/PlanListPage.tsx` para fechar modal, definir página 1 e recarregar a consulta oficial
- [X] T020 [US3] Confirmar em `frontend/src/plans/CreatePlanModal.tsx` e `frontend/src/plans/PlanCard.tsx` que criação, campos, ações e navegação permanecem inalterados

## Phase 6: Polish & Cross-Cutting Concerns

- [X] T021 [P] Atualizar testes existentes em `frontend/tests/plans/plan-list.test.tsx` e `frontend/tests/plans/legacy-routes.test.tsx` para o envelope paginado e preservar rotas/ações
- [X] T022 [P] Atualizar `specs/004-plan-navigation/contracts/frontend-api.md` com o envelope paginado, sem alterar contratos de execuções
- [X] T023 Executar `python -m pytest backend/tests/contract/test_configuration_list_contract.py backend/tests/integration/configuration -q` e corrigir falhas relacionadas à feature
- [X] T024 Executar `npm test -- --run` dentro de `frontend` e corrigir falhas relacionadas à feature
- [X] T025 Executar `npm run build` dentro de `frontend` e validar `specs/006-paginate-verification-plans/quickstart.md`
- [X] T026 Revisar router, `PlanListPage` e contratos para ausência de segredos, paginação local, novos campos temporais e alterações fora do escopo

## Dependencies & Execution Order

- Setup (Phase 1) precede Foundation (Phase 2).
- US1 depende da Foundation e entrega o MVP.
- US2 depende da estrutura de US1.
- US3 depende da estrutura de US1 e pode avançar em paralelo com US2 após o contrato base.
- Polish depende das histórias implementadas.

## Parallel Opportunities

- T001/T002; T003/T004; T005–T007; T012–T014; T017/T018; T021/T022 podem ser executadas em paralelo quando suas dependências estiverem concluídas.

## Implementation Strategy

1. Entregar US1 como MVP.
2. Adicionar estados robustos em US2.
3. Garantir reset após criação em US3.
4. Executar regressão e build no Polish.

## Notes

- Todos os testes usam dados sintéticos.
- Não criar `created_at`, seletor de `page_size`, endpoint novo de execução ou alteração de regras de mineração.
