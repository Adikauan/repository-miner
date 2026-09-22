# Feature Specification: GitLab Repository Author Monitoring

**Feature Branch**: `001-gitlab-repository-mining`

**Created**: 2026-09-18

**Last Updated**: 2026-09-19

**Status**: Draft

**Input**: User description: "Configure, schedule, execute, and monitor incremental inspection of
GitLab commits to detect authors whose e-mail addresses are not allowed for the configuration."

## Clarifications

### Session 2026-09-18

- On the first execution of a configuration, record the current state of each selected branch as
  its baseline and do not inspect earlier commit history.
- Operators may start an execution manually for any valid configuration, even when automatic
  scheduling is disabled.
- A configuration may have at most one active execution. A competing manual request is rejected;
  a due scheduled occurrence is recorded as skipped with the reason.
- Configuration changes apply only to future commits. Existing repository and branch checkpoints
  are preserved, while newly introduced repository and branch combinations start at their current
  branch state.
- A first manual execution of a never-before-executed configuration establishes the same
  current-state baseline and does not inspect earlier history.

### Session 2026-09-19

- Q: O operador poderá cancelar manualmente uma execução em andamento no MVP? → A: Não; o MVP
  não permite cancelamento e não utiliza o estado `cancelled`.
- Q: Como o estado final deve ser determinado quando repositories falham durante uma execução? →
  A: `completed` quando todos terminam com sucesso, `partially_completed` quando há sucessos e
  falhas, e `failed` quando nenhum repository é processado com sucesso.
- Q: Em uma periodicidade mensal configurada para um dia inexistente no mês, quando a execução
  deverá ocorrer? → A: No último dia disponível daquele mês.
- Q: Se a credencial GitLab for marcada como comprometida durante uma execução ativa, o
  processamento ainda poderá fazer novas consultas ao GitLab? → A: Não; novas consultas são
  bloqueadas imediatamente, o trabalho durável concluído é preservado e a execução termina como
  `partially_completed` ou `failed` conforme os resultados já obtidos.
- The MVP validates commit authorship exclusively by comparing the commit author's e-mail address
  with the configuration's allowed-user e-mail list.
- The MVP does not need commit change content because it does not participate in author validation.
- Disabled configurations may be executed manually but never generate scheduled executions.
- A commit is verified at most once for the same configuration, repository, branch, and commit hash.
  Durable commit-verification records suppress repeated author validation even when a repository
  fails before its checkpoint can advance.
- An active GitLab credential may be replaced preventively. A compromised credential cannot return
  to use and must be replaced before the configuration performs further GitLab operations.
- Credential replacement preserves checkpoints, execution history, completed commit verifications,
  and previously recorded alerts.
- The host environment supplies the authenticated operator identity. The MVP does not register,
  authenticate, or manage operator accounts.
- Reused commit verifications remain historical facts of their original execution: they are not
  counted as newly verified and do not reproduce their original alert in a later execution.
- Mining scope and target branch cannot be persisted until the configuration's GitLab connection
  has been validated successfully.
- If a stored repository checkpoint cannot be found on the configured branch, the system treats the
  condition as history divergence. It records a repository-scoped failure, preserves the previous
  checkpoint, and never creates a replacement baseline automatically. This includes a missing
  checkpoint commit, rewritten or deleted branches, and a current branch history that diverges from
  the stored checkpoint.
- Recovery from history divergence requires an explicit operator action to redefine the baseline for
  the specific configuration, repository, and branch. The action is auditable and preserves prior
  executions, verifications, alerts, and their history.
- After application downtime, schedule reconciliation considers only the most recent missed
  occurrence for each configuration. It creates at most one recovery execution, never one execution
  per missed occurrence, and uses the durable occurrence identity to prevent duplication. Disabled
  configurations, compromised credentials, and configurations with an active execution do not create
  recovery executions.
- The canonical execution states are `pending`, `running`, `completed`, `partially_completed`, and
  `failed`. The canonical counters are `repositories_total`, `repositories_completed`,
  `repositories_failed`, `commits_discovered`, `commits_verified`, `allowed_commits`, and
  `unauthorized_commits`.
