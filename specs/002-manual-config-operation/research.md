# Research: Manual Configuration Operation and Editing

## Decision 1: Reuse the existing configuration aggregate

- **Decision**: Use `MonitoringConfiguration` and its existing credential, scope, allowed-user,
  schedule, and validation fields. Add no parallel configuration entity.
- **Rationale**: The current model already separates the mutable configuration from immutable
  mining history and exposes the connection-validation markers needed by FR-006/FR-007.
- **Alternatives considered**: Creating a versioned replacement configuration was rejected because
  it would complicate references and risk breaking checkpoint identity.

## Decision 2: Keep PATCH narrow and dedicated operations canonical

- **Decision**: `PATCH /configurations/{configurationId}` updates only basic fields (name, timezone,
  and enabled status). Scope, repositories, branch, allowed users, schedule, connection validation,
  and credentials continue through their existing dedicated operations.
- **Rationale**: A single editor can still present all data while each persistence boundary keeps
  its own validation and audit rules. This avoids conflicting update paths.
- **Alternatives considered**: A single PATCH payload containing all configuration data was rejected
  because it would duplicate the dedicated operations and make connection validation ordering
  ambiguous.

## Decision 3: Keep credential values write-only

- **Decision**: Return only credential status/reference metadata; accept a replacement token only
  on an explicit write operation and preserve the current credential when omitted.
- **Rationale**: This follows the constitution and existing encrypted `CredentialReference` model.
- **Alternatives considered**: Returning a masked token was rejected because it can still disclose
  secret material and is not needed to edit a configuration.

## Decision 4: Reuse the existing manual execution application service

- **Decision**: Manual execution calls the existing `start_persistent_execution` flow and returns
  its `execution_id`; scheduled execution remains on the same service.
- **Rationale**: This preserves concurrency checks, credential guards, snapshots, checkpoints,
  idempotency, events, and failure isolation in one place.
- **Alternatives considered**: A frontend-specific or configuration-specific runner was rejected
  because it would create divergent mining behavior.

## Decision 5: Preserve incremental identities on edits

- **Decision**: Checkpoints remain keyed by `(configuration_id, repository_id, branch)`, commit
  verifications by `(configuration_id, repository_id, branch, commit_hash)`, and alerts remain owned
  by their original detection execution.
- **Rationale**: Adding a repository or branch naturally enters baseline; removing scope only stops
  future selection and never deletes historical records.
- **Alternatives considered**: Resetting or copying checkpoints on every edit was rejected because
  it would reprocess history or destroy traceability.

## Decision 6: Preserve current real-time monitoring contracts

- **Decision**: The manual-start response exposes the existing execution identifier and the UI opens
  the existing REST snapshot plus temporary-ticket/realtime flow.
- **Rationale**: The database remains authoritative and reconnect behavior is already defined.
- **Alternatives considered**: A separate manual-progress channel was rejected as duplicate state.

## Decision 7: Use synthetic credentials in tests

- **Decision**: Fixtures and tests use only non-sensitive synthetic tokens, sentinel values, or
  fictitious secrets and assert that they never appear in plaintext outputs.
- **Rationale**: This enforces the constitution's credential-security rule without requiring live
  GitLab access.
- **Alternatives considered**: Reusing development or operator tokens was rejected as unsafe and
  unnecessary for deterministic tests.
