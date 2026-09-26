"""Lógica pura de dominio de recetas (sin IO)."""

from app.recipes.matcher import match
from app.recipes.ranker import rank

__all__ = ["match", "rank"]
