"""Acceso a datos de recetas."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models.ingredient import Ingredient
from app.models.recipe import Recipe, RecipeIngredient


class RecipeRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def _base_options(self):
        return (
            selectinload(Recipe.recipe_ingredients)
            .selectinload(RecipeIngredient.ingredient)
            .selectinload(Ingredient.translations),
            selectinload(Recipe.nestle_products).selectinload("*"),
            selectinload(Recipe.sources),
            selectinload(Recipe.nutrition),
            selectinload(Recipe.translations),
        )

    def get(self, recipe_id: int) -> Recipe | None:
        return self.db.get(Recipe, recipe_id)

    def get_full(self, recipe_id: int) -> Recipe | None:
        return self.db.execute(
            select(Recipe).where(Recipe.id == recipe_id).options(*self._base_options())
        ).scalar_one_or_none()

    def get_by_ids(self, ids: list[int]) -> list[Recipe]:
        if not ids:
            return []
        return list(
            self.db.execute(
                select(Recipe).where(Recipe.id.in_(ids)).options(*self._base_options())
            ).scalars()
        )

    def list_paginated(self, page: int, page_size: int) -> tuple[list[Recipe], int]:
        total = self.db.execute(select(func.count(Recipe.id))).scalar_one()
        rows = list(
            self.db.execute(
                select(Recipe)
                .options(*self._base_options())
                .order_by(Recipe.name.asc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            ).scalars()
        )
        return rows, total

    def add(self, recipe: Recipe) -> Recipe:
        self.db.add(recipe)
        return recipe

    def find_by_name_source(self, name: str, source: str) -> Recipe | None:
        return self.db.execute(
            select(Recipe).where(Recipe.name == name, Recipe.source == source)
        ).scalar_one_or_none()
