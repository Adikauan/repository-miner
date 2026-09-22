# Tasks: Manual Configuration Operation and Editing

**Input**: Design documents from `/specs/002-manual-config-operation/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/openapi.yaml`, and `quickstart.md`

**Tests**: Test tasks are included because the specification defines independent acceptance flows and the project requires automated unit, integration, contract, and frontend validation.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm the existing feature boundaries and test scaffolding before implementation.

- [X] T001 Review existing configuration, execution, persistence, authentication, and frontend route modules against `specs/002-manual-config-operation/plan.md` and record any path changes in `specs/002-manual-config-operation/research.md`
- [X] T002 [P] Add feature test fixtures using only synthetic tokens, sentinel values, or fictitious non-sensitive secrets; prohibit real credentials and prohibit synthetic credential values from appearing in exposed fixtures, HTTP responses, logs, error messages, or test snapshots in `backend/tests/fixtures/manual_configuration.py`
- [X] T003 [P] Add frontend API test mocks for configuration detail, update, connection validation, and manual execution responses in `frontend/src/configurations/api.test.ts`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish shared contracts and application boundaries used by all stories.

**CRITICAL**: Complete this phase before implementing any user story.

- [X] T004 Define typed configuration detail/update/manual-start DTOs matching `specs/002-manual-config-operation/contracts/openapi.yaml` in `backend/src/repository_miner/configuration/api/schemas.py`
- [X] T005 [P] Add contract-first tests for `GET /api/v1/configurations/{configurationId}`, basic-fields-only `PATCH /api/v1/configurations/{configurationId}` with `additionalProperties: false`, `POST /api/v1/configurations/{configurationId}/executions`, rejection of PATCH payloads containing scope, branch, allowed users, schedule, or credentials, and rejection of connection-dependent operations with HTTP conflict code `connection_not_validated` in `backend/tests/contract/test_configuration_api.py`
- [X] T006 [P] Add unit tests for write-only credential projections and canonical configuration fields in `backend/tests/unit/configuration/test_configuration_projection.py`
- [X] T007 Define a configuration projection/read service that composes scope, allowed e-mails, schedule, connection validation, and credential status without decrypting credentials in `backend/src/repository_miner/configuration/application/queries.py`
- [X] T008 Define an edit application service with short transaction boundaries and existing validation rules in `backend/src/repository_miner/configuration/application/edit.py`
- [X] T009 Define a single manual-start application boundary that delegates to `start_persistent_execution` and maps domain conflicts to safe application errors in `backend/src/repository_miner/executions/application/start_execution.py`
- [X] T010 [P] Add unit tests for edit validation, active-execution conflict, compromised-credential rejection, and disabled-configuration manual eligibility in `backend/tests/unit/configuration/test_edit_rules.py`
- [X] T011 Register shared dependency wiring for the new projection, edit, and manual-start services without duplicating business logic in `backend/src/repository_miner/app.py`

**Checkpoint**: Shared contracts, projection, edit boundary, and manual-start boundary are available to all stories.

---

## Phase 3: User Story 1 - Consult and edit an existing configuration (Priority: P1) 🎯 MVP

**Goal**: Let an operator open an existing configuration, see persisted non-sensitive values, edit it, and save the same record.

**Independent Test**: Load an existing configuration, verify fields are populated and the credential is unavailable, change a safe field, save, reopen, and confirm no duplicate configuration exists.

### Tests for User Story 1

- [X] T012 [P] [US1] Add integration tests for configuration detail loading, missing configuration, safe load failure, and plaintext credential exclusion in `backend/tests/integration/configuration/test_configuration_detail.py`
- [X] T013 [P] [US1] Add integration tests for updating name, timezone, enabled status, and preserving the existing configuration identifier in `backend/tests/integration/configuration/test_configuration_update.py`
- [X] T014 [P] [US1] Add frontend component tests for populated editor fields, write-only credential messaging, save success, and safe error rendering in `frontend/tests/configurations/configuration-flow.test.tsx` and `frontend/tests/configurations/credential-replacement.test.tsx`

