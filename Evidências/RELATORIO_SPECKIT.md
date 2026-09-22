# Relatório funcional e de utilização do Spec Kit

## 1. Objetivo e escopo

Este relatório consolida as funcionalidades concebidas para o **Repository Miner**, um sistema de monitoramento de branches e verificação de autoria de commits em projetos hospedados no GitLab. A análise foi feita a partir dos artefatos existentes em `specs/`, da constituição do projeto em `.specify/memory/constitution.md`, do workflow e das skills instaladas em `.agents/skills/`.

O repositório contém seis incrementos de produto:

1. `001-gitlab-repository-mining`: núcleo de mineração e monitoramento de autoria;
2. `002-manual-config-operation`: consulta, edição e execução manual de configurações;
3. `003-execution-report-view`: visualização consolidada de relatórios;
4. `004-plan-navigation`: reorganização da experiência em torno de Planos de Verificação;
5. `005-standardize-pagination`: padronização da ordenação cronológica paginada;
6. `006-paginate-verification-plans`: paginação da listagem de Planos de Verificação.

> **Nota de rastreabilidade:** os diretórios e artefatos demonstram quais etapas do Spec Kit produziram resultados, mas não constituem um log completo dos comandos executados. Portanto, o passo a passo abaixo registra o fluxo comprovado pelos arquivos e diferencia evidência direta de inferência baseada na estrutura padrão do Spec Kit.

## 2. Visão geral do produto

O sistema permite configurar um conjunto de projetos ou grupos GitLab, escolher uma branch-alvo, cadastrar autores permitidos e executar verificações periódicas ou manuais. Cada execução procura commits novos, compara o e-mail normalizado do autor com a lista autorizada, registra alertas para autoria não permitida e mantém checkpoints para evitar reprocessamento desnecessário.

A solução foi planejada como um monólito modular, com backend Python/FastAPI, persistência relacional por SQLAlchemy/Alembic, frontend React/TypeScript e comunicação em tempo real por WebSocket. O GitLab é acessado por uma camada de integração isolada e a aplicação trabalha apenas com metadados de commits no MVP, sem clonar repositórios ou ler o conteúdo das alterações.

## 3. Funcionalidades especificadas

### 3.1 Configuração de monitoramento

- Criar, visualizar, editar, habilitar e desabilitar configurações de monitoramento.
- Informar nome, URL da instância GitLab, credencial protegida, escopo, branch-alvo, autores permitidos e agendamento.
- Validar a conexão antes de permitir a persistência de seleções dependentes do GitLab.
- Navegar pela hierarquia de grupos, subgrupos e repositórios acessíveis.
- Selecionar grupos completos, subgrupos ou repositórios individuais.
- Usar `QA` como branch inicial padrão, mantendo-a editável.
- Manter um ou mais e-mails de autores autorizados.
- Suportar recorrências diárias, semanais e mensais, com exibição da próxima execução.

### 3.2 Segurança e ciclo de vida de credenciais

- Tratar tokens como dados de escrita, sem devolvê-los integralmente por API ou interface.
- Armazenar referências de credencial de modo protegido e impedir sua aparição em logs, relatórios, alertas, mensagens e URLs.
- Permitir substituição preventiva de credencial sem alterar o histórico de mineração.
- Marcar credenciais suspeitas como comprometidas, desabilitar configurações relacionadas e interromper novas chamadas ao GitLab.
- Registrar incidentes e preservar rastreabilidade do operador autenticado pelo ambiente hospedeiro.
- Exigir autenticação para emissão de tickets WebSocket, com tickets descartáveis e vinculados ao operador.

### 3.3 Execução manual e agendada

- Iniciar manualmente uma execução válida, inclusive quando o plano estiver desabilitado apenas para agendamento.
- Criar execuções agendadas quando a configuração estiver vencida, sem duplicar ocorrências.
- Limitar a uma execução ativa por configuração e rejeitar concorrência.
- Registrar a origem da execução, manual ou agendada.
- Manter uma fotografia imutável da configuração efetiva usada na execução.
- Reconciliar ocorrências perdidas após indisponibilidade do scheduler, dentro das regras definidas.
- Trabalhar, no MVP, com uma única instância ativa do scheduler.

### 3.4 Mineração incremental de branches

