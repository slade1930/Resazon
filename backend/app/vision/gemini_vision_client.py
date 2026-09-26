"""Cliente de Gemini Vision: imagen → ingredientes candidatos + normalización."""

from app.ai.gemini_client import gemini_client_provider, GeminiResponse
from app.schemas.scan import DetectedIngredientOut


class GeminiVisionClient:
    """Envía una imagen a Gemini Vision y normaliza los ingredientes."""

    def detect_ingredients(self, image_bytes: bytes, mime_type: str) -> list[DetectedIngredientOut]:
        response = gemini_client_provider().detect_ingredients_with_usage(image_bytes, mime_type)
        return response.data

    def detect_ingredients_with_usage(self, image_bytes: bytes, mime_type: str) -> GeminiResponse:
        return gemini_client_provider().detect_ingredients_with_usage(image_bytes, mime_type)
