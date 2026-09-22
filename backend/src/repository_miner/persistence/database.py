from __future__ import annotations

import os
from collections.abc import Generator

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import Session, sessionmaker

from repository_miner.persistence.models import Base


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./repository_miner.db")
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, future=True, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False, class_=Session)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    # Development/test databases may predate the latest migration. Keep startup
    # compatible while production deployments continue to use Alembic.
    columns = {column["name"] for column in inspect(engine).get_columns("mining_executions")}
    missing = []
    if "created_by_operator_id" not in columns:
        missing.append("ALTER TABLE mining_executions ADD COLUMN created_by_operator_id VARCHAR(255)")
    if "snapshot_json" not in columns:
        missing.append("ALTER TABLE mining_executions ADD COLUMN snapshot_json TEXT")
    if "snapshot_created_at" not in columns:
        missing.append("ALTER TABLE mining_executions ADD COLUMN snapshot_created_at DATETIME")
    if "repositories_total" not in columns:
        missing.append("ALTER TABLE mining_executions ADD COLUMN repositories_total INTEGER NOT NULL DEFAULT 0")
    if "repositories_completed" not in columns:
        missing.append("ALTER TABLE mining_executions ADD COLUMN repositories_completed INTEGER NOT NULL DEFAULT 0")
    if missing:
        with engine.begin() as connection:
            for statement in missing:
                connection.execute(text(statement))


def get_session() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
