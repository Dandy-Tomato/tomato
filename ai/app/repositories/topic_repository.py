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

def find_topic_skill_ids_by_topic_id(
    db: Session,
    topic_id: int
) -> list[int]:
    sql = text(
        """
        SELECT ts.skill_id
        FROM topic_skills ts
        WHERE ts.topic_id = :topic_id
        """
    )

    rows = db.execute(sql, {"topic_id": topic_id}).mappings().all()
    return [int(row["skill_id"]) for row in rows]


def find_topic_domain_ids_by_topic_id(
    db: Session,
    topic_id: int
) -> list[int]:
    sql = text(
        """
        SELECT td.domain_id
        FROM topic_domains td
        WHERE td.topic_id = :topic_id
        """
    )

    rows = db.execute(sql, {"topic_id": topic_id}).mappings().all()
    return [int(row["domain_id"]) for row in rows]
