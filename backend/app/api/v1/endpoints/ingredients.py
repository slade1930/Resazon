"""POST /api/v1/ingredients/confirm — confirma/edita los ingredientes detectados."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.v1.deps import db_session
from app.schemas.common import Envelope
from app.schemas.ingredient import ConfirmIngredientsRequest, ConfirmIngredientsResponse
from app.services.scan_service import ScanService

router = APIRouter(prefix="/ingredients", tags=["ingredients"])


@router.post("/confirm", response_model=Envelope[ConfirmIngredientsResponse])
def confirm_ingredients(
    payload: ConfirmIngredientsRequest,
    db: Session = Depends(db_session),
) -> Envelope[ConfirmIngredientsResponse]:
    service = ScanService()
    result = service.confirm(payload.scan_id, [i.name for i in payload.ingredients], db)
    return Envelope(data=result)
