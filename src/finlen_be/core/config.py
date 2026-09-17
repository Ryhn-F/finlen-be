from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", str(BASE_DIR / ".env")),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_NAME: str = "FinLen API"
    APP_ENV: str = "development"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str | None = None
    SEED_DB_ON_STARTUP: bool = True

    # JWT Authentication
    JWT_SECRET_KEY: str | None = None
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 120

    # Gemini & AI Model
    GEMINI_API_KEY: str | None = None
    GEMINI_BASE_URL: str | None = None
    AI_MODEL: str | None = None
    AI_REQUEST_TIMEOUT_SECONDS: float = 45.0

    # Azure AI Document Intelligence
    AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT: str | None = None
    AZURE_DOCUMENT_INTELLIGENCE_KEY: str | None = None

    # Smart Document Analyzer
    DOCUMENT_MAX_FILE_SIZE_MB: int = 10
    DOCUMENT_ANALYSIS_TIMEOUT_SECONDS: int = 60
    GEMINI_MAX_OUTPUT_TOKENS: int = 4096

    # Firebase
    FIREBASE_CREDENTIALS_PATH: str  | None = None
    FIREBASE_PROJECT_ID: str | None = None
    FIREBASE_PRIVATE_KEY_ID: str | None = None
    FIREBASE_PRIVATE_KEY: str | None = None
    FIREBASE_CLIENT_EMAIL: str | None = None
    FIREBASE_CLIENT_ID: str | None = None

    # Supabase (Storage — used to build public URLs for learning material PDFs)
    SUPABASE_URL: str | None = None
    SUPABASE_KEY: str | None = None
    SUPABASE_STORAGE_BUCKET: str = "materials"

    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"

    @property
    def azure_document_intelligence_endpoint(self) -> str | None:
        return self.AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT

    @property
    def azure_document_intelligence_key(self) -> str | None:
        return self.AZURE_DOCUMENT_INTELLIGENCE_KEY

    @property
    def gemini_api_key(self) -> str | None:
        return self.GEMINI_API_KEY

    @property
    def gemini_model(self) -> str:
        return self.GEMINI_MODEL or self.AI_MODEL or "gemini-2.5-flash"

    @property
    def document_max_file_size_mb(self) -> int:
        return self.DOCUMENT_MAX_FILE_SIZE_MB

    @property
    def document_analysis_timeout_seconds(self) -> int:
        return self.DOCUMENT_ANALYSIS_TIMEOUT_SECONDS

    @property
    def gemini_max_output_tokens(self) -> int:
        return self.GEMINI_MAX_OUTPUT_TOKENS

    @property
    def cors_origins_list(self) -> List[str]:
        if not self.CORS_ORIGINS:
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
