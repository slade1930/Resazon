"""Acceso a datos de ingredientes."""

import unicodedata

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.ingredient import Ingredient


class IngredientRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_normalized(self, normalized_name: str) -> Ingredient | None:
        return self.db.execute(
            select(Ingredient).where(Ingredient.normalized_name == normalized_name)
        ).scalar_one_or_none()

    def get_or_create(self, name: str, normalized_name: str | None = None) -> Ingredient:
        name = unicodedata.normalize("NFKC", name.strip())
        key = name.casefold()
        existing = (
            self.db.execute(select(Ingredient).where(func.lower(Ingredient.name) == key))
            .scalars()
            .first()
        )
        if existing:
            return existing
        ingredient = Ingredient(name=name, normalized_name=normalized_name or key)
        self.db.add(ingredient)
        return ingredient

    def bulk_get_by_normalized(self, names: list[str]) -> dict[str, Ingredient]:
        if not names:
            return {}
        rows = list(
            self.db.execute(
                select(Ingredient).where(Ingredient.normalized_name.in_(names))
            ).scalars()
        )
        return {row.normalized_name: row for row in rows}
