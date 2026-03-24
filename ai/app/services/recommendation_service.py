from __future__ import annotations
import numpy as np
from sqlalchemy.orm import Session

from app.schemas.recommendation import RecommendationRequest, TopicItem
from app.repositories.recommendation_repository import RecommendationRepository

import logging

logger = logging.getLogger(__name__)

TOP_K = 20
DOMAIN_BONUS = 0.1

class RecommendationService:

    def __init__(self, db: Session):
        self.repository = RecommendationRepository(db)
    
    def get_recommendations(self, request: RecommendationRequest) -> list[TopicItem]:
        logger.info("[레포지토리 호출 시작]")
        topics = self.repository.find_topics()
        logger.info(f"[레포지토리 호출 완료] 건수={len(topics)}")

        # 점수 계산 완료된 쌍 모아두는 리스트
        scored = []

        for topic in topics:
            score = 0.0

            # preference_embedding 있을 때만 코사인 유사도 계산
            if request.preference_embeddings:
                embedding = topic.get("topic_embedding")
                if embedding is not None:
                    pref_vec = np.array(request.preference_embeddings, dtype=np.float32)
                    topic_vec = np.array(embedding, dtype=np.float32)
                    score = np.dot(pref_vec, topic_vec) / (np.linalg.norm(pref_vec) * np.linalg.norm(topic_vec) + 1e-9)

            # 도메인 보너스 항상 적용
            if topic["domain_id"] in request.domain_ids:
                score += DOMAIN_BONUS

            scored.append((score, topic))
        
        # 점수로 정렬
        scored.sort(key=lambda x: x[0], reverse=True)

        result = []
        for _, t in scored[:TOP_K]:
            item_data = {k: v for k, v in t.items() if k != "topic_embedding"}
            result.append(TopicItem(**item_data))

        logger.info(f"[점수 계산 완료] top_k={len(result)}")
        return result