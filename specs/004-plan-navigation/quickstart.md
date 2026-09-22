# Quickstart: Validar Navegação por Planos

## Prerequisites

- Python 3.13+ com dependências do backend instaladas.
- Node.js e dependências de `frontend/` instaladas.
- Banco de desenvolvimento migrado.
- Somente credenciais e dados sintéticos nos testes.

Os contratos esperados estão em [contracts/frontend-api.md](contracts/frontend-api.md) e os estados em [data-model.md](data-model.md).

## Automated validation

No diretório raiz:

```powershell
Set-Location backend
py -3.14 -m pytest
```

Em outro terminal:

```powershell
Set-Location frontend
npm test -- --run
npm run build
```

Resultados esperados:

- Testes de backend confirmam filtro por `configuration_id`, paginação anterior ao retorno, origem derivada e resumos opcionais de schedule e última execução.
- Testes de frontend cobrem lista/vazio/erro, modal, submissão única, falha parcial, abas, edição, histórico contextual, paginação, execução manual, acompanhamento, relatório e redirecionamentos.
- Testes da integração usam doubles controlados para timeout, rate limit, resposta malformada, indisponibilidade e falha parcial; nenhuma chamada alcança GitLab real.
- Testes responsivos executam em 1440 px e 390 px e verificam usabilidade/estrutura, não igualdade pixel-perfect.
- Testes de desempenho usam respostas controladas e confirmam estado utilizável da lista e do histórico em até 2 segundos, sem atribuir latência externa ao frontend.
- Build conclui sem erros de tipo.

## Start locally

Backend, a partir de `backend/`:

```powershell
$env:PYTHONPATH = (Resolve-Path 'src').Path
py -3.14 -m uvicorn repository_miner.app:app --host 127.0.0.1 --port 8000
```

Frontend, a partir de `frontend/`:

```powershell
npm run dev -- --host 127.0.0.1 --port 5173
```

Abrir `http://127.0.0.1:5173/`.

## End-to-end scenarios

### 1. Initial list

1. Acessar `/`.
2. Confirmar título de Planos de Verificação e ação "Novo plano".
3. Confirmar ausência de navegação principal separada para Configurações e Repositories.
4. Com dados existentes, conferir status, GitLab, branch, periodicidade e última execução quando disponíveis.
5. Sem dados, conferir estado vazio acionável.

### 2. Create plan

1. Abrir "Novo plano" e confirmar que não houve navegação.
2. Preencher nome, URL e token sintéticos.
3. Confirmar que escopo e branch estão bloqueados antes da validação.
4. Validar a conexão e selecionar repositories/branch.
5. Informar e-mails, recorrência, horário e status.
6. Acionar confirmar duas vezes rapidamente e verificar apenas uma submissão.
7. Confirmar fechamento e atualização da lista após sucesso.
8. Reabrir o plano e verificar que o token não aparece.

### 3. Partial failure

1. Simular sucesso na configuração-base e validação, mas falha segura ao salvar schedule.
2. Confirmar que a interface não anuncia criação completa.
3. Confirmar indicação da etapa falha e preservação do ID do plano incompleto.
4. Fechar com confirmação, atualizar a lista e abrir a Configuração para retomada.
5. Inspecionar interface, URL e logs de teste e confirmar ausência do token.

### 4. Plan details and edit

1. Abrir "Visualizar configuração".
2. Confirmar exatamente Configuração e Execuções como abas principais.
3. Editar básicos, escopo, branch, usuários e schedule e recarregar o plano.
4. Alterar a conexão e confirmar bloqueio das dependências até nova validação.
5. Verificar layout em 1440 px e 390 px, teclado e nomes acessíveis das ações, sem exigir pixel-perfect.

### 5. Manual execution and contextual history

1. Em plano habilitado, acionar "Executar agora" e abrir o acompanhamento pelo ID retornado.
2. Repetir com plano desabilitado para schedule e confirmar que a execução manual ainda pode iniciar.
3. Simular concorrência e credencial comprometida e confirmar rejeições seguras.
4. Abrir a aba Execuções em três planos e confirmar que cada lista contém somente seu `configuration_id`.
5. Navegar para a segunda página e confirmar `offset`/`limit` sem carga integral.

