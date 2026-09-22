import { afterEach, describe, expect, it, vi } from "vitest";
import { getConfiguration, startExecution, updateConfiguration, validateConnection } from "./api";

describe("configuration API contracts", () => {
  afterEach(() => vi.unstubAllGlobals());

  it("loads detail without exposing a credential field", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify({ id: "cfg-1", name: "QA", credential_status: "active", connection_validated: false }), { status: 200 })));
    const result = await getConfiguration("cfg-1");
    expect(result).not.toHaveProperty("gitlab_token");
  });

  it("uses PATCH for basic fields and POST for validation/manual execution", async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(new Response(JSON.stringify({ id: "cfg-1" }), { status: 200 }))
      .mockResolvedValueOnce(new Response(JSON.stringify({ validated: true }), { status: 200 }))
      .mockResolvedValueOnce(new Response(JSON.stringify({ id: "execution-1" }), { status: 202 }));
    vi.stubGlobal("fetch", fetchMock);
    await updateConfiguration("cfg-1", { enabled: false });
    await validateConnection("cfg-1");
    await startExecution("cfg-1");
    expect(fetchMock.mock.calls.map(([url, init]) => `${init?.method ?? "GET"} ${url}`)).toEqual([
      "PATCH http://127.0.0.1:8000/api/v1/configurations/cfg-1",
      "POST http://127.0.0.1:8000/api/v1/configurations/cfg-1/connection-test",
      "POST http://127.0.0.1:8000/api/v1/configurations/cfg-1/executions",
    ]);
  });
});
