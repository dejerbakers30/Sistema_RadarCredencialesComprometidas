import pytest
from fastapi import HTTPException

from app.core.config import settings
from app.main import app, ready


def test_cors_comes_from_settings():
    cors = next(m for m in app.user_middleware if m.cls.__name__ == "CORSMiddleware")
    assert cors.kwargs["allow_origins"] == settings.CORS_ORIGINS
    assert cors.kwargs["allow_credentials"] is True


def test_ready_hides_dependency_error(monkeypatch):
    class BrokenEngine:
        def connect(self):
            raise RuntimeError("secret database detail")

    monkeypatch.setattr("app.main.engine", BrokenEngine())
    with pytest.raises(HTTPException) as error:
        ready()
    assert error.value.status_code == 503
    assert "secret database detail" not in str(error.value.detail)
