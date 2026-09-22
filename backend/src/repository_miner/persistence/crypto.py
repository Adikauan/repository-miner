from __future__ import annotations

import base64
import hashlib
import os

from cryptography.fernet import Fernet


def _fernet() -> Fernet:
    configured = os.getenv("ENCRYPTION_KEY")
    if configured:
        key = configured.encode()
        try:
            return Fernet(key)
        except Exception:
            pass
    # Development fallback keeps the secret out of persisted plaintext; production must provide
    # ENCRYPTION_KEY through an external secret mechanism.
    key = base64.urlsafe_b64encode(hashlib.sha256(b"repository-miner-development-key").digest())
    return Fernet(key)


def encrypt_secret(value: str) -> str:
    return _fernet().encrypt(value.encode()).decode()


def decrypt_secret(value: str) -> str:
    return _fernet().decrypt(value.encode()).decode()


def fingerprint(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()
