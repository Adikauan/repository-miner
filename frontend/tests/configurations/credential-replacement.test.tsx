import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { CredentialReplacementPanel } from "../../src/configurations/CredentialReplacementPanel";
import * as api from "../../src/configurations/api";

vi.mock("../../src/configurations/api", async () => {
  const actual = await vi.importActual<typeof import("../../src/configurations/api")>("../../src/configurations/api");
  return { ...actual, compromiseCredential: vi.fn(), replaceCredential: vi.fn() };
});

const base = { id: "cfg-1", name: "QA", gitlab_base_url: "https://gitlab.example", enabled: true, target_branch: "QA", connection_validated: true };

describe("credential replacement", () => {
  beforeEach(() => vi.clearAllMocks());

  it("requires replacement for compromised credentials and never exposes the token", async () => {
    vi.mocked(api.replaceCredential).mockResolvedValue({});
    render(<CredentialReplacementPanel configuration={{ ...base, credential_status: "compromised" }} onChanged={vi.fn()} />);
    expect(screen.getByText(/bloqueada/i)).toBeInTheDocument();
    fireEvent.change(screen.getByLabelText("Nova credencial", { selector: "input" }), { target: { value: "secret-token" } });
    fireEvent.click(screen.getByRole("button", { name: /Substituir credencial/i }));
    await waitFor(() => expect(api.replaceCredential).toHaveBeenCalledWith("cfg-1", "secret-token", "compromise_remediation"));
    expect(screen.queryByText("secret-token")).not.toBeInTheDocument();
  });

  it("allows preventive replacement of an active credential", async () => {
    vi.mocked(api.replaceCredential).mockResolvedValue({});
    render(<CredentialReplacementPanel configuration={{ ...base, credential_status: "active" }} onChanged={vi.fn()} />);
    fireEvent.change(screen.getByLabelText("Nova credencial", { selector: "input" }), { target: { value: "new-token" } });
    fireEvent.click(screen.getByRole("button", { name: /Substituir credencial/i }));
    await waitFor(() => expect(api.replaceCredential).toHaveBeenCalledWith("cfg-1", "new-token", "preventive"));
  });
});
