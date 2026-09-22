# Feature Specification: Navegação por Planos de Verificação

**Feature Branch**: `004-plan-navigation`

**Created**: 2026-09-21

**Status**: Draft

**Input**: User description: reorganizar a navegação e a composição do frontend em torno de Planos de Verificação, preservando as regras de negócio e funcionalidades existentes.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Consultar planos na página inicial (Priority: P1)

Ao entrar no sistema, o operador encontra imediatamente os Planos de Verificação cadastrados, identifica sua situação operacional e escolhe entre criar ou abrir um plano, sem passar por dashboard ou áreas separadas de configuração e escopo.

**Why this priority**: A listagem estabelece o novo modelo mental e é a porta de entrada para todas as demais jornadas.

**Independent Test**: Acessar a entrada principal com e sem planos cadastrados e verificar resumos, estado vazio e ações de criação e visualização.

**Acceptance Scenarios**:

1. **Given** que existem planos, **When** o operador abre o sistema, **Then** a primeira tela lista os planos com nome, status e as informações operacionais disponíveis.
2. **Given** que não existem planos, **When** o operador abre o sistema, **Then** a tela apresenta estado vazio acionável e mantém visível "Novo plano".
3. **Given** um plano listado, **When** o operador escolhe "Visualizar configuração", **Then** o sistema abre os detalhes desse plano na aba Configuração.
4. **Given** a navegação principal, **When** ela é exibida, **Then** não existem entradas independentes para Configurações ou Repositories/escopo.

---

### User Story 2 - Criar um plano em um único fluxo (Priority: P1)

O operador cria um Plano de Verificação em um modal, informando identificação, conexão GitLab, escopo, branch, usuários permitidos, agendamento e status como uma única operação percebida.

**Why this priority**: A criação integrada elimina a fragmentação entre plano e configuração e reduz navegações desnecessárias.

**Independent Test**: Abrir o modal, preencher dados sintéticos, validar a conexão, selecionar escopo e branch, configurar usuários e agendamento e confirmar; verificar o novo plano na lista.

**Acceptance Scenarios**:

1. **Given** a listagem, **When** o operador aciona "Novo plano", **Then** um modal abre sem navegar para outra página e reúne todos os grupos de informação necessários.
2. **Given** uma conexão não validada, **When** o operador tenta acessar grupos, repositories ou branches, **Then** essas operações permanecem indisponíveis e a interface explica como liberá-las.
3. **Given** conexão validada e dados válidos, **When** o operador confirma, **Then** todas as informações obrigatórias são persistidas e o plano aparece na lista atualizada.
4. **Given** uma criação em processamento, **When** o operador tenta confirmar novamente, **Then** a segunda submissão é impedida.
5. **Given** falha em uma operação obrigatória, **When** o fluxo termina, **Then** a interface não anuncia sucesso, identifica com segurança a etapa que falhou e preserva dados reutilizáveis.
6. **Given** uma credencial persistida, **When** o plano volta a ser exibido, **Then** a credencial não é reapresentada em texto aberto.

---

### User Story 3 - Consultar e editar um plano (Priority: P1)

O operador acessa o contexto completo de um plano em uma página com exatamente duas abas principais, Configuração e Execuções, e consulta ou altera as informações suportadas.

**Why this priority**: Centralizar a administração no contexto do plano é o principal ganho de clareza da reorganização.

**Independent Test**: Abrir um plano, verificar as duas abas, editar cada grupo suportado e confirmar que os valores persistidos são apresentados.

**Acceptance Scenarios**:

1. **Given** um plano existente, **When** o operador abre seus detalhes, **Then** a página apresenta somente as abas principais Configuração e Execuções.
2. **Given** a aba Configuração, **When** os dados carregam, **Then** são apresentados nome, GitLab, estado da conexão, escopo, repositories, branch, usuários, agendamento e status quando aplicáveis.
3. **Given** uma alteração válida, **When** o operador a salva, **Then** a operação canônica correspondente é respeitada e a tela reflete o valor persistido.
4. **Given** uma alteração de conexão que invalida a verificação anterior, **When** ela é salva, **Then** operações dependentes ficam bloqueadas até nova validação.
5. **Given** falha de consulta ou edição, **When** ela ocorre, **Then** a interface apresenta mensagem segura e acionável, sem credenciais.

---

### User Story 4 - Executar um plano e consultar seu histórico (Priority: P1)

