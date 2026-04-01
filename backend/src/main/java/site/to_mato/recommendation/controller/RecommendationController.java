package site.to_mato.recommendation.controller;

import java.util.List;

import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import lombok.RequiredArgsConstructor;
import site.to_mato.common.response.ApiResponse;
import site.to_mato.recommendation.dto.response.RecommendationDetailResponse;
import site.to_mato.recommendation.dto.response.RecommendationResponse;
import site.to_mato.recommendation.service.RecommendationService;

@RestController
@RequiredArgsConstructor
@RequestMapping("/projects/{projectId}/recommendations")
public class RecommendationController {

    private final RecommendationService recommendationService;

    @GetMapping
    public ApiResponse<List<RecommendationResponse>> getRecommendations(
            @PathVariable Long projectId) {

        List<RecommendationResponse> responses = recommendationService.getRecommendationsByProjectId(projectId);
        return ApiResponse.ok(responses);
    }

    @GetMapping("/{topicId}")
    public ApiResponse<RecommendationDetailResponse> getRecommendationDetail(
            @AuthenticationPrincipal Long userId,
            @PathVariable Long projectId,
            @PathVariable Long topicId) {

        RecommendationDetailResponse response = recommendationService.getRecommendationDetail(userId, projectId, topicId);
        return ApiResponse.ok(response);
    }
}
