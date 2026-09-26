"""Parseo y validación de salidas estructuradas de Gemini."""

import json
import re
from typing import TypeVar

from pydantic import BaseModel, ValidationError

from app.core.exceptions import AIResponseError

T = TypeVar("T", bound=BaseModel)

_CODE_FENCE_RE = re.compile(r"^```(?:json)?\s*|\s*```$", re.MULTILINE)


def extract_json_block(text: str) -> dict:
    """Extrae el primer objeto JSON de una respuesta que puede traer texto extra."""
    cleaned = _CODE_FENCE_RE.sub("", text or "").strip()

    # Intento directo primero.
    try:
        parsed = json.loads(cleaned)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        pass

    # Buscar el bloque { ... } mejor balanceado.
    start = cleaned.find("{")
    if start == -1:
        raise AIResponseError(message="La IA no devolvió un objeto JSON")

    depth = 0
    in_string = False
    escape = False
    for i in range(start, len(cleaned)):
        ch = cleaned[i]
        if in_string:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
            continue
        if ch == '"':
            in_string = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                block = cleaned[start : i + 1]
                try:
                    parsed = json.loads(block)
                    if isinstance(parsed, dict):
                        return parsed
                    raise AIResponseError(message="El bloque JSON no es un objeto")
                except json.JSONDecodeError as exc:
                    raise AIResponseError(
                        message="La IA devolvió JSON malformado", details=str(exc)
                    ) from exc

    raise AIResponseError(message="No se encontró un objeto JSON válido en la respuesta")


def parse_json_model(text: str, model: type[T]) -> T:
    """Convierte la respuesta de texto de Gemini en un modelo Pydantic validado."""
    try:
        data = extract_json_block(text)
        return model.model_validate(data)
    except AIResponseError:
        raise
    except ValidationError as exc:
        raise AIResponseError(
            message="La IA devolvió un JSON que no cumple el contrato esperado",
            details=exc.errors(),
        ) from exc
