"""Ingredientes del dominio."""

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.recipe import RecipeIngredient


class Ingredient(Base):
    __tablename__ = "ingredients"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    normalized_name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)

    recipe_links: Mapped[list["RecipeIngredient"]] = relationship(back_populates="ingredient")
    translations: Mapped[list["IngredientTranslation"]] = relationship(
        back_populates="ingredient",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Ingredient id={self.id} name={self.name!r}>"


class IngredientTranslation(Base):
    __tablename__ = "ingredient_translations"
    __table_args__ = (
        UniqueConstraint("ingredient_id", "lang", name="uq_ingredient_translations_ingredient_lang"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    ingredient_id: Mapped[int] = mapped_column(
        ForeignKey("ingredients.id", ondelete="CASCADE"), index=True
    )
    lang: Mapped[str] = mapped_column(String(5), nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)

    ingredient: Mapped["Ingredient"] = relationship(back_populates="translations")
