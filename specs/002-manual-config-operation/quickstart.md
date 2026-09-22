# Quickstart: Manual Configuration Operation and Editing

This guide validates the feature against the existing Repository Miner services without requiring
real GitLab credentials.

## Prerequisites

- Python 3.13 and the backend test dependencies installed.
- Node.js and frontend dependencies installed.
- A test database configured for the existing persistence layer.
- A fake GitLab gateway and authenticated-operator fixture.

## Backend validation

From `backend/`:

```powershell
pytest tests/unit/configuration tests/integration/configuration tests/integration/executions
```

Expected scenarios:

1. Create a configuration and validate its GitLab connection.
2. Read the configuration and confirm all non-sensitive values are populated while no token is
   returned.
3. Update name, timezone, and enabled status through the basic PATCH operation; update scope,
   branch, allowed e-mails, schedule, connection validation, and credentials through their
   dedicated operations; reopen the configuration and verify persistence.
4. Change URL or credential and confirm dependent scope/branch writes are rejected until the new
   connection succeeds, with conflict code `connection_not_validated`.
5. Add a repository or branch and verify normal baseline behavior; remove one and verify historical
   checkpoints, verifications, alerts, and executions remain queryable.
6. Start a manual run for an enabled and a disabled configuration. Confirm one `execution_id`,
   reuse of the existing runner, and rejection for compromised credentials or active executions.

## Frontend validation

From `frontend/`:

```powershell
npm run build
npm test -- --run
```

Expected result: the editor loads persisted values, treats the credential as write-only, saves
updates without creating a duplicate configuration, and navigates to the existing execution
snapshot/live-monitoring flow after a successful manual start.

All automated scenarios must use synthetic or sentinel credentials only; verify that no such value
appears in plaintext in responses, logs, errors, or snapshots.

## Contract references

- Feature-specific REST delta: [contracts/openapi.yaml](./contracts/openapi.yaml)
- Existing execution and WebSocket contracts: `specs/001-gitlab-repository-mining/contracts/`
- Persisted entity invariants: [data-model.md](./data-model.md)

## Validation recorded

- `backend`: `pytest -q --disable-warnings` — 110 passed, 1 skipped.
- `backend`: `python -m compileall -q backend/src` — passed.
- `frontend`: `npm run build` — passed.
- `frontend`: `npm test -- --run --passWithNoTests` — 6 passed.
