from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.utils.vector_utils import to_pgvector_literal


def find_preference_embedding_by_project_id(
    db: Session,
    project_id: int,
) -> list[float] | None:
    sql = text(
        """
        SELECT preference_embedding
        FROM projects
        WHERE project_id = :project_id
        """
    )

    row = db.execute(sql, {"project_id": project_id}).fetchone()

    if row is None:
        return None

    embedding = row[0]
    return list(embedding) if embedding is not None else None


def update_preference_embedding(
    db: Session,
    project_id: int,
    embedding: list[float],
) -> int:
    sql = text(
        """
        UPDATE projects
        SET preference_embedding = CAST(:embedding AS vector)
        WHERE project_id = :project_id
        """
    )

    result = db.execute(
        sql,
        {
            "project_id": project_id,
            "embedding": to_pgvector_literal(embedding),
        },
    )
    return result.rowcount
