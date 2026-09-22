# Research: Visualização de Relatório de Execução

## Decision: reutilizar as consultas e rotas existentes

- **Decision**: A tela consumirá o relatório pelo execution_id e reutilizará os recursos de consulta de execução já existentes.
- **Rationale**: O backend já é a fonte oficial do estado, contadores, alertas e falhas; duplicar regras no frontend criaria divergência.
- **Alternatives considered**: Reconstruir o relatório a partir dos eventos de acompanhamento foi rejeitado porque eventos são transitórios e não representam necessariamente o estado final persistido.

## Decision: separar resumo e coleções paginadas

- **Decision**: O resumo será carregado separadamente das coleções de repositories, commits, UnauthorizedCommitAlerts e falhas, respeitando offset e limit quando oferecidos.
- **Rationale**: Coleções podem crescer independentemente e a troca de página não deve recarregar toda a tela.
- **Alternatives considered**: Um payload único sem paginação foi rejeitado por não atender listas potencialmente grandes.

## Decision: reusar o acompanhamento de execuções ativas

- **Decision**: Execuções pending ou running exibem os dados disponíveis e encaminham para o acompanhamento existente; não será criado um segundo canal de atualização.
- **Rationale**: O banco permanece a fonte oficial e o mecanismo atual já trata tickets, reconexão e eventos.
- **Alternatives considered**: Polling agressivo ou um novo fluxo de eventos foi rejeitado por duplicar responsabilidades e aumentar carga.

## Decision: compatibilidade e segurança

- **Decision**: Estados, contadores, ownership de alertas e mensagens seguras serão tratados como valores canônicos; fixtures e mocks usarão apenas dados sintéticos.
- **Rationale**: Preserva contratos existentes e atende à política de não exposição de segredos.
- **Alternatives considered**: Inferir contadores a partir das listas foi rejeitado porque pode produzir números diferentes dos contadores persistidos.

## Decision: ausência de mudanças no backend

- **Decision**: O incremento não cria migration, novo estado, novo endpoint de mineração ou alteração de contrato WebSocket.
- **Rationale**: A especificação explicitamente limita a funcionalidade à visualização frontend e à navegação para acompanhamento.
- **Alternatives considered**: Criar novos dados de relatório ou filtros obrigatórios no backend foi rejeitado; filtros opcionais só serão usados quando já suportados.
