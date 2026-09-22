from __future__ import annotations


def normalize_allowed_emails(emails: list[str]) -> set[str]:
    values = [email.strip().casefold() for email in emails if email.strip()]
    if len(values) != len(set(values)):
        raise ValueError("duplicate_allowed_email")
    return set(values)

