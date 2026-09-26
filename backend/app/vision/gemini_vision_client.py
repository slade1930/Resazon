"""Cliente de Gemini Vision: imagen → ingredientes candidatos + normalización."""

from app.ai.gemini_client import gemini_client_provider, GeminiResponse
from app.schemas.scan import DetectedIngredientOut
from app.vision.ingredient_normalizer import normalize_ingredient
from app.vision.schemas import IngredientsResponse


class GeminiVisionClient:
    """Orquesta: envía la imagen a Gemini Vision y normaliza los nombres."""

    def detect_ingredients(self, image_bytes: bytes, mime_type: str) -> list[DetectedIngredientOut]:
        provider = gemini_client_provider()
        raw: IngredientsResponse = provider.detect_ingredients(image_bytes, mime_type)

        results: list[DetectedIngredientOut] = []
        for item in raw.ingredients:
            normalized = normalize_ingredient(item.name)
            if not normalized:
                continue
            results.append(
                DetectedIngredientOut(
                    name=normalized,
                    confidence=item.confidence,
                )
            )
        return results

    def detect_ingredients_with_usage(self, image_bytes: bytes, mime_type: str) -> GeminiResponse:
        """Detecta ingredientes y retorna metadatos de uso (tokens, modelo)."""
        provider = gemini_client_provider()
        response: GeminiResponse = provider.detect_ingredients_with_usage(image_bytes, mime_type)

        results: list[DetectedIngredientOut] = []
        if response.data:
            for item in response.data.ingredients:
                normalized = normalize_ingredient(item.name)
                if not normalized:
                    continue
                results.append(
                    DetectedIngredientOut(
                        name=normalized,
                        confidence=item.confidence,
                    )
                )

        # Retornar respuesta con ingredientes normalizados y metadatos de uso
        return GeminiResponse(
            data=response.data,
            input_tokens=response.input_tokens,
            output_tokens=response.output_tokens,
            model_used=response.model_used,
        )
