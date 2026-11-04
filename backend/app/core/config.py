"""Configuración central basada en pydantic-settings.
Secretos vía variables de entorno / Docker secrets / Vault (M21).
"""
from functools import lru_cache
from typing import Literal

from pydantic import Field, PostgresDsn, RedisDsn, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
    )

    # --- App ---
    APP_NAME: str = "Radar de Credenciales Comprometidas"
    APP_ENV: Literal["dev", "staging", "prod"] = "dev"
    APP_VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    TIMEZONE: str = "Europe/Madrid"

    # --- Seguridad ---
    JWT_SECRET: SecretStr = Field(..., min_length=32)
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    MFA_REQUIRED_ROLES: list[str] = ["admin", "soc_analyst"]
    PASSWORD_MIN_LENGTH: int = 12
    CORS_ORIGINS: list[str] = ["http://localhost:5173"]

    # --- Base de datos ---
    DATABASE_URL: PostgresDsn
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_ECHO: bool = False

    # --- Redis ---
    REDIS_URL: RedisDsn = "redis://localhost:6379/0"
    HIBP_CACHE_TTL_HOURS: int = 24
    RATE_LIMIT_PER_MINUTE: int = 60

    # --- HIBP ---
    HIBP_API_KEY: SecretStr
    HIBP_BASE_URL: str = "https://haveibeenpwned.com/api/v3"
    HIBP_USER_AGENT: str = "RadarCreds/1.0"
    HIBP_RATE_LIMIT_SECONDS: float = 1.6
    HIBP_MAX_RETRIES: int = 3
    HIBP_BACKOFF_BASE: float = 2.0

    # --- IdP ---
    IDP_PROVIDER: Literal["entra", "google", "ldap", "generic_webhook"] = "generic_webhook"
    IDP_TENANT_ID: str | None = None
    IDP_CLIENT_ID: str | None = None
    IDP_CLIENT_SECRET: SecretStr | None = None
    IDP_WEBHOOK_URL: str | None = None
    IDP_WEBHOOK_HMAC_SECRET: SecretStr | None = None
    LDAP_SERVER: str | None = None
    LDAP_BASE_DN: str | None = None
    LDAP_BIND_DN: str | None = None
    LDAP_BIND_PASSWORD: SecretStr | None = None

    # --- SMTP ---
    SMTP_HOST: str | None = None
    SMTP_PORT: int = 587
    SMTP_USER: str | None = None
    SMTP_PASSWORD: SecretStr | None = None
    SMTP_FROM: str = "radar-creds@example.com"
    SMTP_USE_TLS: bool = True

    # --- Teams / Slack ---
    TEAMS_WEBHOOK_URL: str | None = None
    SLACK_WEBHOOK_URL: str | None = None

    # --- Reintentos ---
    RETRY_BACKOFF_SCHEDULE_MIN: list[int] = [15, 30, 60, 240, 1440]
    RETRY_MAX_ATTEMPTS: int = 5

    # --- Auditoría ---
    AUDIT_RETENTION_DAYS: int = 365
    AUDIT_VERIFY_INTERVAL_HOURS: int = 6

    # --- Reportes ---
    REPORTS_STORAGE_PATH: str = "/var/lib/radar_creds/reports"
    REPORTS_SIGNED_URL_TTL_SECONDS: int = 86400

    # --- Observabilidad ---
    METRICS_ENABLED: bool = True
    LOG_LEVEL: str = "INFO"
    LOG_JSON: bool = True

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def _split_cors(cls, v):
        if isinstance(v, str):
            return [o.strip() for o in v.split(",") if o.strip()]
        return v


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
