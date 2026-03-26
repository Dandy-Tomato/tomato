from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.orm import Session


def find_project_skill_weight(
    db: Session,
    project_id: int,
    skill_id: int,
) -> float | None:
    sql = text(
        """
        SELECT weight
        FROM project_skills
        WHERE project_id = :project_id
          AND skill_id = :skill_id
        """
    )

    row = db.execute(
        sql,
        {
            "project_id": project_id,
            "skill_id": skill_id,
        },
    ).fetchone()

    return None if row is None else float(row[0])


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
        SET weight = EXCLUDED.weight
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


def delete_project_skill_weight_if_exists(
    db: Session,
    project_id: int,
    skill_id: int,
) -> None:
    sql = text(
        """
        DELETE FROM project_skills
        WHERE project_id = :project_id
          AND skill_id = :skill_id
        """
    )

    db.execute(
        sql,
        {
            "project_id": project_id,
            "skill_id": skill_id,
        },
    )
