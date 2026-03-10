package site.to_mato.recommendation.event;

import site.to_mato.recommendation.entity.ActionLog;
import site.to_mato.recommendation.entity.enums.ActionType;

public record ActionLogEvent(
        Long actionLogId,
        Long actorUserId,
        Long projectId,
        Long topicId,
        ActionType actionType
) {

    public static ActionLogEvent from(ActionLog actionLog) {
        return new ActionLogEvent(
                actionLog.getId(),
                actionLog.getActorUserId(),
                actionLog.getProjectId(),
                actionLog.getTopicId(),
                actionLog.getActionType()
        );
    }
}
