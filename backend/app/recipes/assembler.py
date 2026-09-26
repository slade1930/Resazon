"""Ensambla el objeto final de receta (resumen y detalle)."""

from app.ai.models import GeneratedRecipe
from app.i18n import (
    ingredient_name,
    recipe_category,
    recipe_name,
    recipe_steps,
    unit_name,
)
from app.models.recipe import Recipe
from app.recipes.matcher import MatchResult
from app.schemas.nutrition import NutritionFacts
from app.schemas.recipe import (
    RecipeDetail,
    RecipeIngredientOut,
    RecipeSummary,
)
from app.vision.ingredient_normalizer import normalize_ingredient


def _nestle_names(recipe: Recipe) -> list[str]:
    return [link.nestle_product.name for link in recipe.nestle_products]


def _type_value(value) -> str:
    return value.value if hasattr(value, "value") else value


def build_summary(recipe: Recipe, match_result: MatchResult, lang: str | None = None) -> RecipeSummary:
    return RecipeSummary(
        id=recipe.id,
        name=recipe_name(recipe, lang),
        category=recipe_category(recipe, lang),
        match_percentage=match_result.match_percentage,
        available_ingredients=match_result.available_ingredients,
        missing_ingredients=match_result.missing_ingredients,
        preparation_time_minutes=recipe.preparation_time_minutes,
        servings=recipe.servings,
        source=recipe.source,
        type=_type_value(recipe.type),
        difficulty=recipe.difficulty,
        panama_verified=recipe.panama_verified,
        nestle_products=_nestle_names(recipe),
    )


def build_detail(recipe: Recipe, lang: str | None = None) -> RecipeDetail:
    ingredients = [
        RecipeIngredientOut(
            name=ingredient_name(link.ingredient, lang),
            quantity=link.quantity,
            unit=unit_name(link.unit, lang),
            is_optional=link.is_optional,
        )
        for link in recipe.recipe_ingredients
    ]
    nutrition = None
    if recipe.nutrition:
        nutrition = NutritionFacts(
            calories=recipe.nutrition.calories,
            protein_g=recipe.nutrition.protein_g,
            carbs_g=recipe.nutrition.carbs_g,
            fat_g=recipe.nutrition.fat_g,
            fiber_g=recipe.nutrition.fiber_g,
            per_serving=recipe.nutrition.per_serving,
            is_estimated=recipe.nutrition.is_estimated,
            source=recipe.nutrition.source,
        )
    translated_steps = recipe_steps(recipe, lang)
    steps = recipe.preparation_steps or translated_steps
    if not steps and recipe.sources:
        steps = [
            line.strip()
            for line in (recipe.sources[0].raw_text_reference or "").split("\n")
            if line.strip()
        ]
    return RecipeDetail(
        name=recipe_name(recipe, lang),
        category=recipe_category(recipe, lang),
        ingredients=ingredients,
        steps=steps,
        preparation_time_minutes=recipe.preparation_time_minutes,
        servings=recipe.servings,
        type=_type_value(recipe.type),
        source=recipe.source,
        difficulty=recipe.difficulty,
        panama_verified=recipe.panama_verified,
        source_url=recipe.source_url,
        description=recipe.description,
        nutrition=nutrition,
        nestle_products=_nestle_names(recipe),
    )


def build_generated_detail(
    generated: GeneratedRecipe,
    *,
    recipe_type: str,
    source: str,
    nutrition: NutritionFacts | None = None,
) -> RecipeDetail:
    ingredients = [
        RecipeIngredientOut(
            name=ing.name.strip(),
            quantity=ing.quantity,
            unit=ing.unit,
        )
        for ing in generated.ingredients
    ]
    return RecipeDetail(
        name=generated.name,
        ingredients=ingredients,
        steps=generated.steps,
        preparation_time_minutes=generated.preparation_time_minutes,
        servings=generated.servings,
        type=recipe_type,
        source=source,
        nutrition=nutrition,
        nestle_products=[],
    )


def try_normalize(name: str) -> str:
    return normalize_ingredient(name) or name.lower()
