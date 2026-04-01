from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.orm import Session


def find_project_domain_weight(
    db: Session,
    project_id: int,
    domain_id: int,
) -> float | None:
    sql = text(
        """
        SELECT weight
        FROM project_domains
        WHERE project_id = :project_id
          AND domain_id = :domain_id
        """
    )

    row = db.execute(
        sql,
        {
            "project_id": project_id,
            "domain_id": domain_id,
        },
    ).fetchone()

    return None if row is None else float(row[0])


def upsert_project_domain_weight(
    db: Session,
    project_id: int,
    domain_id: int,
    weight: float,
) -> None:
    sql = text(
        """
        INSERT INTO project_domains (
            project_id,
            domain_id,
            weight
        )
        VALUES (
            :project_id,
            :domain_id,
            :weight
        )
        ON CONFLICT (project_id, domain_id)
        DO UPDATE
        SET weight = EXCLUDED.weight
        """
    )

    db.execute(
        sql,
        {
            "project_id": project_id,
            "domain_id": domain_id,
            "weight": weight,
        },
    )


def delete_project_domain_weight_if_exists(
    db: Session,
    project_id: int,
    domain_id: int,
) -> None:
    sql = text(
        """
        DELETE FROM project_domains
        WHERE project_id = :project_id
          AND domain_id = :domain_id
        """
    )

    db.execute(
        sql,
        {
            "project_id": project_id,
            "domain_id": domain_id,
        },
    )
