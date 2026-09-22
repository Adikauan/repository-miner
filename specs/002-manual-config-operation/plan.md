# Implementation Plan: Manual Configuration Operation and Editing

**Branch**: `002-manual-config-operation` | **Date**: 2026-09-20 | **Spec**: [spec.md](./spec.md)

## Summary

Extend the existing Repository Miner configuration experience so an authenticated operator can
read and edit one persisted mining configuration and start a manual execution from that same
context. The feature reuses the existing configuration, credential, scope, scheduling, execution,
checkpoint, alert, REST snapshot, temporary-ticket, and realtime-update contracts. No second
mining pipeline or duplicate history is introduced.

## Technical Context

**Language/Version**: Python 3.13 backend; TypeScript 5.x frontend on the existing supported Node.js runtime

**Primary Dependencies**: Existing FastAPI/Pydantic/SQLAlchemy/Alembic backend and React/Material UI frontend; no new runtime dependency required

**Storage**: Existing relational persistence and migrations; no new durable store required

**Testing**: pytest unit/integration/contract tests and existing frontend build/component tests, using GitLab, clock, operator, dispatcher, and event fakes

**Target Platform**: Existing container-friendly web deployment with one active scheduler instance

**Project Type**: Modular web monolith with separate backend and frontend projects

**Performance Goals**: No new quantitative target; use existing bounded REST pagination and current execution behavior

**Constraints**: Preserve existing contracts and canonical states/counters; never return plaintext credentials; no diff/content retrieval; no duplicate execution or history; manual execution remains available for disabled configurations but not compromised credentials

**Scale/Scope**: One configuration per edit flow, multiple selected repositories, existing MVP scheduling and incremental-processing limits

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked after Phase 1 design.*

| Principle | Design evidence | Gate |
|---|---|---|
| Architectural Simplicity | Reuses the existing modular monolith, persistence, runner, scheduler, and realtime publisher; no new service or broker | PASS |
| Credential Security and Incident Response | Configuration reads expose only credential status/reference; replacement and incident operations remain authenticated and secret-free; all tests use synthetic credentials only | PASS |
| End-to-End Traceability | Editing does not mutate checkpoints, verifications, alerts, executions, or audit records; manual runs retain existing execution and alert provenance | PASS |
| Incremental Mining | Scope/branch edits reuse the existing configuration/repository/branch checkpoint identity and baseline rules | PASS |
| Integration Isolation | Connection validation and GitLab tree loading continue through the existing gateway; use cases do not depend on HTTP clients | PASS |
| Probabilistic AI Findings | Not applicable: this feature does not add semantic or AI analysis | PASS |
| Testability Without External Services | Use existing fakes and add deterministic tests for edit, validation, concurrency, and manual-start rules | PASS |
| Failure Isolation | Manual execution delegates to the existing runner, preserving per-repository failure isolation and terminal-state reconciliation | PASS |
| Code Privacy and Data Minimization | No source content, diffs, or credentials are returned or requested by this feature | PASS |
| Execution Observability | Manual executions use existing durable snapshots, canonical counters, lifecycle events, and reports | PASS |

### Post-Design Re-check

The design adds no new infrastructure, preserves all existing domain identities and terminal states,
and keeps credential values write-only. Configuration updates are versioned/transactional, while
historical mining records remain append-only. Manual execution is a thin application entry point
over the existing `MiningExecution`/`PersistentMiningRunner` flow. All gates pass; no exception is
required.

## Phase 0: Research Decisions

See [research.md](./research.md). Existing project contracts and implementation were inspected;
no unresolved technical unknowns remain.

## Project Structure

