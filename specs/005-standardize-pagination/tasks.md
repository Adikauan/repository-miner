---

description: "Task list for chronological pagination standardization"
---

# Tasks: Padronização da Paginação Cronológica

**Input**: Design documents from `/specs/005-standardize-pagination/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/pagination-order.md`, `quickstart.md`

**Organization**: Tasks are grouped by user story so each story can be implemented and tested independently.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm the existing paginated surfaces and test baselines before changing behavior.

- [X] T001 Review the chronological endpoint inventory and existing pagination envelopes in `backend/src/repository_miner/executions/api/query_router.py`, `backend/src/repository_miner/reporting/api/router.py`, `backend/src/repository_miner/alerts/application/queries.py`, and `frontend/src/reporting/api.ts`.
- [X] T002 Record the current execution/report pagination behavior and synthetic fixture conventions in `backend/tests/contract/test_execution_list_contract.py`, `backend/tests/contract/test_reporting_api.py`, and `frontend/tests/plans/plan-executions-tab.test.tsx`.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish the shared ordering rules before story-specific changes.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [X] T003 Document the canonical temporal field, null handling, and stable-ID tie-breaker for each paginated chronological resource in `specs/005-standardize-pagination/contracts/pagination-order.md` and `specs/005-standardize-pagination/data-model.md`.
- [X] T004 [P] Add shared synthetic record builders with distinct and equal timestamps for pagination tests in `backend/tests/fixtures/pagination.py`.
- [X] T005 [P] Add frontend API-order fixtures covering newest-first, page boundaries, and a newly inserted record in `frontend/tests/plans/pagination-fixtures.ts`.

**Checkpoint**: Ordering rules and deterministic synthetic fixtures are defined; story implementation can proceed.

---

## Phase 3: User Story 1 - Consultar registros mais recentes primeiro (Priority: P1) 🎯 MVP

**Goal**: Ensure execution history returns the newest records on page one and progressively older records on later pages.

**Independent Test**: Seed at least three pages of executions, query every page repeatedly, and verify descending timestamps, stable ties, and no duplicate or omitted IDs.

### Tests for User Story 1

- [X] T006 [P] [US1] Extend `backend/tests/contract/test_execution_list_contract.py` to assert `MiningExecution.started_at DESC NULLS LAST`, filters before pagination, stable ID tie-breaking, and the existing `offset`/`limit` envelope without introducing `created_at`.
- [X] T007 [P] [US1] Add deterministic multi-page scenarios for equal timestamps and multiple `pending` executions with `started_at IS NULL`, proving their `id DESC` order, stable traversal, new-record-first behavior, and no synthetic `created_at` in `backend/tests/integration/executions/test_pagination_order.py`.

### Implementation for User Story 1

- [X] T008 [US1] Update the execution list query in `backend/src/repository_miner/executions/api/query_router.py` to apply configuration/status filters before pagination and order by `MiningExecution.started_at DESC NULLS LAST`, followed by `MiningExecution.id DESC`.
- [X] T009 [US1] Preserve pending executions with `started_at IS NULL` in the final deterministic NULL group ordered by stable ID, without adding `created_at`, while retaining all seven canonical counters in `backend/src/repository_miner/executions/api/query_router.py`.
- [X] T010 [US1] Keep the execution response contract and page bounds unchanged, including `offset` default `0` and `limit` range `1–200`, in `backend/src/repository_miner/executions/api/query_router.py`.

**Checkpoint**: Execution list independently satisfies newest-first, deterministic, filtered, multi-page behavior.

---

## Phase 4: User Story 2 - Obter resultados estáveis entre páginas (Priority: P1)

**Goal**: Make chronological report lists deterministic at page boundaries without changing report semantics or ownership.

**Independent Test**: Seed equal-timestamp UnauthorizedCommitAlerts and repository failures, traverse every applicable page twice, and compare the complete ID sequences while preserving established commit/hash ordering.

### Tests for User Story 2

