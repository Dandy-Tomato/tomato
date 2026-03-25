package site.to_mato.recommendation.dto.response;

import java.util.List;

public record RecommendationDetailResponse(
        Long topicId,
        String title,
        String description,
        Integer expectedDurationWeek,
        Integer recommendedTeamSize,
        Long domainId,
        List<Long> skills,
        Boolean isBookmarked,
        String isReaction,
        Long reactionVersion
) {

    public static RecommendationDetailResponse of(
            Long topicId,
            String title,
            String description,
            Integer expectedDurationWeek,
            Integer recommendedTeamSize,
            Long domainId,
            List<Long> skills,
            Boolean isBookmarked,
            String isReaction,
            Long reactionVersion) {
        return new RecommendationDetailResponse(
                topicId,
                title,
                description,
                expectedDurationWeek,
                recommendedTeamSize,
                domainId,
                skills,
                isBookmarked,
                isReaction,
                reactionVersion);
    }
}