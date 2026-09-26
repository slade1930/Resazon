"""POST /api/v1/scan — detecta ingredientes desde una imagen."""

from fastapi import APIRouter, Depends, File, Header, UploadFile
from sqlalchemy.orm import Session

from app.api.v1.deps import db_session
from app.schemas.common import Envelope
from app.schemas.scan import ScanResponse
from app.services.scan_service import ScanService

router = APIRouter(prefix="/scan", tags=["scan"])


@router.post("", response_model=Envelope[ScanResponse])
def create_scan(
    file: UploadFile = File(...),
    db: Session = Depends(db_session),
    x_session_id: str | None = Header(default=None, alias="X-Session-ID"),
) -> Envelope[ScanResponse]:
    # user_id sería None por ahora (sin auth), session_id viene del header
    result = ScanService().detect(file, db, user_id=None, session_id=x_session_id)
    return Envelope(data=result)