- [X] T011 [P] [US2] Add backend contract coverage for descending alert and failure history, deterministic equal-date ties, and preserved pagination envelopes in `backend/tests/contract/test_reporting_pagination_order.py`.
- [X] T012 [P] [US2] Add backend integration coverage for existing chronological `UnauthorizedCommitAlert` and repository-failure lists, including stable page traversal and no duplicate/omitted records, while preserving established commit/hash ordering and adding no CommitVerification list in `backend/tests/integration/reporting/test_pagination_order.py`.

### Implementation for User Story 2

- [X] T013 [US2] Update chronological query functions in `backend/src/repository_miner/alerts/application/queries.py` to order `UnauthorizedCommitAlert.detected_at` and `RepositoryFailure.occurred_at` descending with each record ID as a deterministic tie-breaker before offset/limit.
- [X] T014 [US2] Update only the existing chronological failure/report query paths in `backend/src/repository_miner/executions/application/queries.py` to use their canonical temporal fields descending with stable IDs; leave the existing repository and execution-commit lists in their established non-chronological order and add no CommitVerification list endpoint.
- [X] T015 [US2] Ensure report routes in `backend/src/repository_miner/reporting/api/router.py` retain existing paths, filters, error behavior, and response fields after query ordering changes.

**Checkpoint**: Chronological report histories are globally ordered and deterministic without changing counters, ownership, or traceability.

---

## Phase 5: User Story 3 - Consultar históricos filtrados e atualizados (Priority: P2)

**Goal**: Ensure frontend pagination, filters, and refreshes consume backend order without re-sorting; preserve page-size behavior only where an existing control is present (currently none).

**Independent Test**: Mock ordered API pages, navigate forward/backward, refresh after inserting a newer item, and assert request parameters plus rendered sequence. Record that no current screen has a page-size control; page-size behavior remains conditional for future screens and no new control is created.

### Tests for User Story 3

- [X] T016 [P] [US3] Add frontend tests for page navigation, return to previous page, loading/empty/error states, and preservation of API order in `frontend/tests/plans/plan-executions-pagination.test.tsx`.
- [X] T017 [P] [US3] Add frontend tests proving report lists render `items` as received and issue a fresh first-page request after refresh in `frontend/tests/reporting/pagination-order.test.tsx`; document that no current screen has an interactive page-size control (`PlanExecutionsTab` is fixed at 20 and report consumers are fixed at 50), so no page-size UI change is implemented.

### Implementation for User Story 3

- [X] T018 [US3] Update `frontend/src/plans/PlanExecutionsTab.tsx` to keep backend item order, reset to page one when the plan/filter context changes, and preserve existing loading, empty, error, and retry behavior.
- [X] T019 [US3] Update paginated report consumers under `frontend/src/reporting/` to pass page parameters through unchanged and avoid local sorting, reversing, or cross-page merging.
- [X] T020 [US3] Preserve pagination types and request bounds in `frontend/src/executions/api.ts` and `frontend/src/reporting/api.ts`, including default first-page behavior (`offset=0`).

**Checkpoint**: Frontend independently displays and navigates API-provided order without reconstructing global order.

---

## Phase 6: User Story 4 - Acompanhar execuções recentes de um plano (Priority: P2)

**Goal**: Make the Plan Verification execution tab show only the current plan's newest executions first.

**Independent Test**: Mock a current plan with more than one page and unrelated executions, open the tab, and verify the first request and rendered sequence contain only current-plan executions.

### Tests for User Story 4

- [X] T021 [P] [US4] Extend `frontend/tests/plans/plan-executions-tab.test.tsx` to assert first-page initialization, newest-first rendering in API order, current-plan filtering, and navigation to older pages.
- [X] T022 [P] [US4] Extend `backend/tests/contract/test_execution_list_contract.py` with a configuration-scoped newest-first assertion covering a new execution appearing on a fresh first-page query.

### Implementation for User Story 4

