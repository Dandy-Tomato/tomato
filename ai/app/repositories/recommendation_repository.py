from __future__ import annotations
from sqlalchemy import text
from sqlalchemy.orm import Session

import logging

logger = logging.getLogger(__name__)

class RecommendationRepository:

    def __init__(self, db: Session):
        self.db = db

    def find_topics(self) -> list[dict]:
        logger.info("[DB 쿼리 실행 시작]")
        sql = text("""
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
                t.topic_embedding,
                COALESCE(array_agg(s.name) FILTER (WHERE s.name IS NOT NULL), '{}') AS skills
            FROM topics t
            JOIN domains d ON t.domain_id = d.domain_id
            LEFT JOIN topic_skills ts ON t.topic_id = ts.topic_id
            LEFT JOIN skills s ON ts.skill_id = s.skill_id
            GROUP BY t.topic_id, d.name
            """)
        rows = self.db.execute(sql).mappings().all()
        result = [dict(row) for row in rows]
        logger.info(f"[DB 쿼리 완료] 건수={len(result)}")
        return result