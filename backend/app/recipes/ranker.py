"""Ordena resultados de búsqueda por relevancia."""

from app.schemas.recipe import RecipeSummary


def rank(recipes: list[RecipeSummary]) -> list[RecipeSummary]:
    """Ordena por: % de coincidencia, luego más disponibles, luego menos faltantes."""
    return sorted(
        recipes,
        key=lambda r: (
            r.match_percentage,
            len(r.available_ingredients),
            -len(r.missing_ingredients),
        ),
        reverse=True,
    )
