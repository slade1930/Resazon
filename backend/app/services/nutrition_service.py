"""Caso de uso: estimación nutricional."""

from app.nutrition.estimator import estimate_macros
from app.schemas.nutrition import NutritionFacts


class NutrientEstimator:
    """Puente entre la estimación (nutrition/) y los servicios (services/)."""

    def estimate(
        self,
        ingredient_names: list[str],
        servings: int = 2,
        source: str | None = None,
    ) -> NutritionFacts:
        return estimate_macros(ingredient_names, servings=servings, source=source)
