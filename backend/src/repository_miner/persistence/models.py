from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class MonitoringConfiguration(Base):
    __tablename__ = "monitoring_configurations"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    gitlab_base_url: Mapped[str] = mapped_column(String(512), nullable=False)
    timezone: Mapped[str] = mapped_column(String(64), default="UTC", nullable=False)
    target_branch: Mapped[str] = mapped_column(String(255), default="QA", nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    current_credential_id: Mapped[Optional[str]] = mapped_column(ForeignKey("credential_references.id"))
    connection_validated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    validated_gitlab_base_url: Mapped[Optional[str]] = mapped_column(String(512))
    validated_credential_id: Mapped[Optional[str]] = mapped_column(String(36))
    credential: Mapped[Optional["CredentialReference"]] = relationship(foreign_keys=[current_credential_id])


class CredentialReference(Base):
    __tablename__ = "credential_references"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    kind: Mapped[str] = mapped_column(String(32), default="gitlab_token", nullable=False)
    status: Mapped[str] = mapped_column(String(16), default="active", nullable=False)
    ciphertext: Mapped[str] = mapped_column(Text, nullable=False)
    key_version: Mapped[str] = mapped_column(String(64), nullable=False)
    fingerprint: Mapped[str] = mapped_column(String(128), nullable=False)
    compromised_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    replaced_by_id: Mapped[Optional[str]] = mapped_column(String(36))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    last_rotated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))


class RepositorySelectionRule(Base):
    __tablename__ = "repository_selection_rules"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    configuration_id: Mapped[str] = mapped_column(ForeignKey("monitoring_configurations.id"), nullable=False)
    kind: Mapped[str] = mapped_column(String(16), nullable=False)
    mode: Mapped[str] = mapped_column(String(16), nullable=False)
    external_id: Mapped[str] = mapped_column(String(255), nullable=False)
    __table_args__ = (UniqueConstraint("configuration_id", "kind", "external_id", name="uq_selection_scope"),)


class AllowedUser(Base):
    __tablename__ = "allowed_users"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    configuration_id: Mapped[str] = mapped_column(ForeignKey("monitoring_configurations.id"), nullable=False)
    original_email: Mapped[str] = mapped_column(String(320), nullable=False)
    normalized_email: Mapped[str] = mapped_column(String(320), nullable=False)
    __table_args__ = (UniqueConstraint("configuration_id", "normalized_email", name="uq_allowed_email"),)


class MiningExecution(Base):
    __tablename__ = "mining_executions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    configuration_id: Mapped[str] = mapped_column(ForeignKey("monitoring_configurations.id"), nullable=False)
    created_by_operator_id: Mapped[Optional[str]] = mapped_column(String(255))
    snapshot_json: Mapped[Optional[str]] = mapped_column(Text)
    snapshot_created_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(24), default="pending", nullable=False)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    terminal_reason: Mapped[Optional[str]] = mapped_column(String(512))
    commits_discovered: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    commits_verified: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    allowed_commits: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    unauthorized_commits: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    repositories_total: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    repositories_completed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    # Kept only for compatibility with databases created before the canonical
    # counters migration; it is never exposed by application contracts.
    repositories_processed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    repositories_failed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


class RepositoryExecution(Base):
    __tablename__ = "repository_executions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    execution_id: Mapped[str] = mapped_column(ForeignKey("mining_executions.id"), nullable=False)
    repository_id: Mapped[str] = mapped_column(String(255), nullable=False)
    branch: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(16), default="pending", nullable=False)
    observed_head: Mapped[Optional[str]] = mapped_column(String(255))
    failure_reason: Mapped[Optional[str]] = mapped_column(String(512))
    __table_args__ = (UniqueConstraint("execution_id", "repository_id", "branch", name="uq_repository_execution"),)


class RepositoryCheckpoint(Base):
    __tablename__ = "repository_checkpoints"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    configuration_id: Mapped[str] = mapped_column(ForeignKey("monitoring_configurations.id"), nullable=False)
    repository_id: Mapped[str] = mapped_column(String(255), nullable=False)
    branch: Mapped[str] = mapped_column(String(255), nullable=False)
    baseline_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    last_processed_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    initialized_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    advanced_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    __table_args__ = (UniqueConstraint("configuration_id", "repository_id", "branch", name="uq_checkpoint_scope"),)


