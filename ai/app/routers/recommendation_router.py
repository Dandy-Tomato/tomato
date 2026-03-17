from __future__ import annotations
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.recommendation import RecommendationRequest, RecommendationResponse
from app.services.recommendation_service import RecommendationService
from app.common.responses import ok, ApiResponse

router = APIRouter(prefix="/recommendations", tags=["recommendation"])


@router.post("", response_model=ApiResponse)
def recommend(
    request: RecommendationRequest,
    db: Session = Depends(get_db),
):
    service = RecommendationService(db)
    topics = service.recommend(request)
    return ok(data=topics)