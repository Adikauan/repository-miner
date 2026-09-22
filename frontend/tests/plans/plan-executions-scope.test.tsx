import { render, screen } from "@testing-library/react";
import { expect, it, vi } from "vitest";
import { PlanExecutionsTab } from "../../src/plans/PlanExecutionsTab";
import { planApi } from "../../src/plans/api";

vi.mock("../../src/plans/api", () => ({ planApi: { listExecutions: vi.fn() } }));

it("requests the selected plan's first page and preserves newest API order", async () => {
  vi.mocked(planApi.listExecutions).mockResolvedValue({ items: [
    { id: "newest", configuration_id: "plan-new", origin: "manual", status: "completed", started_at: "2026-09-21T12:00:00Z", finished_at: null, repositories_total: 0, repositories_completed: 0, repositories_failed: 0, commits_discovered: 0, commits_verified: 0, allowed_commits: 0, unauthorized_commits: 0 },
    { id: "older", configuration_id: "plan-new", origin: "manual", status: "completed", started_at: "2026-09-20T12:00:00Z", finished_at: null, repositories_total: 0, repositories_completed: 0, repositories_failed: 0, commits_discovered: 0, commits_verified: 0, allowed_commits: 0, unauthorized_commits: 0 },
  ], offset: 0, limit: 20 });
  render(<PlanExecutionsTab planId="plan-new" onDetails={vi.fn()} />);
  expect(await screen.findByText("newest")).toBeVisible();
  expect(screen.getByText("older")).toBeVisible();
  expect(planApi.listExecutions).toHaveBeenCalledWith({ configuration_id: "plan-new", offset: 0, limit: 20 });
});
