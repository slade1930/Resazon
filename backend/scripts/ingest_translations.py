"""CLI: ingesta de traducciones de recetas, ingredientes, categorías y unidades.

Uso:
    python -m scripts.ingest_translations [--data data/i18n.json]

Lee el archivo de traducciones autorado y hace upsert en las tablas
`recipe_translations` e `ingredient_translations`. Las categorías de i18n.json
se resuelven por receta (según su categoría actual en BD) antes de persistir.
"""

import argparse
import json
import sys
from pathlib import Path

from sqlalchemy.orm import Session

from app.core.db import SessionLocal
from app.core.logging import get_logger, setup_logging
from app.models.ingredient import Ingredient, IngredientTranslation
from app.models.recipe import Recipe, RecipeTranslation

logger = get_logger("ingest_translations")

LANGS = ("en", "fr")


def _load_data(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def _rows_for(recipe: Recipe, spec: dict, categories: dict) -> list[RecipeTranslation]:
    rows = []
    for lang in LANGS:
        entry = spec.get(lang) or {}
        category = recipe.category
        if category and category in categories:
            category = (categories[category].get(lang) or category)
        rows.append(
            RecipeTranslation(
                recipe_id=recipe.id,
                lang=lang,
                name=(entry.get("name") or None),
                category=category,
                steps=(entry.get("steps") or None),
            )
        )
    return rows


def _upsert_recipe_translations(db: Session, recipe: Recipe, rows: list) -> int:
    created = 0
    for row in rows:
        existing = db.query(RecipeTranslation).filter(
            RecipeTranslation.recipe_id == row.recipe_id,
            RecipeTranslation.lang == row.lang,
        ).one_or_none()
        if existing:
            existing.name = row.name
            existing.category = row.category
            existing.steps = row.steps
        else:
            db.add(row)
            created += 1
    return created


def _upsert_ingredient_translations(db: Session, ingredients_by_name: dict, specs: dict) -> int:
    created = 0
    for name, by_lang in specs.items():
        ingredient = ingredients_by_name.get(name)
        if ingredient is None:
            logger.warning("Ingrediente '%s' no existe en BD — omito traducción", name)
            continue
        translations = (
            db.query(IngredientTranslation)
            .filter(IngredientTranslation.ingredient_id == ingredient.id)
            .all()
        )
        by_ingredient_lang = {row.lang: row for row in translations}
        for lang in LANGS:
            translated = by_lang.get(lang)
            if not translated:
                continue
            row = by_ingredient_lang.get(lang)
            if row:
                row.name = translated
            else:
                db.add(
                    IngredientTranslation(
                        ingredient_id=ingredient.id,
                        lang=lang,
                        name=translated,
                    )
                )
                created += 1
    return created


def main() -> int:
    parser = argparse.ArgumentParser(description="Ingesta traducciones i18n → BD")
    parser.add_argument("--data", default="data/i18n.json", help="JSON con traducciones")
    args = parser.parse_args()

    data_path = Path(args.data)
    if not data_path.exists():
        logger.error("Archivo no existe: %s", data_path)
        return 1
    payload = _load_data(data_path)

    categories = payload.get("categories", {})
    unit_specs = payload.get("units", {})
    ingredient_specs = payload.get("ingredients", {})
    recipe_specs = payload.get("recipes", {})

    if unit_specs:
        from app.i18n import UNITS

        for unit_name, by_lang in unit_specs.items():
            entry = UNITS.setdefault(unit_name, {})
            for lang in LANGS:
                if by_lang.get(lang):
                    entry[lang] = by_lang[lang]

    db: Session = SessionLocal()
    try:
        recipes = db.query(Recipe).all()
        recipe_count = 0
        for recipe in recipes:
            spec = recipe_specs.get(str(recipe.id)) or recipe_specs.get(recipe.name)
            if spec is None:
                logger.warning("Receta %s (#%s) sin traducción — se omite", recipe.name, recipe.id)
                continue
            rows = _rows_for(recipe, spec, categories)
            recipe_count += _upsert_recipe_translations(db, recipe, rows)
        db.flush()

        ingredients_all = db.query(Ingredient).all()
        ingredients_by_name = {item.name: item for item in ingredients_all}
        ingredient_count = _upsert_ingredient_translations(db, ingredients_by_name, ingredient_specs)

        db.commit()
        logger.info(
            "Ingesta completa: %s traducciones de receta nuevas, %s de ingrediente nuevas, %s unidades mapeadas",
            recipe_count,
            ingredient_count,
            len(categories),
        )
        return 0
    except Exception as exc:  # pragma: no cover
        db.rollback()
        logger.exception("Error durante la ingesta: %s", exc)
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    setup_logging()
    sys.exit(main())