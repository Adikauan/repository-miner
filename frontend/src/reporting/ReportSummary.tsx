import { Card, CardContent, Stack, Typography } from "@mui/material";
import { ExecutionReport } from "./api";

export function ReportSummary({ report }: { report: ExecutionReport }) {
  const values: [string, string | number][] = [
    ["Execução", report.execution_id],
    ["Estado", report.status],
    ["Repositories totais", report.repositories_total],
    ["Repositories concluídos", report.repositories_completed],
    ["Repositories com falha", report.repositories_failed],
    ["Commits encontrados", report.commits_discovered],
    ["Commits verificados", report.commits_verified],
    ["Commits permitidos", report.allowed_commits],
    ["Autores não permitidos", report.unauthorized_commits],
  ];
  return <Stack direction={{ xs: "column", md: "row" }} spacing={2}>{values.map(([label, value]) => <Card key={label}><CardContent><Typography variant="body2" color="text.secondary">{label}</Typography><Typography variant="h5">{String(value)}</Typography></CardContent></Card>)}</Stack>;
}
