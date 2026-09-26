"""recipes: difficulty/panama_verified/source_url/search_keywords + new types

Revision ID: 3b2f9c41a7d0
Revises: 828dc779d19b
Create Date: 2026-09-24 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '3b2f9c41a7d0'
down_revision: Union[str, None] = '828dc779d19b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _add_enum_value(enum_type: str, value: str) -> None:
    """ADD VALUE idempotente para el enum recipe_type (PG12+ permite transacción)."""
    conn = op.get_bind()
    exists = conn.execute(
        sa.text(
            "SELECT 1 FROM pg_enum e JOIN pg_type t ON e.enumtypid = t.oid "
            "WHERE t.typname = :tname AND e.enumlabel = :label"
        ),
        {"tname": enum_type, "label": value},
    ).first()
    if not exists:
        conn.execute(sa.text(f"ALTER TYPE {enum_type} ADD VALUE '{value}'"))


def upgrade() -> None:
    op.add_column("recipes", sa.Column("difficulty", sa.String(length=50), nullable=True))
    op.add_column(
        "recipes",
        sa.Column("panama_verified", sa.Boolean(), server_default=sa.text("true"), nullable=False),
    )
    op.add_column("recipes", sa.Column("source_url", sa.String(length=500), nullable=True))
    op.add_column("recipes", sa.Column("search_keywords", sa.Text(), nullable=True))

    # Nuevos tipos: recetas "sencillas" (catálogo general) y postres.
    _add_enum_value("recipe_type", "SIMPLE")
    _add_enum_value("recipe_type", "POSTRE")


def downgrade() -> None:
    # Los valores enum no se pueden remover con ALTER TYPE en PG; se dejan
    # documentados. Se revierten columnas y el resto queda sin efecto.
    op.drop_column("recipes", "search_keywords")
    op.drop_column("recipes", "source_url")
    op.drop_column("recipes", "panama_verified")
    op.drop_column("recipes", "difficulty")