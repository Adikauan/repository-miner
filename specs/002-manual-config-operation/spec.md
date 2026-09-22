# Feature Specification: Manual Configuration Operation and Editing

**Feature Branch**: `002-manual-config-operation`

**Created**: 2026-09-20

**Status**: Draft

**Input**: User description: "Permitir consultar, editar e executar manualmente uma configuração de mineração existente, preservando as regras de mineração já implementadas."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Consult and edit an existing configuration (Priority: P1)

An operator opens an existing mining configuration, reviews its persisted settings, changes allowed values, and saves the same configuration.

**Why this priority**: Operators must be able to maintain configurations without creating duplicates or losing the current setup.

**Independent Test**: Open a persisted configuration, verify that its fields are populated, change a non-sensitive field, save, and reopen it to confirm the updated value.

**Acceptance Scenarios**:

1. **Given** an existing configuration, **When** the operator opens it, **Then** the interface displays its name, GitLab URL, selected scope, branch, allowed users, schedule, and enabled status using the persisted values.
2. **Given** an existing configuration, **When** the operator changes editable fields and saves, **Then** the existing configuration is updated and no second configuration is created.
3. **Given** an existing configuration, **When** it is loaded, **Then** GitLab tokens and other credential values are not returned in plaintext and the interface clearly identifies the credential as unavailable for retrieval.
4. **Given** a configuration with a failed load or update, **When** the operation finishes, **Then** the operator receives a safe, actionable error without secrets.
5. **Given** the operator edits scope, branch, allowed users, schedule, or credentials, **When** the changes are saved, **Then** the interface uses the dedicated operation for that information instead of the basic configuration update operation.
6. **Given** the operator edits the enabled status, **When** the change is saved, **Then** the basic configuration update operation persists `enabled` without requiring GitLab connection validation.

### User Story 2 - Change connection, scope, users, or schedule safely (Priority: P1)

An operator changes the GitLab connection, selected groups, subgroups, repositories, target branch, allowed e-mails, or schedule while preserving prior mining history.

**Why this priority**: Configuration changes are common and must not silently invalidate incremental state or historical results.

**Independent Test**: Modify each supported category, validate the connection when required, save, and verify both the new configuration and preservation of prior checkpoints and records.

**Acceptance Scenarios**:

1. **Given** the GitLab URL or credential changes, **When** the operator saves dependent scope or branch changes without a successful validation of the new connection, **Then** the system rejects those dependent changes.
2. **Given** the operator does not provide a replacement credential, **When** other editable fields are saved, **Then** the currently associated credential remains unchanged.
3. **Given** a new repository or branch combination has no checkpoint, **When** it is processed for the first time, **Then** the current branch state becomes its baseline and prior history is not processed.
4. **Given** repositories or branches are removed from the current scope, **When** a future execution starts, **Then** they are not processed, while their checkpoints, verifications, alerts, and historical executions remain available.
5. **Given** allowed e-mails are changed, **When** a future commit is verified, **Then** comparison uses the normalized e-mail list; previously verified commits are not reprocessed and existing alerts remain unchanged.
6. **Given** schedule parameters or enabled status are changed, **When** the update is saved, **Then** the next occurrence is recalculated, old unexecuted schedule values stop applying, executed occurrences remain historical, and no retroactive execution is created.
7. **Given** a connection change has invalidated the previous validation, **When** a dependent operation is attempted, **Then** the operation is rejected with the functional error code `connection_not_validated` and the application's conflict status.
8. **Given** the operator loads groups, subgroups, repositories, or branches, **When** the current connection is not validated, **Then** the load or selection operation is rejected with `connection_not_validated` and the application's conflict status.

### User Story 3 - Start and follow a manual execution (Priority: P1)

An operator starts mining manually from the configuration screen and follows that execution using the existing execution monitoring experience.

**Why this priority**: Manual execution is the primary operational action for validating a configuration immediately.

**Independent Test**: Start a manual run from an existing configuration, receive its execution identifier, and open its persisted snapshot and live progress.

**Acceptance Scenarios**:

