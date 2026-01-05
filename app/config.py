"""Application configuration."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    # App
    app_name: str = "Kenzy Mail AI"
    app_debug: bool = True
    app_email: str = "ekeneonyekaba@gmail.com"
    app_github: str = "https://github.com/Ekenzy-101/Python-Telegram-Bot"
    app_telegram: str = "kenzy_email_bot"
    app_origins: str = "*"
    app_version: str = "1.0.0"

    google_application_credentials: str = ""

    log_level: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    # OpenAI API
    openai_api_key: str
    openai_api_url: str
    openai_model: str

    redis_url: str

    # Telegram
    telegram_bot_token: str
    telegram_webhook_secret: str
    telegram_webhook_url: str = ""


settings = Settings()
