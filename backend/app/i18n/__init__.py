"""Localización del contenido de recetas (nombres, categorías, pasos, ingredientes, unidades)."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.ingredient import Ingredient
    from app.models.recipe import Recipe

DEFAULT_LANG = "es"
SUPPORTED_LANGS = ("es", "en", "fr")

# Unidades compartidas (texto libre en el modelo): es -> en/fr.
UNITS: dict[str, dict[str, str]] = {
    "Cucharadita": {"en": "teaspoon", "fr": "cuillère à café"},
    "cucharadita": {"en": "teaspoon", "fr": "cuillère à café"},
    "Cucharada": {"en": "tablespoon", "fr": "cuillère à soupe"},
    "cucharada": {"en": "tablespoon", "fr": "cuillère à soupe"},
    "cucharadas": {"en": "tablespoons", "fr": "cuillères à soupe"},
    "Libra": {"en": "lb", "fr": "lb"},
    "libra": {"en": "lb", "fr": "lb"},
    "libras": {"en": "lb", "fr": "lb"},
    "lb": {"en": "lb", "fr": "lb"},
    "Sobre": {"en": "packet", "fr": "sachet"},
    "sobre": {"en": "packet", "fr": "sachet"},
    "Taza": {"en": "cup", "fr": "tasse"},
    "taza": {"en": "cup", "fr": "tasse"},
    "Tazas": {"en": "cups", "fr": "tasses"},
    "tazas": {"en": "cups", "fr": "tasses"},
    "dientes": {"en": "cloves", "fr": "gousses"},
    "hojas": {"en": "leaves", "fr": "feuilles"},
    "lata": {"en": "can", "fr": "boîte"},
    "litro": {"en": "liter", "fr": "litre"},
    "litros": {"en": "liters", "fr": "litres"},
    "rebanadas": {"en": "slices", "fr": "tranches"},
}


def normalize_lang(lang: str | None) -> str:
    """Limpia el idioma solicitado; cae a español si es inválido o nulo."""
    if lang in SUPPORTED_LANGS:
        return lang
    return DEFAULT_LANG


def recipe_translation(recipe: Recipe, lang: str | None):
    """Devuelve la traducción de la receta para `lang`, o None (es / sin traducción)."""
    lang = normalize_lang(lang)
    if lang == DEFAULT_LANG:
        return None
    for translation in recipe.translations:
        if translation.lang == lang:
            return translation
    return None


def recipe_name(recipe: Recipe, lang: str | None) -> str:
    translation = recipe_translation(recipe, lang)
    if translation and translation.name:
        return translation.name
    return recipe.name


def recipe_category(recipe: Recipe, lang: str | None) -> str | None:
    translation = recipe_translation(recipe, lang)
    if translation and translation.category:
        return translation.category
    return recipe.category


def recipe_steps(recipe: Recipe, lang: str | None) -> list[str]:
    translation = recipe_translation(recipe, lang)
    if translation and translation.steps:
        return list(translation.steps)
    return []


def ingredient_name(ingredient: Ingredient, lang: str | None) -> str:
    lang = normalize_lang(lang)
    if lang == DEFAULT_LANG:
        return ingredient.name
    for translation in ingredient.translations:
        if translation.lang == lang and translation.name:
            return translation.name
    return ingredient.name


def unit_name(unit: str | None, lang: str | None) -> str | None:
    lang = normalize_lang(lang)
    if not unit or lang == DEFAULT_LANG:
        return unit
    return UNITS.get(unit, {}).get(lang) or unit