1. **Given** a valid configuration, **When** the operator selects manual execution, **Then** a new execution is created with manual origin when that attribute exists and the existing mining flow starts.
2. **Given** a disabled configuration with valid connection, scope, branch, and users, **When** the operator starts a manual run, **Then** the run is allowed; disabled status prevents only scheduled runs.
3. **Given** an active execution for the same configuration, **When** the operator requests another manual run, **Then** the request is rejected with a clear conflict and no second execution is created.
4. **Given** a compromised credential, **When** the operator requests a manual run, **Then** the request is rejected until the credential is replaced.
5. **Given** a successful manual start, **When** the operator continues to the execution view, **Then** the existing persisted snapshot, temporary access ticket, real-time updates, terminal states, and canonical counters are used.

## Edge Cases

- The requested configuration does not exist or cannot be loaded.
- The GitLab connection is invalid, unavailable, or changed since the last validation.
- The operator submits an empty or malformed branch, schedule, or allowed e-mail value.
- A new branch has no checkpoint while another branch has historical checkpoints for the same configuration and repository.
- A repository is removed after it has historical alerts or verifications.
- A schedule is edited while an execution is active or while a prior occurrence is overdue.
- A manual request races with a scheduled request for the same configuration.
- A credential is marked compromised between validation and execution start.
- The live connection is lost after a manual execution starts; the execution must continue and remain recoverable through the persisted snapshot.
- A test or fixture attempts to use a real credential or exposes a synthetic secret in an HTTP response, log, error message, or test snapshot.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST allow an operator to open an existing mining configuration and view its currently persisted editable settings.
- **FR-002**: The system MUST display the configuration name, GitLab connection reference and URL, selected groups, subgroups, repositories, target branch, allowed users, schedule parameters, and enabled status when those values exist.
- **FR-003**: The system MUST NOT return GitLab tokens or other credential values in plaintext to the interface and MUST distinguish unavailable sensitive fields from ordinary editable fields.
- **FR-004**: Saving edits MUST update the existing configuration rather than create a duplicate configuration.
- **FR-005**: Configuration editing MUST apply the same validation rules used when creating a configuration.
- **FR-006**: Changes to a GitLab URL, credential, or other connection identity MUST invalidate the prior connection validation for dependent scope and branch changes.
- **FR-007**: The system MUST require successful validation of the current GitLab connection before persisting dependent changes to groups, subgroups, repositories, or branch.
- **FR-008**: If no replacement credential is supplied during an edit, the currently associated credential MUST remain unchanged.
- **FR-009**: The operator MUST be able to add, remove, and change selected groups, subgroups, repositories, and target branch subject to connection validation.
- **FR-010**: A configuration/repository/branch combination without a checkpoint MUST use the current branch state as its first baseline and MUST NOT process history before that baseline.
- **FR-011**: Removing a repository or changing away from a branch MUST not delete its checkpoints, commit verifications, alerts, executions, or other historical records.
- **FR-012**: Changes to allowed users MUST affect only future commit validations, using the existing normalized author e-mail comparison, and MUST NOT reprocess completed verifications or modify existing alerts.
- **FR-013**: Changes to recurrence, schedule parameters, time, or enabled status MUST recalculate the next schedule according to existing calendar rules, preserve executed occurrences, and MUST NOT create a retroactive execution.
- **FR-014**: A disabled configuration MUST remain eligible for manual execution while remaining excluded from automatic scheduling.
- **FR-015**: The system MUST provide a manual execution action from the existing configuration view.
- **FR-016**: Manual execution MUST validate all required configuration data before creating an execution and MUST reuse the existing MiningExecution and mining processing flow.
- **FR-017**: A manual request MUST be rejected when another execution for the same configuration is active, and the rejection MUST NOT create another execution record.
- **FR-018**: A configuration with a compromised credential MUST be rejected for manual execution until the credential is replaced according to existing credential rules.
- **FR-019**: A successful manual request MUST provide the execution identifier to the interface for existing snapshot and live monitoring.
- **FR-020**: Manual execution monitoring MUST reuse the existing persisted snapshot, temporary access ticket, real-time updates, terminal states, canonical counters, reconnection, and report behavior.
- **FR-021**: Errors for missing configurations, load/update failures, invalid GitLab connections, compromised credentials, active executions, failed starts, and field validation MUST be presented safely without exposing secrets.
- **FR-022**: Editing MUST preserve prior executions, checkpoints, commit verifications, UnauthorizedCommitAlerts, and existing audit records.
- **FR-023**: The feature MUST preserve baseline, incremental processing, verification idempotency, original alert ownership, execution states, canonical counters, compromised-credential handling, persistent scheduling, history-divergence recovery, and existing real-time monitoring contracts.
- **FR-024**: The configuration `PATCH` operation MUST update only basic configuration fields, specifically the configuration name, timezone, and `enabled` status; `enabled` MUST be updated through PATCH and MUST NOT require GitLab connection validation. PATCH MUST NOT directly update scope, repositories, branch, allowed users, schedule, or credentials.
- **FR-025**: The configuration interface MAY present all editable data together, but persistence MUST use the dedicated existing operation for each group of scope, repositories, branch, allowed-user, schedule, and credential data. The frontend MUST call PATCH for basic fields, including `enabled`, and the canonical dedicated operations for all other groups.
- **FR-026**: A validated GitLab connection MUST be required for loading groups, subgroups, repositories, or branches, for selecting a branch, and for updating scope or repository selections. When validation is absent or invalid, each such operation MUST be rejected with the functional error code `connection_not_validated` and the conflict HTTP status defined by the application contracts. Updating `enabled`, allowed users, or schedule MUST NOT require GitLab connection validation.
- **FR-027**: Fixtures and tests MUST use exclusively synthetic, sentinel, or other fictitious non-sensitive values; no real token or credential may be used, and test values MUST NOT appear in plaintext in HTTP responses, logs, error messages, or test snapshots.

