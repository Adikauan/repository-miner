import { Checkbox, FormControlLabel, Stack, Typography } from "@mui/material";
import { ReactElement } from "react";
import { TreeNode } from "../configurations/api";

function flatten(node: TreeNode): string[] { return [node.id, ...(node.children ?? []).flatMap(flatten)]; }

export function RepositoryTree({ nodes, selected, onToggle }: { nodes: TreeNode[]; selected: Set<string>; onToggle: (node: TreeNode, checked: boolean) => void }) {
  const render = (node: TreeNode, depth = 0): ReactElement => {
    const ids = flatten(node); const selectedCount = ids.filter((id) => selected.has(id)).length;
    return <Stack key={`${node.kind}:${node.id}`} sx={{ pl: depth * 2 }}><FormControlLabel control={<Checkbox checked={selectedCount === ids.length} indeterminate={selectedCount > 0 && selectedCount < ids.length} onChange={(event) => onToggle(node, event.target.checked)} />} label={<Typography variant="body2">{node.full_path ?? node.path ?? node.name ?? node.id}</Typography>} />{node.children?.map((child) => render(child, depth + 1))}</Stack>;
  };
  return <Stack>{nodes.map((node) => render(node))}</Stack>;
}
