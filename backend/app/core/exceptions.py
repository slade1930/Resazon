"""Excepciones de dominio + errores tipados para la API."""

from typing import Any


class AppError(Exception):
    """Error base de la aplicación. Se traduce a envelope estándar en la API."""

    http_status: int = 500
    code: str = "internal_error"
    message: str = "Ocurrió un error inesperado"

    def __init__(self, message: str | None = None, details: Any = None):
        self.message = message or self.message
        self.details = details
        super().__init__(self.message)


class NotFoundError(AppError):
    http_status = 404
    code = "not_found"
    message = "Recurso no encontrado"


class ValidationError(AppError):
    http_status = 422
    code = "validation_error"
    message = "Datos de entrada inválidos"


class ImageValidationError(AppError):
    http_status = 400
    code = "image_validation_error"
    message = "La imagen no es válida"


class UpstreamAIError(AppError):
    http_status = 502
    code = "upstream_ai_error"
    message = "El proveedor de IA no pudo procesar la solicitud"


class AIResponseError(AppError):
    http_status = 502
    code = "ai_response_error"
    message = "La IA devolvió una respuesta no procesable"


class AINotConfiguredError(AppError):
    http_status = 503
    code = "ai_not_configured"
    message = "Gemini no está configurado (falta GEMINI_API_KEY)"


class RAGError(AppError):
    http_status = 500
    code = "rag_error"
    message = "Error en la recuperación semántica"


class DatabaseError(AppError):
    http_status = 500
    code = "database_error"
    message = "Error al interactuar con la base de datos"
