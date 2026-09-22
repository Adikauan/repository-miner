import os

os.environ.setdefault("AUTO_CREATE_SCHEMA", "1")

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from repository_miner.persistence.models import Base


@pytest.fixture
def db_session() -> Session:
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    Base.metadata.drop_all(engine)
