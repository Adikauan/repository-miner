# Feature Specification: Padronização da Paginação Cronológica

**Feature Branch**: `[005-standardize-pagination]`

**Created**: 2026-09-21

**Status**: Draft

**Input**: User description: "Padronizar as listagens cronológicas paginadas do Repository Miner para apresentar os registros mais recentes primeiro, com ordenação global, determinística e consistente entre páginas."

## Clarifications

### Session 2026-09-21

- Q: Como posicionar execuções `pending` sem `started_at`? → A: Usar a semântica temporal persistida já existente; se não houver outro campo aplicável, manter o grupo com `started_at` nulo em ordem determinística pelo identificador estável, sem criar `created_at`.
- Q: Planos de Verificação e CommitVerifications devem receber novos endpoints ou paginação? → A: Não. A feature cobre somente listagens que já são paginadas ou já possuem contrato de paginação; a lista de planos permanece não paginada e CommitVerifications só segue contratos de relatórios paginados existentes.
- Q: Como tratar alteração de tamanho de página? → A: Aplicar somente nas telas que já possuem esse controle, sem criar um novo controle.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Consultar registros mais recentes primeiro (Priority: P1)

Como operador, quero abrir qualquer listagem cronológica paginada e encontrar os registros mais recentes na primeira página, para acompanhar rapidamente a atividade atual sem navegar até o fim do histórico.

**Why this priority**: Esse é o comportamento central da feature e corrige diretamente a dificuldade de localizar os dados mais novos.

**Independent Test**: Preparar uma listagem com registros distribuídos em múltiplas datas e páginas, abri-la na página inicial e confirmar que ela contém o segmento mais recente do conjunto, em ordem decrescente.

**Acceptance Scenarios**:

1. **Given** uma listagem cronológica com registros suficientes para múltiplas páginas, **When** o usuário abre a listagem, **Then** a primeira página exibe os registros mais recentes em ordem decrescente da data cronologicamente relevante.
2. **Given** uma listagem na primeira página, **When** o usuário avança para páginas seguintes, **Then** cada página apresenta registros progressivamente mais antigos que os das páginas anteriores.
3. **Given** uma listagem em uma página posterior, **When** o usuário retorna para uma página anterior, **Then** visualiza registros progressivamente mais recentes.

---

### User Story 2 - Obter resultados estáveis entre páginas (Priority: P1)

Como operador, quero que registros com a mesma data mantenham uma ordem estável, para não encontrar duplicações, omissões ou mudanças arbitrárias ao navegar por um conjunto de dados que não foi alterado.

**Why this priority**: A ordenação cronológica só é confiável se a paginação for determinística em todos os limites de página.

**Independent Test**: Criar registros com datas idênticas, consultar todas as páginas repetidamente sem alterar os dados e verificar que a sequência completa é idêntica, sem registros duplicados ou ausentes.

**Acceptance Scenarios**:

1. **Given** dois ou mais registros com a mesma data principal, **When** a listagem é consultada repetidamente sem alteração dos dados, **Then** esses registros aparecem sempre na mesma ordem determinada por um identificador estável.
2. **Given** um conjunto estável distribuído em múltiplas páginas, **When** todas as páginas são percorridas, **Then** cada registro elegível aparece exatamente uma vez.
3. **Given** uma consulta paginada, **When** os resultados são formados, **Then** a ordenação global é definida antes do recorte de cada página.

---

### User Story 3 - Consultar históricos filtrados e atualizados (Priority: P2)

Como operador, quero que filtros, atualização e alteração do tamanho da página preservem a convenção de mais recentes primeiro, para que a listagem permaneça previsível em todas as formas de consulta.

**Why this priority**: Filtros e parâmetros de paginação não podem produzir uma interpretação cronológica contraditória.

**Independent Test**: Aplicar um filtro a um conjunto com várias páginas, alterar o tamanho da página e atualizar a consulta após criar um registro; em cada caso, confirmar que o resultado elegível é ordenado antes de ser paginado e começa pelos registros mais recentes.

**Acceptance Scenarios**:

1. **Given** uma listagem com filtros ativos, **When** os dados são consultados, **Then** somente os registros elegíveis são considerados, ordenados do mais recente para o mais antigo e depois paginados.
2. **Given** uma listagem que permite alterar o tamanho da página, **When** o usuário escolhe outro tamanho, **Then** a listagem é consultada novamente na primeira página ou conforme o comportamento padrão existente e mantém os registros mais recentes no início.
3. **Given** um novo registro cuja data o torna o mais recente, **When** o usuário realiza uma nova consulta à primeira página, **Then** o novo registro aparece no início lógico da listagem.

---

### User Story 4 - Acompanhar execuções recentes de um plano (Priority: P2)

Como operador de um Plano de Verificação, quero que a aba Execuções abra na primeira página e mostre as execuções mais recentes, para acessar rapidamente o processamento atual ou recém-concluído.

