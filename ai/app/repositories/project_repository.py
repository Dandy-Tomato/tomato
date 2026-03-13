from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.orm import Session


def find_project_preference_state_by_project_id(
    db: Session,
    project_id: int
) -> dict | None:
    query = text(
        """
        SELECT preference_embedding, last_processed_action_log_id
        FROM projects
        WHERE project_id = :project_id
        """
    )

    row = db.execute(query, {"project_id": project_id}).mappings().first()
    return None if row is None else dict(row)


def update_preference_state(
    db: Session,
    project_id: int,
    embedding: list[float],
    last_processed_action_log_id: int,
) -> int:
    query = text(
        """
        UPDATE projects
        SET preference_embedding = :embedding,
            last_processed_action_log_id = :last_processed_action_log_id
        WHERE project_id = :project_id
        """
    )

    result = db.execute(
        query,
        {
            "project_id": project_id,
            "embedding": embedding,
            "last_processed_action_log_id": last_processed_action_log_id,
        },
    )
    return result.rowcount
