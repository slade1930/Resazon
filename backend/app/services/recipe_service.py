"""Caso de uso: buscar recetas tradicionales (RAG + matcher + ranker) y generar."""

from sqlalchemy.orm import Session

from app.ai.gemini_client import gemini_client_provider
from app.ai.models import GeneratedRecipe
from app.ai.prompts.recipe_generation import build_generation_prompt
from app.ai.response_parser import parse_json_model
from app.core.exceptions import NotFoundError
from app.core.logging import get_logger
from app.models.recipe import RecipeType
from app.rag.domain import RetrievedRecipe
from app.rag.retriever import Retriever
from app.recipes.assembler import build_detail, build_generated_detail, build_summary
from app.recipes.matcher import match
from app.recipes.ranker import rank
from app.repositories.recipe_repository import RecipeRepository
from app.schemas.recipe import (
    RecipeDetail,
    RecipeGenerateResponse,
    RecipeSearchResponse,
    RecipeSummary,
)
from app.services.nutrition_service import NutrientEstimator

logger = get_logger("recipe_service")


class RecipeService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.recipes = RecipeRepository(db)
        self.retriever = Retriever(db)
        self.estimator = NutrientEstimator()

    # ── Plato panameño (tradicional) ─────────────────────────────
    def search_traditional(
        self,
        ingredients: list[str],
        lang: str | None = None,
        max_results: int = 10,
    ) -> RecipeSearchResponse:
        """Busca recetas tradicionales SIN llamar a Gemini.

        Cruza los ingredientes detectados contra todas las recetas existentes
        en la base de datos (Python + PostgreSQL) y calcula el % de
        compatibilidad localmente. Cero embeddings, cero llamadas a IA.
        """
        recipes, _ = self.recipes.list_paginated(1, 100)
        summaries: list[RecipeSummary] = []
        for recipe in recipes:
            recipe_ingredients = [link.ingredient.name for link in recipe.recipe_ingredients]
            result = match(ingredients, recipe_ingredients)
            if result.match_percentage <= 0:
                continue
            summaries.append(build_summary(recipe, result, lang=lang))

        ranked = rank(summaries)
        return RecipeSearchResponse(recipes=ranked[:max_results], total=len(ranked))

    # ── Detalle ──────────────────────────────────────────────────
    def get_detail(self, recipe_id: int, lang: str | None = None) -> RecipeDetail:
        recipe = self.recipes.get_full(recipe_id)
        if recipe is None:
            raise NotFoundError(message=f"Receta #{recipe_id} no encontrada")
        return build_detail(recipe, lang=lang)

    # ── Crear con mis ingredientes (generación) ──────────────────
    def generate(
        self, ingredients: list[str], dietary_goal: str | None = None
    ) -> RecipeGenerateResponse:
        retrieved = self._retrieve_context(ingredients, mode="generated")
        context = self._context_to_text(retrieved)

        prompt = build_generation_prompt(ingredients, context)
        provider = gemini_client_provider()
        raw_text = provider.generate_content(prompt, temperature=0.8)
        generated: GeneratedRecipe = parse_json_model(raw_text, GeneratedRecipe)

        included = [ing.name for ing in generated.ingredients]
        nutrition = self.estimator.estimate(
            included,
            servings=generated.servings,
            source="estimación heurística local (generación IA)",
        )
        detail = build_generated_detail(
            generated,
            recipe_type=RecipeType.AI_GENERATED.value,
            source="generada por IA con ingredientes del usuario",
            nutrition=nutrition,
        )
        return RecipeGenerateResponse(recipe=detail)

    # ── helpers ──────────────────────────────────────────────────
    def _retrieve_context(self, ingredients: list[str], mode: str) -> list[RetrievedRecipe]:
        query = self.retriever.build_query(ingredients, mode=mode)
        return self.retriever.search(query, raw_terms=ingredients)

    def _context_to_text(self, retrieved: list[RetrievedRecipe]) -> str:
        parts = []
        for item in retrieved[:3]:
            parts.append(f"- {item.name}:\n{item.chunk_text[:1200]}")
        return "\n\n".join(parts)
