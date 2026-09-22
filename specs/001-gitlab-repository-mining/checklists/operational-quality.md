# Operational Requirements Quality Checklist: GitLab Repository Mining

**Purpose**: Review the completeness, clarity, consistency, measurability, and scenario coverage
of the current MVP requirements for GitLab author monitoring.
**Created**: 2026-09-19
**Feature**: [spec.md](../spec.md)

**Review Ownership**: This checklist is a reviewer-owned requirements-quality artifact. Mark an
item `[x]` only when the reviewer confirms that the criterion is satisfied by the specification,
plan, contracts, or tests. A checked item does not mean implementation work is complete.

## GitLab Connection and Credential Protection

- [x] CHK001 Is the GitLab instance URL required and validated before it can be used?
- [x] CHK002 Are GitLab tokens protected at entry, persistence, use, responses, logs, diagnostics,
  reports, and realtime events?
- [x] CHK003 Are encryption keys and other protection material kept outside persisted credential
  ciphertext and source-controlled configuration?
- [x] CHK004 Is a compromised credential blocked from all new GitLab operations?
- [x] CHK005 Does suspected exposure create an auditable incident without recording the secret
  value and inform the operator about external invalidation or rotation?
- [x] CHK006 Is preventive replacement of an active credential supported?
- [x] CHK007 Is replacement mandatory before a compromised credential can be used again?
- [x] CHK008 Does replacement preserve checkpoints, execution history, commit verifications, and
  UnauthorizedCommitAlerts?
- [x] CHK009 Are credential incident and replacement audits attributed to a valid authenticated
  operator without exposing the credential?

## Connection Validation and Mining Scope

- [x] CHK010 Is persistence of groups, subgroups, repositories, and target branch rejected until
  the exact current GitLab URL and credential have been validated successfully?
- [x] CHK011 Is a previous connection validation invalidated when the GitLab URL or linked
  credential changes?
- [x] CHK012 Are groups, nested subgroups, and repositories discovered with their hierarchy
  preserved?
- [x] CHK013 Can an operator select a complete group, subgroup, or individual repository?
- [x] CHK014 Are inherited selections and explicit exclusions represented consistently?
- [x] CHK015 Is the target branch configurable and defaulted to `QA` when first persisted?
- [x] CHK016 Are allowed-user e-mails stored with both original display value and normalized
  comparison value?
- [x] CHK017 Are duplicate allowed e-mails rejected after trimming and case normalization?

## Baseline, Checkpoints, and Idempotent Verification

- [x] CHK018 Is the baseline moment defined consistently for the first execution and every new
  configuration/repository/branch combination?
- [x] CHK019 Are commits before the baseline excluded from verification?
- [x] CHK020 Is the checkpoint identity unique per configuration, repository, and branch?
- [x] CHK021 Is every commit verification durably identified by configuration, repository, branch,
  and commit hash?
- [x] CHK022 Is author verification performed at most once for that identity?
- [x] CHK023 If a repository fails after some commits are persisted, does its checkpoint remain
  unchanged?
- [x] CHK024 Does a later execution reuse durable verifications and process only commits without a
  completed verification?
- [x] CHK025 Does reuse avoid duplicate author validation and duplicate UnauthorizedCommitAlerts?
- [x] CHK026 Do configuration changes apply only to future commits while preserving prior state?
- [ ] CHK027 Are branch history rewrites, missing checkpoint commits, and deleted branches handled
  as explicit repository outcomes rather than silent re-baselines?

## Allowed-User Rule

- [x] CHK028 Is the author e-mail the sole identity used for the allowed-user comparison?
- [x] CHK029 Are both sides of the comparison trimmed and case-folded consistently?
- [x] CHK030 Is a missing or empty author e-mail classified as not allowed?
- [x] CHK031 Are commit metadata requirements explicit for hash, author, e-mail, date, message,
  repository, and branch?
- [x] CHK032 Is commit change content excluded because it is not used by the author rule?

## Scheduling and Execution Concurrency

- [x] CHK033 Are daily, weekly, and monthly schedules supported with an explicit timezone?
- [x] CHK034 Does a monthly occurrence use the last available calendar day when the configured day
  does not exist?
- [x] CHK035 Do disabled configurations suppress scheduled executions while remaining manually
  executable?
- [x] CHK036 Is at most one active execution allowed per configuration?
- [x] CHK037 Are manual/manual, manual/scheduled, and scheduled/scheduled races handled with
  explicit rejection or skipped-occurrence outcomes?
