import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { ConfigurationEditor } from "../../src/configurations/ConfigurationEditor";
import * as api from "../../src/configurations/api";

vi.mock("../../src/configurations/api", async () => {
  const actual = await vi.importActual<typeof import("../../src/configurations/api")>("../../src/configurations/api");
  return { ...actual, validateConnection: vi.fn(), getGitLabTree: vi.fn(), saveScope: vi.fn(), saveAllowedUsers: vi.fn(), saveSchedule: vi.fn(), compromiseCredential: vi.fn(), replaceCredential: vi.fn() };
});

const configuration: api.Configuration = { id: "cfg-1", name: "QA", gitlab_base_url: "https://gitlab.example", enabled: true, target_branch: null, credential_status: "active", connection_validated: false };

describe("configuration flow", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(api.validateConnection).mockResolvedValue({ validated: true });
    vi.mocked(api.getGitLabTree).mockResolvedValue({ items: [{ id: "repo-1", kind: "repository", full_path: "team/repo" }] });
    vi.mocked(api.saveScope).mockResolvedValue({});
    vi.mocked(api.saveAllowedUsers).mockResolvedValue({});
    vi.mocked(api.saveSchedule).mockResolvedValue({});
  });

  it("validates the connection before enabling scope persistence and defaults to QA", async () => {
    const onSaved = vi.fn();
    render(<ConfigurationEditor configuration={configuration} onSaved={onSaved} onRun={vi.fn()} />);
    expect(screen.getByLabelText("Branch alvo")).toHaveValue("QA");
    expect(screen.getByRole("button", { name: /Salvar configuração/i })).toBeDisabled();
    fireEvent.click(screen.getByRole("button", { name: /Validar conexão/i }));
    await screen.findByText("team/repo");
    expect(screen.getByRole("button", { name: /Salvar configuração/i })).toBeEnabled();
  });

  it("normalizes allowed e-mails and sends the selected schedule", async () => {
    render(<ConfigurationEditor configuration={{ ...configuration, connection_validated: true }} onSaved={vi.fn()} onRun={vi.fn()} />);
    fireEvent.change(screen.getByLabelText(/E-mails permitidos/i, { selector: "textarea" }), { target: { value: " Alice@EXAMPLE.COM; bob@example.com\n" } });
    fireEvent.mouseDown(screen.getByRole("combobox"));
    fireEvent.click(await screen.findByRole("option", { name: "Mensal" }));
    fireEvent.click(screen.getByRole("button", { name: /Salvar configuração/i }));
    await waitFor(() => expect(api.saveAllowedUsers).toHaveBeenCalledWith("cfg-1", ["Alice@EXAMPLE.COM", "bob@example.com"]));
    expect(api.saveSchedule).toHaveBeenCalledWith("cfg-1", expect.objectContaining({ recurrence: "monthly", day_of_month: 1 }));
  });
});