### Implementation for User Story 1

- [X] T015 [US1] Implement the configuration detail query and non-sensitive response projection in `backend/src/repository_miner/configuration/application/queries.py`
- [X] T016 [US1] Implement the detail `GET /api/v1/configurations/{configurationId}` route and preserve existing not-found/error shapes in `backend/src/repository_miner/configuration/api/router.py`
- [X] T017 [US1] Extend the configuration update request model and route to update only basic fields (name, timezone, and enabled status) on the existing row; do not update scope, repositories, branch, allowed users, schedule, or credentials in `backend/src/repository_miner/configuration/api/router.py`
- [X] T018 Add typed frontend methods for detail retrieval and update while never storing or displaying a returned credential value in `frontend/src/configurations/api.ts`
- [X] T019 [US1] Update the editor to load persisted values before rendering editable fields, distinguish write-only credentials, and submit updates without creating a new configuration in `frontend/src/configurations/ConfigurationEditor.tsx`
- [X] T020 [US1] Add configuration detail/edit navigation from the list while preserving existing routes in `frontend/src/app/routes.tsx` and `frontend/src/configurations/ConfigurationListPage.tsx`

**Checkpoint**: US1 independently supports viewing and editing an existing configuration without secret exposure or duplication.

---

## Phase 4: User Story 2 - Change connection, scope, users, or schedule safely (Priority: P1)

**Goal**: Safely change connection-dependent settings while preserving incremental state and historical records.

**Independent Test**: Change URL/credential, scope, branch, allowed e-mails, and schedule; verify required revalidation, baseline/checkpoint preservation, future-only user rules, and recalculated scheduling.

### Tests for User Story 2

- [X] T021 [P] [US2] Add integration tests proving URL or credential changes invalidate connection validation and block group, subgroup, repository, branch, scope, and repository-selection operations until successful revalidation, returning `connection_not_validated` with HTTP conflict in `backend/tests/integration/configuration/test_edit_connection_validation.py`
- [X] T022 [P] [US2] Add integration tests for preserving omitted credentials and replacing credentials without changing checkpoints, executions, commit verifications, or alerts in `backend/tests/integration/configuration/test_credential_replacement.py` and `backend/tests/integration/test_persistence.py`
- [X] T023 [P] [US2] Add integration tests for loading and selecting branches, adding/removing repositories, and changing scope while preserving historical records and creating a new baseline for new combinations in `backend/tests/integration/configuration/test_edit_scope_history.py`
- [X] T024 [P] [US2] Add integration tests asserting that normalized allowed-user changes succeed even when the GitLab connection is not validated, while not reprocessing existing verifications or duplicating alerts, in `backend/tests/integration/configuration/test_edit_allowed_users.py`
- [X] T025 [P] [US2] Add integration tests asserting that daily, weekly, and monthly schedule edits succeed even when the GitLab connection is not validated, including last-day handling, no retroactive run, and disabled scheduling, in `backend/tests/integration/configuration/test_edit_schedule.py`
- [X] T026 [P] [US2] Add frontend tests for connection revalidation messaging, group/subgroup/repository and branch loading, scope/repository selection editing, allowed e-mail editing, schedule editing, and validation/conflict errors in `frontend/tests/configurations/ConfigurationEditor.editing.test.tsx`

### Implementation for User Story 2

