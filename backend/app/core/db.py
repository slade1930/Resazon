"""Motor de base de datos y sesiones SQLAlchemy."""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import NullPool

from app.core.config import settings


def _normalize_driver(url: str) -> str:
    """Fuerza el dialecto psycopg2. SQLAlchemy >=2.1 mapea `postgresql://`
    a psycopg v3 (no instalado), mientras el proyecto usa psycopg2-binary."""
    if url.startswith("postgresql://") and "+psycopg2" not in url:
        return url.replace("postgresql://", "postgresql+psycopg2://", 1)
    return url


engine = create_engine(
    _normalize_driver(settings.DATABASE_URL),
    pool_pre_ping=True,
    poolclass=NullPool,
    future=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    future=True,
)


def get_db() -> Generator[Session, None, None]:
    """Dependencia FastAPI: provee una sesión por request y la cierra."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
