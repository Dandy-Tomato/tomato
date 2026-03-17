package site.to_mato.recommendation.dto.response;

import java.util.List;

public record RecommendationApiResponse(
        String status,
        List<RecommendationResponse> data) {
}