package site.to_mato.recommendation.service;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Propagation;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.transaction.support.TransactionSynchronization;
import org.springframework.transaction.support.TransactionSynchronizationManager;
import site.to_mato.recommendation.entity.ActionLog;
import site.to_mato.recommendation.entity.ActionLogProcess;
import site.to_mato.recommendation.entity.enums.ActionType;
import site.to_mato.recommendation.event.ActionLogEvent;
import site.to_mato.recommendation.producer.RecommendationEventProducer;
import site.to_mato.recommendation.repository.ActionLogProcessRepository;
import site.to_mato.recommendation.repository.ActionLogRepository;

@Slf4j
@Service
@RequiredArgsConstructor
public class ActionLogService {

    private final ActionLogRepository actionLogRepository;
    private final ActionLogProcessRepository actionLogProcessRepository;
    private final RecommendationEventProducer recommendationEventProducer;

    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public Long createActionLog(
            Long actorUserId,
            Long projectId,
            Long topicId,
            ActionType actionType
    ) {
        ActionLog actionLog = ActionLog.of(
                actorUserId,
                projectId,
                topicId,
                actionType,
                null
        );

        ActionLog savedActionLog = actionLogRepository.save(actionLog);

        ActionLogProcess actionLogProcess = ActionLogProcess.of(savedActionLog);
        actionLogProcessRepository.save(actionLogProcess);

        ActionLogEvent event = ActionLogEvent.from(savedActionLog);

        TransactionSynchronizationManager.registerSynchronization(new TransactionSynchronization() {
            @Override
            public void afterCommit() {
                try {
                    recommendationEventProducer.publishActionLog(event);
                } catch (Exception e) {
                    log.error("afterCommit Kafka publish failed. event={}", event, e);
                }
            }
        });

        return savedActionLog.getId();
    }
}
