package site.to_mato.project.dto.response;

public record ProjectTopicReactionResponse(
        String isReaction,
        Long reactionVersion
) {
    public static ProjectTopicReactionResponse of(String isReaction, Long reactionVersion) {
        return new ProjectTopicReactionResponse(isReaction, reactionVersion);
    }
}