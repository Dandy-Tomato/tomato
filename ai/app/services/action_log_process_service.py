from __future__ import annotations

import logging

from app.common.errors import AppError, ErrorCode
from app.common.transaction import session_scope
from app.repositories.action_log_process_repository import (
    find_action_log_process_by_action_log_id,
    mark_action_log_failed,
    mark_action_log_processing,
    mark_action_log_success,
)
from app.schemas.action_log_event import ActionLogEvent
from app.schemas.commit_decision import CommitDecision
from app.schemas.process_status import ProcessStatus
from app.services.preference_update_service import update_preference_by_event

logger = logging.getLogger(__name__)

MAX_RETRY_COUNT = 3


def process_action_log_event(event: ActionLogEvent) -> CommitDecision:
    try:
        process_row = get_required_process_row(event.action_log_id)

        if should_commit_without_processing(process_row, event.action_log_id):
            return CommitDecision.COMMIT

        mark_processing_or_raise(event.action_log_id)

    except AppError:
        logger.exception(
            "Failed before preference update | action_log_id=%s",
            event.action_log_id,
        )
        return CommitDecision.COMMIT

    except Exception:
        logger.exception(
            "Unexpected failure before preference update | action_log_id=%s",
            event.action_log_id,
        )
        return CommitDecision.COMMIT

    try:
        update_preference_by_event(event)
        return mark_success_and_commit(event.action_log_id)

    except Exception as exc:
        return mark_failed_and_decide_retry(
            action_log_id=event.action_log_id,
            error=exc,
        )


def get_required_process_row(action_log_id: int) -> dict:
    with session_scope() as db:
        process_row = find_action_log_process_by_action_log_id(
            db=db,
            action_log_id=action_log_id,
        )

        if process_row is None:
            raise AppError(
                code=ErrorCode.NOT_FOUND,
                detail=f"action_log_process not found: action_log_id={action_log_id}",
                meta={"action_log_id": action_log_id},
            )

        return process_row


def should_commit_without_processing(process_row: dict, action_log_id: int) -> bool:
    status = ProcessStatus(process_row["status"])
    retry_count = int(process_row["retry_count"])

    if status == ProcessStatus.SUCCESS:
        logger.info(
            "Action log already processed | action_log_id=%s",
            action_log_id,
        )
        return True

    if retry_count >= MAX_RETRY_COUNT:
        logger.warning(
            "Retry limit already exceeded | action_log_id=%s retry_count=%s",
            action_log_id,
            retry_count,
        )
        return True

    return False


def mark_processing_or_raise(action_log_id: int) -> None:
    with session_scope() as db:
        updated_row_count = mark_action_log_processing(
            db=db,
            action_log_id=action_log_id,
        )

        if updated_row_count == 0:
            raise AppError(
                code=ErrorCode.NOT_FOUND,
                detail=f"failed to mark processing: action_log_id={action_log_id}",
                meta={"action_log_id": action_log_id},
            )


def mark_success_and_commit(action_log_id: int) -> CommitDecision:
    try:
        with session_scope() as db:
            updated_row_count = mark_action_log_success(
                db=db,
                action_log_id=action_log_id,
            )

            if updated_row_count == 0:
                raise AppError(
                    code=ErrorCode.NOT_FOUND,
                    detail=f"failed to mark success: action_log_id={action_log_id}",
                    meta={"action_log_id": action_log_id},
                )

        logger.info(
            "Action log processed successfully | action_log_id=%s",
            action_log_id,
        )
        return CommitDecision.COMMIT

    except Exception:
        logger.exception(
            "Failed to mark success | action_log_id=%s",
            action_log_id,
        )
        return CommitDecision.COMMIT


def mark_failed_and_decide_retry(
    action_log_id: int,
    error: Exception,
) -> CommitDecision:
    try:
        with session_scope() as db:
            process_row = find_action_log_process_by_action_log_id(
                db=db,
                action_log_id=action_log_id,
            )
            current_retry_count = 0 if process_row is None else int(process_row["retry_count"])

            updated_row_count = mark_action_log_failed(
                db=db,
                action_log_id=action_log_id,
                error_message=str(error),
            )

            if updated_row_count == 0:
                raise AppError(
                    code=ErrorCode.NOT_FOUND,
                    detail=f"failed to mark failed: action_log_id={action_log_id}",
                    meta={"action_log_id": action_log_id},
                )

        next_retry_count = current_retry_count + 1

        logger.error(
            "Action log processing failed | action_log_id=%s retry_count=%s max_retry=%s error=%s",
            action_log_id,
            next_retry_count,
            MAX_RETRY_COUNT,
            str(error),
        )

        if next_retry_count >= MAX_RETRY_COUNT:
            return CommitDecision.COMMIT

        return CommitDecision.RETRY

    except Exception:
        logger.exception(
            "Failed to mark failed status | action_log_id=%s",
            action_log_id,
        )
        return CommitDecision.COMMIT
