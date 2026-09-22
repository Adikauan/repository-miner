import { Button, Stack, Table, TableBody, TableCell, TableHead, TableRow, Typography } from "@mui/material";
import { CommitVerificationItem, Page } from "./api";

export function CommitVerificationList({ page, onPage }: { page: Page<CommitVerificationItem>; onPage: (offset: number) => void }) {
  return <Stack spacing={1}>
    <Typography variant="h6">Commits verificados</Typography>
    {page.items.length === 0 ? <Typography color="text.secondary">Nenhum commit verificado.</Typography> : <Table size="small"><TableHead><TableRow><TableCell>Commit</TableCell><TableCell>Repository</TableCell><TableCell>Branch</TableCell><TableCell>Autor</TableCell><TableCell>E-mail</TableCell><TableCell>Resultado</TableCell></TableRow></TableHead><TableBody>{page.items.map((item) => <TableRow key={item.commit_hash}><TableCell>{item.commit_hash}</TableCell><TableCell>{item.repository ?? "—"}</TableCell><TableCell>{item.branch ?? "—"}</TableCell><TableCell>{item.author ?? "—"}</TableCell><TableCell>{item.author_email ?? "E-mail não disponível"}</TableCell><TableCell>{item.authorization_result ?? "—"}</TableCell></TableRow>)}</TableBody></Table>}
    {page.offset > 0 && <Button onClick={() => onPage(Math.max(0, page.offset - page.limit))}>Página anterior</Button>}
    {page.items.length === page.limit && <Button onClick={() => onPage(page.offset + page.limit)}>Próxima página</Button>}
  </Stack>;
}
