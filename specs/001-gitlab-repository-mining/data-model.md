# Data Model: GitLab Repository Author Monitoring

## Conventions

- Application-generated UUID primary keys.
- Timezone-aware UTC timestamps; schedules also retain an IANA timezone.
- Mutable operator-owned rows use `created_at`, `updated_at`, and optimistic `version` where needed.
- GitLab credential plaintext is never serialized or stored unencrypted.
- Execution snapshots are immutable and contain no readable credential.
- Enumerations are domain values rather than database-specific types.

## Configuration aggregate

### MonitoringConfiguration

| Field | Type | Rules |
|---|---|---|
| id | UUID | Primary key |
| name | string | Required, 1–120 characters |
| gitlab_base_url | URL | HTTPS outside local development |
| gitlab_credential_id | UUID | Required active CredentialReference |
| target_branch | string | Required; defaults to `QA` |
| timezone | IANA timezone | Required |
| enabled | boolean | Controls automatic scheduling only |
| version | integer | Increments on edit |
| connection_validated_at | timestamp/null | Latest successful validation |
| validated_gitlab_base_url | URL/null | Must equal current URL for scope persistence |
| validated_credential_id | UUID/null | Must equal current credential reference for scope persistence |

Relationships: one schedule; many selection rules, allowed users, checkpoints, executions,
credential incidents, and credential replacements through its credential references.

Repository selection and target-branch persistence require non-null validation fields matching the
configuration's current URL and credential reference. Changing either value clears validation.
`credential_status` exposed for a configuration is derived from its currently linked reference and
is therefore only `active` or `compromised`; `replaced` exists only on historical references.

### CredentialReference

| Field | Type | Rules |
|---|---|---|
| id | UUID | Primary key |
| kind | enum | `gitlab_token` only in the MVP |
| ciphertext | bytes | Authenticated encrypted value; never serialized |
| key_version | string | External encryption-key identifier |
| fingerprint | string | Non-reversible operational identifier |
| status | enum | `active`, `compromised`, `replaced` |
| compromised_at | timestamp/null | Required when compromised |
| replaced_by_id | UUID/null | Replacement link; old reference never reactivated |
| created_at/last_rotated_at | timestamp | Required |

Only `active` credentials may be decrypted for a GitLab call. Status is checked immediately before
each external call, including calls made by an already-running execution. An active or compromised
reference may transition to `replaced`; a compromised reference cannot transition back to `active`.
The configuration points to the new active reference without changing mining or execution state.

### CredentialIncident

| Field | Type | Rules |
|---|---|---|
| id | UUID | Primary key |
| credential_id | UUID | Required compromised reference |
| status | enum | `open`, `replacement_recorded`, `closed` |
| suspected_at | timestamp | Required |
| suspected_by | string/UUID | Authenticated operator identity |
| safe_reason | string | Required; contains no secret |
| operator_notified_at | timestamp | Required |
| replacement_credential_id | UUID/null | New reference after replacement |
| replacement_recorded_at | timestamp/null | Audit timestamp |
| replacement_recorded_by | string/UUID/null | Stable authenticated operator identity |

Creation and replacement require an `AuthenticatedOperator` obtained from the host environment
through `AuthenticatedOperatorProvider`. `suspected_by` and the corresponding replacement audit
actor store only the stable operator identifier; no session credential or raw identity claim is
persisted.

### CredentialReplacement

| Field | Type | Rules |
|---|---|---|
| id | UUID | Primary key |
| configuration_id | UUID | Required audit scope |
| previous_credential_id | UUID | Required active or compromised reference |
| replacement_credential_id | UUID | Required new active reference |
| reason | enum | `preventive`, `compromise_remediation` |
| incident_id | UUID/null | Required only for compromise remediation |
| replaced_by | string/UUID | Stable authenticated operator identity |
| replaced_at | timestamp | Required |

Unique: `previous_credential_id`; the same credential cannot be replaced twice. Replacement is
atomic with updating the configuration's active credential reference. It has no relationship that
cascades to `IncrementalCheckpoint`, `Execution`, `CommitVerification`, or
`UnauthorizedCommitAlert`; those records remain unchanged.

### RepositorySelectionRule

Fields: `id`, `configuration_id`, kind (`group`, `subgroup`, `repository`), GitLab `external_id`,
display/audit `path`, and mode (`include`, `exclude`). Unique:
`(configuration_id, kind, external_id)`.

### AllowedUser

| Field | Type | Rules |
|---|---|---|
| id | UUID | Primary key |
| configuration_id | UUID | Required |
| email_original | string | Required non-empty operator input |
| email_normalized | string | Trimmed and case-folded |
| created_at | timestamp | Required |

Unique: `(configuration_id, email_normalized)`.

### Schedule

| Field | Type | Rules |
|---|---|---|
| configuration_id | UUID | Primary/foreign key |
| recurrence | enum | `daily`, `weekly`, `monthly` |
| local_time | time | Required |
| weekday | integer/null | 1–7, required only for weekly |
| day_of_month | integer/null | 1–31, required only for monthly |
| timezone | IANA timezone | Required |
| next_run_at | timestamp | Persisted UTC due time |

