# Tasks: Navegação por Planos de Verificação

**Input**: Design documents from `/specs/004-plan-navigation/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/frontend-api.md, quickstart.md

**Tests**: A specification exige testes frontend e regressão dos contratos afetados; as tarefas de teste devem ser escritas e observadas falhando antes da implementação correspondente.

**Organization**: As tarefas são agrupadas por história de usuário para permitir implementação e validação incrementais.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode executar em paralelo por atuar em arquivos diferentes e não depender de tarefa incompleta.
- **[Story]**: história atendida (`US1` a `US5`); setup, foundation e polish não usam esse rótulo.
- Toda tarefa inclui caminho exato de arquivo.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Preparar a estrutura da feature sem alterar regras ou adicionar dependências.

- [X] T001 Criar a estrutura do módulo de planos e seu arquivo de exportação em `frontend/src/plans/index.ts`
- [X] T002 [P] Criar fixtures exclusivamente sintéticas de plano, schedule e execução em `frontend/tests/plans/fixtures.ts`
- [X] T003 [P] Criar helpers de renderização com roteador e viewport para os testes da feature em `frontend/tests/plans/renderPlanApp.tsx`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Estabelecer tipos, roteamento e tratamento de erro compartilhados por todas as histórias.

**CRITICAL**: Nenhuma história deve ser implementada antes desta fase.

- [X] T004 Definir `VerificationPlanSummary`, `VerificationPlanDetail`, `CreatePlanDraft`, `PlanExecutionSummary` e `PaginatedExecutionPage` em `frontend/src/plans/types.ts`, preservando literalmente: nome obrigatório de 1–120 caracteres; `target_branch` e `last_execution` anuláveis; token apenas efêmero; cinco estados canônicos; sete contadores inteiros não negativos; `offset >= 0`; `limit` entre 1 e 200
- [X] T005 Centralizar adaptadores de plano sobre as operações existentes, sem duplicar chamadas HTTP, em `frontend/src/plans/api.ts`
- [X] T006 Implementar somente a infraestrutura neutra de routing (tipos, helpers e fallback para a superfície existente), sem importar ou registrar páginas ainda inexistentes, em `frontend/src/app/routes.tsx`
- [X] T007 Integrar somente o provedor e o shell de roteamento preservando as superfícies existentes e o build compilável, sem antecipar rotas de user stories, em `frontend/src/app/App.tsx`
- [X] T008 [P] Consolidar a sanitização de mensagens de erro para impedir tokens, ciphertext e detalhes internos em `frontend/src/shared/api/errors.ts`
- [X] T009 Adicionar testes de unidade para sanitização de mensagens sensíveis em `frontend/src/shared/api/errors.test.ts`

**Checkpoint**: Tipos, rotas e erros compartilhados prontos; histórias podem iniciar.

---

## Phase 3: User Story 1 - Consultar planos na página inicial (Priority: P1) MVP

**Goal**: Exibir Planos de Verificação como primeira tela, com resumo, estados e ações principais.

**Independent Test**: Acessar `/` com lista preenchida, vazia e com erro; conferir resumos, "Novo plano", "Visualizar configuração" e ausência de entradas principais separadas.

### Tests for User Story 1

- [X] T010 [P] [US1] Adicionar teste de contrato para `GET /configurations` com `last_execution` e `schedule_summary` opcionais, cobrindo `daily`, `weekly` com `weekday`, `monthly` com `day_of_month`, horário, ausência de schedule e exclusão de estruturas internas/credenciais em `backend/tests/contract/test_configuration_list_contract.py`
- [X] T011 [P] [US1] Adicionar testes da página inicial para loading, lista, dados opcionais, erro e vazio acionável em `frontend/tests/plans/plan-list.test.tsx`
- [X] T012 [P] [US1] Adicionar testes responsivos e acessíveis para cards/linhas e ações de plano em `frontend/tests/plans/plan-list.a11y.test.tsx`

### Implementation for User Story 1

- [X] T013 [US1] Estender a consulta de configurações sem N+1 e sem alterar persistência com `last_execution` opcional (`id`, `status`, `started_at`, `finished_at`) e `schedule_summary` opcional contendo somente `recurrence`, `local_time`, `weekday` e `day_of_month` em `backend/src/repository_miner/configuration/api/router.py`
- [X] T014 [P] [US1] Implementar o item responsivo com nome, status, GitLab, branch, periodicidade, última execução e ação acessível em `frontend/src/plans/PlanCard.tsx`
- [X] T015 [US1] Implementar loading, erro, vazio e listagem de planos com "Novo plano" no topo em `frontend/src/plans/PlanListPage.tsx`
- [X] T016 [US1] Registrar a rota inicial somente depois de `PlanListPage` existir e atualizar a navegação para remover Configurações/Histórico como entradas principais, mantendo o build compilável, em `frontend/src/app/routes.tsx` e `frontend/src/app/App.tsx`

**Checkpoint**: US1 funciona isoladamente como MVP navegável.

---

## Phase 4: User Story 2 - Criar um plano em um único fluxo (Priority: P1)

**Goal**: Criar plano e configuração por um modal único, com conexão validada, dependências desbloqueadas e falha parcial honesta.

**Independent Test**: Abrir o modal, preencher dados sintéticos, validar, selecionar escopo/branch, configurar usuários/schedule/status e confirmar; repetir com falhas e clique duplicado.

### Tests for User Story 2

- [X] T017 [P] [US2] Adicionar testes do estado `CreatePlanDraft` e das transições `editing` até `completed`, `failed` e `failed_partial` em `frontend/src/plans/createPlanState.test.ts`
- [X] T018 [P] [US2] Adicionar testes de abertura, fechamento, confirmação de descarte e bloqueio das dependências antes da validação em `frontend/tests/plans/create-plan-modal.test.tsx`
- [X] T019 [P] [US2] Adicionar testes da sequência canônica, sucesso, retomada e submissão duplicada usando doubles controlados para timeout, rate limit, resposta GitLab malformada, indisponibilidade e falhas parciais em hierarquia, branches ou persistência dependente, sem qualquer GitLab real, em `frontend/tests/plans/create-plan-flow.test.tsx`
- [X] T020 [P] [US2] Adicionar teste que procura o token sintético em UI, mensagens e URL após persistência em `frontend/tests/plans/create-plan-security.test.tsx`

### Implementation for User Story 2

- [X] T021 [US2] Implementar a máquina de estado de criação com uma operação assíncrona ativa, parada na primeira falha obrigatória, invalidação da conexão ao trocar URL/token e limpeza do token após persistência em `frontend/src/plans/createPlanState.ts`
- [X] T022 [US2] Implementar o orquestrador que cria a base, valida a conexão e salva básicos, escopo, usuários e schedule em ordem canônica em `frontend/src/plans/createPlanFlow.ts`
- [X] T023 [P] [US2] Extrair campos reutilizáveis de escopo e branch sobre `RepositoryTree` para `frontend/src/configurations/ScopeFields.tsx`
- [X] T024 [P] [US2] Extrair campos reutilizáveis de usuários permitidos e schedule para `frontend/src/configurations/ScheduleAndUsersFields.tsx`
- [X] T025 [US2] Implementar o modal rolável com identificação, conexão, escopo, branch, usuários, schedule, status, validações e feedback por etapa em `frontend/src/plans/CreatePlanModal.tsx`
- [X] T026 [US2] Conectar o modal à ação "Novo plano", atualizar a lista no sucesso e expor plano incompleto recuperável após falha/fechamento em `frontend/src/plans/PlanListPage.tsx`

**Checkpoint**: US2 cria um plano completo sem sair da lista e nunca anuncia sucesso parcial.

---

## Phase 5: User Story 3 - Consultar e editar um plano (Priority: P1)

**Goal**: Apresentar um plano em uma página de detalhes com exatamente Configuração e Execuções, permitindo edição canônica.

**Independent Test**: Abrir `/plans/{id}`, conferir duas abas, editar cada grupo suportado, invalidar/revalidar conexão e recarregar valores persistidos.

### Tests for User Story 3

- [X] T027 [P] [US3] Adicionar testes de detalhes para loading, inexistente, erro e exatamente duas abas principais em `frontend/tests/plans/plan-details.test.tsx`
- [X] T028 [P] [US3] Atualizar testes de edição para nome 1–120, URL, status, escopo, branch, e-mails únicos após trim + casefold e schedule em `frontend/tests/configurations/ConfigurationEditor.editing.test.tsx`
- [X] T029 [P] [US3] Adicionar testes de alteração de URL/credencial, invalidação da conexão e ausência de plaintext persistido em `frontend/tests/plans/plan-connection-edit.test.tsx`

### Implementation for User Story 3

- [X] T030 [US3] Refatorar o editor existente para reutilizar `ScopeFields` e `ScheduleAndUsersFields`, editar URL/credencial pela operação dedicada e preservar incidentes de credencial em `frontend/src/configurations/ConfigurationEditor.tsx`
- [X] T031 [P] [US3] Implementar a aba Configuração como composição do editor canônico em `frontend/src/plans/PlanConfigurationTab.tsx`
- [X] T032 [US3] Implementar carregamento, cabeçalho, "Executar agora" e exatamente duas abas endereçáveis em `frontend/src/plans/PlanDetailsPage.tsx`
- [X] T033 [US3] Conectar a ação "Visualizar configuração" e a rota `/plans/:planId/configuration` em `frontend/src/app/routes.tsx`

**Checkpoint**: US3 permite consultar e editar um plano no novo contexto sem duplicar regras.

---

## Phase 6: User Story 4 - Executar um plano e consultar seu histórico (Priority: P1)

**Goal**: Iniciar execução manual e listar somente execuções do plano, com paginação, origem, contadores e navegação adequada ao estado.

**Independent Test**: Executar plano habilitado e desabilitado para schedule, validar conflitos, abrir históricos de três planos, paginar e navegar de `running` ao acompanhamento e de terminais ao relatório.

### Tests for User Story 4

- [X] T034 [P] [US4] Adicionar testes de contrato para filtro `configuration_id` antes de `offset`/`limit`, ordenação e sete contadores em `backend/tests/contract/test_execution_list_contract.py`
- [X] T035 [P] [US4] Adicionar testes de integração para origem `scheduled` via `ScheduleOccurrence` e fallback `manual` em `backend/tests/integration/test_execution_origin.py`
- [X] T036 [P] [US4] Adicionar testes da aba para loading, vazio, erro, somente plano atual, origem, cinco estados, sete contadores e paginação em `frontend/tests/plans/plan-executions-tab.test.tsx`
- [X] T037 [P] [US4] Adicionar testes de execução manual habilitada/desabilitada, concorrência, credencial comprometida e uso do `execution_id` em `frontend/tests/plans/manual-execution.test.tsx`
- [X] T038 [P] [US4] Adicionar teste de navegação de `pending`/`running` para acompanhamento e estados terminais para relatório em `frontend/tests/plans/execution-details-navigation.test.tsx`

### Implementation for User Story 4

- [X] T039 [US4] Estender `GET /executions` com `configuration_id` opcional aplicado antes da paginação e `origin` derivado de `ScheduleOccurrence`, sem nova coluna, em `backend/src/repository_miner/executions/api/query_router.py`
- [X] T040 [US4] Atualizar tipos e consulta de execuções para aceitar `configuration_id`, `offset`, `limit`, `origin` e resposta paginada em `frontend/src/executions/api.ts`
- [X] T041 [P] [US4] Implementar linha/card responsivo de execução com origem, horários, estado, sete contadores e "Ver detalhes" acessível em `frontend/src/plans/ExecutionRow.tsx`
- [X] T042 [US4] Implementar loading, vazio, erro e paginação mantendo somente uma página em memória em `frontend/src/plans/PlanExecutionsTab.tsx`
- [X] T043 [US4] Integrar "Executar agora" com mensagens seguras e navegação por `execution_id` em `frontend/src/plans/PlanDetailsPage.tsx`
- [X] T044 [US4] Reutilizar `ExecutionDetailPage` para estados ativos e `ReportDetailPage` para terminais nas rotas por execução em `frontend/src/app/routes.tsx`

**Checkpoint**: US4 mantém execuções e resultados integralmente contextualizados pelo plano.

---

## Phase 7: User Story 5 - Manter caminhos antigos coerentes (Priority: P2)

**Goal**: Remover interfaces redundantes e redirecionar URLs antigas relevantes para seus equivalentes.

**Independent Test**: Abrir todas as URLs antigas conhecidas, verificar redirecionamentos inequívocos e confirmar que nenhum link interno aponta para telas removidas.

### Tests for User Story 5

- [X] T045 [P] [US5] Adicionar testes de redirecionamento de configuração, histórico, acompanhamento e relatório antigos em `frontend/tests/plans/legacy-routes.test.tsx`
- [X] T046 [P] [US5] Adicionar teste que percorre a navegação renderizada e rejeita links para Configurações/Repositories removidos em `frontend/tests/plans/navigation-links.test.tsx`

### Implementation for User Story 5

- [X] T047 [US5] Implementar redirecionamentos de URLs antigas com correspondência inequívoca e fallback para a lista de planos em `frontend/src/app/routes.tsx`
- [X] T048 [US5] Remover o fluxo redundante de listagem/seleção de configurações sem remover APIs e editor reutilizados em `frontend/src/configurations/ConfigurationListPage.tsx`
- [X] T049 [US5] Remover a entrada global redundante de histórico e manter acesso contextual por plano em `frontend/src/app/App.tsx`

**Checkpoint**: US5 encerra a transição sem interfaces concorrentes ou links mortos.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Validar qualidade, segurança, responsividade e regressão de ponta a ponta.

- [X] T050 [P] Adicionar teste responsivo integrado para lista, modal e detalhes nos viewports verificáveis de 1440 px e 390 px, validando usabilidade e ausência de quebra estrutural sem comparação pixel-perfect, em `frontend/tests/plans/plan-navigation.responsive.test.tsx`
- [X] T051 [P] Adicionar varredura de segredos em fixtures, textos renderizados e URLs da feature em `frontend/tests/plans/secret-regression.test.tsx`
- [X] T052 Revisar componentes de `frontend/src/plans/` para foco por teclado, rótulos, tooltips de ícones, feedback de loading, mensagens seguras e comportamento estrutural consistente em 1440 px e 390 px
- [X] T053 Executar e registrar a validação backend (`py -3.14 -m pytest`) e frontend (`npm test -- --run` e `npm run build`) em `specs/004-plan-navigation/quickstart.md`
- [ ] T054 Executar os seis cenários manuais e a regressão de segurança, registrando resultados em `specs/004-plan-navigation/quickstart.md`
- [X] T055 Revisar as alterações contra FR-037 e os dez princípios constitucionais, documentando qualquer desvio encontrado em `specs/004-plan-navigation/plan.md`
- [X] T056 [P] Medir em teste reproduzível o tempo entre entrada na rota e estado utilizável da lista de planos e do histórico com respostas controladas, exigindo no máximo 2 segundos e excluindo latência de GitLab real, em `frontend/tests/plans/perceived-performance.test.tsx`
- [ ] T057 Executar quando houver participantes o roteiro manual não bloqueante de SC-002, SC-003 e SC-012 com no mínimo cinco operadores, registrando cenário, tarefa, resultado observado, taxa de conclusão e notas de clareza em `specs/004-plan-navigation/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: sem dependências.
- **Foundational (Phase 2)**: depende do Setup e bloqueia todas as histórias.
- **US1 (Phase 3)**: depende da Foundation; entrega o MVP.
- **US2 (Phase 4)**: depende da Foundation e integra sua abertura/resultado com a lista da US1.
- **US3 (Phase 5)**: depende da Foundation; usa os campos extraídos na US2 se essa fase já estiver pronta, mas pode extrair os mesmos componentes como primeiro passo para validação isolada.
- **US4 (Phase 6)**: depende da Foundation; integra a aba no shell da US3 e pode ser testada isoladamente por renderização do componente.
- **US5 (Phase 7)**: depende das rotas-alvo de US1, US3 e US4 estarem prontas.
- **Polish (Phase 8)**: depende de todas as histórias desejadas.