### Key Entities

- **MiningConfiguration**: The persisted configuration being viewed and edited, including connection reference, scope, branch, allowed users, schedule, and enabled status.
- **ConfigurationEdit**: The validated set of changes applied to an existing configuration without creating a replacement configuration.
- **ConnectionValidation**: The successful validation state tied to the current GitLab URL and credential reference.
- **MiningExecution**: The existing execution record created by a valid manual request and linked to the existing mining flow.
- **RepositoryCheckpoint**: Incremental state identified by configuration, repository, and branch and preserved across scope edits.
- **CommitVerification**: The durable author validation record reused across executions.
- **UnauthorizedCommitAlert**: The historical alert owned by the execution that originally detected it.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In all supported edit scenarios, reopening a saved configuration displays the persisted values for every non-sensitive editable field.
- **SC-002**: In 100% of edit attempts that change the GitLab connection, dependent scope or branch data is rejected until the new connection is successfully validated.
- **SC-003**: In 100% of configuration reads and edit responses, no plaintext credential value is returned.
- **SC-004**: In 100% of valid manual execution requests, exactly one new execution identifier is returned and the existing mining flow is used.
- **SC-005**: In 100% of concurrent manual execution attempts for one configuration, at most one active execution exists and rejected attempts create no second execution.
- **SC-006**: In 100% of branch or repository scope changes, prior checkpoints, verifications, alerts, and execution history remain queryable and unchanged.
- **SC-007**: In 100% of allowed-user changes, previously completed commit verifications are reused without creating duplicate alerts or reprocessing historical commits.
- **SC-008**: In 100% of schedule edits, the next occurrence reflects the new settings, while already executed occurrences remain in history and no retroactive run is created.
- **SC-009**: An operator can start a valid manual run and reach its execution snapshot or live monitoring view in one continuous workflow.
- **SC-010**: In 100% of edit attempts, basic fields are persisted through the basic configuration operation while scope, branch, allowed-user, schedule, and credential changes use their dedicated operations.
- **SC-011**: In 100% of dependent operations attempted after connection invalidation, the response uses `connection_not_validated` and the defined conflict status until validation succeeds.
- **SC-012**: In 100% of automated tests and fixtures, no real credential is used, `enabled` is persisted through the basic configuration operation, and no synthetic test value appears in plaintext in responses, logs, errors, or snapshots.

## Assumptions

- The feature extends the existing Repository Miner configuration, execution, checkpoint, credential, scheduler, reporting, and WebSocket behavior.
- Operators already have a valid authenticated identity supplied by the hosting environment; this feature does not create local accounts.
- The GitLab instance URL and credential are supplied by the operator, but credential values remain write-only.
- Existing authorization, connection validation, incremental processing, and credential incident rules remain authoritative.
- Manual execution is allowed for disabled configurations but not for configurations with compromised credentials or active executions.
- Mobile-specific layout and bulk editing of multiple configurations are outside this feature.
