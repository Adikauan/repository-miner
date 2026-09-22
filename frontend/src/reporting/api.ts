import { apiRequest } from "../shared/api/client";

export type ExecutionStatus = "pending" | "running" | "completed" | "partially_completed" | "failed";
export type Pagination = { offset: number; limit: number };
export type Page<T> = { items: T[]; offset: number; limit: number };
export type ExecutionReport = {
  execution_id: string;
  configuration_id?: string;
  origin?: string | null;
  started_at?: string | null;
  finished_at?: string | null;
  status: ExecutionStatus;
  repositories_total: number;
  repositories_completed: number;
  repositories_failed: number;
  commits_discovered: number;
  commits_verified: number;
  allowed_commits: number;
  unauthorized_commits: number;
};
export type RepositoryReportItem = { id?: string; repository_id: string; branch: string; status: string; commits_count?: number | null; observed_head?: string | null; failure_reason?: string | null };
export type CommitVerificationItem = { commit_hash: string; repository?: string | null; branch?: string | null; author?: string | null; author_email: string | null; committed_at?: string | null; message?: string | null; authorization_result?: "allowed" | "unauthorized" | string | null; verification_source?: string };
export type UnauthorizedCommit = { id: string; repository_id: string; branch: string; commit_hash: string; author_name: string | null; author_email: string | null; committed_at: string | null; detection_execution_id?: string | null };
export type RepositoryFailure = { id: string; repository_execution_id: string; repository_id?: string | null; branch?: string | null; stage?: string | null; code: string; safe_reason: string; occurred_at: string | null };

export function getReport(id: string) { return apiRequest<ExecutionReport>(`/executions/${id}/report`); }
export function getRepositories(id: string, pagination: Pagination = { offset: 0, limit: 50 }) { return apiRequest<Page<RepositoryReportItem>>(`/executions/${id}/repositories?offset=${pagination.offset}&limit=${pagination.limit}`); }
export function getCommits(id: string, pagination: Pagination = { offset: 0, limit: 50 }) { return apiRequest<Page<CommitVerificationItem>>(`/executions/${id}/commits?offset=${pagination.offset}&limit=${pagination.limit}`); }
export function getUnauthorizedCommits(id: string, pagination: Pagination = { offset: 0, limit: 50 }) { return apiRequest<Page<UnauthorizedCommit>>(`/executions/${id}/unauthorized-commits?offset=${pagination.offset}&limit=${pagination.limit}`); }
export function getRepositoryFailures(id: string, pagination: Pagination = { offset: 0, limit: 50 }) { return apiRequest<Page<RepositoryFailure>>(`/executions/${id}/failures?offset=${pagination.offset}&limit=${pagination.limit}`); }
