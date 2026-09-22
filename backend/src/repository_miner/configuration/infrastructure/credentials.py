from repository_miner.persistence.crypto import encrypt_secret, fingerprint


def is_usable(status: str) -> bool:
    return status == "active"

