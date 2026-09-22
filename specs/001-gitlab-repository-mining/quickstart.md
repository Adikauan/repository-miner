# Quickstart Validation Guide

This guide defines the runnable acceptance path for the planned MVP. Commands assume the project
structure in [plan.md](./plan.md) has been created.

## Prerequisites

- Python 3.13
- Supported Node.js LTS runtime
- PostgreSQL 16+
- Test-only external encryption key and WebSocket-ticket HMAC pepper
- Optional sandbox GitLab credential for separate external contract tests

Never place real credentials in committed environment files, fixtures, output, or screenshots.

## Local setup

```powershell
Copy-Item deploy/env.example deploy/.env
docker compose -f deploy/compose.yaml up -d database
Set-Location backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
alembic upgrade head
Set-Location ..\frontend
npm install
```

## Deterministic test suites

```powershell
Set-Location backend
pytest tests/unit
pytest tests/integration
pytest tests/contract -m "not external"
Set-Location ..\frontend
npm test
npm run build
```

Default suites use a fake GitLab gateway and require no external credentials or network. External
GitLab contract tests are opt-in and must not print credentials or commit messages.

## End-to-end validation scenarios

### 1. Configure and baseline

1. Create a configuration draft and attempt to save repository selection and branch before testing
   its fake GitLab connection.
2. Validate the connection, then save nested repository selection, target branch `QA`, allowed
   e-mail addresses, daily schedule, and scheduling disabled.
3. Change the credential and confirm scope changes are blocked until the new connection validates.
4. Start the first manual execution.

Expected:

- Responses never expose the GitLab token.
- Scope persistence is rejected before successful validation and after URL/credential change until
  revalidation; the first successful scope save defaults its branch to `QA` when omitted by the UI.
- Effective repositories and normalized allowed e-mails are snapshotted.
- Each configuration/repository/branch combination records current HEAD as baseline.
- No prior commit is verified and no change-content endpoint is called.
- Execution is `completed` with all commit counters zero.

### 2. Incremental allowed and unauthorized commits

1. Add three commits after baseline: one matching allowed e-mail with different case/whitespace, one
   unmatched e-mail, and one missing e-mail.
2. Run the configuration again.

Expected:

- Only the three post-baseline commits are discovered and verified.
- Original author metadata is preserved; comparison uses normalized e-mail.
- One commit is allowed and two are unauthorized.
- Exactly two traceable alerts are created.
- Report counters satisfy `commits_verified = allowed_commits + unauthorized_commits` and expose
  `repositories_total`, `repositories_completed`, and `repositories_failed`.
- Repeating the run without new commits does not process them again.

### 3. Repository failure isolation and checkpoint safety

Use one valid repository with a new commit and one repository without branch `QA`. In another
fixture, fail a repository after its first of two commits has been durably verified but before its
checkpoint advances, then rerun it.

Expected:

- Valid repository completes and advances only its checkpoint.
- Missing-branch repository records a safe failure and does not advance its checkpoint.
- A rewritten or divergent branch records `history_diverged`, preserves the prior checkpoint, and
  does not create a replacement baseline automatically.
- Execution becomes `partially_completed`; report shows one processed and one failed repository.
- If every repository is made to fail, execution becomes `failed`.
- The partial repository keeps its old checkpoint, but the next execution reuses the first commit's
  durable verification and validates only the remaining commit.
- The same configuration/repository/branch/SHA never creates a second verification or alert.
- The retry discovers both commits but counts only the remaining newly processed commit in
  `commits_verified` and its result counter; the reused unauthorized result creates no alert event
  or alert detail in the retry report.
- The original alert remains associated with and queryable through its original detection execution.

### 4. Execution exclusion and scheduling

1. Hold an execution in `running`.
2. Request another manual run and simulate a due schedule.
3. Configure a monthly occurrence for day 31 in a 30-day month.
4. Restart with one past-due occurrence and disable another configuration.

Expected:

- Manual request receives a stable conflict; due occurrence is recorded as skipped-active.
- No second active execution row is committed.
- Monthly occurrence uses the month's last calendar day.
- Durable schedules reload and at most the latest missed occurrence starts.
- Restart reconciliation creates at most one recovery execution per configuration and never creates
  executions for disabled, compromised, or already-active configurations.
- Disabled configuration starts no scheduled run but still accepts a manual run.

### 5. Credential compromise during execution

1. Complete one repository in a multi-repository execution.
2. Mark the GitLab credential compromised before the next repository call.

Expected:

- No subsequent GitLab call starts and credential plaintext appears nowhere.
- Completed repository data and checkpoint remain intact.
- Remaining repositories record safe failures caused by credential compromise.
- Execution becomes `partially_completed` and report includes the safe cause.
- Repeating with compromise before any repository succeeds yields `failed`.
- Replacement creates a new encrypted reference and auditable link without reactivating the old one.
- A compromised credential remains unusable until replacement; replacement preserves all
  checkpoints, execution history, completed verifications, and alerts.

