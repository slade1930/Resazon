"""Contractos de confirmación de ingredientes detectados."""

from pydantic import BaseModel, Field

from app.schemas.scan import DetectedIngredientOut


class ConfirmIngredientsRequest(BaseModel):
    scan_id: int
    ingredients: list[DetectedIngredientOut] = Field(min_length=1)


class ConfirmIngredientsResponse(BaseModel):
    scan_id: int
    confirmed: list[str]
