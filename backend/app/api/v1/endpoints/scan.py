"""POST /api/v1/scan — detecta ingredientes desde una imagen."""

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.api.v1.deps import db_session
from app.schemas.common import Envelope
from app.schemas.scan import ScanResponse
from app.services.scan_service import ScanService

router = APIRouter(prefix="/scan", tags=["scan"])


@router.post("", response_model=Envelope[ScanResponse])
def create_scan(
    file: UploadFile = File(...), db: Session = Depends(db_session)
) -> Envelope[ScanResponse]:
    result = ScanService().detect(file, db)
    return Envelope(data=result)