class BaselineResetAudit(Base):
    __tablename__ = "baseline_reset_audits"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    configuration_id: Mapped[str] = mapped_column(ForeignKey("monitoring_configurations.id"), nullable=False)
    repository_id: Mapped[str] = mapped_column(String(255), nullable=False)
    branch: Mapped[str] = mapped_column(String(255), nullable=False)
    previous_checkpoint_hash: Mapped[Optional[str]] = mapped_column(String(255))
    new_baseline_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    operator_id: Mapped[str] = mapped_column(String(255), nullable=False)
    reason: Mapped[str] = mapped_column(String(1024), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class CommitVerification(Base):
    __tablename__ = "commit_verifications"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    configuration_id: Mapped[str] = mapped_column(ForeignKey("monitoring_configurations.id"), nullable=False)
    repository_id: Mapped[str] = mapped_column(String(255), nullable=False)
    branch: Mapped[str] = mapped_column(String(255), nullable=False)
    commit_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    author_name: Mapped[str] = mapped_column(String(320), nullable=False)
    author_email: Mapped[Optional[str]] = mapped_column(String(320))
    committed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    authorization_result: Mapped[str] = mapped_column(String(16), nullable=False)
    first_verified_execution_id: Mapped[str] = mapped_column(ForeignKey("mining_executions.id"), nullable=False)
    verified_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    __table_args__ = (UniqueConstraint("configuration_id", "repository_id", "branch", "commit_hash", name="uq_commit_verification_identity"),)


class UnauthorizedCommitAlert(Base):
    __tablename__ = "unauthorized_commit_alerts"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    configuration_id: Mapped[str] = mapped_column(ForeignKey("monitoring_configurations.id"), nullable=False)
    execution_id: Mapped[str] = mapped_column(ForeignKey("mining_executions.id"), nullable=False)
    commit_verification_id: Mapped[str] = mapped_column(ForeignKey("commit_verifications.id"), nullable=False, unique=True)
    repository_id: Mapped[str] = mapped_column(String(255), nullable=False)
    branch: Mapped[str] = mapped_column(String(255), nullable=False)
    commit_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    author_name: Mapped[str] = mapped_column(String(320), nullable=False)
    author_email: Mapped[Optional[str]] = mapped_column(String(320))
    committed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class WebSocketTicket(Base):
    __tablename__ = "websocket_tickets"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    ticket_digest: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    operator_id: Mapped[str] = mapped_column(String(255), nullable=False)
    execution_id: Mapped[str] = mapped_column(ForeignKey("mining_executions.id"), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    consumed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    __table_args__ = (
        Index("ix_websocket_tickets_expires_at", "expires_at"),
        Index("ix_websocket_tickets_consumed_at", "consumed_at"),
    )


class CredentialIncident(Base):
    __tablename__ = "credential_incidents"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    credential_id: Mapped[str] = mapped_column(ForeignKey("credential_references.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="open", nullable=False)
    suspected_by: Mapped[str] = mapped_column(String(255), nullable=False)
    safe_reason: Mapped[str] = mapped_column(String(512), nullable=False)
    suspected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class CredentialReplacement(Base):
    __tablename__ = "credential_replacements"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    configuration_id: Mapped[str] = mapped_column(ForeignKey("monitoring_configurations.id"), nullable=False)
    previous_credential_id: Mapped[str] = mapped_column(ForeignKey("credential_references.id"), unique=True, nullable=False)
    replacement_credential_id: Mapped[str] = mapped_column(ForeignKey("credential_references.id"), nullable=False)
    reason: Mapped[str] = mapped_column(String(32), nullable=False)
    replaced_by: Mapped[str] = mapped_column(String(255), nullable=False)
    replaced_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    incident_id: Mapped[Optional[str]] = mapped_column(ForeignKey("credential_incidents.id"))


class Schedule(Base):
    __tablename__ = "schedules"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    configuration_id: Mapped[str] = mapped_column(ForeignKey("monitoring_configurations.id"), nullable=False, unique=True)
    recurrence: Mapped[str] = mapped_column(String(16), nullable=False)
    local_time: Mapped[str] = mapped_column(String(16), nullable=False)
    weekday: Mapped[Optional[int]] = mapped_column(Integer)
    day_of_month: Mapped[Optional[int]] = mapped_column(Integer)
    timezone: Mapped[str] = mapped_column(String(64), nullable=False)
    next_run_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))


class ScheduleOccurrence(Base):
    __tablename__ = "schedule_occurrences"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    configuration_id: Mapped[str] = mapped_column(ForeignKey("monitoring_configurations.id"), nullable=False)
    due_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(String(24), nullable=False)
    execution_id: Mapped[Optional[str]] = mapped_column(ForeignKey("mining_executions.id"))
    safe_reason: Mapped[Optional[str]] = mapped_column(String(512))
    __table_args__ = (UniqueConstraint("configuration_id", "due_at", name="uq_schedule_occurrence"),)


class Commit(Base):
    __tablename__ = "commits"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    repository_id: Mapped[str] = mapped_column(String(255), nullable=False)
    commit_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    author_name: Mapped[str] = mapped_column(String(320), nullable=False)
    author_email: Mapped[Optional[str]] = mapped_column(String(320))
    committed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    source_url: Mapped[Optional[str]] = mapped_column(String(1024))
    __table_args__ = (UniqueConstraint("repository_id", "commit_hash", name="uq_repository_commit"),)


class ExecutionCommit(Base):
    __tablename__ = "execution_commits"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    execution_id: Mapped[str] = mapped_column(ForeignKey("mining_executions.id"), nullable=False)
    repository_execution_id: Mapped[str] = mapped_column(ForeignKey("repository_executions.id"), nullable=False)
    commit_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    verification_source: Mapped[str] = mapped_column(String(16), nullable=False)
    __table_args__ = (UniqueConstraint("execution_id", "repository_execution_id", "commit_hash", name="uq_execution_commit"),)


class RepositoryFailure(Base):
    __tablename__ = "repository_failures"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    execution_id: Mapped[str] = mapped_column(ForeignKey("mining_executions.id"), nullable=False)
    repository_execution_id: Mapped[str] = mapped_column(ForeignKey("repository_executions.id"), nullable=False)
    stage: Mapped[str] = mapped_column(String(64), nullable=False)
    code: Mapped[str] = mapped_column(String(64), nullable=False)
    safe_reason: Mapped[str] = mapped_column(String(512), nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    continued: Mapped[bool] = mapped_column(Boolean, nullable=False)
    correlation_id: Mapped[str] = mapped_column(String(64), nullable=False)
