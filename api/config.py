"""Configuration management for AI Image Detector API."""

from pydantic_settings import BaseSettings
from typing import List
from functools import lru_cache


class Settings(BaseSettings):
    """API configuration settings loaded from environment variables."""

    # Server settings
    api_host: str = "127.0.0.1"
    api_port: int = 8000

    # CORS settings
    cors_origins: str = "*"

    # Rate limiting
    rate_limit_requests: int = 30
    rate_limit_window_seconds: int = 60

    # Logging
    log_dir: str = "./logs"
    log_retention_days: int = 30

    # Model settings
    model_name: str = "prithivMLmods/deepfake-detector-model-v1"

    # Cache settings
    cache_max_size: int = 100
    cache_ttl_seconds: int = 300

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        if self.cors_origins == "*":
            return ["*"]
        return [origin.strip() for origin in self.cors_origins.split(",")]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
