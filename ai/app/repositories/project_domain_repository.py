from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.orm import Session


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
        SET weight = project_domains.weight + EXCLUDED.weight
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
