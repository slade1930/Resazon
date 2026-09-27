"""Cliente único y genérico hacia Gemini (texto + visión)."""

import json
import re
import time
from collections.abc import Callable
from dataclasses import dataclass
from functools import lru_cache
from typing import TypeVar

from google import genai
from google.genai import types

from app.core.config import settings
from app.core.exceptions import AINotConfiguredError, UpstreamAIError
from app.vision.schemas import DetectedIngredient, IngredientsResponse

T = TypeVar("T")


@dataclass
class GeminiResponse:
    """Respuesta de Gemini con metadatos de uso."""
    data: T
    input_tokens: int | None = None
    output_tokens: int | None = None
    model_used: str | None = None


_RETRIES_PER_MODEL = 2
_RETRY_DELAYS = (1.0, 3.0)


def _is_transient_saturation(exc: Exception) -> bool:
    """503/429 por saturación ('high demand', UNAVAILABLE, RESOURCE_EXHAUSTED, rate limit)."""
    text = str(exc).lower()
    markers = ("503", "429", "unavailable", "resource_exhausted", "high demand", "rate limit")
    return any(m in text for m in markers)


def _build_error(*attempts: Exception | None) -> UpstreamAIError:
    seen = {str(exc)[:160] for exc in attempts if exc}
    detail = " | ".join(seen) if seen else "sin detalles"
    return UpstreamAIError(message=detail)


def _extract_usage(response: types.GenerateContentResponse) -> tuple[int | None, int | None]:
    """Extrae tokens de uso del response."""
    if hasattr(response, 'usage_metadata') and response.usage_metadata:
        input_tokens = getattr(response.usage_metadata, 'prompt_token_count', None)
        output_tokens = getattr(response.usage_metadata, 'candidates_token_count', None)
        return input_tokens, output_tokens
    return None, None


