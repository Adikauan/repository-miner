import type { Configuration, Schedule, SelectionRule } from "../configurations/api";
import type { ExecutionStatus } from "../executions/api";

export type ScheduleSummary = Pick<Schedule, "recurrence" | "local_time"> & {
  weekday: number | null;
  day_of_month: number | null;
};

export type LastExecutionSummary = {
  id: string;
  status: ExecutionStatus;
  started_at: string | null;
  finished_at: string | null;
};

export type VerificationPlanSummary = Configuration & {
  schedule_summary?: ScheduleSummary | null;
  last_execution?: LastExecutionSummary | null;
};

export type VerificationPlanDetail = VerificationPlanSummary;

export type PaginatedPlanPage = {
  items: VerificationPlanSummary[];
  offset: number;
  limit: number;
  total: number;
  total_pages: number;
};

export type CreatePlanDraft = {
  name: string;
  gitlab_base_url: string;
  gitlab_token: string;
  timezone: string;
  enabled: boolean;
  target_branch: string;
  selections: SelectionRule[];
  allowed_emails: string[];
  schedule: Schedule;
};

export type ExecutionOrigin = "manual" | "scheduled";
export type PlanExecutionSummary = {
  id: string;
  configuration_id: string;
  origin: ExecutionOrigin;
  status: ExecutionStatus;
  started_at: string | null;
  finished_at: string | null;
  repositories_total: number;
  repositories_completed: number;
  repositories_failed: number;
  commits_discovered: number;
  commits_verified: number;
  allowed_commits: number;
  unauthorized_commits: number;
};

export type PaginatedExecutionPage = {
  items: PlanExecutionSummary[];
  offset: number;
  limit: number;
};
