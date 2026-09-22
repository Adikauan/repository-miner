import { render, screen } from "@testing-library/react";
import { expect, it, vi } from "vitest";
import { PlanDetailsPage } from "../../src/plans/PlanDetailsPage";
import { planApi } from "../../src/plans/api";
import { syntheticPlan } from "./fixtures";
vi.mock("../../src/plans/api", () => ({ planApi: { get: vi.fn(), startExecution: vi.fn(), listExecutions: vi.fn() } }));
vi.mock("../../src/plans/PlanConfigurationTab", () => ({ PlanConfigurationTab: () => <div>config content</div> }));
it("renders exactly configuration and executions tabs", async () => { vi.mocked(planApi.get).mockResolvedValue(syntheticPlan); render(<PlanDetailsPage planId={syntheticPlan.id} tab="configuration" onTab={vi.fn()} onBack={vi.fn()} onExecution={vi.fn()} />); expect(await screen.findByText("config content")).toBeInTheDocument(); expect(screen.getAllByRole("tab").map((tab) => tab.textContent)).toEqual(["Configuração", "Execuções"]); });
