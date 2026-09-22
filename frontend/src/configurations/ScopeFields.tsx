import { Card, CardContent, MenuItem, TextField, Typography } from "@mui/material";
import { RepositoryTree } from "../repositories/RepositoryTree";
import type { TreeNode } from "./api";

export function ScopeFields({ validated, tree, selected, branch, branches, onSelectedChange, onBranchChange }: { validated: boolean; tree: TreeNode[]; selected: Set<string>; branch: string; branches: string[]; onSelectedChange: (value: Set<string>) => void; onBranchChange: (value: string) => void }) {
  if (!validated) return <><Typography color="text.secondary">Valide a conexão GitLab para selecionar escopo e branch.</Typography><TextField fullWidth disabled label="Branch alvo" value={branch} /></>;
  return <Card variant="outlined"><CardContent><Typography variant="h6" gutterBottom>Escopo e branch</Typography>{tree.length === 0 ? <Typography color="text.secondary">Nenhum repository encontrado.</Typography> : <RepositoryTree nodes={tree} selected={selected} onToggle={(node, checked) => { const next = new Set(selected); const walk = (item: TreeNode) => { checked ? next.add(item.id) : next.delete(item.id); item.children?.forEach(walk); }; walk(node); onSelectedChange(next); }} />}<TextField fullWidth sx={{ mt: 2 }} select={branches.length > 0} label="Branch alvo" value={branch} onChange={(event) => onBranchChange(event.target.value)}>{branches.map((item) => <MenuItem key={item} value={item}>{item}</MenuItem>)}</TextField></CardContent></Card>;
}
