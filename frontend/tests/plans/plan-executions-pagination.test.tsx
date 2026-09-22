import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { expect, it, vi } from "vitest";
import { PlanExecutionsTab } from "../../src/plans/PlanExecutionsTab";
import { planApi } from "../../src/plans/api";
import { paginatedExecution } from "./pagination-fixtures";

vi.mock("../../src/plans/api", () => ({ planApi: { listExecutions: vi.fn() } }));

it("navigates pages without reordering API items", async () => {
  const firstPage = Array.from({ length: 20 }, (_, index) => paginatedExecution(`new-${index}`, `2026-09-${String(20 - index).padStart(2, "0")}T12:00:00Z`));
  vi.mocked(planApi.listExecutions)
    .mockResolvedValueOnce({ items: firstPage, offset: 0, limit: 20 })
    .mockResolvedValueOnce({ items: [paginatedExecution("old-page", "2026-01-01T12:00:00Z")], offset: 20, limit: 20 });
  render(<PlanExecutionsTab planId="plan-current" onDetails={vi.fn()} />);
  expect(await screen.findByText("new-0")).toBeVisible();
  fireEvent.click(screen.getByLabelText("Go to page 2"));
  await waitFor(() => expect(screen.getByText("old-page")).toBeVisible());
  expect(planApi.listExecutions).toHaveBeenLastCalledWith({ configuration_id: "plan-current", offset: 20, limit: 20 });
});
