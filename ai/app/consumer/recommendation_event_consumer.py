from __future__ import annotations

import json
import logging

from kafka import KafkaConsumer

from app.common.errors import AppError
from app.schemas.action_log_event import ActionLogEvent
from app.schemas.commit_decision import CommitDecision
from app.services.action_log_process_service import process_action_log_event
from app.settings import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_consumer() -> KafkaConsumer:
    return KafkaConsumer(
        settings.KAFKA_ACTION_LOG_TOPIC,
        bootstrap_servers=[settings.KAFKA_BOOTSTRAP_SERVERS],
        group_id=settings.KAFKA_CONSUMER_GROUP,
        auto_offset_reset="earliest",
        enable_auto_commit=False,
        value_deserializer=lambda message: json.loads(message.decode("utf-8")),
    )


def run_consumer() -> None:
    consumer = create_consumer()

    logger.info(
        "Recommendation event consumer started | topic=%s group=%s bootstrap=%s",
        settings.KAFKA_ACTION_LOG_TOPIC,
        settings.KAFKA_CONSUMER_GROUP,
        settings.KAFKA_BOOTSTRAP_SERVERS,
    )

    try:
        for message in consumer:
            try:
                event = ActionLogEvent.model_validate(message.value)
                decision = process_action_log_event(event)

                if decision == CommitDecision.COMMIT:
                    consumer.commit()
                    logger.info(
                        "Kafka offset committed | action_log_id=%s",
                        event.action_log_id,
                    )
                else:
                    logger.info(
                        "Kafka offset not committed for retry | action_log_id=%s",
                        event.action_log_id,
                    )

            except AppError as e:
                logger.error(
                    "Failed to process recommendation event | code=%s detail=%s meta=%s",
                    e.code,
                    e.detail,
                    e.meta,
                )

            except Exception:
                logger.exception(
                    "Unexpected error while processing recommendation event | raw_message=%s",
                    message.value,
                )

    except KeyboardInterrupt:
        logger.info("Recommendation event consumer stopped by keyboard interrupt.")

    finally:
        consumer.close()
        logger.info("Recommendation event consumer closed.")


if __name__ == "__main__":
    run_consumer()
