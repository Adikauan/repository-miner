# Contract: Paginação da Listagem de Planos

## Endpoint

`GET /api/v1/configurations?offset={offset}&limit={limit}`

- `offset`: inteiro maior ou igual a zero; padrão `0`.
- `limit`: inteiro entre `1` e `200`; padrão da tela inicial `20`.

## Ordenação e recorte

O backend deve aplicar filtros existentes, ordenar `MonitoringConfiguration.id DESC`, calcular `total` e então aplicar `offset`/`limit`. O frontend não reordena nem pagina localmente.

## Resposta 200

```json
{
  "items": [{
    "id": "uuid",
    "name": "Plano sintético",
    "gitlab_base_url": "https://gitlab.example.com",
    "timezone": "UTC",
    "enabled": true,
    "target_branch": "QA",
    "credential_status": "active",
    "connection_validated": true,
    "next_run_at": null,
    "schedule_summary": null,
    "last_execution": null
  }],
  "offset": 0,
  "limit": 20,
  "total": 1,
  "total_pages": 1
}
```

`items` preserva os campos atuais dos cards. Segredos e estruturas internas de scheduler são proibidos.

## Empty/out-of-range page

Uma consulta sem planos retorna `200` com `items: []`, `total: 0` e `total_pages: 0`. Se um `offset` posterior ficar inválido após alteração do conjunto, os metadados reais permitem que o frontend corrija para a última página válida ou para a primeira.

## Errors

Parâmetros fora dos limites seguem a validação HTTP existente. Falhas de consulta usam mensagem segura e retry, sem detalhes internos ou credenciais.