If `day_of_month` does not exist in a month, the occurrence uses that month's last calendar day.

## Repository and incremental state

### RepositoryIdentity

Stores GitLab instance identity, project external ID, full path, display name, web URL, and archived
flag. Unique: `(gitlab_base_url, external_id)`.

### IncrementalCheckpoint

| Field | Type | Rules |
|---|---|---|
| configuration_id | UUID | Composite unique key |
| repository_id | UUID | Composite unique key |
| branch | string | Composite unique key |
| baseline_hash | string | HEAD commit hash observed on first execution of the combination |
| last_processed_hash | string | HEAD commit hash through which commit verification completed durably |
| initialized_at | timestamp | Required |
| advanced_at | timestamp | Required |

State transitions:

1. New combination: read HEAD; store it in both SHA fields; process no history.
2. Existing combination: retrieve commit metadata after `last_processed_hash` through observed HEAD.
3. For every discovered commit, reuse an existing completed `CommitVerification` or persist a new
   verification and its alert atomically, then link it to the current execution repository.
4. Complete the repository run and atomically advance `last_processed_hash` to observed HEAD.
5. Failure or interruption: do not advance; already completed verification records remain durable
   and are reused on the next execution.
6. Missing historical SHA: record a repository failure; do not silently rebaseline.

When the stored SHA is not reachable from the configured branch, the failure code is
`history_diverged`; the previous checkpoint remains unchanged and no commit listing is requested.
An authenticated operator may explicitly redefine the baseline for this configuration, repository,
and branch. The reset records the previous checkpoint, new baseline, operator, timestamp, and reason
in an immutable audit record. It does not delete or mutate prior executions, verifications, alerts, or
the historical checkpoint record.

### BaselineResetAudit

| Field | Type | Rules |
|---|---|---|
| id | UUID | Primary key |
| configuration_id | UUID | Required |
| repository_id | UUID | Required |
| branch | string | Required |
| previous_checkpoint_hash | string/null | Preserved prior value |
| new_baseline_hash | string | Current branch commit hash selected by the operator |
| operator_id | string | Validated host-authenticated operator |
| reason | string | Required safe explanation |
| created_at | timestamp | Required |

The record is append-only and does not remove historical executions, verifications, alerts, or
checkpoints.

## Execution aggregate

### Execution

| Field | Type | Rules |
|---|---|---|
| id | UUID | Primary key |
| configuration_id | UUID | Required |
| trigger | enum | `manual`, `scheduled` |
| scheduled_for | timestamp/null | Required for scheduled trigger |
| status | enum | `pending`, `running`, `completed`, `partially_completed`, `failed` |
| configuration_snapshot | JSON | Immutable; includes normalized allowed e-mails and effective settings, no secret |
| revision | integer | Monotonic realtime ordering |
| started_at/finished_at | timestamp/null | Lifecycle |
| terminal_reason | string/null | Safe summary, including credential compromise when applicable |
| counters | JSON | Reconciled convenience snapshot, not source of truth; canonical keys are `repositories_total`, `repositories_completed`, `repositories_failed`, `commits_discovered`, `commits_verified`, `allowed_commits`, and `unauthorized_commits` |

State machine: `pending -> running -> completed | partially_completed | failed`.

Only `pending` and `running` are active. A partial unique constraint permits at most one active
execution per configuration. Terminal reconciliation:

- all repository runs successful → `completed`;
- at least one successful and one failed → `partially_completed`;
- no successful repository run → `failed`.

A successful execution with no new commits is `completed` with zero commit counters.

### ScheduleOccurrence

Fields: configuration, `due_at`, status (`started`, `skipped_active`, `skipped_disabled`,
`skipped_compromised`), optional execution reference, and safe reason. Startup reconciliation selects
only the latest overdue occurrence per configuration and creates at most one recovery execution.
Unique:
`(configuration_id, due_at)`.

### ExecutionRepository

| Field | Type | Rules |
|---|---|---|
| id | UUID | Primary key |
| execution_id | UUID | Required |
| repository_id | UUID | Required |
| branch | string | Immutable snapshot |
| status | enum | `pending`, `running`, `completed`, `failed` |
| observed_head_hash | string/null | HEAD commit hash used for baseline or successful advancement |
| baseline_created | boolean | True when no history was processed |
| commits_discovered | integer | Non-negative |
| commits_verified | integer | Non-negative; counts only `new` verifications in this execution |
| allowed_commits | integer | Non-negative; newly verified allowed commits only |
| unauthorized_commits | integer | Non-negative; newly verified unauthorized commits only |
| started_at/finished_at | timestamp/null | Lifecycle |
| failure_id | UUID/null | Set on failure |

Unique: `(execution_id, repository_id, branch)`.

### Commit

Repository-scoped immutable metadata: SHA, author name, original author e-mail, committed timestamp,
message, and optional source web URL. Unique: `(repository_id, sha)`. No file or change-content data
is stored.

### CommitVerification