class GeminiClient:
    """Wrapper sobre google-genai. No expone nada del SDK al resto del código."""

    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        self.api_key = api_key or settings.GEMINI_API_KEY
        primary = model or settings.GEMINI_MODEL
        self.models = [primary, *(m for m in settings.GEMINI_FALLBACK_MODELS if m != primary)]
        if not settings.GEMINI_AI_ENABLED:
            raise AINotConfiguredError(
                "IA desactivada: define GEMINI_AI_ENABLED=true en backend/.env para activarla."
            )
        if not self.api_key:
            raise AINotConfiguredError("GEMINI_API_KEY no está definida en backend/.env")
        self.client = genai.Client(api_key=self.api_key)

    def _with_fallback(self, caller: Callable[[str], tuple[T, types.GenerateContentResponse]]) -> tuple[T, types.GenerateContentResponse]:
        """Reintenta cada modelo ante 503/429 de saturación; si se agotan, prueba el siguiente."""
        attempts: list[Exception | None] = []
        for model in self.models:
            for attempt in range(_RETRIES_PER_MODEL):
                try:
                    return caller(model)
                except Exception as exc:  # noqa: BLE001 - el SDK lanza excepciones variadas
                    attempts.append(exc)
                    if not _is_transient_saturation(exc) or attempt == _RETRIES_PER_MODEL - 1:
                        break
                    time.sleep(_RETRY_DELAYS[attempt])
        raise _build_error(*attempts)

    def generate_content(self, prompt: str, temperature: float = 0.7) -> str:
        def call(model: str) -> tuple[str, types.GenerateContentResponse]:
            response = self.client.models.generate_content(
                model=model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=temperature,
                    max_output_tokens=settings.GEMINI_OUTPUT_TOKENS,
                ),
            )
            if not response.text:
                raise UpstreamAIError(message="Gemini devolvió una respuesta vacía", details=response)
            return response.text, response

        text, _ = self._with_fallback(call)
        return text

    def generate_content_with_usage(self, prompt: str, temperature: float = 0.7) -> GeminiResponse:
        def call(model: str) -> tuple[str, types.GenerateContentResponse]:
            response = self.client.models.generate_content(
                model=model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=temperature,
                    max_output_tokens=settings.GEMINI_OUTPUT_TOKENS,
                ),
            )
            if not response.text:
                raise UpstreamAIError(message="Gemini devolvió una respuesta vacía", details=response)
            return response.text, response

        text, response = self._with_fallback(call)
        input_tokens, output_tokens = _extract_usage(response)
        return GeminiResponse(data=text, input_tokens=input_tokens, output_tokens=output_tokens, model_used=response.model_version if hasattr(response, 'model_version') else None)

    def detect_ingredients(self, image_bytes: bytes, mime_type: str) -> IngredientsResponse:
        """Envía una imagen a Gemini Vision y pide ingredientes candidatos."""
        prompt = _VISION_PROMPT

        def call(model: str) -> tuple[IngredientsResponse, types.GenerateContentResponse]:
            response = self.client.models.generate_content(
                model=model,
                contents=[
                    types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                    prompt,
                ],
                config=types.GenerateContentConfig(
                    temperature=0.2,
                    max_output_tokens=676,
                    response_mime_type="application/json",
                ),
            )
            if not response.text:
                raise UpstreamAIError(message="Gemini Vision devolvió una respuesta vacía")
            return _parse_ingredients_response(response.text), response

        raw, _ = self._with_fallback(call)
        return raw

    def detect_ingredients_with_usage(self, image_bytes: bytes, mime_type: str) -> GeminiResponse:
        """Envía una imagen a Gemini Vision y retorna ingredientes + metadatos de uso."""
        prompt = _VISION_PROMPT

        def call(model: str) -> tuple[IngredientsResponse, types.GenerateContentResponse]:
            response = self.client.models.generate_content(
                model=model,
                contents=[
                    types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                    prompt,
                ],
                config=types.GenerateContentConfig(
                    temperature=0.2,
                    max_output_tokens=676,
                    response_mime_type="application/json",
                ),
            )
            if not response.text:
                raise UpstreamAIError(message="Gemini Vision devolvió una respuesta vacía")
            return _parse_ingredients_response(response.text), response

        raw, response = self._with_fallback(call)
        input_tokens, output_tokens = _extract_usage(response)

        from app.vision.ingredient_normalizer import normalize_ingredient
        from app.schemas.scan import DetectedIngredientOut

        normalized_results: list[DetectedIngredientOut] = []
        for item in raw.ingredients:
            normalized = normalize_ingredient(item.name)
            if not normalized:
                continue
            normalized_results.append(
                DetectedIngredientOut(
                    name=normalized,
                    confidence=item.confidence,
                )
            )

        return GeminiResponse(
            data=normalized_results,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            model_used=response.model_version if hasattr(response, 'model_version') else None
        )

    def generate_embeddings(self, texts: list[str], model: str | None = None) -> list[list[float]]:
        embedding_model = model or settings.GEMINI_EMBEDDING_MODEL
        try:
            response = self.client.models.embed_content(
                model=embedding_model,
                contents=texts,
                config=types.EmbedContentConfig(
                    output_dimensionality=settings.GEMINI_EMBEDDING_DIM,
                ),
            )
        except Exception as exc:  # noqa: BLE001
            raise UpstreamAIError(message=f"Gemini no pudo generar embeddings: {exc}") from exc

        if not response.embeddings:
            raise UpstreamAIError(message="Gemini devolvió embeddings vacíos")
        return [emb.values for emb in response.embeddings]


