from __future__ import annotations
from sqlalchemy.orm import Session

from app.schemas.recommendation import RecommendationRequest, TopicItem
from app.repositories.recommendation_repository import RecommendationRepository


class RecommendationService:

    def __init__(self, db: Session):
        self.db = db

    def recommend(self, request: RecommendationRequest) -> list[TopicItem]:
        repo = RecommendationRepository(self.db)

        rows = repo.find_topics_by_domain_ids(
            domain_ids=request.domainIds,
            preference_embedding=request.preferenceEmbeddings,
        )

        return [
            TopicItem(
                topic_id=row["topic_id"],
                topic_title=row["title"],
                topic_description=row["description"],
                estimated_development_period=row["expected_duration_week"],
                recommended_team_size=row["recommended_team_size"],
                difficulty=row["difficulty"] or 0,
                domain_id=row["domain_id"],
                reference_repo_id=row["source_repo_id"],
                recommendation_score=round(float(row["score"]), 4),
            )
            for row in rows
        ]