- A verified commit is one whose author validation has completed and been durably persisted for the
  configuration, repository, branch, and commit-hash identity. Reusing an existing verification does
  not repeat validation, create an alert, or increment `commits_verified` in the later execution.
  `UnauthorizedCommitAlert` belongs only to the execution that originally verified the commit and
  detected the unauthorized author.
- The canonical counter definitions are: `commits_discovered` counts commits returned by GitLab as
  later than the checkpoint for the execution; `commits_verified` counts commits whose author
  validation was actually completed and persisted by that execution; `allowed_commits` counts those
  newly verified commits whose author e-mail is allowed; and `unauthorized_commits` counts those
  newly verified commits whose author e-mail is not allowed. A reused `CommitVerification` increments
  none of these three result counters in the later execution.
- The canonical commit identity term is `commit_hash`. It is the hash component of the
  `CommitVerification` identity together with configuration, repository, and branch.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Configure Author Monitoring (Priority: P1)

An operator creates a monitoring configuration, connects it to a GitLab instance, browses the
available hierarchy, selects the required repositories, chooses a target branch, records allowed
user e-mail addresses, and defines the execution schedule.

**Why this priority**: The selected scope, protected GitLab connection, branch, and allowed-user
list are prerequisites for every useful execution.

**Independent Test**: Connect to a controlled GitLab account, select repositories through a nested
hierarchy, retain branch `QA`, enter allowed e-mail addresses and a schedule, save the
configuration, and reopen it without exposing the credential.

**Acceptance Scenarios**:

1. **Given** valid GitLab connection details, **When** the operator tests the connection, **Then**
   accessible groups, subgroups, and repositories are displayed in their hierarchy.
2. **Given** a loaded hierarchy, **When** the operator selects a group or subgroup, **Then** all
   descendant repositories are included and individual descendants can be adjusted.
3. **Given** a configuration with selected repositories, a target branch, allowed e-mail
   addresses, and a schedule, **When** the operator saves it, **Then** it is retained for future
   executions and its credential is never shown in full.
4. **Given** invalid or insufficient GitLab credentials, **When** the connection is tested,
   **Then** no repository hierarchy is loaded and a safe, actionable error is shown.
5. **Given** suspected exposure of a GitLab credential, **When** the operator marks it as
   compromised, **Then** new use is blocked, a secret-free incident is recorded, replacement is
   requested, and the replacement is auditable.
6. **Given** an active GitLab credential, **When** the operator replaces it preventively, **Then**
   the new credential becomes available for subsequent operations without altering prior mining
   state or history.
7. **Given** a compromised GitLab credential, **When** no replacement has been supplied, **Then**
   it remains blocked and cannot be used again; after an auditable replacement, subsequent
   operations use only the replacement credential.
8. **Given** a configuration whose GitLab connection has not been validated successfully, **When**
   the operator attempts to persist groups, subgroups, repositories, or target branch, **Then** the
   scope change is rejected and no unvalidated mining scope is retained.

---

### User Story 2 - Run Incremental Author Verification (Priority: P2)

When an enabled configuration becomes due, or an operator requests a manual run, the system
inspects only new commits on the configured branch of each selected repository and determines
whether each commit author's e-mail address is allowed.

**Why this priority**: Incremental author verification and alerts are the primary operational value
of the product.

**Independent Test**: Establish a baseline, add controlled commits from allowed and non-allowed
e-mail addresses, run the configuration again, and verify incremental collection, classification,
alerts, checkpoints, and continued processing after one repository fails.

**Acceptance Scenarios**:

1. **Given** an enabled configuration whose daily, weekly, or monthly schedule is due, **When**
   scheduling is evaluated, **Then** exactly one execution starts for that occurrence.
2. **Given** a disabled but otherwise valid configuration, **When** the operator requests a manual
   run, **Then** an execution starts; no execution starts merely because its schedule becomes due.
