"""Caso de uso: escaneo de imagen → detección → confirmación de ingredientes."""

from datetime import datetime, timezone
from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import RateLimitExceededError
from app.core.logging import get_logger
from app.core.security import read_upload_safely, sanitize_filename, validate_image_size_and_mime
from app.models.ai_usage import AIUsageLog, UserDailyLimit
from app.repositories.scan_repository import ScanRepository
from app.schemas.ingredient import ConfirmIngredientsResponse
from app.schemas.scan import DetectedIngredientOut, ScanResponse
from app.vision.gemini_vision_client import GeminiVisionClient

logger = get_logger("scan_service")


class ScanService:
    """Orquesta: validar imagen → Gemini Vision → normalizar → persistir."""

    def __init__(self) -> None:
        self.vision = GeminiVisionClient()

    def _check_rate_limit(self, db: Session, user_id: int | None, session_id: str | None) -> None:
        """Verifica límites diarios de análisis de imágenes."""
        if user_id is None and session_id is None:
            return  # Sin identificación, no se aplica límite

        today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        query = db.query(UserDailyLimit).filter(UserDailyLimit.date == today)
        if user_id is not None:
            query = query.filter(UserDailyLimit.user_id == user_id)
        else:
            query = query.filter(UserDailyLimit.session_id == session_id)

        daily_limit = query.first()
        if daily_limit and daily_limit.image_analyses_count >= settings.MAX_IMAGE_ANALYSES_PER_USER_DAY:
            raise RateLimitExceededError(
                message=f"Límite diario de análisis de imágenes alcanzado ({settings.MAX_IMAGE_ANALYSES_PER_USER_DAY} por día)",
                details={"limit": settings.MAX_IMAGE_ANALYSES_PER_USER_DAY, "type": "image_analysis"}
            )
        if daily_limit and daily_limit.total_ai_requests >= settings.MAX_AI_REQUESTS_PER_DAY:
            raise RateLimitExceededError(
                message=f"Límite diario total de IA alcanzado ({settings.MAX_AI_REQUESTS_PER_DAY} por día)",
                details={"limit": settings.MAX_AI_REQUESTS_PER_DAY, "type": "total"}
            )

    def _increment_usage(self, db: Session, user_id: int | None, session_id: str | None, model: str, input_tokens: int | None, output_tokens: int | None, cost: float | None) -> None:
        """Incrementa contadores de uso y registra log."""
        today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        query = db.query(UserDailyLimit).filter(UserDailyLimit.date == today)
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
            db.add(daily_limit)

        daily_limit.image_analyses_count += 1
        daily_limit.total_ai_requests += 1

        # Log de uso
        usage_log = AIUsageLog(
            user_id=user_id,
            session_id=session_id,
            operation_type="image_analysis",
            model_used=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            estimated_cost_usd=cost,
            status="success",
        )
        db.add(usage_log)

    def detect(self, file: UploadFile, db: Session, user_id: int | None = None, session_id: str | None = None) -> ScanResponse:
        # Verificar rate limit
        self._check_rate_limit(db, user_id, session_id)

        content_type = file.content_type
        validated_file = file.file
        content = read_upload_safely(validated_file)
        validate_image_size_and_mime(content, content_type)

        if content_type is None:
            content_type = "image/jpeg"

        # Comprimir imagen si es muy grande (máx 1024x1024)
        content = self._compress_image_if_needed(content)

        # Detectar ingredientes con tracking de uso
        vision_response = self.vision.detect_ingredients_with_usage(content, content_type)
        detected = [d for d in vision_response.data if d.confidence >= 0.5]

        repo = ScanRepository(db)
        scan = repo.create(image_reference=sanitize_filename(file.filename))
        for item in detected:
            repo.add_detected(
                scan_id=scan.id,
                name_raw=item.name,
                normalized_name=item.name,
                confidence=item.confidence,
            )
        db.commit()
        logger.info("Scan #%s con %s ingredientes detectados", scan.id, len(detected))

        # Estimar costo (aproximado para gemini-3.5-flash-lite: $0.075/1M input, $0.30/1M output)
        input_tokens = vision_response.input_tokens or 0
        output_tokens = vision_response.output_tokens or 0
        cost_per_1m_input = 0.075  # USD por 1M tokens de entrada
        cost_per_1m_output = 0.30   # USD por 1M tokens de salida
        estimated_cost = (input_tokens / 1_000_000) * cost_per_1m_input + (output_tokens / 1_000_000) * cost_per_1m_output

        # Registrar uso con tokens y costo
        self._increment_usage(
            db, user_id, session_id,
            vision_response.model_used or settings.GEMINI_MODEL,
            vision_response.input_tokens,
            vision_response.output_tokens,
            estimated_cost,
        )

        # Buscar recetas tradicionales coincidentes en la misma llamada
        from app.services.recipe_service import RecipeService
        recipe_service = RecipeService(db)
        search_result = recipe_service.search_traditional([d.name for d in detected])

        return ScanResponse(
            scan_id=scan.id,
            detected_ingredients=[
                DetectedIngredientOut(name=d.name, confidence=d.confidence) for d in detected
            ],
            traditional_recipes=search_result.recipes,
        )

    def _compress_image_if_needed(self, image_bytes: bytes) -> bytes:
        """Comprime la imagen a máx 800x800 para velocidad de análisis."""
        try:
            from PIL import Image
            import io

            img = Image.open(io.BytesIO(image_bytes))
            if img.width > 800 or img.height > 800:
                img.thumbnail((800, 800), Image.Resampling.LANCZOS)
                output = io.BytesIO()
                img.save(output, format="JPEG", quality=80, optimize=True)
                return output.getvalue()
        except Exception:
            pass
        return image_bytes

    def confirm(
        self, scan_id: int, ingredients: list[str], db: Session
    ) -> ConfirmIngredientsResponse:
        repo = ScanRepository(db)
        scan = repo.get(scan_id)
        if scan is None:
            from app.core.exceptions import NotFoundError

            raise NotFoundError(message=f"Scan #{scan_id} no encontrado")

        repo.confirm(scan_id, ingredients)
        db.commit()
        confirmed = [normalize_confirmed(i) for i in ingredients]
        return ConfirmIngredientsResponse(scan_id=scan_id, confirmed=confirmed)


def normalize_confirmed(name: str) -> str:
    from app.vision.ingredient_normalizer import normalize_ingredient

    return normalize_ingredient(name) or name.strip()
