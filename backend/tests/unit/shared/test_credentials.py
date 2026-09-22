from repository_miner.configuration.infrastructure.credentials import is_usable
from repository_miner.persistence.crypto import decrypt_secret, encrypt_secret, fingerprint


def test_credential_is_authenticated_encrypted_and_round_trips_without_plaintext():
    secret = "glpat-test-secret"
    ciphertext = encrypt_secret(secret)
    assert ciphertext != secret
    assert decrypt_secret(ciphertext) == secret
    assert fingerprint(secret) != secret


def test_credential_status_only_allows_active_reference():
    assert is_usable("active") is True
    assert is_usable("compromised") is False
    assert is_usable("replaced") is False


def test_encryption_key_rotation_changes_ciphertext_but_keeps_plaintext(monkeypatch):
    from cryptography.fernet import Fernet

    key_one = Fernet.generate_key().decode()
    key_two = Fernet.generate_key().decode()
    monkeypatch.setenv("ENCRYPTION_KEY", key_one)
    first = encrypt_secret("token")
    monkeypatch.setenv("ENCRYPTION_KEY", key_two)
    second = encrypt_secret("token")
    assert first != second
    assert decrypt_secret(second) == "token"
