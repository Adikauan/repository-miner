# Feature Specification: Paginação de Planos de Verificação

**Feature Branch**: `006-paginate-verification-plans`

**Created**: 2026-09-21

**Status**: Draft

**Input**: User description: "Adicionar paginação à listagem de Configurações / Planos de Verificação do Repository Miner, mantendo os registros mais recentes primeiro e sem alterar as regras funcionais existentes."

## Clarifications

### Session 2026-09-21

- Q: Qual formato deve ser usado no contrato paginado da listagem de Planos de Verificação? → A: Reutilizar `offset` e `limit`, com metadados de paginação compatíveis.
- Q: A resposta da listagem deve incluir `total` e `total_pages` explicitamente? → A: Sim; ambos serão obrigatórios juntamente com `items`, `offset` e `limit`.

## User Scenarios & Testing

### User Story 1 - Consultar planos recentes (Priority: P1)

Como operador, quero abrir a tela inicial e consultar os Planos de Verificação mais recentes primeiro, para encontrar rapidamente os planos recém-criados.

**Why this priority**: A listagem inicial é o principal ponto de entrada do produto e precisa continuar útil quando houver muitos planos cadastrados.

**Independent Test**: Com mais planos do que uma página, abrir a tela inicial e confirmar que a primeira página contém os planos mais recentes e que as páginas seguintes avançam para planos mais antigos.

**Acceptance Scenarios**:

1. **Given** existem planos cadastrados em quantidade superior ao limite da página, **When** o operador abre a tela inicial, **Then** a primeira página é carregada e mostra os planos mais recentes.
2. **Given** o operador está na primeira página, **When** avança para a página seguinte, **Then** uma nova consulta apresenta os planos imediatamente mais antigos, sem duplicação ou omissão no conjunto estável.
3. **Given** dois planos possuem a mesma data temporal, **When** são listados, **Then** sua ordem permanece determinística usando o identificador estável.

---

### User Story 2 - Navegar e lidar com estados da listagem (Priority: P1)

Como operador, quero navegar entre páginas e receber feedback durante carregamentos, erros e listas vazias, para entender sempre o estado da consulta.

**Why this priority**: Paginação só é utilizável quando a navegação e os estados de interface são claros e seguros.

**Independent Test**: Simular respostas de sucesso, carregamento, erro e lista vazia e verificar os controles e mensagens correspondentes.

**Acceptance Scenarios**:

1. **Given** há mais de uma página, **When** o operador usa os controles de página, **Then** pode avançar, voltar e selecionar páginas disponíveis quando suportado pelo controle visual.
2. **Given** uma consulta está em andamento, **When** o operador troca de página, **Then** a interface exibe carregamento sem recarregar a aplicação inteira.
3. **Given** a consulta falha, **When** a resposta de erro é recebida, **Then** uma mensagem segura é exibida e a ação de tentar novamente permanece disponível conforme o padrão atual.
4. **Given** não existem planos, **When** a primeira página é carregada, **Then** o estado vazio existente é exibido, a ação de criar plano permanece disponível e nenhum controle de paginação desnecessário é mostrado.

---

### User Story 3 - Criar plano e retornar à primeira página (Priority: P2)

Como operador, quero que um plano recém-criado apareça na primeira página após a atualização, para confirmar o resultado sem procurar em páginas antigas.

**Why this priority**: A criação deve permanecer consistente com a ordenação oficial e não pode depender de inserção manual no frontend.

**Independent Test**: Criar um plano enquanto outra página está aberta, atualizar a listagem e confirmar o retorno à primeira página com o novo plano no topo conforme a ordenação.

**Acceptance Scenarios**:

1. **Given** o operador concluiu a criação de um plano, **When** a listagem é atualizada, **Then** a consulta retorna à primeira página quando necessário e o novo plano aparece conforme a ordem do backend.
2. **Given** a quantidade de planos diminuiu e a página atual deixou de existir, **When** a listagem é consultada, **Then** a interface retorna para uma página válida sem permanecer vazia por causa de um índice inválido.

### Edge Cases

- A primeira página tem menos itens que o limite porque o total não é múltiplo do tamanho da página.
- Um plano é removido enquanto o operador está em uma página posterior; a consulta seguinte deve ajustar a página para uma posição válida.
- Dois ou mais planos têm a mesma data temporal; o desempate pelo identificador estável evita mudanças de ordem entre consultas.
- A resposta paginada contém zero itens enquanto ainda há uma ação de criação disponível.
- Falhas de rede durante a troca de página não devem apagar silenciosamente os dados já exibidos.

## Requirements

### Functional Requirements

