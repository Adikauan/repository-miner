import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ConfigurationEditor } from "../../src/configurations/ConfigurationEditor";
import * as api from "../../src/configurations/api";

vi.mock("../../src/configurations/api", async () => {
  const actual = await vi.importActual<typeof import("../../src/configurations/api")>("../../src/configurations/api");
  return { ...actual, getConfiguration: vi.fn().mockRejectedValue({ message: "Configuração indisponível" }) };
});

describe("configuration editor accessibility and error state", () => {
  it("exposes labeled controls and a visible load error", async () => {
    render(<ConfigurationEditor configuration={{ id: "cfg-a11y", name: "QA", gitlab_base_url: "https://gitlab.example", enabled: true, target_branch: "QA", credential_status: "active", connection_validated: false }} onSaved={vi.fn()} onRun={vi.fn()} />);
    expect(screen.getByLabelText("Nome")).toBeInTheDocument();
    expect(screen.getByLabelText("Branch alvo")).toBeInTheDocument();
    expect(await screen.findByRole("alert")).toHaveTextContent("Configuração indisponível");
  });
});
