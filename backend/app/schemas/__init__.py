"""Contratos Pydantic de entrada/salida de la API."""

from app.schemas.common import Envelope, ErrorResponse, PaginationMeta
from app.schemas.ingredient import ConfirmIngredientsRequest, ConfirmIngredientsResponse
from app.schemas.nutrition import NutritionFacts
from app.schemas.recipe import (
    RecipeDetail,
    RecipeGenerateRequest,
    RecipeGenerateResponse,
    RecipeSearchRequest,
    RecipeSearchResponse,
    RecipeSummary,
)
from app.schemas.scan import DetectedIngredientOut, ScanResponse

__all__ = [
    "ConfirmIngredientsRequest",
    "ConfirmIngredientsResponse",
    "DetectedIngredientOut",
    "ErrorResponse",
    "Envelope",
    "NutritionFacts",
    "PaginationMeta",
    "RecipeDetail",
    "RecipeGenerateRequest",
    "RecipeGenerateResponse",
    "RecipeSearchRequest",
    "RecipeSearchResponse",
    "RecipeSummary",
    "ScanResponse",
]
