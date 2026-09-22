# Pagination Ordering Contract

Base path: `/api/v1`. Existing response envelopes, filters, and pagination parameters remain compatible.

## Affected existing endpoints

Only these existing paginated endpoints are changed or verified by this feature:

- `GET /executions?configuration_id={id}&status={status}&offset={offset}&limit={limit}`
- `GET /executions/{execution_id}/repositories?offset={offset}&limit={limit}`
- `GET /executions/{execution_id}/commits?offset={offset}&limit={limit}`
- `GET /executions/{execution_id}/failures?offset={offset}&limit={limit}`
- `GET /executions/{execution_id}/unauthorized-commits?offset={offset}&limit={limit}`
- `GET /executions/{execution_id}/failures-detail?offset={offset}&limit={limit}`

No new endpoint is introduced. `GET /configurations` is not paginated and remains outside the feature. No independent paginated CommitVerification endpoint exists or will be created.

## Ordering guarantee

For an affected endpoint with chronological semantics:

1. Apply resource filters.
2. Order by the canonical temporal field descending with documented NULL handling.
3. Order ties by the stable record identifier descending.
4. Apply `offset` and `limit`.

The API response is authoritative. Clients must display `items` in received order and must not reverse, sort, or merge pages locally.

## Execution history

- `configuration_id` and `status` filters are evaluated before pagination.
- `started_at DESC NULLS LAST` is the primary order when present.
- Rows with `started_at IS NULL` form the final deterministic NULL group ordered by execution `id DESC`; no `created_at` is added.
- Equal non-null timestamps are ordered by `id DESC`.
- `offset` defaults to `0`; `limit` defaults to `50` and remains bounded by `200`.
- `items`, `offset`, and `limit` retain their current shape.

## Report histories

- UnauthorizedCommitAlerts use `detected_at DESC, id DESC`.
- Failure lists use `occurred_at DESC, id DESC`.
- Repository and execution-commit lists retain their established non-chronological domain order.
- Any indirect CommitVerification data follows the report endpoint's existing contract.

## Page size and compatibility

- No current screen has an interactive page-size selector. `PlanExecutionsTab` uses fixed size 20; report consumers use fixed size 50.
- If a screen that already has a selector changes its size, it must issue a new query with the same ordering and follow its existing reset behavior.
- Existing invalid-pagination responses, envelopes, filters, counters, and error behavior remain unchanged.