### 6. Preventive credential replacement

1. Establish checkpoints, completed executions, verifications, and alerts with an active credential.
2. Replace that active credential before any suspected exposure.
3. Run another connection test and incremental execution.

Expected:

- The new credential becomes the sole active reference and the old reference becomes `replaced`.
- The authenticated replacement audit records reason `preventive` without either secret value.
- Existing checkpoints, executions, verifications, and alerts are byte-for-byte logically
  unchanged, and the next execution continues from the previous checkpoint.

### 8. Explicit history recovery

1. Cause a configured branch to diverge from its stored checkpoint.
2. Confirm the repository execution fails with `history_diverged` and the checkpoint is unchanged.
3. As an authenticated operator, invoke the explicit baseline-reset operation with a reason.

Expected outcomes:

- A new baseline is recorded only for the selected configuration/repository/branch.
- The reset is auditable with the previous checkpoint, new baseline, operator, and reason.
- Prior executions, verifications, and alerts remain queryable and unchanged.

### 7. WebSocket authentication and recovery

1. Configure the HTTP adapter with a fake host identity and obtain a one-use ticket through
   authenticated REST after fetching an execution snapshot.
2. Connect, receive progress and an `unauthorized_commit.detected` identifier event, then disconnect.
3. Attempt reuse, expiry, invalid value, wrong-execution scope, and use by a different validated
   operator; reconnect with a fresh ticket.
4. Send duplicate, stale, and deliberately gapped revisions.
5. Repeat ticket issuance with missing/invalid identity and with a valid operator that lacks access.

Expected:

- Invalid ticket cases are rejected uniformly and GitLab credentials are never socket credentials.
- Missing/invalid identity yields `401`; insufficient execution authorization yields `403`; no
  ticket row is created in either case.
- The ticket is bound to the stable ID returned by `AuthenticatedOperatorProvider`, never to an
  operator ID supplied in the request.
- Wrong-operator and wrong-execution attempts are rejected without consuming an otherwise valid
  ticket; a successful handshake atomically records `consumed_at`.
- Disconnect does not alter processing; reconnect obtains REST state before live continuation.
- Duplicate/stale events do not regress UI; a gap triggers REST refetch.
- Terminal event causes final report refetch.

### 8. Authenticated credential-incident audit

1. Attempt to mark a credential compromised and replace it without a host-authenticated identity.
2. Repeat with a valid fake operator identity.
3. Swap the fake HTTP authentication adapter for another implementation while retaining the same
   application use cases.

Expected:

- Missing or invalid identity fails with `401` and creates no incident or replacement audit row.
- A valid identity is recorded by stable operator ID without persisting host credentials or raw
  claims; a valid but unauthorized operator receives `403`.
- No local account, password, registration, or login record is created.
- Both adapters exercise the same ticket and incident use cases unchanged.

### 9. GitLab response and failure translation

Exercise the fake gateway with a valid response, malformed payload, timeout, unavailable service,
unexpected HTTP status, and rate limit response using canary token and response-body secrets.

Expected:

- The valid response produces the expected hierarchy or commit metadata.
- Every failure maps to its documented stable, safe application error; retry guidance is retained
  only when safe and applicable.
- No token, authorization value, raw provider body, or canary secret appears in the returned error,
  logs, failure records, reports, or events.
- Each affected repository fails independently when other repositories remain processable.

### 10. Final report reconciliation

Complete fixtures covering successful, partially completed, failed, and zero-commit executions.

Expected:

- Report exposes repositories processed/failed, commits discovered/verified, allowed commits,
  unauthorized commits, detailed alerts, terminal state, and safe failure reasons.
- Every alert resolves to configuration, execution, repository, branch, commit hash, author,
  author e-mail, and commit date.
- Durable rows reconcile exactly with summary counters.

## Contract verification

- Validate [openapi.yaml](./contracts/openapi.yaml) as OpenAPI 3.1.
- Verify backend routes and frontend DTOs against the REST contract.
- Validate all events against [websocket-events.md](./contracts/websocket-events.md).
- Fail CI when contracts change without consumer types and contract tests changing.

## Release gate

The MVP is ready only when deterministic suites, migrations, and all ten scenarios pass; all
constitution gates remain PASS; and no broker, microservice, repository clone, change-content
retrieval, repository mutation, automatic commit, or merge-request behavior has entered the build.

## Validation record

The deterministic backend suite was executed with `pytest -q` and covers configuration/baseline,
incremental verification, failure isolation, scheduling, credential compromise and replacement,
WebSocket ticket authentication/recovery, report reconciliation, migration upgrade/downgrade,
OpenAPI structure, observability, and secret-leakage checks. External GitLab contract coverage is
kept opt-in and is represented by a skipped marker test when no sandbox credentials are supplied.
The latest validation result was 38 passing tests and 1 intentionally skipped external test.