O operador inicia uma verificação manual para o plano atual, consulta exclusivamente seu histórico e abre o acompanhamento ou relatório de cada execução.

**Why this priority**: A operação e os resultados precisam permanecer ligados ao plano que lhes deu origem.

**Independent Test**: Iniciar execução manual, navegar pelo histórico paginado do plano e acessar uma execução ativa e outra terminal.

**Acceptance Scenarios**:

1. **Given** um plano persistido, inclusive desabilitado para agendamento, **When** o operador aciona "Executar agora" sem outro impedimento, **Then** a execução manual inicia e seu identificador permite acessar o acompanhamento existente.
2. **Given** execução concorrente ou credencial comprometida, **When** o operador tenta executar, **Then** o início é rejeitado e um motivo seguro é apresentado.
3. **Given** a aba Execuções, **When** o histórico carrega, **Then** somente execuções do plano atual são exibidas.
4. **Given** uma execução `running`, **When** o operador escolhe "Ver detalhes", **Then** é aberto o acompanhamento existente.
5. **Given** uma execução terminal, **When** o operador escolhe "Ver detalhes", **Then** é aberto o relatório existente.
6. **Given** histórico paginado, **When** o operador muda de página, **Then** a página solicitada carrega sem buscar todo o histórico nem perder o contexto do plano.

---

### User Story 5 - Manter caminhos antigos coerentes (Priority: P2)

O operador que usa uma URL antiga relevante chega à nova experiência correspondente, sem encontrar duas interfaces concorrentes para a mesma operação.

**Why this priority**: A compatibilidade evita becos sem saída durante a transição, embora seja secundária ao novo fluxo principal.

**Independent Test**: Abrir rotas antigas conhecidas e confirmar remoção quando dispensáveis ou redirecionamento quando houver correspondência inequívoca.

**Acceptance Scenarios**:

1. **Given** uma rota antiga que identifica uma configuração, **When** ela é acessada, **Then** o operador é direcionado ao contexto equivalente do plano.
2. **Given** uma rota antiga sem correspondência útil, **When** os caminhos são verificados, **Then** a rota e seus links não permanecem como interface redundante.

### Edge Cases

