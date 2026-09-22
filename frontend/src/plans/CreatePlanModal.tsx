import { useMemo, useState } from "react";
import { Alert, Button, Dialog, DialogActions, DialogContent, DialogTitle, FormControlLabel, Stack, Switch, TextField, Typography } from "@mui/material";
import { ScopeFields } from "../configurations/ScopeFields";
import { ScheduleAndUsersFields } from "../configurations/ScheduleAndUsersFields";
import type { Schedule, TreeNode } from "../configurations/api";
import { planApi } from "./api";
import { createPlan } from "./createPlanFlow";
import { initialCreatePlanState, type CreatePlanState } from "./createPlanState";

function selectionRules(nodes: TreeNode[], selected: Set<string>) {
  const rules: { kind: TreeNode["kind"]; mode: "include"; external_id: string }[] = [];
  const visit = (node: TreeNode) => { if (selected.has(node.id)) rules.push({ kind: node.kind, mode: "include", external_id: node.id }); node.children?.forEach(visit); };
  nodes.forEach(visit);
  return rules;
}

export function CreatePlanModal({ open, onClose, onCreated }: { open: boolean; onClose: () => void; onCreated: (id: string) => void }) {
  const [name, setName] = useState(""); const [url, setUrl] = useState(""); const [token, setToken] = useState("");
  const [enabled, setEnabled] = useState(true); const [validated, setValidated] = useState(false); const [tree, setTree] = useState<TreeNode[]>([]);
  const [selected, setSelected] = useState(new Set<string>()); const [branch, setBranch] = useState("main"); const [branches, setBranches] = useState<string[]>([]);
  const [emails, setEmails] = useState(""); const [schedule, setSchedule] = useState<Schedule>({ recurrence: "daily", local_time: "09:00", timezone: "America/Sao_Paulo" });
  const [state, setState] = useState<CreatePlanState>(initialCreatePlanState); const dirty = Boolean(name || url || token || emails || selected.size);
  const valid = useMemo(() => name.trim().length >= 1 && name.trim().length <= 120 && /^https?:\/\//.test(url) && (token.length > 0 || Boolean(state.configurationId)), [name, url, token, state.configurationId]);
  const close = () => { if (!state.busy && (!dirty || window.confirm("Descartar alterações não salvas?"))) onClose(); };
  async function validate() {
    setState({ step: "validating_connection", busy: true });
    try {
      const base = await planApi.createBase({ name: name.trim(), gitlab_base_url: url, gitlab_token: token, timezone: schedule.timezone, enabled });
      setToken(""); await planApi.validateConnection(base.id); const hierarchy = await planApi.getTree(base.id); setTree(hierarchy.items); setValidated(true); setState({ step: "editing", busy: false, configurationId: base.id });
    } catch (error) { setState({ step: "failed_partial", busy: false, error: "Não foi possível validar a conexão." }); }
  }
  async function submit() {
    if (state.busy || !valid) return;
    const rules = selectionRules(tree, selected);
    const result = await createPlan({ name, gitlab_base_url: url, gitlab_token: token, timezone: schedule.timezone, enabled, target_branch: branch, selections: rules, allowed_emails: emails.split(/[;,\n]/).map((v) => v.trim()).filter(Boolean), schedule }, setState, { configurationId: state.configurationId, connectionValidated: validated });
    setState(result); if (result.step === "completed" && result.configurationId) onCreated(result.configurationId);
  }
  return <Dialog open={open} onClose={close} fullWidth maxWidth="md"><DialogTitle>Novo plano</DialogTitle><DialogContent dividers><Stack spacing={2}>{state.error && <Alert severity="error">{state.error}{state.configurationId && ` Plano incompleto: ${state.configurationId}`}</Alert>}<Typography variant="h6">Identificação</Typography><TextField autoFocus label="Nome do plano" inputProps={{ maxLength: 120 }} value={name} onChange={(e) => setName(e.target.value)} /><Typography variant="h6">Conexão GitLab</Typography><TextField label="URL da instância" value={url} onChange={(e) => { setUrl(e.target.value); setValidated(false); }} /><TextField label="Token" type="password" autoComplete="new-password" value={token} onChange={(e) => { setToken(e.target.value); setValidated(false); }} /><Button variant="outlined" disabled={!valid || state.busy} onClick={() => void validate()}>Validar conexão</Button><ScopeFields validated={validated} tree={tree} selected={selected} branch={branch} branches={branches} onSelectedChange={(value) => { setSelected(value); const id = [...value][0]; if (state.configurationId && id) void planApi.getBranches(state.configurationId, id).then((result) => setBranches(result.items)); }} onBranchChange={setBranch} /><ScheduleAndUsersFields emails={emails} schedule={schedule} onEmailsChange={setEmails} onScheduleChange={setSchedule} /><FormControlLabel control={<Switch checked={enabled} onChange={(_, checked) => setEnabled(checked)} />} label="Plano habilitado" /></Stack></DialogContent><DialogActions><Button disabled={state.busy} onClick={close}>Cancelar</Button><Button variant="contained" disabled={!valid || !validated || state.busy} onClick={() => void submit()}>{state.busy ? "Criando…" : "Criar plano"}</Button></DialogActions></Dialog>;
}
