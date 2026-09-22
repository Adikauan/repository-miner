from repository_miner.persistence.store import Store


def alerts_for_execution(store: Store, execution_id):
    return [alert for alert in store.alerts.values() if alert.execution_id == execution_id]

