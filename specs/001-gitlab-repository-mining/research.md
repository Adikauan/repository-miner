# Phase 0 Research: GitLab Repository Author Monitoring

## Decision 1: Modular monolith with local dispatch

**Decision**: Deploy React and FastAPI as one logical application with one relational database,
an in-process scheduler, and a local execution dispatcher.

**Rationale**: This is the smallest architecture that meets durable scheduling, incremental mining,
and realtime monitoring needs while preserving module boundaries.

**Alternatives considered**: Workers, brokers, and microservices add operational cost without an
MVP requirement; synchronous request-bound mining would couple long work to client connections.

## Decision 2: Metadata-only GitLab integration

**Decision**: The GitLab gateway exposes connection validation, hierarchy traversal, branch HEAD,
and commit metadata pagination. It has no operation for commit change content or repository mutation.

**Rationale**: Author validation requires only commit metadata. Omitting change-content retrieval
reduces API load, privacy exposure, storage, and implementation complexity.

**Alternatives considered**: Local clones and change-content endpoints provide data that the MVP
never uses.

## Decision 3: E-mail identity normalization

**Decision**: Normalize configured and commit e-mail values by trimming surrounding whitespace and
using case-insensitive comparison. A missing or empty commit e-mail is unauthorized. Preserve the
original commit values for audit.

**Rationale**: It provides deterministic matching without inventing name or alias heuristics.

**Alternatives considered**: Display-name matching is ambiguous; provider user IDs are not
consistently present in commit metadata.

## Decision 4: Repository-scoped checkpoint advancement

**Decision**: Store one checkpoint per configuration, repository, and branch, and a durable commit
verification ledger unique by configuration, repository, branch, and commit SHA. First execution
persists current HEAD as baseline. Later runs enumerate commits after the checkpoint, reuse any
completed ledger entry, durably commit each new verification, and advance the checkpoint to observed
HEAD only after the whole repository succeeds.

**Rationale**: A failed or interrupted repository is retried without losing commits. Although its
checkpoint remains unchanged, already persisted commit verifications are recognized and never
evaluated again, while successful repositories remain incremental and independent.

**Alternatives considered**: Execution-wide checkpoints couple repositories; advancing before
durable verification creates gaps; reprocessing the full branch duplicates alerts.

## Decision 5: Canonical execution reconciliation

**Decision**: Use `pending`, `running`, `completed`, `partially_completed`, and `failed` only.
Every repository success yields `completed`; mixed outcomes yield `partially_completed`; zero
successful repositories yields `failed`. A successful no-new-commit run is `completed`.

**Rationale**: Terminal state is derived deterministically from repository outcomes. Manual
cancellation is outside the MVP.

**Alternatives considered**: A separate no-change state duplicates counters; treating any single
failure as global failure hides successful work.

## Decision 6: Persistent in-process scheduling

**Decision**: Persist recurrence, timezone, next due time, and occurrence uniqueness. Reconcile at
startup in one scheduler instance. For nonexistent monthly days, use the last calendar day.

**Rationale**: Scheduling survives restarts without a broker and has deterministic calendar rules.

**Alternatives considered**: Memory-only schedules are lost on restart; skipping short months
creates surprising gaps; restricting schedules to days 1–28 reduces product capability.

## Decision 7: Credential lifecycle and immediate containment

**Decision**: Authenticated-encrypt GitLab credentials with an external key. An active reference may
be replaced preventively; a compromised reference must be replaced before further use. Every GitLab
call checks active status immediately before decrypt/use. Replacement always creates a new reference
and an authenticated audit record, marks the old reference `replaced`, and never changes checkpoints,
execution history, completed verifications, or alerts. Compromise creates a secret-free incident and
prevents further calls, including inside active executions; completed work remains durable.

**Rationale**: Immediate local containment is enforceable independently of GitLab token-rotation
capabilities and satisfies the constitution without discarding valid completed work.

**Alternatives considered**: Allowing active runs to continue violates containment; discarding
completed data harms auditability; automatic GitLab rotation is not generally portable.

## Decision 7A: Closed GitLab failure taxonomy

**Decision**: `GitLabGateway` translates timeout, service unavailability, rate limit, unexpected
HTTP status, and malformed payload into stable application-level error codes. Errors may carry safe
retry guidance such as retryability or a sanitized retry-after time, but never the token, request
authorization data, raw external response body, or other secrets. Successful responses also pass
strict schema validation before entering application logic.

**Rationale**: Callers can make deterministic repository-scoped decisions without coupling to the
HTTP client or exposing provider data through diagnostics.

