"""Application configuration via environment variables."""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.paths import (
    CANONICAL_PROJECT_ROOT,
    ensure_data_directories,
    get_project_root,
)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Mazi BD DDQ Knowledge Hub"
    app_env: Literal["development", "staging", "production"] = "development"
    app_host: str = "127.0.0.1"
    app_port: int = 8000
    local_only: bool = True  # When true, bind to localhost only (not exposed to network)
    secret_key: SecretStr = Field(default=SecretStr("change-me-in-production"))

    # Project root — all BD DDQ Universe data lives under this folder.
    # Default: C:\Users\KhotsoMokoatle\OneDrive - Mazi\Desktop\Projects\Universe\BD - DDQ
    project_root: str | None = None

    aws_region: str = "eu-north-1"
    s3_bucket: str = "khotso-bd-storage-basin"
    aws_profile: str | None = None

    database_url: str = "postgresql+psycopg://postgres:password@localhost:5432/mazi_ddq"

    max_upload_size_mb: int = 100
    presigned_url_expiry_seconds: int = 900
    source_stale_after_months: int = 12

    ai_enabled: bool = False
    llm_provider: str | None = None
    llm_api_key: SecretStr | None = None
    llm_model: str | None = None

    semantic_search_enabled: bool = False
    ocr_enabled: bool = False

    @property
    def root(self) -> Path:
        if self.project_root:
            return Path(self.project_root).resolve()
        return get_project_root()

    @property
    def sample_documents_dir(self) -> Path:
        return self.root / "sample_documents"

    @property
    def backlog_dir(self) -> Path:
        return self.root / "data" / "backlog"

    @property
    def inbox_dir(self) -> Path:
        return self.root / "data" / "inbox"

    @property
    def reports_dir(self) -> Path:
        return self.root / "data" / "reports"

    @property
    def bind_host(self) -> str:
        """Host address used by uvicorn. Local-only mode always uses 127.0.0.1."""
        if self.local_only:
            return "127.0.0.1"
        return self.app_host

    @property
    def max_upload_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024

    @property
    def ai_available(self) -> bool:
        return self.ai_enabled and bool(self.llm_api_key and self.llm_api_key.get_secret_value())

    def safe_repr(self) -> dict:
        """Return settings safe for logging (no secrets)."""
        return {
            "app_name": self.app_name,
            "app_env": self.app_env,
            "app_host": self.bind_host,
            "app_port": self.app_port,
            "local_only": self.local_only,
            "project_root": str(self.root),
            "canonical_root": str(CANONICAL_PROJECT_ROOT),
            "sample_documents_dir": str(self.sample_documents_dir),
            "backlog_dir": str(self.backlog_dir),
            "aws_region": self.aws_region,
            "s3_bucket": self.s3_bucket,
            "aws_profile": self.aws_profile or "(default chain)",
            "database_url": self._mask_database_url(),
            "max_upload_size_mb": self.max_upload_size_mb,
            "presigned_url_expiry_seconds": self.presigned_url_expiry_seconds,
            "ai_enabled": self.ai_enabled,
            "ai_available": self.ai_available,
            "semantic_search_enabled": self.semantic_search_enabled,
            "ocr_enabled": self.ocr_enabled,
        }

    def _mask_database_url(self) -> str:
        if "@" in self.database_url:
            prefix, rest = self.database_url.split("@", 1)
            if ":" in prefix:
                scheme_user = prefix.rsplit(":", 1)[0]
                return f"{scheme_user}:***@{rest}"
        return "***"


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    if settings.project_root:
        import os
        os.environ["PROJECT_ROOT"] = settings.project_root
    ensure_data_directories()
    return settings