### User Story Dependency Graph

```text
Setup -> Foundation -> US1 (MVP)
                    -> US2
                    -> US3 -> US4
US1 + US3 + US4 ----------------> US5
US1 + US2 + US3 + US4 + US5 ---> Polish
```

### Within Each User Story

- Escrever testes e confirmar falha antes de implementar.
- Tipos/contratos antes de serviços e componentes consumidores.
- Consultas backend antes da integração frontend que depende delas.
- Componentes menores antes da página que os compõe.
- Validar o checkpoint da história antes da próxima fase sequencial.

### Parallel Opportunities

- T002 e T003 podem executar em paralelo após T001.
- T008 pode avançar em paralelo com T004–T007; T009 inicia depois de T008.
- Em US1, T010–T012 podem ser escritos em paralelo; T014 pode avançar em paralelo com T013.
- Em US2, T017–T020 podem ser escritos em paralelo; T023 e T024 podem ser implementados em paralelo.
- Em US3, T027–T029 podem ser escritos em paralelo; T031 pode avançar após a interface do editor estar definida.
- Em US4, T034–T038 podem ser escritos em paralelo; T041 pode avançar em paralelo com T039/T040.
- Em US5, T045 e T046 podem ser escritos em paralelo.
- T050, T051 e T056 podem executar em paralelo no polish; T057 é aceitação manual não bloqueante e ocorre quando houver participantes.

