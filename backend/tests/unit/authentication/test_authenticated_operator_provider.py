from repository_miner.authentication.application.provider import RequestOperatorProvider
from repository_miner.authentication.infrastructure.http import host_operator


def test_provider_exposes_only_stable_operator_identity():
    provider = RequestOperatorProvider(host_operator("operator-42"))
    assert provider.current() is not None
    assert provider.current().operator_id == "operator-42"


def test_missing_or_invalid_host_identity_is_rejected():
    assert host_operator(None) is None
    assert host_operator("   ") is None
    assert host_operator("x" * 129) is None


def test_identity_is_trimmed_and_does_not_depend_on_request_payload_objects():
    operator = host_operator("  operator-42  ")
    assert operator is not None
    assert operator.operator_id == "operator-42"
    assert not hasattr(operator, "token")
