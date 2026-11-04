import os
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.db.base import Base
from app.db.session import get_db
from app.main import app

# BD de test (SQLite en memoria o Postgres de test)
TEST_DB_URL = os.getenv("TEST_DATABASE_URL", "sqlite:///./test.db")
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False} if "sqlite" in TEST_DB_URL else {})
TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db() -> Generator[Session, None, None]:
    s = TestingSession()
    try:
        yield s
        s.commit()
    finally:
        s.close()


@pytest.fixture
def client(db):
    def _get_db():
        yield db
    app.dependency_overrides[get_db] = _get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
