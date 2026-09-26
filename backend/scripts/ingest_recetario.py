"""CLI: ingesta del recetario .txt al vector store.

Uso:
    python -m scripts.ingest_recetario \
        --input data/raw/Recetario_Nuestro_Sabor_Panama_estructurado.txt \
        --input ReSazon_Loop_recetario_ampliado.txt
"""

import argparse
import re
import sys

from sqlalchemy.orm import Session

from app.ai.gemini_client import ai_available
from app.core.config import settings
from app.core.db import SessionLocal
from app.core.exceptions import AppError
from app.core.logging import get_logger, setup_logging
from app.models.nestle_product import NestleProduct
from app.models.recipe import (
    Nutrition,
    Recipe,
    RecipeIngredient,
    RecipeNestleProduct,
    RecipeSource,
    RecipeType,
)
from app.rag.domain import RecipeDocument
from app.rag.embeddings.embedding_client import EmbeddingClient
from app.rag.ingestion.chunker import chunk_recipe
from app.rag.ingestion.recetario_parser import parse_recetario
from app.rag.vector_store import VectorStore
from app.repositories.ingredient_repository import IngredientRepository
from app.repositories.recipe_repository import RecipeRepository
from app.services.nutrition_service import NutrientEstimator
from app.vision.ingredient_normalizer import (
    normalize_ingredient,
    strip_accents,
    synonym_aliases_for,
)

logger = get_logger("ingest")

_SOURCE_NUTRITION_LABEL = "Nutrición de la fuente — Recetas Nestlé CAM"
_ESTIMATED_NUTRITION_LABEL = "estimación heurística local"

_AMPLIADO_MARKERS = (
    "METADATOS PARA RAG",
    "RECETAS PANAMEÑAS SENCILLAS",
    "POSTRES SENCILLOS",
    "REGLA DE RESAZÓN LOOP",
)


def detect_parser(text: str):
    """Elige el parser según el formato del archivo."""
    if any(marker in text.upper() for marker in _AMPLIADO_MARKERS):
        from app.rag.ingestion.ampliado_parser import parse_ampliado

        return parse_ampliado
    return parse_recetario


def _ensure_nestle_product(db: Session, name: str) -> NestleProduct:
    existing = db.query(NestleProduct).filter(NestleProduct.name == name).first()
    if existing:
        return existing
    product = NestleProduct(name=name)
    db.add(product)
    db.flush()
    return product


def build_search_keywords(doc: RecipeDocument) -> str:
    """Bolsa multilingüe de términos para la búsqueda léxica (search_keywords).

    Combina el nombre, cada token del nombre con sus sinónimos ES/EN/FR
    normalizados, la categoría, los productos Nestlé y cada ingrediente junto
    con sus sinónimos. Sin acentos y en minúsculas.
    """
    tokens: set[str] = set()

    def add(text: str) -> None:
        for token in re.split(r"[^a-z0-9áéíóúüñ]+", strip_accents(text).lower()):
            if len(token) >= 2:
                tokens.add(token)

    def add_with_synonyms(text: str) -> None:
        add(text)
        for token in re.split(r"[^a-z0-9áéíóúüñ]+", strip_accents(text).lower()):
            if len(token) < 2:
                continue
            norm = normalize_ingredient(token)
            if norm:
                for alias in synonym_aliases_for(norm):
                    add(alias)

    add_with_synonyms(doc.name)
    if doc.category:
        add(doc.category)
    for product in doc.nestle_products:
        add(product)
    for ref in doc.ingredients:
        norm = normalize_ingredient(ref.name)
        if not norm:
            continue
        add(ref.name)
        tokens.add(norm)
        for alias in synonym_aliases_for(norm):
            add(alias)
    return " ".join(sorted(tokens))


def _set_recipe_fields(recipe: Recipe, doc: RecipeDocument) -> None:
    recipe.category = doc.category
    recipe.preparation_time_minutes = doc.preparation_time_minutes
    recipe.servings = doc.servings
    recipe.country = doc.country
    recipe.type = getattr(RecipeType, doc.recipe_type, RecipeType.TRADITIONAL)
    recipe.difficulty = doc.difficulty
    recipe.panama_verified = doc.panama_verified
    recipe.source_url = doc.source_url
    recipe.search_keywords = build_search_keywords(doc)


