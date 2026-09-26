from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """Configuración central leída desde backend/.env."""

    PROJECT_NAME: str = "ReSazón Loop API"
    VERSION: str = "0.1.0"

    # Gemini / IA
    GEMINI_API_KEY: str = ""
    GEMINI_AI_ENABLED: bool = False
    GEMINI_MODEL: str = "gemini-3.6-flash"
    GEMINI_FALLBACK_MODELS: list[str] = [
        "gemini-3.7-flash",
        "gemini-3.5-flash",
        "gemini-3.1-flash-lite",
        "gemini-flash-lite-latest",
    ]
    GEMINI_EMBEDDING_MODEL: str = "gemini-embedding-001"
    GEMINI_EMBEDDING_DIM: int = 768
    GEMINI_OUTPUT_TOKENS: int = 2048

    # Base de datos
    DATABASE_URL: str = "postgresql+psycopg2://resazon:resazon@localhost:5432/resazon_loop"

    # App
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "info"
    CORS_ALLOWED_ORIGINS: list[str] = ["http://localhost:3000"]

    # Imágenes
    MAX_IMAGE_SIZE_MB: int = 8
    ALLOWED_IMAGE_MIME_TYPES: list[str] = [
        "image/jpeg",
        "image/png",
        "image/webp",
    ]

    # RAG
    RAG_TOP_K: int = 5

    # Recetario
    RECETARIO_PATH: str = "data/raw/Recetario_Nuestro_Sabor_Panama_estructurado.txt"

    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )

    @property
    def max_image_size_bytes(self) -> int:
        return self.MAX_IMAGE_SIZE_MB * 1024 * 1024

    @property
    def recetario_full_path(self) -> Path:
        return BACKEND_DIR / self.RECETARIO_PATH

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == "production"

    @property
    def gemini_configured(self) -> bool:
        return bool(self.GEMINI_API_KEY)


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
