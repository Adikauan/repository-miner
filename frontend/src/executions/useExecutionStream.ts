import { useCallback, useEffect, useRef, useState } from "react";
import { ExecutionEvent, ExecutionSnapshot, getExecution, issueExecutionTicket } from "./api";

export function useExecutionStream(executionId: string) {
  const [snapshot, setSnapshot] = useState<ExecutionSnapshot | null>(null);
  const [events, setEvents] = useState<ExecutionEvent[]>([]);
  const [connected, setConnected] = useState(false);
  const revision = useRef(0);
  const stopped = useRef(false);
  const refresh = useCallback(async () => setSnapshot(await getExecution(executionId)), [executionId]);

  useEffect(() => {
    stopped.current = false;
    let socket: WebSocket | undefined;
    let retry = 0;
    let timer: number | undefined;
    const connect = async () => {
      if (stopped.current) return;
      await refresh();
      const ticket = await issueExecutionTicket(executionId);
      const base = import.meta.env.VITE_WS_URL ?? "ws://localhost:8000";
      socket = new WebSocket(`${base}/api/v1/ws/executions/${executionId}?ticket=${encodeURIComponent(ticket.ticket)}`);
      socket.onopen = () => { retry = 0; setConnected(true); };
      socket.onmessage = (message) => {
        const event = JSON.parse(message.data) as ExecutionEvent | { type: "execution.snapshot"; execution: ExecutionSnapshot };
        if ("execution" in event) { setSnapshot(event.execution); return; }
        const live = event as ExecutionEvent;
        if (live.revision <= revision.current) return;
        if (live.revision > revision.current + 1) { void refresh(); revision.current = live.revision; return; }
        revision.current = live.revision;
        setEvents((current) => [...current, live]);
        if (live.type.startsWith("execution.")) void refresh();
      };
      socket.onclose = () => {
        setConnected(false);
        if (!stopped.current) { const delay = Math.min(30000, 500 * 2 ** retry++); timer = window.setTimeout(() => void connect(), delay); }
      };
      socket.onerror = () => socket?.close();
    };
    void connect().catch(() => { timer = window.setTimeout(() => void connect(), 1000); });
    return () => { stopped.current = true; if (timer) window.clearTimeout(timer); socket?.close(); };
  }, [executionId, refresh]);

  return { snapshot, events, connected, refresh };
}
