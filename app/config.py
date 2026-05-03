from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = Field(default="sqlite+pysqlite:///:memory:", alias="DATABASE_URL")
    telegram_bot_token: str = Field(default="", alias="TELEGRAM_BOT_TOKEN")
    app_env: str = Field(default="local", alias="APP_ENV")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    min_price_improvement_percent: float = Field(default=10, alias="MIN_PRICE_IMPROVEMENT_PERCENT")
    min_score_improvement: float = Field(default=15, alias="MIN_SCORE_IMPROVEMENT")
    notification_cooldown_hours: int = Field(default=12, alias="NOTIFICATION_COOLDOWN_HOURS")
    default_check_frequency_minutes: int = Field(
        default=180,
        alias="DEFAULT_CHECK_FREQUENCY_MINUTES",
    )

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
