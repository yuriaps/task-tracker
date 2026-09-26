from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Central place for all configuration. Values are read from environment
    variables (or a local .env file) instead of being hardcoded, so the
    same code runs in dev, test, and prod with different settings.
    """

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # --- Database ---
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/taskmanager"

    # --- Auth ---
    secret_key: str = "change-me-in-.env"  # never leave this as the default in real use
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # --- Redis / Celery ---
    redis_url: str = "redis://localhost:6379/0"


# A single shared instance imported everywhere else in the app.
settings = Settings()
