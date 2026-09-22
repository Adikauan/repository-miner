import { render, screen } from "@testing-library/react";
import { expect, it, vi } from "vitest";
import { PlanListPage } from "../../src/plans/PlanListPage";
import { PlanExecutionsTab } from "../../src/plans/PlanExecutionsTab";
import { planApi } from "../../src/plans/api";
import { syntheticPlan, syntheticPlanPage } from "./fixtures";
vi.mock("../../src/plans/api", () => ({ planApi: { list: vi.fn(), listExecutions: vi.fn() } }));
it("reaches a usable controlled list in at most two seconds", async () => { vi.mocked(planApi.list).mockResolvedValue(syntheticPlanPage([syntheticPlan])); const start = performance.now(); render(<PlanListPage onOpen={vi.fn()} />); await screen.findByRole("button", { name: "Visualizar configuração" }, { timeout: 2000 }); expect(performance.now() - start).toBeLessThanOrEqual(2000); });
it("reaches a usable controlled history in at most two seconds", async () => { vi.mocked(planApi.listExecutions).mockResolvedValue({ items: [], offset: 0, limit: 20 }); const start = performance.now(); render(<PlanExecutionsTab planId="synthetic" onDetails={vi.fn()} />); await screen.findByText("Este plano ainda não possui execuções.", {}, { timeout: 2000 }); expect(performance.now() - start).toBeLessThanOrEqual(2000); });