3. **Given** a configuration being executed for the first time, **When** each selected repository
   is inspected, **Then** the current target-branch state becomes the baseline and earlier commits
   are not verified.
4. **Given** commits after the stored checkpoint, **When** a repository is processed, **Then** each
   new commit records at least hash, author, author e-mail, date, message, repository, and branch.
5. **Given** a new commit whose normalized author e-mail is present in the allowed list, **When**
   verification occurs, **Then** the commit is recorded as belonging to an allowed user and no
   non-allowed-author alert is created.
6. **Given** a new commit whose author e-mail is absent, empty, or not present in the allowed list,
   **When** verification occurs, **Then** the commit is recorded as not allowed and a traceable
   alert is created.
7. **Given** one repository fails, **When** other selected repositories remain independently
   processable, **Then** their processing continues and the failed repository is recorded.
8. **Given** a repository fails after some commits have been durably verified, **When** a later
   execution reads the same commits because the repository checkpoint did not advance, **Then** the
   existing verification records are recognized and only commits without a completed verification
   are submitted to author validation.
9. **Given** a later execution recognizes a previously completed unauthorized verification,
   **When** its progress and report are calculated, **Then** that commit is not counted as verified
   in the later execution and the original alert is not presented as newly detected; the historical
   alert remains associated with its original detection execution.

---

### User Story 3 - Monitor an Execution (Priority: P3)

An operator opens an execution and follows its current state, repository progress, commits found
and verified, non-allowed-author alerts, and repository failures as processing occurs.

**Why this priority**: Live visibility allows the operator to understand progress and partial
failures without inspecting internal diagnostics.

**Independent Test**: Observe a controlled execution with successful and failed repositories,
temporarily disconnect the interface, reconnect, and verify that the displayed state recovers and
matches the recorded execution without affecting processing.

**Acceptance Scenarios**:

1. **Given** an execution in progress, **When** the operator opens it, **Then** its start time,
   current state, repository progress, commit counts, alerts, and failures are shown.
2. **Given** a temporary loss of the live connection, **When** the interface reconnects, **Then**
   it obtains the current durable state and continues receiving progress without interrupting the
   execution.
3. **Given** an execution with a repository failure and other successful repositories, **When**
   processing ends, **Then** the execution is `partially_completed` and retains both successful
   results and failure details.
4. **Given** no valid authenticated operator identity, **When** WebSocket ticket issuance is
   requested, **Then** the request is rejected and no ticket is issued.
5. **Given** an authenticated operator authorized to observe an execution, **When** a ticket is
   issued, **Then** it expires within 60 seconds, can be consumed only once, and authorizes only
   that operator and that execution.
6. **Given** a ticket issued for one operator or execution, **When** another operator or another
   execution attempts to use it, **Then** the connection is rejected.

---

### User Story 4 - Review the Execution Report (Priority: P4)

After processing, an operator reviews a report summarizing repository outcomes, commit verification,
non-allowed authors, and failures, with every alert linked to its originating commit.

**Why this priority**: The report turns execution results into an auditable list of authorship
exceptions that can be reviewed by an operator.

**Independent Test**: Complete a fixture execution containing allowed commits, non-allowed commits,
and a repository failure, then verify totals, final state, alert details, and source traceability.

**Acceptance Scenarios**:

1. **Given** a terminal execution, **When** the report is opened, **Then** it shows repositories
   processed, commits found, commits verified, allowed-user commits, non-allowed-user commits,
   failed repositories, and final execution state.
2. **Given** a non-allowed-author alert, **When** the operator examines it, **Then** configuration,
   execution, repository, branch, commit hash, author, author e-mail, and commit date are available.
3. **Given** an execution with no commits after the baseline or checkpoint, **When** it finishes,
   **Then** its state is `completed` and all commit counters are zero.
4. **Given** a later execution that only recognizes an earlier completed verification, **When** its
   report is opened, **Then** the commit and original alert are not represented as newly verified or
   detected in that later execution; the original alert remains available through historical
   consultation with its detection execution.

