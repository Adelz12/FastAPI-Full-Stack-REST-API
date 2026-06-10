import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Database configuration
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgrespassword@localhost:5432/fastapi_dev_db"

    # Cache configuration
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT Authentication configuration
    SECRET_KEY: str = "3ec66497f6c382bf832a823b8fca8a4de93a9cf41d2f099182312b9d62886f7c"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Pydantic Settings configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
