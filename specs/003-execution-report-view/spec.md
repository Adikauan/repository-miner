# Feature Specification: Visualização de Relatório de Execução

**Feature Branch**: `003-execution-report-view`

**Created**: 2026-09-20

**Status**: Draft

**Input**: User description: adicionar ao frontend a consulta e visualização do relatório persistido de uma execução de mineração.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Consultar relatório de uma execução (Priority: P1)

O operador consegue abrir o relatório de uma execução a partir do histórico, do acompanhamento ou dos detalhes da execução e consultar o resultado consolidado produzido pelo backend.

**Why this priority**: O relatório é a forma principal de compreender o resultado de uma mineração já iniciada.

**Independent Test**: Com uma execução persistida, abrir o relatório pelo identificador da execução e verificar resumo, contadores e listas disponíveis.

**Acceptance Scenarios**:

1. **Given** uma execução existente, **When** o operador seleciona a ação de relatório, **Then** a interface abre o relatório correspondente sem criar uma nova execução.
2. **Given** uma execução inexistente, **When** o operador acessa seu identificador, **Then** a interface informa que a execução não foi encontrada.
3. **Given** um relatório ainda indisponível, **When** o operador acessa a tela, **Then** a interface informa essa condição e permite retornar ou acompanhar a execução quando aplicável.

### User Story 2 - Interpretar o resultado consolidado (Priority: P1)

O operador visualiza o estado, os dados principais, os sete contadores canônicos e o resultado por repository, commits e alertas de autoria não permitida.

**Why this priority**: A leitura consolidada permite avaliar rapidamente o que foi processado e quais itens exigem atenção.

**Independent Test**: Carregar relatórios sintéticos nos estados terminal e parcial e conferir que todos os valores apresentados correspondem aos dados persistidos.

**Acceptance Scenarios**:

1. **Given** um relatório concluído, **When** ele é carregado, **Then** a interface apresenta identificação, origem, horários, estado, contadores e detalhes disponíveis.
2. **Given** um relatório parcialmente concluído ou falho, **When** ele é carregado, **Then** repositories com falha ficam distinguíveis e suas mensagens seguras são exibidas.
3. **Given** um commit cujo `author_email` é nulo, **When** ele aparece na lista, **Then** a ausência do e-mail é representada explicitamente, sem omitir o campo.

### User Story 3 - Acompanhar uma execução ativa e navegar pelo histórico (Priority: P2)

O operador pode abrir o relatório a partir do histórico, voltar à listagem anterior e, enquanto a execução estiver ativa, acessar o acompanhamento em tempo real já existente.

**Why this priority**: O operador precisa alternar entre acompanhamento e resultado final sem duplicar fluxos ou perder o contexto da execução.

**Independent Test**: Abrir uma execução `running`, acessar o acompanhamento existente, voltar ao histórico e abrir uma execução terminal.

**Acceptance Scenarios**:

1. **Given** uma execução `running`, **When** o operador acessa o relatório, **Then** são mostrados os dados disponíveis e uma ação para o acompanhamento existente.
2. **Given** uma execução terminal, **When** o operador reabre o relatório, **Then** a consulta persistida prevalece sobre eventos anteriores.
3. **Given** uma lista paginada, **When** o operador muda de página, **Then** somente a lista correspondente é atualizada e o restante da tela permanece utilizável.

### Edge Cases

