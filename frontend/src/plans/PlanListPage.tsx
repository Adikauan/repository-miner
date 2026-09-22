import { useCallback, useEffect, useState } from "react";
import { Alert, Box, Button, CircularProgress, Grid2 as Grid, Pagination, Stack, Typography } from "@mui/material";
import { planApi } from "./api";
import type { PaginatedPlanPage, VerificationPlanSummary } from "./types";
import { PlanCard } from "./PlanCard";
import { CreatePlanModal } from "./CreatePlanModal";

const PAGE_SIZE = 20;
const emptyPage: PaginatedPlanPage = { items: [], offset: 0, limit: PAGE_SIZE, total: 0, total_pages: 0 };

export function PlanListPage({ onOpen }: { onOpen: (id: string) => void }) {
  const [page, setPage] = useState(1);
  const [result, setResult] = useState<PaginatedPlanPage>(emptyPage);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>();
  const [success, setSuccess] = useState<string>();
  const [modal, setModal] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    setError(undefined);
    try {
      const value = await planApi.list({ offset: (page - 1) * PAGE_SIZE, limit: PAGE_SIZE });
      if (value.total_pages === 0 && page !== 1) { setPage(1); return; }
      if (value.total_pages > 0 && page > value.total_pages) { setPage(value.total_pages); return; }
      setResult(value);
    } catch {
      setError("Não foi possível carregar os planos.");
    } finally {
      setLoading(false);
    }
  }, [page]);

  useEffect(() => { void load(); }, [load]);

  const items = result.items as VerificationPlanSummary[];
  const onCreated = () => {
    setModal(false);
    setSuccess("Plano criado com sucesso.");
    if (page === 1) void load(); else setPage(1);
  };

  return <Stack spacing={3}>
    <Stack direction={{ xs: "column", sm: "row" }} justifyContent="space-between" gap={2}>
      <Box><Typography variant="h4">Planos de Verificação</Typography><Typography color="text.secondary">Configure e acompanhe as verificações de repositories.</Typography></Box>
      <Button variant="contained" onClick={() => { setSuccess(undefined); setModal(true); }}>Novo plano</Button>
    </Stack>
    {success && <Alert severity="success">{success}</Alert>}
    {loading ? <Stack alignItems="center"><CircularProgress aria-label="Carregando planos" /></Stack> : error ? <Alert severity="error" action={<Button onClick={() => void load()}>Tentar novamente</Button>}>{error}</Alert> : items.length === 0 ? <Alert severity="info" action={<Button onClick={() => setModal(true)}>Novo plano</Button>}>Nenhum plano cadastrado.</Alert> : <>
      <Grid container spacing={2}>{items.map((plan) => <Grid key={plan.id} size={{ xs: 12, md: 6 }}><PlanCard plan={plan} onOpen={onOpen} /></Grid>)}</Grid>
      {result.total_pages > 1 && <Stack alignItems="center"><Pagination page={page} count={result.total_pages} onChange={(_, next) => setPage(next)} aria-label="Paginação de planos" /></Stack>}
    </>}
    <CreatePlanModal open={modal} onClose={() => setModal(false)} onCreated={onCreated} />
  </Stack>;
}