- [X] T027 [US2] Implement and test connection-identity change detection that clears `connection_validated_at`, `validated_gitlab_base_url`, and `validated_credential_id` before dependent writes; complete this rule before T028, T029, and any final dependent-operation implementation in `backend/src/repository_miner/configuration/application/edit.py`
- [X] T028 [US2] Extend configuration edit persistence for GitLab URL and optional replacement credential using existing encrypted credential replacement services, after T027, in `backend/src/repository_miner/configuration/application/edit.py` and `backend/src/repository_miner/configuration/application/credential_replacement.py`
- [X] T029 [US2] Enforce successful current-connection validation before loading groups, subgroups, repositories, or branches and before persisting scope or repository selections; return `connection_not_validated` with HTTP conflict when invalid, and complete this guard before T033 or any final dependent-operation wiring in `backend/src/repository_miner/configuration/api/router.py`
- [X] T030 [US2] Preserve removed scope history and route new repository/branch combinations through existing checkpoint baseline behavior in `backend/src/repository_miner/repositories/application/resolve_scope.py` and `backend/src/repository_miner/mining/application/persistent_runner.py`
- [X] T031 [US2] Persist normalized allowed-user edits with future-only validation semantics in `backend/src/repository_miner/configuration/api/router.py`
- [X] T032 [US2] Recalculate persisted schedule values after recurrence, time, timezone, weekday, day-of-month, or enabled-status edits without creating retroactive executions in `backend/src/repository_miner/scheduling/infrastructure/scheduler.py` and `backend/src/repository_miner/configuration/application/edit.py`
- [X] T033 [US2] Update the frontend editor sections so `enabled` is saved through the configuration PATCH, while scope, branch, allowed users, and schedule are saved through their respective dedicated endpoints; use validated GitLab operations for groups, subgroups, repositories, branch loading, scope, and repository selection in `frontend/src/configurations/ConfigurationEditor.tsx` and `frontend/src/configurations/api.ts`

**Checkpoint**: US2 preserves all prior incremental and audit history while applying validated future configuration changes.

---

## Phase 5: User Story 3 - Start and follow a manual execution (Priority: P1)

**Goal**: Start mining manually from the configuration view and follow the existing persisted/realtime execution flow.

**Independent Test**: Start valid enabled and disabled configurations, receive one execution identifier, reject active/compromised cases without creating executions, and open the existing snapshot/live monitoring view.

### Tests for User Story 3

- [X] T034 [P] [US3] Add integration tests for valid manual execution creation, manual trigger metadata, and execution identifier response in `backend/tests/integration/executions/test_start_execution.py`
- [X] T035 [P] [US3] Add integration tests for disabled-configuration manual execution, compromised-credential rejection, and active-execution conflict with no duplicate `MiningExecution` in `backend/tests/integration/executions/test_start_execution.py`
- [X] T036 [P] [US3] Add integration tests proving manual execution reuses the persistent runner, checkpoint/idempotency behavior, canonical counters, and existing lifecycle events in `backend/tests/integration/mining/test_persistent_runner.py`
- [X] T037 [P] [US3] Add frontend tests for manual-start success, returned execution identifier, conflict/credential errors, and navigation to execution monitoring in `frontend/tests/configurations/ConfigurationEditor.manual.test.tsx`
- [X] T038 [P] [US3] Add contract assertions that the manual-start response and execution snapshot use canonical states and counters in `backend/tests/contract/test_canonical_counters.py`

### Implementation for User Story 3

- [X] T039 [US3] Implement the manual execution endpoint using the shared start service and return `execution_id` with the existing status contract in `backend/src/repository_miner/app.py`
- [X] T040 [US3] Ensure manual start validates required persisted configuration data, active credential state, and one-active-execution locking before creating `MiningExecution` in `backend/src/repository_miner/executions/application/start_execution.py`
- [X] T041 [US3] Wire the configuration editor manual-run action to the existing execution API and navigate to the persisted execution view in `frontend/src/configurations/ConfigurationEditor.tsx` and `frontend/src/configurations/api.ts`
- [X] T042 [US3] Reuse existing REST snapshot, temporary ticket, WebSocket stream, reconnect, terminal-state, and report handling for manually started executions in `frontend/src/executions/ExecutionDetailPage.tsx` and `frontend/src/executions/useExecutionStream.ts`
- [X] T043 [US3] Map missing configuration, invalid connection, compromised credential, active execution, validation, and upstream failures to safe user-facing messages without secrets in `backend/src/repository_miner/shared/api/errors.py` and `frontend/src/shared/api/client.ts`

