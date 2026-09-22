# Data Model: Paginação Cronológica

## Paginated collection

| Field | Meaning | Rule |
|---|---|---|
| `items` | Records in one page | Ordered by the backend before slicing. |
| `offset` | Zero-based start position | Applied after filters and ordering. |
| `limit` | Requested page size | Existing bounds remain unchanged (1–200 for execution/report endpoints). |
| `total` | Optional existing metadata | Preserve when already exposed; do not add only for this feature. |

## Canonical temporal projections

| Resource/list | Primary temporal field | Stable secondary field | Scope |
|---|---|---|---|
| Plan list | Not applicable | Not applicable | `GET /configurations` is not paginated and is outside this feature. |
| Executions | `started_at DESC NULLS LAST`; NULL values form the final deterministic group | `id DESC` | `MiningExecution`, filtered by configuration/status; no `created_at` is added. |
| Repository executions | Existing non-chronological domain order | Existing stable fields | Endpoint remains unchanged unless its current contract is chronological. |
| Commit verifications | No independent paginated projection | Not applicable | Indirect report behavior follows that report's contract. |
| Unauthorized alerts | `detected_at DESC` | `id DESC` | Alerts scoped to an execution. |
| Repository failures | `occurred_at DESC` | `id DESC` | Failure histories scoped to an execution. |
| Execution commits | Existing hash/domain order | Existing stable fields | Not a chronological CommitVerification list. |

## Relationships and invariants

- An execution belongs to one MonitoringConfiguration; configuration/status filters occur before pagination.
- `started_at IS NULL` executions are not assigned a synthetic timestamp; their group uses stable ID ordering.
- UnauthorizedCommitAlert and RepositoryFailure keep existing ownership and traceability relationships.
- CommitVerification is not exposed through a new list endpoint.
- Pagination is read-only and does not alter mining, scheduler, checkpoint, baseline, verification, or counter state.
- A stable dataset traversed page by page yields every eligible record once.