- Na primeira execução, estabelecer um baseline para cada combinação configuração–repositório–branch.
- Nas execuções seguintes, buscar apenas commits posteriores ao checkpoint durável.
- Coletar metadados como hash, autor, e-mail, data, mensagem, repositório e branch.
- Não buscar diffs ou conteúdo dos arquivos no MVP.
- Persistir verificações de commit de forma idempotente e reutilizar verificações já concluídas.
- Avançar o checkpoint somente quando o processamento do repositório for seguro.
- Detectar histórico divergente quando o checkpoint deixa de pertencer à branch e exigir recuperação explícita do baseline.
- Preservar identidades incrementais e checkpoints quando configurações forem editadas.

### 3.5 Verificação de autoria e alertas

- Normalizar e-mails antes da comparação com a lista de autores permitidos.
- Classificar e-mails ausentes, vazios ou não correspondentes como não autorizados.
- Criar alertas com configuração, execução original, repositório, branch, commit e dados seguros do autor.
- Preservar a propriedade do alerta na execução que realizou a verificação original, mesmo quando uma execução posterior reutilizar o resultado.
- Manter contadores canônicos derivados da fonte relacional, evitando divergência entre progresso e relatório.

### 3.6 Isolamento e tratamento de falhas

- Impedir que a falha de um repositório bloqueie os demais.
- Registrar etapa, categoria/código, mensagem segura e data das falhas.
- Traduzir erros do GitLab para uma taxonomia fechada e estável.
- Produzir estados finais coerentes mesmo com falhas parciais.
- Usar apenas os estados `pending`, `running`, `completed`, `partially_completed` e `failed`.
- Não oferecer cancelamento manual de execução no MVP.

### 3.7 Acompanhamento em tempo real

- Exibir início, fim, estado, progresso por repositório, commits e achados.
- Publicar eventos com identificadores estáveis de correlação.
- Usar REST e dados persistidos como fonte de verdade; WebSocket funciona como mecanismo de atualização.
- Permitir recuperação por snapshot após perda da conexão em tempo real.
- Garantir que a desconexão da interface não interrompa nem altere a execução.

### 3.8 Relatórios de execução

- Abrir o relatório a partir do histórico, acompanhamento ou detalhe de uma execução.
- Exibir identificação, configuração, origem, horários e estado final.
- Mostrar sem recalcular os sete contadores canônicos:
  - `repositories_total`;
  - `repositories_completed`;
  - `repositories_failed`;
  - `commits_discovered`;
  - `commits_verified`;
  - `allowed_commits`;
  - `unauthorized_commits`.
- Listar repositórios processados e distinguir visualmente sucesso e falha.
- Listar commits verificados, inclusive representando explicitamente `author_email` ausente.
- Apresentar alertas de commits não autorizados e sua execução original.
- Apresentar falhas por repositório com mensagens sanitizadas.
- Tratar coleções vazias como resultados válidos, e não como erros.
- Priorizar o relatório persistido quando a execução alcançar um estado terminal.
- Reutilizar o fluxo existente de acompanhamento para execuções ativas.

### 3.9 Operação e edição manual de configurações

- Consultar a configuração persistida e editar nome, conexão, escopo, branch, usuários, agenda e estado.
- Reutilizar o agregado e os serviços já existentes, evitando uma segunda regra de domínio no frontend.
- Manter operações dedicadas para alterações sensíveis, em vez de um `PATCH` amplo.
- Invalidar dependências quando URL ou credencial mudar e exigir nova validação da conexão.
- Preservar baseline, checkpoints e histórico nas edições compatíveis.
- Iniciar e acompanhar uma execução manual a partir da própria configuração.

### 3.10 Navegação baseada em Planos de Verificação

- Usar a listagem de planos como página inicial, sem dashboard intermediário.
- Exibir em cada plano nome, estado, GitLab, branch, periodicidade e última execução.
- Criar um plano em um modal único, com validações, seleções dependentes e feedback por etapa.
- Representar sucesso, erro e falha parcial; só anunciar sucesso depois de todas as operações obrigatórias.
- Permitir recuperação de uma criação parcialmente persistida.
- Evitar submissão duplicada e pedir confirmação antes de descartar alterações.
- Exibir exatamente duas abas no detalhe do plano: **Configuração** e **Execuções**.
- Permitir editar a configuração reutilizando o editor canônico.
- Oferecer **Executar agora** e navegar pelo identificador da execução criada.
- Mostrar somente o histórico do plano atual, com paginação e uma página em memória.
- Encaminhar execuções ativas ao acompanhamento e execuções terminais ao relatório.
- Remover telas redundantes e redirecionar rotas antigas relevantes.
- Manter acessibilidade por teclado, nomes acessíveis, estados de carregamento e layout responsivo.

