from __future__ import annotations

import logging

from app.common.errors import AppError, ErrorCode
from app.db import SessionLocal
from app.repositories.action_log_repository import (
    count_effective_actions_by_project_id,
    find_recent_effective_action_logs_with_topic_embedding,
)
from app.repositories.project_repository import (
    find_preference_embedding_by_project_id,
    update_preference_embedding,
)
from app.repositories.topic_repository import find_topic_embedding_by_id
from app.schemas.action_log_event import ActionLogEvent
from app.schemas.action_type import ActionType
from app.services.weight_policy import get_action_weight
from app.utils.vector_utils import add_vectors, multiply_vector, zero_vector

logger = logging.getLogger(__name__)

PREFERENCE_INIT_THRESHOLD = 3
PREFERENCE_INIT_SAMPLE_SIZE = 3

INITIALIZABLE_ACTION_TYPES = (
    ActionType.LIKE,
    ActionType.BOOKMARK,
    ActionType.DETAIL_VIEW,
    ActionType.DISLIKE,
)
INITIALIZABLE_ACTION_TYPE_VALUES = [
    action_type.value for action_type in INITIALIZABLE_ACTION_TYPES
]


def build_initial_preference_embedding(
    db,
    project_id: int,
) -> list[float]:
    recent_actions = find_recent_effective_action_logs_with_topic_embedding(
        db=db,
        project_id=project_id,
        limit=PREFERENCE_INIT_SAMPLE_SIZE,
        action_types=INITIALIZABLE_ACTION_TYPE_VALUES,
    )

    if not recent_actions:
        raise AppError(
            code=ErrorCode.NOT_FOUND,
            detail=f"no effective action logs for initialization: project_id={project_id}",
            meta={"project_id": project_id},
        )

    first_embedding = recent_actions[0]["topic_embedding"]
    if first_embedding is None:
        raise AppError(
            code=ErrorCode.NOT_FOUND,
            detail=f"topic embedding missing during initialization: project_id={project_id}",
            meta={"project_id": project_id},
        )

    accumulated = zero_vector(len(first_embedding))

    for action in recent_actions:
        topic_embedding = action["topic_embedding"]
        action_type = ActionType(action["action_type"])

        if topic_embedding is None:
            continue

        weight = get_action_weight(action_type)
        delta_embedding = multiply_vector(topic_embedding, weight)
        accumulated = add_vectors(accumulated, delta_embedding)

    return accumulated


def update_preference_by_event(event: ActionLogEvent) -> None:
    db = SessionLocal()

    try:
        weight = get_action_weight(event.action_type)

        topic_embedding = find_topic_embedding_by_id(db, event.topic_id)
        if topic_embedding is None:
            raise AppError(
                code=ErrorCode.NOT_FOUND,
                detail=f"topic embedding not found: topic_id={event.topic_id}",
                meta={"topic_id": event.topic_id},
            )

        current_embedding = find_preference_embedding_by_project_id(
            db,
            event.project_id,
        )

        if current_embedding is None:
            effective_action_count = count_effective_actions_by_project_id(
                db=db,
                project_id=event.project_id,
                action_types=INITIALIZABLE_ACTION_TYPE_VALUES,
            )

            if effective_action_count < PREFERENCE_INIT_THRESHOLD:
                logger.info(
                    "Preference embedding initialization skipped | project_id=%s action_log_id=%s effective_action_count=%s threshold=%s",
                    event.project_id,
                    event.action_log_id,
                    effective_action_count,
                    PREFERENCE_INIT_THRESHOLD,
                )
                db.rollback()
                return

            new_embedding = build_initial_preference_embedding(
                db=db,
                project_id=event.project_id,
            )

        else:
            delta_embedding = multiply_vector(topic_embedding, weight)
            new_embedding = add_vectors(current_embedding, delta_embedding)

        updated_row_count = update_preference_embedding(
            db=db,
            project_id=event.project_id,
            embedding=new_embedding,
        )

        if updated_row_count == 0:
            raise AppError(
                code=ErrorCode.NOT_FOUND,
                detail=f"project not found: project_id={event.project_id}",
                meta={"project_id": event.project_id},
            )

        db.commit()

        logger.info(
            "Preference embedding updated | action_log_id=%s project_id=%s topic_id=%s action_type=%s weight=%s",
            event.action_log_id,
            event.project_id,
            event.topic_id,
            event.action_type.value,
            weight,
        )

    except AppError:
        db.rollback()
        raise

    except ValueError as e:
        db.rollback()
        raise AppError(
            code=ErrorCode.INVALID_ARGUMENT,
            detail=str(e),
            meta={
                "action_log_id": event.action_log_id,
                "project_id": event.project_id,
                "topic_id": event.topic_id,
            },
        ) from e

    except Exception as e:
        db.rollback()
        logger.exception(
            "Unexpected error while updating preference embedding | action_log_id=%s project_id=%s topic_id=%s",
            event.action_log_id,
            event.project_id,
            event.topic_id,
        )
        raise AppError(
            code=ErrorCode.INTERNAL_ERROR,
            detail="preference embedding update failed",
            meta={
                "action_log_id": event.action_log_id,
                "project_id": event.project_id,
                "topic_id": event.topic_id,
            },
        ) from e

    finally:
        db.close()
