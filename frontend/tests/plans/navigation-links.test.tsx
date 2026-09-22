import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { expect, it, vi } from "vitest";
import { AppRoutes } from "../../src/app/routes";

vi.mock("../../src/plans/api", () => ({ planApi: { list: vi.fn().mockResolvedValue({ items: [], offset: 0, limit: 20, total: 0, total_pages: 0 }) } }));

it("does not render obsolete top-level navigation links", async () => { render(<MemoryRouter><AppRoutes /></MemoryRouter>); await screen.findByText(/Planos de Verifica/); expect(screen.queryByRole("link", { name: /^Configura/ })).not.toBeInTheDocument(); expect(screen.queryByRole("link", { name: /Repositories/ })).not.toBeInTheDocument(); });
