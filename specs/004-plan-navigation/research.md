# Research: Navegação por Planos de Verificação

## 1. Representação do plano

**Decision**: Tratar `MonitoringConfiguration` como a identidade persistida do Plano de Verificação e introduzir apenas tipos de apresentação no frontend.

**Rationale**: A configuração já agrega conexão, escopo, branch, usuários, schedule, status e execuções. Uma nova entidade duplicaria identidade e sincronização sem valor funcional.

**Alternatives considered**: Criar entidade/tabela `VerificationPlan`; rejeitada por duplicar o modelo. Renomear a entidade backend; rejeitada por ampliar migração sem necessidade.

## 2. Navegação e compatibilidade

**Decision**: Adotar rotas endereçáveis para lista, detalhes com aba, acompanhamento e relatório, mantendo redirecionamentos de URLs antigas com correspondência inequívoca.

**Rationale**: O estado atual em memória não suporta link direto, recarga ou histórico do navegador de forma robusta. As dependências atuais já incluem roteamento.

**Alternatives considered**: Continuar alternando componentes apenas por estado local; rejeitada por não preservar URL/contexto. Manter rotas antigas completas em paralelo; rejeitada por duplicar interfaces.

## 3. Histórico por plano

**Decision**: Estender `GET /api/v1/executions` com `configuration_id`, `offset` e `limit`, aplicando o filtro antes da paginação.

**Rationale**: Filtrar uma página global no cliente pode omitir execuções do plano e exigiria carregar todo o histórico, violando a especificação.

**Alternatives considered**: Filtragem cliente; rejeitada por incorreção e desperdício. Novo endpoint aninhado; viável, mas desnecessário quando o recurso já aceita filtros.

## 4. Origem manual ou agendada

**Decision**: Expor `origin` como campo derivado na consulta: execução associada a uma ocorrência de schedule é `scheduled`; as demais são `manual`.

**Rationale**: `ScheduleOccurrence.execution_id` registra a origem agendada de forma auditável. Não é necessária coluna ou migração.

**Alternatives considered**: Inferir por `created_by_operator_id`; rejeitada porque a ausência de operador não é prova suficiente. Adicionar coluna persistida; rejeitada por redundância.

## 5. Resumos da listagem de planos

**Decision**: Incluir `last_execution` e `schedule_summary` opcionais na representação de lista. `schedule_summary` expõe somente `recurrence`, `local_time`, `weekday` e `day_of_month`.

**Rationale**: Evita consultas por card e fornece data/estado e periodicidade pedidos para identificação operacional, sem expor ocorrências, próximo cálculo ou estruturas internas do scheduler. Os objetos são somente leitura.

**Alternatives considered**: Buscar execuções e schedule separadamente para cada plano; rejeitada pelo padrão N+1. Expor a entidade completa de schedule; rejeitada por vazar detalhes desnecessários. Omitir periodicidade; rejeitada por impedir FR-003.

## 6. Criação composta no modal

**Decision**: Usar um orquestrador frontend com etapas canônicas. Ao validar a conexão pela primeira vez, criar a configuração-base, guardar seu ID somente na sessão do modal e então validar/carregar a hierarquia. Na confirmação, persistir básicos, escopo, usuários e schedule em ordem, parando na primeira falha obrigatória.

**Rationale**: Os contratos GitLab dependentes exigem uma configuração persistida e credencial cifrada. O fluxo permanece uma única criação para o usuário e reutiliza segurança e validações existentes.

**Alternatives considered**: Enviar token a endpoints temporários de preview; rejeitada por ampliar superfície sensível e duplicar integração. Criar endpoint transacional agregado; rejeitada por escopo e por envolver chamadas externas dentro de uma transação longa.

## 7. Recuperação de criação parcial

**Decision**: Se a configuração-base já existir e uma etapa posterior falhar ou o modal for fechado, atualizar a lista, informar que o plano ficou incompleto e oferecer abertura na Configuração para retomada. Nunca anunciar sucesso completo.

**Rationale**: Não existe exclusão canônica segura nem transação distribuída entre chamadas. Tornar o estado persistido visível é mais honesto e recuperável.

