from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"


class Settings(BaseSettings):
    app_name: str = "Flashcard Engine API"
    database_url: str = "sqlite:///./data/app.db"
    openrouter_api_key: str = ""
    openrouter_model: str = "openai/gpt-3.5-turbo"
    frontend_url: str = "http://localhost:3000"

    model_config = SettingsConfigDict(
        env_file=ENV_PATH,
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
