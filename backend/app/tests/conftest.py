import os
from collections.abc import Generator
from pathlib import Path

import pytest
from alembic.config import Config

from alembic import command

os.environ.setdefault(
    "DATABASE_URL",
    os.getenv("TEST_DATABASE_URL", "postgresql+psycopg://radar:test@localhost:5433/radar_test"),
)
os.environ.setdefault("JWT_SECRET", "test-only-secret-with-at-least-32-characters")
os.environ.setdefault("HIBP_API_KEY", "test-only-hibp-key")
os.environ.setdefault("REDIS_REQUIRED", "false")
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db.session import get_db
from app.main import app

# PostgreSQL de test; no se sustituye por SQLite porque el esquema usa tipos,
# extensiones y triggers específicos de PostgreSQL.
TEST_DB_URL = os.getenv("TEST_DATABASE_URL", os.environ["DATABASE_URL"])
engine = create_engine(TEST_DB_URL)
TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)


@pytest.fixture(scope="session")
def setup_db():
    if not os.getenv("TEST_DATABASE_URL"):
        pytest.skip("Las pruebas de integración requieren TEST_DATABASE_URL de PostgreSQL")
    alembic_config = Config(str(Path(__file__).parents[2] / "alembic.ini"))
    command.upgrade(alembic_config, "head")
    yield
    command.downgrade(alembic_config, "base")


@pytest.fixture
def db(setup_db) -> Generator[Session, None, None]:
    s = TestingSession()
    try:
        yield s
    finally:
        s.rollback()
        s.close()


@pytest.fixture
def client(db):
    def _get_db():
        yield db
    app.dependency_overrides[get_db] = _get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
