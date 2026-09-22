from repository_miner.persistence.store import store


def consume_ticket(ticket: str, operator_id: str, execution_id) -> bool:
    return store.consume_ticket(ticket, operator_id, execution_id)

