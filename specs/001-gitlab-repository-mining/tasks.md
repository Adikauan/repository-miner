---
description: "Dependency-ordered implementation tasks for GitLab Repository Author Monitoring"
---

# Tasks: GitLab Repository Author Monitoring

**Input**: Design documents from `/specs/001-gitlab-repository-mining/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Required by the plan and Constitution. Write each listed test first and confirm that it
fails for the intended reason before implementing its corresponding behavior.

**Organization**: Tasks are grouped by user story as independently testable increments.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Parallelizable in a distinct path without an incomplete dependency.
- **[Story]**: Maps to a user story from spec.md.
- Every task includes an exact target path.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize the modular web monolith and quality tooling.

- [X] T001 Create backend module skeleton from plan.md in backend/src/repository_miner/
- [X] T002 Initialize Python 3.13 metadata with FastAPI, Pydantic, SQLAlchemy 2.x, Alembic, APScheduler, HTTP client, cryptography, and pytest in backend/pyproject.toml
- [X] T003 [P] Initialize React 19 and TypeScript 5.x with Material UI, routing, server-state query, and test dependencies in frontend/package.json
- [X] T004 [P] Configure strict TypeScript, aliases, and build settings in frontend/tsconfig.json
- [X] T005 [P] Configure Python linting, typing, pytest markers, and coverage defaults in backend/pyproject.toml
- [X] T006 [P] Configure frontend linting and test runner defaults in frontend/eslint.config.js
- [X] T007 Create local PostgreSQL and single-application topology in deploy/compose.yaml
- [X] T008 Create redacted database, encryption-key, ticket-pepper, timezone, and GitLab settings in deploy/env.example

**Checkpoint**: Both projects install, lint, and start without feature behavior.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish shared test-first infrastructure, persistence, security, ports, and fakes.

**CRITICAL**: No user-story implementation begins until this phase completes.

### Foundational tests — write and fail first

- [X] T009 [P] Add tests for authenticated credential encryption, external key rotation, plaintext non-serialization, and non-active credential refusal in backend/tests/unit/shared/test_credentials.py
- [X] T010 [P] Add tests for correlation IDs, safe errors, and GitLab credential redaction from logs in backend/tests/unit/shared/test_observability.py
- [X] T011 [P] Add tests for `AuthenticatedOperatorProvider` covering valid host identity, absent identity, invalid identity, stable operator mapping, and isolation from HTTP headers/cookies/provider SDK objects in backend/tests/unit/authentication/test_authenticated_operator_provider.py

### Foundational implementation

- [X] T012 Create FastAPI application factory, lifespan hooks, and versioned router in backend/src/repository_miner/app.py
- [X] T013 [P] Define shared UUIDs, UTC timestamps, result types, domain errors, and lifecycle primitives in backend/src/repository_miner/shared/domain/types.py
- [X] T014 [P] Define safe API errors with required `code`, `message`, `trace_id`, optional `details`, and closed GitLab codes `gitlab_timeout|gitlab_unavailable|gitlab_rate_limited|gitlab_unexpected_response|gitlab_malformed_payload` with safe retry metadata in backend/src/repository_miner/shared/api/errors.py
- [X] T015 [P] Implement correlation IDs and credential-safe structured logging filters in backend/src/repository_miner/shared/infrastructure/logging.py
- [X] T016 Configure SQLAlchemy engine and one-session-per-request-or-runner factory in backend/src/repository_miner/persistence/session.py
- [X] T017 Configure Alembic metadata and migration environment in backend/migrations/env.py
- [X] T018 Define GitLabGateway contracts for valid connection/hierarchy/branch HEAD/paginated commit metadata responses and typed timeout, unavailable, rate-limited, unexpected-response, and malformed-payload failures in backend/src/repository_miner/gitlab/application/ports.py
- [X] T019 [P] Define `AuthenticatedOperator` and `AuthenticatedOperatorProvider` ports, including authentication failure and stable operator identifier, in backend/src/repository_miner/authentication/application/ports.py
- [X] T020 Implement authenticated encryption and active-status validation for GitLab credentials in backend/src/repository_miner/configuration/infrastructure/credentials.py
- [X] T021 [P] Create deterministic GitLab fake for hierarchy, branch HEAD, commit metadata pagination, credential compromise, and scoped failures in backend/tests/fakes/gitlab.py
- [X] T022 [P] Create fake clock, host-authenticated operator provider, local dispatcher, and recording event publisher in backend/tests/fakes/execution.py
- [X] T023 [P] Create frontend shell, Material UI theme, error boundary, and route placeholders in frontend/src/app/App.tsx
- [X] T024 [P] Implement typed REST client with safe errors and credential-safe middleware in frontend/src/shared/api/client.ts
- [X] T025 Implement `AuthenticatedOperatorProvider` to expose only validated stable operator identity or an authentication failure to use cases in backend/src/repository_miner/authentication/application/provider.py
- [X] T026 Implement the replaceable HTTP adapter/middleware that obtains host identity, validates presence and validity, feeds `AuthenticatedOperatorProvider`, rejects missing/invalid identity before use cases, and never accepts operator identity from request payloads in backend/src/repository_miner/authentication/infrastructure/http.py

**Checkpoint**: Foundation passes without network or external credentials.

---

## Phase 3: User Story 1 - Configure Author Monitoring (Priority: P1) MVP

**Goal**: Configure protected GitLab access, repository scope, branch, allowed e-mails, schedule,
and credential incident response.

**Independent Test**: Save and reopen a configuration without secret disclosure, browse/select a
nested scope, normalize allowed e-mails, replace an active credential preventively, and remediate a
compromised credential while preserving checkpoints and all historical mining records.

### Tests for User Story 1 — write and fail first

- [X] T027 [P] [US1] Add configuration, connection-test, repository-tree, selection, allowed-user, and credential-incident contract tests from openapi.yaml, including `401` for absent/invalid identity and `403` for an unauthorized valid operator on incident operations, in backend/tests/contract/test_configuration_api.py
- [X] T028 [P] [US1] Add separate GitLab gateway contract cases for a valid response, malformed response, timeout, GitLab unavailability, unexpected HTTP response, and rate limit; assert each failure translates to a stable safe application error and that messages/logs contain neither tokens nor sensitive response data in backend/tests/contract/test_gitlab_gateway.py
- [X] T029 [P] [US1] Add tests for daily/weekly/monthly recurrence, timezone conversion, and last-calendar-day fallback in backend/tests/unit/scheduling/test_recurrence.py
- [X] T030 [P] [US1] Add tests for preventive `active -> replaced`, mandatory `compromised -> replaced`, refusal to reuse compromised credentials before replacement, non-reactivation, authenticated replacement actor, absent/invalid identity failure, and secret-free incident/replacement audit in backend/tests/unit/configuration/test_credential_incidents.py
- [X] T031 [P] [US1] Add frontend tests for connection validation, tri-state selection, QA default, allowed e-mails, schedule, secret masking, and blocked compromised state in frontend/tests/configurations/configuration-flow.test.tsx

### Implementation for User Story 1

#### Models and migration

- [X] T032 [P] [US1] Create MonitoringConfiguration with name 1–120 characters, HTTPS GitLab URL outside local development, target_branch default `QA`, IANA timezone, enabled, and version in backend/src/repository_miner/configuration/infrastructure/models.py
- [X] T033 [P] [US1] Create CredentialReference with kind `gitlab_token`, status `active|compromised|replaced`, ciphertext, key_version, fingerprint, compromised_at, replaced_by_id, created_at, and last_rotated_at in backend/src/repository_miner/configuration/infrastructure/credential_models.py
- [X] T034 [P] [US1] Create CredentialIncident with status `open|replacement_recorded|closed`, credential, stable operator fields and audit timestamps, plus CredentialReplacement unique by previous_credential_id with required configuration/old/new references, `preventive|compromise_remediation`, conditional incident_id, replaced_by, and replaced_at in backend/src/repository_miner/configuration/infrastructure/incident_models.py
- [X] T035 [P] [US1] Create RepositorySelectionRule with kind `group|subgroup|repository`, mode `include|exclude`, and unique configuration-kind-external_id in backend/src/repository_miner/repositories/infrastructure/models.py
- [X] T036 [P] [US1] Create AllowedUser with required non-empty original e-mail, trimmed/case-folded normalized e-mail, and unique configuration-normalized_e-mail in backend/src/repository_miner/configuration/infrastructure/allowed_user_models.py
- [X] T037 [P] [US1] Create Schedule with recurrence `daily|weekly|monthly`, local time, weekday 1–7, day_of_month 1–31, IANA timezone, and next_run_at in backend/src/repository_miner/scheduling/infrastructure/models.py
- [X] T038 [US1] Create configuration, credential lifecycle, CredentialIncident, CredentialReplacement with unique previous credential and conditional incident linkage, selection, allowed-user, schedule, and repository identity migration in backend/migrations/versions/001_configuration.py

#### Persistence tests after migration

- [X] T039 [US1] Add persistence tests after migration for encrypted credentials, CredentialReplacement uniqueness by previous_credential_id, reason/incident linkage rules, configuration constraints, selection uniqueness, normalized e-mail uniqueness, schedules, and current credential status limited to `active|compromised` in backend/tests/integration/configuration/test_persistence.py
- [X] T040 [US1] Add integration test after migration proving groups, subgroups, repositories, and branch cannot be persisted before successful validation of the exact current GitLab URL and credential and become invalid again after either changes in backend/tests/integration/configuration/test_scope_validation.py

#### Services and adapters
- [X] T041 [US1] Implement configuration create/read/update, validation, enable, and disable operations in backend/src/repository_miner/configuration/application/service.py
- [X] T042 [US1] Implement atomic compromise handling that requires `AuthenticatedOperatorProvider`, blocks connection tests and new executions, and records stable operator identity in a secret-free incident in backend/src/repository_miner/configuration/application/credential_incidents.py
- [X] T043 [US1] Implement unit-level credential replacement state rules for preventive `active -> replaced`, mandatory `compromised -> replaced`, permanent retirement, new active reference, and `preventive|compromise_remediation` classification without integrating execution history in backend/src/repository_miner/configuration/domain/credential_replacement.py
- [X] T044 [US1] Implement GitLab connection and hierarchy adapter with pagination, active-credential checks, strict response validation, timeout/unavailability/unexpected-HTTP/rate-limit translation to safe application errors, and token/sensitive-payload redaction in backend/src/repository_miner/gitlab/infrastructure/http_gateway.py
- [X] T045 [US1] Implement scope-persistence precondition in the configuration/repository service: require successful validation matching the current GitLab URL and credential before saving groups, subgroups, repositories, or branch; invalidate validation after URL or credential change in backend/src/repository_miner/repositories/application/service.py
- [X] T046 [US1] Implement allowed-user replacement with trim/case normalization and duplicate rejection in backend/src/repository_miner/configuration/application/allowed_users.py
- [X] T047 [US1] Implement recurrence and next-due calculations including last-day monthly fallback in backend/src/repository_miner/scheduling/domain/recurrence.py
- [X] T048 [US1] Implement configuration, connection, hierarchy, selection, allowed-user, and credential-incident routes in backend/src/repository_miner/configuration/api/router.py
- [X] T049 [P] [US1] Create typed configuration, CredentialIncident, and CredentialReplacement DTOs/query hooks matching openapi.yaml in frontend/src/configurations/api.ts
- [X] T050 [P] [US1] Implement accessible tri-state repository selector in frontend/src/repositories/RepositoryTree.tsx
- [X] T051 [US1] Implement configuration editor for GitLab connection, scope, branch, allowed e-mails, schedule, and review in frontend/src/configurations/ConfigurationEditor.tsx
- [X] T052 [US1] Implement credential incident panel with compromised blocked status, external rotation instruction, and authenticated incident confirmation in frontend/src/configurations/CredentialIncidentPanel.tsx
- [X] T053 [US1] Implement configuration list with enabled state, next due time, compromise warning, edit action, and manual-run entry in frontend/src/configurations/ConfigurationListPage.tsx
- [X] T054 [US1] Register configuration routes and pass the independent US1 scenario in frontend/src/app/routes.tsx

**Checkpoint**: US1 securely configures author monitoring and credential incidents.

---

## Phase 4: User Story 2 - Run Incremental Author Verification (Priority: P2)

**Goal**: Execute baseline and incremental commit-metadata verification, create traceable
unauthorized-author alerts, isolate repository failures, and advance successful checkpoints.

**Independent Test**: Establish baseline, add allowed/unmatched/missing-e-mail commits, verify them
once, fail a repository after some verification rows commit, retain its prior checkpoint, and prove
the next execution reuses completed verifications while processing only the remaining commits.

### Tests for User Story 2 — write and fail first

- [X] T055 [P] [US2] Add tests for first-execution HEAD baseline, new-combination baseline, existing checkpoint range, history rewrite, and no-history processing in backend/tests/unit/mining/test_incremental_rules.py
- [X] T056 [P] [US2] Add tests for exact normalized e-mail matching, original metadata preservation, missing e-mail unauthorized classification, and one-alert uniqueness in backend/tests/unit/mining/test_author_verification.py
- [X] T057 [P] [US2] Add tests proving GitLabGateway exposes and invokes metadata-only operations and never requests commit change content in backend/tests/contract/test_gitlab_commit_gateway.py

### Implementation for User Story 2

#### Models and migration

- [X] T058 [P] [US2] Create Execution with status exactly `pending|running|completed|partially_completed|failed`, immutable snapshot, monotonic revision, lifecycle, terminal_reason, and counters in backend/src/repository_miner/executions/infrastructure/models.py
- [X] T059 [P] [US2] Create ScheduleOccurrence with `started|skipped_active|skipped_disabled|skipped_compromised`, execution reference, safe reason, and unique configuration-due_at in backend/src/repository_miner/scheduling/infrastructure/occurrence_models.py
- [X] T060 [P] [US2] Create IncrementalCheckpoint unique by configuration/repository/branch with baseline_hash, last_processed_hash, initialized_at, and advanced_at in backend/src/repository_miner/mining/infrastructure/checkpoint_models.py
- [X] T061 [P] [US2] Create ExecutionRepository with `pending|running|completed|failed`, observed HEAD, baseline flag, four commit counters, lifecycle, failure reference, and unique execution-repository-branch in backend/src/repository_miner/executions/infrastructure/repository_models.py
- [X] T062 [P] [US2] Create Commit with repository/`commit_hash` uniqueness and only `commit_hash`, author name, original author e-mail, committed timestamp, message, and optional source URL in backend/src/repository_miner/mining/infrastructure/commit_models.py
- [X] T063 [P] [US2] Create immutable CommitVerification with required composite identity `(configuration_id, repository_id, branch, commit_hash)`, normalized e-mail, `allowed|unauthorized`, first_verified_execution_id, and required verified_at, plus ExecutionCommit unique by execution-repository/commit with `new|reused` source in backend/src/repository_miner/mining/infrastructure/verification_models.py
- [X] T064 [P] [US2] Create UnauthorizedCommitAlert containing only identifiers plus configuration, detecting execution, repository, branch, `commit_hash`, author, author e-mail, commit date, and detected_at with unique commit_verification_id in backend/src/repository_miner/alerts/infrastructure/models.py
- [X] T065 [P] [US2] Create RepositoryFailure with execution, repository run, stage, stable code, safe reason, timestamp, continued flag, and correlation ID in backend/src/repository_miner/executions/infrastructure/failure_models.py
- [X] T066 [US2] Create execution, occurrence, checkpoint, repository run, durable verification, execution observation, alert, failure, and active-execution indexes including unique `(configuration_id, repository_id, branch, commit_hash)` in backend/migrations/versions/002_execution_mining.py

#### Persistence tests after migration

- [X] T067 [P] [US2] Add persistence-backed tests after migration for one active `pending|running` execution, manual execution while disabled, skipped scheduled occurrence, and immutable credential-free snapshot in backend/tests/integration/executions/test_start_execution.py
- [X] T068 [P] [US2] Add checkpoint tests after migration proving no advancement after partial failure and advancement only after integral repository success in backend/tests/integration/mining/test_checkpoints.py
- [X] T069 [P] [US2] Add idempotency tests after migration proving an earlier completed verification is detected and never author-validated again, no duplicate UnauthorizedCommitAlert is created, the alert retains its original execution_id, a later execution excludes it from its own alert projection and counters, and a retry processes only unseen commits in backend/tests/integration/mining/test_verification_idempotency.py
- [X] T070 [P] [US2] Add repository-run tests after migration for isolated failures and terminal reconciliation: all success `completed`, mixed `partially_completed`, zero success `failed`, and zero commits `completed` in backend/tests/integration/mining/test_runner.py
- [X] T071 [P] [US2] Add compromised-credential tests after migration for the guard before every GitLab call, preservation of completed checkpoints, and partial/failed outcomes in backend/tests/integration/mining/test_compromised_credential.py
- [X] T072 [P] [US2] Add scheduler tests after migration for enabled/disabled behavior, due uniqueness, restart recovery, latest missed occurrence, active-execution skip, and monthly fallback in backend/tests/integration/scheduling/test_scheduler.py
- [X] T073 [P] [US2] Add credential-replacement preservation tests after execution/checkpoint/verification/alert migrations proving checkpoints, executions, CommitVerification rows, and UnauthorizedCommitAlerts remain unchanged and the alert remains tied to its original execution in backend/tests/integration/configuration/test_credential_replacement.py
- [X] T074 [P] [US2] Add CredentialReplacement endpoint contract tests after migrations for preventive and compromise-remediation responses, current configuration status `active|compromised`, authenticated operator audit, and `401|403|409` failures in backend/tests/contract/test_credential_replacement_api.py
- [X] T075 [P] [US2] Add frontend tests for preventive replacement, mandatory compromised-credential replacement, active current status, and preserved-history confirmation in frontend/tests/configurations/credential-replacement.test.tsx

#### Services and adapters

- [X] T076 [US2] Implement final credential-replacement application service after preservation tests, atomically installing the new active reference and audit while leaving checkpoints, executions, CommitVerification rows, and UnauthorizedCommitAlerts untouched in backend/src/repository_miner/configuration/application/credential_replacement.py
- [X] T077 [US2] Implement authenticated credential-replacement route matching openapi.yaml in backend/src/repository_miner/configuration/api/credential_replacement_router.py
- [X] T078 [US2] Implement preventive/mandatory replacement UI and preserved-history confirmation in frontend/src/configurations/CredentialReplacementPanel.tsx
- [X] T079 [US2] Implement transactional manual/scheduled start with row lock, sanitized snapshot, compromised-credential guard, active conflict, and schedule skip behavior in backend/src/repository_miner/executions/application/start_execution.py
- [X] T080 [US2] Implement local dispatcher and idempotent RunExecution command using durable IDs and independent sessions in backend/src/repository_miner/executions/infrastructure/local_dispatcher.py
- [X] T081 [US2] Extend GitLab adapter with branch HEAD and paginated commit metadata since `commit_hash`, checking active credential immediately before every call and applying the safe error translation established in T028/T043 in backend/src/repository_miner/gitlab/infrastructure/http_gateway.py
- [X] T082 [US2] Implement dynamic selection resolution into immutable execution repository snapshots in backend/src/repository_miner/repositories/application/resolve_scope.py
- [X] T083 [US2] Implement baseline creation, checkpoint-range discovery, history-rewrite failure, and checkpoint advancement only after complete repository success while retaining the previous checkpoint after partial persistence in backend/src/repository_miner/mining/application/incremental.py
- [X] T084 [US2] Implement atomic lookup-or-create commit verification by configuration/repository/branch/commit hash, detect and reuse completed rows, prevent renewed author validation, classify only unseen commits, link `new|reused` observations, and increment verified/result counters only for `new` in backend/src/repository_miner/mining/application/verify_commit.py
- [X] T085 [US2] Implement exactly-one UnauthorizedCommitAlert per durable CommitVerification, keep immutable execution_id as the original detection execution, create no duplicate on reuse, and exclude prior alerts from later execution projections in backend/src/repository_miner/alerts/application/service.py
- [X] T086 [US2] Implement repository runner flow that durably commits each new verification/alert before continuing, survives later repository failure, reuses prior completed rows on retry, and emits progress whose verified/allowed/unauthorized counters exclude reused observations in backend/src/repository_miner/mining/application/repository_runner.py
- [X] T087 [US2] Implement multi-repository isolation, immediate compromise containment, durable-work preservation, and canonical terminal reconciliation in backend/src/repository_miner/mining/application/runner.py
- [X] T088 [US2] Implement persistent in-process schedule reconciliation and application lifespan registration in backend/src/repository_miner/scheduling/infrastructure/scheduler.py
- [X] T089 [US2] Implement manual execution accepted/conflict endpoint in backend/src/repository_miner/executions/api/router.py
- [X] T090 [US2] Wire GitLab, mining, alerts, scheduling, credential guards, dispatcher, and persistence in backend/src/repository_miner/app.py

**Checkpoint**: US2 verifies new commit authors exactly once with safe incremental behavior.

---

## Phase 5: User Story 3 - Monitor an Execution (Priority: P3)

**Goal**: Monitor durable execution state through REST and ticket-authenticated WebSocket events.

**Independent Test**: Resolve a valid host operator, authorize ticket issuance, bind the ticket to
that operator and execution, reject absent/invalid/unauthorized identity plus invalid/reused/
expired/wrong-scope tickets, then reconnect and recover authoritative state through REST.

### Tests for User Story 3 — write and fail first

- [X] T091 [P] [US3] Add execution history/detail/repository/commit query contract tests for canonical states, revisions, counters, and metadata-only commit responses in backend/tests/contract/test_execution_query_api.py
- [X] T092 [P] [US3] Add event tests for all nine event types, exact counters, identifier-only alert event, monotonic revision, coalescing, and terminal notification in backend/tests/contract/test_websocket_events.py
- [X] T093 [P] [US3] Add frontend tests for REST snapshot, ticket issuance, fresh reconnect ticket, stale/duplicate ignore, gap refetch, reconnect state, and terminal refresh in frontend/tests/executions/live-execution.test.tsx

### Implementation for User Story 3

#### Model and migration

- [X] T094 [P] [US3] Create WebSocketTicket with unique HMAC digest, operator_id, execution_id, expires_at issued plus 60 seconds, consumed_at, and created_at in backend/src/repository_miner/executions/infrastructure/websocket_ticket_models.py
- [X] T095 [US3] Add WebSocket ticket table, unique digest index, expiry index, and cleanup support in backend/migrations/versions/003_websocket_tickets.py

#### Persistence and authentication tests after migration
- [X] T096 [P] [US3] Add ticket issuance tests after migration for absent identity `401`, invalid identity `401`, unauthorized operator-on-execution `403`, authorized issuance, 256-bit generation, digest-only storage, 60-second expiry, and exact operator/execution binding in backend/tests/integration/executions/test_websocket_tickets.py
- [X] T097 [P] [US3] Add WebSocket consumption tests after migration rejecting expired, already consumed, wrong-operator, wrong-execution, invalid, and GitLab-credential attempts uniformly with code 1008 and proving failed mismatches do not consume a valid ticket in backend/tests/integration/executions/test_websocket_auth.py

#### Services and adapters
- [X] T098 [US3] Implement ticket issuance through `AuthenticatedOperatorProvider`, fail on absent/invalid identity, authorize the operator for the requested execution, bind operator plus execution, generate 256-bit randomness, persist only the external-pepper digest, and return plaintext once in backend/src/repository_miner/executions/application/websocket_tickets.py
- [X] T099 [US3] Implement atomic ticket consumption comparing the host-validated operator and route execution to stored operator_id/execution_id, rejecting expired, consumed, wrong-operator, and wrong-execution tickets uniformly without consuming valid mismatches in backend/src/repository_miner/executions/application/consume_websocket_ticket.py
- [X] T100 [US3] Implement authenticated ticket issuance route using the host identity middleware with `401`/`403` mapping, no request-body operator identifier, and ticket redaction from access logs in backend/src/repository_miner/executions/api/websocket_ticket_router.py
- [X] T101 [P] [US3] Implement paginated execution, repository-run, and commit-verification queries in backend/src/repository_miner/executions/application/queries.py
- [X] T102 [P] [US3] Implement transactional revisions and envelopes for the nine required event types in backend/src/repository_miner/executions/application/events.py
- [X] T103 [US3] Implement in-memory connection manager and WebSocket route accepting only consumed valid tickets in backend/src/repository_miner/executions/infrastructure/websocket.py
- [X] T104 [US3] Publish started, repository progress/outcome, identifier-only unauthorized alert, and terminal events with one-second repository coalescing in backend/src/repository_miner/executions/application/event_publisher.py
- [X] T105 [US3] Expose authoritative paginated execution query routes in backend/src/repository_miner/executions/api/query_router.py
- [X] T106 [P] [US3] Create typed execution, ticket, commit metadata, and event DTOs/query hooks in frontend/src/executions/api.ts
- [X] T107 [US3] Implement reconnecting client with fresh ticket per attempt, capped jitter, revision checks, post-connect snapshot, and gap/terminal refetch in frontend/src/executions/useExecutionStream.ts
- [X] T108 [US3] Implement execution history with canonical status filters and pagination in frontend/src/executions/ExecutionHistoryPage.tsx
- [X] T109 [US3] Implement live detail with connection state, repository progress, commit counters, alerts, and failures in frontend/src/executions/ExecutionDetailPage.tsx
- [X] T110 [US3] Register execution routes and terminal report transition in frontend/src/app/routes.tsx

**Checkpoint**: US3 remains accurate across disconnects without affecting mining.

---

## Phase 6: User Story 4 - Review the Execution Report (Priority: P4)

**Goal**: Present reconciled execution totals, detailed unauthorized commits, failures, and state.

**Independent Test**: Review successful, partial, failed, and zero-commit fixture reports and verify
counter identities, safe reasons, and metadata-only alert traceability.

### Tests for User Story 4 — write and fail first

- [X] T111 [P] [US4] Add report aggregation tests for `repositories_total`, `repositories_completed`, `repositories_failed`, `commits_discovered`, `commits_verified`, `allowed_commits`, and `unauthorized_commits`, proving reused verifications and prior alerts do not increase the later execution's counters or details and `commits_verified = allowed_commits + unauthorized_commits` in backend/tests/unit/reporting/test_aggregates.py
- [X] T112 [P] [US4] Add report/unauthorized-commit/failure endpoint contract tests with pagination and canonical terminal state in backend/tests/contract/test_reporting_api.py
- [X] T113 [P] [US4] Add tests proving every alert exposes metadata provenance, retains its immutable original detection execution, is historically queryable there, and is absent from later execution-scoped reports that only reused its verification in backend/tests/integration/reporting/test_traceability.py
- [X] T114 [P] [US4] Add frontend tests for report counters, detailed unauthorized commits, failure causes, partial/failed states, and zero-commit completed runs in frontend/tests/reporting/report-page.test.tsx

### Implementation for User Story 4

- [X] T115 [P] [US4] Implement durable report aggregation whose commits_verified, allowed_commits, and unauthorized_commits include only `verification_source = new` observations from the requested execution while commits_discovered may include reused observations in backend/src/repository_miner/reporting/application/queries.py
- [X] T116 [P] [US4] Implement paginated unauthorized-commit projection filtered strictly by immutable original alert execution_id, with no reporting_execution_id and no projection into later reuse executions, plus repository-failure traceability in backend/src/repository_miner/alerts/application/queries.py
- [X] T117 [US4] Implement report, unauthorized-commit, and failure routes matching openapi.yaml in backend/src/repository_miner/reporting/api/router.py
- [X] T118 [P] [US4] Create typed report and unauthorized-commit DTOs/query hooks in frontend/src/reporting/api.ts
- [X] T119 [US4] Implement report cards for repository and commit counters plus terminal state in frontend/src/reporting/ReportSummary.tsx
- [X] T120 [US4] Implement detailed unauthorized-commit and repository-failure tables in frontend/src/reporting/ReportDetailPage.tsx
- [X] T121 [US4] Register report route and execution links in frontend/src/app/routes.tsx

**Checkpoint**: US4 reconciles durable outcomes and exposes proportional traceability.

---

## Phase 7: Polish & Cross-Cutting Concerns

- [X] T122 [P] Add OpenAPI 3.1 validation and frontend DTO drift checks in backend/tests/contract/test_openapi_document.py
- [X] T123 [P] Add canary-secret scans across logs, incidents, REST, ticket URLs, WebSocket events, reports, and snapshots in backend/tests/integration/security/test_secret_leakage.py
- [X] T124 [P] Add clean-install and upgrade migration tests for configuration, mining, alerts, and ticket schemas in backend/tests/integration/persistence/test_migrations.py
- [X] T125 Add lifecycle observability and report-counter reconciliation acceptance tests in backend/tests/integration/executions/test_observability.py
- [X] T126 Add opt-in external GitLab contract markers separate from deterministic suites in backend/tests/contract/test_external_gitlab.py
- [X] T127 Run and record all ten quickstart scenarios in specs/001-gitlab-repository-mining/quickstart.md
- [X] T128 Re-run all Constitution 2.0.0 gates and document any approved exception in specs/001-gitlab-repository-mining/plan.md
- [X] T129 Update operator setup, scheduling, key rotation, incident response, and WebSocket recovery guidance in README.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup**: No dependencies.
- **Foundation**: Depends on Setup; foundational tests T009-T011 precede implementations T012-T026, while shared types/contracts T013-T019 precede every story contract test.
- **US1**: Depends on Foundation; contract/unit/frontend tests T027-T031 precede models/migration T032-T038; persistence tests T039-T040 run after migration and before services/adapters T041-T054.
- **US2**: Depends on US1 configuration entities; unit/contract tests T055-T057 precede models/migration T058-T066; persistence, replacement-contract, and frontend tests T067-T075 run after migration and before services/adapters T076-T090.
- **US3**: Depends on US2 execution state; contract/frontend tests T091-T093 precede model/migration T094-T095; persistence/authentication tests T096-T097 run after migration and before services/adapters T098-T110.
- **US4**: Depends on US2 alerts/outcomes; tests T111-T114 precede services/adapters T115-T121.
- **Polish**: Depends on all stories selected for release.

### User Story Dependency Graph

```text
Setup -> Foundation -> US1 -> US2 -> US3
                              |
                              +-> US4
