"""ingredient normalized_name not unique

Revision ID: 828dc779d19b
Revises: f72b0d8fcbc7
Create Date: 2026-09-23 19:17:38.054004

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '828dc779d19b'
down_revision: Union[str, None] = 'f72b0d8fcbc7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # El initial_schema creó ix_ingredients_normalized_name como UNIQUE.
    # El dedupe por nombre normalizado colapsaba ingredientes distintos
    # ("Consomé de Pollo MAGGI®" vs "Pechuga de pollo" → "pollo"). Ahora el
    # dedupe es por nombre exacto (casefold), así que el índice es no-unique.
    op.drop_index(op.f('ix_ingredients_normalized_name'), table_name='ingredients')
    op.create_index(op.f('ix_ingredients_normalized_name'), 'ingredients', ['normalized_name'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_ingredients_normalized_name'), table_name='ingredients')
    op.create_index(op.f('ix_ingredients_normalized_name'), 'ingredients', ['normalized_name'], unique=True)
