import { Alert, Button, Stack, Typography } from "@mui/material";
import { Page, RepositoryFailure } from "./api";

export function RepositoryFailureList({ page, onPage }: { page: Page<RepositoryFailure>; onPage: (offset: number) => void }) {
  return <Stack spacing={1}><Typography variant="h6">Falhas</Typography>{page.items.length === 0 ? <Typography color="text.secondary">Nenhuma falha registrada.</Typography> : page.items.map((item) => <Alert severity="error" key={item.id}>{item.code}: {item.safe_reason}</Alert>)}{page.offset > 0 && <Button onClick={() => onPage(Math.max(0, page.offset - page.limit))}>Página anterior</Button>}{page.items.length === page.limit && <Button onClick={() => onPage(page.offset + page.limit)}>Próxima página</Button>}</Stack>;
}
