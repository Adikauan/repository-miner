import { Button, Card, CardActions, CardContent, Chip, Stack, Typography } from "@mui/material";
import type { VerificationPlanSummary } from "./types";

function scheduleLabel(plan: VerificationPlanSummary) {
  const value = plan.schedule_summary;
  if (!value) return "Sem agendamento";
  if (value.recurrence === "weekly") return `Semanal · dia ${value.weekday} · ${value.local_time}`;
  if (value.recurrence === "monthly") return `Mensal · dia ${value.day_of_month} · ${value.local_time}`;
  return `Diária · ${value.local_time}`;
}

export function PlanCard({ plan, onOpen }: { plan: VerificationPlanSummary; onOpen: (id: string) => void }) {
  return <Card variant="outlined" sx={{ height: "100%", display: "flex", flexDirection: "column" }}><CardContent sx={{ flexGrow: 1 }}><Stack direction="row" justifyContent="space-between" gap={1} alignItems="flex-start"><Typography variant="h6" sx={{ overflowWrap: "anywhere" }}>{plan.name}</Typography><Chip size="small" color={plan.enabled ? "success" : "default"} label={plan.enabled ? "Habilitado" : "Desabilitado"} /></Stack><Typography color="text.secondary" sx={{ overflowWrap: "anywhere", mt: 1 }}>{plan.gitlab_base_url}</Typography><Typography variant="body2">Branch: {plan.target_branch ?? "Não disponível"}</Typography><Typography variant="body2">{scheduleLabel(plan)}</Typography><Typography variant="body2" sx={{ mt: 1 }}>Última execução: {plan.last_execution ? `${plan.last_execution.status} · ${plan.last_execution.started_at ? new Date(plan.last_execution.started_at).toLocaleString() : "sem data"}` : "Nunca executado"}</Typography></CardContent><CardActions><Button onClick={() => onOpen(plan.id)}>Visualizar configuração</Button></CardActions></Card>;
}