### 3.11 Paginação cronológica padronizada

- Ordenar globalmente os registros elegíveis antes de dividi-los em páginas.
- Exibir os registros mais recentes na primeira página.
- Aplicar filtros antes da ordenação e da paginação.
- Usar o campo temporal canônico já existente para cada recurso.
- Para execuções, usar `started_at`; valores nulos devem ter ordenação determinística sem criar um novo `created_at` para a feature.
- Desempatar datas iguais por identificador estável.
- Garantir ordem repetível, sem duplicação ou omissão em conjuntos de dados estáveis.
- Fazer o frontend preservar exatamente a ordem recebida do backend.
- Manter metadados, filtros, contratos e navegação existentes.
- Limitar a mudança às listas que já são paginadas ou possuem contrato de paginação.
- Manter a lista de planos fora do escopo e não criar novo endpoint específico para `CommitVerification`.

### 3.12 Paginação da listagem de Planos de Verificação

A feature `006` complementa, sem contradizer, a `005`: a `005` padroniza a ordenação das listas que já eram paginadas, enquanto a `006` introduz explicitamente a paginação na listagem de planos.

- Consultar Planos de Verificação/`MiningConfiguration` com os parâmetros canônicos `offset` e `limit`.
- Retornar o envelope `items`, `offset`, `limit`, `total` e `total_pages`.
- Validar `offset >= 0` e `limit` entre 1 e 200.
- Aplicar filtros antes de ordenar e paginar.
- Ordenar os planos mais recentes primeiro antes do recorte da página.
- Usar `MonitoringConfiguration.id DESC` como ordenação determinística, pois o modelo atual não possui campo temporal canônico adequado.
- Não criar um novo campo temporal exclusivamente para a paginação.
- Abrir a tela inicial na primeira página e carregar somente os itens solicitados ao backend.
- Impedir paginação local sobre uma coleção completa ou reconstrução de ordem entre páginas no frontend.
- Permitir avançar, voltar e, quando compatível com o padrão visual, selecionar páginas.
- Fazer uma nova consulta a cada troca de página, com estado de carregamento e sem recarregar toda a aplicação.
- Apresentar erros seguros e acionáveis, sem expor detalhes internos ou credenciais.
- Preservar a ação de criar plano no estado vazio e ocultar controles sem páginas navegáveis.
- Corrigir automaticamente a página atual quando ela deixar de existir após alteração do conjunto de dados.
- Após criar um plano, fechar o modal, retornar à primeira página e recarregar a fonte oficial, sem inserir o novo item manualmente na lista local.
- Preservar todos os dados e ações dos cards: identificação, estado `enabled`, GitLab, periodicidade, última execução e navegação.
- Não alterar criação, edição, execução manual, scheduler, baseline, checkpoints, relatórios, alertas ou regras de mineração.
- Garantir, em conjuntos estáveis, navegação sem duplicação nem omissão de planos.

## 4. Requisitos transversais definidos pela constituição

A constituição do projeto funciona como autoridade superior às specs, planos e tarefas. Seus dez princípios direcionaram as decisões:

1. **Simplicidade arquitetural:** monólito modular e infraestrutura proporcional ao MVP.
2. **Segurança de credenciais e resposta a incidentes:** segredos protegidos e contenção imediata.
3. **Rastreabilidade ponta a ponta:** configuração, execução, commit, alerta e falha correlacionáveis.
4. **Mineração incremental:** checkpoints duráveis e ausência de reprocessamento indevido.
5. **Isolamento de integrações:** acesso ao GitLab atrás de portas/adaptadores.
6. **Achados probabilísticos de IA:** separação entre sinais probabilísticos e fatos determinísticos, caso IA seja adicionada.
7. **Testabilidade sem serviços externos:** doubles e fixtures sintéticas no lugar de dependências reais.
8. **Isolamento de falhas:** erro localizado não derruba todo o processamento.
9. **Privacidade de código e minimização de dados:** somente metadados necessários no MVP.
10. **Observabilidade de execução:** estados, contadores, falhas e eventos coerentes e auditáveis.

## 5. Como as skills do Spec Kit foram utilizadas

