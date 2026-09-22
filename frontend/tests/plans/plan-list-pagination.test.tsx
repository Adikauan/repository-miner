import { fireEvent, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { PlanListPage } from "../../src/plans/PlanListPage";
import { planApi } from "../../src/plans/api";
import { syntheticPlan, syntheticPlanPage } from "./fixtures";
import { renderPlanApp } from "./renderPlanApp";

vi.mock("../../src/plans/api", () => ({ planApi: { list: vi.fn(), createBase: vi.fn() } }));
vi.mock("../../src/plans/CreatePlanModal", () => ({ CreatePlanModal: ({ onCreated }: { onCreated: () => void }) => <button onClick={onCreated}>mock create</button> }));

describe("PlanListPage pagination", () => {
  beforeEach(() => vi.clearAllMocks());

  it("loads the first page and requests the next page from the API", async () => {
    const secondPlan = { ...syntheticPlan, id: "plan-2", name: "Plano dois" };
    vi.mocked(planApi.list)
      .mockResolvedValueOnce(syntheticPlanPage([syntheticPlan], 1, 20, 21))
      .mockResolvedValueOnce(syntheticPlanPage([secondPlan], 2, 20, 21));
    renderPlanApp(<PlanListPage onOpen={vi.fn()} />);

    expect(await screen.findByText(/Plano sint/)).toBeInTheDocument();
    expect(planApi.list).toHaveBeenCalledWith({ offset: 0, limit: 20 });
    fireEvent.click(screen.getByRole("button", { name: /page 2/i }));
    await waitFor(() => expect(screen.getByText("Plano dois")).toBeInTheDocument());
    expect(planApi.list).toHaveBeenLastCalledWith({ offset: 20, limit: 20 });
  });

  it("shows loading, error retry and no pagination for an empty page", async () => {
    vi.mocked(planApi.list).mockRejectedValueOnce(new Error("offline"));
    renderPlanApp(<PlanListPage onOpen={vi.fn()} />);
    expect(await screen.findByRole("button", { name: "Tentar novamente" })).toBeInTheDocument();
    vi.mocked(planApi.list).mockResolvedValueOnce(syntheticPlanPage([], 1, 20, 0));
    fireEvent.click(screen.getByRole("button", { name: "Tentar novamente" }));
    expect(await screen.findByText("Nenhum plano cadastrado.")).toBeInTheDocument();
    expect(screen.queryByRole("navigation", { name: "Paginação de planos" })).not.toBeInTheDocument();
  });

  it("returns to a valid page when the current page disappears", async () => {
    vi.mocked(planApi.list)
      .mockResolvedValueOnce(syntheticPlanPage([syntheticPlan], 1, 20, 21))
      .mockResolvedValueOnce(syntheticPlanPage([], 2, 20, 1))
      .mockResolvedValueOnce(syntheticPlanPage([syntheticPlan], 1, 20, 1));
    renderPlanApp(<PlanListPage onOpen={vi.fn()} />);
    expect(await screen.findByText(/Plano sint/)).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: /page 2/i }));
    await waitFor(() => expect(planApi.list).toHaveBeenLastCalledWith({ offset: 0, limit: 20 }));
    expect(screen.getByText(/Plano sint/)).toBeInTheDocument();
  });

  it("resets to the first page after creation and refetches from the API", async () => {
    vi.mocked(planApi.list)
      .mockResolvedValueOnce(syntheticPlanPage([syntheticPlan], 1, 20, 21))
      .mockResolvedValueOnce(syntheticPlanPage([syntheticPlan], 2, 20, 21))
      .mockResolvedValueOnce(syntheticPlanPage([syntheticPlan], 1, 20, 22));
    renderPlanApp(<PlanListPage onOpen={vi.fn()} />);
    await screen.findByText(/Plano sint/);
    fireEvent.click(screen.getByRole("button", { name: /page 2/i }));
    await waitFor(() => expect(planApi.list).toHaveBeenLastCalledWith({ offset: 20, limit: 20 }));
    fireEvent.click(screen.getByRole("button", { name: "mock create" }));
    await waitFor(() => expect(planApi.list).toHaveBeenLastCalledWith({ offset: 0, limit: 20 }));
  });
});
