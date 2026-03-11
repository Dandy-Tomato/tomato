import json
import logging

from kafka import KafkaConsumer

from app.common.errors import AppError
from app.schemas.action_log_event import ActionLogEvent
from app.services.preference_update_service import update_preference_by_event
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
        "Recommendation event consumer started. topic=%s group=%s bootstrap=%s",
        settings.KAFKA_ACTION_LOG_TOPIC,
        settings.KAFKA_CONSUMER_GROUP,
        settings.KAFKA_BOOTSTRAP_SERVERS,
    )

    try:
        for message in consumer:
            try:
                event = ActionLogEvent.model_validate(message.value)

                update_preference_by_event(event)

                logger.info(
                    "Received event | action_log_id=%s project_id=%s topic_id=%s action_type=%s",
                    event.action_log_id,
                    event.project_id,
                    event.topic_id,
                    event.action_type.value,
                )

                consumer.commit()

            except AppError as e:
                logger.error(
                    "Failed to process recommendation event | code=%s detail=%s meta=%s",
                    e.code,
                    e.detail,
                    e.meta,
                )

            except Exception as e:
                logger.exception("Failed to process recommendation event: %s", e)

    except KeyboardInterrupt:
        logger.info("Recommendation event consumer stopped.")
    finally:
        consumer.close()


if __name__ == "__main__":
    run_consumer()