### Edge Cases

- A selected group later gains or loses repositories; selection is resolved at execution time and
  the effective repositories processed are retained for audit.
- A selected repository lacks the target branch; it fails with a scoped reason while independent
  repositories continue.
- The GitLab credential is revoked or marked compromised; new connection tests, manual executions,
  scheduled executions, and further GitLab queries in an active execution are blocked without
  exposing the credential value. Durable work already completed by the active execution is
  preserved.
- An operator replaces an active credential preventively; subsequent GitLab operations use the
  replacement while checkpoints, execution history, completed verifications, and alerts remain
  unchanged.
- A compromised credential is replaced; the compromised value remains permanently unusable and
  the replacement does not reset or reprocess prior mining state.
- An author e-mail differs only in letter case or surrounding whitespace; comparison uses a
  normalized form while the original commit value remains available for traceability.
- A commit has no author e-mail; it is treated as not allowed and produces an alert.
- Multiple schedule evaluations observe the same due occurrence; only one execution is created.
- A monthly schedule targets a day that does not exist in a particular month; that occurrence is
  due on the last calendar day of that month.
- A configuration already has an active execution; another manual request is rejected and a due
  scheduled occurrence is recorded as skipped.
- A repository stops after some commits have been durably verified; its checkpoint does not advance.
  On the next execution, completed verification records for the same configuration, repository,
  branch, and commit hash are reused, while only unverified commits undergo author validation.
- A configuration is disabled during an active execution; future scheduled occurrences are
  suppressed, while the active execution continues with its immutable configuration snapshot.
- Repository scope, branch, or allowed-user e-mails change; completed commits are not reprocessed,
  retained combinations keep their checkpoints, and new combinations start from current state.
- The target branch history is rewritten and a stored checkpoint can no longer be located; the
  repository records a scoped failure instead of silently treating coverage as complete. The
  previous checkpoint remains unchanged until an operator explicitly redefines the baseline.
- An operator explicitly requests recovery from a divergent history; the system records the action,
  configuration, repository, branch, prior checkpoint, and new baseline without deleting historical
  executions, verifications, or alerts.
- The application restarts after multiple scheduled occurrences were missed; only the latest missed
  occurrence is eligible for one recovery execution, and duplicate reconciliation does not create a
  second execution.
- An identity-dependent operation receives no identity or an invalid identity from the host; the
  operation is rejected without creating a ticket or sensitive audit action.
- A WebSocket ticket is expired, already consumed, scoped to another execution, or presented by
  another operator; it is rejected without affecting the monitored execution.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST allow an operator to create, view, edit, enable, disable, and retain
  monitoring configurations.
- **FR-002**: A configuration MUST contain a name, GitLab instance URL, protected GitLab credential
  reference, repository selection, target branch, allowed-user e-mail list, periodicity, scheduling
  timezone, and enabled state.
- **FR-003**: The system MUST validate a GitLab connection successfully before permitting the
  selection or persistence of groups, subgroups, repositories, or target branch for the monitoring
  scope. An unvalidated or unsuccessfully validated connection MUST cause scope persistence to be
  rejected.
- **FR-004**: The system MUST present accessible GitLab groups, nested subgroups, and repositories
  while preserving their hierarchy.
- **FR-005**: Operators MUST be able to select a complete group, complete subgroup, or individual
  repositories and adjust inherited descendant selections.
- **FR-006**: The initial target branch MUST default to `QA` and remain editable per configuration.
- **FR-007**: Operators MUST be able to maintain one or more allowed-user e-mail addresses for a
  configuration. Stored comparison values MUST ignore surrounding whitespace and letter case.
- **FR-008**: The system MUST support daily, weekly, and monthly periodicities and display the next
  due time in the configured scheduling timezone. When a configured monthly day does not exist in
  a month, that occurrence MUST use the month's last calendar day.
- **FR-009**: When an enabled configuration becomes due, the system MUST create no more than one
  execution for that configuration and occurrence. Disabled configurations MUST NOT generate
  scheduled executions.
