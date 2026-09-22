import { fireEvent, render, screen } from "@testing-library/react";
import { expect, it, vi } from "vitest";
import { CreatePlanModal } from "../../src/plans/CreatePlanModal";
it("opens, blocks dependent fields and closes", () => { const close = vi.fn(); render(<CreatePlanModal open onClose={close} onCreated={vi.fn()} />); expect(screen.getByText("Valide a conexão GitLab para selecionar escopo e branch.")).toBeVisible(); fireEvent.click(screen.getByRole("button", { name: "Cancelar" })); expect(close).toHaveBeenCalled(); });