**Alternatives considered**: Exclusão compensatória; rejeitada porque inexiste contrato e poderia apagar auditoria/credencial. Ocultar o registro; rejeitada por criar estado persistido invisível.

## 8. Estado e cache no frontend

**Decision**: Manter estado local por página/modal, com funções da camada de API como única porta HTTP; atualizar/inutilizar somente as coleções afetadas após mutação.

**Rationale**: O projeto não possui biblioteca global de dados e o escopo não justifica introduzi-la. O padrão atual é suficiente quando encapsulado em hooks/controladores pequenos.

**Alternatives considered**: Adicionar biblioteca global de cache; rejeitada por complexidade sem necessidade evidenciada. Chamadas HTTP em componentes diversos; rejeitada por duplicação.

## 9. Reutilização de configuração e relatório

**Decision**: Extrair seções reutilizáveis do editor atual, mantendo as funções de API canônicas; incorporar o relatório e o acompanhamento existentes por rota, sem bifurcar seus componentes.

**Rationale**: Preserva comportamentos testados, reduz regressão e atende à proibição de implementações paralelas.

**Alternatives considered**: Copiar formulários para o modal e detalhes; rejeitada por divergência futura. Reescrever relatório; rejeitada por duplicar regras de apresentação.

## 10. Responsividade e acessibilidade

**Decision**: Usar lista em cards/linhas responsivas com ações textuais ou ícones rotulados, modal rolável em tela estreita e tabelas de execução com fallback responsivo. Os testes usam 1440 px como desktop e 390 px como tela estreita, validando usabilidade e ausência de quebra estrutural sem comparação pixel-perfect.

**Rationale**: Mantém hierarquia e ações acessíveis sem redesenhar o sistema visual.

**Alternatives considered**: Tabela fixa para todos os tamanhos; rejeitada por baixa usabilidade em viewport estreita. Novo design system; fora do escopo.

## 11. Integração progressiva das rotas

**Decision**: A Foundation configura somente provedor, shell, helpers e uma rota segura para a superfície já existente. Rotas de lista, detalhes, acompanhamento, relatório e compatibilidade são registradas pela user story que entrega cada página.

**Rationale**: Nenhuma fase pode importar componente inexistente ou deixar o build inválido. A rota e sua página tornam-se uma unidade de entrega.

**Alternatives considered**: Declarar antecipadamente todas as rotas; rejeitada porque cria imports quebrados ou placeholders descartáveis. Criar páginas vazias na Foundation; rejeitada por deslocar trabalho das histórias.

## 12. Falhas da integração GitLab

**Decision**: Exercitar o modal com doubles controlados para sucesso, timeout, rate limit, resposta malformada, indisponibilidade e falha parcial nas operações dependentes.

**Rationale**: Atende à constituição e torna os resultados determinísticos, seguros e independentes de rede/credencial real.

**Alternatives considered**: GitLab real em testes; rejeitada por instabilidade, segurança e violação da testabilidade sem serviços externos. Cobertura genérica de erro; rejeitada por não provar os modos de falha exigidos.

## 13. Desempenho percebido

**Decision**: Medir em teste o intervalo entre a entrada na superfície e seu estado utilizável, usando respostas HTTP controladas para lista de planos e histórico; o limite é 2 segundos.

**Rationale**: A medição é reproduzível e isola o frontend. Latência de GitLab real não integra o critério.

**Alternatives considered**: Medir rede externa; rejeitada por variabilidade e por atribuir ao frontend uma latência que ele não controla. Avaliação apenas subjetiva; rejeitada por não ser reproduzível.

## 14. Validação com operadores

**Decision**: SC-002, SC-003 e SC-012 são gates manuais de aceitação, documentados por cenário, tarefa, mínimo de cinco participantes, resultado observado, taxa de conclusão e notas de clareza.

**Rationale**: Esses resultados dependem de julgamento humano. Podem ser executados quando houver participantes e não bloqueiam implementação, testes automatizados ou build durante o desenvolvimento.

**Alternatives considered**: Simular operadores em testes automatizados; rejeitada por não medir compreensão humana. Bloquear desenvolvimento até recrutamento; rejeitada por não agregar segurança técnica.
