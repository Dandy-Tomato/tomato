package site.to_mato.topic.dto.response;

import lombok.Builder;
import lombok.Getter;
import site.to_mato.topic.entity.ChildTopic;

@Getter
@Builder
public class RefinedTopicResponse {
    private Long childTopicId;
    private String title;
    private String content;

    public static RefinedTopicResponse from(ChildTopic childTopic) {
        return RefinedTopicResponse.builder()
                .childTopicId(childTopic.getId())
                .title(childTopic.getTitle())
                .content(childTopic.getContent())
                .build();
    }
}