```text
specs/002-manual-config-operation/
|-- plan.md
|-- research.md
|-- data-model.md
|-- quickstart.md
|-- contracts/
|   `-- openapi.yaml
`-- tasks.md                 # generated later by $speckit-tasks

backend/src/repository_miner/
|-- configuration/
|   |-- api/router.py
|   |-- application/service.py
|   `-- infrastructure/*
|-- executions/application/start_execution.py
|-- mining/application/persistent_runner.py
|-- scheduling/*
|-- persistence/*
`-- authentication/*

frontend/src/
|-- configurations/
|   |-- api.ts
|   |-- ConfigurationEditor.tsx
|   `-- ConfigurationListPage.tsx
|-- executions/*
`-- app/routes.tsx
```

**Structure Decision**: Extend the existing configuration API/application module and existing
configuration editor/list routes. Use the current execution start service and monitoring pages;
do not duplicate runner, scheduler, WebSocket, or persistence logic.

## Design Decisions

### Configuration read and update

- Add/complete a configuration detail projection that includes all non-sensitive persisted fields,
  current credential status, connection-validation status, scope, allowed e-mails, and schedule.
- Restrict `PATCH /configurations/{configurationId}` to basic fields only: name, timezone, and
  enabled status. It MUST NOT write scope, repositories, branch, allowed users, schedule, or
  credentials.
- Keep the dedicated repository-tree, branch-loading, scope, allowed-user, schedule, connection-test,
  and credential replacement operations as the canonical paths for loading or persisting those data
  groups. The single editor screen orchestrates those operations rather than sending all fields
  through PATCH.
- Preserve the existing configuration identity; do not create a replacement row.
- If URL, credential reference, or connection identity changes, clear the validation marker before
  saving dependent scope/branch data. A replacement token is write-only; omission keeps the current
  credential.
- Any dependent operation attempted before successful revalidation returns the existing conflict
  response with functional code `connection_not_validated`.
- Use short transactions and optimistic/version checks where the existing model supports them.

### Scope and incremental history

- Persist scope changes only after the current GitLab connection is successfully validated.
- Keep removed repository selections and old branches' checkpoints, verifications, alerts, and
  executions; only exclude them from future selection resolution.
- New configuration/repository/branch combinations enter the existing baseline path. No checkpoint
  is copied from another branch or repository.
- Allowed-user changes replace the normalized e-mail set for future checks only. Existing
  `CommitVerification` and `UnauthorizedCommitAlert` rows are immutable and are never replayed.

### Manual execution

- Expose a manual-start operation that loads and validates the persisted configuration, checks an
  active credential and active-execution uniqueness, then calls `start_persistent_execution`.
- Disabled status affects scheduling only; compromised credentials and an active execution reject
  the request without creating `MiningExecution`.
- Return the created `execution_id` and preserve the existing snapshot, ticket, REST, WebSocket,
  terminal-state, and canonical-counter contracts.

### Frontend behavior

- Load configuration detail before rendering the editor and distinguish write-only credentials from
  ordinary fields.
- Save edits through the existing REST operations and display safe validation/conflict/upstream
  errors.
- Use PATCH only for basic fields and invoke the dedicated repository-tree, branch-loading, scope,
  branch, allowed-user, schedule, connection-validation, and credential-replacement endpoints.
- Provide a manual-run action that navigates to the existing execution detail flow using the returned
  identifier; reconnection remains snapshot-via-REST followed by a new ticket.

## Complexity Tracking

No constitution violations or additional complexity require justification.

## Contract and Test Rules

- Contract-first coverage MUST assert that dependent updates are rejected with HTTP conflict and
  `connection_not_validated` after a URL or credential change invalidates validation.
- Contract-first coverage MUST reject PATCH payloads containing scope, repositories, branch,
  allowed users, schedule, or credential fields; `ConfigurationUpdate` is closed to additional
  properties.
- Contract-first coverage MUST cover connection-dependent group, subgroup, repository, branch,
  scope, and repository-selection operations with the same conflict code when validation is absent.
- Test fixtures MUST use only synthetic tokens, sentinel values, or fictitious non-sensitive
  secrets. Tests MUST assert that no synthetic value appears in responses, logs, error messages, or
  snapshots.