- Branch, periodicidade ou última execução ausentes são indicados como indisponíveis sem impedir o uso do plano.
- Um plano desabilitado para agendamento ainda permite execução manual quando nenhuma outra regra a impede.
- Uma conexão validada pode tornar-se inválida após alteração da URL ou credencial; suas dependências voltam ao estado bloqueado.
- Consultas de grupos, subgrupos, repositories ou branches podem resultar em lista vazia ou falha parcial; o modal distingue vazio de erro.
- Uma criação composta pode persistir somente parte dos dados; o resultado é falha parcial, nunca sucesso completo, e indica o que exige correção.
- Ao fechar o modal com dados não persistidos, o operador confirma antes de descartá-los.
- Uma execução pode mudar de `pending` ou `running` para estado terminal durante a navegação; o relatório persistido passa a prevalecer.
- O histórico pode estar vazio, ter uma página ou perder itens da página atual após atualização.
- Nomes longos, URLs extensas, muitos planos e telas estreitas não tornam ações essenciais inacessíveis.
- Falhas externas podem conter informações sensíveis; somente mensagens sanitizadas chegam à interface.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: A página inicial MUST ser a listagem de Planos de Verificação, sem dashboard inicial separado.
- **FR-002**: "Plano de Verificação" MUST ser a denominação apresentada para a configuração de mineração existente, sem criar um segundo modelo funcional.
- **FR-003**: Cada plano MUST mostrar nome, status e, quando disponíveis, GitLab, branch principal, periodicidade, data e estado da última execução.
- **FR-004**: A listagem MUST tratar carregamento, sucesso, erro e vazio e manter "Novo plano" claramente visível.
- **FR-005**: A criação MUST ocorrer em modal sobre a listagem e apresentar plano e configuração como uma única operação.
- **FR-006**: O modal MUST reunir identificação, conexão GitLab, escopo, branch, usuários permitidos, agendamento e status.
- **FR-007**: A conexão MUST aceitar URL e nova credencial e oferecer validação explícita.
- **FR-008**: Credenciais persistidas MUST NOT ser reapresentadas, preenchidas novamente, registradas, incluídas em URLs ou expostas em mensagens.
- **FR-009**: Grupos, subgrupos, repositories e branches MUST permanecer indisponíveis até a conexão atual ser validada.
- **FR-010**: Após validação, o operador MUST poder carregar e selecionar grupos, subgrupos, repositories e a branch aplicável.
- **FR-011**: O operador MUST poder informar e revisar e-mails permitidos preservando as regras existentes de normalização e comparação.
- **FR-012**: O operador MUST poder configurar recorrência diária, semanal ou mensal, seus parâmetros e horário conforme as capacidades existentes.
- **FR-013**: O operador MUST poder criar o plano habilitado ou desabilitado.
- **FR-014**: O modal MUST validar campos, contextualizar erros, permitir fechamento explícito e impedir submissão duplicada durante o processamento; ao fechar com alterações não persistidas, MUST solicitar confirmação antes do descarte.
- **FR-015**: A confirmação MUST usar operações canônicas existentes e MUST NOT duplicar regras de domínio na interface.
- **FR-016**: Em uma criação composta, a interface MUST representar processamento, sucesso, erro e falha parcial e anunciar sucesso apenas após todas as operações obrigatórias.
- **FR-017**: Após sucesso, o modal MUST fechar e a lista MUST exibir o plano criado sem recarregamento manual da aplicação.
- **FR-018**: A navegação principal MUST privilegiar planos e MUST NOT conter entradas independentes de Configurações ou Repositories/escopo.
- **FR-019**: Cada plano MUST oferecer uma ação identificável para visualizar sua configuração.
- **FR-020**: A página de detalhes MUST conter exatamente duas abas principais: Configuração e Execuções.
- **FR-021**: A aba Configuração MUST apresentar e permitir editar, quando aplicáveis, nome, URL GitLab, estado de conexão, escopo, repositories, branch, usuários permitidos, agendamento e status, usando as operações dedicadas correspondentes.
- **FR-022**: Alteração de conexão que invalide verificação anterior MUST bloquear operações dependentes até nova validação.
- **FR-023**: A página do plano MUST oferecer "Executar agora" usando a configuração persistida atual.
- **FR-024**: A execução manual MUST funcionar para plano desabilitado apenas para agendamento e respeitar rejeição de concorrência e credencial comprometida.
- **FR-025**: Após iniciar uma execução, a interface MUST usar seu identificador para permitir acesso ao acompanhamento existente.
- **FR-026**: A aba Execuções MUST mostrar exclusivamente o histórico do plano atual.
- **FR-027**: Cada execução MUST mostrar, quando disponíveis, identificador, origem manual/agendada, início, término, estado, repositories processados, commits encontrados, commits verificados, commits permitidos e commits não autorizados.
- **FR-028**: A interface MUST usar exclusivamente `pending`, `running`, `completed`, `partially_completed` e `failed`.
- **FR-029**: O histórico MUST tratar carregamento, vazio, erro e paginação sem carregar desnecessariamente todos os registros.
- **FR-030**: Cada execução MUST oferecer "Ver detalhes"; quando somente um ícone for usado, ele MUST possuir nome acessível e explicação perceptível.
- **FR-031**: Detalhes MUST abrir o acompanhamento existente para execuções ativas e o relatório existente para terminais, sem mecanismos paralelos.
- **FR-032**: O relatório reutilizado MUST manter resumo, sete contadores canônicos, repositories, commits, alertas, falhas e paginação aplicável.
- **FR-033**: O acompanhamento ativo MUST reutilizar snapshot e atualização em tempo real existentes.
- **FR-034**: Telas redundantes MUST ser removidas; URLs antigas relevantes MUST redirecionar à nova experiência e links internos MUST NOT apontar para telas removidas.
- **FR-035**: Listagem, modal e detalhes MUST manter conteúdo e ações essenciais utilizáveis nas dimensões atualmente suportadas.
- **FR-036**: Todos os fluxos MUST tratar carregamento, sucesso, erro, vazio, operação em andamento e validações com linguagem consistente.
- **FR-037**: A reorganização MUST preservar configuração, baseline, checkpoints, idempotência, processamento incremental, alertas, agendamento, execução manual, credenciais comprometidas, recuperação divergente, contadores, acompanhamento e relatórios.
- **FR-038**: Testes MUST cobrir listagem, abertura e fechamento do modal, conexão, seleções dependentes, usuários, agendamento, sucesso, erro, falha parcial, submissão duplicada, detalhes, edição, histórico do plano, paginação, relatório, execução manual, acompanhamento, rotas antigas e ausência de credenciais na interface.
- **FR-039**: Testes e demonstrações MUST usar somente dados sintéticos e sem segredos.