**Why this priority**: O histórico de execuções é uma listagem operacional crítica e deve materializar explicitamente a convenção desta feature.

**Independent Test**: Abrir a aba Execuções de um plano com histórico de múltiplas páginas e confirmar que somente as execuções desse plano são exibidas, começando pelas de início ou criação mais recente.

**Acceptance Scenarios**:

1. **Given** um plano com execuções distribuídas em várias páginas, **When** o usuário abre a aba Execuções, **Then** a primeira página exibe as execuções mais recentes desse plano.
2. **Given** o histórico de execuções de um plano, **When** o usuário avança nas páginas, **Then** visualiza execuções progressivamente mais antigas sem mistura de execuções de outros planos.
3. **Given** uma execução recém-criada, **When** o usuário atualiza ou consulta novamente a primeira página, **Then** ela aparece na posição correspondente à sua data, normalmente no início da lista.

### Edge Cases

- Uma listagem vazia mantém os metadados de paginação existentes e não apresenta erro de ordenação.
- Uma listagem com apenas uma página permanece em ordem decrescente e não oferece navegação inválida.
- Registros com a mesma data, inclusive no limite entre páginas, são desempatados explicitamente por um identificador estável e não trocam de posição em consultas equivalentes.
- Execuções `pending` sem `started_at` não recebem um novo campo temporal; permanecem no grupo de data nula e são desempatadas deterministicamente pelo identificador estável.
- A listagem de Planos de Verificação, por não possuir paginação atualmente, não recebe paginação nem ordenação nova por causa desta feature.
- CommitVerifications sem endpoint paginado próprio não recebem endpoint novo; quando aparecem indiretamente em relatório paginado, seguem o contrato desse relatório.
- Registros cuja data principal seja opcional seguem o comportamento canônico já definido pelo domínio; a feature não inventa uma data substituta nem altera a semântica do recurso.
- Uma página solicitada além do intervalo disponível preserva o comportamento existente da listagem.
- Novos registros inseridos entre duas consultas podem deslocar os limites das páginas; a garantia de ausência de duplicação ou omissão aplica-se a um conjunto de dados estável.
- Listagens de relatório que não possuem natureza cronológica preservam sua ordenação de domínio atual.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Toda listagem cronológica paginada MUST apresentar os registros em ordem decrescente de sua data cronologicamente relevante.
- **FR-002**: A primeira página de cada listagem cronológica paginada MUST representar os registros mais recentes disponíveis no momento da consulta.
- **FR-003**: O sistema MUST definir a ordem do conjunto completo elegível antes de dividi-lo em páginas.
- **FR-004**: Cada listagem abrangida MUST utilizar o campo temporal canônico já existente que melhor representa sua cronologia, sem criar um novo campo exclusivamente para esta feature.
- **FR-005**: O escopo obrigatório MUST limitar-se às listagens que já são paginadas ou que já possuem contrato de paginação definido; a listagem de Planos de Verificação, atualmente não paginada, MUST permanecer fora da alteração de paginação.
- **FR-006**: Execuções MUST usar `started_at` quando disponível; para estado `pending` com `started_at` nulo, MUST usar outro campo temporal persistido semanticamente aplicável se existir e, caso contrário, MUST manter o grupo nulo em ordem determinística pelo identificador estável, sem criar `created_at` para esta feature.
- **FR-007**: UnauthorizedCommitAlerts MUST usar sua data canônica de criação ou detecção.
- **FR-008**: CommitVerifications MUST permanecer fora do escopo obrigatório quando não houver endpoint paginado específico; quando consultados indiretamente por relatório paginado existente, MUST seguir o contrato de ordenação desse relatório.
- **FR-009**: Quando dois registros tiverem a mesma data principal, a listagem MUST aplicar um identificador estável como critério secundário de desempate.
- **FR-010**: O critério secundário MUST ordenar primeiro o registro mais novo quando essa relação puder ser determinada pelo identificador existente; caso contrário, MUST ao menos garantir uma sequência estável e documentada.
- **FR-011**: Consultas equivalentes sobre um conjunto de dados inalterado MUST retornar os registros na mesma sequência.
- **FR-012**: Ao avançar uma página, o usuário MUST receber registros cronologicamente anteriores aos exibidos nas páginas precedentes.
- **FR-013**: Ao retornar uma página, o usuário MUST receber registros cronologicamente posteriores aos exibidos nas páginas seguintes.
- **FR-014**: Após a criação de um registro, uma nova consulta à primeira página MUST posicioná-lo conforme a ordenação cronológica definida.
- **FR-015**: Quando houver filtros, o sistema MUST primeiro determinar os registros elegíveis, depois ordená-los e somente então aplicar a paginação.
- **FR-016**: Endpoints que representem a mesma entidade ou histórico MUST adotar critérios de ordenação cronológica compatíveis.
- **FR-017**: A apresentação MUST preservar exatamente a ordem dos registros recebida da fonte oficial, sem inverter itens da página nem tentar reconstruir uma ordem global a partir de páginas parciais.
- **FR-018**: Toda listagem paginada MUST abrir inicialmente na primeira página, salvo quando um contexto existente e explícito restaurar a posição anterior do usuário.
- **FR-019**: Somente telas que já oferecem controle de tamanho de página MUST realizar nova consulta mantendo a mesma ordenação ao alterar esse tamanho; a feature MUST NOT criar novo controle de tamanho de página.
- **FR-020**: A aba Execuções de um Plano de Verificação MUST exibir somente as execuções daquele plano, com as mais recentes na primeira página.
- **FR-021**: Listas já paginadas e cronológicas dentro de relatórios MUST seguir a mesma convenção, desde que ela não contradiga a semântica própria do recurso; a feature MUST NOT criar novos endpoints de relatório ou de CommitVerification.
- **FR-022**: A alteração MUST preservar, sempre que possível, os campos e metadados atuais de paginação, incluindo página, tamanho da página, total e filtros.
- **FR-023**: A alteração MUST preservar os contratos de relatório e a navegação existente, exceto pela ordem cronológica corrigida.
- **FR-024**: O sistema MUST preservar ownership de UnauthorizedCommitAlert, contadores, resultados da mineração, checkpoints, CommitVerification, execução manual e scheduling.
- **FR-025**: Em um conjunto de dados estável, percorrer todas as páginas MUST retornar todos os registros elegíveis uma única vez, sem duplicação ou omissão.

