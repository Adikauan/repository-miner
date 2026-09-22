import { useEffect, useState } from "react";
import { Button, Card, CardContent, FormControl, InputLabel, MenuItem, Select, Stack, Typography } from "@mui/material";
import { ExecutionStatus, ExecutionSnapshot, listExecutions } from "./api";

export function ExecutionHistoryPage({ onSelect, onReport }: { onSelect: (id: string) => void; onReport: (id: string) => void }) {
  const [status, setStatus] = useState<ExecutionStatus | "">("");
  const [items, setItems] = useState<ExecutionSnapshot[]>([]);
  useEffect(() => { void listExecutions({ status: status || undefined }).then((result) => setItems(result.items)); }, [status]);
  return <Stack spacing={2}><Typography variant="h5">Histórico de execuções</Typography><FormControl size="small"><InputLabel>Status</InputLabel><Select label="Status" value={status} onChange={(event) => setStatus(event.target.value as ExecutionStatus | "")}><MenuItem value="">Todos</MenuItem>{(["pending", "running", "completed", "partially_completed", "failed"] as ExecutionStatus[]).map((value) => <MenuItem key={value} value={value}>{value}</MenuItem>)}</Select></FormControl>{items.map((item) => <Card key={item.id}><CardContent><Stack direction="row" justifyContent="space-between" alignItems="center"><div><Typography>{item.status}</Typography><Typography variant="body2" color="text.secondary">{item.started_at ?? "sem início"}</Typography></div><Stack direction="row" spacing={1}><Button onClick={() => onSelect(item.id)}>Acompanhar</Button><Button variant="outlined" onClick={() => onReport(item.id)}>Relatório</Button></Stack></Stack></CardContent></Card>)}</Stack>;
}
