import { render, screen } from "@testing-library/react";
import { expect, it, vi } from "vitest";
import { PlanExecutionsTab } from "../../src/plans/PlanExecutionsTab";
import { planApi } from "../../src/plans/api";
import { syntheticExecution } from "./fixtures";
vi.mock("../../src/plans/api", () => ({ planApi: { listExecutions: vi.fn() } }));
it("loads only the current plan page, timestamps and seven canonical counters", async () => { vi.mocked(planApi.listExecutions).mockResolvedValue({ items: [syntheticExecution], offset: 0, limit: 20 }); render(<PlanExecutionsTab planId="plan-current" onDetails={vi.fn()} />); expect(await screen.findByText("execution-synthetic")).toBeVisible(); expect(planApi.listExecutions).toHaveBeenCalledWith({ configuration_id: "plan-current", offset: 0, limit: 20 }); expect(screen.getByText("Repositories totais")).toBeVisible(); expect(screen.getByText("Commits não autorizados")).toBeVisible(); expect(screen.getByText(/término:/)).toBeVisible(); });
