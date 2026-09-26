"""CLI: siembra datos base (productos Nestlé canónicos)."""

import sys

from app.core.db import SessionLocal
from app.core.logging import get_logger, setup_logging
from app.models.nestle_product import NestleProduct

logger = get_logger("seed")

CANONICAL_PRODUCTS = [
    ("MAGGI® Sabor de Gallina", "caldo"),
    ("MAGGI® Sabor de Res", "caldo"),
    ("MAGGI® Sazonador Completo", "condimento"),
    ("MAGGI® Tomate", "salsa"),
    ("MAGGI® Mayonesa", "salsa"),
    ("IDEAL® Leche Evaporada", "leche"),
    ("IDEAL® Leche Condensada", "leche"),
    ("Klim® Leche en Polvo", "leche"),
    ("NESTLÉ® ¡Qué Rico! Frozen", "helado"),
    ("NESTLÉ® Cocinero Crema de Leche", "crema"),
    ("NESTLÉ® Chocolate Abuelita", "chocolate"),
    ("NESTLÉ® Sopa Crema de Pollo", "sopa"),
]


def main() -> int:
    setup_logging()
    db = SessionLocal()
    try:
        created = 0
        for name, category in CANONICAL_PRODUCTS:
            exists = db.query(NestleProduct).filter(NestleProduct.name == name).first()
            if exists:
                continue
            db.add(NestleProduct(name=name, category=category))
            created += 1
        db.commit()
        logger.info("Seed completado: %s productos Nestlé nuevos.", created)
    except Exception as exc:  # noqa: BLE001
        db.rollback()
        logger.exception("Error en seed: %s", exc)
        return 1
    finally:
        db.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