- **FR-010**: An operator MUST be able to start a manual execution for any valid configuration,
  including a disabled configuration.
- **FR-011**: The system MUST allow at most one active execution per configuration. It MUST reject
  a competing manual request and record a competing scheduled occurrence as skipped with a clear
  reason.
- **FR-012**: A new execution MUST retain an immutable snapshot of the effective configuration and
  repository scope without readable credential values.
- **FR-013**: The first execution of each configuration, repository, and branch combination MUST
  record the current branch state as its baseline without processing earlier commit history.
- **FR-014**: Later executions MUST identify only commits after the durable checkpoint for the same
  configuration, repository, and branch.
- **FR-015**: For each new commit, the system MUST collect at least hash, author, author e-mail,
  date, message, repository, and branch.
- **FR-016**: The MVP MUST NOT retrieve commit change content as part of author verification.
- **FR-017**: The system MUST compare each commit author's normalized e-mail address with the
  configuration's normalized allowed-user e-mail list.
- **FR-018**: A commit with a missing, empty, or unmatched author e-mail MUST be classified as not
  allowed and MUST create exactly one durable non-allowed-author alert for its completed
  verification. Reuse of that verification in a later execution MUST NOT create another alert.
- **FR-019**: Each non-allowed-author alert MUST identify its configuration, execution, repository,
  branch, commit hash, author, author e-mail, and commit date.
- **FR-020**: Failure of one repository MUST NOT prevent processing of other repositories that can
  be processed independently.
- **FR-021**: Each repository failure MUST record its execution, repository, processing stage,
  time, safe reason, and whether independent processing continued.
- **FR-022**: Each completed author verification MUST be persisted durably and uniquely identified
  by configuration, repository, branch, and commit hash. A commit MUST undergo author validation at
  most once for that combination. If a repository fails after some commits have been verified, its
  checkpoint MUST NOT advance; a later execution MUST recognize the completed verification records
  and process only commits that do not yet have a completed verification. The repository checkpoint
  MUST advance only after the repository finishes successfully.
- **FR-023**: Configuration changes MUST apply only to future commits. Existing repository and
  branch combinations MUST retain checkpoints, and new combinations MUST begin at current state.
- **FR-024**: The system MUST expose execution start, end, current state, repository progress,
  and the canonical counters `repositories_total`, `repositories_completed`,
  `repositories_failed`, `commits_discovered`, `commits_verified`, `allowed_commits`, and
  `unauthorized_commits`, together with alerts and failures, for live operator monitoring.
- **FR-025**: Execution states MUST use only `pending`, `running`, `completed`,
  `partially_completed`, and `failed`. The MVP MUST NOT offer execution cancellation. An execution
  with no new commits MUST finish as `completed` with zero commits found and verified. A terminal
  execution MUST be `completed` when every repository finishes successfully,
  `partially_completed` when at least one repository succeeds and at least one fails, and `failed`
  when no repository is processed successfully.
- **FR-026**: The execution report MUST show the canonical counters `repositories_total`,
  `repositories_completed`, `repositories_failed`, `commits_discovered`, `commits_verified`,
  `allowed_commits`, and `unauthorized_commits`, detailed non-allowed-author alerts, failed
  repositories, and final execution state.
- **FR-027**: GitLab credentials MUST never be returned in full or appear in reports, alerts,
  diagnostics, application logs, or source-controlled configuration.
- **FR-028**: When exposure of a GitLab credential is suspected, the system MUST mark it as
  compromised, prevent its use in new operations, record a secret-free audit incident, inform the
  operator that external invalidation or rotation is required, allow replacement, and record that
  replacement auditably. If compromise is marked during an active execution, the system MUST
  immediately prevent further GitLab queries, preserve durably completed work, and finish the
  execution as `partially_completed` when at least one repository already succeeded or `failed`
  when none succeeded. Automatic external rotation is outside the system's responsibility.