O projeto foi inicializado com **Spec Kit 1.0.8**, integração **Codex**, scripts **PowerShell**, numeração sequencial e skills de agente habilitadas. O workflow registrado como **Full SDD Cycle** define a sequência `specify → revisão da spec → plan → revisão do plano → tasks → implement`.

### 5.1 `$speckit-constitution`

**Finalidade:** estabelecer os princípios não negociáveis do projeto e os gates de engenharia.

**Passo a passo observado:**

1. O template constitucional foi transformado em `.specify/memory/constitution.md`.
2. Foram definidos os dez princípios, restrições de engenharia, gates de entrega e regras de governança.
3. Os planos passaram a conter uma seção **Constitution Check**.
4. Decisões como integração metadata-only, credenciais write-only, testes sem GitLab real e isolamento por repositório foram avaliadas contra esses princípios.
5. Revisões pós-design e pós-implementação registraram que não havia exceções constitucionais pendentes.

**Evidência:** constituição preenchida; referências explícitas nos seis planos e nas tarefas de convergência.

### 5.2 `$speckit-specify`

**Finalidade:** converter uma descrição de negócio em uma especificação verificável e independente de tecnologia.

**Passo a passo observado em cada incremento:**

1. Foi criada uma pasta sequencial em `specs/`, com nome curto da feature.
2. A descrição inicial foi registrada no campo **Input** de `spec.md`.
3. O problema foi decomposto em histórias de usuário priorizadas (`P1`, `P2` etc.).
4. Cada história recebeu cenários de aceitação independentes.
5. Edge cases foram documentados.
6. Requisitos funcionais numerados (`FR-###`) foram produzidos.
7. Entidades-chave, premissas e critérios mensuráveis (`SC-###`) foram definidos.
8. A checklist embutida de qualidade foi criada em `checklists/requirements.md`.

**Evidência:** os seis `spec.md` e as seis checklists de requisitos existem; todas as checklists têm 16 itens marcados como aprovados.

### 5.3 `$speckit-clarify`

**Finalidade:** resolver ambiguidades importantes antes do desenho técnico.

**Passo a passo observado:**

1. Pontos ambíguos das specs foram identificados.
2. Perguntas objetivas foram registradas em sessões datadas na seção **Clarifications**.
3. As respostas foram incorporadas às regras e aos limites de escopo.
4. Exemplos de decisões esclarecidas incluem: ausência de cancelamento manual no MVP, estado final com falhas, recorrência mensal, comprometimento de credencial, ordenação de execuções sem `started_at`, exclusão da lista de planos do escopo da feature `005` e posterior definição explícita da paginação de planos na feature `006`.

**Evidência:** sessões de esclarecimento aparecem diretamente nas specs `001`, `005` e `006`. Nas demais, não há seção equivalente; portanto, não se deve afirmar que a skill foi executada nelas apenas pela existência da spec.

### 5.4 `$speckit-checklist`

**Finalidade:** gerar checklists temáticas para revisar a qualidade dos requisitos, não o progresso da implementação.

**Passo a passo observado:**

1. O diretório `checklists/` foi criado para cada feature.
2. A checklist padrão `requirements.md` foi preenchida e revisada.
3. Na feature `001`, também foi criada `operational-quality.md`, cobrindo qualidade operacional do MVP.
4. Os marcadores foram usados como gate de leitura para implementação; eles não representam tarefas de código.

**Evidência:** todas as features têm `requirements.md`; `001` contém uma checklist temática adicional.

### 5.5 `$speckit-plan`

**Finalidade:** transformar a intenção funcional em desenho técnico compatível com a constituição.

**Passo a passo observado:**

1. A skill leu a spec ativa e a constituição.
2. Produziu `plan.md` com resumo, contexto técnico, estrutura do projeto e gates constitucionais.
3. Registrou decisões e alternativas em `research.md`.
4. Modelou entidades, relações, validações e transições em `data-model.md`.
5. Formalizou interfaces em `contracts/`, usando OpenAPI ou contratos Markdown conforme a feature.
6. Criou `quickstart.md` com validações automatizadas e cenários manuais.
7. Reavaliou a conformidade constitucional depois do desenho.

**Evidência:** todas as seis features possuem `plan.md`, `research.md`, `data-model.md`, `contracts/` e `quickstart.md`.

### 5.6 `$speckit-tasks`

**Finalidade:** decompor o plano em unidades implementáveis, ordenadas e rastreáveis por história.

**Passo a passo observado:**

