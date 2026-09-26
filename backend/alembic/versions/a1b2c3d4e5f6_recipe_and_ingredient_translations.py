"""tablas traducciones: recipe_translations e ingredient_translations

Revision ID: a1b2c3d4e5f6
Revises: 3b2f9c41a7d0
Create Date: 2026-09-24 20:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '3b2f9c41a7d0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "recipe_translations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("recipe_id", sa.Integer(), sa.ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("lang", sa.String(length=5), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("category", sa.String(length=100), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("steps", sa.JSON(), nullable=True),
        sa.UniqueConstraint("recipe_id", "lang", name="uq_recipe_translations_recipe_lang"),
    )
    op.create_index(
        "ix_recipe_translations_recipe_id", "recipe_translations", ["recipe_id"]
    )

    op.create_table(
        "ingredient_translations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("ingredient_id", sa.Integer(), sa.ForeignKey("ingredients.id", ondelete="CASCADE"), nullable=False),
        sa.Column("lang", sa.String(length=5), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.UniqueConstraint("ingredient_id", "lang", name="uq_ingredient_translations_ingredient_lang"),
    )
    op.create_index(
        "ix_ingredient_translations_ingredient_id", "ingredient_translations", ["ingredient_id"]
    )


def downgrade() -> None:
    op.drop_index("ix_ingredient_translations_ingredient_id", table_name="ingredient_translations")
    op.drop_table("ingredient_translations")
    op.drop_index("ix_recipe_translations_recipe_id", table_name="recipe_translations")
    op.drop_table("recipe_translations")