---

## Parallel Examples

### User Story 1

```text
Task T010: contrato backend do resumo de planos
Task T011: estados da listagem frontend
Task T012: acessibilidade e responsividade do item
```

### User Story 2

```text
Task T017: transições da criação
Task T018: comportamento do modal
Task T019: fluxo composto e falha parcial
Task T020: não exposição do token
```

### User Story 3

```text
Task T027: shell de detalhes e abas
Task T028: edição dos grupos canônicos
Task T029: invalidação e segurança da conexão
```

### User Story 4

```text
Task T034: filtro e paginação do contrato
Task T035: derivação da origem
Task T036: histórico contextual
Task T037: execução manual
Task T038: navegação por estado
```

### User Story 5

```text
Task T045: redirecionamentos antigos
Task T046: ausência de links redundantes
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Concluir Setup e Foundation.
2. Concluir T010–T016.
3. Parar e validar a US1 independentemente em `/`.
4. Demonstrar a nova entrada por Planos de Verificação antes de expandir mutações.

### Incremental Delivery

1. US1: lista inicial e novo modelo mental.
2. US2: criação completa em modal.
3. US3: configuração contextual e edição.
4. US4: execução manual, histórico, acompanhamento e relatório.
5. US5: remoção/redirecionamento das experiências antigas.
6. Polish: regressão completa e verificação constitucional.
7. Executar T057 como aceitação manual quando houver participantes, sem bloquear a implementação técnica durante o desenvolvimento.

### Parallel Team Strategy

Depois da Foundation, US1, a máquina/orquestrador de US2 e os contratos backend de US4 podem avançar em paralelo em arquivos distintos. A integração de rotas deve permanecer serializada para evitar conflitos em `frontend/src/app/routes.tsx` e `frontend/src/app/App.tsx`.

## Notes

- `[P]` indica arquivos diferentes e ausência de dependência imediata.
- Cada história possui critério de teste independente e checkpoint explícito.
- Não adicionar entidade persistida, migração, mecanismo paralelo de relatório ou acompanhamento.
- Nunca registrar token, resposta sensível ou fixture real.
- Interromper em falha obrigatória e preservar rastreabilidade do plano/execução.

## Phase 9: Convergence

- [ ] T058 Persistir `timezone` e `enabled` na criação-base e garantir que um Plano de Verificação solicitado como desabilitado permaneça desabilitado após a criação per FR-013 e US2/AC3 (partial)
- [ ] T059 Unificar `CreatePlanModal` com o orquestrador canônico para que validar conexão não conclua silenciosamente uma criação-base, todas as etapas obrigatórias exponham processamento/erro/falha parcial e `failedStep`/ID recuperável sejam preservados per FR-005, FR-016 e US2/AC5 (contradicts)
- [ ] T060 Preservar `group`, `subgroup` e `repository` ao transformar a seleção da árvore GitLab em regras de escopo, incluindo testes para os três tipos per FR-010 (partial)
- [ ] T061 Manter o usuário na listagem após a criação bem-sucedida, fechar o modal, recarregar os planos e tornar o plano criado visível sem navegação automática per FR-017 e US2/AC3 (contradicts)
- [ ] T062 Exibir término e os sete contadores canônicos, incluindo `repositories_total`, em `ExecutionRow`, com cobertura para valores disponíveis e ausentes per FR-027 e T041 (partial)
- [ ] T063 Resolver `configuration_id` para URLs legadas que identificam execução ou relatório e redirecionar ao acompanhamento/relatório contextual equivalente, mantendo fallback somente quando não houver correspondência útil per FR-034 e T045/T047 (partial)
- [ ] T064 Completar os testes frontend de criação, detalhes, execuções, navegação e responsividade com descarte confirmado, retomada, submissão duplicada, falhas por etapa, loading/not-found/error, cinco estados, paginação real e navegação renderizada por estado per FR-038 (partial)
- [ ] T065 Eliminar o N+1 de credenciais em `GET /configurations` com carregamento eager ou consulta em lote e adicionar teste que limite a quantidade de consultas independentemente do número de planos per T013 e plan: query extension (partial)
