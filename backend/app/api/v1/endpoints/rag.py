"""POST /api/v1/rag/search — búsqueda semántica directa (debug/uso interno)."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.v1.deps import db_session
from app.rag.retriever import Retriever
from app.schemas.common import Envelope

router = APIRouter(prefix="/rag", tags=["rag"])


class RagSearchRequest(BaseModel):
    query: str
    top_k: int = 5


@router.post("/search", response_model=Envelope[dict])
def rag_search(payload: RagSearchRequest, db: Session = Depends(db_session)) -> Envelope[dict]:
    results = Retriever(db).search(payload.query, top_k=payload.top_k)
    return Envelope(
        data={
            "results": [
                {
                    "recipe_id": r.recipe_id,
                    "name": r.name,
                    "score": round(r.score, 4),
                    "chunk_text": r.chunk_text[:300],
                }
                for r in results
            ]
        }
    )
