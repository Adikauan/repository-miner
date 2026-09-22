# Data Model: Navegação por Planos de Verificação

## Design boundary

Esta feature não cria entidade persistida. `MonitoringConfiguration` continua sendo a fonte do Plano de Verificação. Os modelos abaixo descrevem projeções de leitura e estado de interface.

## VerificationPlanSummary

Projeção usada na página inicial.

| Field | Type | Rules |
|---|---|---|
| `id` | UUID/string | Identidade da configuração existente. |
| `name` | string | Obrigatório, 1–120 caracteres. |
| `gitlab_base_url` | URL string | Exibível; nunca inclui credencial. |
| `enabled` | boolean | Controla scheduler, não a execução manual. |
| `target_branch` | string/null | Nulo enquanto indisponível/não validado. |
| `credential_status` | string | Estado canônico existente; nunca inclui segredo. |
| `connection_validated` | boolean | Calculado contra URL e credencial atuais. |
| `next_run_at` | datetime/null | Próxima ocorrência quando existe schedule. |
| `schedule_summary` | object/null | Somente `recurrence`, `local_time`, `weekday` e `day_of_month`; nulo sem schedule. |
| `last_execution` | object/null | `id`, `status`, `started_at`, `finished_at`; execução mais recente. |

### ScheduleSummary validation

- `recurrence` é `daily`, `weekly` ou `monthly`.
- `local_time` é o horário local configurado.
- `weekday` é informado somente para recorrência semanal.
- `day_of_month` é informado somente para recorrência mensal.
- Identificadores internos, ocorrências, cálculos e estado operacional do scheduler não integram o resumo.

## VerificationPlanDetail

Projeção da configuração completa existente.

| Field | Type | Rules |
|---|---|---|
| Campos de `VerificationPlanSummary` | — | Mesmo significado e segurança. |
| `timezone` | timezone string | Usada para cálculo do schedule. |
| `selections` | SelectionRule[] | Regras canônicas de include/exclude. |
| `allowed_emails` | string[] | Únicos após trim + casefold. |
| `schedule` | Schedule/null | Recorrência e horário existentes. |

### Relationships

- Um plano possui zero ou muitas regras de seleção.
- Um plano possui zero ou muitos usuários permitidos.
- Um plano possui zero ou um schedule.
- Um plano possui muitas execuções.
- Um plano referencia uma credencial atual, nunca exposta em plaintext.

## CreatePlanDraft

Estado efêmero do modal, não persistido como nova entidade.

| Field | Type | Rules |
|---|---|---|
| `name` | string | Obrigatório, 1–120 caracteres. |
| `gitlab_base_url` | URL string | Obrigatória. |
| `gitlab_token` | secret string | Obrigatório antes da criação-base; mantido somente pelo tempo necessário e limpo após persistência. |
| `timezone` | string | Padrão `UTC`. |
| `enabled` | boolean | Padrão `true`. |
| `connection_validated` | boolean | `false` até validação da identidade atual. |
| `persisted_configuration_id` | string/null | Preenchido quando a configuração-base é criada. |
| `selected_rules` | SelectionRule[] | Editável somente após validação. |
| `target_branch` | string | Padrão existente; dependente da conexão. |
| `allowed_emails` | string[] | Normalizados pelo backend; duplicatas locais devem ser sinalizadas. |
| `schedule` | Schedule | Diário, semanal ou mensal. |
| `phase` | enum | Ver transições abaixo. |
| `failed_step` | enum/null | Etapa obrigatória que falhou. |

### Creation state transitions

```text
editing
  -> persisting_base
  -> validating_connection
  -> connection_ready
  -> saving_basic
  -> saving_scope
  -> saving_users
  -> saving_schedule
  -> completed

qualquer etapa assíncrona -> failed_partial (se já existe ID)
qualquer etapa anterior ao ID -> failed
failed/failed_partial -> retry da etapa segura correspondente
```

Regras:

- Apenas uma transição assíncrona pode estar ativa.
- Falha obrigatória interrompe etapas seguintes.
- `completed` exige sucesso de todas as etapas obrigatórias.
- Trocar URL ou credencial redefine `connection_validated` e limpa opções dependentes.
- Fechar depois de `persisted_configuration_id` informa que existe um plano incompleto e atualiza a lista.

## PlanExecutionSummary

| Field | Type | Rules |
|---|---|---|
| `id` | string | Identificador canônico da execução. |
| `configuration_id` | string | Deve ser igual ao plano da aba atual. |
| `origin` | `manual` \| `scheduled` | Derivado de `ScheduleOccurrence`. |
| `status` | enum | Somente `pending`, `running`, `completed`, `partially_completed`, `failed`. |
| `started_at` / `finished_at` | datetime/null | Término pode ser nulo fora de estado terminal. |
| sete contadores canônicos | integer | Não negativos e fornecidos pelo backend. |

Os sete contadores são `repositories_total`, `repositories_completed`, `repositories_failed`, `commits_discovered`, `commits_verified`, `allowed_commits` e `unauthorized_commits`.

### Execution transitions

```text
pending -> running -> completed
                   -> partially_completed
                   -> failed
pending ----------------> failed
```

O frontend não cria estado adicional nem recalcula o estado terminal.

## PaginatedExecutionPage

| Field | Type | Rules |
|---|---|---|
| `items` | PlanExecutionSummary[] | Todos pertencem ao `configuration_id` solicitado. |
| `offset` | integer | Maior ou igual a zero. |
| `limit` | integer | Entre 1 e 200; interface usa 50. |

## Existing report and live models

`ExecutionReportView`, itens de repository/commit/alerta/falha e eventos de acompanhamento permanecem definidos pelos contratos existentes. Esta feature somente os referencia pelo `execution_id` selecionado.
