from __future__ import annotations

import logging

from app.common.errors import AppError, ErrorCode
from app.common.transaction import session_scope
from app.repositories.action_log_repository import (
    count_effective_actions_by_project_id,
    find_recent_effective_action_logs_with_topic_embedding,
)
from app.repositories.project_repository import (
    find_project_preference_state_by_project_id,
    update_preference_state,
)
from app.repositories.topic_repository import find_topic_embedding_by_id
from app.schemas.action_log_event import ActionLogEvent
from app.schemas.action_type import ActionType
from app.utils.vector_utils import add_vectors, multiply_vector, zero_vector

logger = logging.getLogger(__name__)

PREFERENCE_INIT_THRESHOLD = 3
PREFERENCE_INIT_SAMPLE_SIZE = 3


def update_preference_by_event(event: ActionLogEvent) -> None:
    with session_scope() as db:
        project_state = get_required_project_preference_state(
            db=db,
            project_id=event.project_id,
        )

        last_processed_action_log_id = project_state["last_processed_action_log_id"]
        current_embedding = project_state["preference_embedding"]

        if is_already_processed(
            event_action_log_id=event.action_log_id,
            last_processed_action_log_id=last_processed_action_log_id,
        ):
            logger.info(
                "Action log already reflected in preference embedding | action_log_id=%s project_id=%s last_processed_action_log_id=%s",
                event.action_log_id,
                event.project_id,
                last_processed_action_log_id,
            )
            return

        topic_embedding = get_required_topic_embedding(db, event.topic_id)

        if current_embedding is None:
            new_embedding = build_initial_preference_embedding_or_skip(
                db=db,
                project_id=event.project_id,
                action_log_id=event.action_log_id,
            )
            if new_embedding is None:
                return
        else:
            new_embedding = build_incremental_preference_embedding(
                current_embedding=current_embedding,
                topic_embedding=topic_embedding,
                action_type=event.action_type,
            )

        save_preference_state(
            db=db,
            project_id=event.project_id,
            embedding=new_embedding,
            last_processed_action_log_id=event.action_log_id,
        )

        logger.info(
            "Preference embedding updated | action_log_id=%s project_id=%s topic_id=%s action_type=%s weight=%s",
            event.action_log_id,
            event.project_id,
            event.topic_id,
            event.action_type.value,
            event.action_type.weight,
        )


def get_required_project_preference_state(db, project_id: int) -> dict:
    project_state = find_project_preference_state_by_project_id(
        db=db,
        project_id=project_id,
    )

    if project_state is None:
        raise AppError(
            code=ErrorCode.NOT_FOUND,
            detail=f"project not found: project_id={project_id}",
            meta={"project_id": project_id},
        )

    return project_state


def is_already_processed(
    event_action_log_id: int,
    last_processed_action_log_id: int | None,
) -> bool:
    if last_processed_action_log_id is None:
        return False

    return event_action_log_id <= last_processed_action_log_id


def get_required_topic_embedding(db, topic_id: int) -> list[float]:
    topic_embedding = find_topic_embedding_by_id(db, topic_id)
    if topic_embedding is None:
        raise AppError(
            code=ErrorCode.NOT_FOUND,
            detail=f"topic embedding not found: topic_id={topic_id}",
            meta={"topic_id": topic_id},
        )
    return topic_embedding


def build_initial_preference_embedding_or_skip(
    db,
    project_id: int,
    action_log_id: int,
) -> list[float] | None:
    effective_action_count = count_effective_actions_by_project_id(
        db=db,
        project_id=project_id,
        action_types=ActionType.preference_initializable_values(),
    )

    if effective_action_count < PREFERENCE_INIT_THRESHOLD:
        logger.info(
            "Preference embedding creation skipped | project_id=%s action_log_id=%s effective_action_count=%s threshold=%s",
            project_id,
            action_log_id,
            effective_action_count,
            PREFERENCE_INIT_THRESHOLD,
        )
        return None

    return build_initial_preference_embedding(
        db=db,
        project_id=project_id,
    )


def build_initial_preference_embedding(
    db,
    project_id: int,
) -> list[float]:
    recent_actions = find_recent_effective_action_logs_with_topic_embedding(
        db=db,
        project_id=project_id,
        limit=PREFERENCE_INIT_SAMPLE_SIZE,
        action_types=ActionType.preference_initializable_values(),
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
        if topic_embedding is None:
            continue

        action_type = ActionType(action["action_type"])
        delta_embedding = multiply_vector(topic_embedding, action_type.weight)
        accumulated = add_vectors(accumulated, delta_embedding)

    return accumulated


def build_incremental_preference_embedding(
    current_embedding: list[float],
    topic_embedding: list[float],
    action_type: ActionType,
) -> list[float]:
    delta_embedding = multiply_vector(topic_embedding, action_type.weight)
    return add_vectors(current_embedding, delta_embedding)


def save_preference_state(
    db,
    project_id: int,
    embedding: list[float],
    last_processed_action_log_id: int,
) -> None:
    updated_row_count = update_preference_state(
        db=db,
        project_id=project_id,
        embedding=embedding,
        last_processed_action_log_id=last_processed_action_log_id,
    )

    if updated_row_count == 0:
        raise AppError(
            code=ErrorCode.NOT_FOUND,
            detail=f"failed to update preference state: project_id={project_id}",
            meta={"project_id": project_id},
        )
