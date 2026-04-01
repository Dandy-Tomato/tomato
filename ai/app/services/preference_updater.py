from __future__ import annotations

import logging

from app.common.errors import AppError, ErrorCode
from app.common.transaction import session_scope
from app.repositories.action_log_repository import (
    count_effective_actions_by_project_id,
    find_recent_effective_action_logs_with_topic_embedding,
)
from app.repositories.project_domain_repository import (
    delete_project_domain_weight_if_exists,
    find_project_domain_weight,
    upsert_project_domain_weight,
)
from app.repositories.project_repository import (
    find_project_preference_state_by_project_id,
    update_last_processed_action_log_id,
    update_preference_state,
)
from app.repositories.project_skill_repository import (
    delete_project_skill_weight_if_exists,
    find_project_skill_weight,
    upsert_project_skill_weight,
)
from app.repositories.topic_repository import (
    find_topic_domain_id_by_topic_id,
    find_topic_embedding_by_id,
    find_topic_skill_ids_by_topic_id,
)
from app.schemas.action_log_event import ActionLogEvent
from app.schemas.enums.action_type import ActionType
from app.utils.vector_utils import add_vectors, multiply_vector, zero_vector

logger = logging.getLogger(__name__)

PREFERENCE_INIT_THRESHOLD = 3
PREFERENCE_INIT_SAMPLE_SIZE = 3
MIN_WEIGHT_THRESHOLD = 0.05


def update_project_preference_by_event(
    event: ActionLogEvent,
) -> None:
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
                "Action log already reflected in project preference | action_log_id=%s project_id=%s last_processed_action_log_id=%s",
                event.action_log_id,
                event.project_id,
                last_processed_action_log_id,
            )
            return

        reflect_project_skill_and_domain_weight(
            db=db,
            project_id=event.project_id,
            topic_id=event.topic_id,
            action_type=event.action_type,
        )

        if current_embedding is None:
            new_embedding = build_initial_preference_embedding_or_skip(
                db=db,
                project_id=event.project_id,
                action_log_id=event.action_log_id,
            )

            if new_embedding is None:
                save_last_processed_action_log_id(
                    db=db,
                    project_id=event.project_id,
                    last_processed_action_log_id=event.action_log_id,
                )

                logger.info(
                    "Project weights updated and preference embedding creation skipped | action_log_id=%s project_id=%s topic_id=%s action_type=%s weight=%s",
                    event.action_log_id,
                    event.project_id,
                    event.topic_id,
                    event.action_type.value,
                    event.action_type.weight,
                )
                return

        else:
            topic_embedding = get_required_topic_embedding(db, event.topic_id)
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
            "Preference embedding and project weights updated | action_log_id=%s project_id=%s topic_id=%s action_type=%s weight=%s",
            event.action_log_id,
            event.project_id,
            event.topic_id,
            event.action_type.value,
            event.action_type.weight,
        )


def get_required_project_preference_state(
    db,
    project_id: int,
) -> dict:
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


def get_required_topic_embedding(
    db,
    topic_id: int,
) -> list[float]:
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


def save_last_processed_action_log_id(
    db,
    project_id: int,
    last_processed_action_log_id: int,
) -> None:
    updated_row_count = update_last_processed_action_log_id(
        db=db,
        project_id=project_id,
        last_processed_action_log_id=last_processed_action_log_id,
    )

    if updated_row_count == 0:
        raise AppError(
            code=ErrorCode.NOT_FOUND,
            detail=f"failed to update last processed action log id: project_id={project_id}",
            meta={"project_id": project_id},
        )


def reflect_project_skill_and_domain_weight(
    db,
    project_id: int,
    topic_id: int,
    action_type: ActionType,
) -> None:
    skill_ids = find_topic_skill_ids_by_topic_id(
        db=db,
        topic_id=topic_id,
    )

    domain_id = find_topic_domain_id_by_topic_id(
        db=db,
        topic_id=topic_id,
    )

    for skill_id in skill_ids:
        reflect_project_skill_weight(
            db=db,
            project_id=project_id,
            skill_id=skill_id,
            delta=action_type.weight,
        )

    if domain_id is not None:
        reflect_project_domain_weight(
            db=db,
            project_id=project_id,
            domain_id=domain_id,
            delta=action_type.weight,
        )


def reflect_project_skill_weight(
    db,
    project_id: int,
    skill_id: int,
    delta: float,
) -> None:
    current_weight = find_project_skill_weight(
        db=db,
        project_id=project_id,
        skill_id=skill_id,
    )

    base_weight = 0.0 if current_weight is None else current_weight
    new_weight = max(0.0, base_weight + delta)

    if new_weight < MIN_WEIGHT_THRESHOLD:
        delete_project_skill_weight_if_exists(
            db=db,
            project_id=project_id,
            skill_id=skill_id,
        )
        return

    upsert_project_skill_weight(
        db=db,
        project_id=project_id,
        skill_id=skill_id,
        weight=new_weight,
    )


def reflect_project_domain_weight(
    db,
    project_id: int,
    domain_id: int,
    delta: float,
) -> None:
    current_weight = find_project_domain_weight(
        db=db,
        project_id=project_id,
        domain_id=domain_id,
    )

    base_weight = 0.0 if current_weight is None else current_weight
    new_weight = max(0.0, base_weight + delta)

    if new_weight < MIN_WEIGHT_THRESHOLD:
        delete_project_domain_weight_if_exists(
            db=db,
            project_id=project_id,
            domain_id=domain_id,
        )
        return

    upsert_project_domain_weight(
        db=db,
        project_id=project_id,
        domain_id=domain_id,
        weight=new_weight,
    )
