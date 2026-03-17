package site.to_mato.recommendation.dto.request;

import java.util.List;

public record RecommendationRequest(
        Long projectId,
        List<Long> domainIds,
        List<Float> preferenceEmbeddings) {
}