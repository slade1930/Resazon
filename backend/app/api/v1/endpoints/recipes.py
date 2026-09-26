"""Endpoints de recetas: listado, detalle y búsqueda tradicional."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.v1.deps import db_session
from app.core.exceptions import NotFoundError
from app.i18n import normalize_lang
from app.schemas.common import Envelope, PaginationMeta
from app.schemas.recipe import (
    RecipeDetail,
    RecipeSearchRequest,
    RecipeSearchResponse,
)
from app.services.recipe_service import RecipeService

router = APIRouter(prefix="/recipes", tags=["recipes"])

_LANG_QUERY = Query(default="es", pattern="^(es|en|fr)$", description="Idioma del contenido (es/en/fr)")


@router.post("/search", response_model=Envelope[RecipeSearchResponse])
def search_recipes(
    payload: RecipeSearchRequest,
    lang: str = _LANG_QUERY,
    db: Session = Depends(db_session),
) -> Envelope[RecipeSearchResponse]:
    result = RecipeService(db).search_traditional(payload.ingredients, lang=normalize_lang(lang))
    return Envelope(data=result)


@router.get("", response_model=Envelope[dict])
def list_recipes(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    lang: str = _LANG_QUERY,
    db: Session = Depends(db_session),
) -> Envelope[dict]:
    service = RecipeService(db)
    recipes, total = service.recipes.list_paginated(page, page_size)

    from app.recipes.assembler import build_summary as _bs
    from app.recipes.matcher import match as _match

    summaries = []
    for recipe in recipes:
        names = [link.ingredient.name for link in recipe.recipe_ingredients]
        summaries.append(_bs(recipe, _match([], names), lang=normalize_lang(lang)))
    meta = PaginationMeta(
        page=page,
        page_size=page_size,
        total=total,
        total_pages=(total + page_size - 1) // page_size,
    )
    return Envelope(data={"items": summaries, "meta": meta})


@router.get("/{recipe_id}", response_model=Envelope[RecipeDetail])
def get_recipe(
    recipe_id: int,
    lang: str = _LANG_QUERY,
    db: Session = Depends(db_session),
) -> Envelope[RecipeDetail]:
    try:
        detail = RecipeService(db).get_detail(recipe_id, lang=normalize_lang(lang))
    except NotFoundError as exc:
        raise exc
    return Envelope(data=detail)
