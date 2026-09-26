"""Modelos ORM de la base de datos."""

from app.models.base import Base
from app.models.ingredient import Ingredient
from app.models.nestle_product import NestleProduct
from app.models.recipe import (
    Nutrition,
    Recipe,
    RecipeEmbedding,
    RecipeIngredient,
    RecipeNestleProduct,
    RecipeSource,
)
from app.models.scan import DetectedIngredient, Scan
from app.models.user import User
from app.models.user_preference import UserPreference

__all__ = [
    "Base",
    "Ingredient",
    "NestleProduct",
    "Nutrition",
    "Recipe",
    "RecipeEmbedding",
    "RecipeIngredient",
    "RecipeNestleProduct",
    "RecipeSource",
    "Scan",
    "DetectedIngredient",
    "User",
    "UserPreference",
]
