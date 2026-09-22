import { apiRequest } from "../shared/api/client";

export type ExecutionStatus = "pending" | "running" | "completed" | "partially_completed" | "failed";
export type ExecutionSnapshot = { id: string; configuration_id: string; origin?: "manual" | "scheduled"; status: ExecutionStatus; started_at?: string | null; finished_at?: string | null; repositories_total?: number; repositories_completed?: number; repositories_failed?: number; commits_discovered?: number; commits_verified?: number; allowed_commits?: number; unauthorized_commits?: number };
export type ExecutionEvent = { schema_version: string; event_id: string; type: string; occurred_at: string; execution_id: string; configuration_id: string; repository_id?: string | null; revision: number; payload: Record<string, unknown> };

export function getExecution(id: string) { return apiRequest<ExecutionSnapshot>(`/executions/${id}`); }
export function listExecutions(params: { configuration_id?: string; status?: ExecutionStatus; offset?: number; limit?: number } = {}) {
  const query = new URLSearchParams();
  if (params.configuration_id) query.set("configuration_id", params.configuration_id);
  if (params.status) query.set("status", params.status);
  query.set("offset", String(Math.max(0, params.offset ?? 0)));
  query.set("limit", String(Math.min(200, Math.max(1, params.limit ?? 50))));
  return apiRequest<{ items: ExecutionSnapshot[]; offset: number; limit: number }>(`/executions?${query}`);
}
export function issueExecutionTicket(id: string) { return apiRequest<{ ticket: string; expires_at: string }>(`/executions/${id}/websocket-tickets`, { method: "POST" }); }
export function getExecutionRepositories(id: string, offset = 0) { return apiRequest<{ items: unknown[] }>(`/executions/${id}/repositories?offset=${offset}`); }
export function getExecutionCommits(id: string, offset = 0) { return apiRequest<{ items: unknown[] }>(`/executions/${id}/commits?offset=${offset}`); }