- **FR-029**: Loss of the interface's live connection MUST NOT interrupt or alter execution, and
  reconnection MUST recover the current recorded state before live updates continue.
- **FR-030**: The MVP MUST NOT modify repository code, create commits, or create merge requests.
- **FR-031**: The product MUST provide a coherent web experience for configuration, execution
  monitoring, and report review.
- **FR-032**: An operator MUST be able to replace an active GitLab credential preventively. A
  credential marked as compromised MUST remain unusable and MUST be replaced before the
  configuration can perform further GitLab operations. Credential replacement MUST be auditable
  and MUST NOT alter checkpoints, execution history, completed commit verifications, or previously
  recorded alerts.
- **FR-033**: The MVP MUST NOT register, authenticate, or manage operator accounts. The host
  environment MUST supply the authenticated operator identity. Every operation that depends on an
  operator identity MUST reject absent or invalid identity, and sensitive credential-incident and
  replacement audits MUST record the valid operator identity.
- **FR-034**: WebSocket ticket issuance MUST require a valid authenticated operator. Each ticket
  MUST expire no later than 60 seconds after issuance, be consumable at most once, and be restricted
  to both the execution requested and the operator who requested it. A ticket MUST NOT authorize
  another execution or another operator.
- **FR-035**: When an execution recognizes a commit verification completed in an earlier execution,
  it MUST NOT perform author validation again, create another non-allowed-author alert, count the
  commit as verified in the later execution, or present the original alert as newly detected. The
  original alert MUST remain associated with and historically queryable through its detection
  execution.
- **FR-036**: When the stored checkpoint commit cannot be reconciled with the configured branch,
  including when the commit is missing, the branch is removed or rewritten, or the current history
  is not descended from the persisted checkpoint, the system MUST record a repository-scoped
  `history_diverged` failure, MUST NOT create a baseline automatically, MUST NOT advance the
  checkpoint, and MUST NOT continue incremental processing for that repository. The previous
  checkpoint, verifications, alerts, and execution history MUST remain preserved. An authenticated
  operator MUST be able to explicitly redefine the baseline for the configuration, repository, and
  branch using the current HEAD. The reset MUST process no historical commits, preserve the previous
  checkpoint in an audit record, record operator, date/time, previous checkpoint, new baseline, and
  reason, and MUST NOT delete prior executions, `CommitVerification` records, or
  `UnauthorizedCommitAlert` records.
- **FR-037**: The MVP MUST operate with one active scheduler instance. At application startup, the
  scheduler MUST reconcile persisted schedules. If one or more occurrences became due during
  downtime, it MUST consider only the most recent overdue occurrence, create at most one recovery
  execution, and MUST NOT create one execution per missed occurrence. The persistent occurrence
  identity MUST make reconciliation idempotent and prevent duplicate occurrences or executions.
  Disabled configurations, compromised credentials, and configurations with an active execution MUST
  NOT create recovery executions; the operational reason MUST be recorded without changing
  checkpoints.

### Key Entities

- **Monitoring Configuration**: Named definition of GitLab connection reference, repository scope,
  target branch, allowed-user e-mails, schedule, timezone, and enabled state.
- **Repository Selection**: A group, subgroup, or repository selection rule and the effective
  repositories resolved for an execution.
- **Allowed User**: A normalized e-mail address permitted to author commits in the configuration's
  target branch.
- **Schedule**: Daily, weekly, or monthly recurrence and its next due occurrence.
- **Execution**: An immutable configuration snapshot with lifecycle state, progress counters,
  repository outcomes, alerts, failures, and final report.
- **Repository Run**: Processing state and outcome for one repository in an execution.
- **Commit Verification**: Collected commit metadata, allowed/not-allowed result, and durable
  completion identity unique by configuration, repository, branch, and commit hash, reusable across
  executions when a checkpoint has not advanced.
- **Non-Allowed-Author Alert**: An auditable authorship exception tied to its configuration,
  execution, repository, branch, and commit.
