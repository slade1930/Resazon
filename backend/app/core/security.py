"""Validación y saneamiento de seguridad (imágenes, nombres de archivo)."""

import re
from typing import BinaryIO

from app.core.config import settings
from app.core.exceptions import ImageValidationError

_SAFE_FILENAME = re.compile(r"[^a-zA-Z0-9._\- ]")


def validate_image_size_and_mime(content: bytes, content_type: str | None) -> None:
    """Valida que el contenido no exceda el tamaño límite y tenga un MIME permitido."""
    if not content:
        raise ImageValidationError(message="El archivo está vacío")

    if len(content) > settings.max_image_size_bytes:
        raise ImageValidationError(
            message=(f"La imagen supera el tamaño máximo de {settings.MAX_IMAGE_SIZE_MB} MB")
        )

    if content_type not in settings.ALLOWED_IMAGE_MIME_TYPES:
        raise ImageValidationError(
            message=f"Tipo de imagen no permitido: {content_type or 'desconocido'}"
        )


def read_upload_safely(file: BinaryIO) -> bytes:
    """Lee el archivo respetando el límite de tamaño."""
    content = file.read(settings.max_image_size_bytes + 1)
    if len(content) > settings.max_image_size_bytes:
        raise ImageValidationError(
            message=f"La imagen supera el tamaño máximo de {settings.MAX_IMAGE_SIZE_MB} MB"
        )
    return content


def sanitize_filename(filename: str | None) -> str:
    """Sanitiza un nombre de archivo para usarlo como referencia (nunca como ruta)."""
    if not filename:
        return "upload"
    cleaned = _SAFE_FILENAME.sub("_", filename).strip(" ._")
    return cleaned or "upload"
