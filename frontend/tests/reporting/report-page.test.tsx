import { cleanup, render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ReportDetailPage } from "../../src/reporting/ReportDetailPage";
import * as api from "../../src/reporting/api";

vi.mock("../../src/reporting/api", () => ({ getReport: vi.fn(), getRepositories: vi.fn(), getCommits: vi.fn(), getUnauthorizedCommits: vi.fn(), getRepositoryFailures: vi.fn() }));

describe("report page", () => {
  it("shows canonical counters, unauthorized commits, and failure causes", async () => {
    vi.mocked(api.getReport).mockResolvedValue({ execution_id: "exec-1", status: "partially_completed", repositories_total: 2, repositories_completed: 1, repositories_failed: 1, commits_discovered: 3, commits_verified: 2, allowed_commits: 1, unauthorized_commits: 1 });
    vi.mocked(api.getRepositories).mockResolvedValue({ items: [], offset: 0, limit: 50 });
    vi.mocked(api.getCommits).mockResolvedValue({ items: [], offset: 0, limit: 50 });
    vi.mocked(api.getUnauthorizedCommits).mockResolvedValue({ items: [{ id: "alert-1", repository_id: "repo-1", branch: "QA", commit_hash: "abc123", author_name: "Eve", author_email: null, committed_at: "2026-01-01T00:00:00Z" }] });
    vi.mocked(api.getRepositoryFailures).mockResolvedValue({ items: [{ id: "failure-1", repository_execution_id: "re-1", code: "history_diverged", safe_reason: "Histórico divergente", occurred_at: "2026-01-01T00:00:00Z" }] });
    render(<ReportDetailPage executionId="exec-1" onBack={vi.fn()} />);
    await waitFor(() => expect(screen.getByText("partially_completed")).toBeInTheDocument());
    expect(screen.getByText("3")).toBeInTheDocument();
    expect(screen.getByText("abc123")).toBeInTheDocument();
    expect(screen.getByText("Eve")).toBeInTheDocument();
    expect(screen.getByText("history_diverged: Histórico divergente")).toBeInTheDocument();
  });

  it("keeps the persisted terminal report authoritative over transient state", async () => {
    for (const status of ["completed", "partially_completed", "failed"] as const) {
      vi.mocked(api.getReport).mockResolvedValue({ execution_id: `exec-${status}`, status, repositories_total: 7, repositories_completed: 5, repositories_failed: 2, commits_discovered: 11, commits_verified: 9, allowed_commits: 4, unauthorized_commits: 5 });
      vi.mocked(api.getRepositories).mockResolvedValue({ items: [], offset: 0, limit: 50 });
      vi.mocked(api.getCommits).mockResolvedValue({ items: [], offset: 0, limit: 50 });
      vi.mocked(api.getUnauthorizedCommits).mockResolvedValue({ items: [], offset: 0, limit: 50 });
      vi.mocked(api.getRepositoryFailures).mockResolvedValue({ items: [], offset: 0, limit: 50 });
      const { rerender } = render(<ReportDetailPage executionId={`exec-${status}`} onBack={vi.fn()} />);
      await waitFor(() => expect(screen.getByText(status)).toBeInTheDocument());
      expect(screen.getByText("11")).toBeInTheDocument();
      expect(screen.getByText("9")).toBeInTheDocument();
      expect(screen.getByText("4")).toBeInTheDocument();
      expect(screen.getAllByText("5").length).toBeGreaterThan(0);
      rerender(<ReportDetailPage executionId={`exec-${status}`} onBack={vi.fn()} />);
      expect(screen.getByText(status)).toBeInTheDocument();
      cleanup();
    }
  });
});
