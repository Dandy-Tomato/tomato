package site.to_mato.recommendation.dto.response;

import java.util.List;

public record RecommendationResponse(
        Long topicId,
        String topicTitle,
        String topicDescription,
        Integer estimatedDurationWeek,
        Integer recommendedTeamSize,
        Integer difficulty,
        Long domainId,
        String domainName,
        List<String> skills) {

    public static RecommendationResponse of(
            Long topicId,
            String topicTitle,
            String topicDescription,
            Integer estimatedDurationWeek,
            Integer recommendedTeamSize,
            Integer difficulty,
            Long domainId,
            String domainName,
            List<String> skills) {
        return new RecommendationResponse(
                topicId,
                topicTitle,
                topicDescription,
                estimatedDurationWeek,
                recommendedTeamSize,
                difficulty,
                domainId,
                domainName,
                skills);
    }
}