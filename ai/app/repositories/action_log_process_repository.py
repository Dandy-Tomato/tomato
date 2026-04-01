from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.orm import Session


def find_action_log_process_by_action_log_id(
    db: Session,
    action_log_id: int,
) -> dict | None:
    sql = text(
        """
        SELECT
            action_log_id,
            status,
            retry_count,
            error_message
        FROM action_log_processes
        WHERE action_log_id = :action_log_id
        """
    )

    row = db.execute(sql, {"action_log_id": action_log_id}).fetchone()

    if row is None:
        return None

    return {
        "action_log_id": row[0],
        "status": row[1],
        "retry_count": row[2],
        "error_message": row[3],
    }


def mark_action_log_processing(
    db: Session,
    action_log_id: int,
) -> int:
    sql = text(
        """
        UPDATE action_log_processes
        SET status = 'PROCESSING',
            updated_at = NOW()
        WHERE action_log_id = :action_log_id
          AND status IN ('PENDING', 'FAILED')
        """
    )

    result = db.execute(sql, {"action_log_id": action_log_id})
    return result.rowcount


def mark_action_log_success(
    db: Session,
    action_log_id: int,
) -> int:
    sql = text(
        """
        UPDATE action_log_processes
        SET status = 'SUCCESS',
            updated_at = NOW()
        WHERE action_log_id = :action_log_id
        """
    )

    result = db.execute(sql, {"action_log_id": action_log_id})
    return result.rowcount


def mark_action_log_failed(
    db: Session,
    action_log_id: int,
    error_message: str | None,
) -> int:
    sql = text(
        """
        UPDATE action_log_processes
        SET status = 'FAILED',
            retry_count = retry_count + 1,
            error_message = :error_message,
            updated_at = NOW()
        WHERE action_log_id = :action_log_id
        """
    )

    result = db.execute(
        sql,
        {
            "action_log_id": action_log_id,
            "error_message": error_message,
        },
    )
    return result.rowcount