- [X] T023 [US4] Align the Plan Executions contract documentation with the implemented ordering guarantee in `specs/004-plan-navigation/contracts/frontend-api.md`, distinguishing endpoints whose ordering changes from paginated endpoints whose established order is preserved, and referencing `specs/005-standardize-pagination/contracts/pagination-order.md` without changing response shape.
- [X] T024 [US4] Verify `frontend/src/plans/api.ts` and `frontend/src/plans/PlanExecutionsTab.tsx` use the scoped execution endpoint and do not fetch or merge other plans' histories.

**Checkpoint**: Plan execution history independently opens on recent records and remains scoped to the selected plan.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Validate compatibility, documentation, and the complete feature.

- [X] T025 [P] Add regression assertions for unchanged counters, UnauthorizedCommitAlert ownership, report fields, and mining/scheduler state in `backend/tests/contract/test_cross_artifact_alignment.py`.
- [X] T026 [P] Add frontend regression coverage that no credentials or secret-bearing fields appear while paginating in `frontend/tests/plans/secret-regression.test.tsx`.
- [X] T027 Run the backend and frontend commands from `specs/005-standardize-pagination/quickstart.md` and record results in the implementation handoff.
- [X] T028 Review all changed endpoint queries for database ordering-before-pagination and update comments/documentation where the canonical ordering is not self-evident in `backend/src/repository_miner/`.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies; establishes the inventory and baseline.
- **Foundational (Phase 2)**: Depends on Setup; blocks all user stories.
- **User Story 1 (Phase 3)**: Depends on Foundational; MVP and backend execution ordering baseline.
- **User Story 2 (Phase 4)**: Depends on Foundational; can run in parallel with US1 after shared fixtures are ready.
- **User Story 3 (Phase 5)**: Depends on Foundational and the backend contract shape; can begin after T003–T005, with API mocks, but final validation depends on US1/US2 ordering contracts.
- **User Story 4 (Phase 6)**: Depends on US1 and US3 because it combines scoped execution ordering with the plan tab consumer.
- **Polish (Phase 7)**: Depends on all desired user stories.

### User Story Dependencies

- **US1 (P1)**: No story dependency after Foundational; recommended MVP.
- **US2 (P1)**: No story dependency after Foundational; report endpoints are independently testable.
- **US3 (P2)**: Uses existing envelopes and can be developed with mocks; final integration follows backend ordering contracts.
- **US4 (P2)**: Depends on US1's execution ordering and US3's frontend pagination behavior.

### Parallel Opportunities

- T004 and T005 can run in parallel after T003.
- T006 and T007 can run in parallel; T008–T010 follow them.
- T011 and T012 can run in parallel; T013–T015 follow them.
- T016 and T017 can run in parallel; T018–T020 follow them.
- T021 and T022 can run in parallel after US1/US3 prerequisites.
- T025 and T026 can run in parallel during Polish.

## Parallel Example: User Story 1

```text
Task T006: Extend backend execution contract tests
Task T007: Add deterministic multi-page integration tests
```

## Parallel Example: User Story 2

```text
Task T011: Add alert/failure contract tests
Task T012: Add UnauthorizedCommitAlert/repository-failure integration tests
```

## Parallel Example: User Story 3

```text
Task T016: Add plan execution pagination UI tests
Task T017: Add report pagination UI tests
```

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phases 1–2.
2. Complete US1 backend tests and implementation.
3. Run the US1 contract/integration tests and verify newest-first execution history.
4. Deliver the execution-list MVP before report and frontend cross-cutting work.

### Incremental Delivery

1. Add US2 report ordering and validate independently.
2. Add US3 frontend pass-through pagination and validate with mocked pages.
3. Add US4 Plan Executions integration and validate scoped history.
4. Run Polish tasks and the complete quickstart.

## Notes

- Every task uses the required checklist format with a sequential ID and an exact file path.
- `[P]` marks only tasks that can modify different files without depending on incomplete work.
- No database migration is expected: the plan reuses existing temporal fields and identifiers.
