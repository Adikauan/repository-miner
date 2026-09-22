import { useCallback, useEffect, useState } from "react";
import { Alert, Button, CircularProgress, Stack, Tab, Tabs, Typography } from "@mui/material";
import { planApi } from "./api";
import type { PlanExecutionSummary, VerificationPlanDetail } from "./types";
import { PlanConfigurationTab } from "./PlanConfigurationTab";
import { PlanExecutionsTab } from "./PlanExecutionsTab";

export function PlanDetailsPage({ planId, tab, onTab, onBack, onExecution }: { planId: string; tab: "configuration" | "executions"; onTab: (tab: "configuration" | "executions") => void; onBack: () => void; onExecution: (id: string, report: boolean) => void }) {
  const [plan, setPlan] = useState<VerificationPlanDetail>(); const [loading, setLoading] = useState(true); const [error, setError] = useState<string>(); const [running, setRunning] = useState(false);
  const load = useCallback(async () => { setLoading(true); try { setPlan(await planApi.get(planId)); setError(undefined); } catch { setError("Plano não encontrado ou indisponível."); } finally { setLoading(false); } }, [planId]);
  useEffect(() => { void load(); }, [load]);
  async function run() { if (running) return; setRunning(true); try { const value = await planApi.startExecution(planId); onExecution(value.execution_id ?? value.id, false); } catch { setError("Não foi possível iniciar a execução. Verifique concorrência e credencial."); } finally { setRunning(false); } }
  if (loading) return <Stack alignItems="center"><CircularProgress aria-label="Carregando plano" /></Stack>;
  if (error && !plan) return <Stack spacing={2}><Alert severity="error">{error}</Alert><Button onClick={onBack}>Voltar aos planos</Button></Stack>;
  if (!plan) return null;
  return <Stack spacing={3}><Stack direction={{ xs: "column", sm: "row" }} justifyContent="space-between" gap={2}><div><Button onClick={onBack}>Voltar aos planos</Button><Typography variant="h4">{plan.name}</Typography></div><Button variant="contained" disabled={running} onClick={() => void run()}>{running ? "Iniciando…" : "Executar agora"}</Button></Stack>{error && <Alert severity="error">{error}</Alert>}<Tabs value={tab} onChange={(_, value) => onTab(value)} aria-label="Detalhes do plano"><Tab value="configuration" label="Configuração" /><Tab value="executions" label="Execuções" /></Tabs>{tab === "configuration" ? <PlanConfigurationTab plan={plan} onSaved={() => void load()} onRun={() => void run()} /> : <PlanExecutionsTab planId={planId} onDetails={(execution: PlanExecutionSummary) => onExecution(execution.id, !["pending", "running"].includes(execution.status))} />}</Stack>;
}
