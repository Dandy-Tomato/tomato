from __future__ import annotations
from sqlalchemy import text
from sqlalchemy.orm import Session


class RecommendationRepository:

    def __init__(self, db: Session):
        self.db = db

    def find_topics_by_domain_ids(
        self,
        domain_ids: list[int],
        preference_embedding: list[float] | None,
        top_k: int = 5,
    ) -> list[dict]:

        if preference_embedding:
            sql = text("""
                SELECT
                    t.topic_id,
                    t.title,
                    t.description,
                    t.expected_duration_week,
                    t.recommended_team_size,
                    t.difficulty,
                    t.domain_id,
                    t.source_repo_id,
                    1 - (t.topic_embedding <=> CAST(:embedding AS vector)) AS score
                FROM topics t
                WHERE t.domain_id = ANY(:domain_ids)
                  AND t.topic_embedding IS NOT NULL
                ORDER BY score DESC
                LIMIT :top_k
            """)
            rows = self.db.execute(sql, {
                "embedding": str(preference_embedding),
                "domain_ids": domain_ids,
                "top_k": top_k,
            }).mappings().all()

        else:
            sql = text("""
                SELECT
                    t.topic_id,
                    t.title,
                    t.description,
                    t.expected_duration_week,
                    t.recommended_team_size,
                    t.difficulty,
                    t.domain_id,
                    t.source_repo_id,
                    0.0 AS score
                FROM topics t
                WHERE t.domain_id = ANY(:domain_ids)
                LIMIT :top_k
            """)
            rows = self.db.execute(sql, {
                "domain_ids": domain_ids,
                "top_k": top_k,
            }).mappings().all()

        return [dict(row) for row in rows]