"""Agrega todos los sub-routers de la API v1."""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    ingredients,
    rag,
    recipes,
    recipes_generate,
    scan,
)

api_v1_router = APIRouter()

api_v1_router.include_router(scan.router)
api_v1_router.include_router(ingredients.router)
api_v1_router.include_router(recipes.router)
api_v1_router.include_router(recipes_generate.router)
api_v1_router.include_router(rag.router)


@api_v1_router.get("/health", tags=["health"])
def health() -> dict:
    return {"status": "ok"}