def _strip_code_fence(text: str) -> str:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned[3:]
        if cleaned.startswith("json"):
            cleaned = cleaned[4:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
    return cleaned.strip()


def _coerce_ingredient_name(value: object) -> str:
    if isinstance(value, str):
        return re.sub(r"\s+", " ", value.strip())[:80]
    return ""


def _coerce_ingredient_confidence(value: object) -> float:
    try:
        conf = float(value)
    except (TypeError, ValueError):
        return 0.5
    return min(1.0, max(0.0, conf))


def _parse_ingredients_response(raw_text: str) -> IngredientsResponse:
    """Parsea la respuesta de Gemini Vision de forma tolerante.

    1) Intenta el esquema estricto (pydantic). 2) Si falla, extrae la lista de
    ingredientes a mano (soporta claves en español y valores sucios). 3) Ante
    una respuesta inutilizable devuelve lista vacía. NUNCA lanza: así ninguna
    foto (lata, etiqueta, etc.) provoca un error 500.
    """
    text = _strip_code_fence(raw_text or "")
    if not text:
        return IngredientsResponse(ingredients=[])

    try:
        return IngredientsResponse.model_validate_json(text)
    except Exception:  # noqa: BLE001 - validación estricta; seguimos tolerante
        pass

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end <= start:
            return IngredientsResponse(ingredients=[])
        try:
            data = json.loads(text[start : end + 1])
        except json.JSONDecodeError:
            return IngredientsResponse(ingredients=[])

    if not isinstance(data, dict):
        return IngredientsResponse(ingredients=[])

    for key in ("ingredients", "ingredientes", "alimentos", "items", "detected"):
        raw = data.get(key)
        if not isinstance(raw, list):
            continue
        items: list[DetectedIngredient] = []
        for entry in raw:
            if isinstance(entry, str):
                name, conf = entry, 0.5
            elif isinstance(entry, dict):
                name = entry.get("name") or entry.get("nombre")
                conf = entry.get("confidence") if entry.get("confidence") is not None else entry.get("confianza")
            else:
                continue
            name = _coerce_ingredient_name(name)
            if name:
                items.append(DetectedIngredient(name=name, confidence=_coerce_ingredient_confidence(conf)))
        if items:
            return IngredientsResponse(ingredients=items)

    return IngredientsResponse(ingredients=[])


def ai_available() -> bool:
    return settings.GEMINI_AI_ENABLED and bool(settings.GEMINI_API_KEY)


@lru_cache
def get_gemini_client() -> GeminiClient:
    return GeminiClient()


gemini_client_provider = get_gemini_client


_VISION_PROMPT = """Eres un asistente de cocina panameña. Analiza SOLO los alimentos que son VISIBLES en la fotografía.

Reglas estrictas:
- Devuelve EXCLUSIVAMENTE JSON con este esquema exacto (sin texto adicional):
{"ingredients": [{"name": "string", "confidence": 0.0-1.0}]}
- Detecta solo alimentos reales visibles: arroz, pollo, tomate, plátano, yuca, etc.
- Identifica el OBJETO y su TIPO específico: si ves un empaque (lata, tarro, caja, tetra pak, bolsa, sobre), di qué es el ingrediente real que contiene, leyendo la etiqueta. Ejemplos:
  - lata de leche condensada → "leche condensada"
  - lata de leche evaporada → "leche evaporada"
  - cartón de leche → "leche"
  - bote de crema → "crema de leche"
  - paquete/bolsa de harina → "harina"
  - bolsa de maíz → "maíz"
- Nombres simples en español de Panamá, en singular (ej: "ají", "arroz", "yuca", "plátano", "pescado", "leche condensada").
- IGNORA platos, vasos, cubiertos, bolsas, mesas, sillas, manos, texto no relacionado con comida.
- NO inventes ni asumas ingredientes ocultos/posibles: solo lo que realmente ves. Un empaque cerrado o sin etiqueta legible NO cuenta como ingrediente.
- confidence ≥ 0.7 solo si es indudable; 0.5-0.7 si es probable; NO incluyas dudosos (< 0.5).
- Máximo 10 ingredientes.
- Si la imagen no muestra alimentos con suficiente seguridad, devuelve {"ingredients": []}."""


def get_vision_prompt() -> str:
    return _VISION_PROMPT
