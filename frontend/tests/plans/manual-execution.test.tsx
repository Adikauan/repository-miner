import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { expect, it, vi } from "vitest";
import { PlanDetailsPage } from "../../src/plans/PlanDetailsPage";
import { planApi } from "../../src/plans/api";
import { syntheticPlan } from "./fixtures";
vi.mock("../../src/plans/api", () => ({ planApi: { get: vi.fn(), startExecution: vi.fn(), listExecutions: vi.fn() } }));
vi.mock("../../src/plans/PlanConfigurationTab", () => ({ PlanConfigurationTab: () => <div>configuration</div> }));
it("starts a disabled plan manually and navigates using execution_id", async () => { vi.mocked(planApi.get).mockResolvedValue({ ...syntheticPlan, enabled: false }); vi.mocked(planApi.startExecution).mockResolvedValue({ id: "ignored", execution_id: "execution-new" }); const navigate = vi.fn(); render(<PlanDetailsPage planId={syntheticPlan.id} tab="configuration" onTab={vi.fn()} onBack={vi.fn()} onExecution={navigate} />); fireEvent.click(await screen.findByRole("button", { name: "Executar agora" })); await waitFor(() => expect(navigate).toHaveBeenCalledWith("execution-new", false)); });
it.each(["execution_conflict", "credential_unavailable"])("shows a safe rejection for %s", async (code) => { vi.mocked(planApi.get).mockResolvedValue(syntheticPlan); vi.mocked(planApi.startExecution).mockRejectedValueOnce({ code, message: "safe" }); render(<PlanDetailsPage planId={syntheticPlan.id} tab="configuration" onTab={vi.fn()} onBack={vi.fn()} onExecution={vi.fn()} />); fireEvent.click(await screen.findByRole("button", { name: "Executar agora" })); expect(await screen.findByText(/Não foi possível iniciar/)).toBeVisible(); });
