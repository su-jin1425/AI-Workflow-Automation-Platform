from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "AI Workflow Automation Platform"
    environment: str = Field(default="development")
    api_prefix: str = "/api"
    frontend_origin: str = "http://localhost:3000"

    database_url: str = "postgresql+asyncpg://postgres:password@db:5432/workflow_db"
    redis_url: str = "redis://redis:6379/0"

    secret_key: str = Field(default="change-this-secret-key")
    access_token_expire_minutes: int = 60
    algorithm: str = "HS256"

    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"

    execution_mode: str = "background"
    workflow_node_timeout_seconds: int = 60
    max_workflow_nodes: int = 100

    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_username: str | None = None
    smtp_password: str | None = None
    smtp_from_email: str | None = None
    smtp_use_tls: bool = True


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
