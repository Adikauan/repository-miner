# Data Model: Manual Configuration Operation and Editing

This feature reuses the persisted model defined by feature 001. No new durable entity is required.

## Existing entities used

### MonitoringConfiguration

Editable fields include name, GitLab URL/credential reference, scope selection, target branch,
allowed-user list, schedule parameters, timezone, and enabled status. The row identity remains
stable across edits. `connection_validated_at`, `validated_gitlab_base_url`, and
`validated_credential_id` describe validation for the exact current connection.

The basic configuration PATCH projection contains only name, timezone, and enabled status. Scope,
repositories, branch, allowed users, schedule, connection validation, and credential changes are
persisted through their dedicated operations.

### CredentialReference and CredentialReplacement

Credential values remain encrypted and write-only. Configuration projections expose only
`credential_status` (`active` or `compromised`). Omitting a replacement preserves the current
reference. A successful replacement points the configuration to the new active reference and keeps
the old reference and replacement audit historical.

### RepositorySelectionRule, AllowedUser, and Schedule

Scope rules, normalized allowed e-mails, and schedule values are replaced transactionally for the
existing configuration. Persisting scope or branch requires a successful validation matching the
current URL and credential reference. Schedule edits recalculate the next occurrence without
creating a retroactive run.

### MiningExecution

Manual start creates one execution with `trigger=manual` when supported by the existing model,
stores the immutable effective configuration snapshot, and reuses the canonical execution states
and counters. An active execution prevents creation of another one for the same configuration.

### Incremental and historical entities

`RepositoryCheckpoint` remains keyed by `(configuration_id, repository_id, branch)`.
`CommitVerification` remains keyed by `(configuration_id, repository_id, branch, commit_hash)`.
`UnauthorizedCommitAlert` remains owned by the original detection execution. Editing scope, branch,
allowed users, or credentials never deletes or mutates these records.

## Invariants

1. A configuration update cannot expose plaintext credentials.
2. A dependent scope/branch update cannot be persisted until the current connection is validated.
   When invalid, the operation returns `connection_not_validated` with the application's conflict
   HTTP status.
3. A new configuration/repository/branch combination starts with the normal baseline rule.
4. Removed scope remains queryable historically but is excluded from future execution selection.
5. Allowed-user changes affect future validations only.
6. Manual execution is allowed when disabled, rejected for compromised credentials, and rejected
   when another execution is pending or running.
7. Test fixtures contain only synthetic or sentinel credentials, and those values are never emitted
   in plaintext by responses, logs, errors, or snapshots.
