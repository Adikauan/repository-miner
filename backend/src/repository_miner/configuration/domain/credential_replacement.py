from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


ReplacementReason = Literal["preventive", "compromise_remediation"]


@dataclass(frozen=True)
class CredentialReplacementDecision:
    previous_status: str
    new_status: str
    reason: ReplacementReason


def validate_replacement(previous_status: str, reason: str) -> CredentialReplacementDecision:
    if reason not in {"preventive", "compromise_remediation"}:
        raise ValueError("invalid replacement reason")
    if previous_status == "replaced":
        raise ValueError("credential already replaced")
    if previous_status == "compromised" and reason != "compromise_remediation":
        raise ValueError("compromised credential requires remediation")
    if previous_status not in {"active", "compromised"}:
        raise ValueError("credential unavailable")
    return CredentialReplacementDecision(previous_status, "active", reason)  # type: ignore[arg-type]
