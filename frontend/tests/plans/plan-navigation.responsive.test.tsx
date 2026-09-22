import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { PlanCard } from "../../src/plans/PlanCard";
import { CreatePlanModal } from "../../src/plans/CreatePlanModal";
import { syntheticPlan } from "./fixtures";
describe.each([1440, 390])("plan navigation at %ipx", (width) => { it("keeps primary content and action usable", () => { Object.defineProperty(window, "innerWidth", { value: width, configurable: true }); render(<><PlanCard plan={syntheticPlan} onOpen={vi.fn()} /><CreatePlanModal open onClose={vi.fn()} onCreated={vi.fn()} /></>); expect(screen.getByText("Plano sintético")).toBeInTheDocument(); expect(screen.getByRole("button", { name: "Visualizar configuração", hidden: true })).toBeInTheDocument(); expect(screen.getByRole("dialog")).toBeVisible(); expect(screen.getByRole("button", { name: "Criar plano" })).toBeVisible(); }); });
