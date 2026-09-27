"""Agrega todos los sub-routers de la API v1."""

from fastapi import APIRouter

from app.ai.gemini_client import ai_available, get_vision_prompt
from app.api.v1.endpoints import (
    ingredients,
    rag,
    recipes,
    recipes_generate,
    scan,
)
from app.core.config import settings

api_v1_router = APIRouter()

api_v1_router.include_router(scan.router)
api_v1_router.include_router(ingredients.router)
api_v1_router.include_router(recipes.router)
api_v1_router.include_router(recipes_generate.router)
api_v1_router.include_router(rag.router)


@api_v1_router.get("/health", tags=["health"])
def health() -> dict:
    return {
        "status": "ok",
        "ai_available": ai_available(),
        "ai_model": settings.GEMINI_MODEL,
        "vision_prompt_has_ocr": "EXTRAE (OCR)" in get_vision_prompt(),
    }
