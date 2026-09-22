import { apiRequest } from "../shared/api/client";

export type Configuration = { id: string; name: string; gitlab_base_url: string; timezone?: string; enabled: boolean; target_branch: string | null; credential_status: string; connection_validated: boolean; next_run_at?: string | null; allowed_emails?: string[]; selections?: SelectionRule[]; schedule?: Schedule | null; schedule_summary?: { recurrence: "daily" | "weekly" | "monthly"; local_time: string; weekday: number | null; day_of_month: number | null } | null; last_execution?: { id: string; status: string; started_at: string | null; finished_at: string | null } | null };
export type PaginatedConfigurations = { items: Configuration[]; offset: number; limit: number; total: number; total_pages: number };
export type TreeNode = { id: string; kind: "group" | "subgroup" | "repository"; name?: string; path?: string; full_path?: string; web_url?: string | null; children?: TreeNode[] };
export type SelectionRule = { kind: string; mode: "include" | "exclude"; external_id: string };
export type Schedule = { recurrence: "daily" | "weekly" | "monthly"; local_time: string; weekday?: number; day_of_month?: number; timezone: string };
export type CredentialIncident = { id: string; credential_id: string; status: string; suspected_by: string; suspected_at: string };
export type CredentialReplacement = { id: string; previous_credential_id: string; replacement_credential_id: string; reason: "preventive" | "compromise_remediation"; replaced_by: string; replaced_at: string };
export function listConfigurations(params: { offset?: number; limit?: number } = {}) {
  const offset = Math.max(0, params.offset ?? 0);
  const limit = Math.min(200, Math.max(1, params.limit ?? 20));
  return apiRequest<PaginatedConfigurations>(`/configurations?offset=${offset}&limit=${limit}`);
}
export function getConfiguration(id: string) { return apiRequest<Configuration>(`/configurations/${id}`); }
export function createConfiguration(body: { name: string; gitlab_base_url: string; gitlab_token: string; timezone?: string; enabled?: boolean }) { return apiRequest<Configuration>("/configurations", { method: "POST", body: JSON.stringify(body) }); }
export function validateConnection(id: string) { return apiRequest<{ validated: boolean }>(`/configurations/${id}/connection-test`, { method: "POST" }); }
export function getGitLabTree(id: string) { return apiRequest<{ items: TreeNode[] }>(`/configurations/${id}/gitlab-tree`); }
export function getBranches(id: string, repositoryId: string) { return apiRequest<{ items: string[] }>(`/configurations/${id}/repositories/${repositoryId}/branches`); }
export function saveScope(id: string, target_branch: string, rules: SelectionRule[]) { return apiRequest(`/configurations/${id}/repository-selections`, { method: "PUT", body: JSON.stringify({ target_branch, rules }) }); }
export function saveAllowedUsers(id: string, emails: string[]) { return apiRequest(`/configurations/${id}/allowed-users`, { method: "PUT", body: JSON.stringify({ emails }) }); }
export function startExecution(id: string) { return apiRequest<{ id: string; execution_id?: string }>(`/configurations/${id}/executions`, { method: "POST" }); }
export function saveSchedule(id: string, schedule: Schedule) { return apiRequest(`/configurations/${id}/schedule`, { method: "PUT", body: JSON.stringify(schedule) }); }
export function compromiseCredential(id: string) { return apiRequest(`/configurations/${id}/credential-incidents`, { method: "POST" }); }
export function replaceCredential(id: string, gitlab_token: string, reason: "preventive" | "compromise_remediation") { return apiRequest(`/configurations/${id}/credential-replacements`, { method: "POST", body: JSON.stringify({ gitlab_token, reason }) }); }
export function updateConfiguration(id: string, body: { name?: string; timezone?: string; enabled?: boolean }) { return apiRequest(`/configurations/${id}`, { method: "PATCH", body: JSON.stringify(body) }); }
export function updateConnection(id: string, body: { gitlab_base_url: string; gitlab_token?: string; reason?: "preventive" | "compromise_remediation" }) { return apiRequest(`/configurations/${id}/connection`, { method: "PUT", body: JSON.stringify(body) }); }
