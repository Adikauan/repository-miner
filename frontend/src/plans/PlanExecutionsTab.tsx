import { useCallback, useEffect, useState } from "react";
import { Alert, Button, CircularProgress, Pagination, Stack, Typography } from "@mui/material";
import { planApi } from "./api";
import { ExecutionRow } from "./ExecutionRow";
import type { PlanExecutionSummary } from "./types";

const PAGE_SIZE = 20;
export function PlanExecutionsTab({ planId, onDetails }: { planId: string; onDetails: (execution: PlanExecutionSummary) => void }) {
  const [page, setPage] = useState(1); const [items, setItems] = useState<PlanExecutionSummary[]>([]); const [loading, setLoading] = useState(true); const [error, setError] = useState(false);
  useEffect(() => { setPage(1); }, [planId]);
  const load = useCallback(async () => { setLoading(true); setError(false); try { const value = await planApi.listExecutions({ configuration_id: planId, offset: (page - 1) * PAGE_SIZE, limit: PAGE_SIZE }); setItems(value.items.map((item) => ({ origin: item.origin ?? "manual", started_at: item.started_at ?? null, finished_at: item.finished_at ?? null, repositories_total: item.repositories_total ?? 0, repositories_completed: item.repositories_completed ?? 0, repositories_failed: item.repositories_failed ?? 0, commits_discovered: item.commits_discovered ?? 0, commits_verified: item.commits_verified ?? 0, allowed_commits: item.allowed_commits ?? 0, unauthorized_commits: item.unauthorized_commits ?? 0, ...item })) as PlanExecutionSummary[]); } catch { setError(true); } finally { setLoading(false); } }, [page, planId]);
  useEffect(() => { void load(); }, [load]);
  if (loading) return <Stack alignItems="center"><CircularProgress aria-label="Carregando execuções" /></Stack>;
  if (error) return <Alert severity="error" action={<Button onClick={() => void load()}>Tentar novamente</Button>}>Não foi possível carregar as execuções.</Alert>;
  if (!items.length && page === 1) return <Alert severity="info">Este plano ainda não possui execuções.</Alert>;
  return <Stack spacing={2}>{items.map((item) => <ExecutionRow key={item.id} execution={item} onDetails={onDetails} />)}<Pagination page={page} count={items.length === PAGE_SIZE ? page + 1 : page} onChange={(_, next) => setPage(next)} /></Stack>;
}
