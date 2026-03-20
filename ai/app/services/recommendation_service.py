from __future__ import annotations
import numpy as np
from sqlalchemy.orm import Session

from app.schemas.recommendation import RecommendationRequest, TopicItem
from app.repositories.recommendation_repository import RecommendationRepository

import logging

logger = logging.getLogger(__name__)

TOP_K = 20

class RecommendationService:

    def __init__(self, db: Session):
        self.repository = RecommendationRepository(db)
    
    def get_recommendations(self, request: RecommendationRequest) -> list[TopicItem]:
        logger.info("[레포지토리 호출 시작]")
        
        topics = self.repository.find_topics(
            preference_embedding=request.preference_embeddings,
            domain_ids=request.domain_ids,
            top_k=TOP_K
        )

        logger.info(f"[레포지토리 호출 완료] 건수={len(topics)}")

        return [TopicItem(**topic) for topic in topics]
