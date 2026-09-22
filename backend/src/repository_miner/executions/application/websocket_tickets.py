from repository_miner.persistence.store import store


def issue_ticket(operator_id: str, execution_id):
    return store.issue_ticket(operator_id, execution_id)

