import json
import logging

from kafka import KafkaConsumer

from app.schemas.action_log_event import ActionLogEvent
from app.services.weight_policy import get_action_weight
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
                # Kafka 메시지를 Pydantic schema로 검증
                event = ActionLogEvent.model_validate(message.value)

                # action type → weight 변환
                weight = get_action_weight(event.action_type)

                logger.info(
                    "Received event | action_log_id=%s project_id=%s topic_id=%s action_type=%s weight=%s",
                    event.action_log_id,
                    event.project_id,
                    event.topic_id,
                    event.action_type.value,
                    weight,
                )

                # 정상 처리 시 offset commit
                consumer.commit()

            except Exception as e:
                logger.exception("Failed to process recommendation event: %s", e)

    except KeyboardInterrupt:
        logger.info("Recommendation event consumer stopped.")
    finally:
        consumer.close()


if __name__ == "__main__":
    run_consumer()
