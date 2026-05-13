import logging
from functools import lru_cache
from pathlib import Path

import yaml
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.schemas import AppConfigFile


class Settings(BaseSettings):
    config_path: str = "data/sources.example.yml"
    database_path: str = "data/jobs.db"
    log_level: str = "INFO"
    request_timeout_seconds: float = 15.0
    user_agent: str = "JobWatcherPi/0.1"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()


def configure_logging() -> None:
    settings = get_settings()
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )


def load_app_config(config_path: str | None = None) -> AppConfigFile:
    settings = get_settings()
    path = Path(config_path or settings.config_path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    with path.open("r", encoding="utf-8") as file:
        raw_config = yaml.safe_load(file) or {}

    return AppConfigFile.model_validate(raw_config)