- **Repository Failure**: A safe diagnostic record tied to an execution and repository.
- **Credential Incident**: A secret-free audit record of suspected exposure, blocked use, operator
  notification, and credential replacement.
- **Credential Reference**: A protected reference with an active, compromised, or replaced
  lifecycle; replacement may be preventive or incident-driven and never resets mining state.
- **Incremental Checkpoint**: The latest durable branch/commit position used to avoid reprocessing.
- **Authenticated Operator**: Identity supplied and validated by the host environment for
  identity-dependent operations and sensitive audit attribution; it is not a locally managed
  account.
- **WebSocket Ticket**: Short-lived, single-use authorization associated with one authenticated
  operator and one execution.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-003**: In fixture executions, 100% of eligible commits are verified at most once per
  configuration, repository, branch, and commit hash; after a partial repository failure, every
  durable completed verification is reused, every remaining commit is verified, and no commit
  before the baseline is processed.
- **SC-004**: 100% of fixture commits whose normalized author e-mail appears in the allowed list are
  classified as allowed, and 100% of missing or unmatched e-mails create one non-allowed alert.
- **SC-005**: 100% of non-allowed-author alerts expose configuration, execution, repository, branch,
  commit hash, author, author e-mail, and commit date, with no orphan alerts in acceptance testing.
- **SC-006**: A failure in one fixture repository does not prevent processing of any other
  independently processable repository.
- **SC-007**: Live progress and final report counts match durable processing outcomes in 100% of
  acceptance scenarios, including partial failures and executions with no new commits.
- **SC-008**: Zero full GitLab credential values appear in logs, reports, alerts, incident records,
  audit records, interface responses, or source-controlled configuration during security tests.
- **SC-009**: 100% of enabled due configurations create exactly one execution per scheduled
  occurrence; disabled configurations create zero scheduled executions while remaining manually
  executable.
- **SC-010**: In 100% of acceptance scenarios, the report distinguishes commits found, commits
  verified, allowed-user commits, non-allowed-user commits, and failed repositories without
  double-counting.
- **SC-011**: In 100% of preventive and incident-driven credential replacement scenarios,
  checkpoints, execution history, completed commit verifications, and existing alerts remain
  unchanged; a compromised credential is used in zero subsequent operations.
- **SC-012**: In 100% of authentication acceptance scenarios, identity-dependent operations reject
  absent or invalid identity, and WebSocket tickets succeed only once for their issuing operator
  and designated execution.
- **SC-013**: In 100% of reuse scenarios, a verification completed in an earlier execution causes
  zero repeated author validations, zero duplicate alerts, and zero verified-commit or newly
  detected-alert increments in the later execution.
- **SC-014**: In 100% of configuration acceptance scenarios, mining scope persistence is rejected
  until the associated GitLab connection has completed a successful validation.

## Assumptions

- The MVP serves operators whose authenticated identities and authorization context are supplied by
  the host environment; registration, authentication, account management, and role design remain
  outside this feature.
- The application has one configured scheduling timezone; daylight-saving and calendar behavior
  follow that timezone's published rules.
- The MVP runs one active scheduler instance. After downtime, missed occurrences are reconciled
  using only the latest due occurrence per configuration and at most one recovery execution.
- Repository access is read-only for the MVP.
- Commit author e-mail is the sole allowed-user matching identifier; display-name matching is not
  performed.
- An absent author e-mail cannot be proven to belong to an allowed user and is therefore classified
  as not allowed.
- Repository selection is resolved at execution time, and the effective scope is retained for
  audit.
- The first execution, whether manual or scheduled, establishes the baseline for combinations that
  do not yet have a checkpoint.
- A checkpoint is uniquely identified by configuration, repository, and branch. A completed commit
  verification is uniquely identified by configuration, repository, branch, and commit hash.
- The system stores operational metadata required for traceability while protecting the GitLab
  credential value.
- Quantitative performance and scalability targets are deferred until a representative deployment
  scenario defines GitLab latency, pagination volume, hardware, caching strategy, and benchmark
  conditions.
