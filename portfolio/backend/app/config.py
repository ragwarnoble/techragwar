from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


class Settings(BaseSettings):

    app_name: str = "Framework-FreeFE API"

    app_version: str = "0.2.0"

    database_url: str = "sqlite:///./data/portfolio.db"

    cors_origins: str = "*"

    ai_provider: str = "openai"

    ai_model: str = "gpt-4o-mini"

    ai_api_key: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
