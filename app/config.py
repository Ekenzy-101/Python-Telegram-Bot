"""Application configuration."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    # App
    app_name: str = "Kenzy Mail AI"
    app_version: str = "1.0.0"
    app_debug: bool = False
    app_origins: str = "*"

    log_level: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    # OpenAI API
    openai_api_key: str
    openai_api_url: str
    openai_model: str

    redis_url: str

    # Telegram
    telegram_bot_token: str
    telegram_webhook_url: str


settings = Settings()
