from __future__ import annotations
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.recommendation import RecommendationRequest, TopicItem
from app.services.recommendation_service import RecommendationService
from app.common.responses import ok, ApiResponse
import logging
import time

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/recommendations", tags=["recommendation"])

@router.post("", response_model=ApiResponse)
def recommend(
    request: RecommendationRequest,
    db: Session = Depends(get_db),
):

    logger.info(f"[요청 수신] project_id={request.project_id}")

    # 실행 시간 측정용
    start = time.time()

    service = RecommendationService(db)
    
    logger.info("[서비스 호출 시작]")
    topics = service.get_recommendations(request)
    logger.info(f"[서비스 호출 완료] 건수={len(topics)}")

    # 실행 시간 측정용
    elapsed = time.time() - start
    logger.info(
        f"[v1] 전체 처리: {elapsed:.3f}s | "
        f"반환 건수: {len(topics)}건"
    )

    return ok(data=topics)
