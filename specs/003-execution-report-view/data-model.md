# Data Model: Visualização de Relatório de Execução

Este modelo descreve apenas projeções usadas pela interface. Não cria entidades persistentes novas.

## ExecutionReportView

Visão consolidada identificada por execution_id.

| Campo | Tipo | Regra |
|---|---|---|
| execution_id | string | Obrigatório; identifica a execução consultada |
| configuration_id | string | Quando fornecido pelo contrato de execução |
| status | enum | pending, running, completed, partially_completed ou failed |
| origin | string/null | Manual, agendada ou valor disponível no contrato |
| started_at | datetime/null | Horário de início quando disponível |
| finished_at | datetime/null | Horário de término quando disponível |
| repositories_total | integer | Contador canônico fornecido pelo backend |
| repositories_completed | integer | Contador canônico fornecido pelo backend |
| repositories_failed | integer | Contador canônico fornecido pelo backend |
| commits_discovered | integer | Contador canônico fornecido pelo backend |
| commits_verified | integer | Contador canônico fornecido pelo backend |
| allowed_commits | integer | Contador canônico fornecido pelo backend |
| unauthorized_commits | integer | Contador canônico fornecido pelo backend |

O frontend deve exibir os contadores recebidos e não derivá-los das coleções.

## RepositoryReportItem

Resultado de um repository associado à execução.

| Campo | Tipo | Regra |
|---|---|---|
| id | string | Identificador do item quando disponível |
| repository_id | string | Identifica o repository |
| branch | string | Branch processada |
| status | string | Status informado pelo contrato |
| commits_count | integer/null | Quantidade quando disponível |
| failure | RepositoryFailureItem/null | Falha segura quando aplicável |

## CommitVerificationItem

Commit verificado ou listado pela execução.

| Campo | Tipo | Regra |
|---|---|---|
| commit_hash | string | Identidade canônica do commit |
| repository | string/null | Repository quando fornecido |
| branch | string/null | Branch quando fornecida |
| author | string/null | Autor quando fornecido |
| author_email | string/null | Propriedade presente; null representa ausência |
| committed_at | datetime/null | Data quando fornecida |
| message | string/null | Mensagem quando fornecida |
| authorization_result | string/null | allowed ou unauthorized quando fornecido |

## UnauthorizedCommitAlertItem

Alerta de autoria não permitida pertencente à execução original de detecção.

| Campo | Tipo | Regra |
|---|---|---|
| id | string | Identificador do alerta |
| repository_id | string | Repository de origem |
| branch | string | Branch de origem |
| commit_hash | string | Commit que gerou o alerta |
| author_name | string/null | Autor informado |
| author_email | string/null | Sempre representado, inclusive null |
| committed_at | datetime/null | Data do commit |
| detection_execution_id | string/null | Execução original quando fornecida |

Uma consulta posterior não transfere o ownership do alerta para outra execução.

## RepositoryFailureItem

Falha segura de processamento de repository.

| Campo | Tipo | Regra |
|---|---|---|
| id | string | Identificador quando disponível |
| repository_id | string/null | Repository afetado quando disponível |
| branch | string/null | Branch afetada quando disponível |
| code | string | Código/categoria segura |
| safe_reason | string | Mensagem sem tokens ou segredos |
| occurred_at | datetime/null | Data quando disponível |

## PaginatedCollection

Coleção com items e metadados offset/limit quando o contrato oferecer paginação. A troca de página deve preservar execution_id e o estado das demais áreas.
