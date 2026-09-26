"""Cliente de Gemini Vision: imagen → ingredientes candidatos + normalización."""

from app.ai.gemini_client import gemini_client_provider
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
