from __future__ import annotations

import logging

from sqlalchemy import text
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

# ── 상수 ──────────────────────────────────────────────────
# top_k의 몇 배를 후보로 추릴지
CANDIDATE_K_MULTIPLIER = 5

# domain_score / skill_score:
#   action_type.weight 기반으로 행동 발생 시마다 누적 합산되는 값
#   (project_domains.weight, project_skills.weight)
#   embedding_score(0~1)와 스케일이 다를 수 있으나,
#   누적값이 클수록 선호도가 높다는 의미이므로 그대로 합산
# → 별도 가중치 상수 없이 세 점수를 단순 합산


class RecommendationRepository:
    def __init__(self, db: Session):
        self.db = db

    def find_topics(
        self,
        project_id: int,
        domain_ids: list[int],
        top_k: int,
        preference_embedding: list[float] | None = None,
    ) -> list[dict]:
        """
        추천 주제 조회.

        preference_embedding 유무에 따라 분기:
        - 있음 (웜스타트): 임베딩 유사도 + 도메인/스킬 가중치 복합 점수로 정렬
        - 없음 (콜드스타트): 도메인/스킬 가중치만으로 정렬
        """
        if preference_embedding is not None:
            return self._find_topics_with_embedding(
                project_id=project_id,
                top_k=top_k,
                preference_embedding=preference_embedding,
            )

        return self._find_topics_cold_start(
            project_id=project_id,
            domain_ids=domain_ids,
            top_k=top_k,
        )

    # ── 웜스타트: 임베딩 + 도메인/스킬 가중치 복합 점수 ─────────────────────
    def _find_topics_with_embedding(
        self,
        project_id: int,
        top_k: int,
        preference_embedding: list[float],
    ) -> list[dict]:
        candidate_k = top_k * CANDIDATE_K_MULTIPLIER
        logger.info(
            f"[웜스타트 쿼리] project_id={project_id}, candidate_k={candidate_k}, top_k={top_k}"
        )

        embedding_str = "[" + ",".join(map(str, preference_embedding)) + "]"

        query = text("""
            WITH candidate_topics AS (
                -- 1단계: 임베딩 유사도로 후보 추림
                -- 거리(0~2) → 유사도(0~1)로 변환: 1 - 거리
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
                    1 - (t.topic_embedding <=> CAST(:preference_embedding AS vector)) AS embedding_score
                FROM topics t
                LEFT JOIN domains d ON d.domain_id = t.domain_id
                WHERE t.topic_embedding IS NOT NULL
                ORDER BY t.topic_embedding <=> CAST(:preference_embedding AS vector) ASC
                LIMIT :candidate_k
            ),
            domain_scores AS (
                -- 2단계: 프로젝트 도메인 가중치 매핑
                -- 프로젝트가 선호하지 않는 도메인은 0점 처리
                SELECT
                    ct.topic_id,
                    COALESCE(pd.weight, 0) AS domain_score
                FROM candidate_topics ct
                LEFT JOIN project_domains pd
                    ON pd.project_id = :project_id
                   AND pd.domain_id = ct.domain_id
            ),
            skill_scores AS (
                -- 3단계: 프로젝트 스킬 가중치 합산
                -- action_type.weight 누적값이므로 정규화 없이 그대로 합산
                SELECT
                    ct.topic_id,
                    COALESCE(SUM(ps.weight), 0) AS skill_score
                FROM candidate_topics ct
                LEFT JOIN topic_skills ts
                    ON ts.topic_id = ct.topic_id
                LEFT JOIN project_skills ps
                    ON ps.project_id = :project_id
                   AND ps.skill_id = ts.skill_id
                GROUP BY ct.topic_id
            ),
            topic_skills_agg AS (
                -- 스킬명 목록 집계 (점수 계산과 별개 — 응답용)
                SELECT
                    ct.topic_id,
                    COALESCE(
                        ARRAY_AGG(DISTINCT s.skill_id) FILTER (WHERE s.skill_id IS NOT NULL),
                        ARRAY[]::bigint[]
                    ) AS skills
                FROM candidate_topics ct
                LEFT JOIN topic_skills ts ON ts.topic_id = ct.topic_id
                LEFT JOIN skills s ON s.skill_id = ts.skill_id
                GROUP BY ct.topic_id
            )
            SELECT
                ct.topic_id,
                ct.title,
                ct.description,
                ct.expected_duration_week,
                ct.recommended_team_size,
                ct.difficulty,
                ct.domain_id,
                ct.domain_name,
                ct.source_repo_id,
                tsa.skills,
                ct.embedding_score,
                ds.domain_score,
                ss.skill_score,
                (
                    ct.embedding_score
                    + ds.domain_score
                    + ss.skill_score
                ) AS final_score
            FROM candidate_topics ct
            LEFT JOIN domain_scores ds ON ds.topic_id = ct.topic_id
            LEFT JOIN skill_scores ss ON ss.topic_id = ct.topic_id
            LEFT JOIN topic_skills_agg tsa ON tsa.topic_id = ct.topic_id
            ORDER BY final_score DESC
            LIMIT :top_k
        """)

        rows = (
            self.db.execute(
                query,
                {
                    "preference_embedding": embedding_str,
                    "project_id": project_id,
                    "candidate_k": candidate_k,
                    "top_k": top_k,
                },
            )
            .mappings()
            .all()
        )

        result = [dict(row) for row in rows]
        logger.info(f"[웜스타트 쿼리 완료] 건수={len(result)}")
        return result

    # ── 콜드스타트: 도메인/스킬 가중치만으로 정렬 ─────────────────────────────
    def _find_topics_cold_start(
        self,
        project_id: int,
        domain_ids: list[int],
        top_k: int,
    ) -> list[dict]:
        logger.info(
            f"[콜드스타트 쿼리] project_id={project_id}, domain_ids={domain_ids}, top_k={top_k}"
        )

        query = text("""
            WITH domain_scores AS (
                SELECT
                    t.topic_id,
                    COALESCE(pd.weight, 0) AS domain_score
                FROM topics t
                LEFT JOIN project_domains pd
                    ON pd.project_id = :project_id
                   AND pd.domain_id = t.domain_id
            ),
            skill_scores AS (
                SELECT
                    t.topic_id,
                    COALESCE(SUM(ps.weight), 0) AS skill_score
                FROM topics t
                LEFT JOIN topic_skills ts
                    ON ts.topic_id = t.topic_id
                LEFT JOIN project_skills ps
                    ON ps.project_id = :project_id
                   AND ps.skill_id = ts.skill_id
                GROUP BY t.topic_id
            ),
            topic_skills_agg AS (
                SELECT
                    t.topic_id,
                    COALESCE(
                        ARRAY_AGG(DISTINCT s.skill_id) FILTER (WHERE s.skill_id IS NOT NULL),
                        ARRAY[]::bigint[]
                    ) AS skills
                FROM topics t
                LEFT JOIN topic_skills ts ON ts.topic_id = t.topic_id
                LEFT JOIN skills s ON s.skill_id = ts.skill_id
                GROUP BY t.topic_id
            )
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
                tsa.skills,
                0.0 AS embedding_score,
                ds.domain_score,
                ss.skill_score,
                (
                    ds.domain_score
                    + ss.skill_score
                ) AS final_score
            FROM topics t
            LEFT JOIN domains d ON d.domain_id = t.domain_id
            LEFT JOIN domain_scores ds ON ds.topic_id = t.topic_id
            LEFT JOIN skill_scores ss ON ss.topic_id = t.topic_id
            LEFT JOIN topic_skills_agg tsa ON tsa.topic_id = t.topic_id
            -- 콜드스타트는 domain_ids로 1차 필터 후 점수 정렬
            WHERE t.domain_id = ANY(:domain_ids)
            ORDER BY final_score DESC
            LIMIT :top_k
        """)

        rows = (
            self.db.execute(
                query,
                {
                    "project_id": project_id,
                    "domain_ids": domain_ids,
                    "top_k": top_k,
                },
            )
            .mappings()
            .all()
        )

        result = [dict(row) for row in rows]
        logger.info(f"[콜드스타트 쿼리 완료] 건수={len(result)}")
        return result
