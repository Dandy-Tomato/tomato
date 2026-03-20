package site.to_mato.recommendation.dto.response;

import java.util.List;

public record RecommendationResponse(
        Long topicId,
        String title,
        String description,
        Integer expectedDurationWeek,
        Integer recommendedTeamSize,
        Integer difficulty,
        Long domainId,
        String domainName,
        List<String> skills) {

    public static RecommendationResponse of(
            Long topicId,
            String title,
            String description,
            Integer expectedDurationWeek,
            Integer recommendedTeamSize,
            Integer difficulty,
            Long domainId,
            String domainName,
            List<String> skills) {
        return new RecommendationResponse(
                topicId,
                title,
                description,
                expectedDurationWeek,
                recommendedTeamSize,
                difficulty,
                domainId,
                domainName,
                skills);
    }
}