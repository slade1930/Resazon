"""Utilidades para manipular imágenes."""

from pathlib import Path

# Extensiones permitidas acorde a ALLOWED_IMAGE_MIME_TYPES del core.
EXT_TO_MIME: dict[str, str] = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
}


def guess_mime_from_path(path: str | Path) -> str | None:
    return EXT_TO_MIME.get(Path(path).suffix.lower())
