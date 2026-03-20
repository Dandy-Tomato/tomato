from __future__ import annotations
from sqlalchemy import text
from sqlalchemy.orm import Session

import logging

logger = logging.getLogger(__name__)

DOMAIN_BONUS = 0.1


class RecommendationRepository:

    def __init__(self, db: Session):
        self.db = db

    def find_topics(
        self,
        domain_ids: list[int],
        top_k: int,
        preference_embedding: list[float] | None = None,
    ) -> list[dict]:
        logger.info("[DB 쿼리 실행 시작]")

        if preference_embedding:
            query = text("""
                SELECT
                    t.topic_id,
                    t.title,
                    t.description,
                    t.expected_duration_week,
                    t.recommended_team_size,
                    t.difficulty,
                    t.domain_id,
                    d.name AS domain_name,
                    t.source_repo_id,
                    COALESCE(ARRAY_AGG(s.name) FILTER (WHERE s.name IS NOT NULL), ARRAY[]::text[]) AS skills
                FROM topics t
                LEFT JOIN domains d ON t.domain_id = d.domain_id
                LEFT JOIN topic_skills ts ON t.topic_id = ts.topic_id
                LEFT JOIN skills s ON ts.skill_id = s.skill_id
                WHERE t.topic_embedding IS NOT NULL
                GROUP BY t.topic_id, t.title, t.description, t.difficulty, 
                        t.expected_duration_week, t.recommended_team_size, 
                        t.domain_id, d.name, t.source_repo_id, t.topic_embedding
                ORDER BY (
                    (1 - (t.topic_embeddding <=> :embedding::vector))
                    + CASE WHEN t.domain_id = ANY(:domain_ids) THEN :domain_bonus ELSE 0 END
                ) DESC
                LIMIT :top_k
            """)
        else:
            query = text("""
                SELECT
                    t.topic_id,
                    t.title,
                    t.description,
                    t.expected_duration_week,
                    t.recommended_team_size,
                    t.difficulty,
                    t.domain_id,
                    d.name AS domain_name,
                    t.source_repo_id,
                    COALESCE(ARRAY_AGG(s.name) FILTER (WHERE s.name IS NOT NULL), ARRAY[]::text[]) AS skills
                FROM topics t
                LEFT JOIN domains d ON t.domain_id = d.domain_id
                LEFT JOIN topic_skills ts ON t.topic_id = ts.topic_id
                LEFT JOIN skills s ON ts.skill_id = s.skill_id
                GROUP BY t.topic_id, t.title, t.description, t.difficulty, 
                         t.expected_duration_week, t.recommended_team_size, t.domain_id, d.name, t.source_repo_id
                ORDER BY
                    CASE WHEN t.domain_id = ANY(:domain_ids) THEN 0 ELSE 1 END ASC
                LIMIT :top_k
            """)

        rows = (
            self.db.execute(query, {"domain_ids": domain_ids, "top_k": top_k})
            .mappings()
            .all()
        )

        result = [dict(row) for row in rows]
        logger.info(f"[DB 쿼리 완료] 건수={len(result)}")
        return result
