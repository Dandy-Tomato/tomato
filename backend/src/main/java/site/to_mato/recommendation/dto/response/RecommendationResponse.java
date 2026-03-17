package site.to_mato.recommendation.dto.response;

public record RecommendationResponse(
        Long topicId,
        String topicTitle,
        String topicDescription,
        Integer estimatedDevelopmentPeriod,
        Integer recommendedTeamSize,
        Integer difficulty,
        Long domainId,
        Long referenceRepoId,
        Double recommendationScore) {

    public static RecommendationResponse of(
            Long topicId,
            String topicTitle,
            String topicDescription,
            Integer estimatedDevelopmentPeriod,
            Integer recommendedTeamSize,
            Integer difficulty,
            Long domainId,
            Long referenceRepoId,
            Double recommendationScore) {
        return new RecommendationResponse(
                topicId,
                topicTitle,
                topicDescription,
                estimatedDevelopmentPeriod,
                recommendedTeamSize,
                difficulty,
                domainId,
                referenceRepoId,
                recommendationScore);
    }
}