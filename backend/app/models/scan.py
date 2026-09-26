"""Escaneos de imagen y detección de ingredientes."""

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User


class Scan(TimestampMixin, Base):
    __tablename__ = "scans"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    image_reference: Mapped[str | None] = mapped_column(String(255), nullable=True)

    user: Mapped["User | None"] = relationship(back_populates="scans")
    detected_ingredients: Mapped[list["DetectedIngredient"]] = relationship(
        back_populates="scan",
        cascade="all, delete-orphan",
    )


class DetectedIngredient(Base):
    __tablename__ = "detected_ingredients"

    id: Mapped[int] = mapped_column(primary_key=True)
    scan_id: Mapped[int] = mapped_column(ForeignKey("scans.id", ondelete="CASCADE"), index=True)
    ingredient_name_raw: Mapped[str] = mapped_column(String(150), nullable=False)
    normalized_name: Mapped[str | None] = mapped_column(String(150), nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    was_confirmed: Mapped[bool] = mapped_column(Boolean, default=False)
    was_edited: Mapped[bool] = mapped_column(Boolean, default=False)

    scan: Mapped["Scan"] = relationship(back_populates="detected_ingredients")
