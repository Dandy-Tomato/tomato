from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.orm import Session


def find_topic_embedding_by_id(
    db: Session,
    topic_id: int,
) -> list[float] | None:
    sql = text(
        """
        SELECT topic_embedding
        FROM topics
        WHERE topic_id = :topic_id
        """
    )

    row = db.execute(sql, {"topic_id": topic_id}).fetchone()

    if row is None:
        return None

    embedding = row[0]
    return list(embedding) if embedding is not None else None
