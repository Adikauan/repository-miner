import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ConfigurationEditor } from "../../src/configurations/ConfigurationEditor";
import * as api from "../../src/configurations/api";

vi.mock("../../src/configurations/api", async () => {
  const actual = await vi.importActual<typeof import("../../src/configurations/api")>("../../src/configurations/api");
  return { ...actual, getConfiguration: vi.fn().mockRejectedValue(new Error("offline")) };
});

describe("manual execution action", () => {
  it("passes the persisted configuration identifier to the existing execution flow", () => {
    const onRun = vi.fn();
    render(<ConfigurationEditor configuration={{ id: "cfg-manual", name: "QA", gitlab_base_url: "https://gitlab.example", enabled: false, target_branch: "QA", credential_status: "active", connection_validated: true }} onSaved={vi.fn()} onRun={onRun} />);
    fireEvent.click(screen.getByRole("button", { name: "Executar agora" }));
    expect(onRun).toHaveBeenCalledWith("cfg-manual");
  });
});
