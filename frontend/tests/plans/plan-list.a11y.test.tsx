import { render, screen } from "@testing-library/react";
import { expect, it, vi } from "vitest";
import { PlanCard } from "../../src/plans/PlanCard";
import { syntheticPlan } from "./fixtures";
it("exposes an accessible plan action on narrow screens", () => { Object.defineProperty(window, "innerWidth", { value: 390, configurable: true }); render(<PlanCard plan={syntheticPlan} onOpen={vi.fn()} />); expect(screen.getByRole("button", { name: "Visualizar configuração" })).toBeVisible(); });
