"""Application settings loaded from environment variables with defaults."""

import os


class Settings:
    """Singleton settings for the application."""

    def __init__(self) -> None:
        self.app_db_path: str = os.getenv("APP_DB_PATH", "gestion.db")
        self.secret_key: str = os.getenv("SECRET_KEY", "dev-secret-change-in-production")
        self.session_ttl_minutes: int = int(os.getenv("SESSION_TTL_MINUTES", "30"))
        self.app_name: str = os.getenv("APP_NAME", "Gestión de Transporte")
        self.debug: bool = os.getenv("DEBUG", "true").lower() == "true"


settings = Settings()
