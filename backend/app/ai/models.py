"""Modelos Pydantic de salida estructurada generada por Gemini."""

from typing import Literal

from pydantic import BaseModel, Field


class GeneratedIngredient(BaseModel):
    name: str
    quantity: str | None = None
    unit: str | None = None


class GeneratedRecipe(BaseModel):
    name: str
    ingredients: list[GeneratedIngredient] = Field(min_length=1)
    steps: list[str] = Field(min_length=1)
    preparation_time_minutes: int | None = None
    servings: int = Field(default=2, ge=1)
    tips: list[str] = Field(default=list)


class GeneratedVariant(BaseModel):
    """Versión generada o adaptada que además transporta su origen."""

    recipe: GeneratedRecipe
    origin: Literal["generated", "adapted"] = "generated"