1. A skill carregou spec, plano, modelo de dados, contratos, pesquisa, quickstart e constituição.
2. Criou `tasks.md` em formato de checklist com IDs sequenciais `T###`.
3. Separou setup, fundações bloqueantes, histórias de usuário e acabamento transversal.
4. Indicou tarefas paralelizáveis com `[P]` e associou tarefas às histórias com `[US#]`.
5. Incluiu caminho exato do arquivo a criar ou alterar.
6. Registrou dependências, ordem de execução, estratégia de MVP e entrega incremental.
7. Adicionou fases de convergência quando a verificação revelou lacunas posteriores.

**Evidência:** todas as seis features possuem `tasks.md` com a estrutura descrita.

### 5.7 `$speckit-implement`

**Finalidade:** executar as tarefas respeitando checklists, dependências e testes.

**Passo a passo evidenciado pelos artefatos:**

1. As checklists de requisitos foram verificadas como gate.
2. O contexto técnico e a ordem de tarefas foram carregados.
3. Testes, modelos, migrações, serviços, APIs e componentes foram implementados por fase.
4. As tarefas concluídas foram marcadas com `[X]` no `tasks.md`.
5. Quickstarts receberam registros de validação em features que passaram pela implementação.
6. Testes sintéticos e verificações de segurança foram incorporados para evitar dependência de GitLab real ou exposição de segredos.

**Estado comprovado pelos marcadores:**

| Feature | Concluídas | Pendentes | Leitura do estado |
|---|---:|---:|---|
| `001-gitlab-repository-mining` | 154 | 0 | Implementação marcada como completa |
| `002-manual-config-operation` | 52 | 0 | Implementação marcada como completa |
| `003-execution-report-view` | 45 | 0 | Implementação marcada como completa |
| `004-plan-navigation` | 55 | 10 | Núcleo implementado; tarefas adicionais de convergência pendentes |
| `005-standardize-pagination` | 28 | 0 | Implementação marcada como completa |
| `006-paginate-verification-plans` | 0 | 26 | Planejada, ainda não marcada como implementada |

### 5.8 `$speckit-converge`

**Finalidade:** comparar intenção, desenho, tarefas e implementação para encontrar lacunas acionáveis após uma rodada de implementação.

**Passo a passo observado:**

1. A spec foi tratada como fonte de intenção, sob autoridade da constituição.
2. Plano, tarefas e código foram comparados.
3. Lacunas foram convertidas em novas tarefas sequenciais, sem implementar silenciosamente durante a análise.
4. Novas fases **Convergence** foram anexadas aos arquivos de tarefas.
5. O ciclo esperado passou a ser: implementar tarefas novas e executar convergência novamente até não restarem lacunas relevantes.

**Evidência:** há fases explícitas de convergência em `001`, `002` e `004`; as tarefas pendentes de `004` pertencem à continuidade desse processo.

### 5.9 `$speckit-analyze`

**Finalidade:** realizar análise não destrutiva de consistência e cobertura entre `spec.md`, `plan.md` e `tasks.md`.

**Uso no fluxo:** depois da geração de tarefas, a skill pode apontar duplicações, ambiguidades, requisitos sem cobertura, inconsistências terminológicas e violações constitucionais antes da implementação. A presença de alinhamentos cruzados, revisões constitucionais e incrementos de correção é compatível com esse uso, mas o repositório não mantém um relatório separado que permita atribuir com certeza cada correção a uma execução dessa skill.

### 5.10 `$speckit-taskstoissues`

**Finalidade:** converter tarefas em issues do GitHub, evitando duplicatas por ID `T###`.

**Estado no repositório:** a skill está instalada, porém não há artefato local que comprove a criação de issues. Ela não é necessária para a implementação local e não deve ser considerada utilizada sem consultar o repositório remoto de issues.

## 6. Aplicação do ciclo por feature