```

### Within Each User Story

1. Define shared types and interface contracts.
2. Write contract and unit tests and confirm intended failure.
3. Create models and apply migrations.
4. Write persistence-backed tests and confirm intended failure.
5. Implement domain/application services, then REST, WebSocket, and UI adapters.
6. Pass the independent story test.

### Parallel Opportunities

- Setup T003-T006; foundation T009-T011 and independent ports/fakes.
- US1 pre-migration tests T027-T031 and models T032-T037; post-migration tests T039-T040 can run together.
- US2 pre-migration tests T055-T057 and models T058-T065; post-migration tests T067-T075 can run together where paths differ.
- US3 pre-migration tests T091-T093; post-migration tests T096-T097 can run together.
- US4 tests T111-T114 and query implementations T115-T116.
- Polish T122-T124 after their corresponding stories.

## Parallel Examples

```text
US1: T027-T031 pre-migration tests; T032-T037 models; T039-T040 persistence tests
US2: T055-T057 pre-migration tests; T058-T065 models; T067-T075 post-migration tests
US3: T091-T093 contract/frontend tests; T096-T097 ticket persistence/authentication tests
US4: T111-T114 aggregation, contract, traceability, and frontend tests
```

## Implementation Strategy

### MVP First

1. Complete Setup and Foundation.
2. Complete US1 for secure configuration and allowed-user management.
3. Complete US2 for baseline and incremental author verification.
4. Validate US1+US2 before realtime monitoring.

US1 is independently demonstrable, but minimum product value requires US1+US2.

### Incremental Delivery

1. Protected configuration, scheduling, and incident lifecycle (US1).
2. Baseline, checkpoints, author verification, alerts, and isolation (US2).
3. Ticket-authenticated realtime monitoring (US3).
4. Reconciled reports and detailed unauthorized commits (US4).
5. Cross-cutting release hardening.

## Notes

- `[P]` means distinct paths and no unfinished dependency.
- UnauthorizedCommitAlert traceability uses only commit metadata consumed by the rule.
- The GitLab integration is read-only and metadata-only.
- No task introduces brokers, worker services, repository clones, repository mutation, automatic
  commits, or merge requests.

## Phase 8: Convergence

- [X] T130 Persist `ExecutionCommit` observations with `new|reused` provenance for every processed commit and reconcile report counters per FR-022/FR-035 in `backend/src/repository_miner/persistence/models.py` and `backend/src/repository_miner/reporting/application/queries.py`.
- [X] T131 Replace in-memory configuration, scope, and allowed-user mutations with persistent application services, including edit/enable/disable behavior required by FR-001/FR-023 in `backend/src/repository_miner/app.py` and `backend/src/repository_miner/configuration/application/`.
- [X] T132 Implement authenticated GitLab hierarchy discovery and effective group/subgroup/repository selection resolution required by FR-004/FR-005 in `backend/src/repository_miner/gitlab/application/hierarchy.py` and `backend/src/repository_miner/mining/application/persistent_runner.py`.
- [X] T133 Make connection-test call the GitLab gateway and persist scope only after successful validation, preserving invalidation on URL or credential changes per FR-003 in `backend/src/repository_miner/app.py` and `backend/src/repository_miner/gitlab/infrastructure/http_gateway.py`.
- [X] T134 Add immutable execution snapshots for effective configuration, repository scope, target branch, and allowed-user e-mails required by FR-012 in `backend/src/repository_miner/executions/application/start_execution.py` and `backend/src/repository_miner/persistence/models.py`.
- [X] T135 Enforce operator authorization for execution-scoped WebSocket tickets and return `403` for valid operators without access per FR-033/FR-034 in `backend/src/repository_miner/app.py` and `backend/src/repository_miner/authentication/`.
- [X] T136 Reconcile durable progress, event payloads, and report counters against persisted execution observations and repository outcomes per FR-024/FR-026 in `backend/src/repository_miner/reporting/application/queries.py` and `backend/src/repository_miner/executions/application/event_publisher.py`.
- [X] T137 Remove or isolate legacy in-memory mining and ticket paths so all production flows use persistent state and retain credential-security guarantees per FR-027 and Constitution II in `backend/src/repository_miner/app.py` and `backend/src/repository_miner/persistence/store.py`.

## Phase 9: Specification Alignment Increment

**Purpose**: Implement and verify the newly clarified history-recovery, scheduler-reconciliation,
canonical-counter, and commit-identity requirements. These tasks are intentionally pending until
implemented and validated.

### FR-036 — Divergent history and explicit baseline recovery

- [X] T138 [P] [US2] Add tests for missing checkpoint commit, removed branch, rewritten branch, and non-descendant branch history, asserting repository failure code `history_diverged`, unchanged checkpoint, no automatic baseline, and blocked incremental continuation in `backend/tests/integration/mining/test_history_divergence.py`
- [X] T139 [US2] Add `BaselineResetAudit` persistence model and migration with `configuration_id`, `repository_id`, `branch`, `previous_checkpoint_hash`, `new_baseline_hash`, `operator_id`, `reason`, and `created_at` in `backend/src/repository_miner/persistence/models.py` and `backend/migrations/versions/005_baseline_reset_audit.py`
- [X] T140 [US2] Extend the GitLab gateway and mining application to validate checkpoint reachability/ancestry before commit listing, translate divergence to `history_diverged`, and preserve the previous checkpoint in `backend/src/repository_miner/gitlab/application/ports.py` and `backend/src/repository_miner/mining/application/persistent_runner.py`
- [X] T141 [US2] Implement authenticated baseline-reset application service that validates current branch HEAD, persists `BaselineResetAudit` before updating the checkpoint, uses the current HEAD as the new baseline without retrospective processing, and never deletes historical verifications or alerts in `backend/src/repository_miner/mining/application/baseline_reset.py`
- [X] T142 [US2] Add authenticated baseline-reset REST route and `history_diverged` error contract with canonical `previous_checkpoint_hash` and `new_baseline_hash` fields in `backend/src/repository_miner/app.py` and `specs/001-gitlab-repository-mining/contracts/openapi.yaml`
- [X] T143 [P] [US2] Add integration and contract tests for authenticated reset, audit contents, operator rejection, checkpoint update ordering, preserved historical executions, preserved `CommitVerification` rows, and preserved `UnauthorizedCommitAlert` rows in `backend/tests/integration/mining/test_baseline_reset.py` and `backend/tests/contract/test_history_recovery_api.py`

### FR-037 — Scheduler reconciliation after downtime

- [X] T144 [US2] Formalize the single-active-scheduler invariant and implement startup reconciliation that loads persisted schedules, selects only the latest overdue occurrence per configuration, creates at most one recovery execution, and uses the durable occurrence identity to prevent duplicates in `backend/src/repository_miner/scheduling/infrastructure/scheduler.py`
- [X] T145 [P] [US2] Add scheduler reconciliation tests covering multiple restarts, multiple overdue occurrences, duplicate occurrence identity, disabled configuration, compromised credential, and already-active execution without checkpoint changes in `backend/tests/integration/scheduling/test_reconciliation.py`

### FR-022, FR-024, FR-026 — Idempotency and canonical counters

- [X] T146 [US2] Align persisted execution and repository progress models with canonical counters `repositories_total`, `repositories_completed`, `repositories_failed`, `commits_discovered`, `commits_verified`, `allowed_commits`, and `unauthorized_commits` in `backend/src/repository_miner/persistence/models.py` and `backend/src/repository_miner/reporting/application/queries.py`
- [X] T147 [P] [US3] Update OpenAPI, WebSocket event, report, and response contracts to require only the seven canonical counter names and the five canonical execution states in `specs/001-gitlab-repository-mining/contracts/openapi.yaml` and `specs/001-gitlab-repository-mining/contracts/websocket-events.md`
- [X] T148 [P] [US2] Add contract and integration tests proving canonical counters are persisted and exposed consistently through execution REST responses, reports, repository progress events, terminal events, and zero-commit executions in `backend/tests/contract/test_canonical_counters.py`
- [X] T149 [P] [US2] Add idempotency tests proving an existing `CommitVerification` performs no new author validation, creates no `UnauthorizedCommitAlert`, and does not increment `commits_verified`, `allowed_commits`, or `unauthorized_commits` in the later execution in `backend/tests/integration/mining/test_reused_verification_counters.py`
- [X] T150 [US4] Add report traceability tests proving `UnauthorizedCommitAlert` remains owned only by the original detection execution and is absent from later execution-scoped reports that reuse the verification in `backend/tests/integration/reporting/test_original_alert_ownership.py`

### Canonical commit terminology and cross-artifact alignment

- [X] T151 [P] [US2] Standardize commit identity terminology on `commit_hash` across application DTOs, persistence adapters, event payloads, examples, contract fixtures, and tests, remove legacy aliases, and verify with a repository-wide search in `backend/src`, `backend/tests`, `specs/001-gitlab-repository-mining/contracts`, and `specs/001-gitlab-repository-mining/quickstart.md`
- [X] T152 [P] [US4] Add contract tests for canonical execution states, checkpoint identity `(configuration_id, repository_id, branch)`, `CommitVerification` identity `(configuration_id, repository_id, branch, commit_hash)`, original alert ownership, and reused-commit behavior in `backend/tests/contract/test_cross_artifact_alignment.py`

### Phase 9 Dependencies

- T138-T143 must be completed in order after the existing checkpoint and authenticated-operator foundations; T143 depends on T139-T142.
- T144-T145 depend on the existing persistent schedule and execution-start services.
- T146-T150 depend on the existing persistence and reporting models; T148-T150 are test-first validation tasks.
- T151-T152 are cross-cutting contract tasks and must be completed before the next implementation increment is considered aligned.

## Phase 10: Convergence

- [X] T153 Resolve the frontend Vitest/esbuild `spawn EPERM` execution blocker and run the pending configuration, credential-replacement, live-execution, and report frontend suites (T031, T075, T093, and T114) without changing their required coverage (plan: frontend testing, partial/missing)

## Phase 11: Convergence
- [X] T154 [US2] Rename checkpoint fields and all persistence, migration, runner, baseline-reset, contract, and test references from `baseline_sha`/`last_processed_sha` to the canonical `baseline_hash`/`last_processed_hash` names required by FR-014 and data-model.md, without retaining aliases (plan: incremental checkpoints, partial)

