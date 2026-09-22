# WebSocket Event Contract

## Endpoint and authority

`GET ws(s)://<host>/api/v1/ws/executions/{execution_id}?ticket=<one-time-ticket>`

The socket carries best-effort notifications only. Relational state and REST snapshots are
authoritative. Disconnecting a client never pauses or changes mining.

Before every connection attempt, the client obtains a ticket through authenticated REST:
`POST /api/v1/executions/{execution_id}/websocket-tickets`. The opaque ticket is bound to the
authenticated operator and execution, expires after 60 seconds, and is atomically consumed by the
first valid connection. Invalid, expired, consumed, or incorrectly scoped tickets receive the same
generic policy rejection (close code `1008` after protocol upgrade).

The HTTP adapter obtains the operator from `AuthenticatedOperatorProvider`, validates the
host-supplied identity, and authorizes access to the execution before ticket issuance. The request
does not contain an operator ID. Missing or invalid identity prevents issuance with `401`, and a
valid operator without access receives `403`. The MVP has no operator registration, login,
password, or account-management endpoint; replacing the host authentication adapter does not alter
the ticket use case or this WebSocket protocol.

During the upgrade request, the host authentication adapter also supplies the validated operator
identity independently of the ticket value. Atomic consumption succeeds only when this operator
matches the stored `operator_id`, the route matches the stored `execution_id`, `expires_at` is in
the future, and `consumed_at` is null; it then sets `consumed_at`. A wrong-operator or
wrong-execution attempt receives the same generic policy rejection and does not consume a valid
ticket.

GitLab credentials and persistent application credentials are never accepted as WebSocket
credentials. Ticket values are redacted from access logs and diagnostics.

On page load or reconnect, the client:

1. Fetches the authoritative execution snapshot through REST.
2. Obtains a fresh one-use ticket through a host-authenticated REST request.
3. Opens the WebSocket using that ticket.
4. Refetches the snapshot after subscription to close the connection race.
5. Applies only events with revision greater than the snapshot revision.
6. Refetches on a revision gap, malformed/unknown event, reconnect, or terminal event.

## Envelope

```json
{
  "schema_version": "1",
  "event_id": "0199...",
  "type": "repository.progress",
  "occurred_at": "2026-09-19T15:04:05Z",
  "execution_id": "0199...",
  "configuration_id": "0199...",
  "repository_id": "0199...",
  "revision": 12,
  "payload": {}
}
```

Rules:

- Revision increases monotonically per execution and commits with the durable state change.
- Duplicate or stale events (`revision <= current`) are ignored.
- A gap (`revision > current + 1`) triggers REST refetch.
- Events contain no credential values or full reports.
- `repository.progress` is coalesced to at most once per second per repository unless state changes.

## Event types

| Type | Required payload |
|---|---|
| `execution.started` | `status`, `started_at`, `repositories_total`, `repositories_completed`, `repositories_failed` |
| `repository.started` | `repository_execution_id`, `status`, `started_at` |
| `repository.progress` | `repository_execution_id`, `commits_discovered`, `commits_verified`, `allowed_commits`, `unauthorized_commits` |
| `unauthorized_commit.detected` | `alert_id`, `repository_execution_id`, `commit_hash` |
| `repository.completed` | `repository_execution_id`, `status`, `finished_at`, `counters` |
| `repository.failed` | `repository_execution_id`, `status`, `finished_at`, `failure_id` |
| `execution.completed` | `status`, `finished_at`, `summary_counts` |
| `execution.partially_completed` | `status`, `finished_at`, `summary_counts`, `terminal_reason` |
| `execution.failed` | `status`, `finished_at`, `summary_counts`, `terminal_reason` |

Status values are exactly `pending`, `running`, `completed`, `partially_completed`, and `failed`.
A successful run with no new commits emits `execution.completed` with `commits_discovered = 0` and
`commits_verified = 0`. Summary counters use `repositories_total`, `repositories_completed`,
`repositories_failed`, `commits_discovered`, `commits_verified`, `allowed_commits`, and
`unauthorized_commits`.

`unauthorized_commit.detected` contains only identifiers. The frontend retrieves traceable commit
details through REST. Terminal events instruct the client to fetch the final report.

Progress and summary counters describe work newly performed by the current execution. Recognizing
an `ExecutionCommit` whose `verification_source` is `reused` does not increment `commits_verified`,
`allowed_commits`, or `unauthorized_commits` and does not emit `unauthorized_commit.detected`.

## Delivery behavior

- Delivery is at-most-once; no replay log is promised.
- Server restart or network loss may drop events without losing durable state.
- Reconnect uses exponential backoff with jitter capped at 30 seconds and a fresh ticket per attempt.
- Multiple clients may observe an execution without affecting runner state.
- The in-memory connection manager assumes one application process in the MVP.
