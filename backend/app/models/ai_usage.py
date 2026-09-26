"""Modelos para rate limiting y cost tracking de IA."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User


class AIUsageLog(TimestampMixin, Base):
    """Registro de uso de IA para cost tracking."""

    __tablename__ = "ai_usage_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    session_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    operation_type: Mapped[str] = mapped_column(String(32), nullable=False)  # "image_analysis", "healthy_generation", "recipe_generation"
    model_used: Mapped[str] = mapped_column(String(64), nullable=False)
    input_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    output_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    estimated_cost_usd: Mapped[float | None] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="success")  # "success", "error", "rate_limited"
    error_message: Mapped[str | None] = mapped_column(String(500), nullable=True)

    user: Mapped["User | None"] = relationship(back_populates="ai_usage_logs")


class UserDailyLimit(TimestampMixin, Base):
    """Límites diarios por usuario/sesión."""

    __tablename__ = "user_daily_limits"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True
    )
    session_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now().replace(hour=0, minute=0, second=0, microsecond=0), index=True)
    image_analyses_count: Mapped[int] = mapped_column(Integer, default=0)
    healthy_generations_count: Mapped[int] = mapped_column(Integer, default=0)
    total_ai_requests: Mapped[int] = mapped_column(Integer, default=0)

    user: Mapped["User | None"] = relationship(back_populates="daily_limits")

    __table_args__ = (
        # Un registro por usuario/sesión por día
    )