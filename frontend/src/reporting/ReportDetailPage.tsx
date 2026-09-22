import { Alert, Button, CircularProgress, Stack, TextField, Typography } from "@mui/material";
import { useEffect, useState } from "react";
import * as reportingApi from "./api";
import { CommitVerificationItem, ExecutionReport, Page, RepositoryFailure, RepositoryReportItem, UnauthorizedCommit } from "./api";
import { CommitVerificationList } from "./CommitVerificationList";
import { RepositoryFailureList } from "./RepositoryFailureList";
import { RepositoryReportList } from "./RepositoryReportList";
import { ReportSummary } from "./ReportSummary";
import { UnauthorizedCommitList } from "./UnauthorizedCommitList";
import { reportErrorState, safeErrorMessage } from "./reportViewState";
import { filterAlerts, filterCommits, filterRepositories } from "./reportFilters";

const emptyPage = <T,>(): Page<T> => ({ items: [], offset: 0, limit: 50 });

export function ReportDetailPage({ executionId, onBack, onMonitor }: { executionId: string; onBack: () => void; onMonitor?: (id: string) => void }) {
  const [report, setReport] = useState<ExecutionReport>();
  const [repositories, setRepositories] = useState<Page<RepositoryReportItem>>(emptyPage);
  const [commits, setCommits] = useState<Page<CommitVerificationItem>>(emptyPage);
  const [alerts, setAlerts] = useState<Page<UnauthorizedCommit>>(emptyPage);
  const [failures, setFailures] = useState<Page<RepositoryFailure>>(emptyPage);
  const [error, setError] = useState<string>();
  const [state, setState] = useState<"loading" | "success" | "error" | "not_found" | "unavailable">("loading");
  const [filter, setFilter] = useState("");

  const loadCollection = async (offset: number, setter: (page: any) => void, loader: (id: string, p: { offset: number; limit: number }) => Promise<any>) => {
    try { setter(await loader(executionId, { offset, limit: 50 })); } catch (cause) { setError(safeErrorMessage(cause)); }
  };
  useEffect(() => {
    let active = true;
    setState("loading");
    const repositoriesQuery = reportingApi.getRepositories?.(executionId) ?? Promise.resolve(emptyPage<RepositoryReportItem>());
    const commitsQuery = reportingApi.getCommits?.(executionId) ?? Promise.resolve(emptyPage<CommitVerificationItem>());
    const alertsQuery = reportingApi.getUnauthorizedCommits(executionId);
    const failuresQuery = reportingApi.getRepositoryFailures(executionId);
    void Promise.allSettled([reportingApi.getReport(executionId), repositoriesQuery, commitsQuery, alertsQuery, failuresQuery])
      .then((results) => {
        if (!active) return;
        const summary = results[0];
        if (summary.status === "rejected") { const next = reportErrorState(summary.reason); setState(next); setError(safeErrorMessage(summary.reason)); return; }
        setReport(summary.value);
        const [repos, verified, unauthorized, failed] = results.slice(1);
        if (repos.status === "fulfilled") setRepositories(repos.value as Page<RepositoryReportItem>);
        if (verified.status === "fulfilled") setCommits(verified.value as Page<CommitVerificationItem>);
        if (unauthorized.status === "fulfilled") setAlerts(unauthorized.value as Page<UnauthorizedCommit>);
        if (failed.status === "fulfilled") setFailures(failed.value as Page<RepositoryFailure>);
        const rejected = results.slice(1).find((item) => item.status === "rejected");
        if (rejected?.status === "rejected") setError(safeErrorMessage(rejected.reason));
        setState("success");
      });
    return () => { active = false; };
  }, [executionId]);

  if (state === "loading") return <Stack alignItems="center" spacing={2}><CircularProgress /><Typography>Carregando relatório…</Typography></Stack>;
  if (state === "not_found") return <Stack spacing={2}><Alert severity="error">Execução não encontrada.</Alert><Button onClick={onBack}>Voltar</Button></Stack>;
  if (state === "unavailable") return <Stack spacing={2}><Alert severity="info">Relatório ainda indisponível.</Alert><Button onClick={() => onMonitor?.(executionId)}>Acompanhar execução</Button><Button onClick={onBack}>Voltar</Button></Stack>;
  if (state === "error" || !report) return <Stack spacing={2}><Alert severity="error">{error ?? "Não foi possível carregar o relatório."}</Alert><Button onClick={onBack}>Voltar</Button></Stack>;

  const terminal = ["completed", "partially_completed", "failed"].includes(report.status);
  return <Stack spacing={3}>
    <Stack direction="row" justifyContent="space-between"><Typography variant="h4">Relatório da execução</Typography><Stack direction="row" spacing={1}><Button onClick={onBack}>Voltar</Button>{!terminal && <Button variant="outlined" onClick={() => onMonitor?.(executionId)}>Acompanhar</Button>}</Stack></Stack>
    {error && <Alert severity="warning">{error}</Alert>}
    <ReportSummary report={report} />
    <TextField label="Filtrar repository, commit, autor ou e-mail" value={filter} onChange={(event) => setFilter(event.target.value)} size="small" />
    <RepositoryReportList page={{ ...repositories, items: filterRepositories(repositories.items, filter) }} onPage={(offset) => void loadCollection(offset, setRepositories, reportingApi.getRepositories)} />
    <CommitVerificationList page={{ ...commits, items: filterCommits(commits.items, filter) }} onPage={(offset) => void loadCollection(offset, setCommits, reportingApi.getCommits)} />
    <UnauthorizedCommitList page={{ ...alerts, items: filterAlerts(alerts.items, filter) }} onPage={(offset) => void loadCollection(offset, setAlerts, reportingApi.getUnauthorizedCommits)} />
    <RepositoryFailureList page={failures} onPage={(offset) => void loadCollection(offset, setFailures, reportingApi.getRepositoryFailures)} />
  </Stack>;
}
