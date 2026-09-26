"""Información nutricional."""

from pydantic import BaseModel

NUTRITION_DISCLAIMER = (
    "Valores nutricionales estimados y calculados con heurísticas simples. "
    "No constituyen consejo médico ni diagnóstico."
)


class NutritionFacts(BaseModel):
    calories: float | None = None
    protein_g: float | None = None
    carbs_g: float | None = None
    fat_g: float | None = None
    fiber_g: float | None = None
    per_serving: bool = True
    is_estimated: bool = True
    source: str | None = None
    disclaimer: str | None = NUTRITION_DISCLAIMER