### 6. Details, live flow, report and legacy routes

1. Em `running`, usar "Ver detalhes" e confirmar reuso do acompanhamento por snapshot, ticket e canal existentes.
2. Em cada estado terminal, usar "Ver detalhes" e confirmar reuso do relatório e sete contadores.
3. Acessar URLs antigas relevantes e confirmar redirecionamento para plano/execução equivalentes.
4. Confirmar que links internos não apontam para telas removidas.

## Security regression

- Pesquisar nos elementos renderizados e URLs por tokens usados no teste; resultado esperado: zero ocorrências.
- Confirmar que erros GitLab usam mensagem segura.
- Confirmar que credencial comprometida não inicia execução.
- Confirmar que fixtures contêm apenas valores claramente sintéticos.

## Controlled integration-failure validation

Sem conexão externa, configurar doubles para cada caso e executar o fluxo do modal:

1. Timeout durante validação da conexão.
2. Rate limit durante validação ou descoberta.
3. Resposta malformada na hierarquia ou lista de branches.
4. Indisponibilidade durante validação.
5. Validação bem-sucedida seguida de falha parcial em hierarquia, branches ou persistência dependente.

Em todos os casos, confirmar mensagem segura, ausência de segredo, preservação de dados não sensíveis, bloqueio correto das dependências e ausência de falso sucesso.

## Reproducible perceived-performance validation

1. Usar respostas controladas com dados sintéticos para lista de planos e histórico.
2. Iniciar a medição ao entrar na rota.
3. Encerrar quando o conteúdo e as ações principais estiverem utilizáveis.
4. Confirmar duração menor ou igual a 2 segundos nos dois fluxos.
5. Não incluir latência de GitLab real nem executar rede externa.

## Implementation validation — 2026-09-21

### Automated validation

- Backend: `py -3.14 -m pytest` — 125 passed, 1 external GitLab test skipped, 0 failed.
- Frontend: `npm test -- --run` — 25 files, 48 tests passed, 0 failed.
- Production build: `npm run build` — completed successfully; Vite reported only the existing advisory about a chunk larger than 500 kB.
- Controlled perceived performance: plan list and contextual history reached a usable state within 2 seconds using deterministic mocks and no real GitLab latency.
- Responsive checks: plan content and creation modal passed at 1440 px and 390 px without pixel-perfect assertions.
- GitLab doubles: timeout, rate limit, malformed response, unavailability and dependent partial failure passed without a real GitLab connection.

### Six-scenario manual validation

Status: not executed in this environment. Both available browser surfaces (`chrome` and `iab`) reported `Browser is not available` while the local backend and frontend returned HTTP 200. Automated integration coverage for the same flows passed, but it is not recorded as a substitute for the manual task.

## Manual operator acceptance

Status: pending and non-blocking because no representative participants were available in the implementation environment.

Esta validação cobre SC-002, SC-003 e SC-012. Ela não bloqueia implementação, testes automatizados ou build durante o desenvolvimento. Executar quando houver no mínimo cinco participantes representativos.

| Scenario | Requested task | Minimum participants | Observed result | Completion rate | Clarity notes |
|---|---|---:|---|---:|---|
| Localizar e abrir plano | A partir da entrada, localizar um plano informado e abrir sua configuração em até duas ações. | 5 | A preencher na aceitação | A preencher; alvo >= 90% | Registrar hesitações e termos ambíguos. |
| Iniciar criação | A partir da entrada, iniciar em até 10 segundos e concluir um plano válido sem sair do modal. | 5 | A preencher na aceitação | A preencher; alvo >= 90% | Registrar campos ou etapas pouco claros. |
| Compreender o modelo | Explicar com palavras próprias a relação entre plano, configuração, execução e relatório após concluir os fluxos. | 5 | A preencher na aceitação | A preencher; alvo >= 90% | Registrar confusões de nomenclatura e navegação. |

Para cada participante, registrar somente observações necessárias à aceitação, sem dados pessoais ou credenciais.
