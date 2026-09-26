"""Contractos de escaneo de imagen."""

from pydantic import BaseModel, Field


class DetectedIngredientOut(BaseModel):
    name: str
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)


class ScanResponse(BaseModel):
    scan_id: int
    detected_ingredients: list[DetectedIngredientOut]