- A execução pode estar em `pending`, `running`, `completed`, `partially_completed` ou `failed`; nenhum estado adicional deve ser criado.
- Um relatório pode não possuir repositories, commits, alertas ou falhas; cada lista vazia deve ser apresentada como resultado válido.
- Repositories concluídos e falhos podem coexistir em uma mesma execução.
- Um `UnauthorizedCommitAlert` pertence somente à execução original de detecção; uma execução posterior que reutilize a verificação não deve reapresentá-lo como novo.
- Falhas devem mostrar categoria/código, mensagem segura e data quando disponíveis, sem tokens, credenciais, secrets ou outros dados sensíveis.
- Listas grandes devem respeitar a paginação fornecida pelo serviço existente, sem exigir recarregamento integral da aplicação.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: A interface deve permitir abrir o relatório usando o identificador de uma execução a partir do histórico, acompanhamento ou detalhes da execução.
- **FR-002**: A interface deve consultar os dados persistidos do relatório e não reconstruí-los a partir de eventos quando existir um relatório persistido.
- **FR-003**: A tela deve representar loading, sucesso, erro, execução inexistente e relatório ainda indisponível.
- **FR-004**: O resumo deve apresentar identificador da execução, configuração relacionada, origem quando disponível, início, término e estado final.
- **FR-005**: A interface deve utilizar somente os estados `pending`, `running`, `completed`, `partially_completed` e `failed`.
- **FR-006**: A interface deve exibir, sem recalcular, os contadores `repositories_total`, `repositories_completed`, `repositories_failed`, `commits_discovered`, `commits_verified`, `allowed_commits` e `unauthorized_commits` fornecidos pelo backend.
- **FR-007**: O relatório deve permitir consultar repositories associados à execução com nome, branch, status, quantidade de commits e falha segura quando disponíveis.
- **FR-008**: Repositories concluídos e falhos devem ser visualmente distinguíveis.
- **FR-009**: O relatório deve permitir consultar commits verificados com `commit_hash`, repository, branch, autor, `author_email`, data, mensagem e resultado da validação quando disponíveis.
- **FR-010**: Quando `author_email` for nulo, a propriedade deve permanecer representada explicitamente como ausente.
- **FR-011**: O relatório deve possuir área própria para `UnauthorizedCommitAlert`, apresentando repository, branch, `commit_hash`, autor, `author_email`, data e execução original quando aplicável.
- **FR-012**: A interface não deve atribuir um alerta original a uma execução posterior que apenas reutilizou a verificação do commit.
- **FR-013**: Para estados `partially_completed` e `failed`, a interface deve apresentar repositories falhos, código/categoria, mensagem segura e data quando disponíveis.
- **FR-014**: As listas de repositories, commits verificados, alertas e falhas devem usar a paginação oferecida pelo serviço existente quando aplicável.
- **FR-015**: A interface deve permitir navegar entre páginas sem perder o contexto do relatório ou recarregar toda a aplicação.
- **FR-016**: Filtros por repository, status, autor, e-mail ou resultado de autoria podem ser oferecidos somente quando já suportados pelos dados existentes; filtros não suportados podem ser omitidos.
- **FR-017**: Em `pending`, a interface deve informar que a execução ainda não iniciou.
- **FR-018**: Em `running`, a interface deve mostrar os dados disponíveis e oferecer acesso ao acompanhamento em tempo real existente, sem criar um segundo fluxo de acompanhamento.
- **FR-019**: Em `completed`, a interface deve apresentar o relatório completo disponível.
- **FR-020**: Em `partially_completed`, a interface deve apresentar o relatório disponível e destacar as falhas por repository.
- **FR-021**: Em `failed`, a interface deve apresentar os dados persistidos e os motivos de falha sem presumir que existam commits processados.
- **FR-022**: Ao atingir estado terminal, os dados persistidos do relatório devem prevalecer sobre informações transitórias de acompanhamento.
- **FR-023**: O operador deve poder voltar à listagem anterior e abrir o relatório por uma navegação identificável.
- **FR-024**: Ausência de commits, alertas ou falhas deve ser apresentada como resultado vazio válido, não como erro.
- **FR-025**: A interface deve preservar os contratos, estados, contadores, ownership de alertas e regras de mineração existentes.
- **FR-026**: A apresentação de falhas e erros deve ocultar tokens, credenciais, secrets e informações sensíveis.
- **FR-027**: Testes e dados de demonstração devem utilizar exclusivamente valores sintéticos e não sensíveis.
- **FR-028**: A funcionalidade não deve alterar baseline, checkpoints, idempotência, scheduling, credenciais, execução manual ou contratos de acompanhamento existentes.

### Key Entities

- **ExecutionReportView**: visão consolidada de uma execução, com identificação, estado, horários, origem, contadores e listas relacionadas.
- **RepositoryReportItem**: resultado de um repository na execução, incluindo branch, status, quantidades e falha segura.
- **CommitVerificationItem**: commit verificado na execução e seus metadados de autoria, incluindo `author_email` anulável.
- **UnauthorizedCommitAlertItem**: alerta de autoria não permitida vinculado exclusivamente à execução original de detecção.
- **RepositoryFailureItem**: falha associada a um repository, com categoria/código, mensagem segura e data quando disponível.
- **PaginatedCollection**: lista de itens com informações de página necessárias para navegação.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Em uma execução existente, o operador consegue abrir o relatório a partir do histórico ou dos detalhes em uma ação de navegação.
- **SC-002**: Todo relatório carregado exibe corretamente os sete contadores canônicos, com os mesmos valores fornecidos pelo backend.
- **SC-003**: Relatórios nos cinco estados canônicos apresentam comportamento e linguagem correspondentes ao estado, sem introduzir estados adicionais.
- **SC-004**: Em 100% dos casos de `author_email` nulo, a ausência é visível e nenhum item é descartado por esse motivo.
- **SC-005**: Repositories concluídos e falhos são distinguíveis em todos os relatórios parcialmente concluídos ou falhos que contenham esses itens.
- **SC-006**: Listas paginadas permitem consultar páginas subsequentes sem reiniciar a tela inteira ou perder o identificador da execução.
- **SC-007**: Uma execução ativa oferece acesso ao acompanhamento existente, e sua finalização faz a tela priorizar os dados persistidos.
- **SC-008**: Nenhuma resposta visual, mensagem de erro, log de teste ou dado sintético da funcionalidade contém segredo, token ou credencial real.

## Assumptions

- Os serviços existentes continuam sendo a fonte oficial dos dados do relatório, estados, contadores e ownership de alertas.
- O identificador da execução é suficiente para localizar o relatório e suas listas relacionadas.
- Paginação, filtros e campos são apresentados somente quando suportados pelos contratos existentes; a funcionalidade não exige novos dados de mineração.
- A autenticação e autorização já existentes para o operador continuam válidas para a consulta do relatório.
- O acompanhamento em tempo real existente permanece responsável por execuções ativas; esta feature apenas oferece navegação para ele.
- Visualizações gráficas avançadas, exportação e alteração do processo de mineração permanecem fora do escopo.
