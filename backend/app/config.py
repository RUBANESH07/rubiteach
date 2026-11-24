import secrets
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[2]  # project folder (the one containing backend/ and index.html)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite:///./academy.db"
    # A random key per process is fine for dev (tokens die on restart); set SECRET_KEY in production.
    secret_key: str = secrets.token_urlsafe(48)
    access_token_minutes: int = 1440
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    query_timeout_seconds: float = 2.0
    max_query_chars: int = 5000
    python_timeout_seconds: float = 5.0

    @field_validator("database_url")
    @classmethod
    def _anchor_sqlite_path(cls, v: str) -> str:
        """A relative SQLite file is always placed in the project folder, so the app uses the SAME database
        whether you start it from the project folder or from backend/ (otherwise each folder gets its own)."""
        prefix = "sqlite:///"
        if v.startswith(prefix) and not v.startswith(prefix + ":memory:"):
            raw = v[len(prefix):]
            if raw and not Path(raw).is_absolute():
                return prefix + (ROOT / raw).resolve().as_posix()
        return v


settings = Settings()
