# Repository Miner

## Desenvolvimento

1. Configure `DATABASE_URL`, `ENCRYPTION_KEY` e, opcionalmente, `WEBSOCKET_TICKET_PEPPER`.
2. Execute as migrations com `alembic upgrade head` dentro de `backend`.
3. Instale as dependências Python e execute `uvicorn repository_miner.app:app --reload`.

Tokens GitLab são armazenados cifrados e nunca devem ser incluídos em logs, URLs ou mensagens de erro.

## Agendamento

Schedules persistentes suportam recorrência diária, semanal e mensal. O dia mensal é ajustado para o último
dia disponível quando necessário. Configurações desabilitadas não geram execuções agendadas, mas continuam
aceitando execuções manuais.

## Credenciais e incidentes

Ao suspeitar de exposição, marque a credencial como comprometida e substitua-a antes de nova utilização.
A substituição preserva checkpoints, execuções, verificações e alertas históricos. A rotação junto ao GitLab
é responsabilidade do operador e depende do provedor.

## Acompanhamento em tempo real

Solicite um ticket temporário autenticado por REST antes de abrir o WebSocket. O ticket é vinculado ao
operador e à execução, expira rapidamente e só pode ser usado uma vez. Após perda de conexão, consulte o
estado por REST e solicite um novo ticket; a mineração continua independentemente do socket.
