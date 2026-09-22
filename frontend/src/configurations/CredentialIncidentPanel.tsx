import { useState } from "react";
import { Alert, Button, Stack, TextField, Typography } from "@mui/material";
import { Configuration, compromiseCredential, replaceCredential } from "./api";

export function CredentialIncidentPanel({ configuration, onChanged }: { configuration: Configuration; onChanged: () => void }) {
  const [token, setToken] = useState(""); const [message, setMessage] = useState<string>();
  async function compromise() { await compromiseCredential(configuration.id); setMessage("Credencial marcada como comprometida. Substitua-a antes de reutilizar."); onChanged(); }
  async function replace() { await replaceCredential(configuration.id, token, configuration.credential_status === "compromised" ? "compromise_remediation" : "preventive"); setToken(""); setMessage("Credencial substituída e registrada em auditoria."); onChanged(); }
  return <Stack spacing={1}><Typography variant="h6">Credencial GitLab</Typography>{configuration.credential_status === "compromised" && <Alert severity="warning">Esta credencial está bloqueada. Invalide ou rotacione-a no GitLab e informe a nova credencial.</Alert>}{message && <Alert severity="info">{message}</Alert>}<Button color="warning" onClick={() => void compromise()} disabled={configuration.credential_status !== "active"}>Marcar como comprometida</Button><TextField label="Nova credencial" type="password" value={token} onChange={(event) => setToken(event.target.value)} /><Button variant="outlined" onClick={() => void replace()} disabled={!token}>Substituir credencial</Button></Stack>;
}
