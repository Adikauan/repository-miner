from repository_miner.persistence.models import Base
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect
from pathlib import Path


def test_persistence_metadata_contains_release_tables():
    tables = set(Base.metadata.tables)
    assert {"monitoring_configurations", "mining_executions", "commit_verifications", "unauthorized_commit_alerts", "websocket_tickets", "schedules"} <= tables


def test_migrations_upgrade_and_downgrade_clean_database():
    database = Path(__file__).parents[3] / "migration_test.db"
    config = Config(str(Path(__file__).parents[3] / "alembic.ini"))
    config.set_main_option("sqlalchemy.url", f"sqlite:///{database}")
    command.upgrade(config, "head")
    engine = create_engine(f"sqlite:///{database}")
    assert "websocket_tickets" in inspect(engine).get_table_names()
    command.downgrade(config, "base")
    assert inspect(engine).get_table_names() == ["alembic_version"]
    engine.dispose()
    database.unlink(missing_ok=True)
