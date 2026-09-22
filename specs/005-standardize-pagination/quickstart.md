# Quickstart: Validar Paginação Cronológica

## Prerequisites

- Python environment with backend dependencies installed.
- Node dependencies installed in `frontend`.
- Synthetic test database; no GitLab credentials or network calls are required.

## Backend validation

From the repository root:

```powershell
python -m pytest backend/tests/contract/test_execution_list_contract.py backend/tests/contract/test_reporting_api.py backend/tests/integration/reporting -q
```

Expected result: tests verify execution `started_at DESC`, deterministic NULL `started_at` placement, stable IDs, filters before pagination, affected alert/failure endpoints, and unchanged envelopes.

## Frontend validation

```powershell
Set-Location frontend
npm test -- --run tests/plans/plan-executions-tab.test.tsx tests/reporting/report-page.test.tsx
npm run build
```

Expected result: the execution tab starts at page one, renders API order, uses its fixed page size of 20, and report consumers retain their fixed size of 50. No page-size selector is introduced.

## Manual API check

1. Seed at least three synthetic executions for one configuration with distinct, equal, and NULL `started_at` values.
2. Request `GET /api/v1/executions?configuration_id=<id>&offset=0&limit=2`, then offsets `2` and `4`.
3. Confirm non-null start times descend with NULLs last, NULL rows follow deterministic ID order, and equal timestamps follow ID order.
4. Add a newer execution and request offset `0` again; confirm it appears first.
5. Repeat with a status filter and confirm filtering precedes ordering and pagination.
6. Check `GET /api/v1/configurations` remains a non-paginated plan list and no independent CommitVerification endpoint or new page-size control exists.
