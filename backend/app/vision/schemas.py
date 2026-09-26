"""Schemas del módulo de visión."""

from pydantic import BaseModel, Field


class DetectedIngredient(BaseModel):
    name: str
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)


class IngredientsResponse(BaseModel):
    ingredients: list[DetectedIngredient]