**Alternatives considered**: Propagating raw client exceptions leaks integration details and may
leak secrets; treating every failure identically loses useful retry and operator guidance; accepting
unvalidated payloads moves provider corruption into business rules.

## Decision 8: Durable REST authority with WebSocket notifications

**Decision**: REST returns authoritative snapshots. WebSocket emits coarse versioned events with a
monotonic execution revision. Clients refetch on initial connection, gaps, reconnect, and terminal
events.

**Rationale**: Mining continues independently of browsers and reconnection remains deterministic.

**Alternatives considered**: WebSocket-only state cannot guarantee recovery; polling alone does not
meet the live-monitoring requirement; a broker is unnecessary in a single process.

## Decision 9: Single-use WebSocket tickets

**Decision**: Authenticated REST issues a 256-bit opaque ticket bound to operator and execution,
valid for 60 seconds. Persist only its HMAC-SHA-256 digest using an external pepper. Atomically
consume it on the first valid handshake and uniformly reject invalid, expired, used, or mismatched
tickets.

**Rationale**: This limits replay and prevents persistent credentials from entering WebSocket URLs
or protocols.

**Alternatives considered**: GitLab credentials are prohibited; reusable bearer tickets expand
replay risk; memory-only tickets do not coordinate restart-safe validation.

## Decision 10: Relational source-of-truth counters

**Decision**: Derive final report counts from durable repository and execution-commit rows, then
store a reconciled terminal snapshot. Counters are repositories processed/failed, commits
discovered/verified, allowed commits, and unauthorized commits.

**Rationale**: Durable rows prevent progress-event loss or duplicate delivery from corrupting
reports.

**Alternatives considered**: Increment-only in-memory counters drift after retries or restarts;
WebSocket events are intentionally not a durable ledger.

## Decision 11: Host-provided operator identity behind an application port

**Decision**: The MVP does not own operator accounts. An `AuthenticatedOperatorProvider`
application port returns a validated `AuthenticatedOperator` with a stable operator identifier.
The HTTP adapter validates and translates the host environment's principal before any
identity-dependent use case runs. Missing or invalid identity returns `401`; insufficient resource
authorization returns `403`. WebSocket-ticket issuance and credential-incident/replacement audit
require this identity.

**Rationale**: Use cases need a trustworthy actor for authorization and audit, but they do not need
to know whether the host uses a session cookie, reverse-proxy assertion, OIDC, or another mechanism.
This preserves replaceability without adding account management to the MVP.

**Alternatives considered**: Local account management expands scope; reading cookies or identity
provider objects inside use cases couples business logic to transport; accepting a caller-supplied
operator ID permits spoofing.

## Decision 12: Operator-bound realtime authorization

**Decision**: Ticket issuance takes the validated operator identity from
`AuthenticatedOperatorProvider`, confirms access to the requested execution, and persists only the
operator's stable ID with the ticket digest and execution ID. During upgrade, the host adapter
supplies the validated operator independently of the ticket; atomic consumption requires that ID
and the route execution to match the ticket row, plus unused and unexpired state. Reconnect always
requires a fresh authenticated REST request and ticket.

**Rationale**: Binding both execution and operator prevents a ticket issued for one observer or
execution from authorizing another while keeping persistent credentials out of the WebSocket.

**Alternatives considered**: Execution-only tickets are transferable; reusable tickets increase
replay risk; passing the host session or GitLab token in the WebSocket URL exposes persistent
credentials.

## Decision 13: Execution-local work counters and original alert ownership

**Decision**: `ExecutionCommit.verification_source` distinguishes `new` from `reused`. Only `new`
observations contribute to `commits_verified`, `allowed_commits`, and `unauthorized_commits` for the
current execution. A reused unauthorized result creates no alert and is excluded from that
execution's alert projection. `UnauthorizedCommitAlert.execution_id` remains the original detection
execution; no `reporting_execution_id` exists.

**Rationale**: Reports describe work actually performed during their execution while the durable
verification ledger still prevents repeated validation. Alert provenance remains singular and
historically accurate.

**Alternatives considered**: Counting reused rows as verified misstates work; copying an alert into
later reports suggests a second detection; adding `reporting_execution_id` creates two competing
execution identities for one alert.

## Decision 14: Connection validation gates scope persistence

**Decision**: Store successful connection-validation state against the exact configuration,
GitLab URL, and active credential reference. Repository selection and target-branch persistence
require that state. Changing the URL or credential invalidates it until validation succeeds again.

**Rationale**: A saved mining scope must be derived from the connection that will actually be used,
not stale or unvalidated provider state.

**Alternatives considered**: A process-memory flag is lost on restart; validation detached from URL
and credential can become stale; allowing scope persistence first violates the product precondition.
