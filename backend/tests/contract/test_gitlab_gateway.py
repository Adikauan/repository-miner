from types import SimpleNamespace

import httpx
import pytest

from repository_miner.gitlab.infrastructure.http_gateway import HttpGitLabGateway
from repository_miner.shared.domain.types import GitLabErrorCode


def response(status: int, payload: object) -> SimpleNamespace:
    return SimpleNamespace(status_code=status, json=lambda: payload)


def test_valid_connection_response(monkeypatch):
    monkeypatch.setattr("httpx.get", lambda *args, **kwargs: response(200, {"id": 7}))
    HttpGitLabGateway().validate_connection("https://gitlab.example.com", "secret")


@pytest.mark.parametrize(
    ("side_effect", "status", "payload", "code"),
    [
        (httpx.TimeoutException("timeout"), 200, {}, GitLabErrorCode.TIMEOUT),
        (httpx.ConnectError("offline"), 200, {}, GitLabErrorCode.UNAVAILABLE),
        (None, 429, {}, GitLabErrorCode.RATE_LIMITED),
        (None, 503, {}, GitLabErrorCode.UNAVAILABLE),
        (None, 401, {}, GitLabErrorCode.UNEXPECTED_RESPONSE),
        (None, 200, ValueError("malformed"), GitLabErrorCode.MALFORMED_PAYLOAD),
    ],
)
def test_external_failures_translate_to_safe_application_errors(monkeypatch, side_effect, status, payload, code):
    def fake_get(*args, **kwargs):
        if side_effect:
            raise side_effect
        if isinstance(payload, ValueError):
            return SimpleNamespace(status_code=status, json=lambda: (_ for _ in ()).throw(payload))
        return response(status, payload)

    monkeypatch.setattr("httpx.get", fake_get)
    with pytest.raises(Exception) as exc_info:
        HttpGitLabGateway().validate_connection("https://gitlab.example.com", "CANARY-TOKEN")
    error = exc_info.value
    assert getattr(error, "code", None) == code.value
    assert "CANARY-TOKEN" not in str(error)


def test_malformed_success_payload_is_rejected_without_secret(monkeypatch):
    monkeypatch.setattr("httpx.get", lambda *args, **kwargs: response(200, {"unexpected": True}))
    with pytest.raises(Exception) as exc_info:
        HttpGitLabGateway().validate_connection("https://gitlab.example.com", "CANARY-TOKEN")
    assert exc_info.value.code == GitLabErrorCode.MALFORMED_PAYLOAD.value
    assert "CANARY-TOKEN" not in str(exc_info.value)
