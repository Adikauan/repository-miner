import type { PlanExecutionSummary } from "../../src/plans/types";

export function paginatedExecution(id: string, startedAt: string): PlanExecutionSummary {
  return {
    id,
    configuration_id: "plan-current",
    origin: "manual",
    status: "completed",
    started_at: startedAt,
    finished_at: null,
    repositories_total: 1,
    repositories_completed: 1,
    repositories_failed: 0,
    commits_discovered: 1,
    commits_verified: 1,
    allowed_commits: 1,
    unauthorized_commits: 0,
  };
}
