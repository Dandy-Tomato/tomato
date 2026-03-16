from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.orm import Session


def upsert_project_skill_weight(
    db: Session,
    project_id: int,
    skill_id: int,
    weight: float,
) -> None:
    sql = text(
        """
        INSERT INTO project_skills (
            project_id,
            skill_id,
            weight
        )
        VALUES (
            :project_id,
            :skill_id,
            :weight
        )
        ON CONFLICT (project_id, skill_id)
        DO UPDATE
        SET weight = project_skills.weight + EXCLUDED.weight
        """
    )

    db.execute(
        sql,
        {
            "project_id": project_id,
            "skill_id": skill_id,
            "weight": weight,
        },
    )
