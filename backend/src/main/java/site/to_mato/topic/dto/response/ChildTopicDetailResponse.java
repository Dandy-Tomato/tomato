package site.to_mato.topic.dto.response;

import site.to_mato.topic.entity.ChildTopic;

public record ChildTopicDetailResponse(
        Long childTopicId,
        String title,
        String content
) {
    public static ChildTopicDetailResponse from(ChildTopic childTopic) {
        return new ChildTopicDetailResponse(
                childTopic.getId(),
                childTopic.getTitle(),
                childTopic.getContent()
        );
    }
}
