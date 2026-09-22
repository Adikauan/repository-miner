# Implementation Plan: Navegação por Planos de Verificação

**Branch**: `004-plan-navigation` | **Date**: 2026-09-21 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/004-plan-navigation/spec.md`

## Summary

Reorganizar o frontend para apresentar `MonitoringConfiguration` como Plano de Verificação: a rota inicial passa a listar planos, a criação composta ocorre em modal e os detalhes concentram Configuração e Execuções. A implementação reutiliza editores, árvore de repositories, execução manual, acompanhamento e relatório existentes. O backend recebe apenas extensões de consulta necessárias à apresentação: filtro paginado de execuções por configuração, origem derivada e resumo da última execução. Nenhuma regra de mineração ou entidade persistida nova é introduzida.

## Technical Context

**Language/Version**: TypeScript 5.7 / React 19 no frontend; Python 3.13+ no backend  
**Primary Dependencies**: Material UI 6, React Router 7, Vite 6; FastAPI, Pydantic 2, SQLAlchemy 2 e APScheduler 3  
**Storage**: Banco relacional existente, SQLite no desenvolvimento; nenhuma nova tabela ou migração planejada  
**Testing**: Vitest, Testing Library e jsdom no frontend; pytest no backend  
**Target Platform**: Navegadores web modernos em desktop e viewport estreita; API HTTP executada no ambiente servidor existente  
**Project Type**: Aplicação web com frontend e backend no mesmo repositório  
**Performance Goals**: Primeira página de planos e de execuções utilizável em até 2 segundos sob resposta HTTP controlada em teste; a medição exclui latência de GitLab real; mudança de aba não carrega antecipadamente dados da aba inativa; no máximo uma página de histórico permanece em memória  
**Constraints**: Preservar contratos canônicos e regras existentes; não expor segredos; operações GitLab dependem de conexão validada; criação composta não é transacional entre chamadas; manter cinco estados e sete contadores canônicos; validar layout em 1440 px e 390 px sem exigência pixel-perfect; Foundation cria apenas infraestrutura de roteamento e cada história registra suas rotas depois que as páginas-alvo existem  
**Scale/Scope**: Reorganização de uma aplicação de operador único/MVP, aproximadamente quatro superfícies principais (lista, modal, detalhes e relatório/acompanhamento), com paginação de até 50 execuções por consulta

## Constitution Check

*GATE: Passed before Phase 0 and passed again after Phase 1 design.*

| Principle / gate | Pre-design evaluation | Post-design evaluation |
|---|---|---|
| I. Architectural Simplicity | PASS: composição de capacidades existentes; sem novo serviço ou modelo funcional. | PASS: apenas view models e extensões de leitura; nenhuma tabela, fila ou infraestrutura nova. |
| II. Credential Security | PASS: token somente em entrada protegida e nunca em resumo, rota ou estado reapresentado. | PASS: contratos excluem token de respostas e testes exigem sanitização de erros. |
| III. End-to-End Traceability | PASS: plano, execução e relatório mantêm identificadores canônicos. | PASS: filtro usa `configuration_id`; relatório permanece vinculado a `execution_id`. |
| IV. Incremental Mining | PASS: fora da lógica alterada. | PASS: nenhuma mudança em baseline, checkpoint ou idempotência. |
| V. Integration Isolation | PASS: descoberta GitLab continua nos adaptadores existentes. | PASS: frontend usa a camada de API central e não incorpora regras do provedor. |
| VI. Probabilistic AI Findings | PASS: não afetado. | PASS: nenhum novo fluxo de IA ou representação de achado. |
| VII. Testability Without External Services | PASS: cenários usam doubles sintéticos e controlados. | PASS: timeout, rate limit, resposta malformada, indisponibilidade e falha parcial são exercitados sem GitLab real. |
| VIII. Failure Isolation | PASS: criação composta expõe a etapa e falha parcial. | PASS: orquestrador para após falha obrigatória e preserva ID recuperável. |
| IX. Code Privacy and Data Minimization | PASS: nenhum dado novo de código é coletado. | PASS: resumos contêm somente metadados operacionais existentes. |
| X. Execution Observability | PASS: estados e sete contadores existentes permanecem fonte oficial. | PASS: histórico expõe os contadores sem recalculá-los no cliente. |
| Delivery and review gates | PASS: princípios afetados estão identificados e não há exceção. | PASS: quickstart cobre sucesso, falha parcial, segredos, estados e regressão. |

## Project Structure

### Documentation (this feature)

```text
specs/004-plan-navigation/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── frontend-api.md
├── checklists/
│   └── requirements.md
└── tasks.md             # gerado posteriormente por $speckit-tasks
```

### Source Code (repository root)

```text
backend/
├── src/repository_miner/
│   ├── configuration/api/router.py       # resumo do plano
│   ├── executions/api/query_router.py    # filtro/origem do histórico
│   └── persistence/models.py             # reutilizado, sem nova entidade
└── tests/
    ├── contract/
    └── integration/

frontend/
├── src/
│   ├── app/
│   │   ├── App.tsx
│   │   └── routes.tsx
│   ├── configurations/                 # API e editor canônicos reutilizados
│   ├── plans/                          # lista, modal, detalhes e abas
│   ├── repositories/                   # árvore existente reutilizada
│   ├── executions/                     # histórico contextual e acompanhamento
│   ├── reporting/                      # relatório existente reutilizado
│   └── shared/api/                     # cliente HTTP central
└── tests/
    ├── plans/
    ├── configurations/
    ├── executions/
    └── reporting/
```

**Structure Decision**: Manter a aplicação web atual. O novo diretório `frontend/src/plans` contém apenas composição e apresentação do conceito Plano de Verificação; operações de configuração continuam centralizadas em `configurations`, e acompanhamento/relatório permanecem em seus módulos. A Foundation instala somente o provedor, shell e definições neutras de roteamento; nenhuma rota importa página ainda inexistente. Cada user story registra sua rota junto com a página correspondente, mantendo o build válido ao fim de cada fase. O backend muda somente onde uma consulta contextual não pode ser obtida de forma segura e paginada pelos contratos atuais.

## Phase 0: Research Decisions

As decisões e alternativas estão consolidadas em [research.md](research.md). Todos os pontos de contexto técnico foram resolvidos.

## Phase 1: Design and Contracts

- [data-model.md](data-model.md) define view models, relacionamentos, validações e estados sem criar novas entidades persistidas.
- [contracts/frontend-api.md](contracts/frontend-api.md) registra contratos reutilizados e as extensões mínimas de leitura.
- [quickstart.md](quickstart.md) descreve validação executável de lista, criação composta, detalhes, histórico, acompanhamento, relatório e segurança.

## Post-implementation constitutional review (2026-09-21)

The implementation was reviewed against FR-037 and all ten constitutional principles. No deviation was found: the existing configuration remains the domain model; execution, scheduling, report and live-update mechanisms are reused; no mining, baseline, checkpoint or idempotency rule changed; credentials remain write-only and sanitized; integration tests use controlled doubles; canonical execution states and counters remain authoritative. No constitutional exception or additional infrastructure was introduced.

## Complexity Tracking

Nenhuma violação constitucional exige justificativa. O diretório frontend `plans` é uma fronteira de apresentação dentro do projeto existente, não um novo projeto ou camada de domínio.