- [x] CHK038 Is the scheduled occurrence identity durable enough to prevent duplicate executions?
- [ ] CHK039 Are restart, overdue-occurrence, and single-scheduler assumptions documented?

## Failure Isolation, Credential Compromise, and Execution States

- [x] CHK040 Can a repository failure leave independent repositories processing?
- [x] CHK041 Does each repository failure retain execution, repository, stage, timestamp, and a
  safe reason?
- [x] CHK042 Are only `pending`, `running`, `completed`, `partially_completed`, and `failed`
  used for execution state?
- [x] CHK043 Does an execution with no new commits finish as `completed` with zero commits found
  and verified?
- [x] CHK044 Is `completed` used only when all repositories finish successfully?
- [x] CHK045 Is `partially_completed` used when at least one repository succeeds and another fails?
- [x] CHK046 Is `failed` used when no repository completes successfully?
- [x] CHK047 If a credential becomes compromised during execution, are new GitLab queries blocked,
  completed work preserved, and the final state reconciled correctly?

## UnauthorizedCommitAlert and Reports

- [x] CHK048 Does every UnauthorizedCommitAlert retain configuration, execution, repository,
  branch, commit hash, author, author e-mail, and commit date?
- [x] CHK049 Does an alert remain associated with the execution in which the commit was originally
  verified?
- [x] CHK050 Do later executions that reuse a verification avoid presenting the original alert as
  newly detected?
- [x] CHK051 Do report counters distinguish repositories processed and failed, commits found and
  verified, allowed commits, and non-allowed commits?
- [x] CHK052 Do reused verifications affect only the later execution's discovered-commit count and
  not its verified or non-allowed counts?
- [x] CHK053 Do report details include only alerts detected in the requested execution while the
  general history remains able to locate the original alert?
- [x] CHK054 Are zero-commit, successful, partially completed, and failed reports covered?

## WebSocket Authentication and Reconnection

- [x] CHK055 Is the authenticated operator supplied by the host environment rather than managed by
  the MVP?
- [x] CHK056 Are operations requiring operator identity rejected when identity is absent or invalid?
- [x] CHK057 Is each WebSocket ticket short-lived, single-use, and bound to both operator and
  execution?
- [x] CHK058 Are expired, consumed, invalid, wrong-operator, and wrong-execution tickets rejected?
- [x] CHK059 Are persistent GitLab credentials excluded from WebSocket authentication?
- [x] CHK060 Is REST the authoritative source of execution state while WebSocket carries progress
  notifications?
- [x] CHK061 Can the frontend reconnect with a fresh ticket, recover state through REST, and then
  resume receiving events?
- [x] CHK062 Can lost, duplicate, stale, out-of-order, gapped, or malformed events alter neither
  mining correctness nor persisted execution state?
- [x] CHK063 Are event types, revisions, correlation identifiers, and payload minimization defined
  for execution and repository lifecycle updates?

## GitLab Errors, Observability, and Testing

- [x] CHK064 Are valid, malformed, timed-out, unavailable, rate-limited, and unexpected GitLab
  responses translated into safe application errors?
- [x] CHK065 Do error messages and logs exclude GitLab tokens and other sensitive data?
- [x] CHK066 Are execution start, finish, state changes, repositories processed, commits checked,
  failures, alerts, and report counters observable with correlation identifiers?
- [x] CHK067 Are author rules, baseline, checkpoint, idempotency, scheduling, and state transitions
  covered by unit tests without live GitLab access?
- [x] CHK068 Are persistence, API, credential lifecycle, WebSocket authentication, reconnection,
  and main execution flows covered by integration tests?
- [x] CHK069 Are external GitLab contract tests separated from deterministic unit and integration
  suites?

## Cross-Artifact Alignment

- [ ] CHK070 Do specification, plan, data model, contracts, and tasks use the same execution
  states, counter names, alert ownership, and checkpoint identity?
- [x] CHK071 Do task ordering and migrations place foundational types and persistence before the
  services and tests that depend on them?
- [x] CHK072 Are all Constitution requirements for credential security, traceability, incremental
  processing, integration isolation, testability, failure isolation, privacy, and observability
  represented in the feature artifacts?

## Notes

- Mark items `[x]` only after review confirms the requirements-quality criterion is satisfied.
- Leave items unchecked when clarification, correction, or reviewer evaluation is still required.
- `$speckit-implement` reads checklist state as a gate and must not modify these markers.
- This checklist is limited to the current metadata-only MVP and contains no requirements for
  unrelated analysis capabilities.