| Field | Type | Rules |
|---|---|---|
| id | UUID | Primary key |
| configuration_id | UUID | Required; composite unique key |
| repository_id | UUID | Required; composite unique key |
| branch | string | Required; composite unique key |
| commit_hash | string | Required; composite unique key and reference to repository commit SHA |
| author_email_normalized | string/null | Trimmed and case-folded; null when missing |
| authorization_result | enum | `allowed`, `unauthorized` |
| first_verified_execution_id | UUID | Execution that completed the verification |
| verified_at | timestamp | Required; durable completion marker |

Unique: `(configuration_id, repository_id, branch, commit_hash)`. Concurrent attempts insert through
this constraint and reuse the committed winner. A completed row is immutable and means that author
validation must not run again for this identity.

### ExecutionCommit

| Field | Type | Rules |
|---|---|---|
| id | UUID | Primary key |
| execution_repository_id | UUID | Required |
| commit_id | UUID | Required |
| commit_verification_id | UUID | Required completed verification |
| verification_source | enum | `new`, `reused` |
| discovered_at | timestamp | Required |

Unique: `(execution_repository_id, commit_id)`. This execution-scoped observation supports progress
and reports without causing the commit's authorship to be verified again.

Only observations with `verification_source = new` contribute to the current execution's
`commits_verified`, `allowed_commits`, and `unauthorized_commits`. Reused observations contribute to
`commits_discovered` only.

### UnauthorizedCommitAlert

| Field | Type | Rules |
|---|---|---|
| id | UUID | Primary key |
| configuration_id | UUID | Required traceability |
| execution_id | UUID | Required original detection execution; immutable |
| execution_repository_id | UUID | Required traceability |
| commit_verification_id | UUID | Required; unique to ensure exactly one durable alert |
| repository_id | UUID | Required traceability |
| branch | string | Required |
| commit_hash | string | Required |
| author_name | string | Original commit value |
| author_email | string/null | Original commit value; null when missing |
| committed_at | timestamp | Commit date |
| detected_at | timestamp | Required |

No `reporting_execution_id` exists. Execution-scoped alert/report queries include an alert only
when this `execution_id` equals the requested execution. A reused verification never creates or
projects this alert into a later execution; general history reaches it through its original
detection execution.

### RepositoryFailure

Fields: execution, repository run, stage, stable code, safe reason, timestamp, whether independent
processing continued, and correlation ID. It contains no credential value.

## Realtime authentication

### AuthenticatedOperator (application value object, not persisted as an account)

| Field | Type | Rules |
|---|---|---|
| operator_id | string/UUID | Stable, non-empty identity validated by the host adapter |
| authorization_context | opaque value | Used only by the HTTP adapter/policy layer; never accepted from request payloads |

`AuthenticatedOperatorProvider` returns this value object or an authentication failure. It is an
application port, not a user repository: the MVP creates no operator table, password, registration,
login, or account-lifecycle model.

### WebSocketTicket

| Field | Type | Rules |
|---|---|---|
| id | UUID | Primary key |
| ticket_digest | string | Unique HMAC-SHA-256 digest using external pepper |
| operator_id | string/UUID | Authenticated operator binding |
| execution_id | UUID | Subscription binding |
| expires_at | timestamp | Issued time plus 60 seconds |
| consumed_at | timestamp/null | Set exactly once atomically |
| created_at | timestamp | Required |

Plaintext is returned once and never stored or logged. Acceptance requires an unexpired unused row,
the route execution matching `execution_id`, and the validated host operator supplied during the
upgrade matching `operator_id`; consumption and comparison are atomic.

`operator_id` comes only from a validated `AuthenticatedOperatorProvider`; it is never accepted in
the ticket request body. The MVP defines no local operator-account entity or credential.

## Reporting invariants

- `repositories_total`: repositories in the immutable execution scope.
- `repositories_completed`: repository runs that reached `completed`.
- `repositories_failed`: repository runs that reached `failed`.
- `commits_discovered`: unique ExecutionCommit rows in the execution.
- `commits_verified`: unique ExecutionCommit rows with `verification_source = new` linked to a
  completed `CommitVerification`.
- `allowed_commits`: newly verified execution commits whose linked result is `allowed`.
- `unauthorized_commits`: newly verified execution commits whose linked result is `unauthorized`.
- `commits_verified = allowed_commits + unauthorized_commits`.
- A completed repository may have `commits_discovered > commits_verified` when prior completed
  verifications were recognized and reused.
- Detailed unauthorized commits for an execution include only alerts whose immutable
  `execution_id` is that execution's ID.
- Every alert resolves to configuration, execution, repository, branch, commit, author, e-mail, and
  commit date.
- Final counters are derived from durable rows and reconciled before terminal state publication.

## Concurrency and indexing

- Partial unique index: one `pending` or `running` execution per configuration.
- Unique schedule occurrence by configuration and due time.
- Unique checkpoint by configuration, repository, and branch.
- Unique repository/SHA commit identity.
- Unique durable verification by configuration/repository/branch/commit hash.
- Unique execution-repository/commit observation.
- Unique alert per durable commit verification.
- Unique WebSocket ticket digest; index expiry for cleanup.
- Index execution/status/time, repository run/status, alert/execution/date, and normalized allowed
  e-mail lookup.