### Key Entities

- **Plano de Verificação**: apresenta ao operador a configuração persistida, conexão, escopo, branch, usuários, agendamento e status; não é um novo modelo de domínio.
- **Conexão GitLab**: associa instância, estado de validação e referência segura de credencial ao plano.
- **Escopo de Verificação**: seleção de grupos, subgrupos e repositories dependente de uma conexão validada.
- **Agendamento**: recorrência e horário vinculados ao plano.
- **Execução de Verificação**: ocorrência manual ou agendada pertencente ao plano, com ciclo de vida e contadores canônicos.
- **Relatório de Execução**: resultado persistido com resumo, repositories, commits, alertas e falhas.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Em 100% dos acessos pela entrada principal, a primeira tela funcional é a listagem de planos, sem dashboard intermediário.
- **SC-002**: Pelo menos 90% dos operadores localizam um plano e abrem sua configuração em no máximo duas ações a partir da página inicial.
- **SC-003**: Pelo menos 90% dos operadores iniciam a criação em até 10 segundos e concluem um cenário válido sem sair do modal.
- **SC-004**: Em 100% das criações testadas, sucesso completo somente é apresentado quando todas as informações obrigatórias foram persistidas.
- **SC-005**: Em 100% dos planos abertos, existem exatamente duas abas principais e os dados exibidos pertencem ao plano selecionado.
- **SC-006**: Em históricos de pelo menos três planos, 100% dos itens da aba Execuções pertencem ao plano atual, inclusive após paginação.
- **SC-007**: Em 100% dos estados testados, detalhes levam execução ativa ao acompanhamento existente e execução terminal ao relatório existente.
- **SC-008**: Em 100% dos caminhos revisados, não existem entradas principais separadas de configuração ou escopo nem links para telas removidas.
- **SC-009**: Todos os fluxos principais podem ser concluídos nas menores dimensões atualmente suportadas sem perda de controles essenciais.
- **SC-010**: Nenhuma tela, URL, mensagem, registro de teste ou dado sintético da feature revela token, credencial ou segredo.
- **SC-011**: A regressão confirma que 100% das regras citadas no FR-037 mantêm o comportamento anterior.
- **SC-012**: Pelo menos 90% dos operadores avaliam como clara a relação entre plano, configuração, execuções e relatório.

## Assumptions

- Operador, autenticação e autorização permanecem os mesmos; não há novos perfis de acesso.
- A configuração existente representa adequadamente o plano; a nova nomenclatura é de experiência, não de domínio.
- Os serviços existentes permanecem como fonte oficial para configuração, escopo, usuários, agendamento, execuções, acompanhamento e relatórios.
- Dados de última execução aparecem apenas quando já disponíveis; não se exige novo processamento para o resumo.
- Uma URL antiga é relevante quando identifica inequivocamente plano, execução ou relatório acessível na nova navegação.
- Dashboard analítico, novo design system, novos estados, exportação e alterações na mineração ficam fora do escopo.
- A criação pode exigir várias operações existentes; não se presume atomicidade quando ela não for oferecida.

### Dependencies

- Consulta e persistência existentes de configuração, escopo, branch, usuários e agendamento.
- Validação e descoberta existentes de grupos, subgrupos, repositories e branches.
- Execução manual, histórico paginado, acompanhamento em tempo real e relatório persistido existentes.

### Constitution Alignment

- **Architectural Simplicity**: reorganiza capacidades existentes sem novo modelo, serviço ou mecanismo paralelo.
- **Credential Security and Incident Response**: credenciais não são reapresentadas e credenciais comprometidas continuam bloqueadas.
- **End-to-End Traceability**: execução e relatório permanecem ligados ao plano e aos identificadores canônicos.
- **Incremental Mining**: baseline, checkpoints, idempotência e reuso não são alterados.
- **Integration Isolation and Testability**: capacidades existentes são reutilizadas e testes usam substitutos controlados e dados sintéticos.
- **Failure Isolation and Observability**: falhas parciais e estados canônicos permanecem visíveis sem converter resultado incompleto em sucesso.
- **Data Minimization**: nenhum dado adicional é coletado ou enviado e nenhum novo uso de análise probabilística é introduzido.
- Nenhuma exceção constitucional ou complexidade arquitetural adicional é necessária.
