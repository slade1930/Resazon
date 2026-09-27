"""Contractos de escaneo de imagen."""

from pydantic import BaseModel, Field

from app.schemas.recipe import RecipeSummary


class DetectedIngredientOut(BaseModel):
    name: str
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)


class ScanResponse(BaseModel):
    scan_id: int
    detected_ingredients: list[DetectedIngredientOut]
    traditional_recipes: list[RecipeSummary] = Field(default=list)
    transcript: str | None = None
