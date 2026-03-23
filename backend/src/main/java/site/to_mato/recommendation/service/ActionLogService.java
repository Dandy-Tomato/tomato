package site.to_mato.recommendation.service;

import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import site.to_mato.recommendation.entity.ActionLog;
import site.to_mato.recommendation.entity.ActionLogProcess;
import site.to_mato.recommendation.entity.enums.ActionType;
import site.to_mato.recommendation.event.ActionLogEvent;
import site.to_mato.recommendation.producer.RecommendationEventProducer;
import site.to_mato.recommendation.repository.ActionLogProcessRepository;
import site.to_mato.recommendation.repository.ActionLogRepository;

@Service
@RequiredArgsConstructor
public class ActionLogService {

    private final ActionLogRepository actionLogRepository;
    private final ActionLogProcessRepository actionLogProcessRepository;
    private final RecommendationEventProducer recommendationEventProducer;

    @Transactional
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

        recommendationEventProducer.publishActionLog(event);

        return savedActionLog.getId();
    }
}
