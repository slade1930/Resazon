"""Punto de entrada de ReSazón Loop API."""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_v1_router
from app.core.config import settings
from app.core.exceptions import AppError
from app.core.logging import get_logger, setup_logging
from app.schemas.common import ErrorResponse

logger = get_logger("main")


def _ensure_schema() -> None:
    """Crea las tablas que falten (idempotente). Alembic se usa en desarrollo;
    en serverless (Vercel) algunas migraciones nunca se aplicaron, así que
    garantizamos el esquema aquí al arrancar sin tocar tablas existentes."""
    try:
        import app.models  # noqa: F401 - registra todos los modelos en Base.metadata

        from sqlalchemy import text

        from app.core.db import engine
        from app.models.base import Base

    except Exception:  # noqa: BLE001 - nunca impedir el arranque
        logger.exception("No se pudieron importar los modelos")
        return

    try:
        with engine.begin() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    except Exception:  # noqa: BLE001 - la extensión ya existe en la mayoría de DBs
        logger.exception("No se pudo habilitar la extensión vector (la tablas de IA sí se crearán)")

    try:
        Base.metadata.create_all(bind=engine, checkfirst=True)
        logger.info("Esquema verificado/creado (tablas faltantes añadidas)")
    except Exception:  # noqa: BLE001 - nunca impedir el arranque por un esquema parcial
        logger.exception("No se pudo verificar el esquema al arrancar")


def create_app() -> FastAPI:
    setup_logging()

    application = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        docs_url="/docs" if not settings.is_production else None,
        redoc_url=None,
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.include_router(api_v1_router, prefix="/api/v1")

    @application.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
        payload = ErrorResponse(code=exc.code, message=exc.message, details=exc.details)
        return JSONResponse(status_code=exc.http_status, content=payload.model_dump())

    @application.exception_handler(RequestValidationError)
    async def validation_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        payload = ErrorResponse(
            code="validation_error",
            message="Datos de entrada inválidos",
            details=exc.errors(),
        )
        return JSONResponse(status_code=422, content=payload.model_dump())

    @application.exception_handler(Exception)
    async def unhandled_handler(request: Request, exc: Exception) -> JSONResponse:
        payload = ErrorResponse(code="internal_error", message="Ocurrió un error inesperado")
        return JSONResponse(status_code=500, content=payload.model_dump())

    _ensure_schema()
    return application


app = create_app()
