from __future__ import annotations

from sqlalchemy import bindparam, text
from sqlalchemy.orm import Session


def count_effective_actions_by_project_id(
    db: Session,
    project_id: int,
) -> int:
    sql = text(
        """
        SELECT COUNT(*)
        FROM action_logs al
        WHERE al.project_id = :project_id
        AND al.action_type IN :action_types
        """
    ).bindparams(bindparam("action_types", expanding=True))

    result = db.execute(
        sql,
        {
            "project_id": project_id,
        },
    ).scalar_one()

    return int(result)


def find_recent_effective_action_logs_with_topic_embedding(
    db: Session,
    project_id: int,
    limit: int,
) -> list[dict]:
    sql = text(
        """
        SELECT
            al.action_log_id,
            al.project_id,
            al.topic_id,
            al.action_type,
            al.created_at,
            t.topic_embedding
        FROM action_logs al
        JOIN topics t
          ON t.topic_id = al.topic_id
        WHERE al.project_id = :project_id
          AND al.action_type IN :action_types
          AND t.topic_embedding IS NOT NULL
        ORDER BY al.created_at DESC, al.action_log_id DESC
        LIMIT :limit
        """
    ).bindparams(action_types=INITIALIZABLE_ACTION_TYPES)

    rows = db.execute(
        sql,
        {
            "project_id": project_id,
            "limit": limit,
        },
    ).fetchall()

    result: list[dict] = []
    for row in rows:
        result.append(
            {
                "action_log_id": row[0],
                "project_id": row[1],
                "topic_id": row[2],
                "action_type": row[3],
                "created_at": row[4],
                "topic_embedding": list(row[5]) if row[5] is not None else None,
            }
        )

    return result
