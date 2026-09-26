"""Acceso a datos de escaneos y detecciones."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.scan import DetectedIngredient, Scan


class ScanRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, image_reference: str | None = None) -> Scan:
        scan = Scan(image_reference=image_reference)
        self.db.add(scan)
        self.db.flush()
        return scan

    def get(self, scan_id: int) -> Scan | None:
        return self.db.get(Scan, scan_id)

    def add_detected(
        self,
        scan_id: int,
        name_raw: str,
        normalized_name: str,
        confidence: float,
    ) -> DetectedIngredient:
        row = DetectedIngredient(
            scan_id=scan_id,
            ingredient_name_raw=name_raw,
            normalized_name=normalized_name,
            confidence=confidence,
        )
        self.db.add(row)
        return row

    def list_detected(self, scan_id: int) -> list[DetectedIngredient]:
        return list(
            self.db.execute(
                select(DetectedIngredient)
                .where(DetectedIngredient.scan_id == scan_id)
                .order_by(DetectedIngredient.confidence.desc())
            ).scalars()
        )

    def confirm(self, scan_id: int, ingredients: list[str]) -> None:
        detected = self.list_detected(scan_id)
        by_name = {d.normalized_name or d.ingredient_name_raw: d for d in detected}

        # Marca los confirmados tal cual.
        confirmed_names = {n.strip() for n in ingredients}
        for name, row in by_name.items():
            row.was_confirmed = name in confirmed_names

        # Registro de ediciones: ingredientes que el usuario agregó/renombró.
        for name in ingredients:
            if name not in by_name:
                row = DetectedIngredient(
                    scan_id=scan_id,
                    ingredient_name_raw=name,
                    normalized_name=name,
                    confidence=1.0,
                    was_confirmed=True,
                    was_edited=True,
                )
                self.db.add(row)
