import { act, renderHook, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { useExecutionStream } from "../../src/executions/useExecutionStream";
import * as api from "../../src/executions/api";

vi.mock("../../src/executions/api", () => ({ getExecution: vi.fn(), issueExecutionTicket: vi.fn() }));

class FakeWebSocket {
  static instances: FakeWebSocket[] = [];
  onopen: (() => void) | null = null;
  onmessage: ((event: MessageEvent) => void) | null = null;
  onclose: (() => void) | null = null;
  onerror: (() => void) | null = null;
  url: string;
  constructor(url: string) { this.url = url; FakeWebSocket.instances.push(this); }
  close() { this.onclose?.(); }
  emitMessage(data: unknown) { this.onmessage?.({ data: JSON.stringify(data) } as MessageEvent); }
}

describe("live execution stream", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    FakeWebSocket.instances = [];
    vi.stubGlobal("WebSocket", FakeWebSocket);
    vi.mocked(api.getExecution).mockResolvedValue({ id: "exec-1", configuration_id: "cfg-1", status: "running", commits_discovered: 0 });
    vi.mocked(api.issueExecutionTicket).mockResolvedValue({ ticket: "one-time", expires_at: "2099-01-01T00:00:00Z" });
  });
  afterEach(() => vi.unstubAllGlobals());

  it("loads REST snapshot, authenticates with a fresh ticket, and receives progress", async () => {
    const { result } = renderHook(() => useExecutionStream("exec-1"));
    await waitFor(() => expect(FakeWebSocket.instances).toHaveLength(1));
    expect(FakeWebSocket.instances[0].url).toContain("ticket=one-time");
    act(() => FakeWebSocket.instances[0].onopen?.());
    act(() => FakeWebSocket.instances[0].emitMessage({ schema_version: "1", event_id: "evt-1", type: "repository.progress", occurred_at: "2026-01-01T00:00:00Z", execution_id: "exec-1", configuration_id: "cfg-1", repository_id: "repo-1", revision: 1, payload: { commits_verified: 1 } }));
    await waitFor(() => expect(result.current.events).toHaveLength(1));
    expect(result.current.events[0].type).toBe("repository.progress");
    expect(result.current.connected).toBe(true);
  });
});