def _set_nutrition(db: Session, recipe: Recipe, doc: RecipeDocument) -> None:
    if doc.nutrition:
        values = dict(
            calories=doc.nutrition.calories,
            protein_g=doc.nutrition.protein_g,
            carbs_g=doc.nutrition.carbs_g,
            fat_g=doc.nutrition.fat_g,
            fiber_g=doc.nutrition.fiber_g,
            per_serving=doc.nutrition.per_serving,
            is_estimated=False,
            source=_SOURCE_NUTRITION_LABEL,
        )
    else:
        facts = NutrientEstimator().estimate(
            [ref.name for ref in doc.ingredients],
            servings=doc.servings,
            source=_ESTIMATED_NUTRITION_LABEL,
        )
        values = dict(
            calories=facts.calories,
            protein_g=facts.protein_g,
            carbs_g=facts.carbs_g,
            fat_g=facts.fat_g,
            fiber_g=facts.fiber_g,
            per_serving=facts.per_serving,
            is_estimated=True,
            source=_ESTIMATED_NUTRITION_LABEL,
        )
    if all(v is None for v in (values["calories"], values["protein_g"], values["carbs_g"], values["fat_g"], values["fiber_g"])):
        return
    if recipe.nutrition is not None:
        recipe.nutrition = None
        db.flush()
    recipe.nutrition = Nutrition(recipe_id=recipe.id, **values)
    db.flush()


def ingest_document(db: Session, doc: RecipeDocument) -> None:
    repo = RecipeRepository(db)
    ingredient_repo = IngredientRepository(db)

    existing = repo.find_by_name_source(doc.name, doc.source)
    if existing:
        recipe = existing
        # re-ingesta: reseteamos relaciones para reconstruir limpias
        recipe.recipe_ingredients.clear()
        recipe.nestle_products.clear()
        recipe.sources.clear()
        recipe.embeddings.clear()
        _set_recipe_fields(recipe, doc)
        db.flush()
        _build_recipe_rows(db, recipe, doc, ingredient_repo)
    else:
        recipe = Recipe(
            name=doc.name,
            country=doc.country,
            source=doc.source,
            type=getattr(RecipeType, doc.recipe_type, RecipeType.TRADITIONAL),
        )
        _set_recipe_fields(recipe, doc)
        db.add(recipe)
        db.flush()
        _build_recipe_rows(db, recipe, doc, ingredient_repo)
        logger.info("Receta creada: %s", doc.name)

    _set_nutrition(db, recipe, doc)

    # Embeddings (solo si la IA está activa; con la IA off la búsqueda es léxica).
    if ai_available():
        chunks = chunk_recipe(doc)
        store = VectorStore(db)
        texts = [c.embedding_text for c in chunks]
        embeddings = EmbeddingClient().embed_batch(texts)
        store.replace_for_recipe(
            recipe.id,
            [(c.text, c.chunk_index) for c in chunks],
            embeddings,
        )
        logger.info("  → %s chunks embeddeados", len(chunks))
    else:
        logger.info("  → IA desactivada, embeddings omitidos (búsqueda léxica)")


def _build_recipe_rows(
    db: Session,
    recipe: Recipe,
    doc: RecipeDocument,
    ingredient_repo: IngredientRepository,
) -> None:
    for ref in doc.ingredients:
        normalized = normalize_ingredient(ref.name) or ref.name.lower()
        ingredient = ingredient_repo.get_or_create(ref.name, normalized)
        db.flush()
        recipe.recipe_ingredients.append(
            RecipeIngredient(
                ingredient_id=ingredient.id,
                quantity=ref.quantity,
                unit=ref.unit,
                is_optional=ref.is_optional,
            )
        )

    if doc.page_or_section:
        recipe.sources.append(
            RecipeSource(
                recipe_id=recipe.id,
                document_name=doc.source,
                page_or_section=doc.page_or_section,
                raw_text_reference=doc.preparation_text[:2000],
            )
        )

    for product_name in set(doc.nestle_products):
        product = _ensure_nestle_product(db, product_name)
        db.flush()
        recipe.nestle_products.append(
            RecipeNestleProduct(nestle_product_id=product.id, usage_note=None)
        )


def main() -> int:
    setup_logging()
    parser = argparse.ArgumentParser(description="Ingesta del recetario panameño al RAG")
    parser.add_argument("--input", action="append", dest="inputs")
    args = parser.parse_args()

    inputs = args.inputs or [str(settings.recetario_full_path)]

    documents: list[RecipeDocument] = []
    for path in inputs:
        try:
            text = open(path, encoding="utf-8").read()
        except FileNotFoundError:
            logger.error("Archivo no encontrado: %s", path)
            return 1
        doc_parser = detect_parser(text)
        parsed = doc_parser(text)
        logger.info("Parsiadas %s recetas desde %s (%s)", len(parsed), path, doc_parser.__module__)
        documents.extend(parsed)

    if not documents:
        logger.error("No se parseó ninguna receta; revisa el formato de --input.")
        return 2

    db: Session = SessionLocal()
    try:
        for doc in documents:
            ingest_document(db, doc)
        db.commit()
        total = db.query(Recipe).count()
        logger.info("Ingesta completada. %s recetas en la BD.", total)
    except AppError as exc:
        db.rollback()
        logger.error("Error de ingesta: %s", exc.message)
        return 3
    except Exception as exc:  # noqa: BLE001
        db.rollback()
        logger.exception("Error inesperado: %s", exc)
        return 4
    finally:
        db.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())