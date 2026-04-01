package site.to_mato.project.dto.response;

public record ConfirmedProjectTopicResponse(
        Long projectId,
        boolean topicState,
        Long confirmedChildTopicId
) {

    public static ConfirmedProjectTopicResponse of(Long projectId, boolean topicState, Long confirmedChildTopicId) {
        return new ConfirmedProjectTopicResponse(projectId, topicState, confirmedChildTopicId);
    }
}
