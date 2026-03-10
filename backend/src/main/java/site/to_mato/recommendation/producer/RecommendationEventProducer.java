package site.to_mato.recommendation.producer;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Component;
import site.to_mato.recommendation.event.ActionLogEvent;
import site.to_mato.recommendation.event.RecommendationEventTopics;

@Slf4j
@Component
@RequiredArgsConstructor
public class RecommendationEventProducer {

    private final KafkaTemplate<String, ActionLogEvent> kafkaTemplate;

    public void publishActionLog(ActionLogEvent event) {

        String key = String.valueOf(event.actorUserId());

        kafkaTemplate.send(
                RecommendationEventTopics.ACTION_LOG,
                key,
                event
        ).whenComplete((result, ex) -> {

            if (ex != null) {
                log.error("Kafka publish failed. event={}", event, ex);
                return;
            }

            log.info(
                    "Kafka publish success. topic={}, partition={}, offset={}",
                    result.getRecordMetadata().topic(),
                    result.getRecordMetadata().partition(),
                    result.getRecordMetadata().offset()
            );
        });
    }
}
