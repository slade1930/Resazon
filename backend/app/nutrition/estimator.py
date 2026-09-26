"""Estimador heurístico de macros por ingrediente.

Es una aproximación gruesa por porción típica: cada ingrediente pesa un "valor
por unidad/pieza" razonable para plato panameño promedio. Todo se marca
is_estimated=True. Fuente verificable futura: campo Nutrition.source.
"""

from app.schemas.nutrition import NutritionFacts
from app.vision.ingredient_normalizer import strip_accents

# (kcal, proteína g, carbohidratos g, grasa g, fibra g) por "unidad típica".
MACROS_TABLE: dict[str, tuple[float, float, float, float, float]] = {
    "arroz": (150, 3.0, 33, 0.3, 0.6),
    "pollo": (165, 31, 0, 3.6, 0),
    "carne": (250, 26, 0, 17, 0),
    "cerdo": (242, 27, 0, 14, 0),
    "chancho": (242, 27, 0, 14, 0),
    "pescado": (120, 24, 0, 2, 0),
    "camaron": (99, 24, 0.2, 0.3, 0),
    "huevo": (72, 6, 0.6, 5, 0),
    "harina": (364, 10, 76, 1, 2.7),
    "harina de maiz": (361, 8, 76, 3.9, 7),
    "maiz": (96, 3.4, 21, 1.5, 2.4),
    "yuca": (160, 1.4, 38, 0.3, 1.8),
    "platan": (122, 1.3, 32, 0.2, 2.3),
    "papa": (77, 2, 17, 0.1, 2.2),
    "cebolla": (40, 1.1, 9.3, 0.1, 1.7),
    "aji": (18, 0.9, 4.2, 0.1, 1.5),
    "aji dulce": (18, 0.9, 4.2, 0.1, 1.5),
    "aj": (2, 0.1, 0.5, 0, 0),
    "tomate": (18, 0.9, 3.9, 0.2, 1.2),
    "culantro": (23, 2.1, 3.7, 0.5, 2.8),
    "aceite": (120, 0, 0, 13.6, 0),
    "mantequilla": (102, 0.1, 0, 11.5, 0),
    "leche": (42, 3.4, 5, 1, 0),
    "leche evaporada": (134, 6.8, 10, 7.6, 0),
    "leche condensada": (130, 3.2, 22, 3.3, 0),
    "azucar": (48, 0, 12, 0, 0),
    "sal": (0, 0, 0, 0, 0),
    "frijol": (127, 8.7, 22.8, 0.5, 6.5),
    "guandu": (116, 7.4, 21, 0.5, 5),
    "garbanzo": (164, 8.9, 27.4, 2.6, 7.6),
    "lenteja": (116, 9, 20, 0.4, 7.9),
    "mantequilla de mani": (94, 4, 3.2, 8, 1),
    "tortilla": (218, 5.7, 44, 2.2, 2.1),
    "pan": (265, 9, 49, 3.2, 2.7),
    "queso": (113, 7, 1, 9, 0),
    "crema": (51, 0.9, 0.9, 5, 0),
    "mayonesa": (68, 0.1, 0.1, 7.5, 0),
    "mostaza": (7, 0.4, 0.6, 0.4, 0.3),
    "platano maduro": (122, 1.3, 32, 0.2, 2.3),
    "espinaca": (23, 2.9, 3.6, 0.4, 2.2),
    "brocoli": (35, 2.4, 7, 0.4, 2.6),
    "zanahoria": (41, 0.9, 9.6, 0.2, 2.8),
    "pepino": (15, 0.7, 3.6, 0.1, 0.5),
    "calabacin": (17, 1.2, 3.1, 0.3, 1),
    "chayote": (19, 0.8, 4.5, 0.1, 1.7),
    "aguacate": (160, 2, 8.5, 14.7, 6.7),
    "coco": (354, 3.3, 15.2, 33.5, 9),
    "ñame": (118, 1.5, 28, 0.2, 4.1),
}

DEFAULT_MACROS = (80.0, 3.0, 10.0, 2.5, 1.5)


def _matched_macros(name: str) -> tuple[float, float, float, float, float]:
    key = strip_accents(name.lower().strip())
    # búsqueda por subcadena normalizada para "chicharrón de chancho"→cerdo
    for candidate in MACROS_TABLE:
        if key == candidate or candidate in key:
            value = MACROS_TABLE[candidate]
            if value is not None:
                return value
    return DEFAULT_MACROS


def estimate_macros(
    ingredient_names: list[str],
    servings: int = 2,
    source: str | None = None,
) -> NutritionFacts:
    """Suma la estimación por ingrediente y la expresa por porción."""
    total_cal = total_protein = total_carbs = total_fat = total_fiber = 0.0
    for name in ingredient_names:
        cal, protein, carbs, fat, fiber = _matched_macros(name)
        total_cal += cal
        total_protein += protein
        total_carbs += carbs
        total_fat += fat
        total_fiber += fiber

    servings = max(1, servings)
    return NutritionFacts(
        calories=round(total_cal / servings, 0),
        protein_g=round(total_protein / servings, 1),
        carbs_g=round(total_carbs / servings, 1),
        fat_g=round(total_fat / servings, 1),
        fiber_g=round(total_fiber / servings, 1),
        per_serving=True,
        is_estimated=True,
        source=source or "estimación heurística local",
    )