- **FR-001**: O sistema MUST permitir consultar Planos de Verificação/MiningConfigurations usando os parâmetros `offset` e `limit` do contrato paginado canônico já utilizado pelas execuções.
- **FR-002**: O contrato paginado MUST retornar `items`, `offset`, `limit`, `total` e `total_pages`, permitindo identificar exatamente a página atual, o total de registros e o total de páginas.
- **FR-003**: O backend MUST aplicar filtros existentes, quando houver, antes de ordenar e paginar os planos.
- **FR-004**: O backend MUST ordenar os planos do mais recente para o mais antigo antes de dividir o resultado em páginas, usando o campo temporal canônico de MiningConfiguration.
- **FR-005**: Quando os valores temporais forem iguais, o sistema MUST usar o identificador estável em ordem decrescente para produzir uma ordem determinística.
- **FR-006**: Se não existir campo temporal canônico adequado no modelo atual, a solução MUST usar o identificador estável disponível sem criar automaticamente um novo campo exclusivamente para esta feature.
- **FR-007**: A tela inicial MUST abrir na primeira página e consumir somente os itens da página solicitada, sem carregar todos os planos para paginar localmente.
- **FR-008**: O frontend MUST consumir a ordem e os metadados fornecidos pelo backend e MUST NOT reordenar globalmente itens recebidos de páginas diferentes.
- **FR-009**: A listagem MUST oferecer controles para visualizar a página atual, avançar e voltar entre páginas válidas e selecionar páginas quando o padrão visual existente permitir.
- **FR-010**: A troca de página MUST realizar nova consulta, exibir estado de carregamento e preservar a aplicação sem recarregamento completo.
- **FR-011**: Erros de consulta MUST ser apresentados de forma segura e acionável, sem expor credenciais ou informações sensíveis.
- **FR-012**: O estado vazio MUST manter a ação de criar novo plano e MUST omitir controles de paginação quando não houver páginas navegáveis.
- **FR-013**: Após criar um plano, a listagem MUST ser atualizada e retornar à primeira página quando necessário; o novo item MUST aparecer pela ordenação retornada pelo backend, sem inserção manual local.
- **FR-014**: Se a página atual deixar de existir após remoção ou alteração do conjunto de dados, a interface MUST retornar para uma página válida.
- **FR-015**: A paginação MUST preservar todas as informações e ações atualmente exibidas nos itens, incluindo identificação, enabled, GitLab, periodicidade, última execução e ações disponíveis.
- **FR-016**: A alteração MUST limitar-se à consulta e apresentação paginada de Planos de Verificação e MUST NOT alterar criação, edição, execução manual, scheduler, baseline, checkpoints, relatórios, alertas ou regras de mineração.
- **FR-017**: O sistema MUST manter proteção de credenciais, não exibindo tokens ou segredos em respostas, mensagens, URLs, logs ou fixtures.

### Key Entities

- **Plano de Verificação / MiningConfiguration**: configuração persistida que identifica um plano, seu estado, conexão GitLab, periodicidade, escopo e resumo da última execução.
- **Página de planos**: conjunto ordenado de itens retornado para uma consulta, acompanhado de página atual, tamanho da página, total e, quando disponível, total de páginas.

## Success Criteria

### Measurable Outcomes

- **SC-001**: Em uma consulta com mais de uma página, 100% das primeiras páginas exibem os planos mais recentes segundo a ordenação temporal definida, sem exigir navegação até a última página.
- **SC-002**: Em um conjunto estável de planos paginado em múltiplas páginas, nenhuma consulta de páginas consecutivas produz duplicação ou omissão de registros.
- **SC-003**: Após a criação de um plano, uma nova consulta à listagem apresenta o plano na primeira página em até uma atualização normal da tela.
- **SC-004**: Em testes de interface, 100% das trocas de página exibem estado de carregamento, tratam erro de consulta e mantêm a ação de criação disponível no estado vazio.
- **SC-005**: A listagem mantém todos os campos e ações existentes dos cards/linhas atuais em todas as páginas, sem exposição de credenciais.
- **SC-006**: Nenhuma alteração nos resultados ou regras de execução, scheduler, mineração, baseline, checkpoints, relatórios e alertas é observada nos testes de regressão relacionados.

## Assumptions

- O endpoint atual de configurações será estendido com `offset`/`limit` e os metadados `total`/`total_pages`, mantendo o formato compatível com o padrão existente sem criar um segundo contrato incompatível.
- O modelo atual possui um campo temporal canônico ou uma semântica temporal equivalente; a confirmação do campo concreto será feita no planejamento técnico.
- O tamanho da página terá um valor padrão definido pelo contrato existente; alteração de page size permanece fora do escopo se não houver controle atual.
- Não serão criados filtros novos; filtros existentes, se presentes, continuarão sendo aplicados antes da ordenação e paginação.
- O frontend continuará usando os componentes visuais e as mensagens de estado já adotados pelo Repository Miner.
- A conectividade e o backend estarão disponíveis durante as consultas normais; falhas serão tratadas pela interface conforme os cenários definidos.
