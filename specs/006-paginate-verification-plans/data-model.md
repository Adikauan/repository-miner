# Data Model: Paginação de Planos de Verificação

## MonitoringConfiguration (existente)

Representa um Plano de Verificação persistido.

| Campo | Uso nesta feature |
|---|---|
| `id` | Identificador estável e ordenação descendente nesta consulta |
| `name` | Identificação exibida no card/linha |
| `gitlab_base_url` | Resumo da conexão |
| `timezone` | Contexto de schedule |
| `target_branch` | Branch configurada |
| `enabled` | Estado habilitado/desabilitado |
| `credential_status` | Status seguro da credencial, sem plaintext |
| `connection_validated` | Estado da conexão |
| `next_run_at` | Próxima execução quando existente |
| `schedule_summary` | Recorrência, horário e dia aplicável |
| `last_execution` | Resumo da execução mais recente |

### Ordenação

1. Não existe `created_at` em `MonitoringConfiguration`.
2. A consulta usa `id DESC` antes do recorte.
3. Não adicionar campo temporal ou alterar o modelo persistido.
4. A ordem é determinística para consultas repetidas sobre o mesmo conjunto.

## ConfigurationPage

| Campo | Tipo | Regra |
|---|---|---|
| `items` | lista de resumos | Somente itens da página solicitada |
| `offset` | inteiro | Maior ou igual a zero |
| `limit` | inteiro | Entre 1 e 200 |
| `total` | inteiro | Quantidade após filtros e antes do recorte |
| `total_pages` | inteiro | `ceil(total / limit)`; zero quando `total` é zero |

## Invariantes

- `len(items) <= limit`.
- O mesmo item não aparece em páginas diferentes para um dataset estável.
- Itens e metadados não contêm token, ciphertext ou segredo.
- Criação, edição e execução do plano não mudam de semântica.
