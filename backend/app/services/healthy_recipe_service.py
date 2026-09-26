"""Caso de uso: recetas saludables (adaptación con contexto panameño)."""

from sqlalchemy.orm import Session

from app.ai.gemini_client import gemini_client_provider
from app.ai.models import GeneratedRecipe
from app.ai.prompts.healthy_adaptation import build_healthy_prompt
from app.ai.response_parser import parse_json_model
from app.core.logging import get_logger
from app.models.recipe import RecipeType
from app.rag.retriever import Retriever
from app.recipes.assembler import build_generated_detail
from app.schemas.recipe import RecipeGenerateResponse
from app.services.recipe_service import RecipeService

logger = get_logger("healthy_recipe_service")


class HealthyRecipeService:
    """Adapta una receta tradicional panameña a una versión saludable via Gemini."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.recipe_service = RecipeService(db)
        self.retriever = Retriever(db)

    def generate_healthy(self, ingredients: list[str]) -> RecipeGenerateResponse:
        query = self.retriever.build_query(ingredients, mode="healthy")
        retrieved = self.retriever.search(query)
        context = self.recipe_service._context_to_text(retrieved)

        prompt = build_healthy_prompt(ingredients, context)
        provider = gemini_client_provider()
        raw_text = provider.generate_content(prompt, temperature=0.6)
        generated: GeneratedRecipe = parse_json_model(raw_text, GeneratedRecipe)

        included = [ing.name for ing in generated.ingredients]
        nutrition = self.recipe_service.estimator.estimate(
            included,
            servings=generated.servings,
            source="estimación heurística local (versión saludable)",
        )
        detail = build_generated_detail(
            generated,
            recipe_type=RecipeType.AI_ADAPTED.value,
            source="adaptación saludable de referencia panameña",
            nutrition=nutrition,
        )
        return RecipeGenerateResponse(recipe=detail)
