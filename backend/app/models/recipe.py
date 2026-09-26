"""Recetas, ingredientes asociados, fuentes, nutrición y embeddings RAG."""

import enum
from typing import TYPE_CHECKING

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    JSON,
    Boolean,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.ingredient import Ingredient
    from app.models.nestle_product import NestleProduct


class RecipeType(enum.StrEnum):
    TRADITIONAL = "traditional"
    AI_GENERATED = "ai_generated"
    AI_ADAPTED = "ai_adapted"
    SIMPLE = "simple"
    POSTRE = "postre"


class Recipe(TimestampMixin, Base):
    __tablename__ = "recipes"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    country: Mapped[str] = mapped_column(String(100), default="Panamá", index=True)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    preparation_time_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    servings: Mapped[int] = mapped_column(Integer, default=2)
    source: Mapped[str] = mapped_column(String(255), default="Recetario Nuestro Sabor Panamá")
    type: Mapped[RecipeType] = mapped_column(
        Enum(RecipeType, name="recipe_type"),
        default=RecipeType.TRADITIONAL,
        nullable=False,
        index=True,
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    preparation_steps: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    difficulty: Mapped[str | None] = mapped_column(String(50), nullable=True)
    panama_verified: Mapped[bool] = mapped_column(Boolean, default=True)
    source_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    search_keywords: Mapped[str | None] = mapped_column(Text, nullable=True)

    recipe_ingredients: Mapped[list["RecipeIngredient"]] = relationship(
        back_populates="recipe",
        cascade="all, delete-orphan",
    )
    nestle_products: Mapped[list["RecipeNestleProduct"]] = relationship(
        back_populates="recipe",
        cascade="all, delete-orphan",
    )
    sources: Mapped[list["RecipeSource"]] = relationship(
        back_populates="recipe",
        cascade="all, delete-orphan",
    )
    nutrition: Mapped["Nutrition | None"] = relationship(
        back_populates="recipe",
        uselist=False,
        cascade="all, delete-orphan",
    )
    embeddings: Mapped[list["RecipeEmbedding"]] = relationship(
        back_populates="recipe",
        cascade="all, delete-orphan",
    )
    translations: Mapped[list["RecipeTranslation"]] = relationship(
        back_populates="recipe",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Recipe id={self.id} name={self.name!r} type={self.type.value}>"


class RecipeTranslation(Base):
    __tablename__ = "recipe_translations"
    __table_args__ = (
        UniqueConstraint("recipe_id", "lang", name="uq_recipe_translations_recipe_lang"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id", ondelete="CASCADE"), index=True)
    lang: Mapped[str] = mapped_column(String(5), nullable=False)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    steps: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)

    recipe: Mapped["Recipe"] = relationship(back_populates="translations")


class RecipeIngredient(Base):
    __tablename__ = "recipe_ingredients"

    id: Mapped[int] = mapped_column(primary_key=True)
    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id", ondelete="CASCADE"), index=True)
    ingredient_id: Mapped[int] = mapped_column(
        ForeignKey("ingredients.id", ondelete="RESTRICT"), index=True
    )
    quantity: Mapped[str | None] = mapped_column(String(50), nullable=True)
    unit: Mapped[str | None] = mapped_column(String(50), nullable=True)
    is_optional: Mapped[bool] = mapped_column(Boolean, default=False)

    recipe: Mapped["Recipe"] = relationship(back_populates="recipe_ingredients")
    ingredient: Mapped["Ingredient"] = relationship()


class RecipeSource(Base):
    __tablename__ = "recipe_sources"

    id: Mapped[int] = mapped_column(primary_key=True)
    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id", ondelete="CASCADE"), index=True)
    document_name: Mapped[str] = mapped_column(String(255), nullable=False)
    page_or_section: Mapped[str | None] = mapped_column(String(100), nullable=True)
    raw_text_reference: Mapped[str | None] = mapped_column(Text, nullable=True)

    recipe: Mapped["Recipe"] = relationship(back_populates="sources")


class RecipeNestleProduct(Base):
    __tablename__ = "recipe_nestle_products"

    id: Mapped[int] = mapped_column(primary_key=True)
    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id", ondelete="CASCADE"), index=True)
    nestle_product_id: Mapped[int] = mapped_column(
        ForeignKey("nestle_products.id", ondelete="RESTRICT"), index=True
    )
    usage_note: Mapped[str | None] = mapped_column(String(255), nullable=True)

    recipe: Mapped["Recipe"] = relationship(back_populates="nestle_products")
    nestle_product: Mapped["NestleProduct"] = relationship()


class Nutrition(Base):
    __tablename__ = "nutrition"

    id: Mapped[int] = mapped_column(primary_key=True)
    recipe_id: Mapped[int] = mapped_column(
        ForeignKey("recipes.id", ondelete="CASCADE"), unique=True, index=True
    )
    calories: Mapped[float | None] = mapped_column(Float, nullable=True)
    protein_g: Mapped[float | None] = mapped_column(Float, nullable=True)
    carbs_g: Mapped[float | None] = mapped_column(Float, nullable=True)
    fat_g: Mapped[float | None] = mapped_column(Float, nullable=True)
    fiber_g: Mapped[float | None] = mapped_column(Float, nullable=True)
    per_serving: Mapped[bool] = mapped_column(Boolean, default=True)
    is_estimated: Mapped[bool] = mapped_column(Boolean, default=True)
    source: Mapped[str | None] = mapped_column(String(255), nullable=True)

    recipe: Mapped["Recipe"] = relationship(back_populates="nutrition")


class RecipeEmbedding(Base):
    __tablename__ = "recipe_embeddings"
    __table_args__ = (
        Index(
            "ix_recipe_embeddings_vector",
            "embedding",
            postgresql_using="hnsw",
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id", ondelete="CASCADE"), index=True)
    embedding = mapped_column(Vector(768), nullable=False)
    chunk_text: Mapped[str] = mapped_column(Text, nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, default=0)

    recipe: Mapped["Recipe"] = relationship(back_populates="embeddings")
