"""Productos Nestlé del recetario (MAGGI, IDEAL, Klim, NESTLÉ ¡Qué Rico!)."""

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.recipe import RecipeNestleProduct


class NestleProduct(Base):
    __tablename__ = "nestle_products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)

    recipe_links: Mapped[list["RecipeNestleProduct"]] = relationship(
        back_populates="nestle_product"
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<NestleProduct id={self.id} name={self.name!r}>"
