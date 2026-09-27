"""Caso de uso: recetas saludables (adaptación con contexto panameño).

Flujo: NO se reenvía la fotografía. Solo se envía a Gemini la lista de
ingredientes detectados. Es UNA ÚNICA llamada de generación (sin RAG previo).
"""

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.ai.gemini_client import gemini_client_provider
from app.ai.models import GeneratedRecipe
from app.ai.prompts.healthy_adaptation import build_healthy_prompt
from app.ai.response_parser import parse_json_model
from app.core.config import settings
from app.core.exceptions import RateLimitExceededError
from app.core.logging import get_logger
from app.models.ai_usage import AIUsageLog, UserDailyLimit
from app.models.recipe import RecipeType
from app.recipes.assembler import build_generated_detail
from app.schemas.recipe import RecipeGenerateResponse
from app.services.recipe_service import RecipeService

logger = get_logger("healthy_recipe_service")


class HealthyRecipeService:
    """Adapta una receta tradicional panameña a una versión saludable via Gemini."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.recipe_service = RecipeService(db)

    def generate_healthy(
        self,
        ingredients: list[str],
        user_id: int | None = None,
        session_id: str | None = None,
    ) -> RecipeGenerateResponse:
        self._check_rate_limit(user_id, session_id)

        prompt = build_healthy_prompt(ingredients, context_text=None)
        provider = gemini_client_provider()
        response = provider.generate_content_with_usage(prompt, temperature=0.6)
        generated: GeneratedRecipe = parse_json_model(response.data, GeneratedRecipe)

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

        self._increment_usage(user_id, session_id, response.model_used, response.input_tokens, response.output_tokens)
        return RecipeGenerateResponse(recipe=detail)

    # ── Límites diarios y cost tracking ──────────────────────────
    def _check_rate_limit(self, user_id: int | None, session_id: str | None) -> None:
        if user_id is None and session_id is None:
            return  # Sin identificación, no se aplica límite

        today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        query = self.db.query(UserDailyLimit).filter(UserDailyLimit.date == today)
        if user_id is not None:
            query = query.filter(UserDailyLimit.user_id == user_id)
        else:
            query = query.filter(UserDailyLimit.session_id == session_id)

        daily_limit = query.first()
        if daily_limit and daily_limit.healthy_generations_count >= settings.MAX_HEALTHY_GENERATIONS_PER_USER_DAY:
            raise RateLimitExceededError(
                message=f"Límite diario de generaciones saludables alcanzado ({settings.MAX_HEALTHY_GENERATIONS_PER_USER_DAY} por día)",
                details={"limit": settings.MAX_HEALTHY_GENERATIONS_PER_USER_DAY, "type": "healthy_generation"},
            )
        if daily_limit and daily_limit.total_ai_requests >= settings.MAX_AI_REQUESTS_PER_DAY:
            raise RateLimitExceededError(
                message=f"Límite diario total de IA alcanzado ({settings.MAX_AI_REQUESTS_PER_DAY} por día)",
                details={"limit": settings.MAX_AI_REQUESTS_PER_DAY, "type": "total"},
            )

    def _increment_usage(
        self,
        user_id: int | None,
        session_id: str | None,
        model: str | None,
        input_tokens: int | None,
        output_tokens: int | None,
    ) -> None:
        today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        query = self.db.query(UserDailyLimit).filter(UserDailyLimit.date == today)
        if user_id is not None:
            query = query.filter(UserDailyLimit.user_id == user_id)
        else:
            query = query.filter(UserDailyLimit.session_id == session_id)

        daily_limit = query.first()
        if not daily_limit:
            daily_limit = UserDailyLimit(
                user_id=user_id,
                session_id=session_id,
                date=today,
                image_analyses_count=0,
                healthy_generations_count=0,
                total_ai_requests=0,
            )
            self.db.add(daily_limit)

        daily_limit.healthy_generations_count += 1
        daily_limit.total_ai_requests += 1

        input_tokens = input_tokens or 0
        output_tokens = output_tokens or 0
        cost_per_1m_input = 0.075  # USD por 1M tokens de entrada
        cost_per_1m_output = 0.30  # USD por 1M tokens de salida
        estimated_cost = (input_tokens / 1_000_000) * cost_per_1m_input + (output_tokens / 1_000_000) * cost_per_1m_output

        usage_log = AIUsageLog(
            user_id=user_id,
            session_id=session_id,
            operation_type="healthy_generation",
            model_used=model or settings.GEMINI_MODEL,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            estimated_cost_usd=estimated_cost,
            status="success",
        )
        self.db.add(usage_log)
        self.db.commit()