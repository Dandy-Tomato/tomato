package site.to_mato.recommendation.dto.response;

import java.util.List;

public record RecommendationApiResponse(
        Integer statusCode,
        String message,
        List<RecommendationResponse> data) {
}