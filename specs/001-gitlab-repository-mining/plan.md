# Implementation Plan: GitLab Repository Author Monitoring

**Branch**: `001-gitlab-repository-mining` | **Date**: 2026-09-19 |
**Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-gitlab-repository-mining/spec.md`

## Summary

Build a modular web monolith that configures GitLab repository scope, schedules or manually starts
incremental executions, and detects commits whose author e-mail is not in the configuration's
allowed-user list. The React/TypeScript frontend uses Material UI. The FastAPI backend uses
SQLAlchemy, Alembic, and a relational database. A persistent in-process scheduler and local
execution dispatcher run without queues or brokers. REST and the database are authoritative;
WebSocket carries coarse progress notifications.

The MVP retrieves commit metadata only. It does not retrieve commit change content. GitLab access,
scheduling, persistence, dispatch, and realtime delivery remain behind narrow module boundaries.

## Technical Context

**Language/Version**: Python 3.13 backend; TypeScript 5.x on a supported Node.js LTS runtime

**Primary Dependencies**: FastAPI, Pydantic, SQLAlchemy 2.x, Alembic, relational database driver,
APScheduler, HTTP client, cryptography; React 19, Material UI, React Router, typed server-state query
client

**Storage**: PostgreSQL 16+ as the initial relational database; external encryption key or secret
store for GitLab credential encryption; no repository clones

**Testing**: pytest unit, integration, contract, and API tests; frontend component and user-flow
tests; deterministic fakes for GitLab, clock, dispatcher, authenticated operator, and event sink

**Target Platform**: Container-friendly Linux deployment; evergreen desktop browsers; one active
application/scheduler instance in the MVP

**Project Type**: Separate frontend and backend projects deployed as one logical modular monolith

**Performance Goals**: No quantitative throughput or latency target is set for the MVP until a
representative deployment defines GitLab latency, pagination volume, hardware, caching, and
benchmark conditions; progress events remain coarse and list endpoints use bounded pagination

**Constraints**: No microservices, Celery, RabbitMQ, Kafka, broker, repository mutation, automatic
commit creation, or merge requests. No plaintext credentials. Compromised GitLab credentials stop
all subsequent GitLab calls immediately. GitLab API only. One active execution per configuration.
WebSocket loss does not affect processing; socket authentication uses only short-lived single-use
tickets issued through authenticated REST.

**Scale/Scope**: Trusted-operator MVP; daily, weekly, and monthly schedules; multiple repositories
per execution with isolated failures; commit metadata without change-content retrieval. Capacity
targets will be established from representative deployment measurements after the MVP.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked after Phase 1 design.*

| Principle | Design evidence | Gate |
|---|---|---|
| Architectural Simplicity | One modular monolith, one relational database, one in-process scheduler, no broker or worker service | PASS |
| Credential Security and Incident Response | Authenticated encryption, compromised-state guard before every GitLab call, authenticated preventive/incident replacement audit, immutable mining history, one-use socket tickets | PASS |
| End-to-End Traceability | `UnauthorizedCommitAlert` retains configuration, execution, repository, branch, commit hash, author, author e-mail, and commit date—the complete input provenance used by the deterministic rule | PASS |
| Incremental Mining | Checkpoint per configuration/repository/branch plus a durable verification ledger unique by configuration/repository/branch/commit; baseline on first execution; advancement only after successful repository processing | PASS |
| Integration Isolation | `GitLabGateway` translates a closed safe failure taxonomy; dispatcher, scheduler, repository, identity, and event ports isolate external concerns | PASS |
| Probabilistic-output safeguards | Not applicable because this feature uses deterministic author e-mail comparison only | PASS |
| Testability Without External Services | Author rules and mining orchestration use GitLab, clock, dispatcher, identity, and event fakes | PASS |
| Failure Isolation | Each repository run has independent state and failure; final execution status reconciles durable repository outcomes | PASS |
| Code Privacy and Data Minimization | No commit change content is requested; only required metadata is persisted | PASS |
| Execution Observability | Durable lifecycle, repository results, commit counters, alerts, failures, revisions, and structured events | PASS |

### Post-Design Re-check

The revised model and contracts contain only GitLab author-monitoring concepts and preserve
incremental checkpoints, the durable at-most-once verification ledger, credential containment,
isolated failures, REST authority, and operator-bound ticket-authenticated realtime updates.
`AuthenticatedOperatorProvider` keeps host authentication outside use cases while ensuring ticket
and incident audit operations fail closed without a validated identity. Preventive and
incident-driven credential replacements create authenticated audit records without changing mining
state. The GitLab adapter applies a closed, secret-safe failure taxonomy. `UnauthorizedCommitAlert`
records every metadata field used to produce the result: configuration, execution, repository,
branch, commit hash, author, author e-mail, and commit date. In accordance with Constitution 2.0.0,
its execution is always the original detection execution; later reuse creates no alert projection
or result count. Configuration responses expose only the current credential state, while replaced
references remain historical. The design does not request file or change-content data solely for
provenance. All constitution gates pass and no exception is required.

## Project Structure

### Documentation

```text
specs/001-gitlab-repository-mining/
|-- plan.md
|-- research.md
|-- data-model.md
|-- quickstart.md
|-- contracts/
|   |-- openapi.yaml
|   `-- websocket-events.md
`-- tasks.md
```

### Source Code

```text
backend/
|-- pyproject.toml
|-- alembic.ini
|-- migrations/
|-- src/repository_miner/
|   |-- app.py
|   |-- shared/
|   |-- authentication/
|   |-- configuration/
|   |-- gitlab/
|   |-- repositories/
|   |-- mining/
|   |-- executions/
|   |-- scheduling/
|   |-- alerts/
|   |-- reporting/
|   `-- persistence/
|-- tests/
|   |-- unit/
|   |-- integration/
|   `-- contract/
`-- scripts/

frontend/
|-- package.json
|-- tsconfig.json
|-- src/
|   |-- app/
|   |-- shared/
|   |-- configurations/
|   |-- repositories/
|   |-- executions/
|   |-- alerts/
|   `-- reporting/
|-- tests/
`-- public/

deploy/
|-- compose.yaml
`-- env.example
```

**Structure Decision**: Two code projects share one deployment boundary. Backend modules are
vertical business capabilities with domain/application/infrastructure layers. The frontend mirrors
product capabilities. Scheduler, executor, and WebSocket broadcaster remain in the backend process.

## Key Design Decisions

### Module boundaries

- HTTP routes validate transport data and host-provided identity before invoking application use
  cases; they contain no mining or authentication-provider rule.
- The application depends on an `AuthenticatedOperatorProvider` port that returns a validated,
  stable operator identity supplied by the hosting environment. Use cases never read cookies,
  headers, proxy claims, or identity-provider SDK objects directly.
- The domain depends on `GitLabGateway`, clock, dispatcher, and event ports.
- The GitLab adapter owns pagination, branch and commit metadata requests, and credential status
  checks immediately before each external call. It maps timeout, unavailability, rate limiting,
  unexpected HTTP status, and malformed payload into stable application errors with retry metadata
  when applicable; external bodies, tokens, and secrets never enter user-facing errors or logs.
- No module requests or stores commit change content.

### Configuration and credentials

- Allowed users are stored as unique normalized e-mail addresses per configuration; normalization
  trims surrounding whitespace and applies case-insensitive comparison.
- The original commit author and e-mail remain unchanged for traceability.
- Credential plaintext is authenticated-encrypted and decrypted only inside the GitLab adapter.
- Marking a credential compromised blocks connection tests, new executions, and the next GitLab
  call of any active execution. Completed repository work and checkpoints remain durable.
- An authenticated operator may replace an active credential preventively or replace a compromised
  credential as required remediation. Replacement creates a new encrypted reference and audit
  record; the old reference becomes `replaced` and is never reactivated.
- A compromised credential cannot be used again and the configuration remains blocked until a new
  active reference is installed. Provider-side invalidation remains an operator action.
- Credential references are configuration inputs, not incremental-state identities. Replacement
  never changes checkpoints, execution history, completed verifications, or existing alerts.
- The MVP has no account registration, password, session, or account-management capability.
- The concrete HTTP authentication adapter validates the hosting environment's principal and maps
  it to `AuthenticatedOperator`. Missing or invalid identity fails with `401`; a valid operator
  without access to the target resource fails with `403`.
- WebSocket-ticket issuance and credential-incident/replacement audit require a valid operator.
  Incident records store the stable operator identifier, never authentication credentials or raw
  host claims. The adapter may later be replaced without changing application use cases.
- The MVP owns no operator registration, login, password, session issuance, account lifecycle, or
  role-management capability.
- A successful GitLab connection validation is persisted as configuration state tied to the
  current GitLab URL and credential reference. Saving repository selection or target branch is
  rejected until that exact connection state is valid; changing the URL or credential invalidates
  the validation until it succeeds again.

### Execution and scheduling

- A persistent schedule stores recurrence, timezone, local time, and `next_run_at`.
- Monthly occurrences use the month's last calendar day when the configured day does not exist.
- Disabled configurations never create scheduled executions but remain manually executable.
- Manual and scheduled starts share one transactional use case.
- A configuration row lock plus a partial unique index over `pending` and `running` prevents overlap.
- Due occurrences are unique by configuration and due time. A due occurrence competing with an
  active execution is recorded as skipped.
- The MVP assumes one active scheduler instance. The scheduler reloads durable schedules at startup
  and runs within the application process.
- Startup reconciliation identifies overdue occurrences, selects only the most recent overdue
  occurrence per configuration, and creates at most one recovery execution. It never creates one
  execution per missed occurrence. Existing `ScheduleOccurrence` identity prevents duplicates.
- Disabled configurations, compromised credentials, and configurations with an active execution do
  not create recovery executions; the occurrence is recorded with a safe skipped reason.

### Incremental mining flow

1. Load the immutable execution configuration snapshot.
2. Confirm the GitLab credential is active before any external call.
3. Resolve selections into an immutable repository snapshot.
4. For a new configuration/repository/branch combination, read current HEAD and persist it as the
   baseline without processing history.
5. For an existing checkpoint, first validate that the stored `last_processed_hash` is still
   reachable from the configured branch. If the branch is deleted, the `commit_hash` is missing, or
   the current history diverges,
   record a repository-scoped `history_diverged` failure, preserve the checkpoint, and do not request
   commits or create a replacement baseline.
6. For a valid checkpoint, request commit metadata after the stored `last_processed_hash`.
7. For each discovered commit, look up the durable verification ledger by configuration,
   repository, branch, and `commit_hash`. Reuse an existing completed result without validating the
   author again.
8. For a commit without a ledger entry, compare its normalized author e-mail to the snapshotted
   allowed list and atomically persist the completed verification plus its single alert, when
   unauthorized. This per-commit transaction remains durable even if the repository later fails.
9. Link every discovered commit to the current repository run, marking whether its result was newly
   produced or reused. Only `new` rows increase `commits_verified`, `allowed_commits`, or
   `unauthorized_commits`; `reused` rows prove idempotent recognition but add no verification or
   alert count to the current execution.
10. After the repository completes successfully, atomically advance its checkpoint to the observed
   HEAD. A failed or interrupted repository does not advance its checkpoint.

Consequently, a stale checkpoint after partial repository failure may rediscover commits, but the
unique verification ledger makes author validation at-most-once for the same configuration,
repository, branch, and `commit_hash`. Only commits lacking a completed ledger entry are validated
on retry.

The GitLab gateway contract exposes branch reachability/ancestry, branch HEAD, and commit metadata
only. A missing `last_processed_hash` after history rewrite is a repository-scoped failure, never an
implicit rebaseline.

History recovery is a separate authenticated operator use case. It explicitly redefines the baseline
for one configuration/repository/branch combination and persists a `BaselineResetAudit` containing
`configuration_id`, `repository_id`, `branch`, `previous_checkpoint_hash`, `new_baseline_hash`,
`operator_id`, `reason`, and `created_at`. The audit is written before the checkpoint update and never
deletes executions, verifications, alerts, or prior checkpoints.

### Terminal state reconciliation

- Execution states are only `pending`, `running`, `completed`, `partially_completed`, and `failed`.
- Manual cancellation is not supported.
- `completed`: every repository run completes successfully, including a run with zero new commits.
- `partially_completed`: at least one repository completes and at least one fails.
- `failed`: no repository completes successfully or a shared prerequisite prevents all work.
- If credential compromise occurs during a run, no new GitLab call starts. The above rules use
  repository outcomes already persisted, and the failure reason appears in the report.

### Realtime and reporting

- REST and relational state are authoritative. WebSocket is best-effort notification only.
- Authenticated REST resolves the operator through `AuthenticatedOperatorProvider`, verifies access
  to the execution, and issues a 256-bit opaque ticket bound to that operator and execution. It
  expires after 60 seconds, is stored only as an HMAC-SHA-256 digest, and is consumed atomically
  once. Every reconnect requires a fresh authenticated REST request and ticket.
- During the WebSocket upgrade, the host authentication adapter supplies the validated operator
  identity independently of the ticket value. Consumption atomically requires an unexpired unused
  ticket whose `operator_id` equals that operator and whose `execution_id` equals the route.
- Invalid, expired, consumed, wrong-operator, or wrong-execution tickets receive a uniform
  rejection. GitLab credentials are never WebSocket credentials, and no persistent credential is
  placed in the WebSocket URL or subprotocol.
- Events are `execution.started`, `repository.started`, `repository.progress`,
  `unauthorized_commit.detected`, `repository.completed`, `repository.failed`,
  `execution.completed`, `execution.partially_completed`, and `execution.failed`.
- Events contain identifiers, states, counters, and revision only—never GitLab credentials.
- REST resynchronization occurs at page load, after socket connection, on revision gaps, reconnect,
  and terminal events.
- Report counters are `repositories_total`, `repositories_completed`, `repositories_failed`,
  `commits_discovered`, `commits_verified`, `allowed_commits`, and `unauthorized_commits`, plus terminal state and
  detailed unauthorized commits. The three verification/result counters include only work newly
  completed by that execution; reused verification observations affect none of them.
- `UnauthorizedCommitAlert.execution_id` is always the original detection execution. Execution-
  scoped report and alert queries include only alerts whose detection execution is the requested
  execution. No `reporting_execution_id` or duplicate alert projection is introduced; historical
  queries resolve the original alert through that original execution.

## Complexity Tracking

No constitution violation requires justification. Module ports exist only for mandated external
integration, deterministic tests, scheduling, and realtime delivery; all remain in-process. No
file-level data is collected because it does not participate in the author e-mail rule.
### Constitution gate review

Reviewed against Constitution 2.0.0 on 2026-09-19. Gates for architectural simplicity, credential
security, metadata traceability, incremental processing, integration isolation, testability,
failure isolation, data minimization, and observability are satisfied by the current MVP artifacts.
AI-specific principles remain inactive because semantic analysis is outside the current MVP scope.
No exception was approved.
