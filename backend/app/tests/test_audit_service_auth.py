import pytest
from fastapi import HTTPException
from pydantic import SecretStr

from app.api.v1.audit import require_n8n_service_token
from app.core.config import settings


def test_n8n_service_token_is_required(monkeypatch):
    monkeypatch.setattr(settings, "N8N_SERVICE_TOKEN", SecretStr("test-service-token"))
    assert require_n8n_service_token("Bearer test-service-token") is None

    with pytest.raises(HTTPException) as exc:
        require_n8n_service_token("Bearer wrong-token")
    assert exc.value.status_code == 401
