"""Caso de uso: escaneo de imagen → detección → confirmación de ingredientes."""

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.core.security import read_upload_safely, sanitize_filename, validate_image_size_and_mime
from app.repositories.scan_repository import ScanRepository
from app.schemas.ingredient import ConfirmIngredientsResponse
from app.schemas.scan import DetectedIngredientOut, ScanResponse
from app.vision.gemini_vision_client import GeminiVisionClient

logger = get_logger("scan_service")


class ScanService:
    """Orquesta: validar imagen → Gemini Vision → normalizar → persistir."""

    def __init__(self) -> None:
        self.vision = GeminiVisionClient()

    def detect(self, file: UploadFile, db: Session) -> ScanResponse:
        content_type = file.content_type
        validated_file = file.file
        content = read_upload_safely(validated_file)
        validate_image_size_and_mime(content, content_type)

        if content_type is None:
            content_type = "image/jpeg"

        detected = self.vision.detect_ingredients(content, content_type)

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
        return ScanResponse(
            scan_id=scan.id,
            detected_ingredients=[
                DetectedIngredientOut(name=d.name, confidence=d.confidence) for d in detected
            ],
        )

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
