"""Envelopes de respuesta, paginación y errores comunes."""

from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class Envelope(BaseModel, Generic[T]):
    """Envoltorio estándar: toda respuesta exitosa viaja dentro de `data`."""

    data: T


class ErrorResponse(BaseModel):
    code: str
    message: str
    details: Any = None


class PaginationMeta(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    total: int = 0
    total_pages: int = 0
