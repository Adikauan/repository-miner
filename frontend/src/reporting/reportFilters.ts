import { CommitVerificationItem, RepositoryReportItem, UnauthorizedCommit } from "./api";

export function filterRepositories(items: RepositoryReportItem[], query: string): RepositoryReportItem[] {
  const normalized = query.trim().toLowerCase();
  return normalized ? items.filter((item) => `${item.repository_id} ${item.branch} ${item.status}`.toLowerCase().includes(normalized)) : items;
}

export function filterCommits(items: CommitVerificationItem[], query: string): CommitVerificationItem[] {
  const normalized = query.trim().toLowerCase();
  return normalized ? items.filter((item) => `${item.commit_hash} ${item.repository ?? ""} ${item.author ?? ""} ${item.author_email ?? ""}`.toLowerCase().includes(normalized)) : items;
}

export function filterAlerts(items: UnauthorizedCommit[], query: string): UnauthorizedCommit[] {
  const normalized = query.trim().toLowerCase();
  return normalized ? items.filter((item) => `${item.commit_hash} ${item.repository_id} ${item.author_name ?? ""} ${item.author_email ?? ""}`.toLowerCase().includes(normalized)) : items;
}
