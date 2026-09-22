# Contrato de consumo do relatório

Este documento registra o uso frontend dos contratos existentes. Ele não cria ou altera endpoints.

## Identificação

Todas as consultas usam o execution_id da execução. Uma execução inexistente deve ser tratada como erro de não encontrado.

## Resumo

Consulta GET /api/v1/executions/{execution_id}/report retorna:

- execution_id;
- status, limitado a pending, running, completed, partially_completed e failed;
- repositories_total;
- repositories_completed;
- repositories_failed;
- commits_discovered;
- commits_verified;
- allowed_commits;
- unauthorized_commits.

Quando disponíveis em consulta de execução, também são apresentados configuration_id, origem, started_at e finished_at.

## Coleções

As coleções devem usar os recursos existentes e seus parâmetros de paginação:

- GET /api/v1/executions/{execution_id}/repositories: repository_id, branch, status, observed_head e failure_reason quando disponíveis;
- GET /api/v1/executions/{execution_id}/commits: commit_hash, verification_source e metadados adicionais fornecidos pelo contrato;
- GET /api/v1/executions/{execution_id}/unauthorized-commits: repository_id, branch, commit_hash, author_name, author_email anulável e committed_at;
- GET /api/v1/executions/{execution_id}/failures: repository/branch quando disponíveis, stage, code, safe_reason e occurred_at.

As respostas paginadas devem preservar items, offset e limit. O frontend não deve assumir que uma coleção vazia representa erro.

## Segurança

Mensagens de erro e dados de falha exibidos devem usar somente campos seguros. Tokens, credenciais, secrets e valores de autorização não fazem parte do contrato de apresentação.

## Execuções ativas

Para pending ou running, o frontend pode oferecer navegação para o acompanhamento de execução existente. Não deve abrir um segundo mecanismo de eventos. Após um estado terminal, o relatório persistido é a fonte prioritária.

## Compatibilidade

Nenhum campo novo é obrigatório neste incremento. Quando um campo opcional não existir no payload atual, a interface deve omiti-lo ou exibir a ausência de forma explícita, sem inventar valores.