| Feature | Especificar | Esclarecer | Planejar e desenhar | Gerar tarefas | Implementar | Convergir |
|---|---|---|---|---|---|---|
| `001` | 4 histórias e 37 FRs | Sessões registradas | Pesquisa extensa, modelo, OpenAPI e eventos WebSocket | Fases por US e gates | 154/154 | Múltiplos incrementos concluídos |
| `002` | 3 histórias | Sem evidência direta de sessão | Reuso do agregado, operações dedicadas e credenciais write-only | Fases por edição e execução manual | 52/52 | Fase concluída |
| `003` | 3 histórias e 28 FRs | Sem evidência direta de sessão | Reuso de consultas/rotas; foco no frontend | Fases por relatório, interpretação e histórico | 45/45 | Sem fase explícita no arquivo |
| `004` | 5 histórias e 39 FRs | Sem evidência direta de sessão | Modelos de plano, contratos frontend/API e UX responsiva | Fases por navegação, criação, edição, execução e legado | 55 concluídas, 10 pendentes | Em andamento |
| `005` | 4 histórias e 25 FRs | Sessão registrada | Contrato de ordenação e decisões de desempate | 28 tarefas preparadas | 28/28 concluídas | Implementada |
| `006` | 3 histórias e 17 FRs | Sessão registrada | Envelope paginado, ordenação por ID, contrato backend/frontend e UX de paginação | 26 tarefas preparadas | Ainda não iniciada pelos marcadores | Aguardando implementação |

## 7. Encadeamento prático do processo

O processo seguido pelo projeto pode ser reproduzido assim:

1. **Definir as regras do projeto** com `$speckit-constitution`.
2. **Descrever a necessidade do usuário** com `$speckit-specify`, gerando a feature numerada, histórias, requisitos e critérios de sucesso.
3. **Eliminar ambiguidades relevantes** com `$speckit-clarify` e incorporar as respostas na spec.
4. **Revisar a qualidade dos requisitos** pela checklist padrão e, quando necessário, por `$speckit-checklist` temática.
5. **Aprovar a spec** no gate previsto pelo workflow.
6. **Desenhar a solução** com `$speckit-plan`, gerando pesquisa, modelo de dados, contratos e quickstart.
7. **Verificar a constituição novamente** e aprovar o plano no segundo gate.
8. **Decompor o trabalho** com `$speckit-tasks`, preservando rastreabilidade entre histórias, testes e arquivos.
9. **Analisar consistência** com `$speckit-analyze` antes de alterar o código, quando necessário.
10. **Implementar por fases** com `$speckit-implement`, começando por setup e fundações, depois histórias priorizadas e acabamento.
11. **Validar** com testes unitários, de integração, de contrato e de frontend, além dos cenários do quickstart.
12. **Comparar intenção e resultado** com `$speckit-converge`; transformar lacunas em novas tarefas e repetir implementação/convergência.
13. **Opcionalmente publicar tarefas** como issues usando `$speckit-taskstoissues` quando houver integração com GitHub.

## 8. Artefatos e rastreabilidade

Cada feature segue a cadeia abaixo:

```text
descrição do usuário
  └─ spec.md
      ├─ checklists/requirements.md
      └─ plan.md
          ├─ research.md
          ├─ data-model.md
          ├─ contracts/
          └─ quickstart.md
              └─ tasks.md
                  ├─ testes
                  ├─ código/migrações
                  └─ convergência
```

Essa estrutura permite rastrear uma regra de negócio desde a história e o requisito funcional até a decisão técnica, o contrato, a tarefa, o teste e o arquivo implementado.

## 9. Situação atual e próximos passos

Pelos marcadores dos próprios artefatos:

- o núcleo de mineração (`001`), a operação manual (`002`) e a visualização de relatórios (`003`) estão integralmente marcados como concluídos;
- a navegação por planos (`004`) possui a experiência principal implementada, mas ainda contém 10 tarefas pendentes de convergência;
- a padronização de paginação (`005`) está com todas as suas 28 tarefas marcadas como concluídas;
- a paginação de Planos de Verificação (`006`) também concluiu a fase documental do Spec Kit, mas suas 26 tarefas de implementação permanecem abertas.

O próximo passo coerente com o fluxo Spec Kit é concluir as tarefas pendentes de convergência de `004` e implementar a feature `006`, reutilizando o contrato geral de ordenação já concluído em `005`. A implementação deve começar pelas histórias P1 e validar conjuntamente que a primeira página contém os planos mais recentes, que páginas consecutivas não duplicam nem omitem itens e que o frontend nunca reordena coleções parciais.

## 10. Fontes consultadas

- `.specify/memory/constitution.md`
- `.specify/init-options.json`
- `.specify/workflows/speckit/workflow.yml`
- `.agents/skills/speckit-*/SKILL.md`
- `specs/001-gitlab-repository-mining/`
- `specs/002-manual-config-operation/`
- `specs/003-execution-report-view/`
- `specs/004-plan-navigation/`
- `specs/005-standardize-pagination/`
- `specs/006-paginate-verification-plans/`