**Checkpoint**: US3 supports manual execution and monitoring without a second mining or realtime mechanism.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Validate the integrated feature and keep documentation/contracts aligned.

- [X] T044 [P] Validate the feature OpenAPI document and contract examples in `specs/002-manual-config-operation/contracts/openapi.yaml`
- [X] T045 [P] Add observability assertions for edit, validation, manual-start rejection, and execution correlation without secrets in `backend/tests/integration/security/test_secret_leakage.py` and `backend/tests/unit/shared/test_observability.py`
- [X] T046 [P] Add frontend accessibility and loading/empty/error-state checks for the configuration editor in `frontend/tests/configurations/ConfigurationEditor.a11y.test.tsx`
- [X] T047 Run the feature quickstart scenarios and document actual commands/results in `specs/002-manual-config-operation/quickstart.md`
- [X] T048 Run backend pytest, frontend build/tests, and compile checks; fix regressions without changing existing contracts in `backend/` and `frontend/`

## Phase 7: Convergence

- [X] T049 [US1] Complete persisted-scope visualization by loading the repository tree and available branches for the existing configuration after detail loading, restoring current selections and branch choices through the dedicated validated GitLab operations per FR-001, FR-002, and SC-001 (partial)
- [X] T050 [US1] Align the PATCH response projection with the declared `Configuration` contract while keeping credential fields write-only and preserving the existing configuration identifier per FR-004 and the plan contract rules (partial)
- [X] T051 [US2] Reconcile the canonical connection-test path between backend routes, frontend API calls, and `contracts/openapi.yaml` without introducing duplicate behavior, preserving the `connection_not_validated` conflict contract per FR-026 and the plan (partial)
- [X] T052 [US3] Handle configuration-load, connection-validation, configuration-save, and manual-start failures in the editor with safe actionable messages and no secret values, covering the rejection paths required by FR-021 and SC-003 (partial)

---

## Dependencies & Execution Order

### Phase Dependencies

- Setup (Phase 1) has no dependencies.
- Foundational (Phase 2) depends on Setup and blocks all user stories.
- US1, US2, and US3 depend on Foundational; US2 and US3 reuse US1's editor/navigation work.
- Polish depends on the desired user-story phases.

### User Story Dependencies

- **US1 (P1)**: Depends on Phase 2; delivers the MVP configuration read/edit flow.
- **US2 (P1)**: Depends on Phase 2 and the configuration editor surface from US1; its domain rules can be tested independently.
- **US3 (P1)**: Depends on Phase 2 and the editor/navigation surface from US1; it reuses the existing execution flow rather than depending on US2's data-edit behavior.
- **US2 validation order**: T027 MUST precede T028 and T029; T029 MUST complete before T033 or any final dependent-operation wiring.

### Parallel Opportunities

- T002/T003 and T005/T006/T010 can run in parallel after their referenced contracts are agreed.
- US1 tests T012-T014 can run in parallel.
- US2 tests T021-T026 can run in parallel.
- US3 tests T034-T038 can run in parallel.
- T044-T046 can run in parallel after the corresponding stories are implemented.

## Implementation Strategy

### MVP First

1. Complete Setup and Foundational phases.
2. Complete US1 and validate persisted configuration viewing/editing.
3. Deliver US1 as the first usable increment.

### Incremental Delivery

1. Add US2 and validate safe connection, scope, user, and schedule changes.
2. Add US3 and validate manual execution plus existing monitoring.
3. Run Polish validation and regression tests.

### Notes

- Every task uses the required `- [ ] T### [P?] [Story?] description with file path` format.
- No new migrations are planned because this feature reuses existing entities and persistence keys.
- No task introduces diffs, source-content analysis, AI, or a second execution mechanism.
