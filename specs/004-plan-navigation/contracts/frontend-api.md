# Frontend/API Contract: Planos de Verificação

Base path existente: `/api/v1`. Respostas de erro seguem o envelope seguro já consumido pelo cliente. Nenhuma resposta pode conter token ou ciphertext.

## 1. Listar planos (extensão compatível)

`GET /configurations?offset={offset}&limit={limit}`

Retorna a página solicitada e acrescenta resumos opcionais do schedule e da execução mais recente. O backend ordena por `MonitoringConfiguration.id DESC` apenas como fallback determinístico, pois o modelo atual não possui timestamp canônico de criação; essa ordem não representa cronologia real.

```json
{
  "items": [
    {
    "id": "configuration-synthetic",
    "name": "Plano sintético",
    "gitlab_base_url": "https://gitlab.example.com/",
    "timezone": "America/Sao_Paulo",
    "enabled": true,
    "target_branch": "QA",
    "credential_status": "active",
    "connection_validated": true,
    "next_run_at": "2026-09-22T12:00:00Z",
    "schedule_summary": {
      "recurrence": "weekly",
      "local_time": "09:00",
      "weekday": 1,
      "day_of_month": null
    },
    "last_execution": {
      "id": "execution-synthetic",
      "status": "completed",
      "started_at": "2026-09-21T12:00:00Z",
      "finished_at": "2026-09-21T12:01:00Z"
    }
    }
  ],
  "offset": 0,
  "limit": 20,
  "total": 1,
  "total_pages": 1
}
```

`schedule_summary` é `null` quando não existe schedule. Quando existe:

- `recurrence` é `daily`, `weekly` ou `monthly`;
- `local_time` informa o horário local configurado;
- `weekday` somente é preenchido para `weekly`;
- `day_of_month` somente é preenchido para `monthly`.

O resumo não expõe ID do schedule, ocorrências, cálculos ou estruturas internas do scheduler. `last_execution` é `null` quando o plano nunca foi executado. Campos existentes preservam sua semântica.

## 2. Criar configuração-base (reutilizado)

`POST /configurations`

```json
{
  "name": "Plano sintético",
  "gitlab_base_url": "https://gitlab.example.com/",
  "gitlab_token": "synthetic-secret-value",
  "timezone": "America/Sao_Paulo",
  "enabled": true
}
```

Retorna configuração sem `gitlab_token`. O frontend limpa o token local após sucesso.

## 3. Operações canônicas reutilizadas

| Purpose | Method and path | Precondition |
|---|---|---|
| Detalhar plano | `GET /configurations/{id}` | Plano existente |
| Editar básicos | `PATCH /configurations/{id}` | Campos válidos |
| Alterar conexão | `PUT /configurations/{id}/connection` | Operador autenticado se houver token |
| Validar conexão | `POST /configurations/{id}/connection-test` | Credencial ativa |
| Carregar hierarquia | `GET /configurations/{id}/gitlab-tree` | Conexão atual validada |
| Carregar branches | `GET /configurations/{id}/repositories/{repository_id}/branches` | Conexão atual validada |
| Salvar escopo/branch | `PUT /configurations/{id}/repository-selections` | Conexão atual validada |
| Salvar usuários | `PUT /configurations/{id}/allowed-users` | E-mails únicos após normalização |
| Salvar schedule | `PUT /configurations/{id}/schedule` | Recorrência/parâmetros válidos |
| Executar agora | `POST /configurations/{id}/executions` | Sem execução ativa; credencial utilizável |

Criação composta usa as operações acima em sequência. A resposta visual registra a etapa que falhou, mas nunca inclui corpo sensível.

## 4. Listar execuções por plano (extensão compatível)

`GET /executions?configuration_id={id}&offset={offset}&limit={limit}`

Parâmetros:

- `configuration_id`: opcional para compatibilidade geral, obrigatório na aba de um plano.
- `status`: filtro opcional existente.
- `offset`: inteiro >= 0, padrão 0.
- `limit`: inteiro de 1 a 200, padrão 50.

```json
{
  "items": [
    {
      "id": "execution-synthetic",
      "configuration_id": "configuration-synthetic",
      "origin": "manual",
      "status": "completed",
      "started_at": "2026-09-21T12:00:00Z",
      "finished_at": "2026-09-21T12:01:00Z",
      "repositories_total": 4,
      "repositories_completed": 4,
      "repositories_failed": 0,
      "commits_discovered": 12,
      "commits_verified": 12,
      "allowed_commits": 11,
      "unauthorized_commits": 1
    }
  ],
  "offset": 0,
  "limit": 50
}
```

Garantias:

- O filtro por configuração ocorre antes de `offset`/`limit`.
- `origin` é `scheduled` quando uma `ScheduleOccurrence` referencia a execução; caso contrário, `manual`.
- Ordenação permanece da execução mais recente para a mais antiga.
- Os sete contadores são retornados sem recálculo cliente.

Nesta feature, a ordenação efetivamente alterada é a do histórico de execuções e das listas cronológicas de alertas/falhas. Os endpoints paginados de repositories e commits mantêm sua ordenação de domínio existente.

## 5. Acompanhamento e relatório (reutilizados)

- Snapshot: `GET /executions/{execution_id}`.
- Ticket: `POST /executions/{execution_id}/websocket-tickets`.
- Atualização ao vivo: canal existente vinculado ao ticket descartável.
- Relatório e listas: endpoints de relatório existentes por `execution_id`.

Execuções `pending` e `running` direcionam ao acompanhamento. Estados terminais direcionam ao relatório.

## 6. Error behavior

- `404 configuration_not_found`: plano inexistente; oferecer retorno à lista.
- `409 connection_not_validated`: bloquear escopo/branch e solicitar validação.
- `409 credential_unavailable`: indicar substituição/regularização sem revelar segredo.
- Conflito de execução ativa: manter o plano e oferecer acesso à execução existente quando seu ID estiver disponível.
- `422`: manter valores do formulário e associar validação ao campo ou etapa.
- Falhas externas: exibir apenas a mensagem segura normalizada pelo cliente.

## 7. Contract-test behavior for GitLab dependencies

Validação da conexão, hierarquia e branches devem ser testadas com doubles controlados, nunca com GitLab real. A matriz mínima cobre:

| Scenario | Controlled outcome | Expected UI behavior |
|---|---|---|
| Timeout | Exceção de timeout traduzida para erro seguro | Modal permanece aberto, preserva dados não sensíveis e permite tentar novamente. |
| Rate limit | Resposta controlada equivalente a limite excedido | Mensagem acionável e nenhuma operação dependente liberada indevidamente. |
| Malformed response | Payload fora do contrato | Erro seguro; nenhum dado parcial é interpretado como válido. |
| Unavailable | Falha controlada de indisponibilidade | Erro seguro e estado de conexão não validado. |
| Partial dependent failure | Validação bem-sucedida seguida de falha em hierarquia, branches ou persistência dependente | Indicar a etapa falha, preservar ID recuperável quando existente e nunca anunciar sucesso completo. |
