"""Application configuration loaded from environment variables."""

import os
from dataclasses import dataclass, field
from typing import List


@dataclass(frozen=True)
class Settings:
    app_name: str = field(
        default_factory=lambda: os.getenv("APP_NAME", "three-tier-devsecops-api")
    )
    app_env: str = field(default_factory=lambda: os.getenv("APP_ENV", "development"))
    log_level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))
    database_url: str = field(
        default_factory=lambda: os.getenv(
            "DATABASE_URL", "sqlite:///./local_dev.db"
        )
    )
    allowed_origins_raw: str = field(
        default_factory=lambda: os.getenv(
            "ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5173,http://localhost:8080"
        )
    )

    @property
    def allowed_origins(self) -> List[str]:
        return [
            origin.strip()
            for origin in self.allowed_origins_raw.split(",")
            if origin.strip()
        ]


def get_settings() -> Settings:
    return Settings()
