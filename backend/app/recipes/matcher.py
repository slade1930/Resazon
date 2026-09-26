"""Cálculo del % de coincidencia entre ingredientes del usuario y una receta."""

from dataclasses import dataclass, field
from difflib import SequenceMatcher

from app.vision.ingredient_normalizer import normalize_ingredient

FUZZY_THRESHOLD = 0.72


@dataclass
class MatchResult:
    match_percentage: float = 0.0
    available_ingredients: list[str] = field(default_factory=list)
    missing_ingredients: list[str] = field(default_factory=list)


def _normalize_many(names: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for name in names:
        norm = normalize_ingredient(name)
        if norm and norm not in seen:
            seen.add(norm)
            result.append(norm)
    return result


def _token_subset(a: str, b: str) -> bool:
    """True si los tokens de a son subconjunto de los de b (b más específico)."""
    ta = set(a.split())
    tb = set(b.split())
    return bool(ta) and ta <= tb


def match(user_ingredients: list[str], recipe_ingredients: list[str]) -> MatchResult:
    """Cruza los ingredientes del usuario contra los de la receta.

    - available: ingredientes coincidentes, con el nombre real de la receta.
    - missing: ingredientes de la receta que el usuario NO tiene.
    - match_percentage: % de ingredientes de la receta cubiertos por el usuario.
      Con fuzzy matching para tolerar sinónimos/errores tipográficos leves.
    """
    user_norm = _normalize_many(user_ingredients)
    recipe_pairs: list[tuple[str, str]] = []
    seen_norm: set[str] = set()
    for name in recipe_ingredients:
        norm = normalize_ingredient(name)
        if norm and norm not in seen_norm:
            seen_norm.add(norm)
            recipe_pairs.append((norm, name))
    recipe_norm = [norm for norm, _ in recipe_pairs]
    original_by_norm = {norm: original for norm, original in recipe_pairs}

    available: list[str] = []
    matched_recipe: set[str] = set()

    for u in user_norm:
        best_recipe: str | None = None
        best_ratio = 0.0
        for r in recipe_norm:
            if r == u:
                best_recipe, best_ratio = r, 1.0
                break
            if _token_subset(u, r) or _token_subset(r, u):
                # "cebolla" en "cebolla cortada finamente" → match directo.
                best_recipe, best_ratio = r, 0.85
                break
            ratio = SequenceMatcher(None, u, r).ratio()
            if ratio > best_ratio:
                best_recipe, best_ratio = r, ratio
        if best_recipe is not None and best_ratio >= FUZZY_THRESHOLD:
            available.append(original_by_norm[best_recipe])
            matched_recipe.add(best_recipe)

    missing = [original_by_norm[r] for r in recipe_norm if r not in matched_recipe]

    pct = round(100.0 * len(matched_recipe) / len(recipe_norm), 1) if recipe_norm else 0.0
    return MatchResult(
        match_percentage=pct,
        available_ingredients=available,
        missing_ingredients=missing,
    )
