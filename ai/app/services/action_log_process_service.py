from __future__ import annotations

import logging

from app.common.errors import AppError, ErrorCode
from app.db import SessionLocal
from app.repositories.action_log_process_repository import (
    find_action_log_process_by_action_log_id,
    mark_action_log_failed,
    mark_action_log_processing,
    mark_action_log_success,
)
from app.schemas.action_log_event import ActionLogEvent
from app.services.preference_update_service import update_preference_by_event

logger = logging.getLogger(__name__)

MAX_RETRY_COUNT = 3


def process_action_log_event(event: ActionLogEvent) -> bool:
    """
    Returns:
        True  -> Kafka offset commit
        False -> Kafka offset not commit (retry)
    """
    db = SessionLocal()

    try:
        process_row = find_action_log_process_by_action_log_id(
            db=db,
            action_log_id=event.action_log_id,
        )

        if process_row is None:
            raise AppError(
                code=ErrorCode.NOT_FOUND,
                detail=f"action_log_process not found: action_log_id={event.action_log_id}",
                meta={"action_log_id": event.action_log_id},
            )

        status = process_row["status"]
        retry_count = int(process_row["retry_count"])

        if status == "SUCCESS":
            logger.info(
                "Action log already processed | action_log_id=%s",
                event.action_log_id,
            )
            db.rollback()
            return True

        if retry_count >= MAX_RETRY_COUNT:
            logger.warning(
                "Retry limit already exceeded | action_log_id=%s retry_count=%s",
                event.action_log_id,
                retry_count,
            )
            db.rollback()
            return True

        updated_row_count = mark_action_log_processing(
            db=db,
            action_log_id=event.action_log_id,
        )

        if updated_row_count == 0:
            raise AppError(
                code=ErrorCode.NOT_FOUND,
                detail=f"failed to mark processing: action_log_id={event.action_log_id}",
                meta={"action_log_id": event.action_log_id},
            )

        db.commit()

    except AppError:
        db.rollback()
        db.close()
        raise

    except Exception as e:
        db.rollback()
        db.close()
        logger.exception(
            "Failed before preference update | action_log_id=%s",
            event.action_log_id,
        )
        # 실패 처리 상태조차 못 남기는 상황이라 무한 retry 방지 위해 commit 유도
        return True

    finally:
        if db.is_active:
            db.close()

    try:
        update_preference_by_event(event)

        db = SessionLocal()
        try:
            updated_row_count = mark_action_log_success(
                db=db,
                action_log_id=event.action_log_id,
            )

            if updated_row_count == 0:
                raise AppError(
                    code=ErrorCode.NOT_FOUND,
                    detail=f"failed to mark success: action_log_id={event.action_log_id}",
                    meta={"action_log_id": event.action_log_id},
                )

            db.commit()

            logger.info(
                "Action log processed successfully | action_log_id=%s",
                event.action_log_id,
            )
            return True

        except AppError:
            db.rollback()
            raise

        except Exception:
            db.rollback()
            logger.exception(
                "Failed to mark success | action_log_id=%s",
                event.action_log_id,
            )
            # success 마킹 실패도 무한 retry 방지 위해 commit
            return True

        finally:
            db.close()

    except Exception as e:
        db = SessionLocal()

        try:
            process_row = find_action_log_process_by_action_log_id(
                db=db,
                action_log_id=event.action_log_id,
            )

            current_retry_count = 0 if process_row is None else int(process_row["retry_count"])

            updated_row_count = mark_action_log_failed(
                db=db,
                action_log_id=event.action_log_id,
                error_message=str(e),
            )

            if updated_row_count == 0:
                raise AppError(
                    code=ErrorCode.NOT_FOUND,
                    detail=f"failed to mark failed: action_log_id={event.action_log_id}",
                    meta={"action_log_id": event.action_log_id},
                )

            db.commit()

            next_retry_count = current_retry_count + 1

            logger.error(
                "Action log processing failed | action_log_id=%s retry_count=%s max_retry=%s error=%s",
                event.action_log_id,
                next_retry_count,
                MAX_RETRY_COUNT,
                str(e),
            )

            return next_retry_count >= MAX_RETRY_COUNT

        except Exception:
            db.rollback()
            logger.exception(
                "Failed to mark failed status | action_log_id=%s",
                event.action_log_id,
            )
            # failed 상태 저장도 실패하면 무한 retry 방지 위해 commit
            return True

        finally:
            db.close()
