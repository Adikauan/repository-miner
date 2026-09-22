import { render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { expect, it, vi } from "vitest";
import { AppRoutes } from "../../src/app/routes";
import { getExecution } from "../../src/executions/api";

vi.mock("../../src/executions/api", () => ({ getExecution: vi.fn(), listExecutions: vi.fn().mockResolvedValue({ items: [], offset: 0, limit: 20 }) }));
vi.mock("../../src/plans/api", () => ({ planApi: { list: vi.fn().mockResolvedValue({ items: [], offset: 0, limit: 20, total: 0, total_pages: 0 }) } }));

it("redirects an old configuration URL to its plan", () => { render(<MemoryRouter initialEntries={["/configurations/plan-1"]}><Routes><Route path="/plans/:id/configuration" element={<div>redirected plan</div>} /><Route path="*" element={<AppRoutes />} /></Routes></MemoryRouter>); expect(screen.getByText("redirected plan")).toBeVisible(); });
it.each(["/configurations", "/executions"])("falls back safely from %s", async (route) => { render(<MemoryRouter initialEntries={[route]}><AppRoutes /></MemoryRouter>); expect(await screen.findByText(/Planos de Verifica/)).toBeVisible(); });
it("resolves an old running execution into its contextual live URL", async () => { vi.mocked(getExecution).mockResolvedValue({ id: "execution-1", configuration_id: "plan-1", status: "running" }); render(<MemoryRouter initialEntries={["/executions/execution-1"]}><Routes><Route path="/plans/plan-1/executions/execution-1/live" element={<div>contextual live</div>} /><Route path="*" element={<AppRoutes />} /></Routes></MemoryRouter>); expect(await screen.findByText("contextual live")).toBeVisible(); });
it("resolves an old report into its contextual report URL", async () => { vi.mocked(getExecution).mockResolvedValue({ id: "execution-1", configuration_id: "plan-1", status: "completed" }); render(<MemoryRouter initialEntries={["/reports/execution-1"]}><Routes><Route path="/plans/plan-1/executions/execution-1/report" element={<div>contextual report</div>} /><Route path="*" element={<AppRoutes />} /></Routes></MemoryRouter>); expect(await screen.findByText("contextual report")).toBeVisible(); });
