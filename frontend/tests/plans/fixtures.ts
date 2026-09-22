import type { PaginatedPlanPage, PlanExecutionSummary, VerificationPlanSummary } from "../../src/plans/types";

export const syntheticPlan: VerificationPlanSummary = {
  id: "00000000-0000-4000-8000-000000000001",
  name: "Plano sintético",
  gitlab_base_url: "https://gitlab.example.com/",
  timezone: "America/Sao_Paulo",
  enabled: true,
  target_branch: "main",
  credential_status: "active",
  connection_validated: true,
  schedule_summary: { recurrence: "weekly", local_time: "09:00", weekday: 1, day_of_month: null },
  last_execution: { id: "execution-synthetic", status: "completed", started_at: "2026-09-21T12:00:00Z", finished_at: "2026-09-21T12:01:00Z" },
};

export const syntheticExecution: PlanExecutionSummary = {
  id: "execution-synthetic", configuration_id: syntheticPlan.id, origin: "manual", status: "completed",
  started_at: "2026-09-21T12:00:00Z", finished_at: "2026-09-21T12:01:00Z",
  repositories_total: 4, repositories_completed: 4, repositories_failed: 0,
  commits_discovered: 12, commits_verified: 12, allowed_commits: 11, unauthorized_commits: 1,
};

export const syntheticPlanPage = (items: VerificationPlanSummary[] = [syntheticPlan], page = 1, limit = 20, total = items.length): PaginatedPlanPage => ({
  items, offset: (page - 1) * limit, limit, total, total_pages: total ? Math.ceil(total / limit) : 0,
});
