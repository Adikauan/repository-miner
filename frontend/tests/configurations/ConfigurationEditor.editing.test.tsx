import { render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ConfigurationEditor } from "../../src/configurations/ConfigurationEditor";
import * as api from "../../src/configurations/api";

vi.mock("../../src/configurations/api", async () => {
  const actual = await vi.importActual<typeof import("../../src/configurations/api")>("../../src/configurations/api");
  return { ...actual, getConfiguration: vi.fn(), getGitLabTree: vi.fn(), getBranches: vi.fn(), saveScope: vi.fn(), saveAllowedUsers: vi.fn(), saveSchedule: vi.fn(), updateConfiguration: vi.fn(), validateConnection: vi.fn() };
});

describe("configuration editor dedicated operations", () => {
  it("loads persisted tree selections and branch options after connection validation", async () => {
    vi.mocked(api.getConfiguration).mockResolvedValue({ id: "cfg-1", name: "QA", gitlab_base_url: "https://gitlab.example", enabled: true, target_branch: "QA", credential_status: "active", connection_validated: true, selections: [{ kind: "repository", mode: "include", external_id: "repo-1" }] });
    vi.mocked(api.getGitLabTree).mockResolvedValue({ items: [{ id: "repo-1", kind: "repository", name: "repo-1", path: "team/repo-1" }] });
    vi.mocked(api.getBranches).mockResolvedValue({ items: ["QA", "main"] });
    render(<ConfigurationEditor configuration={{ id: "cfg-1", name: "QA", gitlab_base_url: "https://gitlab.example", enabled: true, target_branch: "QA", credential_status: "active", connection_validated: true }} onSaved={vi.fn()} onRun={vi.fn()} />);
    await waitFor(() => expect(screen.getByText("team/repo-1")).toBeInTheDocument());
    expect(api.getBranches).toHaveBeenCalledWith("cfg-1", "repo-1");
  });
});
