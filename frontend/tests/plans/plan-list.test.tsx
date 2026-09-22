import { screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { PlanListPage } from "../../src/plans/PlanListPage";
import { planApi } from "../../src/plans/api";
import { syntheticPlan, syntheticPlanPage } from "./fixtures";
import { renderPlanApp } from "./renderPlanApp";

vi.mock("../../src/plans/api", () => ({ planApi: { list: vi.fn() } }));

describe("PlanListPage", () => {
  beforeEach(() => vi.clearAllMocks());

  it("shows loading then plans and schedule summary", async () => {
    vi.mocked(planApi.list).mockResolvedValue(syntheticPlanPage());
    renderPlanApp(<PlanListPage onOpen={vi.fn()} />);
    expect(screen.getByLabelText("Carregando planos")).toBeInTheDocument();
    expect(await screen.findByText(/Plano sint/)).toBeInTheDocument();
    expect(screen.getByText(/Semanal/)).toBeInTheDocument();
  });

  it("shows an actionable empty state", async () => {
    vi.mocked(planApi.list).mockResolvedValue(syntheticPlanPage([], 1, 20, 0));
    renderPlanApp(<PlanListPage onOpen={vi.fn()} />);
    expect(await screen.findByText("Nenhum plano cadastrado.")).toBeInTheDocument();
    expect(screen.getAllByRole("button", { name: "Novo plano" }).length).toBeGreaterThan(0);
  });

  it("shows retry on error", async () => {
    vi.mocked(planApi.list).mockRejectedValue(new Error("fail"));
    renderPlanApp(<PlanListPage onOpen={vi.fn()} />);
    expect(await screen.findByRole("button", { name: "Tentar novamente" })).toBeInTheDocument();
  });
});
