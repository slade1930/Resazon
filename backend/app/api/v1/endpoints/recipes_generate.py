"""Endpoints de generación: /recipes/generate y /recipes/healthy."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.v1.deps import db_session
from app.schemas.common import Envelope
from app.schemas.recipe import (
    RecipeGenerateRequest,
    RecipeGenerateResponse,
)
from app.services.healthy_recipe_service import HealthyRecipeService
from app.services.recipe_service import RecipeService

router = APIRouter(prefix="/recipes", tags=["recipes-generate"])


@router.post("/generate", response_model=Envelope[RecipeGenerateResponse])
def generate_recipe(
    payload: RecipeGenerateRequest,
    db: Session = Depends(db_session),
) -> Envelope[RecipeGenerateResponse]:
    result = RecipeService(db).generate(payload.ingredients, payload.dietary_goal)
    return Envelope(data=result)


@router.post("/healthy", response_model=Envelope[RecipeGenerateResponse])
def healthy_recipe(
    payload: RecipeGenerateRequest,
    db: Session = Depends(db_session),
) -> Envelope[RecipeGenerateResponse]:
    result = HealthyRecipeService(db).generate_healthy(payload.ingredients)
    return Envelope(data=result)
