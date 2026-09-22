import { CommitVerificationItem, ExecutionReport, RepositoryFailure, RepositoryReportItem, UnauthorizedCommit } from "../api";

export const reportFixture: ExecutionReport = {
  execution_id: "execution-synthetic",
  configuration_id: "configuration-synthetic",
  status: "completed",
  repositories_total: 2,
  repositories_completed: 1,
  repositories_failed: 1,
  commits_discovered: 3,
  commits_verified: 3,
  allowed_commits: 1,
  unauthorized_commits: 2,
};
export const repositoryFixture: RepositoryReportItem = { id: "repo-execution-synthetic", repository_id: "repository-synthetic", branch: "qa", status: "completed" };
export const commitFixture: CommitVerificationItem = { commit_hash: "commit-synthetic", repository: "repository-synthetic", branch: "qa", author: "Synthetic Author", author_email: null, authorization_result: "unauthorized" };
export const alertFixture: UnauthorizedCommit = { id: "alert-synthetic", repository_id: "repository-synthetic", branch: "qa", commit_hash: "commit-synthetic", author_name: "Synthetic Author", author_email: null, committed_at: null, detection_execution_id: "execution-synthetic" };
export const failureFixture: RepositoryFailure = { id: "failure-synthetic", repository_execution_id: "repo-execution-synthetic", repository_id: "repository-synthetic", branch: "qa", code: "gitlab_unavailable", safe_reason: "GitLab indisponível.", occurred_at: null };