### Key Entities

- **Registro cronológico**: Item de uma listagem que possui uma data canônica capaz de determinar sua posição relativa no histórico e um identificador estável para desempate.
- **Página**: Segmento ordenado do conjunto total elegível, identificado pelos metadados de paginação já existentes.
- **Plano de Verificação**: Configuração de mineração associada a um histórico próprio de execuções; sua listagem atual não é uma listagem paginada abrangida por esta feature.
- **Execução**: Ocorrência manual ou agendada de um Plano de Verificação, ordenada por início ou criação.
- **UnauthorizedCommitAlert**: Alerta associado a uma execução e a um commit, ordenado pela data canônica de criação ou detecção quando listado cronologicamente.
- **CommitVerification**: Registro de verificação de commit, ordenado pela data canônica de verificação ou persistência quando listado cronologicamente.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Em 100% das listagens cronológicas já paginadas ou contratualmente paginadas cobertas, a primeira página contém o segmento mais recente do conjunto elegível no momento da consulta.
- **SC-002**: Em conjuntos estáveis com pelo menos três páginas, 100% dos registros aparecem exatamente uma vez ao percorrer todas as páginas.
- **SC-003**: Em 100% das consultas repetidas sobre dados inalterados com datas empatadas, a sequência retornada permanece idêntica.
- **SC-004**: Em 100% dos cenários com filtros, todos os itens exibidos atendem ao filtro e permanecem ordenados do mais recente para o mais antigo antes da divisão em páginas.
- **SC-005**: Após a criação de um registro mais recente, uma nova consulta à primeira página o apresenta na primeira posição em 100% dos cenários aplicáveis.
- **SC-006**: A aba Execuções apresenta as execuções do plano atual do início mais recente para o mais antigo em 100% das páginas consultadas.
- **SC-007**: Alterações de tamanho de página preservam a ordem cronológica em 100% das telas que já oferecem esse controle, sem exigir novo controle em outras telas.
- **SC-008**: Nenhum contrato funcional de mineração, resultado, contador ou estado operacional sofre alteração observável além da ordem das listagens abrangidas.

## Assumptions

- A feature abrange somente listagens existentes que são paginadas ou já possuem contrato de paginação e que também são cronológicas; listagens ordenadas por relevância, nome, severidade ou outra regra de domínio ficam fora do escopo.
- Planos de Verificação permanecem não paginados e não recebem paginação apenas por causa desta feature.
- CommitVerifications sem endpoint paginado próprio permanecem fora do escopo obrigatório; sua apresentação indireta segue o relatório paginado existente.
- Cada recurso abrangido já possui ao menos um campo temporal canônico e um identificador estável adequados para ordenação determinística, com a exceção explícita de execuções `pending` sem campo temporal aplicável, que usam o identificador para desempate dentro do grupo nulo.
- A ausência de mutações no conjunto entre consultas é necessária para validar rigorosamente ausência de duplicação e omissão em paginação baseada em páginas.
- O comportamento existente para páginas inválidas, listas vazias e restauração explícita da posição do usuário será preservado.
- A atualização automática de uma tela já aberta não faz parte desta feature; novos registros aparecem após nova consulta ou atualização iniciada pelo fluxo existente.
- Nenhuma conexão com serviços externos é necessária para validar a ordenação; dados controlados são suficientes.
